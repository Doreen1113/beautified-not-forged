"""Figure: how each held-out colour filter moves the FF++-only CLIP detector (subspace_probe.json, Addendum 17 A).
Left: mean change of the forged logit on genuine and forged FF++ val frames per filter (dot plot, one row per filter, the two
dots joined). Right: cosine of the mean feature shift with the forged weight vector (lollipop). Shaded rows: the two filters with a
radial luminance overlay. Drawn at final size (4.2 in wide in the supplement) with the shared style docs/paper_v2/figstyle.py.
python docs/paper_v2/make_fig_mechanism.py -> figs/fig_mechanism.pdf"""
import json
import sys
from pathlib import Path

import numpy as np

BASE = Path(r"C:\My_Project\AIGC"); OUT = BASE / "docs/paper_v2/figs"; OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(BASE / "docs/paper_v2"))
import figstyle as FS  # noqa: E402

FS.apply()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

sp = json.loads((BASE / "results/research/retouch_unified_20260929/subspace_probe.json").read_text())["clipe5f_s20260929"]["heldout_filters"]
names = sorted(sp, key=lambda k: -sp[k]["d_logit_genuine"])
g = np.array([sp[k]["d_logit_genuine"] for k in names]); f = np.array([sp[k]["d_logit_forged"] for k in names])
c = np.array([sp[k]["cos_w_meanshift"] for k in names])
vign = {"earlybird", "mayfair"}
y = np.arange(len(names))

fig, ax = plt.subplots(1, 2, figsize=(4.2, 2.15), gridspec_kw={"width_ratios": [1.75, 1], "wspace": 0.08})
fig.subplots_adjust(left=0.16, right=0.98, bottom=0.2, top=0.86)
for a in ax:
    for i, n in enumerate(names):
        if n in vign:
            a.axhspan(i - 0.5, i + 0.5, color=FS.LIGHT, lw=0, zorder=0)
    a.axvline(0, color=FS.MUTED, lw=0.6, zorder=1)
    a.set_ylim(len(names) - 0.5, -0.5); a.tick_params(axis="y", length=0)
    a.spines["left"].set_visible(False)
for i in y:
    ax[0].plot([f[i], g[i]], [i, i], color=FS.GRID, lw=1.8, zorder=2, solid_capstyle="round")
ax[0].plot(g, y, "o", ms=4, color=FS.REAL, zorder=3, label="genuine frames")
ax[0].plot(f, y, "o", ms=4, mfc="white", mec=FS.FAKE, mew=1.0, zorder=3, label="forged frames")
ax[0].set_yticks(y); ax[0].set_yticklabels(names)
for lab, n in zip(ax[0].get_yticklabels(), names):
    if n in vign:
        lab.set_fontweight("bold")
ax[0].set_xlabel("mean change of the forged logit")
ax[1].hlines(y, 0, c, color=FS.INK, lw=0.9, zorder=2)
ax[1].plot(c, y, "o", ms=3.4, color=FS.INK, zorder=3)
ax[1].set_yticks([]); ax[1].set_xlabel(r"$\cos(w,\ \overline{\Delta\phi})$")
ax[1].set_xlim(min(0, c.min()) - 0.02, c.max() * 1.12); ax[1].set_xticks([0, 0.1, 0.2, 0.3])
fig.legend(handles=[Line2D([], [], marker="o", ls="", ms=4, color=FS.REAL, label="genuine frames"),
                    Line2D([], [], marker="o", ls="", ms=4, mfc="white", mec=FS.FAKE, mew=1.0, label="forged frames"),
                    plt.Rectangle((0, 0), 1, 1, fc=FS.LIGHT, ec="none", label="radial luminance overlay")],
           loc="upper center", bbox_to_anchor=(0.55, 1.0), ncol=3, fontsize=FS.FS_NOTE, columnspacing=1.0)
FS.save(fig, OUT / "fig_mechanism")
print("written", OUT / "fig_mechanism.pdf", dict(zip(names, zip(g.round(2), f.round(2), c.round(3)))))
