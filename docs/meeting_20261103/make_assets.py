"""Assets of the final meeting deck (2026-11-03): every figure is a figure of the capstone report, rendered from its vector PDF.

  report figures (docs/capstone/report_v3/figs/*.pdf): overview, engine, model, explain, evidence, twoaxis
  wide versions kept in assets_src/ (the report's one-column layouts before r10, 14.66 cm): teaser, exposure, context, perop
  screenshot: docs/capstone/report_v3/figs/fig_output_a_crop.png (copied)

python docs/meeting_20261103/make_assets.py  -> docs/meeting_20261103/assets/*.png"""
import shutil
from pathlib import Path

import fitz

H = Path(__file__).resolve().parent; OUT = H / "assets"; OUT.mkdir(exist_ok=True)
FIG = H.parent / "capstone/report_v3/figs"
DPI = 240

jobs = [(FIG / f"fig_{n}.pdf", n) for n in ("overview", "engine", "model", "explain", "evidence", "twoaxis")]
jobs += [(H / "assets_src" / f"onecol_fig_{n}.pdf", n) for n in ("teaser", "exposure", "context", "perop")]
for src, name in jobs:
    d = fitz.open(src); d[0].get_pixmap(dpi=DPI).save(OUT / f"{name}.png")
    print(name, d[0].rect.width / 72 * 2.54, "cm")
shutil.copy(FIG / "fig_output_a_crop.png", OUT / "screenshot.png")
print("assets:", len(list(OUT.glob("*.png"))))
