/* The film. Every element's state is a pure function of the time t (seconds): window.seek(t) sets it, so a renderer can
   step through the frames deterministically. Scenes are bound to the narration beats of cues.js (B.<id>.start / .voice /
   .end); in-scene animations are timed from the moment the voice of the beat starts (v = B.<id>.voice).
   Numbers: docs/capstone/report_v3/report.tex and its SOURCES.md. */
(() => {
const CU = window.CUES.cues, TOTAL = window.CUES.total, B = {}; CU.forEach(c => { B[c.id] = c; });
const F = "../report_v3/figs/", A = "../../meeting_20261103/assets/";
const stage = document.getElementById("stage"), scenes = [], tweens = [];
const C = { ink: "#1f2937", muted: "#6b7280", blue: "#0f4d92", red: "#d55e00", green: "#009e73", amber: "#c98a00", purple: "#7b3fa0", grey: "#9aa3ae", cyan: "#26a6dc", pink: "#cc79a7" };
const E = { out: p => 1 - Math.pow(1 - p, 3), io: p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2, lin: p => p,
            back: p => { const c = 1.4; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); } };
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));

function el(parent, tag, cls, style, html) {
  const e = document.createElement(tag); if (cls) e.className = cls; if (style) e.style.cssText = style; if (html != null) e.innerHTML = html;
  parent.appendChild(e); return e;
}
const abs = (p, x, y, w, h, html, cls, style) => el(p, "div", "abs " + (cls || ""), `left:${x}px;top:${y}px;${w != null ? `width:${w}px;` : ""}${h != null ? `height:${h}px;` : ""}${style || ""}`, html);
function img(p, src, x, y, w, h, style) { const e = el(p, "img", "tile", `left:${x}px;top:${y}px;width:${w}px;height:${h}px;${style || ""}`); e.src = src; return e; }
function tw(t0, dur, fn, ease) { tweens.push({ t0, t1: t0 + dur, fn, ease: E[ease || "out"] }); }
function fade(e, t0, dur, dy, dx) { dur = dur || 0.6; dy = dy == null ? 26 : dy; dx = dx || 0; e.style.opacity = 0;
  tw(t0, dur, p => { e.style.opacity = p; e.style.transform = `translate(${dx * (1 - p)}px, ${dy * (1 - p)}px)`; }); return e; }
function pop(e, t0, dur) { dur = dur || 0.55; e.style.opacity = 0;
  tw(t0, dur, p => { e.style.opacity = clamp(p * 1.6, 0, 1); e.style.transform = `scale(${0.82 + 0.18 * p})`; }, "back"); return e; }
function count(e, t0, dur, a, b, fmt) { tw(t0, dur, p => { e.textContent = fmt(a + (b - a) * p); }); return e; }
function grow(e, t0, dur, prop, a, b, unit) { tw(t0, dur, p => { e.style[prop] = (a + (b - a) * p) + (unit || "px"); }); return e; }
function scene(id, beats) {
  const e = el(stage, "div", "scene"); e.id = "s-" + id;
  const s = { el: e, start: B[beats[0]].start, end: B[beats[beats.length - 1]].end }; scenes.push(s);
  tw(s.start, 0.5, p => { e.style.opacity = p; }); tw(s.end - 0.4, 0.4, p => { e.style.opacity = 1 - p; }, "lin");
  return e;
}
function head(sc, tag, title, t0) {
  fade(el(sc, "div", "tag", null, "[" + tag + "]"), t0, 0.5, 0, -20); fade(el(sc, "div", "title", null, title), t0 + 0.1, 0.6, 0, -24);
  el(sc, "div", "sq", "left:1860px;top:50px"); el(sc, "div", "sq", "left:46px;top:1010px");
  el(sc, "div", "abs", "left:90px;top:176px;width:1740px;height:2px;background:#1f2937;opacity:.85");
}
const card = (sc, x, y, w, h, html, extra) => abs(sc, x, y, w, h, html, "card " + (extra || ""));
function stat(sc, x, y, w, big, lab, color, t0, size) {
  const e = abs(sc, x, y, w, null, null, "stat");
  el(e, "div", "big", `color:${color || C.blue};font-size:${size || 84}px`, big); el(e, "div", "lab", null, lab); return fade(e, t0, 0.6, 22);
}
function arrow(sc, x, y, len, t0, vertical) {
  const e = abs(sc, x, y, vertical ? 4 : len, vertical ? len : 4, null, "arrow" + (vertical ? " v" : "")); e.style.transformOrigin = "0 0";
  e.style.opacity = 0; tw(t0, 0.45, p => { e.style.opacity = 1; e.style.transform = vertical ? `scaleY(${p})` : `scaleX(${p})`; }); return e;
}
const pill = (cls, text) => `<span class="pill ${cls}">${text}</span>`;

// ============================================================================ title
{
  const sc = scene("title", ["t1"]), t = B.t1.start;
  fade(abs(sc, -320, 110, 1420, 860, null, null, "border-radius:430px;background:#e8eef7"), t, 0.9, 0, -40);
  el(sc, "div", "sq", "left:1480px;top:110px"); el(sc, "div", "sq", "left:80px;top:1000px");
  fade(abs(sc, 140, 300, 1120, null, "Beautified Is Not Forged", "serif b", "font-size:92px;line-height:1.05;white-space:nowrap"), t + 0.3, 0.8, 30);
  fade(abs(sc, 140, 440, 1000, null, "A face detector that tells beautification from forgery, with checkable evidence", "serif muted", "font-size:40px;line-height:1.25"), t + 1.0, 0.7);
  fade(abs(sc, 140, 640, 1000, null, "NTHU CS Capstone Project &middot; 2026", null, "font-size:31px"), t + 1.6, 0.6);
  fade(abs(sc, 140, 690, 1000, null, "林沁瑩　陳柏融　游宸山", null, "font-size:31px;font-family:var(--cjk)"), t + 1.9, 0.6);
  [["teaser_orig", "p-real", "genuine", 1250, 250], ["teaser_smooth", "p-beau", "beautified", 1560, 250],
   ["teaser_swap", "p-fake", "forged", 1250, 570], ["teaser_swap_beauty", "p-fake", "forged + beautified", 1560, 570]].forEach(([f, cls, lab, x, y], i) => {
    pop(img(sc, F + f + ".png", x, y, 270, 270), t + 2.2 + i * 0.35);
    fade(abs(sc, x - 20, y + 282, 310, null, pill(cls, lab), "lbl"), t + 2.5 + i * 0.35, 0.4, 10);
  });
}

// ============================================================================ background
{
  const sc = scene("bg", ["b1"]), v = B.b1.voice; head(sc, "Background", "Where forgery detectors are used, and what arrives there", B.b1.start);
  [["Content moderation", "platforms screen the faces that users upload"], ["Remote identity verification", "a selfie is matched against an ID document"],
   ["Fact-checking", "a viral photo is checked before it spreads"]].forEach(([h, p], i) =>
    fade(card(sc, 90 + i * 590, 215, 560, 180, `<h3>${h}</h3><p class="muted">${p}</p>`), v + 0.2 + i * 1.1));
  pop(img(sc, F + "teaser_orig.png", 560, 470, 300, 300), v + 5.2); fade(abs(sc, 520, 785, 380, null, "a genuine photo", "lbl muted"), v + 5.3, 0.4, 8);
  arrow(sc, 900, 618, 150, v + 5.8); fade(abs(sc, 870, 560, 210, null, "beauty app", "lbl b"), v + 5.9, 0.4, 8);
  pop(img(sc, F + "teaser_smooth.png", 1090, 470, 300, 300), v + 6.3); fade(abs(sc, 1050, 785, 380, null, "the same photo, smoothed", "lbl muted"), v + 6.4, 0.4, 8);
  fade(abs(sc, 90, 860, 1740, null, "Photos are often beautified before they are uploaded.", "b", "font-size:40px;text-align:center"), v + 7.0, 0.6);
}

// ============================================================================ teaser: two errors
{
  const sc = scene("teaser", ["b2", "b3"]); head(sc, "Problem", "One edit, two errors: a beautified face is neither real nor fake", B.b2.start);
  const A_ = [["Effort", .11, .72, .66], ["Forensics Ad.", .17, .95, .59], ["GenD", .19, .97, .84], ["DFD-HR", .27, .94, .54]];
  const B_ = [["Effort", .97, .44, .81], ["Forensics Ad.", 1.00, .67, .85], ["GenD", .89, .70, .86], ["DFD-HR", .99, .74, .63]];
  function panel(x, t0, headTxt, headCls, imgA, imgB, truth, arrowTxt, rows, verdictPill) {
    const p = card(sc, x, 200, 870, 720, ""); fade(p, t0 - 0.4, 0.6);
    abs(p, 30, 22, 810, null, `<span class="chip ${headCls}">${headTxt}</span>`);
    img(p, F + imgA + ".png", 60, 90, 210, 210); img(p, F + imgB + ".png", 380, 90, 210, 210);
    abs(p, 275, 150, 100, null, '<div class="arrow" style="left:10px;top:38px;width:80px"></div>');
    abs(p, 245, 224, 160, null, arrowTxt, "lbl muted", "font-size:21px;line-height:1.15");
    abs(p, 40, 310, 250, null, "true class " + truth, "lbl", "font-size:23px"); abs(p, 360, 310, 250, null, "after the edit", "lbl muted", "font-size:23px");
    abs(p, 620, 100, 230, null, "scores before &rarr; after<br><span class='muted' style='font-size:21px'>tick: threshold at 5% false alarms</span>", null, "font-size:23px;line-height:1.2");
    rows.forEach(([name, a, b, thr], i) => {
      const y = 365 + i * 72, L = 240, W = 300;
      abs(p, 30, y + 2, 200, null, name, null, "font-size:25px;text-align:right");
      const trk = abs(p, L, y, W, 34, null, "track"); const fill = el(trk, "div", "bar", `left:0;top:0;width:0;background:${a > thr ? C.red : C.green}`);
      el(trk, "div", "tick", `left:${thr * W - 2}px;top:-7px`);
      const val = abs(p, L + W + 18, y, 260, null, "", "b", `font-size:25px;color:${a > thr ? C.red : C.green}`);
      const t1 = t0 + 1.2 + i * 0.25, t2 = t0 + 4.2 + i * 0.35;
      tw(t1, 0.6, q => { fill.style.width = (a * W * q) + "px"; val.textContent = (a * q).toFixed(2) + " " + (a > thr ? "forged" : "genuine"); val.style.opacity = q > 0 ? 1 : 0; });
      tw(t2, 0.9, q => { const s = a + (b - a) * q, f = s > thr; fill.style.width = (s * W) + "px"; fill.style.background = f ? C.red : C.green;
        val.style.color = f ? C.red : C.green; val.textContent = s.toFixed(2) + " " + (f ? "forged" : "genuine"); }, "io");
    });
    fade(abs(p, 30, 655, 810, null, verdictPill, null, "font-size:27px"), t0 + 6.2, 0.5, 14);
  }
  panel(90, B.b2.voice, "(a) Genuine photo, accused after smoothing", "p-fake", "teaser_orig", "teaser_smooth", pill("p-real", "genuine"), "retouching service<br>Smoothing-90", A_,
        pill("p-fake", "False alarm") + "&nbsp; four detectors flip from genuine to forged");
  panel(960, B.b3.voice, "(b) Deepfake, missed after a beauty preset", "p-beau", "teaser_swap", "teaser_swap_beauty", pill("p-fake", "forged"), "app beauty<br>preset", B_,
        pill("p-beau", "Miss") + "&nbsp; three of the four let the face swap through");
}

// ============================================================================ audit: 17 published detectors
{
  const sc = scene("audit", ["b4"]), v = B.b4.voice; head(sc, "Audit &middot; 17 published detectors, official weights", "Smoothed genuine faces called forged", B.b4.start);
  // accused (%) at 5% FPR on untouched originals (report, Table: audit); red = 36% or more (13 of 17)
  const D = [["GenD", 68.7], ["DFD-HR", 64.9], ["SRM", 62.8], ["CORE", 54.8], ["Xception", 51.6], ["SPSL", 51.2], ["F3Net", 50.6], ["Effort", 43.2], ["UCF", 41.4],
             ["Forensics Ad.", 39.7], ["SBI", 37.3], ["RECCE", 36.8], ["EfficientNet-B4", 36.3], ["LAA-Net", 17.2], ["UnivFD", 16.6], ["CADDM", 6.3], ["NPR", 0.0]];
  const cols = 6, cw = 196, ch = 196, x0 = 90, y0 = 205;
  D.forEach(([n, a], i) => {
    const x = x0 + (i % cols) * cw, y = y0 + Math.floor(i / cols) * ch, hot = a >= 36, col = hot ? C.red : C.grey;
    const c = card(sc, x, y, cw - 14, ch - 14, "", ""); c.style.padding = "14px 16px"; pop(c, v + 0.5 + i * 0.22, 0.4);
    abs(c, 0, 0, cw - 46, null, n, "b", `font-size:${n.length > 10 ? 20 : 23}px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis`);
    const trk = abs(c, 0, 44, cw - 46, 70, null, "track", "height:70px;border-radius:10px;background:#eceff3");
    const f = el(trk, "div", "bar", `left:0;bottom:0;top:auto;width:${cw - 46}px;height:0;border-radius:0 0 10px 10px;background:${col}`);
    const vt = abs(c, 0, 124, cw - 46, null, "", "b", `font-size:30px;color:${col};line-height:1`);
    tw(v + 0.9 + i * 0.22, 0.7, p => { f.style.height = (a / 70 * 70 * p) + "px"; vt.textContent = (a * p).toFixed(1) + "%"; });
    abs(c, 0, 150, cw - 46, null, hot ? "accused" : "", "muted", "font-size:18px;line-height:1");
  });
  // ours, after the published ones
  { const x = x0 + 5 * cw, y = y0 + 2 * ch, c = card(sc, x, y, cw - 14, ch - 14, "", ""); c.style.padding = "14px 16px"; c.style.borderColor = C.blue; c.style.borderWidth = "3px"; pop(c, v + 9.4, 0.5);
    abs(c, 0, 0, cw - 46, null, "Ours", "b", `font-size:23px;color:${C.blue}`);
    const trk = abs(c, 0, 44, cw - 46, 70, null, "track", "height:70px;border-radius:10px;background:#eceff3");
    const f = el(trk, "div", "bar", `left:0;bottom:0;top:auto;width:${cw - 46}px;height:0;border-radius:0 0 10px 10px;background:${C.blue}`);
    const vt = abs(c, 0, 124, cw - 46, null, "", "b", `font-size:30px;color:${C.blue};line-height:1`);
    tw(v + 9.8, 0.7, p => { f.style.height = (8.6 * p) + "px"; vt.textContent = (8.6 * p).toFixed(1) + "%"; });
    abs(c, 0, 150, cw - 46, null, "three-way", "muted", `font-size:18px;line-height:1;color:${C.blue}`); }
  fade(abs(sc, 90, 800, 1160, null, `bars: share of commercially smoothed genuine faces called forged, threshold set at 5% false alarms on the untouched originals &middot; <span style="color:${C.red};font-weight:700">red: 36&ndash;69%, 13 of 17</span>`, "muted", "font-size:22px;line-height:1.3"), v + 4.0, 0.5);
  stat(sc, 1300, 215, 540, "16 / 17", "score the smoothed genuine face as more forged than its own untouched original", C.red, v + 2.6, 84);
  fade(abs(sc, 1300, 470, 540, null, "<b>Why</b>A real / fake detector has no &ldquo;beautified&rdquo; answer. A beautified genuine face is neither, and it has to go somewhere.",
       "callout", `background:var(--red-bg);color:${C.red}`), v + 8.0, 0.6);
  fade(abs(sc, 1300, 700, 540, null, pill("p-real", "real") + " &nbsp;" + pill("p-fake", "fake") + " &nbsp;<span class='muted'>&larr; the only two answers</span>", null, "font-size:28px"), v + 8.6, 0.5, 10);
}

// ============================================================================ the idea
{
  const sc = scene("idea", ["b5"]), v = B.b5.voice; head(sc, "Our idea", "A third answer, and evidence that can be checked", B.b5.start);
  [["teaser_orig", "p-real", "real", "the capture as recorded"], ["teaser_swap", "p-fake", "forged", "a person or action that was never captured"],
   ["teaser_smooth", "p-beau", "beautified", "the same person, only the look of the face edited"]].forEach(([f, cls, lab, def], i) => {
    const x = 90 + i * 390; pop(img(sc, F + f + ".png", x, 225, 340, 340), v + 0.3 + i * 0.5);
    fade(abs(sc, x - 20, 585, 380, null, pill(cls, lab), "lbl", "font-size:34px"), v + 0.5 + i * 0.5, 0.4, 10);
    fade(abs(sc, x - 20, 650, 380, null, def, "lbl muted", "font-size:23px"), v + 0.7 + i * 0.5, 0.4, 8);
  });
  fade(abs(sc, 1300, 300, 4, 420, null, null, "background:#d6dbe3"), v + 2.2, 0.4, 0);
  pop(img(sc, F + "ev0_ours.png", 1400, 225, 340, 340), v + 2.6);
  fade(abs(sc, 1370, 585, 400, null, pill("p-blue", "evidence"), "lbl", "font-size:34px"), v + 2.8, 0.4, 10);
  fade(abs(sc, 1370, 650, 400, null, "where the decision comes from, tested against the true edit", "lbl muted", "font-size:23px"), v + 3.0, 0.4, 8);
  fade(abs(sc, 90, 790, 1740, null, "<b>Three answers instead of two</b>real &middot; forged &middot; beautified, plus an evidence map and sentences written by code and checked before they are shown.", "callout", `background:var(--blue-bg);color:${C.blue}`), v + 4.2, 0.6);
}

// ============================================================================ cause: training exposure
{
  const sc = scene("cause", ["m1"]), v = B.m1.voice; head(sc, "Method &middot; cause", "Which class saw smoothing in training decides the error", B.m1.start);
  const ARMS = [["P0", "no class", 54.2, -16.0, C.grey], ["P3", "forged class only", 63.8, -38.5, C.red], ["P1", "genuine class only", 3.7, 51.2, C.amber], ["P2", "both classes", 11.7, -26.5, C.green]];
  const TT = [1.6, 4.6, 8.0, 12.6];
  const pa = card(sc, 90, 200, 860, 580, `<h3>Smoothed genuine faces accused at 5% FPR (%)</h3>`), pb = card(sc, 970, 200, 860, 580, `<h3>Smoothed forgeries: miss rise (points)</h3>`);
  fade(pa, B.m1.start + 0.3); fade(pb, B.m1.start + 0.5);
  abs(pa, 30, 70, 800, null, "same model, same data, same recipe; only which class saw smoothing changes", "muted", "font-size:22px");
  ARMS.forEach(([k, who, acc, miss, col], i) => {
    const x = 70 + i * 200;
    // panel a: bars up from the baseline y = 440, 4 px per point
    const ba = el(pa, "div", "bar", `left:${x}px;top:440px;width:120px;height:0;background:${col};border-radius:8px 8px 0 0`);
    const va = abs(pa, x - 20, 420, 160, null, "", "b", `text-align:center;font-size:27px;color:${col}`);
    tw(v + TT[i], 0.8, p => { const h = acc * 4.6 * p; ba.style.height = h + "px"; ba.style.top = (440 - h) + "px"; va.style.top = (440 - h - 40) + "px"; va.textContent = (acc * p).toFixed(1); va.style.opacity = p > 0 ? 1 : 0; });
    abs(pa, x - 20, 452, 160, null, `<b class="serif" style="font-size:32px;color:${col}">${k}</b><br><span class="muted" style="font-size:21px">${who}</span>`, null, "text-align:center;line-height:1.15");
    // panel b: zero line at y = 300, 2.6 px per point
    const z = 300, bb = el(pb, "div", "bar", `left:${x}px;top:${z}px;width:120px;height:0;background:${col}`);
    const vb = abs(pb, x - 20, z, 160, null, "", "b", `text-align:center;font-size:27px;color:${col}`);
    tw(v + TT[i], 0.8, p => { const h = Math.abs(miss) * 2.6 * p; bb.style.height = h + "px"; bb.style.top = (miss > 0 ? z - h : z) + "px";
      vb.style.top = (miss > 0 ? z - h - 40 : z + h + 4) + "px"; vb.textContent = (miss > 0 ? "+" : "") + (miss * p).toFixed(1); vb.style.opacity = p > 0 ? 1 : 0; });
    abs(pb, x - 20, 452, 160, null, `<b class="serif" style="font-size:32px;color:${col}">${k}</b><br><span class="muted" style="font-size:21px">${who}</span>`, null, "text-align:center;line-height:1.15");
  });
  el(pa, "div", "abs", "left:30px;top:440px;width:800px;height:2px;background:#9aa3ae"); el(pb, "div", "abs", "left:30px;top:300px;width:800px;height:2px;background:#9aa3ae");
  abs(pb, 640, 268, 200, null, "no change", "muted", "font-size:20px;text-align:right");
  fade(abs(sc, 90, 810, 1740, null, "<b>Finding</b>Architecture, data and recipe fixed: which class saw smoothing decides the false alarms. The fix is the training recipe.", "callout", `background:var(--green-bg);color:${C.green}`), v + 15.5);
}

// ============================================================================ data engine
{
  const sc = scene("engine", ["m2"]), v = B.m2.voice; head(sc, "Method &middot; data engine", "A commercial render, split into single operations with exact footprints", B.m2.start);
  const T = (f, x, y, w, h, lab, t0, labCls) => { pop(img(sc, F + f + ".png", x, y, w, h), t0); fade(abs(sc, x - 40, y + h + 8, w + 80, null, lab, "lbl " + (labCls || ""), "font-size:22px"), t0 + 0.1, 0.4, 8); };
  T("method_vendor_O", 90, 230, 200, 240, "original <b>O</b>", v + 0.3); T("method_vendor_R", 90, 580, 200, 240, "render <b>R</b><br><span class='muted'>4 operations at once</span>", v + 0.9);
  arrow(sc, 310, 350, 90, v + 2.6); arrow(sc, 310, 700, 90, v + 5.6);
  T("engine_flow", 420, 230, 200, 240, "optical flow <b>f</b>", v + 2.8); T("engine_resid", 420, 580, 200, 240, "residual <b>P</b> = R &minus; O(x+f)", v + 5.8);
  arrow(sc, 640, 350, 90, v + 3.8); arrow(sc, 640, 700, 90, v + 6.8);
  T("method_comp_eye", 750, 230, 170, 204, "<b>eye</b>: O(x + m<sub>e</sub>&middot;f)", v + 4.0); T("method_comp_contour", 950, 230, 170, 204, "<b>contour</b>: O(x + (1&minus;m<sub>e</sub>)&middot;f)", v + 4.4);
  T("method_comp_tone", 750, 580, 170, 204, "<b>tone</b>: low-pass of P", v + 7.0); T("method_comp_texture", 950, 580, 170, 204, "<b>texture</b>: the rest of P", v + 7.4);
  fade(abs(sc, 740, 505, 400, null, "footprint M of each component outlined in <span style='color:" + C.cyan + ";font-weight:700'>cyan</span>", "lbl muted", "font-size:21px"), v + 8.2, 0.5, 8);
  const k = card(sc, 1230, 215, 600, 300, "<h3>Exact</h3><p>Every component has a pixel-aligned original, so its footprint M = |C &minus; O| &gt; 6, dilated, is known.</p>"); fade(k, v + 1.5);
  const d = stat(sc, 1260, 540, 560, "108.1 dB", "reconstruction of the render from its four components", C.blue, v + 9.6, 70);
  const n = stat(sc, 1260, 740, 560, "18,734 &rarr; 50,112", "Tencent and Megvii renders &rarr; single-operation items; Alibaba is never decomposed, test only", C.blue, v + 13.0, 58);
}

// ============================================================================ model
{
  const sc = scene("model", ["m3"]), v = B.m3.voice; head(sc, "Method &middot; model", "CLIP ViT-L/14 with LoRA; the evidence head learns the exact footprint", B.m3.start);
  pop(img(sc, F + "model_in.png", 90, 330, 240, 240), v + 0.2); fade(abs(sc, 50, 580, 320, null, "input 224&times;224<br><span class='muted'>256 patches + CLS</span>", "lbl", "font-size:22px"), v + 0.3, 0.4, 8);
  arrow(sc, 350, 448, 60, v + 0.9);
  const bb = card(sc, 430, 215, 420, 600, `<h3>CLIP ViT-L/14 image encoder</h3><p class="muted" style="font-size:22px">24 transformer blocks &middot; <b>frozen</b> 303.2 M</p>`); fade(bb, v + 1.0);
  for (let i = 0; i < 24; i++) { el(bb, "div", "abs", `left:30px;top:${100 + i * 17}px;width:360px;height:11px;border-radius:4px;background:#e3e7ec`);
    const lo = el(bb, "div", "abs", `left:300px;top:${100 + i * 17}px;width:90px;height:11px;border-radius:4px;background:${C.blue};opacity:0`); tw(v + 2.6 + i * 0.03, 0.3, p => { lo.style.opacity = p; }); }
  fade(abs(bb, 30, 520, 360, null, pill("p-blue", "LoRA r = 16 on q, k, v, o") + "<br><span class='muted' style='font-size:21px'>96 adapters, trained</span>", null, "font-size:23px;line-height:1.5"), v + 2.8, 0.5, 8);
  const heads = [["classification head", "real / forged / beautified", 4.6], ["operation head", "eye &middot; contour &middot; tone &middot; texture", 5.6], ["quantity head", "four measured amounts, auxiliary", 6.4],
                 ["evidence head", "one score per patch token &rarr; 16&times;16 map", 7.2]];
  heads.forEach(([h, p, t], i) => { arrow(sc, 870, 262 + i * 140, 50, v + t - 0.3); fade(card(sc, 940, 220 + i * 140, 520, 112, `<h3 style="font-size:27px">${h}</h3><p class="muted" style="font-size:22px">${p}</p>`), v + t); });
  pop(img(sc, F + "model_ev16.png", 1520, 230, 150, 150), v + 8.6); fade(abs(sc, 1490, 388, 210, null, "evidence 16&times;16", "lbl", "font-size:21px"), v + 8.7, 0.4, 8);
  fade(abs(sc, 1675, 290, 60, null, "vs", "lbl b muted", "font-size:24px"), v + 9.4, 0.4, 8);
  pop(img(sc, F + "model_M16.png", 1720, 230, 150, 150), v + 9.6); fade(abs(sc, 1690, 388, 210, null, "footprint M", "lbl", `font-size:21px;color:${C.cyan};font-weight:700`), v + 9.7, 0.4, 8);
  fade(abs(sc, 1500, 450, 380, null, "trained with BCE + Dice against M; the classifier never reads this map", "muted", "font-size:21px;line-height:1.25"), v + 10.2, 0.5, 8);
  fade(abs(sc, 940, 790, 890, null, "<b>3.16 M trained parameters</b>P(forged) = &sigma;(f): the forgery score never reads the beauty score b", "callout", `background:var(--blue-bg);color:${C.blue}`), v + 12.6);
}

// ============================================================================ sentences by code
{
  const sc = scene("explain", ["m4"]), v = B.m4.voice; head(sc, "Method &middot; sentences", "Code writes every sentence, and a checker tests it before it is shown", B.m4.start);
  const e = el(sc, "img", "", "position:absolute;left:260px;top:200px;width:1400px;transform-origin:50% 50%;border-radius:12px"); e.src = A + "explain.png";
  fade(e, B.m4.start + 0.4, 0.7, 10); tw(B.m4.start + 1.2, B.m4.end - B.m4.start - 1.2, p => { e.style.transform = `scale(${1 + 0.03 * p})`; }, "lin");
}

// ============================================================================ three-class results
{
  const sc = scene("three", ["r1"]), v = B.r1.voice; head(sc, "Results &middot; three-class", "FF++ test, 7,936 unseen frames: 82.7 / 90.9 / 86.7% recall", B.r1.start);
  const M = [[1088, 78, 150], [352, 4819, 133], [118, 57, 1141]], L = ["real", "forged", "beautified"], S = 200, x0 = 360, y0 = 300;
  fade(abs(sc, x0, y0 - 80, S * 3, null, "predicted", "lbl muted", "font-size:24px;font-style:italic"), v, 0.4);
  L.forEach((l, j) => { fade(abs(sc, x0 + j * S, y0 - 42, S, null, l, "lbl b"), v + 0.2 + j * 0.1, 0.4); fade(abs(sc, x0 - 230, y0 + j * S + S / 2 - 18, 210, null, l, "b", "text-align:right;font-size:26px"), v + 0.2 + j * 0.1, 0.4); });
  fade(abs(sc, x0 - 330, y0 + S * 1.5 - 18, 90, null, "true", "lbl muted", "font-size:24px;font-style:italic"), v, 0.4);
  M.forEach((row, i) => { const tot = row.reduce((a, b) => a + b, 0); row.forEach((n, j) => { const s = n / tot, a = 0.1 + 0.9 * s;
    const bg = `rgb(${Math.round(244 + (15 - 244) * a)},${Math.round(246 + (77 - 246) * a)},${Math.round(249 + (146 - 249) * a)})`;
    const c = abs(sc, x0 + j * S, y0 + i * S, S - 8, S - 8, "", "cell", `background:${bg};color:${s > 0.45 ? "#fff" : C.ink};font-size:40px`);
    const big = el(c, "div"), sm = el(c, "small"); pop(c, v + 0.8 + (i * 3 + j) * 0.12);
    count(big, v + 0.9 + (i * 3 + j) * 0.12, 0.9, 0, 100 * s, x => x.toFixed(1) + "%"); count(sm, v + 0.9 + (i * 3 + j) * 0.12, 0.9, 0, n, x => "(" + Math.round(x).toLocaleString() + ")"); }); });
  fade(abs(sc, 1100, 215, 720, null, "Face-swap methods called forged (%)", "b", `font-size:28px;color:${C.blue}`), v + 4.0, 0.5);
  [["Deepfakes", 98.64, C.red], ["FaceSwap", 96.22, C.red], ["Face2Face", 93.51, C.red], ["NeuralTextures", 75.08, C.amber]].forEach(([n, val, col], i) => {
    const y = 275 + i * 62; abs(sc, 1100, y, 220, null, n, null, "font-size:25px"); const trk = abs(sc, 1330, y + 2, 400, 34, null, "track");
    const f = el(trk, "div", "bar", `left:0;top:0;width:0;background:${col}`); const t = abs(sc, 1745, y, 100, null, "", "b", `font-size:25px;color:${col}`);
    tw(v + 4.4 + i * 0.35, 0.8, p => { f.style.width = (val * 4 * p) + "px"; t.textContent = (val * p).toFixed(1); t.style.opacity = p > 0 ? 1 : 0; }); });
  stat(sc, 1100, 560, 720, "4.3%", "of beautified frames are called forged; the largest error is real &rarr; beautified (11.4%)", C.green, v + 9.0, 72);
}

// ============================================================================ unseen service and filter types
{
  const sc = scene("unseen", ["r2"]), v = B.r2.voice; head(sc, "Results &middot; unseen service and filters", "Alibaba, a retouching service never used in training", B.r2.start);
  const pa = card(sc, 90, 200, 900, 350, `<h3>Called beautified at strength 90 (%)</h3><p class="muted" style="font-size:21px">2,210 pairs of FFHQ originals and Alibaba renders per operation</p>`); fade(pa, B.r2.start + 0.3);
  [["Skin smoothing", 98.8], ["Whitening", 72.3], ["Eye enlarging", 69.7], ["Face slimming", 61.3]].forEach(([n, val], i) => {
    const y = 120 + i * 54; abs(pa, 30, y, 230, null, n, null, "font-size:25px"); const trk = abs(pa, 270, y + 2, 480, 34, null, "track");
    const f = el(trk, "div", "bar", `left:0;top:0;width:0;background:${C.amber}`); const t = abs(pa, 765, y, 100, null, "", "b", `font-size:25px;color:${C.amber}`);
    tw(v + 0.8 + i * 0.35, 0.8, p => { f.style.width = (val * 4.8 * p) + "px"; t.textContent = (val * p).toFixed(1); t.style.opacity = p > 0 ? 1 : 0; }); });
  stat(sc, 120, 600, 400, "&le; 0.8%", "called forged, any operation, any strength", C.green, v + 4.6, 72);
  stat(sc, 560, 600, 420, "84&ndash;99%", "of pairs: the render scores above its own original", C.blue, v + 7.0, 72);
  const pb = card(sc, 1020, 200, 810, 720, `<h3>14 Instagram-style filters on FF++ test videos</h3><p class="muted" style="font-size:21px">called beautified (%), none called forged above 10.7%</p>`); fade(pb, v + 8.0);
  const FL = [["brannan", 100.0], ["toaster", 97.96], ["valencia", 97.1], ["nashville", 96.92], ["hudson", 96.55], ["xpro2", 96.3], ["walden", 95.65], ["rise", 95.35], ["gingham", 94.44], ["stinson", 93.75], ["willow", 91.49], ["lark", 87.72], ["aden", 86.67], ["maven", 86.05]];
  FL.forEach(([n, val], i) => { const y = 112 + i * 42; abs(pb, 30, y, 130, null, n, null, "font-size:22px"); const trk = abs(pb, 170, y + 3, 500, 26, null, "track", "height:26px");
    const f = el(trk, "div", "bar", `left:0;top:0;width:0;height:26px;background:${C.purple}`); const t = abs(pb, 685, y, 100, null, "", "b", `font-size:22px;color:${C.purple}`);
    tw(v + 8.6 + i * 0.12, 0.7, p => { f.style.width = (val * 5 * p) + "px"; t.textContent = (val * p).toFixed(1); t.style.opacity = p > 0 ? 1 : 0; }); });
}

// ============================================================================ fair cross-dataset comparison
{
  const sc = scene("fair", ["r3"]), v = B.r3.voice; head(sc, "Results &middot; cross-dataset, same training data", "AUC after beautification or filtering, with the same training data", B.r3.start);
  const G = [["Celeb-DF-B", "4 app beauty presets", 0.872, 0.838, "DFD-HR", 1.6], ["Celeb-DF-v2", "11 held-out filters", 0.851, 0.856, "GenD", 6.0], ["DFD", "16 fresh filters", 0.932, 0.928, "DFD-HR", 8.4]];
  const base = 760, H = 440, lo = 0.80, hi = 0.95, hpx = x => (x - lo) / (hi - lo) * H;
  G.forEach(([ds, src, ours, best, who, t], i) => {
    const x = 150 + i * 580; fade(abs(sc, x - 30, 215, 560, null, `<b style="font-size:30px">${ds}</b><br><span class="muted">${src}</span>`, null, "text-align:center;font-size:24px"), v + t - 0.6, 0.5);
    [[ours, C.blue, "Ours, FF++ only", 0], [best, C.grey, "best published: " + who, 1]].forEach(([val, col, lab, k]) => {
      const bx = x + 40 + k * 240, b = el(sc, "div", "bar", `left:${bx}px;top:${base}px;width:180px;height:0;background:${col};border-radius:10px 10px 0 0`);
      const vt = abs(sc, bx - 20, base, 220, null, "", "b serif", `text-align:center;font-size:40px;color:${col}`);
      tw(v + t + k * 0.5, 0.9, p => { const h = hpx(val) * p; b.style.height = h + "px"; b.style.top = (base - h) + "px"; vt.style.top = (base - h - 56) + "px"; vt.textContent = (lo + (val - lo) * p).toFixed(3); vt.style.opacity = p > 0 ? 1 : 0; });
      fade(abs(sc, bx - 30, base + 14, 240, null, lab, "lbl", `font-size:22px;color:${k ? C.muted : C.blue};font-weight:${k ? 400 : 700}`), v + t + k * 0.5, 0.4, 6);
    });
  });
  el(sc, "div", "abs", `left:90px;top:${base}px;width:1740px;height:2px;background:#9aa3ae`);
  fade(abs(sc, 90, 850, 1740, null, "Trained on the FF++ c23 videos of Effort, Forensics Adapter, GenD and DFD-HR, nothing else &middot; paired 95% intervals against Effort, Forensics Adapter and SBI exclude zero &middot; the advantage is the recipe, not the data", "callout", `background:var(--green-bg);color:${C.green};font-size:24px`), v + 11.0);
}

// ============================================================================ explainability: restoration test
{
  const sc = scene("evidence", ["r4"]), v = B.r4.voice; head(sc, "Explainability", "Restore the marked region, and the forged decision disappears", B.r4.start);
  [["ev0_input", "input: nose replaced", ""], ["ev0_truth", "true footprint", `<span style="color:${C.green};font-weight:700">green</span> outline`], ["ev0_ours", "evidence map (ours)", pill("p-fake", "fake 1.00")],
   ["ev0_cam", "Score-CAM, no head", ""], ["ev0_restored", "region restored", pill("p-real", "&rarr; real 0.95")]].forEach(([f, lab, sub], i) => {
    const x = 90 + i * 352; pop(img(sc, F + f + ".png", x, 215, 300, 300), v + 0.3 + i * 0.9);
    fade(abs(sc, x - 30, 525, 360, null, lab + (sub ? "<br>" + sub : ""), "lbl", "font-size:24px;line-height:1.35"), v + 0.4 + i * 0.9, 0.4, 8); });
  stat(sc, 90, 660, 400, "94%", "of forged decisions removed by restoring the marked region (ceiling 94.1%)", C.blue, v + 6.4, 78);
  stat(sc, 530, 660, 400, "51%", "with Grad-CAM (Score-CAM 57%): a heat map is not the reason", C.grey, v + 9.4, 78);
  stat(sc, 970, 660, 420, "51&ndash;53%", "VLM free text matched to its photo blind; chance is 50%", C.red, v + 12.8, 78);
  stat(sc, 1440, 660, 400, "361 / 361", "sentences written by code pass every check on the holdout", C.green, v + 17.0, 72);
}

// ============================================================================ system: the browser page
{
  const sc = scene("system", ["r5"]), v = B.r5.voice, s0 = B.r5.start; head(sc, "System", "The page runs in the browser: nothing is uploaded", s0);
  const D = window.DEMO, bw = 1180, bh = Math.round(D.h * bw / D.w);
  const br = abs(sc, 90, 200, bw, bh + 44, `<div class="bar"><i style="left:16px;background:#ff5f57"></i><i style="left:40px;background:#febc2e"></i><i style="left:64px;background:#28c840"></i><div class="url">localhost / demo_ru / index.html</div></div>`, "browser");
  fade(br, s0 + 0.3, 0.7);
  const frames = []; for (let i = 0; i < D.n; i++) { const e = el(br, "img", i === 0 ? "on" : "", `width:${bw}px;height:${bh}px`); e.src = `demo/f${String(i).padStart(4, "0")}.jpg`; frames.push(e); }
  br.__frames = frames; br.__t0 = s0 + 0.8; sc.__browser = br;
  fade(abs(sc, 1320, 215, 510, null, "MediaPipe landmarks &rarr; ONNX Runtime Web, EfficientNet-B4 (67 MB) &rarr; code draws the outline, names the part, writes and checks the sentences.", null, "font-size:25px;line-height:1.3"), v + 0.8);
  stat(sc, 1320, 440, 510, "0.59 s", "per photo, iPhone Safari median (P90 0.79 s)", C.blue, v + 11.0, 76);
  stat(sc, 1320, 640, 510, "0.51 s", "desktop, one WebAssembly thread", C.blue, v + 12.2, 76);
  fade(abs(sc, 1320, 830, 510, null, pill("p-real", "nothing uploaded") + " &nbsp;" + pill("p-blue", "no server"), null, "font-size:26px"), v + 6.0, 0.5, 10);
}

// ============================================================================ future work
{
  const sc = scene("future", ["f1"]), v = B.f1.voice; head(sc, "Future work", "What comes next", B.f1.start);
  [["Reenactment", "DF40 reenactment AUC 0.50 / 0.56: extend the training coverage to expression and pose transfer.", 90, 215, 560],
   ["Untouched originals", "20.8% / 19.6% of FFHQ originals are called beautified: a better operating point and cleaner negatives.", 680, 215, 560],
   ["Monochrome filters", "inkwell, moon and grayscale are the weakest group: add colour-removing filters to the paired data.", 1270, 215, 560],
   ["Naming the operation across services", "Only skin smoothing is reliable across vendors (AUROC 0.999), the others 0.69&ndash;0.72: more vendors in the engine.", 90, 540, 855],
   ["Smaller models", "The 4.7 M RepViT with an evidence head runs in 0.19 s on an iPhone: close its gap to the CLIP model.", 975, 540, 855]].forEach(([h, p, x, y, w], i) =>
    fade(card(sc, x, y, w, 290, `<h3 style="color:${C.blue}">${h}</h3><p>${p}</p>`), v + 0.3 + i * 1.9));
}

// ============================================================================ end
{
  const sc = scene("end", ["e1"]), t = B.e1.start;
  fade(abs(sc, -320, 110, 1420, 860, null, null, "border-radius:430px;background:#e8eef7"), t, 0.6, 0);
  fade(abs(sc, 140, 330, 1300, null, "Beautified Is Not Forged", "serif b", "font-size:96px;line-height:1.05"), t + 0.2, 0.7);
  fade(abs(sc, 140, 470, 1200, null, "Thank you", "serif muted", "font-size:44px"), t + 0.6, 0.6);
  fade(abs(sc, 140, 640, 1000, null, "NTHU CS Capstone Project &middot; 2026", null, "font-size:31px"), t + 0.9, 0.6);
  fade(abs(sc, 140, 690, 1000, null, "林沁瑩　陳柏融　游宸山", null, "font-size:31px;font-family:var(--cjk)"), t + 1.1, 0.6);
}

// ============================================================================ seek
const subEl = document.getElementById("subtext"), prog = document.getElementById("prog");
function apply(t) {
  scenes.forEach(s => { s.el.classList.toggle("on", t >= s.start - 0.02 && t < s.end + 0.02); });
  tweens.forEach(w => { const p = w.t1 > w.t0 ? clamp((t - w.t0) / (w.t1 - w.t0), 0, 1) : (t >= w.t0 ? 1 : 0); w.fn(w.ease(p)); });
  const cue = CU.find(c => t >= c.start && t < c.end); let txt = "", op = 0;
  if (cue) { const r = t - cue.start, s = cue.subs.find(s => r >= s.t0 - 0.1 && r < s.t1 + 0.25);
    if (s) { txt = s.text; op = clamp((r - s.t0 + 0.1) / 0.18, 0, 1) * clamp((s.t1 + 0.25 - r) / 0.18, 0, 1); } }
  subEl.textContent = txt; subEl.style.opacity = op;
  prog.style.width = (clamp(t / TOTAL, 0, 1) * 1920) + "px";
  scenes.forEach(s => { const br = s.el.__browser; if (!br) return; const r = t - br.__t0, D = window.DEMO; let k = 0;
    for (let i = 0; i < D.n; i++) { if (D.times[i] <= r) k = i; } br.__frames.forEach((f, i) => f.classList.toggle("on", i === k)); });
}
const paint = () => new Promise(res => { let done = false; const fin = () => { if (!done) { done = true; res(); } };
  requestAnimationFrame(() => requestAnimationFrame(fin)); setTimeout(fin, 80); });
window.seek = async t => { apply(t); await paint(); return t; };
window.FILM = { total: TOTAL, cues: CU };
window.READY = false;
Promise.all([...stage.querySelectorAll("img")].map(i => (i.decode ? i.decode() : Promise.resolve()).catch(() => null))).then(() => { window.READY = true; });
const h = location.hash;
if (h.startsWith("#t=")) apply(parseFloat(h.slice(3)));
else if (h === "#play") { const t0 = performance.now(); const loop = () => { apply((performance.now() - t0) / 1000); if ((performance.now() - t0) / 1000 < TOTAL) requestAnimationFrame(loop); }; loop(); }
else apply(0);
})();
