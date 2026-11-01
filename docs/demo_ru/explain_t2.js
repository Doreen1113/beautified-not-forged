/* explain_t2.js — JavaScript port of results/research/explain_vlm_20261012/explain_v2.py (condition T2).
 *
 * Pure functions, no DOM, no model code. The input is the same structured record the Python side uses
 * (the evidence JSON of build_evidence_json.py): decision, probabilities, operations, operation_threshold,
 * evidence_mean_per_part, named_parts, whole_face. Sentence rules follow PRE_DECLARED.md section 9.1 exactly:
 *   1. verdict sentence (always)      模型判定為 <decision>（分數 <p, 2 dp>）。
 *   2. region sentence                real → 整臉未偵測到操弄。 / whole face → 證據遍布整臉。 / else 證據集中在<部位>（evidence 平均 <v>）、…。
 *   3. operations sentence (filter)   達到門檻 <thr> 的操作：<op>（<score>）、…。 / 四種操作的分數都未達門檻 <thr>。
 *   4. calibration sentence (always)  分數是模型原始輸出，不是校準過的機率。
 * Equivalence with the Python module is checked by test/run_test_headless.py against test/fixture_t2.json.
 *
 * One addition that Python never needs: when the record has no evidence fields at all (the browser RepViT ONNX has no
 * evidence head), the region sentence is replaced by a fixed sentence that says so, instead of claiming "whole face".
 * Loads as a classic script (window.ExplainT2) and as a CommonJS module.
 *
 * English (2026-10-15): t2Sentences(j, "en") / compose(j, obs, "en") give the English wording of the same four sentences,
 * twin of results/research/explain_vlm_20261012/nl_v5/explain_v2_en.py (same branches, only the strings differ; sentences
 * joined with one space). The default stays Chinese, so every existing caller and test is unchanged.
 *   1. The model's decision is <dec> (score <p>).
 *   2. No manipulation was detected on the face. / The evidence is spread over the whole face. /
 *      The evidence is concentrated on the eyes (mean evidence 0.62) and the mouth (mean evidence 0.55).
 *   3. Operations at or above the threshold of 0.5: skin smoothing (0.91), eye enlargement (0.66). /
 *      None of the four operations reaches the threshold of 0.5.
 *   4. The score is the model's raw output, not a calibrated probability.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.ExplainT2 = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  const OPS = ["eye_enlargement", "face_slimming", "skin_brightening", "skin_smoothing"];
  const OP_ZH = { eye_enlargement: "眼睛放大", face_slimming: "瘦臉", skin_brightening: "美白", skin_smoothing: "磨皮" };
  const PART_ZH = { eyes: "眼睛", nose: "鼻子", mouth: "嘴巴", skin: "皮膚", contour: "臉部輪廓", "whole face": "整臉" };
  const CAL_ZH = "分數是模型原始輸出，不是校準過的機率。";
  const NO_EVIDENCE_ZH = "此瀏覽器版模型未匯出 evidence head，無法指出區域。";
  const OP_EN = { eye_enlargement: "eye enlargement", face_slimming: "face slimming", skin_brightening: "skin whitening", skin_smoothing: "skin smoothing" };
  const PART_EN = { eyes: "the eyes", nose: "the nose", mouth: "the mouth", skin: "the skin", contour: "the face contour", "whole face": "the whole face" };
  const CAL_EN = "The score is the model's raw output, not a calibrated probability.";
  const NO_EVIDENCE_EN = "The fast model has no evidence module, so it cannot point to a face part.";
  const joinEn = (a) => (a.length === 1 ? a[0] : a.slice(0, -1).join(", ") + " and " + a[a.length - 1]);

  // Python f"{x:.2f}" on values the JSON already stores with two decimals; toFixed differs from Python only on exact
  // binary ties (e.g. 0.125), which cannot occur for two-decimal inputs. Verified on the fixture.
  const f2 = (x) => Number(x).toFixed(2);
  // Python f"{thr}" for a float: 0.5 -> "0.5", 0.45 -> "0.45". JS String() gives the same shortest round-trip form.
  const fthr = (t) => String(t);

  // Python's round(x, nd) on a double: correctly rounded from the exact binary value (toFixed does that), except exact
  // binary ties (e.g. 0.125 at 2 dp), where Python rounds half to even. Math.round(x*100)/100 is wrong on values such as
  // 0.985 (binary 0.98499...: Python gives 0.98, Math.round gives 0.99).
  function pyRound(x, nd) {
    const m = Math.pow(10, nd), y = x * m;
    if (Number.isInteger(x * Math.pow(2, nd + 1)) && y - Math.floor(y) === 0.5) { const n0 = Math.floor(y); return (n0 % 2 === 0 ? n0 : n0 + 1) / m; }
    return Number(x.toFixed(nd));
  }

  function hasEvidence(j) {
    return j && j.evidence_mean_per_part && typeof j.evidence_mean_per_part === "object" && Array.isArray(j.named_parts);
  }

  function isWhole(j) {
    const np = j.named_parts || [];
    return np.length === 0 || Boolean(j.whole_face) || (np.length === 1 && np[0] === "whole face");
  }

  function regionParts(j) {
    return isWhole(j) ? ["whole face"] : j.named_parts.slice();
  }

  // Same split as explain_v2.add_op_fields: on the rounded scores the JSON shows, >= threshold vs < threshold.
  function opFields(j) {
    if (Array.isArray(j.operations_at_or_above_threshold)) {
      return { above: j.operations_at_or_above_threshold, below: j.operations_below_threshold || [] };
    }
    const thr = j.operation_threshold, above = [], below = [];
    for (const o of OPS) {
      const s = j.operations[o];
      (s >= thr ? above : below).push({ name: o, score: s });
    }
    return { above, below };
  }

  // Page rule (2026-10-30): name only the operations in opts.namedOps (the page passes ["skin_smoothing"]).
  function namedOpSentence(j, lang, named) {
    const thr = fthr(j.operation_threshold), on = named.filter((o) => j.operations[o] >= j.operation_threshold);
    const off = named.filter((o) => j.operations[o] < j.operation_threshold);
    if (lang === "en") {
      return on.length
        ? "At or above the threshold of " + thr + ": " + on.map((o) => OP_EN[o] + " (" + f2(j.operations[o]) + ")").join(", ") + "."
        : off.map((o) => OP_EN[o].charAt(0).toUpperCase() + OP_EN[o].slice(1) + " (" + f2(j.operations[o]) + ")").join(", ") + " does not reach the threshold of " + thr + ".";
    }
    return on.length
      ? "達到門檻 " + thr + "：" + on.map((o) => OP_ZH[o] + "（" + f2(j.operations[o]) + "）").join("、") + "。"
      : off.map((o) => OP_ZH[o] + "（" + f2(j.operations[o]) + "）").join("、") + "未達門檻 " + thr + "。";
  }

  function t2SentencesEn(j, opts) {
    const dec = j.decision;
    const s1 = "The model's decision is " + dec + " (score " + f2(j.probabilities[dec]) + ").";
    let s2;
    if (dec === "real") s2 = "No manipulation was detected on the face.";
    else if (!hasEvidence(j)) s2 = NO_EVIDENCE_EN;
    else if (isWhole(j)) s2 = "The evidence is spread over the whole face.";
    else s2 = "The evidence is concentrated on " + joinEn(j.named_parts.map((p) => PART_EN[p] + " (mean evidence " + f2(j.evidence_mean_per_part[p]) + ")")) + ".";
    let s3 = null;
    if (dec === "filter" && opts && opts.namedOps) s3 = namedOpSentence(j, "en", opts.namedOps);
    else if (dec === "filter") {
      const { above } = opFields(j), thr = fthr(j.operation_threshold);
      s3 = above.length
        ? "Operations at or above the threshold of " + thr + ": " + above.map((o) => OP_EN[o.name] + " (" + f2(o.score) + ")").join(", ") + "."
        : "None of the four operations reaches the threshold of " + thr + ".";
    }
    return [s1, s2, s3, CAL_EN];
  }

  /** Returns [verdict, region, operationsOrNull, calibration]. lang "zh" (default) or "en". */
  function t2Sentences(j, lang, opts) {
    if (lang === "en") return t2SentencesEn(j, opts);
    const dec = j.decision;
    const s1 = "模型判定為 " + dec + "（分數 " + f2(j.probabilities[dec]) + "）。";
    let s2;
    if (dec === "real") s2 = "整臉未偵測到操弄。";
    else if (!hasEvidence(j)) s2 = NO_EVIDENCE_ZH;
    else if (isWhole(j)) s2 = "證據遍布整臉。";
    else s2 = "證據集中在" + j.named_parts.map((p) => PART_ZH[p] + "（evidence 平均 " + f2(j.evidence_mean_per_part[p]) + "）").join("、") + "。";
    let s3 = null;
    if (dec === "filter" && opts && opts.namedOps) s3 = namedOpSentence(j, "zh", opts.namedOps);
    else if (dec === "filter") {
      const { above } = opFields(j), thr = fthr(j.operation_threshold);
      s3 = above.length
        ? "達到門檻 " + thr + " 的操作：" + above.map((o) => OP_ZH[o.name] + "（" + f2(o.score) + "）").join("、") + "。"
        : "四種操作的分數都未達門檻 " + thr + "。";
    }
    return [s1, s2, s3, CAL_ZH];
  }

  /** Runtime checker on the page (2026-10-30). sentences = t2Sentences(j, lang, opts) before display wording.
   *  Returns { ok, fails: [rule ids] }. Rules: H1 decision word, H2 part words within the named region, H3 named
   *  operations within the allowed set and on the right side of the threshold, H4 every number is a value of the record,
   *  H6 three or four sentences, G8 no certainty word. */
  const CERTAIN_EN = /\b(certain|certainly|definitely|surely|undoubtedly|guaranteed?|proven|proves?|confirmed)\b/i;
  const CERTAIN_ZH = /確定|一定是|肯定|必然|證實|無疑|百分之百/;
  function checkT2(j, sentences, lang, opts) {
    const fails = [], en = lang === "en", s = sentences || [], dec = j.decision;
    const PART = en ? PART_EN : PART_ZH, OPN = en ? OP_EN : OP_ZH;
    if (!(s[0] || "").includes(en ? "decision is " + dec : "判定為 " + dec)) fails.push("H1");
    if (s[1]) {
      const allowed = new Set(dec === "real" ? [] : regionParts(j));
      for (const k of ["eyes", "nose", "mouth", "skin", "contour"]) {
        const w = en ? PART[k] : PART[k];
        if (s[1].includes(w) && !allowed.has(k) && !allowed.has("whole face")) { fails.push("H2"); break; }
      }
    }
    if (s[2]) {
      if (dec !== "filter") fails.push("H3");
      const allowedOps = new Set((opts && opts.namedOps) || OPS), thr = j.operation_threshold;
      for (const o of OPS) {
        if (!s[2].includes(OPN[o]) && !s[2].includes(OPN[o].charAt(0).toUpperCase() + OPN[o].slice(1))) continue;
        if (!allowedOps.has(o)) { fails.push("H3"); break; }
        const saysAbove = en ? /At or above|Operations at or above/.test(s[2]) : /達到門檻/.test(s[2]) && !/未達門檻/.test(s[2]);
        if (saysAbove !== (j.operations[o] >= thr)) { fails.push("H3"); break; }
      }
    } else if (dec === "filter") fails.push("H3");
    const vals = new Set([fthr(j.operation_threshold), f2(j.operation_threshold)]);
    for (const v of Object.values(j.probabilities || {})) vals.add(f2(v));
    for (const v of Object.values(j.operations || {})) vals.add(f2(v));
    for (const v of Object.values(j.evidence_mean_per_part || {})) vals.add(f2(v));
    const nums = s.filter(Boolean).join(" ").match(/\d+\.\d+/g) || [];
    if (nums.some((n) => !vals.has(n))) fails.push("H4");
    const n = s.filter(Boolean).length; if (n < 3 || n > 4) fails.push("H6");
    if (s.filter(Boolean).some((x) => (en ? CERTAIN_EN : CERTAIN_ZH).test(x))) fails.push("G8");
    return { ok: fails.length === 0, fails };
  }

  /** Final text: verdict + region + [observation] + (operations) + calibration — explain_v2.compose. */
  function compose(j, observation, lang) {
    const [s1, s2, s3, s4] = t2Sentences(j, lang);
    return [s1, s2, observation || null, s3, s4].filter(Boolean).join(lang === "en" ? " " : "");
  }

  /** The demo's old English template ("舊模板"), kept selectable; identical to the page's previous wording. */
  function oldTemplate(j) {
    const dec = j.decision, thr = j.operation_threshold;
    const names = { eye_enlargement: "eye enlargement", face_slimming: "face slimming", skin_brightening: "skin brightening", skin_smoothing: "skin smoothing" };
    if (dec === "real") return "No manipulation detected.";
    if (dec === "fake") return "Forgery detected: identity or content appears to have been changed.";
    const ops = j.operations_raw || j.operations;  // the old page compared the un-rounded sigmoids
    const present = OPS.filter((o) => ops[o] >= thr).map((o) => names[o]);
    return "Beautification detected, identity preserved" + (present.length ? ": " + present.join(", ") + "." : "; the operation is unclear.");
  }

  /** Build the structured record from the demo's raw outputs (3 class probs, 4 op sigmoids), rounded to 2 dp as the
   *  Python evidence JSON is. Evidence fields are only filled when a 16x16 map and per-part means are supplied. */
  function recordFromOutputs(probs, ops, extra) {
    const r2 = (x) => pyRound(x, 2);
    const CLS = ["real", "fake", "filter"];
    const p = { real: r2(probs[0]), fake: r2(probs[1]), filter: r2(probs[2]) };
    let k = 0; for (let i = 1; i < 3; i++) if (probs[i] > probs[k]) k = i;
    const rec = {
      decision: CLS[k], probabilities: p,
      operations: { eye_enlargement: r2(ops[0]), face_slimming: r2(ops[1]), skin_brightening: r2(ops[2]), skin_smoothing: r2(ops[3]) },
      operation_threshold: 0.5,
      calibration_note: "scores are raw model outputs, not calibrated probabilities",
    };
    if (extra && extra.evidence_mean_per_part && extra.named_parts) {
      rec.evidence_mean_per_part = extra.evidence_mean_per_part; rec.named_parts = extra.named_parts;
      rec.whole_face = Boolean(extra.whole_face);
    }
    return rec;
  }

  return { OPS, OP_ZH, PART_ZH, CAL_ZH, NO_EVIDENCE_ZH, OP_EN, PART_EN, CAL_EN, NO_EVIDENCE_EN, pyRound, t2Sentences, checkT2, compose, oldTemplate, recordFromOutputs, isWhole, regionParts, hasEvidence };
});
