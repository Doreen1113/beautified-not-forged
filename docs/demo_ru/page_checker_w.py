"""2026-10-30 (Addendum 70, W model shipped by user decision):
1. explain_t2.js: t2Sentences(j, lang, opts) takes opts.namedOps; the page passes ["skin_smoothing"], so the operations
   sentence names smoothing only (the only operation that is reliable across retouching services, XVENDOR_OPS.md; on a
   smoothing-only Alibaba render the browser model also raises eye 0.78 / slim 0.78 / white 0.87). Without opts the output
   is unchanged, so the Python equivalence test (run_test_headless.py, fixture_t2.json) still applies to the research rule.
2. explain_t2.js: checkT2(j, sentences, lang, opts) -- a runtime checker on the page (H1 decision word, H2 part words within
   the named region, H3 named operations within the allowed set and on the right side of the threshold, H4 every number
   is a value of the record, H6 three or four sentences, G8 no certainty word). Until now the page claimed a checker but
   ran none: the gate lived on the LLM server that was removed on 2026-10-29.
3. index.html: renders only text that passes checkT2; otherwise shows a refusal line and a "not shown" badge; stores the
   result in #explain[data-check]. Validation text updated to the W model (Alibaba: retouched -> fake 0.5 %, balanced 72.4 %,
   smoothing -> filter 94-99 %, single operations 36-65 %, originals -> filter 16.7 %).
Exact string replacement; abort on a missing or repeated anchor; backups *_pre_checker_20261030.*; idempotent.
python page_checker_w.py"""
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
JS, HTML = HERE / "explain_t2.js", HERE / "index.html"

JS_EDITS = [
    ("""  function opFields(j) {
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
""",
     """  function opFields(j) {
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
"""),
    ("""  function t2SentencesEn(j) {""", """  function t2SentencesEn(j, opts) {"""),
    ("""    let s3 = null;
    if (dec === "filter") {
      const { above } = opFields(j), thr = fthr(j.operation_threshold);
      s3 = above.length
        ? "Operations at or above the threshold of " + thr + ": " + above.map((o) => OP_EN[o.name] + " (" + f2(o.score) + ")").join(", ") + "."
        : "None of the four operations reaches the threshold of " + thr + ".";
    }
    return [s1, s2, s3, CAL_EN];""",
     """    let s3 = null;
    if (dec === "filter" && opts && opts.namedOps) s3 = namedOpSentence(j, "en", opts.namedOps);
    else if (dec === "filter") {
      const { above } = opFields(j), thr = fthr(j.operation_threshold);
      s3 = above.length
        ? "Operations at or above the threshold of " + thr + ": " + above.map((o) => OP_EN[o.name] + " (" + f2(o.score) + ")").join(", ") + "."
        : "None of the four operations reaches the threshold of " + thr + ".";
    }
    return [s1, s2, s3, CAL_EN];"""),
    ("""  function t2Sentences(j, lang) {
    if (lang === "en") return t2SentencesEn(j);""",
     """  function t2Sentences(j, lang, opts) {
    if (lang === "en") return t2SentencesEn(j, opts);"""),
    ("""    let s3 = null;
    if (dec === "filter") {
      const { above } = opFields(j), thr = fthr(j.operation_threshold);
      s3 = above.length
        ? "達到門檻 " + thr + " 的操作：" + above.map((o) => OP_ZH[o.name] + "（" + f2(o.score) + "）").join("、") + "。"
        : "四種操作的分數都未達門檻 " + thr + "。";
    }
    return [s1, s2, s3, CAL_ZH];
  }
""",
     """    let s3 = null;
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
  const CERTAIN_EN = /\\b(certain|certainly|definitely|surely|undoubtedly|guaranteed?|proven|proves?|confirmed)\\b/i;
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
    const nums = s.filter(Boolean).join(" ").match(/\\d+\\.\\d+/g) || [];
    if (nums.some((n) => !vals.has(n))) fails.push("H4");
    const n = s.filter(Boolean).length; if (n < 3 || n > 4) fails.push("H6");
    if (s.filter(Boolean).some((x) => (en ? CERTAIN_EN : CERTAIN_ZH).test(x))) fails.push("G8");
    return { ok: fails.length === 0, fails };
  }
"""),
    ("""  return { OPS, OP_ZH, PART_ZH, CAL_ZH, NO_EVIDENCE_ZH, OP_EN, PART_EN, CAL_EN, NO_EVIDENCE_EN, pyRound, t2Sentences, compose, oldTemplate, recordFromOutputs, isWhole, regionParts, hasEvidence };""",
     """  return { OPS, OP_ZH, PART_ZH, CAL_ZH, NO_EVIDENCE_ZH, OP_EN, PART_EN, CAL_EN, NO_EVIDENCE_EN, pyRound, t2Sentences, checkT2, compose, oldTemplate, recordFromOutputs, isWhole, regionParts, hasEvidence };"""),
]

HTML_EDITS = [
    ("""  const el = $("explain"), rec = last.r.record, lg = lang;
  el.innerHTML = ExplainT2.t2Sentences(rec, lg).filter(Boolean).map((s) => `<span>${esc(showT2(s))}</span>`).join("");
  setBadge("template");
}""",
     """  const el = $("explain"), rec = last.r.record, lg = lang, opts = { namedOps: ["skin_smoothing"] };
  const sents = ExplainT2.t2Sentences(rec, lg, opts), chk = ExplainT2.checkT2(rec, sents, lg, opts);
  el.dataset.check = chk.ok ? "pass" : chk.fails.join(",");
  if (chk.ok) { el.innerHTML = sents.filter(Boolean).map((s) => `<span>${esc(showT2(s))}</span>`).join(""); setBadge("template"); }
  else { el.textContent = T().checkFail; setBadge("failed"); }
}"""),
    ("""    badge: { template: "Composed by code, checked", fixed: "Fixed answer" },""",
     """    badge: { template: "Composed by code, checked", fixed: "Fixed answer", failed: "Not shown: failed the check" },
    checkFail: "The composed text did not match the model's output, so it is not shown.","""),
    ("""    badge: { template: "程式組成，已查核", fixed: "固定回答" },""",
     """    badge: { template: "程式組成，已查核", fixed: "固定回答", failed: "未通過查核，不顯示" },
    checkFail: "組成的文字和模型輸出對不上，所以不顯示。","""),
    ("""        <li>On a commercial retouching service not seen in training (26,519 retouched photos and their originals), only 0.3% of retouched photos are called fake; the balanced accuracy for retouched vs untouched is 72.6%.</li>
        <li>Skin smoothing is almost always caught (called filter 95–99% of the time); eye enlargement, face slimming or whitening on their own are often missed (called filter about 40–67% of the time); 18.6% of untouched originals are wrongly called filter.</li>""",
     """        <li>On a commercial retouching service not seen in training (26,519 retouched photos and their originals), only 0.5% of retouched photos are called fake; the balanced accuracy for retouched vs untouched is 72.4%.</li>
        <li>Skin smoothing is almost always caught (called filter 94–99% of the time); eye enlargement, face slimming or whitening on their own are often missed (called filter about 36–65% of the time), and on a smoothed photo their scores often rise too, so the explanation names skin smoothing only; 16.7% of untouched originals are wrongly called filter. Ordinary photographs (FairFace): 95.7% called real.</li>"""),
    ("""        <li>在訓練時沒看過的商用修圖服務上（26,519 張修過的照片及其原圖）：修過的照片被誤判為偽造的只有 0.3%；分辨「修過」與「沒修過」的平衡準確率為 72.6%。</li>
        <li>磨皮幾乎都抓得到（判為美顏 95–99%）；單獨的大眼、瘦臉、美白常抓不到（判為美顏約 40–67%）；沒修過的原圖有 18.6% 被誤判為美顏。</li>""",
     """        <li>在訓練時沒看過的商用修圖服務上（26,519 張修過的照片及其原圖）：修過的照片被誤判為偽造的只有 0.5%；分辨「修過」與「沒修過」的平衡準確率為 72.4%。</li>
        <li>磨皮幾乎都抓得到（判為美顏 94–99%）；單獨的大眼、瘦臉、美白常抓不到（判為美顏約 36–65%），而且照片只磨皮時這三項分數也常跟著升高，所以解釋只點名磨皮；沒修過的原圖有 16.7% 被誤判為美顏。一般照片（FairFace）有 95.7% 判為真實。</li>"""),
    ("""(default model 18.6%); retouched photos called fake 0.3%, the same as the default.</li>""",
     """(default model 16.7%); retouched photos called fake 0.3% (default 0.5%).</li>"""),
    ("""（預設模型 18.6%）；修過的照片被誤判為偽造 0.3%，與預設相同。</li>""",
     """（預設模型 16.7%）；修過的照片被誤判為偽造 0.3%（預設 0.5%）。</li>"""),
]


def apply(path, edits, marker):
    t = path.read_text(encoding="utf-8")
    if marker in t:
        print("already patched", path.name); return
    bak = path.with_name(path.stem + "_pre_checker_20261030" + path.suffix)
    if not bak.exists():
        shutil.copy2(path, bak)
    for old, new in edits:
        assert t.count(old) == 1, (path.name, t.count(old), old[:80])
        t = t.replace(old, new)
    path.write_text(t, encoding="utf-8"); print("patched", path.name, "backup", bak.name)


apply(JS, JS_EDITS, "function checkT2(")
apply(HTML, HTML_EDITS, "checkFail:")
