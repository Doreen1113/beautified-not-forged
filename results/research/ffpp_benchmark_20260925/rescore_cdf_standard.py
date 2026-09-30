"""Re-score every model on the STANDARD Celeb-DF-v2 set and quantify the protocol offset.

Prints, per model, the AUC on the old 389-frame `mp035` set next to the AUC on the standard 518-video x 32-frame set,
and the published frame-level figure where one exists. If the offset is the sampling, the standard column should land
near the published column.

python rescore_cdf_standard.py [--models a,b,c]  -> cdf_protocol_comparison.json / .md
"""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

BASE = Path(r"C:\My_Project\AIGC")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "results/research/external_baselines_20260905"))
sys.path.insert(0, str(BASE))

OLD = BASE / "splits/research/crossdataset_table_20260828/celebdf_holdout_mp035.txt"
STD = BASE / "splits/research/ffpp_benchmark_20260925/celebdf_std32.txt"
# published frame-level AUC, Forensics Adapter CVPR'25 Table I / FMSD 2026 Table I / DeepfakeBench
PUBLISHED = {"xception": 0.737, "effnb4": 0.749, "spsl": 0.765, "f3net": 0.735, "ucf": 0.753,
             "recce": 0.732, "core": 0.743, "srm": 0.755, "sbi": 0.932}   # SBI = own paper (video-level, differs)
SEED = 20260925


def read(p, has_vid):
    rows = [l.split("\t") for l in Path(p).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    paths = [r[0] for r in rows]
    y = np.array([int(r[1]) for r in rows])
    vids = [r[2] for r in rows] if has_vid else [Path(r[0]).stem for r in rows]
    return paths, y, vids


def boot_auc(y, s, vids, n=1000):
    rng = np.random.default_rng(SEED)
    by = defaultdict(list)
    for i, v in enumerate(vids):
        by[v].append(i)
    keys = list(by)
    out = []
    for _ in range(n):
        idx = np.concatenate([by[keys[k]] for k in rng.choice(len(keys), len(keys), True)])
        if len(set(y[idx])) < 2:
            continue
        out.append(roc_auc_score(y[idx], s[idx]))
    return [round(float(np.percentile(out, 2.5)), 4), round(float(np.percentile(out, 97.5)), 4)] if out else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="")
    ap.add_argument("--std", default=str(STD))
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    import zoo
    op, oy, ov = read(OLD, False)
    sp, sy, sv = read(a.std, True)
    print(f"old mp035: {len(op):,} frames / {len(set(ov)):,} videos   "
          f"standard: {len(sp):,} frames / {len(set(sv)):,} videos", flush=True)

    names = a.models.split(",") if a.models else ["xception", "effnb4", "f3net", "spsl", "sbi"]
    prev = {}
    fp = HERE / f"cdf_protocol_comparison{a.tag}.json"
    if fp.is_file():
        prev = json.loads(fp.read_text(encoding="utf-8"))
    res = dict(prev)
    for name in names:
        if name in res and "std_auc" in res[name]:
            print(f"[{name}] cached", flush=True); continue
        try:
            m = zoo.ZOO[name]() if callable(zoo.ZOO[name]) else zoo.ZOO[name]
            so = np.asarray(m.score(op), float)
            ss = np.asarray(m.score(sp), float)
        except Exception as e:
            print(f"[{name}] FAILED {type(e).__name__}: {str(e)[:100]}", flush=True)
            res[name] = {"error": f"{type(e).__name__}"}
            fp.write_text(json.dumps(res, indent=1), encoding="utf-8")
            continue
        r = {"old_mp035_auc": round(float(roc_auc_score(oy, so)), 4),
             "std_auc": round(float(roc_auc_score(sy, ss)), 4),
             "std_auc_ci": boot_auc(sy, ss, sv),
             "published_frame_auc": PUBLISHED.get(name),
             "n_old": len(op), "n_std": len(sp)}
        r["offset_old_minus_std"] = round(r["old_mp035_auc"] - r["std_auc"], 4)
        if r["published_frame_auc"]:
            r["std_minus_published"] = round(r["std_auc"] - r["published_frame_auc"], 4)
        res[name] = r
        print(f"[{name}] old {r['old_mp035_auc']:.4f} -> standard {r['std_auc']:.4f} "
              f"(offset {r['offset_old_minus_std']:+.4f}) published {r['published_frame_auc']}", flush=True)
        np.savez(HERE / f"cdfstd{a.tag}_{name}.npz", std=ss, old=so)
        fp.write_text(json.dumps(res, indent=1), encoding="utf-8")
        del m
        import torch; torch.cuda.empty_cache()

    lines = ["| model | our old 389-frame set | our standard 518x32 set [95% CI] | published frame-level | "
             "offset (old - standard) | standard - published |", "|---|---|---|---|---|---|"]
    for k, r in res.items():
        if "std_auc" not in r:
            continue
        lines.append(f"| {k} | {r['old_mp035_auc']} | {r['std_auc']} {r.get('std_auc_ci')} | "
                     f"{r.get('published_frame_auc', '—')} | {r['offset_old_minus_std']:+} | "
                     f"{r.get('std_minus_published', '—')} |")
    (HERE / f"cdf_protocol_comparison{a.tag}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n" + "\n".join(lines), flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
