"""Does smoothing a forgery let it pass? (Addendum 33, check (e); written 2026-10-13 after the threshold-free view showed
that the smoothing-only, genuine-only arm scores a smoothed genuine face BELOW its own original in 97% of pairs.)

Celeb-DF-v2 test frames (our crop, every 4th frame of the 32 per video), untreated and with a bilateral filter applied to
the whole crop at three strengths (9,50,50) / (15,80,80) / (21,100,100), the three settings of the scripted smoothing.
Threshold: 5% FPR on untreated genuine frames. Reported per model and strength: miss on untreated forgeries, miss on
smoothed forgeries, false alarms on smoothed genuine frames, frame AUC untreated and smoothed (smoothed forged against
smoothed genuine, and smoothed forged against untreated genuine), share of forged frames whose score falls after smoothing.
Bootstrap over videos, 1000 draws; paired difference of the miss rise against P0 of the same seed with the same draws.

python smooth_evasion.py score <tag> ... | analyse"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC")
LIST = B / "splits/research/ffpp_benchmark_20260925/celebdf_std32v2.txt"
LEVELS = [(9, 50, 50), (15, 80, 80), (21, 100, 100), "median5", "gblend"]   # the last two are forms no arm has seen (Addendum 34)
NL = len(LEVELS); J = list(range(1, NL + 1))
REF = {"20260929": "clipe5fbp0_s20260929", "20260930": "clipe5fbp0_s20260930", "20261001": "clipe5fbp0_s20261001"}


def apply(im, lv):
    import cv2
    if lv is None:
        return im
    if lv == "median5":
        return cv2.medianBlur(im, 5)
    if lv == "gblend":
        return cv2.addWeighted(im, 0.5, cv2.GaussianBlur(im, (0, 0), 2.0), 0.5, 0)
    return cv2.bilateralFilter(im, *lv)


def rows():
    r = [l.split("\t") for l in LIST.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return [x for x in r if int(Path(x[0]).stem.rsplit("__f", 1)[1]) % 4 == 0]


def score(tag):
    f = HERE / f"smooth_evasion2_{tag}.npz"
    if f.is_file():
        print(tag, "cached"); return
    import cv2, torch
    from PIL import Image
    sys.path.insert(0, str(HERE)); from leak_probe import load; from train_ru3 import to_t2
    model, size, norm = load(tag); r = rows(); S = np.zeros((len(r), 1 + len(LEVELS)), np.float32)
    with torch.no_grad():
        for i in range(0, len(r), 32):
            ims = [np.array(Image.open(x[0]).convert("RGB")) for x in r[i:i + 32]]
            for j, lv in enumerate([None] + LEVELS):
                x = torch.stack([to_t2(apply(im, lv), size, False, norm) for im in ims]).cuda()
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    S[i:i + 32, j] = torch.softmax(model(x)[0].float(), 1)[:, 1].cpu().numpy()
    np.savez(f, S=S, y=np.array([int(x[1]) for x in r]), video=np.array([x[2] for x in r])); print(tag, "done", len(r), flush=True)


def analyse():
    from sklearn.metrics import roc_auc_score
    out = {}; rng = np.random.default_rng(0); files = sorted(HERE.glob("smooth_evasion2_*.npz")); cache = {}
    z0 = np.load(files[0]); y, v = z0["y"], z0["video"]; uv = np.unique(v); by = {k: np.where(v == k)[0] for k in uv}
    draws = [np.concatenate([by[k] for k in rng.choice(uv, len(uv))]) for _ in range(1000)]

    def stat(S, idx):
        s = S[idx]; yy = y[idx]; g, f = yy == 0, yy == 1; t = np.quantile(s[g, 0], 0.95); m0 = (s[f, 0] <= t).mean() * 100
        return [m0] + [((s[f, j] <= t).mean() * 100 - m0) for j in J] + [(s[g, j] > t).mean() * 100 for j in J]

    for fp in files:
        tag = fp.stem[len("smooth_evasion2_"):]; S = np.load(fp)["S"].astype(np.float64); cache[tag] = S
        a = stat(S, np.arange(len(y))); bs = np.array([stat(S, d) for d in draws]); g, f = y == 0, y == 1
        out[tag] = {"miss_untreated": round(a[0], 1),
                    "miss_rise": [[round(a[j], 1)] + [round(float(np.percentile(bs[:, j], q)), 1) for q in (2.5, 97.5)] for j in J],
                    "fa_smoothed_genuine": [round(a[j], 1) for j in [NL + k for k in J]],
                    "auc_untreated": round(float(roc_auc_score(y, S[:, 0])), 3),
                    "auc_smoothed_both": [round(float(roc_auc_score(y, S[:, j])), 3) for j in J],
                    "auc_smoothed_forged_vs_untreated_genuine": [round(float(roc_auc_score(np.r_[np.zeros(g.sum()), np.ones(f.sum())], np.r_[S[g, 0], S[f, j]])), 3) for j in J],
                    "forged_score_falls": [round(float((S[f, j] < S[f, 0]).mean() * 100), 1) for j in J],
                    "genuine_score_falls": [round(float((S[g, j] < S[g, 0]).mean() * 100), 1) for j in J]}
        out[tag]["_bs"] = bs
    for tag in list(out):
        ref = REF.get(tag.rsplit("_s", 1)[1])
        if ref in out and ref != tag:
            d = out[tag]["_bs"] - out[ref]["_bs"]
            out[tag]["miss_rise_minus_P0"] = [[round(out[tag]["miss_rise"][j - 1][0] - out[ref]["miss_rise"][j - 1][0], 1)] + [round(float(np.percentile(d[:, j], q)), 1) for q in (2.5, 97.5)] for j in J]
    for tag in out:
        out[tag].pop("_bs")
    (HERE / "smooth_evasion2.json").write_text(json.dumps(out, indent=1))
    print("tag | miss untreated | miss rise bilateral light / mid / strong / median5 / gaussian blend | FA smoothed genuine | AUC untr | AUC smoothed (both) | forged falls %")
    for t, o in out.items():
        print(f"{t} | {o['miss_untreated']} | " + " / ".join(f"{m[0]:+.1f} [{m[1]:+.1f},{m[2]:+.1f}]" for m in o["miss_rise"]) + f" | {o['fa_smoothed_genuine']} | {o['auc_untreated']} | {o['auc_smoothed_both']} | {o['forged_score_falls']}"
              + (" | vs P0 " + " / ".join(f"{m[0]:+.1f} [{m[1]:+.1f},{m[2]:+.1f}]" for m in o["miss_rise_minus_P0"]) if "miss_rise_minus_P0" in o else ""))


if __name__ == "__main__":
    if sys.argv[1] == "score":
        for t in sys.argv[2:]:
            score(t)
    else:
        analyse()
