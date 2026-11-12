"""fig_exposure_v8b (paper v8, 2026-10-22): the 2 x 2 training-exposure design, column width (3.5 x 3.05 in).

Rows: genuine faces receive smoothed training views (no / yes); columns: forged faces receive them (no / yes). Cells P0 (neither),
P3 (forged only), P1 (genuine only), P2 (both). Each cell shows the two training views (a genuine and a forged face, drawn
smoothed when that class receives smoothing views) and two bars:
  FA     share of the commercial Smoothing-90 renders accused at the threshold that accuses 5 % of their originals
         results/research/retouch_unified_20260929/p3_readout40.json  [arm].smoothing90_at_5fpr[0]  (P3 readout, Addendum 40)
  dMISS  change of the miss rate on Celeb-DF-v2 forgeries under strong whole-crop smoothing (bilateral d21) at the same rule
         p3_readout40.json  [arm].miss_rise[2][0]  (index 2 = bil21; cross-checked against smooth_evasion2.json[tag].miss_rise[2][0])
Both arrays are the first seed (tables/tab_v6_p3.tex and tab_v6b_tradeoff_main.tex print the same cells). Colour semantics:
red = the accusation direction (FA, and a negative dMISS: the arm accuses every smoothed face), amber = the escape direction
(a positive dMISS: smoothed forgeries pass).
Faces as in fig_exposure_v7: genuine = results/research/explain_vlm_20261012/ffhq_demo_edits_holdout/17083_x0.png; forged = the
Celeb-DF-B deepfake frame selected by the rule of make_fig_teaser_v6b.py (re-implemented here, nothing is fabricated).

    python docs/paper_v2/make_fig_exposure_v8b.py  -> docs/paper_v2/figs/fig_exposure_v8b.{pdf,png}
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B / "docs/paper_v2"))
import figstyle as FS  # noqa: E402
import figstyle_v8b as V  # noqa: E402
FS.apply()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch  # noqa: E402

OUT = B / "docs/paper_v2/figs"
RU = B / "results/research/retouch_unified_20260929"
ACC = FS.FAKE            # accusation direction
EVA = "#C98A00"          # escape direction (amber of figs_tikz/style.tex)
VIEW = FS.OURS_ARM       # "smoothed views" chip

# ---------------------------------------------------------------- numbers
p3 = json.loads((RU / "p3_readout40.json").read_text(encoding="utf-8"))
ev = json.loads((RU / "smooth_evasion2.json").read_text(encoding="utf-8"))
TAG = {"P0": "clipe5fbp0_s20260929", "P1": "clipe5fbp1_s20260929", "P2": "clipe5fb_s20260929", "P3": "clipe5fbp3_s20260929"}
CELLS = {"P0": (0, 0, "neither class"), "P3": (1, 0, "forged only"), "P1": (0, 1, "genuine only"), "P2": (1, 1, "both classes")}
NUM = {}
for arm in CELLS:
    fa = p3[arm]["smoothing90_at_5fpr"][0]; dm = p3[arm]["miss_rise"][2][0]
    assert abs(dm - ev[TAG[arm]]["miss_rise"][2][0]) < 1e-9, arm
    NUM[arm] = (fa, dm); print(arm, f"FA {fa:.1f}  dMISS {dm:+.1f}")

# ---------------------------------------------------------------- faces
T = 224
gen = np.array(Image.open(B / "results/research/explain_vlm_20261012/ffhq_demo_edits_holdout/17083_x0.png").convert("RGB"))
gen = cv2.resize(gen[40:470, 60:490], (T, T), interpolation=cv2.INTER_AREA)
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
W, H = FS.COL, 3.05
fig = plt.figure(figsize=(W, H))
LM, TOP, GAP, FOOT, RM = 0.40, 0.32, 0.07, 0.27, 0.03
cw = (W - LM - GAP - RM) / 2; ch = (H - TOP - GAP - FOOT) / 2
x_of = lambda c: LM + c * (cw + GAP); y_of = lambda r: H - TOP - (r + 1) * ch - r * GAP
F = fig.transFigure


def chip(ax):
    """small 'smoothed' chip in the lower-right corner of a thumbnail that receives smoothing views."""
    ax.add_patch(FancyBboxPatch((0.22, 0.04), 0.74, 0.19, boxstyle="round,pad=0,rounding_size=0.08", fc=VIEW, ec="white", lw=0.5,
                                transform=ax.transAxes, zorder=5, clip_on=False))
    ax.text(0.59, 0.135, "smoothed", ha="center", va="center", fontsize=FS.FS_NOTE - 1.8, color="white", transform=ax.transAxes, zorder=6)


FA_MAX = 70.0; DM_LO, DM_HI = -45.0, 55.0
for arm, (c, r, views) in CELLS.items():
    x0, y0 = x_of(c), y_of(r); fa, dm = NUM[arm]
    gen_v, fk_v = (r == 1), (c == 1)
    role = {"P1": ("escape", EVA), "P3": ("accusation", ACC)}.get(arm)
    fig.add_artist(FancyBboxPatch((x0 / W, y0 / H), cw / W, ch / H, boxstyle="round,pad=0,rounding_size=0.015", transform=F,
                                  fc="white", ec=role[1] if role else FS.GRID, lw=1.0 if role else 0.6, zorder=-1))
    fig.text((x0 + 0.07) / W, (y0 + ch - 0.06) / H, arm, ha="left", va="top", fontsize=FS.FS_TEXT + 0.5, fontweight="bold", color=FS.INK)
    fig.text((x0 + 0.07 + 0.22) / W, (y0 + ch - 0.07) / H, views, ha="left", va="top", fontsize=FS.FS_NOTE - 0.5, color=FS.MUTED)
    if role:
        fig.text((x0 + cw - 0.07) / W, (y0 + ch - 0.06) / H, role[0], ha="right", va="top", fontsize=FS.FS_NOTE, fontweight="bold", color=role[1])
    # two training views
    th = 0.52; tg = 0.09; tx = x0 + (cw - 2 * th - tg) / 2; ty = y0 + ch - 0.23 - th
    for k, (cls, smoothed) in enumerate((("genuine", gen_v), ("forged", fk_v))):
        ax = fig.add_axes([(tx + k * (th + tg)) / W, ty / H, th / W, th / H])
        ax.imshow(FACES[cls][1 if smoothed else 0], interpolation="lanczos"); FS.frame(ax, color=FS.MUTED, lw=0.4)
        if smoothed:
            chip(ax)
        fig.text((tx + k * (th + tg) + th / 2) / W, (ty - 0.02) / H, cls, ha="center", va="top", fontsize=FS.FS_NOTE - 0.5,
                 color=FS.REAL if cls == "genuine" else FS.FAKE)
    # bars
    bx0 = x0 + 0.40; bw_ = cw - 0.40 - 0.46; bh = 0.075; by1 = y0 + 0.235; by2 = y0 + 0.085
    fig.text((bx0 - 0.035) / W, (by1 + bh / 2) / H, "FA", ha="right", va="center", fontsize=FS.FS_NOTE - 0.5, color=FS.INK)
    fig.text((bx0 - 0.035) / W, (by2 + bh / 2) / H, "\u0394miss", ha="right", va="center", fontsize=FS.FS_NOTE - 0.5, color=FS.INK)
    fig.add_artist(plt.Rectangle((bx0 / W, by1 / H), bw_ / W, bh / H, transform=F, fc=FS.LIGHT, ec="none"))
    fig.add_artist(plt.Rectangle((bx0 / W, by1 / H), bw_ * fa / FA_MAX / W, bh / H, transform=F, fc=ACC, ec="none"))
    fig.text((bx0 + bw_ + 0.035) / W, (by1 + bh / 2) / H, f"{fa:.1f}%", ha="left", va="center", fontsize=FS.FS_NOTE, color=ACC,
             fontweight="bold" if arm == "P3" else "normal")
    z = bx0 + bw_ * (0 - DM_LO) / (DM_HI - DM_LO)
    fig.add_artist(plt.Rectangle((bx0 / W, by2 / H), bw_ / W, bh / H, transform=F, fc=FS.LIGHT, ec="none"))
    xa, xb = (z, z + bw_ * dm / (DM_HI - DM_LO)) if dm > 0 else (z + bw_ * dm / (DM_HI - DM_LO), z)
    fig.add_artist(plt.Rectangle((xa / W, by2 / H), (xb - xa) / W, bh / H, transform=F, fc=EVA if dm > 0 else ACC, ec="none"))
    fig.add_artist(plt.Line2D([z / W, z / W], [(by2 - 0.012) / H, (by2 + bh + 0.012) / H], transform=F, color=FS.INK, lw=0.6))
    fig.text((bx0 + bw_ + 0.035) / W, (by2 + bh / 2) / H, f"{dm:+.1f} pts".replace("-", "\u2212"), ha="left", va="center", fontsize=FS.FS_NOTE,
             color=EVA if dm > 0 else ACC, fontweight="bold" if arm == "P1" else "normal")

# grid headers
cx_all = LM + cw + GAP / 2
fig.text(cx_all / W, (H - 0.03) / H, "forged faces receive smoothed views", ha="center", va="top", fontsize=FS.FS_TEXT, fontweight="bold")
for c, lab in enumerate(("no", "yes")):
    fig.text((x_of(c) + cw / 2) / W, (H - TOP + 0.04) / H, lab, ha="center", va="bottom", fontsize=FS.FS_TEXT, color=FS.INK)
fig.text(0.04 / W, (y_of(1) + ch + GAP / 2) / H, "genuine faces receive smoothed views", ha="left", va="center", rotation=90,
         fontsize=FS.FS_TEXT, fontweight="bold")
for r, lab in enumerate(("no", "yes")):
    fig.text((LM - 0.05) / W, (y_of(r) + ch / 2) / H, lab, ha="right", va="center", fontsize=FS.FS_TEXT, color=FS.INK)
# footer: the two error directions as arrows
fy = 0.165; ax0 = LM + 0.02
for k, (col, text) in enumerate(((ACC, "accusation: smoothed genuine faces called forged"), (EVA, "escape: smoothed forgeries pass"))):
    yy = fy - k * 0.11
    fig.add_artist(FancyArrowPatch((ax0 / W, yy / H), ((ax0 + 0.16) / W, yy / H), transform=F, arrowstyle="-|>", mutation_scale=6, color=col, lw=1.2))
    fig.text((ax0 + 0.21) / W, yy / H, text, ha="left", va="center", fontsize=FS.FS_NOTE - 0.5, color=FS.INK)
FS.save(fig, OUT / "fig_exposure_v8b"); print("wrote", OUT / "fig_exposure_v8b.pdf")
