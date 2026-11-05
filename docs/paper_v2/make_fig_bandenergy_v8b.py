"""fig_bandenergy_v8b (paper v8, 2026-10-22): restyle of fig_bandenergy (bandenergy_20261018/make_fig_bandenergy.py), column
width (3.5 x 2.45 in). Same data, same two panels:
(a) texture loss per smoothing form (-log high-frequency energy ratio, 0.25 cycles/px, 256-px view, mean and 95 % frame bootstrap):
    results/research/retouch_unified_20260929/bandenergy_20261018/bandenergy.json  loss_per_form["ehf0.25_view"][form].mean, .ci
    the commercial Smoothing-90 (hollow marker) comes from 200 FFHQ pairs, the seven scripted forms from 400 Celeb-DF-v2 frames.
(b) false-alarm rate of each published detector on each form, against that loss:
    bandenergy_20261018/fa_parsed.json  published[det].fa[form]; families bandenergy.json family[det]
    pooled Spearman over the detector x form points is recomputed here as in make_fig_bandenergy.py (NPR x Smoothing-90 excluded).

    python docs/paper_v2/make_fig_bandenergy_v8b.py  -> docs/paper_v2/figs/fig_bandenergy_v8b.{pdf,png}
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B / "docs/paper_v2"))
import figstyle as FS  # noqa: E402
import figstyle_v8b as V  # noqa: E402
FS.apply()
import matplotlib.pyplot as plt  # noqa: E402

OUT = B / "docs/paper_v2/figs"; HERE = B / "results/research/retouch_unified_20260929/bandenergy_20261018"
res = json.loads((HERE / "bandenergy.json").read_text(encoding="utf-8")); fa = json.loads((HERE / "fa_parsed.json").read_text(encoding="utf-8"))["published"]
FORMS = ["bil9", "bil15", "bil21", "median5", "gblend", "fl06", "fl12", "Smoothing_90"]
NAME = {"bil9": "bilateral d9", "bil15": "bilateral d15", "bil21": "bilateral d21", "median5": "median 5", "gblend": "Gaussian blend",
        "fl06": "face-local 6%", "fl12": "face-local 12%", "Smoothing_90": "service S-90"}
fam = res["family"]; PUB = list(fa)
L = res["loss_per_form"]["ehf0.25_view"]; x = {c: L[c]["mean"] for c in FORMS}
order = sorted(FORMS, key=lambda c: x[c])
pts = [(x[c], fa[d]["fa"][c], d, c) for c in FORMS for d in PUB if not (c == "Smoothing_90" and d == "npr")]
rho = stats.spearmanr([p[0] for p in pts], [p[1] for p in pts]).statistic
print("pooled Spearman", round(float(rho), 3))

fig = plt.figure(figsize=(FS.COL, 2.45), layout="constrained")
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.35], wspace=0.04)
# ---- (a) loss per form, ordered
ax = fig.add_subplot(gs[0])
for i, c in enumerate(order):
    lo, hi = L[c]["ci"]; m = L[c]["mean"]
    ax.plot([lo, hi], [i, i], color=FS.INK, lw=0.8, solid_capstyle="butt", zorder=2)
    ax.plot(m, i, marker="o", ms=4.2, color="white" if c == "Smoothing_90" else FS.INK, mec=FS.INK, mew=0.8, ls="", zorder=3)
    ax.text(-0.03, i, f"{i + 1}", ha="right", va="center", fontsize=FS.FS_NOTE, color=FS.MUTED, transform=ax.get_yaxis_transform())
ax.set_yticks(range(len(order))); ax.set_yticklabels([NAME[c] for c in order]); ax.set_ylim(-0.6, len(order) - 0.4)
ax.set_xlim(0, 0.95); ax.set_xticks([0, 0.3, 0.6, 0.9]); ax.set_xlabel("texture loss, $-\\log$ E$_{hf}$ ratio")
ax.tick_params(axis="y", length=0, pad=10); ax.grid(True, axis="x", lw=0.4, color=FS.GRID); ax.set_axisbelow(True)
V.tag(ax, "a", x=-0.75, y=1.0)
# ---- (b) FA vs loss
ax = fig.add_subplot(gs[1]); rng = np.random.default_rng(0)
jit = {d: j for d, j in zip(PUB, rng.permutation(np.linspace(-0.013, 0.013, len(PUB))))}
lab_y = []
for i, c in enumerate(order):
    lab_y.append(104 if (i == 0 or x[c] - x[order[i - 1]] > 0.06 or lab_y[-1] != 104) else 114)
for i, c in enumerate(order):
    ax.axvline(x[c], color=FS.GRID, lw=0.5, zorder=0); ax.text(x[c], lab_y[i], f"{i + 1}", ha="center", va="bottom", fontsize=FS.FS_NOTE, color=FS.MUTED)
for xv, yv, d, c in pts:
    ax.scatter(xv + jit[d], yv, s=11 if fam[d] != "clip" else 10, color=V.COLOR[fam[d]], marker=V.MARK[fam[d]], edgecolor="white", linewidth=0.3,
               alpha=0.95, zorder=3)
ax.axhline(5, color=FS.MUTED, lw=V.REF_LW, ls=V.REF_LS, zorder=1); ax.text(0.48, 7.5, "5% FPR", ha="center", va="bottom", rotation=90, fontsize=FS.FS_NOTE - 0.5, color=FS.MUTED)
ax.text(0.475, 62, f"pooled Spearman $\\rho$ = {rho:+.2f}", ha="center", va="center", rotation=90, fontsize=FS.FS_NOTE, color=FS.INK)
ax.set_xlim(0, 0.95); ax.set_xticks([0, 0.3, 0.6, 0.9]); ax.set_ylim(-2, 122); ax.set_yticks([0, 25, 50, 75, 100])
ax.set_xlabel("texture loss"); ax.set_ylabel("smoothed genuine accused (%)")
V.tag(ax, "b", x=-0.34, y=1.02)
fig.legend(handles=V.legend_handles(("cnn", "gen", "clip")), loc="outside lower center", ncol=3, fontsize=FS.FS_NOTE, columnspacing=1.0,
           handletextpad=0.3)
FS.save(fig, OUT / "fig_bandenergy_v8b"); print("wrote", OUT / "fig_bandenergy_v8b.pdf")
