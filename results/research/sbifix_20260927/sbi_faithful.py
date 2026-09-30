"""Faithful self-blending (PRE_DECLARED §2): blend first, then ONE common transform + ONE crop shared by the triplet.

Differences from fasb.make_triplet (the deviations from official SBI found in sbiscale R0):
  1. common_transforms (colour + JPEG) is applied AFTER synthesis, with identical parameters to real/filter/fake;
  2. the elastic warp deforms the mask only, never the source image;
  3. an identical random crop (each side trims U(0, 6 %)) is applied to the whole triplet.
"""
import sys
from pathlib import Path

import cv2
import numpy as np

BASE = Path(r"C:\My_Project\AIGC")
sys.path.insert(0, str(BASE)); sys.path.insert(0, str(BASE / "results/research/fasb_20260926"))
from sbi.sbi_generator import blend_mask, common_transforms, rand_affine, random_hull, source_transforms  # noqa: E402
from fasb import beautify  # noqa: E402


def elastic_mask(mask, rng, alpha=50.0, sigma=7.0):
    h, w = mask.shape[:2]
    dx = cv2.GaussianBlur((rng.random((h, w)).astype(np.float32) * 2 - 1), (0, 0), sigma) * alpha
    dy = cv2.GaussianBlur((rng.random((h, w)).astype(np.float32) * 2 - 1), (0, 0), sigma) * alpha
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return cv2.remap(mask, gx + dx, gy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def self_blend(img, lm, rng):
    m, _ = random_hull(lm, img.shape, rng)
    if m is None or m.sum() < 16:
        return None
    if rng.random() < 0.5:
        src, _ = source_transforms(img.copy(), rng); tgt = img
    else:
        tgt, _ = source_transforms(img.copy(), rng); src = img
    src, m, _ = rand_affine(src, m, rng)      # affine: image + mask (official randaffine f)
    m = elastic_mask(m, rng)                   # elastic: mask only (official randaffine g)
    mb, _ = blend_mask(m, rng)
    if mb is None:
        return None
    mb = mb * float(rng.choice([0.25, 0.5, 0.75, 1.0, 1.0, 1.0]))
    out = mb[..., None] * src.astype(np.float32) + (1 - mb[..., None]) * tgt.astype(np.float32)
    return np.clip(out, 0, 255).astype(np.uint8)


def shared_post(imgs, rng):
    """Identical common transform and identical crop for every image of a triplet."""
    s = int(rng.integers(0, 2 ** 31 - 1))
    out = [None if im is None else common_transforms(im, np.random.default_rng(s))[0] for im in imgs]
    h, w = out[0].shape[:2]
    t, b, l, r = (rng.uniform(0, 0.06, 4) * np.array([h, h, w, w])).astype(int)
    return [None if im is None else np.ascontiguousarray(im[t:h - b, l:w - r]) for im in out]


def jitter_one(img, rng):
    return shared_post([img], rng)[0]


def make_triplet(rgb, lm, rng, p_compose=0.5, binary=False):
    fake = None
    for _ in range(4):
        fake = self_blend(rgb, lm, rng)
        if fake is not None:
            break
    if fake is None:
        fake = rgb.copy()
    filt = None
    if not binary:
        filt = beautify(rgb, rng)
        if rng.random() < p_compose:
            fake = beautify(fake, rng)
    real, filt, fake = shared_post([rgb, filt, fake], rng)
    return real, filt, fake
