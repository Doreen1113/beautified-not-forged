#!/bin/sh
# Build report.pdf with tectonic (XeLaTeX) on gsplat-ubuntu; Liberation Serif + Noto Serif TC are installed there.
# Since r10 (2026-11-03): cover.tex (department cover, official format) + report.tex (IEEE two-column body) are compiled
# separately and merged here into report.pdf: cover, then the body with its own page numbers from 1.
set -e
D=$(cd "$(dirname "$0")" && pwd); cd "$D"
ssh gsplat-ubuntu 'mkdir -p ~/paper_build/capstone_v3/figs'
scp -q report.tex cover.tex abstract.tex refs.bib gsplat-ubuntu:paper_build/capstone_v3/
scp -q figs/*.pdf figs/*.png figs/*.tex gsplat-ubuntu:paper_build/capstone_v3/figs/
ssh gsplat-ubuntu 'cd ~/paper_build/capstone_v3 && ~/miniconda3/envs/tex/bin/tectonic -k report.tex > t.out 2>&1; tail -2 t.out; grep -E "undefined|Overfull|Missing character|^error" t.out | sort | uniq -c | head; ~/miniconda3/envs/tex/bin/tectonic cover.tex > c.out 2>&1; grep -E "^error|Overfull" c.out | head -3'
scp -q gsplat-ubuntu:paper_build/capstone_v3/report.pdf "$D/report_body.pdf"
scp -q gsplat-ubuntu:paper_build/capstone_v3/cover.pdf "$D/cover.pdf"
/c/Users/2603055/AppData/Local/miniconda3/python.exe -c "
import fitz
out = fitz.open('cover.pdf'); body = fitz.open('report_body.pdf'); out.insert_pdf(body)
out.set_toc([[l, t, p + 1] for l, t, p in body.get_toc()])
out.save('report.pdf', garbage=3, deflate=True)
print('pages', out.page_count, '(cover 1 + body', body.page_count, ')')"
