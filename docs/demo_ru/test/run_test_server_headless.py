"""Server mode, headless (pattern of run_test_evidence_headless.py): start nl_server.py (Qwen2.5-7B, port 8787), serve
docs/demo_ru over HTTP, run test/test_server_page.html in headless Chromium (10 fixture records through the page path:
MediaPipe -> ru4e_effb4.onnx -> masks -> record -> NLClient.explain general/pro + NLClient.qa x 8), then re-check every
returned text in Python: validate_text.validate via nl_core.gate_check (H1-H6, the mode's sentence range) and
nl_core.gate_check_v2 (+ G7 + facts). Stops only the server process this script started.

  python docs/demo_ru/test/run_test_server_headless.py [--lang en|zh|both]   -> test/server_headless_result.json
                                                                              (both: + server_headless_result_en.json)
2026-10-15: lang (default both). English texts are re-checked with nl_v5/validate_text_en (gate_check_en H1-H6 and
gate_check_v2_en + G7 + facts); the page's FIXED_QA_EN must equal nl_core_en.FIXED_QA_EN. One server process serves both.
2026-10-15 (PRE_DECLARED_NL 16): the server gates with gate v3 (gate_v3.py: v2 + G8 + G9); every returned text is also
re-checked with gate v3 (gate_check_v3_en / gate_check_v3_zh) and must pass it.
2026-10-15 (PRE_DECLARED_NL 17): the server's default prompt is design p3. For every LLM text the LLM's own part
(`llm_text`) is re-checked with nl_p3.llm_gate (H1-H5, G7, G8, G9, G10 no number, the facts it must carry) and the shown
text must equal nl_p3.compose(record, llm_text) (styles: code parentheticals + calibration sentence; Q&A: unchanged).
2026-10-15 (PRE_DECLARED_NL 17.8): Chinese default prompt p3r1z; a Chinese text that shows an English class key
(fake / real / filter) or the word "evidence" fails. The p3r1 run is kept as server_headless_result_p3r1.json.
"""
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; DEMO = HERE.parent; ROOT = DEMO.parents[1]
NL = ROOT / "results/research/explain_vlm_20261012/nl_v5"
sys.path.insert(0, str(NL)); sys.path.insert(0, str(HERE))
from run_test_evidence_headless import Handler, State, find_browser  # noqa: E402

PORT = 8787
LANGS = ("en", "zh")
PAYLOADS = {}


def port_free(p):
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", p)) != 0


def main():
    global LANGS
    import nl_core as N
    if "--lang" in sys.argv:
        v = sys.argv[sys.argv.index("--lang") + 1]
        LANGS = ("en", "zh") if v == "both" else (v,)
    if not port_free(PORT):
        sys.exit(f"port {PORT} is in use; not starting a second server")
    b = find_browser()
    if b is None:
        sys.exit("No Chromium-based browser found.")
    log = open(HERE / "server_headless_server.log", "w", encoding="utf-8")
    t0 = time.time()
    proc = subprocess.Popen([sys.executable, str(NL / "nl_server.py"), "--port", str(PORT)], cwd=str(NL), stdout=log, stderr=subprocess.STDOUT,
                            env={**os.environ, "PYTHONIOENCODING": "utf-8", "TF_CPP_MIN_LOG_LEVEL": "3", "USE_TF": "0"})
    load_s = wall = None
    try:
        for _ in range(900):
            if proc.poll() is not None:
                sys.exit("server exited; see test/server_headless_server.log")
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=2).read(); load_s = time.time() - t0; break
            except Exception:
                time.sleep(1)
        print(f"server ready after {load_s:.1f} s (pid {proc.pid})", flush=True)
        srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler); port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        wall = {}
        for lg in LANGS:
            State.payload = None; State.done.clear()   # the hold of the previous language run is released
            url = f"http://127.0.0.1:{port}/test/test_server_page.html?srv=http://127.0.0.1:{PORT}&lang={lg}"
            cmd = [b, "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-extensions", "--window-size=1200,900", "--dump-dom", url]
            t1 = time.time(); subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=3600)
            wall[lg] = time.time() - t1; PAYLOADS[lg] = State.payload
        srv.shutdown()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()
    total = 0
    for lg in LANGS:
        total += check(lg, PAYLOADS.get(lg) or {}, b, load_s, wall[lg], N)
    sys.exit(0 if total == 0 else 1)


def check(lg, P, b, load_s, wall, N):
    import nl_core_en as E
    import validate_text_en as VE
    import gate_v3 as G3
    import nl_p3 as P3
    en = lg == "en"
    if P.get("err") or not P.get("results"):
        print(f"[{lg}] page error: {P.get('err')}"); return 1
    rows = []; fails = 0
    for r in P["results"]:
        j = N.ref_from_record(r["record"])
        for c in r["calls"]:
            mode = c.get("style") or "qa"; qi = c["question_id"] if c["kind"] == "qa" else None
            q = (E.QUESTIONS_EN if en else N.QUESTIONS)[qi] if qi is not None else None
            if en:
                g1 = VE.gate_check_en(j, c["text"], mode); g2 = VE.gate_check_v2_en(j, c["text"], mode, qi)
                g3 = G3.gate_check_v3_en(j, c["text"], mode, qi)
            else:
                g1 = N.gate_check(j, c["text"], mode); g2 = N.gate_check_v2(j, c["text"], mode, q)
                g3 = G3.gate_check_v3_zh(j, c["text"], mode, q)
            p3_ok = None
            if c["source"] == "llm" and c.get("prompt") in P3.PVS[lg]:
                lgt = P3.llm_gate(j, c.get("llm_text") or "", mode, lg, qi)
                p3_ok = (not lgt["any"]) and P3.compose(j, c.get("llm_text") or "", mode, lg) == c["text"]
            # PRE_DECLARED_NL 17.8: no Chinese text may show the English class key (fake / real / filter) or the term "evidence"
            key = None if en else (re.search(r"(?<![A-Za-z])(?:real|fake|filter)(?![A-Za-z])|evidence", c["text"], re.I) or [None])[0]
            ok = not g1["any"] and not g2["any_v2"] and not g3["any_v3"] and p3_ok is not False and key is None; fails += not ok
            rows.append({"lang": lg, "server_lang": c.get("lang"), "id": r["id"], "decision": j["decision"], "kind": c["kind"], "mode": mode, "question": q, "source": c["source"],
                         "server_gate_passed": c["gate"]["passed"], "attempts": c.get("attempts"),
                         "validate_text_H1toH6_pass": not g1["any"], "gate_v2_pass": not g2["any_v2"], "gate_v3_pass": not g3["any_v3"],
                         "prompt": c.get("prompt"), "llm_text": c.get("llm_text"), "code_added": c.get("code_added"),
                         "p3_llm_part_and_composition_pass": p3_ok, "english_key_in_zh": key,
                         "why": g3["why"], "server_ms": c["ms"], "client_ms": round(c["client_ms"], 1), "text": c["text"]})

    # routing v3: the page's offline fixed answers (nl_client.js FIXED_QA) must equal the server's (nl_core.FIXED_QA), and
    # exactly those questions must come back with source "fixed"
    client_fixed = P.get("client_fixed") or {}
    FX = dict(E.FIXED_QA_EN if en else N.FIXED_QA)
    fixed_same = client_fixed == FX
    fixed_routed = all((x["source"] == "fixed") == (x["question"] in FX) for x in rows if x["kind"] == "qa")
    lang_ok = all(x["server_lang"] == lg for x in rows)
    if not lang_ok:
        print(f"FAIL [{lg}] server answered in another language", flush=True); fails += 1
    if not fixed_same:
        print("FAIL client FIXED_QA differs from nl_core.FIXED_QA", flush=True); fails += 1
    if not fixed_routed:
        print("FAIL a question was routed differently from nl_core.FIXED_QA", flush=True); fails += 1

    def lat(sel):
        v = [x["client_ms"] for x in rows if sel(x)]
        return {"n": len(v), "median_ms": round(float(np.median(v)), 1), "p90_ms": round(float(np.percentile(v, 90)), 1), "max_ms": round(max(v), 1)} if v else None
    summ = {"lang": lg, "browser": b, "server_load_s": round(load_s, 1), "browser_process_s": round(wall, 1), "records": len(P["results"]), "texts": len(rows),
            "texts_failing_recheck": fails, "client_fixed_equals_server": fixed_same, "fixed_routing_as_declared": fixed_routed,
            "fixed_questions": list(FX), "server_lang_matches": lang_ok,
            "sources": {s: sum(x["source"] == s for x in rows) for s in ("llm", "template", "fixed")},
            "prompts": sorted({str(x["prompt"]) for x in rows}),
            "zh_texts_with_english_key": None if en else sum(x["english_key_in_zh"] is not None for x in rows),
            "llm_texts_rechecked_p3": sum(x["p3_llm_part_and_composition_pass"] is not None for x in rows),
            "regenerated": sum(1 for x in rows if x["attempts"] and len(x["attempts"]) > 1),
            "latency_client": {"explain_general": lat(lambda x: x["mode"] == "general"), "explain_pro": lat(lambda x: x["mode"] == "pro"),
                               "qa_llm": lat(lambda x: x["mode"] == "qa" and x["source"] != "fixed"), "qa_fixed": lat(lambda x: x["source"] == "fixed")},
            "note": "client_ms = browser fetch round trip incl. greedy generation and, when the gate fails, one sampled regeneration; "
                    "batch 1, bf16, RTX 6000 Ada; the page path (landmarks + ONNX) is not included",
            "rows": rows}
    (HERE / ("server_headless_result_en.json" if en else "server_headless_result.json")).write_text(json.dumps(summ, ensure_ascii=False, indent=1), encoding="utf-8")
    for x in rows:
        print(("PASS" if x["validate_text_H1toH6_pass"] and x["gate_v2_pass"] and x["gate_v3_pass"] and x["p3_llm_part_and_composition_pass"] is not False and x["english_key_in_zh"] is None else "FAIL"), lg, x["id"], x["mode"], x["question"] or "", x["source"],
              f"{x['client_ms']:.0f}ms", x["text"])
    print(json.dumps({k: v for k, v in summ.items() if k != "rows"}, ensure_ascii=False, indent=1))
    return fails


if __name__ == "__main__":
    main()
