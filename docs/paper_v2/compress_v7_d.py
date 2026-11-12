"""v7 compression pass D: boundary and notation tables out, DF40 table out, exposure subsection, limitations, conclusion."""
from pathlib import Path

p = Path(__file__).resolve().parent / "main_v7.tex"; s = p.read_text(encoding="utf-8")


def cut(start, end, new, inclusive_end=False):
    global s
    a = s.index(start); b = s.index(end, a + 1)
    if inclusive_end:
        b += len(end)
    s = s[:a] + new + s[b:]


def drop_float(label):
    global s
    i = s.index("\\label{" + label + "}"); a = s.rfind("\\begin{table", 0, i); b = s.index("\\end{table", i); b = s.index("}", b) + 1
    if s[b] == "\n":
        b += 1
    s = s[:a] + s[b:]


drop_float("tab:boundary"); drop_float("tab:notation"); drop_float("tab:df40")
s = s.replace("Table~\\ref{tab:boundary} lists the cases near the boundary\n(17 rows in Table~\\ref{S-tab:labels}).", "The supplement lists 17 cases near the boundary with their labels.")
s = s.replace("(Table~\\ref{tab:notation}, Fig.~\\ref{fig:exposure})", "(Fig.~\\ref{fig:exposure}; arm definitions in the supplement)")
s = s.replace("\\textbf{DF40} (Table~\\ref{tab:df40}).", "\\textbf{DF40} (Table~\\ref{S-tab:v4df40full}).")
s = s.replace("(Table~\\ref{tab:notation})", "(supplement)")

exposure = r"""With architecture, data and recipe fixed, P0--P3 differ only in which class receives beautified views
(Fig.~\ref{fig:exposure}; arm definitions in the supplement). On Celeb-DF-B the beautification-specific miss rise is
11--17 points for P0 (three seeds), 20--22 for P1 and 10--13 for P2; P1 exceeds P0 by 4.5--9.5 points in every seed
(Holm-adjusted $p\le0.01$), while P2 against P0 changes sign within the seed spread (Table~\ref{S-tab:exposure}). The
forged-only arm P3 (one seed, pre-declared reading) mirrors P1: it accuses 63.8\% of the Smoothing-90 renders ($+9.6$ over P0)
and 98--100\% of smoothed genuine frames, catches smoothed forgeries more often than untreated ones, and accuses 47\% of filtered
Celeb-DF-v2 genuine frames against 19\% for P0 (Table~\ref{S-tab:p3}). The sign rule holds: genuine-only views lower the
accusation and open evasion, forged-only views raise the accusation and close evasion, and views on both classes sit in between.
Exposure moves errors between misses and false alarms; it does not make the classes more separable (P3 untreated Celeb-DF-v2
video AUC 0.943 against 0.938 for P0). P0 already keeps more AUC under the presets (0.86--0.88) than released Effort (0.81), so
most of the margin of our models over the CLIP baselines comes from the base recipe, not from exposure.

"""
cut("With architecture, data and recipe fixed, P0--P3 differ only in which class receives beautified views", "\\subsection{Smoothing views: what the exposure arms taught}", exposure)

limits = r"""\section{Limitations}
\label{sec:limits}
The measurement covers four app presets, 27 colour filters, eight AR filters on two face sets and one retouching service that
became an analysis set; a fresh smoothing source is needed, and the AR capture path is confounded with the beautification. The
class boundary is stated, not measured. P3 and the one-sided, Gaussian and $\lambda=0.03$ arms have one seed, and no non-CLIP
pipeline was trained with the rule. Our models accuse AR renders as much as the published CLIP detectors (\oursB{} 79--90\%,
SIC 68\%), so the rule removes the accusation for the smoothing family it was drawn from, not for beautification in general.
\oursB{} is behind GenD and DFD-HR on DF40 reenactment and every SIC member is a further 0.06--0.09 below; the full model's
beautified head costs detection and sends 21\% of the service's originals to the beautified class. Effort and DFD-HR were not
reproduced at their published numbers, DFDC is not evaluated, and inference cost was not measured.

\section{Conclusion}
Seventeen published detectors share one failure: a skin-smoothed genuine face is scored as more forged than the same face
untouched, because the detectors respond to flattened skin with kept edges, which beautification produces and forgery leaves
behind. The failure comes from training: the class that receives smoothed views sets the sign of the error, and genuine-only
views open an evasion route. It cannot be removed at the threshold, because the smoothed scores of genuine and forged faces
coincide. A class-symmetric smoothing view with a consistency term on the forgery logit keeps the separation under smoothing
and removes the accusation, and we report what that costs along the penalty weight: untreated detection at large weights,
misses on smoothed forgeries at small ones, and reenactment at every weight. The sources, the rule and the paired reader are
released so that the next detector can be read the same way.

"""
cut("\\section{Limitations}", "\\bibliographystyle{IEEEtran}", limits)
p.write_text(s, encoding="utf-8"); print("pass D done; leftover refs:", s.count("tab:boundary"), s.count("tab:notation"), s.count("ref{tab:df40}"))
