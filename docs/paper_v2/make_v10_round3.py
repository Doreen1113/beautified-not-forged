"""Round-3 polish (REVIEW_V10 MINORs), in place on main_v10.tex: Finding 7 split into two sentences; the three paragraphs over
20 printed lines (Sources, SIC family, Both axes) split at their natural seams. Whitespace-flexible exact matching."""
import re
from pathlib import Path
D = Path(r"C:\My_Project\AIGC\docs\paper_v2"); p = D / "main_v10.tex"; s = p.read_text(encoding="utf-8")
R = [
 ("""while every texture detector loses most of its own, but its operating point moves, so a detector that uses it needs a beautification-aware threshold.}""",
  """while every texture detector loses most of its own. Its operating point does move, so a detector that uses it needs a beautification-aware threshold.}"""),
 ("""than a blind test. \\emph{App-beautified deepfake videos}:""", """than a blind test.

\\emph{App-beautified deepfake videos}:"""),
 ("""so what remains is the beautification alone. \\emph{Scripted smoothing}:""", """so what remains is the beautification alone.

\\emph{Scripted smoothing}:"""),
 ("""and the penalty arms 2--13\\%.""", """and the penalty arms 2--13\\%.
"""),
]
def flex(a): return r"\s+".join(re.escape(t) for t in a.split())
for i, (a, b) in enumerate(R):
    m = list(re.finditer(flex(a), s))
    if len(m) != 1: raise SystemExit(f"edit {i}: {len(m)} matches: {a[:70]!r}")
    s = s[:m[0].start()] + b + s[m[0].end():]
# the SIC paragraph: a blank line before "The cost has two faces" (the % comment lines stay attached to the first half)
s = re.sub(r"\n(The cost has two faces that trade against each other along)", r"\n\n\1", s, count=1)
s = re.sub(r"\n(The controlled comparison is the same architecture)", r"\n\n\1", s, count=1)
p.write_text(s, encoding="utf-8"); print("round-3 edits applied")
