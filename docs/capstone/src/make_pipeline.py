"""System diagram for the capstone poster: docs/capstone/pipeline.svg + pipeline.png (2400 px wide).

Text is converted to paths in the SVG (svg.fonttype = 'path'), so the file renders without Microsoft JhengHei installed.
Run: python docs/capstone/src/make_pipeline.py [--en]   (--en writes pipeline_en.svg / pipeline_en.png with English labels)

Drawn to match the shipped system (2026-10-27): no language model anywhere. Photo -> face crop -> detector ->
evidence map -> part naming -> record -> sentences composed by code -> checks (H1-H6) -> output.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = Path(__file__).resolve().parents[1]
EN = "--en" in sys.argv


def L(zh, en):
    return en if EN else zh


for f in ("msjh.ttc", "msjhbd.ttc"):
    p = Path("C:/Windows/Fonts") / f
    if p.exists():
        font_manager.fontManager.addfont(str(p))
plt.rcParams["font.family"] = ["Microsoft JhengHei"]
plt.rcParams["svg.fonttype"] = "path"
plt.rcParams["axes.unicode_minus"] = False

INK = "#1f2933"; MUTED = "#52606d"; LINE = "#7b8794"
CAT = {  # fill, edge
    "io":    ("#f5f7fa", "#9aa5b1"),
    "model": ("#e3ecfb", "#2f5fb3"),
    "prog":  ("#e6f2ee", "#2d7a5f"),
    "check": ("#efe8f8", "#6b46c1"),
}

W, H = 16.0, 6.3
fig = plt.figure(figsize=(W, H), dpi=150)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(0, H); ax.axis("off")
fig.patch.set_facecolor("white")

BW, BH = 2.62, 1.55


def box(cx, cy, title, sub, cat, w=BW, h=BH, num=None):
    fc, ec = CAT[cat]
    ax.add_patch(FancyBboxPatch((cx - w / 2, cy - h / 2), w, h, boxstyle="round,pad=0,rounding_size=0.14",
                                fc=fc, ec=ec, lw=2.0, zorder=2))
    dy = 0.28 if h > 1.3 else 0.2
    ax.text(cx, cy + (dy if sub else 0), title, ha="center", va="center", fontsize=17, fontweight="bold", color=INK, zorder=3)
    if sub:
        ax.text(cx, cy - (0.33 if h > 1.3 else 0.22), sub, ha="center", va="center", fontsize=10.8, color=MUTED, zorder=3, linespacing=1.35)
    if num is not None:
        ax.text(cx - w / 2 + 0.17, cy + h / 2 - 0.2, str(num), ha="center", va="center", fontsize=10.5, color=ec,
                fontweight="bold", zorder=3)
    return (cx, cy, w, h)


def arrow(p, q, color=LINE, style="-|>", lw=2.0, rad=0.0, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=18, color=color, lw=lw, linestyle=ls,
                                 connectionstyle=f"arc3,rad={rad}", zorder=1, shrinkA=0, shrinkB=0))


def tag(x, y, text, cat):
    fc, ec = CAT[cat]
    ax.text(x, y, text, ha="center", va="center", fontsize=11.5, color=ec, fontweight="bold", zorder=4,
            bbox=dict(boxstyle="round,pad=0.32,rounding_size=0.25", fc="white", ec=ec, lw=1.4, ls="--"))


# ---- row 1 (left to right): photo -> crop -> detector -> evidence map -> part naming
y1 = 4.45
xs1 = [1.55, 4.65, 7.75, 10.85, 13.95]
r1 = [(L("照片", "Photo"),
       L("使用者上傳或拍照\n瀏覽器內處理，不上傳", "uploaded or taken by the user\nprocessed in the browser"), "io"),
      (L("人臉偵測與裁切", "Face detection, crop"),
       L("MediaPipe 特徵點\n依訓練方式裁臉\n找不到臉就停止，不判定", "MediaPipe landmarks,\naligned face crop;\nstops if no face is found"), "prog"),
      (L("偵測器", "Detector"),
       L("CLIP ViT-L/14 + LoRA\n三類判定：真實／偽造／美顏", "CLIP ViT-L/14 + LoRA\nreal / fake / beautified"), "model"),
      (L("證據圖", "Evidence map"),
       L("證據頭：16×16 的證據位置圖\n美顏時另給磨皮分數\n（其他三種操作不支援）",
         "evidence head: 16×16 map of\nwhere the evidence sits; for\nbeautified, a smoothing score only"), "model"),
      (L("部位對應", "Part naming"),
       L("眼／鼻／嘴／皮膚／輪廓\n取證據平均最高的部位\n並畫出該部位的輪廓",
         "eyes, nose, mouth, skin, contour\nhighest mean evidence,\noutline drawn"), "prog")]
B1 = [box(x, y1, t, s, c, num=i + 1) for i, (x, (t, s, c)) in enumerate(zip(xs1, r1))]
for a, b in zip(B1, B1[1:]):
    arrow((a[0] + a[2] / 2 + 0.05, y1), (b[0] - b[2] / 2 - 0.05, y1))

# ---- row 2 (left to right): record -> sentences by code -> checks -> output
y2 = 1.65
W2 = [2.9, 3.7, 3.6, 2.6]
GAP = 0.5
x0 = (W - (sum(W2) + GAP * (len(W2) - 1))) / 2
xs2 = []
for w in W2:
    xs2.append(x0 + w / 2); x0 += w + GAP
r2 = [(L("結構化紀錄", "Record"),
       L("判定、分數、點名的部位、操作\n整理成一筆紀錄", "decision, scores, named part,\noperation: one structured record"), "prog"),
      (L("程式寫句子", "Sentences by code"),
       L("固定模板，每個數字都從紀錄複製\n答不了的四個問題用固定句回答",
         "fixed templates; every number\ncopied from the record; fixed\nanswers to four open questions"), "prog"),
      None,
      (L("輸出", "Output"),
       L("判定、證據輪廓、\n解釋句子", "decision, evidence outline,\nsentences"), "io")]
B2 = []
for i, (x, w, r) in enumerate(zip(xs2, W2, r2)):
    if r is None:
        B2.append(None); continue
    B2.append(box(x, y2, r[0], r[1], r[2], w=w, num=i + 6))
# the check box: same top as the row, taller, title at the top and one line per check
CHK_H = 1.75
cy = y2 + BH / 2 - CHK_H / 2
fc, ec = CAT["check"]
ax.add_patch(FancyBboxPatch((xs2[2] - W2[2] / 2, cy - CHK_H / 2), W2[2], CHK_H, boxstyle="round,pad=0,rounding_size=0.14",
                            fc=fc, ec=ec, lw=2.0, zorder=2))
ax.text(xs2[2], y2 + BH / 2 - 0.36, L("自動查核", "Automatic checks"), ha="center", va="center", fontsize=17, fontweight="bold", color=INK, zorder=3)
ax.text(xs2[2] - W2[2] / 2 + 0.17, y2 + BH / 2 - 0.2, "8", ha="center", va="center", fontsize=10.5, color=ec, fontweight="bold", zorder=3)
checks = L("六項規則 H1–H6・分數對門檻\n事實完整・不得宣稱確定\n分數不得掛在部位上",
           "H1–H6 · score vs threshold\nall facts · no certainty claims\nscore not attached to a part")
ax.text(xs2[2], y2 + BH / 2 - 0.66, checks, ha="center", va="top", fontsize=11.5, color=MUTED, zorder=3, linespacing=1.45)
chk = (xs2[2], cy, W2[2], CHK_H)
B2[2] = (xs2[2], y2, W2[2], BH)
for a, b in zip(B2, B2[1:]):
    arrow((a[0] + a[2] / 2 + 0.05, y2), (b[0] - b[2] / 2 - 0.05, y2))
ax.text((B2[2][0] + B2[2][2] / 2 + B2[3][0] - B2[3][2] / 2) / 2, y2 + 0.2, L("通過", "pass"), ha="center", va="bottom", fontsize=11.5, color="#2d7a5f", fontweight="bold")

# row 1 end -> row 2 start: down from 部位對應, along a gutter, into 結構化紀錄
gy = (y1 - BH / 2 + y2 + BH / 2) / 2
ax.plot([xs1[4], xs1[4]], [y1 - BH / 2 - 0.05, gy], color=LINE, lw=2.0, zorder=1)
ax.plot([xs1[4], xs2[0]], [gy, gy], color=LINE, lw=2.0, zorder=1)
arrow((xs2[0], gy), (xs2[0], y2 + BH / 2 + 0.05))

# ---- validation annotations
tag(xs1[4] - (0.6 if EN else 0), y1 + BH / 2 + 0.38, L("驗證：還原測試（點名部位是否真的造成判定）", "Validated: restoration test of the named part"), "check")
tag(chk[0] - 0.4, y2 + BH / 2 + 0.38, L("驗證：幻覺查核（每段文字出貨前）", "Validated: hallucination check (every text before display)"), "check")

# ---- legend (one row, top left)
lx, ly = 0.35, 5.85
for k, lab in [("model", L("神經網路模型", "neural network")), ("prog", L("程式（固定規則）", "code (fixed rules)")), ("check", L("查核", "check"))]:
    fc, ec = CAT[k]
    ax.add_patch(FancyBboxPatch((lx, ly - 0.11), 0.32, 0.22, boxstyle="round,pad=0,rounding_size=0.04", fc=fc, ec=ec, lw=1.5))
    t = ax.text(lx + 0.43, ly, lab, ha="left", va="center", fontsize=11.5, color=INK)
    lx += 0.43 + (0.11 if EN else 0.2) * len(lab) + 0.5

stem = "pipeline_en" if EN else "pipeline"
fig.savefig(OUT / f"{stem}.png", dpi=150, facecolor="white")
fig.savefig(OUT / f"{stem}.svg", facecolor="white")
print("wrote", OUT / f"{stem}.png", OUT / f"{stem}.svg")
