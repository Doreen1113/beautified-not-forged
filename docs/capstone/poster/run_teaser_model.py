"""Run the main model (CLIP ViT-L/14 + LoRA + heads, clipe5 seed 20260929) on the poster's teaser images, so the poster shows
the model's own output on those images, not a population number. Same preprocessing as the report's make_tiles_method.py
(FFHQ: the ffhq_boxes crop at 224; Celeb-DF-B: the standardised frame crop at 224).
Writes assets/teaser_model.json.  python docs/capstone/poster/run_teaser_model.py"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

B = Path(r"C:\My_Project\AIGC"); H = Path(__file__).resolve().parent
RU = B / "results/research/retouch_unified_20260929"
sys.path.insert(0, str(B / "docs/capstone/report_v3")); sys.path.insert(0, str(B / "docs/paper_v2")); sys.path.insert(0, str(RU))
import make_tiles_method as MT  # noqa: E402

tag, run = MT.main_model()
box = json.loads((RU / "ffhq_boxes.json").read_text())["17003"]
ffhq = lambda p: np.ascontiguousarray(cv2.imread(str(p))[..., ::-1][box[1]:box[3], box[0]:box[2]])
F = B / "external_data/celebdfb/frames_std32v3"
items = {"genuine": ffhq(B / "ffhq_originals/Part2/17003.png"),
         "genuine_smoothed": ffhq(B / "FFHQ_ali_process/Smoothing_90/17000/17003.png"),
         "swap": np.ascontiguousarray(cv2.imread(str(F / "synthesis/id17_id35_0000__f05.jpg"))[..., ::-1]),
         "swap_beautified": np.ascontiguousarray(cv2.imread(str(F / "synthesis_beautified/id17_id35_0000__f05.jpg"))[..., ::-1])}
out = {"model": tag, "classes": ["real", "forged", "beautified"]}
for k, rgb in items.items():
    p, pr, ev = run(rgb, 224)
    out[k] = {"p": [round(float(v), 3) for v in p], "label": ["real", "forged", "beautified"][int(np.argmax(p))],
              "ops_eye_contour_tone_texture": [round(float(v), 3) for v in pr]}
    print(k, out[k])
(H / "assets/teaser_model.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
