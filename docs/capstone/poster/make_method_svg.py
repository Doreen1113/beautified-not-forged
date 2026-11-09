"""The poster's Method figure as inline vector SVG (crisp Arial text, images from assets/tiles).
Coordinates are hundredths of an inch at printed size, so a font-size here is a real point size on the 90 x 120 cm sheet.
Numbers: report_v3/report.tex L234-237 (data counts), assets/model_numbers.json (make_model_tiles.py, main model on the
held-out part-level forgery FF++ 682, nose from a donor). Writes the SVG between <!--METHOD_SVG--> markers in poster.html
and a copy to assets/fig_method.svg.   python docs/capstone/poster/make_method_svg.py"""
import json
from pathlib import Path

H = Path(__file__).resolve().parent
INK, MUTED, GREEN, AMBER, RED, BLUE, GREY, LIGHT, EDGE, CYAN = "#1a1a1a", "#5a6270", "#0a8f68", "#b8860b", "#c8521a", "#1d4f91", "#aab2bd", "#f3f6fa", "#b9c4d4", "#1b8fc2"
W = 1594
N = json.loads((H / "assets/model_numbers.json").read_text(encoding="utf-8"))
P = dict(zip(["real", "forged", "beautified"], N["p_real_forged_beautified"]))
OPS = dict(zip(["eye", "contour", "tone", "texture"], N["ops_eye_contour_tone_texture"]))
NAMED, EVN = N["named"], N["part_means"][N["named"]]
out = []


def pt(p):          # points -> units (1 unit = 0.01 in)
    return p / 0.72


def T(x, y, s, size=20, weight=400, color=INK, anchor="start", italic=False):
    st = f"font-size:{pt(size):.1f}px;font-weight:{weight};fill:{color}" + (";font-style:italic" if italic else "")
    out.append(f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" style="{st}">{s}</text>')


def IMG(href, x, y, w, h, border=None, lw=5):
    out.append(f'<image href="assets/tiles/{href}" x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" preserveAspectRatio="none"/>')
    if border:
        out.append(f'<rect x="{x + lw / 2:.1f}" y="{y + lw / 2:.1f}" width="{w - lw:.1f}" height="{h - lw:.1f}" fill="none" stroke="{border}" stroke-width="{lw}"/>')


def RECT(x, y, w, h, fill="white", stroke=EDGE, lw=2.5, r=10):
    out.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{lw}"/>')


def ARROW(x1, y1, x2, y2, color=INK, lw=3.2):
    out.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{color}" stroke-width="{lw}" marker-end="url(#ah)"/>')


def LINE(x1, y1, x2, y2, color=INK, lw=3.2):
    out.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{color}" stroke-width="{lw}"/>')


def BAR(y, label, val, color, x_lab=1170, x0=1180, w=80, h=15, size=15, bold=False):
    T(x_lab, y + h - 2, label, size, 700 if bold else 400, INK, "end")
    out.append(f'<rect x="{x0}" y="{y}" width="{w}" height="{h}" rx="3" fill="#e6eaf0"/>')
    if val > 0.005:
        out.append(f'<rect x="{x0}" y="{y}" width="{max(3, w * val):.1f}" height="{h}" rx="3" fill="{color}"/>')
    T(x0 + w + 9, y + h - 2, f"{val:.2f}", size, 700 if bold else 400, color if val > 0.5 else INK)


# ------------------------------------------------------------------ A. training data
T(0, 30, "Training data: every edit comes with its pixel-exact footprint M", 24, 700, BLUE)
tw, th = 158, 190
# row 1: FF++ frames, smoothing on both classes
y = 54
for x, f, lab, col in zip([0, 206, 452, 658], ["ffpp_real", "ffpp_filter", "ffpp_fake", "ffpp_fake_filter"], ["real", "beautified", "forged", "forged"], [GREEN, AMBER, RED, RED]):
    IMG(f"method_{f}.png", x, y, tw, th, border=col); T(x + tw / 2, y + th + 28, lab, 20, 700, col, "middle")
for x in (0, 452):
    ARROW(x + tw + 8, y + th / 2, x + 206 - 10, y + th / 2)
T(880, y + 74, "Both classes see skin smoothing,", 22, 700); T(880, y + 114, "so smoothing is not a forgery cue.", 22, 700)
T(880, y + 158, "41,512 genuine and 41,526 forged FF++ frames", 19, 400, MUTED)
# row 2: one commercial render split into single operations
y = 300
IMG("method_vendor_O.png", 0, y, tw, th, border=GREEN); T(tw / 2, y + th + 28, "original", 19, 400, INK, "middle")
ARROW(tw + 8, y + th / 2, 206 - 10, y + th / 2)
IMG("method_vendor_R.png", 206, y, tw, th, border=AMBER); T(206 + tw / 2, y + th + 28, "app render", 19, 400, INK, "middle")
ARROW(206 + tw + 8, y + th / 2, 412 - 10, y + th / 2)
for i, k in enumerate(["eye", "contour", "tone", "texture"]):
    x = 412 + i * 178; IMG(f"method_comp_{k}.png", x, y, tw, th); T(x + tw / 2, y + th + 28, k, 19, 400, INK, "middle")
for i, s in enumerate(["Optical flow and the photometric", "residual split one app render", "into single operations, each", "with its own"]):
    T(1150, y + 36 + i * 37, s, 21)
T(1150 + 128, y + 36 + 3 * 37, "footprint M (cyan).", 21, 700, CYAN)
T(1150, y + 36 + 4 * 37 + 6, "18,734 renders → 50,112 items", 18, 400, MUTED)
# row 3: part-level forgery
y = 546
for i, (f, lab, col) in enumerate([("part_x0", "original", GREEN), ("part_x", "nose from a donor", RED), ("part_M", "footprint M", None)]):
    x = i * 240; IMG(f"method_{f}.png", x, y, th, th, border=col)
    T(x + th / 2, y + th + 28, lab, 19, 700 if col is None else 400, CYAN if col is None else INK, "middle")
for x in (0, 240):
    ARROW(x + th + 8, y + th / 2, x + 240 - 10, y + th / 2)
T(740, y + 74, "Part-level forgeries: one face part replaced,", 21); T(740, y + 114, "nothing outside M touched.", 21)
T(740, y + 156, "61,510 edits; the model is tested on held-out ones", 19, 400, MUTED)

# ------------------------------------------------------------------ B. model
LINE(0, 798, W, 798, "#d5dae2", 2)
T(0, 836, "Model: one frozen backbone, 3.16 M trained parameters, task heads", 24, 700, BLUE)
Y = 858
l = lambda ly: Y + ly
# input
IMG("model_in.png", 0, l(64), 220, 220, border=RED)
T(110, l(312), "input", 18, 700, INK, "middle"); T(110, l(335), "the forgery above", 15, 400, MUTED, "middle")
ARROW(226, l(174), 282, l(174))
# encoder
RECT(286, l(8), 330, 362, "white", EDGE, 2.5, 14)
T(304, l(48), "CLIP ViT-L/14", 22, 700); T(304, l(78), "image encoder, frozen", 17, 400, MUTED)
for i in range(7):
    by = l(102 + i * 31)
    out.append(f'<rect x="302" y="{by}" width="178" height="24" rx="4" fill="#dfe5ee" stroke="{EDGE}" stroke-width="1.5"/>')
    out.append(f'<rect x="486" y="{by}" width="38" height="24" rx="4" fill="{BLUE}"/>')
T(566, l(220), "×24", 22, 700, INK, "middle")
out.append(f'<rect x="302" y="{l(324)}" width="22" height="16" rx="3" fill="#dfe5ee" stroke="{EDGE}" stroke-width="1.5"/>'); T(332, l(338), "frozen, 303 M parameters", 15, 400, MUTED)
out.append(f'<rect x="302" y="{l(346)}" width="22" height="16" rx="3" fill="{BLUE}"/>'); T(332, l(360), "LoRA, r = 16, 3.16 M trained", 15, 700, BLUE)
# tokens -> heads
LINE(616, l(132), 662, l(132)); LINE(662, l(76), 662, l(178)); ARROW(662, l(76), 700, l(76)); ARROW(662, l(178), 700, l(178))
T(639, l(120), "CLS", 15, 400, MUTED, "middle")
ARROW(616, l(298), 700, l(298)); T(656, l(286), "patches", 15, 400, MUTED, "middle")
heads = [(34, "class head", "forged logit f, beautified logit b", "P(forged) = σ(f), never reads b", False),
         (136, "operation head", "eye · contour · tone · texture", "on the pooled CLS token", False),
         (246, "evidence head", "one linear map per patch token", "16×16 map m, trained against M", True)]
for ly, k, d1, d2, hi in heads:
    RECT(700, l(ly), 370, 84 if not hi else 104, "#e3ebf7" if hi else "white", BLUE if hi else EDGE, 3.5 if hi else 2.5)
    T(716, l(ly + 30), k, 19, 700, BLUE); T(716, l(ly + 54), d1, 16); T(716, l(ly + 76), d2, 15, 400, MUTED)
# outputs
for i, k in enumerate(["real", "forged", "beautified"]):
    BAR(l(44 + i * 26), k, P[k], {"real": GREEN, "forged": RED, "beautified": AMBER}[k], bold=(P[k] > 0.5))
for i, k in enumerate(["eye", "contour", "tone", "texture"]):
    BAR(l(146 + i * 19), k, OPS[k], AMBER, h=13, size=14)
IMG("model_ev16.png", 1080, l(252), 92, 92); IMG("model_M16.png", 1200, l(252), 92, 92)
out.append(f'<line x1="1177" y1="{l(298)}" x2="1195" y2="{l(298)}" stroke="{INK}" stroke-width="2.5" marker-start="url(#ahs)" marker-end="url(#ah)"/>')
T(1126, l(366), "map m", 15, 400, INK, "middle"); T(1246, l(366), "footprint M", 15, 700, CYAN, "middle")
ARROW(1300, l(298), 1344, l(298))
# page output card
RECT(1350, l(8), 244, 362, "#e4f2ea", GREEN, 2.5, 14)
IMG("model_named.png", 1380, l(20), 184, 184)
T(1364, l(232), "named part:", 18, 700); T(1364 + 150, l(232), NAMED, 18, 700, RED)
for i, s in enumerate(["The evidence is", "concentrated on the", f"{NAMED} (mean {EVN:.2f})."]):
    T(1364, l(258 + i * 21), s, 15, 400, INK, italic=True)
T(1364, l(332), "sentence by code,", 14, 400, MUTED); T(1364, l(353), "checked by rules", 14, 400, MUTED)

HGT = 1240
defs = (f'<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="4" markerHeight="4" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
        f'<marker id="ahs" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="4" markerHeight="4" orient="auto">'
        f'<path d="M10,0 L0,5 L10,10 z" fill="{INK}"/></marker></defs>')
svg = (f'<svg class="fig" viewBox="0 0 {W} {HGT}" width="{W / 100:.2f}in" height="{HGT / 100:.2f}in" xmlns="http://www.w3.org/2000/svg" '
       f'style="font-family:Arial,Helvetica,sans-serif;display:block">{defs}\n' + "\n".join(out) + "\n</svg>")
(H / "assets/fig_method.svg").write_text(svg.replace('href="assets/', 'href="../assets/'), encoding="utf-8")
p = H / "poster.html"; s = p.read_text(encoding="utf-8")
a, b = "<!--METHOD_SVG-->", "<!--/METHOD_SVG-->"
assert a in s and b in s, "markers missing in poster.html"
s = s[:s.index(a) + len(a)] + "\n" + svg + "\n" + s[s.index(b):]
p.write_text(s, encoding="utf-8"); print("method svg:", len(out), "elements,", f"{W / 100:.2f} x {HGT / 100:.2f} in")
