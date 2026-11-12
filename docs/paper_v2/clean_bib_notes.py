"""Strip provenance `note = {...}` lines (our verification bookkeeping) from refs_v8.bib so that they do not print in the
reference list. Only notes that start with 'verified', 'author names', or 'arXiv:' + 'verified' are removed; a note that is
part of the citation itself (e.g. 'arXiv:2207.12319') is kept. Idempotent."""
import re
from pathlib import Path
for p in [Path(r"C:\My_Project\AIGC\docs\paper_v2\refs_v8.bib"), Path(r"C:\My_Project\AIGC\docs\paper_v2\arxiv_v10\refs_v8.bib")]:
    if not p.exists():
        continue
    lines = p.read_text(encoding="utf-8").splitlines(True); out = []; n = 0
    for l in lines:
        m = re.match(r"\s*note\s*=\s*\{(.*)\}\s*,?\s*$", l)
        if m and re.match(r"(verified|author names|DOI and journal)", m.group(1), re.I):
            n += 1; continue
        out.append(l)
    # a removed note may leave a trailing comma on the previous field: harmless in BibTeX
    p.write_text("".join(out), encoding="utf-8"); print(p.name, "notes removed:", n)
