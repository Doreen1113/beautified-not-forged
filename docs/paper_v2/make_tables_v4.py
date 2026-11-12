"""LaTeX tables for the v4 rewrite (commercial retouching, DF40, smoothed-forgery evasion, exposure trade-off), generated from
result files only; nothing hand-typed. Conventions follow make_tables_v3.py (3 decimals for AUC, 1 decimal for percentages,
bootstrap CIs as [lo, hi], booktabs, \\ours macro, detector names / cite keys from NICE).

Sources
  alipair_zeroshot_20260929/published_ali.json, smoothing90_thresholdfree.json   (17 published detectors + main + binary control)
  retouch_unified_20260929/ali_scores_<tag>.npz                                   (FF++-only exposure arms; computed here with
                                                                                   eval_published_ali.block and the threshold-free
                                                                                   statistics of smoothing90_thresholdfree.json)
  df40_eval_20261012/df40_eval.json                                               (DF40 held-out video AUC)
  retouch_unified_20260929/smooth_evasion2.json                                   (smooth_evasion.py analyse)
  retouch_unified_20260929/cdf_filtered_scores_<tag>.npz, dfd_v3_scores_<tag>.npz (untreated video AUC = mean frame score per video)
  celebdfb_v2_20260927/fair_RU-<tag>.log (JSON line) or fair_cdfb.json            (Celeb-DF-B one rule)

  retouch_unified_20260929/fusion37.json                                          (Addendum 37, fusion with CADDM)
  make_tables_v3.row_twosided + fair_cdfb.json, cdf_filteredff.json, dfd_filteredff.json (v4 variant of the main two-sided table)

Where a json does not yet hold a tag whose score file exists (DF40, smoothed-forgery test, filter sources), the same statistic is
computed here from the score file with the code of the analysis script, checked against the json on a tag that is in it, and the
tag is listed under "computed (not read)". No result file is written.

python docs/paper_v2/make_tables_v4.py -> docs/paper_v2/tables/tab_v4_retouch.tex, tab_v4_df40.tex, tab_v4_evasion.tex, tab_v4_tradeoff.tex,
                                         tab_v4_fusion.tex, tab_v4_twosided.tex, tab_v4_df40_main.tex, tab_v4_perop.tex, tab_v4_retouch_main.tex
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

BASE = Path(r"C:\My_Project\AIGC"); R = BASE / "results/research"; OUT = BASE / "docs/paper_v2/tables"; OUT.mkdir(parents=True, exist_ok=True)
ALI = R / "alipair_zeroshot_20260929"; RU = R / "retouch_unified_20260929"; CDFB = R / "celebdfb_v2_20260927"; DF40 = R / "df40_eval_20261012"
PUB = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "univfd", "npr", "effort", "fadapter", "gend", "dfdhr", "caddm", "laanetr"]
NICE = {"effort": "Effort~\\cite{effort}", "fadapter": "Forensics Adapter~\\cite{forensicsadapter}", "xception": "Xception", "effnb4": "EfficientNet-B4", "spsl": "SPSL",
        "f3net": "F3Net", "ucf": "UCF", "recce": "RECCE", "core": "CORE", "srm": "SRM", "sbi": "SBI~\\cite{sbi}", "univfd": "UnivFD", "npr": "NPR", "gend": "GenD~\\cite{gend2026}", "dfdhr": "DFD-HR~\\cite{dfdhr2026}",
        "caddm": "CADDM~\\cite{caddm}", "laanetr": "LAA-Net~\\cite{laanet} (own crop rebuilt)"}
SEED = {"s1": "s20260929", "s2": "s20260930", "s3": "s20261001"}
# exposure arms (FF++ only unless noted): label, tag prefix
ARMS = [("P0", "clipe5fbp0"), ("P2", "clipe5fb"), ("P2 no smoothing", "clipe5fbn"), ("P2 smoothing only", "clipe5fbg0o"), ("P1", "clipe5fbp1"),
        ("P1 smoothing only", "clipe5fbg0p1o"), ("P2 symmetric smoothing", "clipe5fbg0oy")]
# Addendum 35: the symmetric smoothing view under Effort's tuning scheme, each arm after its own reference
ARMS_E = [("Effort scheme, no beautified views", "clipe5fbp0E"), ("Effort scheme, symmetric smoothing", "clipe5fbg0oyE"),
          ("released Effort fine-tuned, no beautified views", "clipe5fbp0Ei"), ("released Effort fine-tuned, symmetric smoothing", "clipe5fbg0oyEi")]
MAIN = ("\\ours{}, three-way, full data", "clipe5"); BIN = ("\\ours{}, binary control", "clipe5b")
SYM = ("\\ours{}, symmetric-view variant", "clipe5y")   # Addendum 36: reported beside the main model, not as the main model
PEND_TAGS = ("clipe5y",)   # a missing source of these is still being produced: the cell is \textit{pend.}, not "--"
PEND = r"\textit{pend.}"; NA = r"n/a"
MISSING = []     # (table, tag) whose source file was absent
COMPUTED = {}    # formula -> tags whose numbers were computed here rather than read from a json


def jl(p):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def ci(v, d=1, plus=False):
    f = f"{{:{'+' if plus else ''}.{d}f}}"
    return f"{f.format(v[0])} [{f.format(v[1])}, {f.format(v[2])}]"


def tabular(spec, lines, name):
    L = [rf"\begin{{tabular}}{{{spec}}}", r"\toprule"] + lines + [r"\bottomrule", r"\end{tabular}"]
    (OUT / name).write_text("\n".join(L) + "\n", encoding="utf-8")
    return L


# ---------------------------------------------------------------- 1. commercial retouching -----------------------------------------
def _eval_published_ali():
    spec = importlib.util.spec_from_file_location("eval_published_ali", ALI / "eval_published_ali.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def thresholdfree(s, g, st):
    """Same statistics as smoothing90_thresholdfree.json: Smoothing-90 renders vs their own originals (verified to reproduce P0 s1 bit for bit)."""
    o = g == "orig_0"; sm = g == "Smoothing_90"; so = dict(zip(st[o], s[o])); t = float(np.nanquantile(s[o], 0.95))
    return {"auroc_s90": round(float(roc_auc_score(np.r_[np.zeros(o.sum()), np.ones(sm.sum())], np.r_[s[o], s[sm]])), 3),
            "paired_up": round(float(np.mean([v > so[k] for v, k in zip(s[sm], st[sm])]) * 100), 1), "t": round(t, 4),
            "fa_s90": round(float((s[sm] > t).mean() * 100), 1), "med_orig": round(float(np.median(s[o])), 3), "med_s90": round(float(np.median(s[sm])), 3)}


def ali_arm(tag, mod):
    f = RU / f"ali_scores_{tag}.npz"
    if not f.is_file():
        MISSING.append(("retouch", tag)); return None
    z = np.load(f); s = z["P"][:, 1].astype(np.float64); g = z["group"]; st = z["stem"]
    b = mod.block(s, g, st); tf = thresholdfree(s, g, st)
    COMPUTED.setdefault("ali block(): t = 95th pct of P(fake) on originals; all renders > t (%); AUROC all renders vs originals; and threshold-free: share of "
                        "Smoothing_90 renders with score > own original (%), median P(fake) originals / Smoothing_90, Smoothing_90 > t (%), AUROC Smoothing_90 vs originals", set()).add(tag)
    return b, tf


def retouch_row(lab, b, tf):
    if b is None:
        return f"{lab} & " + " & ".join([PEND] * 5) + r" \\"
    return " & ".join([lab, f"{tf['paired_up']:.1f}", f"{tf['med_orig']:.3f} $\\rightarrow$ {tf['med_s90']:.3f}", f"{tf['fa_s90']:.1f}", f"{b['ret_fake_at_t']:.1f}", f"{b['auroc_ret_vs_orig']:.3f}"]) + r" \\"


def tab_retouch():
    pub = jl(ALI / "published_ali.json"); s90 = jl(ALI / "smoothing90_thresholdfree.json"); mod = _eval_published_ali()
    L = [r" & \multicolumn{3}{c}{Smoothing-90 renders} & \multicolumn{2}{c}{all renders} \\", r"\cmidrule(lr){2-4}\cmidrule(lr){5-6}",
         r"Detector & above own original (\%) & median $P(\text{fake})$ orig.\ $\rightarrow$ render & above 5\%-FPR thr.\ (\%) & above 5\%-FPR thr.\ (\%) & AUROC render vs orig. \\", r"\midrule"]
    for k in PUB:
        if k == "npr":
            L.append(f"{NICE[k]} & " + " & ".join([NA + r" (saturated)"] + [NA] * 4) + r" \\"); continue
        b = pub.get(k); tf = s90.get(k)
        L.append(retouch_row(NICE[k], b, tf) if b and tf else f"{NICE[k]} & " + " & ".join([PEND] * 5) + r" \\")
        if not (b and tf):
            MISSING.append(("retouch", k))
    L.append(r"\midrule")
    for lab, kb, ks in ((MAIN[0], "ours main", "main 3-way full"), (BIN[0], "ours binary control", "binary full")):
        L.append(retouch_row(lab, pub.get(kb), s90.get(ks)))
        if kb == "ours main":
            r = ali_arm(f"{SYM[1]}_{SEED['s1']}", mod); L.append(retouch_row(SYM[0], *(r if r else (None, None))))
    L.append(r"\midrule"); L.append(r"\multicolumn{6}{@{}l}{\ours{}, FF++ only, exposure arms (seed 1)} \\")
    for lab, pre in ARMS:
        r = ali_arm(f"{pre}_{SEED['s1']}", mod)
        if r is not None:
            key = {"clipe5fbp0": "P0 s1", "clipe5fb": "P2 s1", "clipe5fbn": "P2 no-smooth s1", "clipe5fbg0o": "P2 smooth-only s1", "clipe5fbp1": "P1 s1", "clipe5fbg0p1o": "P1 smooth-only s1"}.get(pre)
            if key and key in s90:
                assert all(abs(s90[key][q] - r[1][q]) < 1e-9 for q in ("paired_up", "fa_s90", "auroc_s90", "med_orig", "med_s90")), (key, s90[key], r[1])
        L.append(retouch_row(f"\\quad {lab}", *(r if r else (None, None))))
    L.append(r"\midrule"); L.append(r"\multicolumn{6}{@{}l}{\ours{} pipeline, FF++ only, Effort's tuning scheme (seed 1)} \\")
    for lab, pre in ARMS_E:
        r = ali_arm(f"{pre}_{SEED['s1']}", mod); L.append(retouch_row(f"\\quad {lab}", *(r if r else (None, None))))
    return tabular("@{}l ccc cc@{}", L, "tab_v4_retouch.tex")


def tab_retouch_main():
    """Single-column version for the main paper: the published detectors and the full-data models, Smoothing-90 columns only."""
    s90 = jl(ALI / "smoothing90_thresholdfree.json"); mod = _eval_published_ali()
    cell = lambda lab, tf: " & ".join([lab, f"{tf['paired_up']:.1f}", f"{tf['med_orig']:.3f} $\\rightarrow$ {tf['med_s90']:.3f}", f"{tf['fa_s90']:.1f}"]) + r" \\"
    none = lambda lab, x: f"{lab} & " + " & ".join([x] * 3) + r" \\"
    L = [r"Detector & above own orig.\ (\%) & median $P(\text{fake})$ & above thr.\ (\%) \\", r"\midrule"]
    for k in PUB:
        lab = NICE[k].replace(" (own crop rebuilt)", "")
        L.append(none(lab, NA) if k == "npr" else (cell(lab, s90[k]) if k in s90 else none(lab, PEND)))
    L.append(r"\midrule"); L.append(cell(r"\ours{}", s90["main 3-way full"]))
    r = ali_arm(f"{SYM[1]}_{SEED['s1']}", mod); L.append(cell(r"\quad symmetric-view variant", r[1]) if r else none(r"\quad symmetric-view variant", PEND))
    L.append(cell("binary control", s90["binary full"]))
    return tabular("@{}l ccc@{}", L, "tab_v4_retouch_main.tex")


# ---------------------------------------------------------------- 2. DF40 ---------------------------------------------------------------
DF40_COLS = ["ff/FS", "ff/FR", "cdf/FS", "cdf/FR"]
DF40_FOOT = ("Video AUC, mean frame score per video. Real videos are the FF++ and Celeb-DF-v2 test reals; the 718 mobileswap videos from "
             "FF++ train identities were removed; 140 fake videos per method in the Celeb-DF domain. FS: face swap; FR: face reenactment. "
             "95\\% bootstrap intervals over videos.")


_DF40 = {}


def _df40_setup():
    """Groups and bootstrap draws exactly as df40_eval.analyse (default_rng(0), same order), for tags whose scores exist but are not in df40_eval.json yet."""
    if "groups" in _DF40:
        return _DF40
    r = [l.split("\t") for l in (DF40 / "df40_eval_list.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    vid = np.array([f"{x[4]}|{x[3]}|{x[2]}" for x in r]); uv, inv = np.unique(vid, return_inverse=True)
    vdom = np.array([u.split("|")[0] for u in uv]); vmeth = np.array([u.split("|")[1] for u in uv]); rng = np.random.default_rng(0); groups = {}
    for dm in ("ff", "cdf"):
        real = np.where((vdom == dm) & (vmeth == "real"))[0]
        for m in sorted(set(vmeth[vdom == dm]) - {"real"}):
            groups[(dm, m)] = (real, np.where((vdom == dm) & (vmeth == m))[0])
    draws = {k: [(rng.integers(0, len(a), len(a)), rng.integers(0, len(b), len(b))) for _ in range(1000)] for k, (a, b) in groups.items()}
    _DF40.update(inv=inv, n=len(uv), groups=groups, draws=draws); return _DF40


def _df40_compute(tag):
    S = _df40_setup(); FS = {"blendface", "e4s", "facedancer", "faceswap", "fsgan", "inswap", "mobileswap", "simswap", "uniface"}
    s = np.load(DF40 / f"scores_{tag}.npz")["s"].astype(np.float64); ok = ~np.isnan(s)
    num = np.bincount(S["inv"][ok], s[ok], S["n"]); den = np.bincount(S["inv"][ok], minlength=S["n"]); V = np.where(den > 0, num / np.maximum(den, 1), np.nan)

    def auc(a, b):
        x = np.concatenate([V[a], V[b]]); y = np.r_[np.zeros(len(a)), np.ones(len(b))]; k = ~np.isnan(x)
        return roc_auc_score(y[k], x[k])

    def means(i=None):
        per = {k: (auc(a, b) if i is None else auc(a[S["draws"][k][i][0]], b[S["draws"][k][i][1]])) for k, (a, b) in S["groups"].items()}
        return {f"{dm}/{fam}": float(np.mean([v for (dd, m), v in per.items() if dd == dm and ((m in FS) == (fam == "FS"))])) for dm in ("ff", "cdf") for fam in ("FS", "FR")}

    agg = means(); bs = [means(i) for i in range(1000)]
    return {k: [round(v, 4)] + [round(float(np.percentile([b[k] for b in bs], q)), 4) for q in (2.5, 97.5)] for k, v in agg.items()}


def df40_mean(tag, d):
    """Mean-over-methods video AUC with intervals: df40_eval.json, else computed from scores_<tag>.npz (None if neither exists)."""
    if tag in d:
        return d[tag]["mean"]
    if not (DF40 / f"scores_{tag}.npz").is_file():
        return None
    if tag not in _DF40.setdefault("cache", {}):
        if "checked" not in _DF40:   # the replicated analysis must reproduce the json on a tag that is in it
            ref = "effort"; got = _df40_compute(ref); assert all(got[c] == d[ref]["mean"][c] for c in DF40_COLS), (got, d[ref]["mean"]); _DF40["checked"] = True
        _DF40["cache"][tag] = _df40_compute(tag)
        COMPUTED.setdefault("DF40 video AUC, mean over methods, 1000 video draws: df40_eval.analyse replicated on scores_<tag>.npz (tag not in df40_eval.json; replication verified on 'effort')", set()).add(tag)
    return _DF40["cache"][tag]


def tab_df40():
    d = jl(DF40 / "df40_eval.json")
    L = [r" & \multicolumn{2}{c}{FF++ domain} & \multicolumn{2}{c}{Celeb-DF domain} \\", r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}", r"Detector & FS & FR & FS & FR \\", r"\midrule"]
    row = lambda lab, m: " & ".join([lab] + [ci(m[c], 3) for c in DF40_COLS]) + r" \\"
    for k in PUB:
        m = df40_mean(k, d)
        if m:
            L.append(row(NICE[k].replace(" (own crop rebuilt)", ""), m))
    L.append(r"\midrule")
    ours = [(MAIN[0], "clipe5_s20260929"), (r"\quad second seed", "clipe5_s20260930"), (SYM[0], f"{SYM[1]}_{SEED['s1']}"), (BIN[0], "clipe5b_s20260929"), (r"\ours{}, FF++ only, three-way", "clipe5f_s20260929")]
    for lab, pre in ARMS + ARMS_E:
        for sd in ("s1", "s2", "s3"):
            tag = f"{pre}_{SEED[sd]}"
            if df40_mean(tag, d):
                ours.append((rf"\quad {lab}" + ("" if sd == "s1" else f", seed {sd[1]}"), tag))
    for lab, tag in ours:
        m = df40_mean(tag, d)
        if m:
            L.append(row(lab, m))
        else:
            MISSING.append(("df40", tag))
            if tag.startswith(PEND_TAGS):
                L.append(f"{lab} & " + " & ".join([PEND] * 4) + r" \\")
    pm = d.get("paired_main_minus", {})
    if pm:
        L += [r"\midrule", r"\multicolumn{5}{@{}l}{paired difference, \ours{} (three-way, full data) minus} \\"]
        for k, v in pm.items():
            lab = NICE.get(k, {"clipe5b_s20260929": "binary control"}.get(k, k))
            L.append(" & ".join([rf"\quad {lab}"] + [ci(v[c], 3, plus=True) for c in DF40_COLS]) + r" \\")
    return tabular("@{}l cccc@{}", L, "tab_v4_df40.tex")


def tab_df40_main():
    """Compact DF40 table for the main paper: the CLIP detectors, CADDM, and our models; point values only (intervals in tab_v4_df40.tex)."""
    d = jl(DF40 / "df40_eval.json")
    L = [r" & \multicolumn{2}{c}{FF++ domain} & \multicolumn{2}{c}{Celeb-DF domain} \\", r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}", r"Detector & FS & FR & FS & FR \\", r"\midrule"]
    cnn = [df40_mean(k, d) for k in ("xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm")]
    L.append("eight CNNs (range) & " + " & ".join(f"{min(m[c][0] for m in cnn):.3f}--{max(m[c][0] for m in cnn):.3f}" for c in DF40_COLS) + r" \\")
    rows = [(NICE[k], k) for k in ("effort", "fadapter", "gend", "dfdhr", "caddm")] + [None, (r"\ours{}", "clipe5_s20260929"), (r"\quad second seed", "clipe5_s20260930"),
            (r"\quad symmetric-view variant", f"{SYM[1]}_{SEED['s1']}"), ("binary control", "clipe5b_s20260929"), ("P0 (FF++ only)", "clipe5fbp0_s20260929"), ("P2 symmetric smoothing", "clipe5fbg0oy_s20260929")]
    for r in rows:
        if r is None:
            L.append(r"\midrule"); continue
        m = df40_mean(r[1], d)
        L.append(" & ".join([r[0]] + ([f"{m[c][0]:.3f}" for c in DF40_COLS] if m else [PEND] * 4)) + r" \\")
    return tabular("@{}l cc cc@{}", L, "tab_v4_df40_main.tex")


# ---------------------------------------------------------------- 3. smoothed-forgery evasion ----------------------------------------------
_EV = {}


def _evasion_compute(tag):
    """smooth_evasion.analyse replicated for one tag (same statistic, same 1000 video draws from default_rng(0))."""
    z = np.load(RU / f"smooth_evasion2_{tag}.npz"); S = z["S"].astype(np.float64); y = z["y"]; v = z["video"]; J = list(range(1, S.shape[1])); NL = len(J)
    if "draws" not in _EV:
        rng = np.random.default_rng(0); uv = np.unique(v); by = {k: np.where(v == k)[0] for k in uv}
        _EV["draws"] = [np.concatenate([by[k] for k in rng.choice(uv, len(uv))]) for _ in range(1000)]

    def stat(idx):
        s = S[idx]; yy = y[idx]; g, f = yy == 0, yy == 1; t = np.quantile(s[g, 0], 0.95); m0 = (s[f, 0] <= t).mean() * 100
        return [m0] + [((s[f, j] <= t).mean() * 100 - m0) for j in J] + [(s[g, j] > t).mean() * 100 for j in J]

    a = stat(np.arange(len(y))); bs = np.array([stat(dr) for dr in _EV["draws"]])
    return {"miss_untreated": round(a[0], 1), "miss_rise": [[round(a[j], 1)] + [round(float(np.percentile(bs[:, j], q)), 1) for q in (2.5, 97.5)] for j in J],
            "fa_smoothed_genuine": [round(a[j], 1) for j in [NL + k for k in J]], "auc_untreated": round(float(roc_auc_score(y, S[:, 0])), 3),
            "auc_smoothed_both": [round(float(roc_auc_score(y, S[:, j])), 3) for j in J]}


def evasion_rec(tag, e):
    """Record of the smoothed-forgery test: smooth_evasion2.json, else computed from smooth_evasion2_<tag>.npz (None if neither exists)."""
    if tag in e:
        return e[tag]
    if not (RU / f"smooth_evasion2_{tag}.npz").is_file():
        return None
    if tag not in _EV.setdefault("cache", {}):
        if "checked" not in _EV:
            ref = "clipe5fbp0_s20260929"; got = _evasion_compute(ref); assert all(got[k] == e[ref][k] for k in got), (got, e[ref]); _EV["checked"] = True
        _EV["cache"][tag] = _evasion_compute(tag)
        COMPUTED.setdefault("smoothed-forgery test: smooth_evasion.analyse replicated on smooth_evasion2_<tag>.npz (tag not in smooth_evasion2.json; replication verified on P0 seed 1)", set()).add(tag)
    return _EV["cache"][tag]


def tab_evasion():
    e = jl(RU / "smooth_evasion2.json")
    rows = [("P0", "clipe5fbp0", ("s1", "s2", "s3")), ("P2", "clipe5fb", ("s1",)), ("P2 no smoothing", "clipe5fbn", ("s1",)), ("P2 smoothing only", "clipe5fbg0o", ("s1",)),
            ("P1", "clipe5fbp1", ("s1",)), ("P1 smoothing only", "clipe5fbg0p1o", ("s1", "s2", "s3")), ("P2 symmetric smoothing", "clipe5fbg0oy", ("s1", "s2"))] \
        + [(lab, pre, ("s1",)) for lab, pre in ARMS_E] + [(MAIN[0], "clipe5", ("s1",)), (SYM[0], SYM[1], ("s1",)), (BIN[0], "clipe5b", ("s1",))]
    L = [r" & & \multicolumn{5}{c}{miss rise (points, 95\% CI)} & \multicolumn{5}{c}{false alarms, smoothed genuine (\%)} & \\",
         r"\cmidrule(lr){3-7}\cmidrule(lr){8-12}",
         r"Arm & miss untr.\ & bil.\ light & bil.\ mid & bil.\ strong & median 5 & Gauss.\ blend & bil.\ light & bil.\ mid & bil.\ strong & median 5 & Gauss.\ blend & AUC both smoothed (strong) \\", r"\midrule"]
    for lab, pre, seeds in rows:
        for sd in seeds:
            tag = f"{pre}_{SEED[sd]}"; o = evasion_rec(tag, e); name = lab if sd == "s1" else rf"\quad seed {sd[1]}"
            if o is None:
                MISSING.append(("evasion", tag))
                if pre in PEND_TAGS:
                    L.append(f"{name} & " + " & ".join([PEND] * 12) + r" \\")
                continue
            L.append(" & ".join([name, f"{o['miss_untreated']:.1f}"] + [ci(m, 1, plus=True) for m in o["miss_rise"]] + [f"{v:.1f}" for v in o["fa_smoothed_genuine"]] + [f"{o['auc_smoothed_both'][2]:.3f}"]) + r" \\")
    return tabular("@{}l c ccccc ccccc c@{}", L, "tab_v4_evasion.tex")


# ---------------------------------------------------------------- 4. trade-off per exposure arm ----------------------------------------------
def video_auc(f, skey):
    """Untreated video AUC: mean frame score per video, label per video, AUC over videos."""
    if not f.is_file():
        return None
    z = np.load(f); s = z[skey].astype(np.float64); y = z["y"]; v = z["video"]
    vid, inv = np.unique(v, return_inverse=True); ms = np.bincount(inv, weights=s) / np.bincount(inv); yv = np.zeros(len(vid), int); yv[inv] = y
    return float(roc_auc_score(yv, ms))


CDFB_ALIAS = {"clipe5_s20260929": "clipe5", "clipe5_s20260930": "clipe5-s2", "clipe5b_s20260929": "clipe5b"}   # older log names of the full-data models


def cdfb(tag):
    """Celeb-DF-B one-rule record: the JSON line of fair_RU-<tag>.log, else fair_cdfb.json, else results_v3.json."""
    for k in (tag, CDFB_ALIAS.get(tag, tag)):
        f = CDFB / f"fair_RU-{k}.log"
        if f.is_file():
            for line in reversed(f.read_text(encoding="utf-8").splitlines()):
                m = re.match(rf"RU-{re.escape(k)} (\{{.*\}})\s*$", line)
                if m:
                    return json.loads(m.group(1))
        r = jl(CDFB / "fair_cdfb.json").get(f"RU-{k}") or jl(CDFB / "results_v3.json").get(f"RU-{k}")
        if r:
            return r
    return None


def tab_tradeoff():
    s90 = jl(ALI / "smoothing90_thresholdfree.json"); pub = jl(ALI / "published_ali.json"); e = jl(RU / "smooth_evasion2.json"); d = jl(DF40 / "df40_eval.json"); mod = _eval_published_ali()
    arms = ARMS + ARMS_E + [(MAIN[0], "clipe5"), SYM, (BIN[0], "clipe5b")]
    L = [r" & \multicolumn{2}{c}{commercial Smoothing-90} & smoothed forgery & \multicolumn{2}{c}{untreated video AUC} & \multicolumn{2}{c}{Celeb-DF-B} & \multicolumn{2}{c}{DF40 reenactment AUC} \\",
         r"\cmidrule(lr){2-3}\cmidrule(lr){5-6}\cmidrule(lr){7-8}\cmidrule(lr){9-10}",
         r"Arm & above thr.\ (\%) & above own orig.\ (\%) & miss rise, strong bil. & Celeb-DF-v2 & DFD & AUC$_b$ & $\Delta$MISS$_\text{beauty}$ & FF++ dom. & Celeb-DF dom. \\", r"\midrule"]
    for lab, pre in arms:
        cells = {k: [] for k in ("fa", "up", "rise", "cdf", "dfd", "aucb", "dmiss", "ff", "cd")}; seeds = []
        for sd in ("s1", "s2", "s3"):
            tag = f"{pre}_{SEED[sd]}"
            have = any((RU / f"{p}_{tag}.npz").is_file() for p in ("ali_scores", "cdf_filtered_scores", "dfd_v3_scores")) or tag in e or tag in d or cdfb(tag)
            if not have:
                continue
            seeds.append(sd); NO = PEND if pre in PEND_TAGS else "--"; ev = evasion_rec(tag, e)
            # commercial retouching
            if pre in ("clipe5", "clipe5b"):
                kb = {"clipe5": {"s1": ("ours main", "main 3-way full"), "s2": ("ours main s2", None)}, "clipe5b": {"s1": ("ours binary control", "binary full")}}[pre].get(sd)
                b = pub.get(kb[0]) if kb else None; tf = s90.get(kb[1]) if kb and kb[1] else None
                if b and not tf and (RU / f"ali_scores_{tag}.npz").is_file():
                    z = np.load(RU / f"ali_scores_{tag}.npz"); tf = thresholdfree(z["P"][:, 1].astype(np.float64), z["group"], z["stem"]); COMPUTED.setdefault("threshold-free Smoothing-90 statistics from ali_scores npz (not in smoothing90_thresholdfree.json)", set()).add(tag)
            else:
                r = ali_arm(tag, mod); b, tf = r if r else (None, None)
            cells["fa"].append(f"{tf['fa_s90']:.1f}" if tf else NO); cells["up"].append(f"{tf['paired_up']:.1f}" if tf else NO)
            cells["rise"].append(f"{ev['miss_rise'][2][0]:+.1f}" if ev else NO)
            a = video_auc(RU / f"cdf_filtered_scores_{tag}.npz", "untreated"); cells["cdf"].append(f"{a:.3f}" if a is not None else NO)
            a2 = video_auc(RU / f"dfd_v3_scores_{tag}.npz", "s"); cells["dfd"].append(f"{a2:.3f}" if a2 is not None else NO)
            if a is not None or a2 is not None:
                COMPUTED.setdefault("untreated video AUC = roc_auc_score over videos, score = mean of frame scores per video, label per video (cdf_filtered_scores 'untreated' / dfd_v3_scores 's')", set()).add(tag)
            for k in ("cdf_filtered_scores", "dfd_v3_scores"):
                if not (RU / f"{k}_{tag}.npz").is_file():
                    MISSING.append(("tradeoff", f"{k}_{tag}"))
            c = cdfb(tag); cells["aucb"].append(f"{c['auc_beautified']:.3f}" if c else NO); cells["dmiss"].append(f"{c['d_miss_beauty_only']:+.1f}" if c else NO)
            if not c:
                MISSING.append(("tradeoff", f"fair_RU-{tag}"))
            m = df40_mean(tag, d); cells["ff"].append(f"{m['ff/FR'][0]:.3f}" if m else NO); cells["cd"].append(f"{m['cdf/FR'][0]:.3f}" if m else NO)
            if not m:
                MISSING.append(("tradeoff", f"df40 {tag}"))
        if not seeds:
            MISSING.append(("tradeoff", pre)); continue
        L.append(" & ".join([lab] + [" / ".join(cells[k]) for k in ("fa", "up", "rise", "cdf", "dfd", "aucb", "dmiss", "ff", "cd")]) + r" \\")
    return tabular("@{}l cc c cc cc cc@{}", L, "tab_v4_tradeoff.tex")


# ---------------------------------------------------------------- 4b. retouching service per operation (supplement) ---------------------------
def tab_perop():
    """Share of renders above the 5%-FPR threshold of the originals, per operation: by_op of published_ali.json (17 detectors, main,
    binary control) and, for P0 / the symmetric arm / the symmetric-view variant, the same statistic from ali_scores_<tag>.npz."""
    pub = jl(ALI / "published_ali.json"); cols = ["Whitening_90", "FaceLifting_90", "EyeEnlarging_90", "Smoothing_30", "Smoothing_60", "Smoothing_90"]
    L = [r" & \multicolumn{3}{c}{level 90} & \multicolumn{3}{c}{smoothing} \\", r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}", r"Detector & whitening & face slimming & eye enlarging & level 30 & level 60 & level 90 \\", r"\midrule"]
    for k in PUB:
        if k == "npr":
            L.append(f"{NICE[k]} & " + " & ".join([NA] * 6) + r" \\"); continue
        b = pub.get(k, {}).get("by_op")
        L.append(" & ".join([NICE[k].replace(" (own crop rebuilt)", "")] + ([f"{b[c]['fake_at_t']:.1f}" for c in cols] if b else [PEND] * 6)) + r" \\")
    L.append(r"\midrule")
    for lab, kb in ((MAIN[0], "ours main"), (BIN[0], "ours binary control")):
        b = pub.get(kb, {}).get("by_op"); L.append(" & ".join([lab] + ([f"{b[c]['fake_at_t']:.1f}" for c in cols] if b else [PEND] * 6)) + r" \\")
    for lab, tag in ((SYM[0], f"{SYM[1]}_{SEED['s1']}"), (r"\ours{}, FF++ only, P0", f"clipe5fbp0_{SEED['s1']}"), (r"\ours{}, FF++ only, P2 symmetric smoothing", f"clipe5fbg0oy_{SEED['s1']}")):
        f = RU / f"ali_scores_{tag}.npz"
        if not f.is_file():
            MISSING.append(("perop", tag)); L.append(f"{lab} & " + " & ".join([PEND] * 6) + r" \\"); continue
        z = np.load(f); s = z["P"][:, 1].astype(np.float64); g = z["group"]; t = float(np.nanquantile(s[g == "orig_0"], 0.95))
        L.append(" & ".join([lab] + [f"{(s[g == c] > t).mean() * 100:.1f}" for c in cols]) + r" \\")
        COMPUTED.setdefault("per operation: share of renders of a group above the 95th percentile of P(fake) on the originals (ali_scores npz)", set()).add(tag)
    return tabular("@{}l ccc ccc@{}", L, "tab_v4_perop.tex")


# ---------------------------------------------------------------- 5. fusion with CADDM (Addendum 37) ----------------------------------------
def tab_fusion():
    f = jl(RU / "fusion37.json")
    if not f:
        MISSING.append(("fusion", "fusion37.json")); return None
    nice = dict(NICE); nice["clipe5fbp0_s20260929"] = r"\ours{} P0 (FF++ only, no beautified views)"
    L = [r" & \multicolumn{2}{c}{commercial Smoothing-90} & \multicolumn{2}{c}{untreated video AUC} & \multicolumn{2}{c}{DF40, FF++ domain} & \multicolumn{2}{c}{DF40, Celeb-DF domain} \\",
         r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}",
         r"Score & above 5\%-FPR thr.\ (\%) & above own orig.\ (\%) & Celeb-DF-v2 & DFD & FS & FR & FS & FR \\"]
    for pair, res in f.items():
        a, b = pair.split("+"); L += [r"\midrule", rf"\multicolumn{{9}}{{@{{}}l}}{{{nice[a]} with {nice[b]}}} \\"]
        for k, lab in ((a, "first member alone"), (b, "CADDM alone"), ("mean", "fusion, mean"), ("min", "fusion, minimum"), ("prod", "fusion, product")):
            rt = res["retouch"][k]; g = lambda src, key: f"{res[src][key]:.3f}" if isinstance(res.get(src, {}).get(key), (int, float)) else PEND
            d4 = res.get("df40", {}).get(k); L.append(" & ".join([rf"\quad {lab}", f"{rt['s90_at_5fpr']:.1f}", f"{rt['s90_above_own_original']:.1f}", g("cdf", k), g("dfd", k)]
                                                                + ([f"{d4[c]:.3f}" for c in DF40_COLS] if d4 else [PEND] * 4)) + r" \\")
            if not d4:
                MISSING.append(("fusion", f"df40 {pair}"))
    return tabular("@{}l cc cc cc cc@{}", L, "tab_v4_fusion.tex")


# ---------------------------------------------------------------- 6. two-sided main table, v4 (17 detectors + symmetric-view variant) ----------
def _filt_compute(pre, tag):
    """cdf_filtered_eval.analyse statistics for one tag from <pre>_scores_<tag>.npz. Point values are those of the script; the 500 video
    draws start a fresh default_rng(1) (the script shares one generator across detectors), so the intervals are valid but not the script's digits."""
    f = RU / f"{pre}_scores_{tag}.npz"
    if not f.is_file():
        return None
    z = np.load(f); su, sf, y, v = z["untreated"].astype(np.float64), z["filtered"].astype(np.float64), z["y"], z["video"]
    vids = sorted(set(v)); vix = {k: np.where(v == k)[0] for k in vids}; rng = np.random.default_rng(1)
    boots = [np.concatenate([vix[vids[j]] for j in rng.choice(len(vids), len(vids), True)]) for _ in range(500)]

    def st(idx):
        t = np.quantile(su[idx][y[idx] == 0], 0.95); g = y[idx] == 0; k = ~g
        return {"auc_u": float(roc_auc_score(y[idx], su[idx])), "auc_f": float(roc_auc_score(y[idx], sf[idx])), "miss_u": 100 * float((su[idx][k] <= t).mean()),
                "miss_f": 100 * float((sf[idx][k] <= t).mean()), "fa_u": 100 * float((su[idx][g] > t).mean()), "fa_f": 100 * float((sf[idx][g] > t).mean())}
    a = st(np.arange(len(y))); bs = [st(b) for b in boots]; r = {k: round(vv, 4 if k.startswith("auc") else 2) for k, vv in a.items()}
    r["d_miss"] = round(a["miss_f"] - a["miss_u"], 2); r["d_fa"] = round(a["fa_f"] - a["fa_u"], 2)
    r["ci"] = {"d_miss": [round(float(np.percentile([x["miss_f"] - x["miss_u"] for x in bs], q)), 2) for q in (2.5, 97.5)],
               "d_fa": [round(float(np.percentile([x["fa_f"] - x["fa_u"] for x in bs], q)), 2) for q in (2.5, 97.5)]}
    return r


def tab_twosided_v4():
    """tab_twosided of make_tables_v3 with the CADDM and LAA-Net rows and the symmetric-view variant; the row logic is imported, not copied."""
    sys.path.insert(0, str(Path(__file__).resolve().parent)); import make_tables_v3 as v3
    v3.NICE.update({k: NICE[k].replace(" (own crop rebuilt)", "") for k in PUB})
    tag = f"{SYM[1]}_{SEED['s1']}"; rec = cdfb(tag)
    if rec and f"RU-{tag}" not in v3.cb:
        v3.cb[f"RU-{tag}"] = rec
    for pre, tab in (("cdf_filteredff", v3.cf), ("dfd_filteredff", v3.df)):
        if tag in tab:
            continue
        chk = _filt_compute(pre, "effort"); assert chk and all(chk[k] == tab["effort"][k] for k in ("auc_u", "auc_f", "d_miss", "d_fa")), (pre, chk, tab["effort"])
        r = _filt_compute(pre, tag)
        if r:
            tab[tag] = r
            COMPUTED.setdefault("filter sources (AUC, AUC_f, dMISS, dFA; own 500 video draws for the intervals): cdf_filtered_eval.analyse statistics on <src>_scores_<tag>.npz (tag not in the json; point values verified on 'effort')", set()).add(f"{pre}:{tag}")
        else:
            MISSING.append(("twosided", f"{pre}_scores_{tag}"))
    L = [r" & \multicolumn{4}{c}{Celeb-DF-B (app presets)} & \multicolumn{4}{c}{Celeb-DF-v2 + 11 held-out filters} & \multicolumn{4}{c}{DFD + 16 fresh filters} \\",
         r"\cmidrule(lr){2-5}\cmidrule(lr){6-9}\cmidrule(lr){10-13}",
         r"Detector & AUC & AUC$_b$ & $\Delta$MISS$_\text{beauty}$ & FA$_b$ & AUC & AUC$_f$ & $\Delta$MISS & $\Delta$FA & AUC & AUC$_f$ & $\Delta$MISS & $\Delta$FA \\", r"\midrule"]
    for k in PUB:
        L.append(v3.row_twosided(v3.NICE[k], k, k))
        if v3.PEND in L[-1]:
            MISSING.append(("twosided", k))
    L.append(r"\midrule")
    for kb, kf, lab in (("RU-clipe5f", "clipe5f_s20260929", r"\ours{}, FF++ only"), ("RU-clipe5", "clipe5_s20260929", r"\ours{} (full data, three-way)"), ("RU-clipe5-s2", "clipe5_s20260930", r"\quad second seed"),
                        (f"RU-{tag}", tag, r"\quad symmetric-view variant"), ("RU-clipe5b", "clipe5b_s20260929", r"same data, forged head only")):
        L.append(v3.row_twosided(lab, kb, kf))
        if v3.PEND in L[-1]:
            MISSING.append(("twosided", kf))
    return tabular("@{}l cccc cccc cccc@{}", L, "tab_v4_twosided.tex")


# ---------------------------------------------------------------- checks --------------------------------------------------------------------
def check(name):
    t = (OUT / name).read_text(encoding="utf-8"); assert t.count("{") == t.count("}"), f"{name}: unbalanced braces"
    spec = re.search(r"\\begin\{tabular\}\{(.*)\}", t).group(1); ncol = len(re.findall(r"[lcr]", re.sub(r"@\{[^}]*\}", "", spec)))
    rows = [ln for ln in t.splitlines() if ln.rstrip().endswith(r"\\") and not ln.lstrip().startswith(("\\cmidrule", "\\multicolumn{" + str(ncol)))]
    bad = []
    for ln in rows:
        n = len(re.findall(r"(?<!\\)&", ln)) + 1
        for m in re.finditer(r"\\multicolumn\{(\d+)\}", ln):
            n += int(m.group(1)) - 1
        if n != ncol:
            bad.append((n, ln))
    assert not bad, f"{name}: column count != {ncol}: {bad}"
    print(f"{name}: {len(rows)} body rows x {ncol} columns, braces balanced\n" + t)


if __name__ == "__main__":
    tab_retouch(); tab_retouch_main(); tab_df40(); tab_df40_main(); tab_evasion(); tab_tradeoff(); tab_perop(); tab_fusion(); tab_twosided_v4()
    for n in ("tab_v4_retouch.tex", "tab_v4_df40.tex", "tab_v4_evasion.tex", "tab_v4_tradeoff.tex", "tab_v4_fusion.tex", "tab_v4_twosided.tex", "tab_v4_df40_main.tex", "tab_v4_perop.tex", "tab_v4_retouch_main.tex"):
        check(n)
    print("DF40 footnote:", DF40_FOOT)
    print("missing sources:", sorted(set(MISSING)) or "none")
    print("computed (not read):"); [print("  ", k, "->", " ".join(sorted(v))) for k, v in COMPUTED.items()]
    print("tables written to", OUT)
