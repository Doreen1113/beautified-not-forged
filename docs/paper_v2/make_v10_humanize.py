"""main_v9.tex -> main_v10.tex: the 34 wording-only items of HUMANIZER_AUDIT_V9_20261028.md.

Every `old` is copied exactly from main_v9.tex (line breaks kept) and must occur exactly once;
the script aborts on the first pair that does not. No number, interval, citation key, \\ref, \\label
or % source comment is changed. main_v9.tex is not modified.

Rows that share a sentence are applied as one replacement: rows 3+4+23 (contribution 2),
rows 15+25 (Sec. III-B opening), rows 13+34 (line 569), rows 3+5+33 (conclusion sentence).
"""
from pathlib import Path

D = Path(r"C:\My_Project\AIGC\docs\paper_v2")
SRC = D / "main_v9.tex"
DST = D / "main_v10.tex"
s = SRC.read_text(encoding="utf-8")

R = []  # (row label, old, new)


def r(label, a, b):
    R.append((label, a, b))


# ---------------------------------------------------------------- header + supplement link
r("header",
  "%  Beautified Is Not Forged -- paper v9 (2026-10-28): main_v8.tex with CONSISTENCY_AUDIT_20261023 items M01-M25 applied,",
  "%  Beautified Is Not Forged -- paper v10 (2026-10-28): main_v9.tex with the 34 wording-only edits of\n"
  "%  HUMANIZER_AUDIT_V9_20261028.md applied by make_v10_humanize.py (repeated clauses varied, punch sentences folded in,\n"
  "%  the thirteen longest sentences split, two coined phrases and two \"therefore\" removed). No number, interval, citation,\n"
  "%  cross-reference or source comment changed; no claim strengthened or weakened. Supplement: supplement_v10.tex.\n"
  "%  Former header of v9 (2026-10-28): main_v8.tex with CONSISTENCY_AUDIT_20261023 items M01-M25 applied,")
r("externaldocument", r"\externaldocument[S-]{supplement_v9}", r"\externaldocument[S-]{supplement_v10}")

# ---------------------------------------------------------------- row 21 (abstract)
r("21",
  r"""sets the sign of the error and that exposure to smoothing is necessary and sufficient for it; the cue is a face smoother than
its own context, not blur and not the boundary line.""",
  r"""sets the sign of the error, and that exposure to smoothing is necessary and sufficient for it. The cue is a face smoother than
its own context, not blur and not the boundary line.""")

# ---------------------------------------------------------------- row 1 (intro)
r("1-intro",
  r"""Fig.~\ref{fig:teaser} shows what happens today: fifteen of the seventeen published detectors we
scored rank the smoothed photograph above the untouched one in 89--99\% of pairs.""",
  r"""Fig.~\ref{fig:teaser} shows what happens today: for fifteen of the seventeen published detectors we
scored, the retouched copy outranks the original in 89--99\% of pairs.""")

# ---------------------------------------------------------------- row 22
r("22",
  r"""We build such a measurement from three beautification sources in the main text (commercial retouching pairs, app-beautified
deepfake videos and scripted smoothing; colour-filter and AR sources are in the supplement), replicate the accusation on an
open-source beauty engine, and score seventeen published detectors and a family of our own controlled arms with one rule. Our contributions are:""",
  r"""We build such a measurement from three beautification sources in the main text: commercial retouching pairs, app-beautified
deepfake videos and scripted smoothing (colour-filter and AR sources are in the supplement). We replicate the accusation on an
open-source beauty engine and score seventeen published detectors and a family of our own controlled arms with one rule. Our contributions are:""")

# ---------------------------------------------------------------- rows 1 + 2 (contribution 1)
r("1+2-contrib1",
  r"""Findings~1--2): on pixel-aligned commercial retouching pairs fifteen detectors score the smoothed genuine face above its
own original in nearly every pair, and on app-beautified deepfake videos fourteen miss more forgeries once re-encoding is
removed; smoothing the skin alone is enough.""",
  r"""Findings~1--2): on pixel-aligned commercial retouching pairs fifteen detectors rank the retouched copy above its original
in nearly every pair, and on app-beautified deepfake videos fourteen miss more forgeries once re-encoding is removed; the
skin smoothing operation by itself produces the shift.""")

# ---------------------------------------------------------------- rows 3 + 4 + 23 (contribution 2)
r("3+4+23-contrib2",
  r"""\item The cause by intervention (Findings~3--4): a complete $2\times2$ training-exposure design on face forgery, extending
Ricker et al.~\cite{ricker2026biasid} with the both-classes cell, shows that the class receiving smoothed views sets the
sign of the error and that smoothing exposure is necessary and sufficient; a band-energy analysis and an edge-treatment
ablation show that the cue is a face smoother than its own context, neither texture loss nor the boundary line.""",
  r"""\item The cause by intervention (Findings~3--4). A complete $2\times2$ training-exposure design on face forgery, extending
Ricker et al.~\cite{ricker2026biasid} with the both-classes cell, shows that the class receiving smoothed views sets the
sign of the error, that removing smoothing from the views brings the error back and that smoothing alone sets it. A
band-energy analysis and an edge-treatment ablation then show that the cue is the contrast between a flattened face and its
untouched surroundings, neither texture loss nor the boundary line.""")

# ---------------------------------------------------------------- row 6 (contribution 3)
r("6-contrib3",
  r"""smoothed forged faces for any of the detectors, and four repairs (a conditional threshold, a routed expert, a consistency
loss, test-time context matching) each reduce to a recalibration, since every model loses separability when both classes
are smoothed.""",
  r"""smoothed forged faces for any of the detectors, and four repairs (a conditional threshold, a routed expert, a consistency
loss, test-time context matching) each turn out to move the operating point rather than restore separation, since every
model loses separability when both classes are smoothed.""")

# ---------------------------------------------------------------- row 8 (contribution 4)
r("8-contrib4",
  r"""real app presets but not its operating point; the channel is prior art and no fusion method is claimed.""",
  r"""real app presets but not its operating point; the channel is prior art and we claim no fusion with it.""")

# ---------------------------------------------------------------- row 10 (contribution 5)
r("10-contrib5",
  r"""\item An audit reference (Sec.~\ref{sec:companion}): a three-way detector trained on more data, low on both axes, and a
forgery-head-only control on the same data that does as well.""",
  r"""\item An audit reference (Sec.~\ref{sec:companion}): a three-way detector that sees smoothing on both classes, with a
forgery-head-only control on the same data that does as well; it is trained on more data than the published detectors and
is not ranked against them.""")

# ---------------------------------------------------------------- row 24
r("24",
  r"""is no no-filter pass through that path, so the filter cannot be separated from the pipeline: a model trained on such pairs
calls 94.8\% of filtered images beautified with the face greyed out,""",
  r"""is no no-filter pass through that path, so the filter cannot be separated from the pipeline. A model trained on such pairs
calls 94.8\% of filtered images beautified with the face greyed out,""")

# ---------------------------------------------------------------- row 18
r("18",
  r"""The operation is smoothing. Whitening, face slimming and eye enlarging at their strongest level stay within 3.7--8.1\% for
thirteen of the sixteen detectors other than NPR""",
  r"""Only smoothing produces the shift: whitening, face slimming and eye enlarging at their strongest level stay within 3.7--8.1\%
for thirteen of the sixteen detectors other than NPR""")

# ---------------------------------------------------------------- row 14
r("14",
  r"""training set. Future evaluations of benign processing should read the pair before the AUC.""",
  r"""training set. Evaluations of benign processing should report the paired ranking before any AUC.""")

# ---------------------------------------------------------------- rows 15 + 25 (Sec. III-B opening)
r("15+25",
  r"""Table~\ref{tab:dirB} reads the same detectors on deepfake videos beautified by a real app. Here the accusation is small:
beautified genuine frames are accused at 2--15\%, close to the 5\% floor for most detectors.
% FAIR_cdfb.md FA beautified genuine column (SBI 1.8 .. DFD-HR 14.6)
The escape is not. Once the rise under re-encoding is subtracted, fourteen of the seventeen detectors miss 3--22 points
more of the beautified forgeries, with the interval above zero;
% FAIR_cdfb.md last column: 14 detectors with CI > 0 (EfficientNet-B4 +3.4 .. SBI +21.8); UnivFD, NPR, CADDM not
the largest rises belong to SBI, SRM and Forensics Adapter, and every detector that detects the untreated forgeries loses
0.04--0.17 of frame AUC beyond re-encoding (LAA-Net 0.870 to 0.698, SBI 0.861 to 0.752).""",
  r"""Table~\ref{tab:dirB} reads the same detectors on deepfake videos beautified by a real app. On this source the accusation
is small, 2--15\% of beautified genuine frames against a 5\% floor for most detectors, and the escape is not.
% FAIR_cdfb.md FA beautified genuine column (SBI 1.8 .. DFD-HR 14.6)
Once the rise under re-encoding is subtracted, fourteen of the seventeen detectors miss 3--22 points
more of the beautified forgeries, with the interval above zero.
% FAIR_cdfb.md last column: 14 detectors with CI > 0 (EfficientNet-B4 +3.4 .. SBI +21.8); UnivFD, NPR, CADDM not
The largest rises belong to SBI, SRM and Forensics Adapter. Every detector that detects the untreated forgeries loses
0.04--0.17 of frame AUC beyond re-encoding (LAA-Net 0.870 to 0.698, SBI 0.861 to 0.752).""")

# ---------------------------------------------------------------- row 9 (Finding 2 tail)
r("9",
  r"""The two directions appear on different sources because the operating point differs; both are the same shift read from two
sides, which Finding~5 makes explicit.""",
  r"""The two directions appear on different sources because the operating point differs; Finding~5 shows that they are one
shift seen from either side of the threshold.""")

# ---------------------------------------------------------------- row 26
r("26",
  r"""Giving the views to genuine faces only (P1) removes the accusation and opens an evasion route: on Celeb-DF-B its
beautification-only miss rise exceeds P0's by 4.5--9.5 points in every one of three seeds (Holm-adjusted $p\le0.01$),
% supplement_v7.tex Sec. S-exposure: P1-P0 +4.5 / +7.5 / +9.5, adjusted p = 0.009
and on frames it has never seen it misses 96--100\% of bilaterally smoothed forgeries when smoothing is the only view
(a miss rise of 56--63 points on three seeds).""",
  r"""Giving the views to genuine faces only (P1) removes the accusation and opens an evasion route. On Celeb-DF-B its
beautification-only miss rise exceeds P0's by 4.5--9.5 points in every one of three seeds (Holm-adjusted $p\le0.01$).
% supplement_v7.tex Sec. S-exposure: P1-P0 +4.5 / +7.5 / +9.5, adjusted p = 0.009
On frames it has never seen it misses 96--100\% of bilaterally smoothed forgeries when smoothing is the only view
(a miss rise of 56--63 points on three seeds).""")

# ---------------------------------------------------------------- rows 11 + 19 (Finding 3 tail)
r("11+19",
  r"""learning~\cite{geirhos2020} under class-dependent augmentation~\cite{balestriero2022}, which Ricker et
al.~\cite{ricker2026biasid} observed for JPEG with two cells; here all four cells are measured on face forgery, three of
them with replication. The practical reading is a warning: a ``filter-robust genuine class'', the recipe a defender would
reach for first, is the P1 cell.""",
  r"""learning~\cite{geirhos2020} under class-dependent augmentation~\cite{balestriero2022}, which Ricker et
al.~\cite{ricker2026biasid} saw for JPEG in two of the four cells; here all four are measured on face forgery, three of
them with replication. In practice this is a warning: a ``filter-robust genuine class'', the recipe a defender would
reach for first, is the P1 cell.""")

# ---------------------------------------------------------------- row 27
r("27",
  r"""nearly every detector. Three contrasts show what the detectors do follow. With the same kernel, confining the smoothing to
the face raises the accusation by 28 points (16 of 17 detectors, $p=5\times10^{-4}$); at equal energy loss an
edge-preserving filter is accused 67 points more than a uniform blur (16 of 17); and only the band 0.02--0.12 cycles per
pixel, the skin relief that a bilateral filter flattens and a Gaussian blend leaves, correlates with the accusation
($\rho=+0.45$).""",
  r"""nearly every detector. Three contrasts show what the detectors do follow. With the same kernel, confining the smoothing to
the face raises the accusation by 28 points (16 of 17 detectors, $p=5\times10^{-4}$). At equal energy loss an
edge-preserving filter is accused 67 points more than a uniform blur (16 of 17). Only the band 0.02--0.12 cycles per
pixel, the skin relief that a bilateral filter flattens and a Gaussian blend leaves, correlates with the accusation
($\rho=+0.45$).""")

# ---------------------------------------------------------------- row 28
r("28",
  r"""(65\%), which are trained on blending boundaries, against 92--100\% for the whole face, and smoothing face and surroundings
alike is accused much less (UCF 13.6\%, Effort 30.3\%).""",
  r"""(65\%), which are trained on blending boundaries, against 92--100\% for the whole face. Smoothing face and surroundings
alike is accused much less (UCF 13.6\%, Effort 30.3\%).""")

# ---------------------------------------------------------------- row 20
r("20",
  r"""The penalty buys the operating point and leaves separability where the view put it. The control that settles this is the $\lambda=0$ model read with
the oracle smoothing-conditional threshold of Finding~5: with both classes smoothed it keeps an AUC of 0.832 (bilateral) and
0.764 (face-local) against 0.790 and 0.778 for SIC at $\lambda=1$ and 0.802 and 0.778 at $\lambda=0.1$, and its
recalibrated miss rate (57 and 77\%) is not higher than SIC's (64--73\% on two seeds).""",
  r"""The penalty buys the operating point and leaves separability where the view put it. The deciding control is the $\lambda=0$ model read with
the oracle smoothing-conditional threshold of Finding~5. With both classes smoothed it keeps an AUC of 0.832 (bilateral) and
0.764 (face-local), against 0.790 and 0.778 for SIC at $\lambda=1$ and 0.802 and 0.778 at $\lambda=0.1$. Its
recalibrated miss rate (57 and 77\%) is not higher than SIC's (64--73\% on two seeds).""")

# ---------------------------------------------------------------- row 6 (Sec. III-F; the one "therefore" kept, row 34)
r("6-sicF",
  r"""SIC therefore equals a symmetric view plus a recalibration that one threshold can carry across untreated and smoothed
inputs; it does not keep separation that the view alone would lose.""",
  r"""SIC therefore amounts to a symmetric view plus one threshold shift that carries across untreated and smoothed
inputs; it does not keep separation that the view alone would lose.""")

# ---------------------------------------------------------------- row 29
r("29",
  r"""Nor does a routed expert: a second model trained only on
smoothed copies, selected by the smoothing score, clears the accusation (face-local 51--52 and 80--85\% to 1--2\%) and raises
the miss on smoothed forgeries by 41--46 points, and its both-classes-smoothed AUC is below the untreated detector's on seven
of the eight forms, on both seeds (Table~\ref{S-tab:sce}).""",
  r"""Nor does a routed expert. A second model trained only on
smoothed copies, selected by the smoothing score, clears the accusation (face-local 51--52 and 80--85\% to 1--2\%) and raises
the miss on smoothed forgeries by 41--46 points; its both-classes-smoothed AUC is below the untreated detector's on seven
of the eight forms, on both seeds (Table~\ref{S-tab:sce}).""")

# ---------------------------------------------------------------- row 30
r("30",
  r"""Nor does a rule at test time: calling a face forged only if it also exceeds the threshold after its whole crop is smoothed,
which removes the face-versus-context contrast, clears the accusation for 10 of 15 face detectors, but at a matched false-alarm
rate on the smoothed genuine frames it misses smoothed forgeries within a few points of the recalibrated single score for all
fifteen (Sec.~\ref{S-sec:supp_context}).""",
  r"""Nor does a rule at test time. Calling a face forged only if it also exceeds the threshold after its whole crop is smoothed,
which removes the face-versus-context contrast, clears the accusation for 10 of 15 face detectors. At a matched false-alarm
rate on the smoothed genuine frames, however, it misses smoothed forgeries within a few points of the recalibrated single
score for all fifteen (Sec.~\ref{S-sec:supp_context}).""")

# ---------------------------------------------------------------- row 16
r("16",
  r"""The loss is general. With both classes smoothed, every one of the seventeen published detectors loses AUC, by 0.06--0.28 at""",
  r"""The loss is not confined to the shortcut arms: with both classes smoothed, every one of the seventeen published detectors
loses AUC, by 0.06--0.28 at""")

# ---------------------------------------------------------------- rows 13 + 34 (line 569)
r("13+34",
  r"""Part of the forgery evidence is therefore erased by smoothing itself, beyond the shortcut; how much of the published
detectors' loss is shortcut saturation and how much is erased evidence cannot be separated with these data, and we call the
$\lambda=0$ loss a measured loss, not a bound.""",
  r"""Part of the forgery evidence is erased by smoothing itself, beyond the shortcut; how much of the published detectors'
loss comes from the shortcut being pushed to its ceiling and how much from erased evidence cannot be separated with these
data, and we call the $\lambda=0$ loss a measured loss, not a bound.""")

# ---------------------------------------------------------------- row 34 (line 579)
r("34-579",
  r"""A fix for the accusation therefore has to be bought with misses on smoothed forgeries or with untreated detection, and a""",
  r"""A fix for the accusation has to be bought with misses on smoothed forgeries or with untreated detection, and a""")

# ---------------------------------------------------------------- row 31
r("31",
  r"""The controlled comparison is the same architecture with and without
beautified views (Table~\ref{tab:exposure}): both-class views take the accusation from 54.2 to 11.7\% and change the escape by
$-7.2$, $-4.0$ and $+2.0$ points over three seeds, and on the full data a forgery-head-only model is as good on both axes
within seed spread (9.1 and 6.5\% accused, beautified AUC 0.896 and 0.904), so the gain comes from the training data, not
from the third class.""",
  r"""The controlled comparison is the same architecture with and without
beautified views (Table~\ref{tab:exposure}). Both-class views take the accusation from 54.2 to 11.7\% and change the escape by
$-7.2$, $-4.0$ and $+2.0$ points over three seeds. On the full data a forgery-head-only model is as good on both axes
within seed spread (9.1 and 6.5\% accused, beautified AUC 0.896 and 0.904), so the gain comes from the training data, not
from the third class.""")

# ---------------------------------------------------------------- row 17
r("17",
  r"""\textbf{Costs, stated.} Four are real.""",
  r"""\textbf{Costs.} Four are measured.""")

# ---------------------------------------------------------------- row 32
r("32",
  r"""15\% at its strongest level, against 2.4--4.9\% for the same pipeline without smoothing) but not the ranking of the detectors (Spearman
0.24 against the scripted bilateral form); it is a port of the shader, not the compiled library.""",
  r"""15\% at its strongest level, against 2.4--4.9\% for the same pipeline without smoothing) but not the ranking of the detectors (Spearman
0.24 against the scripted bilateral form). It is a port of the shader, not the compiled library.""")

# ---------------------------------------------------------------- row 12 (related work)
r("12",
  r"""edge-treatment ablation shows that face-local skin smoothing reproduces the same face-versus-context inconsistency without a
boundary line.""",
  r"""edge-treatment ablation shows that face-local skin smoothing produces that inconsistency with no boundary line at all.""")

# ---------------------------------------------------------------- rows 3 + 5 + 33 (conclusion) and row 7
r("3+5+33-concl",
  r"""The cue is set by which class saw smoothing in training; it is a face
smoother than its own context, which face-local beautification produces and face-swap detectors are built to flag; and no
threshold, routing, consistency loss or test-time rule removes it, because the smoothed scores of the two classes coincide.""",
  r"""The cue is set by which class saw smoothing in training. It is the
contrast between a flattened face and its untouched surroundings, which face-local beautification produces and face-swap
detectors are built to flag. No threshold, routing, consistency loss or test-time rule removes it, because, once both
classes are smoothed, no score separates them.""")
r("7-concl",
  r"""identity against a reference keeps its separation under real app
presets, at a threshold that has to know about beautification.""",
  r"""identity against a reference keeps its separation under real app
presets, provided the threshold is set on beautified genuine faces.""")

# ---------------------------------------------------------------- apply
for i, (label, a, b) in enumerate(R):
    n = s.count(a)
    if n != 1:
        raise SystemExit(f"ABORT: pair {i} (row {label}) occurs {n} times, expected 1:\n{a[:120]!r}")
    s = s.replace(a, b)

DST.write_text(s, encoding="utf-8", newline="\n")
print(f"wrote {DST} ({len(R)} replacements applied)")
