"""fig_dirs_v9 (paper v10, 2026-10-28): the two directions on seventeen published detectors and ours, one row per detector
(7.16 x 2.45 in). This is panels (b) and (c) of fig_teaser_v8b, unchanged in data and style, moved from Fig. 1 (now a
motivated example, make_fig_teaser_v9.py) to the results section.
(a) Direction A: share of the 2,210 Smoothing-90 renders accused at the threshold that accuses 5 % of the untouched
    originals, 95 % interval; grey number = share of pairs in which the render scores above its own original.
    results/research/alipair_zeroshot_20260929/main_claim_A.json rows[key].fa_s90_at_5pct, fa_ci, paired_up
(b) Direction B: beautification-only rise of the miss rate on Celeb-DF-B deepfakes, 95 % video-cluster interval.
    results/research/celebdfb_v2_20260927/fair_cdfb.json [key].d_miss_beauty_only, ci.d_miss_beauty_only
    python docs/paper_v2/make_fig_dirs_v9.py -> docs/paper_v2/figs/fig_dirs_v9.{pdf,png}
"""
import json
import sys
from pathlib import Path

import numpy as np

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

W, H = FS.FULL, 2.8
fig = plt.figure(figsize=(W, H))
AXB = 0.36                         # bottom of the dot panels (inches): room for ticks and the axis label

ytop = H - 0.5
ybot = AXB

# ------------------------------------------------------------------ (b) (c) dot panels -------------------------------------------
rows = []
for ka, kb, name, fam in V.DETECTORS:
    a = A[ka]; b = Bd[kb]
    rows.append(dict(name=name, fam=fam, fa=a["fa_s90_at_5pct"], fa_ci=a["fa_ci"], up=a["paired_up"], dm=b["d_miss_beauty_only"], dm_ci=b["ci"]["d_miss_beauty_only"]))
n = len(rows); ys = np.arange(n)[::-1]

PL, PW, PG = 1.05, 2.5, 0.95          # left of panel b, width of each panel, gap between b and c (inches)
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
V.tag(axb, "a", x=-0.3, y=1.1); V.tag(axc, "b", x=-0.06, y=1.1)
# family legend across the top right
fig.legend(handles=V.legend_handles(), loc="upper right", bbox_to_anchor=(0.995, 1.0), ncol=4, fontsize=FS.FS_NOTE,
           columnspacing=1.0, handletextpad=0.3, frameon=False, borderaxespad=0.1)
FS.save(fig, OUT / "fig_dirs_v9"); print("wrote", OUT / "fig_dirs_v9.pdf")
for r in rows:
    print(f"{r['name']:18s} A {r['fa']:5.1f} {r['fa_ci']}  B {r['dm']:+6.2f} {r['dm_ci']}")
