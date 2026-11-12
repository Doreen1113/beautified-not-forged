"""Round-4 fixes (REVIEW_V10_R3_20261028.md), 2026-10-28, in place on main_v10.tex, supplement_v10.tex, tables/tab_v8_fbops.tex,
then the supplement twins: supplement_v10c.tex (cross-references main_v10c) and supplement_v10j.tex (cross-references
main_v10j; its Tables S3/S4 become one-line stubs because the journal body carries them).
Main: CADDM / LAA-Net check pointed at the supplement section that holds it, 75-word sentence split; release sentences name the
result files and the pre-registration log; Costs paragraph split with an "Operation scores" lead; "Table VII and Fig. S3 in the
supplement" rephrased; "which" -> "that" in the abstract; "--" legend in the Table I caption.
Supplement: " ," residue of the pointer cleanup, "(clipe7)" renamed, "--" legend in the comparison-table caption."""
import re
from pathlib import Path
D = Path(r"C:\My_Project\AIGC\docs\paper_v2")
def flex(a): return r"\s+".join(re.escape(t) for t in a.split())
def apply(path, R):
    s = path.read_text(encoding="utf-8")
    for i, (a, b) in enumerate(R):
        m = list(re.finditer(flex(a), s))
        if len(m) != 1: raise SystemExit(f"{path.name} edit {i}: {len(m)} matches: {a[:70]!r}")
        s = s[:m[0].start()] + b + s[m[0].end():]
    path.write_text(s, encoding="utf-8"); print(path.name, len(R), "edits")

apply(D / "main_v10.tex", [
 ("""the eight DeepfakeBench CNNs land within 0.035 frame AUC of the published value, Forensics Adapter and GenD reproduce their video AUC, CADDM and LAA-Net reproduce theirs within 0.011 on their own crops, and Effort and DFD-HR fall 0.02--0.03 short and are used as released (Sec.~\\ref{sec:limits}); SBI, UnivFD and NPR have no comparable published number on this protocol.""",
  """the eight DeepfakeBench CNNs land within 0.035 frame AUC of the published value, Forensics Adapter and GenD reproduce their video AUC, and Effort and DFD-HR fall 0.02--0.03 short and are used as released (Sec.~\\ref{sec:limits}). CADDM and LAA-Net reproduce their video AUC within 0.011 on their own crops (Sec.~\\ref{S-sec:baselines}); SBI, UnivFD and NPR have no comparable published number on this protocol."""),
 ("""We release the source manifests, the scorer and the paired reader.""",
  """We release the source manifests, the scorer, the paired reader, the per-detector result files and the dated pre-registration log."""),
 ("""The manifests, the rule and the paired reader are released.""",
  """The manifests, the rule, the paired reader, the per-detector result files and the pre-registration log are released."""),
 ("""Its four operation scores are reliable only for smoothing:""", """

\\textbf{Operation scores.} Its four operation scores are reliable only for smoothing:"""),
 ("""Table~\\ref{tab:sic} and Fig.~\\ref{S-fig:siccurve} in the supplement give the family.""",
  """Table~\\ref{tab:sic} gives the family and Fig.~\\ref{S-fig:siccurve} in the supplement plots it."""),
 ("""show that the class which receives smoothed views during training""", """show that the class that receives smoothed views during training"""),
 ("""NPR scores everything at 1.0. Ours (bold):""", """NPR scores everything at 1.0; --: not scored. Ours (bold):"""),
])
sp = D / "supplement_v10.tex"; t = sp.read_text(encoding="utf-8")
n = len(re.findall(r" ,", t)); t = t.replace(" ,", ","); print("supplement ' ,' fixed:", n)
apply(sp, [
 ("""and a model trained with the AR pairs (clipe7) are listed for""", """and a model trained with the AR pairs are listed for"""),
 ("""Thr.: a threshold rule tested. Rel.: sources and scorer released.}""", """Thr.: a threshold rule tested. Rel.: sources and scorer released. --: not done or not applicable.}"""),
])
tb = D / "tables/tab_v8_fbops.tex"; u = tb.read_text(encoding="utf-8")
k = u.count("clipe7") + u.count("clipe5M"); u = re.sub(r"\(?clipe7\)?", "trained with AR pairs", u).replace(" (clipe5M)", "")
tb.write_text(u, encoding="utf-8"); print("tab_v8_fbops internal names removed:", k)

# ---- supplement twins
t = sp.read_text(encoding="utf-8")
assert t.count("\\externaldocument[M-]{main_v10}") == 1
(D / "supplement_v10c.tex").write_text(t.replace("\\externaldocument[M-]{main_v10}", "\\externaldocument[M-]{main_v10c}"), encoding="utf-8")
j = t.replace("\\externaldocument[M-]{main_v10}", "\\externaldocument[M-]{main_v10j}")
for lab, word in (("tab:reproduce", "reproduced numbers"), ("tab:compare", "comparison with prior evaluations")):
    t0 = j.rfind("\\begin{table}", 0, j.index("\\label{%s}" % lab)); t1 = j.index("\\end{table}", t0) + len("\\end{table}")
    j = j[:t0] + ("\\begin{table}[H]\\centering\\caption{The %s are Table~\\ref{M-%s} of the paper (journal version).}\\label{%s}\\end{table}" % (word, lab, lab)) + j[t1:]
(D / "supplement_v10j.tex").write_text(j, encoding="utf-8"); print("supplement_v10c.tex and supplement_v10j.tex written")
