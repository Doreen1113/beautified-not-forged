import re
from pathlib import Path
s = (Path(__file__).resolve().parent / "main_v7.tex").read_text(encoding="utf-8")
secs = [(m.start(), m.group(0)) for m in re.finditer(r"\\(?:sub)?section\{[^}]*\}", s)]
for i, (a, name) in enumerate(secs):
    b = secs[i + 1][0] if i + 1 < len(secs) else len(s)
    body = re.sub(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", " ", s[a:b], flags=re.S)
    body = re.sub(r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", " ", body, flags=re.S)
    words = len(re.sub(r"\\[a-zA-Z]+|[{}]|%.*", " ", body).split())
    print(f"{words:5d}  {name}")
