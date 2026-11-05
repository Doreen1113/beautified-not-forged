"""Run test_explain_t2.html in a headless Chromium (Chrome or Edge, whichever is installed) and print PASS/FAIL per record.

The JavaScript under test (../explain_t2.js) is executed by the browser's own engine (V8); nothing is re-implemented
here. Node.js is not required (it is not installed on this machine). Exit code 0 only if every record passes.

  python docs/demo_ru/test/run_test_headless.py            (expects fixture_t2.js; build it with make_fixture.py)
  python docs/demo_ru/test/run_test_headless.py --lang en  (English sentences: test_explain_t2_en.html + fixture_t2_en.js,
                                                            built by make_fixture_en.py from nl_v5/explain_v2_en.py)
"""
import html
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = HERE / "test_explain_t2.html"
CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "chromium-browser", "msedge",
]


def find_browser():
    for c in CANDIDATES:
        if Path(c).is_file():
            return c
        w = shutil.which(c)
        if w:
            return w
    return None


def main():
    en = "--lang" in sys.argv and sys.argv[sys.argv.index("--lang") + 1] == "en"
    page, fx = (HERE / "test_explain_t2_en.html", "fixture_t2_en.js") if en else (PAGE, "fixture_t2.js")
    if not (HERE / fx).is_file():
        sys.exit(f"{fx} missing: run {'make_fixture_en.py' if en else 'make_fixture.py'} first")
    b = find_browser()
    if b is None:
        sys.exit("No Chromium-based browser found. Open test_explain_t2.html in any browser: it prints PASS/FAIL per record.")
    url = "file:///" + page.as_posix().lstrip("/")
    cmd = [b, "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-extensions", "--dump-dom", url]
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120).stdout
    m = re.search(r"T2_RESULT\t(\d+)\t(\d+)\t(\d+)\n(.*?)\nT2_END", out, re.S)
    if not m:
        sys.exit("could not find the report block in the dumped DOM (browser: %s)" % b)
    npass, nfail, n = int(m.group(1)), int(m.group(2)), int(m.group(3))
    print("browser:", b)
    for line in html.unescape(m.group(4)).splitlines():
        print(line)
    print(f"T2 {'English ' if en else ''}equivalence: {npass} PASS / {nfail} FAIL of {n}")
    sys.exit(0 if nfail == 0 and npass == n and n > 0 else 1)


if __name__ == "__main__":
    main()
