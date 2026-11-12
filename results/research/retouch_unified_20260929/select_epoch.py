"""Addendum 5: choose the epoch of a `--save-all` CLIP run on validation data only.

C2 = 0.5 * (FF++ val macro-F1 + vendor-val balanced accuracy), evaluation preprocessing (eval_ru.run).
Vendor val = held-out Tencent / Megvii bases: originals, renders, and the components above the noise floor.
Balanced accuracy = mean(filter items called filter, originals not called filter). Ties -> earlier epoch.

python select_epoch.py --tag clipe4r_s20260929 [--epochs 8]
  -> select_<tag>.json, checkpoints/.../ru_<tag>.pth (copy of the selected epoch)
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import f1_score

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from train_ru import UNI, CKPT, read_manifest, remap  # noqa: E402
from train_ru3 import FLOOR  # noqa: E402
from train_ru_clip import load_clip  # noqa: E402
from eval_ru import run  # noqa: E402

OPS = ["eye", "jaw", "white", "smooth"]


def val_sets():
    r = [l.split("\t") for l in (UNI / "ffpp3_val.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    ff = [(remap(x[0]), None) for x in r]; fy = np.array([int(x[1]) for x in r])
    items, kind = [], []
    for v in read_manifest(HERE / "manifest_val.tsv"):
        if v["src"] == "vendor_single":
            j = int(np.argmax(v["pres"]))
            if v["q"] is None or v["q"][j] < FLOOR[OPS[j]]:
                continue
            kind.append("component")
        elif v["src"] in ("tencent", "megvii"):
            kind.append("render")
        elif v["src"] == "ffhq_orig":
            kind.append("original")
        else:
            continue
        items.append((v["path"], v["box"]))
    return ff, fy, items, np.array(kind)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", required=True); ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--criterion", default="c2", choices=["c2", "ffpp_f1", "ffpp_auc"], help="ffpp_f1: FF++-only control (Addendum 11); ffpp_auc: binary control, which has no filter output (Addendum 9)")
    a = ap.parse_args()
    ff, fy, vi, kind = val_sets(); o = kind == "original"
    print(f"FF++ val {len(ff)} | vendor val originals {int(o.sum())} renders {int((kind == 'render').sum())} components {int((kind == 'component').sum())}", flush=True)
    rows = []
    for ep in [e for e in range(1, a.epochs + 1) if (CKPT / f"ru_{a.tag}_e{e:02d}.pth").is_file()]:   # runs with fewer epochs (Addendum 30: 2) have fewer files
        m = load_clip(f"{a.tag}_e{ep:02d}", head=True); m.norm = "clip"; m = m.cuda().eval().to(memory_format=torch.channels_last)
        Pf = run(m, ff, 224)[0]; pf = Pf.argmax(1); pv = run(m, vi, 224)[0].argmax(1)
        from sklearn.metrics import roc_auc_score
        rf = np.isin(fy, [0, 1]); auc = float(roc_auc_score((fy[rf] == 1).astype(int), Pf[rf, 1]))
        f1 = float(f1_score(fy, pf, average="macro")); sens = float((pv[~o] == 2).mean()); spec = float((pv[o] != 2).mean())
        rows.append(dict(epoch=ep, ffpp_val_macro_f1=round(f1, 4), vendor_filter_to_filter=round(100 * sens, 2),
                         vendor_orig_not_filter=round(100 * spec, 2), vendor_orig_real=round(100 * float((pv[o] == 0).mean()), 2),
                         vendor_balanced=round(50 * (sens + spec), 2), ffpp_val_auc=round(auc, 4), C2=round(0.5 * (f1 + 0.5 * (sens + spec)), 4)))
        print(json.dumps(rows[-1]), flush=True); del m; torch.cuda.empty_cache()
    key = {"c2": "C2", "ffpp_f1": "ffpp_val_macro_f1", "ffpp_auc": "ffpp_val_auc"}[a.criterion]
    best = max(rows, key=lambda r: (r[key], -r["epoch"]))
    shutil.copyfile(CKPT / f"ru_{a.tag}_e{best['epoch']:02d}.pth", CKPT / f"ru_{a.tag}.pth")
    (HERE / f"select_{a.tag}.json").write_text(json.dumps({"tag": a.tag, "criterion": a.criterion,
                                                           "selected_epoch": best["epoch"], "epochs": rows}, indent=1))
    print("SELECTED", json.dumps(best), flush=True)


if __name__ == "__main__":
    main()
