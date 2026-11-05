/* face_masks.js — landmark face-part masks and rule B in the browser.
 *
 * Port of docs/paper_v2/occlusion_regions.region_masks (eyes, nose, mouth, skin, contour) and of the named-part rule of
 * results/research/retouch_unified_20260929/explain_ours.explain (rule B): mean of the up-sampled evidence map inside
 * each part, the part with the largest mean is named, "whole face" when eyes, nose and mouth all have mean >= 0.5.
 *
 * Same 478-point MediaPipe FaceLandmarker topology and the same index lists (R_EYE, L_EYE, LIPS, NOSE, FACE_OVAL of
 * sbi/sbi_generator.py). Masks are rasterised on a square W x H grid (the page uses 224 x 224) from landmarks already
 * mapped into crop coordinates. Differences from the Python version, all documented in README.md:
 *   - Python builds the masks on the crop at its native resolution and detects the landmarks again on that crop;
 *     here the page's one detection on the full photo is mapped into the crop grid.
 *   - cv2.convexHull / cv2.fillConvexPoly are replaced by a monotone-chain hull and a scanline fill (pixel centres);
 *     cv2.getStructuringElement(MORPH_ELLIPSE) is reproduced with OpenCV's own row formula; dilate/erode use
 *     OpenCV's default border rule (dilate: outside = 0, erode: outside = 1).
 * Pure functions, no DOM. Loads as a classic script (window.FaceMasks) and as a CommonJS module.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.FaceMasks = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  const R_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246, 46, 53, 52, 65, 55, 70, 63, 105, 66, 107];
  const L_EYE = [263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466, 276, 283, 282, 295, 285, 300, 293, 334, 296, 336];
  const LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185];
  const NOSE = [168, 6, 197, 195, 5, 4, 1, 19, 94, 2, 98, 97, 326, 327, 294, 278, 344, 440, 275, 45, 220, 115, 48, 64];
  const FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58,
                     132, 93, 234, 127, 162, 21, 54, 103, 67, 109];
  const FACE = ["eyes", "nose", "mouth", "skin", "contour"];

  // Same as ExplainT2.pyRound (kept local so this module has no dependency): Python's round(x, nd) on a double: correctly rounded from the exact binary value (toFixed does that), except exact
  // binary ties (e.g. 0.125 at 2 dp), where Python rounds half to even. Math.round(x*100)/100 is wrong on values such as
  // 0.985 (binary 0.98499...: Python gives 0.98, Math.round gives 0.99).
  function pyRound(x, nd) {
    const m = Math.pow(10, nd), y = x * m;
    if (Number.isInteger(x * Math.pow(2, nd + 1)) && y - Math.floor(y) === 0.5) { const n0 = Math.floor(y); return (n0 % 2 === 0 ? n0 : n0 + 1) / m; }
    return Number(x.toFixed(nd));
  }

  // cv2.convexHull on int32 points (astype(int32) truncates toward zero; coordinates are >= 0 here).
  function convexHull(pts) {
    const p = pts.map(([x, y]) => [Math.trunc(x), Math.trunc(y)]).sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    const n = p.length; if (n < 3) return p;
    const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    const lower = []; for (const q of p) { while (lower.length >= 2 && cross(lower[lower.length - 2], lower[lower.length - 1], q) <= 0) lower.pop(); lower.push(q); }
    const upper = []; for (let i = n - 1; i >= 0; i--) { const q = p[i]; while (upper.length >= 2 && cross(upper[upper.length - 2], upper[upper.length - 1], q) <= 0) upper.pop(); upper.push(q); }
    lower.pop(); upper.pop(); return lower.concat(upper);
  }

  // Convex polygon fill, boundary inclusive (as cv2.fillConvexPoly without anti-aliasing): for each row, the pixels
  // whose centre column lies within the polygon's horizontal extent on that row, edges rounded outward.
  function fillConvex(mask, W, H, poly) {
    const n = poly.length; if (!n) return mask;
    let ymin = Infinity, ymax = -Infinity; for (const [, y] of poly) { ymin = Math.min(ymin, y); ymax = Math.max(ymax, y); }
    for (let y = Math.max(0, ymin); y <= Math.min(H - 1, ymax); y++) {
      let xl = Infinity, xr = -Infinity;
      for (let i = 0; i < n; i++) {
        const [x0, y0] = poly[i], [x1, y1] = poly[(i + 1) % n];
        if (y0 === y1) { if (y === y0) { xl = Math.min(xl, x0, x1); xr = Math.max(xr, x0, x1); } continue; }
        const lo = Math.min(y0, y1), hi = Math.max(y0, y1); if (y < lo || y > hi) continue;
        const x = x0 + (y - y0) * (x1 - x0) / (y1 - y0); xl = Math.min(xl, x); xr = Math.max(xr, x);
      }
      if (xl === Infinity) continue;
      for (let x = Math.max(0, Math.round(xl)); x <= Math.min(W - 1, Math.round(xr)); x++) mask[y * W + x] = 1;
    }
    return mask;
  }

  // cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)) as a list of [dx, dy] offsets (OpenCV's row formula).
  function ellipseOffsets(k) {
    const r = Math.floor(k / 2), inv = 1 / (r * r || 1), off = [];
    for (let i = 0; i < k; i++) {
      const dy = i - r; let j1 = 0, j2 = 0;
      if (Math.abs(dy) <= r) { const dx = Math.round(r * Math.sqrt(Math.max(0, (r * r - dy * dy) * inv))); j1 = Math.max(r - dx, 0); j2 = Math.min(r + dx + 1, k); }
      for (let j = j1; j < j2; j++) off.push([j - r, dy]);
    }
    return off;
  }

  function morph(mask, W, H, k, dilate) {
    const off = ellipseOffsets(k), out = new Uint8Array(W * H), outside = dilate ? 0 : 1;
    for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
      let v = dilate ? 0 : 1;
      for (const [dx, dy] of off) {
        const xx = x + dx, yy = y + dy;
        const m = (xx < 0 || yy < 0 || xx >= W || yy >= H) ? outside : mask[yy * W + xx];
        if (dilate ? m : !m) { v = dilate ? 1 : 0; break; }
      }
      out[y * W + x] = v;
    }
    return out;
  }

  function hull(W, H, pts, dil) {
    const m = fillConvex(new Uint8Array(W * H), W, H, convexHull(pts));
    return dil ? morph(m, W, H, dil, true) : m;
  }

  /** lm: array of 478 [x, y] in grid pixel coordinates (W x H). Returns {eyes, nose, mouth, skin, contour} Uint8Arrays. */
  function regionMasks(lm, W, H) {
    const sel = (idx) => idx.map((i) => lm[i]);
    let xmin = Infinity, xmax = -Infinity; for (const [x] of lm) { xmin = Math.min(xmin, x); xmax = Math.max(xmax, x); }
    const fw = xmax - xmin, k = Math.max(3, Math.trunc(fw * 0.06)) | 1, band = Math.trunc(fw * 0.10) | 1, N = W * H;
    const face = hull(W, H, sel(FACE_OVAL), 0);
    const re = hull(W, H, sel(R_EYE), k), le = hull(W, H, sel(L_EYE), k), eyes = new Uint8Array(N);
    for (let i = 0; i < N; i++) eyes[i] = re[i] | le[i];
    const nose = hull(W, H, sel(NOSE), k), mouth = hull(W, H, sel(LIPS), k);
    const inner = morph(face, W, H, band, false), outer = morph(face, W, H, band, true);
    const contour = new Uint8Array(N), skin = new Uint8Array(N);
    for (let i = 0; i < N; i++) { contour[i] = outer[i] & (1 - inner[i]); skin[i] = inner[i] & (1 - eyes[i]) & (1 - nose[i]) & (1 - mouth[i]); }
    return { eyes, nose, mouth, skin, contour };
  }

  /** Mean of `up` (Float32Array W*H) inside each mask, rounded to 3 dp as explain_ours does; 0 for an empty mask. */
  function partMeans(up, masks) {
    const out = {};
    for (const k of FACE) {
      const m = masks[k]; let s = 0, n = 0;
      for (let i = 0; i < m.length; i++) if (m[i]) { s += up[i]; n++; }
      out[k] = n ? pyRound(s / n, 3) : 0;
    }
    return out;
  }

  /** Rule B. parts: 3-dp means. Returns {named_parts, whole_face, top}. First maximum wins on ties (Python max()). */
  function ruleB(parts) {
    let top = FACE[0]; for (const k of FACE) if (parts[k] > parts[top]) top = k;
    const whole = parts.eyes >= 0.5 && parts.nose >= 0.5 && parts.mouth >= 0.5;
    return { named_parts: whole ? ["whole face"] : [top], whole_face: whole, top };
  }

  /** Full step from a 16x16 map (array of rows) and crop-grid landmarks: {evidence_mean_per_part (2 dp, as the evidence
   *  JSON stores it), parts3 (3 dp), named_parts, whole_face}. `upsample` is EvidenceOverlay.upsample. */
  function evidenceParts(map16, lm, W, H, upsample) {
    const up = upsample(map16, W, H), masks = regionMasks(lm, W, H), parts3 = partMeans(up, masks), rb = ruleB(parts3);
    const parts2 = {}; for (const k of FACE) parts2[k] = pyRound(parts3[k], 2);
    return { evidence_mean_per_part: parts2, parts3, named_parts: rb.named_parts, whole_face: rb.whole_face, masks };
  }

  return { FACE, pyRound, R_EYE, L_EYE, LIPS, NOSE, FACE_OVAL, convexHull, fillConvex, ellipseOffsets, morph, regionMasks, partMeans, ruleB, evidenceParts };
});
