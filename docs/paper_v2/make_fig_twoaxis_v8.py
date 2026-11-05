"""Fig. "both axes at once" of main_v8.tex (fig_twoaxis_v8): the seventeen published detectors and our three-way model (two
seeds) on the two directions of the measurement.

x: Direction A, false alarms on Smoothing-90 renders at the threshold that accuses 5 % of the originals
   (results/research/alipair_zeroshot_20260929/main_claim_A.json, rows[*].fa_s90_at_5pct, CI fa_ci).
y: Direction B, beautification-only miss rise on Celeb-DF-B
   (results/research/celebdfb_v2_20260927/fair_cdfb.json, [*].d_miss_beauty_only, CI ci.d_miss_beauty_only).
Marker area: untreated Celeb-DF-B frame AUC (fair_cdfb.json [*].auc_untreated).
Usage: python make_fig_twoaxis_v8.py   (writes figs/fig_twoaxis_v8.pdf and .png)
"""
import json
from pathlib import Path

import matplotlib.pyplot as plt

import figstyle as FS

ROOT = Path(__file__).resolve().parents[2]
A = json.load(open(ROOT / "results/research/alipair_zeroshot_20260929/main_claim_A.json"))["rows"]
B = json.load(open(ROOT / "results/research/celebdfb_v2_20260927/fair_cdfb.json"))

# (key in main_claim_A, key in fair_cdfb, printed name, family)
DET = [
    ("xception", "xception", "Xception", "cnn"), ("effnb4", "effnb4", "EffNet-B4", "cnn"), ("f3net", "f3net", "F3Net", "cnn"),
    ("spsl", "spsl", "SPSL", "cnn"), ("ucf", "ucf", "UCF", "cnn"), ("recce", "recce", "RECCE", "cnn"), ("core", "core", "CORE", "cnn"),
    ("srm", "srm", "SRM", "cnn"), ("sbi", "sbi", "SBI", "cnn"), ("caddm", "caddm", "CADDM", "cnn"), ("laanetr", "laanetr", "LAA-Net", "cnn"),
    ("univfd", "univfd", "UnivFD", "gen"), ("npr", "npr", "NPR", "gen"),
    ("effort", "effort", "Effort", "clip"), ("fadapter", "fadapter", "Forensics Ad.", "clip"), ("gend", "gend", "GenD", "clip"),
    ("dfdhr", "dfdhr", "DFD-HR", "clip"),
    ("ours main s1", "RU-clipe5", "Ours s1", "ours"), ("ours main s2", "RU-clipe5-s2", "Ours s2", "ours"),
]
COLOR = {"cnn": FS.CNN, "gen": FS.BINARY, "clip": FS.CLIP, "ours": FS.OURS}
MARK = {"cnn": "o", "gen": "D", "clip": "s", "ours": "*"}
# label offsets (points) chosen by hand so that no two labels overlap at column width
OFF = {"Xception": (5, 0), "EffNet-B4": (4, -8), "F3Net": (-1, -9), "SPSL": (-5, 5), "UCF": (-5, 1), "RECCE": (-5, 1),
       "CORE": (4, 3), "SRM": (4, 1), "SBI": (5, 1), "CADDM": (5, -2), "LAA-Net": (-5, 1), "UnivFD": (5, -1), "NPR": (0, -8),
       "Effort": (5, -6), "Forensics Ad.": (5, 1), "GenD": (0, -9), "DFD-HR": (-5, -7), "Ours s1": (6, -2), "Ours s2": (6, 1)}
HA = {"SPSL": "right", "RECCE": "right", "DFD-HR": "right", "UCF": "right", "LAA-Net": "right", "F3Net": "center",
      "GenD": "center", "NPR": "center"}


def main():
    FS.apply()
    fig, ax = plt.subplots(figsize=(FS.COL, 2.35), layout="constrained")
    ax.axvline(5, color=FS.MUTED, lw=0.6, ls=(0, (3, 2)), zorder=0)
    ax.axhline(0, color=FS.MUTED, lw=0.6, ls=(0, (3, 2)), zorder=0)
    ax.text(5.5, 24.5, "5 % FPR floor", color=FS.MUTED, fontsize=FS.FS_NOTE, va="top", ha="left")
    seen = set()
    for ka, kb, name, fam in DET:
        x = A[ka]["fa_s90_at_5pct"]; xlo, xhi = A[ka]["fa_ci"]
        y = B[kb]["d_miss_beauty_only"]; ylo, yhi = B[kb]["ci"]["d_miss_beauty_only"]
        auc = B[kb]["auc_untreated"]
        size = 10 + 110 * max(auc - 0.5, 0) ** 1.5 * 2   # 0.50 -> 10, 0.94 -> ~72 (marker area, pt^2)
        if fam == "ours":
            size *= 2.2
        ax.errorbar(x, y, xerr=[[x - xlo], [xhi - x]], yerr=[[y - ylo], [yhi - y]], fmt="none", ecolor=COLOR[fam],
                    elinewidth=0.5, capsize=0, alpha=0.7, zorder=1)
        label = {"cnn": "face-forgery CNN", "gen": "generated-image detector", "clip": "CLIP ViT-L/14 detector",
                 "ours": "ours, three-way (two seeds)"}[fam]
        ax.scatter([x], [y], s=size, marker=MARK[fam], color=COLOR[fam], edgecolor="white", linewidth=0.4, zorder=3,
                   label=label if fam not in seen else None)
        seen.add(fam)
        dx, dy = OFF[name]
        ax.annotate(name, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=FS.FS_NOTE, ha=HA.get(name, "left"),
                    va="center", color=FS.INK if fam != "cnn" else FS.MUTED, zorder=4)
    ax.set_xlim(-2, 74); ax.set_ylim(-10, 26)
    ax.set_xlabel("Direction A: Smoothing-90 renders accused (%) at 5 % FPR")
    ax.set_ylabel("Direction B: miss rise from\nbeautification alone (points)")
    ax.legend(loc="lower right", fontsize=FS.FS_NOTE, markerscale=0.8, handletextpad=0.3, borderpad=0.2)
    FS.save(fig, Path(__file__).parent / "figs" / "fig_twoaxis_v8")
    print("written figs/fig_twoaxis_v8.pdf/.png")


if __name__ == "__main__":
    main()
