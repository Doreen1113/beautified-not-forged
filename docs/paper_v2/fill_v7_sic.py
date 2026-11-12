"""Fill the SIC placeholders of main_v7.tex with the Addendum 46/47 readouts (2026-10-20). python fill_v7_sic.py"""
from pathlib import Path

p = Path(__file__).resolve().parent / "main_v7.tex"; s = p.read_text(encoding="utf-8")
B = "\\"


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:60]); s = s.replace(old, new)


# abstract
rep("SIC lowers the false alarm on skin-smoothed genuine faces from [[FA before]]\\% to\n[[FA after]]\\% while leaving untreated detection within the confidence interval of the same model trained without it\n([[AUC on Celeb-DF-v2]] on Celeb-DF-v2). We release the six sources, the scorer and the paired reader as a benchmark.",
    "At a penalty weight of 0.1, SIC lowers the false alarm on skin-smoothed genuine faces from 85\\% to 4\\% while untreated\nvideo AUC on Celeb-DF-v2 moves from 0.956 to 0.930. No setting removes the cue for free: raising the decision threshold with a\nsmoothing estimate clears the genuine faces and lets every smoothed forgery through, and the penalty weight trades untreated\ndetection against the miss on smoothed forgeries. We release the six sources, the scorer and the paired reader as a benchmark.")
# introduction, method paragraph
rep("The\nmodel keeps its three-way output and four operation scores; only the forgery logit is constrained. [[One sentence with the\nSIC headline from READOUT46: FA on skin-smoothed genuine faces, miss change, untreated AUC.]]",
    "The\nmodel keeps its three-way output and four operation scores; only the forgery logit is constrained. At a weight of 0.1 the\nfalse alarm on skin-smoothed genuine faces falls from 85\\% to 4\\% and untreated Celeb-DF-v2 video AUC from 0.956 to 0.930\n(two seeds). The family traces a three-way trade-off between that false alarm, the miss on smoothed forgeries and untreated\ndetection, and a threshold rule, which we also test, cannot reach a better point.")
rep("\\item SIC, a training rule that removes the cue [[at the stated cost]], evaluated on pre-registered bars with two seeds and a\n$\\lambda = 0$ control, together with the released benchmark.",
    "\\item SIC, a training rule that removes the cue at a measured cost, evaluated on pre-registered bars with two seeds, a\n$\\lambda=0$ control and a blur ablation; the finding that no threshold rule separates smoothed genuine from smoothed forged\nfaces for any of the detectors; and the released benchmark.")
# method section sentence
rep("the stop-gradient removes that pull. [[One sentence on what SIC-sg reaches: FA at the face-local forms,\nmiss change, untreated CDFv2 and DFD against the model without the rule, DF40 reenactment.]]",
    "the stop-gradient removes part of that pull. With it and $\\lambda=0.1$, false alarms at the face-local forms are 4--7\\% (two\nseeds), the miss rise on strongly smoothed forgeries $+16$ to $+18$ points, untreated Celeb-DF-v2 video AUC 0.930 against 0.956\nand DFD 0.974--0.980 against 0.987, Celeb-DF-B above the model without the rule, and DF40 reenactment 0.07 below it\n(Table~\\ref{tab:sic}, Fig.~\\ref{fig:siccurve}).")
# table caption
rep("(FF++ identities); bars passed of the six pre-registered bars. [[fill after the readouts; two seeds per arm]]}",
    "(FF++ identities); bars passed of the six pre-registered bars. Seed 1 and 2 where both were trained.}")
# results paragraph
old = s[s.index("[[Paragraph: what the symmetric penalty does"):]
old = old[:old.index("]]") + 2]
new = r"""\begin{figure}[t]
\centering
\includegraphics[width=\columnwidth]{fig_sic_curve}
\caption{The trade-off traced by the SIC family. Each point is one trained model: untreated Celeb-DF-v2 video AUC against the
share of skin-smoothed genuine faces accused (face-local 0.12, log scale); colour gives the rise of the miss rate on the same
smoothing applied to forgeries. The star is the model without the rule; crosses are Effort and Forensics Adapter. Every
penalty weight removes the accusation; smaller weights keep untreated detection and let more smoothed forgeries through;
the one-sided penalty keeps everything except the forgeries. The Gaussian view fails the accusation bar.}
\label{fig:siccurve}
\end{figure}
\textbf{Three ways not to remove the cue.} A fixed threshold accuses smoothed genuine faces (Sec.~\ref{sec:accuse}).
Raising the threshold with a smoothing estimate does not help either: with the full model's smoothing-presence output as
the covariate and the shift learnt on FF++ validation genuine renders only, the accusation of strongly smoothed genuine
faces falls to 0--1\% for Effort, Forensics Adapter, DFD-HR and our model, and 78--100\% of the smoothed forgeries now pass,
because the two score distributions coincide (AUC between smoothed genuine and smoothed forged faces 0.60--0.66 for the four
CLIP detectors; supplement). Changing the weights with a view on genuine faces only removes the accusation and opens the
evasion route (Sec.~\ref{sec:exposure}). What remains is a view on both classes with a constraint on the forgery logit.

\textbf{What the constraint buys and costs.} Table~\ref{tab:sic} and Fig.~\ref{fig:siccurve} give the family. The
symmetric view alone ($\lambda=0$) leaves detection untouched and the accusation in place (54 / 92\% at the two face-local
strengths), so the consistency term, not the view, removes the accusation; every $\lambda\ge0.03$ does so (3--7\%). The term
also sets the cost, and the cost has two faces. With the gradient through both sides at $\lambda=1$ the clean forgery score is
pulled toward its smoothed copy and untreated detection falls (Celeb-DF-v2 0.866, in-domain forgery recall 90.9 to 69.8\%);
the stop-gradient halves that loss (0.907) and smaller weights shrink it further (0.930 at 0.1, 0.946 at 0.03), but as
$\lambda$ falls the smoothed forgery's score falls with the genuine one and its miss rises ($+10$, $+16$, $+24$ points). The
one-sided penalty, which forbids a rise of the forgery logit under smoothing and allows a fall, is the limit of that
direction: untreated AUC 0.954, accusation 0.1\%, and 57 points more smoothed forgeries missed. DF40 reenactment is 0.06--0.09
below the model without the rule at every weight (its seed spread is 0.014), the one bar no member passes. A Gaussian blur
of the same spatial support in place of the skin-smoothing operator fails the accusation bar at the strong face-local form
(19.5\%) and opens the bilateral evasion ($+14$ to $+22$ points): the operator has to be the beautification signature.
Trained on FF++ alone, the rule still removes the accusation (5--7\%), so the effect does not depend on our added data.
Instagram AR renders stay accused (SIC 67.7\%, Effort 67.8\%; Sec.~\ref{sec:limits}). Under smoothing of both classes the SIC
models keep an AUC of 0.77--0.78 at the strong face-local form against 0.60--0.66 for the published CLIP detectors
(supplement): the separation that a threshold cannot recover is kept, at the price above."""
s = s.replace(old, new)
p.write_text(s, encoding="utf-8"); print("filled;", s.count("[["), "placeholders left")
