"""v10 review fixes (2026-10-28), applied in place to main_v10.tex after make_v10_humanize.py and before make_v10_figs.py.
Source: REVIEW_V9_20261028.md (pre-submission-reviewer skill), items D1-1..8, 10..13, D2-1, D2-4, D3-1..7, D4-1, D4-3, D4-6,
D5-1. Matching is whitespace-flexible (any run of blanks / newlines in `old` matches any run in the file) because
make_v10_humanize.py re-wraps some lines; every `old` must match exactly once or the script aborts."""
import re
from pathlib import Path
D = Path(r"C:\My_Project\AIGC\docs\paper_v2")
p = D / "main_v10.tex"; s = p.read_text(encoding="utf-8")
R = []
def r(a, b): R.append((a, b))

# D1-1 reproduce contradiction (Sec. II)
r("""all with released weights, each on its own crop; released checkpoints reproduce their published Celeb-DF-v2 numbers within the margins listed in Table~\\ref{S-tab:reproduce}.""",
  """all with released weights, each on its own crop; fifteen of the seventeen released checkpoints reproduce their published Celeb-DF-v2 numbers within the margins of Table~\\ref{S-tab:reproduce}, and Effort and DFD-HR fall short of theirs and are used as released (Sec.~\\ref{sec:limits}).""")
# D1-2 swallowed sentence
r("""% tables/tab_v6b_reproduce.tex (former Table VI of v8) On DF40 face swaps""", """% tables/tab_v6b_reproduce.tex (former Table VI of v8)
On DF40 face swaps""")
# D1-3 + D3-4 Addendum pointer
r("""and the FairFace originals themselves are called genuine by only 18.2\\% of a multi-operation arm whose AR accusation did not fall (Addendum 56).""",
  """and a multi-operation arm whose AR accusation did not fall calls only 18.2\\% of the FairFace originals genuine (Sec.~\\ref{S-sec:ar}).""")
# D1-4 universals
r("""\\textbf{Finding 1.} \\emph{Every published face-forgery detector, whatever its family or year, scores""",
  """\\textbf{Finding 1.} \\emph{Every one of the seventeen published detectors we scored, across four families and seven years, scores""")
r("""The one channel beautification leaves intact is identity against a reference of the claimed person:""",
  """The one channel we tested that beautification leaves intact is identity against a reference of the claimed person:""")
r("""is the one channel that beautification leaves: under real app presets""", """is the one channel we tested that beautification leaves: under real app presets""")
# D1-5 data affinity and bold in Table I; Sec. II sentence
r("""NPR scores everything at 1.0. Ours: the three-way detector of Sec.~\\ref{sec:companion}, two seeds.}""",
  """NPR scores everything at 1.0. Ours (bold): the three-way detector of Sec.~\\ref{sec:companion}, two seeds; it was trained on renders of two other services from the same RetouchingFFHQ release and on more data than the published detectors, so its rows are a reference, not a ranking.}""")
r("""No model was trained on this service, but it was read during the study, so it is an analysis set rather than a blind test.""",
  """No model was trained on this service, but our companion model saw renders of the two other services of the same release (Sec.~\\ref{sec:companion}), and the service was read during the study, so it is an analysis set rather than a blind test.""")
# D1-6 Table II bold
r("""Bold: best per column among detectors that detect the untreated forgeries (NPR is at chance and not bolded).}""",
  """Bold: highest AUC per column (NPR, at chance, is not bolded).}""")
# D1-7 citations
r("""Identity evidence is prior art~\\cite{idreveal2021,ict2022,yin2026}, as is the stable-AUC, moving-threshold pattern under beauty filters~\\cite{mirabet2025}; the measurement under beautification is new.""",
  """Identity evidence is prior art~\\cite{identitydriven2020,idreveal2021,ict2022,yin2026}, including detectors personalised on reference images of a protected identity~\\cite{vipguard2025}, and the stable-AUC, moving-threshold pattern under beauty filters is known from face recognition~\\cite{mirabet2025}; those works build detectors, whereas the measurement of the channel under beautification is new.""")
r("""Identity-referenced detection~\\cite{idreveal2021,ict2022,yin2026} and face recognition under beauty filters~\\cite{mirabet2025} are the prior art for Finding~7;""",
  """Identity-referenced detection~\\cite{identitydriven2020,idreveal2021,ict2022,yin2026,vipguard2025} and face recognition under beauty filters~\\cite{mirabet2025} are the prior art for Finding~7;""")
# D1-8 (a) Related Work: leading sentence and paragraphs
r("""\\label{sec:related}
Libourel et al.~\\cite{libourel2024}, Saeed et al.~\\cite{saeed2025} and Concas et al.~\\cite{concas2025} are discussed in""",
  """\\label{sec:related}
Four strands of prior work touch this measurement: beautification evaluations, benign-edit benchmarks, shortcut learning and identity evidence. Libourel et al.~\\cite{libourel2024}, Saeed et al.~\\cite{saeed2025} and Concas et al.~\\cite{concas2025} are discussed in""")
r("""rules out for skin smoothing. Retouching detection and""", """rules out for skin smoothing.

Retouching detection and""")
r("""treat edits as corruptions of one class. Shortcut learning~\\cite{geirhos2020}""", """treat edits as corruptions of one class.

Shortcut learning~\\cite{geirhos2020}""")
r("""boundary line at all. Identity-referenced detection""", """boundary line at all.

Identity-referenced detection""")
# D1-8 (b) Sec. III-F paragraph splits
r("""it does not keep separation that the view alone would lose. Nor does a routed expert.""",
  """it does not keep separation that the view alone would lose.

Nor does a routed expert.""")
r("""% results/research/retouch_unified_20260929/CTX38.md (Addendum 61): prediction 1 10/15, prediction 2 0/15, KILLED
The loss is not confined to the shortcut arms:""",
  """% results/research/retouch_unified_20260929/CTX38.md (Addendum 61): prediction 1 10/15, prediction 2 0/15, KILLED

The loss is not confined to the shortcut arms:""")
# D1-10
r("""extending Ricker et al.~\\cite{ricker2026biasid} with the both-classes cell,""", """extending Ricker et al.~\\cite{ricker2026biasid} to all four cells,""")
# D1-11 JPEG view evidence
r("""It is why Gaussian blur or JPEG as a training view does not remove the accusation (Finding~6)""",
  """It is why Gaussian blur or JPEG as a training view does not remove the accusation (Finding~6; P0 itself trains with blur and JPEG, Sec.~\\ref{S-sec:chain})""")
# D1-12 Concas
r("""test images of two in-house CNNs and observe that the two detectors move in opposite directions, which they report but do not explain.""",
  """test images of two CNNs they trained (AlexNet, VGG19) and observe that the two move in opposite directions, which they attribute to the detector rather than to a cause.""")
# D1-13 running example + D4-1 fig:twoaxes reference, after Finding 2
r("""Finding~5 shows that they are one shift seen from either side of the threshold.""",
  """Finding~5 shows that they are one shift seen from either side of the threshold. For the uploader of Sec.~\\ref{sec:intro} this is a 17--69\\% chance of accusation at the strongest smoothing level, and for a remote identity check a 3--22 point higher chance that a beautified swap passes; both axes for every detector are in Fig.~\\ref{fig:twoaxes}.""")
# D2-1 topic sentence of the AR paragraph
r("""\\textbf{What is not a clean source.} Instagram AR filters rendered through OpenFilter~\\cite{openfilter2022} (FairBeauty, B-LFW) were scored but are not used as evidence.""",
  """\\textbf{What is not a clean source.} Instagram AR filters rendered through OpenFilter~\\cite{openfilter2022} (FairBeauty, B-LFW) were scored but are excluded as evidence, for one reason: the filter cannot be separated from the capture pipeline.""")
# D2-4 which predictions held
r("""so no fusion method is claimed.""", """so no fusion method is claimed. Two of the four predictions held (the stable AUC and the recalibrated miss) and two did not (the fusion bars and the size of the operating-point shift).""")
# D3-1
r("""Each study measures one direction, a handful of detectors, or no cause.""", """Each study measures one direction with a handful of detectors, and none tests a cause.""")
# D3-2
r("""Answering them needs both directions read on the same detector with the same rule, pairs read without a threshold where the original exists, re-encoding controlled, the cause tested by intervention on training, and uncertainty reported at the sampled unit, pairs or videos rather than frames.""",
  """Answering them needs four things. Both directions must be read on the same detector with the same rule; pairs must be read without a threshold where the original exists; re-encoding must be controlled and the cause tested by intervention on training; and uncertainty must be reported at the sampled unit, pairs or videos rather than frames.""")
# D3-3
r("""stay within 3.7--8.1\\% for thirteen of the sixteen detectors other than NPR""", """stay at 3.7--8.1\\%, within three points of the 5\\% floor, for thirteen of the sixteen detectors other than NPR""")
# D3-6
r("""loses most of its, but its operating point moves""", """loses most of its own, but its operating point moves""")
# D3-7 tense
r("""We scored the ArcFace distance between each Celeb-DF-B frame""", """We score the ArcFace distance between each Celeb-DF-B frame""")
r("""A rank-mean fusion with a texture detector met the pre-declared bars""", """A rank-mean fusion with a texture detector meets the pre-declared bars""")
# D4-1 fig:method reference in the Introduction
r("""and score seventeen published detectors and a family of our own controlled arms with one rule.""",
  """and score seventeen published detectors and a family of our own controlled arms with one rule (Fig.~\\ref{fig:method}).""")
# D4-3 caption colour
r("""a negative change (red) means the arm accuses every smoothed face, a positive one (amber)""", """a negative change (dark orange) means the arm accuses every smoothed face, a positive one (amber)""")
# D5-1 two-axis caption: finding first, v10 figure, no area encoding
r("""\\includegraphics[width=\\columnwidth]{fig_twoaxis_v8b}
\\caption{Both directions at once. Each point is one detector:""",
  """\\includegraphics[width=\\columnwidth]{fig_twoaxis_v10}
\\caption{No published detector is low on both axes; ours and CADDM sit in the lower-left corner. Each point is one detector:""")
r("""bars are the 95\\% intervals, marker area grows with untreated Celeb-DF-B AUC, NPR is saturated at zero.""",
  """bars are the 95\\% intervals, NPR is saturated at zero.""")
r("""% figs/fig_twoaxis_v8b.pdf (make_fig_twoaxis_v8b.py)""", """% figs/fig_twoaxis_v10.pdf (make_fig_twoaxis_v10.py; = v8b with one marker size and stronger label repulsion)""")

def flex(a):
    return r"\s+".join(re.escape(t) for t in a.split())
for i, (a, b) in enumerate(R):
    m = list(re.finditer(flex(a), s))
    if len(m) != 1:
        raise SystemExit(f"edit {i}: {len(m)} matches: {a[:90]!r}")
    s = s[:m[0].start()] + b + s[m[0].end():]
# D4-6 unused macros
for mac in ("\\newcommand{\\xmark}{--}\n", "\\newcommand{\\todo}[1]{\\textcolor{red}{[TODO: #1]}}\n"):
    name = mac.split("{")[1].rstrip("}")
    if s.count(name) == 1:
        s = s.replace(mac, "")
p.write_text(s, encoding="utf-8"); print("main_v10.tex review fixes applied,", len(R), "edits")
