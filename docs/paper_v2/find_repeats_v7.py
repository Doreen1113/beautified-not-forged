import re
from pathlib import Path
s = (Path(__file__).resolve().parent / "main_v7.tex").read_text(encoding="utf-8")
b = s[s.index("\\begin{abstract}"):s.index("\\bibliographystyle")]
b = "\n".join(l for l in b.splitlines() if not l.lstrip().startswith("%"))
print("real em-dashes (---):", len(re.findall(r"(?<!-)---(?!-)", b)), "| unicode:", b.count("—"))
for m in re.finditer(r"sets the sign of\s+the error|scored as more forged than\s+the same face\s+untouched", b):
    print("---", b[max(0, m.start() - 90):m.end() + 15].replace("\n", " "))
