"""In-vendor held-out evaluation (Tencent / Megvii validation base indices, never trained): routing of originals, composites
and single-operation components, per-op presence TP / same-image TN on components, and Spearman of the blind quantity vs
the measured one on components. Separates "cannot read single operations" from "cannot cross vendors".

python eval_vendor_val.py --arch effb4 [--arm ru1|ru2]  -> vendor_val_<tag>.json
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from train_ru import RUNet, ARCH, CKPT, read_manifest  # noqa: E402
from eval_ru import run  # noqa: E402
OPS = ["eye", "jaw", "white", "smooth"]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--arch", default="effb4"); ap.add_argument("--arm", default="ru1")
    ap.add_argument("--seed", type=int, default=20260929); a = ap.parse_args()
    tag = f"{a.arch}_s{a.seed}" if a.arm == "ru1" else f"{a.arm}_{a.arch}_s{a.seed}"; size = ARCH[a.arch][1]
    if a.arm in ("clip", "clipe", "clipe4"):
        from train_ru_clip import load_clip
        tag = f"{a.arm}_s{a.seed}"; size = 224; m = load_clip(tag, head=a.arm != "clip"); m.norm = "clip"
    elif a.arm in ("ru3", "ru3e", "ru4e"):   # RUNet3 shares the RUNet interface (cls, pres, q [, ev]); drop the evidence map
        from train_ru3 import RUNet3
        inner = RUNet3(a.arch, head=a.arm.endswith("e")); inner.load_state_dict(torch.load(CKPT / f"ru_{tag}.pth", map_location="cpu"))
        class _W(torch.nn.Module):
            def __init__(s, m): super().__init__(); s.m = m
            def forward(s, x): return s.m(x)[:3]
        m = _W(inner)
    else:
        m = RUNet(a.arch); m.load_state_dict(torch.load(CKPT / f"ru_{tag}.pth", map_location="cpu"))
    m = m.cuda().eval().to(memory_format=torch.channels_last)
    rows = read_manifest(HERE / "manifest_val.tsv")
    P, R, Q = run(m, [(r["path"], r["box"]) for r in rows], size)
    am = P.argmax(1); src = np.array([r["src"] for r in rows]); out = {"tag": tag}
    for s in ("ffhq_orig", "tencent", "megvii", "vendor_single"):
        k = src == s
        out[s] = {"n": int(k.sum()), **{c: round(float((am[k] == i).mean() * 100), 2) for i, c in enumerate(["real", "fake", "filter"])}}
    comp = np.where(src == "vendor_single")[0]
    op_of = np.array([int(np.argmax(rows[i]["pres"])) for i in comp])
    vend = np.array(["megvii" if "megvii" in rows[i]["path"] else "tencent" for i in comp])
    out["components"] = {}
    for j, op in enumerate(OPS):
        for v in ("tencent", "megvii"):
            k = comp[(op_of == j) & (vend == v)]
            if len(k) == 0:
                continue
            pres = R[k] >= 0.5; others = [t for t in range(4) if t != j]
            meas = np.array([rows[i]["q"][j] for i in k]); pred = Q[k, j]
            out["components"][f"{v}_{op}"] = {"n": int(len(k)), "to_filter": round(float((am[k] == 2).mean() * 100), 2),
                                               "to_real": round(float((am[k] == 0).mean() * 100), 2), "TP": round(float(pres[:, j].mean()), 3),
                                               "TN_same_image": round(float((~pres[:, others]).all(1).mean()), 3),
                                               "spearman": round(float(spearmanr(pred, meas).correlation), 3),
                                               "pred_mean": round(float(pred.mean()), 4), "meas_mean": round(float(meas.mean()), 4)}
    np.savez(HERE / f"vendor_val_scores_{tag}.npz", P=P, src=src)
    (HERE / f"vendor_val_{tag}.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
