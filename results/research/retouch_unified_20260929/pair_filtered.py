"""Paired video-cluster bootstrap between two of our models on a filtered source (same rule as cdf_filtered_eval.py).
python pair_filtered.py <prefix: dfd_filteredff|cdf_filteredff> A B [A B ...] -> pair_filtered.json (differences A - B)"""
import json, sys
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
HERE = Path(__file__).resolve().parent; pre = sys.argv[1]; names = sys.argv[2:]; NB = 1000
def load(n):
    z = np.load(HERE / f"{pre}_scores_{n}.npz"); return z["untreated"], z["filtered"], z["y"], z["video"]
def st(su, sf, y, idx):
    su, sf, y = su[idx], sf[idx], y[idx]; t = np.quantile(su[y == 0], 0.95); g = y == 0; k = ~g
    return np.array([roc_auc_score(y, su), roc_auc_score(y, sf), 100 * ((sf[k] <= t).mean() - (su[k] <= t).mean()), 100 * ((sf[g] > t).mean() - (su[g] > t).mean())])
f = HERE / "pair_filtered.json"; out = json.loads(f.read_text()) if f.is_file() else {}
for a, b in zip(names[::2], names[1::2]):
    A, B = load(a), load(b); v = A[3]; vids = sorted(set(v)); vix = {k: np.where(v == k)[0] for k in vids}; rng = np.random.default_rng(1)
    d = []
    for _ in range(NB):
        idx = np.concatenate([vix[vids[j]] for j in rng.choice(len(vids), len(vids), True)]); d.append(st(*A[:3], idx) - st(*B[:3], idx))
    d = np.array(d); pt = st(*A[:3], np.arange(len(v))) - st(*B[:3], np.arange(len(v)))
    r = {k: {"diff": round(float(pt[j]), 4), "ci": [round(float(np.percentile(d[:, j], q)), 4) for q in (2.5, 97.5)]} for j, k in enumerate(("auc_u", "auc_f", "d_miss", "d_fa"))}
    out[f"{pre}: {a} minus {b}"] = r; print(pre, a.replace("clipe5", ""), "-", b.replace("clipe5", ""), "| AUC_f", r["auc_f"]["diff"], r["auc_f"]["ci"], "| dMISS", r["d_miss"]["diff"], r["d_miss"]["ci"], "| dFA", r["d_fa"]["diff"], r["d_fa"]["ci"], "| AUC_u", r["auc_u"]["diff"], r["auc_u"]["ci"])
f.write_text(json.dumps(out, indent=1))
