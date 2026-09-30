"""LaTeX tables for docs/paper_v2/main.tex, generated from result files only. Re-run after new results land.

python docs/paper_v2/make_tables.py -> docs/paper_v2/tables/*.tex
"""
import json
from pathlib import Path

import numpy as np

BASE = Path(r"C:\My_Project\AIGC")
R = BASE / "results/research"
OUT = BASE / "docs/paper_v2/tables"; OUT.mkdir(parents=True, exist_ok=True)
PUB = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter", "univfd", "npr"]
NICE = {"effort": "Effort (CLIP-L/14)", "fadapter": "Forensics Adapter (CLIP-L/14)", "xception": "Xception", "effnb4": "EfficientNet-B4", "spsl": "SPSL", "f3net": "F3Net", "ucf": "UCF",
        "recce": "RECCE", "core": "CORE", "srm": "SRM", "sbi": "SBI", "univfd": "UnivFD", "npr": "NPR"}
PEND = r"\textit{pend.}"


def jl(p):
    p = Path(p)
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def log_json(p, prefix):
    p = Path(p)
    if not p.is_file():
        return None
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.startswith(prefix + " "):
            return json.loads(l[len(prefix) + 1:])
    return None


def f3(x):
    return PEND if x is None else f"{x:.3f}"


def f1(x):
    return PEND if x is None else f"{x:.1f}"


bench = jl(R / "ffpp_benchmark_20260925/benchmark_final.json")
cdf = jl(R / "ffpp_benchmark_20260925/cdf_protocol_comparison_v2.json")
dfd = jl(R / "ffpp_benchmark_20260925/cdf_protocol_comparison_dfdv2.json")
cb = jl(R / "celebdfb_v2_20260927/results_v3.json")
tri = jl(R / "tripair_20260927/eval_tripair.json")["arms"]
hyb1 = log_json(R / "sbiscale_20260926/eval_SBI.log", "HYB")
sbiL = log_json(R / "sbiscale_20260926/eval_SBI.log", "SBI")
hyb2 = jl(R / "sbiscale_20260926/eval_sbiscale_HYBisSEED2.json")["HYB"]
fasbL = jl(R / "sbiscale_20260926/eval_sbiscale_HYBisSEED2.json")["FASB"]
# seed-1 B1 was computed in the eval_SBI run (12 detectors incl. SBI-L); that json was later overwritten, the verdict row survives
_row = [l for l in (R / "sbiscale_20260926/eval_SBI.log").read_text(encoding="utf-8").splitlines() if l.startswith("| HYB-L |")][0]
hyb1["b1_dominated_by"] = [] if "none (of 12)" in _row else ["see eval_SBI.log"]
hyb1["b1_n_detectors"] = 12
sbifix = jl(R / "sbifix_20260927/eval_sbifix.json") or {}
cgdD = jl(R / "cgd_20260927/eval_cgd_detect.json") or {}
ru1 = (jl(R / "retouch_unified_20260929/eval_ru_effb4_s20260929.json") or {}).get("ffpp")
ru2 = (jl(R / "retouch_unified_20260929/eval_ru_ru2_effb4_s20260929.json") or {}).get("ffpp")
ru2b = (jl(R / "retouch_unified_20260929/eval_ru_ru2_effb4_s20260930.json") or {}).get("ffpp")
ru3 = (jl(R / "retouch_unified_20260929/eval_ru_ru3_effb4_s20260929.json") or {}).get("ffpp")
ru3e = (jl(R / "retouch_unified_20260929/eval_ru_ru3e_effb4_s20260929.json") or {}).get("ffpp")
ruclip = (jl(R / "retouch_unified_20260929/eval_ru_clipe_s20260929.json") or {}).get("ffpp")
ruclip2 = (jl(R / "retouch_unified_20260929/eval_ru_clipe_s20260930.json") or {}).get("ffpp")
ruclip4 = (jl(R / "retouch_unified_20260929/eval_ru_clipe4_s20260929.json") or {}).get("ffpp")
ru4e = (jl(R / "retouch_unified_20260929/eval_ru_ru4e_effb4_s20260929.json") or {}).get("ffpp")

OURS = [  # (label, params, eval dict, celebdfb key, training fakes, backbone)
    (r"\ours{}-S (RepViT)", 4.7, tri["BASE"], "ours_repvit20", "observed", "RepViT-M0.9"),
    (r"\ours{}-SB (self-blend only)", 17.6, fasbL, "FASB-L", "self-blend", "EffNet-B4"),
    (r"\ours{}-SUP (observed only)", 17.6, sbifix.get("SUP"), "SUP-F", "observed", "EffNet-B4"),
    (r"\ours{} HYB, seed 1", 17.6, hyb1, "HYB-L", "both", "EffNet-B4"),
    (r"\ours{} HYB, seed 2", 17.6, hyb2, "HYB-L-s2", "both", "EffNet-B4"),
    (r"\ours{} HYB-F (faithful blend)", 17.6, sbifix.get("HYB"), "HYB-F", "both", "EffNet-B4"),
    (r"\ours{} HYB-D (+ symmetric degradation)", 17.6, sbifix.get("HYBD"), "HYBD-F", "both", "EffNet-B4"),
    (r"\ours{} HYB-PE (+ part-level edits)", 17.6, cgdD.get("HYBPE"), "cgd_HYBPE", "both+parts", "EffNet-B4"),
    (r"\ours{} HYB-PE + evidence head", 17.6, cgdD.get("MASK"), "cgd_MASK", "both+parts", "EffNet-B4"),
    (r"\ours{}-RU1 (+ vendor composites)", 17.6, ru1, "RU-effb4", "both+vendor", "EffNet-B4"),
    (r"\textbf{\ours{}-RU2, seed 1}", 17.6, ru2, "RU2-effb4", "both+vendor", "EffNet-B4"),
    (r"\textbf{\ours{}-RU2, seed 2}", 17.6, ru2b, "RU2-effb4-s2", "both+vendor", "EffNet-B4"),
    (r"\ours{}-RU3 (cleaned components)", 17.6, ru3, "RU3-effb4", "both+vendor", "EffNet-B4"),
    (r"\ours{}-RU3 + evidence head", 17.6, ru3e, "RU3e-effb4", "both+vendor", "EffNet-B4"),
    (r"\textbf{\ours{}-RU3 + CLIP-L/14 LoRA, seed 1}", 306.3, ruclip, "RU-clipe", "both+vendor", "CLIP ViT-L/14"),
    (r"\textbf{\ours{}-RU3 + CLIP-L/14 LoRA, seed 2}", 306.3, ruclip2, "RU-clipe-s2", "both+vendor", "CLIP ViT-L/14"),
    (r"\ours{}-RU4 + evidence head (EffNet-B4)", 17.6, ru4e, "RU4e-effb4", "both+vendor+parts", "EffNet-B4"),
    (r"\textbf{\ours{}-RU4 + CLIP-L/14 LoRA (unified)}", 306.3, ruclip4, "RU-clipe4", "both+vendor+parts", "CLIP ViT-L/14"),
]


# Main-text tables report one model (+ its small-backbone version); every other variant is ablation (supplement).
MAIN = [(r"\textbf{\ours{}} (CLIP ViT-L/14 + LoRA)", 306.3, ruclip4, "RU-clipe4", "both+vendor+parts", "CLIP ViT-L/14"),
        (r"\ours{}-lite (EfficientNet-B4)", 17.6, ru4e, "RU4e-effb4", "both+vendor+parts", "EffNet-B4")]


def cb_get(k, *path):
    if cb is None or k not in cb:
        return None
    v = cb[k]
    for p in path:
        v = v[p]
    return v


def curve(z_f, z_e):
    ts = np.unique(np.concatenate([z_f, z_e, [-1, 2]]))
    return np.array([(z_f > t).mean() * 100 for t in ts]), np.array([(z_e <= t).mean() * 100 for t in ts])


VL = jl(R / "ffpp_benchmark_20260925/video_level.json") or {}
VLKEY = {"HYB-L-s2": "HYB-L-s2", "HYB-F": "HYB-F", "ours_repvit20": "RepViT20", "SUP-F": "SUP-F", "HYBD-F": "HYBD-F", "cgd_MASK": "MASK", "cgd_HYBPE": "HYBPE",
         "RU-effb4": "RU-effb4", "RU2-effb4": "RU2-effb4", "RU2-effb4-s2": "RU2-effb4-s2", "RU-clipe": "RU-clipe", "RU-clipe-s2": "RU-clipe-s2", "RU3-effb4": "RU3-effb4", "RU3e-effb4": "RU3e-effb4", "RU4e-effb4": "RU4e-effb4", "RU-clipe4": "RU-clipe4"}


def vl(name, s):
    v = VL.get(VLKEY.get(name, name), {}).get(s, {}).get("video")
    return "--" if v is None else f"{v:.3f}"


def tab_cross():
    L = [r"\begin{tabular}{lrcccccc}", r"\toprule",
         r" & & \multicolumn{2}{c}{CDFv2} & \multicolumn{2}{c}{DFD} & Celeb-DF-B \\", r"\cmidrule(lr){3-4}\cmidrule(lr){5-6}",
         r"Detector & Params (M) & frame & video & frame & video & frame \\", r"\midrule",
         r"\multicolumn{7}{l}{\textit{Published binary detectors, official weights, our frames}} \\"]
    for b in PUB:
        L.append(f"{NICE[b]} & {bench[b]['params_M']:.1f} & {f3(cdf.get(b, {}).get('std_auc'))} & {vl(b, 'cdf')} & "
                 f"{f3(dfd.get(b, {}).get('std_auc'))} & {vl(b, 'dfd')} & {f3(cb_get(b, 'auc_untreated'))} \\\\".replace(PEND, "--"))
    L.append(r"\midrule")
    L.append(r"\multicolumn{7}{l}{\textit{Three-way, trained with FF++ c23, two retouching vendors and part-level edits (ours)}} \\")
    for lab, par, ev, k, _, _ in MAIN:
        L.append(f"{lab} & {par:.1f} & {f3(ev and ev['cdf']['auc'])} & {vl(k, 'cdf')} & {f3(ev and ev['dfd']['auc'])} & {vl(k, 'dfd')} & {f3(cb_get(k, 'auc_untreated'))} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_cross.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def tab_beauty():
    rows = [l.split("\t") for l in (BASE / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    folder = np.array([r[3] for r in rows]); rb, sb = folder == "real_beautified", folder == "synthesis_beautified"
    L = [r"\begin{tabular}{l cc c cc}", r"\toprule",
         r" & \multicolumn{3}{c}{FF++ c23 test (paired)} & \multicolumn{2}{c}{Celeb-DF-B (zero-shot)} \\",
         r"\cmidrule(lr){2-4}\cmidrule(lr){5-6}",
         r"Detector & FA & MISS & FA at MISS$\le$5\% & $\Delta$MISS (pp) & FA at MISS$\le$" + f"{cb_get('RU-clipe4', 'MISS'):.1f}" + r"\% \\", r"\midrule"]
    for b in PUB:
        z = np.load(R / f"ffpp_benchmark_20260925/scores_{b}.npz"); fa, ms = curve(z["filter"], z["escape"])
        need = fa[ms <= 5].min() if (ms <= 5).any() else float("nan")
        p = np.load(R / "celebdfb_v2_20260927/scores_v3" / f"{b}.npz")["p"][:, 1]; fa2, ms2 = curve(p[rb], p[sb])
        hyb_miss = cb_get("RU-clipe4", "MISS")   # the main model's escape rate under beautification
        need2 = fa2[ms2 <= hyb_miss].min() if (ms2 <= hyb_miss).any() else float("nan")
        d, ci = cb_get(b, "dMISS"), cb_get(b, "ci", "dMISS")
        L.append(f"{NICE[b]} & {bench[b]['FA']:.1f} & {bench[b]['MISS']:.1f} & {need:.1f} & "
                 f"{d:+.1f} [{ci[0]:+.1f}, {ci[1]:+.1f}] & {need2:.1f} \\\\")
    L.append(r"\midrule")
    for lab, _, ev, k, _, _ in MAIN:
        if ev is None:
            continue
        d, ci = cb_get(k, "dMISS"), cb_get(k, "ci", "dMISS")
        cbs = PEND if d is None else f"{d:+.1f} [{ci[0]:+.1f}, {ci[1]:+.1f}]"
        L.append(f"{lab} & {ev['FA']:.1f} & {ev['MISS']:.1f} & -- & {cbs} & "
                 f"{f1(cb_get(k, 'FA'))} (MISS {f1(cb_get(k, 'MISS'))}) \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_beauty.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def tab_main():
    """Main comparison table: forgery detection (CDFv2, DFD, Celeb-DF-B) and beautification errors (FF++ paired corpus,
    Celeb-DF-B) for the 13 published detectors and the two reported models. Best value per column in bold."""
    rows_cb = [l.split("\t") for l in (BASE / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    folder = np.array([r[3] for r in rows_cb]); rb, sb = folder == "real_beautified", folder == "synthesis_beautified"
    ours_miss = cb_get("RU-clipe4", "MISS")
    R_ = []   # name, params, cdf f, cdf v, dfd f, dfd v, cdfb auc, ffpp FA@MISS<=5 (or native), dMISS, cdfb FA@MISS<=ours (or native)
    for b in PUB:
        z = np.load(R / f"ffpp_benchmark_20260925/scores_{b}.npz"); fa, ms = curve(z["filter"], z["escape"])
        need = fa[ms <= 5].min() if (ms <= 5).any() else float("nan")
        p = np.load(R / "celebdfb_v2_20260927/scores_v3" / f"{b}.npz")["p"][:, 1]; fa2, ms2 = curve(p[rb], p[sb])
        need2 = fa2[ms2 <= ours_miss].min() if (ms2 <= ours_miss).any() else float("nan")
        v = lambda s_: VL.get(VLKEY.get(b, b), {}).get(s_, {}).get("video")
        R_.append([NICE[b], bench[b]["params_M"], cdf.get(b, {}).get("std_auc"), v("cdf"), dfd.get(b, {}).get("std_auc"), v("dfd"),
                   cb_get(b, "auc_untreated"), need, cb_get(b, "dMISS"), need2, None, None])
    for lab, par, ev, k, _, _ in MAIN:
        v = lambda s_: VL.get(VLKEY.get(k, k), {}).get(s_, {}).get("video")
        R_.append([lab, par, ev["cdf"]["auc"], v("cdf"), ev["dfd"]["auc"], v("dfd"), cb_get(k, "auc_untreated"),
                   ev["FA"], cb_get(k, "dMISS"), cb_get(k, "FA"), ev["MISS"], cb_get(k, "MISS")])
    best = {}
    for c, fn in ((2, max), (3, max), (4, max), (5, max), (6, max), (7, min), (9, min)):
        best[c] = fn(r[c] for r in R_ if r[c] is not None and r[c] == r[c])
    bestd = min(abs(r[8]) for r in R_ if r[8] is not None)

    def cell(r, c, fmt):
        x = r[c]
        if x is None or x != x:
            return "--"
        s_ = fmt.format(x)
        return r"\textbf{" + s_ + "}" if c in best and abs(x - best[c]) < 1e-9 else s_

    L = [r"\begin{tabular}{lr cc cc c c cc}", r"\toprule",
         r" & & \multicolumn{2}{c}{Celeb-DF-v2} & \multicolumn{2}{c}{DFD} & Celeb-DF-B & FF++ beautified & \multicolumn{2}{c}{Celeb-DF-B beautified} \\",
         r"\cmidrule(lr){3-4}\cmidrule(lr){5-6}\cmidrule(lr){7-7}\cmidrule(lr){8-8}\cmidrule(lr){9-10}",
         r"Detector & Params (M) & frame & video & frame & video & AUC & FA at MISS$\le$5 & $\Delta$MISS & FA at MISS$\le$" + f"{ours_miss:.1f}" + r" \\",
         r"\midrule", r"\multicolumn{10}{l}{\textit{Published binary detectors, official weights, our frames; FA read off the full threshold sweep}} \\"]
    for i, r in enumerate(R_):
        if i == len(PUB):
            L += [r"\midrule", r"\multicolumn{10}{l}{\textit{Three-way, native argmax rule, no threshold (MISS in parentheses)}} \\"]
        dm = "--" if r[8] is None else f"{r[8]:+.1f}".replace("-", "$-$")   # not bolded: the smallest |dMISS| belongs to detectors near chance (UnivFD, NPR)
        if i < len(PUB):
            fa1, fa2 = cell(r, 7, "{:.1f}"), cell(r, 9, "{:.1f}")
        else:
            fa1 = cell(r, 7, "{:.1f}") + f" ({r[10]:.1f})"; fa2 = cell(r, 9, "{:.1f}") + f" ({r[11]:.1f})"
        L.append(f"{r[0]} & {r[1]:.1f} & {cell(r, 2, '{:.3f}')} & {cell(r, 3, '{:.3f}')} & {cell(r, 4, '{:.3f}')} & {cell(r, 5, '{:.3f}')} & "
                 f"{cell(r, 6, '{:.3f}')} & {fa1} & {dm} & {fa2} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_main.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def tab_ablation():
    L = [r"\begin{tabular}{llccccccc}", r"\toprule",
         r"Variant & Fakes seen & CDFv2 & DFD & real & fake & filter & FA / MISS & B1 \\", r"\midrule"]
    for lab, _, ev, k, fk, bb in OURS:
        if ev is None:
            L.append(f"{lab} & {fk} & " + " & ".join([PEND] * 7) + r" \\"); continue
        dom = ev.get("b1_dominated_by")
        b1 = PEND if dom is None and "b1_dominated_by" not in ev else (f"{len(dom)}/{ev.get('b1_n_detectors', 11)}" if dom is not None else "0/11")
        if k == "ours_repvit20":
            b1 = f"{len(jl(R / 'tripair_20260927/eval_tripair.json')['b1_violations']['BASE'])}/11"
        ind = ev["indomain"]
        L.append(f"{lab} & {fk} & {f3(ev['cdf']['auc'])} & {f3(ev['dfd']['auc'])} & {ind['real']:.1f} & {ind['fake']:.1f} & "
                 f"{ind['filter']:.1f} & {ev['FA']:.1f} / {ev['MISS']:.1f} & {b1} \\\\")
    if sbiL:
        L.append(r"\midrule")
        L.append(f"SBI recipe, our pipeline (binary) & self-blend & {f3(sbiL['cdf']['auc'])} & {f3(sbiL['dfd']['auc'])} & "
                 f"-- & -- & -- & {sbiL['at_5fpr']['FA']:.1f} / {sbiL['at_5fpr']['MISS']:.1f} & -- \\\\")
    sf = sbifix.get("SBI")
    L.append(f"SBI recipe, faithful blend (binary) & self-blend & {f3(sf and sf['cdf']['auc'])} & {f3(sf and sf['dfd']['auc'])} & -- & -- & -- & "
             + (PEND if sf is None else f"{sf['at_5fpr']['FA']:.1f} / {sf['at_5fpr']['MISS']:.1f}") + r" & -- \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_ablation.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    tab_cross(); tab_beauty(); tab_main(); tab_ablation(); print("tables ->", OUT)


def tab_preset():
    names = ["sbi", "srm", "core", "ucf", "xception", "effnb4", "SBI-F", "HYB-L", "HYB-L-s2", "HYB-F", "HYBD-F", "ours_repvit20"]
    lab = {**NICE, "HYB-L": r"\ours{} HYB s1", "HYB-L-s2": r"\ours{} HYB s2", "ours_repvit20": r"\ours{}-S",
           "SBI-F": r"SBI obj., our pipeline", "HYB-F": r"\ours{} HYB-F", "HYBD-F": r"\ours{} HYB-D"}
    pres = ["brown", "california_dreamin", "hawaii_grain", "relax_you_pretty"]
    L = [r"\begin{tabular}{lrrrr|r|rr}", r"\toprule",
         r"Detector & brown & calif. & hawaii & relax & compress & all & all$-$compr. \\", r"\midrule"]
    for n in names:
        if cb is None or n not in cb:
            continue
        r = cb[n]
        L.append(f"{lab[n]} & " + " & ".join(f"{r['per_preset'][p]['dMISS']:+.1f}" for p in pres)
                 + f" & {r['dMISS_c']:+.1f} & {r['dMISS']:+.1f} & {r['dMISS'] - r['dMISS_c']:+.1f} \\\\")
        if n == "effnb4":
            L.append(r"\midrule")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_preset.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


tab_preset()
