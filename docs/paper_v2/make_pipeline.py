"""Method overview figure (fig_pipeline): HYB training triplet (left) and three-way vs binary inference (right).

python docs/paper_v2/make_pipeline.py
"""
import sys
from pathlib import Path

import cv2
import matplotlib
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BASE = Path(r"C:\My_Project\AIGC")
sys.path.insert(0, str(BASE / "docs/paper_v2")); sys.path.insert(0, str(BASE / "results/research/sbifix_20260927"))
import make_figures as MF  # noqa: E402
from sbi_faithful import beautify, self_blend  # noqa: E402

GREEN, AMBER, RED, BLUE = "#2f7d32", "#8a6d00", "#B64342", "#0F4D92"


def thumbs():
    z = np.load(BASE / "results/research/fasb_20260926/landmarks_train.npz")
    stem = sorted(z.files)[20000]
    rgb = cv2.imread(str(BASE / "FaceForensics_protocol_frames_dense/train/real" / f"{stem}.jpg"))[..., ::-1].copy()
    rng = np.random.default_rng(7); sb = None
    while sb is None:
        sb = self_blend(rgb, z[stem], rng)
    obs = [l.split("\t")[0] for l in (BASE / "results/research/ffpp_unified_20260925/ffpp3_train.txt").read_text(encoding="utf-8").splitlines()[1:]
           if l.split("\t")[1:2] == ["1"]]
    of = cv2.imread(obs[len(obs) // 3])[..., ::-1]
    obf = [l.split("\t")[0] for l in (BASE / "results/research/ffpp_unified_20260925/ffpp3_train.txt").read_text(encoding="utf-8").splitlines()[1:]
           if l.split("\t")[1:2] == ["2"] and "eye_enlarging" in l]
    ofl = cv2.imread(obf[len(obf) // 2])[..., ::-1]
    r = lambda im: cv2.resize(np.ascontiguousarray(im), (100, 120))
    return {"real": r(rgb), "beaut": r(beautify(rgb, np.random.default_rng(3))), "sb": r(sb),
            "sbb": r(beautify(sb, np.random.default_rng(3))), "obs": r(of), "obsf": r(ofl)}


def box(ax, x, y, w, h, text, fc, ec, fs=7, bold=False, tc=None):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=1.0))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc or MF.INK,
            fontweight="bold" if bold else "normal")


def arrow(ax, a, b, c=MF.INK, lw=1.0, style="-|>"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=style, mutation_scale=8, color=c, lw=lw, shrinkA=1, shrinkB=1))


def img(ax, im, x, y, w=0.9, h=1.08, ec=None):
    ax.imshow(im, extent=(x, x + w, y, y + h), zorder=3)
    if ec:
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=False, ec=ec, lw=1.6, zorder=4))


def main():
    t = thumbs()
    fig, ax = plt.subplots(figsize=(7.1, 3.05))
    ax.set_xlim(0, 14.6); ax.set_ylim(0, 6.1); ax.axis("off")
    # ---- left: training
    ax.text(0.1, 5.85, "Training: one FF++ photograph $\\rightarrow$ a triplet (every step)", fontsize=8, fontweight="bold", color=MF.INK)
    img(ax, t["real"], 0.15, 2.55, ec=GREEN); ax.text(0.6, 2.35, "genuine", ha="center", fontsize=6.5)
    rows = [(4.3, "real", GREEN, [("real", t["real"])]),
            (2.65, "filter", AMBER, [("beautify", t["beaut"]), ("observed", t["obsf"])]),
            (1.0, "fake", RED, [("self-blend", t["sb"]), ("+ beautify", t["sbb"]), ("observed", t["obs"])])]
    for y, lab, col, ims in rows:
        arrow(ax, (1.1, 3.1), (1.65, y + 0.54), MF.MUTED)
        for k, (cap, im) in enumerate(ims):
            x = 1.7 + k * 1.02
            img(ax, im, x, y, ec=col); ax.text(x + 0.45, y - 0.18, cap, ha="center", fontsize=5.8, color=MF.INK)
        ax.text(1.7 + len(ims) * 1.02 + 0.05, y + 0.54, lab, fontsize=7.5, color=col, fontweight="bold", va="center")
    ax.text(3.2, 0.22, "p = 0.5 each branch; a beautified forgery stays $\\it{fake}$", fontsize=6.2, ha="center", color=MF.MUTED)
    box(ax, 5.95, 2.3, 1.55, 1.55, "EffNet-B4\n380 px\nSGD + SAM", "#eef3fa", BLUE, fs=6.6)
    for y in (4.84, 3.19, 1.54):
        arrow(ax, (5.45, y), (5.95, 3.07), MF.MUTED)
    box(ax, 7.75, 2.55, 1.0, 1.05, "3-way\nhead", "#eef3fa", BLUE, fs=7, bold=True, tc=BLUE)
    arrow(ax, (7.5, 3.07), (7.75, 3.07), BLUE)
    ax.plot([9.0, 9.0], [0.2, 5.9], color="#d0d0d0", lw=0.8)
    # ---- right: inference contrast
    ax.text(9.15, 5.85, "Inference on a beautified face", fontsize=8, fontweight="bold", color=MF.INK)
    ax.text(9.15, 5.35, "binary detector (one threshold $t$)", fontsize=6.8, color=MF.C_SBI, fontweight="bold")
    box(ax, 9.15, 4.0, 2.55, 1.1, "beautified genuine\ncalled fake\n(false accusation)", "#fbeeee", MF.C_SBI, fs=6.2)
    box(ax, 11.95, 4.0, 2.55, 1.1, "beautified deepfake\ncalled real\n(escape)", "#fbeeee", MF.C_SBI, fs=6.2)
    ax.text(11.85, 3.62, "lowering $t$ trades one error for the other", ha="center", fontsize=6.0, color=MF.MUTED)
    ax.text(9.15, 3.05, "ours (three-way, argmax)", fontsize=6.8, color=BLUE, fontweight="bold")
    img(ax, t["beaut"], 9.2, 1.6, ec=AMBER); img(ax, t["sbb"], 9.2, 0.25, ec=RED)
    box(ax, 10.65, 1.75, 1.4, 0.75, "filter", "#faf4e3", AMBER, fs=7.5, bold=True, tc=AMBER)
    box(ax, 10.65, 0.42, 1.4, 0.75, "fake", "#fbeeee", RED, fs=7.5, bold=True, tc=RED)
    arrow(ax, (10.15, 2.14), (10.65, 2.12), MF.INK); arrow(ax, (10.15, 0.79), (10.65, 0.8), MF.INK)
    ax.text(12.25, 2.12, "genuine, edited:\nnot accused", fontsize=6.2, va="center", color=MF.INK)
    ax.text(12.25, 0.8, "forgery found\nunder the filter", fontsize=6.2, va="center", color=MF.INK)
    MF.save(fig, "fig_pipeline")


if __name__ == "__main__":
    main(); print("ok")
