"""fig_evidence: held-out part edits with GT footprint, evidence head map, Score-CAM on HYBPE, and the restored
counterfactual (CGD region restored) with the model's decision on it.

python docs/paper_v2/make_fig_evidence.py                 (runs the two models, caches the tiles in figs/fig_evidence_tiles.npz, draws)
python docs/paper_v2/make_fig_evidence.py --render-only   (redraws from the cache)
Drawing: shared style docs/paper_v2/figstyle.py (same overlays as docs/capstone/paper/src/make_fig_evidence_vs_gradcam.py): true footprint
in blue (dashed on the map panels), the region cut from the evidence map (the one that is restored) in yellow.
"""
import json
import sys
from pathlib import Path

import cv2
import matplotlib
import numpy as np
import torch

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BASE = Path(r"C:\My_Project\AIGC")
sys.path.insert(0, str(BASE / "docs/paper_v2")); sys.path.insert(0, str(BASE / "results/research/cgd_20260927"))
import make_figures as MF  # noqa: E402
import figstyle as FS  # noqa: E402
FS.apply()   # after make_figures, which sets its own rcParams on import
from eval_cgd_explain import CAM, TF, SIZE, dilate_t, footprint_gt, load_items, region_from_map  # noqa: E402
from train_cgd import CGDNet  # noqa: E402
from PIL import Image  # noqa: E402

CK = BASE / "checkpoints/research/cgd_20260927"
CLS = ["real", "fake", "filter"]
MECH = {"donor": "donor", "sd": "SD-1.5"}
CACHE = BASE / "docs/paper_v2/figs/fig_evidence_tiles.npz"


def load(arm):
    n = CGDNet(head=arm != "HYBPE"); n.load_state_dict(torch.load(CK / f"cgd_{arm}_s20260928.pth", map_location="cpu")); return n.cuda().eval()


def heat(im, m, alpha=0.45):
    hm = cv2.applyColorMap((np.clip(m, 0, 1) * 255).astype(np.uint8), cv2.COLORMAP_JET)[..., ::-1]
    return ((1 - alpha) * im + alpha * hm).astype(np.uint8)


def main():
    cgd, hyb = load("MASK"), load("HYBPE"); cam = CAM(hyb)
    rng = np.random.default_rng(11)
    picks = []
    for mech in ("donor", "sd"):
        items = load_items([mech]); rng.shuffle(items)
        for it in items:
            if it["part"] in [p["part"] for p in picks if p["mech"] == mech]:
                continue
            with torch.no_grad():   # keep the figure consistent with the table: correctly detected items only
                pp = torch.softmax(cgd(TF(Image.open(it["x"]).convert("RGB"))[None].cuda())[0], 1)[0]
                if pp.argmax().item() != 1 or pp[1].item() < 0.7:   # detected with margin; borderline cases are in the table
                    continue
            picks.append(it)
            if sum(p["mech"] == mech for p in picks) == 1:
                break
    T = {k: [] for k in ("img", "gt", "ev", "reg", "sc", "rest", "p", "pr", "label")}
    for it in picks:
        im = Image.open(it["x"]).convert("RGB"); im0 = Image.open(it["x0"]).convert("RGB").resize(im.size)
        x, x0 = TF(im)[None].cuda(), TF(im0)[None].cuda()
        gt = footprint_gt(im, im0); area = gt.mean().item()
        with torch.no_grad():
            lo, ev = cgd(x); p = torch.softmax(lo, 1)[0].cpu().numpy()
            e = torch.sigmoid(ev[0, 0]).float(); reg0 = region_from_map(e, area); reg = dilate_t(reg0)
            xr = (1 - reg[None, None]) * x + reg[None, None] * x0
            pr = torch.softmax(cgd(xr)[0], 1)[0].cpu().numpy()
        sc = cam.scorecam(x, 1)
        e_up = torch.nn.functional.interpolate(e[None, None], size=(SIZE, SIZE), mode="bilinear")[0, 0].cpu().numpy()
        sc_up = cv2.resize((sc / (sc.max() + 1e-8)).cpu().numpy(), (SIZE, SIZE))
        rest = ((xr[0].cpu().permute(1, 2, 0).numpy() * 0.5 + 0.5) * 255).clip(0, 255).astype(np.uint8)
        for k, v in (("img", np.array(im.resize((SIZE, SIZE)))), ("gt", gt.cpu().numpy()), ("ev", np.clip(e_up, 0, 1)),   # sigmoid map drawn as is (as before)
                     ("reg", reg0.cpu().numpy()), ("sc", np.clip(sc_up, 0, 1)), ("rest", rest), ("p", p), ("pr", pr),
                     ("label", f"{MECH[it['mech']]}, {it['part']}")):
            T[k].append(v)
    np.savez_compressed(CACHE, **{k: np.stack(v) if k != "label" else np.array(v) for k, v in T.items()})
    json.dump([{k: str(v) for k, v in p.items()} for p in picks], open(MF.OUT / "fig_evidence_items.json", "w"), indent=1)


def render():
    """2 x 5 grid at final size (5.0 in wide in the supplement): same overlays as the capstone evidence figure (figstyle)."""
    z = np.load(CACHE); n = len(z["img"])
    heads = ["input", "true footprint", "evidence map (ours)", "Score-CAM (no head)", "region restored"]
    W, lm, gap, hgap, top = 5.0, 0.17, 0.05, 0.2, 0.17
    tw = (W - lm - 4 * gap - 0.01) / 5; H = top + n * tw + (n - 1) * hgap + 0.17
    fig = plt.figure(figsize=(W, H))
    for r in range(n):
        y0 = H - top - (r + 1) * tw - r * hgap
        img, gt, p, pr = z["img"][r], z["gt"][r], z["p"][r], z["pr"][r]
        for c in range(5):
            ax = fig.add_axes([(lm + c * (tw + gap)) / W, y0 / H, tw / W, tw / H]); FS.frame(ax, color=FS.MUTED, lw=0.4)
            if c == 0:
                ax.imshow(img); ax.set_ylabel(str(z["label"][r]), fontsize=FS.FS_NOTE, labelpad=2)
            elif c == 1:
                FS.footprint(ax, img, gt)
            elif c == 2:
                ax.imshow(FS.overlay(img, z["ev"][r])); FS.footprint(ax, None, gt, fill=False); FS.region(ax, z["reg"][r])
                d = int(p.argmax()); ax.set_xlabel(f"{CLS[d]} {p.max():.2f}", fontsize=FS.FS_NOTE, labelpad=1.5, color=FS.ERR if d == 1 else FS.OK)
            elif c == 3:
                ax.imshow(FS.overlay(img, z["sc"][r])); FS.footprint(ax, None, gt, fill=False)
            else:
                ax.imshow(z["rest"][r]); FS.region(ax, z["reg"][r])
                d = int(pr.argmax()); ax.set_xlabel(f"→ {CLS[d]} {pr.max():.2f}", fontsize=FS.FS_NOTE, labelpad=1.5, color=FS.ERR if d == 1 else FS.OK)
            if r == 0:
                ax.set_title(heads[c], fontsize=FS.FS_NOTE, pad=3)
    FS.save(fig, MF.OUT / "fig_evidence")
    print("fig_evidence done", [(str(l), CLS[int(a.argmax())], round(float(a.max()), 2), CLS[int(b.argmax())], round(float(b.max()), 2))
                                for l, a, b in zip(z["label"], z["p"], z["pr"])])


if __name__ == "__main__":
    if "--render-only" not in sys.argv:
        main()
    render()
