"""Paired video-cluster bootstrap of the AUC difference between our main model (clipe4) and each strong published
detector (SBI, Effort, Forensics Adapter) on the same CDFv2 / DFD std32 frames. Needed before the paper may say that the
main model leads at video level.

python compare_sota.py [tag]  -> compare_sota_<tag>.json
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

from compare_sbi import SETS, BD, HERE, rows, vid

PUBS = ("sbi", "effort", "fadapter")


def load_pub(name, sname):
    return np.load(BD / (f"cdfstd_v2_{name}.npz" if sname == "cdf" else f"cdfstd_dfdv2_{name}.npz"))["std"]


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "clipe4_s20260929"
    rng = np.random.default_rng(0); out = {}
    for sname, f in SETS.items():
        y, v = rows(f); ours = np.load(HERE / f"{sname}_scores_{tag}.npz")["P"][:, 1]
        idx = defaultdict(list)
        for i, c in enumerate(v):
            idx[c].append(i)
        vids = sorted(idx); res = {}
        for pub in PUBS:
            other = load_pub(pub, sname); assert len(other) == len(ours)
            d_f, d_v = [], []
            for _ in range(1000):
                pick = rng.choice(len(vids), len(vids), replace=True)
                ii = np.concatenate([idx[vids[j]] for j in pick])
                vv = np.concatenate([[f"{j}_{k}"] * len(idx[vids[j]]) for k, j in enumerate(pick)])
                yy = y[ii]
                if yy.min() == yy.max():
                    continue
                d_f.append(roc_auc_score(yy, ours[ii]) - roc_auc_score(yy, other[ii]))
                ya, sa, _ = vid(yy, ours[ii], vv); yb, sb, _ = vid(yy, other[ii], vv)
                d_v.append(roc_auc_score(ya, sa) - roc_auc_score(yb, sb))
            ya, sa, _ = vid(y, ours, v); yb, sb, _ = vid(y, other, v)
            res[pub] = {"ours_frame": round(float(roc_auc_score(y, ours)), 4), "pub_frame": round(float(roc_auc_score(y, other)), 4),
                        "ours_video": round(float(roc_auc_score(ya, sa)), 4), "pub_video": round(float(roc_auc_score(yb, sb)), 4),
                        "diff_frame_CI": [round(float(np.percentile(d_f, 2.5)), 4), round(float(np.percentile(d_f, 97.5)), 4)],
                        "diff_video_CI": [round(float(np.percentile(d_v, 2.5)), 4), round(float(np.percentile(d_v, 97.5)), 4)]}
        out[sname] = res; print(sname, json.dumps(res), flush=True)
    (HERE / f"compare_sota_{tag}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
