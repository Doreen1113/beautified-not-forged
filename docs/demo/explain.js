// Explanation logic of the web demo, as pure functions (no DOM) so it can be tested in node against the Python version
// (results/research/retouch_unified_20260929/explain_ours.py, occlusion_regions.region_masks).
//
// Facial parts are built from MediaPipe's 478 landmarks exactly as in region_masks: convex hulls of the eye+brow, nose
// and lip point sets dilated by k = 6 % of the face width, a contour band of 10 % of the face width around the face
// oval, and skin = the face oval eroded by half that band, minus eyes, nose and mouth. The part is named by the MEAN
// evidence inside each part (rule B: right part in 97.7-99.0 % of held-out part forgeries); "whole face" when eyes,
// nose and mouth all exceed 0.5.

export const CLS = ["real", "fake", "filter"];
export const OPS = ["eye", "contour", "tone", "texture"];
export const OP_TEXT = { eye: "eyes enlarged", contour: "face reshaped", tone: "skin brightened", texture: "skin smoothed" };
export const PARTS = ["eyes", "nose", "mouth", "skin", "contour"];

const R_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246, 46, 53, 52, 65, 55, 70, 63, 105, 66, 107];
const L_EYE = [263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466, 276, 283, 282, 295, 285, 300, 293, 334, 296, 336];
const LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185];
const NOSE = [168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 98, 97, 326, 327, 294, 278, 344, 440, 275, 45, 220, 115, 48, 64];
const FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150,
  136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109];

export const softmax = (v) => { const m = Math.max(...v), e = v.map((x) => Math.exp(x - m)), s = e.reduce((a, b) => a + b); return e.map((x) => x / s); };
export const sigmoid = (x) => 1 / (1 + Math.exp(-x));

// Andrew's monotone chain; returns the hull counter-clockwise
function convexHull(pts) {
  const p = pts.map((q) => [q[0], q[1]]).sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
  const lo = [], up = [];
  for (const q of p) { while (lo.length >= 2 && cross(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
  for (const q of p.slice().reverse()) { while (up.length >= 2 && cross(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
  return lo.slice(0, -1).concat(up.slice(0, -1));
}

// signed distance to a convex polygon: negative inside, positive outside
function signedDist(h, x, y) {
  let inside = true, dmin = Infinity;
  for (let i = 0; i < h.length; i++) {
    const [ax, ay] = h[i], [bx, by] = h[(i + 1) % h.length];
    if ((bx - ax) * (y - ay) - (by - ay) * (x - ax) < 0) inside = false;
    const vx = bx - ax, vy = by - ay, t = Math.max(0, Math.min(1, ((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy || 1)));
    dmin = Math.min(dmin, Math.hypot(x - ax - t * vx, y - ay - t * vy));
  }
  return inside ? -dmin : dmin;
}

// lm: 478 [x, y] points in the coordinates of an S x S crop; returns boolean masks on an R x R grid
export function partMasks(lm, S, R = 95) {
  const s = R / S, P = lm.map(([x, y]) => [x * s, y * s]);
  const xs = P.map((p) => p[0]); const fw = Math.max(...xs) - Math.min(...xs);
  const k = (Math.max(3, Math.floor(fw * 0.06)) | 1) / 2, band = (Math.floor(fw * 0.10) | 1) / 2;
  const hull = (idx) => convexHull(idx.map((i) => P[i]));
  const H = { reye: hull(R_EYE), leye: hull(L_EYE), nose: hull(NOSE), mouth: hull(LIPS), face: hull(FACE_OVAL) };
  const M = Object.fromEntries(PARTS.map((p) => [p, new Uint8Array(R * R)]));
  for (let y = 0; y < R; y++) for (let x = 0; x < R; x++) {
    const cx = x + 0.5, cy = y + 0.5, i = y * R + x;
    const eyes = signedDist(H.reye, cx, cy) <= k || signedDist(H.leye, cx, cy) <= k;
    const nose = signedDist(H.nose, cx, cy) <= k, mouth = signedDist(H.mouth, cx, cy) <= k;
    const df = signedDist(H.face, cx, cy);
    const inner = df <= -band;                       // face oval eroded by band
    M.eyes[i] = eyes; M.nose[i] = nose; M.mouth[i] = mouth;
    M.contour[i] = df <= band && !inner;             // dilated minus eroded oval
    M.skin[i] = inner && !eyes && !nose && !mouth;
  }
  return M;
}

// bilinear upsampling of an h x w grid to R x R with half-pixel centres (torch align_corners=False)
export function upsample(grid, h, w, R) {
  const out = new Float32Array(R * R);
  for (let y = 0; y < R; y++) for (let x = 0; x < R; x++) {
    const gy = Math.min(h - 1, Math.max(0, (y + 0.5) * h / R - 0.5)), gx = Math.min(w - 1, Math.max(0, (x + 0.5) * w / R - 0.5));
    const y0 = Math.floor(gy), x0 = Math.floor(gx), y1 = Math.min(h - 1, y0 + 1), x1 = Math.min(w - 1, x0 + 1), fy = gy - y0, fx = gx - x0;
    out[y * R + x] = grid[y0 * w + x0] * (1 - fy) * (1 - fx) + grid[y0 * w + x1] * (1 - fy) * fx
      + grid[y1 * w + x0] * fy * (1 - fx) + grid[y1 * w + x1] * fy * fx;
  }
  return out;
}

// logits: 3, presence: 4 logits, evLogits: h*w, lm: 478 [x,y] in crop coordinates of size S
export function explain(logits, presence, evLogits, h, w, lm, S, R = 95) {
  const p = softmax(Array.from(logits)), label = CLS[p.indexOf(Math.max(...p))];
  const ops = Array.from(presence).map(sigmoid);
  const ev = upsample(Array.from(evLogits).map(sigmoid), h, w, R);
  let parts = null, top = null, whole = false;
  if (lm) {
    const M = partMasks(lm, S, R); parts = {};
    for (const k of PARTS) { let s = 0, n = 0; for (let i = 0; i < R * R; i++) if (M[k][i]) { s += ev[i]; n++; } parts[k] = n ? s / n : 0; }
    top = PARTS.reduce((a, b) => (parts[b] > parts[a] ? b : a));
    whole = ["eyes", "nose", "mouth"].every((k) => parts[k] >= 0.5);
  }
  const named = OPS.filter((_, j) => ops[j] >= 0.5).map((o) => OP_TEXT[o]);
  let sentence;
  if (label === "real") sentence = "No manipulation detected.";
  else if (label === "fake") sentence = whole ? "Forgery detected; evidence across the whole face."
    : top ? `Forgery detected; evidence on the ${top}.` : "Forgery detected.";
  else sentence = "Beautified, identity kept: " + (named.length ? named.join(", ") : "operation unclear") + ".";
  return { label, probs: p, ops, parts, top: whole ? "whole face" : top, sentence, ev, R };
}
