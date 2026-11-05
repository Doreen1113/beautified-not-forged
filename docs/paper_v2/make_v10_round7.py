"""Round-7 fixes (REVIEW_V10_R6_20261028.md, three MINORs), in place on main_v10.tex (abstract), plus the IJCB CORE sentence
in make_v10_conf.py."""
import re
from pathlib import Path
D = Path(r"C:\My_Project\AIGC\docs\paper_v2")
def flex(a): return r"\s+".join(re.escape(t) for t in a.split())
p = D / "main_v10.tex"; s = p.read_text(encoding="utf-8")
R = [
 ("""We score seventeen published detectors, from Xception to the current CLIP-based detectors, on pixel-aligned retouching pairs and on app-beautified deepfake videos with one decision rule. Fifteen of them score""",
  """We score seventeen published detectors on pixel-aligned retouching pairs and on app-beautified deepfake videos with one decision rule. Fifteen of the seventeen score"""),
 ("""Training arms with architecture, data and recipe fixed show that the class that receives smoothed views during training""",
  """Controlled training arms show that the class that receives smoothed views during training"""),
]
for i, (a, b) in enumerate(R):
    m = list(re.finditer(flex(a), s))
    if len(m) != 1: raise SystemExit(f"edit {i}: {len(m)} matches: {a[:70]!r}")
    s = s[:m[0].start()] + b + s[m[0].end():]
p.write_text(s, encoding="utf-8")
a0 = s.index("\\begin{abstract}"); a1 = s.index("\\end{abstract}")
print("abstract words (master):", len(re.sub(r"%.*", "", s[a0 + 16:a1]).split()))
c = D / "make_v10_conf.py"; t = c.read_text(encoding="utf-8")
a = 'and still accuses (Table~\\\\ref{tab:dirA}); the alpha-blending hypothesis'
assert t.count(a) == 1, "conf CORE anchor"
t = t.replace(a, 'and still accuses 54.8\\\\% of the Smoothing-90 renders (Table~\\\\ref{tab:dirA}); the alpha-blending hypothesis')
c.write_text(t, encoding="utf-8"); print("conf script CORE sentence patched")
