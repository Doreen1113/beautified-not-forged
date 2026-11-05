"""main_v10j.tex = main_v10.tex under the IEEEtran journal class with Index Terms (TIFS form). Text otherwise identical."""
from pathlib import Path
D = Path(r"C:\My_Project\AIGC\docs\paper_v2")
s = (D / "main_v10.tex").read_text(encoding="utf-8")
a = "\\documentclass[conference]{IEEEtran}"
assert s.count(a) == 1
s = s.replace(a, "\\documentclass[journal]{IEEEtran}  % journal variant (TIFS); main_v10.tex is the conference-format twin")
assert s.count("\\externaldocument[S-]{supplement_v10}") == 1
s = s.replace("\\externaldocument[S-]{supplement_v10}", "\\externaldocument[S-]{supplement_v10j}")
old = "\\end{abstract}\n"
new = ("\\end{abstract}\n\\begin{IEEEkeywords}\nDeepfake detection, face forgery, beautification, skin smoothing, robustness "
       "evaluation, shortcut learning, identity verification.\n\\end{IEEEkeywords}\n")
assert s.count(old) == 1
s = s.replace(old, new)
# journal author block (single-blind venue): placeholder to be filled by the authors
old = "\\author{\\IEEEauthorblockN{Anonymous submission}}"
assert s.count(old) == 1
s = s.replace(old, "\\author{First~Author, Second~Author, and Third~Author\\thanks{Author names, affiliations and the "
              "corresponding address are to be filled in before submission; the arXiv and IJCB versions use the anonymous block.}}")
# abstract: the challenge sentence (REVIEW_V9 D1-14), journal page budget only
old = ("app-beautified deepfake videos with one decision rule. Fifteen of the seventeen score the smoothed genuine face above its own original\n")
assert s.count(old) == 1, "abstract anchor"
s = s.replace(old, "app-beautified deepfake videos with one decision rule. Prior evaluations measured one direction, a few detectors and no\n"
              "cause; reading both directions needs one rule, control of re-encoding and a training intervention that tests the\n"
              "cause. Fifteen of the seventeen score the smoothed genuine face above its own original\n")
# journal layout: Fig. 1 as an ordinary full-width float after the abstract, not injected above it (REVIEW_V10 minor)
t0 = s.index("\\IEEEaftertitletext{"); t1 = s.index("\\maketitle")
block = s[t0:t1]
inner = block[block.index("\\begin{center}") + len("\\begin{center}"):block.rindex("\\end{center}")]
inner = inner.replace("\\captionof{figure}", "\\caption")
s = s[:t0] + s[t1:]
fig1 = "\\begin{figure*}[!t]\n\\centering" + inner + "\\end{figure*}\n"
anchor = "% ----------------------------------------------------------------------------\n\\section{Introduction}\n"
assert s.count(anchor) == 1, "intro anchor"
s = s.replace(anchor, anchor + fig1)
# journal page budget: the reproduction table (S3) and the protocol-comparison table (S4) move into the body (REVIEW_V9 D1-9a)
supp = (D / "supplement_v10.tex").read_text(encoding="utf-8")
t0 = supp.rfind("\\begin{table}", 0, supp.index("\\label{tab:reproduce}")); t1 = supp.index("\\end{table}", t0) + len("\\end{table}")
tab = supp[t0:t1].replace("\\begin{table}[H]", "\\begin{table*}[t]").replace("\\end{table}", "\\end{table*}")
tab = tab.replace("\\begin{table}", "\\begin{table*}").replace("\\label{tab:reproduce}", "\\label{tab:reproduce}")
tab = tab.replace("max width=\\linewidth", "max width=\\textwidth")
anchor = "Table~\\ref{S-tab:compare} compares this protocol with the prior evaluations of Sec.~\\ref{sec:intro} feature by feature.\n"
assert s.count(anchor) == 1, "compare anchor"
c0 = supp.rfind("\\begin{table}", 0, supp.index("\\label{tab:compare}")); c1 = supp.index("\\end{table}", c0) + len("\\end{table}")
ctab = supp[c0:c1].replace("\\begin{table}[H]", "\\begin{table*}[t]").replace("\\end{table}", "\\end{table*}").replace("max width=\\linewidth", "max width=\\textwidth")
s = s.replace(anchor, anchor + tab + "\n" + ctab + "\n")
s = s.replace("Table~\\ref{S-tab:reproduce}", "Table~\\ref{tab:reproduce}").replace("Table~\\ref{S-tab:compare}", "Table~\\ref{tab:compare}")
for mac in ("\\newcommand{\\oursB}{\\textsc{Ours}, forgery head only}\n", "\\newcommand{\\oursF}{\\textsc{Ours}, full model}\n",
            "\\newcommand{\\cmark}{\\checkmark}\n", "\\newcommand{\\xmark}{--}\n"):
    if mac.split("}")[0] + "}" not in s:
        s = s.replace("\\newcommand{\\ours}{\\textsc{Ours}}\n", "\\newcommand{\\ours}{\\textsc{Ours}}\n" + mac)
(D / "main_v10j.tex").write_text(s, encoding="utf-8")
bad = [(i + 1, l) for i, l in enumerate(s.splitlines()) if any(ord(c) < 32 and c not in "\t" for c in l)]
print("main_v10j.tex written; control chars:", bad[:3])
