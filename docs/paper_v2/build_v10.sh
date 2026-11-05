#!/bin/sh
# Build paper v10 (main_v10.tex + supplement_v10.tex) on gsplat-ubuntu (tectonic) and copy the PDFs back.
# Order: main, supplement, main, supplement (xr cross-references both ways). Run from anywhere: sh docs/paper_v2/build_v8.sh
set -e
D=$(cd "$(dirname "$0")" && pwd)
cd "$D"
scp -q main_v10.tex supplement_v10.tex refs_v6.bib refs_v8.bib gsplat-ubuntu:paper_build/paper_v2/
scp -q tables/tab_sic.tex tables/tab_sic_full.tex tables/tab_v8_*.tex tables/tab_v9_*.tex tables/tab_v6b_*.tex tables/tab_v6_*.tex tables/tab_v5_*.tex tables/tab_exposure.tex tables/tab_exposure_ext.tex tables/tab_mechanism.tex tables/tab_erasure.tex tables/tab_operator.tex tables/tab_cgd_explain.tex gsplat-ubuntu:paper_build/paper_v2/tables/
scp -q figs/fig_method_v8b.pdf figs/fig_teaser_v8b.pdf figs/fig_exposure_v8b.pdf figs/fig_bandenergy_v8b.pdf figs/fig_sic_curve_v8b.pdf figs/fig_twoaxis_v8b.pdf figs/fig_teaser_v7.pdf figs/fig_exposure_v7.pdf figs/fig_bandenergy.pdf figs/fig_sic_curve.pdf figs/fig_twoaxis_v8.pdf figs/fig_mechanism.pdf figs/fig_context_v8b.pdf figs/fig_teaser_v9.pdf figs/fig_dirs_v9.pdf figs/fig_twoaxis_v10.pdf figs/fig_method_v10.pdf figs/fig_exposure_v10.pdf figs/fig_evidence.pdf gsplat-ubuntu:paper_build/paper_v2/figs/
ssh gsplat-ubuntu 'cd ~/paper_build/paper_v2 && T=~/miniconda3/envs/tex/bin/tectonic;
  for f in main_v10 supplement_v10 main_v10 supplement_v10; do $T -k $f.tex > t_$f.out 2>&1 || { echo FAIL $f; grep -A8 "error" t_$f.out | head -30; }; done;
  grep -hE "Overfull|undefined|Writing .*pdf" t_main_v10.out t_supplement_v10.out | sort | uniq -c'
# copy back; a PDF that is open in a viewer on Windows cannot be overwritten, then the copy lands next to it as <name>_new.pdf
for f in main_v10 supplement_v10; do
  scp -q gsplat-ubuntu:paper_build/paper_v2/$f.pdf "$D/$f.pdf" 2>/dev/null || { echo "WARNING: $f.pdf is locked locally, written as ${f}_new.pdf"; scp -q gsplat-ubuntu:paper_build/paper_v2/$f.pdf "$D/${f}_new.pdf"; }
done
python -c "import fitz,sys,os; [print(f, fitz.open(f).page_count) for f in ('main_v10.pdf','main_v10_new.pdf','supplement_v10.pdf','supplement_v10_new.pdf') if os.path.exists(f)]" 2>/dev/null || true
