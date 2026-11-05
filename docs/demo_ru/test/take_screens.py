"""Screenshots of index.html in headless Chrome over the Chrome DevTools Protocol (websockets; no Selenium/Playwright).

Serves docs/demo_ru over HTTP, opens the page at a given viewport, waits for the page's own state flag
(<html data-state="...">: loading -> ready -> busy -> done), optionally taps an example, and saves PNGs to test/screens/.
Also reports horizontal overflow (document scrollWidth > viewport width) for each shot.

  python docs/demo_ru/test/take_screens.py
"""
import asyncio
import io
import base64
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

HERE = Path(__file__).resolve().parent; DEMO = HERE.parent; OUT = HERE / "screens"
sys.path.insert(0, str(HERE))
from run_test_headless import find_browser  # noqa: E402
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

SHOTS = [  # name, width, height, mobile, example to tap (None = empty state), dark theme, language (page default = English)
    ("412_empty", 412, 900, True, None, False, None),
    ("412_example2", 412, 900, True, 2, False, None),
    ("1366_example3", 1366, 900, False, 3, False, None),
    ("412_example3_dark", 412, 900, True, 3, True, None),
    ("1366_example2", 1366, 900, False, 2, False, None),
    ("412_example3_zh", 412, 900, True, 3, False, "zh"),
]


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

    async def wait_state(self, states, timeout=300):
        t0 = time.time()
        while time.time() - t0 < timeout:
            s = await self.js("document.documentElement.dataset.state || ''")
            if s in states:
                return s
            await asyncio.sleep(0.25)
        raise TimeoutError(f"page state never reached {states}")


async def shoot(cdp, base, name, w, h, mobile, example, dark, lang=None):
    await cdp.call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=1, mobile=mobile)
    await cdp.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "dark" if dark else "light"}])
    await cdp.call("Page.navigate", url=base + "index.html" + (f"?lang={lang}" if lang else ""))
    await asyncio.sleep(0.5)
    st = await cdp.wait_state({"ready", "error"})
    if example is not None and st == "ready":
        await cdp.js(f'document.querySelector(\'.ex[data-ex="{example}"]\').click()')
        await asyncio.sleep(0.3)
        st = await cdp.wait_state({"done", "error", "error-photo"})
        await cdp.js("document.getElementById('result').scrollIntoView({block:'start'}); window.scrollBy(0, -8)") if mobile else None
    await asyncio.sleep(0.6)  # fonts / transitions
    info = await cdp.js("({sw: document.documentElement.scrollWidth, iw: innerWidth, state: document.documentElement.dataset.state, lang: document.documentElement.lang,"
                        " text: (document.getElementById('body')||{}).innerText || ''})")
    img = await cdp.call("Page.captureScreenshot", format="png")
    (OUT / f"{name}.png").write_bytes(base64.b64decode(img["data"]))
    full = await cdp.call("Page.captureScreenshot", format="png", captureBeyondViewport=True,
                          clip={"x": 0, "y": 0, "width": w, "height": await cdp.js("document.documentElement.scrollHeight"), "scale": 1})
    (OUT / f"{name}_full.png").write_bytes(base64.b64decode(full["data"]))
    return {"shot": name, "lang": info["lang"], "state": info["state"], "scrollWidth": info["sw"], "innerWidth": info["iw"],
            "horizontal_overflow": info["sw"] > info["iw"], "result_text": info["text"][:600]}


async def main_async(chrome_port, base):
    for _ in range(100):
        try:
            tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{chrome_port}/json/list", timeout=1).read()); break
        except Exception:
            await asyncio.sleep(0.2)
    page = next(t for t in tabs if t["type"] == "page")
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=2 ** 28) as ws:
        cdp = CDP(ws); await cdp.call("Page.enable"); await cdp.call("Runtime.enable")
        rows = []
        for s in SHOTS:
            rows.append(await shoot(cdp, base, *s)); print(json.dumps(rows[-1], ensure_ascii=False), flush=True)
        return rows


def main():
    OUT.mkdir(exist_ok=True)
    b = find_browser()
    if b is None:
        sys.exit("No Chromium-based browser found.")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Quiet); threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    cp = free_port(); prof = tempfile.mkdtemp(prefix="demo_ru_cdp_")
    proc = subprocess.Popen([b, "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-extensions", f"--remote-debugging-port={cp}",
                             f"--user-data-dir={prof}", "--hide-scrollbars", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        rows = asyncio.run(main_async(cp, base))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
        srv.shutdown()
    (OUT / "screens.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(0 if all(not r["horizontal_overflow"] for r in rows) else 1)


if __name__ == "__main__":
    main()
