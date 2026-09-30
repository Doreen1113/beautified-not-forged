"""Part-level fake generation on FF++ real frames with EXACT ground-truth masks (two mechanisms).

  donor   : landmark-aligned part transplant from a different identity (affine on part landmarks, feathered blend)
  inpaint : Stable Diffusion 1.5 inpainting restricted to the part mask (512 px working resolution)

Parts: eyes (both), nose, mouth. Every output stores the binary mask actually used for compositing.

python part_edit_gen.py --demo            -> demo_grid.jpg (4 photos x parts x mechanisms)
python part_edit_gen.py --n 2000 --part all --mech both   (full generation, later)
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image

BASE = Path(r"C:\My_Project\AIGC")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "docs/paper_v2"))
from occlusion_regions import L_EYE, LIPS, NOSE, R_EYE  # noqa: E402  MediaPipe index sets
sys.path.insert(0, str(BASE))
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402

REAL = BASE / "FaceForensics_protocol_frames_dense/train/real"
LM = np.load(BASE / "results/research/fasb_20260926/landmarks_train.npz")
STEMS = sorted(LM.files)
PARTS = {"eyes": R_EYE + L_EYE, "nose": NOSE, "mouth": LIPS}
PROMPT = {"eyes": "close-up photo of a person's eyes, natural skin, realistic",
          "nose": "close-up photo of a person's nose, natural skin, realistic",
          "mouth": "close-up photo of a person's natural lips, realistic skin, plain"}
NEG = "object, text, teeth grill, jewelry, blurry, deformed, cartoon, painting, black"
STRENGTH = {"eyes": 0.85, "nose": 0.85, "mouth": 0.7}


def part_mask(shape, lm, part, grow=0.08):
    pts = lm[PARTS[part]].astype(np.float32)
    fw = lm[:, 0].max() - lm[:, 0].min(); k = max(3, int(fw * grow)) | 1
    m = np.zeros(shape[:2], np.uint8)
    if part == "eyes":  # two hulls, not one bridge-spanning hull
        for idx in (R_EYE, L_EYE):
            cv2.fillConvexPoly(m, cv2.convexHull(lm[idx].astype(np.int32)), 1)
    else:
        cv2.fillConvexPoly(m, cv2.convexHull(pts.astype(np.int32)), 1)
    m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    return m.astype(bool)


def load(stem):
    return np.array(Image.open(REAL / f"{stem}.jpg").convert("RGB")), LM[stem][:, :2].astype(np.float32)


# --------------------------------------------------------------------------- mechanism 1: donor transplant
def donor_edit(img, lm, part, rng, tries=20):
    """Warp the same part from a different identity onto img via similarity transform on part landmarks."""
    idx = PARTS[part]
    for _ in range(tries):
        ds = STEMS[int(rng.integers(0, len(STEMS)))]
        if ds.split("__")[0] == "":  # never same video
            continue
        dimg, dlm = load(ds)
        M, _ = cv2.estimateAffinePartial2D(dlm[idx], lm[idx], method=cv2.LMEDS)
        if M is None:
            continue
        warped = cv2.warpAffine(dimg, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
        m = part_mask(img.shape, lm, part)
        # colour-match donor part to target skin statistics inside the mask
        a, b = warped[m].astype(np.float32), img[m].astype(np.float32)
        warped = np.clip((warped.astype(np.float32) - a.mean(0)) * (b.std(0) / (a.std(0) + 1e-6)) + b.mean(0), 0, 255)
        fw = lm[:, 0].max() - lm[:, 0].min(); s = max(1.0, fw * 0.03)
        alpha = cv2.GaussianBlur(m.astype(np.float32), (0, 0), s)[..., None]
        out = (alpha * warped + (1 - alpha) * img.astype(np.float32)).astype(np.uint8)
        return out, m, ds
    return None, None, None


# --------------------------------------------------------------------------- mechanism 2: diffusion inpainting
_PIPE = None
_PIPE_XL = None


def pipe_xl():
    """Held-out third mechanism (PRE_DECLARED cgd §3): SDXL inpainting, never used for training."""
    global _PIPE_XL
    if _PIPE_XL is None:
        from diffusers import AutoPipelineForInpainting
        _PIPE_XL = AutoPipelineForInpainting.from_pretrained("diffusers/stable-diffusion-xl-1.0-inpainting-0.1",
                                                             torch_dtype=torch.float16, variant="fp16").to("cuda")
        _PIPE_XL.set_progress_bar_config(disable=True)
    return _PIPE_XL


def pipe():
    global _PIPE
    if _PIPE is None:
        from diffusers import StableDiffusionInpaintPipeline
        _PIPE = StableDiffusionInpaintPipeline.from_pretrained("stable-diffusion-v1-5/stable-diffusion-inpainting",
                                                               torch_dtype=torch.float16, safety_checker=None).to("cuda")
        _PIPE.set_progress_bar_config(disable=True)
    return _PIPE


def quality_ok(img, out, lm, part, m):
    """Reject degenerate inpaints: the part must still be detected close to where it was, and must not turn into a
    dark/blown-out blob (SD sometimes paints an object or black lips)."""
    lm2 = get_landmarks(np.ascontiguousarray(out))
    if lm2 is None:
        return False, "no_face"
    fw = lm[:, 0].max() - lm[:, 0].min()
    disp = np.linalg.norm(lm2[PARTS[part]] - lm[PARTS[part]], axis=1).mean()
    if disp > 0.06 * fw:
        return False, f"landmark_shift_{disp / fw:.3f}"
    L0 = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)[..., 0][m].astype(np.float32)
    L1 = cv2.cvtColor(out, cv2.COLOR_RGB2LAB)[..., 0][m].astype(np.float32)
    if abs(L1.mean() - L0.mean()) > 35 or L1.std() > 2.5 * L0.std() + 10:
        return False, "luminance"
    d = np.abs(out.astype(np.float32) - img.astype(np.float32)).mean(2)[m]
    if d.mean() > 60 or (d > 120).mean() > 0.15:   # an inserted object / colour blob, not a re-textured part
        return False, f"delta_{d.mean():.1f}"
    return True, "ok"


def inpaint_edit(img, lm, part, rng, steps=30, strength=None, tries=3, xl=False):
    strength = STRENGTH[part] if strength is None else strength
    for _ in range(tries):
        out, m = _inpaint_once(img, lm, part, rng, steps, strength, xl=xl)
        ok, why = quality_ok(img, out, lm, part, m)
        if ok:
            return out, m
    return None, None


def _inpaint_once(img, lm, part, rng, steps=30, strength=1.0, xl=False):
    m = part_mask(img.shape, lm, part)
    h, w = img.shape[:2]
    S = 1024 if xl else 512
    im512 = Image.fromarray(img).resize((S, S), Image.BICUBIC)
    mk512 = Image.fromarray((m * 255).astype(np.uint8)).resize((S, S), Image.NEAREST)
    g = torch.Generator("cuda").manual_seed(int(rng.integers(0, 2 ** 31 - 1)))
    out = (pipe_xl() if xl else pipe())(prompt=PROMPT[part], negative_prompt=NEG,
                 image=im512, mask_image=mk512, num_inference_steps=steps, strength=strength,
                 guidance_scale=6.0, generator=g).images[0]
    out = np.array(out.resize((w, h), Image.LANCZOS))
    # keep untouched pixels bit-exact outside the (feathered) mask, so the GT mask is exact
    fw = lm[:, 0].max() - lm[:, 0].min(); s = max(1.0, fw * 0.02)
    alpha = cv2.GaussianBlur(m.astype(np.float32), (0, 0), s)[..., None]
    return (alpha * out.astype(np.float32) + (1 - alpha) * img.astype(np.float32)).astype(np.uint8), m


def demo_sd_only():
    rng = np.random.default_rng(2)
    rows = []
    for i in (500, 9000, 17000, 30000, 4000, 22000):
        img, lm = load(STEMS[i]); tiles = [img]
        for part in ("eyes", "nose", "mouth"):
            p, m = inpaint_edit(img, lm, part, rng); tiles.append(p if p is not None else np.zeros_like(img))
        rows.append(np.concatenate([cv2.resize(t, (200, 240)) for t in tiles], 1))
    cv2.imwrite(str(HERE / "demo_grid_sd.jpg"), np.concatenate(rows, 0)[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 92]); print("demo_grid_sd.jpg")


def demo(mech="both"):
    rng = np.random.default_rng(1)
    stems = [STEMS[i] for i in (500, 9000, 17000, 30000)]
    rows = []
    for st in stems:
        img, lm = load(st)
        tiles = [img]
        for part in ("eyes", "nose", "mouth"):
            d, m, _ = donor_edit(img, lm, part, rng)
            tiles.append(d if d is not None else img)
        for part in ("eyes", "nose", "mouth"):
            if mech == "both":
                p, m = inpaint_edit(img, lm, part, rng); tiles.append(p if p is not None else np.zeros_like(img))
        mk = np.zeros_like(img)
        for c, part in zip(((255, 80, 80), (80, 255, 80), (80, 120, 255)), ("eyes", "nose", "mouth")):
            mk[part_mask(img.shape, lm, part)] = c
        tiles.append((0.5 * img + 0.5 * mk).astype(np.uint8))
        rows.append(np.concatenate([cv2.resize(t, (200, 240)) for t in tiles], 1))
    grid = np.concatenate(rows, 0)
    hdr = np.full((28, grid.shape[1], 3), 255, np.uint8)
    names = ["real", "donor eyes", "donor nose", "donor mouth"] + (["SD eyes", "SD nose", "SD mouth"] if mech == "both" else []) + ["GT masks"]
    for i, t in enumerate(names):
        cv2.putText(hdr, t, (i * 200 + 8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (30, 30, 30), 1, cv2.LINE_AA)
    cv2.imwrite(str(HERE / f"demo_grid_{mech}.jpg"), np.concatenate([hdr, grid], 0)[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 92])
    print("demo_grid.jpg")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--demo", action="store_true"); ap.add_argument("--mech", default="both"); a = ap.parse_args()
    if a.demo and a.mech == "sd":
        demo_sd_only()
    elif a.demo:
        demo(a.mech)
