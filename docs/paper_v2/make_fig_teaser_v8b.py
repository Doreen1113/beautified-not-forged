"""fig_teaser_v8b (paper v8, 2026-10-22): Fig. 1, the two directions of the measurement in one picture (7.16 x 2.5 in).

(a) three genuine FFHQ faces and their renders by the commercial retouching service (Smoothing-90): the same crops as
    fig_teaser_v7 (stems 17001-17003 = first three present in both folders; central 640 x 640 crop of the aligned 1024 image).
    ffhq_originals/Part2/<stem>.png and FFHQ_ali_process/Smoothing_90/<index // 1000 * 1000>/<stem>.png.
(b) Direction A, one row per detector: share of the 2,210 Smoothing-90 renders accused at the threshold that accuses 5 % of
    the untouched originals, with its 95 % interval; the grey number at the right edge is the threshold-free companion, the
    share of pairs in which the render scores above its own original.
    results/research/alipair_zeroshot_20260929/main_claim_A.json  rows[key].fa_s90_at_5pct, fa_ci, paired_up  (main_claim_A.py)
(c) Direction B, same rows: beautification-only rise of the miss rate on Celeb-DF-B deepfakes (app presets, re-encoding
    subtracted), with its 95 % video-cluster interval.
    results/research/celebdfb_v2_20260927/fair_cdfb.json  [key].d_miss_beauty_only, ci.d_miss_beauty_only  (fair_cdfb.py)
Rows: the registry figstyle_v8b.DETECTORS (paper order; families colour-coded, ours in the house blue). NPR's Direction A is
0.0 because its scores saturate at 1.0 on this source (the paper lists it as n/a); the figure keeps the row and marks it.

    python docs/paper_v2/make_fig_teaser_v8b.py  -> docs/paper_v2/figs/fig_teaser_v8b.{pdf,png}
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B / "docs/paper_v2"))
import figstyle as FS  # noqa: E402
import figstyle_v8b as V  # noqa: E402
FS.apply()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402

OUT = B / "docs/paper_v2/figs"
A = json.loads((B / "results/research/alipair_zeroshot_20260929/main_claim_A.json").read_text(encoding="utf-8"))["rows"]
Bd = json.loads((B / "results/research/celebdfb_v2_20260927/fair_cdfb.json").read_text(encoding="utf-8"))
STEMS = ["17001", "17002", "17003"]

W, H = FS.FULL, 2.75
fig = plt.figure(figsize=(W, H))
AXB = 0.36                         # bottom of the dot panels (inches): room for ticks and the axis label

# ------------------------------------------------------------------ (a) image pairs ---------------------------------------------
gap, vgap = 0.05, 0.05
x0, ytop = 0.2, H - 0.5
tw = (ytop - AXB - 2 * vgap) / 3        # tile side: the image block ends where the dot panels end
for r, st in enumerate(STEMS):
    o = np.array(Image.open(B / "ffhq_originals/Part2" / f"{st}.png").convert("RGB"))[200:840, 192:832]
    s = np.array(Image.open(B / "FFHQ_ali_process/Smoothing_90" / f"{int(st) // 1000 * 1000}" / f"{st}.png").convert("RGB"))[200:840, 192:832]
    y = ytop - (r + 1) * tw - r * vgap
    for c, im in enumerate((o, s)):
        ax = fig.add_axes([(x0 + c * (tw + gap)) / W, y / H, tw / W, tw / H])
        ax.imshow(im, interpolation="lanczos"); FS.frame(ax, color=FS.MUTED, lw=0.4)
for c, lab in enumerate(("original", "smoothed")):
    fig.text((x0 + c * (tw + gap) + tw / 2) / W, (ytop + 0.04) / H, lab, ha="center", va="bottom", fontsize=FS.FS_TEXT, color=FS.INK)
fig.text((x0 + tw + gap / 2) / W, (ytop + 0.2) / H, "genuine faces, retouching service", ha="center", va="bottom",
         fontsize=FS.FS_TEXT, color=FS.MUTED)
fig.add_artist(FancyArrowPatch(((x0 + tw - 0.03) / W, (ytop + 0.085) / H), ((x0 + tw + gap + 0.03) / W, (ytop + 0.085) / H),
                               transform=fig.transFigure, arrowstyle="-|>", mutation_scale=5, color=FS.MUTED, lw=0.6))
V.fig_tag(fig, "a", 0.04, H - 0.2)
ybot = AXB

# ------------------------------------------------------------------ (b) (c) dot panels -------------------------------------------
rows = []
for ka, kb, name, fam in V.DETECTORS:
    a = A[ka]; b = Bd[kb]
    rows.append(dict(name=name, fam=fam, fa=a["fa_s90_at_5pct"], fa_ci=a["fa_ci"], up=a["paired_up"], dm=b["d_miss_beauty_only"], dm_ci=b["ci"]["d_miss_beauty_only"]))
n = len(rows); ys = np.arange(n)[::-1]

PL, PW, PG = 2.75, 1.78, 0.56          # left of panel b, width of each panel, gap between b and c (inches)
axb = fig.add_axes([PL / W, ybot / H, PW / W, (ytop - ybot) / H])
axc = fig.add_axes([(PL + PW + PG) / W, ybot / H, PW / W, (ytop - ybot) / H])
for ax, key, ci, xlim, ticks, xlab, ref, reflab in (
        (axb, "fa", "fa_ci", (-3, 76), [0, 25, 50, 75], "smoothed genuine faces accused (%)", 5, "5% FPR floor"),
        (axc, "dm", "dm_ci", (-11, 27), [-10, 0, 10, 20], "beautified deepfakes: miss rise (points)", 0, "no change")):
    # family bands behind the rows
    fam_prev = None
    for i, r in enumerate(rows):
        if fam_prev is not None and r["fam"] != fam_prev:
            ax.axhline(ys[i] + 0.5, color=FS.GRID, lw=0.5, zorder=0)
        fam_prev = r["fam"]
    ax.axvline(ref, color=FS.MUTED, lw=V.REF_LW, ls=V.REF_LS, zorder=0)
    ax.text(ref, n - 0.35, reflab, ha="center", va="bottom", fontsize=FS.FS_NOTE - 0.5, color=FS.MUTED)
    for i, r in enumerate(rows):
        c = V.COLOR[r["fam"]]; lo, hi = r[ci]; v = r[key]
        ax.plot([lo, hi], [ys[i], ys[i]], color=c, lw=0.8 if r["fam"] != "ours" else 1.1, alpha=0.55, solid_capstyle="butt", zorder=2)
        ax.plot(v, ys[i], marker=V.MARK[r["fam"]], ms=3.4 if r["fam"] != "ours" else 6.5, color=c, mec="white", mew=0.4, ls="", zorder=3)
    ax.set_xlim(*xlim); ax.set_ylim(-0.7, n - 0.3); ax.set_xticks(ticks)
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    ax.set_xlabel(xlab, labelpad=2)
    ax.tick_params(axis="x", labelsize=FS.FS_TICK)
# row names once, on the left of (b); ours in bold blue
for i, r in enumerate(rows):
    axb.text(-0.03, ys[i], r["name"], transform=axb.get_yaxis_transform(), ha="right", va="center", fontsize=FS.FS_NOTE + 0.3,
             color=FS.OURS if r["fam"] == "ours" else FS.INK, fontweight="bold" if r["fam"] == "ours" else "normal")
# threshold-free companion of (b): share of pairs in which the render scores above its own original (main_claim_A paired_up)
for i, r in enumerate(rows):
    axb.text(1.04, ys[i], f"{r['up']:.0f}%", transform=axb.get_yaxis_transform(), ha="left", va="center", fontsize=FS.FS_NOTE,
             color=FS.OURS if r["fam"] == "ours" else FS.MUTED, fontweight="bold" if r["fam"] == "ours" else "normal")
axb.text(1.04, n - 0.35, "above\nown", transform=axb.get_yaxis_transform(), ha="left", va="bottom", fontsize=FS.FS_NOTE - 0.5, color=FS.MUTED, linespacing=0.95)
# NPR saturates: say so at its row in (b)
i_npr = [r["name"] for r in rows].index("NPR")
axb.text(4.5, ys[i_npr], "scores saturate (n/a)", ha="left", va="center", fontsize=FS.FS_NOTE - 1, color=FS.MUTED)
# direction headers and panel tags
axb.set_title("Direction A: accusation", loc="left", fontsize=FS.FS_TEXT, fontweight="bold", pad=10, color=FS.INK)
axc.set_title("Direction B: escape", loc="left", fontsize=FS.FS_TEXT, fontweight="bold", pad=10, color=FS.INK)
V.tag(axb, "b", x=-0.33, y=1.1); V.tag(axc, "c", x=-0.06, y=1.1)
# family legend across the top right
fig.legend(handles=V.legend_handles(), loc="upper right", bbox_to_anchor=(0.995, 1.0), ncol=4, fontsize=FS.FS_NOTE,
           columnspacing=1.0, handletextpad=0.3, frameon=False, borderaxespad=0.1)
FS.save(fig, OUT / "fig_teaser_v8b"); print("wrote", OUT / "fig_teaser_v8b.pdf")
for r in rows:
    print(f"{r['name']:18s} A {r['fa']:5.1f} {r['fa_ci']}  B {r['dm']:+6.2f} {r['dm_ci']}")
