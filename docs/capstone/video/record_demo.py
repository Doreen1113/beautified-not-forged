"""Record the browser page (docs/demo_ru/index.html) for the system scene: headless Chrome over the DevTools protocol,
a cursor drawn into the page, Page.startScreencast frames with their timestamps.

Sequence: page ready (models loaded) -> cursor moves to Example 2 (FF++ test frame, mouth replaced) -> click -> result ->
scroll to the sentences and the follow-up questions -> click "Where does it differ from the original photo?".

python docs/capstone/video/record_demo.py -> demo/f0000.jpg ..., demo/demo_frames.js ({fps, times[], w, h, n}), demo/record.json
"""
import asyncio
import base64
import json
import socket
import subprocess
import sys
import tempfile
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import websockets

H = Path(__file__).resolve().parent; B = H.parents[2]; DEMO = B / "docs/demo_ru"; OUT = H / "demo"
sys.path.insert(0, str(DEMO / "test"))
from run_test_headless import find_browser  # noqa: E402

W, Hh = 1180, 760
CURSOR = """(() => {
  const c = document.createElement('div'); c.id = '__cur';
  c.style.cssText = 'position:fixed;left:-40px;top:-40px;width:22px;height:22px;border-radius:50%;background:rgba(15,77,146,.55);border:2.5px solid #fff;box-shadow:0 0 0 1.5px rgba(0,0,0,.35);z-index:99999;pointer-events:none;transform:translate(-50%,-50%);transition:left .7s cubic-bezier(.4,0,.2,1), top .7s cubic-bezier(.4,0,.2,1), background .15s';
  document.body.appendChild(c);
  window.__moveCur = (x, y) => { c.style.left = x + 'px'; c.style.top = y + 'px'; };
  window.__pressCur = (on) => { c.style.background = on ? 'rgba(213,94,0,.75)' : 'rgba(15,77,146,.55)'; };
})()"""


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
        self.ws, self.n, self.frames, self.events = ws, 0, [], []

    async def call(self, method, **params):
        self.n += 1; mid = self.n
        await self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            m = json.loads(await self.ws.recv())
            if m.get("id") == mid:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})
            await self.event(m)

    async def event(self, m):
        if m.get("method") == "Page.screencastFrame":
            p = m["params"]; self.frames.append((p["metadata"]["timestamp"], p["data"]))
            await self.ws.send(json.dumps({"id": 0, "method": "Page.screencastFrameAck", "params": {"sessionId": p["sessionId"]}}))

    async def pump(self, secs):
        """Receive events (screencast frames) for a while."""
        t0 = time.time()
        while time.time() - t0 < secs:
            try:
                m = json.loads(await asyncio.wait_for(self.ws.recv(), timeout=max(0.01, secs - (time.time() - t0))))
            except asyncio.TimeoutError:
                break
            if "id" not in m or m["id"] == 0:
                await self.event(m)

    async def js(self, expr):
        r = await self.call("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        return r.get("result", {}).get("value")

    async def wait_state(self, states, timeout=300):
        t0 = time.time()
        while time.time() - t0 < timeout:
            if (await self.js("document.documentElement.dataset.state || ''")) in states:
                return
            await self.pump(0.2)
        raise TimeoutError(states)

    async def move(self, x, y, secs=0.9):
        await self.js(f"__moveCur({x}, {y})"); await self.call("Input.dispatchMouseEvent", type="mouseMoved", x=x, y=y); await self.pump(secs)

    async def click(self, x, y):
        await self.js("__pressCur(true)")
        await self.call("Input.dispatchMouseEvent", type="mousePressed", x=x, y=y, button="left", clickCount=1); await self.pump(0.12)
        await self.call("Input.dispatchMouseEvent", type="mouseReleased", x=x, y=y, button="left", clickCount=1)
        await self.js("__pressCur(false)")

    async def centre(self, sel):
        return await self.js(f"(() => {{ const r = document.querySelector('{sel}').getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; }})()")


async def run(port, base):
    for _ in range(100):
        try:
            import urllib.request
            tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=1).read()); break
        except Exception:
            await asyncio.sleep(0.2)
    page = next(t for t in tabs if t["type"] == "page")
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=2 ** 28) as ws:
        cdp = CDP(ws); await cdp.call("Page.enable"); await cdp.call("Runtime.enable")
        await cdp.call("Emulation.setDeviceMetricsOverride", width=W, height=Hh, deviceScaleFactor=1, mobile=False)
        await cdp.call("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": "light"}])
        await cdp.call("Page.navigate", url=base + "index.html"); await asyncio.sleep(0.5)
        await cdp.wait_state({"ready", "error"}); await cdp.js(CURSOR)
        await cdp.js("window.scrollTo(0, 0)"); await asyncio.sleep(0.5)
        log = []; t0 = time.time()
        await cdp.call("Page.startScreencast", format="jpeg", quality=88, maxWidth=W, maxHeight=Hh, everyNthFrame=1)
        await cdp.move(W * 0.55, Hh * 0.45, 0.1); await cdp.pump(1.0); log.append(("idle", time.time() - t0))
        x, y = await cdp.centre('.ex[data-ex="2"]'); await cdp.move(x, y, 1.1); log.append(("hover example 2", time.time() - t0))
        await cdp.click(x, y); log.append(("click example 2", time.time() - t0))
        await cdp.wait_state({"done", "error", "error-photo"}); log.append(("done", time.time() - t0)); await cdp.pump(2.2)
        top = await cdp.js("document.getElementById('result').getBoundingClientRect().top + window.scrollY - 24")
        await cdp.js(f"window.scrollTo({{top: {top}, behavior: 'smooth'}})"); await cdp.pump(1.6); log.append(("scroll result", time.time() - t0))
        await cdp.pump(1.6)
        chip = await cdp.js("(() => { const c = [...document.querySelectorAll('#chips .chip')].find(b => /differ/i.test(b.textContent)); if (!c) return null;"
                            " const r = c.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2, r.bottom]; })()")
        if chip:
            if chip[2] > Hh - 40:
                await cdp.js(f"window.scrollBy({{top: {chip[2] - Hh + 120}, behavior: 'smooth'}})"); await cdp.pump(1.2)
                chip = await cdp.js("(() => { const c = [...document.querySelectorAll('#chips .chip')].find(b => /differ/i.test(b.textContent)); const r = c.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2, r.bottom]; })()")
            await cdp.move(chip[0], chip[1], 1.0); await cdp.click(chip[0], chip[1]); log.append(("click chip", time.time() - t0)); await cdp.pump(3.0)
        await cdp.pump(0.8); log.append(("end", time.time() - t0))
        await cdp.call("Page.stopScreencast"); await cdp.pump(0.3)
        info = await cdp.js("({state: document.documentElement.dataset.state, text: (document.getElementById('body')||{}).innerText || ''})")
        return cdp.frames, log, info


def main():
    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("f*.jpg"):
        f.unlink()
    b = find_browser()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Quiet); threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    cp = free_port(); prof = tempfile.mkdtemp(prefix="film_demo_cdp_")
    proc = subprocess.Popen([b, "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-extensions", f"--remote-debugging-port={cp}",
                             f"--user-data-dir={prof}", "--hide-scrollbars", f"--window-size={W},{Hh}", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        frames, log, info = asyncio.run(run(cp, base))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
        srv.shutdown()
    frames.sort(key=lambda f: f[0]); t0 = frames[0][0]
    # keep at most 30 frames per second
    kept, last = [], -1
    for ts, data in frames:
        if ts - t0 - last >= 1 / 30 - 1e-6:
            kept.append((ts - t0, data)); last = ts - t0
    for i, (_, data) in enumerate(kept):
        (OUT / f"f{i:04d}.jpg").write_bytes(base64.b64decode(data))
    times = [round(t, 4) for t, _ in kept]
    (OUT / "demo_frames.js").write_text("window.DEMO = " + json.dumps({"w": W, "h": Hh, "n": len(kept), "times": times}) + ";\n", encoding="utf-8")
    (OUT / "record.json").write_text(json.dumps({"frames_received": len(frames), "frames_kept": len(kept), "duration": times[-1], "log": log,
                                                 "final_state": info["state"], "result_text": info["text"][:800]}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"frames {len(frames)} -> kept {len(kept)}, {times[-1]:.1f} s; final state {info['state']}")
    for name, t in log:
        print(f"  {t:5.1f}s {name}")


if __name__ == "__main__":
    main()
