"""fig_sic_curve_v8b (paper v8, 2026-10-22): restyle of fig_sic_curve (make_fig_sic_curve.py), column width (3.5 x 2.7 in).
Same data: x = untreated Celeb-DF-v2 video AUC, y = skin-smoothed genuine faces accused (face-local 0.12, %, log scale), colour =
miss rise on the same smoothing applied to forgeries (points).
  results/research/retouch_unified_20260929/readout46.json  [arm].untreated_cdf_video_vs_binary.arm (x), .smoothing.fl12.fa (y),
                                                            .smoothing.fl12.miss_rise (colour); the reference (star) is
                                                            [clipe5bzsg_s20260929].untreated_cdf_video_vs_binary.ref
  published CLIP detectors: fl12 FA from SMOOTH38.md (table row, last column), video AUC from compare_sota_clipe5b_s20260929.json
                                                            cdf[det].pub_video (Effort, Forensics Adapter; GenD / DFD-HR when present)
  reference FA: smooth38.json [clipe5b_s20260929].forms.fl12.fa[0] (the binary control = forgery head only, Table V row 1).

    python docs/paper_v2/make_fig_sic_curve_v8b.py  -> docs/paper_v2/figs/fig_sic_curve_v8b.{pdf,png}
"""
import json
import re
import sys
from pathlib import Path

B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B / "docs/paper_v2"))
import figstyle as FS  # noqa: E402
import figstyle_v8b as V  # noqa: E402
FS.apply()
import matplotlib.pyplot as plt  # noqa: E402

OUT = B / "docs/paper_v2/figs"; R = B / "results/research/retouch_unified_20260929"
d = json.loads((R / "readout46.json").read_text(encoding="utf-8"))
ARMS = [("clipe5bzl0_s20260929", "view only, $\\lambda=0$", "o"), ("clipe5bzsgl003_s20260929", "SIC $\\lambda=0.03$", "s"),
        ("clipe5bzsgl01_s20260929", "SIC $\\lambda=0.1$", "s"), ("clipe5bzsgl03_s20260929", "SIC $\\lambda=0.3$", "s"),
        ("clipe5bzsg_s20260929", "SIC $\\lambda=1$", "s"), ("clipe5bzsgh_s20260929", "one-sided penalty", "D"),
        ("clipe5bzl01_s20260929", "symmetric $\\lambda=0.1$", "^"), ("clipe5bz_s20260929", "symmetric $\\lambda=1$", "^"),
        ("clipe5bzsgG_s20260929", "Gaussian view", "X")]
pts = []
for tag, lab, mk in ARMS:
    r = d.get(tag, {})
    if r.get("smoothing"):
        pts.append((lab, mk, r["untreated_cdf_video_vs_binary"]["arm"], r["smoothing"]["fl12"]["fa"], r["smoothing"]["fl12"]["miss_rise"]))
ref_x = d["clipe5bzsg_s20260929"]["untreated_cdf_video_vs_binary"]["ref"]
ref_fa = json.loads((R / "smooth38.json").read_text(encoding="utf-8"))["clipe5b_s20260929"]["forms"]["fl12"]["fa"][0]
sm = (R / "SMOOTH38.md").read_text(encoding="utf-8"); pub = {}
for name, lab in (("effort", "Effort"), ("fadapter", "Forensics Adapter"), ("gend", "GenD"), ("dfdhr", "DFD-HR")):
    m = re.search(rf"^\| {name} \|.*$", sm, re.M)
    if m:
        pub[lab] = float(re.search(r"/ ([0-9.]+) \[", m.group(0).split("|")[-2]).group(1))
cs = json.loads((R / "compare_sota_clipe5b_s20260929.json").read_text(encoding="utf-8"))
pub_auc = {lab: cs["cdf"][k]["pub_video"] for k, lab in (("effort", "Effort"), ("fadapter", "Forensics Adapter"), ("gend", "GenD"), ("dfdhr", "DFD-HR"))
           if k in cs.get("cdf", {})}
print("arms", len(pts), "| reference", ref_x, ref_fa, "| published", pub, pub_auc)

fig = plt.figure(figsize=(FS.COL, 2.7))
ax = fig.add_axes([0.15, 0.15, 0.56, 0.82])
norm = plt.Normalize(-45, 60); cmap = plt.get_cmap("coolwarm")
FLOOR = 0.12
for i, (lab, mk, x, y, mr) in enumerate(pts, 1):
    yy = max(y, FLOOR)
    ax.scatter(x, yy, marker=mk, s=46, c=[cmap(norm(mr))], edgecolors=FS.INK, linewidths=0.5, zorder=4)
    ax.annotate(str(i), (x, yy), (4, -8) if i == 1 else (4, 4), textcoords="offset points", fontsize=FS.FS_NOTE, color=FS.INK, zorder=5)
ax.scatter(ref_x, ref_fa, marker="*", s=110, c=FS.OURS, edgecolors="white", linewidths=0.5, zorder=4)
ax.annotate("forgery head only\n(no view, no penalty)", (ref_x, ref_fa), (-4, -16), textcoords="offset points", fontsize=FS.FS_NOTE - 0.5,
            color=FS.OURS, ha="right", va="top", linespacing=1.0)
for lab, y in pub.items():
    if lab in pub_auc:
        ax.scatter(pub_auc[lab], y, marker=V.MARK["clip"], s=26, c=V.COLOR["clip"], edgecolors="white", linewidths=0.4, zorder=3)
        if lab == "Effort":
            ax.annotate(lab, (pub_auc[lab], y), (-5, 0), textcoords="offset points", fontsize=FS.FS_NOTE - 0.5, color=V.COLOR["clip"], ha="right", va="center")
        else:
            ax.annotate(lab, (pub_auc[lab], y), (0, 6), textcoords="offset points", fontsize=FS.FS_NOTE - 0.5, color=V.COLOR["clip"], ha="center", va="bottom")
ax.axhline(15, color=FS.FAKE, lw=V.REF_LW, ls=V.REF_LS, zorder=1)
ax.text(0.843, 15 / 1.15, "pre-declared bar: $\\leq$ 15%", fontsize=FS.FS_NOTE - 0.5, color=FS.FAKE, va="top", ha="left")
ax.set_yscale("log"); ax.set_ylim(0.1, 160); ax.set_yticks([0.1, 1, 10, 100]); ax.set_yticklabels(["0.1", "1", "10", "100"])
ax.set_xlim(0.84, 0.975); ax.set_xticks([0.85, 0.90, 0.95])
ax.set_xlabel("untreated Celeb-DF-v2, video AUC"); ax.set_ylabel("smoothed genuine faces accused (%)")
# colour bar and the numbered key in a column on the right
cax = fig.add_axes([0.76, 0.60, 0.025, 0.36]); cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax)
cb.set_label("miss rise on smoothed\nforgeries (points)", fontsize=FS.FS_NOTE - 0.5, labelpad=3); cb.ax.tick_params(labelsize=FS.FS_NOTE - 0.5, length=2)
cb.outline.set_linewidth(0.5)
key = "\n".join(f"{i}  {lab}" for i, (lab, *_) in enumerate(pts, 1))
fig.text(0.745, 0.52, key, fontsize=FS.FS_NOTE - 0.5, va="top", ha="left", color=FS.INK, linespacing=1.35)
fig.text(0.745, 0.545, "trained models", fontsize=FS.FS_NOTE - 0.5, va="bottom", ha="left", color=FS.MUTED)
FS.save(fig, OUT / "fig_sic_curve_v8b"); print("wrote", OUT / "fig_sic_curve_v8b.pdf")
