"""Run test_masks50.html in headless Chrome/Edge (file://, no model, no network) and print the JS-vs-cv2 mask comparison.

  python docs/demo_ru/test/run_test_masks_headless.py   (expects fixture_masks50.js; build it with make_fixture_masks50.py)
"""
import html
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from run_test_headless import find_browser  # noqa: E402


def main():
    if not (HERE / "fixture_masks50.js").is_file():
        sys.exit("fixture_masks50.js missing: run make_fixture_masks50.py first")
    b = find_browser()
    if b is None:
        sys.exit("No Chromium-based browser found. Open test_masks50.html in any browser.")
    url = "file:///" + (HERE / "test_masks50.html").as_posix().lstrip("/")
    out = subprocess.run([b, "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-extensions", "--dump-dom", url],
                         capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300).stdout
    m = re.search(r"MASK_RESULT\t(\d+)\t(\d+)\t(\d+)\t([\d.]+)\t(\d+)\t([\d.]+)\n(.*?)\nMASK_END", out, re.S)
    if not m:
        sys.exit("could not find the report block in the dumped DOM")
    same, diff, n, dmax, same_native, ms = int(m.group(1)), int(m.group(2)), int(m.group(3)), float(m.group(4)), int(m.group(5)), float(m.group(6))
    print("browser:", b)
    for line in html.unescape(m.group(7)).splitlines():
        print(line)
    print(f"JS masks vs cv2 masks (same landmarks, same map, 224 grid): named part same {same}/{n}, different {diff}/{n}, max |d part mean| {dmax}; "
          f"same as cv2 at native crop resolution {same_native}/{n}; {ms} ms per image for masks + rule B")
    sys.exit(0 if diff == 0 else 1)


if __name__ == "__main__":
    main()
