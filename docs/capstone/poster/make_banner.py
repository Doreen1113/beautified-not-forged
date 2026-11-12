"""Turn the template banner (113 學年度...) into 115: paint the "3" over with the banner's own gradient (per-row interpolation
between the pixels left and right of the glyph) and draw a Times New Roman "5" at the same digit height. Writes
assets/banner_115.png; assets/banner.png is the untouched template image (media/image1.png of the .odp)."""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

A = Path(__file__).resolve().parent / "assets"
im = Image.open(A / "banner.png").convert("RGBA"); a = np.array(im).astype(np.float32)
X0, X1, Y0, Y1 = 618, 778, 136, 390          # box around the "3" (glyph bbox 635-759 x 156-365)
for y in range(Y0, Y1):
    row = a[y]; L, R = row[X0 - 1, :3], row[X1, :3]
    for x in range(X0, X1):
        t = (x - X0) / (X1 - X0); row[x, :3] = L * (1 - t) + R * t; row[x, 3] = 255
out = Image.fromarray(a.astype(np.uint8))
d = ImageDraw.Draw(out)
target_h = 365 - 156 + 1; size = 100; f = ImageFont.truetype(r"C:\Windows\Fonts\times.ttf", size)
bb = d.textbbox((0, 0), "5", font=f); h = bb[3] - bb[1]
size = int(round(size * target_h / h)); f = ImageFont.truetype(r"C:\Windows\Fonts\times.ttf", size)
bb = d.textbbox((0, 0), "5", font=f); w, h = bb[2] - bb[0], bb[3] - bb[1]
cx, top = (635 + 759) / 2, 156
d.text((cx - w / 2 - bb[0], top - bb[1]), "5", font=f, fill=(255, 255, 255, 255))
out.save(A / "banner_115.png"); print("banner_115.png", out.size, "glyph", w, "x", h, "font size", size)
