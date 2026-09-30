"""After score_sota.py: add Effort / Forensics Adapter to the benchmark JSONs the paper tables read, with the same
definitions as run_benchmark.py (P(fake) at 5 % clean-real FPR; FA = filter frames called fake, MISS = escape frames called real),
and recompute B1 dominance for every RU model against the enlarged detector set.

python add_sota_bench.py
"""
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

B = Path(r"C:\My_Project\AIGC"); R = B / "results/research"; BD = R / "ffpp_benchmark_20260925"
SP = B / "splits/research/ffpp_benchmark_20260925"
PARAMS = {"effort": 303.4, "fadapter": 309.7}   # parameters used in the forward pass (README_setup.md)


def ci(fn, arr, n=1000, seed=1):
    rng = np.random.default_rng(seed); v = [fn(arr[rng.integers(0, len(arr), len(arr))]) for _ in range(n)]
    return [round(float(np.percentile(v, 2.5)), 2), round(float(np.percentile(v, 97.5)), 2)]


def main():
    bench = json.loads((BD / "benchmark_final.json").read_text())
    cdf = json.loads((BD / "cdf_protocol_comparison_v2.json").read_text()); dfd = json.loads((BD / "cdf_protocol_comparison_dfdv2.json").read_text())
    for d in ("effort", "fadapter"):
        z = np.load(BD / f"scores_{d}.npz"); sr, sf, sl, se = z["real"], z["fake"], z["filter"], z["escape"]
        t = float(np.quantile(sr, 0.95))
        bench[d] = {"params_M": PARAMS[d], "FA": round(float((sl > t).mean() * 100), 2), "MISS": round(float((se <= t).mean() * 100), 2),
                    "clean_fake_recall": round(float((sf > t).mean() * 100), 2),
                    "auroc_real_vs_fake": round(float(roc_auc_score(np.r_[np.zeros(len(sr)), np.ones(len(sf))], np.r_[sr, sf])), 4),
                    "auroc_real_vs_filter": round(float(roc_auc_score(np.r_[np.zeros(len(sr)), np.ones(len(sl))], np.r_[sr, sl])), 4),
                    "rule": "P(fake) at 5% clean-real FPR", "FA_ci": ci(lambda a: (a > t).mean() * 100, sl), "MISS_ci": ci(lambda a: (a <= t).mean() * 100, se),
                    "threshold": round(t, 4), "note": "official weights, authors' preprocessing, our frames; frame-level bootstrap CI"}
        for nm, js, lst in (("cdf", cdf, "celebdf_std32v2.txt"), ("dfd", dfd, "dfd_std32v2.txt")):
            y = np.array([int(l.split("\t")[1]) for l in (SP / lst).read_text(encoding="utf-8").splitlines()[1:] if l.strip()])
            s = np.load(BD / (f"cdfstd_v2_{d}.npz" if nm == "cdf" else f"cdfstd_dfdv2_{d}.npz"))["std"]
            js[d] = {"std_auc": round(float(roc_auc_score(y, s)), 4), "n_std": int(len(y)), "note": "official weights, our frames"}
        print(d, bench[d]["FA"], bench[d]["MISS"], cdf[d]["std_auc"], dfd[d]["std_auc"])
    (BD / "benchmark_final.json").write_text(json.dumps(bench, indent=1))
    (BD / "cdf_protocol_comparison_v2.json").write_text(json.dumps(cdf, indent=1)); (BD / "cdf_protocol_comparison_dfdv2.json").write_text(json.dumps(dfd, indent=1))
    # B1 dominance for RU models against the enlarged set
    def curve(sr, sl, se):
        ts = np.unique(np.concatenate([sr, sl, se])); ts = ts[::max(1, len(ts) // 3000)]
        return np.array([(sl > t).mean() * 100 for t in ts]), np.array([(se <= t).mean() * 100 for t in ts])
    curves = {}
    for b in ["xception", "effnb4", "spsl", "f3net", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter", "univfd", "npr"]:
        z = np.load(BD / f"scores_{b}.npz"); curves[b] = curve(z["real"], z["filter"], z["escape"])
    for nm, fp in (("SBI-L", R / "sbiscale_20260926/scores_SBI-L.npz"), ("SBI-F", R / "sbifix_20260927/scores_SBI-F.npz")):
        z = np.load(fp); curves[nm] = curve(z["real"], z["filter"], z["escape"])
    for f in sorted((R / "retouch_unified_20260929").glob("eval_ru_*.json")):
        J = json.loads(f.read_text()); r = J.get("ffpp")
        if not r:
            continue
        r["b1_dominated_by"] = [b for b, (FA, MS) in curves.items() if ((FA <= r["FA"]) & (MS <= r["MISS"])).any()]; r["b1_n_detectors"] = len(curves)
        f.write_text(json.dumps(J, indent=1)); print(f.name, "dominated by", r["b1_dominated_by"], "of", len(curves))


if __name__ == "__main__":
    main()
