"""Round-5 fixes (REVIEW_V10_R4_20261028.md, all MINOR), 2026-10-28. Supplement: stray spaces before commas / full stops left by
the pointer cleanup; the two supplement twins are regenerated here (replaces the twin step of make_v10_round4.py) with
grammatical stubs and, in the journal twin, in-text references to the moved tables pointing at the paper. Tables S24 / S25:
internal checkpoint keys replaced by their descriptions (post-processing of tables/tab_v8_bars.tex and tab_sic_full.tex)."""
import re
from pathlib import Path
D = Path(r"C:\My_Project\AIGC\docs\paper_v2")
sp = D / "supplement_v10.tex"; t = sp.read_text(encoding="utf-8")
n1 = len(re.findall(r"[ \t\n]+,", t)); t = re.sub(r"[ \t\n]+,", ",", t)
n2 = t.count("Celeb-DF-B ."); t = t.replace("Celeb-DF-B .", "Celeb-DF-B.")
t = t.replace("% Cross-references to the paper (\"M-\" labels) from main_v8.aux.", "% Cross-references to the paper (\"M-\" labels) from the paired main file's .aux (see \\externaldocument).")
sp.write_text(t, encoding="utf-8"); print("supplement: spaces before commas", n1, "; 'Celeb-DF-B .'", n2)

# twins
assert t.count("\\externaldocument[M-]{main_v10}") == 1
(D / "supplement_v10c.tex").write_text(t.replace("\\externaldocument[M-]{main_v10}", "\\externaldocument[M-]{main_v10c}"), encoding="utf-8")
j = t.replace("\\externaldocument[M-]{main_v10}", "\\externaldocument[M-]{main_v10j}")
for lab, word in (("tab:reproduce", "The reproduced numbers are"), ("tab:compare", "The comparison with prior evaluations is")):
    t0 = j.rfind("\\begin{table}", 0, j.index("\\label{%s}" % lab)); t1 = j.index("\\end{table}", t0) + len("\\end{table}")
    j = j[:t0] + ("\\begin{table}[H]\\centering\\caption{%s Table~\\ref{M-%s} of the paper.}\\label{%s}\\end{table}" % (word, lab, lab)) + j[t1:]
    # every other reference to the moved table points at the paper
    j = re.sub(r"\\ref\{%s\}" % re.escape(lab), "\\\\ref{M-%s}" % lab, j)
    # ... except the stub's own caption, which already says M-; the label itself is untouched
    j = j.replace("\\ref{M-M-%s}" % lab, "\\ref{M-%s}" % lab)
(D / "supplement_v10j.tex").write_text(j, encoding="utf-8"); print("twins written; journal refs to moved tables:", len(re.findall(r"ref\{M-tab:(reproduce|compare)\}", j)))

# tables: internal keys -> descriptions
b = D / "tables/tab_v8_bars.tex"; u = b.read_text(encoding="utf-8")
u = u.replace("Arm (READOUT46 key)", "Arm")
u2 = []
for line in u.splitlines(True):
    m = re.match(r"^(clipe\S+) \((.*)\) & ", line)
    if m:
        desc = re.sub(r"\s*\(am\. \d+\)", "", m.group(2))
        line = desc + " & " + line[m.end():]
    u2.append(line)
u = "".join(u2); b.write_text(u, encoding="utf-8"); print("tab_v8_bars keys left:", len(re.findall(r"^clipe", u, re.M)))
s = D / "tables/tab_sic_full.tex"; v = s.read_text(encoding="utf-8")
v = re.sub(r"^clipe5bzxs & ", "smoothing expert (trained on smoothed copies only; routed model B) & ", v, flags=re.M)
v = re.sub(r"^clipe5fbp0F2 & ", "FF++-only P0 without Deepfakes and NeuralTextures & ", v, flags=re.M)
s.write_text(v, encoding="utf-8"); print("tab_sic_full keys left:", len(re.findall(r"^clipe", v, re.M)))
