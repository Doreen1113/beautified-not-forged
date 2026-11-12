"""Exploratory, post hoc (PRE_DECLARED Addendum 5): what limits retouched-vs-original separation on the unseen service?

Uses only scores that already exist (ali_scores_<tag>.npz, one Alibaba read per model) and the pair measurements
(pairs_ali.tsv). Nothing is selected or tuned from these numbers.

 A. Separability as a function of the measured size of the edit. Renders are binned by the measured quantity of their own
    operation (eye-width ratio - 1, 1 - jaw-width ratio, dL of the skin, 1 - high-frequency ratio) and by the overall
    mean absolute difference inside the face hull (mad_hull, 8-bit levels). Per bin: share called filter, AUROC of
    P(filter) against ALL untouched originals, and the paired rank (render above its own original).
 B. Between-image spread: the standard deviation of logit P(filter) across untouched originals, against the mean paired
    shift caused by the edit (same face, render minus original). A paired shift that is small next to the spread means the
    edit is seen but cannot be told from the variation between photographs.
 C. Which untouched originals are called filter: Spearman correlation and AUROC of image statistics inside the face hull
    (skin lightness L, high-frequency energy, Laplacian sharpness, face size) against P(filter).

python detectability.py  -> detectability<SUFFIX>.json (detectability.json = the earlier clipe4 checkpoint)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B))
sys.path.insert(0, str(HERE))
from main_model import MAIN_TAG, LITE_TAG, SUFFIX  # noqa: E402
TAGS = {"Ours": MAIN_TAG, "Ours-lite": LITE_TAG}
OPQ = {"EyeEnlarging": ("eye_ratio", lambda v: v - 1), "FaceLifting": ("jaw_ratio", lambda v: 1 - v),
       "Whitening": ("dL_skin", lambda v: v), "Smoothing": ("hf_ratio", lambda v: 1 - v)}


def logit(p):
    p = np.clip(p, 1e-6, 1 - 1e-6); return np.log(p / (1 - p))


def load_pairs():
    rows = [l.split("\t") for l in (HERE / "pairs_ali.tsv").read_text(encoding="utf-8").splitlines()]
    h = rows[0]; out = {}
    for r in rows[1:]:
        d = dict(zip(h, r)); out[(d["group"], Path(d["retouched"]).stem)] = {k: float(d[k]) for k in h[3:]}
    return out


def bins(x, edges):
    return np.digitize(x, edges)


def part_ab(tag, pairs):
    z = np.load(HERE / f"ali_scores_{tag}.npz"); P = z["P"]; g = z["group"].astype(str); st = z["stem"].astype(str)
    o = np.char.startswith(g, "orig"); pf = P[:, 2]; am = P.argmax(1)
    of = dict(zip(st[o], pf[o])); res = {"n_orig": int(o.sum()), "orig_called_filter": round(100 * float((am[o] == 2).mean()), 2)}
    # ---- B: spread vs paired shift
    lo = logit(pf[o]); res["orig_logit_sd"] = round(float(lo.std()), 3)
    shifts = {}
    for op in OPQ:
        for lv in (30, 60, 90):
            m = g == f"{op}_{lv}"
            d = logit(pf[m]) - logit(np.array([of[s] for s in st[m]]))
            shifts[f"{op}_{lv}"] = {"mean_paired_shift": round(float(d.mean()), 3), "shift_over_sd": round(float(d.mean() / lo.std()), 2),
                                    "paired_rank": round(100 * float((d > 0).mean()), 1),
                                    "auroc_vs_all_orig": round(float(roc_auc_score(np.r_[np.zeros(o.sum()), np.ones(m.sum())], np.r_[pf[o], pf[m]])), 3),
                                    "called_filter": round(100 * float((am[m] == 2).mean()), 1)}
    res["by_group"] = shifts
    # ---- A: by measured magnitude of the render's own operation, and by overall MAD
    A = {}
    for op, (key, f) in OPQ.items():
        m = np.char.startswith(g, op); q = np.array([f(pairs[(gg, s)][key]) if (gg, s) in pairs else np.nan for gg, s in zip(g[m], st[m])])
        ok = ~np.isnan(q); qq = q[ok]; pp = pf[m][ok]; aa = am[m][ok]; dd = logit(pp) - logit(np.array([of[s] for s in st[m][ok]]))
        edges = np.quantile(qq, [0.2, 0.4, 0.6, 0.8]); b = bins(qq, edges); rows = []
        for k in range(5):
            s = b == k
            rows.append({"q_lo": round(float(qq[s].min()), 4), "q_hi": round(float(qq[s].max()), 4), "q_median": round(float(np.median(qq[s])), 4), "n": int(s.sum()),
                         "called_filter": round(100 * float((aa[s] == 2).mean()), 1), "paired_rank": round(100 * float((dd[s] > 0).mean()), 1),
                         "auroc_vs_all_orig": round(float(roc_auc_score(np.r_[np.zeros(o.sum()), np.ones(s.sum())], np.r_[pf[o], pp[s]])), 3)})
        A[op] = {"quantity": key, "spearman_q_vs_pfilter": round(float(spearmanr(qq, pp).correlation), 3), "quintiles": rows}
    m = ~o; mad = np.array([pairs[(gg, s)]["mad_hull"] if (gg, s) in pairs else np.nan for gg, s in zip(g[m], st[m])]); ok = ~np.isnan(mad)
    edges = [1, 2, 3, 4, 6, 8, 12]; b = bins(mad[ok], edges); rows = []
    for k in range(len(edges) + 1):
        s = b == k
        if s.sum() < 50:
            continue
        rows.append({"mad_lo": ([0] + edges)[k], "mad_hi": (edges + [None])[k], "n": int(s.sum()), "called_filter": round(100 * float((am[m][ok][s] == 2).mean()), 1),
                     "auroc_vs_all_orig": round(float(roc_auc_score(np.r_[np.zeros(o.sum()), np.ones(s.sum())], np.r_[pf[o], pf[m][ok][s]])), 3)})
    A["overall_mad"] = rows; res["by_magnitude"] = A
    return res, dict(zip(st[o], zip(pf[o], am[o])))


def orig_stats(stems):
    from filters_v2.scale_normalized_filters import get_landmarks
    cache = HERE / "detectability_orig_stats.json"
    if cache.is_file():
        return json.loads(cache.read_text())
    out = {}
    for i, s in enumerate(sorted(stems)):
        im = cv2.imread(str(B / "ffhq_originals/Part2" / f"{s}.png"))
        if im is None:
            continue
        im = cv2.resize(im, (512, 512), interpolation=cv2.INTER_AREA); rgb = np.ascontiguousarray(im[..., ::-1]); lm = get_landmarks(rgb)
        if lm is None:
            continue
        m = np.zeros((512, 512), np.uint8); cv2.fillConvexPoly(m, cv2.convexHull(lm.astype(np.float32)).astype(np.int32), 255); m = m > 0
        lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32); L = lab[..., 0]
        out[s] = {"L_mean": float(L[m].mean()), "hf_energy": float(np.abs(L - cv2.GaussianBlur(L, (0, 0), 3))[m].mean()),
                  "lap_var": float(cv2.Laplacian(L, cv2.CV_32F)[m].var()), "chroma": float(np.hypot(lab[..., 1] - 128, lab[..., 2] - 128)[m].mean()),
                  "face_frac": float(m.mean())}
        if i % 400 == 0:
            print("stats", i, flush=True)
    cache.write_text(json.dumps(out)); return out


def part_c(orig_scores, stats):
    keys = [s for s in orig_scores if s in stats]; pf = np.array([orig_scores[s][0] for s in keys]); called = np.array([orig_scores[s][1] == 2 for s in keys])
    res = {"n": len(keys)}
    for k in ("L_mean", "hf_energy", "lap_var", "chroma", "face_frac"):
        v = np.array([stats[s][k] for s in keys])
        res[k] = {"spearman_vs_pfilter": round(float(spearmanr(v, pf).correlation), 3), "auroc_called_filter": round(float(roc_auc_score(called, v)), 3),
                  "median_called_filter": round(float(np.median(v[called])), 3), "median_not_called": round(float(np.median(v[~called])), 3)}
    return res


def main():
    pairs = load_pairs(); out = {}; scores = {}
    for name, tag in TAGS.items():
        out[name], scores[name] = part_ab(tag, pairs)
    stats = orig_stats(list(scores["Ours"]))
    for name in TAGS:
        out[name]["originals_called_filter_vs_image_statistics"] = part_c(scores[name], stats)
    a, b = scores["Ours"], scores["Ours-lite"]; ks = sorted(set(a) & set(b))
    out["agreement_on_originals"] = {"spearman_pfilter_ours_vs_lite": round(float(spearmanr([a[k][0] for k in ks], [b[k][0] for k in ks]).correlation), 3),
                                     "both_filter": round(100 * float(np.mean([(a[k][1] == 2) and (b[k][1] == 2) for k in ks])), 1),
                                     "ours_only": round(100 * float(np.mean([(a[k][1] == 2) and (b[k][1] != 2) for k in ks])), 1),
                                     "lite_only": round(100 * float(np.mean([(a[k][1] != 2) and (b[k][1] == 2) for k in ks])), 1)}
    (HERE / f"detectability{SUFFIX}.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
