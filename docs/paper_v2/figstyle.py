"""Shared figure style for the submission paper (docs/paper_v2/main_v5.tex, supplement_v5.tex) and the capstone paper
(docs/capstone/paper/capstone.tex). Every figure generator of both papers imports this module, so fonts, line weights and the
colour of each method family are the same in every figure.

House style adapted from figures4papers (Chen Liu, github.com/ChenLiu-1996/figures4papers, CC BY-NC 4.0; only the conventions
are reused, no code is copied): sans-serif text, no top/right spines, frameless legends, minimal grid, deep blue #0F4D92 for the
proposed method, neutral grey for baselines, vector export. Changed for a two-column IEEE page: figures are drawn at their final
printed size (column 3.5 in, full width 7.16 in) so that 8 pt in the script is 8 pt on paper, and the palette is restricted to
colour-blind-safe hues (Okabe & Ito 2008 / Wong 2011, Nature Methods 8:441) plus the house blue.

    import figstyle as FS; FS.apply(); fig, ax = plt.subplots(figsize=(FS.COL, 2.4), layout="constrained"); ...; FS.save(fig, path)
"""
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

# ------------------------------------------------------------------ page geometry (inches) -------------------------------------
COL = 3.5          # IEEEtran column width (252 pt)
FULL = 7.16        # IEEEtran text width (516 pt)
SUPP = 6.7         # supplement (article, letter, 0.9 in margins) text width

# ------------------------------------------------------------------ type sizes (pt, at final size) -----------------------------
FS_TEXT = 8.0      # axis labels, legends, panel titles
FS_TICK = 7.5      # tick labels
FS_NOTE = 7.0      # in-plot annotations, cell values (smallest size used anywhere)

# ------------------------------------------------------------------ colours -----------------------------------------------------
INK = "#222222"    # text, axes
MUTED = "#6b6b6b"  # secondary text, reference lines
GRID = "#e5e5e5"   # grid, separators
LIGHT = "#f2f2f2"  # row bands

# one fixed colour per method family (used in every figure of both papers)
OURS = "#0F4D92"       # ours, full data (three-way); house "blue_main"
OURS_ARM = "#5B9BD5"   # ours, FF++-only exposure arms (same family, lighter)
BINARY = "#E69F00"     # binary control (our architecture and data, two classes)
CLIP = "#CC79A7"       # published CLIP-based detectors (UnivFD, Effort, Forensics Adapter, GenD, DFD-HR)
CNN = "#8C8C8C"        # published CNN detectors (DeepfakeBench set, SBI, CADDM, LAA-Net, NPR)
FAMILY = {"ours": OURS, "arm": OURS_ARM, "binary": BINARY, "clip": CLIP, "cnn": CNN}
CLIP_DETECTORS = {"univfd", "effort", "fadapter", "gend", "dfdhr"}

# class / outcome colours (Okabe-Ito); never used for a method family
REAL = "#009E73"       # genuine, or a correct decision
FAKE = "#D55E00"       # forged, or an error
OK, ERR = REAL, FAKE
HILITE = "#FFD700"     # single call-out (map region contour)
TRUTH = "#56B4E9"      # ground-truth footprint contour

SEQ_CMAP = "Blues"     # sequential colour scale (confusion matrices)
MAP_CMAP = "YlOrRd"     # saliency / evidence maps (drawn with value-dependent opacity)


def family_of(key):
    return "clip" if key in CLIP_DETECTORS else "cnn"


def apply():
    matplotlib.use("Agg")
    plt.rcParams.update({
        "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": FS_TEXT, "axes.titlesize": FS_TEXT, "axes.labelsize": FS_TEXT, "legend.fontsize": FS_NOTE + 0.5,
        "xtick.labelsize": FS_TICK, "ytick.labelsize": FS_TICK, "figure.titlesize": FS_TEXT,
        "axes.linewidth": 0.6, "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": INK, "ytick.color": INK, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5, "xtick.major.pad": 2, "ytick.major.pad": 2,
        "axes.labelpad": 2.5, "axes.titlepad": 3, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": False, "grid.color": GRID, "grid.linewidth": 0.5,
        "legend.frameon": False, "legend.handlelength": 1.2, "legend.handletextpad": 0.4, "legend.borderaxespad": 0.2,
        "lines.linewidth": 1.0, "lines.markersize": 4, "patch.linewidth": 0.5,
        "figure.dpi": 150, "savefig.dpi": 300, "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "figure.constrained_layout.h_pad": 0.02, "figure.constrained_layout.w_pad": 0.02,
        "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold",
    })


def frame(ax, color=MUTED, lw=0.5):
    """Thin frame and no ticks, for image tiles."""
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True); s.set_color(color); s.set_linewidth(lw)


def save(fig, stem, png=True):
    """Vector PDF at the drawn size (no tight cropping, so the printed size equals the figure size) plus a 300 dpi PNG preview."""
    stem = Path(stem); stem.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(stem.with_suffix(".pdf"))
    if png:
        fig.savefig(stem.with_suffix(".png"), dpi=300)
    plt.close(fig)
    return stem.with_suffix(".pdf")


def overlay(img, hm):
    """Saliency / evidence map over a photo, identical in every qualitative figure: the photo slightly dimmed, the map in MAP_CMAP
    with opacity growing with the (0-1 normalised) map value, so low values leave the photo visible. Returns float RGB in [0, 1]."""
    import numpy as np
    hm = np.clip(np.asarray(hm, np.float32), 0, 1)
    rgb = plt.get_cmap(MAP_CMAP)(hm)[..., :3]; a = (0.75 * hm ** 0.8)[..., None]
    im = np.asarray(img, np.float32) / 255
    base = 0.8 * im + 0.2 * im.mean(2, keepdims=True)
    return np.clip((1 - a) * base * 0.9 + a * rgb, 0, 1)


def footprint(ax, img, gt, fill=True):
    """True edit footprint: blue contour (and a light blue fill on the footprint panel itself)."""
    if img is not None:
        ax.imshow(img)
    if fill:
        ax.contourf(gt, levels=[0.5, 1.5], colors=[TRUTH], alpha=0.25)
        ax.contour(gt, levels=[0.5], colors=[TRUTH], linewidths=1.0)
    else:
        ax.contour(gt, levels=[0.5], colors=[TRUTH], linewidths=0.7, linestyles=[(0, (2.2, 1.4))])


def region(ax, reg):
    """Region cut from a map (same area as the footprint): yellow contour."""
    ax.contour(reg, levels=[0.5], colors=[HILITE], linewidths=1.0)
