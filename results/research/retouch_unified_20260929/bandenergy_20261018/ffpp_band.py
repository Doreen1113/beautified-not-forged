"""Do FF++ training forgeries carry the smoothing signature? (2026-10-21, exploratory, CPU only; written before reading results)

Hypothesis (from the 2026-10-18 band-energy analysis): detectors trained on FF++ learn 'flattened skin with kept edges inside the
face' as forgery evidence because the training forgeries carry it. Prediction: inside the face hull, forged training frames have
less relative energy in the low skin-relief band 0.02-0.12 cycles/px than genuine frames of the same source video, and the gap is
of the same sign as the change caused by bilateral smoothing; the high band (> 0.25) need not differ in the same way.
Design: FF++ c23 TRAIN split (ffpp3_train.txt), paired by source video: for each of 200 source videos (seed 0) one genuine frame
and one frame of each of the four manipulations built on that video's target (Deepfakes, Face2Face, FaceSwap, NeuralTextures,
matched by the leading video id), the same landmark hull per frame (MediaPipe on that frame). Statistic per frame: share of power
in [0.02, 0.12) and above 0.25 cycles/px (luminance, hull bounding box, Hann window, DC removed; same code as bandenergy.py),
plus mean |Laplacian| inside the hull. Report per manipulation: median paired log-ratio fake / genuine with a bootstrap CI over
videos, and the sign test. Reference: the same statistics for genuine frames under bil15 and fl06 (the smoothing forms).
python ffpp_band.py -> ffpp_band.json, FFPP_BAND.md"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
import bandenergy as BE  # noqa: E402

B = Path(r"C:\My_Project\AIGC"); LST = B / "results/research/ffpp_unified_20260925/ffpp3_train.txt"
METHODS = ["Deepfakes", "Face2Face", "FaceSwap", "NeuralTextures"]; NV = 200; RNG = np.random.default_rng(0)


def band_stats(rgb, lm):
    h, w = rgb.shape[:2]; x0, y0, x1, y1 = BE.box_of(lm, h, w); L = BE.lum(rgb)[y0:y1, x0:x1]
    if min(L.shape) < 24:
        return None
    win = np.outer(np.hanning(L.shape[0]), np.hanning(L.shape[1])).astype(np.float32); x = (L - L.mean()) * win
    P = np.abs(np.fft.fft2(x)) ** 2; P[0, 0] = 0.0
    r = np.sqrt(np.fft.fftfreq(L.shape[0])[:, None] ** 2 + np.fft.fftfreq(L.shape[1])[None, :] ** 2); tot = P.sum()
    m = BE.hull(lm, h, w); lap = np.abs(cv2.Laplacian(BE.lum(rgb), cv2.CV_32F))[m].mean()
    return {"low": float(P[(r >= 0.02) & (r < 0.12)].sum() / tot), "high": float(P[r > 0.25].sum() / tot), "lap": float(lap)}


def main():
    rows = [l.split("\t") for l in LST.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    by = defaultdict(lambda: defaultdict(list))   # target video id -> source -> paths
    for p, lab, vid, src in rows:
        if src == "real":
            by[vid]["real"].append(p)
        elif src in METHODS:
            by[vid.split("_")[0]][src].append(p)
    vids = sorted(v for v, d in by.items() if d["real"] and all(d[m] for m in METHODS))
    vids = sorted(RNG.choice(vids, min(NV, len(vids)), replace=False).tolist())
    detect = BE.landmarker(); out = {v: {} for v in vids}
    from ops import op_smooth
    for i, v in enumerate(vids):
        for src in ["real"] + METHODS:
            p = by[v][src][int(RNG.integers(0, len(by[v][src])))]
            rgb = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB); lm = detect(rgb)
            if lm is None:
                continue
            st = band_stats(rgb, lm)
            if st:
                out[v][src] = st
            if src == "real" and st:
                s15 = cv2.bilateralFilter(rgb, 15, 80, 80); out[v]["real_bil15"] = band_stats(s15, lm)
                fl = op_smooth(rgb, lm, np.random.default_rng(1), frac=0.06, mix=1.0)[0]; out[v]["real_fl06"] = band_stats(fl, lm)
        if i % 50 == 0:
            print(i, len(vids), flush=True)
    res = {}
    for comp in METHODS + ["real_bil15", "real_fl06"]:
        ok = [v for v in vids if "real" in out[v] and comp in out[v] and out[v][comp]]
        r = {}
        for k in ("low", "high", "lap"):
            d = np.array([np.log(out[v][comp][k] / out[v]["real"][k]) for v in ok])
            bs = [np.median(RNG.choice(d, len(d))) for _ in range(1000)]
            r[k] = {"median_log_ratio": round(float(np.median(d)), 4), "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)],
                    "share_below_genuine": round(float((d < 0).mean() * 100), 1), "n": len(d)}
        res[comp] = r
    (HERE / "ffpp_band.json").write_text(json.dumps(res, indent=1))
    L = ["# FF++ training forgeries vs their genuine source frames: low skin-relief band, high band, Laplacian (inside the face)", "",
         "Median paired log-ratio (forged / genuine of the same video) [95% CI over videos]; share of videos where the forged frame is lower.",
         "Negative low-band ratio = less skin relief, as under smoothing. Rows real_bil15 / real_fl06: genuine frames after our smoothing forms (reference).", "",
         "| comparison | low band 0.02-0.12 | % lower | high band > 0.25 | % lower | |Laplacian| | % lower | n |", "|---|---|---|---|---|---|---|---|"]
    for comp, r in res.items():
        L.append(f"| {comp} | {r['low']['median_log_ratio']} {r['low']['ci']} | {r['low']['share_below_genuine']} | {r['high']['median_log_ratio']} {r['high']['ci']} | {r['high']['share_below_genuine']} | {r['lap']['median_log_ratio']} {r['lap']['ci']} | {r['lap']['share_below_genuine']} | {r['low']['n']} |")
    (HERE / "FFPP_BAND.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    main()
