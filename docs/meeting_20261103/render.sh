#!/bin/bash
# render a deck with LibreOffice on the Ubuntu box (no local soffice), pull back PNGs of every slide and a contact sheet
# usage: bash render.sh report_senior_20261018 [dpi]
set -e
D=${1:-final_meeting_20261103}; H=/c/My_Project/AIGC/docs/meeting_20261103
SP=/c/Users/2603055/AppData/Local/Temp/claude/c--My-Project-AIGC/96db1b8f-0cd1-4fe0-83dd-0c3954b13ed8/scratchpad/$D
mkdir -p $SP; rm -f $SP/*.png $SP/*.pdf
scp -q $H/$D.pptx gsplat-ubuntu:~/lo/
ssh -n gsplat-ubuntu "cd ~/lo && rm -f $D.pdf && HOME=\$HOME/lo timeout 300 ./root/opt/libreoffice26.2/program/soffice --headless --convert-to pdf $D.pptx >/dev/null 2>&1; ls -la $D.pdf"
scp -q gsplat-ubuntu:~/lo/$D.pdf $SP/
/c/Users/2603055/AppData/Local/miniconda3/python.exe - "$SP" "$D" "${2:-110}" <<'PY'
import fitz, pathlib, sys
from PIL import Image
sp = pathlib.Path(sys.argv[1]); d = fitz.open(sp / f"{sys.argv[2]}.pdf"); dpi = int(sys.argv[3])
ims = []
for i, pg in enumerate(d):
    p = sp / f"s{i+1:02d}.png"; pg.get_pixmap(dpi=dpi).save(p); ims.append(Image.open(p).convert("RGB"))
w, h = 800, 450; cols = 4; rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * (w + 10) + 10, rows * (h + 10) + 10), "#888")
for i, im in enumerate(ims):
    sheet.paste(im.resize((w, h)), (10 + (i % cols) * (w + 10), 10 + (i // cols) * (h + 10)))
sheet.save(sp / "sheet.png"); print("rendered", len(ims), sp)
PY
