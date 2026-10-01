"""Extra slide assets added on 2026-10-01 after the meeting feedback (label definitions, train / val / test accuracy).

python docs/meeting_20260930/make_assets_v4.py   -> tex/tab_labels.tex, tex/tab_splits.tex (compile with build_tex.sh),
                                                    assets/fig_training.png, assets/fig_confusion.png
The split table is the paper's table (docs/paper_v2/tables/tab_splits.tex, from make_tables_splits.py) with the
commercial-originals cells of Ours highlighted; the figures are the paper's vector PDFs rasterised at 400 dpi.
"""
from pathlib import Path

import fitz

H = Path(__file__).resolve().parent; P = Path(r"C:\My_Project\AIGC\docs\paper_v2")
HEAD = (r"\documentclass[border=4pt]{standalone}" "\n"
        r"\usepackage{fontspec}\setmainfont{texgyretermes}[Extension=.otf,UprightFont=*-regular,BoldFont=*-bold,"
        r"ItalicFont=*-italic,BoldItalicFont=*-bolditalic]" "\n"
        r"\usepackage{booktabs,colortbl,xcolor,amssymb,array}" "\n"
        r"\definecolor{pass}{HTML}{DCEFD9}\definecolor{fail}{HTML}{F6D5D2}" "\n"
        r"\definecolor{cr}{HTML}{2F7D4F}\definecolor{cf}{HTML}{B64342}\definecolor{cl}{HTML}{A8781A}" "\n"
        r"\newcommand{\ours}{\textsc{Ours}}" "\n")

LABELS = r"""\begin{document}\Large
\begin{tabular}{>{\raggedright\arraybackslash}p{8.6cm}l>{\raggedright\arraybackslash}p{5.6cm}}
\toprule
Case & Label & In our data \\
\midrule
Camera processing, JPEG, video coding & \textcolor{cr}{\textbf{real}} & all sets \\[3pt]
Make-up worn at capture & \textcolor{cr}{\textbf{real}} & incidental \\[3pt]
Beautification by an app or a service, neural or not & \textcolor{cl}{\textbf{filter}} & scripted, 3 services, app presets \\[3pt]
Reenactment by another person's performance & \textcolor{cf}{\textbf{fake}} & Face2Face, NeuralTextures \\[3pt]
A part from another face, or inpainted & \textcolor{cf}{\textbf{fake}} & part-level forgeries \\[3pt]
Face swap & \textcolor{cf}{\textbf{fake}} & FF++, Celeb-DF, DFD \\[3pt]
Beautified forgery & \textcolor{cf}{\textbf{fake}} & FF++, Celeb-DF-B \\[3pt]
Expression editing; synthesised face & \textcolor{cf}{\textbf{fake}} & \cellcolor{fail}not tested \\
\bottomrule
\end{tabular}
\end{document}
"""


def main():
    (H / "tex/tab_labels.tex").write_text(HEAD + LABELS, encoding="utf-8")
    t = (P / "tables/tab_splits.tex").read_text(encoding="utf-8")
    row = next(l for l in t.splitlines() if l.startswith("Commercial & originals"))
    cells = row.rstrip(" \\").split(" & ")
    for k in (5, 6, 7):                      # Ours train / val / test on untouched commercial originals
        cells[k] = r"\cellcolor{fail}" + cells[k]
    t = t.replace(row, " & ".join(cells) + r" \\")
    (H / "tex/tab_splits.tex").write_text(HEAD + r"\begin{document}\Large" + "\n" + t + r"\end{document}" + "\n", encoding="utf-8")
    for name in ("fig_training", "fig_confusion"):
        fitz.open(P / f"figs/{name}.pdf")[0].get_pixmap(dpi=400).save(H / f"assets/{name}.png"); print("->", name)


if __name__ == "__main__":
    main()
