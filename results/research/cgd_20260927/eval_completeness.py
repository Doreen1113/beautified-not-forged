"""Completeness analyses for the paper (reviewer gaps): per-forgery-method and per-filter-type recall with confusion
matrix on FF++ test, robustness sweep (JPEG / blur / downscale) on FF++ test reals+fakes, and latency / size for each model.

python eval_completeness.py --arm MASK  -> completeness_<ARM>.json, figs/fig_confusion_<ARM>.png, figs/fig_robust.png
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

import cv2
import matplotlib
import numpy as np
import timm
import torch
from PIL import Image
from sklearn.metrics import confusion_matrix

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
BASE = Path(r"C:\My_Project\AIGC")
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(BASE / "docs/paper_v2"))
from train_cgd import CGDNet, MODEL, NORM, SIZE, remap  # noqa: E402
import make_figures as MF  # noqa: E402
from torchvision import transforms  # noqa: E402

UNI = BASE / "results/research/ffpp_unified_20260925"
TF = transforms.Compose([transforms.Resize((SIZE, SIZE)), transforms.ToTensor(), NORM])
CLS = ["real", "fake", "filter"]


def rows():
    return [l.split("\t") for l in (UNI / "ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]


@torch.no_grad()
def predict(net, ims, bs=48):
    out = []
    for i in range(0, len(ims), bs):
        x = torch.stack([TF(Image.fromarray(a) if isinstance(a, np.ndarray) else Image.open(a).convert("RGB")) for a in ims[i:i + bs]]).cuda()
        with torch.autocast("cuda", dtype=torch.bfloat16):
            out.append(torch.softmax(net(x)[0].float(), 1).cpu())
    return torch.cat(out).numpy()


def per_source(net, arm):
    R = rows(); y = np.array([int(r[1]) for r in R]); src = [r[3] for r in R]
    P = predict(net, [remap(r[0]) for r in R]); am = P.argmax(1)
    cm = confusion_matrix(y, am, labels=[0, 1, 2]); cmn = cm / cm.sum(1, keepdims=True)
    groups = {}
    for s, yy, a in zip(src, y, am):
        key = s if yy == 0 else (s.split(":")[0] if yy == 1 else "filter:" + s.split(":")[1])
        groups.setdefault(key, []).append((yy, a))
    per = {k: {"n": len(v), "recall": float(np.mean([a == yy for yy, a in v]) * 100),
               "to": {CLS[c]: float(np.mean([a == c for _, a in v]) * 100) for c in range(3)}} for k, v in groups.items()}
    fig, ax = plt.subplots(figsize=(2.6, 2.3))
    ax.imshow(cmn, cmap="Blues", vmin=0, vmax=1)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{100 * cmn[i, j]:.1f}", ha="center", va="center", fontsize=8, color="white" if cmn[i, j] > 0.5 else MF.INK)
    ax.set_xticks(range(3), CLS); ax.set_yticks(range(3), CLS); ax.set_xlabel("predicted"); ax.set_ylabel("true"); ax.grid(False)
    for s_ in ax.spines.values():
        s_.set_visible(False)
    fig.tight_layout(); MF.save(fig, f"fig_confusion_{arm}")
    return {"confusion_rows_pct": (100 * cmn).round(1).tolist(), "per_source": per}


def robustness(nets, arm="MASK"):
    """FF++ test reals and fakes (300 each): recall of the true class under JPEG q, Gaussian blur sigma, downscale factor."""
    R = rows(); rng = np.random.default_rng(0)
    reals = [remap(r[0]) for r in R if r[1] == "0"]; fakes = [remap(r[0]) for r in R if r[1] == "1"]
    rng.shuffle(reals); rng.shuffle(fakes); reals, fakes = reals[:300], fakes[:300]
    ims = {"real": [np.array(Image.open(p).convert("RGB")) for p in reals], "fake": [np.array(Image.open(p).convert("RGB")) for p in fakes]}
    def jpeg(a, q):
        return cv2.imdecode(cv2.imencode(".jpg", a[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, q])[1], 1)[..., ::-1]
    def down(a, f):
        h, w = a.shape[:2]; s = cv2.resize(a, (max(8, int(w / f)), max(8, int(h / f))), interpolation=cv2.INTER_AREA); return cv2.resize(s, (w, h), interpolation=cv2.INTER_LINEAR)
    conds = [("orig", lambda a: a)] + [(f"jpeg{q}", (lambda q: lambda a: jpeg(a, q))(q)) for q in (70, 50, 30)] + \
            [(f"blur{s}", (lambda s: lambda a: cv2.GaussianBlur(a, (0, 0), s))(s)) for s in (0.8, 1.5, 2.5)] + \
            [(f"down{f}", (lambda f: lambda a: down(a, f))(f)) for f in (1.5, 2, 3)]
    out = {}
    for name, net in nets.items():
        out[name] = {}
        for cname, fn in conds:
            r = {}
            for cls, k in (("real", 0), ("fake", 1)):
                P = predict(net, [fn(a) for a in ims[cls]]); r[cls] = float((P.argmax(1) == k).mean() * 100)
                r[cls + "_called_fake"] = float((P.argmax(1) == 1).mean() * 100)
            out[name][cname] = r
            print(name, cname, r, flush=True)
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.4))
    labels = [c for c, _ in conds]
    for ax, cls in zip(axes, ("real", "fake")):
        for name in nets:
            ax.plot(range(len(labels)), [out[name][c][cls] for c in labels], marker="o", ms=3, lw=1.2, label=name,
                    color=MF.C_OURS if "HYB-D" in name else (MF.C_OURS2 if "MASK" in name or "HYB" in name else MF.C_BIN))
        ax.set_xticks(range(len(labels)), labels, rotation=40, ha="right", fontsize=7); ax.set_ylim(0, 105)
        ax.set_ylabel(f"{cls} recall (%)"); ax.grid(True, color=MF.GRID, lw=0.5)
    axes[1].legend(fontsize=7, loc="lower left"); fig.tight_layout(); MF.save(fig, f"fig_robust_{arm}")
    return out


def latency(nets, n=50):
    res = {}
    for name, (net, size) in nets.items():
        params = sum(p.numel() for p in net.parameters()) / 1e6
        x = torch.randn(1, 3, size, size)
        net_c = net.float().cpu().eval()
        with torch.no_grad():
            for _ in range(5):
                net_c(x)
            t0 = time.perf_counter()
            for _ in range(n):
                net_c(x)
            cpu_ms = (time.perf_counter() - t0) / n * 1000
        net_g = net_c.cuda(); xg = x.cuda()
        with torch.no_grad():
            for _ in range(10):
                net_g(xg)
            torch.cuda.synchronize(); t0 = time.perf_counter()
            for _ in range(n):
                net_g(xg)
            torch.cuda.synchronize(); gpu_ms = (time.perf_counter() - t0) / n * 1000
        res[name] = {"params_M": round(params, 2), "input": size, "cpu_ms": round(cpu_ms, 1), "gpu_ms": round(gpu_ms, 2)}
        print(name, res[name], flush=True)
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--arm", default="MASK"); ap.add_argument("--seed", type=int, default=20260928); a = ap.parse_args()
    CK = BASE / "checkpoints/research"
    mask = CGDNet(head=True); mask.load_state_dict(torch.load(CK / f"cgd_20260927/cgd_{a.arm}_s{a.seed}.pth", map_location="cpu")); mask = mask.cuda().eval()
    R = {"per_source": per_source(mask, a.arm)}
    def effb4(ck):
        m = timm.create_model(MODEL, pretrained=False, num_classes=3); m.load_state_dict(torch.load(ck, map_location="cpu")); return m.cuda().eval()
    class Wrap(torch.nn.Module):
        def __init__(self, m): super().__init__(); self.m = m
        def forward(self, x): return (self.m(x), None)
    hyb = Wrap(effb4(CK / "sbiscale_20260926/sbiscale_HYB_s20260927.pth")); hybd = Wrap(effb4(CK / "sbifix_20260927/sbifix_HYBD_s20260928.pth"))
    R["robustness"] = robustness({"HYB": hyb, "HYB-D": hybd, f"{a.arm} (evidence head)": mask}, a.arm)
    rep = timm.create_model("repvit_m0_9.dist_300e_in1k", pretrained=False, num_classes=3); rep.load_state_dict(torch.load(CK / "ffpp_unified_20260925/ffpp3_FLAT_repvit20.pth", map_location="cpu"))
    R["latency"] = latency({"RepViT-M0.9 (ours-S)": (rep, 224), "EfficientNet-B4 (HYB)": (hyb.m, 380), f"EfficientNet-B4 + evidence head ({a.arm})": (mask, 380)})
    json.dump(R, open(HERE / f"completeness_{a.arm}.json", "w"), indent=1); print("DONE")


if __name__ == "__main__":
    main()
