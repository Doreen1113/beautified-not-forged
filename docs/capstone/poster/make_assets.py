"""Poster assets from the report's vector figures: rasterise docs/capstone/report_v3/figs/*.pdf at print resolution with PyMuPDF
and crop the parts the poster shows. Writes assets/fig_overview_top.png (panels 1-3 of the overview) and
assets/fig_evidence_row.png (the donor-nose row of the evidence figure). The banner is made by make_banner.py."""
from pathlib import Path

import fitz
from PIL import Image

H = Path(__file__).resolve().parent; F = H.parents[0] / "report_v3/figs"; A = H / "assets"; A.mkdir(exist_ok=True)


def raster(name, zoom):
    p = fitz.open(F / f"{name}.pdf")[0]
    out = A / f"{name}_hi.png"; p.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False).save(out)
    return Image.open(out)


im = raster("fig_overview", 9); w, h = im.size
im.crop((0, 0, w, int(h * 0.632))).save(A / "fig_overview_top.png")
im = raster("fig_evidence", 8); w, h = im.size
im.crop((0, int(h * 0.080), w, int(h * 0.512))).save(A / "fig_evidence_row.png")
for n in ("fig_overview_hi.png", "fig_evidence_hi.png"):
    (A / n).unlink()
print("fig_overview_top.png", Image.open(A / "fig_overview_top.png").size, "fig_evidence_row.png", Image.open(A / "fig_evidence_row.png").size)
