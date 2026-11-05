"""True-footprint tiles of Fig. 6 (ev{i}_truth.png), redrawn from docs/paper_v2/figs/fig_evidence_tiles.npz.

The other four tiles per row (input, ours, cam, restored) are unchanged. The outline was sky blue (#56B4E9, figstyle.TRUTH),
too close to the cyan half-strength contour of the web page screenshot (Fig. 7), so the report draws it green. Drawing rule
fitted to the earlier tiles (mean abs. difference 0.009 of 255 with the old colour): 5 px anti-aliased outer contour of
gt > 0.5 on the 380 px crop, then LANCZOS to 360 px. figstyle.TRUTH (paper and website) is not changed.
python docs/capstone/report_v3/make_tiles_evidence.py"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

H = Path(__file__).resolve().parent; B = H.parents[2]
TRUTH = (0, 200, 83)     # true footprint, green; legend in make_html_figs.evidence()

z = np.load(B / "docs/paper_v2/figs/fig_evidence_tiles.npz")
for i in range(len(z["img"])):
    im = z["img"][i].copy()
    cs, _ = cv2.findContours((z["gt"][i] > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(im, cs, -1, TRUTH, 5, cv2.LINE_AA)
    inp = Image.fromarray(z["img"][i]).resize((360, 360), Image.LANCZOS)
    assert np.array_equal(np.asarray(inp), np.asarray(Image.open(H / f"figs/ev{i}_input.png").convert("RGB"))), "cache and tiles differ"
    Image.fromarray(im).resize((360, 360), Image.LANCZOS).save(H / f"figs/ev{i}_truth.png")
    print("wrote", f"figs/ev{i}_truth.png")
