/* nl_client.js — the page's client for the optional server mode (results/research/explain_vlm_20261012/nl_v5/nl_server.py).
 *
 * The server runs Qwen2.5-7B-Instruct and checks every text with gate v3 (H1-H6 of validate_text.py, the
 * decision-score-vs-threshold check G7, fact preservation, G8 certainty words, G9 score on a part) before returning it; when the model's text fails twice the
 * server returns the code template instead (source "template"); the three limitation questions are answered by fixed
 * code sentences (source "fixed"). No LLM runs in the browser. Shared by index.html and test/test_server_page.html.
 *
 * Routing v3 (PRE_DECLARED_NL 14, 2026-10-15): four questions are answered by fixed code sentences (the three limitation
 * questions and 「這個分數代表什麼？」), four go to the LLM. FIXED_QA below carries the same four strings as
 * nl_core.FIXED_QA (checked by test/run_test_server_headless.py), so the page answers them without the server.
 *
 * English (2026-10-15, PRE_DECLARED_NL 15): every call takes the page locale `lang` ("en" default, "zh"); the server answers
 * in that language (English: prompt p2en + validate_text_en gate). QUESTIONS_EN / FIXED_QA_EN carry the same questions by
 * index and the same four fixed answers as nl_core_en.QUESTIONS_EN / FIXED_QA_EN (checked by run_test_server_headless.py).
 *
 * Design p3 (2026-10-15, PRE_DECLARED_NL 17; the server's default prompt): the LLM writes the wording only, with no numbers
 * and nothing about certainty or calibration; the server's code adds the decision score (expert style: also mean evidence
 * and operation scores) in labelled parentheticals and the fixed calibration sentence, and gates both the LLM's own text
 * (incl. G10: no number at all) and the composed text (gate v3). The reply then also carries `prompt` (version used),
 * `llm_text` (the LLM's own text) and `code_added` ({parentheticals, calibration}); `text` is the composed text.
 * badgeKey(res) -> "llmCode" when code added numbers / the calibration sentence to LLM text, else res.source, so the
 * page's caption says truthfully who wrote what. Q&A answers have no code additions (badge "llm").
 * Optional `prompt` argument ("p3" default | "p2" = the old flow) for reproducing earlier recordings.
 *
 * NLClient.health(url)                          -> server info, or throws
 * NLClient.explain(url, record, style, lang[, prompt]) -> {text, source, gate, ms, lang, prompt, llm_text?, code_added?}
 * NLClient.qa(url, record, questionId, lang[, prompt]) -> {text, source, gate, ms, lang, prompt, question, llm_text?}
 * NLClient.badgeKey(res)                        -> "llmCode" | "llm" | "template" | "fixed"
 * NLClient.questions(lang)                      -> the eight questions in that language (same order)
 * NLClient.usable(record)                       -> true when the record carries the evidence fields the server needs
 * NLClient.isFixed(questionId)                  -> true for the four fixed-answer questions (same in both languages)
 * NLClient.fixedAnswer(questionId, lang)        -> {text, source: "fixed", ms: 0, question}  (offline, no server)
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.NLClient = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  const QUESTIONS = ["為什麼判定為假？", "哪裡被改了？", "有沒有美顏？", "這個分數代表什麼？",
                     "可以確定嗎？", "和原圖比差在哪？", "是誰？", "為什麼不是真的？"];
  const DEFAULT_URL = "http://127.0.0.1:8787";
  const FIXED_QA = {
    "和原圖比差在哪？": "系統使用時拿不到原圖，所以說不出這張照片和原本的照片差在哪裡。",
    "是誰？": "系統不辨識身分，無法回答照片裡是誰。",
    "可以確定嗎？": "無法確定。分數是模型的原始輸出，不是校準過的機率，判定也可能出錯。",
    "這個分數代表什麼？": "分數是模型對它所選判定的原始輸出，數值越高表示模型越偏向這個判定。它不是校準過的機率，分數高也不代表判定正確，模型也可能判錯。",
  };
  const QUESTIONS_EN = ["Why is it judged fake?", "Where was it changed?", "Was it retouched?", "What does this score mean?",
                        "Is this certain?", "Where does it differ from the original photo?", "Who is this?", "Why is it not real?"];
  const FIXED_QA_EN = {
    "Where does it differ from the original photo?": "The system has no access to the original photo, so it cannot say how this photo differs from it.",
    "Who is this?": "The system does not recognize identities, so it cannot say who is in the photo.",
    "Is this certain?": "No. The score is the model's raw output, not a calibrated probability, and the decision can be wrong.",
    "What does this score mean?": "The score is the model's raw output for the decision it chose; a higher value means the model leans more toward that decision. It is not a calibrated probability, a high score does not mean the decision is correct, and the model can be wrong.",
  };
  const langOf = (lang) => (lang === "zh" ? "zh" : "en");
  const questions = (lang) => (langOf(lang) === "zh" ? QUESTIONS : QUESTIONS_EN);
  const isFixed = (i) => Object.prototype.hasOwnProperty.call(FIXED_QA, QUESTIONS[i]);
  function fixedAnswer(i, lang) {
    const zh = langOf(lang) === "zh", q = questions(lang)[i];
    if (!isFixed(i)) throw new Error("not a fixed-answer question: " + q);
    return { text: (zh ? FIXED_QA : FIXED_QA_EN)[q], source: "fixed", ms: 0, question: q };
  }

  async function call(url, path, body, timeoutMs) {
    const ctl = new AbortController(), timer = setTimeout(() => ctl.abort(), timeoutMs);
    try {
      const r = await fetch(url.replace(/\/+$/, "") + path, body === undefined ? { signal: ctl.signal } :
        { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body), signal: ctl.signal });
      if (!r.ok) throw new Error("server " + r.status);
      return await r.json();
    } finally { clearTimeout(timer); }
  }

  function usable(record) {
    return Boolean(record && record.evidence_mean_per_part && Array.isArray(record.named_parts));
  }

  function badgeKey(res) {
    const ca = res && res.code_added;
    return res && res.source === "llm" && ca && (ca.calibration || (ca.parentheticals || []).length) ? "llmCode" : (res && res.source);
  }

  return {
    QUESTIONS, QUESTIONS_EN, DEFAULT_URL, FIXED_QA, FIXED_QA_EN, questions, usable, isFixed, fixedAnswer, badgeKey,
    health: (url) => call(url, "/health", undefined, 2000),
    explain: (url, record, style, lang, prompt) => call(url, "/explain", { facts: record, style, lang: langOf(lang), prompt: prompt || "p3" }, 60000),
    qa: (url, record, questionId, lang, prompt) => call(url, "/qa", { facts: record, question_id: questionId, lang: langOf(lang), prompt: prompt || "p3" }, 60000),
  };
});
