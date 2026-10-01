import socket, subprocess, time, glob, os, json
from playwright.sync_api import sync_playwright
s = socket.socket(); s.bind(("", 0)); PORT = s.getsockname()[1]; s.close()
D = "/home/intern_2603055/demo_page"
srv = subprocess.Popen(["python3", "-m", "http.server", str(PORT)], cwd=D, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(3)
INJECT = """(() => {
  const c = document.createElement('div'); c.id = '__cur';
  c.style.cssText = 'position:fixed;left:0;top:0;width:18px;height:18px;border-radius:50%;background:rgba(15,77,146,.55);border:2px solid #fff;box-shadow:0 0 0 1px rgba(0,0,0,.3);z-index:99999;pointer-events:none;transform:translate(-50%,-50%);transition:left .35s ease, top .35s ease';
  document.addEventListener('mousemove', e => { c.style.left = e.clientX + 'px'; c.style.top = e.clientY + 'px'; });
  document.addEventListener('mousedown', () => { c.style.background = 'rgba(179,52,43,.7)'; });
  document.addEventListener('mouseup', () => { c.style.background = 'rgba(15,77,146,.55)'; });
  document.body.appendChild(c);
  const b = document.createElement('div'); b.id = '__cap';
  b.style.cssText = 'position:fixed;left:0;right:0;bottom:0;min-height:74px;padding:14px 60px;background:rgba(22,27,36,.94);color:#f0f0f0;font:24px/1.35 Calibri,"IBM Plex Sans",sans-serif;z-index:99998;display:flex;align-items:center';
  document.body.appendChild(b); document.body.style.paddingBottom = '110px';
})()"""
def cap(pg, t): pg.evaluate("t => { document.getElementById('__cap').innerHTML = '<span>' + t + '</span>'; }", t)
log = []
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1280, "height": 720}, record_video_dir=f"{D}/video2", record_video_size={"width": 1280, "height": 720})
        pg = ctx.new_page()
        pg.goto(f"http://localhost:{PORT}/index.html"); pg.evaluate(INJECT)
        cap(pg, "Open the page: the 70 MB model and the face-landmark model load once; everything then runs on this device.")
        pg.mouse.move(640, 300)
        pg.wait_for_function("document.getElementById('status').textContent === 'ready'", timeout=240000); time.sleep(2.5)
        cap(pg, "Each example comes with its <b>known answer</b>, so the output can be checked. Pick one and the model analyses it.")
        time.sleep(3.5)
        pre = {1: "Next example: an untouched photo.", 4: "Next example: skin whitened.", 5: "Next example: skin smoothed.", 3: "Next example: face slimmed.", 2: "Next example: eyes enlarged."}
        steps = [(1, "An untouched photo: <b>real</b> &#10003;. The class probabilities are shown under the answer."),
                 (4, "Skin whitening: <b>filter</b> &#10003;, and the sentence names the operation (tone score close to 1)."),
                 (5, "Skin smoothing: <b>filter</b> &#10003;, not fake. The evidence map shows where the model looked."),
                 (3, "Face slimming: <b>filter</b> &#10003;, operation named: face reshaped."),
                 (2, "Eye enlargement: the model says <b>real</b> &#10007;. A known weakness, shown as it is.")]
        for i, text in steps:
            btn = pg.query_selector_all("#gallery button")[i]; btn.scroll_into_view_if_needed(); box = btn.bounding_box()
            cap(pg, pre[i]); pg.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2); time.sleep(1.2)
            pg.evaluate("document.getElementById('label').textContent=''"); pg.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            pg.wait_for_function("document.getElementById('label').textContent !== ''", timeout=60000); time.sleep(0.6)
            log.append((i, pg.inner_text("#label"), pg.inner_text("#truth"))); cap(pg, text)
            box = pg.query_selector("#result").bounding_box(); pg.mouse.move(box["x"] + 470, box["y"] + 60); time.sleep(4.2)
        for f, before, text in (("part_nose.jpg", "Now upload your own photo (an FF++ video frame, not one of the examples)...", "Your own photo: a <b>part-level forgery</b> (nose from another person). <b>fake</b>, and the sentence names the nose."),
                        ("deepfake.jpg", "...and another one.", "A <b>whole-face deepfake</b>: fake, with the evidence spread across the whole face.")):
            btn = pg.query_selector("label.btn"); btn.scroll_into_view_if_needed(); box = btn.bounding_box()
            cap(pg, before); pg.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2); time.sleep(1.5)
            pg.evaluate("document.getElementById('label').textContent=''"); pg.set_input_files("#file", f"{D}/imgs/{f}")
            pg.wait_for_function("document.getElementById('label').textContent !== ''", timeout=60000); time.sleep(0.6)
            log.append((f, pg.inner_text("#label"), pg.inner_text("#sentence"))); cap(pg, text)
            pg.evaluate("document.getElementById('result').scrollIntoView({behavior: 'smooth', block: 'start'})"); time.sleep(0.8)
            box = pg.query_selector("#view").bounding_box(); pg.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2); time.sleep(4.5)
        cap(pg, "The evidence map can be switched off to see the face itself.")
        cb = pg.query_selector("#showev").bounding_box()
        for _ in range(2):
            pg.mouse.move(cb["x"] + 6, cb["y"] + 6); time.sleep(0.5); pg.mouse.click(cb["x"] + 6, cb["y"] + 6); time.sleep(1.7)
        acc = pg.query_selector("#accbars"); acc.scroll_into_view_if_needed(); time.sleep(0.5)
        cap(pg, "On 50 more faces of each kind this model is right 38&ndash;96&nbsp;%: the page says how often to trust it.")
        time.sleep(5)
        pg.query_selector(".notes").scroll_into_view_if_needed(); time.sleep(0.5)
        cap(pg, "...and states its limits: what it was trained on and where it fails.")
        time.sleep(4.5)
        ctx.close(); b.close()
finally:
    srv.terminate()
print(json.dumps(log)); print("VIDEO", sorted(glob.glob(f"{D}/video2/*.webm"), key=os.path.getmtime)[-1])
