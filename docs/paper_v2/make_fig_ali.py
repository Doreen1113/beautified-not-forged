"""Commercial-retouching figures (every value read from results files):
  fig_alibars   - Alibaba originals and the four operations (levels pooled): share routed to real / fake / filter, per model
  fig_accuse    - published FF++ detectors vs ours: retouched genuine faces called fake at 5 % FPR on originals
  fig_tradeoff  - forgery detection (Celeb-DF-B untreated AUC) vs commercial-retouching balanced accuracy, per model

python docs/paper_v2/make_fig_ali.py
"""
import json
import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

B = Path(r"C:\My_Project\AIGC"); R = B / "results/research"
sys.path.insert(0, str(B / "docs/paper_v2"))
import make_figures as MF  # noqa: E402

A = json.loads((R / "alipair_zeroshot_20260929/results.json").read_text())
RUJ = {t: json.loads((R / f"retouch_unified_20260929/eval_ru_{t}.json").read_text())["ali"] for t in
       ("effb4_s20260929", "repvit_s20260929", "ru2_effb4_s20260929", "ru2_effb4_s20260930", "clipe_s20260929", "clipe_s20260930", "clipe4_s20260929", "ru4e_effb4_s20260929")}
CB = json.loads((R / "celebdfb_v2_20260927/results_v3.json").read_text())
OPS = [("EyeEnlarging", "eye enl."), ("FaceLifting", "lifting"), ("Whitening", "whitening"), ("Smoothing", "smoothing")]
C_REAL, C_FAKE, C_FILT = "#7fae8c", MF.C_SBI, "#d9b04c"


def pooled(res, op):
    g = [res["by_group"][f"{op}_{lv}"] for lv in (30, 60, 90)]
    return [float(np.mean([x[k] for x in g])) for k in ("to_real", "to_fake", "to_filter")]


def fig_alibars():
    models = [("FF++ only, best\n(\\ours{}-SUP)".replace("\\ours{}", "Ours"), A["SUP-F"]), ("FF++ only,\nevidence head", A["MASK"]),
              ("Ours-lite\n(EffNet-B4)", RUJ["ru4e_effb4_s20260929"]), ("Ours\n(CLIP + LoRA)", RUJ["clipe4_s20260929"])]
    cats = [("untouched\noriginals", None)] + [(lab, op) for op, lab in OPS]
    fig, ax = plt.subplots(figsize=(7.0, 2.35))
    w = 0.19; x0 = np.arange(len(cats))
    for m, (name, res) in enumerate(models):
        for c, (clab, op) in enumerate(cats):
            if op is None:
                o = res["orig"]; v = [o["real"], o["fake"], o["filter"]]
            else:
                v = pooled(res, op)
            x = x0[c] + (m - 1.5) * (w + 0.02); bot = 0
            for val, col in zip(v, (C_REAL, C_FAKE, C_FILT)):
                ax.bar(x, val, w, bottom=bot, color=col, edgecolor="white", linewidth=0.6); bot += val
            if c == 0:
                ax.text(x, 103, ["SUP", "head", "lite", "ours"][m], ha="center", fontsize=5.8, color=MF.INK)
    ax.set_xticks(x0, [c for c, _ in cats], fontsize=7); ax.set_ylim(0, 110); ax.set_ylabel("% of images routed to")
    ax.set_yticks([0, 25, 50, 75, 100])
    for c in range(1, len(cats)):
        ax.axvline(c - 0.5, color=MF.GRID, lw=0.8)
    h = [plt.Rectangle((0, 0), 1, 1, color=col) for col in (C_REAL, C_FAKE, C_FILT)]
    ax.legend(h, ["real", "fake", "filter"], ncol=3, fontsize=7, loc="upper right", bbox_to_anchor=(1.0, 1.2))
    ax.text(0.0, 1.14, "bars per group: FF++-only best (SUP), FF++-only evidence head, Ours-lite, Ours", transform=ax.transAxes, fontsize=6.3, color=MF.MUTED)
    fig.tight_layout(); MF.save(fig, "fig_alibars")


def fig_tradeoff():
    pts = [("\\ours{}-S", "RepViT", "ours_repvit20", A["RepViT"]["pooled"]["balanced_acc"], "o", MF.C_BIN),
           ("SUP", "SUP-F", "SUP-F", A["SUP-F"]["pooled"]["balanced_acc"], "o", MF.C_BIN),
           ("HYB", "HYB", "HYB-L-s2", A["HYB"]["pooled"]["balanced_acc"], "o", MF.C_BIN),
           ("HYB-F", "HYB-F", "HYB-F", A["HYB-F"]["pooled"]["balanced_acc"], "o", MF.C_BIN),
           ("HYB-D", "HYB-D", "HYBD-F", A["HYB-D"]["pooled"]["balanced_acc"], "o", MF.C_BIN),
           ("evidence head", "MASK", "cgd_MASK", A["MASK"]["pooled"]["balanced_acc"], "o", MF.C_BIN),
           ("RU1 RepViT", None, "RU-repvit", RUJ["repvit_s20260929"]["pooled"]["balanced_acc"], "^", MF.C_OURS2),
           ("RU1", None, "RU-effb4", RUJ["effb4_s20260929"]["pooled"]["balanced_acc"], "s", MF.C_OURS2),
           ("RU2 s1", None, "RU2-effb4", RUJ["ru2_effb4_s20260929"]["pooled"]["balanced_acc"], "D", MF.C_OURS),
           ("RU2 s2", None, "RU2-effb4-s2", RUJ["ru2_effb4_s20260930"]["pooled"]["balanced_acc"], "D", MF.C_OURS),
           ("CLIP s1", None, "RU-clipe", RUJ["clipe_s20260929"]["pooled"]["balanced_acc"], "P", MF.C_OURS),
           ("CLIP s2", None, "RU-clipe-s2", RUJ["clipe_s20260930"]["pooled"]["balanced_acc"], "P", MF.C_OURS),
           ("unified", None, "RU-clipe4", RUJ["clipe4_s20260929"]["pooled"]["balanced_acc"], "*", MF.C_OURS)]
    fig, ax = plt.subplots(figsize=(3.45, 2.6))
    ax.axhspan(45, 55, color="#f1f1f1", lw=0); ax.text(0.745, 45.8, "chance band", fontsize=6, color=MF.MUTED, va="center")
    ax.axvline(CB["sbi"]["auc_untreated"], color=MF.C_SBI, lw=1.0, ls="--")
    ax.axvline(CB["effort"]["auc_untreated"], color=MF.C_SBI, lw=0.8, ls=":"); ax.text(CB["effort"]["auc_untreated"] + 0.002, 46.5, "Effort / F. Adapter", fontsize=5.4, color=MF.C_SBI, va="bottom", ha="left")
    ax.text(CB["sbi"]["auc_untreated"] - 0.002, 77.3, "official SBI\n(binary, no filter class)", fontsize=5.6, color=MF.C_SBI, va="top", ha="right")
    OFF = {"HYB-F": (-0.004, -2.4, "right"), "SUP": (0.003, -1.9, "left"), "evidence head": (0.0, -2.6, "center"),
           "HYB-D": (0.004, 0.7, "left"), "HYB": (-0.003, 0.8, "right"), "RU1 RepViT": (-0.004, 0.3, "right"),
           "RU1": (0.003, -1.9, "left"), "RU2 s1": (0.004, 0.2, "left"), "RU2 s2": (0.004, -1.3, "left"),
           "CLIP s1": (0.003, 0.4, "left"), "CLIP s2": (0.003, -1.6, "left"), "unified": (0.0, -2.6, "center")}
    for lab, _, cbk, y, mk, col in pts:
        x = CB[cbk]["auc_untreated"]
        ax.scatter([x], [y], s=(90 if mk == "*" else 30), marker=mk, color=col, edgecolor="white", linewidth=0.7, zorder=5)
        dx, dy, ha = OFF.get(lab, (0.003, 0.6, "left"))
        ax.text(x + dx, y + dy, lab.replace("\\ours{}", "Ours"), fontsize=5.6, color=MF.INK, ha=ha)
    ax.set_xlabel("forgery detection: Celeb-DF-B AUC")
    ax.set_ylabel("commercial retouching:\nbalanced accuracy (%)")
    ax.set_xlim(0.74, 0.95); ax.set_ylim(44, 78); ax.grid(True, color=MF.GRID, lw=0.5)
    fig.tight_layout(); MF.save(fig, "fig_tradeoff")


def fig_accuse():
    """Published FF++-trained detectors vs ours: share of commercially retouched genuine faces called fake at a threshold that
    keeps each model's untouched-original false-positive rate at 5 % (chosen on the test originals themselves)."""
    P = json.loads((R / "alipair_zeroshot_20260929/published_ali.json").read_text())
    rows = [(MF.NICE[d], P[d]) for d in ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter"]] + \
           [("three-way, FF++ only\n(evidence head)", P["ours MASK"]), ("Ours-lite (EffNet-B4)", P["ours lite"]), ("Ours (CLIP + LoRA)", P["ours main"])]
    fig, ax = plt.subplots(figsize=(3.45, 2.95))
    y = np.arange(len(rows))[::-1]
    for yy, (lab, v) in zip(y, rows):
        col = MF.C_SBI if lab in ("SBI", "Effort", "Forensics Adapter") else (MF.C_OURS if lab.startswith("Ours") else MF.C_BIN)
        ax.barh(yy + 0.2, v["by_op"]["Smoothing_90"]["fake_at_t"], 0.38, color=col, alpha=1.0)
        ax.barh(yy - 0.2, v["ret_fake_at_t"], 0.38, color=col, alpha=0.45)
        ax.text(v["by_op"]["Smoothing_90"]["fake_at_t"] + 1, yy + 0.2, f'{v["by_op"]["Smoothing_90"]["fake_at_t"]:.0f}', va="center", fontsize=5.6, color=MF.INK)
    ax.axvline(5, color=MF.MUTED, lw=0.8, ls="--"); ax.text(5.8, y[0] + 0.75, "5% on untouched originals", fontsize=5.4, color=MF.MUTED)
    ax.set_yticks(y, [r[0] for r in rows], fontsize=6.2); ax.set_xlabel("retouched genuine faces called fake (%)"); ax.set_xlim(0, 70)
    h = [plt.Rectangle((0, 0), 1, 1, color=MF.C_BIN), plt.Rectangle((0, 0), 1, 1, color=MF.C_BIN, alpha=0.45)]
    ax.legend(h, ["strongest smoothing", "all operations"], fontsize=6, loc="lower right")
    fig.tight_layout(); MF.save(fig, "fig_accuse")


if __name__ == "__main__":
    fig_alibars(); fig_tradeoff(); fig_accuse(); print("ali figures ok")
