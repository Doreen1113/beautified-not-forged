"""High-resolution copies of the report's method tiles for the poster (the report's are 300 x 360 px, printed at 1.5 cm).
Reuses docs/capstone/report_v3/make_tiles_method.py on the same records, at 720 x 864 px, into assets/tiles/.
python docs/capstone/poster/make_tiles_hires.py"""
import sys
from pathlib import Path

import cv2
import numpy as np

B = Path(r"C:\My_Project\AIGC"); H = Path(__file__).resolve().parent
RU = B / "results/research/retouch_unified_20260929"
sys.path.insert(0, str(B / "docs/capstone/report_v3")); sys.path.insert(0, str(B / "docs/paper_v2")); sys.path.insert(0, str(RU))
import make_tiles_method as MT  # noqa: E402

W, Hh = 720, 864
OUT = H / "assets/tiles"; OUT.mkdir(parents=True, exist_ok=True)
MT.OUT, MT.W, MT.H = OUT, W, Hh
MT.fit = lambda im, w=W, h=Hh: cv2.resize(np.ascontiguousarray(im), (w, h), interpolation=cv2.INTER_AREA)


def footprint_tile(m01, w=W, h=Hh):
    m = cv2.resize(m01.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA) > 0.5
    rgb = np.full((h, w, 3), 236, np.uint8); rgb[m] = MT.NN; return rgb


MT.footprint_tile = footprint_tile
print("ffpp", MT.ffpp_triplet())
print("vendor", MT.vendor())
it, x = MT.part_edit()
print("part", it["x"])
print(sorted(p.name for p in OUT.glob("*.png")))
