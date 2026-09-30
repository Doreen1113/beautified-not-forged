"""Landmarks (478 x 2) and FF++-style face boxes for the FFHQ originals (Part7 = training base, Part2 = Alibaba test base).
Incremental: existing entries are kept.  python prep_ffhq.py  -> ffhq_landmarks.npz, ffhq_boxes.json"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

BASE = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402
MARGIN = 0.35


def box(lm, w, h):
    (x0, y0), (x1, y1) = lm.min(0), lm.max(0); bw, bh = x1 - x0, y1 - y0
    return [max(0, int(x0 - bw * MARGIN)), max(0, int(y0 - bh * MARGIN)), min(w, int(x1 + bw * MARGIN)), min(h, int(y1 + bh * MARGIN))]


def main():
    lmf, bxf = HERE / "ffhq_landmarks.npz", HERE / "ffhq_boxes.json"
    L = dict(np.load(lmf)) if lmf.is_file() else {}; B = json.loads(bxf.read_text()) if bxf.is_file() else {}
    files = sorted((BASE / "ffhq_originals/Part7").glob("*.png")) + sorted((BASE / "ffhq_originals/Part2").glob("*.png"))
    n = 0
    for p in files:
        if p.stem in L:
            continue
        rgb = np.array(Image.open(p).convert("RGB")); lm = get_landmarks(rgb)
        if lm is None:
            continue
        L[p.stem] = np.asarray(lm, np.float32)[:, :2]; B[p.stem] = box(L[p.stem], rgb.shape[1], rgb.shape[0]); n += 1
        if n % 500 == 0:
            print(n, flush=True); np.savez(lmf, **L); bxf.write_text(json.dumps(B))
    np.savez(lmf, **L); bxf.write_text(json.dumps(B)); print("DONE", len(L), "new", n, flush=True)


if __name__ == "__main__":
    main()
