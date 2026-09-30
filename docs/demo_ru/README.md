# Retouch or forgery? — browser demo (RU RepViT)

Runs the vendor-supervised three-way model (real / fake / filter + four retouching-operation probabilities) entirely in
the browser: MediaPipe FaceLandmarker (478 landmarks) crops the face exactly as in training (landmark bounding box + 35 %
per side), then ONNX Runtime Web runs the 4.7 M-parameter RepViT model on WebAssembly.

## Run
```
cd docs/demo_ru
python -m http.server 8000
```
Open http://localhost:8000 on a computer, or http://<this machine's IP>:8000 on a phone in the same network, and choose a
face photo. Nothing is uploaded; the MediaPipe face model is fetched from Google's public model bucket on first load.

## Model
`models/ru_repvit.onnx` — exported by `results/research/retouch_unified_20260929/export_ru_tflite.py` (same export also
produces the TFLite files in `results/mobile_export/ru_<arm>_repvit/`; all four deployment gates pass, 200/200 decision
agreement with PyTorch, 9.7 ms per image single-thread desktop CPU for RU1). Output vector: 3 class logits, 4 operation
logits (eye enlargement, face slimming, whitening, smoothing), 4 quantity estimates (not shown: they failed validation).

## Honest limits (shown on the page)
On an unseen commercial retouching service the model family calls 0.3 % of retouched faces fake and reaches 71–73 %
balanced accuracy on retouched vs untouched; smoothing is recognised reliably, single eye enlargement / slimming /
whitening often are not, and some untouched photos are called filter. Probabilities are not calibrated.
