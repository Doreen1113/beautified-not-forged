/* evidence_overlay.js — draws the evidence contour overlay of vlm_explain.overlay() / run_v3.py on a canvas:
 *   iso-line at 0.5 (absolute, cyan) and the boundary of the top-12 % area (0.88 quantile of the up-sampled map, yellow),
 *   each as a 2 px coloured line over a 4 px black line (scaled to the canvas size; the Python version draws at 448 px).
 * Up-sampling is bilinear (cv2.INTER_LINEAR with half-pixel centres), the quantile uses numpy's default linear
 * interpolation, the iso-lines are traced with marching squares on the up-sampled grid. Lines only, no fill.
 * Pure: needs a 16x16 map (array of rows) and a CanvasRenderingContext2D. No model code, no DOM lookups.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.EvidenceOverlay = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  function upsample(map, W, H) {
    const h = map.length, w = map[0].length, out = new Float32Array(W * H);
    const sx = w / W, sy = h / H;
    for (let y = 0; y < H; y++) {
      let fy = (y + 0.5) * sy - 0.5; fy = Math.max(0, Math.min(h - 1, fy));
      const y0 = Math.floor(fy), y1 = Math.min(h - 1, y0 + 1), wy = fy - y0;
      for (let x = 0; x < W; x++) {
        let fx = (x + 0.5) * sx - 0.5; fx = Math.max(0, Math.min(w - 1, fx));
        const x0 = Math.floor(fx), x1 = Math.min(w - 1, x0 + 1), wx = fx - x0;
        out[y * W + x] = (1 - wy) * ((1 - wx) * map[y0][x0] + wx * map[y0][x1]) + wy * ((1 - wx) * map[y1][x0] + wx * map[y1][x1]);
      }
    }
    return out;
  }

  function quantile(arr, q) {  // numpy default: linear interpolation between order statistics
    const s = Float32Array.from(arr).sort(), pos = (s.length - 1) * q, lo = Math.floor(pos), hi = Math.min(s.length - 1, lo + 1);
    return s[lo] + (s[hi] - s[lo]) * (pos - lo);
  }

  /** Marching squares: segments of the iso-line {v >= thr} on a WxH grid, in pixel coordinates (cell centres). */
  function isoSegments(v, W, H, thr) {
    const segs = [];
    const at = (x, y) => v[y * W + x] >= thr ? 1 : 0;
    const lerp = (a, b, va, vb) => a + (thr - va) / ((vb - va) || 1e-9) * (b - a);
    for (let y = 0; y < H - 1; y++) for (let x = 0; x < W - 1; x++) {
      const c = (at(x, y) << 3) | (at(x + 1, y) << 2) | (at(x + 1, y + 1) << 1) | at(x, y + 1);
      if (c === 0 || c === 15) continue;
      const tl = v[y * W + x], tr = v[y * W + x + 1], br = v[(y + 1) * W + x + 1], bl = v[(y + 1) * W + x];
      const top = [lerp(x, x + 1, tl, tr) + 0.5, y + 0.5], right = [x + 1.5, lerp(y, y + 1, tr, br) + 0.5];
      const bottom = [lerp(x, x + 1, bl, br) + 0.5, y + 1.5], left = [x + 0.5, lerp(y, y + 1, tl, bl) + 0.5];
      const T = { 1: [left, bottom], 2: [bottom, right], 3: [left, right], 4: [top, right], 5: [top, left, bottom, right], 6: [top, bottom], 7: [top, left],
                  8: [top, left], 9: [top, bottom], 10: [top, right, bottom, left], 11: [top, right], 12: [left, right], 13: [bottom, right], 14: [left, bottom] }[c];
      for (let i = 0; i < T.length; i += 2) segs.push([T[i], T[i + 1]]);
    }
    return segs;
  }

  function strokeSegs(ctx, segs, colour, width) {
    ctx.save(); ctx.strokeStyle = colour; ctx.lineWidth = width; ctx.lineCap = "round"; ctx.beginPath();
    for (const [a, b] of segs) { ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); }
    ctx.stroke(); ctx.restore();
  }

  /** Draw the two iso-lines on ctx over a W x H canvas. Returns {thrTop12, n05, nTop12} for the caption. */
  function drawContours(ctx, map16, W, H) {
    const up = upsample(map16, W, H), scale = W / 448;
    const thrTop = quantile(up, 0.88);
    const layers = [[thrTop, "rgb(255,220,0)"], [0.5, "rgb(0,230,255)"]];  // same order as the Python overlay
    const counts = [];
    for (const [thr, col] of layers) {
      const segs = isoSegments(up, W, H, thr); counts.push(segs.length);
      strokeSegs(ctx, segs, "rgb(0,0,0)", 4 * scale); strokeSegs(ctx, segs, col, 2 * scale);
    }
    return { thrTop12: thrTop, nTop12: counts[0], n05: counts[1] };
  }

  return { upsample, quantile, isoSegments, drawContours };
});
