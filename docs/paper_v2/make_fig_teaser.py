"""fig_teaser: the problem in one picture. Celeb-DF-B frames of one genuine video and one deepfake video, untreated and
app-beautified (same frame index), with the official SBI decision at its 5 %-FPR threshold on untreated genuine frames and
the RU2 three-way decision. Examples are selected where SBI errs after beautification and RU2 does not (stated in the
caption); rates are in the paper.  python docs/paper_v2/make_fig_teaser.py"""
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

rows = [l.split("\t") for l in (B / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
S = B / "results/research/celebdfb_v2_20260927/scores_v3"
sbi = np.load(S / "sbi.npz")["p"][:, 1]; ru = np.load(S / "RU-clipe4.npz")["p"]
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
CLS = ["real", "fake", "filter"]; COL = {"real": "#2f7d4f", "fake": MF.C_SBI, "filter": "#9a6a00"}

fig = plt.figure(figsize=(7.1, 2.55))
spec = [("genuine face", gi, "untreated"), ("genuine face", gj, "beautified (app preset)"),
        ("deepfake", fi, "untreated"), ("deepfake", fj, "beautified (app preset)")]
xs = [0.02, 0.255, 0.52, 0.755]; w = 0.2
for k, (kind, i, cond) in enumerate(spec):
    ax = fig.add_axes([xs[k], 0.30, w, 0.60])
    ax.imshow(np.array(Image.open(rows[i][0]).convert("RGB").resize((220, 250))), aspect="auto"); ax.set_xticks([]); ax.set_yticks([])
    for s_ in ax.spines.values():
        s_.set_visible(True); s_.set_color(MF.MUTED); s_.set_linewidth(0.6)
    ax.set_title(f"{kind}, {cond}", fontsize=7, color=MF.INK, pad=3)
    truth_fake = kind == "deepfake"
    sd = "fake" if sbi[i] > t else "real"; sbi_ok = (sd == "fake") == truth_fake
    fig.text(xs[k] + w / 2, 0.20, f"binary (SBI): {sd}" + ("" if sbi_ok else ("  \u2717 accused" if not truth_fake else "  \u2717 escaped")),
             ha="center", fontsize=6.8, color=MF.INK if sbi_ok else MF.C_SBI, fontweight="normal" if sbi_ok else "bold")
    od = CLS[int(ru[i].argmax())]
    fig.text(xs[k] + w / 2, 0.09, f"three-way (ours): {od}", ha="center", fontsize=6.8, color=COL[od], fontweight="bold")
for a, b in ((0, 1), (2, 3)):
    fig.add_artist(FancyArrowPatch((xs[a] + w + 0.004, 0.60), (xs[b] - 0.004, 0.60), transform=fig.transFigure,
                                   arrowstyle="-|>", mutation_scale=9, color=MF.MUTED, lw=0.9))
fig.add_artist(plt.Line2D([0.497, 0.497], [0.05, 0.95], transform=fig.transFigure, color=MF.GRID, lw=1.0))
MF.save(fig, "fig_teaser")
print("teaser", rows[gi][2], rows[gi][0].split("__")[-1], rows[fi][2], rows[fi][0].split("__")[-1],
      "sbi", round(float(sbi[gi]), 3), round(float(sbi[gj]), 3), round(float(sbi[fi]), 3), round(float(sbi[fj]), 3), "t", round(t, 3))
