"""Round-6 fixes (REVIEW_V10_R5_20261028.md, four MINORs), in place on main_v10.tex and tables/tab_v8_bars.tex."""
import re
from pathlib import Path
D = Path(r"C:\My_Project\AIGC\docs\paper_v2")
def flex(a): return r"\s+".join(re.escape(t) for t in a.split())
p = D / "main_v10.tex"; s = p.read_text(encoding="utf-8")
R = [
 ("""Four repairs, a smoothing-conditional threshold, a routed expert, a consistency loss and test-time context matching, each reduce to moving the operating point, because under smoothing the scores of genuine and forged faces coincide.""",
  """Four repairs, from a conditional threshold to a consistency loss, each reduce to moving the operating point, because under smoothing the scores of genuine and forged faces coincide."""),
 ("""We release the source manifests, the scorer, the paired reader, the per-detector result files and the dated pre-registration log.""",
  """Manifests, scorer, paired reader, result files and the pre-registration log are released."""),
 ("""Table~\\ref{S-tab:compare} sets this protocol against the prior evaluations of Sec.~\\ref{sec:intro} feature by feature.""",
  """Table~\\ref{S-tab:compare} compares this protocol with the prior evaluations of Sec.~\\ref{sec:intro} feature by feature."""),
 ("""A model trained on such pairs calls 94.8\\% of filtered images beautified with the face greyed out,""",
  """A model trained on such pairs still calls 94.8\\% of filtered images beautified when the face is greyed out,"""),
]
for i, (a, b) in enumerate(R):
    m = list(re.finditer(flex(a), s))
    if len(m) != 1: raise SystemExit(f"edit {i}: {len(m)} matches: {a[:70]!r}")
    s = s[:m[0].start()] + b + s[m[0].end():]
p.write_text(s, encoding="utf-8")
a0 = s.index("\\begin{abstract}"); a1 = s.index("\\end{abstract}")
words = len(re.sub(r"%.*", "", s[a0 + 16:a1]).split()); print("main_v10 edits 4; abstract words:", words)
b = D / "tables/tab_v8_bars.tex"; u = b.read_text(encoding="utf-8"); k = len(re.findall(r"\s*\(am\. [\d/]+\)", u))
u = re.sub(r"\s*\(am\. [\d/]+\)", "", u); b.write_text(u, encoding="utf-8"); print("tab_v8_bars '(am.' removed:", k)
