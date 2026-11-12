"""Fixture for the JS-mask check on the 50 verification images of demo_export/export_ru4e_onnx.py: for each image the
landmarks (Python MediaPipe on the fixed-set crop) mapped into the 224 grid, the ONNX 16x16 evidence map, and the
Python (cv2) part means / named part on that grid, so test_masks50.html can run face_masks.js on the same inputs and
report how many of the 50 named parts differ because of the JavaScript mask rasterisation alone.

python docs/demo_ru/test/make_fixture_masks50.py -> test/fixture_masks50.js
"""
import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
import torch.nn.functional as F
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "results/research/explain_vlm_20261012"; RU = ROOT / "results/research/retouch_unified_20260929"
for p in (RU, ROOT / "docs/paper_v2", ROOT):
    sys.path.insert(0, str(p))
from train_ru import crop  # noqa: E402
from train_ru3 import to_t2  # noqa: E402
from occlusion_regions import region_masks  # noqa: E402
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402

HERE = Path(__file__).resolve().parent; FACE = ["eyes", "nose", "mouth", "skin", "contour"]; G = 224


def rule_b(up, M):
    parts = {k: round(float(up[M[k]].mean()) if M[k].any() else 0.0, 3) for k in FACE}
    top = max(parts, key=parts.get); whole = all(parts[k] >= 0.5 for k in ("eyes", "nose", "mouth"))
    return parts, (["whole face"] if whole else [top])


def main():
    sess = ort.InferenceSession(str(ROOT / "docs/demo_ru/models/ru7we_effb4.onnx"), providers=["CPUExecutionProvider"])
    jl = {json.loads(l)["id"]: json.loads(l) for l in (EXP / "evidence.jsonl").open(encoding="utf-8")}
    ver = [json.loads(l) for l in (EXP / "demo_export/verify_50.jsonl").open(encoding="utf-8")]
    out = []
    for v in ver:
        r = jl[v["id"]]; arr = crop(np.array(Image.open(r["image"]).convert("RGB")), r["box"]); h, w = arr.shape[:2]
        _, e = sess.run(None, {"input": to_t2(arr, 380, False, "half")[None].numpy()}); e16 = e[0].reshape(16, 16)
        lm = get_landmarks(np.ascontiguousarray(arr)); lmg = np.stack([lm[:, 0] * G / w, lm[:, 1] * G / h], 1).astype(np.float32)
        M = region_masks(np.zeros((G, G, 3), np.uint8), lmg)
        up = F.interpolate(torch.from_numpy(e16)[None, None], size=(G, G), mode="bilinear", align_corners=False)[0, 0].numpy()
        parts, named = rule_b(up, M)
        Mn = region_masks(arr, lm); upn = F.interpolate(torch.from_numpy(e16)[None, None], size=(h, w), mode="bilinear", align_corners=False)[0, 0].numpy()
        parts_n, named_n = rule_b(upn, Mn)
        out.append({"id": r["id"], "landmarks_grid": [[round(float(a), 3), round(float(b), 3)] for a, b in lmg], "evidence_map16": [[float(x) for x in row] for row in e16],
                    "cv2_grid224": {"parts3": parts, "named_parts": named}, "cv2_native": {"parts3": parts_n, "named_parts": named_n, "shape": [h, w]},
                    "mask_area_cv2": {k: int(M[k].sum()) for k in FACE}})
    txt = json.dumps({"n": len(out), "grid": G, "records": out})
    (HERE / "fixture_masks50.js").write_text("window.MASK_FIXTURE = " + txt + ";\n", encoding="utf-8")
    nd = sum(o["cv2_grid224"]["named_parts"] != o["cv2_native"]["named_parts"] for o in out)
    print(f"records {len(out)}; cv2 at 224 grid vs cv2 at native crop resolution: named part differs on {nd}/{len(out)}")


if __name__ == "__main__":
    main()
