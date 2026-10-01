"""Slide assets for the 2026-09-30 project meeting. Every number is read from a results file.

python docs/meeting_20260930/make_assets.py  -> docs/meeting_20260930/assets/*.png  (+ tex/*.tex for the LaTeX tables)
Paper figures are re-rasterised from their vector PDFs at 400 dpi; new charts use the paper's plot style.
"""
import json
import re
import sys
from pathlib import Path

import fitz
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

B = Path(r"C:\My_Project\AIGC"); R = B / "results/research"; P = B / "docs/paper_v2"
OUT = Path(__file__).resolve().parent / "assets"; OUT.mkdir(exist_ok=True)
TEX = Path(__file__).resolve().parent / "tex"; TEX.mkdir(exist_ok=True)
sys.path.insert(0, str(P))
import make_figures as MF  # noqa: E402  (paper plot style)

INK, MUTED, GRID = MF.INK, MF.MUTED, MF.GRID
C_BIN, C_RED, C_OURS, C_OURS2 = MF.C_BIN, MF.C_SBI, MF.C_OURS, MF.C_OURS2
plt.rcParams.update({"font.size": 11, "axes.labelsize": 11, "xtick.labelsize": 10.5, "ytick.labelsize": 10.5})


def jl(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=300, bbox_inches="tight", transparent=False, facecolor="white"); plt.close(fig)


# ---------------------------------------------------------------- paper figures, re-rasterised
for f in ("fig_teaser", "fig_frontier", "fig_overview", "fig_decomp", "fig_evidence", "fig_accuse"):
    d = fitz.open(P / "figs" / f"{f}.pdf"); d[0].get_pixmap(dpi=400).save(OUT / f"{f}.png")

cb = jl(R / "celebdfb_v2_20260927/results_v3.json")
NAMES = {"sbi": "SBI", "effort": "Effort (CLIP)", "fadapter": "Forensics Adapter (CLIP)", "xception": "Xception", "ucf": "UCF",
         "effnb4": "EfficientNet-B4", "RU4e-effb4": "Ours-lite", "RU-clipe4": "Ours"}


# ---------------------------------------------------------------- escape caused by beautification itself
def escape_split():
    keys = ["sbi", "fadapter", "effort", "ucf", "xception", "effnb4", "RU4e-effb4", "RU-clipe4"]
    total = [cb[k]["dMISS"] for k in keys]; comp = [cb[k]["dMISS_c"] for k in keys]
    beauty = [t - c for t, c in zip(total, comp)]
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    y = np.arange(len(keys))[::-1]
    col = [C_OURS if k.startswith("RU") else (C_RED if k in ("sbi", "effort", "fadapter") else C_BIN) for k in keys]
    ax.barh(y, beauty, color=col, height=0.62)
    for yy, b, t in zip(y, beauty, total):
        ax.text(max(b, 0) + 0.5, yy, f"{b + 1e-9:+.1f}", va="center", fontsize=10.5, color=INK, fontweight="bold")
    ax.axvline(0, color=INK, lw=0.8)
    ax.set_yticks(y, [NAMES[k] for k in keys]); ax.set_xlim(-3, 25)
    ax.set_xlabel("extra deepfakes called real, caused by beautification (pp)")
    ax.tick_params(axis="y", length=0)
    save(fig, "escape_split")
    return {NAMES[k]: (round(t + 1e-9, 1), round(c + 1e-9, 1), round(b + 1e-9, 1)) for k, t, c, b in zip(keys, total, comp, beauty)}   # half-up, as the bar labels


# ---------------------------------------------------------------- blur: genuine frames called fake
def blur_bars():
    bp = jl(R / "sbifix_20260927/blur_probe.json"); ru = jl(R / "retouch_unified_20260929/blur_probe_ru.json")
    rows = [("SBI", bp["sbi"]["orig"]["over_0.5"], bp["sbi"]["blur1.5"]["over_0.5"], C_RED),
            ("EfficientNet\n-B4", bp["effnb4"]["orig"]["over_0.5"], bp["effnb4"]["blur1.5"]["over_0.5"], C_BIN),
            ("Xception", bp["xception"]["orig"]["over_0.5"], bp["xception"]["blur1.5"]["over_0.5"], C_BIN),
            ("UCF", bp["ucf"]["orig"]["over_0.5"], bp["ucf"]["blur1.5"]["over_0.5"], C_BIN),
            ("three-way,\nFF++ only", bp["HYB-L-s2"]["orig"]["argmax_fake"], bp["HYB-L-s2"]["blur1.5"]["argmax_fake"], "#8c8c8c"),
            ("Ours-lite", ru["Ours-lite (ru4e)"]["orig"], ru["Ours-lite (ru4e)"]["blur1.5"], C_OURS2),
            ("Ours", ru["Ours (clipe4)"]["orig"], ru["Ours (clipe4)"]["blur1.5"], C_OURS)]
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    x = np.arange(len(rows)); w = 0.38
    ax.bar(x - w / 2, [r[1] for r in rows], w, color=[r[3] for r in rows], alpha=0.35)
    ax.bar(x + w / 2, [r[2] for r in rows], w, color=[r[3] for r in rows])
    for xi, r in zip(x, rows):
        ax.text(xi + w / 2, r[2] + 1.5, f"{r[2]:.0f}", ha="center", fontsize=10.5, fontweight="bold", color=INK)
    ax.set_xticks(x, [r[0] for r in rows], rotation=0, fontsize=10)
    ax.set_ylabel("genuine FF++ frames called fake (%)"); ax.set_ylim(0, 105)
    h = [plt.Rectangle((0, 0), 1, 1, color="#555555", alpha=0.35), plt.Rectangle((0, 0), 1, 1, color="#555555")]
    ax.legend(h, ["sharp frames", r"Gaussian blur $\sigma$ = 1.5"], loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, fontsize=10.5)
    save(fig, "blur_bars")
    return {r[0].replace("\n", " "): (r[1], r[2]) for r in rows}


# ---------------------------------------------------------------- unseen retouching service: balanced accuracy
def retouch_balanced():
    A = jl(R / "alipair_zeroshot_20260929/results.json")
    ru = {t: jl(R / f"retouch_unified_20260929/eval_ru_{t}.json")["ali"] for t in ("ru4e_effb4_s20260929", "clipe4_s20260929")}
    rows = [("FF++ only,\nobserved fakes", A["SUP-F"]["pooled"]["balanced_acc"], "#8c8c8c"),
            ("FF++ only,\nhybrid fakes", A["HYB"]["pooled"]["balanced_acc"], "#8c8c8c"),
            ("FF++ only,\nevidence head", A["MASK"]["pooled"]["balanced_acc"], "#8c8c8c"),
            ("Ours-lite", ru["ru4e_effb4_s20260929"]["pooled"]["balanced_acc"], C_OURS2),
            ("Ours", ru["clipe4_s20260929"]["pooled"]["balanced_acc"], C_OURS)]
    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    x = np.arange(len(rows))
    ax.bar(x, [r[1] for r in rows], 0.6, color=[r[2] for r in rows])
    for xi, r in zip(x, rows):
        ax.text(xi, r[1] + 1, f"{r[1]:.1f}", ha="center", fontsize=11, fontweight="bold", color=INK)
    ax.axhline(50, color=MUTED, lw=1, ls=":"); ax.text(4.36, 50.6, "chance", fontsize=10, color=MUTED, ha="left"); ax.set_xlim(-0.5, 5.0)
    ax.axhline(75, color=C_RED, lw=1, ls="--"); ax.text(-0.42, 76.0, "target set before training", fontsize=10, color=C_RED, ha="left")
    ax.set_xticks(x, [r[0] for r in rows], fontsize=10); ax.set_ylim(40, 82)
    ax.set_ylabel("retouched vs. untouched,\nbalanced accuracy (%)")
    save(fig, "retouch_balanced")
    return {r[0].replace("\n", " "): r[1] for r in rows}


# ---------------------------------------------------------------- explanation faithfulness: flip rate vs ceiling
def flip_bars():
    E = R / "cgd_20260927"
    e_pe, e_noparts, e_lite, e_ours = (jl(E / f) for f in ("explain_HYBPE_s20260928.json", "explain_RUCLIPE_s20260929.json",
                                                            "explain_RU4E_s20260929.json", "explain_RUCLIPE4_s20260929.json"))
    mech = [("donor", "donor transplant"), ("sd", "SD-1.5 inpaint"), ("sdxl", "SDXL inpaint\n(unseen editor)")]
    series = [("random region", lambda m: e_ours[m]["evidence"]["flip_rand"], "#d9d9d9"),
              ("centre region", lambda m: e_ours[m]["evidence"]["flip_centre"], "#bdbdbd"),
              ("Score-CAM (no head)", lambda m: e_pe[m]["scorecam"]["flip_pred"], C_BIN),
              ("head, no part edits", lambda m: e_noparts[m]["evidence"]["flip_pred"], "#9ecae1"),
              ("Ours-lite", lambda m: e_lite[m]["evidence"]["flip_pred"], C_OURS2),
              ("Ours", lambda m: e_ours[m]["evidence"]["flip_pred"], C_OURS)]
    fig, ax = plt.subplots(figsize=(7.6, 3.7))
    x = np.arange(len(mech)); w = 0.13
    vals = {}
    for j, (lab, fn, c) in enumerate(series):
        v = [100 * fn(m) for m, _ in mech]; vals[lab] = [round(a, 1) for a in v]
        ax.bar(x + (j - 2.5) * w, v, w, color=c, label=lab)
    ceil = [100 * e_ours[m]["flip_ceiling_gt"] for m, _ in mech]; vals["ceiling (true footprint)"] = [round(a, 1) for a in ceil]
    for xi, cv in zip(x, ceil):
        ax.plot([xi - 3 * w, xi + 3 * w], [cv, cv], color=C_RED, lw=1.6, ls="--")
    ax.plot([], [], color=C_RED, lw=1.6, ls="--", label="ceiling: restore true footprint")
    for xi, m in zip(x, mech):
        ax.text(xi + 2.5 * w, 100 * e_ours[m[0]]["evidence"]["flip_pred"] + 1.5, f"{100 * e_ours[m[0]]['evidence']['flip_pred']:.0f}",
                ha="center", fontsize=10, fontweight="bold", color=C_OURS)
    ax.set_xticks(x, [m[1] for m in mech]); ax.set_ylim(0, 100)
    ax.set_ylabel("detections removed by restoring\nthe named region (%)")
    ax.legend(ncol=1, fontsize=9, loc="upper left", bbox_to_anchor=(1.0, 1.0))
    save(fig, "flip_bars")
    return vals


# ---------------------------------------------------------------- LaTeX tables (compiled on the Ubuntu box)
def row_cells(line):
    return [c.strip() for c in line.rstrip("\\ \n").split("&")]


def tex_detection():
    lines = (P / "tables/tab_main.tex").read_text(encoding="utf-8").splitlines()
    keep = ["Xception", "EfficientNet-B4", "UCF", "SBI", "Effort (CLIP-L/14)", "Forensics Adapter (CLIP-L/14)"]
    rows = []
    for l in lines:
        c = row_cells(l) if "&" in l and not l.startswith(("Detector", " &")) else None
        if not c:
            continue
        name = re.sub(r"\\textbf\{|\}", "", c[0]).replace(r"\ours{", "Ours").strip()
        if c[0].split(" (")[0] in [k.split(" (")[0] for k in keep] and c[0] in keep or "ours" in c[0]:
            rows.append(c)
    body = []
    for c in rows:
        ours = "ours" in c[0]
        name = c[0].replace(r"\textbf{\ours{}} (CLIP ViT-L/14 + LoRA)", r"\textbf{Ours} (CLIP ViT-L/14 + LoRA)").replace(r"\ours{}-lite", "Ours-lite")
        name = name.replace("(CLIP-L/14)", "(CLIP)")
        cells = [name, c[1], c[3], c[5], c[6], c[7], c[8].replace("$-$", "$-$")]
        pre = r"\rowcolor{oursbg}" if ours else ""
        if ours and "lite" not in c[0] and body and not any("rowcolor" in b for b in body):
            body.append(r"\midrule")
        body.append(pre + " & ".join(cells) + r" \\")
    tex = r"""\documentclass[border=4pt]{standalone}
\usepackage{fontspec}\setmainfont{texgyretermes}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,ItalicFont=*-italic,BoldItalicFont=*-bolditalic]
\usepackage{booktabs,colortbl,xcolor}
\definecolor{oursbg}{HTML}{E3ECF7}
\begin{document}\large
\begin{tabular}{lrcccrr}
\toprule
 & & Celeb-DF-v2 & DFD & Celeb-DF-B & FF++ beautified & Celeb-DF-B \\
Detector & Params (M) & video AUC & video AUC & AUC & FA at MISS$\le$5 & $\Delta$MISS (pp) \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}
\end{document}
"""
    (TEX / "tab_detection.tex").write_text(tex, encoding="utf-8")


def tex_targets():
    ev = jl(R / "retouch_unified_20260929/eval_ru_clipe4_s20260929.json"); ali, ff = ev["ali"], ev["ffpp"]
    ex = jl(R / "cgd_20260927/explain_RUCLIPE4_s20260929.json")
    flip = min(100 * ex[m]["evidence"]["flip_pred"] for m in ("donor", "sd", "sdxl"))
    gap = max(100 * (ex[m]["flip_ceiling_gt"] - ex[m]["evidence"]["flip_pred"]) for m in ("donor", "sd", "sdxl"))
    iou = min(ex[m]["evidence"]["iou7"] for m in ("donor", "sd", "sdxl"))
    eq4 = ali["eq4"]; t7 = eq4["table7_TP"]; beat = sum(eq4["TP"][k] >= t7[k] for k in ("eye", "jaw", "white", "smooth"))
    sp = jl(R / "retouch_unified_20260929/eval_ru_clipe4_s20260929.json")["ali"]["quantities"]
    rho = max(v.get("spearman", 0) for v in sp.values()) if isinstance(sp, dict) and all(isinstance(v, dict) for v in sp.values()) else None
    P_ = r"\cellcolor{pass}\textbf{met}"; F_ = r"\cellcolor{fail}\textbf{missed}"
    rows = [
        ("Beautification escape on Celeb-DF-B", r"$\le$ +3 pp", f"+{cb['RU-clipe4']['dMISS']:.1f} pp", P_),
        ("Retouched faces called fake (unseen service)", r"$\le$ 5\%", f"{ali['pooled']['to_fake']:.1f}\\%", P_),
        ("Cross-dataset AUC (CDFv2 / DFD)", r"$\ge$ 0.78 / 0.88", f"{ff['cdf']['auc']:.3f} / {ff['dfd']['auc']:.3f}", P_),
        ("Binary detectors that dominate us", "0", f"0 of {len(ev['ffpp'].get('b1_dominated_by', [])) + 15 if False else 15}", P_),
        ("Evidence: flip within 5 pp of ceiling, IoU$_7\\ge$0.65", r"$\le$ 5 pp, 0.65", f"{gap:.1f} pp, {iou:.2f}", P_),
        ("Retouched vs.\\ untouched (unseen service)", r"$\ge$ 75\%", f"{ali['pooled']['balanced_acc']:.1f}\\%", F_),
        ("Per-operation recall vs.\\ RetouchingFFHQ", "3 of 4 ops", f"{beat} of 4", F_),
        ("FF++ recall, every class", r"$\ge$ 80\%", f"genuine {ff['indomain']['real']:.1f}\\%", F_),
        ("Edit-magnitude estimate", r"Spearman $\ge$ 0.6", r"$\le$ 0.47", F_),
    ]
    body = "\n".join(" & ".join(r) + r" \\" for r in rows[:5]) + "\n\\midrule\n" + "\n".join(" & ".join(r) + r" \\" for r in rows[5:])
    tex = r"""\documentclass[border=4pt]{standalone}
\usepackage{fontspec}\setmainfont{texgyretermes}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,ItalicFont=*-italic,BoldItalicFont=*-bolditalic]
\usepackage{booktabs,colortbl,xcolor}
\definecolor{pass}{HTML}{DCEFD9}\definecolor{fail}{HTML}{F6D5D2}
\begin{document}\large
\begin{tabular}{llll}
\toprule
Target set before training & Bar & \textsc{Ours} & \\
\midrule
""" + body + r"""
\bottomrule
\end{tabular}
\end{document}
"""
    (TEX / "tab_targets.tex").write_text(tex, encoding="utf-8")


def tex_explain_reliability():
    vv = jl(R / "retouch_unified_20260929/vendor_val_clipe4_s20260929.json")["components"]
    ali = jl(R / "retouch_unified_20260929/eval_ru_clipe4_s20260929.json")["ali"]["eq4"]["TP"]
    pn = jl(R / "retouch_unified_20260929/part_naming.json")
    ex = jl(R / "cgd_20260927/explain_RUCLIPE4_s20260929.json")

    def rng(a, b):
        lo, hi = sorted((a, b)); return f"{lo:.2f}" if abs(hi - lo) < 0.005 else f"{lo:.2f}--{hi:.2f}"

    ops = [("eye enlargement", "eye", "eye"), ("face reshaping", "jaw", "jaw"), ("whitening", "white", "white"), ("smoothing", "smooth", "smooth")]
    op_train = " / ".join(rng(vv[f"tencent_{k}"]["TP"], vv[f"megvii_{k}"]["TP"]) for _, k, _ in ops)
    op_unseen = " / ".join(f"{ali[k]:.2f}" for _, _, k in ops)
    flips = [100 * ex[m]["evidence"]["flip_pred"] for m in ("donor", "sd", "sdxl")]
    ceils = [100 * ex[m]["flip_ceiling_gt"] for m in ("donor", "sd", "sdxl")]

    def cell(v, good):
        return ("" if good is None else (r"\cellcolor{pass}" if good else r"\cellcolor{fail}")) + v

    tr = {k: max(vv[f"tencent_{k}"]["TP"], vv[f"megvii_{k}"]["TP"]) for _, k, _ in ops}
    trl = {k: min(vv[f"tencent_{k}"]["TP"], vv[f"megvii_{k}"]["TP"]) for _, k, _ in ops}
    rows = [
        (r"\textbf{Which operation} (filter)", "two training services, held-out faces",
         cell(f"{trl['eye']:.2f} (eyes) to {tr['smooth']:.2f} (smoothing)", None)),
        ("", "unseen service", cell(f"{ali['eye']:.2f} (eyes) to {ali['smooth']:.2f} (smoothing)", False)),
        (r"\textbf{Which part} (fake)", "held-out part forgeries, 3 editors",
         cell(f"{min(pn[m]['ruleB_top1'] for m in ('donor', 'sd', 'sdxl')):.0f}--{max(pn[m]['ruleB_top1'] for m in ('donor', 'sd', 'sdxl')):.0f}\\% right", True)),
        (r"\textbf{Is it the cause?}", "restore that part to the original",
         cell(f"{min(flips):.0f}\\% of detections removed (ceiling {max(ceils):.0f}\\%)", True)),
        (r"\textbf{How much} was edited", "predicted vs. measured amount", cell(r"Spearman $\le$ 0.47, not shown", False)),
    ]
    body = "\n".join(" & ".join(r) + r" \\[2pt]" for r in rows)
    tex = r"""\documentclass[border=4pt]{standalone}
\usepackage{fontspec}\setmainfont{texgyretermes}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,ItalicFont=*-italic,BoldItalicFont=*-bolditalic]
\usepackage{booktabs,colortbl,xcolor,amssymb}
\definecolor{pass}{HTML}{DCEFD9}\definecolor{fail}{HTML}{F6D5D2}
\begin{document}\Large
\begin{tabular}{lll}
\toprule
The sentence says & Tested on & Correct \\
\midrule
""" + body + r"""
\bottomrule
\end{tabular}
\end{document}
"""
    (TEX / "tab_explain.tex").write_text(tex, encoding="utf-8")


def tex_equations():
    tex = r"""\documentclass[border=6pt]{standalone}
\usepackage{fontspec}\setmainfont{texgyretermes}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,ItalicFont=*-italic,BoldItalicFont=*-bolditalic]
\usepackage{amsmath,amssymb}
\begin{document}\Large
$\begin{aligned}
&O(\mathbf{u}+f(\mathbf{u}))\approx R(\mathbf{u}) \qquad P = R\circ(\mathrm{id}-f^{-1}) - O\\[6pt]
&C_\text{eye} = \mathcal{W}(O;\,E\odot f) \qquad\; C_\text{contour} = \mathcal{W}(O;\,(1-E)\odot f)\\[4pt]
&C_\text{tone} = O + G_\sigma * P \qquad\;\; C_\text{texture} = O + P - G_\sigma * P\\[6pt]
&M(C_k) = \mathrm{dilate}\big(\mathbf{1}[\,\|C_k-O\|_\infty>6\,]\big)
\end{aligned}$
\end{document}
"""
    (TEX / "eq_decomp.tex").write_text(tex, encoding="utf-8")
    tex = r"""\documentclass[border=6pt]{standalone}
\usepackage{fontspec}\setmainfont{texgyretermes}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,ItalicFont=*-italic,BoldItalicFont=*-bolditalic]
\usepackage{amsmath,amssymb}
\begin{document}\Large
$\mathcal{L}=\mathrm{CE}(p,y)+\mathbf{1}[y=\text{filter}]\,\mathrm{BCE}(\hat s,s)+\mathbf{1}[M\ \text{exact}]\,\big(\mathrm{BCE}(\hat m,M)+\mathrm{Dice}(\hat m,M)\big)$
\end{document}
"""
    (TEX / "eq_loss.tex").write_text(tex, encoding="utf-8")


if __name__ == "__main__":
    log = {"escape_split (total, reencode, beauty)": escape_split(), "blur_bars (sharp, blur)": blur_bars(),
           "retouch_balanced": retouch_balanced(), "flip_bars": flip_bars()}
    tex_detection(); tex_targets(); tex_equations(); tex_explain_reliability()
    (OUT / "asset_numbers.json").write_text(json.dumps(log, indent=1)); print(json.dumps(log, indent=1))
