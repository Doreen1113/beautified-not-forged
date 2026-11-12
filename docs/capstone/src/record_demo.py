"""Record the browser demo (docs/demo_ru) in headless Chrome over the DevTools Protocol and write docs/capstone/demo.gif.

No ffmpeg on this machine, so the output is an animated GIF (1280x800). Frames are periodic Page.captureScreenshot calls;
each step's frames are re-timed to a fixed on-screen length and a caption is burned in with PIL.
If the NL server (nl_v5/nl_server.py) answers on --nl-url, the server-mode steps are recorded too; this script does not
start or stop that server.

--lang zh (default): page opened with ?lang=zh, Chinese captions -> demo.gif, src/record_demo_log.json
--lang en          : page opened with ?lang=en, English captions -> demo_en.gif, src/record_demo_log_en.json
Captions of steps 5 and 7 follow the server's reply: template / code answer, LLM words + code numbers (design p3,
reply field code_added), or LLM answer.
Server mode uses the General style. The page's fetch is wrapped so the log also holds every request sent to the NL server
(the facts record) and its reply, for checking the recorded LLM texts against the facts.

  python docs/capstone/src/record_demo.py [--lang en] [--nl-url http://127.0.0.1:8787] [--llm-q 0]
"""
import argparse
import asyncio
import base64
import io
import json
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import websockets
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
DEMO = ROOT / "docs" / "demo_ru"; OUT = ROOT / "docs" / "capstone"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
W, H = 1280, 800
FONTS = {"zh": (ImageFont.truetype("C:/Windows/Fonts/msjhbd.ttc", 28), ImageFont.truetype("C:/Windows/Fonts/msjh.ttc", 18)),
         "en": (ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 24), ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 17))}


class Quiet(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(DEMO), **k)

    def log_message(self, *a):
        pass


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); return s.getsockname()[1]


class CDP:
    def __init__(self, ws):
        self.ws, self.n = ws, 0

    async def call(self, method, **params):
        self.n += 1; mid = self.n
        await self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            m = json.loads(await self.ws.recv())
            if m.get("id") == mid:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})

    async def js(self, expr):
        r = await self.call("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        return r.get("result", {}).get("value")


class Rec:
    def __init__(self, cdp):
        self.cdp, self.frames = cdp, []   # (segment, t, PIL image)
        self.seg = None

    async def snap(self):
        r = await self.cdp.call("Page.captureScreenshot", format="png")
        self.frames.append((self.seg, time.time(), Image.open(io.BytesIO(base64.b64decode(r["data"]))).convert("RGB")))

    async def hold(self, secs, every=0.25):
        t0 = time.time()
        while time.time() - t0 < secs:
            await self.snap(); await asyncio.sleep(every)

    async def until(self, expr, timeout=120, every=0.25):
        t0 = time.time()
        while time.time() - t0 < timeout:
            await self.snap()
            if await self.cdp.js(expr):
                return True
            await asyncio.sleep(every)
        return False


QUESTIONS = {  # nl_core.QUESTIONS / nl_core_en.QUESTIONS_EN order
    "zh": ["為什麼判定為假？", "哪裡被改了？", "有沒有美顏？", "這個分數代表什麼？", "可以確定嗎？", "和原圖比差在哪？", "是誰？", "為什麼不是真的？"],
    "en": ["Why is it judged fake?", "Where was it changed?", "Was it retouched?", "What does this score mean?", "Is this certain?",
           "Where does it differ from the original photo?", "Who is this?", "Why is it not real?"]}

# page texts the script waits on (index.html I18N srvOk / rewriting / thinking) and the corner tag
UI = {"zh": {"srvOk": "已連線", "rewriting": "改寫中", "thinking": "思考中", "tag": "實機錄影（headless Chrome）"},
      "en": {"srvOk": "Connected", "rewriting": "rewriting", "thinking": "Thinking", "tag": "Live recording (headless Chrome)"}}

SEGMENTS_EN = [  # key, caption, seconds on screen
    ("load", "1. Open the page: face detection and the analysis model load in the browser; no upload", 6.0),
    ("ex3", "2. Example 3 (commercial retouch, eye enlargement): judged retouched, operations listed", 9.0),
    ("ex2", "3. Example 2 (partial forgery, mouth): judged fake; outline and text point to the mouth", 9.0),
    ("models", "4. Settings: three analysis models (EfficientNet-B4 evidence model is the default)", 6.0),
    ("server", "5. Server mode, General style: Qwen2.5-7B rewrites; shown only if it passes the checks", 9.0),
    ("fixed", "6. Fixed question \"Is this certain?\": answered by code, no LLM", 5.0),
    ("llmq", "7. \"{q}\": LLM answer; if it fails the checks, the code answer is shown", 8.0),
]
FIXED_QI = (3, 4, 5, 6)   # nl_core.FIXED_QA / nl_core_en.FIXED_QA_EN: answered by code, no LLM
FIXED_STEP7 = {"en": "7. \"{q}\": also a fixed code answer, no LLM", "zh": "7. 追問「{q}」：同樣是固定的程式回答，不經過 LLM"}
# captions used when the server returned the code fallback (source "template"), so the caption says what is on screen
TEMPLATE_STEP5 = {"en": "5. Server mode, General style: LLM text did not pass the checks; template shown",
                  "zh": "5. 伺服器模式（範例 2）：LLM 文字未通過查核，顯示程式範本"}
TEMPLATE_STEP7 = {"en": "7. \"{q}\": LLM answer did not pass the checks; code answer shown",
                  "zh": "7. 追問「{q}」：LLM 回答未通過查核，顯示程式答案"}
# design p3 (PRE_DECLARED_NL 17): the LLM writes the words only; code adds the score in parentheses and the calibration
# sentence (reply field code_added). Captions say so when that is what is on screen.
LLMCODE_STEP5 = {"en": "5. Server mode (General): LLM writes the words; code adds the score and calibration sentence",
                 "zh": "5. 伺服器模式（範例 2）：LLM 寫文字，分數與校準句由程式加上，通過查核"}
LLM_STEP7 = {"en": "7. \"{q}\": LLM answer, no numbers; passed the checks",
             "zh": "7. 追問「{q}」：LLM 回答，通過查核"}

SEGMENTS = [  # key, caption, seconds on screen
    ("load", "1. 開啟網頁：人臉偵測與分析模型在瀏覽器內載入，照片不上傳", 6.0),
    ("ex3", "2. 範例 3（商用美顏：眼睛放大）：判定為美顏，列出達門檻的操作", 9.0),
    ("ex2", "3. 範例 2（局部偽造：嘴巴）：判定為偽造，證據輪廓與解釋指向嘴巴", 9.0),
    ("models", "4. 設定：三種分析模型可選（EfficientNet-B4 證據版為預設）", 6.0),
    ("server", "5. 伺服器模式（範例 2）：Qwen2.5-7B 改寫，通過查核才顯示", 9.0),
    ("fixed", "6. 固定問題「可以確定嗎？」：由程式回答，不經過 LLM", 5.0),
    ("llmq", "7. 追問「{q}」：LLM 回答，未通過查核就改用程式答案", 8.0),
]


async def run(chrome_port, base, nl_ok, log, llm_q, lang):
    ui = UI[lang]
    for _ in range(100):
        try:
            tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{chrome_port}/json/list", timeout=1).read()); break
        except Exception:
            await asyncio.sleep(0.2)
    page = next(t for t in tabs if t["type"] == "page")
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=2 ** 28) as ws:
        cdp = CDP(ws); await cdp.call("Page.enable"); await cdp.call("Runtime.enable")
        await cdp.call("Emulation.setDeviceMetricsOverride", width=1024, height=640, deviceScaleFactor=1.25, mobile=False)  # 1280x800 pixels, larger text
        await cdp.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
        rec = Rec(cdp)
        state = "document.documentElement.dataset.state || ''"

        # keep every NL-server request (facts record) and reply, for checking the recorded LLM texts
        await cdp.call("Page.addScriptToEvaluateOnNewDocument", source="""
          window.__nl = []; const _f = window.fetch;
          window.fetch = async (u, o) => { const r = await _f(u, o);
            if (o && o.method === 'POST') { r.clone().json().then(j => window.__nl.push({url: String(u), req: JSON.parse(o.body), res: j})).catch(() => {}); }
            return r; };""")
        rec.seg = "load"
        await cdp.call("Page.navigate", url=base + f"index.html?lang={lang}")
        await asyncio.sleep(0.3)
        ok = await rec.until(f"['ready','error'].includes({state})", timeout=180)
        log["load_state"] = await cdp.js(state); await rec.hold(1.0)

        for seg, n in (("ex3", 3), ("ex2", 2)):  # example 2 last, so server mode works on it
            rec.seg = seg
            await cdp.js(f"document.querySelector('.ex[data-ex=\"{n}\"]').scrollIntoView({{block:'center'}})")
            await rec.hold(0.6)
            await cdp.js(f"document.querySelector('.ex[data-ex=\"{n}\"]').click()")
            await asyncio.sleep(0.2)
            await rec.until(f"['done','error','error-photo'].includes({state})", timeout=60)
            log[seg] = await cdp.js("(document.getElementById('body')||{}).innerText||''")
            await cdp.js("document.getElementById('result').scrollIntoView({block:'start'}); window.scrollBy(0,-12)")
            await rec.hold(3.0)
            await cdp.js("window.scrollBy({top: 220, behavior: 'smooth'})")
            await rec.hold(2.5)

        rec.seg = "models"
        await cdp.js("document.getElementById('openSettings').click()")
        await asyncio.sleep(0.3)
        await cdp.js("document.getElementById('settings').scrollIntoView({block:'start'}); window.scrollBy(0,-12)")
        await rec.hold(3.5)

        if nl_ok:
            rec.seg = "server"
            await cdp.js("document.getElementById('srvOn').click()")
            await cdp.js("document.querySelector('input[name=nlstyle][value=general]').click()")
            await rec.until(f"(document.getElementById('srvStatus').textContent||'').includes('{ui['srvOk']}')", timeout=30)
            await rec.hold(1.5)
            await cdp.js("document.getElementById('result').scrollIntoView({block:'start'}); window.scrollBy(0,-12)")
            await rec.until(f"!((document.getElementById('srcBadge')||{{}}).textContent||'').includes('{ui['rewriting']}')", timeout=60)
            log["server_badge"] = await cdp.js("document.getElementById('srcBadge').textContent")
            log["server_text"] = await cdp.js("document.getElementById('explain').innerText")
            await cdp.js("document.getElementById('explain').scrollIntoView({block:'center'})")
            await rec.hold(4.0)

            rec.seg = "fixed"
            await cdp.js("document.getElementById('chips').scrollIntoView({block:'center'})")
            await rec.hold(0.8)
            await cdp.js("document.querySelectorAll('.chip')[4].click()")
            await rec.hold(3.0)
            log["fixed_answer"] = await cdp.js("document.getElementById('answer').innerText")

            rec.seg = "llmq"
            await cdp.js(f"document.querySelectorAll('.chip')[{llm_q}].click()")
            await rec.until(f"!(document.getElementById('answer').innerText||'').includes('{ui['thinking']}')", timeout=60)
            await rec.hold(3.5)
            log["llm_question_index"] = llm_q
            log["llm_answer"] = await cdp.js("document.getElementById('answer').innerText")
            await asyncio.sleep(0.5)
            log["nl_calls"] = await cdp.js("window.__nl")
        return rec.frames


def caption(img, text, lang):
    FONT, FONT_S = FONTS[lang]
    img = img.copy(); d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, H - 64, W, H], fill=(20, 28, 38, 225))
    d.text((28, H - 32), text, font=FONT, fill=(255, 255, 255), anchor="lm")
    tag = UI[lang]["tag"]
    if 28 + d.textlength(text, font=FONT) + 24 < W - 20 - d.textlength(tag, font=FONT_S):  # skip the tag rather than overlap
        d.text((W - 20, H - 32), tag, font=FONT_S, fill=(190, 198, 207), anchor="rm")
    return img


def assemble(frames, out_gif, qtext, lang, fixed_q=False, server_caption=None, llmq_caption=None):
    segs = [s for s in (SEGMENTS_EN if lang == "en" else SEGMENTS) if any(f[0] == s[0] for f in frames)]
    segs = [(k, FIXED_STEP7[lang] if (k == "llmq" and fixed_q) else (server_caption if (k == "server" and server_caption)
             else (llmq_caption if (k == "llmq" and llmq_caption) else t)), d)
            for k, t, d in segs]
    out, durs = [], []
    for key, text, secs in segs:
        text = text.replace("{q}", qtext)
        fs = [f for f in frames if f[0] == key]
        ts = [f[1] for f in fs] + [fs[-1][1] + 0.25]
        real = [max(ts[i + 1] - ts[i], 0.01) for i in range(len(fs))]
        k = secs / sum(real)
        for (_, _, im), r in zip(fs, real):
            im = caption(im, text, lang); dur = r * k
            if out and im.tobytes() == out[-1].tobytes():
                durs[-1] += dur
            else:
                out.append(im); durs.append(dur)
    # GIF timing is in 10 ms units; keep total length while rounding
    ms = [max(20, int(round(d * 100)) * 10) for d in durs]
    pal = [im.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE) for im in out]
    pal[0].save(out_gif, save_all=True, append_images=pal[1:], duration=ms, loop=0, optimize=True, disposal=1)
    return len(out), sum(ms) / 1000


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--nl-url", default="http://127.0.0.1:8787")
    ap.add_argument("--llm-q", type=int, default=0, help="index of the question chip asked in step 7 (0 = why fake; 3-6 are fixed code answers)")
    ap.add_argument("--server-caption", default=None, help="replace the step-5 caption (e.g. to note a recorded text that fails the fact check)")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh", help="page and caption language (en -> demo_en.gif)")
    a = ap.parse_args()
    try:
        nl_ok = bool(json.loads(urllib.request.urlopen(a.nl_url + "/health", timeout=3).read()).get("ok"))
    except Exception:
        nl_ok = False
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Quiet); threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    cp = free_port(); prof = tempfile.mkdtemp(prefix="capstone_cdp_")
    proc = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-extensions",
                             f"--remote-debugging-port={cp}", f"--user-data-dir={prof}", "--hide-scrollbars",
                             f"--window-size={W},{H}", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = {"lang": a.lang, "nl_server_reachable": nl_ok, "http_port": srv.server_address[1]}
    try:
        frames = asyncio.run(run(cp, base, nl_ok, log, a.llm_q, a.lang))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
        srv.shutdown()
    qtext = QUESTIONS[a.lang][a.llm_q]
    gif = OUT / ("demo_en.gif" if a.lang == "en" else "demo.gif")
    # when the server shipped the code fallback, the caption says so (unless a caption was given explicitly)
    calls = log.get("nl_calls") or []
    exp = next((c["res"] for c in calls if "/explain" in c["url"]), None); qa = next((c["res"] for c in calls if "/qa" in c["url"]), None)
    server_caption = a.server_caption or (TEMPLATE_STEP5[a.lang] if exp and exp.get("source") == "template" else
                                          LLMCODE_STEP5[a.lang] if exp and exp.get("source") == "llm" and exp.get("code_added") else None)
    llmq_caption = (TEMPLATE_STEP7[a.lang] if (qa and qa.get("source") == "template" and a.llm_q not in FIXED_QI) else
                    LLM_STEP7[a.lang] if (qa and qa.get("source") == "llm" and a.llm_q not in FIXED_QI) else None)
    n, secs = assemble(frames, gif, qtext, a.lang, a.llm_q in FIXED_QI, server_caption, llmq_caption)
    log.update(step7_fixed_question=a.llm_q in FIXED_QI, server_caption=server_caption, llmq_caption=llmq_caption,
               server_source=exp and exp.get("source"), llmq_source=qa and qa.get("source"),
               server_prompt=exp and exp.get("prompt"), server_llm_text=exp and exp.get("llm_text"),
               server_code_added=exp and exp.get("code_added"), llmq_prompt=qa and qa.get("prompt"), llmq_llm_text=qa and qa.get("llm_text"))
    log.update(frames_captured=len(frames), frames_written=n, seconds=secs)
    (OUT / "src" / ("record_demo_log_en.json" if a.lang == "en" else "record_demo_log.json")).write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(log, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
