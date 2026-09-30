"""Check the analytic targets of ops.py against re-detected landmarks / direct measurement on FFHQ originals, and check
the slimming direction (jaw_ratio < 1).  python verify_ops.py [n]"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

BASE = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE)); sys.path.insert(0, str(HERE))
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402
from ops import OPS, OP_FN, _eye_width, JAW_LEFT, JAW_RIGHT, _L, _hf, hull_mask  # noqa: E402

n = int(sys.argv[1]) if len(sys.argv) > 1 else 12
files = sorted((BASE / "ffhq_originals/Part2").glob("*.png"))[:n]
rng = np.random.default_rng(0); rows = []
for p in files:
    rgb = np.array(Image.open(p).convert("RGB")); lm = get_landmarks(rgb)
    if lm is None:
        continue
    for name in OPS:
        out, q = OP_FN[name](rgb, lm, rng); lm2 = get_landmarks(np.ascontiguousarray(out))
        if lm2 is None:
            continue
        h, w = rgb.shape[:2]; m = hull_mask(lm, h, w)
        meas = np.array([_eye_width(lm2) / _eye_width(lm) - 1, 1 - np.linalg.norm(lm2[JAW_LEFT] - lm2[JAW_RIGHT]) / np.linalg.norm(lm[JAW_LEFT] - lm[JAW_RIGHT]),
                         (_L(out) - _L(rgb))[m].mean() / 20, 1 - _hf(_L(out), m) / _hf(_L(rgb), m)])
        rows.append((name, q, meas))
for i, name in enumerate(OPS):
    A = np.array([q for nm, q, _ in rows if nm == name]); M = np.array([mm for nm, _, mm in rows if nm == name])
    print(f"{name:7s} n={len(A)}  analytic q[{i}] mean {A[:, i].mean():+.4f}  measured {M[:, i].mean():+.4f}  "
          f"|diff| {np.abs(A[:, i] - M[:, i]).mean():.4f}  corr {np.corrcoef(A[:, i], M[:, i])[0, 1]:.3f}  "
          f"cross-talk measured (other q) {np.abs(np.delete(M, i, 1)).mean():.4f}")
