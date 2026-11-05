"""Multi-operation beautification chain (Addendum 56). Order as in the GPUPixel demo chain: face reshape (thin face, big eye)
-> skin smoothing -> whitening.
  thin face / big eye: numpy port of GPUPixel FaceReshapeFilter (curveWarp: linear radial pull of nine contour points towards
      nose points; enlargeEye: radial zoom with quadratic weight, radius 5 x centre-corner distance), with MediaPipe-478
      equivalents of the 106-point pairs (so: GPUPixel-style, not bit-exact);
  smoothing: gpupixel_port.beauty_at_scale (ported shader, Addendum 54);
  whitening: ops.op_white (GPUPixel's whitening is a 3-LUT chain whose assets are not ported).
apply(rgb, lm, rng, ops=None, strengths=None) -> out, presence(4), q(4), params.  Strength ranges are set by calibrate()."""
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import gpupixel_port as G  # noqa: E402
import ops as O  # noqa: E402

# 106-point pairs (3,44) (29,44) (7,45) (25,45) (10,46) (22,46) (14,49) (18,49) (16,49): contour point -> nose point.
# MediaPipe equivalents: left contour 58, 136, 150, 176; right 288, 365, 378, 400; chin 152; nose 6 (bridge top), 197, 195, 4 (tip).
THIN_PAIRS = [(58, 6), (288, 6), (136, 197), (365, 197), (150, 195), (378, 195), (176, 4), (400, 4), (152, 4)]
EYES = [((33, 133, 159, 145), 159), ((362, 263, 386, 374), 386)]   # eye centre (mean of corners and lids) -> upper-lid point (106-pt 74->72, 77->75); works with 468 or 478 points
# strength ranges (set by calibrate() against the Alibaba 30-90 effect sizes, then widened x1.5 for AR-type filters)
RANGE = {"thin": (0.01, 0.06), "eye": (0.05, 0.30), "smooth": (0.3, 1.0), "white": (0.01, 0.12)}


def reshape_map(h, w, lm, thin=0.0, eye=0.0):
    X, Y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    if thin > 0:
        for a, b in THIN_PAIRS:
            ox, oy = lm[a]; tx, ty = lm[b]; r = float(np.hypot(tx - ox, ty - oy)) + 1e-6
            d = np.sqrt((X - ox) ** 2 + (Y - oy) ** 2); ratio = np.clip(1.0 - d / r, 0.0, 1.0)
            X = X - (tx - ox) * thin * ratio; Y = Y - (ty - oy) * thin * ratio
    if eye > 0:
        for c, o in EYES:
            cx, cy = lm[list(c)].mean(0); r = 5.0 * float(np.hypot(*(lm[o] - np.array([cx, cy]))))
            wgt = np.sqrt((X - cx) ** 2 + (Y - cy) ** 2) / r
            wgt = np.clip(1.0 - (1.0 - wgt * wgt) * eye, 0.0, 1.0)
            X = cx + (X - cx) * wgt; Y = cy + (Y - cy) * wgt
    return X, Y


def apply(rgb, lm, rng, ops=None, strengths=None):
    """ops: subset of ["eye", "jaw", "white", "smooth"] (None = random non-empty subset); strengths: dict or None (random)."""
    names = ["eye", "jaw", "white", "smooth"]
    if ops is None:
        k = int(rng.integers(1, 5)); ops = list(rng.choice(names, k, replace=False))
    s = dict(strengths or {})
    for o in ops:
        if o not in s:
            lo, hi = RANGE[{"jaw": "thin"}.get(o, o)]; s[o] = float(rng.uniform(lo, hi))
    h, w = rgb.shape[:2]; out = rgb; lm2 = lm.copy(); q = np.zeros(4, np.float32)
    if "jaw" in ops or "eye" in ops:
        X, Y = reshape_map(h, w, lm, thin=s.get("jaw", 0.0), eye=s.get("eye", 0.0))
        out = cv2.remap(out, X, Y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        for k in (O.JAW_LEFT, O.JAW_RIGHT) + O.LEFT_EYE + O.RIGHT_EYE:
            lm2[k] = O._inverse_point(X, Y, lm[k])
        if "eye" in ops:
            q[0] = O.EYE_CAL * (O._eye_width(lm2) / O._eye_width(lm) - 1.0)
        if "jaw" in ops:
            q[1] = O.JAW_CAL * (1.0 - float(np.linalg.norm(lm2[O.JAW_LEFT] - lm2[O.JAW_RIGHT])) / float(np.linalg.norm(lm[O.JAW_LEFT] - lm[O.JAW_RIGHT])))
    if "smooth" in ops:
        m = O.hull_mask(lm2, h, w); L0 = O._L(out)
        out = G.beauty_at_scale(out, s["smooth"])
        q[3] = 1.0 - O._hf(O._L(out), m) / max(O._hf(L0, m), 1e-6)
    if "white" in ops:
        out, qw = O.op_white(out, lm2, rng, strength=s["white"]); q[2] = qw[2]
    pres = np.array([o in ops for o in names], np.float32)
    return out, pres, q, {o: s[o] for o in ops}


def calibrate(n=40):
    """Median measured effect per strength on FFHQ Part2 originals (Alibaba crops), for setting RANGE."""
    import json
    import measure_pairs as M
    boxes = json.loads((HERE / "ffhq_boxes.json").read_text()); orig = Path(r"C:\My_Project\AIGC\ffhq_originals\Part2")
    stems = sorted(p.stem for p in orig.glob("*.png") if p.stem in boxes)[:n]; imgs = []
    for st in stems:
        im = np.array(cv2.cvtColor(cv2.imread(str(orig / f"{st}.png")), cv2.COLOR_BGR2RGB)); x0, y0, x1, y1 = boxes[st]; im = im[y0:y1, x0:x1]
        im = cv2.resize(im, (512, 512), interpolation=cv2.INTER_AREA); lm = M.get_landmarks(im)
        if lm is not None:
            imgs.append((im, lm))
    rng = np.random.default_rng(0)
    for op, vals in [("eye", [0.05, 0.1, 0.2, 0.3])]:
        for v in vals:
            eff = []
            for im, lm in imgs:
                out, _, q, _ = apply(im, lm, rng, ops=[op], strengths={op: v}); lr = M.get_landmarks(out)
                if lr is None:
                    continue
                jo, eo = M.geo(lm); jr, er = M.geo(lr); m = M.hull_mask(lm, *im.shape[:2])
                Lo = cv2.cvtColor(im, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32); Lr = cv2.cvtColor(out, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
                hf = lambda L: np.abs(L - cv2.GaussianBlur(L, (0, 0), 3))[m].mean()
                eff.append([er / eo, jr / jo, float((Lr - Lo)[m].mean()), hf(Lr) / max(hf(Lo), 1e-6)])
            if not eff:
                print(op, v, "no landmarks"); continue
            e = np.median(np.array(eff), 0); print(f"{op} {v}: eye {e[0]:.3f} jaw {e[1]:.3f} dL {e[2]:.2f} hf {e[3]:.3f} (n {len(eff)})", flush=True)


if __name__ == "__main__":
    calibrate()
