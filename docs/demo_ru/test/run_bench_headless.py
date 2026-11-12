"""Runs bench.html in headless Chrome (desktop baseline for the phone measurement) and writes
test/bench_desktop_<model>.json plus a 412 px screenshot of the finished page. Usage: python test/run_bench_headless.py [effb4|repvit_ev]"""
import asyncio, base64, json, subprocess, sys, tempfile, threading, time
from http.server import ThreadingHTTPServer

from take_screens import CDP, HERE, Quiet, find_browser, free_port, main_async  # noqa: F401
import urllib.request, websockets

MODEL = sys.argv[1] if len(sys.argv) > 1 else "effb4"


async def run(cp, base):
    for _ in range(100):
        try:
            tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{cp}/json/list", timeout=1).read()); break
        except Exception:
            await asyncio.sleep(0.2)
    page = next(t for t in tabs if t["type"] == "page")
    async with websockets.connect(page["webSocketDebuggerUrl"], max_size=2 ** 28) as ws:
        cdp = CDP(ws); await cdp.call("Page.enable"); await cdp.call("Runtime.enable")
        await cdp.call("Emulation.setDeviceMetricsOverride", width=412, height=1400, deviceScaleFactor=2, mobile=True)
        await cdp.call("Page.navigate", url=base + "bench.html")
        t0 = time.time()
        while not await cdp.js("!!document.getElementById('go') && !document.getElementById('go').disabled"):
            if time.time() - t0 > 300: raise TimeoutError("landmarker")
            await asyncio.sleep(0.5)
        await cdp.js(f"document.getElementById('model').value='{MODEL}'; document.getElementById('go').click(); true")
        while not await cdp.js("!document.getElementById('out').hidden || document.getElementById('status').textContent.includes('失敗')"):
            if time.time() - t0 > 900: raise TimeoutError("bench")
            await asyncio.sleep(1)
        out = await cdp.js("document.getElementById('out').value") or await cdp.js("document.getElementById('status').textContent")
        shot = await cdp.call("Page.captureScreenshot", format="png")
        (HERE / "screens" / f"bench_412_{MODEL}.png").write_bytes(base64.b64decode(shot["data"]))
        return out


def main():
    b = find_browser()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Quiet); threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    cp = free_port(); prof = tempfile.mkdtemp(prefix="demo_ru_bench_")
    proc = subprocess.Popen([b, "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-extensions", f"--remote-debugging-port={cp}",
                             f"--user-data-dir={prof}", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        out = asyncio.run(run(cp, base))
    finally:
        proc.terminate(); srv.shutdown()
    print(out)
    (HERE / f"bench_desktop_{MODEL}.json").write_text(out, encoding="utf-8")


if __name__ == "__main__":
    main()
