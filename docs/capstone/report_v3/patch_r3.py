"""Report round 3 (2026-10-29): architecture and explanation figures in TikZ, the page's result card as a figure, the
exposure experiment as bars, accusation per operation and strength, and two tables (three-class recall, per-operation
routing). Exact string replacement with unique anchors; idempotent; backup report_pre_r3.tex.
python patch_r3.py"""
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent; P = HERE / "report.tex"
t = P.read_text(encoding="utf-8")
if "fig_arch.tex" in t:
    print("already patched"); raise SystemExit
bak = HERE / "report_pre_r3.tex"
if not bak.exists():
    shutil.copy2(P, bak)

EDITS = [
    # preamble
    (r"\usepackage{xcolor}" + "\n",
     r"\usepackage{xcolor}" + "\n" + r"\usepackage{tikz}" + "\n" + r"\usetikzlibrary{positioning,arrows.meta}" + "\n" + r"\usepackage{pifont}" + "\n"),
    # system overview at the start of Methods
    (r"\section{Methods and Steps}" + "\n",
     r"\section{Methods and Steps}" + "\n\n" +
     r"Figure~\ref{fig:arch} gives the system. Steps 1 to 6 run on the user's device; the detector is trained once, offline." + "\n\n" +
     r"\begin{figure}[t]" + "\n" + r"\centering" + "\n" + r"\input{figs/fig_arch.tex}" + "\n" +
     r"\caption{System architecture. Blue: the neural network, trained once offline (top). Green: code with fixed rules." + "\n" +
     r"Purple: the checks a sentence must pass before it is shown. The record produced by steps 2 and 3 is the only input to the" + "\n" +
     r"sentences; no language model writes or rewords them.}" + "\n" + r"\label{fig:arch}" + "\n" + r"\end{figure}" + "\n"),
    # explanation figure after the sentences paragraph
    (r"answer (the difference from an original, identity, certainty, the meaning of the score) get fixed sentences." + "\n",
     r"answer (the difference from an original, identity, certainty, the meaning of the score) get fixed sentences." + "\n" +
     r"Figure~\ref{fig:explain} shows the composition and the checks on one held-out record." + "\n\n" +
     r"\begin{figure}[t]" + "\n" + r"\centering" + "\n" + r"\input{figs/fig_explain.tex}" + "\n" +
     r"\caption{How the sentences are composed and checked, on one held-out record (FFHQ 17042 with the nose replaced from" + "\n" +
     r"another photograph). Every number in the text is copied from the record; the third template stays silent because no" + "\n" +
     r"operation reaches the threshold. The bottom row is a sentence the checker rejects.}" + "\n" +
     r"\label{fig:explain}" + "\n" + r"\end{figure}" + "\n"),
    # the browser system: result card instead of the old strip figure
    (r"Figure~\ref{fig:pipeline} draws the shipped path on one real record. The page loads",
     r"Figure~\ref{fig:output} shows the page's result card on two of the bundled examples. The page loads"),
    (r"\begin{figure}[t]" + "\n" + r"\centering" + "\n" + r"\includegraphics[width=\textwidth]{figs/pipeline_en.pdf}" + "\n" +
     r"\caption{The shipped path on one held-out part-level forgery (FF++ test frame 454 with the mouth replaced from a donor):" + "\n" +
     r"landmarks and crop; class scores and evidence map; part masks and the named part; the record, the composed sentences and the" + "\n" +
     r"checks. Restoring the mouth from the original lowers the forgery score from 1.00 to 0.08.}" + "\n" +
     r"\label{fig:pipeline}" + "\n" + r"\end{figure}" + "\n",
     r"\begin{figure}[p]" + "\n" + r"\centering" + "\n" +
     r"\includegraphics[width=0.96\textwidth]{figs/fig_output_a.png}\\[2pt]" + "\n" +
     r"{\small (a) Example 2: FF++ test frame 454, the mouth replaced from a donor (held out).}\\[8pt]" + "\n" +
     r"\includegraphics[width=0.96\textwidth]{figs/fig_output_b.png}\\[2pt]" + "\n" +
     r"{\small (b) Example 3: FFHQ 17001 rendered by the Alibaba service at Smoothing-90 (a service never used in training).}" + "\n" +
     r"\caption{The page's result card (browser model, 1366 px viewport, 2026-10-29). Left: the photo with the evidence outline" + "\n" +
     r"(yellow: strongest evidence; cyan: half strength) and the named part. Right: the forgery and retouch chips with raw scores," + "\n" +
     r"the three-way decision, the sentences composed by code with the badge of the checker, and, when beautification is detected," + "\n" +
     r"the four operation scores. In (a) restoring the mouth from the original lowers the forgery score from 1.00 to 0.08. In (b)" + "\n" +
     r"the browser model also raises the eye, slimming and whitening scores on a smoothing-only render; the page says under the" + "\n" +
     r"bars that only the smoothing score is reliable across services (Section~\ref{sec:res-text}).}" + "\n" +
     r"\label{fig:output}" + "\n" + r"\end{figure}" + "\n"),
    # exposure figure
    (r"\includegraphics[width=0.66\textwidth]{figs/fig_exposure_v10.pdf}",
     r"\includegraphics[width=\textwidth]{figs/fig_exposure_r3.pdf}"),
    (r"\caption{The training-exposure experiment (seed 1). FA: commercial Smoothing-90 renders accused at 5\% false alarms on their" + "\n" +
     r"originals. $\Delta$miss: change in the miss rate on strongly smoothed Celeb-DF-v2 forgeries. Smoothing seen only by forged faces" + "\n" +
     r"(P3) produces the accusation; seen only by genuine faces (P1) it produces the escape.}",
     r"\caption{The training-exposure experiment (seed 1, 95\% bootstrap intervals). Under each arm: which class saw skin-smoothed" + "\n" +
     r"views in training. Left: commercial Smoothing-90 renders accused at 5\% false alarms on their originals. Right: change in the" + "\n" +
     r"miss rate on strongly smoothed Celeb-DF-v2 forgeries. Smoothing seen only by forged faces (P3) produces the accusation; seen" + "\n" +
     r"only by genuine faces (P1) it produces the escape; seen by both (P2) neither.}"),
    # three-class accuracy first in the results
    (r"\section{Performance Evaluation and Results}" + "\n",
     r"\section{Performance Evaluation and Results}" + "\n\n" +
     r"\subsection{Three-class accuracy on held-out data}" + "\n" + r"\label{sec:res-threeclass}" + "\n\n" +
     r"Table~\ref{tab:threeclass} gives the per-class recall on the FF++ (c23) test split, 7,936 frames of 140 videos never used" + "\n" +
     r"for training or selection, and the direction of the errors. The main model keeps every class above 80\% on seed 1; its errors" + "\n" +
     r"are genuine frames called beautified (11.4\%) rather than forged (5.9\%), and beautified frames called genuine (9.0\%) rather" + "\n" +
     r"than forged (4.3\%). The browser model trades beautified recall for a higher forged recall. On ordinary photographs outside" + "\n" +
     r"FF++ the main model calls 78.4\% of the 2,210 untouched FFHQ originals real, 20.8\% beautified and 0.8\% forged" + "\n" +
     r"(Table~\ref{tab:perop}); the cross-dataset video results are in Table~\ref{tab:browser}." + "\n\n" +
     r"\begin{table}[t]" + "\n" + r"\centering" + "\n" +
     r"\caption{Three-class recall (\%) on the FF++ test split and the direction of the errors (\%). Main: CLIP ViT-L/14 + LoRA," + "\n" +
     r"seed 1 / seed 2. Browser: EfficientNet-B4 shipped on the page. The candidate of Section~\ref{sec:res-browser} is read" + "\n" +
     r"after its pre-declared gate.}" + "\n" + r"\label{tab:threeclass}" + "\n" + r"\small" + "\n" +
     r"\begin{adjustbox}{max width=\textwidth}" + "\n" + r"\begin{tabular}{@{}lccccccc@{}}" + "\n" + r"\toprule" + "\n" +
     r" & \multicolumn{3}{c}{recall} & \multicolumn{4}{c}{errors} \\" + "\n" + r"\cmidrule(lr){2-4}\cmidrule(lr){5-8}" + "\n" +
     r"Model & real & forged & beautified & real$\to$forged & real$\to$beautified & beautified$\to$forged & beautified$\to$real \\" + "\n" +
     r"\midrule" + "\n" +
     r"Main (s1 / s2) & 82.7 / 76.9 & 90.9 / 92.3 & 86.7 / 86.3 & 5.9 / 9.0 & 11.4 / 14.1 & 4.3 / 6.5 & 9.0 / 7.3 \\" + "\n" +
     r"Browser, shipped & 74.2 & 93.3 & 76.4 & 11.6 & 14.1 & 11.7 & 11.9 \\" + "\n" +
     r"Browser, candidate & \pending{} & \pending{} & \pending{} & \pending{} & \pending{} & \pending{} & \pending{} \\" + "\n" +
     r"\bottomrule" + "\n" + r"\end{tabular}" + "\n" + r"\end{adjustbox}" + "\n" + r"\end{table}" + "\n"),
    # per operation and strength after the two-axis figure
    (r"\label{fig:twoaxis}" + "\n" + r"\end{figure}" + "\n",
     r"\label{fig:twoaxis}" + "\n" + r"\end{figure}" + "\n\n" +
     r"\subsection{Per operation and per strength}" + "\n" + r"\label{sec:res-perop}" + "\n\n" +
     r"Figure~\ref{fig:perop} breaks the accusation down by operation and strength. For eye enlarging, face slimming and whitening" + "\n" +
     r"every detector stays near the 5\% floor at every strength (Effort and UnivFD reach 11 to 17\% on the strongest eye" + "\n" +
     r"enlarging); for skin smoothing the published detectors rise with strength to 37 to 52\% at level 90 (UnivFD 16.6\%), while" + "\n" +
     r"ours stays between 5.0 and 12.5\%. Table~\ref{tab:perop} gives the three-way routing of our model on the same pairs: a" + "\n" +
     r"render is called forged in at most 0.8\% of pairs at any operation and strength; smoothing is called beautified in 90 to 99\%" + "\n" +
     r"of pairs; eye enlarging, face slimming and whitening are called beautified in 46 to 72\% of pairs and otherwise real, although" + "\n" +
     r"the render's beautified score exceeds its own original's in 84 to 98\% of pairs. The three single operations are therefore" + "\n" +
     r"detected relative to the original but not reliably in absolute terms, the limitation stated in Section~\ref{sec:res-text}." + "\n\n" +
     r"\begin{figure}[t]" + "\n" + r"\centering" + "\n" + r"\includegraphics[width=\textwidth]{figs/fig_perop.pdf}" + "\n" +
     r"\caption{Genuine faces accused after each retouching operation of the Alibaba service, at strengths 30, 60 and 90, at the" + "\n" +
     r"threshold that accuses 5\% of the untouched originals (dashed line). 2,210 pairs per cell. Five published detectors and" + "\n" +
     r"both seeds of our model.}" + "\n" + r"\label{fig:perop}" + "\n" + r"\end{figure}" + "\n\n" +
     r"\begin{table}[t]" + "\n" + r"\centering" + "\n" +
     r"\caption{Our model (seed 1) on the 2,210 Alibaba pairs per operation and strength: where the three-way decision routes the" + "\n" +
     r"render (\%), the share of pairs in which the render's beautified score exceeds its own original's (paired rank, \%), and" + "\n" +
     r"the renders accused at the 5\% FPR threshold of Figure~\ref{fig:perop} (\%). The untouched originals are routed real 78.4," + "\n" +
     r"forged 0.8, beautified 20.8.}" + "\n" + r"\label{tab:perop}" + "\n" + r"\small" + "\n" +
     r"\begin{tabular}{@{}llccccc@{}}" + "\n" + r"\toprule" + "\n" +
     r"Operation & strength & $\to$ real & $\to$ forged & $\to$ beautified & paired rank & accused \\" + "\n" + r"\midrule" + "\n" +
     r"Eye enlarging & 30 & 52.9 & 0.5 & 46.5 & 92.4 & 4.4 \\" + "\n" +
     r" & 60 & 39.7 & 0.5 & 59.8 & 96.3 & 4.3 \\" + "\n" +
     r" & 90 & 29.8 & 0.5 & 69.7 & 97.6 & 3.6 \\" + "\n" +
     r"Face slimming & 30 & 53.5 & 0.4 & 46.1 & 84.1 & 4.2 \\" + "\n" +
     r" & 60 & 46.0 & 0.4 & 53.7 & 89.8 & 3.9 \\" + "\n" +
     r" & 90 & 38.3 & 0.4 & 61.3 & 93.7 & 3.7 \\" + "\n" +
     r"Whitening & 30 & 47.9 & 0.6 & 51.5 & 85.4 & 4.3 \\" + "\n" +
     r" & 60 & 35.8 & 0.6 & 63.6 & 87.6 & 4.1 \\" + "\n" +
     r" & 90 & 26.9 & 0.8 & 72.3 & 92.2 & 4.8 \\" + "\n" +
     r"Skin smoothing & 30 & 8.9 & 0.6 & 90.5 & 97.6 & 6.2 \\" + "\n" +
     r" & 60 & 0.7 & 0.4 & 99.0 & 99.4 & 5.0 \\" + "\n" +
     r" & 90 & 0.5 & 0.8 & 98.8 & 99.2 & 8.6 \\" + "\n" +
     r"\bottomrule" + "\n" + r"\end{tabular}" + "\n" + r"\end{table}" + "\n"),
    # appendix sources
    (r"\item Costs: \texttt{docs/paper\_v2/tables/tab\_v4\_df40.tex};",
     r"\item Figures~\ref{fig:arch} and \ref{fig:explain}: drawn in TikZ (\texttt{docs/capstone/report\_v3/figs/}); the record" + "\n" +
     r"of Figure~\ref{fig:explain} is \texttt{docs/demo\_ru/test/fixture\_t2.json}, id \texttt{ffhq\_demo\_edit:17042\_nose}." + "\n" +
     r"\item Figure~\ref{fig:output}: \texttt{docs/demo\_ru/test/take\_screens.py}, shots \texttt{1366\_example2}," + "\n" +
     r"\texttt{1366\_example3} (2026-10-29), cropped by \texttt{make\_figs\_r3.py}." + "\n" +
     r"\item Table~\ref{tab:threeclass}: \texttt{retouch\_unified\_20260929/RESULTS\_clipe5\_s20260929.md} and" + "\n" +
     r"\texttt{\ldots\_s20260930.md} (block ``FF++ / cross-dataset''); browser row \texttt{split\_eval.json} (\texttt{Ours-lite})." + "\n" +
     r"\item Figure~\ref{fig:perop}, Table~\ref{tab:perop}: \texttt{alipair\_zeroshot\_20260929/published\_ali.json}" + "\n" +
     r"(\texttt{by\_op}, \texttt{fake\_at\_t}); routing and paired rank \texttt{RESULTS\_clipe5\_s20260929.md} (Alibaba table)." + "\n" +
     r"\item Costs: \texttt{docs/paper\_v2/tables/tab\_v4\_df40.tex};"),
]
for old, new in EDITS:
    assert t.count(old) == 1, ("anchor", t.count(old), old[:90])
    t = t.replace(old, new)
assert "fig:pipeline" not in t
P.write_text(t, encoding="utf-8"); print("patched report.tex; backup", bak.name)

b = HERE / "build.sh"; s = b.read_text(encoding="utf-8")
if "figs/*.png" not in s:
    s = s.replace("scp -q figs/*.pdf gsplat-ubuntu:paper_build/capstone_v3/figs/",
                  "scp -q figs/*.pdf figs/*.png figs/*.tex gsplat-ubuntu:paper_build/capstone_v3/figs/")
    b.write_text(s, encoding="utf-8"); print("patched build.sh")
