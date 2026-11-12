"""Figure: the SIC trade-off (Addendum 46 family). x = untreated Celeb-DF-v2 video AUC, y = false alarm on face-local
skin-smoothed genuine faces (fl12, %), marker colour = miss rise on smoothed forgeries (fl12, points). Published CLIP detectors
from SMOOTH38 (fl12 FA) and compare_sota (video AUC). python docs/paper_v2/make_fig_sic_curve.py -> figs/fig_sic_curve.{pdf,png}"""
import json
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

H = Path(__file__).resolve().parent; R = H.parents[1] / "results/research/retouch_unified_20260929"
import sys  # noqa: E402
sys.path.insert(0, str(H)); import figstyle as FS  # noqa: E402

d = json.loads((R / "readout46.json").read_text(encoding="utf-8"))
ARMS = {"clipe5bzl0_s20260929": ("view only, $\\lambda=0$", "o"), "clipe5bzsgl003_s20260929": ("SIC $\\lambda=0.03$", "s"), "clipe5bzsgl01_s20260929": ("SIC $\\lambda=0.1$", "s"),
        "clipe5bzsgl03_s20260929": ("SIC $\\lambda=0.3$", "s"), "clipe5bzsg_s20260929": ("SIC $\\lambda=1$", "s"), "clipe5bzsgh_s20260929": ("one-sided", "D"),
        "clipe5bz_s20260929": ("symmetric $\\lambda=1$", "^"), "clipe5bzl01_s20260929": ("symmetric $\\lambda=0.1$", "^"), "clipe5bzsgG_s20260929": ("Gaussian view", "x")}
pts = []
for tag, (lab, mk) in ARMS.items():
    r = d.get(tag, {})
    if not r.get("smoothing"):
        continue
    pts.append((lab, mk, r["untreated_cdf_video_vs_binary"]["arm"], r["smoothing"]["fl12"]["fa"], r["smoothing"]["fl12"]["miss_rise"]))
ref = d["clipe5bzsg_s20260929"]["untreated_cdf_video_vs_binary"]["ref"]
# published CLIP detectors: fl12 FA from SMOOTH38.md, video AUC from compare_sota of the reference model (pub_video)
sm = (R / "SMOOTH38.md").read_text(encoding="utf-8"); pub = {}
for name, lab in (("effort", "Effort"), ("fadapter", "Forensics Adapter"), ("gend", "GenD"), ("dfdhr", "DFD-HR")):
    m = re.search(rf"^\| {name} \|.*$", sm, re.M)
    if m:
        cells = m.group(0).split("|"); fl12 = cells[-2]   # last form column
        fa = float(re.search(r"/ ([0-9.]+) \[", fl12).group(1)); pub[lab] = fa
cs = json.loads((R / "compare_sota_clipe5b_s20260929.json").read_text(encoding="utf-8"))
pub_auc = {"Effort": cs["cdf"]["effort"]["pub_video"], "Forensics Adapter": cs["cdf"]["fadapter"]["pub_video"]}
for name, lab in (("gend", "GenD"), ("dfdhr", "DFD-HR")):
    if name in cs.get("cdf", {}):
        pub_auc[lab] = cs["cdf"][name]["pub_video"]

fig, ax = plt.subplots(figsize=(3.5, 3.0)); fig.subplots_adjust(left=0.155, right=0.77, top=0.97, bottom=0.16)
norm = plt.Normalize(-45, 60); cmap = plt.get_cmap("coolwarm")
order = ["view only", "SIC $\lambda=0.03$", "SIC $\lambda=0.1$", "SIC $\lambda=0.3$", "SIC $\lambda=1$", "sym. $\lambda=0.1$", "sym. $\lambda=1$", "one-sided", "Gaussian view"]
pts.sort(key=lambda t: order.index(t[0]) if t[0] in order else 99)
legend = []
for i, (lab, mk, x, y, mr) in enumerate(pts, 1):
    yy = max(y, 0.12)
    ax.scatter(x, yy, marker=mk, s=52, c=[cmap(norm(mr))], edgecolors=FS.INK, linewidths=0.6, zorder=3)
    ax.annotate(str(i), (x, yy), (x + 0.0025, yy * 1.18), fontsize=6.0, color=FS.INK)
    legend.append(f"{i}  {lab}")
ax.scatter(ref, 84.5, marker="*", s=95, c=FS.BINARY, edgecolors=FS.INK, linewidths=0.6, zorder=4)
ax.annotate("forgery head only\n(no view, no SIC)", (ref, 84.5), (ref - 0.07, 84.5 * 0.62), fontsize=6.0, color=FS.INK)
for lab, fa in pub.items():
    if lab in pub_auc:
        ax.scatter(pub_auc[lab], fa, marker="P", s=42, c=FS.CLIP, edgecolors=FS.INK, linewidths=0.5, zorder=3)
        ax.annotate(lab, (pub_auc[lab], fa), (pub_auc[lab] - 0.003, fa * (0.60 if lab == "Effort" else 1.12)), fontsize=6.0, color=FS.INK, ha="right")
ax.axhline(15, color=FS.FAKE, lw=0.9, ls=(0, (4, 3))); ax.text(0.8415, 16.8, "pre-declared bar: FA $\leq$ 15", fontsize=6.2, color=FS.FAKE)
ax.set_yscale("log"); ax.set_ylim(0.1, 130); ax.set_yticks([0.1, 1, 10, 100]); ax.set_yticklabels(["0.1", "1", "10", "100"])
ax.set_xlabel("untreated Celeb-DF-v2, video AUC", fontsize=FS.FS_TEXT); ax.set_ylabel("skin-smoothed genuine faces accused (%)", fontsize=FS.FS_TEXT)
ax.set_xlim(0.84, 0.975); ax.tick_params(labelsize=FS.FS_TICK)
for s_ in ("top", "right"):
    ax.spines[s_].set_visible(False)
sm_ = plt.cm.ScalarMappable(norm=norm, cmap=cmap); cax = fig.add_axes([0.80, 0.56, 0.022, 0.38]); cb = fig.colorbar(sm_, cax=cax)
cb.set_label("miss rise on smoothed\nforgeries (points)", fontsize=6.2); cb.ax.tick_params(labelsize=6)
fig.text(0.79, 0.50, "\n".join(legend), fontsize=5.9, va="top", color=FS.INK, linespacing=1.25)
(H / "figs").mkdir(exist_ok=True)
for ext in ("pdf", "png"):
    fig.savefig(H / "figs" / f"fig_sic_curve.{ext}", dpi=300)
print("wrote figs/fig_sic_curve.pdf", len(pts), "arms", pub, pub_auc)
