#!/bin/sh
# Build figs/fig_engine.pdf (+ .png preview) from fig_engine.tex with tectonic on gsplat-ubuntu (Liberation Sans is installed
# there). Tiles first: python make_tiles_method.py vendor && python make_tiles_engine.py.
set -e
D=$(cd "$(dirname "$0")" && pwd); cd "$D"
ssh gsplat-ubuntu 'mkdir -p ~/paper_build/capstone_v3/figs'
scp -q fig_engine.tex gsplat-ubuntu:paper_build/capstone_v3/
scp -q figs/method_vendor_O.png figs/method_vendor_R.png figs/engine_*.png figs/method_comp_eye.png figs/method_comp_contour.png figs/method_comp_tone.png figs/method_comp_texture.png gsplat-ubuntu:paper_build/capstone_v3/figs/
ssh gsplat-ubuntu 'cd ~/paper_build/capstone_v3 && ~/miniconda3/envs/tex/bin/tectonic fig_engine.tex > fe.out 2>&1; tail -2 fe.out; grep -iE "error|overfull|missing character" fe.out | head'
scp -q gsplat-ubuntu:paper_build/capstone_v3/fig_engine.pdf "$D/figs/fig_engine.pdf"
/c/Users/2603055/AppData/Local/miniconda3/python.exe -c "
import fitz; d=fitz.open('figs/fig_engine.pdf'); p=d[0]; r=p.rect
print('size cm %.2f x %.2f' % (r.width/72*2.54, r.height/72*2.54))
p.get_pixmap(dpi=300).save('figs/fig_engine.png')"
