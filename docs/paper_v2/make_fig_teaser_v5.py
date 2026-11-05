"""fig_teaser_v5 (paper v5): same selection rule and layout as make_fig_teaser.py, with the main model (RU-clipe5, seed 20260929)
in place of the superseded RU-clipe4 checkpoint.

fig_teaser: the problem in one picture. Celeb-DF-B frames of one genuine video and one deepfake video, untreated and
app-beautified (same frame index), with the official SBI decision at its 5 %-FPR threshold on untreated genuine frames and
the RU2 three-way decision. Examples are selected where SBI errs after beautification and RU2 does not (stated in the
caption); rates are in the paper.  python docs/paper_v2/make_fig_teaser_v5.py
Drawing (2026-10-16): shared style docs/paper_v2/figstyle.py; decisions in green when correct and vermillion (bold, with the error named)
when wrong; a genuine face called filter counts as not accused."""
import sys
from pathlib import Path

import matplotlib
import numpy as np
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402

B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B / "docs/paper_v2"))
import make_figures as MF  # noqa: E402
import figstyle as FS  # noqa: E402
FS.apply()   # after make_figures, which sets its own rcParams on import

rows = [l.split("\t") for l in (B / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
S = B / "results/research/celebdfb_v2_20260927/scores_v3"
sbi = np.load(S / "sbi.npz")["p"][:, 1]; ru = np.load(S / "RU-clipe5.npz")["p"]
folder = np.array([r[3] for r in rows]); vid = np.array([r[2] for r in rows]); fr = np.array([Path(r[0]).stem.split("__")[-1] for r in rows])
t = float(np.quantile(sbi[folder == "real"], 0.95)); am = ru.argmax(1)
idx = {(f, v, x): i for i, (f, v, x) in enumerate(zip(folder, vid, fr))}


def pick(a, b, ok):
    best = None
    for (f, v, x), i in idx.items():
        if f != a:
            continue
        j = idx.get((b, v, x))
        if j is not None and ok(i, j):
            score = abs(sbi[i] - sbi[j]) + ru[j].max()
            if best is None or score > best[0]:
                best = (score, i, j)
    return best[1], best[2]


gi, gj = pick("real", "real_beautified", lambda i, j: sbi[i] <= t and sbi[j] > t and am[i] == 0 and am[j] == 2)
fi, fj = pick("synthesis", "synthesis_beautified", lambda i, j: sbi[i] > t and sbi[j] <= t and am[i] == 1 and am[j] == 1 and ru[j, 1] > 0.8)
CLS = ["real", "fake", "filter"]

# ---- drawing (shared style docs/paper_v2/figstyle.py), at final size: 0.84 x text width = 6.0 in
W, H = 6.0, 2.25
fig = plt.figure(figsize=(W, H))
spec = [("genuine", gi, "untreated"), ("genuine", gj, "beautified"), ("deepfake", fi, "untreated"), ("deepfake", fj, "beautified")]
lm, tw, th, gap, mid = 0.98, 1.08, 1.18, 0.17, 0.32          # left margin (row labels), tile w/h, gap in a pair, gap between pairs
xs = [lm, lm + tw + gap, lm + 2 * tw + gap + mid, lm + 3 * tw + 2 * gap + mid]
ytile = 0.62; yr1, yr2 = 0.40, 0.17                            # tile bottom, decision rows
for k, (kind, i, cond) in enumerate(spec):
    ax = fig.add_axes([xs[k] / W, ytile / H, tw / W, th / H])
    ax.imshow(np.array(Image.open(rows[i][0]).convert("RGB").resize((216, 246))), aspect="auto"); FS.frame(ax, color=FS.MUTED, lw=0.4)
    ax.set_title(cond, fontsize=FS.FS_NOTE + 0.5, pad=2.5, color=FS.INK)
    truth = 1 if kind == "deepfake" else 0
    sd = 1 if sbi[i] > t else 0                                # SBI at its 5%-FPR threshold
    od = int(ru[i].argmax())                                   # ours, three-way
    ok_s = sd == truth
    ok_o = (od == 1) if truth == 1 else (od != 1)             # a genuine face called filter is not accused
    cx = (xs[k] + tw / 2) / W
    for y, word, ok in ((yr1, ["real", "fake"][sd], ok_s), (yr2, CLS[od], ok_o)):
        tag = "" if ok else ("  (accused)" if truth == 0 else "  (missed)")
        fig.text(cx, y / H, word + tag, ha="center", va="center", fontsize=FS.FS_TEXT, color=FS.OK if ok else FS.ERR,
                 fontweight="normal" if ok else "bold")
for k0, lab in ((0, "genuine video"), (2, "deepfake video")):
    x0, x1 = xs[k0] / W, (xs[k0 + 1] + tw) / W
    fig.text((x0 + x1) / 2, (H - 0.03) / H, lab, ha="center", va="top", fontsize=FS.FS_TEXT, fontweight="bold")
    fig.add_artist(plt.Line2D([x0, x1], [(H - 0.215) / H] * 2, transform=fig.transFigure, color=FS.MUTED, lw=0.6))
    fig.add_artist(FancyArrowPatch(((xs[k0] + tw + 0.02) / W, (ytile + th / 2) / H), ((xs[k0 + 1] - 0.02) / W, (ytile + th / 2) / H),
                                   transform=fig.transFigure, arrowstyle="-|>", mutation_scale=9, color=FS.MUTED, lw=0.9))
fig.text(0.02, yr1 / H, "binary (SBI)", ha="left", va="center", fontsize=FS.FS_TEXT, color=FS.INK)
fig.text(0.02, yr2 / H, "three-way (ours)", ha="left", va="center", fontsize=FS.FS_TEXT, color=FS.OURS, fontweight="bold")
for y in ((yr1 + yr2) / 2, ):
    fig.add_artist(plt.Line2D([0.02, (xs[3] + tw) / W], [y / H] * 2, transform=fig.transFigure, color=FS.GRID, lw=0.5))
fig.add_artist(plt.Line2D([(xs[1] + tw + mid / 2) / W] * 2, [0.06 / H, (H - 0.04) / H], transform=fig.transFigure, color=FS.GRID, lw=0.8))
FS.save(fig, MF.OUT / "fig_teaser_v5")
print("teaser", rows[gi][2], rows[gi][0].split("__")[-1], rows[fi][2], rows[fi][0].split("__")[-1],
      "sbi", round(float(sbi[gi]), 3), round(float(sbi[gj]), 3), round(float(sbi[fi]), 3), round(float(sbi[fj]), 3), "t", round(t, 3))
