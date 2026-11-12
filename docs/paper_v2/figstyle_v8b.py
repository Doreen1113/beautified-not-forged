"""Additions to figstyle.py shared by the v8b figures of main_v8.tex (make_fig_*_v8b.py, 2026-10-22).

figstyle.py stays the single source of fonts, sizes, spines and the family colours OURS / CLIP / CNN. This module adds what the
v8b set needs on top of it and nothing else: the colour of the generated-image detectors (Okabe-Ito sky blue, the one family
figstyle has no entry for), one marker per family so the families stay apart in grey print, the ordered detector registry
(key in main_claim_A.json, key in fair_cdfb.json, printed name, family) in the paper's order, the panel tag and the common
reference-line style.

    import figstyle as FS, figstyle_v8b as V; FS.apply(); ...; V.tag(ax, "a")
"""
import figstyle as FS

GEN = "#56B4E9"                                        # generated-image detectors (UnivFD, NPR); Okabe-Ito sky blue
COLOR = {"cnn": FS.CNN, "gen": GEN, "clip": FS.CLIP, "ours": FS.OURS}
MARK = {"cnn": "o", "gen": "D", "clip": "s", "ours": "*"}
FAMILY_LABEL = {"cnn": "face-forgery CNN", "gen": "generated-image detector", "clip": "CLIP-based detector", "ours": "ours, three-way"}

# (key in alipair_zeroshot_20260929/main_claim_A.json rows, key in celebdfb_v2_20260927/fair_cdfb.json, printed name, family),
# in the order of Sec. 2 of the paper: eleven face-forgery CNNs, two generated-image detectors, four CLIP-based, ours (two seeds).
DETECTORS = [
    ("xception", "xception", "Xception", "cnn"), ("effnb4", "effnb4", "EfficientNet-B4", "cnn"), ("f3net", "f3net", "F3Net", "cnn"),
    ("spsl", "spsl", "SPSL", "cnn"), ("ucf", "ucf", "UCF", "cnn"), ("recce", "recce", "RECCE", "cnn"), ("core", "core", "CORE", "cnn"),
    ("srm", "srm", "SRM", "cnn"), ("sbi", "sbi", "SBI", "cnn"), ("caddm", "caddm", "CADDM", "cnn"), ("laanetr", "laanetr", "LAA-Net", "cnn"),
    ("univfd", "univfd", "UnivFD", "gen"), ("npr", "npr", "NPR", "gen"),
    ("effort", "effort", "Effort", "clip"), ("fadapter", "fadapter", "Forensics Adapter", "clip"), ("gend", "gend", "GenD", "clip"),
    ("dfdhr", "dfdhr", "DFD-HR", "clip"),
    ("ours main s1", "RU-clipe5", "Ours (seed 1)", "ours"), ("ours main s2", "RU-clipe5-s2", "Ours (seed 2)", "ours"),
]

REF_LS = (0, (3, 2))      # dashed reference lines
REF_LW = 0.6


def tag(ax, letter, x=-0.02, y=1.02, **kw):
    """Bold panel tag "(a)" just outside the top-left corner of an axes (axes fraction coordinates)."""
    kw.setdefault("fontsize", FS.FS_TEXT + 0.5)
    ax.text(x, y, f"({letter})", transform=ax.transAxes, ha="right", va="bottom", fontweight="bold", color=FS.INK, **kw)


def fig_tag(fig, letter, x, y, **kw):
    """Same tag placed in figure inches (for panels made of image tiles without a common axes)."""
    w, h = fig.get_size_inches()
    kw.setdefault("fontsize", FS.FS_TEXT + 0.5)
    fig.text(x / w, y / h, f"({letter})", ha="left", va="bottom", fontweight="bold", color=FS.INK, **kw)


def legend_handles(families=("cnn", "gen", "clip", "ours")):
    import matplotlib.lines as ml
    return [ml.Line2D([], [], ls="", marker=MARK[f], color=COLOR[f], markersize=5 if f != "ours" else 8,
                      markeredgecolor="white", markeredgewidth=0.4, label=FAMILY_LABEL[f]) for f in families]
