"""Poster figures, drawn at their printed size (inches) so every label is a real point size on the 90 x 120 cm sheet.
One style for all figures: Arial (figure text) on a transparent background, class colours real / beautified / forged = green / amber / red, ours = blue, published = grey.
Numbers: docs/capstone/report_v3/report.tex (line numbers in the comments); teaser outputs of our model: assets/teaser_model.json
(run_teaser_model.py). Writes assets/figs2/*.png at 300 dpi.
python docs/capstone/poster/make_figs.py [teaser exposure method auc scatter unseen evidence]"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402
from PIL import Image  # noqa: E402

H = Path(__file__).resolve().parent; A = H / "assets"; OUT = A / "figs2"; OUT.mkdir(parents=True, exist_ok=True)
R3 = H.parent / "report_v3/figs"; TL = A / "tiles"
plt.rcParams.update({"font.family": "Arial", "font.size": 22, "axes.edgecolor": "#333", "axes.linewidth": 1.6,
                     "xtick.labelsize": 21, "ytick.labelsize": 21, "xtick.major.width": 1.5, "ytick.major.width": 1.5,
                     "xtick.major.size": 6, "ytick.major.size": 6, "axes.spines.top": False, "axes.spines.right": False,
                     "svg.fonttype": "none"})
INK, MUTED, GREEN, AMBER, RED, BLUE, GREY, SLATE, LIGHT = "#1a1a1a", "#5a6270", "#0a8f68", "#b8860b", "#c8521a", "#1d4f91", "#aab2bd", "#6a7d9c", "#eef2f7"
CLS = {"real": GREEN, "beautified": AMBER, "forged": RED}


class Canvas:
    """A figure in inches: add images, axes, text and arrows at inch coordinates (origin bottom left)."""
    def __init__(self, w, h):
        self.w, self.h = w, h; self.fig = plt.figure(figsize=(w, h))

    def box(self, x, y, w, h):
        return [x / self.w, y / self.h, w / self.w, h / self.h]

    def img(self, path, x, y, w, h, border=None, lw=5):
        ax = self.fig.add_axes(self.box(x, y, w, h)); im = Image.open(path).convert("RGB")
        ax.imshow(np.asarray(im), interpolation="lanczos", aspect="auto"); ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_visible(border is not None); s.set_color(border or "none"); s.set_linewidth(lw)
        return ax

    def ax(self, x, y, w, h):
        return self.fig.add_axes(self.box(x, y, w, h))

    def text(self, x, y, s, **k):
        k.setdefault("color", INK); k.setdefault("fontsize", 22)
        return self.fig.text(x / self.w, y / self.h, s, **k)

    def arrow(self, x1, y1, x2, y2, color=INK, lw=3.5, ms=34):
        self.fig.patches.append(FancyArrowPatch((x1 / self.w, y1 / self.h), (x2 / self.w, y2 / self.h), transform=self.fig.transFigure,
                                                arrowstyle="-|>", mutation_scale=ms, lw=lw, color=color, shrinkA=0, shrinkB=0))

    def rbox(self, x, y, w, h, fc=LIGHT, ec="#b9c4d4", lw=2.0, r=0.12):
        self.fig.patches.append(FancyBboxPatch((x / self.w, y / self.h), w / self.w, h / self.h, transform=self.fig.transFigure,
                                               boxstyle=f"round,pad=0,rounding_size={r / self.h}", fc=fc, ec=ec, lw=lw))

    def save(self, name):
        self.fig.savefig(OUT / f"{name}.png", dpi=300, transparent=True); plt.close(self.fig); print("wrote", name)


# ======================================================================================= Fig. 1 teaser
def teaser():
    tm = json.loads((A / "teaser_model.json").read_text())
    # published detectors on the same images: report.tex L54-67 (figs/fig_teaser.html): (name, before, after, threshold)
    rows = [("(a)  A genuine photo after commercial skin smoothing", "hero_orig", "hero_smooth", "genuine", "smoothed",
             [("Effort", .11, .72, .66), ("Forensics Ad.", .17, .95, .59), ("GenD", .19, .97, .84), ("DFD-HR", .27, .94, .54)],
             "4 of 4 call it fake: false alarm", tm["genuine_smoothed"]),
            ("(b)  A face swap after an app beauty preset", "hero_swap", "hero_swap_beauty", "face swap", "beautified",
             [("Effort", .97, .44, .81), ("Forensics Ad.", 1.00, .67, .85), ("GenD", .89, .70, .86), ("DFD-HR", .99, .74, .63)],
             "3 of 4 call it real: missed", tm["swap_beautified"])]
    c = Canvas(15.9, 7.3); s = 2.2
    for r, (head, a, b, la, lb, dets, verdict, ours) in enumerate(rows):
        yt = 7.3 - r * 3.7
        c.text(0, yt - 0.36, head, fontsize=25, fontweight="bold")
        y0 = yt - 0.72 - s
        tagc = GREEN if r == 0 else RED
        c.img(A / f"{a}.png", 0, y0, s, s, border=tagc); c.img(A / f"{b}.png", 3.0, y0, s, s, border=tagc)
        c.arrow(2.32, y0 + s / 2, 2.88, y0 + s / 2)
        c.text(s / 2, y0 - 0.33, la, ha="center", fontsize=21, fontweight="bold", color=tagc)
        c.text(3.0 + s / 2, y0 - 0.33, lb, ha="center", fontsize=20, color=MUTED)
        # published detectors: before (open) -> after (filled), tick = own threshold
        ax = c.ax(7.15, y0 + 0.5, 3.95, s - 0.95); n = len(dets)
        for i, (nm, bef, aft, thr) in enumerate(dets):
            yy = n - 1 - i; col = RED if aft > thr else GREEN
            ax.plot([0, 1], [yy, yy], color="#dfe3ea", lw=6, solid_capstyle="round", zorder=1)
            ax.plot([thr, thr], [yy - 0.32, yy + 0.32], color=INK, lw=3.2, zorder=2)
            ax.annotate("", xy=(aft, yy), xytext=(bef, yy), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=2.2, mutation_scale=22,
                                                                         shrinkA=9, shrinkB=11), zorder=3)
            ax.scatter([bef], [yy], s=230, facecolor="white", edgecolor=MUTED, linewidth=2.4, zorder=4)
            ax.scatter([aft], [yy], s=300, color=col, zorder=5)
        ax.set_yticks(range(n)); ax.set_yticklabels([d[0] for d in dets][::-1], fontsize=20)
        ax.set_xlim(-0.04, 1.04); ax.set_ylim(-0.6, n - 0.4); ax.set_xticks([0, 0.5, 1]); ax.tick_params(axis="x", labelsize=18)
        ax.spines["left"].set_visible(False); ax.tick_params(axis="y", length=0)
        c.text(5.55, yt - 0.98, "Published detectors (tick = own threshold)", fontsize=19, fontweight="bold", color=MUTED)
        c.text(5.55, y0 - 0.33, verdict, fontsize=20, fontweight="bold", color=RED)
        # ours on the after image: three-way probabilities from the model
        p = dict(zip(["real", "forged", "beautified"], ours["p"])); lab = ours["label"]
        ax2 = c.ax(13.05, y0 + 0.4, 2.2, s - 0.95)
        names = ["real", "forged", "beautified"]
        for i, k in enumerate(names):
            yy = 2 - i; on = k == lab
            ax2.barh(yy, p[k], height=0.62, color=CLS[k] if on else "#d6dbe2")
            ax2.text(p[k] + 0.04, yy, f"{p[k]:.2f}", va="center", fontsize=19, fontweight="bold" if on else "normal", color=CLS[k] if on else MUTED)
        ax2.set_yticks([2, 1, 0]); ax2.set_yticklabels(names, fontsize=20); ax2.set_xlim(0, 1.3); ax2.set_xticks([])
        ax2.spines["bottom"].set_visible(False); ax2.spines["left"].set_visible(False); ax2.tick_params(axis="y", length=0)
        for t, k in zip(ax2.get_yticklabels(), names):
            t.set_color(CLS[k] if k == lab else MUTED); t.set_fontweight("bold" if k == lab else "normal")
        c.text(11.75, yt - 0.98, "Ours", fontsize=21, fontweight="bold", color=BLUE)
        c.text(11.75, y0 - 0.33, f"{lab}: correct", fontsize=20, fontweight="bold", color=CLS[lab])
    c.save("fig1_teaser")


# ======================================================================================= Fig. 2 training exposure
def exposure():
    # report.tex Table exposure (seed 1): accused %, miss rise (points)
    arms = ["none", "forged\nonly", "genuine\nonly", "both"]; acc = [54.2, 63.8, 3.7, 11.7]; miss = [-16.0, -38.5, 51.2, -26.5]
    cols = [GREY, GREY, GREY, BLUE]
    c = Canvas(15.9, 4.6)
    a1 = c.ax(1.05, 1.15, 6.3, 2.75); a2 = c.ax(9.35, 1.15, 6.3, 2.75)
    for ax, v, ttl, lim in ((a1, acc, "Smoothed genuine faces called forged (%)", (0, 75)), (a2, miss, "Smoothed deepfakes: change in misses (points)", (-62, 66))):
        b = ax.bar(range(4), v, width=0.6, color=cols)
        for i, x in enumerate(v):
            ax.text(i, x + (2.2 if x >= 0 else -2.2) * (lim[1] - lim[0]) / 75, f"{x:+.1f}" if ax is a2 else f"{x:.1f}", ha="center",
                    va="bottom" if x >= 0 else "top", fontsize=21, fontweight="bold", color=BLUE if i == 3 else INK)
        ax.set_xticks(range(4)); ax.set_xticklabels(arms, fontsize=20); ax.set_ylim(*lim); ax.axhline(0, color="#333", lw=1.6)
        ax.yaxis.grid(True, color="#e6e9ef", lw=1.2); ax.set_axisbelow(True); ax.tick_params(axis="x", length=0)
        c.text(ax.get_position().x0 * c.w - 0.75, 4.25, ttl, fontsize=22, fontweight="bold")
    c.text(7.95, 0.2, "which class saw skin smoothing in training (same model, same data, same recipe)", ha="center", fontsize=20, color=MUTED)
    a1.annotate("our recipe", xy=(3, 21), xytext=(2.35, 45), fontsize=20, color=BLUE, fontweight="bold", ha="center",
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=2.2, mutation_scale=20))
    a2.annotate("misses\ndeepfakes", xy=(2, 51.2), xytext=(0.9, 40), fontsize=19, color=RED, ha="center", va="center",
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=2.0, mutation_scale=18))
    c.save("fig2_exposure")


# ======================================================================================= Fig. 3 method
def method():
    c = Canvas(15.9, 10.6)
    NN = "#26a6dc"
    c.text(0, 10.32, "Training data: every edit has a pixel-exact footprint M", fontsize=24, fontweight="bold", color=BLUE)
    # row 1: FF++ frames, both classes see smoothing
    tw, th, y = 1.5, 1.8, 8.1
    xs = [0, 2.15, 4.55, 6.7]
    for x, f, lab, col in zip(xs, ["ffpp_real", "ffpp_filter", "ffpp_fake", "ffpp_fake_filter"], ["real", "beautified", "forged", "forged"],
                              [GREEN, AMBER, RED, RED]):
        c.img(TL / f"method_{f}.png", x, y, tw, th, border=col, lw=4); c.text(x + tw / 2, y - 0.32, lab, ha="center", fontsize=20, fontweight="bold", color=col)
    for x in (xs[0], xs[2]):
        c.arrow(x + tw + 0.06, y + th / 2, x + 2.09, y + th / 2, lw=2.8, ms=26)
    c.text(8.65, y + 1.25, "Both classes see skin smoothing,", fontsize=22, fontweight="bold")
    c.text(8.65, y + 0.85, "so smoothing is not a forgery cue.", fontsize=22, fontweight="bold")
    c.text(8.65, y + 0.35, "FF++ frames: 41,512", fontsize=20, color=MUTED)
    # row 2: one commercial render split into single operations
    tw, th, y = 1.4, 1.68, 5.6
    c.img(TL / "method_vendor_O.png", 0, y, tw, th, border=GREEN, lw=4); c.text(tw / 2, y - 0.32, "original", ha="center", fontsize=19)
    c.arrow(tw + 0.08, y + th / 2, 1.88, y + th / 2, lw=2.8, ms=26)
    c.img(TL / "method_vendor_R.png", 1.95, y, tw, th, border=AMBER, lw=4); c.text(1.95 + tw / 2, y - 0.32, "app render", ha="center", fontsize=19)
    c.arrow(1.95 + tw + 0.08, y + th / 2, 3.95, y + th / 2, lw=2.8, ms=26)
    for i, k in enumerate(["eye", "contour", "tone", "texture"]):
        x = 4.05 + i * 1.52; c.img(TL / f"method_comp_{k}.png", x, y, tw, th); c.text(x + tw / 2, y - 0.32, k, ha="center", fontsize=19)
    c.text(10.35, y + 1.28, "Optical flow and the photometric", fontsize=21); c.text(10.35, y + 0.9, "residual split one render into", fontsize=21)
    c.text(10.35, y + 0.52, "single operations, each with its", fontsize=21)
    c.text(10.35, y + 0.14, "footprint M, outlined in cyan.", fontsize=21, color="#1b8fc2", fontweight="bold")
    c.text(10.35, y - 0.32, "18,734 renders → 50,112 items", fontsize=20, color=MUTED)
    # row 3: part-level forgery
    tw, y = 1.5, 3.45
    for i, (f, lab, col) in enumerate([("part_x0", "original", GREEN), ("part_x", "donor nose", RED), ("part_M", "footprint M", None)]):
        x = i * 1.95; c.img(TL / f"method_{f}.png", x, y, tw, tw, border=col, lw=4)
        c.text(x + tw / 2, y - 0.32, lab, ha="center", fontsize=19, color=NN if col is None else INK, fontweight="bold" if col is None else "normal")
    c.text(6.0, y + 0.95, "Part-level forgeries: one face part replaced,", fontsize=21); c.text(6.0, y + 0.57, "nothing outside M touched.", fontsize=21)
    c.text(6.0, y + 0.05, "61,510 edits", fontsize=20, color=MUTED)
    # model
    c.fig.add_artist(plt.Line2D([0, 1], [2.85 / c.h, 2.85 / c.h], transform=c.fig.transFigure, color="#d5dae2", lw=2))
    c.text(0, 2.43, "Model: one frozen backbone, four heads", fontsize=24, fontweight="bold", color=BLUE)
    y0, hh = 0.05, 1.95
    c.img(TL / "method_part_x.png", 0, y0, hh, hh, border=RED, lw=4)
    c.arrow(hh + 0.08, y0 + hh / 2, 2.55, y0 + hh / 2, lw=2.8, ms=26)
    c.rbox(2.62, y0, 3.3, hh)
    c.text(2.82, y0 + hh - 0.42, "CLIP ViT-L/14", fontsize=22, fontweight="bold")
    for i in range(5):
        yy = y0 + 0.62 + i * 0.16
        c.rbox(2.82, yy, 2.2, 0.1, fc="#d3dae5", ec="none", lw=0, r=0.03); c.rbox(5.1, yy, 0.62, 0.1, fc=BLUE, ec="none", lw=0, r=0.03)
    c.text(5.1, y0 + 0.36, "LoRA", fontsize=17, color=BLUE, fontweight="bold")
    c.text(2.82, y0 + 0.36, "24 blocks frozen", fontsize=17, color=MUTED)
    c.text(2.82, y0 + 0.08, "3.16 M parameters trained", fontsize=17, color=BLUE, fontweight="bold")
    c.arrow(5.98, y0 + hh / 2, 6.44, y0 + hh / 2, lw=2.8, ms=26)
    heads = [("classification", "real / forged / beautified"), ("operation", "eye · contour · tone · texture"),
             ("evidence", "16×16 map, trained on M")]
    for i, (k, d) in enumerate(heads):
        yy = y0 + hh - 0.6 - i * 0.67
        c.rbox(6.5, yy, 5.2, 0.56, fc="white", ec=BLUE if k == "evidence" else "#b9c4d4", lw=2.4 if k == "evidence" else 2.0)
        c.text(6.65, yy + 0.17, k, fontsize=19, fontweight="bold", color=BLUE); c.text(8.3, yy + 0.17, d, fontsize=17)
    c.arrow(11.74, y0 + 0.29, 12.2, y0 + 0.29, lw=2.8, ms=26)
    c.img(R3 / "model_ev16.png", 12.25, y0 + 0.05, 1.45, 1.45)
    c.text(12.25 + 0.725, y0 + 1.62, "evidence map", ha="center", fontsize=16, color=MUTED)
    c.arrow(13.75, y0 + 0.78, 14.13, y0 + 0.78, lw=2.8, ms=26)
    c.rbox(14.18, y0, 1.72, hh, fc="#eaf5f0", ec=GREEN, lw=2.2)
    for i, line in enumerate(["named part:", "nose", "", "sentence by", "code, checked", "by rules"]):
        c.text(14.3, y0 + hh - 0.36 - i * 0.29, line, fontsize=17, fontweight="bold" if line in ("nose",) else "normal",
               color=RED if line == "nose" else INK)
    c.save("fig3_method")


# ======================================================================================= Fig. 4 AUC after beautification
PUB = {  # report.tex Table audit (L435-451): accused at 5% FPR, AUC after beautification, miss rise; family
    "Xception": (51.6, .737, 10.9, "cnn"), "EfficientNet-B4": (36.3, .762, 3.4, "cnn"), "F3Net": (50.6, .731, 10.9, "cnn"),
    "SPSL": (51.2, .727, 12.4, "cnn"), "UCF": (41.4, .777, 11.3, "cnn"), "RECCE": (36.8, .723, 13.8, "cnn"), "CORE": (54.8, .752, 13.5, "cnn"),
    "SRM": (62.8, .733, 15.3, "cnn"), "SBI": (37.3, .752, 21.8, "cnn"), "CADDM": (6.3, .762, -2.9, "cnn"), "LAA-Net": (17.2, .698, 14.7, "cnn"),
    "UnivFD": (16.6, .624, -7.2, "gen"), "NPR": (0.0, .498, -0.7, "gen"), "Effort": (43.2, .807, 11.0, "clip"),
    "Forensics Adapter": (39.7, .828, 15.2, "clip"), "GenD": (68.7, .807, 12.0, "clip"), "DFD-HR": (64.9, .838, 3.6, "clip")}


def auc():
    rows = sorted([(k, v[1], v[3]) for k, v in PUB.items()], key=lambda r: r[1]) + [("Ours", 0.872, "ours")]
    c = Canvas(7.75, 7.6); ax = c.ax(2.85, 0.75, 4.45, 6.2)
    for i, (k, v, fam) in enumerate(rows):
        col = BLUE if fam == "ours" else (SLATE if fam == "clip" else GREY)
        ax.barh(i, v - 0.4, left=0.4, height=0.68, color=col)
        ax.text(v + 0.006, i, f"{v:.3f}", va="center", fontsize=19, fontweight="bold" if fam != "cnn" and fam != "gen" else "normal",
                color=BLUE if fam == "ours" else INK)
    ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows], fontsize=20)
    for t, r in zip(ax.get_yticklabels(), rows):
        if r[2] == "ours": t.set_color(BLUE); t.set_fontweight("bold"); t.set_fontsize(21)
        elif r[2] == "clip": t.set_color(SLATE); t.set_fontweight("bold")
    ax.set_xlim(0.4, 0.93); ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9]); ax.tick_params(axis="x", labelsize=18); ax.tick_params(axis="y", length=0)
    ax.set_ylim(-0.6, len(rows) - 0.4); ax.spines["left"].set_visible(False)
    ax.xaxis.grid(True, color="#e6e9ef", lw=1.2); ax.set_axisbelow(True)
    c.text(0.05, 7.25, "AUC after app beautification (Celeb-DF-B)", fontsize=22, fontweight="bold")
    c.text(0.05, 0.12, "ours is trained on FF++ only, like the face-forgery detectors", fontsize=17, color=MUTED)
    c.save("fig4_auc")


# ======================================================================================= Fig. 5 both errors
def scatter():
    c = Canvas(7.75, 7.6); ax = c.ax(1.35, 1.2, 6.2, 5.75)
    ax.add_patch(Rectangle((-3, -11), 18, 21.5, color="#e5f3ec", zorder=0))
    ax.text(-2, -10.3, "both errors low", fontsize=18, color=GREEN, fontweight="bold")
    ax.axhline(0, color=MUTED, ls=(0, (5, 4)), lw=1.8)
    lab = {"SBI": (12, 6), "CADDM": (14, -4), "Effort": (-14, -26), "Forensics Adapter": (8, 14), "GenD": (-12, 12), "DFD-HR": (-14, -24),
           "LAA-Net": (12, 6), "UnivFD": (-14, -6)}
    for k, (x, _, y, fam) in PUB.items():
        if fam == "clip":
            ax.scatter(x, y, s=260, marker="s", color=SLATE, zorder=3, edgecolor="white", linewidth=1.5)
        else:
            ax.scatter(x, y, s=230, color=GREY, zorder=3, edgecolor="white", linewidth=1.5)
        if k in lab:
            dx, dy = lab[k]
            ax.annotate(k, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=20, ha="left" if dx > 0 else "right",
                        color=SLATE if fam == "clip" else MUTED, fontweight="bold" if fam == "clip" else "normal")
    for (x, y), nm, off in (((8.6, 6.7), "Ours (two seeds)", (16, -28)), ((12.5, 8.3), "", (0, 0))):  # report.tex L455-456
        ax.scatter(x, y, s=900, marker="*", color=BLUE, zorder=5, edgecolor="white", linewidth=1.5)
        ax.annotate(nm, (x, y), xytext=off, textcoords="offset points", fontsize=19, color=BLUE, fontweight="bold", ha="left" if off[0] > 0 else "right")
    ax.set_xlim(-3, 73); ax.set_ylim(-11, 25); ax.set_xticks(range(0, 71, 10)); ax.set_yticks([-10, 0, 10, 20])
    ax.tick_params(labelsize=20); ax.set_xlabel("smoothed genuine faces called forged (%)", fontsize=21)
    ax.set_ylabel("extra misses on beautified deepfakes (points)", fontsize=19)
    c.text(0.05, 7.25, "Both errors, 17 published detectors", fontsize=22, fontweight="bold")
    lx, ly = 4.6, 1.6
    ax.scatter([], [], s=200, color=GREY, label="CNN / generated-image"); ax.scatter([], [], s=220, marker="s", color=SLATE, label="CLIP-based, 2025–26")
    ax.scatter([], [], s=500, marker="*", color=BLUE, label="ours")
    ax.legend(loc="lower right", fontsize=18, frameon=True, framealpha=0.95, edgecolor="#d5dae2", handletextpad=0.3, borderpad=0.5, labelspacing=0.4)
    c.save("fig5_scatter")


# ======================================================================================= Fig. 6 unseen retouching service
def unseen():
    # report.tex L476-479, L375-378: strength 90 of the Alibaba service, never used in training
    ops = [("op_orig_full", "original", 78.4, "called real", GREEN), ("op_eye_full", "eye enlarging", 69.7, "beautified", AMBER),
           ("op_slim_full", "face slimming", 61.3, "beautified", AMBER), ("op_smooth_full", "skin smoothing", 98.8, "beautified", AMBER),
           ("op_white_full", "whitening", 72.3, "beautified", AMBER)]
    c = Canvas(15.9, 4.25); s = 2.5; g = (15.9 - 5 * s) / 4
    for i, (f, nm, v, w, col) in enumerate(ops):
        x = i * (s + g); c.img(A / f"{f}.png", x, 1.62, s, s, border=col, lw=5)
        c.text(x + s / 2, 1.22, nm, ha="center", fontsize=21, fontweight="bold")
        c.text(x + s / 2, 0.55, f"{v:.1f}%", ha="center", fontsize=30, fontweight="bold", color=col)
        c.text(x + s / 2, 0.12, w, ha="center", fontsize=18, color=MUTED)
    c.save("fig6_unseen")


# ======================================================================================= Fig. 7 evidence
def evidence():
    # report.tex Table restoration (L574-580), donor-transplant column
    meth = [("centre of face", 38.6), ("Grad-CAM", 50.9), ("Grad-CAM++", 51.7), ("Score-CAM", 56.5), ("Ours: evidence head", 94.0)]
    c = Canvas(15.9, 4.7); s = 2.45
    for i, (f, l1, l2, col) in enumerate([("ev0_input", "nose from a donor", "forged 1.00", RED), ("ev0_ours", "our evidence map", "marks the nose", BLUE),
                                          ("ev0_restored", "nose restored", "→ real 0.95", GREEN)]):
        x = i * (s + 0.25); c.img(R3 / f"{f}.png", x, 1.18, s, s, border=col if i != 1 else None, lw=5)
        c.text(x + s / 2, 0.82, l1, ha="center", fontsize=19); c.text(x + s / 2, 0.38, l2, ha="center", fontsize=21, fontweight="bold", color=col)
    ax = c.ax(11.2, 0.8, 4.2, 2.95)
    for i, (k, v) in enumerate(meth):
        on = k.startswith("Ours"); ax.barh(i, v, height=0.62, color=BLUE if on else GREY)
        ax.text(v + 1.5, i, f"{v:.1f}", va="center", fontsize=18, fontweight="bold" if on else "normal", color=BLUE if on else INK)
    ax.axvline(94.1, color=INK, ls=(0, (4, 3)), lw=1.8); ax.text(94.1, 4.62, "true edit 94.1", ha="right", fontsize=16, color=MUTED)
    ax.set_yticks(range(len(meth))); ax.set_yticklabels([m[0] for m in meth], fontsize=18); ax.set_xlim(0, 112); ax.set_xticks([0, 25, 50, 75, 100])
    ax.tick_params(axis="x", labelsize=17); ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
    yl = ax.get_yticklabels()[-1]; yl.set_color(BLUE); yl.set_fontweight("bold")
    ax.xaxis.grid(True, color="#e6e9ef", lw=1.2); ax.set_axisbelow(True)
    c.text(8.35, 4.3, "Forgery decisions removed by restoring", fontsize=21, fontweight="bold")
    c.text(8.35, 3.93, "the marked region (%)", fontsize=21, fontweight="bold")
    c.save("fig7_evidence")


if __name__ == "__main__":
    which = sys.argv[1:] or ["teaser", "exposure", "auc", "scatter", "unseen", "evidence"]   # method: make_method_svg.py (inline SVG)
    for w in which:
        globals()[w]()
