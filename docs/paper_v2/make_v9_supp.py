from pathlib import Path
import re
D = Path(r"C:\My_Project\AIGC\docs\paper_v2")
RU = Path(r"C:\My_Project\AIGC\results\research\retouch_unified_20260929")
s = (D / "supplement_v8.tex").read_text(encoding="utf-8")
R = []
def r(a, b): R.append((a, b))

r("% Supplement to \"Beautified Is Not Forged\" v8 (2026-10-22)",
  "% v9 (2026-10-28): supplement_v8.tex with CONSISTENCY_AUDIT_20261023 items S02, S04-S09 applied, Sec. supp_context corrected\n"
  "% (frames are Celeb-DF-v2 test frames, ring width, ring range), SCE seed 1 added, new sections for GPUPixel (Addendum 54),\n"
  "% training without Deepfakes/NeuralTextures (Addendum 49) and identity on Celeb-DF-B (Addendum 62, tables/tab_v9_cdfbid.tex).\n"
  "% Supplement to \"Beautified Is Not Forged\" v8 (2026-10-22)")
r("\\externaldocument[M-]{main_v8}", "\\externaldocument[M-]{main_v9}")

# S04
r("""Listing the full-data model trained with the forgery head only
(\\oursB{}) first in the detection tables, with the full model (\\oursF{}, three classes and operation scores) beside it, was
decided after both seeds of both models had been read; no model, checkpoint or number changed with that decision.""",
  """In the main paper the three-way model
(\\oursF{}) is the only `Ours' row of the detection tables and \\oursB{} appears as the same-data control; this ordering was
decided after both seeds of both models had been read; no model, checkpoint or number changed with that decision.""")
# S05
r("""\\oursB{} is above Effort on both sets and above every CLIP detector on DFD frames, and on""",
  """Read as an audit (our models were trained on more data), \\oursB{} is above Effort's reproduction on both sets and above
every CLIP detector on DFD frames, and on""")
# S06
r("(2,919 pairs measured)", "(2,919 of the 2,927 pairs measurable)")
r("The multi-operation-view model (clipe5M)",
  "The multi-operation arm (RU9, clipe5M; Addendum 56, whose pre-declared AR endpoint failed)")
# S09
r("\\caption{The cue is the smoothing signature rather than blur.",
  "\\caption{The cue is the smoothing signature rather than blur; Sec.~\\ref{sec:supp_context} shows that it is a face smoother\nthan its context, not the boundary line.")
# S08 + seed 1
r("""Table~\\ref{tab:sce} gives seed 20260930, the only seed read so far. Routing clears the accusation on
the face-local forms (51.2 and 79.9\\% to 2.1 and 1.3\\%), raises the miss on the same smoothed forgeries by 40.6 and 46.0
points, and B's both-classes-smoothed AUC is below A's on seven of the eight forms. On the commercial renders the routed
decision accuses 0.2\\% of Smoothing-90 renders (A: 6.5\\%) and 4.8\\% of the originals; 99.4\\% of the renders and 0.9\\% of the
originals are routed.""",
  """Table~\\ref{tab:sce} gives seed 20260930. Routing clears the accusation on
the face-local forms (51.2 and 79.9\\% to 2.1 and 1.3\\%), raises the miss on the same smoothed forgeries by 40.6 and 46.0
points, and B's both-classes-smoothed AUC is below A's on seven of the eight forms. On the commercial renders the routed
decision accuses 0.2\\% of Smoothing-90 renders (A: 6.5\\%) and 4.8\\% of the originals; 99.4\\% of the renders and 0.9\\% of the
originals are routed. Seed 20260929 (SCE\\_s1.md) repeats the pattern: face-local 51.6 and 84.5\\% to 0.9 and 1.3\\%, miss rise
41.7 and 44.4 points, B below A on seven of the eight forms (face-local 0.12 the exception on both seeds), Smoothing-90 renders
accused 0.1\\% (A: 9.1\\%).""")

# context section corrections
r("""the same
bilateral strength is applied to Celeb-DF-B genuine frames in four face-local forms whose only difference is the edge treatment
(hard edge, then feathered over 1, 5 and 15 px), to the whole crop, and to a 12-px ring at the face edge alone, with the face
interior untouched.""",
  """the same
bilateral strength as the face-local 0.12 form is applied to the Celeb-DF-v2 test frames of Sec.~\\ref{sec:smooth38} in four
face-local forms whose only difference is the edge treatment (hard edge, then feathered over 1, 5 and 15\\% of the crop width),
to the whole crop, and to a band at the face edge alone, one tenth of the jaw width wide, with the face interior untouched.""")
r("""The ring alone accuses 7--13\\% of the frames for
fifteen of the seventeen published detectors, against 92--100\\% for the face-local form (prediction ``ring reaches 70\\% of
face-local'' holds for 1 of 15 face detectors, bar 10 of 15).""",
  """The ring alone accuses a median of 12\\% of the frames
(7--51\\%) for the thirteen face detectors other than CADDM and LAA-Net, against 92--100\\% for the face-local form (prediction
``ring reaches 70\\% of face-local'' holds for 1 of 15 face detectors, bar 10 of 15); the four CLIP detectors and SBI are the
upper half of that range (22--51\\%).""")
r("""\\caption{Smoothed genuine Celeb-DF-B frames called forged at each detector's own 5\\% FPR threshold, with the same bilateral
strength applied to the face only, to the whole crop, and to a 12-px ring at the face edge. Rows sorted by the face-only
share. The ring alone accuses almost nothing except for CADDM and LAA-Net; the whole crop accuses less than the face alone for
most detectors and more for ours.}""",
  """\\caption{Smoothed genuine Celeb-DF-v2 test frames called forged at each detector's own 5\\% FPR threshold, with the same
bilateral strength applied to the face only, to the whole crop, and to a band at the face edge. Rows sorted by the face-only
share. The band alone accuses far less than the face for every detector except CADDM and LAA-Net; the whole crop accuses less
than the face alone for most detectors and more for ours (BDRY38.md).}""")

# S07
s_tmp = s
# new sections: GPUPixel + Addendum 49 after supp_context figure; Addendum 62 after idref section
r("""\\section{Identity as a reference channel}
\\label{sec:idref}""",
  r"""\section{A second beauty engine: GPUPixel}
\label{sec:gpx}
Pre-registered on 2026-10-21 (Addendum 54), the skin smoothing of the open-source GPUPixel beauty engine (BeautyFaceFilter,
commit ef552bf8), ported to numpy from its shaders with 8-bit intermediate buffers, is applied to the whole crop of both classes
of the Celeb-DF-v2 test frames of Sec.~\ref{sec:smooth38} at blur strengths 0.3, 0.6 and 0.9 (levels 3, 6 and 9 of the demo
slider); level 0 passes the frame through the same pipeline without smoothing and is the null form. No design
decision of this study touched this source. Three predictions were written: (1) at level 9 more than 15\% of genuine frames
are accused for at least 10 of 15 face detectors, which holds for 14 (SRM 12.5\% is the exception; level 0 gives 2.4--4.9\%);
(2) the AUC with both classes smoothed falls monotonically with the level for at least 12 of 15, which holds for 11 and fails;
(3) the ranking of the detectors by accusation agrees with the scripted bilateral form (Spearman at least 0.5), which gives
0.243 and fails. The accusation replicates on an untouched engine; the ordering of the detectors does not. Our forgery-head
arms accuse 17.1--24.6\% at level 9. The port is not the compiled library, so we do not claim byte equivalence (GPX38.md).

\section{Training without the texture-poor FF++ families}
\label{sec:noDFNT}
Deepfakes and NeuralTextures forgeries have less high-frequency energy inside the face than their source frames (ratio $-1.09$
and $-0.65$; FFPP\_BAND.md). Pre-registered on 2026-10-21 (Addendum 49), an FF++-only arm with the P0 recipe was trained on
Face2Face and FaceSwap forgeries alone. It accuses face-local smoothing at 95.5\% (strength 0.06) and 100\% (0.12), against
95.8 and 100\% for P0 on both seeds, with an untreated Celeb-DF-v2 AUC of 0.857 (P0: 0.883 and 0.892). The predicted fall of
at least 15 points did not occur, so the texture-poor families do not teach the cue and the paper attributes no origin to them.

\section{Identity as a reference channel}
\label{sec:idref}""")

r("""\\section{Second seeds of the variant and of the forgery-head-only model}""",
  r"""\section{Identity under real app presets (Celeb-DF-B)}
\label{sec:cdfbid}
Pre-registered on 2026-10-28 (Addendum 62) before any score was read. The probes are the 32 standardised frames per video of
the six Celeb-DF-B folders (43,363 frames; face detection fails on none of the genuine frames). The reference of each claimed
person is the normalised mean ArcFace (buffalo\_l) embedding of five frames from each of up to four Celeb-DF-v2 Celeb-real
videos of that person, excluding the 231 genuine videos of Celeb-DF-B; the identity score is one minus the cosine similarity
between the probe and that reference. Texture
scores are those of Table~\ref{M-tab:dirB}. Fusion is the mean of the two scores after each is mapped to its quantile among
the untreated genuine frames; the gate variant replaces the fused score by $\min(\text{fused}, 0.5)$ whenever identity alone
calls the frame genuine. All thresholds accuse 5\% of the untreated genuine frames unless stated, and beautification-only
changes subtract the change under re-encoding, with 95\% video-cluster bootstrap intervals. Predictions: (1) the identity video
AUC falls by at most 0.03 under the presets (kill above 0.05): holds, no fall; (2) at a threshold re-set to 5\% FA on the
beautified genuine frames, identity misses at most 15\% and every texture detector at least 40\%: holds (0.6 against
46.2--72.2\%); (3) both rank-mean fusions keep the beautification-only FA rise within 10 points and the miss rise within 5:
fails, Effort plus identity raises the miss by 8.5 [5.4, 11.5]; (4) identity's beautification-only FA rise is at least 10
points: fails narrowly, 8.5 [6.4, 10.6]. The gate variant passes (3) for every pair because its misses equal identity's
(CDFB\_ID.md).
\begin{table}[H]
\centering
\caption{Identity and texture detectors on Celeb-DF-B (Addendum 62). vAUC: video AUC untreated / beautified / re-encoded.
$\Delta$FA, $\Delta$MISS: beautification-only change at the untreated 5\%-FPR threshold (points, 95\% video-bootstrap). Last
column: miss on beautified forgeries at the threshold that accuses 5\% of the beautified genuine frames.}
\label{tab:cdfbid}
\scriptsize
\begin{adjustbox}{max width=\linewidth}\input{tables/tab_v9_cdfbid.tex}\end{adjustbox}
\end{table}

\section{Second seeds of the variant and of the forgery-head-only model}""")

for a, b in R:
    n = s.count(a)
    if n != 1:
        raise SystemExit(f"count {n}: {a[:90]!r}")
    s = s.replace(a, b)
s = s.replace("to \\textsc{filter}", "to the beautified class").replace("\\textsc{filter}", "the beautified class")
(D / "supplement_v9.tex").write_text(s, encoding="utf-8")

# table from CDFB_ID.md
NAMES = {"identity": "Identity (ArcFace + reference)", "effort": "Effort", "fadapter": "Forensics Adapter", "gend": "GenD",
         "dfdhr": "DFD-HR", "sbi": "SBI", "caddm": "CADDM", "xception": "Xception", "ours": "\\ours{}, seed 1",
         "ours_s2": "\\ours{}, seed 2", "fusion_ours+identity": "Fusion, \\ours{} + identity",
         "fusion_effort+identity": "Fusion, Effort + identity", "fusion_fadapter+identity": "Fusion, Forensics Adapter + identity",
         "fusion_gend+identity": "Fusion, GenD + identity", "gate_ours+identity": "Gate, \\ours{} + identity",
         "gate_effort+identity": "Gate, Effort + identity"}
rows = {}
for line in (RU / "CDFB_ID.md").read_text(encoding="utf-8").splitlines():
    c = [x.strip() for x in line.strip("|").split("|")]
    if len(c) == 7 and c[0] in NAMES:
        rows[c[0]] = c
def m(x):
    return x.replace("-", "$-$").replace("+", "+")
out = ["% generated by make_v9_supp.py from results/research/retouch_unified_20260929/CDFB_ID.md (Addendum 62)",
       "\\begin{tabular}{@{}l c c c c@{}}", "\\toprule",
       "Score & vAUC untr. / beaut. / re-enc. & $\\Delta$FA beauty only & $\\Delta$MISS beauty only & MISS at 5\\% FA on beautified \\\\",
       "\\midrule"]
for k in NAMES:
    c = rows[k]
    if k == "ours": out.append("\\midrule")
    if k == "fusion_ours+identity": out.append("\\midrule")
    out.append(f"{NAMES[k]} & {c[1]} & {m(c[3])} & {m(c[5])} & {c[6]} \\\\")
out += ["\\bottomrule", "\\end{tabular}"]
(D / "tables" / "tab_v9_cdfbid.tex").write_text("\n".join(out) + "\n", encoding="utf-8")
print("supplement_v9.tex and tables/tab_v9_cdfbid.tex written;", len(R), "edits;", len(rows), "table rows")
