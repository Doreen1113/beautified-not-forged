"""Addendum 64: remote photoplethysmography (rPPG) under real app presets, Celeb-DF-B. Zero training.
  python cdfb_rppg_probe.py extract   -> cdfb_rppg_traces.npz  (per video: 300 x 3 mean-RGB trace of the cheek+forehead ROI, detect rate)
  python cdfb_rppg_probe.py analyse   -> cdfb_rppg.json, CDFB_RPPG.md
ROI: MediaPipe FaceLandmarker (478 points); left cheek, right cheek and forehead polygons from fixed landmark indices; the
per-frame score is the mean RGB inside the union. POS (Wang et al., IEEE TBME 2017) with 1.6-s windows and overlap-add,
band-pass 0.7-3 Hz, SNR in dB (de Haan & Jeanne 2013 definition). Forgery score = -SNR. Rule and bootstrap as cdfb_id_probe.py."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent; B = HERE.parents[2]
VID = B / "external_data/celebdfb/Celeb-DF-B"
FOLDERS = ["real", "real_beautified", "real_compressed", "synthesis", "synthesis_beautified", "synthesis_compressed"]
N_FRAMES = 300; FPS = 30.0
# MediaPipe face-mesh polygons (canonical 468 indexing): cheeks and forehead, eyes and mouth excluded
LEFT_CHEEK = [50, 101, 118, 123, 147, 187, 207, 206, 203]
RIGHT_CHEEK = [280, 330, 347, 352, 376, 411, 427, 426, 423]
FOREHEAD = [10, 338, 297, 332, 284, 301, 293, 334, 296, 336, 9, 107, 66, 105, 63, 71, 54, 103, 67, 109]


def landmarker():
    import mediapipe as mp
    from mediapipe.tasks import python as mpp
    from mediapipe.tasks.python import vision
    data = (B / "face_landmarker.task").read_bytes()
    opts = vision.FaceLandmarkerOptions(base_options=mpp.BaseOptions(model_asset_buffer=data), num_faces=1, running_mode=vision.RunningMode.VIDEO)
    return vision.FaceLandmarker.create_from_options(opts), mp


def roi_mean(frame_rgb, lm):
    h, w = frame_rgb.shape[:2]; mask = np.zeros((h, w), np.uint8)
    for poly in (LEFT_CHEEK, RIGHT_CHEEK, FOREHEAD):
        pts = np.array([[int(lm[i].x * w), int(lm[i].y * h)] for i in poly], np.int32)
        cv2.fillPoly(mask, [pts], 1)
    m = mask.astype(bool)
    if m.sum() < 50:
        return None
    return frame_rgb[m].reshape(-1, 3).mean(0)


def extract():
    lmk, mp = landmarker(); out = {}
    vids = [(f, p) for f in FOLDERS for p in sorted((VID / f).glob("*.mp4"))]
    print("videos", len(vids), flush=True)
    for k, (f, p) in enumerate(vids):
        cap = cv2.VideoCapture(str(p)); tr = np.full((N_FRAMES, 3), np.nan, np.float32); ok = 0
        for i in range(N_FRAMES):
            r, fr = cap.read()
            if not r:
                break
            rgb = cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)
            res = lmk.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb), int(i * 1000 / FPS) + k * 100000)
            if res.face_landmarks:
                v = roi_mean(rgb, res.face_landmarks[0])
                if v is not None:
                    tr[i] = v; ok += 1
        cap.release(); out[f"{f}/{p.stem}"] = tr; out[f"{f}/{p.stem}/ok"] = ok
        if k % 50 == 0:
            print(k, f, p.stem, "ok", ok, flush=True)
    np.savez_compressed(HERE / "cdfb_rppg_traces.npz", **{k.replace("/", "|"): v for k, v in out.items()}); print("extract done", flush=True)


def pos(rgb, fps=FPS, win_s=1.6):
    """Wang et al. 2017 plane-orthogonal-to-skin; rgb: T x 3 (NaN-free). returns pulse signal T"""
    T = len(rgb); L = int(win_s * fps); H = np.zeros(T)
    for n in range(L, T + 1):
        C = rgb[n - L:n].T; mu = C.mean(1, keepdims=True)
        if np.any(mu == 0):
            continue
        Cn = C / mu; S = np.array([[0, 1, -1], [-2, 1, 1]], float) @ Cn
        a = S[1].std(); h = S[0] + (S[0].std() / a) * S[1] if a > 0 else S[0]
        H[n - L:n] += h - h.mean()
    return H


def snr_db(x, fps=FPS, lo=0.7, hi=3.0):
    from scipy.signal import butter, filtfilt
    b, a = butter(3, [lo / (fps / 2), hi / (fps / 2)], btype="band"); y = filtfilt(b, a, x)
    f = np.fft.rfftfreq(len(y), 1 / fps); P = np.abs(np.fft.rfft(y - y.mean())) ** 2
    band = (f >= lo) & (f <= hi); fp = f[band][np.argmax(P[band])]
    sig = band & (np.abs(f - fp) <= 0.1) | (band & (np.abs(f - 2 * fp) <= 0.1))
    ps, pn = P[sig].sum(), P[band & ~sig].sum()
    return float(10 * np.log10(ps / pn)) if pn > 0 else np.nan, float(fp)


def analyse():
    from sklearn.metrics import roc_auc_score
    from scipy.stats import spearmanr
    z = np.load(HERE / "cdfb_rppg_traces.npz"); rows = []
    for key in z.files:
        if key.endswith("|ok"):
            continue
        tr = z[key]; ok = int(z[key + "|ok"]); f, stem = key.split("|")
        if ok < 0.9 * N_FRAMES:
            rows.append((f, stem, np.nan, np.nan, ok)); continue
        t = tr.copy(); bad = np.isnan(t[:, 0])
        if bad.any():   # linear fill of the few missing frames
            idx = np.arange(N_FRAMES)
            for c in range(3):
                t[bad, c] = np.interp(idx[bad], idx[~bad], t[~bad, c])
        s, fp = snr_db(pos(t)); rows.append((f, stem, s, fp, ok))
    fold = np.array([r[0] for r in rows]); vid = np.array([r[1] for r in rows]); snr = np.array([r[2] for r in rows]); okn = np.array([r[4] for r in rows])
    score = -snr; sel = {d: fold == d for d in FOLDERS}; fin = np.isfinite(score)
    res = {"n_videos": {d: int(sel[d].sum()) for d in FOLDERS}, "dropped_landmark_fail": {d: int((sel[d] & ~fin).sum()) for d in FOLDERS},
           "median_snr_db": {d: round(float(np.nanmedian(snr[sel[d]])), 2) for d in FOLDERS}}

    def auc(g, f_):
        a = score[sel[g] & fin]; b = score[sel[f_] & fin]; return float(roc_auc_score([0] * len(a) + [1] * len(b), np.concatenate([a, b])))

    rng = np.random.default_rng(0)

    def boot(fn, n=2000):
        ids = np.unique(vid); byv = {v: np.flatnonzero(vid == v) for v in ids}; out = []
        for _ in range(n):
            pick = rng.choice(ids, len(ids)); idx = np.concatenate([byv[v] for v in pick]); out.append(fn(idx))
        return [float(np.nanpercentile(out, 2.5)), float(np.nanpercentile(out, 97.5))]

    res["auc_untreated"] = auc("real", "synthesis"); res["auc_beautified"] = auc("real_beautified", "synthesis_beautified"); res["auc_compressed"] = auc("real_compressed", "synthesis_compressed")
    res["d_auc_beauty_only"] = res["auc_beautified"] - res["auc_compressed"]
    t = np.nanquantile(score[sel["real"]], 0.95)

    def fa(idx, d): v = score[idx][sel[d][idx] & fin[idx]]; return float((v > t).mean() * 100) if len(v) else np.nan
    def miss(idx, d): v = score[idx][sel[d][idx] & fin[idx]]; return float((v <= t).mean() * 100) if len(v) else np.nan
    allidx = np.arange(len(vid))
    for d in FOLDERS:
        res[("fa_" if d.startswith("real") else "miss_") + d] = round((fa if d.startswith("real") else miss)(allidx, d), 2)
    res["d_fa_beauty_only"] = round(res["fa_real_beautified"] - res["fa_real_compressed"], 2); res["ci_d_fa"] = boot(lambda i: fa(i, "real_beautified") - fa(i, "real_compressed"))
    res["d_miss_beauty_only"] = round(res["miss_synthesis_beautified"] - res["miss_synthesis_compressed"], 2); res["ci_d_miss"] = boot(lambda i: miss(i, "synthesis_beautified") - miss(i, "synthesis_compressed"))
    # complementarity with Effort (video mean of frame scores from scores_v3)
    q = np.load(B / "results/research/celebdfb_v2_20260927/scores_v3/effort.npz", allow_pickle=True); pp = q["p"][:, 1]
    paths = [x.replace("\\", "/") for x in q["paths"].tolist()]; ef = {}
    for s_, p_ in zip(pp, paths):
        fo = p_.split("/")[-2]; st = p_.split("/")[-1].split("__")[0]; ef.setdefault((fo, st), []).append(s_)
    e = np.array([np.mean(ef.get((f, v), [np.nan])) for f, v in zip(fold, vid)]); m = sel["synthesis"] & fin & np.isfinite(e)
    res["spearman_vs_effort_untreated_forged"] = round(float(spearmanr(score[m], e[m]).correlation), 3)
    res["predictions"] = {"1_auc_untreated_ge_0.70": res["auc_untreated"] >= 0.70, "1_kill_lt_0.60": res["auc_untreated"] < 0.60,
                          "2_d_auc_beauty_only_ge_-0.05": res["d_auc_beauty_only"] >= -0.05, "2_kill_lt_-0.10": res["d_auc_beauty_only"] < -0.10,
                          "3_miss_rise_le5_fa_rise_le5": res["d_miss_beauty_only"] <= 5 and res["d_fa_beauty_only"] <= 5,
                          "4_spearman_vs_effort_lt_0.3": res["spearman_vs_effort_untreated_forged"] < 0.3}
    res["predictions"] = {k: bool(v) for k, v in res["predictions"].items()}
    (HERE / "cdfb_rppg.json").write_text(json.dumps(res, indent=1))
    L = ["# Addendum 64: rPPG (POS, SNR) under real app presets, Celeb-DF-B, one score per video, zero training", "",
         f"videos {res['n_videos']}; dropped (landmarker < 90 % of frames) {res['dropped_landmark_fail']}", "",
         f"median SNR dB {res['median_snr_db']}", "",
         f"AUC untreated {res['auc_untreated']:.3f} | beautified {res['auc_beautified']:.3f} | compressed {res['auc_compressed']:.3f} | beauty-only dAUC {res['d_auc_beauty_only']:+.3f}", "",
         f"At the untreated 5 % FPR threshold: FA real/beaut/compr {res['fa_real']:.1f} / {res['fa_real_beautified']:.1f} / {res['fa_real_compressed']:.1f} (dFA beauty-only {res['d_fa_beauty_only']:+.1f} [{res['ci_d_fa'][0]:+.1f}, {res['ci_d_fa'][1]:+.1f}]); "
         f"miss syn/beaut/compr {res['miss_synthesis']:.1f} / {res['miss_synthesis_beautified']:.1f} / {res['miss_synthesis_compressed']:.1f} (dMISS beauty-only {res['d_miss_beauty_only']:+.1f} [{res['ci_d_miss'][0]:+.1f}, {res['ci_d_miss'][1]:+.1f}])", "",
         f"Spearman(-SNR, Effort) on untreated forgeries {res['spearman_vs_effort_untreated_forged']}", "",
         "Predictions: " + json.dumps(res["predictions"])]
    (HERE / "CDFB_RPPG.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    {"extract": extract, "analyse": analyse}[sys.argv[1]]()
