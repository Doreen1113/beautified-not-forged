"""Assemble main_v7.tex from main_v6b.tex: new abstract and introduction (ABSTRACT_INTRO_v7_draft.tex), v7 figures
(teaser, exposure, architecture, band energy) with new captions. Result-dependent text keeps [[placeholders]].
python make_v7_skeleton.py"""
import re
from pathlib import Path

H = Path(__file__).resolve().parent
src = (H / "main_v6b.tex").read_text(encoding="utf-8")
draft = (H / "ABSTRACT_INTRO_v7_draft.tex").read_text(encoding="utf-8")
B = "\\"   # one backslash

abs_new = draft[draft.index(B + "begin{abstract}"):draft.index(B + "end{abstract}") + len(B + "end{abstract}")]
intro_new = draft[draft.index(B + "section{Introduction}"):].rstrip() + "\n\n"
s = src
s = re.sub(r"\\title\{[^\n]*\}", lambda m: B + "title{Beautified Is Not Forged: Skin Smoothing Is a Shared Shortcut of Face-Forgery Detectors}", s, count=1)
a0 = s.index(B + "begin{abstract}"); a1 = s.index(B + "end{abstract}") + len(B + "end{abstract}"); s = s[:a0] + abs_new + s[a1:]
i0 = s.index(B + "section{Introduction}"); i1 = s.index("% ----------------------------------------------------------------------------\n" + B + "section{Related Work}")
s = s[:i0] + intro_new + s[i1:]

t0 = s.index(B + "includegraphics[width=0.79" + B + "textwidth]{fig_teaser_v6b}"); t1 = s.index(B + "label{fig:teaser}")
teaser = r"""\includegraphics[width=0.98\textwidth]{fig_teaser_v7}
\captionof{figure}{Every published detector scores a skin-smoothed genuine face as more forged than the same face untouched.
Left: three FFHQ photographs and their renders by a commercial retouching service (skin smoothing, strongest level). Right: for
sixteen published detectors and two of ours, where the smoothed render falls among the 2,210 untouched originals (quantile of
the forgery score; 0.95 is the threshold that accuses 5\% of originals), with the share of pairs in which the render scores
above its own original at the right. NPR is omitted: its scores saturate on this source. Families: face-forgery CNNs,
generated-image detector, CLIP-based detectors, ours.}"""
s = s[:t0] + teaser + s[t1:]

s = s.replace(B + "includegraphics[width=" + B + "columnwidth]{figs_tikz/fig_arch}", B + "includegraphics[width=" + B + "columnwidth]{figs_tikz/fig_arch_v7}")
c0 = s.index(B + "caption{The full model. A frozen CLIP ViT-L/14 with rank-16 LoRA on the q, k, v and output projections of all 24 blocks; linear")
c1 = s.index(B + "label{fig:arch}")
arch_cap = r"""\caption{The model and the training rule. A frozen CLIP ViT-L/14 with rank-16 LoRA on the q, k, v and output projections
of all 24 blocks (3.2\,M of 306\,M parameters trained); linear heads on the CLS token give the forged logit $z_f$, the
beautified logit $z_b$ and four operation presence and quantity scores; a linear layer on the 256 patch tokens gives the
$16\times16$ evidence map $\hat m$, trained with BCE and Dice against the exact footprint $M$ of the edit. The forgery decision
reads $P(\text{fake})=\sigma(z_f)$ only. Training only: a skin-smoothed copy $x_s$ of every item, drawn by one operator for
every class, passes through the same network and $\mathcal{L}_\text{cons}=\lambda\,(z_f(x)-z_f(x_s))^2$ ties its forged logit
to the clean one (SIC, Sec.~\ref{sec:sic}). Example: a held-out part-level forgery (mouth of another identity) and its map.}
"""
s = s[:c0] + arch_cap + s[c1:]

s = s.replace(B + "includegraphics[width=" + B + "columnwidth]{figs_tikz/fig_exposure}", B + "includegraphics[width=" + B + "columnwidth]{fig_exposure_v7}")
e0 = s.index(B + "caption{Which class receives beautified training views decides the sign of the error (FF++-only arms, first seed;")
e1 = s.index(B + "label{fig:exposure}")
exp_cap = r"""\caption{Which class receives smoothed training views sets the sign of the error. FF++-only arms with the same architecture,
data and recipe, first seed (Table~\ref{tab:tradeoff}). FA: commercial Smoothing-90 renders accused at the threshold that
accuses 5\% of their originals. $\Delta$miss: change of the miss rate on Celeb-DF-v2 forgeries under strong whole-crop
smoothing at the same rule; a negative change means the arm accuses every smoothed face. Thumbnails show the training views
each class receives; a badge marks a class that receives smoothed views. P1 opens an evasion route; P3 accuses.}
"""
s = s[:e0] + exp_cap + s[e1:]

d0 = s.index(B + "subsection{Dose response}")
band = r"""\subsection{Dose response}
\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{fig_bandenergy}
\caption{The shared cue is the beautification signature, not blur. (a) Texture loss of eight smoothing forms, measured as the
high-frequency energy removed inside the face hull of 400 genuine Celeb-DF-v2 frames (commercial Smoothing-90 on 200 FFHQ
pairs, hollow). (b) False-alarm rate of each published detector at each form against that loss: pooled Spearman $-0.01$.
A Gaussian blend removes the most energy and is accused least; a face-local bilateral filter removes less and is accused by
nearly every detector. [[matched contrasts sentence]]}
\label{fig:bandenergy}
\end{figure}
"""
s = s[:d0] + band + s[d0 + len(B + "subsection{Dose response}"):]
(H / "main_v7.tex").write_text(s, encoding="utf-8")
print("main_v7.tex written;", len(s.split()), "words;", s.count("[["), "placeholders")
