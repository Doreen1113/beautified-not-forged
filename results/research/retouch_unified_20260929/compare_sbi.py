"""RU vs official SBI (and MASK / MASK-D) on the SAME CDFv2 / DFD std32 frames: frame AUC, video AUC, paired video-cluster
bootstrap of the AUC difference (1,000 resamples). python compare_sbi.py <tag...>  -> compare_sbi.json"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

B = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent
SP = B / "splits/research/ffpp_benchmark_20260925"; BD = B / "results/research/ffpp_benchmark_20260925"
SETS = {"cdf": "celebdf_std32v2.txt", "dfd": "dfd_std32v2.txt"}


def rows(f):
    r = [l.split("\t") for l in (SP / f).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return np.array([int(x[1]) for x in r]), np.array([x[2] for x in r])


def vid(y, s, v):
    by = defaultdict(list); yy = {}
    for a, b, c in zip(y, s, v):
        by[c].append(b); yy[c] = a
    k = list(by); return np.array([yy[x] for x in k]), np.array([np.mean(by[x]) for x in k]), k


def sbi_scores(name):
    f = BD / (f"cdfstd_{name}.npz" if name == "cdf" else f"cdfstd_dfdv2_{name}.npz")
    return None


def load_sbi(sname):
    f = BD / ("cdfstd_v2_sbi.npz" if sname == "cdf" else "cdfstd_dfdv2_sbi.npz")   # v2 = the std32v2 frame list (the v1 file has the same length, different frames)
    return np.load(f)["std"]


def main():
    tags = sys.argv[1:] or ["effb4_s20260929"]
    out = {}
    rng = np.random.default_rng(0)
    for sname, f in SETS.items():
        y, v = rows(f); sbi = load_sbi(sname)
        models = {"SBI": sbi}
        for t in tags:
            models[f"RU {t}"] = np.load(HERE / f"{sname}_scores_{t}.npz")["P"][:, 1]
        for nm, p in (("MASK", BD / f"ours_frames_MASK_{sname}.npz"),):
            if p.is_file():
                models[nm] = np.load(p)["p"][:, 1]
        vids = sorted(set(v)); idx = defaultdict(list)
        for i, c in enumerate(v):
            idx[c].append(i)
        res = {}
        for nm, s in models.items():
            yv, sv, _ = vid(y, s, v)
            res[nm] = {"frame": round(float(roc_auc_score(y, s)), 4), "video": round(float(roc_auc_score(yv, sv)), 4)}
        # paired bootstrap of RU - SBI (frame and video)
        for t in tags:
            nm = f"RU {t}"; d_f, d_v = [], []
            for _ in range(1000):
                ks = rng.choice(len(vids), len(vids), replace=True); ii = np.concatenate([idx[vids[k]] for k in ks])
                if len(set(y[ii])) < 2:
                    continue
                d_f.append(roc_auc_score(y[ii], models[nm][ii]) - roc_auc_score(y[ii], sbi[ii]))
                yv1, sv1, _ = vid(y[ii], models[nm][ii], np.array([f"{v[i]}#{j}" for j, i in enumerate(ii)]) if False else v[ii])
                yv2, sv2, _ = vid(y[ii], sbi[ii], v[ii])
                d_v.append(roc_auc_score(yv1, sv1) - roc_auc_score(yv2, sv2))
            res[nm]["minus_SBI_frame_CI"] = [round(float(np.percentile(d_f, 2.5)), 4), round(float(np.percentile(d_f, 97.5)), 4)]
            res[nm]["minus_SBI_video_CI"] = [round(float(np.percentile(d_v, 2.5)), 4), round(float(np.percentile(d_v, 97.5)), 4)]
        out[sname] = res; print(sname, json.dumps(res), flush=True)
    json.dump(out, open(HERE / "compare_sbi.json", "w"), indent=1)


if __name__ == "__main__":
    main()
