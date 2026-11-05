/* demo_core.js — the page's analysis path, shared by index.html and test/test_evidence_page.html so the headless test
 * runs exactly what the page runs. Needs window.ort (ONNX Runtime Web), ExplainT2, EvidenceOverlay, FaceMasks.
 *
 * MODELS: file, input size and whether the graph has the 16x16 `evidence` output.
 *   ru_repvit.onnx   224 px, output `out` [1,11] only (export_ru_tflite.py)                      -> no region naming
 *   ru7we_effb4.onnx 380 px, outputs `out` [1,11] + `evidence` [1,256] (demo_export/export_ru4e_onnx.py --arm ru7we; Addendum 70
 *                    W model, default since 2026-10-30; ru4e_effb4.onnx kept for rollback)
 *   ru4e_repvit.onnx 224 px, outputs `out` [1,11] + `evidence` [1,256] (export_ru4e_onnx.py --arch repvit; native 7x7 map
 *                    resampled in-graph to 16x16), same preprocessing as the others (PIL-bilinear port, size from MODELS)
 * All three share the input normalisation (x/255 - 0.5) / 0.5 and the `out` layout: 3 class logits, 4 operation logits,
 * 4 quantities.
 *
 * analyse(bitmap, landmarks, opts) -> { record, label, p, ops, evidence, ms, timing, landmarksGrid }
 *   crop = landmark bounding box + 35 % per side (training crop), read at native resolution and resized to the model
 *   input with a port of PIL's bilinear resampling (train_ru3.to_t2), and drawn on the 224 x 224 display canvas; the 478 landmarks are mapped into the 224 grid, the evidence map is up-sampled to that
 *   grid, face-part masks are built on it and rule B names the part (FaceMasks). The record goes to ExplainT2.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.DemoCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  const MODELS = {
    repvit: { file: "models/ru_repvit.onnx", size: 224, evidence: false, label: "RepViT（快，無證據頭）", name: "快速版", params: "4.7 M" },
    effb4: { file: "models/ru7we_effb4.onnx", size: 380, evidence: true, label: "EfficientNet-B4 + evidence head（預設）", name: "證據版", params: "17.6 M" },
    repvit_ev: { file: "models/ru4e_repvit.onnx", size: 224, evidence: true, label: "RepViT 證據版（小，約 19 MB）", name: "小型證據版", params: "4.7 M" },
  };
  const CLS = ["real", "fake", "filter"];
  const GRID = 224;  // mask / overlay grid

  function cropBox(lm, w, h) {
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    for (const p of lm) { const x = p.x * w, y = p.y * h; x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x); y1 = Math.max(y1, y); }
    const bw = x1 - x0, bh = y1 - y0, m = 0.35;
    return [Math.max(0, Math.floor(x0 - bw * m)), Math.max(0, Math.floor(y0 - bh * m)),
            Math.min(w, Math.floor(x1 + bw * m)), Math.min(h, Math.floor(y1 + bh * m))];
  }

  // PIL Image.resize(..., BILINEAR) for uint8 RGB(A) data: separable triangle filter whose support grows with the scale
  // when down-sampling (antialiased), weights normalised, two passes (horizontal then vertical) each rounded to uint8,
  // as Pillow's ImagingResample does. This is the resize of train_ru3.to_t2, so the model input matches training and
  // the Python reference, which Canvas drawImage (Skia's own filter) does not: see README "What still differs".
  const PREC = 22, HALF = 1 << (PREC - 1), ONE = 1 << PREC;   // Pillow's PRECISION_BITS for 8-bit data
  function pilCoeffs(inSize, outSize) {
    const scale = inSize / outSize, fs = Math.max(scale, 1), support = 1.0 * fs, ks = [];
    for (let xx = 0; xx < outSize; xx++) {
      const center = (xx + 0.5) * scale;
      const xmin = Math.max(0, Math.trunc(center - support + 0.5)), xmax = Math.min(inSize, Math.trunc(center + support + 0.5));
      const w = []; let sum = 0;
      for (let x = xmin; x < xmax; x++) { const t = Math.abs((x - center + 0.5) / fs); const v = t < 1 ? 1 - t : 0; w.push(v); sum += v; }
      // normalise, then quantise to 22-bit fixed point exactly as Pillow's normalize_coeffs_8bpc
      ks.push([xmin, w.map((v) => { const k = sum ? v / sum : 0; return k < 0 ? Math.trunc(-0.5 + k * ONE) : Math.trunc(0.5 + k * ONE); })]);
    }
    return ks;
  }
  const fix8 = (acc) => { const r = Math.floor(acc / ONE); return r < 0 ? 0 : r > 255 ? 255 : r; };   // (acc >> PRECISION_BITS) clipped
  function pilResizeRGB(data, sw, sh, dw, dh) {   // data: RGBA Uint8ClampedArray (sw x sh) -> RGB Uint8Array (dw x dh)
    const kx = pilCoeffs(sw, dw), ky = pilCoeffs(sh, dh), tmp = new Uint8Array(dw * sh * 3), out = new Uint8Array(dw * dh * 3);
    for (let y = 0; y < sh; y++) for (let xx = 0; xx < dw; xx++) {
      const [x0, w] = kx[xx]; let r = HALF, g = HALF, b = HALF;
      for (let k = 0; k < w.length; k++) { const i = (y * sw + x0 + k) * 4; r += w[k] * data[i]; g += w[k] * data[i + 1]; b += w[k] * data[i + 2]; }
      const o = (y * dw + xx) * 3; tmp[o] = fix8(r); tmp[o + 1] = fix8(g); tmp[o + 2] = fix8(b);
    }
    for (let yy = 0; yy < dh; yy++) { const [y0, w] = ky[yy]; for (let xx = 0; xx < dw; xx++) {
      let r = HALF, g = HALF, b = HALF;
      for (let k = 0; k < w.length; k++) { const i = ((y0 + k) * dw + xx) * 3; r += w[k] * tmp[i]; g += w[k] * tmp[i + 1]; b += w[k] * tmp[i + 2]; }
      const o = (yy * dw + xx) * 3; out[o] = fix8(r); out[o + 1] = fix8(g); out[o + 2] = fix8(b);
    } }
    return out;
  }

  /** Model input from the crop pixels: PIL-bilinear resize to size x size, then (x/255 - 0.5) / 0.5, CHW. */
  function toTensorFromCrop(rgba, sw, sh, size) {
    const rgb = pilResizeRGB(rgba, sw, sh, size, size), n = size * size, t = new Float32Array(3 * n);
    for (let i = 0; i < n; i++) for (let c = 0; c < 3; c++) t[c * n + i] = (rgb[i * 3 + c] / 255 - 0.5) / 0.5;
    return new ort.Tensor("float32", t, [1, 3, size, size]);
  }

  function toTensor(canvas, size) {   // previous path (Canvas-resized pixels), kept for reference / RepViT comparisons
    const d = canvas.getContext("2d").getImageData(0, 0, size, size).data, n = size * size, t = new Float32Array(3 * n);
    for (let i = 0; i < n; i++) for (let c = 0; c < 3; c++) t[c * n + i] = (d[i * 4 + c] / 255 - 0.5) / 0.5;
    return new ort.Tensor("float32", t, [1, 3, size, size]);
  }

  const softmax = (v) => { const m = Math.max(...v), e = v.map((x) => Math.exp(x - m)), s = e.reduce((a, b) => a + b); return e.map((x) => x / s); };
  const sigmoid = (x) => 1 / (1 + Math.exp(-x));

  // bytes (optional): the model file already downloaded by the caller (index.html fetches it itself to show download
  // progress); the session is then created from those bytes instead of fetching the URL again. Same graph either way.
  async function loadModel(key, baseUrl, bytes) {
    const m = MODELS[key], url = (baseUrl || "") + m.file;
    const t0 = performance.now();
    const session = await ort.InferenceSession.create(bytes || url, { executionProviders: ["wasm"] });
    return { key, session, size: m.size, hasEvidence: m.evidence, loadMs: performance.now() - t0, file: m.file };
  }

  function evidenceFromOutputs(out) {
    const t = out.evidence;
    if (!t || t.data.length !== 256) return null;
    const m = []; for (let y = 0; y < 16; y++) m.push(Array.from(t.data.slice(16 * y, 16 * y + 16)));
    return m;
  }

  /** bitmap: ImageBitmap/Image; landmarks: res.faceLandmarks[0] (normalised x, y); model: from loadModel;
   *  canvases: { model: canvas size x size (created if absent), display: 224 canvas or null }. */
  async function analyse(bitmap, landmarks, model, canvases) {
    const T = {}; let t = performance.now();
    const w = bitmap.width, h = bitmap.height, [x0, y0, x1, y1] = cropBox(landmarks, w, h);
    // crop pixels at native resolution (exact copy: 1:1 drawImage with integer source rectangle), then PIL-style resize
    const cw = x1 - x0, ch = y1 - y0;
    const mc = (canvases && canvases.model) || document.createElement("canvas"); mc.width = cw; mc.height = ch;
    const mctx = mc.getContext("2d", { willReadFrequently: true }); mctx.imageSmoothingEnabled = false;
    mctx.drawImage(bitmap, x0, y0, cw, ch, 0, 0, cw, ch);
    const rgba = mctx.getImageData(0, 0, cw, ch).data;
    if (canvases && canvases.display) {
      const dctx = canvases.display.getContext("2d"); dctx.imageSmoothingQuality = "high";
      dctx.drawImage(bitmap, x0, y0, cw, ch, 0, 0, GRID, GRID);
    }
    const input = toTensorFromCrop(rgba, cw, ch, model.size); T.preprocess = performance.now() - t; t = performance.now();
    const out = await model.session.run({ input });
    T.inference = performance.now() - t; t = performance.now();
    const v = Array.from(out.out.data);
    const p = softmax(v.slice(0, 3)), ops = v.slice(3, 7).map(sigmoid), k = p.indexOf(Math.max(...p)), label = CLS[k];
    const map16 = model.hasEvidence ? evidenceFromOutputs(out) : null;
    // landmarks in the 224 grid of the crop (the page's single detection on the full photo, mapped; see README)
    const sx = GRID / (x1 - x0), sy = GRID / (y1 - y0);
    const lmGrid = landmarks.map((q) => [(q.x * w - x0) * sx, (q.y * h - y0) * sy]);
    let evidence = null;
    if (map16) {
      const ep = FaceMasks.evidenceParts(map16, lmGrid, GRID, GRID, EvidenceOverlay.upsample);
      evidence = { evidence_map16: map16, evidence_mean_per_part: ep.evidence_mean_per_part, parts3: ep.parts3,
                   named_parts: ep.named_parts, whole_face: ep.whole_face };
    }
    T.evidence = performance.now() - t;
    const record = ExplainT2.recordFromOutputs(p, ops, evidence);
    record.operations_raw = { eye_enlargement: ops[0], face_slimming: ops[1], skin_brightening: ops[2], skin_smoothing: ops[3] };
    T.total = T.preprocess + T.inference + T.evidence;
    return { record, label, p, ops, evidence, box: [x0, y0, x1, y1], ms: T.inference, timing: T, landmarksGrid: lmGrid, raw: v };
  }

  return { MODELS, CLS, GRID, cropBox, toTensor, toTensorFromCrop, pilResizeRGB, pilCoeffs, softmax, sigmoid, loadModel, analyse, evidenceFromOutputs };
});
