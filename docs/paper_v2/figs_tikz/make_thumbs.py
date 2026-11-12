"""Image thumbnails for the TikZ figures (fig_arch, fig_system). No model is run: every thumbnail is a stored image, a stored
evidence map (results/research/explain_vlm_20261012/evidence_maps.npz, model clipe5_s20260929) or a fixed image operation.

Example: held-out part-level forgery part_forgery:donor:454__f0140__mouth (the demo's example 2; decision fake, P(fake) 1.00,
named part mouth, mean evidence on the mouth 0.99; restoring the mouth flips the decision). Landmarks: cached MediaPipe output
in v3_landmarks.npz (not re-detected). The model input is drawn as the whole stored crop resized to 224 x 224, as in the
evidence overlays of explain_vlm_20261012/overlays.

    python docs/paper_v2/figs_tikz/make_thumbs.py   -> docs/paper_v2/figs_tikz/img/*.png
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

H = Path(__file__).resolve().parent; BASE = H.parents[2]; OUT = H / "img"; OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(H.parent))
import figstyle as FS  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

EX = BASE / "results/research/explain_vlm_20261012"
KEY = "part_forgery:donor:454__f0140__mouth"
rec = [json.loads(l) for l in open(EX / "evidence.jsonl", encoding="utf-8") if KEY in l][0]
img = np.array(Image.open(rec["image"]).convert("RGB")); x0 = np.array(Image.open(rec["x0"]).convert("RGB"))
lm = np.load(EX / "v3_landmarks.npz")[KEY].astype(np.float32)          # (478, 2), pixel coordinates of img
ev = np.load(EX / "evidence_maps.npz")[KEY].astype(np.float32)        # (16, 16) in [0, 1]
h0, w0 = img.shape[:2]; S = 448                                          # thumbnails at 2x the model's 224 px
sx, sy = S / w0, S / h0
lmS = lm * np.array([sx, sy], np.float32)

R_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246, 46, 53, 52, 65, 55, 70, 63, 105, 66, 107]
L_EYE = [263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466, 276, 283, 282, 295, 285, 300, 293, 334, 296, 336]
LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]
NOSE = [168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 98, 97, 326, 327, 294, 278, 344, 440, 275, 45, 220, 115, 48, 64]
FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
             172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]


def hexrgb(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def hull(idx, shape=(S, S)):
    m = np.zeros(shape, np.uint8); cv2.fillConvexPoly(m, cv2.convexHull(lmS[idx].astype(np.int32)), 1); return m


def save(arr, name):
    a = np.asarray(arr)
    if a.dtype != np.uint8:
        a = (np.clip(a, 0, 1) * 255).round().astype(np.uint8)
    Image.fromarray(a).save(OUT / f"{name}.png"); print("wrote", OUT / f"{name}.png")


x = cv2.resize(img, (S, S), interpolation=cv2.INTER_AREA)
save(x, "x")                                                               # model input (face crop)

# smoothed view x_s: face-local bilateral filter inside the feathered landmark hull (the training form when landmarks exist)
face = hull(FACE_OVAL).astype(np.float32); face = cv2.GaussianBlur(face, (0, 0), 6)
bil = cv2.bilateralFilter(x, 15, 80, 80); bil = cv2.bilateralFilter(bil, 15, 80, 80)
xs = (face[..., None] * bil + (1 - face[..., None]) * x).astype(np.uint8)
save(xs, "xs")

# evidence map: 16 x 16 grid (nearest) and the overlay on the crop (figstyle.overlay)
cm = plt.get_cmap(FS.MAP_CMAP)
grid = cv2.resize(ev, (S, S), interpolation=cv2.INTER_NEAREST)
g = cm(grid)[..., :3]
g[(np.arange(S) % (S // 16) == 0)[:, None].repeat(S, 1) | (np.arange(S) % (S // 16) == 0)[None, :].repeat(S, 0)] *= 0.93
save(g, "ev_grid")
save(FS.overlay(x, cv2.resize(ev, (S, S), interpolation=cv2.INTER_CUBIC)), "ev_overlay")

# exact footprint M = dilate(1[|x - x0|_inf > 6]) on the native image, then its 16 x 16 target (area average)
d = np.abs(img.astype(np.int16) - x0.astype(np.int16)).max(2) > 6
M = cv2.dilate(d.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
n_, lab_, st_, _ = cv2.connectedComponentsWithStats(M)   # drawn: the largest component (the edited part); a few re-encoding
M = (lab_ == 1 + int(np.argmax(st_[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)   # specks at the frame border are left out
M16 = cv2.resize(M.astype(np.float32), (16, 16), interpolation=cv2.INTER_AREA)
t = cv2.resize(M16, (S, S), interpolation=cv2.INTER_NEAREST)
c0, c1 = np.ones(3), hexrgb(FS.TRUTH) / 255
t = np.clip(t / max(t.max(), 1e-6), 0, 1) ** 0.7
tg = (1 - t[..., None]) * c0 + t[..., None] * c1
tg[(np.arange(S) % (S // 16) == 0)[:, None].repeat(S, 1) | (np.arange(S) % (S // 16) == 0)[None, :].repeat(S, 0)] *= 0.93
save(tg, "footprint16")

# photo with landmarks and the training crop box (+35 % per side)
P = 2.0; ph = cv2.resize(img, (int(w0 * P), int(h0 * P)), interpolation=cv2.INTER_CUBIC)
det = ph.copy()
for (u, v) in lm * P:
    cv2.circle(det, (int(round(u)), int(round(v))), 1, (15, 77, 146), -1, lineType=cv2.LINE_AA)
xa, ya = lm.min(0) * P; xb, yb = lm.max(0) * P; bw, bh = xb - xa, yb - ya
X0, Y0, X1, Y1 = [int(round(v)) for v in (xa - 0.35 * bw, ya - 0.35 * bh, xb + 0.35 * bw, yb + 0.35 * bh)]
cv2.rectangle(det, (max(X0, 1), max(Y0, 1)), (min(X1, det.shape[1] - 2), min(Y1, det.shape[0] - 2)), (213, 94, 0), 3, lineType=cv2.LINE_AA)
save(ph, "photo"); save(det, "detect")

# part masks (eyes, nose, mouth, skin, contour) on the crop, rule as in face_masks.js / occlusion_regions
eyes = np.maximum(hull(R_EYE), hull(L_EYE)); nose = hull(NOSE); mouth = hull(LIPS); oval = hull(FACE_OVAL)
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))
contour = cv2.dilate(oval, k) - cv2.erode(oval, k)
skin = np.clip(cv2.erode(oval, k) - cv2.dilate(np.maximum.reduce([eyes, nose, mouth]), k), 0, 1)
cols = {"skin": "#E69F00", "contour": "#8C8C8C", "eyes": "#56B4E9", "nose": "#009E73", "mouth": "#D55E00"}
base = x.astype(np.float32) * 0.55 + 255 * 0.45
mk = base.copy()
for nm, m in (("skin", skin), ("contour", contour), ("eyes", eyes), ("nose", nose), ("mouth", mouth)):
    a = 0.55 * m[..., None].astype(np.float32); mk = (1 - a) * mk + a * hexrgb(cols[nm])
save(mk.astype(np.uint8), "masks")

# output: crop with the named part's contour (HILITE)
out = x.copy()
cs, _ = cv2.findContours(cv2.dilate(mouth, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(out, cs, -1, (40, 40, 40), 7, lineType=cv2.LINE_AA)
cv2.drawContours(out, cs, -1, tuple(int(v) for v in hexrgb(FS.HILITE)), 4, lineType=cv2.LINE_AA)
save(out, "out_contour")

# untouched original x0 at the same size (for the footprint panel)
x0S = cv2.resize(x0, (S, S), interpolation=cv2.INTER_AREA); save(x0S, "x0")
# beautified genuine item for the training-triplet panel: the same face-local smoothing applied to the untouched original
b0 = cv2.bilateralFilter(cv2.bilateralFilter(x0S, 15, 80, 80), 15, 80, 80)
save((face[..., None] * b0 + (1 - face[..., None]) * x0S).astype(np.uint8), "x0_smooth")
print(json.dumps({k: rec[k] for k in ("decision", "probabilities", "evidence_mean_per_part", "named_parts")}))
