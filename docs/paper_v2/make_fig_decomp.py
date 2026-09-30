"""fig_decomp: a Tencent four-operation render split into single-operation components (decompose.py), with |component -
original| x4 below each. python docs/paper_v2/make_fig_decomp.py"""
import sys
from pathlib import Path

import cv2
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

B = Path(r"C:\My_Project\AIGC"); RU = B / "results/research/retouch_unified_20260929"
sys.path.insert(0, str(RU)); sys.path.insert(0, str(B / "docs/paper_v2"))
import decompose as D  # noqa: E402
import make_figures as MF  # noqa: E402
import json  # noqa: E402

stem = "60002"
row = [l.split("\t") for l in (RU / "pairs_tencent.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.split("\t")[0].endswith(f"{stem}.png")][0]
O, R, comp, _ = D.decompose(row[0], row[1], stem)
box = [int(v / 2) for v in json.loads((RU / "ffhq_boxes.json").read_text())[stem]]
c = lambda im: im[box[1]:box[3], box[0]:box[2]]
tiles = [("original", O), ("vendor render\n(4 operations)", R), ("eye component", comp["eye"]), ("jaw component", comp["jaw"]),
         ("tone component", comp["white"]), ("texture component", comp["smooth"])]
fig, ax = plt.subplots(2, 6, figsize=(7.1, 2.75))
for j, (t, im) in enumerate(tiles):
    ax[0, j].imshow(c(im)); ax[0, j].set_title(t, fontsize=6.3)
    d = np.abs(c(im).astype(np.float32) - c(O).astype(np.float32)).mean(2)
    ax[1, j].imshow(np.clip(d * 4, 0, 255), cmap="magma", vmin=0, vmax=255)
    for a in ax[:, j]:
        a.set_xticks([]); a.set_yticks([])
ax[1, 0].set_ylabel("|x - original| x4", fontsize=6)
fig.tight_layout(pad=0.3); MF.save(fig, "fig_decomp"); print("fig_decomp done")
