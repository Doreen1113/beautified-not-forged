"""Tables, numbers and the new figure for paper v6 (Addenda 38-45 of results/research/retouch_unified_20260929/FINDINGS.md).
Computed from existing score / result files only; no model is run. v4 and v5 tables are left untouched; this script writes
tab_v6_*.tex, figs/fig_accuse_v6.{pdf,png} and v6_numbers.json. Formulas are logged in V6_CHANGES.md.

New sources (all read-only)
  review_v4_exps_20261016/ar_source.json        Addendum 43, Instagram AR filters (FairBeauty, its JPEG-q90 control, B-LFW)
  review_v4_exps_20261016/ffpp_val_thr.json     Addendum 44, oracle and FF++-validation (deployable) rates per source and detector
  review_v4_exps_20261016/identity_summary.json Addendum 45, intervals that change category under identity resampling
  review_v4_exps_20261016/readout42.json        Addendum 42, second seeds of the variant and the binary control
  retouch_unified_20260929/smooth38.json        Addendum 38, whole-crop and face-local smoothing of both classes
  retouch_unified_20260929/dose39.json          Addendum 39, dose response of the four released CLIP detectors
  retouch_unified_20260929/p3_readout40.json    Addendum 40, forged-only exposure P3
  df40_eval_20261012/df40_efs41.json            Addendum 41, DF40 entire-face synthesis
plus the v4 sources reused for the trade-off table (smooth_evasion2.json, ali_scores_<tag>.npz, cdf_filtered_scores, dfd_v3_scores,
fair_cdfb.json, df40_eval.json).

python docs/paper_v2/make_tables_v6.py
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import make_tables_v4 as v4   # noqa: E402  (helpers only; v4 tables are not rewritten)
import figstyle as FS          # noqa: E402

BASE = Path(r"C:\My_Project\AIGC"); R = BASE / "results/research"; OUT = HERE / "tables"
RU = R / "retouch_unified_20260929"; RV = R / "review_v4_exps_20261016"; DF40 = R / "df40_eval_20261012"; ALI = R / "alipair_zeroshot_20260929"
PUB = v4.PUB
CITE = {"xception": "Xception~\\cite{xception}", "effnb4": "EfficientNet-B4~\\cite{efficientnet}", "f3net": "F3Net~\\cite{f3net}", "spsl": "SPSL~\\cite{spsl}",
        "ucf": "UCF~\\cite{ucf}", "recce": "RECCE~\\cite{recce}", "core": "CORE~\\cite{core}", "srm": "SRM~\\cite{srm}", "sbi": "SBI~\\cite{sbi}",
        "univfd": "UnivFD$^\\ddagger$~\\cite{univfd}", "npr": "NPR$^\\ddagger$~\\cite{npr}", "effort": "Effort~\\cite{effort}",
        "fadapter": "Forensics Adapter~\\cite{forensicsadapter}", "gend": "GenD~\\cite{gend2026}", "dfdhr": "DFD-HR~\\cite{dfdhr2026}",
        "caddm": "CADDM~\\cite{caddm}", "laanetr": "LAA-Net~\\cite{laanet}"}
SHORT = {"xception": "Xception", "effnb4": "EfficientNet-B4", "f3net": "F3Net", "spsl": "SPSL", "ucf": "UCF", "recce": "RECCE", "core": "CORE",
         "srm": "SRM", "sbi": "SBI", "univfd": "UnivFD", "npr": "NPR", "effort": "Effort", "fadapter": "Forensics Adapter", "gend": "GenD",
         "dfdhr": "DFD-HR", "caddm": "CADDM", "laanetr": "LAA-Net"}
OURS = [("main s1", "clipe5_s20260929", r"\ours{}"), ("main s2", "clipe5_s20260930", r"\quad second seed"),
        ("variant s1", "clipe5y_s20260929", r"\ours{} variant"), ("variant s2", "clipe5y_s20260930", r"\quad second seed"),
        ("binary s1", "clipe5b_s20260929", "binary control"), ("binary s2", "clipe5b_s20260930", r"\quad second seed")]
NUM = {}


def jl(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def tabular(spec, lines, name):
    (OUT / name).write_text("\n".join([rf"\begin{{tabular}}{{{spec}}}", r"\toprule"] + lines + [r"\bottomrule", r"\end{tabular}"]) + "\n", encoding="utf-8")


def check(name):
    t = (OUT / name).read_text(encoding="utf-8"); assert t.count("{") == t.count("}"), name
    spec = re.search(r"\\begin\{tabular\}\{(.*)\}", t).group(1); ncol = len(re.findall(r"[lcrp]\b|[lcr]|p\{", re.sub(r"@\{[^}]*\}|>\{[^}]*\}|\{[0-9.]+\\(?:linewidth|columnwidth)\}", "", spec)))
    for ln in t.splitlines():
        if not ln.rstrip().endswith(r"\\") or ln.lstrip().startswith("\\cmidrule"):
            continue
        n = len(re.findall(r"(?<!\\)&", ln)) + 1 + sum(int(m) - 1 for m in re.findall(r"\\multicolumn\{(\d+)\}", ln))
        assert n == ncol, (name, ncol, n, ln)
    print(f"{name}: ok ({ncol} columns)")


# ============================================================ 1. trade-off table with P3 and the second seeds =========================
ARMS6 = [("P0", "clipe5fbp0"), ("P1", "clipe5fbp1"), ("P2", "clipe5fb"), ("P3", "clipe5fbp3"), ("P2-nosmooth", "clipe5fbn"), ("P2-smooth", "clipe5fbg0o"),
         ("P1-smooth", "clipe5fbg0p1o"), ("P2-sym", "clipe5fbg0oy"), ("Effort scheme, P0", "clipe5fbp0E"), ("Effort scheme, P2-sym", "clipe5fbg0oyE"),
         ("released Effort fine-tuned, no views", "clipe5fbp0Ei"), ("released Effort fine-tuned, P2-sym view", "clipe5fbg0oyEi"),
         (r"\ours{}", "clipe5"), (r"\ours{} variant", "clipe5y"), ("binary control", "clipe5b")]


def tradeoff():
    """Same cells as make_tables_v4.tab_tradeoff (+ v5's 'AUC both smoothed'), with two changes: the forged-only arm P3 (Addendum 40)
    and the second seeds of the variant and binary control (Addendum 42). Smoothing-90 cells of our full-data models are computed from
    ali_scores_<tag>.npz with make_tables_v4.thresholdfree for every seed (for seed 1 asserted equal to smoothing90_thresholdfree.json)."""
    s90 = v4.jl(ALI / "smoothing90_thresholdfree.json"); e = v4.jl(RU / "smooth_evasion2.json"); d = v4.jl(DF40 / "df40_eval.json")
    rows = {}
    for lab, pre in ARMS6:
        cells = {k: [] for k in ("fa", "up", "rise", "aucs", "cdf", "dfd", "aucb", "dmiss", "ff", "cd")}
        for sd in ("s1", "s2", "s3"):
            tag = f"{pre}_{v4.SEED[sd]}"; f = RU / f"ali_scores_{tag}.npz"; ev = v4.evasion_rec(tag, e); c = v4.cdfb(tag); m = v4.df40_mean(tag, d)
            if not (f.is_file() or ev or c or m):
                continue
            tf = None
            if f.is_file():
                z = np.load(f); tf = v4.thresholdfree(z["P"][:, 1].astype(np.float64), z["group"], z["stem"])
                ref = {"clipe5_s20260929": "main 3-way full", "clipe5b_s20260929": "binary full"}.get(tag)
                if ref and ref in s90:
                    assert abs(tf["fa_s90"] - s90[ref]["fa_s90"]) < 0.06 and abs(tf["paired_up"] - s90[ref]["paired_up"]) < 0.06, (tag, tf, s90[ref])
            cells["fa"].append(f"{tf['fa_s90']:.1f}" if tf else "--"); cells["up"].append(f"{tf['paired_up']:.1f}" if tf else "--")
            cells["rise"].append(f"{ev['miss_rise'][2][0]:+.1f}" if ev else "--"); cells["aucs"].append(f"{ev['auc_smoothed_both'][2]:.3f}" if ev else "--")
            a = v4.video_auc(RU / f"cdf_filtered_scores_{tag}.npz", "untreated"); cells["cdf"].append(f"{a:.3f}" if a is not None else "--")
            a2 = v4.video_auc(RU / f"dfd_v3_scores_{tag}.npz", "s"); cells["dfd"].append(f"{a2:.3f}" if a2 is not None else "--")
            cells["aucb"].append(f"{c['auc_beautified']:.3f}" if c else "--"); cells["dmiss"].append(f"{c['d_miss_beauty_only']:+.1f}" if c else "--")
            cells["ff"].append(f"{m['ff/FR'][0]:.3f}" if m else "--"); cells["cd"].append(f"{m['cdf/FR'][0]:.3f}" if m else "--")
        rows[lab] = {k: " / ".join(v) for k, v in cells.items()}
    # the v5 rows must be reproduced wherever v5 had the same seeds (only P3 and the added seeds may differ)
    v5 = {}
    for ln in (OUT / "tab_v5_tradeoff_main.tex").read_text(encoding="utf-8").splitlines():
        if ln.endswith(r"\\") and " & " in ln and not ln.startswith(("Arm", " &")):
            c = ln[:-2].rstrip().split(" & "); v5[c[0]] = c[1:]
    for lab, r in rows.items():
        if lab in v5 and lab not in (r"\ours{}", r"\ours{} variant", "binary control"):
            got = [r[k] for k in ("fa", "up", "rise", "aucs", "cdf", "aucb", "ff")]
            assert got == v5[lab], (lab, got, v5[lab])
        if lab in (r"\ours{}", r"\ours{} variant", "binary control"):   # seed-1 part must equal v5
            got = [r[k].split(" / ")[0] for k in ("fa", "up", "rise", "aucs", "cdf", "aucb", "ff")]
            assert got == [c.split(" / ")[0] for c in v5[lab]], (lab, got, v5[lab])
    full = [r" & \multicolumn{2}{c}{commercial Smoothing-90} & \multicolumn{2}{c}{smoothed Celeb-DF-v2 (strong bil.)} & \multicolumn{2}{c}{untreated video AUC} & \multicolumn{2}{c}{Celeb-DF-B (frame)} & \multicolumn{2}{c}{DF40 FR video AUC} \\",
            r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}\cmidrule(lr){10-11}",
            r"Arm & accused (\%) & above own orig.\ (\%) & miss rise & frame AUC, both smoothed & Celeb-DF-v2 & DFD & AUC$_b$ & $\Delta$MISS$_\text{beauty}$ & FF++ dom. & Celeb-DF dom. \\", r"\midrule"]
    main = [r" & \multicolumn{2}{c}{commercial Smoothing-90} & \multicolumn{2}{c}{smoothed Celeb-DF-v2} & Celeb-DF-v2 & Celeb-DF-B & DF40 FR \\",
            r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}",
            r"Arm & accused (\%) & above own orig.\ (\%) & miss rise & frame AUC & video AUC & frame AUC$_b$ & video AUC \\", r"\midrule"]
    for lab, r in rows.items():
        full.append(" & ".join([lab] + [r[k] for k in ("fa", "up", "rise", "aucs", "cdf", "dfd", "aucb", "dmiss", "ff", "cd")]) + r" \\")
        main.append(" & ".join([lab] + [r[k] for k in ("fa", "up", "rise", "aucs", "cdf", "aucb", "ff")]) + r" \\")
    tabular("@{}l cc cc cc cc cc@{}", full, "tab_v6_tradeoff.tex"); tabular("@{}l cc cc c c c@{}", main, "tab_v6_tradeoff_main.tex")
    NUM["tradeoff_rows"] = rows
    return rows


# ============================================================ 2. commercial table with the deployable column ===========================
def retouch_main():
    """tab_v5_retouch_main.tex plus one column: accused share of Smoothing-90 at the FF++-validation threshold (Addendum 44)."""
    th = jl(RV / "ffpp_val_thr.json")["sources"]["commercial retouching"]
    key = {CITE[k]: k for k in PUB}; key.update({r"\ours{}$^\dagger$": "clipe5_s20260929", r"\quad \ours{} variant$^\dagger$": "clipe5y_s20260929",
                                                   r"binary control$^\dagger$": "clipe5b_s20260929"})
    out = []
    for ln in (OUT / "tab_v5_retouch_main.tex").read_text(encoding="utf-8").splitlines():
        if ln.startswith(r"\begin{tabular}"):
            out.append(r"\begin{tabular}{@{}l ccccc@{}}"); continue
        if ln.startswith("Detector &"):
            out.append(ln[:-2].rstrip() + r" & FF++-val.\ thr.\ (\%) \\"); continue
        if ln.endswith(r"\\") and " & " in ln:
            lab = ln.split(" & ")[0]; k = key.get(lab)
            v = "n/a" if k == "npr" else (f"{th[k]['Smoothing_90']['deploy']:.1f}" if k in th else "--")
            if k in th and k != "npr":   # the oracle column must equal the 5%-FPR rate of the threshold file
                assert abs(th[k]["Smoothing_90"]["oracle"] - float(ln[:-2].split(" & ")[-1])) < 0.06, (lab, th[k], ln)
            out.append(ln[:-2].rstrip() + f" & {v} " + r"\\"); continue
        out.append(ln)
    (OUT / "tab_v6_retouch_main.tex").write_text("\n".join(out) + "\n", encoding="utf-8")
    NUM["s90_deployable"] = {k: th[k]["Smoothing_90"]["deploy"] for k in th}


# ============================================================ 3. accusation heatmap (four sources x 17 detectors) =====================
ORDER = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "caddm", "laanetr", "univfd", "npr", "effort", "fadapter", "gend", "dfdhr"]
OURS_FIG = [("Ours (main)", "clipe5_s20260929"), ("Ours variant", "clipe5y_s20260929"), ("Binary control", "clipe5b_s20260929")]


def heat_values():
    th = jl(RV / "ffpp_val_thr.json")["sources"]; ar = jl(RV / "ar_source.json"); sm = jl(RU / "smooth38.json")
    cols = [("Presets\nCDF-B", lambda k: th["Celeb-DF-B"][k]["real_beautified"]["oracle"]),
            ("Colour\nDFD", lambda k: th["DFD + colour filters (full frame)"][k]["genuine filtered"]["oracle"]),
            ("Service\nS-90", lambda k: None if k == "npr" else th["commercial retouching"][k]["Smoothing_90"]["oracle"]),
            ("AR\nFB", lambda k: ar["fb"][k]["accused"]),
            ("AR\nB-LFW", lambda k: ar["blfw"][k]["accused"]),
            ("Face-\nlocal", lambda k: sm[k]["forms"]["fl06"]["fa"][0])]
    keys = ORDER + [t for _, t in OURS_FIG]
    M = np.array([[np.nan if f(k) is None else float(f(k)) for _, f in cols] for k in keys])
    # cross-checks against the published per-source records
    assert abs(M[ORDER.index("sbi"), 0] - 1.8) < 0.06 and abs(M[ORDER.index("gend"), 2] - 68.7) < 0.06 and abs(M[ORDER.index("dfdhr"), 3] - 85.9) < 0.06
    assert abs(M[len(ORDER), 3] - 75.1) < 0.06 and abs(M[len(ORDER), 4] - 86.7) < 0.06 and abs(M[len(ORDER), 5] - 5.8) < 0.06
    NUM["heatmap"] = {"columns": [c.replace("\n", " ") for c, _ in cols], "rows": keys, "values": [[None if np.isnan(x) else round(float(x), 1) for x in r] for r in M]}
    return cols, keys, M


def fig_accuse():
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize
    FS.apply(); cols, keys, M = heat_values(); labels = [SHORT[k] for k in ORDER] + [l for l, _ in OURS_FIG]
    fig, ax = plt.subplots(figsize=(FS.COL, 3.45), layout="constrained")
    cmap = plt.get_cmap(FS.SEQ_CMAP).copy(); cmap.set_bad(FS.LIGHT); norm = Normalize(0, 100)
    ax.imshow(np.ma.masked_invalid(M), cmap=cmap, norm=norm, aspect="auto", interpolation="nearest")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]; txt = "n/a" if np.isnan(v) else f"{v:.0f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=FS.FS_NOTE, color="white" if (not np.isnan(v) and v > 55) else FS.INK)
    ax.set_xticks(range(M.shape[1])); ax.set_xticklabels([c for c, _ in cols], fontsize=FS.FS_NOTE, linespacing=0.95)
    ax.xaxis.tick_top(); ax.tick_params(axis="x", length=0, pad=1.5)
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=FS.FS_NOTE); ax.tick_params(axis="y", length=0, pad=1.5)
    for i, k in enumerate(keys):
        fam = "ours" if i >= len(ORDER) else FS.family_of(k)
        ax.get_yticklabels()[i].set_color({"ours": FS.OURS, "clip": FS.INK, "cnn": FS.INK}[fam])
    for y in (10.5, 12.5, 16.5):   # CNN detectors | general detectors | CLIP detectors | ours
        ax.axhline(y, color="white", lw=1.6)
    ax.axvline(4.5, color="white", lw=1.6)
    for s in ax.spines.values():
        s.set_visible(False)
    FS.save(fig, HERE / "figs" / "fig_accuse_v6")


# ============================================================ 4. supplement tables ====================================================
def tab_ar():
    ar = jl(RV / "ar_source.json")
    L = [r" & \multicolumn{4}{c}{FairBeauty (2,927 pairs)} & \multicolumn{3}{c}{B-LFW (3,000 pairs, 2,016 identities)} \\", r"\cmidrule(lr){2-5}\cmidrule(lr){6-8}",
         r"Detector & accused (\%) [95\% CI] & AUROC & above own orig.\ (\%) & accused, JPEG q90 & accused (\%) [95\% CI] & AUROC & above own orig.\ (\%) \\", r"\midrule"]
    def row(lab, k):
        a, j, b = ar["fb"][k], ar["fbj"][k], ar["blfw"][k]
        c = lambda r: f"{r['accused']:.1f} [{r['ci']['accused'][0]:.1f}, {r['ci']['accused'][1]:.1f}]"
        return " & ".join([lab, c(a), f"{a['auc']:.3f}", f"{a['paired']:.1f}", f"{j['accused']:.1f}", c(b), f"{b['auc']:.3f}", f"{b['paired']:.1f}"]) + r" \\"
    for k in PUB:
        L.append(row(CITE[k], k))
    L.append(r"\midrule")
    for lab, k in ((r"\ours{}", "clipe5_s20260929"), (r"\ours{} variant", "clipe5y_s20260929"), (r"\quad second seed", "clipe5y_s20260930"),
                   ("binary control", "clipe5b_s20260929"), (r"\quad second seed", "clipe5b_s20260930")):
        L.append(row(lab + r"$^\dagger$", k))
    tabular("@{}l cccc ccc@{}", L, "tab_v6_ar.tex")
    NUM["ar_published_accusing"] = {s: sum(bool(ar[s][k]["accuses"]) for k in PUB) for s in ("fb", "fbj", "blfw")}
    NUM["ar_pipeline_ratio"] = ar["pipeline_ratio_fbj_over_fb"]; NUM["ar_spearman_vs_commercial"] = ar["spearman_vs_commercial_smoothing90"]


FORMS = [("bil9", "bil.\\ light"), ("bil15", "bil.\\ mid"), ("bil21", "bil.\\ strong"), ("median5", "median 5"), ("gblend", "Gauss.\\ blend"),
         ("fl06", "face-local 0.06"), ("fl12", "face-local 0.12")]


def tab_smooth38():
    s = jl(RU / "smooth38.json")
    L = [r" & \multicolumn{7}{c}{false alarms on smoothed genuine frames (\%), and in parentheses the change of the miss rate on smoothed forgeries (points)} \\",
         r"\cmidrule(lr){2-8}", "Model & " + " & ".join(f for _, f in FORMS) + r" \\", r"\midrule"]
    def row(lab, k):
        f = s[k]["forms"]
        return " & ".join([lab] + [f"{f[x]['fa'][0]:.1f} ({f[x]['miss_rise'][0]:+.1f})" for x, _ in FORMS]) + r" \\"
    for k in PUB:
        L.append(row(CITE[k], k))
    L.append(r"\midrule")
    arms = [("P0", "clipe5fbp0_s20260929"), (r"\quad seed 2", "clipe5fbp0_s20260930"), (r"\quad seed 3", "clipe5fbp0_s20261001"), ("P1-smooth", "clipe5fbg0p1o_s20260929"),
            ("P2", "clipe5fb_s20260929"), (r"\quad seed 2", "clipe5fb_s20260930"), ("P2-sym", "clipe5fbg0oy_s20260929"), (r"\quad seed 2", "clipe5fbg0oy_s20260930"),
            ("P3", "clipe5fbp3_s20260929"), (r"\ours{}$^\dagger$", "clipe5_s20260929"), (r"\ours{} variant$^\dagger$", "clipe5y_s20260929"),
            (r"binary control$^\dagger$", "clipe5b_s20260929")]
    for lab, k in arms:
        L.append(row(lab, k))
    tabular("@{}l ccccccc@{}", L, "tab_v6_smooth38.tex")
    cnt = {x: {c: sum(s[k]["forms"][x]["class"] == c for k in PUB) for c in ("accuses", "lets through", "both", "neither")} for x, _ in FORMS}
    NUM["smooth38_classes_published"] = cnt; NUM["smooth38_n"] = {k: s[k] for k in ("n_frames", "n_genuine", "n_forged", "n_videos")}


def tab_dose():
    d = jl(RU / "dose39.json")
    lv = [("vig010", "vignette 0.1"), ("vig080", "vignette 0.8"), ("fl03", "face-local 0.03"), ("fl12", "face-local 0.12"), ("bil9", r"bil.\ light"), ("bil21", r"bil.\ strong")]
    L = [r"Detector (gap) & " + " & ".join(b for _, b in lv) + r" & dose response \\", r"\midrule"]
    for k in ("effort", "fadapter", "gend", "dfdhr"):
        r = d[k]; cells = []
        for a, _ in lv:
            x = r["levels"][a]; m = x["median_dlogit"]
            cells.append(f"{m[0]:+.2f} [{m[1]:+.2f}, {m[2]:+.2f}] / {x['dlogit_over_gap']:.2f}")
        dtxt = " / ".join("yes" if r[f"dose_response_{f}"] else "no" for f in ("vignette", "face_local_smoothing", "whole_crop_bilateral"))
        L.append(" & ".join([f"{SHORT[k]} ({r['gap_forged_minus_genuine_logit']:.2f})"] + cells + [dtxt]) + r" \\")
    tabular("@{}l " + "c" * len(lv) + " c@{}", L, "tab_v6_dose.tex")
    NUM["dose39"] = {k: {kk: v for kk, v in d[k].items() if kk != "levels"} for k in d}


def tab_deploy():
    t = jl(RV / "ffpp_val_thr.json"); th = t["threshold"]; s = t["sources"]
    cols = [("Celeb-DF-B", "real", "CDF-B untr."), ("Celeb-DF-B", "real_beautified", "CDF-B beaut."), ("Celeb-DF-B", "synthesis_beautified", "CDF-B beaut.\\ forged (miss)"),
            ("DFD + colour filters (full frame)", "genuine filtered", "DFD filt."), ("commercial retouching", "originals", "service orig."),
            ("commercial retouching", "Smoothing_90", "Smoothing-90"), ("FairBeauty AR", "renders", "FairBeauty"), ("B-LFW AR", "renders", "B-LFW")]
    L = ["Detector & threshold [CI] & " + " & ".join(c for _, _, c in cols) + r" \\", r"\midrule"]
    def row(lab, k):
        c = [f"{th[k]['t']:.2f} [{th[k]['ci'][0]:.2f}, {th[k]['ci'][1]:.2f}]"]
        for src, cond, _ in cols:
            r = s[src].get(k, {}).get(cond)
            c.append("n/a" if (k == "npr" and src == "commercial retouching") else (f"{r['deploy']:.1f} / {r['oracle']:.1f}" if r else "--"))
        return " & ".join([lab] + c) + r" \\"
    for k in PUB:
        L.append(row(CITE[k], k))
    L.append(r"\midrule")
    for lab, k in ((r"\ours{}", "clipe5_s20260929"), (r"\quad second seed", "clipe5_s20260930"), (r"\ours{} variant", "clipe5y_s20260929"),
                   (r"\quad second seed", "clipe5y_s20260930"), ("binary control", "clipe5b_s20260929"), (r"\quad second seed", "clipe5b_s20260930")):
        L.append(row(lab + r"$^\dagger$", k))
    tabular("@{}l c " + "c" * len(cols) + "@{}", L, "tab_v6_deploy.tex")
    NUM["deploy_rank_spearman"] = t["ranking_oracle_vs_deploy"]


def tab_identity():
    i = jl(RV / "identity_summary.json"); ib = jl(RV / "identity_boot.json")   # identity_boot.json is the later run (second seeds included)
    nice = lambda q: re.sub(r"clipe5_s20260929", r"\\ours{}", re.sub(r"clipe5_s20260930", r"\\ours{} s2", re.sub(r"clipe5b_s20260929", "binary", re.sub(
        r"clipe5y_s20260929", "variant", re.sub(r"clipe5f_s20260929", "FF++-only three-way", re.sub(r"clipe5y_s20260930", "variant s2", re.sub(r"clipe5b_s20260930", "binary s2", q))))))).replace("_", r"\_")
    L = [r"Source & quantity & estimate & video CI & identity CI & change \\", r"\midrule"]
    for c in ib["category_changes"]:
        c = dict(c, video_cat=c["categories"]["video"], identity_cat=c["categories"]["identity"])
        L.append(" & ".join([c["source"], nice(c["quantity"]), f"{c['estimate']:+.4f}" if abs(c["estimate"]) < 1 else f"{c['estimate']:+.2f}",
                             f"[{c['video'][0]:+.3f}, {c['video'][1]:+.3f}]", f"[{c['identity'][0]:+.3f}, {c['identity'][1]:+.3f}]",
                             f"{c['video_cat']} $\\rightarrow$ {c['identity_cat']}"]) + r" \\")
    tabular("@{}l l c c c l@{}", L, "tab_v6_identity.tex")
    NUM["identity"] = {"first_run": {"n_intervals": i["n_intervals"], "n_changed": len(i["changed"]), "widening": i["widening"], "units": i["units"]},
                       "rerun_with_second_seeds": {"n_changed": len(ib["category_changes"])}}


def tab_efs():
    e = jl(DF40 / "df40_efs41.json"); meth = ["sd2.1", "DiT", "SiT", "ddim", "pixart", "StyleGAN3"]
    L = ["Detector & " + " & ".join(meth) + r" \\", r"\midrule"]
    for lab, k in (("Effort~\\cite{effort}", "effort"), ("Forensics Adapter~\\cite{forensicsadapter}", "fadapter"), ("GenD~\\cite{gend2026}", "gend"),
                   ("DFD-HR~\\cite{dfdhr2026}", "dfdhr"), (r"\ours{}$^\dagger$", "clipe5_s20260929"), (r"\ours{} variant$^\dagger$", "clipe5y_s20260929"),
                   (r"binary control$^\dagger$", "clipe5b_s20260929")):
        L.append(" & ".join([lab] + [f"{e[k][m + '/ff']['above_thr']:.1f} / {e[k][m + '/cdf']['above_thr']:.1f}" for m in meth]) + r" \\")
    L += [r"\midrule", r"\multicolumn{7}{@{}l}{\ours{}, native three-way decision, share called \emph{beautified} (FF++ / Celeb-DF domain, \%)} \\",
          r"\quad beautified & " + " & ".join(f"{e['clipe5_s20260929'][m + '/ff']['native_real_fake_beautified'][2]:.1f} / {e['clipe5_s20260929'][m + '/cdf']['native_real_fake_beautified'][2]:.1f}" for m in meth) + r" \\"]
    tabular("@{}l cccccc@{}", L, "tab_v6_efs.tex")
    NUM["efs41"] = e


def tab_seeds():
    r = jl(RV / "readout42.json"); a1, a2 = r["20260929"]["A_symmetric_vs_main"], r["20260930"]["A_symmetric_vs_main"]
    b1, b2 = r["20260929"]["B_binary_minus_main"], r["20260930"]["B_binary_minus_main"]; rep = r["replication"]
    fa = lambda a: f"{'/'.join(f'{x:.1f}' for x in a['i_smoothed_genuine_FA']['variant'][:3])} (main {'/'.join(f'{x:.1f}' for x in a['i_smoothed_genuine_FA']['main'][:3])})"
    com = lambda a: f"{a['ii_commercial']['variant']['smoothing90_accused']:.1f}, {a['ii_commercial']['variant']['smoothing90_above_own']:.1f} (main {a['ii_commercial']['main']['smoothing90_accused']:.1f}, {a['ii_commercial']['main']['smoothing90_above_own']:.1f})"
    vid = lambda a: f"{a['iii_cdf_video']['diff']:+.3f} [{a['iii_cdf_video']['ci'][0]:+.3f}, {a['iii_cdf_video']['ci'][1]:+.3f}] / {a['iii_dfd_video']['diff']:+.3f} [{a['iii_dfd_video']['ci'][0]:+.3f}, {a['iii_dfd_video']['ci'][1]:+.3f}]"
    flp = lambda a: "/".join(f"{a['iv_flip']['variant'][x]:.1f}" for x in ("donor", "sd", "sdxl")) + " vs " + "/".join(f"{a['iv_flip']['main'][x]:.1f}" for x in ("donor", "sd", "sdxl"))
    aub = lambda a: f"{a['v_cdfb_auc_b']['variant']:.3f} vs {a['v_cdfb_auc_b']['main']:.3f}"
    yn = lambda k: "yes" if rep[k]["replicated"] else "no"
    L = [r"Criterion & seed 1 & seed 2 & replicated \\", r"\midrule",
         r"\multicolumn{4}{@{}l}{(A) symmetric-view variant against \ours{}, same seed} \\",
         rf"(i) whole-crop smoothed genuine FA $\le$15\% (bil.\ light/mid/strong) & {fa(a1)} & {fa(a2)} & {yn('A (i)')} \\",
         rf"(ii) Smoothing-90 accused $\le$15, above own in [25, 75] & {com(a1)} & {com(a2)} & {yn('A (ii)')} \\",
         rf"(iii) video AUC Celeb-DF-v2 / DFD not lower by $>$0.010 & {vid(a1)} & {vid(a2)} & {yn('A (iii)')} \\",
         rf"(iv) explanation flip not lower by $>$1.0 (donor/SD/SDXL) & {flp(a1)} & {flp(a2)} & {yn('A (iv)')} \\",
         rf"(v) Celeb-DF-B AUC$_b$ not lower by $>$0.010 & {aub(a1)} & {aub(a2)} & {yn('A (v)')} \\", r"\midrule",
         r"\multicolumn{4}{@{}l}{(B) binary control minus \ours{}, same seed} \\"]
    lab = {"cdf_frame": "Celeb-DF-v2 frame AUC", "cdf_video": "Celeb-DF-v2 video AUC", "dfd_frame": "DFD frame AUC", "dfd_video": "DFD video AUC",
           "cdfb_auc_b": "Celeb-DF-B AUC$_b$", "df40_ff_FR": "DF40 FR, FF++ domain", "df40_cdf_FR": "DF40 FR, Celeb-DF domain"}
    rk = {"cdf_frame": "B cdf_frame", "cdf_video": "B cdf_video", "dfd_frame": "B dfd_frame", "dfd_video": "B dfd_video", "cdfb_auc_b": "B cdfb_auc_b",
          "df40_ff_FR": "B df40_reenactment ff/FR", "df40_cdf_FR": "B df40_reenactment cdf/FR"}
    for k in lab:
        if k.startswith("df40_"):
            dk = "ff/FR" if k == "df40_ff_FR" else "cdf/FR"; x1 = b1["df40_reenactment"][dk]; x2 = b2["df40_reenactment"][dk]
        else:
            x1, x2 = b1[k], b2[k]
        f = lambda x: f"{x['diff']:+.3f} [{x['ci'][0]:+.3f}, {x['ci'][1]:+.3f}]"
        L.append(f"{lab[k]} & {f(x1)} & {f(x2)} & {yn(rk[k])} " + r"\\")
    tabular("@{}>{\\raggedright\\arraybackslash}p{0.34\\linewidth} c c c@{}", L, "tab_v6_seeds.tex")
    NUM["readout42"] = r


def tab_p3():
    p = jl(RU / "p3_readout40.json")
    L = [r"Arm & Smoothing-90 accused (\%) [CI] & above own (\%) & FA bil.\ light/mid/strong/med./blend & face-local 0.06/0.12 & DF40 FR ff / cdf \\", r"\midrule"]
    sm = jl(RU / "smooth38.json"); tags = {"P0": "clipe5fbp0_s20260929", "P1": None, "P2": "clipe5fb_s20260929", "P3": "clipe5fbp3_s20260929"}
    for a in ("P0", "P1", "P2", "P3"):
        r = p[a]; s = r["smoothing90_at_5fpr"]; fl = sm[tags[a]]["forms"] if tags[a] else None
        flc = f"{fl['fl06']['fa'][0]:.1f} / {fl['fl12']['fa'][0]:.1f}" if fl else "--"
        L.append(" & ".join([a, f"{s[0]:.1f} [{s[1]:.1f}, {s[2]:.1f}]", f"{r['smoothing90_above_own_original']:.1f}",
                             " / ".join(f"{x:.1f}" for x in r["fa_smoothed_genuine_bil9_15_21_med5_gblend"]), flc,
                             f"{r['df40_mean']['ff/FR'][0]:.3f} / {r['df40_mean']['cdf/FR'][0]:.3f}"]) + r" \\")
    tabular("@{}l c c c c c@{}", L, "tab_v6_p3.tex")
    NUM["p3"] = {k: p[k] for k in p if k.startswith("P3_minus")}; NUM["p3_reading"] = p.get("reading")


if __name__ == "__main__":
    tradeoff(); retouch_main(); fig_accuse(); tab_ar(); tab_smooth38(); tab_dose(); tab_deploy(); tab_identity(); tab_efs(); tab_seeds(); tab_p3()
    for n in ("tab_v6_tradeoff.tex", "tab_v6_tradeoff_main.tex", "tab_v6_retouch_main.tex", "tab_v6_ar.tex", "tab_v6_smooth38.tex", "tab_v6_dose.tex",
              "tab_v6_deploy.tex", "tab_v6_identity.tex", "tab_v6_efs.tex", "tab_v6_seeds.tex", "tab_v6_p3.tex"):
        check(n)
    (HERE / "v6_numbers.json").write_text(json.dumps(NUM, indent=1, default=str), encoding="utf-8")
    print("computed (not read):", {k: sorted(v) for k, v in v4.COMPUTED.items()})
