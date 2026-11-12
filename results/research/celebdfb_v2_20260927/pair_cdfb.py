"""Paired video-cluster bootstrap of Celeb-DF-B metrics between any two detectors in scores_v3/ (same draws as fair_cdfb.py).
python pair_cdfb.py A B [A B ...]  -> prints and appends to pair_cdfb.json: AUC-b difference, beauty-only MISS-rise difference, untreated AUC difference."""
import json, sys
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
HERE = Path(__file__).resolve().parent; BASE = Path(r"C:\My_Project\AIGC"); SPLIT = BASE / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt"; NB = 1000
rows = [l.split("\t") for l in SPLIT.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
folder = np.array([r[3] for r in rows]); vid = np.array([r[2] for r in rows]); vids = sorted(set(vid)); vix = {v: np.where(vid == v)[0] for v in vids}
rng = np.random.default_rng(1); boots = [np.concatenate([vix[vids[j]] for j in rng.choice(len(vids), len(vids), True)]) for _ in range(NB)]
def stats(s, idx):
    f = folder[idx]; x = s[idx]; g = lambda k: x[f == k]; t = np.quantile(g("real"), 0.95); miss = lambda k: 100 * float((g(k) <= t).mean())
    auc = lambda a, b: float(roc_auc_score(np.r_[np.zeros(len(g(a))), np.ones(len(g(b)))], np.r_[g(a), g(b)]))
    return auc("real", "synthesis"), auc("real_beautified", "synthesis_beautified"), (miss("synthesis_beautified") - miss("synthesis")) - (miss("synthesis_compressed") - miss("synthesis"))
out = {}; f = HERE / "pair_cdfb.json"; old = json.loads(f.read_text()) if f.is_file() else {}
names = sys.argv[1:]
for a, b in zip(names[::2], names[1::2]):
    sa = np.load(HERE / "scores_v3" / f"{a}.npz")["p"][:, 1]; sb = np.load(HERE / "scores_v3" / f"{b}.npz")["p"][:, 1]
    d = np.array([np.array(stats(sa, i)) - np.array(stats(sb, i)) for i in boots]); pt = np.array(stats(sa, np.arange(len(rows)))) - np.array(stats(sb, np.arange(len(rows))))
    r = {k: {"diff": round(float(pt[j]), 4), "ci": [round(float(np.percentile(d[:, j], q)), 4) for q in (2.5, 97.5)]} for j, k in enumerate(("auc_untreated", "auc_beautified", "d_miss_beauty_only"))}
    old[f"{a} minus {b}"] = r; print(a, "minus", b, json.dumps(r))
f.write_text(json.dumps(old, indent=1))
