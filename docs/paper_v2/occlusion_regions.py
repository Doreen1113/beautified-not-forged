"""Region-occlusion explainability for the three-way detector (causal, not gradient-based).

For correctly classified FF++ test images of every forgery method and every filter type, each facial region is occluded
in turn (feathered fill with the image's mean colour) and the drop in the probability of the true class is recorded.
Regions come from MediaPipe FaceMesh landmarks: eyes+brows, nose, mouth, skin (face hull minus the others),
contour band (along the face oval), background (outside the dilated face hull).

python docs/paper_v2/occlusion_regions.py [n_per_group] -> figs/fig_occl.pdf|png, figs/occlusion_results.json
"""
import json
import sys
from pathlib import Path

import cv2
import matplotlib
import numpy as np
import timm
import torch
from PIL import Image
from torchvision import transforms

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BASE = Path(r"C:\My_Project\AIGC")
sys.path.insert(0, str(BASE)); sys.path.insert(0, str(BASE / "docs/paper_v2"))
import make_figures as MF  # noqa: E402
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402
from sbi.sbi_generator import FACE_OVAL  # noqa: E402

CK = BASE / "checkpoints/research/sbiscale_20260926/sbiscale_HYB_s20260927.pth"
T = transforms.Compose([transforms.Resize((380, 380)), transforms.ToTensor(), transforms.Normalize([0.5] * 3, [0.5] * 3)])
R_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246, 46, 53, 52, 65, 55, 70, 63, 105, 66, 107]
L_EYE = [263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466, 276, 283, 282, 295, 285, 300, 293, 334, 296, 336]
LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185]
NOSE = [168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 98, 97, 326, 327, 294, 278, 344, 440, 275, 45, 220, 115, 48, 64]
REGIONS = ["eyes", "nose", "mouth", "skin", "contour", "background"]


def hull(shape, pts, dil=0):
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillConvexPoly(m, cv2.convexHull(pts.astype(np.int32)), 1)
    if dil:
        m = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dil, dil)))
    return m.astype(bool)


def region_masks(img, lm):
    h, w = img.shape[:2]
    fw = lm[:, 0].max() - lm[:, 0].min(); k = max(3, int(fw * 0.06)) | 1
    face = hull(img.shape, lm[FACE_OVAL])
    eyes = hull(img.shape, lm[R_EYE], k) | hull(img.shape, lm[L_EYE], k)
    nose = hull(img.shape, lm[NOSE], k); mouth = hull(img.shape, lm[LIPS], k)
    band = int(fw * 0.10) | 1
    inner = cv2.erode(face.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (band, band))).astype(bool)
    outer = cv2.dilate(face.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (band, band))).astype(bool)
    contour = outer & ~inner
    skin = inner & ~eyes & ~nose & ~mouth
    bg = ~outer
    return {"eyes": eyes, "nose": nose, "mouth": mouth, "skin": skin, "contour": contour, "background": bg}


def occlude(img, m):
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 3)[..., None]
    fill = np.full_like(img, img.reshape(-1, 3).mean(0).astype(np.uint8))
    return (img * (1 - a) + fill * a).astype(np.uint8)


@torch.no_grad()
def probs(m, ims):
    x = torch.stack([T(Image.fromarray(i)) for i in ims]).cuda()
    with torch.autocast("cuda", dtype=torch.bfloat16):
        return torch.softmax(m(x).float(), 1).cpu().numpy()


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
    res, area = {}, {}
    for (y, key), lst in sorted(groups.items()):
        drops = {r: [] for r in REGIONS}; ar = {r: [] for r in REGIONS}; used = 0
        for p in rng.permutation(lst):
            img = np.array(Image.open(p).convert("RGB"))
            p0 = probs(m, [img])[0]
            if p0.argmax() != y:
                continue
            lm = get_landmarks(np.ascontiguousarray(img))
            if lm is None:
                continue
            lm = np.asarray(lm, np.float32)[:, :2]
            M = region_masks(img, lm)
            po = probs(m, [occlude(img, M[r]) for r in REGIONS])
            for j, r in enumerate(REGIONS):
                drops[r].append(float(p0[y] - po[j, y])); ar[r].append(float(M[r].mean()))
            used += 1
            if used == n:
                break
        res[f"{['real', 'fake', 'filter'][y]}:{key}"] = {r: float(np.mean(drops[r])) for r in REGIONS}
        area[f"{['real', 'fake', 'filter'][y]}:{key}"] = {r: float(np.mean(ar[r])) for r in REGIONS}
        res[f"{['real', 'fake', 'filter'][y]}:{key}"]["n"] = used
        print(key, used, {r: round(res[f"{['real', 'fake', 'filter'][y]}:{key}"][r], 3) for r in REGIONS}, flush=True)
    json.dump({"drop_true_class_prob": res, "region_area_fraction": area}, open(MF.OUT / "occlusion_results.json", "w"), indent=1)

    order = ["fake:Deepfakes", "fake:FaceSwap", "fake:Face2Face", "fake:NeuralTextures",
             "filter:eye_enlarging", "filter:face_reshaping_slim", "filter:smoothing", "filter:whitening", "filter:pilgram"]
    lab = {"fake:Deepfakes": "Deepfakes", "fake:FaceSwap": "FaceSwap", "fake:Face2Face": "Face2Face",
           "fake:NeuralTextures": "NeuralTextures", "filter:eye_enlarging": "eye enlarging", "filter:face_reshaping_slim": "face slimming",
           "filter:smoothing": "skin smoothing", "filter:whitening": "whitening", "filter:pilgram": "photometric (14)"}
    order = [o for o in order if o in res]
    A = np.array([[res[o][r] for r in REGIONS] for o in order])
    fig, ax = plt.subplots(figsize=(3.45, 3.0))
    vmax = max(0.05, np.abs(A).max())
    im = ax.imshow(A, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            ax.text(j, i, f"{A[i, j]:.2f}", ha="center", va="center", fontsize=6.3,
                    color="white" if abs(A[i, j]) > 0.55 * vmax else MF.INK)
    ax.set_xticks(range(len(REGIONS)), REGIONS, rotation=35, ha="right")
    ax.set_yticks(range(len(order)), [lab[o] for o in order])
    ax.axhline(3.5, color=MF.INK, lw=0.8)
    cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03); cb.ax.tick_params(labelsize=6.5)
    cb.set_label("drop in P(true class) when occluded", fontsize=7)
    for s in ax.spines.values():
        s.set_visible(False)
    fig.tight_layout()
    MF.save(fig, "fig_occl")


if __name__ == "__main__":
    main()
