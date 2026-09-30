"""Fit analytic->measured calibration for the two geometric ops (eye, jaw) on n FFHQ Part2 originals."""
import sys; from pathlib import Path; import numpy as np; from PIL import Image
BASE = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE)); sys.path.insert(0, str(HERE))
from filters_v2.scale_normalized_filters import get_landmarks
from ops import op_eye, op_jaw, _eye_width, JAW_LEFT, JAW_RIGHT
n = int(sys.argv[1]); files = sorted((BASE / "ffhq_originals/Part2").glob("*.png"))[100:100 + n]; rng = np.random.default_rng(1)
E, J = [], []
for p in files:
    rgb = np.array(Image.open(p).convert("RGB")); lm = get_landmarks(rgb)
    if lm is None: continue
    for _ in range(2):
        out, q = op_eye(rgb, lm, rng); lm2 = get_landmarks(np.ascontiguousarray(out))
        if lm2 is not None: E.append((q[0], _eye_width(lm2) / _eye_width(lm) - 1))
        out, q = op_jaw(rgb, lm, rng); lm2 = get_landmarks(np.ascontiguousarray(out))
        if lm2 is not None: J.append((q[1], 1 - np.linalg.norm(lm2[JAW_LEFT] - lm2[JAW_RIGHT]) / np.linalg.norm(lm[JAW_LEFT] - lm[JAW_RIGHT])))
for name, A in (("eye", np.array(E)), ("jaw", np.array(J))):
    a, m = A[:, 0], A[:, 1]; k = float((a * m).sum() / (a * a).sum())   # through-origin slope
    print(f"{name} n={len(A)} slope(measured/analytic)={k:.3f} corr={np.corrcoef(a, m)[0,1]:.3f} resid_std={np.std(m - k * a):.4f} measured_mean={m.mean():.4f}")
