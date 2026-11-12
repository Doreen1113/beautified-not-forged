"""v7 compression pass B: both-errors subsection and dose-response subsection."""
from pathlib import Path

p = Path(__file__).resolve().parent / "main_v7.tex"; s = p.read_text(encoding="utf-8")


def cut(start, end, new):
    global s
    a = s.index(start); b = s.index(end, a); s = s[:a] + new + s[b:]


both = r"""\textbf{Commercial retouching.} Table~\ref{tab:retouch} reads the Smoothing-90 renders against their own originals. Fifteen
of the seventeen detectors score the render above its original in 89--99\% of pairs, and the median $P(\text{fake})$ moves
from 0.21 to 0.99 for SBI and from 0.23 to 0.92 for GenD: a heavily smoothed genuine face is scored like a forgery whatever the
threshold (sign test $p<10^{-10}$ for every detector but NPR, whose scores saturate; CADDM 60.9\%). At the threshold that
accuses 5\% of the originals thirteen detectors accuse 36--69\% of the renders; with a threshold fixed on FF++ validation they
accuse 15--93\%, and three of them already call 31--45\% of the untouched originals fake (Table~\ref{S-tab:deploy}).
Whitening, face slimming and eye enlarging at their strongest level stay at 3.7--8.1\% for thirteen of the sixteen detectors
other than NPR (Table~\ref{S-tab:v4perop}); they pass through the same service, encoder and resolution, so the retouching
result is a smoothing result. Our full-data models accuse 6.5--12.5\% of the renders, but none leaves the score unmoved:
\oursB{} still ranks the render above its original in 68--71\% of pairs, and \oursF{} moves it the other way (below its
original in 67.5\%). They were trained on renders of the two sister services, which the published detectors were not.

\textbf{Skin-only smoothing.} A bilateral filter inside the face hull, background untouched, is accused by all seventeen
detectors (Fig.~\ref{fig:accuse}, Table~\ref{S-tab:smooth38}): the four CLIP detectors call 88--99\% of genuine frames forged at
the milder strength and 99.9--100\% at the stronger one, the eleven face-forgery CNNs 64--100\% and 92--100\%, UnivFD 14 and
55\%. At matched visible strength skin-only smoothing is accused more often than whole-crop smoothing.

\textbf{Instagram AR filters.} All seventeen detectors accuse FairBeauty renders above the 5\% floor (10.7--85.9\%) and sixteen
accuse B-LFW renders (12.0--96.6\%); every published detector ranks the render above its own original in 69--99\% of pairs
(Table~\ref{S-tab:ar}). Re-compressing both sides keeps 0.64--1.05 of each accused share, so re-compression does not carry the
effect, although the AR capture path stays confounded with the beautification. Our models are not exempt (\oursB{} 79--82\%
on FairBeauty, more than Effort and Forensics Adapter): our training removes the accusation on the vendor family it saw, not on
AR filters.

\textbf{App presets.} On Celeb-DF-B every detector that detects the untreated forgeries loses frame AUC beyond what
re-encoding costs (Table~\ref{tab:twosided}): SBI 0.861 to 0.752, CADDM 0.850 to 0.762, LAA-Net 0.870 to 0.698, and
0.066--0.091 for the four CLIP detectors; at video level CADDM goes from 0.965 to 0.832, against 0.91 to 0.76 reported by
Libourel et al.~\cite{libourel2024}. Beyond re-encoding the presets raise the miss rate by 11--22 points (SBI, Effort,
Forensics Adapter, GenD, LAA-Net) and false alarms by 4--10 points (GenD, CADDM, DFD-HR); under the DFD filters Effort's miss
rate rises by 15.1 points and Forensics Adapter's by 8.0.

"""
cut("\\textbf{Commercial retouching.} Table~\\ref{tab:retouch}", "\\subsection{Dose response}", both)

dose = r"""\label{sec:mechanism}
On the 1,348 genuine Celeb-DF-v2 frames we varied the strength of three edits and read the forgery logit of the four released
CLIP detectors (Table~\ref{S-tab:dose}). Under face-local smoothing the logit rises in at least 97.9\% of frames at every level
for all four and the median shift grows with strength: the weakest level already moves it by 1.0--1.9 times the gap between
the detector's mean forged and mean genuine logit, the strongest by 1.9--3.0 gaps. Whole-crop bilateral smoothing gives the
same picture at smaller shifts. A radial vignette alone does not: three of the four move the other way. For the published
CLIP detectors smoothing is the operative edit, and a genuine face is pushed past the forged mean.

\textbf{The cue is the signature, not the blur.} If the detectors reacted to lost texture, forms that remove more
high-frequency energy would be accused more. They are not (Fig.~\ref{fig:bandenergy}): on 400 genuine frames the energy above
0.25 cycles per pixel lost inside the face hull ranges from 0.19 (face-local 0.06) to 0.94 (Gaussian blend, whole-crop
bilateral 21), and the false-alarm rate of the seventeen detectors across the seven forms does not follow it (pooled Spearman
$+0.06$). What it follows is the beautification signature: with the same kernel, confining the smoothing to the face raises the
accusation by 28 points (16 of 17 detectors, $p=5\times10^{-4}$); at equal energy loss an edge-preserving filter is accused 67
points more than a uniform blur (16 of 17); and only the band 0.02--0.12 cycles per pixel, the skin relief that a bilateral
filter flattens and a Gaussian blend leaves, correlates with the accusation ($\rho=+0.45$). The detectors respond to flattened
skin with kept edges inside the face, which a beautification filter produces and a forgery boundary or a generator leaves
behind, not to blur as such. This is why Gaussian blur or JPEG as a training view does not remove the accusation
(Sec.~\ref{sec:chain}) and why the operator of Sec.~\ref{sec:sic} is skin smoothing.

"""
cut("\\label{sec:mechanism}\nOn the 1,348 genuine Celeb-DF-v2 frames", "\\subsection{Which class receives beautified views}", dose)
p.write_text(s, encoding="utf-8"); print("pass B done")
