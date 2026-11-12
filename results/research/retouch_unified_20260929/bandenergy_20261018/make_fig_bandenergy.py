"""Figure: (a) high-frequency texture loss per smoothing form, (b) false alarms of the published detectors against it.
Reads bandenergy.json and fa_parsed.json (bandenergy.py). Writes fig_bandenergy.{pdf,png}, 3.3 in wide.
All eight forms are shown at the 256-px view (the commercial S-90 crops are 960 px and must be resized to be comparable);
the seven Celeb-DF forms at their stored resolution give the same ordering (bandenergy_tables.md)."""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

B = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(B / "docs/paper_v2")); import figstyle as FS; FS.apply()  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

res = json.loads((HERE / "bandenergy.json").read_text()); fa = json.loads((HERE / "fa_parsed.json").read_text())["published"]
FORMS = ["bil9", "bil15", "bil21", "median5", "gblend", "fl06", "fl12", "Smoothing_90"]
PUB = [d for d in fa]; fam = res["family"]; GEN = "#56B4E9"
FAMC = {"cnn": FS.CNN, "clip": FS.CLIP, "gen": GEN}; MK = {"cnn": "o", "clip": "s", "gen": "^"}
NAME = {"bil9": "bilateral d9", "bil15": "bilateral d15", "bil21": "bilateral d21", "median5": "median 5", "gblend": "Gaussian blend",
        "fl06": "face-local 6%", "fl12": "face-local 12%", "Smoothing_90": "service S-90"}
KEY = "ehf0.25_view"; L = res["loss_per_form"][KEY]
order = sorted(FORMS, key=lambda c: L[c]["mean"]); x = {c: L[c]["mean"] for c in FORMS}
pts = [(x[c], fa[d]["fa"][c], d, c) for c in FORMS for d in PUB if not (c == "Smoothing_90" and d == "npr")]
rho = stats.spearmanr([p[0] for p in pts], [p[1] for p in pts]).statistic
rho7 = res["pooled"]["ehf0.25_native"]["7forms"]["spearman"]

fig = plt.figure(figsize=(3.3, 2.5), layout="constrained")
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.45], wspace=0.02)
# ---- (a) loss per form, ordered
ax = fig.add_subplot(gs[0]); ys = np.arange(len(order))
for i, c in enumerate(order):
    lo, hi = L[c]["ci"]; m = L[c]["mean"]
    ax.plot([lo, hi], [i, i], color=FS.INK, lw=0.7, solid_capstyle="butt")
    ax.plot(m, i, marker="o", ms=4, color=FS.INK if c != "Smoothing_90" else "white", markeredgecolor=FS.INK, markeredgewidth=0.7, ls="")
    ax.text(-0.025, i, f"{i + 1}", ha="right", va="center", fontsize=FS.FS_NOTE, color=FS.MUTED, transform=ax.get_yaxis_transform())
ax.set_yticks(ys); ax.set_yticklabels([NAME[c] for c in order]); ax.set_ylim(-0.6, len(order) - 0.4)
ax.set_xlim(0, 0.95); ax.set_xticks([0, 0.3, 0.6, 0.9]); ax.set_xlabel("texture loss, $-\\log$ E$_{hf}$ ratio")
ax.tick_params(axis="y", length=0, pad=10); ax.set_title("(a) loss per form", loc="left")
ax.grid(True, axis="x", lw=0.4, color=FS.GRID); ax.set_axisbelow(True)
# ---- (b) FA vs loss, one marker per detector x form
ax = fig.add_subplot(gs[1]); rng = np.random.default_rng(0); jit = {d: j for d, j in zip(PUB, rng.permutation(np.linspace(-0.013, 0.013, len(PUB))))}
lab_y = []   # stagger strip numbers whose neighbour is closer than 0.06
for i, c in enumerate(order):
    lab_y.append(103 if (i == 0 or x[c] - x[order[i - 1]] > 0.06 or lab_y[-1] != 103) else 112)
for i, c in enumerate(order):
    ax.axvline(x[c], color=FS.GRID, lw=0.5, zorder=0); ax.text(x[c], lab_y[i], f"{i + 1}", ha="center", va="bottom", fontsize=FS.FS_NOTE, color=FS.MUTED)
for xv, yv, d, c in pts:
    ax.scatter(xv + jit[d], yv, s=9, color=FAMC[fam[d]], marker=MK[fam[d]], edgecolor="white", linewidth=0.25, alpha=0.95, zorder=3)
ax.axhline(5, color=FS.MUTED, lw=0.5, ls=(0, (2.5, 1.5)), zorder=1); ax.text(0.47, 7.5, "5% FPR", ha="center", va="bottom", fontsize=FS.FS_NOTE, color=FS.MUTED)
ax.set_xlim(0, 0.95); ax.set_xticks([0, 0.3, 0.6, 0.9]); ax.set_ylim(-2, 120); ax.set_yticks([0, 25, 50, 75, 100])
ax.set_xlabel("texture loss"); ax.set_ylabel("false alarms on smoothed genuine (%)")
ax.set_title(f"(b) pooled $\\rho$ = {rho:+.2f}", loc="left")
h = [plt.Line2D([], [], ls="", marker=MK[f], color=FAMC[f], markersize=4, label=n) for f, n in (("cnn", "face-forgery CNN"), ("gen", "generated-image"), ("clip", "CLIP-based"))]
fig.legend(handles=h, loc="outside lower center", ncol=3, fontsize=FS.FS_NOTE, columnspacing=1.0, handletextpad=0.3)
p = FS.save(fig, HERE / "fig_bandenergy"); print("written", p, "pooled rho 8 forms view256", round(float(rho), 3), "| 7 forms native", round(rho7, 3))
