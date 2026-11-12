"""Render an HTML figure to a vector PDF (and a 2x PNG preview) with headless Chrome over the DevTools protocol.
The HTML sets its own page size with @page { size: W H; margin: 0 }. Usage:
  python render_html_fig.py figs/fig_system.html            -> figs/fig_system.pdf, figs/fig_system.png
Reuses the browser discovery of docs/demo_ru/test/run_test_headless.py."""
import asyncio
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

B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B / "docs/demo_ru/test"))
from run_test_headless import find_browser  # noqa: E402

SRC = Path(sys.argv[1]).resolve(); DIR = SRC.parent
WIDTH_PX = int(sys.argv[2]) if len(sys.argv) > 2 else 560     # CSS px of the page width, for the PNG preview


class Quiet(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(DIR), **k)

    def log_message(self, *a):
        pass


async def call(ws, n, method, **params):
    await ws.send(json.dumps({"id": n, "method": method, "params": params}))
    while True:
        m = json.loads(await ws.recv())
        if m.get("id") == n:
            if "error" in m:
                raise RuntimeError(f"{method}: {m['error']}")
            return m.get("result", {})


async def run(port, base):
    for _ in range(100):
        try:
            tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=1).read()); break
        except Exception:
            await asyncio.sleep(0.2)
    page = next(t for t in tabs if t["type"] == "page")
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=2 ** 28) as ws:
        n = 0
        n += 1; await call(ws, n, "Page.enable")
        n += 1; await call(ws, n, "Emulation.setDeviceMetricsOverride", width=WIDTH_PX, height=900, deviceScaleFactor=3, mobile=False)
        n += 1; await call(ws, n, "Page.navigate", url=base + SRC.name)
        await asyncio.sleep(1.2)
        n += 1; r = await call(ws, n, "Runtime.evaluate", expression="document.fonts.ready.then(()=>({w: document.body.scrollWidth, h: document.body.scrollHeight}))",
                               returnByValue=True, awaitPromise=True)
        dims = r["result"]["value"]; print("body px", dims)
        n += 1; shot = await call(ws, n, "Page.captureScreenshot", format="png", captureBeyondViewport=True,
                                  clip={"x": 0, "y": 0, "width": dims["w"], "height": dims["h"], "scale": 1})
        SRC.with_suffix(".png").write_bytes(base64.b64decode(shot["data"]))
        n += 1; pdf = await call(ws, n, "Page.printToPDF", printBackground=True, preferCSSPageSize=False,
                                 paperWidth=dims["w"] / 96, paperHeight=dims["h"] / 96 + 0.002,
                                 marginTop=0, marginBottom=0, marginLeft=0, marginRight=0)
        SRC.with_suffix(".pdf").write_bytes(base64.b64decode(pdf["data"]))
        print("wrote", SRC.with_suffix(".pdf").name, SRC.with_suffix(".png").name)


def main():
    b = find_browser()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Quiet); threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); cp = s.getsockname()[1]
    prof = tempfile.mkdtemp(prefix="fig_cdp_")
    proc = subprocess.Popen([b, "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-extensions", f"--remote-debugging-port={cp}",
                             f"--user-data-dir={prof}", "--hide-scrollbars", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        asyncio.run(run(cp, base))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
        srv.shutdown()


if __name__ == "__main__":
    main()
