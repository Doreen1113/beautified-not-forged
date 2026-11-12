"""Bar chart for the poster: share of commercially smoothed genuine faces (Alibaba Smoothing-90) that each detector scores
as more fake than the same face's own untouched original. Source: docs/paper_v2/tables/tab_v4_retouch.tex, column
"above own original (%)" (same values as results/research/alipair_zeroshot_20260929/smoothing90_thresholdfree.json,
key paired_up). NPR is n/a in the table (scores saturated), so it is shown without a bar.

Run: python docs/capstone/src/make_retouch_chart.py [--en]  -> docs/capstone/img/retouch_paired[_en].svg / .png
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

OUT = Path(__file__).resolve().parents[1] / "img"; OUT.mkdir(exist_ok=True)
EN = "--en" in sys.argv
OURS_NAME = "Ours (three-way)" if EN else "我們（三類偵測器）"
for f in ("msjh.ttc", "msjhbd.ttc"):
    font_manager.fontManager.addfont(f"C:/Windows/Fonts/{f}")
plt.rcParams.update({"font.family": ["Microsoft JhengHei"], "svg.fonttype": "path"})

ROWS = [("SRM", 99.3), ("DFD-HR", 99.0), ("GenD", 98.5), ("F3Net", 97.8), ("SPSL", 97.3), ("CORE", 96.6), ("RECCE", 96.5),
        ("SBI", 96.2), ("Effort", 95.6), ("UCF", 95.4), ("Xception", 95.2), ("EfficientNet-B4", 93.7),
        ("Forensics Adapter", 93.3), ("UnivFD", 90.4), ("LAA-Net", 89.2), ("CADDM", 60.9), ("NPR", None),
        (OURS_NAME, 32.5)]
NAMED = {"DFD-HR", "GenD", "Effort", "Forensics Adapter", "CADDM", OURS_NAME}
INK, MUTED, GRID = "#1f2933", "#616e7c", "#e4e7eb"
PUB, OURS = "#9aa5b1", "#2f5fb3"

fig, ax = plt.subplots(figsize=(7.2, 7.4), dpi=200)
ys = list(range(len(ROWS)))[::-1]
for y, (name, v) in zip(ys, ROWS):
    ours = name == OURS_NAME
    if v is None:
        ax.text(1, y, "n/a (scores saturated)" if EN else "n/a（分數飽和）", va="center", ha="left", fontsize=12, color=MUTED)
    else:
        ax.barh(y, v, height=0.68, color=OURS if ours else PUB, edgecolor="white", linewidth=1.0)
        if name in NAMED:
            ax.text(v + 1.2, y, f"{v:.1f}", va="center", ha="left", fontsize=13, color=INK, fontweight="normal")
ax.set_yticks(ys)
ax.set_yticklabels([n for n, _ in ROWS], fontsize=13, color=INK)
for lab in ax.get_yticklabels():
    if lab.get_text() in NAMED:
        lab.set_fontweight("bold")
ax.set_xlim(0, 108); ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xticklabels(["0", "25", "50", "75", "100%"], fontsize=12, color=MUTED)
ax.axvline(50, color=MUTED, lw=1, ls=(0, (3, 3)))
ax.text(50.6, len(ROWS) - 0.35, "50%: no difference from the original" if EN else "50%：與原圖無差別", fontsize=11.5, color=MUTED, va="bottom")
ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID); ax.tick_params(length=0)
ax.set_ylim(-0.7, len(ROWS) - 0.1)
fig.tight_layout()
stem = "retouch_paired_en" if EN else "retouch_paired"
fig.savefig(OUT / f"{stem}.svg", facecolor="white")
fig.savefig(OUT / f"{stem}.png", facecolor="white")
print("ok")
