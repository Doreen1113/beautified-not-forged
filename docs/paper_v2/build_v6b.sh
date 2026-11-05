#!/bin/sh
# Build paper v6b on gsplat-ubuntu (tectonic) and copy the PDFs back. Order: main, supplement, main, supplement (xr cross-references).
# Run from anywhere: sh docs/paper_v2/build_v6b.sh
set -e
D=$(cd "$(dirname "$0")" && pwd)
cd "$D"
scp -q main_v6b.tex supplement_v6b.tex refs_v6.bib gsplat-ubuntu:paper_build/paper_v2/
scp -q tables/tab_v6b_*.tex tables/tab_v6_*.tex tables/tab_v5_*.tex tables/tab_cgd_explain.tex gsplat-ubuntu:paper_build/paper_v2/tables/
scp -q figs/fig_accuse_v6b.pdf figs/fig_teaser_v6b.pdf gsplat-ubuntu:paper_build/paper_v2/figs/
ssh gsplat-ubuntu 'cd ~/paper_build/paper_v2 && T=~/miniconda3/envs/tex/bin/tectonic;
  for f in main_v6b supplement_v6b main_v6b supplement_v6b; do $T -k $f.tex > t_$f.out 2>&1 || { echo FAIL $f; grep -A8 "error" t_$f.out | head -30; }; done;
  grep -hE "Overfull|undefined|Writing .*pdf" t_main_v6b.out t_supplement_v6b.out | sort | uniq -c'
scp -q gsplat-ubuntu:paper_build/paper_v2/main_v6b.pdf gsplat-ubuntu:paper_build/paper_v2/supplement_v6b.pdf "$D/"
python -c "import fitz,sys; [print(f, fitz.open(f).page_count) for f in ('main_v6b.pdf','supplement_v6b.pdf')]" 2>/dev/null || true
