"""Addendum 2 secondary analysis: threshold t* on p(filter) chosen on the vendor validation split only (max balanced accuracy,
originals vs composites+components), applied unchanged to Alibaba; plus threshold-free Alibaba AUROC.
python val_threshold.py -> val_threshold.json"""
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
OPS = ["EyeEnlarging", "FaceLifting", "Whitening", "Smoothing"]


def decide(P, t):
    am = P.argmax(1); out = np.where(P[:, 2] >= t, 2, 0); out[am == 1] = 1; return out


def main():
    res = {}
    tags = sorted(f.stem.replace("vendor_val_scores_", "") for f in HERE.glob("vendor_val_scores_*.npz") if (HERE / f"ali_scores_{f.stem.replace('vendor_val_scores_', '')}.npz").is_file())
    for tag in tags:
        v = np.load(HERE / f"vendor_val_scores_{tag}.npz"); P, src = v["P"], v["src"]
        neg = src == "ffhq_orig"; pos = np.isin(src, ["tencent", "megvii", "vendor_single"])
        ts = np.unique(np.quantile(P[neg | pos, 2], np.linspace(0, 1, 2001)))
        bal = [((decide(P[pos], t) == 2).mean() + (decide(P[neg], t) != 2).mean()) / 2 for t in ts]
        t = float(ts[int(np.argmax(bal))])
        a = np.load(HERE / f"ali_scores_{tag}.npz"); Pa, g = a["P"], a["group"]; o = g == "orig_0"
        d = decide(Pa, t); spec = float((d[o] != 2).mean() * 100); sens = float((d[~o] == 2).mean() * 100)
        r = {"t_star": round(t, 4), "vendor_val_balanced": round(float(max(bal)) * 100, 2),
             "ali_balanced": round((spec + sens) / 2, 2), "ali_orig_to_filter": round(100 - spec, 2), "ali_ret_to_filter": round(sens, 2),
             "ali_ret_to_fake": round(float((d[~o] == 1).mean() * 100), 2), "ali_orig_to_fake": round(float((d[o] == 1).mean() * 100), 2),
             "ali_auroc_pfilter": round(float(roc_auc_score((~o).astype(int), Pa[:, 2])), 4),
             "per_op_to_filter": {op: round(float((d[np.char.startswith(g.astype(str), op)] == 2).mean() * 100), 1) for op in OPS},
             "argmax_balanced": None}
        am = Pa.argmax(1); r["argmax_balanced"] = round(((am[~o] == 2).mean() * 100 + (am[o] != 2).mean() * 100) / 2, 2)
        r["bar_secondary_balanced>=75"] = r["ali_balanced"] >= 75
        res[tag] = r; print(tag, json.dumps(r))
    (HERE / "val_threshold.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
