from pathlib import Path
D = Path(r"C:\My_Project\AIGC\docs\paper_v2")
s = (D / "main_v8.tex").read_text(encoding="utf-8")
R = []
def r(a, b): R.append((a, b))

# header
r("%  Beautified Is Not Forged -- paper v8 (2026-10-22).",
  "%  Beautified Is Not Forged -- paper v9 (2026-10-28): main_v8.tex with CONSISTENCY_AUDIT_20261023 items M01-M25 applied,\n"
  "%  Addenda 48 (both seeds), 49, 54 (GPUPixel), 57 (face vs context), 61 (context matching) and 62 (identity on Celeb-DF-B)\n"
  "%  written in, the prevalence \\todo removed (no prevalence is claimed). Changes are listed in V9_CHANGES.md.\n"
  "%  Former header of v8 (2026-10-22).")
r("\\externaldocument[S-]{supplement_v8}", "\\externaldocument[S-]{supplement_v9}")

# Fig. 1 caption, M22
r("NPR is n/a because\nits scores saturate on this source.",
  "NPR is drawn as n/a because\nits scores saturate at 1.0 on this source (Table~\\ref{tab:dirA} lists its raw numbers).")

# Abstract
a0 = s.index("\\begin{abstract}"); a1 = s.index("\\end{abstract}")
r(s[a0:a1], r"""\begin{abstract}
Published face-forgery detectors read skin smoothing as forgery evidence, and the error runs in both directions: a genuine
face smoothed by a retouching service is accused, and a deepfake beautified by an app preset is let through. We score seventeen
published detectors, from Xception to the current CLIP-based detectors, on pixel-aligned retouching pairs and on
app-beautified deepfake videos with one decision rule. Fifteen of them score the smoothed genuine face above its own original
in 89--99\% of pairs,
% docs/capstone/MAIN_CLAIMS_20261022.md, Direction A table (main_claim_A.json)
and fourteen miss 3--22 points more of the beautified deepfakes than of the untreated ones once re-encoding is controlled for.
% results/research/celebdfb_v2_20260927/FAIR_cdfb.md, "rise from beautification alone" column, detectors with CI above 0
Training arms with architecture, data and recipe fixed show that the class which receives smoothed views during training
sets the sign of the error and that exposure to smoothing is necessary and sufficient for it; the cue is a face smoother than
its own context, not blur and not the boundary line. Four repairs, a smoothing-conditional threshold, a routed expert, a
consistency loss and test-time context matching, each reduce to moving the operating point, because under smoothing the
scores of genuine and forged faces coincide. The one channel beautification leaves intact is identity against a reference of
the claimed person: on app-beautified face swaps it misses 0.6\% of the forgeries at the false-alarm rate where texture
detectors miss 46--72\%,
% results/research/retouch_unified_20260929/CDFB_ID.md (Addendum 62), last column
but its threshold still has to know about beautification. We release the source manifests, the scorer and the paired reader.
""")

# Intro opening, M12 + prevalence
r("""A person takes a selfie, lets the camera app smooth the skin, and uploads it.""",
  """A person takes a selfie, lets a beauty app or a retouching service smooth the skin, and uploads it.""")
r("""changes neither who is shown nor what the person does, and skin smoothing, whitening, eye enlargement and face slimming are
default options in camera apps and retouching services\\todo{add a citable prevalence source for beautification before upload;
none in the project files}. Fig.~\\ref{fig:teaser} shows what happens today: every published detector we scored ranks the
smoothed selfie as more forged than the untouched one.""",
  """changes neither who is shown nor what the person does. Skin smoothing, whitening, eye enlarging and face slimming are offered
by camera apps, AR filters and retouching services~\\cite{openfilter2022,retouchingffhq,libourel2024}; we make no claim about
how often they are used. Fig.~\\ref{fig:teaser} shows what happens today: fifteen of the seventeen published detectors we
scored rank the smoothed photograph above the untouched one in 89--99\\% of pairs.""")

# M10
r("""We build such a measurement from six beautification sources, four of them never touched by a design decision, and score
seventeen published detectors and a family of our own controlled arms with one rule.""",
  """We build such a measurement from three beautification sources in the main text (commercial retouching pairs, app-beautified
deepfake videos and scripted smoothing; colour-filter and AR sources are in the supplement), replicate the accusation on an
open-source beauty engine, and score seventeen published detectors and a family of our own controlled arms with one rule.""")

# contributions
r("""sign of the error and that smoothing exposure is necessary and sufficient; a band-energy analysis shows that the cue is
face-local and edge-preserving rather than loss of texture.""",
  """sign of the error and that smoothing exposure is necessary and sufficient; a band-energy analysis and an edge-treatment
ablation show that the cue is a face smoother than its own context, neither texture loss nor the boundary line.""")
r("""\\item Two negative results that bound what a fix can do (Findings~5--6): no threshold rule separates smoothed genuine from
smoothed forged faces for any of the detectors, and a training rule that removes the accusation is a recalibration, since
every model, fixed or not, loses separability when both classes are smoothed.
\\item A companion three-way detector (Sec.~\\ref{sec:companion}) that is low on both axes and on par with the CLIP detectors
on untreated deepfakes, with its costs stated.
\\end{itemize}
Identity as a reference channel is examined as a seventh, discussion-level finding because it is prior art.""",
  """\\item Negative results that bound what a fix can do (Findings~5--6): no threshold rule separates smoothed genuine from
smoothed forged faces for any of the detectors, and four repairs (a conditional threshold, a routed expert, a consistency
loss, test-time context matching) each reduce to a recalibration, since every model loses separability when both classes
are smoothed.
\\item The channel that survives (Finding~7): identity against a reference of the claimed person, measured for the first time
under real app presets; its separation does not move but its operating point does, so a detector that uses it needs a
beautification-aware threshold. The channel itself is prior art and fusion with it is not claimed as a method.
\\item An audit reference (Sec.~\\ref{sec:companion}): our full-data three-way detector, trained on more data than the published
detectors, accuses 9--13\\% of the smoothed genuine faces and keeps the highest beautified AUC among the detectors scored,
while a forgery-head-only model on the same data does as well within seed spread.
\\end{itemize}""")

# M14
r("""and the FairFace originals themselves are called genuine by only 18.2\\% of our best model.""",
  """and the FairFace originals themselves are called genuine by only 18.2\\% of a multi-operation arm whose AR accusation did
not fall (Addendum 56).""")

# Finding 4 section, M07 + M08
f0 = s.index("\\subsection{The cue: face-local, edge-preserving flattening}")
f1 = s.index("\\subsection{A threshold cannot separate}")
old = s[f0:f1]
keep0 = old.index("If the detectors reacted to lost texture")
keep1 = old.index("Why would a detector trained on FF++ carry this cue?")
r(old, "\\subsection{The cue: a face smoother than its context}\n\\label{sec:signature}\n"
  "% fig_bandenergy_v8b in the supplement (Fig. S-fig:bandenergy); edge-treatment ablation in Sec. S-sec:supp_context\n\n"
  + old[keep0:keep1] +
  r"""Two further probes, both pre-registered, locate the cue (Sec.~\ref{S-sec:supp_context}). Keeping the bilateral strength
of the face-local form and changing only the edge treatment, smoothing a band at the face edge alone, with the interior
untouched, is accused at a median of 12\% (7--51\%) by the thirteen face detectors other than CADDM and LAA-Net, against
92--100\% for the full face-local form, and smoothing face and surroundings alike is accused much less (UCF 13.6\%, Effort
30.3\%, Forensics Adapter 59.3\%). CADDM (94\%) and LAA-Net (65\%), both trained on blending boundaries, are the detectors that
read the edge.
% results/research/retouch_unified_20260929/BDRY38.md (Addendum 57): ring column, fe01 column, whole column
Nor is the cue taught by the texture-poor FF++ families. Deepfakes and NeuralTextures forgeries have less fine texture inside
the face than their source frames (high-band ratio $-1.09$ and $-0.65$), but an FF++-only arm trained without them accuses
face-local smoothing at 95.5 and 100\% (P0: 95.8 and 100\%), and UnivFD, which never saw FF++, accuses skin-only smoothing
too; we claim no training-data origin beyond the exposure result of Finding~3.
% bandenergy_20261018/FFPP_BAND.md; FINDINGS.md 2026-10-23 Addendum 49 (clipe5fbp0F2: fl06 95.5, fl12 100, untreated AUC 0.857)

\textbf{Finding 4.} \emph{The shared cue is a face that is smoother than its own context: skin flattened with kept edges
inside the face while the surroundings keep their texture. It is not blur, not texture loss as such and not the boundary
line.} This is the face-versus-context inconsistency that face-swap detectors are built to find, which face-local
beautification reproduces by construction. It is why Gaussian blur or JPEG as a training view does not remove the
accusation (Finding~6) and why a training-time fix has to use the smoothing signature itself.

""")

# M21 + Addendum 61
r("""a second model trained only on
smoothed copies, selected by the smoothing score, clears the accusation (face-local 51 and 80\\% to 2 and 1\\%) and raises the
miss on smoothed forgeries by 41--46 points, and its both-classes-smoothed AUC is below the untreated detector's on seven of
the eight forms (one seed; the second is running; Table~\\ref{S-tab:sce}).
% results/research/retouch_unified_20260929/SCE_s2.md: fl06 51.2 -> 2.1, fl12 79.9 -> 1.3; miss rise 40.6 / 46.0; AUC A/B bil15 0.843/0.752""",
  """a second model trained only on
smoothed copies, selected by the smoothing score, clears the accusation (face-local 51--52 and 80--85\\% to 1--2\\%) and raises
the miss on smoothed forgeries by 41--46 points, and its both-classes-smoothed AUC is below the untreated detector's on seven
of the eight forms, on both seeds (Table~\\ref{S-tab:sce}).
% results/research/retouch_unified_20260929/SCE_s1.md and SCE_s2.md: fl06 51.6/51.2 -> 0.9/2.1, fl12 84.5/79.9 -> 1.3/1.3;
% miss rise 41.7/44.4 (s1), 40.6/46.0 (s2); B below A on 7 of 8 forms on both seeds (fl12 the exception)
Nor does a rule at test time: calling a face forged only if it also exceeds the threshold after its whole crop is smoothed,
which removes the face-versus-context contrast, clears the accusation for 10 of 15 face detectors, but at a matched false-alarm
rate on the smoothed genuine frames it misses smoothed forgeries within a few points of the recalibrated single score for all
fifteen (Sec.~\\ref{S-sec:supp_context}).
% results/research/retouch_unified_20260929/CTX38.md (Addendum 61): prediction 1 10/15, prediction 2 0/15, KILLED""")

r("""a smoothing-conditional recalibration, since the view-only model read with a conditional threshold separates smoothed
faces at least as well; with both classes smoothed every detector, published or ours, loses separability.}""",
  """a smoothing-conditional recalibration, since the view-only model read with a conditional threshold separates smoothed
faces at least as well; a routed expert and test-time context matching are recalibrations too, and with both classes
smoothed every detector, published or ours, loses separability.}""")

# Finding 7 rewrite
i0 = s.index("\\subsection{Identity as a reference channel}")
i1 = s.index("\\begin{figure}[t]\n\\centering\n\\includegraphics[width=\\columnwidth]{fig_twoaxis_v8b}")
r(s[i0:i1], r"""\subsection{Identity: the channel that survives}
\label{sec:identity}
Smoothing erases texture evidence but should not change who the person is. On the Celeb-DF-v2 probes of Finding~5, the
ArcFace distance to the claimed person's other videos separates genuine from forged with an AUC of 0.996 untreated and 0.984,
0.963 and 0.982 under bilateral 15, bilateral 21 and face-local 0.12, against 0.924 falling to 0.823, 0.778 and 0.751 for our
forgery head on the same frames (Table~\ref{S-tab:idref}).
% results/research/retouch_unified_20260929/ID_REF.md AUC table (identity, clipe5b rows)
ICT and ICT-Ref~\cite{ict2022}, run with their released weights, lose 0.08--0.12 of AUC under the three stronger forms and fail
the other way, letting smoothed forgeries through (Table~\ref{S-tab:ict}).
% ICT_PROBE.md: ICT-Ref 0.863 -> 0.781 / 0.755 / 0.836 / 0.783; FA 2.9-7.2; miss 47 -> 55-70

We then asked the question of Finding~2 with real app presets, pre-registering four predictions (Table~\ref{S-tab:cdfbid}). On
Celeb-DF-B the reference is up to four Celeb-DF-v2 genuine videos of the claimed person that are not among the benchmark's
genuine videos. The identity channel's video AUC is 1.000 untreated, beautified and re-encoded. At the 5\%-FPR threshold of
untreated frames its miss on beautified forgeries does not rise ($-0.3$ points), but its false alarm on beautified genuine
frames rises by 8.5 points [6.4, 10.6] beyond re-encoding. When every score is re-thresholded to accuse 5\% of the beautified
genuine frames, identity misses 0.6\% of the beautified forgeries, against 46--72\% for the texture detectors (ours 51.1 and
46.2\%, Effort 51.9\%, GenD 61.9\%, SBI 69.6\%, CADDM 72.1\%).
% CDFB_ID.md (Addendum 62): identity vAUC 1.000/1.000/1.000; dFA +8.5 [+6.4, +10.6]; dMISS -0.3; last column
Two predictions failed. The operating-point shift was predicted at 10 points or more and its interval reaches only 10.6. A
rank-mean fusion of identity with a texture detector was required to keep the beautification-only false-alarm rise within 10
points and the miss rise within 5 for both pairs scored: with our model it does (+7.7 and +2.9), with Effort it does not
(miss rise +8.5 [5.4, 11.5]); a gate that trusts identity whenever it says genuine passes for every pair but equals identity
alone. We therefore report no fusion method.
% CDFB_ID.md rows fusion_ours+identity, fusion_effort+identity, gate_*+identity

\textbf{Finding 7.} \emph{A recognition embedding compared with a reference of the claimed person is the one channel that
beautification leaves: under real app presets on face swaps its separation does not move, while every texture detector loses
most of its. Its operating point still moves, so a detector that uses it needs a beautification-aware threshold.} The
boundary is wide. The channel needs a reference video of the claimed person, without which it is useless (AUC 0.59); it is
blind by construction to reenactment and attribute edits, which keep the identity; and Celeb-DF swaps are easy for it, so
the 1.000 is an upper bound. Identity as detection evidence is prior art~\cite{idreveal2021,ict2022,yin2026}, and the
stable-AUC, moving-threshold pattern is known from face recognition under beauty filters~\cite{mirabet2025}. What is new is
the measurement under beautification and the conclusion that the remaining evidence is not in the texture.
% AUC 0.59 without a reference: FFPP_ARCFACE.md (Addendum 53)

""")

# Companion section, M18, M03, M17, M23
r("""The findings say what a detector that handles beautification must do: see smoothing on both classes in training, read the
forgery decision from a head that is not asked to be smoothing-invariant, and report beautification as a separate attribute
rather than as evidence either way. Our companion model does this (Fig.~\\ref{fig:method}b).""",
  """The findings say what a detector that handles beautification must do: see smoothing on both classes in training and read
the forgery decision from a head that is not asked to be smoothing-invariant. A separate beautified attribute is optional: on
the same data a forgery-head-only model is at least as good on every forgery number and better on reenactment, so the third
class is reported as an attribute with its own error rates. Our companion model (Fig.~\\ref{fig:method}b) was trained on
more data than the published detectors, so the comparisons below are an audit reference, not a ranking.""")
r("""It is therefore not the model with the smallest escape; it is the only model low on both axes, which Fig.~\\ref{fig:twoaxes}
shows.""",
  """It is therefore not the model with the smallest escape, and CADDM is lower on both raw axes (6.3\\% and $-2.9$ points) at a
beautified AUC of 0.762 (Fig.~\\ref{fig:twoaxes}). The controlled comparison is the same architecture with and without
beautified views (Table~\\ref{tab:exposure}): both-class views take the accusation from 54.2 to 11.7\\% and change the escape by
$-7.2$, $-4.0$ and $+2.0$ points over three seeds, and on the full data a forgery-head-only model is as good on both axes
within seed spread (9.1 and 6.5\\% accused, beautified AUC 0.896 and 0.904), so the gain comes from the training data, not
from the third class.
% tab_exposure.tex (P2 - P0 per seed); BCT.md clipe5b rows; FAIR_cdfb.md RU-clipe5b rows""")
r("""\\textbf{Costs, stated.} Three are real.""", """\\textbf{Costs, stated.} Four are real.""")
r("""a cost the retouching source pays for the low accusation. Its four operation scores""",
  """a cost the retouching source pays for the low accusation. Its beautified class is itself an escape route: on Celeb-DF-B it
sends 16.6 and 16.1\\% of the beautified deepfakes to beautified, against 3.6 and 3.9\\% of the same deepfakes untreated; these
count as misses in Table~\\ref{tab:dirB}.
% FINDINGS.md Addendum 54 last paragraph (three-way decision on Celeb-DF-B)
Its four operation scores""")
r("""on the
service's single-operation renders at the strongest level the presence head recovers""",
  """on the
service's single-operation renders the presence head recovers""")

# Limitations M19, M20
r("""The measurement covers one commercial retouching service, four app presets on one video dataset, and seven scripted
smoothing forms. The retouching source was read during the study and is an analysis set; a smoothing source that no design
decision has touched is needed before the headline numbers can be called a blind test.""",
  """The measurement covers one commercial retouching service, four app presets on one video dataset, seven scripted smoothing
forms and one open-source beauty engine. The retouching source was read during the study and is an analysis set. GPUPixel's
skin smoothing, a source no design decision touched, reproduces the accusation (14 of 15 face detectors above
15\\% at its strongest level, against 2.4--4.9\\% for the same pipeline without smoothing) but not the ranking of the detectors (Spearman
0.24 against the scripted bilateral form); it is a port of the shader, not the compiled library.
% results/research/retouch_unified_20260929/GPX38.md (Addendum 54)
""")
r("""Three claims of earlier drafts are withdrawn and one result is moved out.""",
  """Four claims of earlier drafts are withdrawn and one result is moved out. The FF++ texture origin of the cue: an arm trained
without Deepfakes and NeuralTextures accuses as much (Sec.~\\ref{sec:signature}).""")

# Related work M09
r("""holds that frame-based detectors read compositing artefacts, and our
band analysis adds a second low-level cue.""",
  """holds that frame-based detectors read compositing artefacts; our
edge-treatment ablation shows that face-local skin smoothing reproduces the same face-versus-context inconsistency without a
boundary line.""")

# Conclusion M04, M11
c0 = s.index("\\section{Conclusion}"); c1 = s.index("\\bibliographystyle")
r(s[c0:c1], r"""\section{Conclusion}
Seventeen published face-forgery detectors read skin smoothing as forgery evidence: one cue accuses the smoothed genuine
photograph and lets the app-beautified deepfake through. The cue is set by which class saw smoothing in training; it is a face
smoother than its own context, which face-local beautification produces and face-swap detectors are built to flag; and no
threshold, routing, consistency loss or test-time rule removes it, because the smoothed scores of the two classes coincide.
What beautification does not erase is who the person is: identity against a reference keeps its separation under real app
presets, at a threshold that has to know about beautification. The manifests, the rule and the paired reader are released.

""")

r("% FINDINGS.md Addendum 40: P3 63.8 [59.1, 67.8]",
  "% FINDINGS.md rounding note 2026-10-17: P3 63.756 [59.050, 67.784] -> 63.8 [59.0, 67.8]")

for a, b in R:
    n = s.count(a)
    if n != 1:
        raise SystemExit(f"count {n}: {a[:80]!r}")
    s = s.replace(a, b)

# ---- second pass: cut back to eight body pages ----
P = []
i0 = s.index("\\subsection{Identity: the channel that survives}")
i1 = s.index("\\begin{figure}[t]\n\\centering\n\\includegraphics[width=\\columnwidth]{fig_twoaxis_v8b}")
P.append((s[i0:i1], r"""\subsection{Identity: the channel that survives}
\label{sec:identity}
Smoothing erases texture evidence but not who the person is. We scored the ArcFace distance between each Celeb-DF-B frame and
a reference of the claimed person, made from up to four of that person's Celeb-DF-v2 genuine videos outside the benchmark, with
four predictions written before any frame was embedded (Table~\ref{S-tab:cdfbid}; scripted forms and ICT-Ref~\cite{ict2022} in
Tables~\ref{S-tab:idref} and~\ref{S-tab:ict}). Its video AUC is 1.000 untreated, beautified and re-encoded. Re-thresholded to
accuse 5\% of the beautified genuine frames, it misses 0.6\% of the beautified forgeries, against 46--72\% for the texture
detectors (ours 51.1 and 46.2\%, Effort 51.9\%, SBI 69.6\%, CADDM 72.1\%). Its operating point still moves: at the untreated
threshold its false alarm on beautified genuine frames rises by 8.5 points [6.4, 10.6] beyond re-encoding, short of the
predicted 10. A rank-mean fusion with a texture detector met the pre-declared bars with our model (false-alarm rise +7.7, miss
rise +2.9) but not with Effort (miss rise +8.5 [5.4, 11.5] against a bar of 5), so no fusion method is claimed.
% results/research/retouch_unified_20260929/CDFB_ID.md (Addendum 62): identity vAUC 1.000/1.000/1.000; dFA +8.5 [+6.4, +10.6];
% last column; fusion_ours+identity, fusion_effort+identity rows. Scripted forms: ID_REF.md; ICT-Ref: ICT_PROBE.md

\textbf{Finding 7.} \emph{A recognition embedding compared with a reference of the claimed person is the one channel that
beautification leaves: under real app presets on face swaps its separation does not move while every texture detector loses
most of its, but its operating point moves, so a detector that uses it needs a beautification-aware threshold.} The channel
needs a reference, without which it is near chance (AUC 0.59); it is blind to reenactment and attribute edits, which keep the
identity; and Celeb-DF swaps are easy for it, so the 1.000 is an upper bound. Identity evidence is prior
art~\cite{idreveal2021,ict2022,yin2026}, as is the stable-AUC, moving-threshold pattern under beauty filters~\cite{mirabet2025};
the measurement under beautification is new.
% AUC 0.59 without a reference: FFPP_ARCFACE.md (Addendum 53)

"""))
t0 = s.index("\\begin{table}[t]\n\\centering\n\\caption{Untreated detection of the companion model")
t1 = s.index("\\end{table}", t0) + len("\\end{table}\n")
P.append((s[t0:t1], ""))
b0 = s.index("\\textbf{Both axes.}"); b1 = s.index("The controlled comparison is the same architecture")
P.append((s[b0:b1], r"""\textbf{Both axes.} On the retouching pairs the model ranks the render above its original in 32.5 and 41.3\% of pairs on
its two seeds and accuses 8.6 and 12.5\% (Table~\ref{tab:dirA}); its native decision sends 98.8 and 99.2\% of the renders to
beautified. On Celeb-DF-B it keeps the highest AUC under the presets, 0.866 and 0.883, and its beautification-only miss rise
of 6.7 and 8.3 points is smaller than that of Forensics Adapter, SBI and GenD but larger than that of DFD-HR and CADDM
(Table~\ref{tab:dirB}). CADDM is lower on both raw axes (6.3\% and $-2.9$ points) at a beautified AUC of 0.762
(Fig.~\ref{fig:twoaxes}).
% MAIN_CLAIMS_20261022.md Direction A and B, ours s1 / s2 rows and paired-difference lines
"""))
P.append(("""\\textbf{Untreated detection.} On Celeb-DF-v2 and DFD the model is on par with all four CLIP detectors (Table~\\ref{tab:companion});
no paired interval excludes zero in either direction.""",
  """\\textbf{Untreated detection.} On Celeb-DF-v2 and DFD the model is on par with all four CLIP detectors (frame AUC 0.891 and
0.942, video 0.947; no paired interval excludes zero in either direction; Table~\\ref{S-tab:reproduce}).
% tables/tab_v6b_reproduce.tex (former Table VI of v8)"""))
P.append(("""A measurement that can answer these questions needs five properties. Both directions must be read on the same detector with
the same rule. Where the untouched original of a beautified face exists, the pair should be read without a threshold, because
a detector near saturation hides the shift behind its operating point. Re-encoding must be controlled, since every app
re-compresses. The cause must be established by intervention on training, with everything else fixed. Uncertainty must be
reported at the unit that was sampled, pairs or videos rather than frames.""",
  """Answering them needs both directions read on the same detector with the same rule, pairs read without a threshold where
the original exists, re-encoding controlled, the cause tested by intervention on training, and uncertainty reported at the
sampled unit, pairs or videos rather than frames."""))
P.append(("""\\item The channel that survives (Finding~7): identity against a reference of the claimed person, measured for the first time
under real app presets; its separation does not move but its operating point does, so a detector that uses it needs a
beautification-aware threshold. The channel itself is prior art and fusion with it is not claimed as a method.
\\item An audit reference (Sec.~\\ref{sec:companion}): our full-data three-way detector, trained on more data than the published
detectors, accuses 9--13\\% of the smoothed genuine faces and keeps the highest beautified AUC among the detectors scored,
while a forgery-head-only model on the same data does as well within seed spread.""",
  """\\item The channel that survives (Finding~7): identity against a reference of the claimed person keeps its separation under
real app presets but not its operating point; the channel is prior art and no fusion method is claimed.
\\item An audit reference (Sec.~\\ref{sec:companion}): a three-way detector trained on more data, low on both axes, and a
forgery-head-only control on the same data that does as well."""))
P.append(("""Two further probes, both pre-registered, locate the cue (Sec.~\\ref{S-sec:supp_context}). Keeping the bilateral strength
of the face-local form and changing only the edge treatment, smoothing a band at the face edge alone, with the interior
untouched, is accused at a median of 12\\% (7--51\\%) by the thirteen face detectors other than CADDM and LAA-Net, against
92--100\\% for the full face-local form, and smoothing face and surroundings alike is accused much less (UCF 13.6\\%, Effort
30.3\\%, Forensics Adapter 59.3\\%). CADDM (94\\%) and LAA-Net (65\\%), both trained on blending boundaries, are the detectors that
read the edge.""",
  """A pre-registered edge ablation locates the cue (Sec.~\\ref{S-sec:supp_context}). At the same strength, smoothing only a band
at the face edge is accused at a median of 12\\% (7--51\\%) by the thirteen face detectors other than CADDM (94\\%) and LAA-Net
(65\\%), which are trained on blending boundaries, against 92--100\\% for the whole face, and smoothing face and surroundings
alike is accused much less (UCF 13.6\\%, Effort 30.3\\%)."""))
P.append(("""Nor is the cue taught by the texture-poor FF++ families. Deepfakes and NeuralTextures forgeries have less fine texture inside
the face than their source frames (high-band ratio $-1.09$ and $-0.65$), but an FF++-only arm trained without them accuses
face-local smoothing at 95.5 and 100\\% (P0: 95.8 and 100\\%), and UnivFD, which never saw FF++, accuses skin-only smoothing
too; we claim no training-data origin beyond the exposure result of Finding~3.""",
  """Nor do the texture-poor FF++ families teach it: an FF++-only arm trained without Deepfakes and NeuralTextures accuses
face-local smoothing at 95.5 and 100\\% (P0: 95.8 and 100\\%; Sec.~\\ref{S-sec:noDFNT}), and UnivFD, which never saw FF++, accuses
it too."""))
P.append(("""Each training step builds three items from one genuine frame of FF++ c23~\\cite{ffpp} or FFHQ: the frame itself, a beautified
item (a landmark or skin operation at random strength, one of 14 colour filters~\\cite{pilgram}, a random colour grading, or a
render by two retouching services that are sister services of the test service, whole or decomposed into single-operation
components) and a forged item (a self-blend~\\cite{sbi}, an observed FF++ forgery or one of 61,510 part-level forgeries), the
forged item beautified with probability 0.5 so that both classes receive the views. FFHQ contributes 7,831 photographs
(7,015 for training, 816 for checkpoint selection) and their renders.""",
  """Each training step builds a genuine, a beautified and a forged item from one genuine FF++ c23~\\cite{ffpp} or FFHQ frame
(Fig.~\\ref{fig:method}b; sources in the supplement), the forged item beautified with probability 0.5 so that both classes
receive the views; the beautified renders come from two retouching services that are sister services of the test service."""))
P.append(("""Instagram AR filters: the renders cannot be separated from the OpenFilter
capture pipeline (Sec.~\\ref{sec:protocol}), our models accuse them as much as the published CLIP detectors (75--82\\% against
64--86\\%; Table~\\ref{S-tab:ar}),
% tables/tab_v6b_ar.tex FairBeauty accused: oursF 75.1, oursB 79.0 / 82.1; Effort 67.8, FA 63.9, GenD 75.6, DFD-HR 85.9
and training with multi-operation beautification on both classes does not lower the accusation (78 against 75\\%), so no
statement about AR filters is made.""",
  """Instagram AR filters: the renders cannot be separated from the OpenFilter
capture pipeline (Sec.~\\ref{sec:protocol}) and our models accuse them as much as the CLIP detectors (Table~\\ref{S-tab:ar}).
% tables/tab_v6b_ar.tex FairBeauty accused: oursF 75.1, oursB 79.0 / 82.1; Effort 67.8, FA 63.9, GenD 75.6, DFD-HR 85.9"""))
P.append(("""and on real-app filters that combine operations it recognises almost none of them (recall 0.003--0.24; Table~\\ref{S-tab:fbops}).""",
  """and on real-app filters almost none (recall 0.003--0.24; Table~\\ref{S-tab:fbops})."""))
P.append(("""At matched visible strength skin-only smoothing is accused more often than whole-crop smoothing. For the four CLIP detectors
the forgery logit rises in at least 97.9\\% of genuine frames at every strength, and the weakest face-local level already moves
it by 1.0--1.9 times the detector's gap between its mean forged and mean genuine logit, the strongest by 1.9--3.0 gaps; a
radial vignette alone moves three of the four the other way (Table~\\ref{S-tab:dose}).""",
  """For the four CLIP detectors the forgery logit rises in at least 97.9\\% of genuine frames at every strength, the weakest
face-local level by 1.0--1.9 times the gap between the mean forged and mean genuine logit (Table~\\ref{S-tab:dose})."""))
P.append(("""The two directions appear on different sources because the operating point differs: a
retouching render lands above the threshold set on sharp originals, while an app preset applied to a forgery that was already
scored near the threshold pushes it below. Both are the same shift read from two sides, which Finding~5 makes explicit.""",
  """The two directions appear on different sources because the operating point differs; both are the same shift read from two
sides, which Finding~5 makes explicit."""))
P.append(("""Tariq et al.~\\cite{moire2025} benchmark fifteen detectors against moir\\'e and name beautification as
future work; von Stryk and Keuper~\\cite{laionmobile2026} find that the false alarms of generated-image detectors on smartphone
photographs follow threshold calibration, which Finding~5 shows is not available for skin smoothing.""",
  """Tariq et al.~\\cite{moire2025} benchmark detectors against moir\\'e and name beautification as future work; von Stryk and
Keuper~\\cite{laionmobile2026} find that false alarms on smartphone photographs follow threshold calibration, which Finding~5
rules out for skin smoothing."""))
for a, b in P:
    n = s.count(a)
    if n != 1:
        raise SystemExit(f"pass2 count {n}: {a[:80]!r}")
    s = s.replace(a, b)
(D / "main_v9.tex").write_text(s, encoding="utf-8")
print("main_v9.tex written,", len(R), "edits")
