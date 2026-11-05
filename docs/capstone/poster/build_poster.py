"""Print poster.html to poster.pdf (90 x 120 cm, the department template's page size) with headless Chrome over the DevTools
protocol, then rasterise the PDF for a look: preview/poster.png (whole page, ~1800 px tall) and preview/zoom_*.png (banner "115",
smallest text).

python docs/capstone/poster/build_poster.py
"""
import asyncio
import base64
import json
import socket
import subprocess
import sys
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import websockets

H = Path(__file__).resolve().parent; ROOT = H.parents[2]
sys.path.insert(0, str(ROOT / "docs/demo_ru/test"))
from run_test_headless import find_browser  # noqa: E402

PAGE_W, PAGE_H = 35.43056, 47.20833   # inches, from the .odp template


class Quiet(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def log_message(self, *a):
        pass


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0)); return s.getsockname()[1]


async def call(ws, n, method, **params):
    await ws.send(json.dumps({"id": n, "method": method, "params": params}))
    while True:
        m = json.loads(await ws.recv())
        if m.get("id") == n:
            if "error" in m:
                raise RuntimeError(f"{method}: {m['error']}")
            return m.get("result", {})


async def print_pdf(port, base, out):
    import urllib.request
    for _ in range(100):
        try:
            tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=1).read()); break
        except Exception:
            await asyncio.sleep(0.2)
    page = next(t for t in tabs if t["type"] == "page")
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=2 ** 30) as ws:
        n = 1; await call(ws, n, "Page.enable"); n += 1; await call(ws, n, "Runtime.enable")
        n += 1; await call(ws, n, "Emulation.setDeviceMetricsOverride", width=int(PAGE_W * 96), height=int(PAGE_H * 96), deviceScaleFactor=1, mobile=False)
        n += 1; await call(ws, n, "Page.navigate", url=base + "docs/capstone/poster/poster.html")
        ready = ("document.fonts.ready.then(() => Promise.all([...document.images].map(i => i.complete ? null : new Promise(r => { i.onload = r; i.onerror = r; }))))"
                 ".then(() => [...document.images].every(i => i.naturalWidth > 0))")
        for _ in range(300):
            await asyncio.sleep(0.2)
            n += 1; r = await call(ws, n, "Runtime.evaluate", expression=ready, awaitPromise=True, returnByValue=True)
            if r.get("result", {}).get("value") is True:
                break
        else:
            raise TimeoutError("fonts/images never became ready")
        n += 1; fonts = (await call(ws, n, "Runtime.evaluate", expression="[...document.fonts].filter(f => f.status === 'loaded').map(f => f.family).filter((v, i, a) => a.indexOf(v) === i).join(', ')", returnByValue=True))["result"]["value"]
        print("fonts loaded:", fonts)
        n += 1; r = await call(ws, n, "Page.printToPDF", paperWidth=PAGE_W, paperHeight=PAGE_H, printBackground=True, preferCSSPageSize=True,
                               marginTop=0, marginBottom=0, marginLeft=0, marginRight=0, scale=1)
        out.write_bytes(base64.b64decode(r["data"]))


def rasterise(pdf):
    import fitz
    d = fitz.open(pdf); p = d[0]; r = p.rect
    print(f"pages {len(d)}  MediaBox {r.width / 72:.4f} x {r.height / 72:.4f} in  ({r.width / 72 * 2.54:.2f} x {r.height / 72 * 2.54:.2f} cm)  {pdf.stat().st_size / 1e6:.1f} MB")
    pv = H / "preview"; pv.mkdir(exist_ok=True)
    z = 1800 / r.height; p.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False).save(pv / "poster.png")
    # zooms at 100 dpi: the banner's "115", the title block, the smallest text of the results row, the footer
    for name, (x0, y0, x1, y1) in {"zoom_banner": (0, 0, 14, 4), "zoom_title": (0, 7.5, 24, 12.5), "zoom_problem": (0.5, 12, 18, 23),
                                   "zoom_results": (0.5, 32.5, 18, 42), "zoom_results_r": (18, 32.5, 35.4, 42), "zoom_footer": (0.5, 42, 35.4, 47.2),
                                   "zoom_method": (0.5, 22, 35.4, 33)}.items():
        clip = fitz.Rect(x0 * 72, y0 * 72, x1 * 72, y1 * 72)
        p.get_pixmap(matrix=fitz.Matrix(100 / 72, 100 / 72), clip=clip, alpha=False).save(pv / f"{name}.png")
    print("previews in", pv)


def main():
    b = find_browser()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Quiet); threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    cp = free_port(); prof = tempfile.mkdtemp(prefix="poster_cdp_")
    proc = subprocess.Popen([b, "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-extensions", f"--remote-debugging-port={cp}",
                             f"--user-data-dir={prof}", "--hide-scrollbars", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    out = H / "poster.pdf"
    try:
        asyncio.run(print_pdf(cp, base, out))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
        srv.shutdown()
    rasterise(out)


if __name__ == "__main__":
    main()
