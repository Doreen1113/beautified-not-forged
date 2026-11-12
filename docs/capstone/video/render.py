"""Render the film: headless Chrome steps film.html frame by frame (window.seek(t)), the PNG screenshots go to ffmpeg
(libx264), and the narration track (audio/narration.wav) is muxed in.

python docs/capstone/video/render.py --preview 3,9,15      -> preview/t003.0.png ... (look before rendering)
python docs/capstone/video/render.py                       -> capstone_video.mp4 (1920x1080, 30 fps, AAC narration)
python docs/capstone/video/render.py --fps 30 --crf 18
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

H = Path(__file__).resolve().parent; ROOT = H.parents[2]
sys.path.insert(0, str(ROOT / "docs/demo_ru/test"))
from run_test_headless import find_browser  # noqa: E402

W, Hh = 1920, 1080


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


class Quiet(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

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
        if "exceptionDetails" in r:
            raise RuntimeError(r["exceptionDetails"].get("text", "") + " " + json.dumps(r["exceptionDetails"].get("exception", {}))[:500])
        return r.get("result", {}).get("value")

    async def shot(self):
        return base64.b64decode((await self.call("Page.captureScreenshot", format="png", fromSurface=True))["data"])


async def open_film(port, base):
    import urllib.request
    for _ in range(100):
        try:
            tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=1).read()); break
        except Exception:
            await asyncio.sleep(0.2)
    page = next(t for t in tabs if t["type"] == "page")
    ws = await websockets.connect(page["webSocketDebuggerUrl"], max_size=2 ** 28)
    cdp = CDP(ws); await cdp.call("Page.enable"); await cdp.call("Runtime.enable")
    await cdp.call("Emulation.setDeviceMetricsOverride", width=W, height=Hh, deviceScaleFactor=1, mobile=False)
    await cdp.call("Page.navigate", url=base + "docs/capstone/video/film.html"); await asyncio.sleep(0.5)
    for _ in range(600):
        if await cdp.js("window.READY === true"):
            break
        await asyncio.sleep(0.1)
    else:
        raise TimeoutError("film never became READY (images)")
    total = await cdp.js("window.FILM.total"); return cdp, ws, total


async def preview(port, base, times):
    cdp, ws, total = await open_film(port, base); out = H / "preview"; out.mkdir(exist_ok=True)
    for t in times:
        await cdp.js(f"window.seek({t})"); (out / f"t{t:05.1f}.png").write_bytes(await cdp.shot()); print("preview", t, flush=True)
    await ws.close(); return total


async def render(port, base, fps, crf, out):
    cdp, ws, total = await open_film(port, base); n = int(total * fps) + 1
    video_only = H / "film_video.mp4"
    ff = subprocess.Popen([ffmpeg(), "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "png", "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(video_only)], stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(n):
        t = i / fps; await cdp.js(f"window.seek({t})"); ff.stdin.write(await cdp.shot())
        if i % (fps * 10) == 0:
            el = time.time() - t0; print(f"frame {i}/{n}  t={t:6.1f}s  {el:5.0f}s elapsed, ~{el / max(i, 1) * (n - i):4.0f}s left", flush=True)
    ff.stdin.close(); ff.wait(); await ws.close()
    subprocess.run([ffmpeg(), "-y", "-v", "error", "-i", str(video_only), "-i", str(H / "audio/narration.wav"), "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
                    "-shortest", "-movflags", "+faststart", str(out)], check=True)
    r = subprocess.run([ffmpeg(), "-i", str(out)], capture_output=True, text=True)
    print([l.strip() for l in r.stderr.splitlines() if "Duration" in l or "Stream" in l])
    return total


def main():
    args = sys.argv[1:]; fps = 30; crf = 18
    if "--fps" in args:
        fps = int(args[args.index("--fps") + 1])
    if "--crf" in args:
        crf = int(args[args.index("--crf") + 1])
    b = find_browser()
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Quiet); threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}/"
    cp = free_port(); prof = tempfile.mkdtemp(prefix="film_cdp_")
    proc = subprocess.Popen([b, "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-extensions", f"--remote-debugging-port={cp}",
                             f"--user-data-dir={prof}", "--hide-scrollbars", f"--window-size={W},{Hh}", "--force-device-scale-factor=1", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        if "--preview" in args:
            times = [float(x) for x in args[args.index("--preview") + 1].split(",")]
            asyncio.run(preview(cp, base, times))
        else:
            asyncio.run(render(cp, base, fps, crf, H / "capstone_video.mp4"))
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
        srv.shutdown()


if __name__ == "__main__":
    main()
