# Retouch or forgery? — browser demo (RU EfficientNet-B4 + evidence head)

**What this page is.** The product of the project: a visitor chooses or takes a face photograph and the page answers
real / fake / filter (beauty retouching), outlines the evidence on the face and names the part, shows sentences that code
composed and checked, and, for a filter verdict, the four operation scores. Everything runs in the browser (MediaPipe
FaceLandmarker, 478 landmarks, crops the face exactly as in training; ONNX Runtime Web runs the model on WebAssembly);
nothing is uploaded. `cases.html` holds examples with known answers and the accuracy on 50 faces per condition, for the
exhibition. Open it on a phone in the same network (see "Run") or host the folder as static files.

**Models on the page (two since 2026-10-31):**

- **EfficientNet-B4 + evidence head (default)** — `models/ru7we_effb4.onnx` (W, `ru_ru7we_effb4_s20260929`, 17.6 M
  parameters, 380 px input, 67 MB); the model since 2026-10-30, see the last section. Its evidence head lets the page name
  the face part and draw the evidence contour.
- **RepViT evidence model (small, about 19 MB)** — `models/ru4e_repvit.onnx` (4.7 M, 224 px), for older phones; weaker
  (the page's validation text gives its numbers).
- Removed from the menu on 2026-10-31: the RepViT model without an evidence head (`models/ru_repvit.onnx`, file and
  `DemoCore.MODELS.repvit` kept for the tests); it could not mark a face part, which the page promises.
- Not on the page: the paper's main model (CLIP ViT-L/14 + LoRA, too large for a browser) and the previous browser model
  `models/ru4e_effb4.onnx` (kept for rollback). The v8 ShuffleNet pipeline at the repository root (`pipeline.py`) is a
  legacy line and is not part of this demo. Sections below that name `ru4e_effb4.onnx` as the default describe the page
  before 2026-10-30.

## Page design (2026-10-15 redesign)
Presentation only; the analysis path (`demo_core.js`, `explain_t2.js`, `face_masks.js`, `evidence_overlay.js`, `nl_client.js`)
is unchanged except two additive hooks: `DemoCore.loadModel(key, baseUrl, bytes)` accepts the already downloaded model
bytes (the page fetches the 67 MB file itself to show download progress), and `NLClient.FIXED_QA` / `isFixed` /
`fixedAnswer` answer the four fixed questions offline. UI text was Traditional Chinese at the time (English default since 2026-10-15, see "English UI" below); flow: 選擇照片／拍照 → four
bundled examples (`examples/ex1–4.png`, copies of `test/img/` files: FF++ real 220, part forgery 454 mouth, Alibaba
Smoothing_90 17001 (since 2026-10-28; EyeEnlarging_90 17001 before, kept in examples/backup_ex3_eye90/, because smoothing is the only supported operation name), Deepfakes 154_386; ground truth revealed after analysis) → result card (是否偽造 chip + raw fake
score, 美顏 wording, decision label row, crop with contour and named part, T2 or LLM text with a source badge, operation
bars for filter, 8 question chips). 美顏 wording: 未偵測到 unless filter is the argmax; 可能有修圖 when it is; 明顯修圖 when
it is and P(filter) >= 0.80 (presentation threshold, shown on the page). T2 sentences are displayed with the class names
and「evidence 平均」in Chinese (display mapping only; `explain_t2.js` output unchanged). Settings (model, server mode,
URL, style) and 「關於這個系統」 are collapsed. Validation numbers on the page are those of `ru4e_effb4`
(`results/research/retouch_unified_20260929/RESULTS_ru4e_effb4_s20260929.md`: Alibaba to-fake 0.33 %, balanced 72.61 %,
originals to filter 18.6 %). Screenshots: `python test/take_screens.py` (CDP, writes `test/screens/`, fails on horizontal
overflow).

Server routing v3 (`PRE_DECLARED_NL.md` §14): 「這個分數代表什麼？」 is now a fixed answer too (it failed the LLM path
94.7 % on the holdout); four fixed, four to the LLM. `run_test_server_headless.py` also checks that the page's
`FIXED_QA` equals `nl_core.FIXED_QA` and that exactly those questions come back as `fixed`.

## English UI (2026-10-15)
The page is English by default with a 中文 toggle (header button, also a Language radio in Settings; `?lang=zh|en` in the
URL; the choice is kept in `localStorage` when available). All strings live in one dictionary `I18N = {en, zh}` in
`index.html` (no framework); the Chinese strings are the previous ones, unchanged. Switching language re-renders the
status line, the result card, chips and any open answer; the analysis itself is not re-run.

- Explanation (T2): `ExplainT2.t2Sentences(rec, "en")` / `compose(rec, obs, "en")` give the English four sentences
  (`The model's decision is fake (score 0.97).` / `The evidence is concentrated on the nose (mean evidence 0.81).` /
  `Operations at or above the threshold of 0.5: skin smoothing (0.91).` or `None of the four operations reaches the
  threshold of 0.5.` / `The score is the model's raw output, not a calibrated probability.`). Default stays Chinese, so
  every older caller is unchanged. Python twin: `results/research/explain_vlm_20261012/nl_v5/explain_v2_en.py`.
- Server mode: `NLClient.explain/qa(url, record, …, lang)` send the page locale; `nl_server.py` takes `lang` ("en"
  default, "zh"). English uses prompt `p2en1` (translation of the frozen p2 + one dev-set revision, `PRE_DECLARED_NL.md`
  §15) and the English gate `validate_text_en.py` (H1–H6 + G7 + facts); the four fixed questions are answered offline by
  `NLClient.FIXED_QA_EN` (equal to `nl_core_en.FIXED_QA_EN`, checked by the server test).
  2026-10-15 (`PRE_DECLARED_NL.md` §17): the server's default is design p3 (prompts `p3en1` / `p3r1`, `nl_p3.py`): the
  LLM writes the words only, with no numbers and nothing about certainty or calibration; code adds the decision score
  (expert style: also mean evidence and operation scores) in labelled parentheticals and the fixed calibration sentence.
  The reply carries `prompt`, `llm_text` and `code_added`; the badge then reads "LLM wording, numbers and score note by
  code; passed the checks" (`NLClient.badgeKey`). The old flow stays selectable with `prompt: "p2"`. Gate: gate v3 on the
  shown text plus, on the LLM's own text, G10 (no number at all).
  2026-10-15 (`PRE_DECLARED_NL.md` §17.8): Chinese default prompt `p3r1z` = `p3r1` with the Chinese class labels
  (偽造／真實／美顏修圖) in the fact list and question plan instead of the English keys, which the model had copied
  (「模型的判定是 fake」); the expert parenthetical writes 證據平均 and the p3 code fallbacks show Chinese labels too. The
  server test now fails any Chinese text that shows fake / real / filter or "evidence".
- Tests: `python test/make_fixture_en.py && python test/run_test_headless.py --lang en` (JS vs Python, English: the 50
  fixture records + 4 synthetic branch cases); `run_test_headless.py` (Chinese) unchanged;
  `run_test_server_headless.py [--lang en|zh|both]` (default both; English texts re-checked with `validate_text_en`,
  result `test/server_headless_result_en.json`); `take_screens.py` now shoots English at 412 and 1366 px plus one Chinese
  shot (`412_example3_zh`).

## Run
```
cd docs/demo_ru
python -m http.server 8000
```
Open http://localhost:8000 on a computer, or http://<this machine's IP>:8000 on a phone in the same network, and choose a
face photo. Nothing is uploaded; the MediaPipe face model is fetched from Google's public model bucket on first load.

Phone latency (2026-11-01): open `bench.html` on the phone (same address, `/bench.html`), choose the model, press the
button. It runs the page's chain (MediaPipe → crop → ONNX on one WebAssembly thread → part matching) on the four
examples, one warm-up pass and ten timed passes each (40 timed photos), and shows median and P90 per step plus a JSON
block (device, model load time, raw times) to copy back. Desktop baseline in headless Chrome:
`python test/run_bench_headless.py effb4` → `test/bench_desktop_effb4.json` (2026-11-01: end-to-end median 512 ms, P90
544 ms; model 422 ms; warm-up labels real/fake/filter/fake = the examples' truths).

## Models
`models/ru4e_effb4.onnx` (66.97 MB, opset 17, sha256 `477f69a7…`) — exported by
`results/research/explain_vlm_20261012/demo_export/export_ru4e_onnx.py` from `checkpoints/research/retouch_unified_20260929/ru_ru4e_effb4_s20260929.pth`
(`train_ru3.RUNet3("effb4", head=True)`, loaded as `eval_ru.py` does). Input `input` float32 `[1,3,380,380]`,
`(x/255 − 0.5)/0.5`, RGB, PIL-bilinear resize of the crop (`train_ru3.to_t2`). Outputs: `out` `[1,11]` with the same
layout as the RepViT file (3 class logits, 4 operation logits, 4 quantities), and `evidence` `[1,256]` = sigmoid of the
evidence head resampled bilinearly (align_corners=False) from the backbone's native 12×12 grid (380/32) to the 16×16 the
page expects, row-major. Verification on 50 fixed-set images (`demo_export/export_report.json`, `verify_50.jsonl`): max
|Δ| onnxruntime vs PyTorch fp32 = 7.4e-6 (`out`), 6.6e-6 (`evidence`), 1.5e-6 (class probabilities); argmax decision 50/50
and rule-B named part 50/50 identical to PyTorch on the same 16×16 map; 48/50 identical to rule B applied to the native
12×12 map (two images where the 12→16→crop two-step resampling moves the top part). Against `evidence.jsonl` the
agreement was 43/50 decisions and 38/50 named parts for that model — that file comes from the paper's main model `clipe5_s20260929`
(CLIP ViT-L/14 + LoRA), a different network, so this is a cross-model number, not an export check. onnxruntime CPU
20.7 ms per image.

`models/ru4e_repvit.onnx` (18.11 MB, opset 17, sha256 `423f9116…`, 2026-10-15) — the third option「RepViT 證據版（小，約 19 MB）」
(`DemoCore.MODELS.repvit_ev`), for old phones. Exported by the same script with `--arch repvit` from
`ru_ru4e_repvit_s20260929.pth` (`RUNet3("repvit", head=True)`, 4.72 M parameters, same RU4 recipe as the EfficientNet-B4
evidence model). Input `[1,3,224,224]`, same `(x/255 − 0.5)/0.5` and PIL-bilinear resize (the page's resize port with
size 224); `out` `[1,11]` and `evidence` `[1,256]` as above, the evidence map resampled in-graph from the native 7×7 grid
(224/32). Verification on the same 50 images (`demo_export/export_report_repvit.json`, `verify_50_repvit.jsonl`): max |Δ|
onnxruntime vs PyTorch 1.0e-5 (`out`), 4.2e-6 (`evidence`), 1.7e-6 (class probabilities); decision 50/50, rule-B named part
50/50 on the same 16×16 map, 47/50 vs rule B on the native 7×7 map. onnxruntime CPU (same machine, same session): 11.1 ms
single-thread / 5.8 ms default threads, vs 74.7 / 29.1 ms for `ru4e_effb4.onnx`. Validation
(`results/research/retouch_unified_20260929/RESULTS_ru4e_repvit_s20260929.md`): Alibaba balanced 66.2 % (B4 72.6),
originals → filter 49.1 % (B4 18.6), retouched → fake 0.33 % (B4 0.33); CDFv2 frame AUC 0.756 (0.848), DFD 0.892 (0.915);
explanation (`results/research/cgd_20260927/explain_RU4E-repvit_s20260929.json`) IoU7 0.74 on donor/SD/SDXL (B4 0.80–0.82),
restoration flip 0.85/0.83/0.83 against GT-restore ceilings 0.85/0.83/0.83 (B4 0.88/0.87/0.87 vs 0.88/0.88/0.87).
Test: `make_fixture_ev.py --model repvit_ev` + `run_test_evidence_headless.py --model repvit_ev` (same 20 images):
decision 20/20, named part 20/20, sentences 19/20 — the one difference is a part mean on a rounding boundary (JS mask
0.735 vs cv2 mask 0.736 on the browser's own landmarks and map → 「0.73」 vs 「0.74」), the known mask-rasterisation
difference (max 0.008 in the 50-image mask test), not the model path. Headless Chrome, 1 WASM thread, 20 images:
inference median 70 ms (B4 465 ms), wall median 176 ms (B4 559 ms), model load 0.6 s (B4 0.7 s).

`models/ru_repvit.onnx` — exported by `results/research/retouch_unified_20260929/export_ru_tflite.py` (same export also
produces the TFLite files in `results/mobile_export/ru_<arm>_repvit/`; all four deployment gates pass, 200/200 decision
agreement with PyTorch, 9.7 ms per image single-thread desktop CPU for RU1). Output vector: 3 class logits, 4 operation
logits (eye enlargement, face slimming, whitening, smoothing), 4 quantity estimates (not shown: they failed validation).

## Honest limits (shown on the page)
On an unseen commercial retouching service the model family calls 0.3 % of retouched faces fake and reaches 71–73 %
balanced accuracy on retouched vs untouched; smoothing is recognised reliably, single eye enlargement / slimming /
whitening often are not, and some untouched photos are called filter. Probabilities are not calibrated.

## Explanation text (2026-10-14)

The page now writes the four-sentence T2 explanation of the explain branch (`explain_t2.js`, a line-by-line port of
`results/research/explain_vlm_20261012/explain_v2.py`, rules in `PRE_DECLARED.md` section 9.1): verdict sentence, region
sentence, operations sentence (operations at or above the 0.5 threshold with their scores, or the fixed sentence
「四種操作的分數都未達門檻 0.5」), calibration sentence. The old one-line English template stays selectable as「舊模板」.
The「VLM 觀察句」slot shows a fixed note: this version does not call a VLM, because the observation sentence did not pass
the blind matching test (report section 5.2).

- `explain_t2.js` — pure functions, no DOM (`t2Sentences`, `compose`, `oldTemplate`, `recordFromOutputs`).
- `evidence_overlay.js` — contour overlay as in `vlm_explain.overlay()` / `run_v3.py`: 0.5 iso-line (cyan) and the
  top-12 % boundary (0.88 quantile of the bilinearly up-sampled 16x16 map, yellow), lines only.
- `face_masks.js` — face-part masks and rule B in the browser (see below).
- `demo_core.js` — the page's analysis path (crop, PIL-style resize, model run, masks, rule B, record), shared by
  `index.html` and the headless test so the test runs exactly what the page runs.

### Evidence head in the browser (2026-10-14)

With the EfficientNet-B4 model the page computes the region sentence and the overlay itself:

1. the 478 landmarks of the page's one detection (full photo) are mapped into the 224×224 grid of the crop;
2. `face_masks.js` builds the eyes / nose / mouth / skin / contour masks on that grid following
   `docs/paper_v2/occlusion_regions.region_masks` — same landmark index lists (`R_EYE`, `L_EYE`, `LIPS`, `NOSE`,
   `FACE_OVAL`), same dilation `k = max(3, int(0.06·face width)) | 1`, same contour band `int(0.10·face width) | 1`,
   same set algebra (skin = eroded face hull minus eyes/nose/mouth, contour = dilated minus eroded hull);
3. the 16×16 map is up-sampled bilinearly to the grid (`EvidenceOverlay.upsample`), the mean inside each mask is rounded
   to 3 dp, the part with the largest mean is named, 「整臉」when eyes, nose and mouth all reach 0.5 (rule B of
   `explain_ours.explain`); the 2-dp means go into the record for `explain_t2.js`;
4. the overlay draws the 0.5 iso-line and the top-12 % boundary as before.

Differences from the Python pipeline, and their measured effect:

| difference | Python | browser | effect |
|---|---|---|---|
| landmarks for the masks | detected again on the crop (`get_landmarks(arr)`), masks at native crop resolution | the single full-photo detection mapped into the 224 grid | named part identical on 20/20 (fixture) and, cv2 at 224 vs cv2 at native resolution, 50/50 |
| hull / fill / morphology | `cv2.convexHull`, `cv2.fillConvexPoly`, `cv2.dilate`/`erode` with `MORPH_ELLIPSE` | monotone-chain hull, scanline fill (pixel centres), OpenCV's ellipse row formula, same border rule | same landmarks + same map: named part 50/50 identical, max abs Δ part mean 0.008, mask area within 4 % |
| landmark detector | mediapipe 0.10.35 Python, `face_landmarker.task` | tasks-vision 0.10.14 JS, float16 `face_landmarker.task` | crop box identical 20/20 in the fixture |
| resize to the model input | PIL `BILINEAR` | port of Pillow's resampling in `demo_core.js` (triangle filter with scale-dependent support, 22-bit fixed-point weights, two passes rounded to uint8) | max abs Δ class probability 0.0000 on 20/20 (with Canvas `drawImage` it was up to 0.093 and flipped one decision) |
| rounding to 2 / 3 dp | Python `round()` | `pyRound` (correctly rounded from the binary value, half-to-even on exact ties) | needed: 0.985 → Python 0.98, `Math.round` 0.99 |

What still differs from the Python pipeline: the photo is decoded by the browser (identical for PNG; JPEG decoders may
differ by ±1 LSB), the landmark model is the JS float16 build (crop boxes matched on all fixtures but can differ by a
pixel on other photos), and the masks are built on the 224 grid from mapped landmarks rather than on the native crop from
a second detection. Everything downstream (ONNX graph, rule B, sentences) is the same code path or a verified port.

Timing in headless Chrome (WebAssembly, 1 thread, desktop CPU, 20 fixture images): landmarks 25 ms, preprocess 11 ms,
EfficientNet-B4 inference 457–463 ms (median 457), masks + rule B 59 ms, **wall 563–568 ms per image** (median 556);
model load 0.7 s, MediaPipe load 0.55 s. The RepViT model remains the fast option (tens of ms).

### Tests (no Node.js needed; a Chromium browser is used headless)
```
python test/make_fixture.py                    # 50 records of evidence.jsonl + Python T2 text  -> fixture_t2.js
python test/run_test_headless.py               # explain_t2.js equivalence: last run 50 PASS / 0 FAIL
python test/make_fixture_ev.py                 # 20 fixed-set images (4 per group) -> test/img/*.png + Python reference of the page path (fixture_ev.js)
python test/run_test_evidence_headless.py      # full page path in headless Chrome over a local HTTP server: last run 20 PASS / 0 FAIL
python test/make_fixture_masks50.py            # 50 verification images: landmarks + ONNX map + cv2 masks -> fixture_masks50.js
python test/run_test_masks_headless.py         # face_masks.js vs cv2 on the same inputs: last run 50/50 same named part
```
`run_test_evidence_headless.py` serves `docs/demo_ru` over HTTP (the ONNX file and images cannot be fetched from
`file://`); a pending `<img src="/__hold">` keeps the page's load event from firing until the page POSTs its results to
`/__done`, so `--dump-dom` dumps only after all images are analysed. It compares decision, named parts and the four T2
sentences with the Python reference (same ONNX, PIL resize, cv2 masks, `explain_v2.t2_sentences`), then feeds the
browser's own landmarks and map to the cv2 masks to isolate the mask-rasterisation effect, and writes
`test/evidence_headless_result.json`. The fixture images are crops of the project's fixed explanation set (FF++, Alibaba
renders, part edits, FFHQ demo edits), no new data.

The JavaScript is always executed by the browser's own engine; expected values come from the Python modules. Without a
Chromium browser, open `test/test_explain_t2.html` or `test/test_masks50.html` in any browser (file://) and
`test/test_evidence_page.html` over HTTP: each prints PASS/FAIL per record.

The page still fetches ONNX Runtime Web, the MediaPipe bundle and its face model from CDNs on first load, exactly as
before; the model files are local. Note that `models/ru4e_effb4.onnx` is 67 MB.

## Server mode: LLM explanation (2026-10-15, optional, off by default)

No LLM runs in the browser. When「伺服器模式（LLM 解釋）」is ticked, the page sends the structured record only (decision,
three class scores, four operation scores, evidence means per part, named part; never the photo) to a local server and
shows the text it returns; when the server cannot be reached the page keeps T2 and shows nothing else.

```
python results/research/explain_vlm_20261012/nl_v5/nl_server.py            # Qwen2.5-7B-Instruct, bf16, ~16 GB GPU; http://127.0.0.1:8787
```
- `POST /explain {facts, style}` (style `general` | `pro`) and `POST /qa {facts, question_id}` (0-7) return
  `{text, source, gate, ms}`; `source` is `llm` (the model's text passed the gate), `template` (the model's text failed
  the gate twice, the code template is returned) or `fixed` (the three limitation questions 和原圖比差在哪？／是誰？／可以確定嗎？
  are answered by fixed code sentences, no model call). Prompt `p2` of the NL line, unchanged.
- The gate runs on the server (`nl_core.gate_check_v2`): H1-H6 of `validate_text.py`, G7 (the decision score compared
  with the 0.5 operation threshold) and fact preservation. Flow: greedy, then one sampled regeneration, then the template.
- Needs the evidence head (EfficientNet-B4 model); with RepViT the page stays on T2.
- `nl_client.js` holds the fetch calls (shared by `index.html` and the test page); the page's controls: the toggle, the
  server URL (default `http://127.0.0.1:8787`), style 一般／專業, and the eight questions as buttons.
- Numbers for the gate and the routed questions on the 361-image holdout: `results/research/explain_vlm_20261012/nl_v5/QA_ROUTE_RESULTS.md`.

Test (`test/run_test_server_headless.py`): starts `nl_server.py` on port 8787 (refuses if the port is taken), serves the
demo over HTTP, runs `test/test_server_page.html` in headless Chrome: 10 fixture records (`fixture_ev.js`, every second
one) through the page path (MediaPipe, `ru4e_effb4.onnx`, masks, record), then `NLClient.explain` in both styles and
`NLClient.qa` for the 8 questions; every returned text is re-checked in Python with `validate_text.validate` (via
`nl_core.gate_check`, H1-H6) and `gate_check_v2`; the server it started is stopped at the end. Last run: 100 texts,
0 failing the re-check; sources 55 llm / 15 template / 30 fixed; 18 needed the sampled regeneration; server load 17.6 s;
browser round trip median (p90) 1.52 s (1.93) general, 2.32 s (3.72) pro, 1.19 s (2.15) for the five LLM questions,
2 ms for the fixed answers (`test/server_headless_result.json`; RTX 6000 Ada, bf16, batch 1).

## 2026-10-30: default model W, sentences name smoothing only, runtime checker

Cross-model check of the shipped model (`export_report_ru7we.json`): against `evidence.jsonl`, the main model's records, the agreement is 43/50 decisions and 38/50 named parts (the shipped and the previous browser model decide differently on 3 of the 50; the counts coincide). ONNX vs PyTorch of the same model: 50/50 decisions and named parts.

- Default evidence model is now `models/ru7we_effb4.onnx` (Addendum 70 W model, epoch 11 chosen on validation; shipped by
  user decision although the pre-declared gate failed on G1, see `results/research/retouch_unified_20260929/PRE_DECLARED.md`
  "Addendum 70 deviation"). ONNX vs PyTorch: 50/50 decisions and named parts, max |d out| 3.8e-4, 67 MB. The previous
  `models/ru4e_effb4.onnx` is kept for rollback (change `MODELS.effb4.file` in `demo_core.js`).
- The operations sentence names skin smoothing only (`t2Sentences(rec, lang, {namedOps: ["skin_smoothing"]})`); the other
  three scores stay visible as bars with the note that only smoothing is reliable across services. Without the option the
  sentences are the research rule, so `run_test_headless.py` still checks equivalence with Python (50/50 zh, 54/54 en).
- `ExplainT2.checkT2` runs on the page before display (H1 decision word, H2 part words, H3 named operations, H4 numbers
  from the record, H6 sentence count, G8 certainty words); text that fails is not shown and the badge says so. Before this
  change the page claimed a checker that only existed on the removed LLM server. Test: `test/test_checker.html` (100/100
  composed sentences pass, 8/8 deliberately broken sentences rejected).
- Evidence path test with W: 19/20 identical sentences; the one difference is a rounding boundary (nose mean evidence
  ~0.995: 1.00 in the browser, 0.99 in Python); decisions and named parts 20/20. Old fixtures in `test/backup_ru4e_20261030/`.
- Patch scripts: `page_checker_w.py` (backups `*_pre_checker_20261030.*`).
