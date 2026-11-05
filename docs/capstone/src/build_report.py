"""Render docs/capstone/REPORT.md to REPORT.html (images embedded) and REPORT.pdf (headless Chrome, A4).

Run: python docs/capstone/src/build_report.py
"""
import base64
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import markdown

CAP = Path(__file__).resolve().parents[1]
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

CSS = """
@page { size: A4; margin: 16mm 16mm 16mm 16mm; }
:root { --ink:#1f2933; --muted:#52606d; --line:#d9dee3; --panel:#f5f7fa; --accent:#2f5fb3; }
html, body { background:#fff; color:var(--ink); }
body { font-family: "Noto Sans TC", "Microsoft JhengHei", "Segoe UI", sans-serif; font-size: 9.6pt; line-height: 1.45;
       margin: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
h1 { font-size: 17pt; line-height: 1.25; margin: 0 0 4mm; }
h2 { font-size: 13pt; margin: 6mm 0 2mm; border-bottom: 0.4mm solid var(--line); padding-bottom: 1mm; break-after: avoid; }
h3 { font-size: 11pt; margin: 4mm 0 1.5mm; break-after: avoid; }
p { margin: 0 0 2.2mm; text-align: justify; }
ol, ul { margin: 0 0 2.5mm; padding-left: 6mm; }
li { margin: 0.8mm 0; }
code { font-family: Consolas, "Cascadia Mono", monospace; font-size: 8.4pt; background: var(--panel); padding: 0 1mm; border-radius: 1mm; }
table { border-collapse: collapse; width: 100%; font-size: 8.3pt; margin: 2mm 0 1mm; break-inside: avoid; font-variant-numeric: tabular-nums; }
th, td { border-bottom: 0.25mm solid var(--line); padding: 0.9mm 1.4mm; vertical-align: top; }
thead th { border-bottom: 0.45mm solid var(--ink); text-align: left; color: var(--muted); font-weight: 700; }
td strong { color: var(--accent); }
p > em:only-child { display: block; font-style: normal; color: var(--muted); font-size: 8.6pt; margin-bottom: 3mm; }
img { display: block; max-width: 100%; margin: 3mm auto 1mm; }
figure { margin: 3mm 0; break-inside: avoid; }
figcaption { color: var(--muted); font-size: 8.6pt; text-align: center; }
img.wide { width: 100%; }
img.chart { width: 52%; }
img.shot { width: 46%; border: 0.3mm solid var(--line); border-radius: 1.5mm; }
blockquote { margin: 2mm 0 3mm; padding: 2mm 3.5mm; background: var(--panel); border-left: 1mm solid var(--accent); font-size: 9pt; }
blockquote p { margin: 0 0 1.5mm; }
.cover { break-after: page; }
.cover h1 { font-size: 20pt; text-align: center; margin: 8mm 0 10mm; }
.cover table { font-size: 11pt; break-inside: avoid; }
.cover td:first-child { width: 30mm; font-weight: 700; white-space: nowrap; }
.cover thead { display: none; }
.cover p { font-size: 10.5pt; line-height: 1.75; }
.refs p, h2#references + p { font-size: 8.4pt; text-align: left; }
"""

IMG_CLASS = {"pipeline_en.png": "wide", "retouch_paired_en.png": "chart", "screen_mobile_example2_crop.png": "shot",
             "screen_mobile_example2_en_crop.png": "shot"}


def data_uri(path):
    mime = "image/png" if path.suffix == ".png" else "image/svg+xml"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def figures(html):
    # <p><img alt="Figure n. ..." src="x"></p>  ->  <figure><img class=..><figcaption>..</figcaption></figure>
    def rep(m):
        alt, src = m.group(1), m.group(2)
        cls = IMG_CLASS.get(Path(src).name, "wide")
        return (f'<figure><img class="{cls}" src="{data_uri(CAP / src)}" alt="{alt}">'
                f'<figcaption>{alt}</figcaption></figure>')
    return re.sub(r'<p><img alt="([^"]*)" src="([^"]+)"\s*/?></p>', rep, html)


def main():
    md = (CAP / "REPORT.md").read_text(encoding="utf-8")
    body = markdown.markdown(md, extensions=["tables", "md_in_html", "toc"])
    body = figures(body)
    html = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            "<title>Capstone Report</title><style>" + CSS + "</style></head><body>" + body + "</body></html>")
    out_html = CAP / "REPORT.html"; out_html.write_text(html, encoding="utf-8")
    prof = tempfile.mkdtemp(prefix="capstone_pdf_")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={prof}",
                    f"--print-to-pdf={CAP / 'REPORT.pdf'}", out_html.as_uri()], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    print("wrote", out_html, CAP / "REPORT.pdf")


if __name__ == "__main__":
    sys.exit(main())
