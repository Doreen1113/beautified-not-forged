"""main_v10c.tex = the IJCB (conference, 8 body pages) cut of main_v10.tex. Only prose is shortened; every number, table, figure
and citation of main_v10.tex stays. The journal twin main_v10j.tex keeps the full text. Whitespace-flexible exact matching."""
import re
from pathlib import Path
D = Path(r"C:\My_Project\AIGC\docs\paper_v2")
s = (D / "main_v10.tex").read_text(encoding="utf-8")
R = []
def r(a, b): R.append((a, b))
r("\\externaldocument[S-]{supplement_v10}", "\\externaldocument[S-]{supplement_v10c}")
r("%  Beautified Is Not Forged -- paper v10", "%  main_v10c = conference (IJCB, 8 body pages) cut of main_v10 made by make_v10_conf.py; main_v10j = journal twin.\n%  Beautified Is Not Forged -- paper v10")
r("""The two directions appear on different sources because the operating point differs; Finding~5 shows that they are one shift seen from either side of the threshold. For the uploader of Sec.~\\ref{sec:intro} this is a 17--69\\% chance of accusation at the strongest smoothing level, and for a remote identity check a 3--22 point higher chance that a beautified swap passes; both axes for every detector are in Fig.~\\ref{fig:twoaxes}.""",
  """The two directions appear on different sources because the operating point differs; Finding~5 shows that they are one shift seen from either side of the threshold, and Fig.~\\ref{fig:twoaxes} gives both axes for every detector.""")
r("""so no fusion method is claimed. Two of the four predictions hold (the stable AUC and the recalibrated miss) and two do not (the fusion bars and the size of the operating-point shift).""",
  """so no fusion method is claimed; two of the four predictions hold.""")
r("""\\textbf{What is not a clean source.} Instagram AR filters rendered through OpenFilter~\\cite{openfilter2022} (FairBeauty, B-LFW) were scored but are excluded as evidence, for one reason: the filter cannot be separated from the capture pipeline. The AR engine re-renders the face through its own capture path, and there is no no-filter pass through that path. A model trained on such pairs still calls 94.8\\% of filtered images beautified when the face is greyed out,""",
  """\\textbf{What is not a clean source.} Instagram AR filters rendered through OpenFilter~\\cite{openfilter2022} (FairBeauty, B-LFW) were scored but are excluded as evidence, for one reason: the AR engine re-renders the face through its own capture path with no no-filter pass, so the filter cannot be separated from the pipeline. A model trained on such pairs still calls 94.8\\% of filtered images beautified when the face is greyed out,""")
r("""Operation naming: the four operation scores identify smoothing on the training family and little else (Sec.~\\ref{sec:companion}). Language-model explanations did not differ from template sentences in any measured respect and were removed; localisation of part-level forgeries and its restoration test are in the supplement.""",
  """Operation naming: the four operation scores identify smoothing on the training family and little else (Sec.~\\ref{sec:companion}). Language-model explanations were removed (supplement), as was part-level localisation.""")
# Related Work: keep the leading sentence, two paragraphs instead of four
r("""rules out for skin smoothing.

Retouching detection and""", """rules out for skin smoothing. Retouching detection and""")
r("""boundary line at all.

Identity-referenced detection""", """boundary line at all. Identity-referenced detection""")
# the seventeen-detector dot figure (Fig. 3 of the journal version) is dropped here: Tables I and II carry the same numbers
f0 = s.index("\\begin{figure*}[t]\n\\centering\n\\includegraphics[width=0.98\\textwidth]{fig_dirs_v9}")
f1 = s.index("\\end{figure*}", f0) + len("\\end{figure*}\n")
r(s[f0:f1], "")
r("the pattern is the rule, not the exception (Fig.~\\ref{fig:dirs}).}", "the pattern is the rule, not the exception (Tables~\\ref{tab:dirA} and~\\ref{tab:dirB}).}")
r("in 89--99\\% of pairs for fifteen of them (Fig.~\\ref{fig:dirs}).", "in 89--99\\% of pairs for fifteen of them (Table~\\ref{tab:dirA}).")
r("is the quantity of Fig.~\\ref{fig:dirs}.", "is the first column of Table~\\ref{tab:dirA}.")
# further prose cuts for the 8-page budget (journal twin keeps the full text)
r("""Bars are $P(\\text{fake})$, ticks are each detector's own threshold, set where it accuses 5\\% of the untouched genuine faces of the same source; (b) uses the video mean over 32 frames. Across seventeen published detectors the pattern is the rule, not the exception (Tables~\\ref{tab:dirA} and~\\ref{tab:dirB}).}""",
  """Bars: $P(\\text{fake})$; ticks: each detector's own threshold at 5\\% false alarms on untouched genuine faces of the same source; (b) uses video means over 32 frames. Across seventeen published detectors the pattern is the rule (Tables~\\ref{tab:dirA} and~\\ref{tab:dirB}).}""")
r("""GPUPixel's skin smoothing, a source no design decision touched, reproduces the accusation (14 of 15 face detectors above 15\\% at its strongest level, against 2.4--4.9\\% for the same pipeline without smoothing) but not the ranking of the detectors (Spearman 0.24 against the scripted bilateral form). It is a port of the shader, not the compiled library.""",
  """GPUPixel's skin smoothing, a source no design decision touched, reproduces the accusation (14 of 15 face detectors above 15\\% at its strongest level, 2.4--4.9\\% without smoothing) but not the detectors' ranking (Spearman 0.24); it is a port of the shader, not the compiled library.""")
r("""CORE~\\cite{core} ties representations across generic augmentations and still ranks a smoothed genuine face above its original in 97\\% of pairs; the alpha-blending hypothesis""", """CORE~\\cite{core} ties representations across generic augmentations and still accuses 54.8\\% of the Smoothing-90 renders (Table~\\ref{tab:dirA}); the alpha-blending hypothesis""")
r("""Sec.~\\ref{sec:intro}; Libourel et al.\\ close by recommending a dedicated filter-detection stage, which the companion model's beautified head is. Tariq""", """Sec.~\\ref{sec:intro}. Tariq""")
r("""Ours (bold): the three-way detector of Sec.~\\ref{sec:companion}, two seeds; it was trained on renders of two other services from the same RetouchingFFHQ release and on more data than the published detectors, so its rows are a reference, not a ranking.}""",
  """Ours (bold): the three-way detector of Sec.~\\ref{sec:companion}, two seeds, trained on renders of two other services of the same RetouchingFFHQ release and on more data than the published detectors; a reference, not a ranking.}""")
r("""Evaluations of benign processing should report the paired ranking before any AUC.""", "")
r("""Calibration on untreated data, the remedy proposed for smartphone photographs~\\cite{laionmobile2026}, does not apply here, because the problem is not where the threshold sits but that there is no threshold to find.""",
  """Calibration on untreated data~\\cite{laionmobile2026} does not apply here: there is no threshold to find.""")
r("""\\caption{Smoothing-invariant consistency (SIC) against the same model trained without it (forgery head only, same data, views, seeds and checkpoint rule). FA: smoothed genuine Celeb-DF-v2 frames called fake at the 5\\%-FPR rule (face-local 0.06 / 0.12, whole-crop bilateral 15); S-90: commercial Smoothing-90 renders accused; $\\Delta$miss: miss rise on face-local 0.12 smoothed forgeries; untreated video AUC on Celeb-DF-v2 and DFD; Celeb-DF-B AUC under the presets; DF40 reenactment video AUC (FF++ domain); bars passed of six pre-registered bars. The view-only control ($\\lambda=0$) draws the same smoothed copy for both classes without the penalty.}""",
  """\\caption{Smoothing-invariant consistency (SIC) against the same model without it (forgery head only, same data, views, seeds, checkpoint rule). FA: smoothed genuine Celeb-DF-v2 frames called fake at the 5\\%-FPR rule (face-local 0.06 / 0.12, bilateral 15); S-90: Smoothing-90 renders accused; $\\Delta$miss: miss rise on face-local 0.12 smoothed forgeries; untreated video AUC (Celeb-DF-v2, DFD); Celeb-DF-B AUC under the presets; DF40 reenactment video AUC; bars passed of six pre-registered. $\\lambda=0$: the same smoothed copy for both classes, no penalty.}""")
r("""\\caption{A smoothing-conditional threshold. Fixed: fake iff $s>t_0$ with $t_0$ at 5\\% FPR on untreated genuine frames. Conditional: $t_0+\\Delta(b)$ with $\\Delta$ learnt on FF++ validation genuine renders only, $b$ the smoothing-presence score of our three-way model. FA on face-local smoothed genuine frames (strength 0.12) and MISS on the same smoothing applied to forgeries, fixed $\\to$ conditional. AUC: both classes smoothed, same form. Recal.\\ MISS: miss rate when the threshold is re-set at 5\\% FPR on the smoothed genuine frames themselves (an oracle). Celeb-DF-v2 frames with landmarks.}""",
  """\\caption{A smoothing-conditional threshold. Fixed: fake iff $s>t_0$, $t_0$ at 5\\% FPR on untreated genuine frames; conditional: $t_0+\\Delta(b)$, $\\Delta$ learnt on FF++ validation genuine renders only, $b$ our model's smoothing-presence score. FA on face-local (0.12) smoothed genuine frames and MISS on the same smoothing on forgeries, fixed $\\to$ conditional; AUC with both classes smoothed; Recal.\\ MISS: threshold re-set at 5\\% FPR on the smoothed genuine frames (oracle). Celeb-DF-v2 frames with landmarks.}""")
r("""Libourel et al.~\\cite{libourel2024} reported the AUC drop for three of these detectors; the one-rule reading adds that the drop is almost entirely misses.""", "")
r("""Table~\\ref{S-tab:reproduce} sets the released checkpoints against their published Celeb-DF-v2 numbers: the eight DeepfakeBench CNNs land within 0.035 frame AUC of the published value, Forensics Adapter and GenD reproduce their video AUC, and Effort and DFD-HR fall 0.02--0.03 short and are used as released (Sec.~\\ref{sec:limits}). CADDM and LAA-Net reproduce their video AUC within 0.011 on their own crops (Sec.~\\ref{S-sec:baselines}); SBI, UnivFD and NPR have no comparable published number on this protocol.""",
  """Against their published Celeb-DF-v2 numbers (Table~\\ref{S-tab:reproduce}, Sec.~\\ref{S-sec:baselines}), the eight DeepfakeBench CNNs, Forensics Adapter, GenD, CADDM and LAA-Net reproduce theirs within 0.035 AUC; Effort and DFD-HR fall 0.02--0.03 short and are used as released (Sec.~\\ref{sec:limits}); SBI, UnivFD and NPR have no comparable published number.""")
r("""Counts, crops and preprocessing are in the supplement.""", "")
r("""Four strands of prior work touch this measurement: beautification evaluations, benign-edit benchmarks, shortcut learning and identity evidence. Libourel""", """Libourel""")
r("""\\textbf{Operation scores.} Its four operation scores are reliable only for smoothing:""", """Its four operation scores are reliable only for smoothing:""")
r("""(NPR only on the scripted forms, where its scores do not saturate)""", """(NPR on the scripted forms only)""")
r("""The manifests, the rule, the paired reader, the per-detector result files and the pre-registration log are released.""",
  """Manifests, rule, paired reader, result files and pre-registration log are released.""")
r("""The two directions appear on different sources because the operating point differs; Finding~5 shows that they are one shift seen from either side of the threshold, and Fig.~\\ref{fig:twoaxes} gives both axes for every detector.""",
  """Finding~5 shows that the two directions are one shift seen from either side of the threshold; Fig.~\\ref{fig:twoaxes} gives both axes for every detector.""")
r("""but not the detectors' ranking (Spearman 0.24); it is a port of the shader, not the compiled library.""",
  """but not the detectors' ranking (Spearman 0.24); it is a shader port, not the compiled library.""")
r("""\\emph{Calibration renders}: FF++ validation genuine frames under the same forms, used only to fit the threshold rule of Finding~5. \\emph{Untreated detection}:""",
  """\\emph{Untreated detection}:""")
def flex(a):
    return r"\s+".join(re.escape(t) for t in a.split())
for i, (a, b) in enumerate(R):
    m = list(re.finditer(flex(a), s))
    if len(m) != 1:
        raise SystemExit(f"edit {i}: {len(m)} matches: {a[:80]!r}")
    s = s[:m[0].start()] + b + s[m[0].end():]
(D / "main_v10c.tex").write_text(s, encoding="utf-8"); print("main_v10c.tex written,", len(R), "edits")
