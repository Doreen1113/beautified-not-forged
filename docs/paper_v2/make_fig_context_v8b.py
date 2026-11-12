"""fig_context_v8b (2026-10-27): the mechanism figure of Addendum 57, column width (3.5 x 2.9 in).

One row per detector; three dots on each row = the share of smoothed genuine Celeb-DF-B frames called forged at the detector's own
5 % FPR threshold (set on the untreated frames) when the same bilateral strength is applied to
    face-local   (fe01: the face interior, soft edge)      results/research/retouch_unified_20260929/bdry38.json rows[k]["fe01"]["fa"]
    ring only    (the 12-px band at the face edge)                                                   rows[k]["ring"]["fa"]
    whole crop   (face and background alike)                                                         rows[k]["whole"]["fa"]
Reading: the ring alone accuses almost nothing (edge lines are not the cue) and the whole crop accuses far less than the face
alone, so what most detectors read is "a face smoother than its context". Detectors and families: figstyle_v8b.DETECTORS; ours =
the main model, two seeds are not available for this probe so only seed 1 is drawn. Rows sorted by the face-local share.

    python docs/paper_v2/make_fig_context_v8b.py  -> docs/paper_v2/figs/fig_context_v8b.{pdf,png}
"""
import json
import sys
from pathlib import Path

B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B / "docs/paper_v2"))
import figstyle as FS  # noqa: E402
import figstyle_v8b as V  # noqa: E402
FS.apply()
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.lines as ml  # noqa: E402

OUT = B / "docs/paper_v2/figs"
R = json.loads((B / "results/research/retouch_unified_20260929/bdry38.json").read_text(encoding="utf-8"))["rows"]
KEY = {"ours main s1": "clipe5_s20260929"}
rows = [(KEY.get(ka, ka), name, fam) for ka, _, name, fam in V.DETECTORS if KEY.get(ka, ka) in R]
rows.sort(key=lambda r: R[r[0]]["fe01"]["fa"])
SHORT = {"EfficientNet-B4": "EffNet-B4", "Forensics Adapter": "Forensics Ad.", "Ours (seed 1)": "Ours"}
FORMS = [("fe01", "face only", FS.INK, "o", 1.0), ("whole", "face + background", FS.MUTED, "s", 1.0), ("ring", "edge ring only", "#C98A00", "D", 1.0)]

fig, ax = plt.subplots(figsize=(FS.COL, 3.1), layout="constrained")
n = len(rows)
for i, (k, name, fam) in enumerate(rows):
    if i % 2 == 0:
        ax.axhspan(i - 0.5, i + 0.5, color=FS.LIGHT, lw=0, zorder=0)
    xs = {f: R[k][f]["fa"] for f, *_ in FORMS}
    ax.plot([min(xs.values()), max(xs.values())], [i, i], color=FS.GRID, lw=1.2, zorder=1)
    for f, lab, col, mk, _ in FORMS:
        ax.scatter([xs[f]], [i], s=22 if f != "fe01" else 26, marker=mk, color=col if fam != "ours" or f != "fe01" else FS.OURS,
                   edgecolor="white", linewidth=0.4, zorder=3)
ax.axvline(5, color=FS.MUTED, lw=V.REF_LW, ls=V.REF_LS, zorder=1)
ax.text(6.5, n - 1, "5% FPR", color=FS.MUTED, fontsize=FS.FS_NOTE - 0.5, ha="left", va="center")
ax.set_yticks(range(n)); ax.set_yticklabels([SHORT.get(nm, nm) for _, nm, _ in rows], fontsize=FS.FS_TICK - 0.5)
for lab, (_, _, fam) in zip(ax.get_yticklabels(), rows):
    lab.set_color(FS.OURS if fam == "ours" else FS.INK); lab.set_fontweight("bold" if fam == "ours" else "normal")
ax.set_ylim(-0.6, n - 0.4); ax.set_xlim(-2, 103); ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xlabel("smoothed genuine frames called forged (%)")
ax.tick_params(axis="y", length=0)
handles = [ml.Line2D([], [], ls="", marker=mk, color=col, markersize=5, markeredgecolor="white", markeredgewidth=0.4, label=lab)
           for _, lab, col, mk, _ in FORMS]
ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3, fontsize=FS.FS_NOTE, frameon=False, handletextpad=0.3,
          columnspacing=1.0, borderaxespad=0.1)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
FS.save(fig, OUT / "fig_context_v8b")
print("rows", n, {k: (R[k]["fe01"]["fa"], R[k]["whole"]["fa"], R[k]["ring"]["fa"]) for k, _, _ in rows[-3:]})
