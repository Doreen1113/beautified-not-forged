#!/bin/bash
# compile tex/*.tex on the Ubuntu box (tectonic), rasterise to assets/*.png at 400 dpi
set -e
H=/c/My_Project/AIGC/docs/meeting_20260930
ssh -n gsplat-ubuntu 'mkdir -p ~/meeting_tex'
scp -q $H/tex/*.tex gsplat-ubuntu:~/meeting_tex/
ssh -n gsplat-ubuntu 'cd ~/meeting_tex && for f in *.tex; do ~/miniconda3/envs/tex/bin/tectonic -X compile $f >/dev/null 2>&1 || echo "FAIL $f"; done; ls *.pdf'
for f in $(ssh -n gsplat-ubuntu 'cd ~/meeting_tex && ls *.pdf'); do scp -q gsplat-ubuntu:~/meeting_tex/$f $H/tex/; done
python - <<'PY'
import fitz, pathlib
H = pathlib.Path(r"C:\My_Project\AIGC\docs\meeting_20260930")
for f in (H / "tex").glob("*.pdf"):
    fitz.open(f)[0].get_pixmap(dpi=400).save(H / "assets" / (f.stem + ".png")); print("->", f.stem)
PY
