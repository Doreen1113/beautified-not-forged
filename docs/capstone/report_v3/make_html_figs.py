"""Report figures 1, 3, 6, 7, 8, 9 as HTML/SVG pages in the design system of fig_system.html, rendered to vector PDF by
render_html_fig.py (headless Chrome, Arial embedded). Each page is laid out at its print width, text 8-9 pt, nothing
scaled afterwards. Data sources are the same files the paper's matplotlib scripts read (listed per figure below).
python make_html_figs.py            -> figs/fig_{teaser,exposure,twoaxis,perop,context,evidence}.{html,pdf,png}
2026-11-03 (report r10, IEEE two-column): teaser, exposure, perop and context are laid out at the column width COL;
evidence is laid out at the full text width 18.13 cm (figure*); twoaxis is no longer in the report."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

B = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent; OUT = HERE / "figs"
RU = B / "results/research/retouch_unified_20260929"; ALI = B / "results/research/alipair_zeroshot_20260929"; CDFB = B / "results/research/celebdfb_v2_20260927"
PY = sys.executable
INK, MUTED, GRID = "#1f2937", "#6b7280", "#e5e7eb"
NN, CODE, CHK = "#0f4d92", "#1b7f4c", "#6a3d9a"
FAKE, REAL, BEAU = "#d55e00", "#009e73", "#c98a00"
CNN, GEN, CLIP, OURS, OURS2 = "#8c8c8c", "#56b4e9", "#cc79a7", "#0f4d92", "#5b9bd5"
FAM_COL = {"cnn": CNN, "gen": GEN, "clip": CLIP, "ours": OURS}
DETECTORS = [  # (alipair key, celebdfb key, name, family) = figstyle_v8b.DETECTORS
    ("xception", "xception", "Xception", "cnn"), ("effnb4", "effnb4", "EfficientNet-B4", "cnn"), ("f3net", "f3net", "F3Net", "cnn"),
    ("spsl", "spsl", "SPSL", "cnn"), ("ucf", "ucf", "UCF", "cnn"), ("recce", "recce", "RECCE", "cnn"), ("core", "core", "CORE", "cnn"),
    ("srm", "srm", "SRM", "cnn"), ("sbi", "sbi", "SBI", "cnn"), ("caddm", "caddm", "CADDM", "cnn"), ("laanetr", "laanetr", "LAA-Net", "cnn"),
    ("univfd", "univfd", "UnivFD", "gen"), ("npr", "npr", "NPR", "gen"),
    ("effort", "effort", "Effort", "clip"), ("fadapter", "fadapter", "Forensics Adapter", "clip"), ("gend", "gend", "GenD", "clip"),
    ("dfdhr", "dfdhr", "DFD-HR", "clip"),
    ("ours main s1", "RU-clipe5", "Ours (seed 1)", "ours"), ("ours main s2", "RU-clipe5-s2", "Ours (seed 2)", "ours"),
]
SHORT = {"EfficientNet-B4": "EffNet-B4", "Forensics Adapter": "Forensics Ad.", "Ours (seed 1)": "Ours s1", "Ours (seed 2)": "Ours s2"}
PX = 96 / 2.54   # CSS px per cm
COL = 8.86       # IEEEtran a4 conference \\columnwidth (252 pt)

CSS = """
  @page { margin: 0; }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: #fff; }
  body { font-family: Arial, "Liberation Sans", Helvetica, sans-serif; color: #1f2937; font-size: 8.5pt; line-height: 1.25; padding: 0.22cm 0 0.02cm 0; }
  .row { display: flex; gap: 0.3cm; align-items: stretch; }
  .panel { position: relative; border-radius: 0.22cm; background: #f7f8fb; border: 0.4pt solid #d6dbe3; padding: 0.42cm 0.22cm 0.18cm; }
  .panel > .chip { position: absolute; top: -0.19cm; left: 0.22cm; font-size: 8.5pt; font-weight: 700; color: #fff; padding: 0.045cm 0.22cm; border-radius: 0.3cm; white-space: nowrap; }
  .nn > .chip { background: #0f4d92; } .code > .chip { background: #1b7f4c; } .chk > .chip { background: #6a3d9a; } .fk > .chip { background: #d55e00; } .ink > .chip { background: #374151; }
  svg text { font-family: Arial, "Liberation Sans", Helvetica, sans-serif; }
  .legend { font-size: 8pt; color: #6b7280; margin-top: 0.12cm; padding-left: 0.05cm; }
  .legend i { display: inline-block; width: 0.26cm; height: 0.18cm; border-radius: 0.05cm; vertical-align: -0.03cm; margin: 0 0.08cm 0 0.3cm; }
  .legend i:first-child { margin-left: 0; }
"""


def page(body, width_cm, title):
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{title}</title><style>{CSS}'
            f'body{{width:{width_cm}cm;}}</style></head><body>{body}</body></html>')


def T(x, y, s, size=11.3, anchor="start", color=INK, weight=None, extra=""):
    w = f' font-weight="{weight}"' if weight else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{color}"{w} {extra}>{s}</text>'


def render(name, html, width_cm):
    (OUT / f"{name}.html").write_text(html, encoding="utf-8")
    subprocess.run([PY, str(HERE / "render_html_fig.py"), str(OUT / f"{name}.html"), str(round(width_cm * PX))], check=True)


# ======================================================================= Figure 1: the two errors (teaser) ======================
def teaser():
    """Data: published_scores_<k>.npz (Alibaba pair of FFHQ 17003, threshold = 95th percentile of the originals) and
    celebdfb_v2 scores_v3/<k>.npz (video id17_id35_0000 frame 05, threshold = 95th percentile of the untreated genuine frames)."""
    DETS = [("effort", "Effort"), ("fadapter", "Forensics<br>Ad."), ("gend", "GenD"), ("dfdhr", "DFD-HR")]
    STEM, VID, FRAME = "17003", "id17_id35_0000", "05"
    A, Bv = {}, {}
    for k, _ in DETS:
        z = np.load(ALI / f"published_scores_{k}.npz"); s, g, st = z["s"], z["group"], z["stem"]
        thr = float(np.quantile(s[g == "orig_0"], 0.95))
        A[k] = (float(s[(g == "orig_0") & (st == STEM)][0]), float(s[(g == "Smoothing_90") & (st == STEM)][0]), thr)
        z = np.load(CDFB / "scores_v3" / f"{k}.npz", allow_pickle=True); p = z["p"][:, 1]
        paths = np.array([x.replace("\\", "/") for x in z["paths"]]); fold = np.array([x.split("/")[-2] for x in paths])
        vid = np.array([x.split("/")[-1].split("__")[0] for x in paths]); fr = np.array([x.split("__f")[-1][:2] for x in paths])
        thr = float(np.quantile(p[fold == "real"], 0.95))
        Bv[k] = (float(p[(fold == "synthesis") & (vid == VID) & (fr == FRAME)][0]), float(p[(fold == "synthesis_beautified") & (vid == VID) & (fr == FRAME)][0]), thr)
    o = np.array(Image.open(B / "ffhq_originals/Part2" / f"{STEM}.png").convert("RGB"))[200:840, 192:832]
    s = np.array(Image.open(B / "FFHQ_ali_process/Smoothing_90" / f"{int(STEM) // 1000 * 1000}" / f"{STEM}.png").convert("RGB"))[200:840, 192:832]
    F = B / "external_data/celebdfb/frames_std32v3"
    def sq(im):
        h, w = im.shape[:2]; m = min(h, w); y0, x0 = (h - m) // 2, (w - m) // 2; return im[y0:y0 + m, x0:x0 + m]
    fu = sq(np.array(Image.open(F / "synthesis" / f"{VID}__f{FRAME}.jpg").convert("RGB")))
    fb = sq(np.array(Image.open(F / "synthesis_beautified" / f"{VID}__f{FRAME}.jpg").convert("RGB")))
    for n, im in (("orig", o), ("smooth", s), ("swap", fu), ("swap_beauty", fb)):
        Image.fromarray(im).resize((420, 420), Image.LANCZOS).save(OUT / f"teaser_{n}.png", optimize=True)

    def bars(rows, left_lab, right_lab):
        h = ""
        for name, a, b, thr in rows:
            def one(v, verdict_fake):
                col = FAKE if verdict_fake else REAL; txt = ("forged" if verdict_fake else "genuine")
                return (f'<div class="bar"><div class="t"><div class="f" style="width:{v*100:.0f}%;background:{col}"></div>'
                        f'<div class="tick" style="left:{thr*100:.0f}%"></div></div><div class="v" style="color:{col}">{v:.2f} {txt}</div></div>')
            h += f'<div class="brow"><div class="dn">{name}</div>{one(a, a > thr)}{one(b, b > thr)}</div>'
        return h
    sty = """<style>
      .tp { width: 8.86cm; }
      .stack { display: flex; flex-direction: column; gap: 0.42cm; }
      .imgs { display: grid; grid-template-columns: 1.5cm 2.5cm 1.45cm 2.5cm; align-items: center; column-gap: 0; }
      .imgs img { width: 2.5cm; height: 2.5cm; object-fit: cover; border-radius: 0.14cm; box-shadow: 0 1px 2.5px rgba(0,0,0,.28); display: block; }
      .cls { font-size: 8pt; color: #6b7280; line-height: 1.2; }
      .cls b { color: #1f2937; display: block; font-size: 8.5pt; }
      .arr { text-align: center; font-size: 8pt; color: #6b7280; line-height: 1.15; }
      .arr svg { width: 1.1cm; height: 0.3cm; display: block; margin: 0.04cm auto; }
      .under { display: grid; grid-template-columns: 1.5cm 2.5cm 1.45cm 2.5cm; font-size: 8.5pt; text-align: center; margin-top: 0.08cm; }
      .under .b { font-weight: 700; }
      .brow { display: grid; grid-template-columns: 1.5cm 3.4cm 3.4cm; column-gap: 0.04cm; align-items: center; height: 0.5cm; }
      .dn { font-size: 8pt; text-align: right; padding-right: 0.08cm; line-height: 1.05; }
      .bar { display: flex; align-items: center; gap: 0.08cm; }
      .t { position: relative; width: 1.5cm; height: 0.22cm; background: #e8eaef; border-radius: 0.11cm; overflow: visible; flex: none; }
      .f { height: 100%; border-radius: 0.11cm; }
      .tick { position: absolute; top: -0.06cm; width: 0.05cm; height: 0.34cm; background: #1f2937; }
      .v { font-size: 8pt; font-weight: 700; white-space: nowrap; }
      .hdr { display: grid; grid-template-columns: 1.5cm 3.4cm 3.4cm; column-gap: 0.04cm; font-size: 8pt; color: #6b7280; margin: 0.12cm 0 0.04cm; }
      .hdr div:nth-child(2) { padding-left: 0; }
    </style>"""
    arrow = '<svg viewBox="0 0 40 10"><path d="M0 5h33M30 1l6 4-6 4" fill="none" stroke="#1f2937" stroke-width="1.5"/></svg>'
    pa = (f'<div class="panel code tp"><div class="chip">(a) Genuine photo, accused after smoothing</div>'
          f'<div class="imgs"><div class="cls">true class<b>genuine</b></div><img src="teaser_orig.png"><div class="arr">retouching<br>service{arrow}</div><img src="teaser_smooth.png"></div>'
          f'<div class="under"><div></div><div>original</div><div></div><div class="b" style="color:{FAKE}">accused</div></div>'
          f'<div class="hdr"><div></div><div>detector decision</div><div>after Smoothing-90</div></div>'
          f'{bars([(n, A[k][0], A[k][1], A[k][2]) for k, n in DETS], "", "")}</div>')
    pb = (f'<div class="panel fk tp"><div class="chip">(b) Deepfake, missed after a beauty preset</div>'
          f'<div class="imgs"><div class="cls">true class<b>forged</b><span>(face swap)</span></div><img src="teaser_swap.png"><div class="arr">beauty<br>app{arrow}</div><img src="teaser_swap_beauty.png"></div>'
          f'<div class="under"><div></div><div>as recorded</div><div></div><div class="b" style="color:{REAL}">missed</div></div>'
          f'<div class="hdr"><div></div><div>detector decision</div><div>after the preset</div></div>'
          f'{bars([(n, Bv[k][0], Bv[k][1], Bv[k][2]) for k, n in DETS], "", "")}</div>')
    foot = '<div class="legend">bars: each detector\'s forgery score &middot; black tick: its own threshold, set at 5% false alarms on untouched genuine faces of the same source</div>'
    render("fig_teaser", page(sty + f'<div class="stack">{pa}{pb}</div>{foot}', COL, "The two errors"), COL)


# ======================================================================= Figure 3: training exposure ===========================
def exposure():
    """Data: p3_readout40.json (seed 1): smoothing90_at_5fpr [v, lo, hi]; miss_rise[2] = strongest smoothing [v, lo, hi]."""
    p = json.loads((RU / "p3_readout40.json").read_text(encoding="utf-8"))
    arms = [("P0", "–", "–"), ("P3", "–", "smoothed"), ("P1", "smoothed", "–"), ("P2", "smoothed", "smoothed")]
    fa = [p[a]["smoothing90_at_5fpr"] for a, *_ in arms]; dm = [p[a]["miss_rise"][2] for a, *_ in arms]

    def chart(vals, ymin, ymax, ticks, ref, ylab, fmt, color_of):
        W, H = 310, 150; L, R, Tp, Bt = 38, 6, 10, 20
        def Y(v): return Tp + (ymax - v) / (ymax - ymin) * (H - Tp - Bt)
        g = ""
        for t in ticks:
            g += f'<line x1="{L}" x2="{W-R}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" stroke="{GRID}" stroke-width="0.8"/>' + T(L - 5, Y(t) + 3.5, str(t), 10.7, "end", MUTED)
        g += f'<line x1="{L}" x2="{W-R}" y1="{Y(ref):.1f}" y2="{Y(ref):.1f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 2.5"/>'
        bw = 34; step = (W - L - R) / 4
        for i, (v, lo, hi) in enumerate(vals):
            x = L + step * (i + 0.5) - bw / 2; y0, y1 = Y(max(v, 0)), Y(min(v, 0))
            g += f'<rect x="{x:.1f}" y="{y0:.1f}" width="{bw}" height="{max(y1-y0,0.5):.1f}" rx="2" fill="{color_of(v)}"/>'
            cx = x + bw / 2
            g += (f'<line x1="{cx}" x2="{cx}" y1="{Y(lo):.1f}" y2="{Y(hi):.1f}" stroke="{INK}" stroke-width="1"/>'
                  f'<line x1="{cx-4}" x2="{cx+4}" y1="{Y(lo):.1f}" y2="{Y(lo):.1f}" stroke="{INK}" stroke-width="1"/>'
                  f'<line x1="{cx-4}" x2="{cx+4}" y1="{Y(hi):.1f}" y2="{Y(hi):.1f}" stroke="{INK}" stroke-width="1"/>')
            ly = Y(hi) - 4 if v >= 0 else Y(0) - 4
            g += T(cx, ly, fmt(v), 11.3, "middle", INK, "700")
            g += T(cx, H - 5, arms[i][0], 12, "middle", INK, "700")
        g += f'<line x1="{L}" x2="{L}" y1="{Tp}" y2="{H-Bt}" stroke="{MUTED}" stroke-width="0.8"/>'
        g += T(10, (Tp + H - Bt) / 2, ylab, 10.7, "middle", INK, extra=f'transform="rotate(-90 10 {(Tp + H - Bt) / 2:.1f})"')
        return f'<svg viewBox="0 0 {W} {H}" width="{W/37.8:.2f}cm" height="{H/37.8:.2f}cm" style="display:block">{g}</svg>'

    def table():
        c = '<div class="tbl"><div class="k">genuine faces</div>' + "".join(f'<div class="{"on" if g != "–" else "off"}">{g}</div>' for _, g, _ in arms)
        c += '<div class="k">forged faces</div>' + "".join(f'<div class="{"on" if f != "–" else "off"}">{f}</div>' for _, _, f in arms) + "</div>"
        return c
    sty = """<style>
      .ep { width: 8.86cm; }
      .stack { display: flex; flex-direction: column; gap: 0.42cm; }
      .tbl { display: grid; grid-template-columns: 1.55cm repeat(4, 1fr); row-gap: 0.04cm; font-size: 8pt; text-align: center; margin: 0.02cm 0 0 0.3cm; }
      .tbl .k { text-align: right; color: #6b7280; padding-right: 0.12cm; }
      .tbl .on { color: #1f2937; font-weight: 700; background: #e6eef9; border-radius: 0.1cm; margin: 0 0.06cm; }
      .tbl .off { color: #9ca3af; }
      .sub { font-size: 8pt; color: #6b7280; text-align: center; margin-top: 0.05cm; }
    </style>"""
    pa = (f'<div class="panel fk ep"><div class="chip">Accusation: Smoothing-90 renders called forged</div>'
          + chart(fa, 0, 75, [0, 20, 40, 60], 5, "accused at 5% FPR (%)", lambda v: f"{v:.1f}", lambda v: FAKE if v > 15 else CNN)
          + table() + '<div class="sub">which class saw smoothed views in training &middot; dashed line: the 5% floor</div></div>')
    pb = (f'<div class="panel ink ep"><div class="chip">Escape: smoothed forgeries missed</div>'
          + chart(dm, -50, 65, [-40, -20, 0, 20, 40, 60], 0, "miss rise (points)", lambda v: f"{v:+.1f}", lambda v: BEAU if v > 5 else (FAKE if v < -5 else CNN))
          + table() + '<div class="sub">which class saw smoothed views in training &middot; dashed line: no change</div></div>')
    render("fig_exposure", page(sty + f'<div class="stack">{pa}{pb}</div>', COL, "Training exposure"), COL)


# ======================================================================= Figure 6: two directions per detector =================
def twoaxis():
    """Data: main_claim_A.json rows[k].fa_s90_at_5pct, fa_ci; fair_cdfb.json [k].d_miss_beauty_only, ci."""
    A = json.loads((ALI / "main_claim_A.json").read_text(encoding="utf-8"))["rows"]
    Bd = json.loads((CDFB / "fair_cdfb.json").read_text(encoding="utf-8"))
    W, H = 400, 300; L, R, Tp, Bt = 46, 10, 10, 40; xmin, xmax, ymin, ymax = -3, 76, -11, 27
    def X(v): return L + (v - xmin) / (xmax - xmin) * (W - L - R)
    def Y(v): return Tp + (ymax - v) / (ymax - ymin) * (H - Tp - Bt)
    g = f'<rect x="{X(xmin)}" y="{Tp}" width="{X(5)-X(xmin):.1f}" height="{H-Tp-Bt}" fill="#eef2f7"/>'
    for t in range(0, 80, 10):
        g += f'<line x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{Tp}" y2="{H-Bt}" stroke="{GRID}" stroke-width="0.8"/>' + T(X(t), H - Bt + 13, str(t), 10.7, "middle", MUTED)
    for t in range(-10, 30, 10):
        g += f'<line x1="{L}" x2="{W-R}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" stroke="{GRID}" stroke-width="0.8"/>' + T(L - 5, Y(t) + 3.5, str(t), 10.7, "end", MUTED)
    g += f'<line x1="{X(5):.1f}" x2="{X(5):.1f}" y1="{Tp}" y2="{H-Bt}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 2.5"/>'
    g += f'<line x1="{L}" x2="{W-R}" y1="{Y(0):.1f}" y2="{Y(0):.1f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 2.5"/>'
    g += T(X(5) + 3, Tp + 10, "5% FPR floor", 10.7, "start", MUTED) + T(X(22), Y(0) - 3, "no miss rise", 10.7, "start", MUTED)
    g += T((L + W - R) / 2, H - 4, "Direction A: smoothed genuine faces accused (%)", 11.3, "middle", INK)
    g += T(12, (Tp + H - Bt) / 2, "Direction B: beautified deepfakes, miss rise (points)", 11.3, "middle", INK, extra=f'transform="rotate(-90 12 {(Tp + H - Bt) / 2:.1f})"')
    # label placement (dx, dy in px from the marker; leader line when far)
    OFF = {"Xception": (6, 14), "EfficientNet-B4": (6, 13), "F3Net": (-6, 14), "SPSL": (-12, -20), "UCF": (6, -6), "RECCE": (-6, -7), "CORE": (10, -24),
           "SRM": (6, -7), "SBI": (6, -6), "CADDM": (6, 13), "LAA-Net": (6, -6), "UnivFD": (6, 13), "NPR": (6, -7), "Effort": (-6, 13),
           "Forensics Adapter": (6, -8), "GenD": (6, -7), "DFD-HR": (6, 13), "Ours (seed 1)": (8, 14), "Ours (seed 2)": (8, -8)}
    pts = ""
    for ka, kb, name, fam in DETECTORS:
        x = A[ka]["fa_s90_at_5pct"]; xlo, xhi = A[ka]["fa_ci"]; y = Bd[kb]["d_miss_beauty_only"]; ylo, yhi = Bd[kb]["ci"]["d_miss_beauty_only"]
        c = FAM_COL[fam]; cx, cy = X(x), Y(y)
        pts += (f'<line x1="{X(xlo):.1f}" x2="{X(xhi):.1f}" y1="{cy:.1f}" y2="{cy:.1f}" stroke="{c}" stroke-width="0.8" opacity="0.45"/>'
                f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{Y(ylo):.1f}" y2="{Y(yhi):.1f}" stroke="{c}" stroke-width="0.8" opacity="0.45"/>')
        if fam == "cnn":
            pts += f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.2" fill="{c}" stroke="#fff" stroke-width="1"/>'
        elif fam == "gen":
            pts += f'<path d="M{cx:.1f} {cy-5.5:.1f} l5.5 5.5 l-5.5 5.5 l-5.5 -5.5 z" fill="{c}" stroke="#fff" stroke-width="1"/>'
        elif fam == "clip":
            pts += f'<rect x="{cx-4:.1f}" y="{cy-4:.1f}" width="8" height="8" fill="{c}" stroke="#fff" stroke-width="1"/>'
        else:
            s = "".join(f'{cx + 6.5*np.cos(a):.1f},{cy + 6.5*np.sin(a):.1f} {cx + 2.8*np.cos(a+np.pi/5):.1f},{cy + 2.8*np.sin(a+np.pi/5):.1f} '
                        for a in np.linspace(-np.pi / 2, 1.5 * np.pi, 5, endpoint=False))
            pts += f'<polygon points="{s}" fill="{c}" stroke="#fff" stroke-width="0.8"/>'
        dx, dy = OFF[name]; anchor = "start" if dx > 0 else "end"
        if abs(dy) > 15:   # far label: leader line from the marker to the label's near end
            pts += f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx + dx*0.85:.1f}" y2="{cy + dy*0.85:.1f}" stroke="{MUTED}" stroke-width="0.7"/>'
        pts += T(cx + dx, cy + dy + 3, SHORT.get(name, name), 10.7, anchor, INK if fam in ("ours", "clip", "gen") else "#4b5563", "700" if fam == "ours" else None)
    # legend
    lx, ly = X(44), Y(-3.2)
    leg = (f'<rect x="{lx-6}" y="{ly-12}" width="{W-R-lx+4}" height="58" rx="4" fill="#fff" stroke="{GRID}"/>'
           f'<circle cx="{lx+4}" cy="{ly}" r="4" fill="{CNN}"/>' + T(lx + 12, ly + 3.5, "face-forgery CNN", 10.7) +
           f'<path d="M{lx+4} {ly+9} l5 5 l-5 5 l-5 -5 z" fill="{GEN}"/>' + T(lx + 12, ly + 17.5, "generated-image detector", 10.7) +
           f'<rect x="{lx}" y="{ly+24}" width="8" height="8" fill="{CLIP}"/>' + T(lx + 12, ly + 31.5, "CLIP-based detector", 10.7) +
           f'<polygon points="{lx+4},{ly+36} {lx+5.5},{ly+40} {lx+9.5},{ly+40} {lx+6.5},{ly+42.5} {lx+7.5},{ly+46.5} {lx+4},{ly+44} {lx+0.5},{ly+46.5} {lx+1.5},{ly+42.5} {lx-1.5},{ly+40} {lx+2.5},{ly+40}" fill="{OURS}"/>' + T(lx + 12, ly + 45.5, "ours, three-way", 10.7))
    svg = f'<svg viewBox="0 0 {W} {H}" width="{W/37.8:.2f}cm" height="{H/37.8:.2f}cm" style="display:block">{g}{pts}{leg}</svg>'
    body = f'<div class="panel ink" style="width:11.2cm"><div class="chip">Both directions per detector</div>{svg}</div>'
    render("fig_twoaxis", page(body, 11.2, "Two directions"), 11.2)


# ======================================================================= Figure 7: per operation and strength ==================
def perop():
    """Data: published_ali.json [k].by_op[op_level].fake_at_t (accused at the detector's own 5 % FPR threshold)."""
    d = json.loads((ALI / "published_ali.json").read_text(encoding="utf-8"))
    ops = [("EyeEnlarging", "Eye enlarging"), ("FaceLifting", "Face slimming"), ("Whitening", "Whitening"), ("Smoothing", "Skin smoothing")]
    series = [("xception", "Xception", CNN, "", "circle"), ("sbi", "SBI", CNN, "5 3", "square"), ("univfd", "UnivFD", GEN, "2 2", "diamond"),
              ("effort", "Effort", CLIP, "", "square"), ("fadapter", "Forensics Ad.", CLIP, "5 3", "square"),
              ("ours main", "Ours s1", OURS, "", "star"), ("ours main s2", "Ours s2", OURS2, "5 3", "star")]
    W, H = 150, 146; L, R, Tp, Bt = 26, 8, 16, 24; ymin, ymax = 0, 56
    def X(v): return L + (v - 22) / (98 - 22) * (W - L - R)
    def Y(v): return Tp + (ymax - v) / (ymax - ymin) * (H - Tp - Bt)
    def mark(kind, x, y, c, big):
        r = 4.2 if big else 3
        if kind == "circle": return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{c}" stroke="#fff" stroke-width="0.8"/>'
        if kind == "square": return f'<rect x="{x-r:.1f}" y="{y-r:.1f}" width="{2*r}" height="{2*r}" fill="{c}" stroke="#fff" stroke-width="0.8"/>'
        if kind == "diamond": return f'<path d="M{x:.1f} {y-r-1:.1f} l{r+1} {r+1} l-{r+1} {r+1} l-{r+1} -{r+1} z" fill="{c}" stroke="#fff" stroke-width="0.8"/>'
        s = "".join(f'{x + 6*np.cos(a):.1f},{y + 6*np.sin(a):.1f} {x + 2.6*np.cos(a+np.pi/5):.1f},{y + 2.6*np.sin(a+np.pi/5):.1f} ' for a in np.linspace(-np.pi / 2, 1.5 * np.pi, 5, endpoint=False))
        return f'<polygon points="{s}" fill="{c}" stroke="#fff" stroke-width="0.6"/>'
    panels = ""
    for i, (key, title) in enumerate(ops):
        g = T(W / 2 + 8, 10, title, 11.3, "middle", INK, "700")
        for t in (0, 20, 40):
            g += f'<line x1="{L}" x2="{W-R}" y1="{Y(t):.1f}" y2="{Y(t):.1f}" stroke="{GRID}" stroke-width="0.8"/>'
            if i % 2 == 0: g += T(L - 4, Y(t) + 3.5, str(t), 10.7, "end", MUTED)
        g += f'<line x1="{L}" x2="{W-R}" y1="{Y(5):.1f}" y2="{Y(5):.1f}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 2.5"/>'
        for lv in (30, 60, 90):
            g += T(X(lv), H - Bt + 12, str(lv), 10.7, "middle", MUTED)
        g += T((L + W - R) / 2, H - 2, "strength", 10.7, "middle", INK)
        for name, lab, c, dash, kind in series:
            ys = [d[name]["by_op"][f"{key}_{lv}"]["fake_at_t"] for lv in (30, 60, 90)]; big = name.startswith("ours")
            pth = " ".join(f'{"M" if j == 0 else "L"}{X(lv):.1f} {Y(v):.1f}' for j, (lv, v) in enumerate(zip((30, 60, 90), ys)))
            g += f'<path d="{pth}" fill="none" stroke="{c}" stroke-width="{2.2 if big else 1.2}" stroke-dasharray="{dash}"/>'
            g += "".join(mark(kind, X(lv), Y(v), c, big) for lv, v in zip((30, 60, 90), ys))
        if i % 2 == 0: g += T(9, (Tp + H - Bt) / 2, "accused at 5% FPR (%)", 10.7, "middle", INK, extra=f'transform="rotate(-90 9 {(Tp + H - Bt) / 2:.1f})"')
        panels += f'<svg viewBox="0 0 {W} {H}" width="{W/37.8:.2f}cm" height="{H/37.8:.2f}cm">{g}</svg>'
    leg = '<div class="lg">' + "".join(
        f'<span><svg viewBox="0 0 30 12" width="0.8cm" height="0.32cm"><path d="M2 6h26" stroke="{c}" stroke-width="{2.2 if n.startswith("ours") else 1.4}" stroke-dasharray="{dash}"/>{mark(kind, 15, 6, c, n.startswith("ours"))}</svg>{lab}</span>'
        for n, lab, c, dash, kind in series) + "</div>"
    sty = """<style>
      .lg { display: flex; flex-wrap: wrap; gap: 0.08cm 0.4cm; justify-content: center; font-size: 8.5pt; margin-bottom: 0.22cm; }
      .lg span { display: inline-flex; align-items: center; gap: 0.1cm; }
      .pp { display: flex; flex-wrap: wrap; row-gap: 0.15cm; justify-content: space-around; }
    </style>"""
    body = f'<div class="panel fk" style="width:{COL}cm"><div class="chip">Genuine faces accused, per operation</div>{leg}<div class="pp">{panels}</div><div class="legend">dashed line: the 5% floor &middot; 2,210 pairs per point &middot; each detector at its own threshold</div></div>'
    render("fig_perop", page(sty + body, COL, "Per operation"), COL)


# ======================================================================= Figure 8: edge treatment (context) ====================
def context():
    """Data: bdry38.json rows[k].{fe01,whole,ring}.fa (genuine Celeb-DF-v2 frames called forged at the detector's 5 % FPR)."""
    R = json.loads((RU / "bdry38.json").read_text(encoding="utf-8"))["rows"]
    KEY = {"ours main s1": "clipe5_s20260929"}
    rows = [(KEY.get(ka, ka), name, fam) for ka, _, name, fam in DETECTORS if KEY.get(ka, ka) in R]
    rows.sort(key=lambda r: R[r[0]]["fe01"]["fa"])
    n = len(rows); W, H = 316, 24 * n + 44; L, Rm, Tp = 86, 10, 6
    def X(v): return L + v / 100 * (W - L - Rm)
    g = ""
    for i, (k, name, fam) in enumerate(rows):
        y = Tp + 24 * i + 12
        if i % 2 == 0: g += f'<rect x="{L}" y="{y-11}" width="{W-L-Rm}" height="22" fill="#eef1f6"/>'
        v = R[k]; a, b, c = v["fe01"]["fa"], v["whole"]["fa"], v["ring"]["fa"]
        g += f'<line x1="{X(min(a,b,c)):.1f}" x2="{X(max(a,b,c)):.1f}" y1="{y}" y2="{y}" stroke="#c9ced8" stroke-width="2"/>'
        g += f'<rect x="{X(b)-4:.1f}" y="{y-4}" width="8" height="8" fill="{MUTED}" stroke="#fff" stroke-width="0.8"/>'
        g += f'<path d="M{X(c):.1f} {y-5.5} l5.5 5.5 l-5.5 5.5 l-5.5 -5.5 z" fill="{BEAU}" stroke="#fff" stroke-width="0.8"/>'
        g += f'<circle cx="{X(a):.1f}" cy="{y}" r="4.5" fill="{OURS if fam == "ours" else INK}" stroke="#fff" stroke-width="0.8"/>'
        g += T(L - 6, y + 3.8, "Ours" if fam == "ours" else SHORT.get(name, name), 10.7, "end", OURS if fam == "ours" else INK, "700" if fam == "ours" else None)
    yb = Tp + 24 * n + 4
    for t in (0, 25, 50, 75, 100):
        g += f'<line x1="{X(t):.1f}" x2="{X(t):.1f}" y1="{Tp}" y2="{yb}" stroke="{GRID}" stroke-width="0.8"/>' + T(X(t), yb + 12, str(t), 10.7, "middle", MUTED)
    g += f'<line x1="{X(5):.1f}" x2="{X(5):.1f}" y1="{Tp}" y2="{yb}" stroke="{MUTED}" stroke-width="1" stroke-dasharray="3 2.5"/>' + T(X(5) + 3, Tp + 9, "5% FPR", 10.7, "start", MUTED)
    g += T((L + W - Rm) / 2, H - 3, "smoothed genuine frames called forged (%)", 11.3, "middle", INK)
    svg = f'<svg viewBox="0 0 {W} {H}" width="{W/37.8:.2f}cm" height="{H/37.8:.2f}cm" style="display:block">{g}</svg>'
    leg = (f'<div class="lg"><span><svg viewBox="0 0 12 12" width="0.3cm" height="0.3cm"><circle cx="6" cy="6" r="4.5" fill="{INK}"/></svg>face only</span>'
           f'<span><svg viewBox="0 0 12 12" width="0.3cm" height="0.3cm"><rect x="2" y="2" width="8" height="8" fill="{MUTED}"/></svg>face + background</span>'
           f'<span><svg viewBox="0 0 12 12" width="0.3cm" height="0.3cm"><path d="M6 0.5 l5.5 5.5 l-5.5 5.5 l-5.5 -5.5 z" fill="{BEAU}"/></svg>edge ring only</span></div>')
    sty = """<style>.lg { display: flex; gap: 0.35cm; justify-content: center; font-size: 8.5pt; margin-bottom: 0.06cm; } .lg span { display: inline-flex; align-items: center; gap: 0.1cm; }</style>"""
    body = f'<div class="panel ink" style="width:{COL}cm"><div class="chip">Same smoothing strength, three edge treatments</div>{leg}{svg}</div>'
    render("fig_context", page(sty + body, COL, "Edge treatment"), COL)


# ======================================================================= Figure 9: evidence maps ===============================
def evidence():
    """Tiles exported from docs/paper_v2/figs/fig_evidence_tiles.npz (ev{i}_*.png): two held-out part-level forgeries."""
    z = np.load(B / "docs/paper_v2/figs/fig_evidence_tiles.npz")
    cols = [("input", "input"), ("truth", "true footprint"), ("ours", "evidence map (ours)"), ("cam", "Score-CAM (no head)"), ("restored", "region restored")]
    sty = """<style>
      .grid { display: grid; grid-template-columns: 1.6cm repeat(5, 3.08cm); column-gap: 0.14cm; row-gap: 0.06cm; align-items: center; }
      .grid img { width: 3.08cm; height: 3.08cm; object-fit: cover; border-radius: 0.14cm; box-shadow: 0 1px 2.5px rgba(0,0,0,.28); display: block; }
      .h { font-size: 8.5pt; text-align: center; color: #1f2937; font-weight: 700; }
      .rl { font-size: 8.5pt; color: #1f2937; text-align: right; padding-right: 0.1cm; line-height: 1.2; }
      .s { font-size: 8.5pt; text-align: center; font-weight: 700; height: 0.4cm; }
      .pillf { display: inline-block; color: #d55e00; background: #fbe8dc; border-radius: 0.3cm; padding: 0 0.2cm; }
      .pillr { display: inline-block; color: #009e73; background: #e3f2e8; border-radius: 0.3cm; padding: 0 0.2cm; }
    </style>"""
    h = '<div class="grid"><div></div>' + "".join(f'<div class="h">{t}</div>' for _, t in cols)
    for i in range(len(z["img"])):
        lab = str(z["label"][i]); p, pr = z["p"][i], z["pr"][i]
        h += f'<div class="rl">{lab.replace(", ", "<br>")}</div>' + "".join(f'<img src="ev{i}_{c}.png">' for c, _ in cols)
        h += (f'<div></div><div></div><div></div><div class="s"><span class="pillf">fake {p[1]:.2f}</span></div><div></div>'
              f'<div class="s"><span class="pillr">&rarr; real {pr[0]:.2f}</span></div>')
    h += "</div>"
    foot = '<div class="legend">green line: true footprint &middot; yellow line: the region the map selects &middot; heat: evidence or Score-CAM, opacity = value</div>'
    body = f'<div class="panel code" style="width:18.13cm"><div class="chip">Held-out part-level forgeries: where the evidence is, and what restoring it does</div>{h}{foot}</div>'
    render("fig_evidence", page(sty + body, 18.13, "Evidence maps"), 18.13)


if __name__ == "__main__":
    which = sys.argv[1:] or ["teaser", "exposure", "twoaxis", "perop", "context", "evidence"]
    for w in which:
        print("==", w); globals()[w]()
