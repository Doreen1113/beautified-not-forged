"""v7 compression pass C: method section and SIC subsection."""
from pathlib import Path

p = Path(__file__).resolve().parent / "main_v7.tex"; s = p.read_text(encoding="utf-8")


def cut(start, end, new):
    global s
    a = s.index(start); b = s.index(end, a + 1); s = s[:a] + new + s[b:]


method = r"""\textbf{Training data.} Every edited training image has a pixel-aligned original $x_0$, so the footprint of the edit is
exact, $M(x)=\mathrm{dilate}_\rho(\mathbf{1}[\|x-x_0\|_\infty>\tau])$ with $\tau=6$ on 8-bit intensities. On FF++
c23~\cite{ffpp} (official split) each step draws, from a genuine frame $x_0$, a genuine item, a beautified item (one of four
landmark and skin operations at a random strength, one of 14 colour filters~\cite{pilgram} or a random colour grading) and a
forged item (a self-blend of $x_0$~\cite{sbi}, an observed FF++ forgery or a part-level forgery), the forged item beautified
with probability 0.5; forged items without landmarks receive skin smoothing as a whole-crop filter rather than the face-local
operation, an asymmetry whose effect Sec.~\ref{sec:chain} measures. The FF++-only arms use nothing else. The full-data models
add 7,831 FFHQ photographs~\cite{ffhq} and their renders by Tencent and Megvii~\cite{retouchingffhq}, sister services of the
test service, each render decomposed by optical flow and a photometric residual into single-operation components (supplement),
and 61,510 part-level forgeries that transplant the eyes, nose or mouth of another identity or regenerate the part with
Stable Diffusion inpainting.

\textbf{Model} (Fig.~\ref{fig:arch}). A frozen CLIP ViT-L/14~\cite{clip} with rank-16 LoRA~\cite{lora} on every attention
projection (3.2\,M of 306\,M parameters trained). Two linear heads on the pooled feature give the forged logit $z_f$ and the
beautified logit $z_b$, with $P(\text{fake})=\sigma(z_f)$; an operation-presence head and a $1\times1$ convolution on the
spatial tokens (the $16\times16$ evidence map $\hat m$) are trained against the operation labels and $M$ with BCE and Dice,
and the classifier does not read $\hat m$. The forgery decision is read from $z_f$ alone; the beautified class and the
operation scores are attributes reported separately. The forgery-head-only model keeps $z_f$ and nothing else on the same
data; it is the first row of every detection table because it is at or above the full model on every untreated source on
both seeds, while the shared beautified head costs reenactment (Sec.~\ref{sec:detect}). Training: 224\,px, AdamW at
$10^{-4}$, 8 epochs, 16 genuine bases per batch; checkpoints are chosen on validation data only (supplement).

"""
cut("Every edited training image has a pixel-aligned original $x_0$, so the footprint of the edit is exact,", "\\subsection{Smoothing-invariant consistency}", method)

sic = r"""\subsection{Smoothing-invariant consistency}
\label{sec:sic}
The sign of the error follows the class that receives smoothed views (Sec.~\ref{sec:exposure}) and the cue is the
skin-smoothing signature itself (Fig.~\ref{fig:bandenergy}); the rule follows from both. For every training item $x$,
genuine, beautified or forged, a smoothed copy $x_s$ is drawn by one operator with one distribution of strengths, so that no
class can learn the form of the smoothing as a label, and the forged logit of the copy is asked not to move:
\begin{equation}
\mathcal{L}=\mathcal{L}_\text{BCE}\big(z_f(x),y\big)+\mathcal{L}_\text{map}+\lambda\,\big(\operatorname{sg}[z_f(x)]-z_f(x_s)\big)^2,
\label{eq:sic}
\end{equation}
where $\operatorname{sg}$ stops the gradient: the clean logit is the target, only the smoothed view is pulled, and the clean
path is trained by the classification loss alone. The map target of $x_s$ is the footprint of $x$. The operator is face-local
bilateral smoothing inside the landmark hull at a random strength, or whole-crop bilateral smoothing where no landmarks are
carried; the median filter, the Gaussian blend, the commercial renders and the AR renders are never used in training. Generic
consistency does not reach this: CORE~\cite{core} ties representations across flips, rotations, Gaussian blur and JPEG
re-encoding and still scores a smoothed genuine face above its original in 97\% of pairs (Fig.~\ref{fig:teaser}). The bars for
the rule were written before training (supplement): false alarms at most 15\% on face-local and whole-crop smoothing and on
the commercial renders; a miss rise on smoothed forgeries at most 5 points above the arm without views; untreated video AUC on
Celeb-DF-v2 and DFD, Celeb-DF-B AUC and DF40 reenactment AUC within stated bands of the model without the rule; a $\lambda=0$
control; two seeds. Sec.~\ref{sec:sicres} reports what the rule reaches and what it costs.

"""
cut("\\subsection{Smoothing-invariant consistency}", "% ----------------------------------------------------------------------------\n\\section{Results}", sic)
p.write_text(s, encoding="utf-8"); print("pass C done")
