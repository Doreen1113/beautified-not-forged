"""fig_exposure_v10 (paper v10, 2026-10-28): the 2 x 2 training-exposure design without thumbnails (REVIEW_V9 D5-4: the
smoothed thumbnails were not visibly smoother at print size). Column width, 3.5 x 2.55 in. Same numbers and sources as
fig_exposure_v8b (p3_readout40.json [arm].smoothing90_at_5fpr[0] and [arm].miss_rise[2][0], first seed, cross-checked against
smooth_evasion2.json). Each cell: the arm, which class receives smoothed views (two chips), and two bars:
  FA     Smoothing-90 renders accused at the threshold that accuses 5 % of their originals
  dMISS  change of the miss rate on Celeb-DF-v2 forgeries under strong whole-crop smoothing (bilateral d21), same rule
Colours: FS.FAKE = accusation direction (FA, and a negative dMISS), amber = escape direction (a positive dMISS).

    python docs/paper_v2/make_fig_exposure_v10.py  -> docs/paper_v2/figs/fig_exposure_v10.{pdf,png}
"""
import json
import sys
from pathlib import Path

B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B / "docs/paper_v2"))
import figstyle as FS  # noqa: E402
FS.apply()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch  # noqa: E402

OUT = B / "docs/paper_v2/figs"; RU = B / "results/research/retouch_unified_20260929"
ACC = FS.FAKE; EVA = "#C98A00"; VIEW = FS.OURS_ARM
p3 = json.loads((RU / "p3_readout40.json").read_text(encoding="utf-8"))
ev = json.loads((RU / "smooth_evasion2.json").read_text(encoding="utf-8"))
TAG = {"P0": "clipe5fbp0_s20260929", "P1": "clipe5fbp1_s20260929", "P2": "clipe5fb_s20260929", "P3": "clipe5fbp3_s20260929"}
CELLS = {"P0": (0, 0, "neither class"), "P3": (1, 0, "forged only"), "P1": (0, 1, "genuine only"), "P2": (1, 1, "both classes")}
NUM = {}
for arm in CELLS:
    fa = p3[arm]["smoothing90_at_5fpr"][0]; dm = p3[arm]["miss_rise"][2][0]
    assert abs(dm - ev[TAG[arm]]["miss_rise"][2][0]) < 1e-9, arm
    NUM[arm] = (fa, dm); print(arm, f"FA {fa:.1f}  dMISS {dm:+.1f}")

W, H = FS.COL, 2.72
fig = plt.figure(figsize=(W, H)); F = fig.transFigure
LM, TOP, GAP, FOOT, RM = 0.40, 0.32, 0.07, 0.30, 0.03
cw = (W - LM - GAP - RM) / 2; ch = (H - TOP - GAP - FOOT) / 2
x_of = lambda c: LM + c * (cw + GAP); y_of = lambda r: H - TOP - (r + 1) * ch - r * GAP
FA_MAX = 70.0; DM_LO, DM_HI = -45.0, 55.0


def chipbox(x, y, w, h, text, on):
    fig.add_artist(FancyBboxPatch((x / W, y / H), w / W, h / H, boxstyle="round,pad=0,rounding_size=0.03", transform=F,
                                  fc=VIEW if on else "white", ec=VIEW if on else FS.GRID, lw=0.6))
    fig.text((x + w / 2) / W, (y + h / 2) / H, text, ha="center", va="center", fontsize=FS.FS_NOTE - 0.8,
             color="white" if on else FS.MUTED, fontweight="bold" if on else "normal")


for arm, (c, r, views) in CELLS.items():
    x0, y0 = x_of(c), y_of(r); fa, dm = NUM[arm]
    gen_v, fk_v = (r == 1), (c == 1)
    role = {"P1": ("escape", EVA), "P3": ("accusation", ACC)}.get(arm)
    fig.add_artist(FancyBboxPatch((x0 / W, y0 / H), cw / W, ch / H, boxstyle="round,pad=0,rounding_size=0.015", transform=F,
                                  fc="white", ec=role[1] if role else FS.GRID, lw=1.0 if role else 0.6, zorder=-1))
    fig.text((x0 + 0.07) / W, (y0 + ch - 0.06) / H, arm, ha="left", va="top", fontsize=FS.FS_TEXT + 0.5, fontweight="bold", color=FS.INK)
    fig.text((x0 + 0.07 + 0.24) / W, (y0 + ch - 0.07) / H, views, ha="left", va="top", fontsize=FS.FS_NOTE - 0.5, color=FS.MUTED)
    if role:
        fig.text((x0 + cw - 0.07) / W, (y0 + ch - 0.06) / H, role[0], ha="right", va="top", fontsize=FS.FS_NOTE, fontweight="bold", color=role[1])
    # the two training views as chips: class name, then "smoothed" or "clean"
    cy = y0 + ch - 0.53; chw = (cw - 0.14 - 0.06) / 2; chh = 0.17
    for k, (cls, on) in enumerate((("genuine", gen_v), ("forged", fk_v))):
        cx = x0 + 0.07 + k * (chw + 0.06)
        fig.text((cx + chw / 2) / W, (cy + chh + 0.025) / H, cls, ha="center", va="bottom", fontsize=FS.FS_NOTE - 0.5,
                 color=FS.REAL if cls == "genuine" else FS.FAKE)
        chipbox(cx, cy, chw, chh, "smoothed views" if on else "clean only", on)
    # bars
    bx0 = x0 + 0.40; bw_ = cw - 0.40 - 0.48; bh = 0.10; by1 = y0 + 0.30; by2 = y0 + 0.10
    fig.text((bx0 - 0.035) / W, (by1 + bh / 2) / H, "FA", ha="right", va="center", fontsize=FS.FS_NOTE - 0.3, color=FS.INK)
    fig.text((bx0 - 0.035) / W, (by2 + bh / 2) / H, "\u0394miss", ha="right", va="center", fontsize=FS.FS_NOTE - 0.3, color=FS.INK)
    fig.add_artist(plt.Rectangle((bx0 / W, by1 / H), bw_ / W, bh / H, transform=F, fc=FS.LIGHT, ec="none"))
    fig.add_artist(plt.Rectangle((bx0 / W, by1 / H), bw_ * fa / FA_MAX / W, bh / H, transform=F, fc=ACC, ec="none"))
    fig.text((bx0 + bw_ + 0.035) / W, (by1 + bh / 2) / H, f"{fa:.1f}%", ha="left", va="center", fontsize=FS.FS_NOTE, color=ACC,
             fontweight="bold" if arm == "P3" else "normal")
    z = bx0 + bw_ * (0 - DM_LO) / (DM_HI - DM_LO)
    fig.add_artist(plt.Rectangle((bx0 / W, by2 / H), bw_ / W, bh / H, transform=F, fc=FS.LIGHT, ec="none"))
    xa, xb = (z, z + bw_ * dm / (DM_HI - DM_LO)) if dm > 0 else (z + bw_ * dm / (DM_HI - DM_LO), z)
    fig.add_artist(plt.Rectangle((xa / W, by2 / H), (xb - xa) / W, bh / H, transform=F, fc=EVA if dm > 0 else ACC, ec="none"))
    fig.add_artist(plt.Line2D([z / W, z / W], [(by2 - 0.015) / H, (by2 + bh + 0.015) / H], transform=F, color=FS.INK, lw=0.6))
    fig.text((bx0 + bw_ + 0.035) / W, (by2 + bh / 2) / H, f"{dm:+.1f} pts".replace("-", "\u2212"), ha="left", va="center",
             fontsize=FS.FS_NOTE, color=EVA if dm > 0 else ACC, fontweight="bold" if arm == "P1" else "normal")

cx_all = LM + cw + GAP / 2
fig.text(cx_all / W, (H - 0.03) / H, "forged faces receive smoothed views", ha="center", va="top", fontsize=FS.FS_TEXT, fontweight="bold")
for c, lab in enumerate(("no", "yes")):
    fig.text((x_of(c) + cw / 2) / W, (H - TOP + 0.04) / H, lab, ha="center", va="bottom", fontsize=FS.FS_TEXT, color=FS.INK)
fig.text(0.04 / W, (y_of(1) + ch + GAP / 2) / H, "genuine faces receive smoothed views", ha="left", va="center", rotation=90,
         fontsize=FS.FS_TEXT, fontweight="bold")
for r, lab in enumerate(("no", "yes")):
    fig.text((LM - 0.05) / W, (y_of(r) + ch / 2) / H, lab, ha="right", va="center", fontsize=FS.FS_TEXT, color=FS.INK)
fy = 0.19; ax0 = LM + 0.02
for k, (col, text) in enumerate(((ACC, "accusation: smoothed genuine faces called forged (FA; \u0394miss < 0)"),
                                 (EVA, "escape: smoothed forgeries pass (\u0394miss > 0)"))):
    yy = fy - k * 0.12
    fig.add_artist(FancyArrowPatch((ax0 / W, yy / H), ((ax0 + 0.16) / W, yy / H), transform=F, arrowstyle="-|>", mutation_scale=6, color=col, lw=1.2))
    fig.text((ax0 + 0.21) / W, yy / H, text, ha="left", va="center", fontsize=FS.FS_NOTE - 0.5, color=FS.INK)
FS.save(fig, OUT / "fig_exposure_v10"); print("wrote", OUT / "fig_exposure_v10.pdf")
