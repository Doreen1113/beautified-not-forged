"""Region-RESTORATION explainability (replaces occlusion, which injects a blending-like seam and is confounded).

For each correctly classified edited FF++ test image (filter types: pixel-aligned paired original; forgeries: the
real frame of the same target video and frame index, resized to the fake crop -- approximate alignment), each facial
region is restored to the unedited pixels (feathered) and the drop in P(true class) is measured. Controls: full-image
restoration (upper bound) and an area-matched random-location patch (baseline).

python docs/paper_v2/restore_regions.py [n] -> figs/fig_restore.pdf|png, figs/restore_results.json
"""
import json
import os
import sys
from pathlib import Path

import cv2
import matplotlib
import numpy as np
import timm
import torch
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BASE = Path(r"C:\My_Project\AIGC")
sys.path.insert(0, str(BASE)); sys.path.insert(0, str(BASE / "docs/paper_v2"))
import make_figures as MF  # noqa: E402
from occlusion_regions import CK, REGIONS, T, probs, region_masks  # noqa: E402
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402

REAL = BASE / "FaceForensics_protocol_frames/test/real"


def paired_real(path, y):
    b = os.path.basename(path)
    if y == 2:
        vid, fr = b.split("__")[:2]
    else:
        vid, fr = b.split("_")[0], b.split("__")[1].replace(".jpg", "")
    q = REAL / f"{vid}__{fr}.jpg"
    return q if q.is_file() else None


def restore(ed, orig, m):
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 2)[..., None]
    return (ed * (1 - a) + orig * a).astype(np.uint8)


def random_patch_like(m, rng):
    h, w = m.shape; area = m.sum()
    s = int(np.sqrt(max(area, 16)))
    y0, x0 = rng.integers(0, max(1, h - s)), rng.integers(0, max(1, w - s))
    r = np.zeros_like(m); r[y0:y0 + s, x0:x0 + s] = True
    return r


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 80
    rows = [l.split("\t") for l in (BASE / "results/research/ffpp_unified_20260925/ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    groups = {}
    for p, y, v, src in rows:
        key = src.split(":")[0] if y == "1" else (src.split(":")[1] if y == "2" else None)
        if key:
            groups.setdefault((int(y), key), []).append(p)
    rng = np.random.default_rng(0)
    m = timm.create_model("tf_efficientnet_b4.ap_in1k", pretrained=False, num_classes=3)
    m.load_state_dict(torch.load(CK, map_location="cpu")); m = m.cuda().eval()
    res = {}
    for (y, key), lst in sorted(groups.items()):
        D = {r: [] for r in REGIONS + ["full", "random"]}; used = 0
        for p in rng.permutation(lst):
            q = paired_real(p, y)
            if q is None:
                continue
            ed = np.array(Image.open(p).convert("RGB"))
            orig = np.array(Image.open(q).convert("RGB").resize(ed.shape[1::-1], Image.BILINEAR))
            p0 = probs(m, [ed])[0]
            if p0.argmax() != y:
                continue
            lm = get_landmarks(np.ascontiguousarray(orig))
            if lm is None:
                continue
            M = region_masks(ed, np.asarray(lm, np.float32)[:, :2])
            ims = [restore(ed, orig, M[r]) for r in REGIONS] + [orig]
            rnd = [restore(ed, orig, random_patch_like(M[r], rng)) for r in REGIONS]
            po = probs(m, ims + rnd)
            for j, r in enumerate(REGIONS):
                D[r].append(float(p0[y] - po[j, y]))
            D["full"].append(float(p0[y] - po[len(REGIONS), y]))
            D["random"].append(float(np.mean([p0[y] - po[len(REGIONS) + 1 + j, y] for j in range(len(REGIONS))])))
            used += 1
            if used == n:
                break
        k = f"{['real', 'fake', 'filter'][y]}:{key}"
        res[k] = {r: float(np.mean(v)) for r, v in D.items()}; res[k]["n"] = used
        print(k, used, {r: round(v, 3) for r, v in res[k].items() if r != "n"}, flush=True)
    json.dump(res, open(MF.OUT / "restore_results.json", "w"), indent=1)

    order = ["fake:Deepfakes", "fake:FaceSwap", "fake:Face2Face", "fake:NeuralTextures",
             "filter:eye_enlarging", "filter:face_reshaping_slim", "filter:smoothing", "filter:whitening", "filter:pilgram"]
    lab = {"fake:Deepfakes": "Deepfakes*", "fake:FaceSwap": "FaceSwap*", "fake:Face2Face": "Face2Face*",
           "fake:NeuralTextures": "NeuralTextures*", "filter:eye_enlarging": "eye enlarging", "filter:face_reshaping_slim": "face slimming",
           "filter:smoothing": "skin smoothing", "filter:whitening": "whitening", "filter:pilgram": "photometric"}
    cols = REGIONS + ["random", "full"]
    order = [o for o in order if o in res]
    A = np.array([[res[o][c] for c in cols] for o in order])
    fig, ax = plt.subplots(figsize=(3.45, 3.05))
    im = ax.imshow(A, cmap="Blues", vmin=0, vmax=1, aspect="auto")
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            ax.text(j, i, f"{A[i, j]:.2f}", ha="center", va="center", fontsize=6.0, color="white" if A[i, j] > 0.55 else MF.INK)
    ax.set_xticks(range(len(cols)), [c if c not in ("random", "full") else f"[{c}]" for c in cols], rotation=35, ha="right")
    ax.set_yticks(range(len(order)), [lab[o] for o in order])
    ax.axhline(3.5, color=MF.INK, lw=0.8); ax.axvline(len(REGIONS) - 0.5, color=MF.INK, lw=0.8)
    cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03); cb.ax.tick_params(labelsize=6.5)
    cb.set_label("drop in P(true class) when restored", fontsize=7)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    MF.save(fig, "fig_restore")


if __name__ == "__main__":
    main()
