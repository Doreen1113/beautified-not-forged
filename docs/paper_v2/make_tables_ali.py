"""tab_alipair: FF++-only three-way models on Alibaba commercial retouching pairs (alipair_zeroshot_20260929/results.json),
plus RU rows when results/research/retouch_unified_20260929/eval_ru_<tag>.json exist.

python docs/paper_v2/make_tables_ali.py -> docs/paper_v2/tables/tab_alipair.tex
"""
import json
from pathlib import Path

BASE = Path(r"C:\My_Project\AIGC"); OUT = BASE / "docs/paper_v2/tables"
A = json.loads((BASE / "results/research/alipair_zeroshot_20260929/results.json").read_text())
LAB = {"HYB": r"three-way, hybrid fakes (HYB)", "HYB-F": r"HYB, faithful blend", "HYB-D": r"HYB + symmetric degradation", "SUP-F": r"three-way, observed fakes (SUP)",
       "MASK": r"three-way, part edits + evidence head", "RepViT": r"three-way, RepViT-M0.9"}
ORDER = ["RepViT", "SUP-F", "HYB", "HYB-F", "HYB-D", "MASK"]


def row(lab, o, p, g):
    sm = g["Smoothing_90"]; ey = g["EyeEnlarging_90"]
    return (f"{lab} & {o['real']:.1f}/{o['fake']:.1f}/{o['filter']:.1f} & {p['to_filter']:.1f} & {p['to_fake']:.1f} & {p['balanced_acc']:.1f} & {p['paired_rank']:.1f} & "
            f"{ey['paired_rank']:.0f} / {g['Whitening_90']['paired_rank']:.0f} / {g['FaceLifting_90']['paired_rank']:.0f} / {sm['paired_rank']:.0f} & {sm['to_fake']:.1f} \\\\")


L = [r"\begin{tabular}{l c cc c c c c}", r"\toprule",
     r" & originals & \multicolumn{2}{c}{retouched (pooled)} & & & paired rank at level 90 & smoothing-90 \\",
     r"\cmidrule(lr){3-4}",
     r"Model & real/fake/filter & $\to$filter & $\to$fake & balanced & paired rank & eye / white / lift / smooth & $\to$fake \\", r"\midrule",
     r"\multicolumn{8}{l}{\textit{FF++ c23 training only (zero-shot)}} \\"]
for k in ORDER:
    r = A[k]; L.append(row(LAB[k], r["orig"], r["pooled"], r["by_group"]))
ru = sorted((BASE / "results/research/retouch_unified_20260929").glob("eval_ru_*.json"))
RUJ = {f.stem.replace("eval_ru_", ""): json.loads(f.read_text()).get("ali") for f in ru}
# main text: the two reported models; supplement: every vendor-trained variant
MAIN = [("clipe4_s20260929", r"\textbf{\ours{}} (CLIP ViT-L/14 + LoRA)"), ("ru4e_effb4_s20260929", r"\ours{}-lite (EfficientNet-B4)")]
L_main = [l for l in L if not any(l.startswith(LAB[k]) for k in ("RepViT", "HYB", "HYB-F", "HYB-D"))]   # main text: best and evidence-head FF++-only rows
L_main += [r"\midrule", r"\multicolumn{8}{l}{\textit{Trained with two vendors' renders and their single-operation components; Alibaba never seen (ours)}} \\"]
for tag, lab in MAIN:
    if RUJ.get(tag):
        L_main.append(row(lab, RUJ[tag]["orig"], RUJ[tag]["pooled"], RUJ[tag]["by_group"]))
L_main += [r"\bottomrule", r"\end{tabular}"]
(OUT / "tab_alipair.tex").write_text("\n".join(L_main) + "\n", encoding="utf-8"); print("tab_alipair ->", OUT)
ARM = {"effb4": "RU1 renders only", "repvit": "RU1 renders only", "ru2": "RU2 + components", "ru3": "RU3 cleaned components", "ru3e": "RU3 + evidence head",
       "ru4e": "RU4 + part edits (lite)", "clip": "RU3, CLIP", "clipe": "RU3 + evidence head, CLIP", "clipe4": "RU4 + part edits, CLIP (main)"}
L_all = L + [r"\midrule", r"\multicolumn{8}{l}{\textit{Vendor-trained variants (all single Alibaba reads)}} \\"]
for tag in sorted(RUJ, key=lambda t: (list(ARM).index(t.split("_")[0]) if t.split("_")[0] in ARM else 99, t)):
    R = RUJ[tag]
    if not R:
        continue
    arm = ARM.get(tag.split("_")[0], tag); bb = "CLIP-L/14" if tag.startswith("clip") else ("EffNet-B4" if "effb4" in tag else "RepViT")
    sd = "" if bb == "RepViT" else (", s2" if tag.endswith("20260930") else ", s1")
    L_all.append(row(arm + " (" + bb + sd + ")", R["orig"], R["pooled"], R["by_group"]))
L_all += [r"\bottomrule", r"\end{tabular}"]
(OUT / "tab_alipair_all.tex").write_text("\n".join(L_all) + "\n", encoding="utf-8"); print("tab_alipair_all ->", OUT)
