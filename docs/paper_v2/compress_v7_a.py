"""v7 compression pass A: chain subsection, untreated-detection subsection, rule and sources paragraphs, protocol figure out."""
from pathlib import Path

p = Path(__file__).resolve().parent / "main_v7.tex"; s = p.read_text(encoding="utf-8")


def cut(start, end, new, keep_end=True):
    global s
    a = s.index(start); b = s.index(end, a)
    s = s[:a] + new + (s[b:] if keep_end else s[b + len(end):])


chain = r"""\subsection{Smoothing views: what the exposure arms taught}
\label{sec:chain}
Three findings from FF++-only arms with pre-registered bars (supplement Sec.~\ref{S-sec:chain},
Table~\ref{S-tab:tradeofffull}). First, no other view substitutes for smoothing: P0 accuses 44--56\% of the Smoothing-90
renders although it trains with label-symmetric blur, rescaling and JPEG, and removing smoothing from the beautified views
(P2-nosmooth) brings the accusation back to 55--67\%. Second, genuine-only smoothing views are an evasion route: P1-smooth
accuses 0.7--1.0\% of the renders and then misses 96--100\% of bilaterally smoothed forgeries on frames it has never seen
(a miss rise of 56--63 points), 75--84\% of median-filtered ones and 51--54\% of blended ones; it has learnt that smoothed means
genuine. Third, a class-asymmetric form is learnt as a label: when genuine items receive face-local smoothing and forged items
a whole-crop filter, a whole-crop filter on a genuine frame is called forged in 35--90\% of frames by \oursF{}, against
1--40\% for P0. Drawing one form for both classes (P2-sym) removes the whole-crop accusation (false alarms 2--6\%) but not
the skin-only one (38--99\%), and under Effort's tuning scheme it meets only one of its two bars. These limits are what the
constraint of Sec.~\ref{sec:sic} addresses.

"""
cut("\\subsection{Skin smoothing: a chain of pre-registered arms}", "\\subsection{Removing the cue: SIC}", chain)

untreated = r"""\textbf{Celeb-DF-v2 and DFD.} Each baseline is scored on its own crop and our models on ours (Table~\ref{S-tab:reproduce}).
\oursB{} reaches a frame AUC of 0.914 on Celeb-DF-v2 and 0.961 on DFD (second seed 0.923 and 0.951): above Effort on both
sets, above all four CLIP detectors on DFD, and on par with Forensics Adapter and GenD on Celeb-DF-v2 (paired intervals). Under
the app presets it keeps 0.896 and 0.904 against 0.807--0.838 for the four CLIP detectors, every paired interval above zero
under video and identity resampling (Table~\ref{S-tab:cdfbpaired}); the equal-data arm P0 is 0.022--0.053 above them as well.
Identity resampling changes 24 of 563 intervals, none of them a headline (Table~\ref{S-tab:identity}).

\textbf{Forgery head only against the full model.} On the same data \oursB{} is above \oursF{} on Celeb-DF-v2 frames
($+0.023$, $+0.036$), on Celeb-DF-B under the presets ($+0.030$, $+0.021$) and most on DF40 reenactment ($+0.076$ to $+0.145$),
every interval above zero on both seeds: the shared beautified head costs detection.

\textbf{DF40} (Table~\ref{tab:df40}). On the nine face-swap methods \oursB{} is on par with GenD, at or above Effort and
Forensics Adapter, and 0.012--0.024 behind DFD-HR. On the twelve reenactment methods it is 0.076--0.094 behind GenD and DFD-HR in
the FF++ domain and 0.13--0.18 behind GenD in the Celeb-DF domain, on par with Effort and Forensics Adapter; every SIC member
is a further 0.06--0.09 below (Sec.~\ref{sec:sicres}). Across the published detectors the share of smoothed renders ranked
above their original does not predict reenactment AUC ($\rho=0.36$, $p=0.23$), so we claim no link beyond our arms. On six
entire-face synthesis methods our models are below Effort and GenD on every method (Table~\ref{S-tab:efs}), and the three-way
model sends 42--89\% of ddim and SiT stills to \emph{beautified}: smooth synthesised skin is absorbed by that class.

"""
cut("\\textbf{Celeb-DF-v2 and DFD.} Each DeepfakeBench-trained baseline", "\\subsection{Localisation and restoration of part-level forgeries}", untreated)

rule = r"""\textbf{Rule.} A detector should return a forgery score that does not move when a face is beautified; whether a face was
beautified can be reported as a separate attribute, and every detection number reads the forgery score alone. Each detector is
scored by $P(\text{fake})$ with the threshold that accuses 5\% of each source's untreated genuine frames; we also report one
deployable threshold per detector (95th percentile on 530 genuine FF++ validation frames) and, where originals exist, the
share of pairs in which the beautified face scores above its own original, which needs no threshold. Under beautification we
report the false-alarm rate FA (genuine faces called fake) and the miss rate MISS (forgeries not called fake); a forgery that
a three-way model sends to its beautified class is a miss. AUCs are labelled frame or video level. Intervals are 95\%
percentile bootstraps over videos, originals or pairs with the threshold re-estimated in every draw (1,000 draws, 500 for the
filter sources), repeated with identities as the unit where videos share them (supplement); differences between models use
identical draws.

"""
cut("\\textbf{Requirement and rule.}", "\\textbf{Sources.}", rule)

sources = r"""\textbf{Sources.} Six beautification sources, four of them untouched by every training and design decision.
\emph{Celeb-DF-B}~\cite{libourel2024}: 232 Celeb-DF-v2 videos per condition (as recorded, re-encoded, beautified by one of
four app presets; genuine and synthesised), 32 frames each; the rise under a preset is read minus the rise under re-encoding.
\emph{Colour filters}: 516 Celeb-DF-v2 test videos~\cite{celebdf} under eleven filters~\cite{pilgram} (a development source)
and 332 DFD videos~\cite{dfd} under sixteen filters from a second library, built after every method decision. \emph{AR
filters}~\cite{openfilter2022}: FairBeauty, 2,927 FairFace photographs and their Instagram AR renders, and B-LFW, 3,000 LFW
pairs; the AR engine re-renders the face through its own capture path, so these numbers are an upper bound on the effect of
the beautification itself. \emph{Commercial retouching}: 2,210 FFHQ originals and their renders by one service from
RetouchingFFHQ~\cite{retouchingffhq} (four operations, three levels), image-disjoint from our training originals; no model was
trained on it, but it was read during the study, so it is an analysis set rather than a clean test. \emph{Scripted smoothing}:
4,016 Celeb-DF-v2 test frames (1,348 genuine, 513 videos) under a whole-crop bilateral filter at three strengths, a median
filter, a Gaussian blend, and a bilateral filter inside the landmark face hull at two strengths (\emph{face-local}), applied
to both classes. \emph{Untreated detection}: Celeb-DF-v2, DFD and the held-out methods of DF40~\cite{df40}. The supplement
gives every count and preprocessing step.

"""
cut("\\textbf{Sources.} \\emph{Celeb-DF-B}", "\\begin{figure}[t]\n\\centering\n\\includegraphics[width=\\columnwidth]{figs_tikz/fig_protocol}", sources)
# protocol figure out
a = s.index("\\begin{figure}[t]\n\\centering\n\\includegraphics[width=\\columnwidth]{figs_tikz/fig_protocol}"); b = s.index("\\end{figure}", a) + len("\\end{figure}\n")
s = s[:a] + s[b:]
s = s.replace(" (Fig.~\\ref{fig:protocol})", "")
p.write_text(s, encoding="utf-8"); print("pass A done; fig:protocol refs left:", s.count("fig:protocol"))
