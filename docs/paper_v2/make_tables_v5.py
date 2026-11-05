"""Tables and numbers for paper v5 (review REVIEW_V4_20261016.md). Computed from existing score / result files only; no model is run.
Formulas are logged in V5_CHANGES.md. make_tables_v4.py and its tables are left untouched; this script writes tab_v5_*.tex and
v5_numbers.json next to it.

Sources (all read-only)
  celebdfb_v2_20260927/scores_v3/<name>.npz (+ split cdfb_std32v3.txt)     Celeb-DF-B frame scores, as used by fair_cdfb.py
  celebdfb_v2_20260927/fair_cdfb.json                                       one-rule record (checked against the recomputation)
  alipair_zeroshot_20260929/published_scores_<det>.npz                       service scores, published detectors
  retouch_unified_20260929/ali_scores_<tag>.npz                              service scores, our models
  alipair_zeroshot_20260929/smoothing90_thresholdfree.json                   threshold-free Smoothing-90 statistics
  df40_eval_20261012/df40_eval.json                                          DF40 video AUC (mean over methods)
  retouch_unified_20260929/smooth_evasion2.json (via make_tables_v4)         smoothed-forgery test
  retouch_unified_20260929/{cdf,dfd}_filteredff.json                         filter sources

python docs/paper_v2/make_tables_v5.py
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, spearmanr
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import make_tables_v4 as v4   # noqa: E402  (functions and paths only; v4 tables are not rewritten)

BASE = Path(r"C:\My_Project\AIGC"); R = BASE / "results/research"; OUT = HERE / "tables"
CDFB = R / "celebdfb_v2_20260927"; ALI = R / "alipair_zeroshot_20260929"; RU = R / "retouch_unified_20260929"; DF40 = R / "df40_eval_20261012"
NB = 1000
PUB = v4.PUB
CITE = {"xception": "Xception~\\cite{xception}", "effnb4": "EfficientNet-B4~\\cite{efficientnet}", "f3net": "F3Net~\\cite{f3net}", "spsl": "SPSL~\\cite{spsl}",
        "ucf": "UCF~\\cite{ucf}", "recce": "RECCE~\\cite{recce}", "core": "CORE~\\cite{core}", "srm": "SRM~\\cite{srm}", "sbi": "SBI~\\cite{sbi}",
        "univfd": "UnivFD$^\\ddagger$~\\cite{univfd}", "npr": "NPR$^\\ddagger$~\\cite{npr}", "effort": "Effort~\\cite{effort}",
        "fadapter": "Forensics Adapter~\\cite{forensicsadapter}", "gend": "GenD~\\cite{gend2026}", "dfdhr": "DFD-HR~\\cite{dfdhr2026}",
        "caddm": "CADDM~\\cite{caddm}", "laanetr": "LAA-Net~\\cite{laanet}"}
NUM = {}   # every computed number, written to v5_numbers.json


def tabular(spec, lines, name):
    (OUT / name).write_text("\n".join([rf"\begin{{tabular}}{{{spec}}}", r"\toprule"] + lines + [r"\bottomrule", r"\end{tabular}"]) + "\n", encoding="utf-8")


# ======================================================================== 1. Celeb-DF-B =================================================
def cdfb_setup():
    rows = [l.split("\t") for l in (BASE / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    folder = np.array([r[3] for r in rows]); vid = np.array([r[2] for r in rows])
    vids = sorted(set(vid)); vix = {v: np.where(vid == v)[0] for v in vids}
    rng = np.random.default_rng(1); boots = [np.concatenate([vix[vids[j]] for j in rng.choice(len(vids), len(vids), True)]) for _ in range(NB)]
    NUM["cdfb_videos_per_folder"] = {f: int(len(set(vid[folder == f]))) for f in sorted(set(folder))}
    NUM["cdfb_frames_per_folder"] = {f: int((folder == f).sum()) for f in sorted(set(folder))}
    return folder, vid, boots


def cdfb_stats(s, folder, idx):
    """fair_cdfb.stats restricted to what v5 needs (same threshold rule: 95th percentile of untreated genuine frames inside the draw)."""
    f = folder[idx]; x = s[idx]; g = lambda k: x[f == k]; t = np.quantile(g("real"), 0.95)
    miss = lambda k: 100 * float((g(k) <= t).mean()); fa = lambda k: 100 * float((g(k) > t).mean())
    auc = lambda a, b: float(roc_auc_score(np.r_[np.zeros(len(g(a))), np.ones(len(g(b)))], np.r_[g(a), g(b)]))
    return {"auc_b": auc("real_beautified", "synthesis_beautified"), "fa_b": fa("real_beautified"), "fa_c": fa("real_compressed"),
            "dmb": (miss("synthesis_beautified") - miss("synthesis")) - (miss("synthesis_compressed") - miss("synthesis"))}


def video_auc_cdfb(s, folder, vid, a, b):
    """Video-level AUC: mean frame score per (folder, video), genuine folder a against forged folder b."""
    out = []
    for fo in (a, b):
        m = folder == fo; u, inv = np.unique(vid[m], return_inverse=True); out.append(np.bincount(inv, s[m]) / np.bincount(inv))
    return float(roc_auc_score(np.r_[np.zeros(len(out[0])), np.ones(len(out[1]))], np.r_[out[0], out[1]]))


OURS_CDFB = [("main s1", "RU-clipe5"), ("main s2", "RU-clipe5-s2"), ("variant", "RU-clipe5y_s20260929"), ("binary", "RU-clipe5b"),
             ("FF++ only three-way", "RU-clipe5f"), ("P0 s1", "RU-clipe5fbp0_s20260929"), ("P2 sym s1", "RU-clipe5fbg0oy_s20260929"),
             ("P2 sym s2", "RU-clipe5fbg0oy_s20260930")]
REF4 = ["effort", "fadapter", "gend", "dfdhr"]


def cdfb_all():
    folder, vid, boots = cdfb_setup(); fair = json.loads((CDFB / "fair_cdfb.json").read_text())
    names = PUB + [n for _, n in OURS_CDFB]
    S = {n: np.load(CDFB / "scores_v3" / f"{n}.npz")["p"][:, 1].astype(np.float64) for n in names}
    rec = {}
    for n in names:
        r = fair[n]
        a = cdfb_stats(S[n], folder, np.arange(len(folder)))
        assert abs(a["auc_b"] - r["auc_beautified"]) < 1e-3 and abs(a["fa_b"] - r["fa_b"]) < 0.01 and abs(a["dmb"] - r["d_miss_beauty_only"]) < 0.02, (n, a, r)
        rec[n] = {"auc_u": r["auc_untreated"], "auc_c": r["auc_compressed"], "auc_b": r["auc_beautified"], "auc_loss_total": round(r["auc_untreated"] - r["auc_beautified"], 4),
                  "auc_loss_reenc": round(r["auc_untreated"] - r["auc_compressed"], 4), "auc_loss_beauty": round(r["auc_compressed"] - r["auc_beautified"], 4),
                  "fa_c": r["fa_c"], "fa_b": r["fa_b"], "dfa_beauty": round(r["fa_b"] - r["fa_c"], 2), "dmiss_beauty": r["d_miss_beauty_only"],
                  "video_auc_u": round(video_auc_cdfb(S[n], folder, vid, "real", "synthesis"), 4),
                  "video_auc_b": round(video_auc_cdfb(S[n], folder, vid, "real_beautified", "synthesis_beautified"), 4),
                  "video_auc_c": round(video_auc_cdfb(S[n], folder, vid, "real_compressed", "synthesis_compressed"), 4)}
        if "native" in r:
            rec[n]["native_filter_rate"] = {k: v["filter"] for k, v in r["native"].items()}
    # bootstrap: dFA_beauty CI for all; paired AUC_b differences (ours minus each CLIP detector) on identical draws
    bs = {n: [cdfb_stats(S[n], folder, b) for b in boots] for n in names}
    for n in names:
        d = np.array([x["fa_b"] - x["fa_c"] for x in bs[n]]); rec[n]["dfa_beauty_ci"] = [round(float(np.percentile(d, q)), 2) for q in (2.5, 97.5)]
    paired = {}
    for lab, n in OURS_CDFB:
        paired[lab] = {}
        for ref in REF4:
            d = np.array([x["auc_b"] for x in bs[n]]) - np.array([x["auc_b"] for x in bs[ref]])
            paired[lab][ref] = [round(rec[n]["auc_b"] - rec[ref]["auc_b"], 4)] + [round(float(np.percentile(d, q)), 4) for q in (2.5, 97.5)]
            if ref in fair[n].get("auc_beautified_minus", {}):   # same draws as fair_cdfb.py: must reproduce its interval
                assert np.allclose(paired[lab][ref][1:], fair[n]["auc_beautified_minus"][ref], atol=2e-4), (n, ref, paired[lab][ref], fair[n]["auc_beautified_minus"][ref])
    # family of exposure contrasts on Celeb-DF-B dMISS_beauty (3 seeds x 3 contrasts), bootstrap p and Holm
    fam = {}
    for sd in ("20260929", "20260930", "20261001"):
        T = {a: f"RU-clipe5fb{a}_s{sd}" if a else f"RU-clipe5fb_s{sd}" for a in ("p0", "p1", "")}
        Sx = {a: np.load(CDFB / "scores_v3" / f"{t}.npz")["p"][:, 1].astype(np.float64) for a, t in T.items()}
        B = {a: np.array([cdfb_stats(Sx[a], folder, b)["dmb"] for b in boots]) for a in Sx}
        P = {a: fair[T[a]]["d_miss_beauty_only"] for a in Sx}
        for lab, x, y in (("P1-P0", "p1", "p0"), ("P2-P0", "", "p0"), ("P2-P1", "", "p1")):
            d = B[x] - B[y]; p = max(2 * min((d <= 0).mean(), (d >= 0).mean()), 1 / NB)
            fam[f"{lab} seed {sd}"] = {"diff": round(P[x] - P[y], 2), "ci": [round(float(np.percentile(d, q)), 2) for q in (2.5, 97.5)], "p_boot": float(p)}
    keys = sorted(fam, key=lambda k: fam[k]["p_boot"]); m = len(keys); prev = 0.0
    for i, k in enumerate(keys):
        prev = max(prev, min(1.0, (m - i) * fam[k]["p_boot"])); fam[k]["p_holm"] = round(prev, 4)
    NUM["cdfb"] = rec; NUM["cdfb_paired_aucb"] = paired; NUM["cdfb_exposure_family_holm"] = fam
    return rec, paired


# ======================================================================== 2. service: paired logit shift ======================================
def logit(p):
    p = np.clip(p.astype(np.float64), 1e-7, 1 - 1e-7); return np.log(p) - np.log1p(-p)


def paired_shift(s, g, st, rng):
    o = g == "orig_0"; m = g == "Smoothing_90"; so = dict(zip(st[o], logit(s[o])))
    keys = st[m]; d = logit(s[m]) - np.array([so[k] for k in keys])
    pos, neg = int((d > 0).sum()), int((d < 0).sum())
    bs = [np.median(d[rng.integers(0, len(d), len(d))]) for _ in range(NB)]
    return {"n": int(len(d)), "median_dlogit": round(float(np.median(d)), 3), "ci": [round(float(np.percentile(bs, q)), 3) for q in (2.5, 97.5)],
            "n_up": pos, "n_down": neg, "n_tie": int(len(d) - pos - neg), "sign_p": float(binomtest(pos, pos + neg, 0.5).pvalue) if pos + neg else None}


OURS_ALI = [("main s1", "clipe5_s20260929"), ("main s2", "clipe5_s20260930"), ("variant", "clipe5y_s20260929"), ("binary", "clipe5b_s20260929"),
            ("P0 s1", "clipe5fbp0_s20260929"), ("P2 s1", "clipe5fb_s20260929"), ("P1 s1", "clipe5fbp1_s20260929"), ("P1 smoothing only s1", "clipe5fbg0p1o_s20260929"),
            ("P2 smoothing only s1", "clipe5fbg0o_s20260929"), ("P2 sym s1", "clipe5fbg0oy_s20260929"), ("P2 sym s2", "clipe5fbg0oy_s20260930")]


def service_shift():
    out = {}
    for k in PUB:
        if k == "npr":
            continue
        z = np.load(ALI / f"published_scores_{k}.npz"); out[k] = paired_shift(z["s"], z["group"], z["stem"], np.random.default_rng(0))
    for lab, tag in OURS_ALI:
        z = np.load(RU / f"ali_scores_{tag}.npz"); out[lab] = paired_shift(z["P"][:, 1], z["group"], z["stem"], np.random.default_rng(0))
    s90 = json.loads((ALI / "smoothing90_thresholdfree.json").read_text())
    for k in PUB:   # the share with d > 0 must equal paired_up of the v4 tables (same strict ">" rule)
        if k in out:
            assert abs(100 * out[k]["n_up"] / out[k]["n"] - s90[k]["paired_up"]) < 0.06, (k, out[k], s90[k])
    NUM["service_paired_shift_smoothing90"] = out
    return out


# ======================================================================== 3. cross-detector correlation (B2) ================================
def correlations():
    s90 = json.loads((ALI / "smoothing90_thresholdfree.json").read_text()); d = json.loads((DF40 / "df40_eval.json").read_text())
    dets = [k for k in PUB if k in d and k in s90]
    up = [s90[k]["paired_up"] for k in dets]; acc = [s90[k]["fa_s90"] for k in dets]
    ff = [d[k]["mean"]["ff/FR"][0] for k in dets]; cd = [d[k]["mean"]["cdf/FR"][0] for k in dets]
    res = {"detectors": dets, "n": len(dets)}
    for lab, x in (("above_own_original", up), ("accused_5fpr", acc)):
        for dl, y in (("FR_ffdomain", ff), ("FR_cdfdomain", cd)):
            r = spearmanr(x, y); res[f"{lab} vs {dl}"] = {"rho": round(float(r.statistic), 2), "p": round(float(r.pvalue), 3)}
            k2 = [i for i, k in enumerate(dets) if k != "caddm"]; r2 = spearmanr([x[i] for i in k2], [y[i] for i in k2])
            res[f"{lab} vs {dl}, without CADDM"] = {"rho": round(float(r2.statistic), 2), "p": round(float(r2.pvalue), 3)}
    ps = sorted((v["p"], k) for k, v in res.items() if isinstance(v, dict) and "without" not in k); m = len(ps); prev = 0.0
    for i, (p, k) in enumerate(ps):
        prev = max(prev, min(1.0, (m - i) * p)); res[k]["p_holm4"] = round(prev, 3)
    NUM["cross_detector_spearman"] = res
    # same reading across our FF++-only arms, seed 1 (above own original vs FF++-domain reenactment)
    arms = {"P0": "clipe5fbp0_s20260929", "P2": "clipe5fb_s20260929", "P2 no smoothing": "clipe5fbn_s20260929", "P2 smoothing only": "clipe5fbg0o_s20260929",
            "P1": "clipe5fbp1_s20260929", "P1 smoothing only": "clipe5fbg0p1o_s20260929", "P2 symmetric": "clipe5fbg0oy_s20260929"}
    xs, ys = [], []
    for lab, tag in arms.items():
        z = np.load(RU / f"ali_scores_{tag}.npz"); tf = v4.thresholdfree(z["P"][:, 1].astype(np.float64), z["group"], z["stem"]); xs.append(tf["paired_up"])
        ys.append(v4.df40_mean(tag, d)["ff/FR"][0])
    r = spearmanr(xs, ys); NUM["arms_spearman_up_vs_FRff"] = {"arms": list(arms), "up": xs, "fr": ys, "rho": round(float(r.statistic), 2), "p": round(float(r.pvalue), 3)}
    return res


# ======================================================================== 4. tables ==========================================================
TRAIN = {k: "FF++ c23" for k in PUB}; TRAIN.update({"univfd": "ProGAN$^\\ddagger$", "npr": "ProGAN$^\\ddagger$", "caddm": "FF++ raw", "laanetr": "FF++ raw"})


def f3(x):
    return f"{x:.3f}"


def tab_twosided_main(rec):
    """Main Table: Celeb-DF-B (frame AUC untreated / re-encoded / beautified, beauty-only AUC loss, dMISS_beauty, FA_b, dFA_beauty) and
    the DFD filter source (frame AUC, AUC_f, dMISS, dFA). Point values; intervals in the supplement."""
    dfd = json.loads((RU / "dfd_filteredff.json").read_text())
    L = [r" & & \multicolumn{7}{c}{Celeb-DF-B, app presets (frame level)} & \multicolumn{4}{c}{DFD + 16 held-out filters (frame level)} \\",
         r"\cmidrule(lr){3-9}\cmidrule(lr){10-13}",
         r"Detector & train & AUC & AUC$_c$ & AUC$_b$ & AUC$_c{-}$AUC$_b$ & $\Delta$MISS$_\text{beauty}$ & FA$_b$ & $\Delta$FA$_\text{beauty}$ & AUC & AUC$_f$ & $\Delta$MISS & $\Delta$FA \\", r"\midrule"]

    def row(lab, tr, n, k):
        r = rec[n]; q = dfd[k]
        return " & ".join([lab, tr, f3(r["auc_u"]), f3(r["auc_c"]), f3(r["auc_b"]), f"{r['auc_loss_beauty']:.3f}", f"{r['dmiss_beauty']:+.1f}", f"{r['fa_b']:.1f}",
                           f"{r['dfa_beauty']:+.1f}", f3(q["auc_u"]), f3(q["auc_f"]), f"{q['d_miss']:+.1f}", f"{q['d_fa']:+.1f}"]) + r" \\"
    for k in PUB:
        L.append(row(CITE[k], TRAIN[k], k, k))
    L.append(r"\midrule")
    for lab, tr, n, k in ((r"\ours{} P0 (no beautified views)", "FF++", "RU-clipe5fbp0_s20260929", "clipe5fbp0_s20260929"),
                          (r"\ours{} P2 symmetric smoothing", "FF++", "RU-clipe5fbg0oy_s20260929", "clipe5fbg0oy_s20260929"),
                          (r"\ours{} three-way, full data$^\dagger$", "FF++, FFHQ", "RU-clipe5", "clipe5_s20260929"),
                          (r"\quad second seed$^\dagger$", "FF++, FFHQ", "RU-clipe5-s2", "clipe5_s20260930"),
                          (r"\quad symmetric-view variant$^\dagger$", "FF++, FFHQ", "RU-clipe5y_s20260929", "clipe5y_s20260929"),
                          (r"\ours{} binary control$^\dagger$", "FF++, FFHQ", "RU-clipe5b", "clipe5b_s20260929")):
        if k not in dfd:
            r2 = v4._filt_compute("dfd_filteredff", k); assert r2 is not None, k; dfd[k] = r2
            v4.COMPUTED.setdefault("dfd filter source from npz", set()).add(k)
        L.append(row(lab, tr, n, k))
    tabular("@{}ll ccccccc cccc@{}", L, "tab_v5_twosided_main.tex")


def tab_cdfb_extra(rec, paired):
    """Supplement: Celeb-DF-B per detector with re-encoding separated on both errors, video-level AUC, and paired AUC_b differences."""
    L = [r" & \multicolumn{3}{c}{frame AUC} & \multicolumn{3}{c}{video AUC} & \multicolumn{3}{c}{false alarms (\%)} \\",
         r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}\cmidrule(lr){8-10}",
         r"Detector & untreated & re-encoded & beautified & untreated & re-encoded & beautified & FA$_c$ & FA$_b$ & $\Delta$FA$_\text{beauty}$ [95\% CI] \\", r"\midrule"]
    lab = dict(CITE); lab.update({n: l for l, n in [(r"\ours{} three-way, full data", "RU-clipe5"), (r"\quad second seed", "RU-clipe5-s2"),
                                                     (r"\quad symmetric-view variant", "RU-clipe5y_s20260929"), (r"\ours{} binary control", "RU-clipe5b"),
                                                     (r"\ours{} FF++ only, three-way", "RU-clipe5f"), (r"\ours{} P0", "RU-clipe5fbp0_s20260929"),
                                                     (r"\ours{} P2 symmetric smoothing", "RU-clipe5fbg0oy_s20260929"), (r"\quad seed 2", "RU-clipe5fbg0oy_s20260930")]})
    for n in PUB + [n for _, n in OURS_CDFB]:
        if n == "RU-clipe5f":
            L.append(r"\midrule")
        r = rec[n]
        L.append(" & ".join([lab[n], f3(r["auc_u"]), f3(r["auc_c"]), f3(r["auc_b"]), f3(r["video_auc_u"]), f3(r["video_auc_c"]), f3(r["video_auc_b"]),
                             f"{r['fa_c']:.1f}", f"{r['fa_b']:.1f}", f"{r['dfa_beauty']:+.1f} [{r['dfa_beauty_ci'][0]:+.1f}, {r['dfa_beauty_ci'][1]:+.1f}]"]) + r" \\")
    tabular("@{}l ccc ccc ccc@{}", L, "tab_v5_cdfb_extra.tex")
    P = [r"Model & Effort & Forensics Adapter & GenD & DFD-HR \\", r"\midrule"]
    pl = {"main s1": r"\ours{} three-way, full data", "main s2": r"\quad second seed", "variant": r"\quad symmetric-view variant", "binary": r"\ours{} binary control",
          "FF++ only three-way": r"\ours{} FF++ only, three-way", "P0 s1": r"\ours{} P0 (FF++ only)", "P2 sym s1": r"\ours{} P2 symmetric smoothing", "P2 sym s2": r"\quad seed 2"}
    for k, v in paired.items():
        P.append(" & ".join([pl[k]] + [f"{v[r][0]:+.3f} [{v[r][1]:+.3f}, {v[r][2]:+.3f}]" for r in REF4]) + r" \\")
    tabular("@{}l cccc@{}", P, "tab_v5_cdfb_paired.tex")


def tab_retouch_main(sh):
    """Main Table: Smoothing-90 against own original: share above, median P(fake) orig -> render, accused at 5%-FPR, median paired logit shift [CI]."""
    s90 = json.loads((ALI / "smoothing90_thresholdfree.json").read_text())
    L = [r"Detector & above own orig.\ (\%) & median $P(\text{fake})$ & median $\Delta$logit [95\% CI] & accused (\%) \\", r"\midrule"]
    cell = lambda lab, tf, q: " & ".join([lab, f"{tf['paired_up']:.1f}", f"{tf['med_orig']:.2f} $\\rightarrow$ {tf['med_s90']:.2f}",
                                          f"{q['median_dlogit']:+.2f} [{q['ci'][0]:+.2f}, {q['ci'][1]:+.2f}]", f"{tf['fa_s90']:.1f}"]) + r" \\"
    for k in PUB:
        L.append(f"{CITE[k]} & " + " & ".join(["n/a"] * 4) + r" \\" if k == "npr" else cell(CITE[k], s90[k], sh[k]))
    L.append(r"\midrule")
    mod = v4._eval_published_ali()
    for lab, key, tag in ((r"\ours{} P0 (FF++ only)", "P0 s1", "clipe5fbp0_s20260929"), (r"\ours{} P2 symmetric smoothing", "P2 sym s1", "clipe5fbg0oy_s20260929"),
                          (r"\ours{} three-way, full data$^\dagger$", "main s1", "clipe5_s20260929"), (r"\quad symmetric-view variant$^\dagger$", "variant", "clipe5y_s20260929"),
                          (r"\ours{} binary control$^\dagger$", "binary", "clipe5b_s20260929")):
        z = np.load(RU / f"ali_scores_{tag}.npz"); tf = v4.thresholdfree(z["P"][:, 1].astype(np.float64), z["group"], z["stem"])
        L.append(cell(lab, tf, sh[key]))
    tabular("@{}l cccc@{}", L, "tab_v5_retouch_main.tex")


def tab_tradeoff_v5():
    """tab_v4_tradeoff with the AUC under strong whole-crop smoothing of both classes added (second reading of the smoothed-forgery test)."""
    e = json.loads((RU / "smooth_evasion2.json").read_text())
    t = (OUT / "tab_v4_tradeoff.tex").read_text(encoding="utf-8").splitlines()
    lab2pre = dict(v4.ARMS + v4.ARMS_E + [(v4.MAIN[0], "clipe5"), v4.SYM, (v4.BIN[0], "clipe5b")])
    out = []
    for ln in t:
        if ln.startswith(r"\begin{tabular}"):
            out.append(r"\begin{tabular}{@{}l cc cc cc cc cc@{}}"); continue
        if ln.startswith(r" & \multicolumn{2}{c}{commercial"):
            out.append(r" & \multicolumn{2}{c}{commercial Smoothing-90} & \multicolumn{2}{c}{smoothed Celeb-DF-v2 (strong bil.)} & \multicolumn{2}{c}{untreated video AUC} & \multicolumn{2}{c}{Celeb-DF-B (frame)} & \multicolumn{2}{c}{DF40 FR video AUC} \\"); continue
        if ln.startswith(r"\cmidrule"):
            out.append(r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}\cmidrule(lr){10-11}"); continue
        if ln.startswith("Arm &"):
            out.append(r"Arm & accused (\%) & above own orig.\ (\%) & miss rise & frame AUC, both smoothed & Celeb-DF-v2 & DFD & AUC$_b$ & $\Delta$MISS$_\text{beauty}$ & FF++ dom. & Celeb-DF dom. \\"); continue
        m = re.match(r"^(.*?) & (.*) \\\\$", ln)
        if m and m.group(1) in lab2pre:
            pre = lab2pre[m.group(1)]; cells = m.group(2).split(" & "); seeds = len(cells[0].split(" / ")); aucs = []
            for sd in ("s1", "s2", "s3")[:seeds]:
                o = v4.evasion_rec(f"{pre}_{v4.SEED[sd]}", e); aucs.append(f"{o['auc_smoothed_both'][2]:.3f}" if o else "--")
            out.append(" & ".join([m.group(1)] + cells[:3] + [" / ".join(aucs)] + cells[3:]) + r" \\"); continue
        out.append(ln)
    (OUT / "tab_v5_tradeoff.tex").write_text("\n".join(out) + "\n", encoding="utf-8")


def tab_tradeoff_main():
    """Main-paper version of tab_v5_tradeoff.tex: the same cells with three columns left out (untreated DFD video AUC,
    Celeb-DF-B dMISS_beauty, Celeb-DF-domain reenactment), which stay in the supplement version."""
    keep = [0, 1, 2, 3, 4, 5, 7, 9]   # Arm, accused, above own, miss rise, AUC both smoothed, Celeb-DF-v2 video AUC, AUC_b, FR FF++ domain
    out = [r"\begin{tabular}{@{}l cc cc c c c@{}}", r"\toprule",
           r" & \multicolumn{2}{c}{commercial Smoothing-90} & \multicolumn{2}{c}{smoothed Celeb-DF-v2} & Celeb-DF-v2 & Celeb-DF-B & DF40 FR \\",
           r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}",
           r"Arm & accused (\%) & above own orig.\ (\%) & miss rise & frame AUC & video AUC & frame AUC$_b$ & video AUC \\", r"\midrule"]
    for ln in (OUT / "tab_v5_tradeoff.tex").read_text(encoding="utf-8").splitlines():
        if ln.endswith(r"\\") and " & " in ln and "multicolumn" not in ln and not ln.startswith("Arm &"):
            c = ln[:-2].rstrip().split(" & "); out.append(" & ".join(c[i] for i in keep) + r" \\")
    out += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_v5_tradeoff_main.tex").write_text("\n".join(out) + "\n", encoding="utf-8")


RENAME = [(r"\ours{}, three-way, full data", r"\ours{}"), (r"\ours{} three-way, full data", r"\ours{}"), (r"\ours{}, symmetric-view variant", r"\ours{} variant"),
          (r"\quad symmetric-view variant", r"\quad \ours{} variant"), (r"\ours{}, binary control", "binary control"), (r"\ours{} binary control", "binary control"),
          (r"\ours{} P0 (no beautified views)", "P0"), (r"\ours{} P0 (FF++ only)", "P0"), ("P0 (FF++ only)", "P0"), (r"\ours{} P2 symmetric smoothing", "P2-sym"),
          ("P2 symmetric smoothing", "P2-sym"), ("P2 no smoothing", "P2-nosmooth"), ("P2 smoothing only", "P2-smooth"), ("P1 smoothing only", "P1-smooth"),
          ("Effort scheme, no beautified views", "Effort scheme, P0"), ("Effort scheme, symmetric smoothing", "Effort scheme, P2-sym"),
          ("released Effort fine-tuned, no beautified views", "released Effort fine-tuned, no views"), ("released Effort fine-tuned, symmetric smoothing", "released Effort fine-tuned, P2-sym view")]


def rename_main(src, dst):
    """Row labels of the main-paper tables in the names of the notation table (Table II of the paper)."""
    t = (OUT / src).read_text(encoding="utf-8")
    for a, b in RENAME:
        t = re.sub(rf"(?m)^{re.escape(a)}(?= &|\$)", b.replace("\\", "\\\\"), t)
    (OUT / dst).write_text(t, encoding="utf-8")


def add_cites(src, dst):
    """Copy of a v4 table with every published detector cited in its row (review F2); nothing else changes."""
    t = (OUT / src).read_text(encoding="utf-8")
    for k, plain in (("xception", "Xception"), ("effnb4", "EfficientNet-B4"), ("f3net", "F3Net"), ("spsl", "SPSL"), ("ucf", "UCF"), ("recce", "RECCE"),
                     ("core", "CORE"), ("srm", "SRM"), ("univfd", "UnivFD"), ("npr", "NPR")):
        t = re.sub(rf"(?m)^{re.escape(plain)} &", CITE[k].replace("\\", "\\\\") + " &", t)
    t = re.sub(r"(?m)^LAA-Net~\\cite\{laanet\} \(own crop rebuilt\)", r"LAA-Net~\\cite{laanet}", t)
    (OUT / dst).write_text(t, encoding="utf-8")


ALIPAIR_LABELS = [("three-way, observed fakes (SUP)", "three-way, observed forgeries"), ("three-way, hybrid fakes (HYB)", "three-way, observed and self-blended forgeries"),
                  ("HYB, faithful blend", "same, faithful blend"), ("HYB + symmetric degradation", "same, label-symmetric degradation"),
                  ("Vendor-trained variants (all single Alibaba reads)", "Variants trained with two services' renders (each read once on the test service)"),
                  ("RU1 renders only", "renders only"), ("RU2 + components", "renders + single-operation components"),
                  ("RU3 cleaned components", "components below noise floor removed"), ("RU3 + evidence head, CLIP", "same + evidence head, CLIP"),
                  ("RU3 + evidence head", "same + evidence head"), ("RU4 + part edits (lite)", "same + part-level forgeries (lite)"),
                  ("RU4 + part edits, CLIP (filter-F1 selection)", "same + part-level forgeries, CLIP, filter-F1 selection (superseded)"),
                  ("RU4 + part edits, CLIP", "same + part-level forgeries, CLIP"), ("RU5 without colour grading", "main recipe without colour grading"),
                  ("RU5 without vendor edit on forgeries", "main recipe without service edits on forgeries"), ("RU5 data, three-way softmax", "main data, three-way softmax head"),
                  ("RU5, CLIP (main)", r"main model (\ours{})"), ("RU4, CLIP (filter-F1 selected, superseded)", "full-data CLIP model, filter-F1 selection (superseded)")]


def relabel(src, dst):
    t = (OUT / src).read_text(encoding="utf-8")
    for a, b in ALIPAIR_LABELS:
        t = t.replace(a, b)
    assert not re.search(r"\bRU\d|\(SUP\)|\(HYB\)|\bHYB\b", t), (dst, re.findall(r".*RU\d.*", t))
    (OUT / dst).write_text(t, encoding="utf-8")


def tab_baselines():
    """Supplement: provenance of every published detector (weights, training data, input). Facts from the scorer headers in external_baselines/."""
    rows = [("Xception, EfficientNet-B4, F3Net, SPSL, UCF, RECCE, CORE, SRM", r"DeepfakeBench release~\cite{deepfakebench}", "FF++ c23", "256 px"),
            ("SBI", "authors' release (FFc23)", "FF++ c23 reals, self-blended", "380 px"),
            ("Effort", "authors' release", "FF++ c23", "224 px"),
            ("Forensics Adapter", "authors' release", "FF++ c23", "256 px, resized to 224 for CLIP"),
            ("GenD (CLIP ViT-L/14)", "authors' release", "FF++ c23", "224 px"),
            ("DFD-HR", "authors' release", "FF++ c23", "448 px"),
            ("CADDM (EfficientNet-B4)", "authors' release", "FF++ raw", "own 5-point alignment, 224 px"),
            ("LAA-Net", "authors' release (SBI-trained)", "FF++ raw, self-blended", "own crop rebuilt in our box, 384 px"),
            ("UnivFD", "authors' release (linear probe on CLIP)", "ProGAN images (not faces)", "224 px centre crop"),
            ("NPR", "authors' release", "ProGAN images (not faces)", "256 px")]
    L = [r"Detector & weights & training data & input \\", r"\midrule"] + [" & ".join(r) + r" \\" for r in rows]
    tabular("@{}>{\\raggedright\\arraybackslash}p{0.27\\linewidth}>{\\raggedright\\arraybackslash}p{0.2\\linewidth}>{\\raggedright\\arraybackslash}p{0.2\\linewidth}>{\\raggedright\\arraybackslash}p{0.26\\linewidth}@{}", L, "tab_v5_baselines.tex")


def tab_shift_all(sh):
    """Supplement: paired logit shift on Smoothing-90 for every detector and arm, with the two-sided sign test (ties dropped)."""
    lab = dict(CITE); lab.update({"main s1": r"\ours{} three-way, full data", "main s2": r"\quad second seed", "variant": r"\quad symmetric-view variant",
                                  "binary": r"\ours{} binary control", "P0 s1": "P0", "P2 s1": "P2", "P1 s1": "P1", "P1 smoothing only s1": "P1-smooth",
                                  "P2 smoothing only s1": "P2-smooth", "P2 sym s1": "P2-sym", "P2 sym s2": r"\quad P2-sym, seed 2"})
    def pfmt(p):
        if p is None:
            return "n/a"
        if p < 1e-10:
            return r"$<10^{-10}$"
        e = int(np.floor(np.log10(p))); return f"{p:.2f}" if p >= 0.01 else rf"${p / 10 ** e:.1f}\times10^{{{e}}}$"
    L = [r"Model & up / down / tie & median $\Delta$logit [95\% CI] & sign test $p$ \\", r"\midrule"]
    for k, q in sh.items():
        if k == "main s1":
            L.append(r"\midrule")
        L.append(" & ".join([lab[k], f"{q['n_up']} / {q['n_down']} / {q['n_tie']}", f"{q['median_dlogit']:+.2f} [{q['ci'][0]:+.2f}, {q['ci'][1]:+.2f}]", pfmt(q["sign_p"])]) + r" \\")
    tabular("@{}l ccc@{}", L, "tab_v5_shift_all.tex")


if __name__ == "__main__" and sys.argv[1:] == ["--shift-only"]:
    tab_tradeoff_main(); v4.check("tab_v5_tradeoff_main.tex")
    for s, d in (("tab_v5_tradeoff_main.tex", "tab_v5_tradeoff_main.tex"), ("tab_v5_twosided_main.tex", "tab_v5_twosided_main.tex"), ("tab_v5_retouch_main.tex", "tab_v5_retouch_main.tex"), ("tab_v4_df40_main.tex", "tab_v5_df40_main.tex")):
        rename_main(s, d)
    tab_shift_all(json.loads((HERE / "v5_numbers.json").read_text())["service_paired_shift_smoothing90"]); v4.check("tab_v5_shift_all.tex")
elif __name__ == "__main__":
    rec, paired = cdfb_all(); sh = service_shift(); cor = correlations()
    tab_twosided_main(rec); tab_cdfb_extra(rec, paired); tab_retouch_main(sh); tab_shift_all(sh); tab_tradeoff_v5(); tab_tradeoff_main(); tab_baselines()
    for s, d in (("tab_v4_twosided.tex", "tab_v5_twosided_full.tex"), ("tab_v4_retouch.tex", "tab_v5_retouch_full.tex"), ("tab_v4_perop.tex", "tab_v5_perop.tex"),
                 ("tab_v4_df40.tex", "tab_v5_df40_full.tex"), ("tab_fullframe.tex", "tab_v5_fullframe.tex"), ("tab_reproduce.tex", "tab_v5_reproduce.tex")):
        add_cites(s, d)
    for s, d in (("tab_v5_tradeoff_main.tex", "tab_v5_tradeoff_main.tex"), ("tab_v5_twosided_main.tex", "tab_v5_twosided_main.tex"), ("tab_v5_retouch_main.tex", "tab_v5_retouch_main.tex"), ("tab_v4_df40_main.tex", "tab_v5_df40_main.tex")):
        rename_main(s, d)
    relabel("tab_alipair_all.tex", "tab_v5_alipair_all.tex"); relabel("tab_alipair.tex", "tab_v5_alipair.tex"); relabel("tab_cgd_explain_all.tex", "tab_v5_cgd_explain_all.tex")
    for n in ("tab_v5_twosided_main.tex", "tab_v5_cdfb_extra.tex", "tab_v5_cdfb_paired.tex", "tab_v5_retouch_main.tex", "tab_v5_tradeoff.tex"):
        v4.check(n)
    (HERE / "v5_numbers.json").write_text(json.dumps(NUM, indent=1), encoding="utf-8")
    print(json.dumps({k: NUM[k] for k in ("cdfb_videos_per_folder", "cdfb_paired_aucb", "cdfb_exposure_family_holm", "cross_detector_spearman", "arms_spearman_up_vs_FRff")}, indent=1))
    print("service shift:", json.dumps(sh, indent=0))
    print("computed (not read):", {k: sorted(v) for k, v in v4.COMPUTED.items()})
