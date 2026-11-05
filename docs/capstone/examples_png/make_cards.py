"""Example cards (PNG, 2400 px wide) with real images and the verbatim text outputs of the explanation layers.

All text drawn on the cards is copied from the result files listed in INDEX.md; the only text written here is labels,
headers and the plain-language names of the gate checks. Run:

    python docs/capstone/examples_png/make_cards.py            (all cards)
    python docs/capstone/examples_png/make_cards.py pipeline   (one family: pipeline, pairs, fakevlm, gate, history)
    python docs/capstone/examples_png/make_cards.py pipeline --en-only --out docs/meeting_20261018/assets
        --en-only: English prompts and model outputs only (pipeline cards: the Chinese p3r1z text block is omitted; the PNG
        is written as card_pipeline_example_<k>_en.png); the other card families have no Chinese text block to omit except
        the VLM pair card, whose observation sentences are Chinese model outputs, so `pairs` refuses --en-only.
        --out DIR: write the PNGs into DIR instead of this folder. Without these options the behaviour is unchanged.
"""
import difflib
import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

B = Path(r"C:\My_Project\AIGC")
EX = B / "results/research/explain_vlm_20261012"
NL = EX / "nl_v5"
OUT = Path(__file__).resolve().parent
EN_ONLY = "--en-only" in sys.argv
if EN_ONLY:
    sys.argv.remove("--en-only")
if "--out" in sys.argv:
    _i = sys.argv.index("--out"); OUT = Path(sys.argv[_i + 1]).resolve(); OUT.mkdir(parents=True, exist_ok=True)
    del sys.argv[_i:_i + 2]
sys.path.insert(0, str(B / "docs/paper_v2"))
sys.path.insert(0, str(NL))

import figstyle as FS  # noqa: E402
import matplotlib  # noqa: E402
FS.apply()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager as fm  # noqa: E402
from matplotlib.backends.backend_agg import RendererAgg  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import Rectangle, FancyBboxPatch  # noqa: E402

for f in (r"C:\Windows\Fonts\msjh.ttc", r"C:\Windows\Fonts\msjhbd.ttc"):
    fm.fontManager.addfont(f)
FAMILY = ["Arial", "Microsoft JhengHei", "DejaVu Sans"]
plt.rcParams["font.sans-serif"] = FAMILY
plt.rcParams["font.family"] = "sans-serif"

import nl_core_en as NE  # noqa: E402  (QUESTIONS_EN, FIXED_QA_EN, LLM_QI, FIXED_QI: verbatim strings of the deployed design)

W = 2400
DPI = 300
M = 60                     # page margin (px)
PX = DPI / 72.0            # px per pt
INK, MUTED, GRID, LIGHT = FS.INK, FS.MUTED, FS.GRID, FS.LIGHT
CODE = FS.OURS             # code-added text
OK, ERR = FS.OK, FS.ERR
WARN = "#B8860B"

_R = RendererAgg(W, 200, DPI)
_WCACHE = {}


def fp(size, weight="normal", style="normal"):
    return FontProperties(family=FAMILY, size=size, weight=weight, style=style)


def tw(s, size, weight="normal"):
    k = (s, size, weight)
    if k not in _WCACHE:
        w, h, d = _R.get_text_width_height_descent(s, fp(size, weight), ismath=False)
        _WCACHE[k] = w
    return _WCACHE[k]


TOK = re.compile(r"[\u2e80-\u9fff\uf900-\ufaff\u3000-\u303f\uff00-\uffef]|[^\s\u2e80-\u9fff\uf900-\ufaff\u3000-\u303f\uff00-\uffef]+[ ]*|\s+")


# ------------------------------------------------------------------ canvas (layout in px from the top, drawn at the end)
class Canvas:
    def __init__(self):
        self.ops = []; self.h = 0

    def bump(self, y):
        self.h = max(self.h, y)

    def text(self, x, y, s, size=8.0, color=INK, weight="normal", ha="left", va="baseline"):
        self.ops.append(("text", x, y, s, size, color, weight, ha, va)); self.bump(y + size * PX * 0.4)

    def rect(self, x, y, w, h, fc="none", ec="none", lw=0.0, rounded=False):
        self.ops.append(("rect", x, y, w, h, fc, ec, lw, rounded)); self.bump(y + h)

    def line(self, x0, y0, x1, y1, color=GRID, lw=0.8):
        self.ops.append(("line", x0, y0, x1, y1, color, lw)); self.bump(max(y0, y1))

    def image(self, x, y, w, h, arr):
        self.ops.append(("img", x, y, w, h, arr)); self.bump(y + h)

    def rich(self, x, y, runs, maxw, size=8.0, lh=1.45, bg=None):
        """runs = [(text, color, weight)]; wraps at maxw; y = top of the first line. Returns the y below the last line.
        bg: optional {color: background colour} drawn behind runs of that colour."""
        lhp = size * PX * lh; asc = size * PX * 0.95
        lines = [[]]; cx = 0.0
        for text, color, weight in runs:
            for t in TOK.findall(text):
                if t == "\n":
                    lines.append([]); cx = 0.0; continue
                if t.isspace() and "\n" in t:
                    for _ in range(t.count("\n")):
                        lines.append([])
                    cx = 0.0; continue
                w_strip = tw(t.rstrip(), size, weight); w_full = tw(t, size, weight) if t.endswith(" ") else w_strip
                if cx > 0 and cx + w_strip > maxw:
                    lines.append([]); cx = 0.0
                    if t.isspace():
                        continue
                lines[-1].append((t, color, weight, cx)); cx += w_full
        yy = y
        for ln in lines:
            # merge consecutive tokens of the same style into runs
            merged = []
            for t, c, wgt, x0 in ln:
                if merged and merged[-1][1] == c and merged[-1][2] == wgt:
                    merged[-1][0] += t
                else:
                    merged.append([t, c, wgt, x0])
            for t, c, wgt, x0 in merged:
                if bg and c in bg and t.strip():
                    self.rect(x + x0 - 3, yy + 2, tw(t.rstrip(), size, wgt) + 6, lhp - 4, fc=bg[c])
                self.text(x + x0, yy + asc, t, size, c, wgt)
            yy += lhp
        self.bump(yy)
        return yy

    def para(self, x, y, s, maxw, size=8.0, color=INK, weight="normal", lh=1.45):
        return self.rich(x, y, [(s, color, weight)], maxw, size, lh)

    def chip(self, x, y, label, fc, size=6.8, color="white"):
        w = tw(label, size, "bold") + 24; h = size * PX * 1.55
        self.rect(x, y, w, h, fc=fc, rounded=True)
        self.text(x + 12, y + h * 0.72, label, size, color, "bold")
        return x + w

    def render(self, path, pad=M):
        H = int(np.ceil(self.h + pad))
        fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
        fig.patch.set_facecolor("white")
        tf = fig.transFigure
        X = lambda v: v / W; Y = lambda v: 1 - v / H  # noqa: E731
        for op in self.ops:
            k = op[0]
            if k == "text":
                _, x, y, s, size, color, weight, ha, va = op
                fig.text(X(x), Y(y), s, fontproperties=fp(size, weight), color=color, ha=ha, va=va, transform=tf)
            elif k == "rect":
                _, x, y, w, h, fc, ec, lw, rounded = op
                if rounded:
                    p = FancyBboxPatch((X(x), Y(y + h)), w / W, h / H, boxstyle=f"round,pad=0,rounding_size={min(h / 2, 14) / W}",
                                       transform=tf, fc=fc, ec=ec, lw=lw, mutation_aspect=W / H)
                else:
                    p = Rectangle((X(x), Y(y + h)), w / W, h / H, transform=tf, fc=fc, ec=ec, lw=lw)
                fig.add_artist(p)
            elif k == "line":
                _, x0, y0, x1, y1, color, lw = op
                fig.add_artist(plt.Line2D([X(x0), X(x1)], [Y(y0), Y(y1)], transform=tf, color=color, lw=lw))
            elif k == "img":
                _, x, y, w, h, arr = op
                ax = fig.add_axes([X(x), Y(y + h), w / W, h / H]); ax.imshow(arr, interpolation="lanczos"); ax.set_axis_off()
        fig.savefig(path, dpi=DPI, facecolor="white")
        plt.close(fig)
        print("wrote", path, f"{W}x{H}")


# ------------------------------------------------------------------ data
def jl(p):
    return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]


EVD = {r["id"]: r for r in jl(EX / "evidence.jsonl")}
EVH = {r["id"]: r for r in jl(EX / "evidence_holdout.jsonl")}
MAPS_D = np.load(EX / "evidence_maps.npz"); MAPS_H = np.load(EX / "evidence_maps_holdout.npz")


def rec_of(i):
    if i in EVH:
        return EVH[i], MAPS_H[i], "evidence_holdout.jsonl"
    return EVD[i], MAPS_D[i], "evidence.jsonl"


def crop(a, box):
    if box is None:
        return a
    x0, y0, x1, y1 = box
    return np.ascontiguousarray(a[y0:y1, x0:x1])


def rgb(p):
    return np.array(Image.open(p).convert("RGB"))


def overlay(rec, ev16, size=620, contours=True):
    """vlm_explain.overlay at `size` px: iso-lines of the up-sampled 16x16 evidence map, top-12 % boundary (yellow) and the
    absolute 0.5 level (cyan), black under-stroke; drawn only when the decision is not real (as in the deployed system)."""
    im = cv2.resize(crop(rgb(rec["image"]), rec["box"]), (size, size), interpolation=cv2.INTER_AREA)
    s = size / 448.0
    if contours and rec["decision"] != "real" and ev16 is not None:
        up = cv2.resize(ev16.astype(np.float32), (size, size), interpolation=cv2.INTER_LINEAR)
        for thr, col in ((float(np.quantile(up, 0.88)), (255, 220, 0)), (0.5, (0, 230, 255))):
            cs, _ = cv2.findContours((up >= thr).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(im, cs, -1, (0, 0, 0), max(1, int(round(4 * s)))); cv2.drawContours(im, cs, -1, col, max(1, int(round(2 * s))))
    return im


def contour_legend(cv, x, y, rec, w):
    if rec["decision"] == "real":
        return cv.para(x, y, "No contour: decision is real (contours are drawn only for fake / filter).", w, 6.6, MUTED)
    cv.rect(x, y + 10, 34, 8, fc="#FFDC00"); cv.text(x + 44, y + 22, "top-12 % evidence boundary", 6.6, MUTED)
    cv.rect(x, y + 46, 34, 8, fc="#00E6FF"); cv.text(x + 44, y + 58, "evidence 0.5 iso-line", 6.6, MUTED)
    return y + 76


def split_code(llm, composed):
    """Runs of composed text: spans that also occur in the LLM text (in order) vs spans the code inserted."""
    sm = difflib.SequenceMatcher(None, llm, composed, autojunk=False)
    runs = []; eq = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if j2 > j1:
            runs.append((composed[j1:j2], "llm" if tag == "equal" else "code"))
        if tag == "equal":
            eq += i2 - i1
    assert eq == len(llm), ("LLM text is not contained in the composed text", llm, composed)
    # shift each inserted span right while its first char equals the next LLM char (so ") (score x" + ")" -> ")" + " (score x)")
    for i in range(1, len(runs) - 1):
        (pt, pk), (t, k), (nt, nk) = runs[i - 1], runs[i], runs[i + 1]
        if k == "code" and pk == "llm" and nk == "llm":
            while t and nt and t[0] == nt[0]:
                pt += t[0]; t = t[1:] + nt[0]; nt = nt[1:]
            runs[i - 1], runs[i], runs[i + 1] = (pt, pk), (t, k), (nt, nk)
    return [r for r in runs if r[0]]


def colored(runs, llm_color=INK, code_color=CODE):
    return [(t, llm_color if k == "llm" else code_color, "normal") for t, k in runs]


def small_id(cv, x, y, s, w=None):
    return cv.para(x, y, s, w or (W - 2 * M), 6.0, "#9a9a9a")


def header(cv, title, sub, y=M):
    y = cv.para(M, y, title, W - 2 * M, 13, INK, "bold", lh=1.3) + 8
    y = cv.para(M, y, sub, W - 2 * M, 7.4, MUTED)
    cv.line(M, y + 14, W - M, y + 14, GRID, 1.0)
    return y + 40


def bar(cv, x, y, w, h, v, color, thr=None):
    cv.rect(x, y, w, h, fc=LIGHT)
    cv.rect(x, y, max(1.0, w * min(max(v, 0), 1)), h, fc=color)
    if thr is not None:
        cv.line(x + w * thr, y - 6, x + w * thr, y + h + 6, INK, 0.9)


CLS_COL = {"real": OK, "fake": ERR, "filter": FS.BINARY}
OP_NAMES = ("eye_enlargement", "face_slimming", "skin_brightening", "skin_smoothing")


# ================================================================== 1. pipeline example cards
P3EN = NL / "out/holdout_p3en1_7b.jsonl"; P3ZH = NL / "out/holdout_p3r1z_7b.jsonl"
PIPE = [
    ("ffpp_real:462__f0265", "Genuine photo (FF++ real frame)"),
    ("part_forgery:donor:422__f0283__mouth", "Mouth part forgery (donor mouth pasted into an FF++ real frame)"),
    ("alibaba:EyeEnlarging:17082", "Commercial eye enlargement (Alibaba retouching, FFHQ photo)"),
    ("ffpp_fake:Deepfakes:135_880__f0119", "Whole-face swap (FF++ Deepfakes)"),
]


def load_p3():
    D = {}
    for p in (P3EN, P3ZH):
        for r in jl(p):
            D[(r["id"], r["lang"], r["mode"], r["qi"])] = r
    return D


def shipped_runs(r):
    """(runs, gate words) for a style output: LLM / code split of the shipped text."""
    if r["source"] in ("greedy", "regen"):
        g = r[r["source"]]
        assert g["composed"] == r["shipped"]
        runs = split_code(g["llm_text"], g["composed"])
        note = "gate: passed (first LLM draft)" if r["source"] == "greedy" else "gate: first draft blocked, regenerated draft passed"
        return runs, note
    return [(r["shipped"], "code")], "gate: LLM drafts blocked; code fallback shipped"


def card_pipeline(k, rid, kind, P3):
    rec, ev, src = rec_of(rid)
    cv = Canvas()
    langs = (("en", "English (p3en1)"),) if EN_ONLY else (("en", "English (p3en1)"), ("zh", "Chinese (p3r1z)"))
    y = header(cv, f"Explanation pipeline, example {k}: {kind}",
               "Left: face crop given to the system, with the evidence contours of the detector. Middle: the structured record "
               "the detector writes. Right: the shipped explanation (final design: Qwen2.5-7B writes the words, code adds every "
               "number and the score sentence; " + ("English prompt p3en1" if EN_ONLY else "English prompt p3en1, Chinese prompt p3r1z")
               + "). Bottom: the eight user questions; four are answered by the LLM and checked, four by fixed code sentences.")
    y = small_id(cv, M, y - 22, f"record {rid}  ·  truth: {rec['truth']}  ·  detector {rec['model']}  ·  source {src}, "
                            "nl_v5/out/holdout_p3en1_7b.jsonl" + ("" if EN_ONLY else ", nl_v5/out/holdout_p3r1z_7b.jsonl")
                            + " (holdout set)") + 24
    # ---- column 1: image
    x1, w1 = M, 600
    img = overlay(rec, ev, 600)
    cv.image(x1, y, w1, w1, img)
    yy = contour_legend(cv, x1, y + w1 + 12, rec, w1)
    parts = rec["named_parts"]
    if rec["decision"] != "real":
        cv.text(x1, yy + 30, "named part: " + ", ".join(parts), 8.2, INK, "bold")
        yy += 50
    col_bottom = yy
    # ---- column 2: structured record
    x2, w2 = x1 + w1 + 50, 660
    cv.text(x2, y + 26, "Structured record (detector output)", 8.6, INK, "bold")
    yy = y + 80
    cv.text(x2, yy, "decision", 7.4, MUTED); cv.chip(x2 + 210, yy - 34, rec["decision"], CLS_COL[rec["decision"]], 7.4)
    yy += 70
    cv.text(x2, yy, "class scores (raw model outputs)", 7.4, MUTED); yy += 46
    for c in ("real", "fake", "filter"):
        v = rec["probabilities"][c]
        cv.text(x2, yy, c, 7.4, INK); bar(cv, x2 + 190, yy - 22, 330, 24, v, CLS_COL[c]); cv.text(x2 + 545, yy, f"{v:.2f}", 7.4, INK)
        yy += 46
    yy += 16
    cv.text(x2, yy, f"operation scores (threshold {rec['operation_threshold']})", 7.4, MUTED); yy += 46
    for o in OP_NAMES:
        v = rec["operations"][o]
        cv.text(x2, yy, o, 7.0, INK); bar(cv, x2 + 280, yy - 22, 240, 24, v, CODE, rec["operation_threshold"])
        cv.text(x2 + 545, yy, f"{v:.2f}", 7.4, INK, "bold" if v >= rec["operation_threshold"] else "normal")
        yy += 46
    yy += 16
    cv.text(x2, yy, "named_parts", 7.4, MUTED); cv.text(x2 + 210, yy, json.dumps(parts), 7.4, INK); yy += 40
    cv.text(x2, yy, "whole_face", 7.4, MUTED); cv.text(x2 + 210, yy, str(rec["whole_face"]).lower(), 7.4, INK); yy += 40
    if rec["decision"] == "real":
        yy = cv.para(x2, yy - 10, "For a real decision the fact list given to the LLM carries no part and no operation.", w2, 6.4, MUTED)
    yy = cv.para(x2, yy + 4, "calibration_note: " + rec["calibration_note"], w2, 6.4, MUTED)
    col_bottom = max(col_bottom, yy)
    # ---- column 3: explanation
    x3 = x2 + w2 + 50; w3 = W - M - x3
    cv.text(x3, y + 26, "Shipped explanation, general style", 8.6, INK, "bold")
    yy = y + 52
    cv.rect(x3, yy + 8, 26, 22, fc=INK); cv.text(x3 + 36, yy + 28, "written by the LLM", 6.8, MUTED)
    cv.rect(x3 + 330, yy + 8, 26, 22, fc=CODE); cv.text(x3 + 366, yy + 28, "added by code (numbers, score sentence)", 6.8, MUTED)
    yy += 66
    for lang, lab in langs:
        r = P3[(rid, lang, "general", None)]
        runs, note = shipped_runs(r)
        cv.text(x3, yy + 20, lab, 7.4, MUTED, "bold"); yy += 36
        yy = cv.rich(x3, yy, colored(runs), w3, 8.4 if lang == "en" else 8.6, bg={CODE: "#E6EEF7"})
        cv.text(x3, yy + 22, note, 6.6, OK if r["source"] == "greedy" else WARN); yy += 64
    col_bottom = max(col_bottom, yy)
    # ---- bottom: Q&A
    y = col_bottom + 30
    cv.line(M, y, W - M, y, GRID, 1.0); y += 26
    cv.text(M, y + 26, "Questions (English line; answers shipped to the user)", 8.6, INK, "bold"); y += 50
    cv.chip(M, y, "LLM", FS.OURS); cv.text(M + 110, y + 28, "LLM answer, passed the checks", 6.6, MUTED)
    cv.chip(M + 560, y, "fixed", "#555555"); cv.text(M + 680, y + 28, "fixed code sentence (no LLM)", 6.6, MUTED)
    cv.chip(M + 1140, y, "fallback", WARN); cv.text(M + 1290, y + 28, "LLM answer blocked; code answer shipped", 6.6, MUTED)
    y += 64
    colw = (W - 2 * M - 60) / 2
    order = list(NE.LLM_QI) + list(NE.FIXED_QI)
    ys = [y, y]
    for n, qi in enumerate(order):
        c = n // 4; x = M + c * (colw + 60); yy = ys[c]
        q = NE.QUESTIONS_EN[qi]
        if qi in NE.LLM_QI:
            r = P3[(rid, "en", "qa", qi)]
            if r["source"] == "fallback":
                tag, col = "fallback", WARN
            else:
                tag, col = "LLM", FS.OURS
            ans = r["shipped"]
        else:
            tag, col, ans, r = "fixed", "#555555", NE.FIXED_QA_EN[q], None
        xe = cv.chip(x, yy, tag, col)
        cv.text(xe + 16, yy + 28, q, 7.8, INK, "bold"); yy += 50
        yy = cv.para(x + 20, yy, ans, colw - 20, 7.8, INK)
        if r is not None and r["source"] == "fallback":
            g = r["greedy"]
            yy = cv.rich(x + 20, yy + 4, [("blocked LLM draft: ", WARN, "bold"), (g["llm_text"], MUTED, "normal")], colw - 20, 6.8)
            yy = cv.para(x + 20, yy, "failed check: " + "; ".join(g["llm_why"] + [w for w in g["full_why"] if w not in g["llm_why"]])
                         + " (the answer lacks a fact the question requires)", colw - 20, 6.4, WARN)
        elif r is not None:
            yy = cv.para(x + 20, yy, "gate: passed" + (" (first draft)" if r["source"] == "greedy" else " (regenerated)"), colw - 20, 6.4, OK)
        ys[c] = yy + 22
    cv.bump(max(ys))
    png = f"card_pipeline_example_{k}{'_en' if EN_ONLY else ''}.png"
    cv.render(OUT / png)
    return {"png": png, "ids": [rid], "src": [src, "nl_v5/out/holdout_p3en1_7b.jsonl",
            "nl_v5/out/holdout_p3r1z_7b.jsonl", "nl_v5/nl_core_en.py (FIXED_QA_EN, QUESTIONS_EN)", "evidence map: " +
            ("evidence_maps_holdout.npz" if src.endswith("holdout.jsonl") else "evidence_maps.npz")]}


# ================================================================== 2. VLM observation pairs
WRITERS = [("q2", "Qwen2-VL-7B", "obs_v3.jsonl", "judge_v3.jsonl"), ("q25", "Qwen2.5-VL-7B", "obs_v3.jsonl", "judge_v3.jsonl"),
           ("q32", "Qwen2.5-VL-32B", "obs_v3_32b.jsonl", "judge_v3_32b.jsonl"),
           ("q25l", "Qwen2.5-VL-7B + LoRA", "obs_v4_lora.jsonl", "judge_v4_lora.jsonl")]
PAIRS_SAME = ["part_forgery:donor:314__f0370__mouth", "alibaba:Whitening_90:17364", "ffhq_demo_edit:17074_slim"]
PAIRS_DIFF = ["part_forgery:sdxl:169__f0410__eyes", "part_forgery:donor:454__f0140__mouth", "part_forgery:donor:024__f0030__mouth"]


def face448_box(arr, box, size):
    im = cv2.resize(arr, (size, size), interpolation=cv2.INTER_AREA)
    H, Wd = arr.shape[:2]; x0, y0, x1, y1 = box; s = size / 448.0
    cv2.rectangle(im, (int(round(x0 * size / Wd)), int(round(y0 * size / H))), (int(round(x1 * size / Wd)) - 1, int(round(y1 * size / H)) - 1),
                  (255, 0, 0), max(2, int(round(2 * s))))
    return im


def native_pair(rec):
    a = crop(rgb(rec["image"]), rec["box"]); a0 = crop(rgb(rec["x0"]), rec["box"])
    if a0.shape != a.shape:
        a0 = cv2.resize(a0, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_AREA)
    return a, a0


def card_pairs():
    O, J = {}, {}
    for w, _, fo, fj in WRITERS:
        for r in jl(EX / fo):
            if r["writer"] == w and r["exp"] == "V3" and r["cond"] == "V3" and r["side"] in "mo":
                O[(w, r["id"], r["side"])] = r["observation"]
        for r in jl(EX / fj):
            if r["writer"] == w and r["judge"] == "q25" and r["exp"] == "V3" and r["test"] == "M1" and r["view"] == "Z" and r["cond"] == "V3":
                J[(w, r["id"], r["shown"])] = r["correct"]
    geo = json.load(open(EX / "v3_geometry.json", encoding="utf-8"))["regions"]
    cv = Canvas()
    y = header(cv, "What a vision-language model says about the edited region: manipulated image vs its untouched original",
               "Prompt v3: the VLM sees the face crop with the region box (red) and a zoom of the region, and writes one sentence "
               "about the region (no detector output given). Four writers on the same 177 development pairs. Judge: Qwen2.5-VL-7B, "
               "test M1 on the zoom view: it sees one side's image and picks which of the two sentences was written for it. "
               "\u2713 = picked the sentence written for that image, \u2717 = picked the other side's sentence; identical sentences "
               "are not sent to the judge (scored 0.5). Rows 1\u20133: all four writers produce identical sentences on both sides; "
               "rows 4\u20136: all four differ.")
    y = small_id(cv, M, y - 22, "sources: obs_v3.jsonl (q2, q25), obs_v3_32b.jsonl (q32), obs_v4_lora.jsonl (q25l), judge_v3.jsonl, "
                            "judge_v3_32b.jsonl, judge_v4_lora.jsonl (judge q25, test M1, view Z, cond V3), v3_geometry.json (region box); "
                            "development set, MATCHING_v3*.md / MATCHING_v4_LORA.md") + 24
    IM = 300; xs = M + 2 * IM + 30 + 50
    wl = 420; colw = (W - M - xs - wl - 40) / 2
    ids = []
    for n, rid in enumerate(PAIRS_SAME + PAIRS_DIFF):
        rec, ev, src = rec_of(rid); ids.append(rid)
        if n == 3:
            cv.line(M, y - 10, W - M, y - 10, INK, 1.2)
        a, a0 = native_pair(rec); box = geo[rid]["box"]
        cv.image(M, y, IM, IM, face448_box(a, box, IM)); cv.image(M + IM + 30, y, IM, IM, face448_box(a0, box, IM))
        cv.text(M, y + IM + 34, "manipulated", 7.0, MUTED); cv.text(M + IM + 30, y + IM + 34, "original", 7.0, MUTED)
        yy = small_id(cv, M, y + IM + 50, f"{rid}  ·  region: {', '.join(geo[rid]['parts'])}  ·  detector decision {rec['decision']}", 2 * IM + 30)
        imb = yy
        # sentence table
        cv.text(xs + wl, y + 26, "sentence for the manipulated image", 7.4, MUTED, "bold")
        cv.text(xs + wl + colw + 40, y + 26, "sentence for the original", 7.4, MUTED, "bold")
        ty = y + 48
        for w, name, _, _ in WRITERS:
            sm, so = O[(w, rid, "m")], O[(w, rid, "o")]
            cv.text(xs, ty + 30, name, 7.4, INK, "bold")
            ident = sm == so
            h0 = ty
            hs = []
            for c, (s, side) in enumerate(((sm, "m"), (so, "o"))):
                xc = xs + wl + c * (colw + 40)
                if ident:
                    mark, mc = "=", MUTED
                else:
                    ok = J.get((w, rid, side)); mark, mc = ("\u2713", OK) if ok else ("\u2717", ERR)
                cv.text(xc, h0 + 30, mark, 9.5, mc, "bold")
                hs.append(cv.para(xc + 46, h0 + 2, s, colw - 50, 8.0, INK))
            ty = max(hs) + 4
            if ident:
                ty = cv.para(xs + wl, ty, "identical on both sides; not sent to the judge (scores 0.5)", 2 * colw, 6.2, MUTED)
            ty += 12
            cv.line(xs, ty, W - M, ty, GRID, 0.6); ty += 6
        y = max(imb, ty) + 40
    cv.render(OUT / "card_vlm_observation_pairs.png")
    return {"png": "card_vlm_observation_pairs.png", "ids": ids, "src": ["obs_v3.jsonl", "obs_v3_32b.jsonl", "obs_v4_lora.jsonl",
            "judge_v3.jsonl", "judge_v3_32b.jsonl", "judge_v4_lora.jsonl", "v3_geometry.json", "evidence.jsonl (image, x0, box)"]}


# ================================================================== 3. FakeVLM vs ours
FV = [("alibaba:EyeEnlarging_90:17001", "commercial retouch (identity kept) \u2192 FakeVLM says fake"),
      ("alibaba:Smoothing_90:17049", "commercial retouch (identity kept) \u2192 FakeVLM says fake"),
      ("part_forgery:sd:190__f0208__mouth", "mouth forgery \u2192 FakeVLM says real"),
      ("ffhq_demo_edit:17066_mouth", "mouth forgery \u2192 FakeVLM says real")]
P3EN_DEV = NL / "out/dev_p3en1_7b.jsonl"


def card_fakevlm():
    F = {(r["id"], r["side"]): r for r in jl(EX / "fakevlm_f.jsonl")}
    D = {(r["id"], r["mode"]): r for r in jl(P3EN_DEV)}
    cv = Canvas()
    y = header(cv, "FakeVLM (fine-tuned LLaVA-1.5-7B) vs our checked explanation, on images where FakeVLM's verdict is wrong",
               "FakeVLM (lingcco/fakeVLM, 4-bit) reads the 448 px face crop and answers real / fake with a free-text explanation "
               "(generation capped at 200 new tokens; 'truncated' marks a cut-off text). Our side: detector decision with the "
               "evidence contour and the shipped English explanation (final design p3en1, LLM words + code numbers, checked). "
               "FakeVLM has only real / fake, so an identity-keeping commercial retouch called 'fake' is wrong under the three-class "
               "definition (real / fake / filter).")
    y = small_id(cv, M, y - 22, "sources: fakevlm_f.jsonl (verdict, explanation), fakevlm_inputs/ (its input image), evidence.jsonl + "
                            "evidence_maps.npz, nl_v5/out/dev_p3en1_7b.jsonl (general style, shipped); development set") + 24
    IM = 360; xt1 = M + 2 * IM + 30 + 50; wt = (W - M - xt1 - 50) / 2; xt2 = xt1 + wt + 50
    ids = []
    for rid, kind in FV:
        f = F[(rid, "m")]; rec, ev, src = rec_of(rid); ids.append(rid)
        r = D[(rid, "general")]
        cv.text(M, y + 30, kind, 9.0, INK, "bold"); y += 52
        small_id(cv, M, y, f"{rid}  ·  truth: {f['truth']}  ·  FakeVLM verdict: {f['verdict']}  ·  our decision: {rec['decision']}")
        y += 34
        cv.image(M, y, IM, IM, rgb(EX / "fakevlm_inputs" / f["file"]))
        cv.image(M + IM + 30, y, IM, IM, overlay(rec, ev, IM))
        cv.text(M, y + IM + 32, "FakeVLM input", 6.8, MUTED); cv.text(M + IM + 30, y + IM + 32, "ours: evidence contour", 6.8, MUTED)
        yi = y + IM + 50
        cv.text(xt1, y + 26, "FakeVLM", 8.4, INK, "bold"); xe = cv.chip(xt1 + 160, y, "verdict: " + f["verdict"], ERR)
        yy = cv.para(xt1, y + 54, f["explanation"] + (" [truncated]" if f["truncated"] else ""), wt, 7.0, INK)
        cv.text(xt2, y + 26, "Ours", 8.4, INK, "bold"); cv.chip(xt2 + 110, y, "decision: " + rec["decision"], CLS_COL[rec["decision"]])
        runs, note = shipped_runs(r)
        y2 = cv.rich(xt2, y + 54, colored(runs), wt, 8.0, bg={CODE: "#E6EEF7"})
        y2 = cv.para(xt2, y2 + 4, note + ("  ·  named part: " + ", ".join(rec["named_parts"])), wt, 6.6, OK if r["source"] == "greedy" else WARN)
        y = max(yi, yy, y2) + 30
        cv.line(M, y, W - M, y, GRID, 1.0); y += 24
    cv.render(OUT / "card_fakevlm_vs_ours.png")
    return {"png": "card_fakevlm_vs_ours.png", "ids": ids, "src": ["fakevlm_f.jsonl", "fakevlm_inputs/", "evidence.jsonl",
            "evidence_maps.npz", "nl_v5/out/dev_p3en1_7b.jsonl"]}


# ================================================================== 4. gate catches
def card_gate():
    p2en1 = {(r["id"], r["mode"], r["qi"]): r for r in jl(NL / "out/holdout_p2en1_7b.jsonl")}
    p3en1 = jl(NL / "out/holdout_p3en1_7b.jsonl")
    G = json.load(open(NL / "out/gate_v3_rerun_holdout.json", encoding="utf-8"))["en"]

    def from_rerun(sect, i):
        b = [x for x in G[sect]["blocked"] if x["id"] == i][0]
        return b["text"], b["why"], b["after_text"], b["after"]

    rows = []
    t, w, s, a = from_rerun("general", "ffpp_real:135__f0264")
    rows.append(("Certainty clause", "Talks about how certain the model is. Certainty words are banned outside the fixed answers, "
                 "because the score is not a calibrated probability.", "ffpp_real:135__f0264", "p2en1, general style; gate v3 re-run",
                 "nl_v5/out/gate_v3_rerun_holdout.json (en/general)", t, w, s, a, ["certain"]))
    t, w, s, a = from_rerun("qa0: Why is it judged fake?", "ffpp_real:485__f0151")
    rows.append(("Score attached to a part", "Puts the decision score on the region ('a score of 0.97 concentrated on the eyes'); "
                 "the decision score belongs to the whole image, not to a part.", "ffpp_real:485__f0151",
                 "p2en1, question 'Why is it judged fake?'; gate v3 re-run", "nl_v5/out/gate_v3_rerun_holdout.json (en/qa0)",
                 t, w, s, a, ["with a score of 0.97 concentrated on the eyes"]))
    r = p2en1[("ffpp_real:135__f0061", "pro", None)]
    rows.append(("Invented operation", "Says the operations below the threshold (skin smoothing, skin whitening) 'contribute to the "
                 "overall retouched appearance', i.e. treats operations the detector did not find as applied.",
                 "ffpp_real:135__f0061", "p2en1, expert style", "nl_v5/out/holdout_p2en1_7b.jsonl", r["greedy"]["text"],
                 r["greedy"]["why"], r["shipped"], r["source"], ["all operations below the threshold contribute to the overall retouched appearance"]))
    r = p2en1[("ffpp_real:358__f0053", "qa", 7)]
    rows.append(("\"Compared with the original\"", "Refers to how the photo compares with the original; the system never sees "
                 "an original photo. The answer also drops the evidence region the question needs.", "ffpp_real:358__f0053",
                 "p2en1, question 'Why is it not real?'", "nl_v5/out/holdout_p2en1_7b.jsonl", r["greedy"]["text"],
                 r["greedy"]["why"], r["shipped"], r["source"], ["compares to the original", "cannot be certain"]))
    r = p2en1[("ffpp_real:135__f0119", "pro", None)]
    rows.append(("Number not in the record", "Writes 'a mean evidence of 0.68', a number that is not in the structured record. "
                 "(In the final design the LLM may write no number at all, G10 digit / number word; G10 never fired on a real output, "
                 "so this H4 catch from the earlier design stands in for it.)", "ffpp_real:135__f0119", "p2en1, expert style",
                 "nl_v5/out/holdout_p2en1_7b.jsonl", r["greedy"]["text"], r["greedy"]["why"], r["shipped"], r["source"], ["0.68"]))
    fb = [x for x in p3en1 if x["source"] == "fallback" and x["id"] != "alibaba:EyeEnlarging:17082" and x["decision"] == "fake"]
    r = fb[0] if fb else [x for x in p3en1 if x["source"] == "fallback" and x["id"] != "alibaba:EyeEnlarging:17082"][0]
    rows.append(("Missing fact", "The answer leaves out a fact the question requires (final design: each LLM question has its list of "
                 "facts that must appear).", r["id"], f"p3en1 (final design), question '{r['question']}'",
                 "nl_v5/out/holdout_p3en1_7b.jsonl", r["greedy"]["llm_text"], r["greedy"]["llm_why"], r["shipped"], r["source"], []))
    cv = Canvas()
    y = header(cv, "What the checks block: six real LLM texts and what the user received instead",
               "Each row is an LLM text that was generated and blocked by a deterministic check (gate). Left: the blocked text, with "
               "the offending words highlighted; right: what was shipped (a code fallback written only from the structured record). "
               "Holdout set, Qwen2.5-7B.")
    y += 14
    xl = M + 520; wl = (W - M - xl - 50) / 2; xr = xl + wl + 50
    cv.text(xl, y + 20, "blocked LLM text", 7.4, MUTED, "bold"); cv.text(xr, y + 20, "shipped instead", 7.4, MUTED, "bold"); y += 44
    ids = []; srcs = set()
    for name, words, rid, ver, src, text, why, shipped, after, hl in rows:
        ids.append(rid); srcs.add(src)
        cv.line(M, y, W - M, y, GRID, 1.0); y += 18
        yl = cv.para(M, y + 2, name, 470, 9.0, ERR, "bold", lh=1.25)
        yl = cv.para(M, yl + 4, words, 480, 6.8, INK)
        yl = cv.para(M, yl + 6, "check: " + "; ".join(why), 480, 6.0, MUTED)
        yl = small_id(cv, M, yl + 4, f"{rid}  ·  {ver}  ·  {src}", 480)
        # highlight spans
        runs = []; pos = 0
        spans = sorted([(text.find(h), text.find(h) + len(h)) for h in hl if h and text.find(h) >= 0])
        for a0, a1 in spans:
            if a0 < pos:
                continue
            runs.append((text[pos:a0], INK, "normal")); runs.append((text[a0:a1], ERR, "bold")); pos = a1
        runs.append((text[pos:], INK, "normal"))
        y1 = cv.rich(xl, y + 6, runs, wl, 7.8, bg={ERR: "#FBE5D6"})
        tag = {"fallback": "code fallback", "regen": "regenerated LLM text", "greedy": "LLM text"}.get(after, after)
        cv.chip(xr, y + 6, tag, WARN if after == "fallback" else OK, 6.4)
        y2 = cv.para(xr, y + 64, shipped, wl, 7.8, INK)
        y = max(yl, y1, y2) + 26
    cv.render(OUT / "card_gate_catches.png")
    return {"png": "card_gate_catches.png", "ids": ids, "src": sorted(srcs)}


# ================================================================== 5. one record across versions
HIST_ID = "alibaba:EyeEnlarging_90:17001"


def card_history():
    rid = HIST_ID; rec, ev, src = rec_of(rid)
    v0 = [r for r in jl(EX / "V1_v0.jsonl") if r["id"] == rid][0]
    v0v = [r for r in jl(EX / "V1_v0.validated.jsonl") if r["id"] == rid][0]
    p2 = [r for r in jl(NL / "out/dev_p2_7b.jsonl") if r["id"] == rid and r["mode"] == "general"][0]
    p2en = [r for r in jl(NL / "out/dev_p2en1_7b.jsonl") if r["id"] == rid and r["mode"] == "general"][0]
    p3 = [r for r in jl(NL / "out/dev_p3en1_7b.jsonl") if r["id"] == rid and r["mode"] == "general"][0]
    cv = Canvas()
    y = header(cv, "One record through the design versions",
               "The same image and detector record, explained by each design in turn (development set). The detector output never "
               "changes; only the text layer does. 'Gate' = the deterministic checks of that version.")
    y = small_id(cv, M, y - 22, f"record {rid}  ·  sources: V1_v0.jsonl + V1_v0.validated.jsonl, nl_v5/out/dev_p2_7b.jsonl, "
                            "nl_v5/out/dev_p2en1_7b.jsonl, nl_v5/out/dev_p3en1_7b.jsonl (general style), evidence.jsonl + evidence_maps.npz") + 24
    IM = 520
    cv.image(M, y, IM, IM, overlay(rec, ev, IM))
    yy = contour_legend(cv, M, y + IM + 10, rec, IM)
    xr = M + IM + 60; wr = W - M - xr
    yy2 = cv.para(xr, y + 4, f"Image: Alibaba commercial eye-enlargement edit of FFHQ photo 17001 (truth: {rec['truth']}).", wr, 8.0)
    yy2 = cv.para(xr, yy2 + 8, f"Detector record: decision {rec['decision']}; class scores real {rec['probabilities']['real']:.2f}, "
                               f"fake {rec['probabilities']['fake']:.2f}, filter {rec['probabilities']['filter']:.2f}; operation scores "
                  + ", ".join(f"{o} {rec['operations'][o]:.2f}" for o in OP_NAMES) + f" (threshold {rec['operation_threshold']}); "
                  f"named_parts {json.dumps(rec['named_parts'])}.", wr, 8.0)
    yy2 = cv.para(xr, yy2 + 8, "The detector itself scores skin brightening (whitening), not eye enlargement, above the threshold on this image; every text below can only "
                               "repeat what the record says.", wr, 7.2, MUTED)
    y = max(yy, yy2, y + IM) + 40
    rows = [
        ("VLM v0", "Qwen2-VL-7B sees the image with contours + the record, writes JSON (prompt v0)",
         [("verdict_restated: ", MUTED, "normal"), (v0["parsed"]["verdict_restated"], INK, "normal"),
          ("   named_region: ", MUTED, "normal"), (json.dumps(v0["parsed"]["named_region"], ensure_ascii=False), INK, "normal"),
          ("   operations_mentioned: ", MUTED, "normal"), (json.dumps(v0["parsed"]["operations_mentioned"], ensure_ascii=False), INK, "normal"),
          ("\n", INK, "normal"), ("explanation_zh: ", MUTED, "normal"), (v0["explanation_zh"], INK, "normal"),
          ("\n", INK, "normal"), ("explanation_en: ", MUTED, "normal"), (v0["explanation_en"], INK, "normal")],
         ERR, "failed: " + "; ".join(v0v["why"]) + "  (verdict written as '濾鏡' instead of the class key; region '整臉' and only one sentence)",
         "checks H1–H6 run offline by validate_text.py (HALLUCINATION_v0.md); v0 shipped the parsed text"),
        ("LLM p2 (Chinese)", "Qwen2.5-7B, text only, gets a fact list from the record (no image)",
         [(p2["greedy"]["text"], INK, "normal")], OK if not p2["greedy"]["why"] else ERR,
         "gate v2: passed" if not p2["greedy"]["why"] else "gate v2: " + "; ".join(p2["greedy"]["why"]),
         f"shipped: {p2['source']} text"),
        ("LLM p2en1 (English)", "same design, English prompt",
         [(p2en["greedy"]["text"], INK, "normal")], ERR,
         "gate v2: blocked, " + "; ".join(p2en["greedy"]["why"]) + " (the evidence region 'whole face' is missing); regenerated draft "
         "blocked for the same reason: " + "; ".join(p2en["regen"]["why"]),
         None),
        ("LLM p3en1 (final)", "LLM writes words only; code adds every number and the score sentence (blue)",
         colored(split_code(p3["greedy"]["llm_text"], p3["greedy"]["composed"])), OK if p3["greedy"]["passed"] else ERR,
         "gate v3 + LLM-part gate (H1\u2013H5, G7\u2013G10, facts): passed" if p3["greedy"]["passed"] else "blocked", f"shipped: {p3['source']} text"),
    ]
    for lab, desc, runs, gc, gate, shipnote in rows:
        cv.line(M, y, W - M, y, GRID, 1.0); y += 18
        cv.text(M, y + 32, lab, 9.4, INK, "bold")
        yl = cv.para(M, y + 52, desc, 460, 6.8, MUTED)
        yt = cv.rich(M + 520, y + 6, runs, W - 2 * M - 520, 8.2, bg={CODE: "#E6EEF7"})
        yt = cv.para(M + 520, yt + 4, gate, W - 2 * M - 520, 6.8, gc)
        if shipnote is None:
            yt = cv.rich(M + 520, yt + 8, [("shipped instead (code fallback): ", WARN, "bold"), (p2en["shipped"], INK, "normal")],
                         W - 2 * M - 520, 8.2)
        else:
            yt = cv.para(M + 520, yt, shipnote, W - 2 * M - 520, 6.4, MUTED)
        y = max(yl, yt) + 24
    cv.render(OUT / "card_llm_history.png")
    return {"png": "card_llm_history.png", "ids": [rid], "src": ["V1_v0.jsonl", "V1_v0.validated.jsonl", "nl_v5/out/dev_p2_7b.jsonl",
            "nl_v5/out/dev_p2en1_7b.jsonl", "nl_v5/out/dev_p3en1_7b.jsonl", "evidence.jsonl", "evidence_maps.npz"]}


# ================================================================== main
def main():
    which = sys.argv[1:] or ["pipeline", "pairs", "fakevlm", "gate", "history"]
    made = []
    if "pipeline" in which:
        P3 = load_p3()
        for k, (rid, kind) in enumerate(PIPE, 1):
            made.append(card_pipeline(k, rid, kind, P3))
    if "pairs" in which:
        if EN_ONLY:
            raise SystemExit("pairs: the observation sentences are Chinese model outputs; --en-only would leave the card empty")
        made.append(card_pairs())
    if "fakevlm" in which:
        made.append(card_fakevlm())
    if "gate" in which:
        made.append(card_gate())
    if "history" in which:
        made.append(card_history())
    return made


if __name__ == "__main__":
    main()
