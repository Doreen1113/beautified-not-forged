"""Addendum 57: is the smoothing cue the BOUNDARY (smooth interior against textured exterior) rather than the smoothness?
Same bilateral strength inside the face hull (frac 0.12, as fl12), only the treatment of the hull edge changes:
  hard   feather sigma 0            (sharpest boundary)
  fe01   feather sigma 0.01 w       (= the fl12 form)
  fe05   feather sigma 0.05 w
  fe15   feather sigma 0.15 w       (boundary spread over most of the crop)
  whole  bilateral on the whole crop (no boundary)
  ring   smoothing only in a band at the hull edge (band width 0.10 x jaw width, feather 0.01 w); interior untouched
Frames: smooth38 (Celeb-DF-v2 test, 4,016; landmarks re-detected here). Scoring reuses smooth_probe38.score with the file
names mapped smooth38 -> bdry38.   python bdry_probe.py prep | score <name> ... | analyse"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE)); B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B))
OUT = Path(r"N:\2603055\AIGC\smooth_probe_20261016"); FORMS = ["hard", "fe01", "fe05", "fe15", "whole", "ring"]; FRAC = 0.12


def render(rgb, lm, form):
    import cv2
    from ops import hull_mask, JAW_LEFT, JAW_RIGHT
    h, w = rgb.shape[:2]; jaw_w = float(np.linalg.norm(lm[JAW_LEFT] - lm[JAW_RIGHT]))
    d = int(np.clip(round(FRAC * jaw_w), 5, 45)) | 1; sigma = float(np.clip(d * 80.0 / 15.0, 30, 160))
    sm = cv2.bilateralFilter(rgb, d, sigma, sigma)
    if form == "whole":
        return sm
    m = hull_mask(lm, h, w).astype(np.float32)
    if form == "ring":
        k = max(3, int(round(0.10 * jaw_w)) | 1); inner = cv2.erode(m, np.ones((k, k), np.uint8)); m = m - inner
    fe = {"hard": 0.0, "fe01": 0.01, "fe05": 0.05, "fe15": 0.15, "ring": 0.01}[form]
    a = cv2.GaussianBlur(m, (0, 0), max(2.0, fe * w)) if fe > 0 else m
    return np.clip(rgb * (1 - a[..., None]) + sm * a[..., None], 0, 255).astype(np.uint8)


def prep():
    import cv2
    from filters_v2.scale_normalized_filters import get_landmarks
    m = json.loads((HERE / "smooth38_list.json").read_text()); P = {"untreated": m["paths"]["untreated"]}; ok = []
    for c in FORMS:
        (OUT / f"bdry_{c}").mkdir(parents=True, exist_ok=True); P[c] = []
    for i, p in enumerate(m["paths"]["untreated"]):
        bgr = cv2.imread(p); rgb = np.ascontiguousarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)); lm = get_landmarks(rgb); ok.append(lm is not None)
        for c in FORMS:
            f = OUT / f"bdry_{c}" / f"{Path(p).stem}.png"
            if not f.is_file():
                out = render(rgb, lm, c) if lm is not None else rgb
                cv2.imwrite(str(f), cv2.cvtColor(out, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_PNG_COMPRESSION, 1])
            P[c].append(str(f))
        if i % 500 == 0:
            print(i, len(m["y"]), flush=True)
    (HERE / "bdry38_list.json").write_text(json.dumps({"paths": P, "y": m["y"], "video": m["video"], "lm_ok": ok})); print("prep done", sum(ok))


def score(names):
    import smooth_probe38 as S
    base = type(S.HERE)

    class Mapped(base):
        def __truediv__(self, k):
            return base.__truediv__(self, str(k).replace("smooth38", "bdry38"))
    S.HERE = Mapped(str(S.HERE)); S.FORMS = list(FORMS); S.DOSE = []
    for n in names:
        S.score(n)


def analyse():
    from sklearn.metrics import roc_auc_score
    import smooth_probe38 as S
    m = json.loads((HERE / "bdry38_list.json").read_text()); y = np.array(m["y"]); ok = np.array(m["lm_ok"])
    names = [n for n in S.PUB + list(S.OURS) if (HERE / f"bdry38_{n}.npz").is_file()]; rows = {}
    for n in names:
        z = np.load(HERE / f"bdry38_{n}.npz"); u = z["untreated"].astype(float); g0 = ok & (y == 0); t = np.nanquantile(u[g0], 0.95); r = {}
        for c in ["untreated"] + FORMS:
            s = z[c].astype(float); k = ok & ~np.isnan(s)
            r[c] = {"fa": round(float((s[k & (y == 0)] > t).mean() * 100), 1), "auc_both": round(float(roc_auc_score(y[k], s[k])), 4)}
        rows[n] = r
    face = [n for n in names if n in S.PUB and n not in ("univfd", "npr")]
    mono = sum(rows[n]["hard"]["fa"] >= rows[n]["fe01"]["fa"] >= rows[n]["fe05"]["fa"] >= rows[n]["fe15"]["fa"] for n in face)
    ring = sum(rows[n]["ring"]["fa"] >= 0.7 * rows[n]["fe01"]["fa"] for n in face)
    whole_lt = sum(rows[n]["whole"]["fa"] < rows[n]["fe01"]["fa"] - 10 for n in face)
    res = {"rows": rows, "pred1_monotone_hard_to_fe15": f"{mono}/{len(face)}", "pred2_ring_at_least_70pct_of_fe01": f"{ring}/{len(face)}", "pred3_whole_below_fe01_by_10": f"{whole_lt}/{len(face)}"}
    (HERE / "bdry38.json").write_text(json.dumps(res, indent=1))
    L = ["# Addendum 57: boundary vs smoothness (same bilateral strength inside the hull; only the edge treatment changes)", "",
         f"Predictions: (1) FA monotone hard >= fe01 >= fe05 >= fe15: {res['pred1_monotone_hard_to_fe15']} face detectors (bar >= 10/15); "
         f"(2) ring-only FA >= 70 % of fe01 FA: {res['pred2_ring_at_least_70pct_of_fe01']} (bar >= 10/15); (3) whole-crop below fe01 by >= 10 points: {res['pred3_whole_below_fe01_by_10']}", "",
         "Cell: FA % of smoothed genuine frames at the untreated 5 % FPR threshold | AUC with both classes treated", "",
         "| detector | " + " | ".join(["untreated"] + FORMS) + " |", "|---" * (len(FORMS) + 2) + "|"]
    for n, r in rows.items():
        L.append(f"| {n} | " + " | ".join(f"{r[c]['fa']} \\| {r[c]['auc_both']}" for c in ["untreated"] + FORMS) + " |")
    (HERE / "BDRY38.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    {"prep": lambda: prep(), "score": lambda: score(sys.argv[2:]), "analyse": lambda: analyse()}[sys.argv[1]]()
