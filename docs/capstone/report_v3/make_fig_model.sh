#!/bin/sh
# Build figs/fig_model.pdf (+ .png preview) from fig_model.tex with tectonic on gsplat-ubuntu (Liberation Sans is installed
# there). Tiles first: python make_tiles_model.py.
set -e
D=$(cd "$(dirname "$0")" && pwd); cd "$D"
ssh gsplat-ubuntu 'mkdir -p ~/paper_build/capstone_v3/figs'
scp -q fig_model.tex gsplat-ubuntu:paper_build/capstone_v3/
scp -q figs/model_in.png figs/model_ev16.png figs/model_M16.png gsplat-ubuntu:paper_build/capstone_v3/figs/
ssh gsplat-ubuntu 'cd ~/paper_build/capstone_v3 && ~/miniconda3/envs/tex/bin/tectonic fig_model.tex > fm.out 2>&1; tail -2 fm.out; grep -iE "error|overfull|missing character" fm.out | head'
scp -q gsplat-ubuntu:paper_build/capstone_v3/fig_model.pdf "$D/figs/fig_model.pdf"
/c/Users/2603055/AppData/Local/miniconda3/python.exe -c "
import fitz; d=fitz.open('figs/fig_model.pdf'); p=d[0]; r=p.rect
print('size cm %.2f x %.2f' % (r.width/72*2.54, r.height/72*2.54))
p.get_pixmap(dpi=300).save('figs/fig_model.png')"
