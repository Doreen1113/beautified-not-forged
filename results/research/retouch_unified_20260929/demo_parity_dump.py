"""Inputs for testing docs/demo/explain.js against the Python explanation. Crops are made the way the web demo makes them
(MediaPipe landmarks on the full image, bounding box + 35 % per side, stretched to 380 x 380), the ONNX model of the demo
is run, and the Python rule-B part names are computed with occlusion_regions.region_masks on the same crop.
Samples fixed in advance: 90 held-out part forgeries (donor / SD / SDXL, eyes / nose / mouth balanced), 40 FF++ test frames.

python demo_parity_dump.py -> demo_parity_inputs.json (consumed by docs/demo/test_explain.mjs)
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort
from PIL import Image

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC")
sys.path.insert(0, str(B / "docs/paper_v2")); sys.path.insert(0, str(B))
from occlusion_regions import region_masks  # noqa: E402
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402

S = 380; PARTS = ["eyes", "nose", "mouth", "skin", "contour"]
sig = lambda z: 1 / (1 + np.exp(-z))  # noqa: E731


def samples():
    parts = [(p, p.stem.split("__")[-1]) for m in ("donor", "sd", "sdxl") for p in sorted((B / "ffpp_partedit/test" / m).glob("*.jpg"))[::131][:30]]
    rows = [l.split("\t") for l in (B / "results/research/ffpp_unified_20260925/ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:]]
    ff = [(Path(r[0]), r[3]) for r in rows][::211][:40]
    return parts + ff


def main():
    sess = ort.InferenceSession(str(B / "docs/demo/models/ours_lite.onnx"), providers=["CPUExecutionProvider"])
    out = []
    for path, truth in samples():
        img = np.array(Image.open(path).convert("RGB")); lm = get_landmarks(img)
        if lm is None:
            continue
        h, w = img.shape[:2]; x0, y0 = lm.min(0); x1, y1 = lm.max(0); bw, bh = x1 - x0, y1 - y0
        bx0, by0 = max(0, int(np.floor(x0 - .35 * bw))), max(0, int(np.floor(y0 - .35 * bh)))
        bx1, by1 = min(w, int(np.floor(x1 + .35 * bw))), min(h, int(np.floor(y1 + .35 * bh)))
        crop = cv2.resize(img[by0:by1, bx0:bx1], (S, S), interpolation=cv2.INTER_AREA)
        lmc = np.stack([(lm[:, 0] - bx0) * S / (bx1 - bx0), (lm[:, 1] - by0) * S / (by1 - by0)], 1)
        x = ((crop.astype(np.float32) / 255 - 0.5) / 0.5).transpose(2, 0, 1)[None]
        lo, pr, ev = sess.run(None, {"input": x})
        up = cv2.resize(sig(ev[0, 0]), (S, S), interpolation=cv2.INTER_LINEAR)
        M = region_masks(crop, lmc.astype(np.float32))
        py = {k: float(up[M[k]].mean()) if M[k].any() else 0.0 for k in PARTS}
        out.append({"path": str(path), "truth": truth, "logits": lo[0].tolist(), "presence": pr[0].tolist(),
                    "ev": ev[0, 0].ravel().tolist(), "h": int(ev.shape[2]), "w": int(ev.shape[3]), "lm": lmc.round(3).tolist(),
                    "py_parts": py, "py_top": max(py, key=py.get)})
    (HERE / "demo_parity_inputs.json").write_text(json.dumps(out)); print(len(out), "items")


if __name__ == "__main__":
    main()
