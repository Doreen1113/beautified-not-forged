import re
import sys
from pathlib import Path
s = (Path(__file__).resolve().parent / "main_v7.tex").read_text(encoding="utf-8")
a = s.index(sys.argv[1]); b = s.index(sys.argv[2], a + 1)
body = re.sub(r"\\begin\{(figure|table)\*?\}.*?\\end\{(figure|table)\*?\}", "[FLOAT]", s[a:b], flags=re.S)
print(body)
