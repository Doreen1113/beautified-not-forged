#!/bin/bash
# render the deck with LibreOffice on the Ubuntu box, pull back PNGs of every slide
set -e
H=/c/My_Project/AIGC/docs/meeting_20260930; SP=/c/Users/2603055/AppData/Local/Temp/claude/c--My-Project-AIGC/96db1b8f-0cd1-4fe0-83dd-0c3954b13ed8/scratchpad/deck
mkdir -p $SP; rm -f $SP/*.png
scp -q $H/meeting_20260930_v4.pptx gsplat-ubuntu:~/lo/
ssh -n gsplat-ubuntu 'cd ~/lo && rm -f meeting_20260930_v4.pdf && HOME=$HOME/lo timeout 300 ./root/opt/libreoffice26.2/program/soffice --headless --convert-to pdf meeting_20260930_v4.pptx >/dev/null 2>&1; ls -la meeting_20260930_v4.pdf'
scp -q gsplat-ubuntu:~/lo/meeting_20260930_v4.pdf $SP/
python - <<'PY'
import fitz, pathlib
sp = pathlib.Path(r"C:\Users\2603055\AppData\Local\Temp\claude\c--My-Project-AIGC\96db1b8f-0cd1-4fe0-83dd-0c3954b13ed8\scratchpad\deck")
d = fitz.open(sp / "meeting_20260930_v4.pdf")
for i, pg in enumerate(d):
    pg.get_pixmap(dpi=60).save(sp / f"s{i+1:02d}.png")
print("rendered", len(d))
PY
