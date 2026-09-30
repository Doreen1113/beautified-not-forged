# Beautified or forged? (browser demo)

Runs **Ours-lite** (EfficientNet-B4, 17.6 M parameters, three heads) entirely in the browser: MediaPipe FaceLandmarker
(478 landmarks) crops the face (bounding box + 35 % per side, 380 × 380), ONNX Runtime Web runs the model, and
`explain.js` turns its outputs into the label, the retouching operations, the evidence map, the evidence per facial part
and a template sentence. Nothing is uploaded.

## Run
```
cd docs/demo
python -m http.server 8000
```
Open http://localhost:8000 (or http://<this machine's IP>:8000 on a phone in the same network).

## Files
- `models/ours_lite.onnx` exported by `results/research/retouch_unified_20260929/export_demo_onnx.py`; ONNX vs PyTorch on
  60 FF++ test frames: max |difference| 2.2e-5, 60/60 identical decisions.
- `explain.js` part naming (mean evidence per landmark part, rule B) and sentence template, as pure functions.
- `test_explain.mjs` checks `explain.js` against the Python implementation on the crops written by
  `results/research/retouch_unified_20260929/demo_parity_dump.py`: 128/128 identical part names (max difference of a
  part mean 0.014), and the edited part named correctly in 81/81 detected held-out part forgeries.

## Examples and video
- `samples/` eight FFHQ faces (never used in training) with their known answer, and `accuracy.json`, the accuracy of this
  model on 50 more faces per condition; made by `make_samples.py` (strengths = upper end of the training ranges, fixed
  before any result). Ours-lite gets 4 of the 8 examples right; per condition 38-96 %.
- `video/demo_walkthrough.mp4` a 54 s recording of the page (headless Chromium, Playwright): examples, two uploaded
  FF++ images, the evidence-map toggle, the accuracy table.

## Earlier demos
`../demo_v8_legacy/` (v8.x hierarchical ShuffleNetV2 production line) and `../demo_ru/` (RU1 RepViT, 4.7 M).
