"""Training curves and train / val / test confusion matrices of the two main models (every value read from results files):
  fig_training   - per epoch: training loss, FF++ validation macro-F1, commercial-validation filter F1; the selected epoch
                   (max of the selection criterion 0.5 * (FF++ macro-F1 + commercial filter F1)) is marked
  fig_confusion  - FF++ three-way confusion matrices (row-normalised) on the training sample, validation and test split

python docs/paper_v2/make_fig_training.py   (after results/research/retouch_unified_20260929/split_eval.py)
"""
import csv
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

B = Path(r"C:\My_Project\AIGC"); RU = B / "results/research/retouch_unified_20260929"; OUT = B / "docs/paper_v2/figs"
sys.path.insert(0, str(B / "docs/paper_v2"))
import make_figures as MF  # noqa: E402

MODELS = [("Ours (CLIP + LoRA)", "clipe4_s20260929", MF.C_OURS),
          ("Ours-lite (EffNet-B4)", "ru4e_effb4_s20260929", MF.C_OURS2)]


def log(tag):
    with open(RU / f"train_ru_{tag}.csv", encoding="utf-8") as f:
        r = list(csv.DictReader(f))
    return {k: np.array([float(x[k]) for x in r]) for k in r[0]}


def fig_training():
    fig, axs = plt.subplots(1, 3, figsize=(7.0, 1.95))
    panels = [("loss", "training loss", None), ("ffpp_val_f1", "FF++ val. macro-F1", (0.5, 1.0)),
              ("vendor_val_f1", "commercial val. filter F1", (0.5, 1.0))]
    sel = {}
    for name, tag, col in MODELS:
        L = log(tag); crit = 0.5 * (L["ffpp_val_f1"] + L["vendor_val_f1"]); k = int(np.argmax(crit)); sel[tag] = int(L["epoch"][k])
        for ax, (key, lab, lim) in zip(axs, panels):
            ax.plot(L["epoch"], L[key], "-o", color=col, ms=2.5, lw=1.4, label=name)
            ax.plot(L["epoch"][k], L[key][k], "*", color=col, ms=9, mec="white", mew=0.6, zorder=5)
    for ax, (key, lab, lim) in zip(axs, panels):
        ax.set_title(lab, fontsize=8.5); ax.set_xlabel("epoch", fontsize=8); ax.tick_params(labelsize=7)
        ax.set_xticks([1, 4, 8, 12])
        ax.grid(alpha=0.25, lw=0.5); ax.spines[["top", "right"]].set_visible(False)
        if lim:
            ax.set_ylim(*lim)
    axs[0].legend(fontsize=6.5, frameon=False, loc="upper right")
    fig.tight_layout(pad=0.4, w_pad=1.0)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_training.{ext}", dpi=300)
    plt.close(fig); return sel


def fig_confusion():
    fig, axs = plt.subplots(2, 3, figsize=(5.6, 3.7))
    lab = ["real", "fake", "filter"]
    J = json.loads((RU / "split_eval.json").read_text())
    for r, (name, tag, _) in enumerate(MODELS):
        for c, sp in enumerate(("train", "val", "test")):
            cm = np.array(J[name.split(" (")[0]][f"ffpp/{sp}"]["confusion"], float); n = cm.sum(1, keepdims=True); cmn = cm / n * 100
            ax = axs[r, c]; ax.imshow(cmn, cmap="Blues", vmin=0, vmax=100)
            for i in range(3):
                for j in range(3):
                    ax.text(j, i, f"{cmn[i, j]:.1f}", ha="center", va="center", fontsize=7, color="white" if cmn[i, j] > 55 else "#1d1f24")
            ax.set_xticks(range(3)); ax.set_yticks(range(3)); ax.set_xticklabels(lab, fontsize=6.5); ax.set_yticklabels(lab, fontsize=6.5)
            ax.tick_params(length=0)
            if r == 0:
                ax.set_title({"train": "training sample", "val": "validation", "test": "test"}[sp] + f"\n(n = {int(cm.sum()):,})", fontsize=7.5)
            else:
                ax.set_title(f"(n = {int(cm.sum()):,})", fontsize=7.5)
            if c == 0:
                ax.set_ylabel(name + "\ntrue class", fontsize=7)
            if r == 1:
                ax.set_xlabel("predicted", fontsize=7)
    fig.tight_layout(pad=0.3, h_pad=0.6, w_pad=0.4)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"fig_confusion.{ext}", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    print("selected epochs", fig_training())
    if (RU / "split_eval.json").is_file():
        fig_confusion()
