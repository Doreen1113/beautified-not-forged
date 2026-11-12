"""LaTeX tables for the 2026-10 rewrite (robust training over the beautification set), generated from result files only.

Sources: celebdfb_v2_20260927/fair_cdfb.json (one rule), retouch_unified_20260929/cdf_filtered.json (Celeb-DF-v2 + eleven
held-out filters), dfd_filtered.json (DFD v3 + sixteen fresh filters), dfd_v3.json, subspace_probe.json, fit_operator*.json.
python docs/paper_v2/make_tables_v3.py -> docs/paper_v2/tables/tab_twosided.tex, tab_method.tex, tab_mechanism.tex, tab_operator.tex
"""
import json
from pathlib import Path

BASE = Path(r"C:\My_Project\AIGC"); R = BASE / "results/research"; OUT = BASE / "docs/paper_v2/tables"; OUT.mkdir(parents=True, exist_ok=True)
PUB = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "univfd", "npr", "effort", "fadapter", "gend", "dfdhr"]
NICE = {"effort": "Effort~\\cite{effort}", "fadapter": "Forensics Adapter~\\cite{forensicsadapter}", "xception": "Xception", "effnb4": "EfficientNet-B4", "spsl": "SPSL",
        "f3net": "F3Net", "ucf": "UCF", "recce": "RECCE", "core": "CORE", "srm": "SRM", "sbi": "SBI~\\cite{sbi}", "univfd": "UnivFD", "npr": "NPR", "gend": "GenD~\\cite{gend2026}", "dfdhr": "DFD-HR~\\cite{dfdhr2026}"}
# our arms: (fair_cdfb key, filtered-source key, label, group)
ARMS = [("RU-clipe5f", "clipe5f_s20260929", "FF++ only, random grading", "equal"),
        ("RU-clipe5fg0", "clipe5fg0_s20260929", "FF++ only, no grading", "equal"),
        ("RU-clipe5rf_s20260929", "clipe5rf_s20260929", "FF++ only, random operator", "equal"),
        ("RU-clipe5kf_s20260929", "clipe5kf_s20260929", "FF++ only, worst of 4 draws", "equal"),
        ("RU-clipe5af_s20260929", "clipe5af_s20260929", "FF++ only, worst case (1 step)", "equal"),
        ("RU-clipe5awpf_s20260929", "clipe5awpf_s20260929", "FF++ only, plausible worst case", "equal"),
        ("RU-clipe5awpf_s20260930", "clipe5awpf_s20260930", "\\quad seed 2", "equal"),
        ("RU-clipe5awptf_s20260929", "clipe5awptf_s20260929", "FF++ only, plausible worst case, consistency", "equal"),
        ("RU-clipe5awps3f_s20260929", "clipe5awps3f_s20260929", "FF++ only, plausible worst case, 3 steps", "equal"),
        ("RU-clipe4r", "clipe4r_s20260929", "full data, no grading (RU4)", "full"),
        ("RU-clipe5", "clipe5_s20260929", "full data, random grading (RU5)", "full"),
        ("RU-clipe5-s2", "clipe5_s20260930", "\\quad seed 2", "full"),
        ("RU-clipe5b", "clipe5b_s20260929", "full data, forged head only", "full"),
        ("RU-clipe5awpb_s20260929", "clipe5awpb_s20260929", "full data, forged head only, plausible worst case", "full"),
        ("RU-clipe5awpb_s20260930", "clipe5awpb_s20260930", "\\quad seed 2", "full"),
        ("RU-clipe5awpd_s20260929", "clipe5awpd_s20260929", "full data, detached heads, plausible worst case", "full")]
PEND = r"\textit{pend.}"


def jl(p):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


cb = jl(R / "celebdfb_v2_20260927/fair_cdfb.json"); cf = jl(R / "retouch_unified_20260929/cdf_filteredff.json"); df = jl(R / "retouch_unified_20260929/dfd_filteredff.json")   # filter on the full frame (Addendum 23)


def ci(r, k, d=1):
    return f"[{r['ci'][k][0]:.{d}f}, {r['ci'][k][1]:.{d}f}]"


def row_twosided(name, kb, kf):
    b = cb.get(kb); c = cf.get(kf); d = df.get(kf)
    cells = [name]
    cells += [f"{b['auc_untreated']:.3f}", f"{b['auc_beautified']:.3f}", f"{b['d_miss_beauty_only']:+.1f} {ci(b, 'd_miss_beauty_only')}", f"{b['fa_b']:.1f}"] if b else [PEND] * 4
    for z in (c, d):
        cells += [f"{z['auc_u']:.3f}", f"{z['auc_f']:.3f}", f"{z['d_miss']:+.1f} {ci(z, 'd_miss')}", f"{z['d_fa']:+.1f} {ci(z, 'd_fa')}"] if z else [PEND] * 4
    return " & ".join(cells) + r" \\"


def tab_twosided():
    L = [r"\begin{tabular}{@{}l cccc cccc cccc@{}}", r"\toprule",
         r" & \multicolumn{4}{c}{Celeb-DF-B (app presets)} & \multicolumn{4}{c}{Celeb-DF-v2 + 11 held-out filters} & \multicolumn{4}{c}{DFD + 16 fresh filters} \\",
         r"\cmidrule(lr){2-5}\cmidrule(lr){6-9}\cmidrule(lr){10-13}",
         r"Detector & AUC & AUC$_b$ & $\Delta$MISS$_\text{beauty}$ & FA$_b$ & AUC & AUC$_f$ & $\Delta$MISS & $\Delta$FA & AUC & AUC$_f$ & $\Delta$MISS & $\Delta$FA \\", r"\midrule"]
    for k in PUB:
        L.append(row_twosided(NICE[k], k, k))
    L.append(r"\midrule")
    MAIN_ROWS = [("RU-clipe5f", "clipe5f_s20260929", r"\ours{}, FF++ only"), ("RU-clipe5", "clipe5_s20260929", r"\ours{} (full data, three-way)"),
                 ("RU-clipe5-s2", "clipe5_s20260930", r"\quad second seed"), ("RU-clipe5b", "clipe5b_s20260929", r"same data, forged head only")]   # all other arms: supplement
    for kb, kf, lab in MAIN_ROWS:
        L.append(row_twosided(lab, kb, kf))
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_twosided.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def tab_controls():
    """Equal-data arms and controls: the three sources, untreated accuracy, and the operator probe."""
    pr = jl(R / "retouch_unified_20260929/adv_probe.json")
    L = [r"\begin{tabular}{@{}l ccc cc cc cc@{}}", r"\toprule",
         r" & \multicolumn{3}{c}{Celeb-DF-B} & \multicolumn{2}{c}{Celeb-DF-v2 + filters} & \multicolumn{2}{c}{DFD + fresh filters} & \multicolumn{2}{c}{probe: genuine acc.} \\",
         r"\cmidrule(lr){2-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}\cmidrule(lr){9-10}",
         r"Training (FF++ only) & AUC & AUC$_b$ & $\Delta$MISS$_\text{beauty}$ & AUC & AUC$_f$ & AUC & AUC$_f$ & 1 step & 10 steps \\", r"\midrule"]
    for kb, kf, lab, grp in ARMS:
        if grp != "equal" or not (kb in cb or kf in cf):
            continue
        b = cb.get(kb); c = cf.get(kf); d = df.get(kf); p = pr.get(kf, {})
        cells = [lab] + ([f"{b['auc_untreated']:.3f}", f"{b['auc_beautified']:.3f}", f"{b['d_miss_beauty_only']:+.1f}"] if b else [PEND] * 3)
        cells += [f"{c['auc_u']:.3f}", f"{c['auc_f']:.3f}"] if c else [PEND] * 2
        cells += [f"{d['auc_u']:.3f}", f"{d['auc_f']:.3f}"] if d else [PEND] * 2
        cells += [f"{p['1-step']['genuine_acc']:.1f}", f"{p['10-step']['genuine_acc']:.1f}"] if p else [PEND] * 2
        L.append(" & ".join(cells) + r" \\")
    L += [r"\midrule"]
    for k in ("effort", "fadapter"):
        b = cb[k]; c = cf[k]; d = df[k]
        L.append(" & ".join([NICE[k], f"{b['auc_untreated']:.3f}", f"{b['auc_beautified']:.3f}", f"{b['d_miss_beauty_only']:+.1f}", f"{c['auc_u']:.3f}", f"{c['auc_f']:.3f}", f"{d['auc_u']:.3f}", f"{d['auc_f']:.3f}", "--", "--"]) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_controls.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def tab_exposure():
    """Who gets the beautified views: three seeds per arm (Addendum 25), Celeb-DF-B one-rule metrics and paired differences."""
    pair = jl(R / "celebdfb_v2_20260927/pair_cdfb.json")
    arms = (("P0", "no beautified views", "RU-clipe5fbp0"), ("P1", "beautified genuine faces only", "RU-clipe5fbp1"), ("P2", "beautified genuine and forged faces", "RU-clipe5fb"))
    seeds = ("s20260929", "s20260930", "s20261001")
    L = [r"\begin{tabular}{@{}llccc@{}}", r"\toprule", r"Arm & Beautified training views & AUC$_b$ (3 seeds) & $\Delta$MISS$_\text{beauty}$ (3 seeds) & FA$_b$ \\", r"\midrule"]
    for a, lab, pre in arms:
        rs = [cb.get(f"{pre}_{sd}") for sd in seeds]; rs = [r for r in rs if r]
        L.append(f"{a} & {lab} & " + " / ".join(f"{r['auc_beautified']:.3f}" for r in rs) + " & " + " / ".join(f"{r['d_miss_beauty_only']:+.1f}" for r in rs) + " & " + " / ".join(f"{r['fa_b']:.1f}" for r in rs) + r" \\")
    L += [r"\midrule", r"\multicolumn{5}{@{}l}{Paired differences, 95\% video-cluster intervals (seeds 1 / 2 / 3)} \\"]
    for lab, a, b in (("P1 $-$ P0", "RU-clipe5fbp1", "RU-clipe5fbp0"), ("P2 $-$ P0", "RU-clipe5fb", "RU-clipe5fbp0"), ("P2 $-$ P1", "RU-clipe5fb", "RU-clipe5fbp1")):
        cells = []
        for sd in seeds:
            r = pair.get(f"{a}_{sd} minus {b}_{sd}")
            cells.append(f"{r['d_miss_beauty_only']['diff']:+.1f} [{r['d_miss_beauty_only']['ci'][0]:.1f}, {r['d_miss_beauty_only']['ci'][1]:.1f}]" if r else PEND)
        L.append(rf"{lab} & $\Delta$MISS$_\text{{beauty}}$ & \multicolumn{{3}}{{l}}{{" + " / ".join(cells) + r"} \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_exposure.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def tab_reproduce():
    """Reported versus reproduced: each baseline on the DeepfakeBench crop (its own) and on ours; published numbers from published_numbers.json."""
    pub = jl(BASE / "docs/paper_v2/published_numbers.json"); dfb = jl(R / "ffpp_benchmark_20260925/dfb_crop_eval.json")
    L = [r"\begin{tabular}{@{}l cc cc cc@{}}", r"\toprule", r" & \multicolumn{2}{c}{Celeb-DF-v2 frame AUC} & \multicolumn{2}{c}{Celeb-DF-v2 video AUC} & \multicolumn{2}{c}{DFD frame AUC} \\",
         r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}", r"Detector & published & ours, DFB crop / our crop & published & ours, DFB crop / our crop & published & ours, DFB crop / our crop \\", r"\midrule"]
    for k in PUB:
        if k in ("univfd", "npr", "sbi"):
            continue
        p = pub.get(k, {}); c = dfb.get("cdf", {}).get("auc", {}); d = dfb.get("dfd", {}).get("auc", {})
        g = lambda t, key, m: f"{t[f'{k}|dfb'][m]:.3f} / {t[f'{k}|ours'][m]:.3f}" if f"{k}|dfb" in t and f"{k}|ours" in t else PEND
        f = lambda v: f"{v:.3f}" if isinstance(v, (int, float)) else "--"
        L.append(f"{NICE[k]} & {f(p.get('cdf_frame'))} & {g(c, k, 'frame')} & {f(p.get('cdf_video'))} & {g(c, k, 'video')} & {f(p.get('dfd_frame'))} & {g(d, k, 'frame')} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_reproduce.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def tab_fullframe():
    """Filter on the face crop vs on the full frame, both synthetic sources, published detectors and our main models."""
    RU = R / "retouch_unified_20260929"; A = {"cdf": (jl(RU / "cdf_filtered.json"), jl(RU / "cdf_filteredff.json")), "dfd": (jl(RU / "dfd_filtered.json"), jl(RU / "dfd_filteredff.json"))}
    L = [r"\begin{tabular}{@{}l ccc ccc@{}}", r"\toprule", r" & \multicolumn{3}{c}{Celeb-DF-v2, 11 filters} & \multicolumn{3}{c}{DFD, 16 filters} \\", r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}",
         r"Detector & AUC & AUC$_f$ crop & AUC$_f$ full frame & AUC & AUC$_f$ crop & AUC$_f$ full frame \\", r"\midrule"]
    rows = [(NICE[k], k) for k in PUB] + [(r"\ours{}", "clipe5_s20260929"), (r"\ours{}, FF++ only", "clipe5f_s20260929"), ("binary control", "clipe5b_s20260929")]
    for lab, k in rows:
        cells = [lab]
        for st in ("cdf", "dfd"):
            a, b = A[st]
            cells += [f"{a[k]['auc_u']:.3f}", f"{a[k]['auc_f']:.3f}", f"{b[k]['auc_f']:.3f}"] if k in a and k in b else [PEND] * 3
        L.append(" & ".join(cells) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_fullframe.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def tab_negative():
    """Every method arm that was tried under a pre-registered bar (FF++ only unless noted), one row each."""
    RU = R / "retouch_unified_20260929"; cff = jl(RU / "cdf_filteredff.json"); dff = jl(RU / "dfd_filteredff.json"); c0 = jl(RU / "cdf_filtered.json")
    arms = [("random colour grading (reference)", "RU-clipe5f", "clipe5f_s20260929"), ("no grading", "RU-clipe5fg0", "clipe5fg0_s20260929"),
            ("operator, random edits", "RU-clipe5rf_s20260929", "clipe5rf_s20260929"), ("operator, worst of 4 draws", "RU-clipe5kf_s20260929", "clipe5kf_s20260929"),
            ("operator, 1-step search", "RU-clipe5af_s20260929", "clipe5af_s20260929"), ("operator, search within measured edits", "RU-clipe5awpf_s20260929", "clipe5awpf_s20260929"),
            ("operator, consistency objective", "RU-clipe5awptf_s20260929", "clipe5awptf_s20260929"), ("operator, 3-step search", "RU-clipe5awps3f_s20260929", "clipe5awps3f_s20260929"),
            ("decision pooled from the evidence map", "RU-clipe5mf_s20260929", "clipe5mf_s20260929"), ("same, no beautified views", "RU-clipe5mfp0_s20260929", "clipe5mfp0_s20260929"),
            ("full data, binary (reference)", "RU-clipe5b", "clipe5b_s20260929"), ("full data, binary, operator search", "RU-clipe5awpb_s20260930", "clipe5awpb_s20260930"),
            ("released Effort, mapped (reference)", "RU-clipe5fbEi0_s20260929", "clipe5fbEi0_s20260929"), ("released Effort + 2 epochs, no beautified views", "RU-clipe5fbp0Ei_s20260929", "clipe5fbp0Ei_s20260929"),
            ("released Effort + 2 epochs, both classes", "RU-clipe5fbEi_s20260929", "clipe5fbEi_s20260929")]
    L = [r"\begin{tabular}{@{}l cccc c c@{}}", r"\toprule", r" & \multicolumn{4}{c}{Celeb-DF-B} & Celeb-DF-v2 & DFD filters \\", r"\cmidrule(lr){2-5}",
         r"Arm & AUC & AUC$_b$ & $\Delta$MISS$_\text{beauty}$ & FA$_b$ & AUC untreated & AUC$_f$ \\", r"\midrule"]
    for lab, kb, kf in arms:
        b = cb.get(kb); x = c0.get(kf) or cff.get(kf); d = dff.get(kf)
        if "reference" in lab and lab != arms[0][0]:
            L.append(r"\midrule")
        L.append(" & ".join([lab] + ([f"{b['auc_untreated']:.3f}", f"{b['auc_beautified']:.3f}", f"{b['d_miss_beauty_only']:+.1f}", f"{b['fa_b']:.1f}"] if b else [PEND] * 4)
                            + [f"{x['auc_u']:.3f}" if x else PEND, f"{d['auc_f']:.3f}" if d else PEND]) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_negative.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def tab_exposure_ext():
    """Exposure arms on the other sources and inside Effort's tuning scheme."""
    RU = R / "retouch_unified_20260929"; cff = jl(RU / "cdf_filteredff.json"); dff = jl(RU / "dfd_filteredff.json")
    groups = [("LoRA", [("P0", "clipe5fbp0"), ("P1", "clipe5fbp1"), ("P2", "clipe5fb")], ("s20260929", "s20260930", "s20261001")),
              ("Effort scheme", [("P0", "clipe5fbp0E"), ("P2", "clipe5fbE")], ("s20260929", "s20260930"))]
    L = [r"\begin{tabular}{@{}ll ccc cc cc@{}}", r"\toprule", r" & & \multicolumn{3}{c}{Celeb-DF-B} & \multicolumn{2}{c}{Celeb-DF-v2 filters} & \multicolumn{2}{c}{DFD filters} \\",
         r"\cmidrule(lr){3-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}", r"Tuning & Arm & AUC & AUC$_b$ & $\Delta$MISS$_\text{beauty}$ & AUC$_f$ & $\Delta$MISS & AUC$_f$ & $\Delta$MISS \\", r"\midrule"]
    for g, arms, seeds in groups:
        for a, pre in arms:
            bs = [cb.get(f"RU-{pre}_{sd}") for sd in seeds]; xs = [cff.get(f"{pre}_{sd}") for sd in seeds]; ds = [dff.get(f"{pre}_{sd}") for sd in seeds]
            j = lambda vals, fmt: " / ".join(fmt(v) if v else "--" for v in vals)
            L.append(" & ".join([g, a, j(bs, lambda b: f"{b['auc_untreated']:.3f}"), j(bs, lambda b: f"{b['auc_beautified']:.3f}"), j(bs, lambda b: f"{b['d_miss_beauty_only']:+.1f}"),
                                 j(xs, lambda x: f"{x['auc_f']:.3f}"), j(xs, lambda x: f"{x['d_miss']:+.1f}"), j(ds, lambda x: f"{x['auc_f']:.3f}"), j(ds, lambda x: f"{x['d_miss']:+.1f}")]) + r" \\")
        L.append(r"\midrule")
    L[-1] = r"\bottomrule"; L.append(r"\end{tabular}")
    (OUT / "tab_exposure_ext.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def tab_mechanism():
    sp = jl(R / "retouch_unified_20260929/subspace_probe.json").get("clipe5f_s20260929")
    if not sp:
        return
    L = [r"\begin{tabular}{@{}lrrrrr@{}}", r"\toprule", r"Held-out filter & $n$ & $\cos(w,\bar\Delta)$ & $\Delta$logit genuine & $\Delta$logit forged & energy in $V_{16}$ \\", r"\midrule"]
    for k, v in sorted(sp["heldout_filters"].items(), key=lambda kv: -kv[1]["d_logit_genuine"]):
        L.append(f"{k} & {v['n']} & {v['cos_w_meanshift']:.2f} & {v['d_logit_genuine']:+.2f} & {v['d_logit_forged']:+.2f} & {v['energy_in_train_V16']:.2f} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_mechanism.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    e = sp["erasure"]; o = sp["original_head"]
    L = [r"\begin{tabular}{@{}lcccc@{}}", r"\toprule", r"Forged head & AUC clean & AUC filtered & FA filtered & MISS filtered \\", r"\midrule",
         f"trained head & {o['auc_clean']:.3f} & {o['auc_filtered']:.3f} & {o['fa_filtered']:.1f} & {o['miss_filtered']:.1f} \\\\"]
    for k in ("0", "2", "8", "32"):
        v = e[k]; L.append(f"refit, {k} directions erased & {v['auc_clean']:.3f} & {v['auc_filtered']:.3f} & {v['fa_filtered']:.1f} & {v['miss_filtered']:.1f} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_erasure.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def tab_operator():
    fo = jl(R / "retouch_unified_20260929/fit_operator_wide.json") or jl(R / "retouch_unified_20260929/fit_operator.json")
    if not fo:
        return
    lab = {"tencent": "Tencent retouching", "megvii": "Megvii retouching", "pilgram_train": "training colour filters", "random_grade": "random grading"}
    L = [r"\begin{tabular}{@{}lrrrr@{}}", r"\toprule", r"Measured edit & $n$ & PSNR before & PSNR after fit & 10th pct \\", r"\midrule"]
    for k, v in fo.items():
        L.append(f"{lab[k]} & {v['n']} & {v['psnr_before']:.1f} & {v['psnr_after']:.1f} & {v['psnr_after_p10']:.1f} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_operator.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    tab_twosided(); tab_controls(); tab_exposure(); tab_reproduce(); tab_fullframe(); tab_negative(); tab_exposure_ext(); tab_mechanism(); tab_operator(); print("tables written to", OUT)
