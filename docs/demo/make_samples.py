"""Example images for the web demo, each with its known answer, plus the accuracy of the demo model on 50 more faces per
condition, so a visitor can judge single examples against the typical rate.

Faces: FFHQ (NVIDIA, CC BY-NC-SA 4.0) indices 17001-19999, never used in training. Examples = the first eight stems with a
detected face (sorted); the accuracy set = the next 50 stems per condition. Strength rule, fixed before any result: the
UPPER END of the range each operation was trained with (retouch_unified_20260929/ops.py random_op_v2), i.e. the most
visible edit that is still inside the training distribution:
  eye enlargement x1.25, face slimming 0.065, whitening 0.33, smoothing frac 0.08 with blend 0.4.
(A first version used stronger, out-of-range strengths from the older v1 generator, e.g. smoothing blend 1.0; the model
called that smoothed face fake. Kept in the record, not on the page.)
Forgeries: donor transplant of the nose / mouth from another FFHQ face (algorithm of partedit_20260927 donor_edit).
The demo model (Ours-lite, the same weights as docs/demo/models/ours_lite.onnx) is run in PyTorch with the page's crop.

python docs/demo/make_samples.py -> docs/demo/samples/*.jpg, samples.json, accuracy.json
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image

B = Path(r"C:\My_Project\AIGC"); OUT = Path(__file__).resolve().parent / "samples"; OUT.mkdir(exist_ok=True)
for p in (B / "results/research/retouch_unified_20260929", B / "docs/paper_v2", B):
    sys.path.insert(0, str(p))
from ops import op_eye, op_jaw, op_white, op_smooth  # noqa: E402
from occlusion_regions import LIPS, NOSE  # noqa: E402
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402
from train_ru3 import RUNet3  # noqa: E402

SIZE, S = 512, 380
PARTS = {"nose": NOSE, "mouth": LIPS}
CLS = ["real", "fake", "filter"]


def load(stem):
    a = np.array(Image.open(B / "ffhq_originals/Part2" / f"{stem}.png").convert("RGB").resize((SIZE, SIZE), Image.LANCZOS))
    lm = get_landmarks(a)
    return a, (None if lm is None else lm.astype(np.float32))


def part_mask(shape, lm, part, grow=0.08):
    fw = lm[:, 0].max() - lm[:, 0].min(); k = max(3, int(fw * grow)) | 1
    m = np.zeros(shape[:2], np.uint8); cv2.fillConvexPoly(m, cv2.convexHull(lm[PARTS[part]].astype(np.int32)), 1)
    return cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))).astype(bool)


def donor(img, lm, dimg, dlm, part):
    idx = PARTS[part]
    M, _ = cv2.estimateAffinePartial2D(dlm[idx], lm[idx], method=cv2.LMEDS)
    warped = cv2.warpAffine(dimg, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    m = part_mask(img.shape, lm, part)
    a, b = warped[m].astype(np.float32), img[m].astype(np.float32)
    warped = np.clip((warped.astype(np.float32) - a.mean(0)) * (b.std(0) / (a.std(0) + 1e-6)) + b.mean(0), 0, 255)
    fw = lm[:, 0].max() - lm[:, 0].min(); alpha = cv2.GaussianBlur(m.astype(np.float32), (0, 0), max(1.0, fw * 0.03))[..., None]
    return (alpha * warped + (1 - alpha) * img.astype(np.float32)).astype(np.uint8)


def conditions(a, lm, a2, lm2, rng):
    return {"real": (a, "real", "untouched photo"),
            "eyes": (op_eye(a, lm, rng, scale=1.25)[0], "filter", "eyes enlarged"),
            "slim": (op_jaw(a, lm, rng, shrink=0.065)[0], "filter", "face slimmed"),
            "white": (op_white(a, lm, rng, strength=0.33)[0], "filter", "skin whitened"),
            "smooth": (op_smooth(a, lm, rng, frac=0.08, mix=0.4)[0], "filter", "skin smoothed"),
            "nose": (donor(a, lm, a2, lm2, "nose"), "fake", "nose from another person"),
            "mouth": (donor(a, lm, a2, lm2, "mouth"), "fake", "mouth from another person")}


class Demo:
    """Ours-lite with the page's preprocessing: landmark box + 35 % per side, stretched to 380 x 380."""

    def __init__(self):
        self.net = RUNet3("effb4", head=True)
        self.net.load_state_dict(torch.load(B / "checkpoints/research/retouch_unified_20260929/ru_ru4e_effb4_s20260929.pth", map_location="cpu"))
        self.net = self.net.cuda().eval()

    @torch.no_grad()
    def __call__(self, img):
        lm = get_landmarks(img)
        if lm is None:
            return None
        h, w = img.shape[:2]; x0, y0 = lm.min(0); x1, y1 = lm.max(0); bw, bh = x1 - x0, y1 - y0
        bx0, by0 = max(0, int(np.floor(x0 - .35 * bw))), max(0, int(np.floor(y0 - .35 * bh)))
        bx1, by1 = min(w, int(np.floor(x1 + .35 * bw))), min(h, int(np.floor(y1 + .35 * bh)))
        c = cv2.resize(img[by0:by1, bx0:bx1], (S, S), interpolation=cv2.INTER_AREA)
        x = torch.from_numpy(((c.astype(np.float32) / 255 - .5) / .5).transpose(2, 0, 1))[None].cuda()
        return CLS[int(self.net(x)[0].argmax(1))]


def main():
    faces = []
    for p in sorted((B / "ffhq_originals/Part2").glob("*.png")):
        a, lm = load(p.stem)
        if lm is not None:
            faces.append((p.stem, a, lm))
        if len(faces) == 8 + 51:
            break
    rng = np.random.default_rng(0); demo = Demo()

    # the eight examples: conditions assigned to faces in a fixed order
    plan = [("real_1", 0, "real"), ("real_2", 1, "real"), ("filter_eyes", 2, "eyes"), ("filter_slim", 3, "slim"),
            ("filter_white", 4, "white"), ("filter_smooth", 5, "smooth"), ("fake_nose", 6, "nose"), ("fake_mouth", 7, "mouth")]
    meta = []
    for name, i, cond in plan:
        s, a, lm = faces[i]; s2, a2, lm2 = faces[7 if i == 6 else 6]
        img, truth, what = conditions(a, lm, a2, lm2, rng)[cond]
        Image.fromarray(img).save(OUT / f"{name}.jpg", quality=95)
        meta.append({"file": f"samples/{name}.jpg", "truth": truth, "what": what,
                     "ffhq": s + (f" + {cond} of {s2}" if truth == "fake" else ""), "python_pred": demo(img)})
    (OUT / "samples.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")

    # accuracy on the next 50 faces per condition (donor = the following face)
    pool = faces[8:]; acc = {}
    for k in range(50):
        s, a, lm = pool[k]; s2, a2, lm2 = pool[k + 1]
        for cond, (img, truth, what) in conditions(a, lm, a2, lm2, rng).items():
            pred = demo(img); r = acc.setdefault(cond, {"what": what, "truth": truth, "n": 0, "right": 0, "pred": {}})
            if pred is None:
                continue
            r["n"] += 1; r["right"] += pred == truth; r["pred"][pred] = r["pred"].get(pred, 0) + 1
    for r in acc.values():
        r["accuracy"] = round(100 * r["right"] / max(1, r["n"]), 1)
    (OUT / "accuracy.json").write_text(json.dumps(acc, indent=1), encoding="utf-8")
    for m in meta:
        print(f"{m['file']:26s} truth={m['truth']:6s} pred={m['python_pred']}")
    for c, r in acc.items():
        print(f"{c:7s} {r['accuracy']:5.1f}%  {r['pred']}")


if __name__ == "__main__":
    main()
