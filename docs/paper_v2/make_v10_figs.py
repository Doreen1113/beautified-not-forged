"""v10 figure wiring (2026-10-28), applied in place to main_v10.tex after make_v10_humanize.py:
Fig. 1 becomes the motivated example fig_teaser_v9 (one retouching pair, one Celeb-DF-B video, four CLIP detectors' scores);
the seventeen-detector dot panels of the old Fig. 1 become fig_dirs_v9 in Sec. III-B. Exact-string replacement; aborts if a
target is not found exactly once."""
from pathlib import Path
D = Path(r"C:\My_Project\AIGC\docs\paper_v2")
p = D / "main_v10.tex"; s = p.read_text(encoding="utf-8")
R = []
t0 = s.index("\\IEEEaftertitletext{"); t1 = s.index("\\maketitle")
R.append((s[t0:t1], r"""\IEEEaftertitletext{\vspace{-0.6\baselineskip}\begin{center}
\includegraphics[width=0.98\textwidth]{fig_teaser_v9}
\captionof{figure}{One cue, two errors. (a) A genuine FFHQ photograph and its render by a commercial retouching service
(skin smoothing, strongest level): the four CLIP-based detectors call the original genuine and the retouched copy forged.
(b) A Celeb-DF-B face-swap video as recorded and after an app beauty preset: the same detectors catch the deepfake as
recorded and miss it after the preset. Bars are $P(\text{fake})$, ticks are each detector's own threshold, set where it
accuses 5\% of the untouched genuine faces of the same source; (b) uses the video mean over 32 frames. Across seventeen
published detectors the pattern is the rule, not the exception (Fig.~\ref{fig:dirs}).}
% figs/fig_teaser_v9.pdf, make_fig_teaser_v9.py: (a) published_scores_<det>.npz stem 17003, orig_0 / Smoothing_90, threshold =
% 95th pct of orig_0 (Effort 0.11 -> 0.72, thr 0.66; Forensics Adapter 0.17 -> 0.95, thr 0.59; GenD 0.19 -> 0.97, thr 0.84;
% DFD-HR 0.27 -> 0.94, thr 0.54). (b) celebdfb_v2_20260927/scores_v3/<det>.npz video id17_id35_0000, means over frames,
% threshold = 95th pct of real/ (Effort 0.96 -> 0.63, thr 0.81; FA 0.99 -> 0.66, thr 0.85; GenD 0.92 -> 0.67, thr 0.86;
% DFD-HR 0.94 -> 0.61, thr 0.63); frame f05 shown (its own scores: Effort 0.97 -> 0.44, FA 1.00 -> 0.67, GenD 0.89 -> 0.70,
% DFD-HR 0.99 -> 0.74).
\label{fig:teaser}
\end{center}\vspace{0.1\baselineskip}}
"""))
R.append(("""Fig.~\\ref{fig:teaser} shows what happens today: for fifteen of the seventeen published detectors we scored, the retouched copy
outranks the original in 89--99\\% of pairs.""",
          """Fig.~\\ref{fig:teaser} shows what happens today on one photograph and one video; across the seventeen published detectors we
scored, the retouched copy outranks the original in 89--99\\% of pairs for fifteen of them (Fig.~\\ref{fig:dirs})."""))
R.append(("is the quantity of Fig.~\\ref{fig:teaser}.", "is the quantity of Fig.~\\ref{fig:dirs}."))
# results figure in Sec. III-B, before the Direction B table
R.append(("""\\subsection{Direction B: the escape}
\\label{sec:escape}
""", r"""\subsection{Direction B: the escape}
\label{sec:escape}
\begin{figure*}[t]
\centering
\includegraphics[width=0.98\textwidth]{fig_dirs_v9}
\caption{The two directions on seventeen published detectors and ours, one row per detector. (a) Direction A: share of the
2,210 Smoothing-90 renders accused at the threshold that accuses 5\% of the untouched originals (dot, 95\% interval over pairs;
dashed line: the 5\% floor); the grey number is the threshold-free reading, the share of pairs in which the render scores above
its own original. NPR is n/a because its scores saturate. (b) Direction B: rise of the miss rate on Celeb-DF-B deepfakes from
the app presets alone, re-encoding subtracted (95\% video-cluster intervals). Families from top to bottom: face-forgery CNNs,
generated-image detectors, CLIP-based detectors, ours (two seeds).}
% figs/fig_dirs_v9.pdf, make_fig_dirs_v9.py (= panels b, c of the former fig_teaser_v8b) from alipair_zeroshot_20260929/
% main_claim_A.json (fa_s90_at_5pct, fa_ci, paired_up) and celebdfb_v2_20260927/fair_cdfb.json (d_miss_beauty_only, ci).
\label{fig:dirs}
\end{figure*}
"""))
import re
def flex(a):
    return r"\s+".join(re.escape(t) for t in a.split())
for a, b in R:
    m = list(re.finditer(flex(a), s))
    if len(m) != 1:
        raise SystemExit(f"count {len(m)}: {a[:90]!r}")
    s = s[:m[0].start()] + b + s[m[0].end():]
p.write_text(s, encoding="utf-8"); print("main_v10.tex figures wired,", len(R), "edits")
