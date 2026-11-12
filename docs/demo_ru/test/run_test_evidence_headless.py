"""Run test_evidence_page.html in a headless Chromium (Chrome or Edge) over a local HTTP server and compare the browser's
full page path (MediaPipe landmarks -> crop -> ru4e_effb4.onnx -> face-part masks -> rule B -> T2 sentences) with the
Python reference in fixture_ev.js (build it with make_fixture_ev.py).

The page is served over HTTP (fetch of the 67 MB ONNX file and of the fixture images does not work from file://). A
pending <img src="/__hold"> keeps the page's load event from firing until the page POSTs its results to /__done, so
`--dump-dom` only dumps after all images are analysed. Nothing is re-implemented here: the JavaScript is executed by
the browser's engine, the expected values come from Python.

Afterwards the browser's own landmarks and evidence map are fed to the Python masks (cv2, occlusion_regions.region_masks)
on the same 224 grid, which isolates the effect of the JavaScript mask rasterisation from everything else.

  python docs/demo_ru/test/run_test_evidence_headless.py   -> prints PASS/FAIL per image, writes test/evidence_headless_result.json
  python docs/demo_ru/test/run_test_evidence_headless.py --model repvit_ev   -> same 20 images through models/ru4e_repvit.onnx
      against fixture_ev_repvit_ev.js; writes test/evidence_headless_result_repvit_ev.json
"""
import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; DEMO = HERE.parent; ROOT = DEMO.parents[1]
sys.path.insert(0, str(ROOT / "docs/paper_v2")); sys.path.insert(0, str(ROOT))
CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "chromium-browser", "msedge",
]
FACE = ["eyes", "nose", "mouth", "skin", "contour"]


def find_browser():
    for c in CANDIDATES:
        if Path(c).is_file():
            return c
        w = shutil.which(c)
        if w:
            return w
    return None


class State:
    done = threading.Event(); payload = None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(DEMO), **k)

    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.startswith("/__hold"):
            State.done.wait(timeout=1800)
            self.send_response(204); self.end_headers(); return
        super().do_GET()

    def do_POST(self):
        if self.path.startswith("/__done"):
            n = int(self.headers.get("content-length", 0)); State.payload = json.loads(self.rfile.read(n).decode("utf-8"))
            self.send_response(204); self.end_headers(); State.done.set(); return
        self.send_response(404); self.end_headers()


def python_masks_on_browser_landmarks(res):
    """cv2 masks (region_masks) on the browser's landmarks + browser's evidence map, same 224 grid: how much of any
    difference comes from the JS mask rasterisation alone."""
    import torch
    import torch.nn.functional as F
    from occlusion_regions import region_masks
    rows = []
    for r in res:
        if not r.get("landmarks_grid") or not r.get("evidence_map16"):
            continue
        lm = np.asarray(r["landmarks_grid"], np.float32); G = 224
        M = region_masks(np.zeros((G, G, 3), np.uint8), lm)
        up = F.interpolate(torch.tensor(r["evidence_map16"], dtype=torch.float32)[None, None], size=(G, G), mode="bilinear", align_corners=False)[0, 0].numpy()
        parts = {k: round(float(up[M[k]].mean()) if M[k].any() else 0.0, 3) for k in FACE}
        top = max(parts, key=parts.get); whole = all(parts[k] >= 0.5 for k in ("eyes", "nose", "mouth")); named = ["whole face"] if whole else [top]
        js = r["parts3"]; dmax = max(abs(js[k] - parts[k]) for k in FACE)
        rows.append({"id": r["id"], "named_js": r["named_parts"], "named_cv2_same_landmarks": named, "same": named == r["named_parts"], "max_abs_dmean": round(dmax, 4),
                     "parts_js": js, "parts_cv2": parts})
    return rows


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model", default="effb4"); key = ap.parse_args().model
    suf = "" if key == "effb4" else f"_{key}"; fxname = f"fixture_ev{suf}"
    if not (HERE / f"{fxname}.js").is_file():
        sys.exit(f"{fxname}.js missing: run make_fixture_ev.py --model {key} first")
    b = find_browser()
    if b is None:
        sys.exit("No Chromium-based browser found. Serve docs/demo_ru over HTTP and open test/test_evidence_page.html: it prints PASS/FAIL per image.")
    srv = ThreadingHTTPServer(("127.0.0.1", 0), Handler); port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{port}/test/test_evidence_page.html" + ("" if key == "effb4" else f"?model={key}")
    cmd = [b, "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-extensions", "--window-size=1200,900", "--dump-dom", url]
    t0 = time.time()
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800).stdout
    wall = time.time() - t0; srv.shutdown()
    m = re.search(r"EV_RESULT\t(\d+)\t(\d+)\t(\d+)\n(.*?)\nEV_END", out, re.S)
    if not m:
        sys.exit("could not find the report block in the dumped DOM (browser: %s)" % b)
    npass, nfail, n = int(m.group(1)), int(m.group(2)), int(m.group(3))
    print("browser:", b)
    for line in html.unescape(m.group(4)).splitlines():
        print(line)
    print(f"evidence page: {npass} PASS / {nfail} FAIL of {n}   (browser process {wall:.0f} s)")
    P = State.payload or {}; res = P.get("results", [])
    summary = {"model": key, "browser": b, "pass": npass, "fail": nfail, "n": n, "load_ms": P.get("load"), "browser_process_s": round(wall, 1)}
    if res:
        ok = [r for r in res if r.get("timing")]
        summary["per_image_ms"] = {
            "wall_mean": round(float(np.mean([r["wall_ms"] for r in ok])), 1), "wall_median": round(float(np.median([r["wall_ms"] for r in ok])), 1),
            "inference_mean": round(float(np.mean([r["timing"]["inference"] for r in ok])), 1), "inference_median": round(float(np.median([r["timing"]["inference"] for r in ok])), 1),
            "landmarks_mean": round(float(np.mean([r["landmark_ms"] for r in ok])), 1), "masks_ruleB_mean": round(float(np.mean([r["timing"]["evidence"] for r in ok])), 1),
            "preprocess_mean": round(float(np.mean([r["timing"]["preprocess"] for r in ok])), 1)}
        fx = {r["id"]: r for r in json.loads((HERE / f"{fxname}.json").read_text(encoding="utf-8"))["records"]}
        dp = [max(abs(a - b) for a, b in zip(r["p"], fx[r["id"]]["p_raw"])) for r in ok]
        dm = [max(abs(r["parts3"][k] - fx[r["id"]]["parts3"][k]) for k in FACE) for r in ok if r.get("parts3")]
        box_same = sum(r["box"] == fx[r["id"]]["box"] for r in ok)
        summary["browser_vs_python"] = {"max_abs_dprob": round(max(dp), 4), "max_abs_dpartmean": round(max(dm), 4) if dm else None, "crop_box_identical": f"{box_same}/{len(ok)}",
                                        "decision_agree": f"{sum(r['okDec'] for r in res)}/{n}", "named_agree": f"{sum(r['okNamed'] for r in res)}/{n}", "sentences_agree": f"{sum(r['okS'] for r in res)}/{n}"}
        mk = python_masks_on_browser_landmarks(res)
        summary["js_masks_vs_cv2_masks_same_landmarks"] = {"n": len(mk), "named_same": sum(x["same"] for x in mk), "max_abs_dmean": max(x["max_abs_dmean"] for x in mk) if mk else None, "rows": mk}
        jl = {r["id"]: fx[r["id"]]["jsonl"] for r in res}
        summary["browser_vs_evidence_jsonl_clipe5"] = {"decision_agree": f"{sum(r['decision'] == jl[r['id']]['decision'] for r in res)}/{n}",
                                                       "named_agree": f"{sum(r['named_parts'] == jl[r['id']]['named_parts'] for r in res)}/{n}",
                                                       "note": "evidence.jsonl comes from the CLIP main model, not from ru4e_effb4"}
        summary["results"] = res
    (HERE / f"evidence_headless_result{suf}.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "results" and k != "js_masks_vs_cv2_masks_same_landmarks"}, ensure_ascii=False, indent=1))
    if "js_masks_vs_cv2_masks_same_landmarks" in summary:
        s = summary["js_masks_vs_cv2_masks_same_landmarks"]; print(f"JS masks vs cv2 masks on the browser's own landmarks: named part same {s['named_same']}/{s['n']}, max |d mean| {s['max_abs_dmean']}")
    sys.exit(0 if nfail == 0 and npass == n and n > 0 else 1)


if __name__ == "__main__":
    main()
