"""Addendum 54: GPUPixel smoothing forms on the smooth38 frames; scoring reuses smooth_probe38.score with its file names mapped
smooth38 -> gpx38.  python gpx_probe.py prep | score <name> ... | analyse"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
OUT = Path(r"N:\2603055\AIGC\smooth_probe_20261016"); GFORMS = {"gpx0": 0.0, "gpx3": 0.3, "gpx6": 0.6, "gpx9": 0.9}


def prep():
    import cv2
    import gpupixel_port as G
    m = json.loads((HERE / "smooth38_list.json").read_text()); P = {"untreated": m["paths"]["untreated"]}
    for c, a in GFORMS.items():
        (OUT / c).mkdir(parents=True, exist_ok=True); P[c] = []
        for i, p in enumerate(m["paths"]["untreated"]):
            f = OUT / c / f"{Path(p).stem}.png"
            if not f.is_file():
                rgb = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB)
                cv2.imwrite(str(f), cv2.cvtColor(G.beauty_at_scale(rgb, a), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_PNG_COMPRESSION, 1])
            P[c].append(str(f))
            if i % 1000 == 0:
                print(c, i, flush=True)
    (HERE / "gpx38_list.json").write_text(json.dumps({"paths": P, "y": m["y"], "video": m["video"], "lm_ok": m["lm_ok"]})); print("prep done")


def score(names):
    import smooth_probe38 as S
    base = type(S.HERE)

    class Mapped(base):
        def __truediv__(self, k):
            return base.__truediv__(self, str(k).replace("smooth38", "gpx38"))
    S.HERE = Mapped(str(S.HERE)); S.FORMS = list(GFORMS); S.DOSE = []
    for n in names:
        S.score(n)


def analyse():
    from sklearn.metrics import roc_auc_score
    from scipy.stats import spearmanr
    m = json.loads((HERE / "gpx38_list.json").read_text()); y = np.array(m["y"]); ok = np.array(m["lm_ok"])
    import smooth_probe38 as S
    names = [n for n in S.PUB + list(S.OURS) if (HERE / f"gpx38_{n}.npz").is_file()]
    conds = ["untreated"] + list(GFORMS); rows = {}
    for n in names:
        z = np.load(HERE / f"gpx38_{n}.npz"); u = z["untreated"].astype(float); t = np.nanquantile(u[(y == 0) & ok], 0.95); r = {}
        for c in conds:
            s = z[c].astype(float); k = ok & ~np.isnan(s); g = s[k & (y == 0)]; f = s[k & (y == 1)]
            rt = np.quantile(g, 0.95)
            r[c] = {"fa": round(float((g > t).mean() * 100), 1), "miss": round(float((f <= t).mean() * 100), 1), "auc": round(float(roc_auc_score(y[k], s[k])), 4),
                    "recal_miss": round(float((f <= rt).mean() * 100), 1)}
        rows[n] = r
    face = [n for n in names if n in S.PUB and n not in ("univfd", "npr")]
    p1 = sum(rows[n]["gpx9"]["fa"] > 15 for n in face)
    p2 = sum(rows[n]["untreated"]["auc"] >= rows[n]["gpx3"]["auc"] >= rows[n]["gpx6"]["auc"] >= rows[n]["gpx9"]["auc"] for n in face)
    s38 = {n: np.load(HERE / f"smooth38_{n}.npz") for n in face}
    def fa38(n):
        z = s38[n]; u = z["untreated"].astype(float); t = np.nanquantile(u[(y == 0) & ok], 0.95); g = z["bil15"].astype(float)[(y == 0) & ok]; return float((g > t).mean())
    rho = spearmanr([rows[n]["gpx9"]["fa"] for n in face], [fa38(n) for n in face]).correlation
    res = {"rows": rows, "pred1_n_face_fa_gt15": f"{p1}/{len(face)}", "pred2_n_monotone": f"{p2}/{len(face)}", "pred3_spearman_vs_bil15": round(float(rho), 3)}
    (HERE / "gpx38.json").write_text(json.dumps(res, indent=1))
    L = [f"# Addendum 54: GPUPixel smoothing (camera scale) on Celeb-DF-v2 smooth38 frames", "",
         f"Prediction (1) gpx9 FA > 15% at untreated threshold: {res['pred1_n_face_fa_gt15']} face detectors (need >= 10/15); (2) AUC monotone: {res['pred2_n_monotone']} (need >= 12/15); (3) Spearman vs bil15 FA: {res['pred3_spearman_vs_bil15']} (need >= 0.5)", "",
         "Cell: FA% / miss% at the untreated 5% FPR threshold | AUC both smoothed | recalibrated miss%", "", "| detector | " + " | ".join(conds) + " |", "|---" * (len(conds) + 1) + "|"]
    for n, r in rows.items():
        L.append(f"| {n} | " + " | ".join(f"{r[c]['fa']} / {r[c]['miss']} \| {r[c]['auc']} \| {r[c]['recal_miss']}" for c in conds) + " |")
    (HERE / "GPX38.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    {"prep": lambda: prep(), "score": lambda: score(sys.argv[2:]), "analyse": lambda: analyse()}[sys.argv[1]]()
