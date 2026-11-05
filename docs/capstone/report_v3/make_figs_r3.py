"""Report figures, round 3 (2026-10-29). Every figure is drawn at its print width (text width 14.66 cm = 5.77 in) with
Times New Roman at 9-10 pt, so nothing is scaled down after drawing. Outputs in figs/:
  fig_perop.pdf      accusation per retouching operation and level, ours vs five published detectors (published_ali.json)
  fig_exposure_r3.pdf the four training-exposure arms as two bar panels (p3_readout40.json)
  fig_output_a.png / fig_output_b.png  the browser page's result card, cropped from the 1366 px headless screenshots
python make_figs_r3.py"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image

B = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent; OUT = HERE / "figs"
RU = B / "results/research/retouch_unified_20260929"
W = 5.77                                   # print width in inches (A4, 3.17 cm side margins)
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 10, "axes.labelsize": 10, "xtick.labelsize": 9,
                     "ytick.labelsize": 9, "legend.fontsize": 9, "axes.linewidth": 0.6, "pdf.fonttype": 42,
                     "axes.spines.top": False, "axes.spines.right": False})
INK, MUTED, GRID = "#222222", "#6B6B6B", "#E5E5E5"
OURS, CLIP, CNN, ACC, EVA = "#0F4D92", "#CC79A7", "#8C8C8C", "#D55E00", "#C98A00"


def per_operation():
    d = json.loads((B / "results/research/alipair_zeroshot_20260929/published_ali.json").read_text(encoding="utf-8"))
    ops = [("EyeEnlarging", "Eye enlarging"), ("FaceLifting", "Face slimming"), ("Whitening", "Whitening"), ("Smoothing", "Skin smoothing")]
    series = [("xception", "Xception", CNN, "-", "o"), ("sbi", "SBI", CNN, "--", "s"), ("univfd", "UnivFD", CLIP, ":", "^"),
              ("effort", "Effort", CLIP, "-", "D"), ("fadapter", "Forensics Adapter", CLIP, "--", "v"),
              ("ours main", "Ours (seed 1)", OURS, "-", "*"), ("ours main s2", "Ours (seed 2)", OURS, "--", "*")]
    fig, axes = plt.subplots(1, 4, figsize=(W, 2.35), sharey=True)
    for ax, (key, title) in zip(axes, ops):
        for name, label, c, ls, m in series:
            y = [d[name]["by_op"][f"{key}_{lv}"]["fake_at_t"] for lv in (30, 60, 90)]
            ours = name.startswith("ours")
            ax.plot([30, 60, 90], y, ls=ls, color=c, marker=m, ms=7 if ours else 4.5, lw=1.8 if ours else 1.0,
                    zorder=5 if ours else 3, label=label)
        ax.axhline(5, color=MUTED, lw=0.7, ls=(0, (3, 2)))
        ax.set_title(title, fontsize=10, pad=4)
        ax.set_xticks([30, 60, 90]); ax.set_xlim(22, 98); ax.set_ylim(0, 56)
        ax.grid(axis="y", color=GRID, lw=0.5); ax.set_axisbelow(True)
        ax.set_xlabel("strength", labelpad=2)
    axes[0].set_ylabel("accused at 5% FPR (%)")
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="upper center", ncol=4, frameon=False, bbox_to_anchor=(0.5, 1.02), handlelength=2.2, columnspacing=1.2)
    fig.subplots_adjust(left=0.085, right=0.99, bottom=0.2, top=0.68, wspace=0.12)
    fig.savefig(OUT / "fig_perop.pdf"); fig.savefig(OUT / "fig_perop.png", dpi=200); plt.close(fig)


def exposure():
    p = json.loads((RU / "p3_readout40.json").read_text(encoding="utf-8"))
    arms = [("P0", "neither", "–", "–"), ("P3", "forged only", "–", "smoothed"), ("P1", "genuine only", "smoothed", "–"),
            ("P2", "both", "smoothed", "smoothed")]
    fa = [p[a]["smoothing90_at_5fpr"] for a, *_ in arms]           # [value, lo, hi]
    dm = [p[a]["miss_rise"][2] for a, *_ in arms]                   # strongest smoothing: [value, lo, hi]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(W, 2.6))
    x = range(4)
    for ax, vals, title, ylab, floor in ((a1, fa, "Accusation of Smoothing-90 renders", "accused at 5% FPR (%)", 5),
                                         (a2, dm, "Escape of smoothed forgeries", "miss rise (points)", 0)):
        v = [t[0] for t in vals]; lo = [t[0] - t[1] for t in vals]; hi = [t[2] - t[0] for t in vals]
        cols = [ACC if (ax is a1 and t[0] > 15) or (ax is a2 and t[0] < -5) else (EVA if ax is a2 and t[0] > 5 else CNN) for t in vals]
        ax.bar(x, v, color=cols, width=0.62, zorder=3)
        ax.errorbar(x, v, yerr=[lo, hi], fmt="none", ecolor=INK, elinewidth=0.8, capsize=2.5, zorder=4)
        for i, t in enumerate(vals):
            # value label: above the interval for a positive bar, just above the zero line for a negative bar
            yy = (t[2] + (1.5 if ax is a1 else 2.0)) if t[0] >= 0 else 2.0
            ax.text(i, yy, f"{t[0]:+.1f}" if ax is a2 else f"{t[0]:.1f}", ha="center", va="bottom", fontsize=9, color=INK)
        ax.axhline(floor, color=MUTED, lw=0.7, ls=(0, (3, 2)))
        ax.set_title(title, fontsize=10, pad=4); ax.set_ylabel(ylab, fontsize=9)
        ax.set_xticks(list(x)); ax.set_xticklabels([a for a, *_ in arms], fontsize=10, fontweight="bold")
        ax.grid(axis="y", color=GRID, lw=0.5); ax.set_axisbelow(True)
        for i, (_, _, g, f) in enumerate(arms):
            ax.text(i, -0.19, g, transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=8, color=INK if g != "–" else MUTED)
            ax.text(i, -0.30, f, transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=8, color=INK if f != "–" else MUTED)
        ax.text(-0.62, -0.19, "genuine:", transform=ax.get_xaxis_transform(), ha="right", va="top", fontsize=8, color=MUTED)
        ax.text(-0.62, -0.30, "forged:", transform=ax.get_xaxis_transform(), ha="right", va="top", fontsize=8, color=MUTED)
        ax.set_xlim(-0.6, 3.6)
    a1.set_ylim(0, 75)
    a2.set_ylim(-52, 68)
    fig.subplots_adjust(left=0.13, right=0.99, bottom=0.27, top=0.9, wspace=0.45)
    fig.savefig(OUT / "fig_exposure_r3.pdf"); fig.savefig(OUT / "fig_exposure_r3.png", dpi=200); plt.close(fig)


def crops():
    S = B / "docs/demo_ru/test/screens"
    # the result card at a 1366 px viewport; bottom cut just above the question chips (a) / the help paragraph (b)
    for src, dst, box in (("1366_example2_full.png", "fig_output_a.png", (178, 536, 1187, 1160)),
                          ("1366_example3_full.png", "fig_output_b.png", (178, 536, 1187, 1187))):
        im = Image.open(S / src).convert("RGB").crop(box); im.save(OUT / dst, optimize=True); print(dst, im.size)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True); per_operation(); exposure(); crops(); print("done")
