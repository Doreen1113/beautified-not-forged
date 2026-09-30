"""Decompose a multi-operation commercial render R of original O into single-operation components, all in O's geometry:
  eye   : O warped by the render's flow inside the eye regions only
  jaw   : O warped by the render's flow outside the eye regions (face lifting / contour)
  white : O + low-pass photometric residual  (tone / brightness change)
  smooth: O + high-pass photometric residual (texture change)
Geometry: dense DIS optical flow on locally-normalised luminance (robust to the render's tone change), f: R -> O so that
O(x + f(x)) ~ R(x); the photometric residual P = R - O(x + f) is carried back to O's geometry with the inverse flow g.
By construction O(x+f) + P = R, so the four parts account for the whole render.

python decompose.py <src tencent|megvii> <shard> <nshards> [--check N]
  -> vendor_single/<src>/<op>/<stem>.png  (512 px, whole image) and decomp_<src>_<shard>.tsv (measured q per component)
"""
import sys
from pathlib import Path

import cv2
import numpy as np

BASE = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE)); sys.path.insert(0, str(HERE))
from measure_pairs import measure  # noqa: E402  (same measurement as vendor pairs and Alibaba ground truth)
from ops import LEFT_EYE, RIGHT_EYE  # noqa: E402
S = 512
OUT = BASE / "vendor_single"
LM = np.load(HERE / "ffhq_landmarks.npz")


def norm_lum(rgb):
    L = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
    m = cv2.GaussianBlur(L, (0, 0), 6); d = L - m; s = np.sqrt(cv2.GaussianBlur(d * d, (0, 0), 6)) + 2.0
    return np.clip(d / s * 40 + 128, 0, 255).astype(np.uint8)


DIS = None


def flow(a, b):
    global DIS
    if DIS is None:
        DIS = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
    return DIS.calc(a, b, None)


def sample(img, fl):
    h, w = fl.shape[:2]; gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return cv2.remap(img, gx + fl[..., 0], gy + fl[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)


def eye_mask(lm, h, w):
    m = np.zeros((h, w), np.float32)
    for eye in (LEFT_EYE, RIGHT_EYE):
        c = lm[list(eye)].mean(0); ew = np.linalg.norm(lm[eye[0]] - lm[eye[1]])
        cv2.circle(m, (int(c[0]), int(c[1])), int(ew * 1.9), 1.0, -1)
    return cv2.GaussianBlur(m, (0, 0), max(2.0, 0.006 * w))


def decompose(o_path, r_path, stem):
    O = cv2.resize(cv2.imread(str(o_path))[..., ::-1], (S, S), interpolation=cv2.INTER_AREA)
    R = cv2.imread(str(r_path))[..., ::-1]
    if R.shape[0] != S:
        R = cv2.resize(R, (S, S), interpolation=cv2.INTER_AREA)
    O = np.ascontiguousarray(O); R = np.ascontiguousarray(R)
    no, nr = norm_lum(O), norm_lum(R)
    f = flow(nr, no); g = flow(no, nr)                      # O(x+f)~R(x);  R(x+g)~O(x)
    f = cv2.GaussianBlur(f, (0, 0), 2.0); g = cv2.GaussianBlur(g, (0, 0), 2.0)
    f[np.linalg.norm(f, axis=2) < 0.15] = 0
    lm = LM[stem] * (S / 1024.0); me = eye_mask(lm, S, S)[..., None]
    W = sample(O, f).astype(np.float32); P = R.astype(np.float32) - W
    low = cv2.GaussianBlur(P, (0, 0), 6.0); high = P - low
    lowO, highO = sample(low, g), sample(high, g)
    comp = {"eye": sample(O, f * me), "jaw": sample(O, f * (1 - me)),
            "white": np.clip(O + lowO, 0, 255).astype(np.uint8), "smooth": np.clip(O + highO, 0, 255).astype(np.uint8)}
    recon_psnr = float(10 * np.log10(255 ** 2 / max(np.mean((np.clip(W + P, 0, 255) - R) ** 2), 1e-6)))
    return O, R, comp, recon_psnr


def main():
    src, shard, nsh = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]); check = int(sys.argv[5]) if "--check" in sys.argv else 0
    rows = [l.split("\t") for l in (HERE / f"pairs_{src}.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    rows = rows[shard::nsh][:check] if check else rows[shard::nsh]
    out = ["component\torig\tsrc_render\top\teye_ratio\tjaw_ratio\tdL_skin\thf_ratio\tmad_hull"]
    tmp = HERE / "_decomp_tmp"; tmp.mkdir(exist_ok=True)
    for i, r in enumerate(rows):
        o_path, r_path = r[0], r[1]; stem = Path(o_path).stem
        if stem not in LM.files:
            continue
        rname = Path(r_path).stem
        O, R, comp, _ = decompose(o_path, r_path, stem)
        o512 = tmp / f"o_{shard}.png"; cv2.imwrite(str(o512), O[..., ::-1])
        for op, im in comp.items():
            d = OUT / src / op; d.mkdir(parents=True, exist_ok=True); p = d / f"{rname}.png"
            cv2.imwrite(str(p), np.ascontiguousarray(im)[..., ::-1])
            m = measure(o512, p)
            if m:
                out.append("\t".join([str(p), o_path, r_path, op] + [f"{m[k]:.5f}" for k in ("eye_ratio", "jaw_ratio", "dL_skin", "hf_ratio", "mad_hull")]))
        if i % 200 == 0:
            print(src, shard, i, len(rows), flush=True)
    (HERE / f"decomp_{src}_{shard}{'_check' if check else ''}.tsv").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("DONE", len(out) - 1, flush=True)


if __name__ == "__main__":
    main()
