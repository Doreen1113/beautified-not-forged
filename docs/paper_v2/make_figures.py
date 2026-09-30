"""Figures for docs/paper_v2/main.tex. Every value is read from a results file; nothing is typed in.

python docs/paper_v2/make_figures.py -> docs/paper_v2/figs/*.pdf|png
"""
import json
import sys
from pathlib import Path

import cv2
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BASE = Path(r"C:\My_Project\AIGC")
OUT = BASE / "docs/paper_v2/figs"; OUT.mkdir(parents=True, exist_ok=True)
BENCH = BASE / "results/research/ffpp_benchmark_20260925"
CDFB = BASE / "results/research/celebdfb_v2_20260927"
PUB = ["xception", "effnb4", "spsl", "f3net", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter", "univfd", "npr"]
NICE = {"effort": "Effort", "fadapter": "Forensics Adapter", "xception": "Xception", "effnb4": "EffNet-B4", "spsl": "SPSL", "f3net": "F3Net", "ucf": "UCF", "recce": "RECCE",
        "core": "CORE", "srm": "SRM", "sbi": "SBI", "univfd": "UnivFD", "npr": "NPR"}
# figures4papers (ChenLiu-1996) conventions: blue = proposed, neutral grey = baselines, strong red = the baseline to
# beat; no top/right spines, minimal grid, frameless legends, heavier axes, 300 dpi, vector text.
INK, MUTED, GRID = "#272727", "#4d4d4d", "#e6e6e6"
C_BIN, C_SBI, C_OURS, C_OURS2 = "#b5b4b4", "#B64342", "#0F4D92", "#3775BA"
plt.rcParams.update({"font.family": ["Arial", "DejaVu Sans"], "font.size": 8.5, "axes.titlesize": 9,
                     "axes.labelsize": 8.5, "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.linewidth": 1.0,
                     "axes.edgecolor": INK, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "xtick.major.width": 1.0, "ytick.major.width": 1.0, "axes.spines.top": False,
                     "axes.spines.right": False, "axes.grid": False, "legend.frameon": False,
                     "pdf.fonttype": 42, "svg.fonttype": "none", "savefig.dpi": 300})


def curve(s_filter, s_escape):
    ts = np.unique(np.concatenate([s_filter, s_escape, [-1, 2]]))
    return np.array([(s_filter > t).mean() * 100 for t in ts]), np.array([(s_escape <= t).mean() * 100 for t in ts])


def save(fig, name):
    fig.savefig(OUT / f"{name}.pdf", bbox_inches="tight"); fig.savefig(OUT / f"{name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig_frontier():
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0))
    # (a) FF++ paired corpus
    ax = axes[0]
    for b in PUB:
        z = np.load(BENCH / f"scores_{b}.npz"); fa, ms = curve(z["filter"], z["escape"])
        ax.plot(fa, ms, color=C_SBI if b == "sbi" else C_BIN, lw=1.4 if b == "sbi" else 0.8, alpha=1 if b == "sbi" else 0.8,
                label="SBI (best binary cross-dataset)" if b == "sbi" else ("other 12 binary detectors" if b == "xception" else None))
    RU = BASE / "results/research/retouch_unified_20260929"
    m1 = json.load(open(RU / "eval_ru_clipe4_s20260929.json"))["ffpp"]; m2 = json.load(open(RU / "eval_ru_ru4e_effb4_s20260929.json"))["ffpp"]
    pts = [("Ours (CLIP ViT-L/14 + LoRA)", m1["FA"], m1["MISS"], C_OURS, "*"), ("Ours-lite (EfficientNet-B4)", m2["FA"], m2["MISS"], C_OURS2, "^")]
    for lab, fa, ms, c, mk in pts:
        ax.scatter([fa], [ms], s=(90 if mk == "*" else 34), color=c, marker=mk, zorder=5, edgecolor="white", linewidth=0.8, label=lab)
        ax.add_patch(plt.Rectangle((0, 0), fa, ms, color=c, alpha=0.06, lw=0))
    ax.set(xlim=(0, 60), ylim=(0, 60), xlabel="beautified genuine faces called fake (%)",
           ylabel="beautified deepfakes called real (%)", title="(a) FF++ c23 test, paired beautification")
    ax.grid(True, color=GRID, lw=0.6)
    ins = ax.inset_axes([0.42, 0.42, 0.55, 0.52])   # zoom on the region where the three-way points sit
    for b in PUB:
        z = np.load(BENCH / f"scores_{b}.npz"); fa, ms = curve(z["filter"], z["escape"])
        ins.plot(fa, ms, color=C_SBI if b == "sbi" else C_BIN, lw=1.2 if b == "sbi" else 0.7)
    for lab, fa, ms, c, mk in pts:
        ins.scatter([fa], [ms], s=(80 if mk == "*" else 30), color=c, marker=mk, zorder=5, edgecolor="white", linewidth=0.8)
        ins.add_patch(plt.Rectangle((0, 0), fa, ms, color=c, alpha=0.10, lw=0))
    ins.set(xlim=(0, 16), ylim=(0, 8)); ins.tick_params(labelsize=6.5)
    for sp in ("top", "right"):
        ins.spines[sp].set_visible(True)
    ins.set_title("zoom", fontsize=7, pad=2)
    ax.indicate_inset_zoom(ins, edgecolor=MUTED)
    # (b) Celeb-DF-B external
    ax = axes[1]
    rows = [l.split("\t") for l in (BASE / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    folder = np.array([r[3] for r in rows])
    rb, sb = folder == "real_beautified", folder == "synthesis_beautified"
    for b in PUB:
        p = np.load(CDFB / "scores_v3" / f"{b}.npz")["p"][:, 1]; fa, ms = curve(p[rb], p[sb])
        ax.plot(fa, ms, color=C_SBI if b == "sbi" else C_BIN, lw=1.4 if b == "sbi" else 0.8, alpha=1 if b == "sbi" else 0.8)
    for n, lab, c, mk in (("RU-clipe4", "Ours (CLIP ViT-L/14 + LoRA)", C_OURS, "*"), ("RU4e-effb4", "Ours-lite (EfficientNet-B4)", C_OURS2, "^")):
        am = np.load(CDFB / "scores_v3" / f"{n}.npz")["p"].argmax(1)
        fa, ms = (am[rb] == 1).mean() * 100, (am[sb] == 0).mean() * 100
        ax.scatter([fa], [ms], s=(90 if mk == "*" else 34), color=c, marker=mk, zorder=5, edgecolor="white", linewidth=0.8)
        ax.add_patch(plt.Rectangle((0, 0), fa, ms, color=c, alpha=0.06, lw=0))
    ax.set(xlim=(0, 60), ylim=(0, 100), xlabel="beautified genuine frames called fake (%)",
           ylabel="beautified deepfake frames called real (%)", title="(b) Celeb-DF-B (third-party, zero-shot)")
    ax.grid(True, color=GRID, lw=0.6)
    h, l = axes[0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.07), fontsize=7)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save(fig, "fig_frontier")


def fig_escape():
    r = json.load(open(CDFB / "results_v3.json"))
    names = PUB[:] + ["SBI-F", "HYB-F", "RU-clipe4", "RU4e-effb4"]
    lab = {**NICE, "RU-clipe4": "Ours (CLIP + LoRA)", "RU4e-effb4": "Ours-lite (EffNet-B4)",
           "SBI-F": "SBI objective, our pipeline", "HYB-F": "three-way, same pipeline (FF++ only)"}
    names = [n for n in names if n in r]
    names.sort(key=lambda n: (n in PUB or n == "SBI-F", r[n]["dMISS"]))
    d = [r[n]["dMISS"] for n in names]; lo = [r[n]["ci"]["dMISS"][0] for n in names]; hi = [r[n]["ci"]["dMISS"][1] for n in names]
    fig, ax = plt.subplots(figsize=(3.3, 3.5))
    y = np.arange(len(names))
    col = [("#E9A6A1" if n == "SBI-F" else (C_OURS2 if n == "HYB-F" else C_OURS)) if n not in PUB else (C_SBI if n == "sbi" else C_BIN) for n in names]
    ax.barh(y, d, color=col, height=0.66, edgecolor=INK, linewidth=0.6)
    ax.errorbar(d, y, xerr=[np.array(d) - lo, np.array(hi) - d], fmt="none", ecolor=INK, elinewidth=0.7, capsize=1.5)
    ax.axvline(0, color=INK, lw=0.7)
    ax.set_yticks(y, [lab[n] for n in names]); ax.invert_yaxis(); ax.grid(axis="y", visible=False)
    ax.set_xlabel(r"$\Delta$ escape rate, beautified $-$ untreated (pp)")
    for yi, di, hi_ in zip(y, d, hi):
        ax.text(max(hi_, 0) + 0.8, yi, f"{di:+.1f}", va="center", fontsize=7, color=INK)
    ax.set_xlim(min(lo) - 2, max(hi) + 7)
    save(fig, "fig_escape")


def fig_samples():
    sys.path.insert(0, str(BASE / "results/research/sbifix_20260927"))
    from sbi_faithful import beautify, self_blend, shared_post
    z = np.load(BASE / "results/research/fasb_20260926/landmarks_train.npz")
    stem = sorted(z.files)[20000]
    rgb = cv2.imread(str(BASE / "FaceForensics_protocol_frames_dense/train/real" / f"{stem}.jpg"))[..., ::-1].copy()
    rng = np.random.default_rng(7)
    sb = None
    while sb is None:
        sb = self_blend(rgb, z[stem], rng)
    filt = beautify(rgb, np.random.default_rng(3))
    comp = beautify(sb, np.random.default_rng(3))
    vid = stem.split("__")[0]
    obs = [l.split("\t")[0] for l in (BASE / "results/research/ffpp_unified_20260925/ffpp3_train.txt").read_text(encoding="utf-8").splitlines()[1:]
           if l.split("\t")[1:2] == ["1"]]
    of = cv2.imread(obs[len(obs) // 3])[..., ::-1]
    ims = [("real", rgb, "real"), ("filter", filt, "beautified"), ("fake", sb, "self-blend"), ("fake", comp, "self-blend +\nbeautified"),
           ("fake", of, "observed FF++\nforgery")]
    fig, axes = plt.subplots(1, 5, figsize=(7.0, 1.9))
    for ax, (cls, im, cap) in zip(axes, ims):
        ax.imshow(cv2.resize(np.ascontiguousarray(im), (200, 240))); ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
        for s in ax.spines.values():
            s.set_visible(True); s.set_color({"real": "#2f7d32", "filter": "#8a6d00", "fake": "#b3261e"}[cls]); s.set_linewidth(2)
        ax.set_title(f"{cls}", fontsize=8, color={"real": "#2f7d32", "filter": "#8a6d00", "fake": "#b3261e"}[cls], fontweight="bold")
        ax.set_xlabel(cap, fontsize=7)
    fig.tight_layout()
    save(fig, "fig_samples")


if __name__ == "__main__":
    fig_frontier(); fig_escape(); fig_samples(); print("figures ->", OUT)
