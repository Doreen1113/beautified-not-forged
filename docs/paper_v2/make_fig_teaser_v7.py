"""fig_teaser_v7 (paper v7, 2026-10-18): the problem in one picture, double-column width (6.9 x 2.6 in).

Message: every published deepfake detector scores a skin-smoothed genuine face as more forged than the same face untouched.

Left: three FFHQ originals (ffhq_originals/Part*/<stem>.png) and their commercial Smoothing-90 renders
(FFHQ_ali_process/Smoothing_90/<index//1000*1000>/<stem>.png). Stems: the first three in sorted order present in both folders
(17001, 17002, 17003); central 640 x 640 crop of the 1024 x 1024 aligned image.
Right: one row per detector. For each detector the score of every original and every render is mapped to its quantile among
the 2,210 originals (mid-rank empirical CDF of the originals, so every detector lives on the same 0-1 axis). fig_teaser_v7 shows
where the smoothed render lands on that axis (ridge = Gaussian KDE of quantile(render), reflected at 0 and 1; dot = median;
dashed lines at the median original and at the 5 %-FPR accusation point 0.95) and, at the right edge, the share of pairs in
which the render scores above its own original (threshold-free, the number used in the paper). fig_teaser_v7_diff is the same
figure with the paired shift quantile(render) - quantile(original) on the axis; that shift is bounded by 1 - quantile(original),
so its distribution is a plateau for every detector and discriminates less (kept as an alternative).
Data: results/research/alipair_zeroshot_20260929/published_scores_<name>.npz (s, group, stem) for the published detectors and
results/research/retouch_unified_20260929/ali_scores_clipe5b_s20260929.npz (ours, forgery head only) and
ali_scores_clipe5_s20260929.npz (ours, full model), P[:, 1] = P(fake). NPR is omitted: its scores saturate (40 % of the
originals at exactly 1.0, 19 % exact ties), so a quantile has no meaning for it (the paper lists it as n/a).

    python docs/paper_v2/make_fig_teaser_v7.py  -> docs/paper_v2/figs/fig_teaser_v7.{pdf,png}
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.stats import gaussian_kde

B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B / "docs/paper_v2"))
import figstyle as FS  # noqa: E402
FS.apply()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch  # noqa: E402

OUT = B / "docs/paper_v2/figs"
PUB = B / "results/research/alipair_zeroshot_20260929"
RU = B / "results/research/retouch_unified_20260929"
GEN = "#56B4E9"   # general generated-image detector (Okabe-Ito sky blue; the family has no entry in figstyle)

# (key, printed name, family); paper order inside each family (Sec. 2: eleven face-forgery CNNs, two general detectors, four CLIP)
DETS = [("xception", "Xception", "cnn"), ("effnb4", "EfficientNet-B4", "cnn"), ("f3net", "F3Net", "cnn"), ("spsl", "SPSL", "cnn"),
        ("ucf", "UCF", "cnn"), ("recce", "RECCE", "cnn"), ("core", "CORE", "cnn"), ("srm", "SRM", "cnn"), ("sbi", "SBI", "cnn"),
        ("caddm", "CADDM", "cnn"), ("laanetr", "LAA-Net", "cnn"),
        ("univfd", "UnivFD", "gen"),
        ("effort", "Effort", "clip"), ("fadapter", "Forensics Adapter", "clip"), ("gend", "GenD", "clip"), ("dfdhr", "DFD-HR", "clip"),
        ("ours_b", "Ours (binary)", "ours"), ("ours_f", "Ours (full)", "ours")]
COLOR = {"cnn": FS.CNN, "gen": GEN, "clip": FS.CLIP, "ours": FS.OURS}
FAMILY_NAME = {"cnn": "face-forgery CNN", "gen": "generated-image detector", "clip": "CLIP-based", "ours": "ours"}


def pairs(key):
    if key.startswith("ours"):
        d = np.load(RU / ("ali_scores_clipe5b_s20260929.npz" if key == "ours_b" else "ali_scores_clipe5_s20260929.npz"), allow_pickle=True)
        s = d["P"][:, 1]
    else:
        d = np.load(PUB / f"published_scores_{key}.npz", allow_pickle=True); s = d["s"]
    g = d["group"].astype(str); st = d["stem"].astype(str)
    o = dict(zip(st[g == "orig_0"], s[g == "orig_0"])); r = dict(zip(st[g == "Smoothing_90"], s[g == "Smoothing_90"]))
    ks = sorted(set(o) & set(r)); return np.array([o[k] for k in ks], float), np.array([r[k] for k in ks], float)


def quantile_shift(a, b):
    """mid-rank quantile among the originals a, for the originals themselves and for the renders b."""
    srt = np.sort(a); n = len(a)
    q = lambda v: (np.searchsorted(srt, v, "left") + np.searchsorted(srt, v, "right")) / (2 * n)
    return q(a), q(b), float((b > a).mean())


rows = []
for key, name, fam in DETS:
    a, b = pairs(key); qa, qb, share = quantile_shift(a, b)
    rows.append((name, fam, qa, qb, share))
    print(f"{name:18s} n={len(qa)} median q(render) {np.median(qb):.3f}  median shift {np.median(qb - qa):+.3f}  "
          f"render>original {100 * share:.1f}%  above 5%-FPR {100 * (qb > 0.95).mean():.1f}%")


def draw(variant):
    """variant "land": ridge of q(render) (where the smoothed face lands among the originals) with the 5 %-FPR line;
    variant "diff": ridge of q(render) - q(original), the paired shift (bounded by 1 - q(original), hence a plateau)."""
    W, H = 6.9, 2.7
    fig = plt.figure(figsize=(W, H))
    STEMS = ["17001", "17002", "17003"]
    tw = 0.75; gap = 0.035; x0 = 0.08; ytop = H - 0.33; vgap = 0.04
    for r, st in enumerate(STEMS):
        o = np.array(Image.open(B / "ffhq_originals/Part2" / f"{st}.png").convert("RGB"))[200:840, 192:832]
        s = np.array(Image.open(B / "FFHQ_ali_process/Smoothing_90" / f"{int(st) // 1000 * 1000}" / f"{st}.png").convert("RGB"))[200:840, 192:832]
        y = ytop - (r + 1) * tw - r * vgap
        for c, im in enumerate((o, s)):
            ax = fig.add_axes([(x0 + c * (tw + gap)) / W, y / H, tw / W, tw / H])
            ax.imshow(im, interpolation="lanczos"); FS.frame(ax, color=FS.MUTED, lw=0.4)
    for c, lab in enumerate(("original", "smoothed by a service")):
        fig.text((x0 + c * (tw + gap) + tw / 2) / W, (ytop + 0.03) / H, lab, ha="center", va="bottom", fontsize=FS.FS_NOTE + 0.5, color=FS.INK)
    fig.text((x0 + tw + gap / 2) / W, (ytop + 0.03 + 0.13) / H, "genuine FFHQ faces", ha="center", va="bottom",
             fontsize=FS.FS_NOTE + 0.5, color=FS.INK, fontweight="bold")
    fig.add_artist(FancyArrowPatch(((x0 + tw + 0.004) / W, (ytop + 0.065) / H), ((x0 + tw + gap - 0.004) / W, (ytop + 0.065) / H),
                                   transform=fig.transFigure, arrowstyle="-|>", mutation_scale=5, color=FS.MUTED, lw=0.6))

    AXL, AXR, AXB, AXT = 2.92, 6.44, 0.34, H - 0.42
    ax = fig.add_axes([AXL / W, AXB / H, (AXR - AXL) / W, (AXT - AXB) / H])
    n = len(rows); pitch = 1.0; FS_T = FS.FS_NOTE + 0.3
    lo, hi = (0, 1) if variant == "land" else (-1, 1)
    grid = np.linspace(lo, hi, 401)
    dens = {}
    for i, (name, fam, qa, qb, share) in enumerate(rows):
        v = qb if variant == "land" else qb - qa
        dens[i] = gaussian_kde(np.concatenate([v, 2 * hi - v, 2 * lo - v]), bw_method=0.05)(grid) * 3
    fam_prev = None
    for i, (name, fam, qa, qb, share) in enumerate(rows):
        v = qb if variant == "land" else qb - qa
        yb = (n - 1 - i) * pitch; col = COLOR[fam]
        # KDE reflected at the axis ends (mass piled at 1 or 0 is not smeared outside the range), each row scaled to its own peak
        kde = dens[i] / dens[i].max() * 0.86 * pitch
        ax.fill_between(grid, yb, yb + kde, color=col, alpha=0.42 if fam != "ours" else 0.55, lw=0)
        ax.plot(grid, yb + kde, color=col, lw=0.6)
        med = float(np.median(v))
        ax.plot([med], [yb + 0.1], marker="o", ms=3.0, mec="white", mew=0.5, mfc=col, ls="none", zorder=5, clip_on=False)
        ax.text(lo - 0.015 * (hi - lo), yb + 0.08, name, ha="right", va="bottom", fontsize=FS_T,
                color=FS.OURS if fam == "ours" else FS.INK, fontweight="bold" if fam == "ours" else "normal")
        ax.text(hi + 0.015 * (hi - lo), yb + 0.08, f"{100 * share:.0f}%", ha="left", va="bottom", fontsize=FS_T,
                color=FS.INK if fam == "cnn" else col, fontweight="bold" if fam == "ours" else "normal")
        if fam_prev is not None and fam != fam_prev:
            ax.axhline(yb + pitch - 0.03, color=FS.GRID, lw=0.5, xmin=-0.3, xmax=1.12, clip_on=False)
        fam_prev = fam
    ax.set_xlim(lo, hi); ax.set_ylim(-0.05, n * pitch + 0.05)
    ax.set_yticks([]); ax.spines["left"].set_visible(False)
    if variant == "land":
        ax.axvline(0.5, color=FS.MUTED, lw=0.6, ls=(0, (2.5, 1.8)), zorder=0)
        ax.axvline(0.95, color=FS.FAKE, lw=0.7, ls=(0, (2.5, 1.8)), zorder=0)
        ax.text(0.5, n * pitch + 0.1, "median original", ha="center", va="bottom", fontsize=FS.FS_NOTE - 0.5, color=FS.MUTED)
        ax.text(0.94, n * pitch + 0.1, "accused at 5% FPR →", ha="right", va="bottom", fontsize=FS.FS_NOTE - 0.5, color=FS.FAKE)
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); ax.set_xticklabels(["0", "0.25", "0.5", "0.75", "1"])
        ax.set_xlabel("forgery score of the smoothed face, as a quantile among the 2,210 untouched originals", labelpad=2)
    else:
        ax.axvline(0, color=FS.MUTED, lw=0.6, ls=(0, (2.5, 1.8)), zorder=0)
        ax.set_xticks([-1, -0.5, 0, 0.5, 1]); ax.set_xticklabels(["−1", "−0.5", "0", "+0.5", "+1"])
        ax.set_xlabel("paired shift of the forgery score after smoothing, in quantiles of the untouched originals", labelpad=2)
    ax.text(hi + 0.015 * (hi - lo), n * pitch + 0.1, "render >\noriginal", ha="left", va="bottom", fontsize=FS.FS_NOTE - 0.5,
            color=FS.MUTED, linespacing=0.95)
    leg = [plt.Rectangle((0, 0), 1, 1, fc=COLOR[f], alpha=0.6, ec=COLOR[f], lw=0.5) for f in ("cnn", "gen", "clip", "ours")]
    ax.legend(leg, [FAMILY_NAME[f] for f in ("cnn", "gen", "clip", "ours")], loc="lower left", bbox_to_anchor=(-0.02, 1.06), ncol=4,
              fontsize=FS.FS_NOTE - 0.3, handlelength=0.9, handleheight=0.8, columnspacing=0.9, handletextpad=0.35, frameon=False)
    stem = OUT / ("fig_teaser_v7" if variant == "land" else "fig_teaser_v7_diff")
    FS.save(fig, stem); print("wrote", stem.with_suffix(".pdf"))


draw("land")
draw("diff")
