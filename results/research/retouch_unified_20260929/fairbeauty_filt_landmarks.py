"""Landmarks of the FairBeauty TRAIN filtered crops (fairbeauty_train_pairs/filt), needed to self-blend them (RU8). Ubuntu."""
import os, sys
from pathlib import Path
import numpy as np
from PIL import Image
B = Path(os.environ["AIGC_BASE"]); sys.path.insert(0, str(B))
from filters_v2.scale_normalized_filters import get_landmarks
D = B / "external_data/fairbeauty_train_pairs"; out = {}
for k, p in enumerate(sorted((D / "filt").glob("*.png"))):
    lm = get_landmarks(np.array(Image.open(p).convert("RGB")))
    if lm is not None: out[p.stem] = lm.astype(np.float32)
    if k % 5000 == 0: print(k, len(out), flush=True)
np.savez(D / "filt_landmarks.npz", **out); print("saved", len(out))
