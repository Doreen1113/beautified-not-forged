"""Tiles for fig_model (the model architecture figure): the held-out part-level forgery of fig_method (FF++ test frame 682,
nose from a donor), its 16x16 evidence map from the main model (clipe5 seed 20260929, sigmoid of the evidence head, as the
model outputs it before any upsampling) and the training target at the same grid (exact footprint vs the pixel-aligned
original, train_ru3.footprint, resized to 16x16 with INTER_AREA as train_ru3.RUData3 does).
-> figs/model_in.png, figs/model_ev16.png, figs/model_M16.png, figs/model_numbers.json"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from matplotlib import colormaps

HERE = Path(__file__).resolve().parent; FIG = HERE / "figs"
sys.path.insert(0, str(HERE))
import make_tiles_method as T  # noqa: E402  (part_edit, main_model, paths)
from train_ru3 import footprint  # noqa: E402  (importable once make_tiles_method has set sys.path)

PX = 320   # tile size; every 16x16 cell is 20 px


def cells(a, rgb_of):
    """16x16 array -> PX x PX image, nearest upsampling, 1 px white grid lines between cells."""
    im = np.repeat(np.repeat(rgb_of(a), PX // 16, 0), PX // 16, 1)
    im[::PX // 16, :, :] = 255; im[:, ::PX // 16, :] = 255
    return np.ascontiguousarray(im)


def main():
    it, x = T.part_edit()
    x0 = cv2.imread(it["x0"])[..., ::-1].copy()
    S = min(x.shape[:2]); xs, x0s = np.ascontiguousarray(x[:S, :S]), np.ascontiguousarray(x0[:S, :S])
    tag, run = T.main_model()
    p, pr, ev = run(x, 380)                        # as make_tiles_method.outputs: whole image at 380, then 224 inside
    M16 = cv2.resize(footprint(xs, x0s), (16, 16), interpolation=cv2.INTER_AREA)
    cv2.imwrite(str(FIG / "model_in.png"), cv2.resize(xs, (PX, PX), interpolation=cv2.INTER_AREA)[..., ::-1])
    inferno = colormaps["inferno"]
    ev_rgb = cells(ev, lambda a: (inferno(np.clip(a, 0, 1))[..., :3] * 255).astype(np.uint8))
    cv2.imwrite(str(FIG / "model_ev16.png"), ev_rgb[..., ::-1])
    lo, hi = np.array([238, 238, 238], np.float32), np.array(T.NN, np.float32)   # footprint cyan of fig_method
    M_rgb = cells(M16, lambda a: (lo + (hi - lo) * a[..., None]).astype(np.uint8))
    cv2.imwrite(str(FIG / "model_M16.png"), M_rgb[..., ::-1])
    pm, named = T.part_means(x, ev)
    num = {"model": tag, "image": it["x"], "p_real_forged_beautified": [round(float(v), 3) for v in p],
           "ops_eye_contour_tone_texture": [round(float(v), 3) for v in pr], "evidence_max": round(float(ev.max()), 3),
           "M16_cells_over_half": int((M16 > 0.5).sum()), "part_means": pm, "named": named}
    (FIG / "model_numbers.json").write_text(json.dumps(num, indent=1), encoding="utf-8"); print(json.dumps(num, indent=1))


if __name__ == "__main__":
    main()
