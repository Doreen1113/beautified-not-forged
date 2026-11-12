"""Per-filter AUC on the held-out filter sets (Celeb-DF-v2 + 11 colour filters, DFD + 16 fresh filters), from the frame
scores already written by results/research/retouch_unified_20260929 (cdf|dfd_filteredff_scores_<detector>.npz: untreated and
filtered scores, labels, the filter applied to each frame). No model is run here. Frame AUC on the filtered frames of each
filter (genuine and forged frames of the videos that received it), and the untreated AUC of the same frames.
python docs/meeting_20261103/per_filter_auc.py  -> per_filter_auc.json"""
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

RU = Path(r"C:\My_Project\AIGC\results\research\retouch_unified_20260929"); H = Path(__file__).resolve().parent
DET = [("clipe5_s20260929", "Ours s1"), ("clipe5_s20260930", "Ours s2"), ("clipe5f_s20260929", "Ours, FF++ only"),
       ("effort", "Effort"), ("fadapter", "Forensics Adapter"), ("gend", "GenD"), ("dfdhr", "DFD-HR"), ("sbi", "SBI"), ("caddm", "CADDM")]
out = {}
for ds in ("cdf", "dfd"):
    out[ds] = {}
    for key, name in DET:
        z = np.load(RU / f"{ds}_filteredff_scores_{key}.npz", allow_pickle=True)
        y, f, u, filt = z["y"], z["filtered"], z["untreated"], z["filt"]
        row = {"all": {"auc_f": round(float(roc_auc_score(y, f)), 4), "auc_u": round(float(roc_auc_score(y, u)), 4), "n": int(len(y))}}
        for k in sorted(set(filt.tolist())):
            m = filt == k
            if len(set(y[m].tolist())) < 2:
                continue
            row[k] = {"auc_f": round(float(roc_auc_score(y[m], f[m])), 4), "auc_u": round(float(roc_auc_score(y[m], u[m])), 4),
                      "n": int(m.sum()), "n_fake": int(y[m].sum())}
        out[ds][name] = row
(H / "per_filter_auc.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
for ds in out:
    names = list(out[ds]); filters = [k for k in out[ds][names[0]] if k != "all"]
    print(f"== {ds}: {len(filters)} filters")
    print("filter".ljust(14) + "".join(n[:10].rjust(11) for n in names))
    for k in filters + ["all"]:
        print(k.ljust(14) + "".join(f"{out[ds][n][k]['auc_f']:.3f}".rjust(11) if k in out[ds][n] else " " * 11 for n in names))
