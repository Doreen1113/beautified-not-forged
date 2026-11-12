"""Addendum 70: choose the epoch of an RU (RUNet3, EfficientNet-B4, 380 px, "half" normalisation) run on validation only,
with the same criterion as select_epoch.py (Addendum 5): C2 = 0.5 * (FF++ val macro-F1 + vendor-val balanced accuracy).
The selected epoch is copied to checkpoints/.../ru_<tag>.pth, so every evaluation script loads it under the plain tag.
python select_epoch_ru.py --tag ru7we_effb4_s20260929 --epochs 12  -> select_<tag>.json"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import f1_score, roc_auc_score

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from train_ru import CKPT  # noqa: E402
from train_ru3 import RUNet3  # noqa: E402
from eval_ru import run  # noqa: E402
from select_epoch import val_sets  # noqa: E402


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--tag", required=True); ap.add_argument("--epochs", type=int, default=12)
    ap.add_argument("--arch", default="effb4"); ap.add_argument("--size", type=int, default=380)
    a = ap.parse_args()
    ff, fy, vi, kind = val_sets(); o = kind == "original"
    print(f"FF++ val {len(ff)} | vendor val originals {int(o.sum())} renders {int((kind == 'render').sum())} components {int((kind == 'component').sum())}", flush=True)
    rows = []
    for ep in [e for e in range(1, a.epochs + 1) if (CKPT / f"ru_{a.tag}_e{e:02d}.pth").is_file()]:
        m = RUNet3(a.arch, head=True); m.load_state_dict(torch.load(CKPT / f"ru_{a.tag}_e{ep:02d}.pth", map_location="cpu"))
        m.norm = "half"; m = m.cuda().eval().to(memory_format=torch.channels_last)
        Pf = run(m, ff, a.size)[0]; pf = Pf.argmax(1); pv = run(m, vi, a.size)[0].argmax(1)
        rf = np.isin(fy, [0, 1]); auc = float(roc_auc_score((fy[rf] == 1).astype(int), Pf[rf, 1]))
        f1 = float(f1_score(fy, pf, average="macro")); sens = float((pv[~o] == 2).mean()); spec = float((pv[o] != 2).mean())
        rows.append(dict(epoch=ep, ffpp_val_macro_f1=round(f1, 4), vendor_filter_to_filter=round(100 * sens, 2),
                         vendor_orig_not_filter=round(100 * spec, 2), vendor_orig_real=round(100 * float((pv[o] == 0).mean()), 2),
                         vendor_balanced=round(50 * (sens + spec), 2), ffpp_val_auc=round(auc, 4), C2=round(0.5 * (f1 + 0.5 * (sens + spec)), 4)))
        print(json.dumps(rows[-1]), flush=True); del m; torch.cuda.empty_cache()
    best = max(rows, key=lambda r: (r["C2"], -r["epoch"]))
    shutil.copyfile(CKPT / f"ru_{a.tag}_e{best['epoch']:02d}.pth", CKPT / f"ru_{a.tag}.pth")
    (HERE / f"select_{a.tag}.json").write_text(json.dumps({"tag": a.tag, "criterion": "c2", "selected_epoch": best["epoch"], "epochs": rows}, indent=1))
    print("SELECTED", json.dumps(best), flush=True)


if __name__ == "__main__":
    main()
