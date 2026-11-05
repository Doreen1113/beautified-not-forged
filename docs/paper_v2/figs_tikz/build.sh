#!/bin/sh
# Compile the TikZ figures on gsplat-ubuntu (tectonic) and render 300-dpi PNGs locally with fitz.
# usage: sh docs/paper_v2/figs_tikz/build.sh [fig_arch fig_system ...]
set -e
D=$(cd "$(dirname "$0")" && pwd); cd "$D"
FIGS=${*:-"fig_arch fig_arch_wide fig_system fig_protocol fig_exposure fig_explain_layers"}
ssh -n gsplat-ubuntu 'mkdir -p ~/paper_build/figs_tikz/img'
scp -q style.tex $(for f in $FIGS; do echo $f.tex; done) gsplat-ubuntu:paper_build/figs_tikz/
scp -q img/*.png gsplat-ubuntu:paper_build/figs_tikz/img/
for f in $FIGS; do
  ssh -n gsplat-ubuntu "cd ~/paper_build/figs_tikz && timeout 300 ~/miniconda3/envs/tex/bin/tectonic -k $f.tex > $f.out 2>&1 || { echo FAIL $f; grep -B2 -A6 '^!\|error' $f.out | head -30; }; grep -E 'Overfull|Underfull|Missing character' $f.out | sort | uniq -c | head"
  scp -q gsplat-ubuntu:paper_build/figs_tikz/$f.pdf "$D/" || true
done
/c/Users/2603055/AppData/Local/miniconda3/python.exe - $FIGS <<'PY'
import fitz, sys
for f in sys.argv[1:]:
    try:
        d = fitz.open(f + ".pdf"); r = d[0].rect; d[0].get_pixmap(dpi=300).save(f + ".png")
        print(f"{f}: {r.width/72:.2f} x {r.height/72:.2f} in")
    except Exception as e:
        print(f, "no pdf", e)
PY
