"""fig_exposure_v7 (paper v7, 2026-10-18): which class receives smoothing training views, as a 2 x 2 picture (column width).

Replaces the text matrix figs_tikz/fig_exposure.tex. Numbers are copied from that file (FF++-only arms P0-P3, first seed;
docs/paper_v2/tables/tab_v6b_tradeoff_main.tex): FA = share of commercial Smoothing-90 renders accused at the threshold that accuses
5 % of their originals (P0 54.2, P3 63.8, P1 3.7, P2 11.7 %); dMISS = change of the miss rate on Celeb-DF-v2 forgeries under strong
whole-crop smoothing at the same rule (P0 -16.0, P3 -38.5, P1 +51.2, P2 -26.5 points).
Each cell shows the two training views: a genuine face and a forged face, each drawn smoothed (cv2.bilateralFilter on the
thumbnail, twice) with a sparkle badge when that class received smoothing views. Genuine face: an FFHQ demo original
(results/research/explain_vlm_20261012/ffhq_demo_edits_holdout/17083_x0.png). Forged face: the Celeb-DF-B deepfake frame of
fig_teaser_v6b (same selection rule as make_fig_teaser_v6b.py, untreated frame); no forgery is fabricated.

    python docs/paper_v2/make_fig_exposure_v7.py  -> docs/paper_v2/figs/fig_exposure_v7.{pdf,png}
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B / "docs/paper_v2"))
import figstyle as FS  # noqa: E402
FS.apply()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Circle  # noqa: E402

OUT = B / "docs/paper_v2/figs"
WARN = "#C98A00"          # warning / filter colour of the TikZ style (style.tex "amber"); used for the miss change
VIEW = FS.OURS_ARM        # smoothing-view badge
CELLS = {  # arm: (col, row, FA %, dMISS points, views)
    "P0": (0, 0, 54.2, -16.0, "no views"), "P3": (1, 0, 63.8, -38.5, "forged only"),
    "P1": (0, 1, 3.7, +51.2, "genuine only"), "P2": (1, 1, 11.7, -26.5, "both classes")}

# ---------------------------------------------------------------- faces
T = 224
gen = np.array(Image.open(B / "results/research/explain_vlm_20261012/ffhq_demo_edits_holdout/17083_x0.png").convert("RGB"))
gen = cv2.resize(gen[40:470, 60:490], (T, T), interpolation=cv2.INTER_AREA)
# forged face: the deepfake frame of fig_teaser_v6b (selection rule copied from make_fig_teaser_v6b.py, which must not be imported
# because it redraws its figure on import)
rows = [l.split("\t") for l in (B / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
S = B / "results/research/celebdfb_v2_20260927/scores_v3"
sbi = np.load(S / "sbi.npz")["p"][:, 1]; ru = np.load(S / "RU-clipe5.npz")["p"]
folder = np.array([r[3] for r in rows]); vid = np.array([r[2] for r in rows]); fr = np.array([Path(r[0]).stem.split("__")[-1] for r in rows])
t = float(np.quantile(sbi[folder == "real"], 0.95)); am = ru.argmax(1)
idx = {(f, v, x): i for i, (f, v, x) in enumerate(zip(folder, vid, fr))}
best = None
for (f, v, x), i in idx.items():
    if f != "synthesis":
        continue
    j = idx.get(("synthesis_beautified", v, x))
    if j is not None and sbi[i] > t and sbi[j] <= t and am[i] == 1 and am[j] == 1 and ru[j, 1] > 0.8:
        sc = abs(sbi[i] - sbi[j]) + ru[j].max()
        if best is None or sc > best[0]:
            best = (sc, i, j)
forged_path = rows[best[1]][0]; print("forged thumbnail:", forged_path)
fk = np.array(Image.open(forged_path).convert("RGB")); h, w = fk.shape[:2]; s = min(h, w)
fk = cv2.resize(fk[(h - s) // 2:(h - s) // 2 + s, (w - s) // 2:(w - s) // 2 + s], (T, T), interpolation=cv2.INTER_AREA)


def smooth(im):
    return cv2.bilateralFilter(cv2.bilateralFilter(im, 11, 70, 70), 11, 70, 70)


FACES = {"genuine": (gen, smooth(gen)), "forged": (fk, smooth(fk))}

# ---------------------------------------------------------------- drawing, at final size
W, H = 3.3, 3.2
fig = plt.figure(figsize=(W, H))
LM, TOP, GAP, FOOT = 0.44, 0.33, 0.06, 0.34       # row-header width, column-header height, cell gap, footer
cw = (W - LM - GAP - 0.04) / 2; ch = (H - TOP - GAP - FOOT) / 2
x_of = lambda c: LM + c * (cw + GAP); y_of = lambda r: H - TOP - (r + 1) * ch - r * GAP      # cell lower-left (inches)
F = fig.transFigure


def sparkle(ax, cx, cy, r, color):
    pts = []
    for k in range(8):
        a = np.pi / 2 + k * np.pi / 4; rr = r if k % 2 == 0 else 0.38 * r
        pts.append((cx + rr * np.cos(a), cy + rr * np.sin(a)))
    ax.add_patch(Polygon(pts, closed=True, fc="white", ec="none", transform=ax.transAxes, zorder=6, clip_on=False))


def badge(ax):
    """smoothing-view badge in the thumbnail's top-right corner: a coloured disc with a white sparkle."""
    ax.add_patch(Circle((0.84, 0.84), 0.15, fc=VIEW, ec="white", lw=0.6, transform=ax.transAxes, zorder=5, clip_on=False))
    sparkle(ax, 0.84, 0.84, 0.1, "white")


for arm, (c, r, fa, dm, views) in CELLS.items():
    x0, y0 = x_of(c), y_of(r)
    gen_v, fk_v = (r == 1), (c == 1)                                    # which class receives smoothing views
    role = "evasion" if arm == "P1" else ("accusation" if arm == "P3" else None)
    edge = {"P1": WARN, "P3": FS.FAKE}.get(arm, FS.GRID)
    fig.add_artist(FancyBboxPatch((x0 / W, y0 / H), cw / W, ch / H, boxstyle="round,pad=0,rounding_size=0.012", transform=F,
                                  fc="white", ec=edge, lw=1.1 if role else 0.6, zorder=-1))
    fig.text((x0 + 0.06) / W, (y0 + ch - 0.055) / H, arm, ha="left", va="top", fontsize=FS.FS_TEXT, fontweight="bold", color=FS.INK)
    fig.text((x0 + 0.06 + 0.2) / W, (y0 + ch - 0.058) / H, views, ha="left", va="top", fontsize=FS.FS_NOTE - 0.5, color=FS.MUTED)
    if role:
        fig.text((x0 + cw - 0.06) / W, (y0 + ch - 0.055) / H, role, ha="right", va="top", fontsize=FS.FS_NOTE, fontweight="bold", color=edge)
    # the two training views
    th = 0.5; tg = 0.08; tx = x0 + (cw - 2 * th - tg) / 2; ty = y0 + ch - 0.21 - th
    for k, (cls, smoothed) in enumerate((("genuine", gen_v), ("forged", fk_v))):
        ax = fig.add_axes([(tx + k * (th + tg)) / W, ty / H, th / W, th / H])
        ax.imshow(FACES[cls][1 if smoothed else 0], interpolation="lanczos"); FS.frame(ax, color=FS.MUTED, lw=0.4)
        if smoothed:
            badge(ax)
        fig.text((tx + k * (th + tg) + th / 2) / W, (ty - 0.015) / H, cls, ha="center", va="top",
                 fontsize=FS.FS_NOTE - 0.5, color=FS.REAL if cls == "genuine" else FS.FAKE)
    # bars: FA (0-100 %) and dMISS (-40 .. +55 points, zero marked)
    bx0, bw_ = x0 + 0.36, cw - 0.36 - 0.5; by1, by2 = y0 + 0.24, y0 + 0.09; bh = 0.075
    fig.text((bx0 - 0.03) / W, (by1 + bh / 2) / H, "FA", ha="right", va="center", fontsize=FS.FS_NOTE - 0.5, color=FS.INK)
    fig.text((bx0 - 0.03) / W, (by2 + bh / 2) / H, "\u0394miss", ha="right", va="center", fontsize=FS.FS_NOTE - 0.5, color=FS.INK)
    fig.add_artist(plt.Rectangle((bx0 / W, by1 / H), bw_ / W, bh / H, transform=F, fc=FS.LIGHT, ec="none"))
    fig.add_artist(plt.Rectangle((bx0 / W, by1 / H), bw_ * fa / 100 / W, bh / H, transform=F, fc=FS.FAKE, ec="none"))
    fig.text((bx0 + bw_ + 0.03) / W, (by1 + bh / 2) / H, f"{fa:.1f}%", ha="left", va="center", fontsize=FS.FS_NOTE, color=FS.FAKE,
             fontweight="bold" if arm == "P3" else "normal")
    lo, hi = -40.0, 55.0; z = bx0 + bw_ * (0 - lo) / (hi - lo)
    fig.add_artist(plt.Rectangle((bx0 / W, by2 / H), bw_ / W, bh / H, transform=F, fc=FS.LIGHT, ec="none"))
    xa, xb = (z, z + bw_ * dm / (hi - lo)) if dm > 0 else (z + bw_ * dm / (hi - lo), z)
    fig.add_artist(plt.Rectangle((xa / W, by2 / H), (xb - xa) / W, bh / H, transform=F, fc=WARN, ec="none"))
    fig.add_artist(plt.Line2D([z / W, z / W], [(by2 - 0.015) / H, (by2 + bh + 0.015) / H], transform=F, color=FS.INK, lw=0.6))
    fig.text((bx0 + bw_ + 0.03) / W, (by2 + bh / 2) / H, f"{dm:+.1f} pts".replace("-", "−"), ha="left", va="center", fontsize=FS.FS_NOTE, color=WARN,
             fontweight="bold" if arm == "P1" else "normal")

# axes of the grid
cx_all = LM + cw + GAP / 2
fig.text(cx_all / W, (H - 0.03) / H, "forged faces receive smoothing views", ha="center", va="top", fontsize=FS.FS_TEXT, fontweight="bold")
for c, lab in enumerate(("no", "yes")):
    fig.text((x_of(c) + cw / 2) / W, (H - TOP + 0.03) / H, lab, ha="center", va="bottom", fontsize=FS.FS_TEXT, color=FS.INK)
fig.text(0.03 / W, (y_of(0) + ch / 2 - (ch + GAP) / 2) / H, "genuine faces receive\nsmoothing views", ha="left", va="center", rotation=90,
         fontsize=FS.FS_TEXT, fontweight="bold", linespacing=1.0)
for r, lab in enumerate(("no", "yes")):
    fig.text((LM - 0.04) / W, (y_of(r) + ch / 2) / H, lab, ha="right", va="center", fontsize=FS.FS_TEXT, color=FS.INK)
fig.text(cx_all / W, 0.04 / H, "FF++-only training, first seed; same architecture, data and recipe", ha="center", va="bottom",
         fontsize=FS.FS_NOTE, color=FS.MUTED)
# legend for the badge
lx, ly = LM + 0.3, 0.215
lax = fig.add_axes([lx / W, (ly - 0.05) / H, 0.1 / W, 0.1 / H]); lax.axis("off")
lax.add_patch(Circle((0.5, 0.5), 0.45, fc=VIEW, ec="white", lw=0.6, transform=lax.transAxes, clip_on=False)); sparkle(lax, 0.5, 0.5, 0.3, "white")
fig.text((lx + 0.14) / W, ly / H, "this class receives smoothing views (drawn smoothed)", ha="left", va="center", fontsize=FS.FS_NOTE - 0.5, color=FS.MUTED)
FS.save(fig, OUT / "fig_exposure_v7")
print("wrote", OUT / "fig_exposure_v7.pdf")
