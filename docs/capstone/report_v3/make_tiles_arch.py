"""Image tiles for the system-overview figure (figs/fig_arch.tex), from one real record: the part-level forgery
part_forgery:donor:454__f0140__mouth (FF++ test frame 454, mouth replaced from a donor), the same record as the old
docs/capstone/src/make_pipeline_v2.py. Sources: docs/demo_ru/test/fixture_ev.json (the page's ONNX record and its
16x16 evidence map), MediaPipe landmarks (filters_v2.scale_normalized_filters.get_landmarks) and the part masks
(docs/paper_v2/occlusion_regions.region_masks). Writes figs/arch_*.png and figs/arch_numbers.tex (TikZ macros).
python make_tiles_arch.py"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

B = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent; OUT = HERE / "figs"
for p in (B, B / "docs/paper_v2", B / "docs/capstone/src"):
    sys.path.insert(0, str(p))
from occlusion_regions import region_masks  # noqa: E402
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402

ID = "part_forgery:donor:454__f0140__mouth"
ev = json.loads((B / "docs/demo_ru/test/fixture_ev.json").read_text(encoding="utf-8"))
R = next(r for r in ev["records"] if r["id"] == ID); rec = R["record"]
img = np.array(Image.open(B / "docs/demo_ru/test" / R["file"]).convert("RGB")); h, w = img.shape[:2]
print("image", R["file"], img.shape, "record keys", sorted(rec)[:20])
lm = np.asarray(get_landmarks(np.ascontiguousarray(img)), np.float32)[:, :2]
M = region_masks(img, lm)
e16 = np.asarray(R["evidence_map16"], np.float32)
parts = rec["evidence_mean_per_part"]; named = rec["named_parts"][0]; prob = rec["probabilities"]; ops = rec.get("operations", {})
print("prob", prob, "ops", ops, "parts", parts, "named", named)

S = 512  # tile side in px (printed at ~2.2 cm)


def save(name, arr):
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); hh, ww = arr.shape[:2]
    im.resize((round(S * ww / hh), S), Image.LANCZOS).save(OUT / f"arch_{name}.png", optimize=True)   # keep the aspect


# 1 photo with landmarks (one in three) and the crop box
x0, y0 = lm[:, 0].min(), lm[:, 1].min(); x1, y1 = lm[:, 0].max(), lm[:, 1].max(); mw, mh = (x1 - x0) * 0.35, (y1 - y0) * 0.35
bx0, by0, bx1, by1 = int(max(0, x0 - mw)), int(max(0, y0 - mh)), int(min(w, x1 + mw)), int(min(h, y1 + mh))
a = img.copy()
for (x, y) in lm[::3]:
    cv2.circle(a, (int(x), int(y)), 2, (255, 255, 255), -1, cv2.LINE_AA)
save("photo_plain", img)
save("photo", a)
b = img.copy()
for i in range(0, 2 * (bx1 - bx0 + by1 - by0), 14):  # dashed box
    pass
cv2.rectangle(b, (bx0, by0), (bx1, by1), (255, 209, 102), 4, cv2.LINE_AA)
for (x, y) in lm[::3]:
    cv2.circle(b, (int(x), int(y)), 2, (255, 255, 255), -1, cv2.LINE_AA)
save("photo_box", b)

# 2 the aligned crop (what the model sees)
save("crop", img)

# 3 the raw 16x16 evidence map
cmap = cv2.applyColorMap((np.clip(e16, 0, 1) * 255).astype(np.uint8), cv2.COLORMAP_MAGMA)[:, :, ::-1]
Image.fromarray(cmap).resize((S, S), Image.NEAREST).save(OUT / "arch_map16.png", optimize=True)

# 4 the evidence map on the face (bilinear upsampling, magma, opacity = value, white 0.5 contour)
e_up = np.clip(cv2.resize(e16, (w, h), interpolation=cv2.INTER_LINEAR), 0, 1)
heat = cv2.applyColorMap((e_up * 255).astype(np.uint8), cv2.COLORMAP_MAGMA)[:, :, ::-1].astype(np.float32)
alpha = (e_up * 0.85)[:, :, None]
c = img.astype(np.float32) * (1 - alpha) + heat * alpha
cs, _ = cv2.findContours((e_up >= 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
c = c.astype(np.uint8).copy(); cv2.drawContours(c, cs, -1, (255, 255, 255), 2, cv2.LINE_AA)
save("evidence", c)

# 5 the five part masks, the named part highlighted
COL = {"eyes": (86, 180, 233), "nose": (0, 158, 115), "mouth": (255, 209, 102), "skin": (204, 121, 167), "contour": (240, 228, 66)}
d = img.astype(np.float32)
for k in ("skin", "contour", "eyes", "nose", "mouth"):
    m = M[k].astype(bool)[:, :, None]; col = np.array(COL[k], np.float32)
    d = np.where(m, d * 0.55 + col * 0.45, d)
d = d.astype(np.uint8).copy()
for k in ("skin", "contour", "eyes", "nose", "mouth"):
    cs, _ = cv2.findContours(M[k].astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(d, cs, -1, COL[k] if k != named else (255, 255, 255), 5 if k == named else 2, cv2.LINE_AA)
save("parts", d)

# 6 the named part alone (yellow contour) on the plain crop
e = img.copy()
cs, _ = cv2.findContours(M[named].astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(e, cs, -1, (255, 209, 102), 6, cv2.LINE_AA)
save("named", e)

# numbers for TikZ
def f2(x):
    return f"{x:.2f}"
mac = [r"\newcommand{\pReal}{%s}" % f2(prob["real"]), r"\newcommand{\pFake}{%s}" % f2(prob["fake"]), r"\newcommand{\pBeau}{%s}" % f2(prob["filter"]),
       r"\newcommand{\evEyes}{%s}" % f2(parts["eyes"]), r"\newcommand{\evNose}{%s}" % f2(parts["nose"]), r"\newcommand{\evMouth}{%s}" % f2(parts["mouth"]),
       r"\newcommand{\evSkin}{%s}" % f2(parts["skin"]), r"\newcommand{\evContour}{%s}" % f2(parts["contour"]), r"\newcommand{\namedPart}{%s}" % named]
for k, mk in (("eye_enlargement", "opEye"), ("face_slimming", "opSlim"), ("skin_brightening", "opWhite"), ("skin_smoothing", "opSmooth")):
    mac.append(r"\newcommand{\%s}{%s}" % (mk, f2(ops.get(k, 0.0))))
(OUT / "arch_numbers.tex").write_text("\n".join(mac) + "\n", encoding="utf-8")
print("\n".join(mac)); print("tiles written")
