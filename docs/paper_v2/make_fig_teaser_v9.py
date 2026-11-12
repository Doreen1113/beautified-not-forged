"""fig_teaser_v9 (paper v9, 2026-10-28): Fig. 1 as a motivated example (running example + failure case), 7.16 x 2.45 in.

(a) Direction A on one real pair: FFHQ photograph 17003 and its Smoothing-90 render by the commercial retouching service
    (ffhq_originals/Part2/17003.png, FFHQ_ali_process/Smoothing_90/17000/17003.png; central 640 x 640 crop of the 1024 image,
    as fig_teaser_v8b). Under the pair, the P(fake) of the four CLIP detectors on each image, with each detector's own
    threshold (the score that accuses 5 % of the 2,210 untouched originals) as a tick; a bar past its tick is a "forged" call.
    results/research/alipair_zeroshot_20260929/published_scores_<det>.npz (s, group, stem); threshold = 95th percentile of
    group orig_0, exactly as main_claim_A.py.
(b) Direction B on one real video: Celeb-DF-B deepfake id17_id35_0000, frame f05, as recorded and after the app preset
    (external_data/celebdfb/frames_std32v3/synthesis/ and synthesis_beautified/). Same four detectors, same bar; threshold =
    95th percentile of the real folder (untreated genuine frames), as fair_cdfb.py. Scores are the video means over the 32
    frames (the quantity the paper's video-level numbers use); the frame shown is representative (its own scores are in the
    source comment of the LaTeX caption).
    results/research/celebdfb_v2_20260927/scores_v3/<det>.npz (p[:, 1] = P(fake), paths).
Neither the pair nor the video was chosen by score first: 17003 is one of the three stems of fig_teaser_v8b (first stems
present in both folders) and id17_id35_0000 is the first video, in sorted order, that all four CLIP detectors catch as
recorded and after re-encoding and miss after the preset (the search is in the 2026-10-28 session log).

    python docs/paper_v2/make_fig_teaser_v9.py  -> docs/paper_v2/figs/fig_teaser_v9.{pdf,png}
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B / "docs/paper_v2"))
import figstyle as FS  # noqa: E402
import figstyle_v8b as V  # noqa: E402
FS.apply()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, Rectangle  # noqa: E402

OUT = B / "docs/paper_v2/figs"
DETS = [("effort", "Effort"), ("fadapter", "Forensics Ad."), ("gend", "GenD"), ("dfdhr", "DFD-HR")]
STEM = "17003"; VID = "id17_id35_0000"; FRAME = "05"

# ---------------------------------------------------------------- data ---------------------------------------------------------
A = {}
for k, _ in DETS:
    z = np.load(B / "results/research/alipair_zeroshot_20260929" / f"published_scores_{k}.npz")
    s, g, st = z["s"], z["group"], z["stem"]
    thr = float(np.quantile(s[g == "orig_0"], 0.95))
    A[k] = (float(s[(g == "orig_0") & (st == STEM)][0]), float(s[(g == "Smoothing_90") & (st == STEM)][0]), thr)
Bv = {}
for k, _ in DETS:
    z = np.load(B / "results/research/celebdfb_v2_20260927/scores_v3" / f"{k}.npz", allow_pickle=True)
    p = z["p"][:, 1]; paths = np.array([x.replace("\\", "/") for x in z["paths"]])
    fold = np.array([x.split("/")[-2] for x in paths]); vid = np.array([x.split("/")[-1].split("__")[0] for x in paths])
    fr = np.array([x.split("__f")[-1][:2] for x in paths])
    thr = float(np.quantile(p[fold == "real"], 0.95))
    u = float(p[(fold == "synthesis") & (vid == VID)].mean()); b = float(p[(fold == "synthesis_beautified") & (vid == VID)].mean())
    uf = float(p[(fold == "synthesis") & (vid == VID) & (fr == FRAME)][0]); bf = float(p[(fold == "synthesis_beautified") & (vid == VID) & (fr == FRAME)][0])
    Bv[k] = (u, b, thr, uf, bf)
print("A", {k: tuple(round(x, 3) for x in v) for k, v in A.items()})
print("B (video mean untreated, beautified, thr, frame untreated, frame beautified)", {k: tuple(round(x, 3) for x in v) for k, v in Bv.items()})

# ---------------------------------------------------------------- images --------------------------------------------------------
o = np.array(Image.open(B / "ffhq_originals/Part2" / f"{STEM}.png").convert("RGB"))[200:840, 192:832]
s = np.array(Image.open(B / "FFHQ_ali_process/Smoothing_90" / f"{int(STEM) // 1000 * 1000}" / f"{STEM}.png").convert("RGB"))[200:840, 192:832]
F = B / "external_data/celebdfb/frames_std32v3"
fu = np.array(Image.open(F / "synthesis" / f"{VID}__f{FRAME}.jpg").convert("RGB"))
fb = np.array(Image.open(F / "synthesis_beautified" / f"{VID}__f{FRAME}.jpg").convert("RGB"))
def square(im):
    h, w = im.shape[:2]; m = min(h, w); y0 = (h - m) // 2; x0 = (w - m) // 2; return im[y0:y0 + m, x0:x0 + m]
fu, fb = square(fu), square(fb)

# ---------------------------------------------------------------- layout --------------------------------------------------------
W, H = FS.FULL, 2.55
fig = plt.figure(figsize=(W, H))
PANW = 3.45; PX = [0.0, W - PANW - 0.22]    # panel left edges (inches)
IMW = 0.9; IMGAP = 0.62; IMTOP = H - 0.34     # image tile side, gap for the arrow, top of the tiles
LABW = 0.76                                   # label column for the bars
BARW = 0.6                                    # bar length for P(fake) = 1
BARH = 0.105; BARG = 0.055                    # bar height and gap
BAR0 = IMTOP - IMW - 0.44                     # top of the first bar row

def panel(px, letter, title, ims, imlabs, arrow, rows, truth, wrong_side, wrong_word):
    """rows: list of (name, score_left, score_right, thr). truth: 'genuine' or 'forged' (the true class of both images)."""
    V.fig_tag(fig, letter, px + 0.04, H - 0.17)
    fig.text((px + 0.26) / W, (H - 0.13) / H, title, ha="left", va="center", fontsize=FS.FS_TEXT, color=FS.INK, fontweight="bold")
    xs = [px + LABW + 0.02, px + LABW + 0.02 + IMW + IMGAP]
    for i, (im, lab) in enumerate(zip(ims, imlabs)):
        ax = fig.add_axes([xs[i] / W, (IMTOP - IMW) / H, IMW / W, IMW / H])
        ax.imshow(im, interpolation="lanczos"); FS.frame(ax, color=FS.MUTED, lw=0.5)
        fig.text((xs[i] + IMW / 2) / W, (IMTOP - IMW - 0.035) / H, lab, ha="center", va="top", fontsize=FS.FS_NOTE, color=FS.INK)
    # arrow with the edit named on it
    ax0 = xs[0] + IMW + 0.04; ax1 = xs[1] - 0.04; ay = IMTOP - IMW / 2
    fig.add_artist(FancyArrowPatch((ax0 / W, ay / H), (ax1 / W, ay / H), transform=fig.transFigure, arrowstyle="-|>",
                                   mutation_scale=7, color=FS.INK, lw=0.8))
    fig.text(((ax0 + ax1) / 2) / W, (ay + 0.06) / H, arrow, ha="center", va="bottom", fontsize=FS.FS_NOTE, color=FS.INK,
             bbox=dict(boxstyle="square,pad=0.1", facecolor="white", edgecolor="none"))
    # true class, written once above the label column
    fig.text((px + 0.02) / W, (IMTOP - 0.02) / H, f"true class:\n{truth}", ha="left", va="top", fontsize=FS.FS_NOTE, color=FS.INK)
    # bar rows: label | bar left | bar right ; a bar is P(fake), the tick is the detector's own threshold
    for r, (name, sl, sr, thr) in enumerate(rows):
        y = BAR0 - r * (BARH + BARG)
        fig.text((px + LABW - 0.04) / W, (y + BARH / 2) / H, name, ha="right", va="center", fontsize=FS.FS_NOTE, color=FS.INK)
        for i, sc in enumerate((sl, sr)):
            x = xs[i]; forged = sc > thr
            col = FS.FAKE if forged else FS.REAL
            fig.add_artist(Rectangle((x / W, y / H), BARW / W, BARH / H, transform=fig.transFigure, facecolor=FS.LIGHT, edgecolor="none"))
            fig.add_artist(Rectangle((x / W, y / H), sc * BARW / W, BARH / H, transform=fig.transFigure, facecolor=col, edgecolor="none"))
            fig.add_artist(plt.Line2D([(x + thr * BARW) / W] * 2, [(y - 0.02) / H, (y + BARH + 0.02) / H], transform=fig.transFigure, color=FS.INK, lw=0.7))
            word = "forged" if forged else "genuine"
            fig.text((x + BARW + 0.04) / W, (y + BARH / 2) / H, f"{sc:.2f} {word}", ha="left", va="center", fontsize=FS.FS_NOTE,
                     color=col, fontweight="bold" if (i == wrong_side) else "normal")
    # column headers over the bars: the decision on each image, and the error named on the wrong column
    for i, hdr in enumerate(("detector decision", wrong_word)):
        xh = xs[i]; iswrong = i == wrong_side
        fig.text((xh + BARW / 2) / W, (BAR0 + BARH + 0.06) / H, hdr if iswrong else "detector decision", ha="center", va="bottom",
                 fontsize=FS.FS_NOTE, color=FS.FAKE if iswrong else FS.MUTED, fontweight="bold" if iswrong else "normal")

rowsA = [(n, A[k][0], A[k][1], A[k][2]) for k, n in DETS]
rowsB = [(n, Bv[k][0], Bv[k][1], Bv[k][2]) for k, n in DETS]
panel(PX[0], "a", "A genuine photograph is accused after skin smoothing", (o, s), ("original", "retouched (Smoothing-90)"),
      "retouching service", rowsA, "genuine", 1, "accused")
panel(PX[1], "b", "A deepfake is let through after an app beauty preset", (fu, fb), ("as recorded", "app preset"),
      "beauty app", rowsB, "forged\n(face swap)", 1, "missed")
# one shared note under both panels (7 pt, not clipped)
fig.text(0.5, (BAR0 - 4 * (BARH + BARG) + 0.02) / H, "bars: P(fake) of each detector;  ticks: its own threshold, set at 5 % false alarms on untouched genuine faces of the same source",
         ha="center", va="top", fontsize=FS.FS_NOTE, color=FS.MUTED)
# divider
fig.add_artist(plt.Line2D([(PX[1] - 0.14) / W] * 2, [0.12, 0.97], transform=fig.transFigure, color=FS.GRID, lw=0.8))
FS.save(fig, OUT / "fig_teaser_v9")
print("saved", OUT / "fig_teaser_v9.pdf")
