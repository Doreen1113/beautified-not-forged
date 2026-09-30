"""Score OUR checkpoints on the standard cross-dataset sets (CDFv2 518x32, DFD all-held x32).

Uses P(fake) from the 3-class softmax as the detection score (P(manipulated) also reported), frame-level AUC with a
video-cluster bootstrap CI -- the same convention as rescore_cdf_standard.py for the published detectors, so the rows
are directly comparable.

python score_ours_standard.py [--sets cdf,dfd]  -> ours_standard.json / .md
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import timm
import torch
from PIL import Image
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

BASE = Path(r"C:\My_Project\AIGC")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "results/research/ffpp_arch_20260925"))
SETS = {"cdf": BASE / "splits/research/ffpp_benchmark_20260925/celebdf_std32.txt",
        "dfd": BASE / "splits/research/ffpp_benchmark_20260925/dfd_std32.txt",
        "cdf2": BASE / "splits/research/ffpp_benchmark_20260925/celebdf_std32v2.txt",
        "dfd2": BASE / "splits/research/ffpp_benchmark_20260925/dfd_std32v2.txt"}
CK_U = BASE / "checkpoints/research/ffpp_unified_20260925"
CK_A = BASE / "checkpoints/research/ffpp_arch_20260925"
MNV4, REPVIT = "mobilenetv4_conv_small.e2400_r224_in1k", "repvit_m0_9.dist_300e_in1k"
MODELS = {
    "ours3_mnv4_10ep":   ("timm", CK_U / "ffpp3_FLAT.pth", MNV4),
    "ours3_mnv4_20ep":   ("timm", CK_U / "ffpp3_FLAT_mnv420.pth", MNV4),
    "ours3_repvit_20ep": ("timm", CK_U / "ffpp3_FLAT_repvit20.pth", REPVIT),
    "ours3_repvit_40ep": ("timm", CK_U / "ffpp3_FLAT_repvit40.pth", REPVIT),
    "fasb_SBI":          ("timm2", BASE / "checkpoints/research/fasb_20260926/fasb_SBI_repvit30.pth", REPVIT),
    "fasb_FASB0":        ("timm", BASE / "checkpoints/research/fasb_20260926/fasb_FASB0_repvit30.pth", REPVIT),
    "fasb_FASB":         ("timm", BASE / "checkpoints/research/fasb_20260926/fasb_FASB_repvit30.pth", REPVIT),
    "pfd_PLAIN":         ("timm", CK_A / "pfd_PLAIN_mnv4.pth", MNV4),
    "pfd_NOPAIR":        ("pfd", CK_A / "pfd_NOPAIR_mnv4.pth", ("mnv4", True)),
    "pfd_PFD":           ("pfd", CK_A / "pfd_PFD_mnv4.pth", ("mnv4", True)),
    "pfd_NORES":         ("pfd", CK_A / "pfd_NORES_mnv4.pth", ("mnv4", False)),
}
T = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(), transforms.Normalize([0.5] * 3, [0.5] * 3)])
SEED = 20260925


class DS(Dataset):
    def __init__(self, p):
        self.p = p

    def __len__(self):
        return len(self.p)

    def __getitem__(self, i):
        try:
            return T(Image.open(self.p[i]).convert("RGB")), i
        except Exception:
            return torch.zeros(3, 224, 224), i


def build(kind, ck, arg, dev):
    if kind in ("timm", "timm2"):
        m = timm.create_model(arg, pretrained=False, num_classes=3 if kind == "timm" else 2)
    else:
        from pfd_net import PFDNet
        m = PFDNet(arg[0], 3, use_residual=arg[1], region_head=False, pretrained=False)
    m.load_state_dict(torch.load(ck, map_location="cpu"))
    return m.to(dev).eval()


def probs(m, paths, dev):
    out = None
    dl = DataLoader(DS(paths), batch_size=128, num_workers=0)
    with torch.no_grad():
        for x, i in dl:
            pr = torch.softmax(m(x.to(dev)), 1).cpu().numpy()
            if out is None:
                out = np.zeros((len(paths), pr.shape[1]))
            out[i.numpy()] = pr
    if out.shape[1] == 2:          # binary model: pad a zero `filter` column so P(manip) == P(fake)
        out = np.concatenate([out, np.zeros((len(out), 1))], 1)
    return out


def boot(y, s, vids, n=1000):
    rng = np.random.default_rng(SEED)
    by = defaultdict(list)
    for i, v in enumerate(vids):
        by[v].append(i)
    keys = list(by); r = []
    for _ in range(n):
        idx = np.concatenate([by[keys[k]] for k in rng.choice(len(keys), len(keys), True)])
        if len(set(y[idx])) == 2:
            r.append(roc_auc_score(y[idx], s[idx]))
    return [round(float(np.percentile(r, 2.5)), 4), round(float(np.percentile(r, 97.5)), 4)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default="cdf,dfd")
    ap.add_argument("--models", default="")
    a = ap.parse_args()
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    out_p = HERE / "ours_standard.json"
    res = json.loads(out_p.read_text(encoding="utf-8")) if out_p.is_file() else {}
    data = {}
    for s in a.sets.split(","):
        if not SETS[s].is_file():
            print(f"[skip set {s}: not built yet]", flush=True); continue
        rows = [l.split("\t") for l in SETS[s].read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
        data[s] = ([r[0] for r in rows], np.array([int(r[1]) for r in rows]), [r[2] for r in rows])
        print(f"set {s}: {len(rows):,} frames / {len(set(r[2] for r in rows))} videos", flush=True)
    names = a.models.split(",") if a.models else list(MODELS)
    for name in names:
        kind, ck, arg = MODELS[name]
        if not Path(ck).is_file():
            print(f"[{name}] missing ckpt", flush=True); continue
        m = build(kind, ck, arg, dev)
        res.setdefault(name, {})
        for s, (paths, y, vids) in data.items():
            p = probs(m, paths, dev)
            s_fake, s_manip = p[:, 1], p[:, 1] + p[:, 2]
            res[name][s] = {"auc_pfake": round(float(roc_auc_score(y, s_fake)), 4),
                            "auc_pfake_ci": boot(y, s_fake, vids),
                            "auc_pmanip": round(float(roc_auc_score(y, s_manip)), 4),
                            "n": len(paths)}
            print(f"[{name}] {s}: AUC P(fake) {res[name][s]['auc_pfake']} {res[name][s]['auc_pfake_ci']}  "
                  f"P(manip) {res[name][s]['auc_pmanip']}", flush=True)
        out_p.write_text(json.dumps(res, indent=1), encoding="utf-8")
        del m; torch.cuda.empty_cache()
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
