"""Training-panel tiles for the system figure: a genuine FF++ frame and a forged one (the page's examples 1 and 4), each
with the scripted skin smoothing used in training (ops.op_smooth, the beautified-view operation of the RU recipe), so the
figure shows the rule "smoothing is shown to both classes" on real training-type images. Writes figs/train_*.png.
python make_tiles_train.py"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

B = Path(r"C:\My_Project\AIGC"); OUT = Path(__file__).resolve().parent / "figs"
for p in (B, B / "results/research/retouch_unified_20260929"):
    sys.path.insert(0, str(p))
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402
import ops  # noqa: E402

rng = np.random.default_rng(0)
for name, src in (("genuine", "ex1.png"), ("forged", "ex4.png")):
    img = np.array(Image.open(B / "docs/demo_ru/examples" / src).convert("RGB")); h, w = img.shape[:2]
    lm = np.asarray(get_landmarks(np.ascontiguousarray(img)), np.float32)[:, :2]
    sm, q = ops.op_smooth(img, lm, rng, frac=0.10, mix=0.6)
    s = min(h, w); y0, x0 = (h - s) // 2, (w - s) // 2          # square centre crop for the small tiles
    for tag, arr in ((name, img), (name + "_smooth", sm)):
        Image.fromarray(arr[y0:y0 + s, x0:x0 + s]).resize((360, 360), Image.LANCZOS).save(OUT / f"train_{tag}.png", optimize=True)
    print(name, src, img.shape, "texture loss", round(float(q[3]), 3))
