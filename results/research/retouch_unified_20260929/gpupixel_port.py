"""numpy port of GPUPixel BeautyFaceFilter skin smoothing (pixpark/gpupixel commit ef552bf8, Apache-2.0); see Addendum 54.
beauty(rgb_uint8, blur_alpha) -> rgb_uint8. Sharpen and whitening are 0 (not ported)."""
import numpy as np

TAPS = [(0, 1 / 9), (6, 2 / 9), (-6, 2 / 9), (14, 2 / 9), (-14, 2 / 9)]   # radius 4, texel spacing 4, offsets 1.5 / 3.5 steps


def _q(x):   # 8-bit RGBA framebuffer between passes
    return np.round(np.clip(x, 0.0, 1.0) * 255.0) / 255.0


def _shift(x, d, axis):   # sample at +d px with clamp-to-edge
    n = x.shape[axis]; idx = np.clip(np.arange(n) + d, 0, n - 1)
    return np.take(x, idx, axis=axis)


def box_blur(x):
    h = _q(sum(w * _shift(x, d, 1) for d, w in TAPS))
    return _q(sum(w * _shift(h, d, 0) for d, w in TAPS))


def beauty(rgb, blur_alpha, delta=7.07, theta=0.1):
    I = rgb.astype(np.float64) / 255.0
    mean = box_blur(I)                                   # BeautyFaceFilter's own box blur
    var = _q((I - box_blur(I)) * delta)                  # BoxHighPassFilter (its own blur, same settings), clamped to [0,1]
    if blur_alpha <= 0:
        return rgb.copy()
    p = np.clip((np.minimum(I[..., 0], mean[..., 0] - 0.1) - 0.2) * 4.0, 0.0, 1.0)
    mv = var.mean(-1)
    k = np.clip((1.0 - mv / (mv + theta)) * p * blur_alpha, 0.0, 1.0)[..., None]
    out = I * (1 - k) + mean * k
    return np.round(np.clip(out, 0, 1) * 255.0).astype(np.uint8)


def beauty_at_scale(rgb, blur_alpha, short=512):
    """Apply at camera scale: resize so the shorter side is `short` px (the engine's fixed 14 px taps assume camera-resolution
    faces), smooth, resize back with INTER_AREA (Addendum 54 amendment 1)."""
    import cv2
    h, w = rgb.shape[:2]; s = short / min(h, w)
    big = cv2.resize(rgb, (round(w * s), round(h * s)), interpolation=cv2.INTER_CUBIC if s > 1 else cv2.INTER_AREA)
    out = beauty(big, blur_alpha)
    return cv2.resize(out, (w, h), interpolation=cv2.INTER_AREA)
