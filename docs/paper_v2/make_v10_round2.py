"""Round-2 review fixes (REVIEW_V10_20261028.md), applied in place to main_v10.tex and supplement_v10.tex, 2026-10-28.
MAJOR 1: the reproduction sentence of Sec. II now says what Table S3 shows. MAJOR 2: lab-notebook pointers (Addendum numbers,
result-file names) in the supplement are replaced by the released-repository convention stated once at the top. MAJOR 3: bold
in Tables I-II follows their captions. MINORs: Finding 1 and NPR; "within three points"; Concas attribution; Sec. IV opening
restating Finding 6; tense in Sec. III-G; unused macros; EffNet-B4 abbreviation in the Fig. 5 caption.
Whitespace-flexible exact matching; each target must occur once. Idempotent only in the sense that a second run aborts."""
import re
from pathlib import Path
D = Path(r"C:\My_Project\AIGC\docs\paper_v2")

def flex(a):
    return r"\s+".join(re.escape(t) for t in a.split())

def apply(path, R):
    s = path.read_text(encoding="utf-8")
    for i, (a, b) in enumerate(R):
        m = list(re.finditer(flex(a), s))
        if len(m) != 1:
            raise SystemExit(f"{path.name} edit {i}: {len(m)} matches: {a[:80]!r}")
        s = s[:m[0].start()] + b + s[m[0].end():]
    path.write_text(s, encoding="utf-8"); print(path.name, len(R), "edits")

M = []
# MAJOR 1
M.append(("""all with released weights, each on its own crop; fifteen of the seventeen released checkpoints reproduce their published Celeb-DF-v2 numbers within the margins of Table~\\ref{S-tab:reproduce}, and Effort and DFD-HR fall short of theirs and are used as released (Sec.~\\ref{sec:limits}).""",
  """all with released weights, each on its own crop. Table~\\ref{S-tab:reproduce} sets the released checkpoints against their published Celeb-DF-v2 numbers: the eight DeepfakeBench CNNs land within 0.035 frame AUC of the published value, Forensics Adapter and GenD reproduce their video AUC, CADDM and LAA-Net reproduce theirs within 0.011 on their own crops, and Effort and DFD-HR fall 0.02--0.03 short and are used as released (Sec.~\\ref{sec:limits}); SBI, UnivFD and NPR have no comparable published number on this protocol."""))
# MAJOR 3
M.append(("""\\textbf{\\ours{}}, seed 1 & \\textbf{32.5} [30.5, 34.4] & \\textbf{8.6} [7.4, 9.7] & 4.8 & 3.7 & 3.6 \\\\
\\ours{}, seed 2 & 41.3 [39.3, 43.3] & 12.5 [11.1, 13.8] & -- & -- & -- \\\\""",
  """\\textbf{\\ours{}}, seed 1 & 32.5 [30.5, 34.4] & 8.6 [7.4, 9.7] & 4.8 & 3.7 & 3.6 \\\\
\\textbf{\\ours{}}, seed 2 & 41.3 [39.3, 43.3] & 12.5 [11.1, 13.8] & -- & -- & -- \\\\"""))
M.append(("""\\textbf{\\ours{}}, seed 1 & 0.938 & \\textbf{0.866} [0.841, 0.890] & 9.5 & +6.7 [4.0, 9.5] \\\\
\\ours{}, seed 2 & \\textbf{0.941} & 0.883 [0.861, 0.902] & 6.7 & +8.3 [5.6, 11.0] \\\\""",
  """\\ours{}, seed 1 & 0.938 & 0.866 [0.841, 0.890] & 9.5 & +6.7 [4.0, 9.5] \\\\
\\ours{}, seed 2 & \\textbf{0.941} & \\textbf{0.883} [0.861, 0.902] & 6.7 & +8.3 [5.6, 11.0] \\\\"""))
# Finding 1 and NPR
M.append(("""\\textbf{Finding 1.} \\emph{Every one of the seventeen published detectors we scored, across four families and seven years, scores a skin-smoothed genuine face as more forged than the same face untouched; smoothing the skin alone is enough, and the other beautification operations do not produce the shift.}""",
  """\\textbf{Finding 1.} \\emph{Every one of the seventeen published detectors we scored, across four families and seven years, scores a skin-smoothed genuine face as more forged than the same face untouched (NPR only on the scripted forms, where its scores do not saturate); smoothing the skin alone is enough, and the other beautification operations do not produce the shift.}"""))
# "within three points" and the comma
M.append(("""stay at 3.7--8.1\\%, within three points of the 5\\% floor, for thirteen of the sixteen detectors other than NPR""",
  """stay at 3.7--8.1\\%, close to the 5\\% floor, for thirteen of the sixteen detectors other than NPR,"""))
# Concas
M.append(("""which they attribute to the detector rather than to a cause.""",
  """which they attribute to the detector (``the underlying system'') without tracing it to training."""))
# Sec. IV opening: do not restate Finding 6
M.append(("""The findings say what a detector that handles beautification must do: see smoothing on both classes in training and read the forgery decision from a head that is not asked to be smoothing-invariant. A separate beautified attribute is optional: on the same data a forgery-head-only model is at least as good on every forgery number and better on reenactment, so the third class is reported as an attribute with its own error rates. Our companion model (Fig.~\\ref{fig:method}b) was trained on more data than the published detectors, so the comparisons below are an audit reference, not a ranking.""",
  """Our companion model (Fig.~\\ref{fig:method}b) is the detector that Findings~3 and~6 call for: smoothing on both classes in training, and the forgery decision read from a head that is not asked to be smoothing-invariant. Its beautified attribute is optional, since on the same data a forgery-head-only model is at least as good on every forgery number and better on reenactment, and the model was trained on more data than the published detectors, so the comparisons below are an audit reference, not a ranking."""))
# tense
M.append(("""Two of the four predictions held (the stable AUC and the recalibrated miss) and two did not (the fusion bars and the size of the operating-point shift).""",
  """Two of the four predictions hold (the stable AUC and the recalibrated miss) and two do not (the fusion bars and the size of the operating-point shift)."""))
# Fig. 5 caption abbreviation
M.append(("""bars are the 95\\% intervals, NPR is saturated at zero.""", """bars are the 95\\% intervals, NPR is saturated at zero, EffNet-B4 is EfficientNet-B4."""))
apply(D / "main_v10.tex", M)
# unused macros in the main file
p = D / "main_v10.tex"; s = p.read_text(encoding="utf-8")
for mac in ("\\newcommand{\\oursB}{\\textsc{Ours}, forgery head only}\n", "\\newcommand{\\oursF}{\\textsc{Ours}, full model}\n", "\\newcommand{\\cmark}{\\checkmark}\n"):
    name = mac.split("{")[1].rstrip("}")
    if s.count(name) == 1:
        s = s.replace(mac, ""); print("removed", name)
p.write_text(s, encoding="utf-8")

# ---- supplement: lab-notebook pointers -> released-repository convention
S = []
S.append(("""Section, table and figure numbers without the prefix S refer to the paper.""",
  """Section, table and figure numbers without the prefix S refer to the paper. Names in small capitals such as \\textsc{bdry38} are the result files of the released repository that hold the numbers of the section; pre-registration dates refer to its \\textsc{pre\\_declared} log."""))
sp = D / "supplement_v10.tex"; t = sp.read_text(encoding="utf-8")
for a, b in S:
    assert t.count(a) == 1, a[:40]; t = t.replace(a, b)
n0 = len(re.findall(r"Addendum \d+", t))
# "(Addendum 57)" / "(Addendum 46 and its amendments; READOUT46.md)" / ", Addendum 51" / "Addendum 62, whose ..." forms
t = re.sub(r"\s*\(Addendum \d+ and its amendments; ([A-Z0-9_\\]+)\.md\)", lambda m: " (\\textsc{%s})" % m.group(1).replace("\\_", "\\_").lower(), t)
t = re.sub(r", Addendum \d+\)", ")", t)
t = re.sub(r"\(Addendum \d+\)", "", t)
t = re.sub(r"Addendum \d+, whose pre-declared AR endpoint failed", "whose pre-declared AR endpoint failed", t)
t = re.sub(r"; Addendum \d+(?=[,;)])", "", t)
t = re.sub(r"\(RU9, clipe5M; ", "(", t)
t = re.sub(r"\(BCT, Addendum \d+\)", "", t)
t = re.sub(r"\bAddendum \d+\b", "the pre-registration", t)
# result-file names: FOO\_BAR.md -> \textsc{foo\_bar}
t = re.sub(r"([A-Z][A-Z0-9]*(?:\\_[A-Za-z0-9]+)*)\.md", lambda m: "\\textsc{%s}" % m.group(1).lower(), t)
t = t.replace("  ", " ")
sp.write_text(t, encoding="utf-8")
print("supplement: Addendum mentions", n0, "->", len(re.findall(r"Addendum \d+", t)), "; .md left:", len(re.findall(r"\.md\b", t)))
