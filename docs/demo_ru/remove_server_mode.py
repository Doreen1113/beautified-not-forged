"""2026-10-29: remove the LLM server mode from the browser demo (index.html). The language-model rewording was tested and
removed from the evaluated system (capstone REPORT_v2 §5.2, CONSISTENCY_AUDIT D01); it stayed in the page only as a
test switch. Kept: the code-composed explanation (explain_t2.js) and the four questions answered by fixed code sentences
(nl_client.js FIXED_QA, offline). Removed: the server switch, URL, style choice, LLM rewrite, LLM questions and their strings.
Exact string replacement; abort if an anchor is missing or repeated; backup index_pre_noserver_20261029.html; idempotent.
python remove_server_mode.py"""
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent; P = HERE / "index.html"
EDITS = [
    # settings block
    ("""      <div class="field">
        <div class="lab" data-i18n="srvLab">Server mode</div>
        <label class="switch"><input type="checkbox" id="srvOn"><span data-i18n="srvSwitch">Use the LLM on a server to rewrite the explanation and answer the other questions</span></label>
        <p class="note" data-i18n="srvNote"></p>
        <div style="margin-top:8px"><label class="note" for="srvUrl" data-i18n="srvUrl">Server URL</label></div>
        <input id="srvUrl" type="url" value="http://127.0.0.1:8787" spellcheck="false" autocomplete="off" inputmode="url">
        <p class="note" id="srvStatus" role="status" aria-live="polite"></p>
        <div class="seg" role="radiogroup" aria-label="Explanation style" data-i18n-aria="styleAria" style="margin-top:8px">
          <label><input type="radio" name="nlstyle" value="general" checked><span data-i18n-html="styleGeneral"></span></label>
          <label><input type="radio" name="nlstyle" value="pro"><span data-i18n-html="stylePro"></span></label>
        </div>
      </div>
""", ""),
    # how-it-works text, English
    ("""        <li>The explanation is written by code with fixed rules and states only what the model actually output. With server mode on, an LLM (Qwen2.5-7B) rewrites the wording in plainer language, but writes no numbers and nothing about certainty: the scores (in parentheses) and the sentence saying the score is not a calibrated probability are added by code. Every text is checked automatically (no numbers in the LLM's words, no claims of certainty, the score not attached to a face part, every fact present, and so on), and a text that fails goes back to the code template.</li>
        <li>Four questions are answered by fixed code sentences, not by the LLM: "Where does it differ from the original photo?", "Who is this?", "Is this certain?" and "What does this score mean?".</li>""",
     """        <li>The explanation is composed by code with fixed rules and states only what the model actually output; no language model writes or rewords it. Before it is shown, a rule checker matches every sentence to the model's output (decision, region, operations, numbers) and rejects any wording about certainty.</li>
        <li>Four questions that the model's output cannot answer get fixed code sentences: "Where does it differ from the original photo?", "Who is this?", "Is this certain?" and "What does this score mean?".</li>"""),
    # how-it-works text, Chinese
    ("""        <li>解釋文字由程式依固定規則產生，只寫模型真的輸出的內容。開啟伺服器模式時，改由 LLM（Qwen2.5-7B）把文字重寫成較口語的說法，但 LLM 不寫數字、也不談確定性：括號裡的分數與「分數不是校準過的機率」那一句由程式加上。每段文字都會自動檢查（LLM 的文字不能有數字、不能說「確定」、分數不能掛在部位上、事實要齊全等），沒通過就改回程式模板。</li>
        <li>「和原圖比差在哪？」「是誰？」「可以確定嗎？」「這個分數代表什麼？」四題由程式固定回答，不經過 LLM。</li>""",
     """        <li>解釋文字由程式依固定規則組成，只寫模型真的輸出的內容，不經過任何語言模型。顯示前，規則查核器會把每一句和模型輸出（判定、部位、操作、數字）逐項比對，並擋下任何關於「確定」的說法。</li>
        <li>模型輸出回答不了的四個問題由程式固定回答：「和原圖比差在哪？」「是誰？」「可以確定嗎？」「這個分數代表什麼？」。</li>"""),
    # explanation: code template only
    ("""  const el = $("explain"), rec = last.r.record, seq = ++srv.seq, lg = lang;
  el.innerHTML = ExplainT2.t2Sentences(rec, lg).filter(Boolean).map((s) => `<span>${esc(showT2(s))}</span>`).join("");
  setBadge("template");
  if (!srv.ok || !NLClient.usable(rec)) return;                    // T2 stays
  const style = document.querySelector("input[name=nlstyle]:checked").value;
  $("srcBadge").textContent = T().rewriting;
  NLClient.explain($("srvUrl").value, rec, style, lg).then((res) => {
    if (seq !== srv.seq || !last || rec !== last.r.record || lg !== lang) return;
    el.textContent = showServer(res);
    setBadge(NLClient.badgeKey(res));
  }).catch(() => { if (seq === srv.seq) setBadge("template"); });  // unreachable: T2 stays
}""",
     """  const el = $("explain"), rec = last.r.record, lg = lang;
  el.innerHTML = ExplainT2.t2Sentences(rec, lg).filter(Boolean).map((s) => `<span>${esc(showT2(s))}</span>`).join("");
  setBadge("template");
}"""),
    # questions: only the four fixed-answer ones
    ("""  const usable = srv.ok && NLClient.usable(last.r.record);
  box.innerHTML = "";
  NLClient.questions(lang).forEach((q, i) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.textContent = q; b.setAttribute("aria-pressed", "false");
    b.disabled = !NLClient.isFixed(i) && !usable;
    b.addEventListener("click", () => ask(i, b));
    box.appendChild(b);
  });
  $("chipNote").textContent = usable ? "" : (srv.ok ? T().chipNeedEv : T().chipNeedSrv);""",
     """  box.innerHTML = "";
  NLClient.questions(lang).forEach((q, i) => {
    if (!NLClient.isFixed(i)) return;   // only the questions answered by fixed code sentences
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.textContent = q; b.setAttribute("aria-pressed", "false");
    b.addEventListener("click", () => ask(i, b));
    box.appendChild(b);
  });
  $("chipNote").textContent = "";"""),
    ("""  const lg = lang, q = NLClient.questions(lg)[i], seq = ++srv.qseq;
  if (NLClient.isFixed(i)) { const r = NLClient.fixedAnswer(i, lg); showAnswer(q, r.text, "fixed"); return; }
  if (!srv.ok || !last) return;
  const rec = last.r.record; showAnswer(q, T().thinking, null);
  NLClient.qa($("srvUrl").value, rec, i, lg).then((res) => {
    if (seq !== srv.qseq || !last || rec !== last.r.record || lg !== lang) return;
    showAnswer(q, showServer(res), NLClient.badgeKey(res));
  }).catch(() => { if (seq === srv.qseq && lg === lang) showAnswer(q, T().qaFail, null); });
}

function srvMsg(key) { MSG.srv = key ? [key] : null; $("srvStatus").textContent = key ? tr([key]) : ""; }

async function checkServer() {
  srv.ok = false; srvMsg(null);
  if ($("srvOn").checked) {
    srvMsg("srvConnecting");
    try { const h = await NLClient.health($("srvUrl").value); srv.ok = Boolean(h && h.ok); }
    catch (e) { srv.ok = false; }
    srvMsg(srv.ok ? "srvOk" : "srvFail");
  }
  if (last) { renderExplanation(); buildChips(); }
}""",
     """  const q = NLClient.questions(lang)[i];
  if (NLClient.isFixed(i)) { const r = NLClient.fixedAnswer(i, lang); showAnswer(q, r.text, "fixed"); }
}"""),
    ("""document.querySelectorAll("input[name=nlstyle]").forEach((r) => r.addEventListener("change", renderExplanation));
$("srvOn").addEventListener("change", checkServer);
$("srvUrl").addEventListener("change", checkServer);
""", ""),
    ("""  if (MSG.srv) $("srvStatus").textContent = tr(MSG.srv);
""", ""),
    ("""const showServer = (res) => (res.source === "llm" ? res.text : lang === "en" ? showT2(res.text) : res.text.split(/(?<=。)/).map(showT2).join(""));
""", ""),
    # strings
    ("""    srvLab: "Server mode", srvSwitch: "Use the LLM on a server to rewrite the explanation and answer the other questions",
    srvNote: "Only scores and face-part names are sent, never the photo. The explanation server has to be started separately; if it cannot be reached, the page uses the code template.",
    srvUrl: "Server URL", styleAria: "Explanation style",
    styleGeneral: "General explanation", stylePro: "Expert explanation<small>Includes more numbers</small>",
""", ""),
    ("""    badge: { llm: "LLM-written, passed the automatic checks", llmCode: "LLM wording, numbers and score note by code; passed the checks", template: "Template", fixed: "Fixed answer" },
    rewriting: "LLM rewriting…", thinking: "Thinking…",
    chipNeedEv: "The other four questions need an evidence model.",
    chipNeedSrv: "The other four questions need server mode (turn it on in Settings).",
    qaFail: "Cannot reach the server, so this question cannot be answered right now.",
    srvConnecting: "Connecting…", srvOk: "Connected. Explanations will be rewritten by the LLM.",
    srvFail: "Cannot reach the server; explanations use the code template.",
""", """    badge: { template: "Composed by code, checked", fixed: "Fixed answer" },
"""),
    ("""    srvLab: "伺服器模式", srvSwitch: "用伺服器上的 LLM 改寫解釋、回答其餘問題",
    srvNote: "只會傳送分數與部位名稱，不會傳送照片。需要另外啟動解釋伺服器；連不上時自動改用程式模板。",
    srvUrl: "伺服器網址", styleAria: "解釋風格",
    styleGeneral: "一般說明", stylePro: "專業說明<small>附上更多數值</small>",
""", ""),
    ("""    badge: { llm: "LLM 生成，已通過自動檢查", llmCode: "LLM 撰寫文字，數字與分數說明由程式加上，已通過檢查", template: "模板", fixed: "固定回答" },
    rewriting: "LLM 改寫中…", thinking: "思考中…",
    chipNeedEv: "其餘四題需要證據版模型。",
    chipNeedSrv: "其餘四題需要在「設定」開啟伺服器模式。",
    qaFail: "連不上伺服器，這題暫時無法回答。",
    srvConnecting: "連線中…", srvOk: "已連線。解釋會由 LLM 改寫。", srvFail: "連不上伺服器，解釋改用程式模板。",
""", """    badge: { template: "程式組成，已查核", fixed: "固定回答" },
"""),
]
t = P.read_text(encoding="utf-8")
if 'id="srvOn"' not in t:
    print("already patched"); raise SystemExit
bak = HERE / "index_pre_noserver_20261029.html"
if not bak.exists():
    shutil.copy2(P, bak)
for old, new in EDITS:
    assert t.count(old) == 1, ("anchor", t.count(old), old[:80])
    t = t.replace(old, new)
for k in ("srvOn", "srvUrl", "srvStatus", "NLClient.explain", "NLClient.qa", "NLClient.health", "showServer", "checkServer", "nlstyle"):
    assert k not in t, ("left", k)
P.write_text(t, encoding="utf-8"); print("patched index.html; backup", bak.name)
