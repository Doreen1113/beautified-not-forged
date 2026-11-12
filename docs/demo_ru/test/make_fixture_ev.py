"""Build the evidence-page fixture: 20 images of the fixed explanation set (4 per group) copied to test/img/ and, for each,
the Python reference of the browser path, so test_evidence_page.html can compare decision, named parts and the four
T2 sentences produced in the browser with the Python pipeline.

Reference per image (ru4e_effb4 ONNX, the same file the page loads):
  landmarks  MediaPipe FaceLandmarker (Python, filters_v2.scale_normalized_filters.get_landmarks) on the fixture image
  crop       landmark bounding box + 35 % per side, floor/clip as DemoCore.cropBox
  input      PIL bilinear resize to 380, (x/255-0.5)/0.5 (train_ru3.to_t2)       -> onnxruntime -> decision, ops, evidence
  masks      docs/paper_v2/occlusion_regions.region_masks on the 224 x 224 grid with the landmarks mapped into the crop
             (what the page does); also the project's own convention (landmarks detected again on the native crop,
             explain_ours.explain) as `python_native`, to report how often the two conventions name different parts
  sentences  results/research/explain_vlm_20261012/explain_v2.t2_sentences on the record (imported, not re-implemented)
The clipe5 record of evidence.jsonl is attached as `jsonl` for the cross-model comparison.

python docs/demo_ru/test/make_fixture_ev.py -> test/img/*.png, test/fixture_ev.json, test/fixture_ev.js
python docs/demo_ru/test/make_fixture_ev.py --model repvit_ev -> test/fixture_ev_repvit_ev.json/.js: the same 20 images (ids and
  files read from fixture_ev.json, images not rewritten) through models/ru4e_repvit.onnx at 224 px, everything else identical
"""
import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort
import torch
import torch.nn.functional as F
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "results/research/explain_vlm_20261012"; RU = ROOT / "results/research/retouch_unified_20260929"
for p in (EXP, RU, ROOT / "docs/paper_v2", ROOT):
    sys.path.insert(0, str(p))
import explain_v2  # noqa: E402
from train_ru import crop  # noqa: E402
from train_ru3 import to_t2  # noqa: E402
from occlusion_regions import region_masks  # noqa: E402
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402

HERE = Path(__file__).resolve().parent; IMG = HERE / "img"
MODELS = {"effb4": ("ru7we_effb4.onnx", 380), "repvit_ev": ("ru4e_repvit.onnx", 224)}   # keys = DemoCore.MODELS keys
CLS = ["real", "fake", "filter"]; FACE = ["eyes", "nose", "mouth", "skin", "contour"]; GRID = 224
OPN = ["eye_enlargement", "face_slimming", "skin_brightening", "skin_smoothing"]
PER_GROUP = 4


def crop_box(lm, w, h):
    x0, y0 = lm[:, 0].min(), lm[:, 1].min(); x1, y1 = lm[:, 0].max(), lm[:, 1].max(); bw, bh, m = x1 - x0, y1 - y0, 0.35
    return [max(0, int(np.floor(x0 - bw * m))), max(0, int(np.floor(y0 - bh * m))), min(w, int(np.floor(x1 + bw * m))), min(h, int(np.floor(y1 + bh * m)))]


def upsample(grid, shape):
    return F.interpolate(torch.from_numpy(np.asarray(grid, np.float32))[None, None], size=shape, mode="bilinear", align_corners=False)[0, 0].numpy()


def rule_b(up, M):
    parts = {k: round(float(up[M[k]].mean()) if M[k].any() else 0.0, 3) for k in FACE}
    top = max(parts, key=parts.get); whole = all(parts[k] >= 0.5 for k in ("eyes", "nose", "mouth"))
    return parts, (["whole face"] if whole else [top]), whole


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", default="effb4", choices=list(MODELS)); key = ap.parse_args().model
    fn_onnx, SIZE = MODELS[key]; ONNX = ROOT / "docs/demo_ru/models" / fn_onnx; suf = "" if key == "effb4" else f"_{key}"
    sess = ort.InferenceSession(str(ONNX), providers=["CPUExecutionProvider"])
    ver = [json.loads(l) for l in (EXP / "demo_export/verify_50.jsonl").open(encoding="utf-8")]
    jl = {json.loads(l)["id"]: json.loads(l) for l in (EXP / "evidence.jsonl").open(encoding="utf-8")}
    chosen, cnt = [], {}
    for v in list(ver) + list(jl.values()):   # verify_50 first; groups short of 4 there are topped up from evidence.jsonl in file order
        if cnt.get(v["group"], 0) < PER_GROUP and jl[v["id"]] not in chosen:
            chosen.append(jl[v["id"]]); cnt[v["group"]] = cnt.get(v["group"], 0) + 1
    if key != "effb4":   # exactly the images of the effb4 fixture, in its order
        chosen = [jl[r["id"]] for r in json.loads((HERE / "fixture_ev.json").read_text(encoding="utf-8"))["records"]]
    IMG.mkdir(exist_ok=True); out = []
    for r in chosen:
        arr = crop(np.array(Image.open(r["image"]).convert("RGB")), r["box"])   # the fixed-set crop = the fixture image
        fn = r["id"].replace(":", "__").replace("/", "_") + ".png"
        if key == "effb4":
            Image.fromarray(arr).save(IMG / fn)
        else:
            assert np.array_equal(np.array(Image.open(IMG / fn).convert("RGB")), arr), fn
        lm = get_landmarks(np.ascontiguousarray(arr)); h, w = arr.shape[:2]
        box = crop_box(lm, w, h); x0, y0, x1, y1 = box; c = arr[y0:y1, x0:x1]
        x = to_t2(np.ascontiguousarray(c), SIZE, False, "half")[None].numpy()
        o, e = sess.run(None, {"input": x}); o = o[0]; e16 = e[0].reshape(16, 16)
        p = np.exp(o[:3] - o[:3].max()); p /= p.sum(); ops = 1 / (1 + np.exp(-o[3:7])); dec = CLS[int(p.argmax())]
        # page convention: the full-image landmarks mapped into the 224 grid of the crop
        lmg = np.stack([(lm[:, 0] - x0) * GRID / (x1 - x0), (lm[:, 1] - y0) * GRID / (y1 - y0)], 1).astype(np.float32)
        M = region_masks(np.zeros((GRID, GRID, 3), np.uint8), lmg); parts3, named, whole = rule_b(upsample(e16, (GRID, GRID)), M)
        # project convention: landmarks detected again on the native crop, masks at native resolution (explain_ours)
        lm2 = get_landmarks(np.ascontiguousarray(c)); native = None
        if lm2 is not None:
            M2 = region_masks(c, np.asarray(lm2, np.float32)[:, :2]); p3n, nn, _ = rule_b(upsample(e16, c.shape[:2]), M2); native = {"parts3": p3n, "named_parts": nn}
        rec = {"decision": dec, "probabilities": {k: round(float(v), 2) for k, v in zip(CLS, p)},
               "operations": {k: round(float(v), 2) for k, v in zip(OPN, ops)}, "operation_threshold": 0.5,
               "evidence_mean_per_part": {k: round(v, 2) for k, v in parts3.items()}, "named_parts": named, "whole_face": whole,
               "calibration_note": "scores are raw model outputs, not calibrated probabilities"}
        s = explain_v2.t2_sentences(rec)
        out.append({"id": r["id"], "group": r["group"], "truth": r["truth"], "file": "img/" + fn, "image_wh": [w, h], "box": box,
                    "record": rec, "t2_sentences": list(s), "t2_text": explain_v2.compose(rec), "p_raw": [float(v) for v in p], "ops_raw": [float(v) for v in ops],
                    "parts3": parts3, "evidence_map16": [[round(float(v), 4) for v in row] for row in e16], "landmarks_grid": [[round(float(a), 2), round(float(b), 2)] for a, b in lmg],
                    "python_native": native,
                    "jsonl": {"model": r["model"], "decision": r["decision"], "named_parts": r["named_parts"], "t2_sentences": list(explain_v2.t2_sentences(r))}})
        print(f"{r['id']:45s} {dec:6s} {named} native={native['named_parts'] if native else None} jsonl={r['decision']}/{r['named_parts']}")
    fx = {"source": "results/research/explain_vlm_20261012/fixed_set.txt (4 per group of demo_export/verify_50.jsonl)", "model": f"models/{fn_onnx}", "model_key": key,
          "n": len(out), "grid": GRID, "size": SIZE, "records": out}
    txt = json.dumps(fx, ensure_ascii=False, indent=1)
    (HERE / f"fixture_ev{suf}.json").write_text(txt, encoding="utf-8"); (HERE / f"fixture_ev{suf}.js").write_text("window.EV_FIXTURE = " + txt + ";\n", encoding="utf-8")
    nd = sum(1 for o in out if o["python_native"] and o["python_native"]["named_parts"] != o["record"]["named_parts"])
    print(f"records {len(out)}; mapped-landmark vs re-detected-on-crop named part differs on {nd}/{len(out)}")


if __name__ == "__main__":
    main()
