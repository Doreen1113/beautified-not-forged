"""Tiles for fig_engine (how a commercial render is split into single operations), from the same Tencent pair as fig_method
(FFHQ 60002) and the same code (results/research/retouch_unified_20260929/decompose.py, steps repeated here so the
intermediate fields can be drawn):
  flow  : DIS optical flow f on locally normalised luminance, O(x+f) ~ R(x); drawn as arrows over O (length x6, every 16 px)
  eyes  : the eye mask m_e built from landmarks (circles of 1.9 eye widths, blurred), over O
  resid : photometric residual P = R - O(x+f), mean over RGB, diverging map clipped at its 99.5th |P| percentile
  low / high : the Gaussian low-pass (sigma 6 px) and high-pass parts of P, same scale as P
Also checks that the steps reproduce decompose.decompose (components bit-identical, reconstruction PSNR) and writes
figs/engine_numbers.json. The component tiles themselves are method_comp_*.png (make_tiles_method.py vendor()).
python make_tiles_engine.py"""
import json

import cv2
import numpy as np
from matplotlib import colormaps

import make_tiles_method as T
D = T.D
STEM = "60002"


def main():
    row = [l.split("\t") for l in (T.RU / "pairs_tencent.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.split("\t")[0].endswith(f"{STEM}.png")][0]
    O0, R0, comp_ref, psnr = D.decompose(row[0], row[1], STEM)
    S = D.S
    O = np.ascontiguousarray(cv2.resize(cv2.imread(row[0])[..., ::-1], (S, S), interpolation=cv2.INTER_AREA))
    R = cv2.imread(row[1])[..., ::-1]
    R = np.ascontiguousarray(cv2.resize(R, (S, S), interpolation=cv2.INTER_AREA) if R.shape[0] != S else R)
    no, nr = D.norm_lum(O), D.norm_lum(R)
    f = D.flow(nr, no); g = D.flow(no, nr)
    f = cv2.GaussianBlur(f, (0, 0), 2.0); g = cv2.GaussianBlur(g, (0, 0), 2.0); f[np.linalg.norm(f, axis=2) < 0.15] = 0
    lm = D.LM[STEM] * (S / 1024.0); me = D.eye_mask(lm, S, S)
    Wp = D.sample(O, f).astype(np.float32); P = R.astype(np.float32) - Wp
    low = cv2.GaussianBlur(P, (0, 0), 6.0); high = P - low
    comp = {"eye": D.sample(O, f * me[..., None]), "jaw": D.sample(O, f * (1 - me[..., None])),
            "white": np.clip(O + D.sample(low, g), 0, 255).astype(np.uint8), "smooth": np.clip(O + D.sample(high, g), 0, 255).astype(np.uint8)}
    same = {k: bool(np.array_equal(np.asarray(comp[k]), np.asarray(comp_ref[k]))) for k in comp}

    b = [int(v / 2) for v in json.loads((T.RU / "ffhq_boxes.json").read_text())[STEM]]
    crop = lambda im: np.ascontiguousarray(im[b[1]:b[3], b[0]:b[2]])
    grey = lambda im: np.repeat(cv2.cvtColor(im, cv2.COLOR_RGB2GRAY)[..., None], 3, 2).astype(np.float32) * 0.55 + 255 * 0.45

    # flow arrows over O (crop coordinates, then fitted to the tile)
    oc = crop(O); fc = crop(f); hgt, wid = oc.shape[:2]; sx, sy = T.W / wid, T.H / hgt
    tile = T.fit(grey(oc)).astype(np.uint8).copy()
    mags = []
    for y in range(8, hgt, 16):
        for x in range(8, wid, 16):
            u, v = fc[y, x]; m = float(np.hypot(u, v)); mags.append(m)
            if m < 0.3:
                continue
            p0 = (int(x * sx), int(y * sy)); p1 = (int((x + 6 * u) * sx), int((y + 6 * v) * sy))
            cv2.arrowedLine(tile, p0, p1, (15, 77, 146), 2, cv2.LINE_AA, tipLength=0.35)
    out = {"flow": tile}
    # eye mask
    mc = crop(me); t2 = T.fit(grey(oc)); a = T.fit(mc[..., None].repeat(3, 2))
    out["eyes"] = (t2 * (1 - 0.55 * a) + np.array([15, 77, 146], np.float32) * 0.55 * a)
    # residual and its two parts, diverging, one scale
    Pm, Lm, Hm = (crop(x).mean(2) for x in (P, low, high))
    rdbu = colormaps["RdBu_r"]

    def div(a, s):
        return (rdbu(np.clip(0.5 + 0.5 * a / s, 0, 1))[..., :3] * 255).astype(np.uint8)
    sP = max(float(np.percentile(np.abs(Pm), 99.5)), 1.0)
    out["resid"] = T.fit(div(Pm, sP)); out["low"] = T.fit(div(Lm, sP)); out["high"] = T.fit(div(Hm, sP))
    for k, v in out.items():
        cv2.imwrite(str(T.OUT / f"engine_{k}.png"), np.ascontiguousarray(np.clip(v, 0, 255).astype(np.uint8))[..., ::-1])
    face = crop(np.linalg.norm(f, axis=2))
    num = {"stem": STEM, "render": row[1], "recon_psnr_db": round(psnr, 1), "components_identical_to_decompose": same,
           "flow_px_at_512_median_in_crop": round(float(np.median(face)), 3), "flow_px_at_512_p99_in_crop": round(float(np.percentile(face, 99)), 3),
           "residual_scale_99p5_abs": round(sP, 2), "arrow_scale": 6, "arrow_grid_px": 16}
    (T.OUT / "engine_numbers.json").write_text(json.dumps(num, indent=1), encoding="utf-8"); print(json.dumps(num, indent=1))


if __name__ == "__main__":
    main()
