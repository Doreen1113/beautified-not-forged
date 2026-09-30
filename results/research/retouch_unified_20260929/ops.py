"""Parametric single-operation beautification with continuous strength and ANALYTIC targets (no landmark re-detection).

Each op takes an RGB uint8 image and its 478-point MediaPipe landmarks and returns (out, q) where q is the 4-vector of
verifiable quantities in the paper's convention:
    q = (eye_ratio - 1, 1 - jaw_ratio, dL_skin / 20, 1 - hf_ratio)
i.e. positive = "eyes enlarged", "face slimmer", "skin brighter", "skin smoother". Targets for the two geometric ops are read
off the warp map at the landmark positions (fixed-point solve of the inverse map); the two photometric ones are measured
directly on the L channel inside the face hull, exactly as measure_pairs.py measures vendor pairs.

Face slimming moves cheek content TOWARDS the nose (jaw_ratio < 1). The project's earlier remap wrote the opposite
direction (face_reshaping_direction_audit_20260913); verify_ops.py checks this against re-detected landmarks.
"""
import cv2
import numpy as np

LEFT_EYE = (33, 133, 159, 145)
RIGHT_EYE = (362, 263, 386, 374)
JAW_LEFT, JAW_RIGHT, NOSE_TIP = 234, 454, 1
OPS = ["eye", "jaw", "white", "smooth"]   # order of q and of the presence vector
# calib_ops.py (120 samples each): re-detected landmarks under-read the analytic warp displacement; targets are scaled to the
# measured convention so synthetic and vendor (measure_pairs.py) targets share one scale. eye corr 0.68, jaw corr 0.81.
EYE_CAL, JAW_CAL = 0.412, 0.697


def hull_mask(lm, h, w):
    m = np.zeros((h, w), np.uint8); cv2.fillConvexPoly(m, cv2.convexHull(lm.astype(np.float32)).astype(np.int32), 255); return m > 0


def _L(rgb):
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)


def _hf(L, m):
    return float(np.abs(L - cv2.GaussianBlur(L, (0, 0), 3))[m].mean())


def _inverse_point(map_x, map_y, p, iters=8):
    """Where does source point p land in the output? Solve f(g) = p for the remap f(g) = (map_x[g], map_y[g])."""
    h, w = map_x.shape; g = p.astype(np.float64).copy()
    for _ in range(iters):
        x = int(np.clip(round(g[0]), 0, w - 1)); y = int(np.clip(round(g[1]), 0, h - 1))
        f = np.array([map_x[y, x], map_y[y, x]], np.float64)
        g = g + (p - f)
    return g


def _eye_width(lm):
    return float(np.mean([np.linalg.norm(lm[e[0]] - lm[e[1]]) for e in (LEFT_EYE, RIGHT_EYE)]))


def op_eye(rgb, lm, rng, scale=None):
    """Eye enlarging, scale in [1.06, 1.40]; identical warp to the project's v1/v2 generator."""
    scale = float(rng.uniform(1.06, 1.40)) if scale is None else scale
    h, w = rgb.shape[:2]; out = rgb.copy(); lm2 = lm.copy()
    for eye in (LEFT_EYE, RIGHT_EYE):
        pts = lm[list(eye)]; cx, cy = pts.mean(0); eye_w = float(np.linalg.norm(lm[eye[0]] - lm[eye[1]]))
        radius = max(eye_w * 1.70, 8.0)
        x0 = max(0, int(cx - radius)); x1 = min(w, int(cx + radius + 1)); y0 = max(0, int(cy - radius)); y1 = min(h, int(cy + radius + 1))
        gx, gy = np.meshgrid(np.arange(x0, x1, dtype=np.float32), np.arange(y0, y1, dtype=np.float32))
        dx, dy = gx - cx, gy - cy; nd = np.clip(np.sqrt(dx ** 2 + dy ** 2) / radius, 0, 1)
        ls = 1.0 + (scale - 1.0) * (1.0 - nd) ** 2
        mx = (cx + dx / ls).astype(np.float32); my = (cy + dy / ls).astype(np.float32)
        roi = cv2.remap(rgb, mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101)
        alpha = np.clip((1.0 - nd) / 0.18, 0, 1)[..., None]
        out[y0:y1, x0:x1] = np.clip(out[y0:y1, x0:x1] * (1 - alpha) + roi * alpha, 0, 255).astype(np.uint8)
        for k in eye:   # landmark moves outward: source distance d -> output distance d*ls(g), solved on the local map
            p = lm[k].astype(np.float64); g = p.copy()
            for _ in range(8):
                d = np.array([g[0] - cx, g[1] - cy]); n = min(np.linalg.norm(d) / radius, 1.0)
                l = 1.0 + (scale - 1.0) * (1.0 - n) ** 2
                g = np.array([cx, cy]) + (p - np.array([cx, cy])) * l
            lm2[k] = g
    q = np.zeros(4, np.float32); q[0] = EYE_CAL * (_eye_width(lm2) / _eye_width(lm) - 1.0)
    return out, q


def op_jaw(rgb, lm, rng, shrink=None):
    """Face slimming: cheek content pulled towards the nose tip; strength = fraction of the cheek displacement, in [0.03, 0.14]."""
    shrink = float(rng.uniform(0.03, 0.14)) if shrink is None else shrink
    h, w = rgb.shape[:2]; center = lm[NOSE_TIP].astype(np.float32)
    jaw_w = float(np.linalg.norm(lm[JAW_LEFT] - lm[JAW_RIGHT])); radius = float(np.clip(0.45 * jaw_w, 15, 400))
    map_x, map_y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    for k in (JAW_LEFT, JAW_RIGHT):
        cx, cy = lm[k]
        x0, x1 = max(0, int(cx - radius)), min(w, int(cx + radius)); y0, y1 = max(0, int(cy - radius)), min(h, int(cy + radius))
        if x1 <= x0 or y1 <= y0:
            continue
        gx = map_x[y0:y1, x0:x1]; gy = map_y[y0:y1, x0:x1]
        dist = np.sqrt((gx - cx) ** 2 + (gy - cy) ** 2); within = dist < radius
        # output pixel g shows source content farther from the nose (factor > 1) => content moves inward => slimmer
        factor = np.where(within, 1 + shrink * (1 - dist / radius), 1.0)
        map_x[y0:y1, x0:x1] = np.where(within, center[0] + (gx - center[0]) * factor, gx)
        map_y[y0:y1, x0:x1] = np.where(within, center[1] + (gy - center[1]) * factor, gy)
    out = cv2.remap(rgb, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    g_l = _inverse_point(map_x, map_y, lm[JAW_LEFT]); g_r = _inverse_point(map_x, map_y, lm[JAW_RIGHT])
    q = np.zeros(4, np.float32); q[1] = JAW_CAL * (1.0 - float(np.linalg.norm(g_l - g_r)) / jaw_w)
    return out, q


def op_white(rgb, lm, rng, strength=None):
    """Whitening: LAB-L push L + s(255-L) inside a feathered face hull, s in [0.05, 0.35]."""
    strength = float(rng.uniform(0.05, 0.35)) if strength is None else strength
    h, w = rgb.shape[:2]; m = hull_mask(lm, h, w)
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32); L0 = lab[..., 0].copy()
    lab[..., 0] = L0 + strength * (255.0 - L0)
    whole = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2RGB)
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), max(2.0, 0.01 * w))[..., None]
    out = np.clip(rgb * (1 - a) + whole * a, 0, 255).astype(np.uint8)
    q = np.zeros(4, np.float32); q[2] = float((_L(out) - L0)[m].mean()) / 20.0
    return out, q


def op_smooth(rgb, lm, rng, frac=None, mix=1.0):
    """Skin smoothing: bilateral filter with diameter = frac * jaw width (frac in [0.03, 0.12]) blended inside the hull,
    with an extra blend weight `mix` (RU2: light, vendor-like strengths)."""
    frac = float(rng.uniform(0.03, 0.12)) if frac is None else frac
    h, w = rgb.shape[:2]; m = hull_mask(lm, h, w)
    jaw_w = float(np.linalg.norm(lm[JAW_LEFT] - lm[JAW_RIGHT])); d = int(np.clip(round(frac * jaw_w), 5, 45)) | 1
    sigma = float(np.clip(d * 80.0 / 15.0, 30, 160))
    sm = cv2.bilateralFilter(rgb, d, sigma, sigma)
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), max(2.0, 0.01 * w))[..., None] * mix
    out = np.clip(rgb * (1 - a) + sm * a, 0, 255).astype(np.uint8)
    L0 = _L(rgb); q = np.zeros(4, np.float32); q[3] = 1.0 - _hf(_L(out), m) / max(_hf(L0, m), 1e-6)
    return out, q


OP_FN = {"eye": op_eye, "jaw": op_jaw, "white": op_white, "smooth": op_smooth}


def random_op(rgb, lm, rng):
    """One random single operation; returns out, presence(4), q(4), name."""
    i = int(rng.integers(0, 4)); name = OPS[i]
    out, q = OP_FN[name](rgb, lm, rng)
    pres = np.zeros(4, np.float32); pres[i] = 1.0
    return out, pres, q, name


def _logu(rng, lo, hi):
    return float(np.exp(rng.uniform(np.log(lo), np.log(hi))))


def random_op_v2(rgb, lm, rng):
    """RU2: log-uniform strengths spanning the TRAINING vendors' measured range (Tencent levels 30-90, Megvii medians):
    eye +0.3..4.6 %, jaw -0.3..4 %, dL ~0.5..33, smoothing texture loss ~3..32 % (mix 0.03..0.4). Calibrated on FFHQ Part7 only."""
    i = int(rng.integers(0, 4)); name = OPS[i]
    if name == "eye":
        out, q = op_eye(rgb, lm, rng, scale=1.0 + _logu(rng, 0.015, 0.25))
    elif name == "jaw":
        out, q = op_jaw(rgb, lm, rng, shrink=_logu(rng, 0.005, 0.065))
    elif name == "white":
        out, q = op_white(rgb, lm, rng, strength=_logu(rng, 0.012, 0.33))
    else:
        out, q = op_smooth(rgb, lm, rng, frac=float(rng.uniform(0.03, 0.08)), mix=_logu(rng, 0.03, 0.4))
    pres = np.zeros(4, np.float32); pres[i] = 1.0
    return out, pres, q, name
