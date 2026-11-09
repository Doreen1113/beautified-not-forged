"""Tiles for the poster's model row (Method figure), all from ONE held-out record: the part-level forgery of the report's
fig_method (FF++ test frame 682, nose from a donor). Same model and preprocessing as report_v3/make_tiles_model.py
(clipe5 seed 20260929; whole image at 380 then 224 inside); evidence map = sigmoid of the evidence head at 16x16;
footprint M = train_ru3.footprint vs the pixel-aligned original, resized to 16x16 with INTER_AREA as training does;
part masks = occlusion_regions.region_masks on MediaPipe landmarks (as the page names the part).
Writes assets/tiles/model_{in,ev16,M16,evface,named}.png and assets/model_numbers.json.
python docs/capstone/poster/make_model_tiles.py"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from matplotlib import colormaps

B = Path(r"C:\My_Project\AIGC"); H = Path(__file__).resolve().parent; TL = H / "assets/tiles"
sys.path.insert(0, str(B / "docs/capstone/report_v3")); sys.path.insert(0, str(B / "docs/paper_v2"))
sys.path.insert(0, str(B / "results/research/retouch_unified_20260929")); sys.path.insert(0, str(B)); sys.path.insert(0, str(B / "docs/capstone/src"))
import make_tiles_method as T  # noqa: E402
from train_ru3 import footprint  # noqa: E402
from occlusion_regions import region_masks  # noqa: E402
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402

PX, GRID = 720, 480
NN = (38, 166, 220)          # footprint cyan, as in the data rows
PART = (255, 209, 102)       # named-part outline, as on the demo page


def cells(a, rgb_of, px=GRID):
    im = np.repeat(np.repeat(rgb_of(a), px // 16, 0), px // 16, 1)
    im[::px // 16, :, :] = 255; im[:, ::px // 16, :] = 255
    return np.ascontiguousarray(im)


def w(name, rgb):
    cv2.imwrite(str(TL / f"model_{name}.png"), np.ascontiguousarray(rgb)[..., ::-1]); print("wrote", name, rgb.shape[:2])


def main():
    it, x = T.part_edit()
    x0 = cv2.imread(it["x0"])[..., ::-1].copy()
    S = min(x.shape[:2]); xs, x0s = np.ascontiguousarray(x[:S, :S]), np.ascontiguousarray(x0[:S, :S])
    tag, run = T.main_model()
    p, pr, ev = run(x, 380)
    M16 = cv2.resize(footprint(xs, x0s), (16, 16), interpolation=cv2.INTER_AREA)
    w("in", cv2.resize(xs, (PX, PX), interpolation=cv2.INTER_AREA))
    inferno = colormaps["inferno"]
    w("ev16", cells(ev, lambda a: (inferno(np.clip(a, 0, 1))[..., :3] * 255).astype(np.uint8)))
    lo, hi = np.array([238, 238, 238], np.float32), np.array(NN, np.float32)
    w("M16", cells(M16, lambda a: (lo + (hi - lo) * a[..., None]).astype(np.uint8)))
    # evidence on the face: bilinear upsampling, inferno, opacity = value, white contour at 0.5 (as report fig_arch)
    e_up = np.clip(cv2.resize(ev, (S, S), interpolation=cv2.INTER_LINEAR), 0, 1)
    heat = (inferno(e_up)[..., :3] * 255).astype(np.float32)
    c = xs.astype(np.float32) * (1 - (e_up * 0.85)[..., None]) + heat * (e_up * 0.85)[..., None]
    c = np.clip(c, 0, 255).astype(np.uint8).copy()
    cs, _ = cv2.findContours((e_up >= 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(c, cs, -1, (255, 255, 255), 3, cv2.LINE_AA)
    w("evface", cv2.resize(c, (PX, PX), interpolation=cv2.INTER_AREA))
    # named part: mean evidence per landmark part, the top part outlined on the plain crop
    lm = np.asarray(get_landmarks(np.ascontiguousarray(x)), np.float32)[:, :2]
    M = region_masks(x, lm)
    e_full = cv2.resize(ev, (x.shape[1], x.shape[0]), interpolation=cv2.INTER_LINEAR)
    pm = {k: round(float(e_full[np.asarray(m) > 0].mean()), 3) for k, m in M.items() if np.asarray(m).sum() > 0}
    named = max(pm, key=pm.get)
    n = xs.copy()
    cs, _ = cv2.findContours(np.asarray(M[named]).astype(np.uint8)[:S, :S], cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(n, cs, -1, PART, 7, cv2.LINE_AA)
    w("named", cv2.resize(n, (PX, PX), interpolation=cv2.INTER_AREA))
    num = {"model": tag, "image": it["x"], "p_real_forged_beautified": [round(float(v), 3) for v in p],
           "ops_eye_contour_tone_texture": [round(float(v), 3) for v in pr], "evidence_max": round(float(ev.max()), 3),
           "M16_cells_over_half": int((M16 > 0.5).sum()), "part_means": pm, "named": named}
    (H / "assets/model_numbers.json").write_text(json.dumps(num, indent=1), encoding="utf-8"); print(json.dumps(num, indent=1))


if __name__ == "__main__":
    main()
