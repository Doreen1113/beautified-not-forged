"""fig_twoaxis_v8b (paper v8, 2026-10-22): both directions at once, column width (3.5 x 2.6 in). Restyled fig_twoaxis_v8.

x: Direction A, Smoothing-90 renders accused (%) at the threshold that accuses 5 % of the originals
   results/research/alipair_zeroshot_20260929/main_claim_A.json  rows[key].fa_s90_at_5pct, fa_ci
y: Direction B, beautification-only miss rise on Celeb-DF-B (points)
   results/research/celebdfb_v2_20260927/fair_cdfb.json  [key].d_miss_beauty_only, ci.d_miss_beauty_only
marker area: untreated Celeb-DF-B frame AUC (fair_cdfb.json [key].auc_untreated), same mapping as fig_twoaxis_v8.
Detectors and families: figstyle_v8b.DETECTORS. Labels are placed by adjustText (repelled from markers and each other), the
interval bars are drawn light so that the markers carry the figure; the two guide lines are labelled on the axes.

    python docs/paper_v2/make_fig_twoaxis_v8b.py  -> docs/paper_v2/figs/fig_twoaxis_v8b.{pdf,png}
"""
import json
import sys
from pathlib import Path

B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B / "docs/paper_v2"))
import figstyle as FS  # noqa: E402
import figstyle_v8b as V  # noqa: E402
FS.apply()
import matplotlib.pyplot as plt  # noqa: E402
from adjustText import adjust_text  # noqa: E402

OUT = B / "docs/paper_v2/figs"
A = json.loads((B / "results/research/alipair_zeroshot_20260929/main_claim_A.json").read_text(encoding="utf-8"))["rows"]
Bd = json.loads((B / "results/research/celebdfb_v2_20260927/fair_cdfb.json").read_text(encoding="utf-8"))
SHORT = {"EfficientNet-B4": "EffNet-B4", "Forensics Adapter": "Forensics Ad.", "Ours (seed 1)": "Ours s1", "Ours (seed 2)": "Ours s2"}

fig, ax = plt.subplots(figsize=(FS.COL, 2.6), layout="constrained")
# shaded "both low" corner and the two guide lines
ax.axvspan(-3, 5, color=FS.LIGHT, zorder=0, lw=0)
ax.axvline(5, color=FS.MUTED, lw=V.REF_LW, ls=V.REF_LS, zorder=1)
ax.axhline(0, color=FS.MUTED, lw=V.REF_LW, ls=V.REF_LS, zorder=1)
ax.text(5.8, 27.5, "5% FPR floor", color=FS.MUTED, fontsize=FS.FS_NOTE - 0.5, va="top", ha="left")
ax.text(26, -0.7, "no miss rise", color=FS.MUTED, fontsize=FS.FS_NOTE - 0.5, va="top", ha="center")
texts, fixed, pts_x, pts_y = [], [], [], []
for ka, kb, name, fam in V.DETECTORS:
    x = A[ka]["fa_s90_at_5pct"]; xlo, xhi = A[ka]["fa_ci"]
    y = Bd[kb]["d_miss_beauty_only"]; ylo, yhi = Bd[kb]["ci"]["d_miss_beauty_only"]; auc = Bd[kb]["auc_untreated"]
    size = 10 + 110 * max(auc - 0.5, 0) ** 1.5 * 2
    if fam == "ours":
        size *= 2.4
    ax.errorbar(x, y, xerr=[[x - xlo], [xhi - x]], yerr=[[y - ylo], [yhi - y]], fmt="none", ecolor=V.COLOR[fam], elinewidth=0.6,
                capsize=0, alpha=0.3, zorder=2)
    ax.scatter([x], [y], s=size, marker=V.MARK[fam], color=V.COLOR[fam], edgecolor="white", linewidth=0.4, zorder=4)
    lab = SHORT.get(name, name)
    if fam == "ours":   # placed by hand (below-right for seed 1, above-right for seed 2); the other labels are repelled from them
        fixed.append(ax.annotate(lab, (x, y), (6, -7) if "s1" in lab else (6, 6), textcoords="offset points", fontsize=FS.FS_NOTE,
                                 color=FS.OURS, fontweight="bold", ha="left", va="center", zorder=5))
        continue
    texts.append(ax.text(x, y, lab, fontsize=FS.FS_NOTE, color=FS.MUTED if fam == "cnn" else FS.INK, zorder=5))
    pts_x.append(x); pts_y.append(y)
ax.set_xlim(-3, 75); ax.set_ylim(-11, 28)
ax.set_xticks([0, 10, 20, 30, 40, 50, 60, 70]); ax.set_yticks([-10, 0, 10, 20])
ax.set_xlabel("Direction A: smoothed genuine faces accused (%)")
ax.set_ylabel("Direction B: beautified deepfakes,\nmiss rise (points)")
fig.canvas.draw()
adjust_text(texts, x=pts_x, y=pts_y, ax=ax, objects=fixed, expand=(1.25, 1.5), force_text=(0.4, 0.8), force_points=(0.3, 0.5),
            only_move={"points": "xy", "text": "xy"}, arrowprops=dict(arrowstyle="-", color=FS.GRID, lw=0.5, shrinkA=0, shrinkB=2),
            min_arrow_len=6, time_lim=5)
ax.legend(handles=V.legend_handles(), loc="lower right", fontsize=FS.FS_NOTE, handletextpad=0.3, borderpad=0.2, labelspacing=0.3)
FS.save(fig, OUT / "fig_twoaxis_v8b"); print("wrote", OUT / "fig_twoaxis_v8b.pdf")
