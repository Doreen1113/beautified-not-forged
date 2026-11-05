"""System figure of the capstone, drawn from one real record instead of text boxes (2026-10-28).

The example is the part-level forgery part_forgery:donor:454__f0140__mouth (FF++ genuine frame 454, mouth replaced from a donor):
the shipped model calls it fake (1.00), the evidence head puts 0.98 of its mean evidence on the mouth, the code names the mouth,
composes three sentences from the record, and the restoration test (mouth restored from the original) flips the score to 0.08.
Sources: docs/demo_ru/test/fixture_ev.json (ONNX record of the page), results/research/explain_vlm_20261012/evidence.jsonl
(restoration test), docs/demo_ru/explain_t2.js (sentence templates), docs/paper_v2/occlusion_regions.py (part masks).

    python docs/capstone/src/make_pipeline_v2.py [--zh]   -> docs/capstone/pipeline_en.{pdf,png,svg} (pipeline.* with --zh)
"""
import json
import sys
import textwrap
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

B = Path(r"C:\My_Project\AIGC"); OUT = Path(__file__).resolve().parents[1]
for p in ("docs/paper_v2", "results/research/explain_vlm_20261012", "results/research/retouch_unified_20260929", "."):
    sys.path.insert(0, str(B / p))
import figstyle as FS  # noqa: E402
FS.apply()
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402
from occlusion_regions import region_masks  # noqa: E402
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402

ZH = "--zh" in sys.argv
if ZH:
    for f in ("msjh.ttc", "msjhbd.ttc"):
        if (Path("C:/Windows/Fonts") / f).exists():
            font_manager.fontManager.addfont(str(Path("C:/Windows/Fonts") / f))
    plt.rcParams["font.family"] = ["Microsoft JhengHei"]; plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "Arial"]


def L(zh, en):
    return zh if ZH else en


# ---------------- data: the record ----------------
ID = "part_forgery:donor:454__f0140__mouth"
ev = json.loads((B / "docs/demo_ru/test/fixture_ev.json").read_text(encoding="utf-8"))
R = next(r for r in ev["records"] if r["id"] == ID); rec = R["record"]
J = next(json.loads(l) for l in (B / "results/research/explain_vlm_20261012/evidence.jsonl").open(encoding="utf-8") if json.loads(l)["id"] == ID)
img = np.array(Image.open(B / "docs/demo_ru/test" / R["file"]).convert("RGB")); h, w = img.shape[:2]
lm = np.asarray(get_landmarks(np.ascontiguousarray(img)), np.float32)[:, :2]
M = region_masks(img, lm)
e16 = np.asarray(R["evidence_map16"], np.float32)
e_up = cv2.resize(e16, (w, h), interpolation=cv2.INTER_LINEAR)
parts = rec["evidence_mean_per_part"]; named = rec["named_parts"][0]; prob = rec["probabilities"]
rt = J["restoration_test"]
PART_EN = {"eyes": "eyes", "nose": "nose", "mouth": "mouth", "skin": "skin", "contour": "face contour"}
PART_ZH = {"eyes": "眼睛", "nose": "鼻子", "mouth": "嘴巴", "skin": "皮膚", "contour": "臉部輪廓"}
CLS_EN = {"real": "real", "fake": "fake", "filter": "beautified"}; CLS_ZH = {"real": "真實", "fake": "偽造", "filter": "美顏"}
dec = rec["decision"]
S1 = L(f"模型判定為{CLS_ZH[dec]}（分數 {prob[dec]:.2f}）。", f"The model's decision is {CLS_EN[dec]} (score {prob[dec]:.2f}).")
S2 = L(f"證據集中在{PART_ZH[named]}（evidence 平均 {parts[named]:.2f}）。", f"The evidence is concentrated on the {PART_EN[named]} (mean evidence {parts[named]:.2f}).")
S3 = L("分數是模型原始輸出，不是校準過的機率。", "Scores are raw model outputs, not calibrated probabilities.")

# ---------------- palette and type ----------------
MODEL, CODE, CHECK = "#0F4D92", "#2d7a5f", "#6b46c1"
MODEL_BG = "#e8eef8"
FAKE, REAL, FILT = "#C0392B", "#2d7a5f", "#C98A00"
INK, MUTED, GRID = FS.INK, FS.MUTED, FS.GRID
F_TITLE, F_CAP, F_SMALL, F_MONO = 7.5, 5.2, 5.2, 5.0
MONO = "Microsoft JhengHei" if ZH else "DejaVu Sans Mono"

W, H = 7.16, 3.15
fig = plt.figure(figsize=(W, H))
bg = fig.add_axes([0, 0, 1, 1]); bg.set_xlim(0, W); bg.set_ylim(0, H); bg.axis("off")


def ax_in(x, y, w_, h_):
    return fig.add_axes([x / W, y / H, w_ / W, h_ / H])


def stage(x0, x1, num, title, col):
    bg.add_patch(Rectangle((x0, H - 0.27), x1 - x0, 0.04, color=col, lw=0))
    bg.add_patch(plt.Circle((x0 + 0.09, H - 0.13), 0.075, color=col, lw=0))
    bg.text(x0 + 0.09, H - 0.13, str(num), ha="center", va="center", fontsize=6, color="white", fontweight="bold")
    bg.text(x0 + 0.21, H - 0.13, title, ha="left", va="center", fontsize=F_TITLE, color=INK, fontweight="bold")


def chevron(x, y):
    bg.add_patch(FancyArrowPatch((x - 0.08, y), (x + 0.08, y), arrowstyle="-|>", mutation_scale=11, color=MUTED, lw=1.1))


def show(ax, arr):
    ax.imshow(arr); ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor(GRID); sp.set_linewidth(0.6)


def caption(x, y, text, col=MUTED, ha="left"):
    bg.text(x, y, text, ha=ha, va="top", fontsize=F_CAP, color=col, linespacing=1.3)


IMW = 1.12; IMH = IMW * h / w; IMY = H - 0.42 - IMH; YMID = IMY + IMH / 2
C1, C2, C3, C4 = 0.06, 1.52, 4.02, 5.46          # column starts
E1, E2, E3, E4 = 1.34, 3.86, 5.30, 7.12          # column ends

# ---- stage 1: photo, landmarks, crop box ----
stage(C1, E1, 1, L("照片與裁臉", "Photo, face crop"), CODE)
a1 = ax_in(C1 + 0.10, IMY, IMW, IMH); show(a1, img)
a1.scatter(lm[::3, 0], lm[::3, 1], s=1.0, color="#ffffff", alpha=0.75, lw=0)
x0, y0 = lm[:, 0].min(), lm[:, 1].min(); x1, y1 = lm[:, 0].max(), lm[:, 1].max(); mw, mh = (x1 - x0) * 0.35, (y1 - y0) * 0.35
a1.add_patch(Rectangle((max(0, x0 - mw), max(0, y0 - mh)), min(w, x1 + mw) - max(0, x0 - mw), min(h, y1 + mh) - max(0, y0 - mh),
                       fill=False, ec="#ffd166", lw=0.9, ls=(0, (3, 2))))
caption(C1 + 0.10, IMY - 0.08, L("478 個 MediaPipe 特徵點（畫 1/3）\n依訓練方式裁出對齊的臉\n全部在瀏覽器內完成",
                                 "478 MediaPipe landmarks\n(one in three drawn)\naligned crop, as in training\nruns in the browser"))
chevron((E1 + C2) / 2, YMID)

# ---- stage 2: detector with its outputs, and the evidence head ----
stage(C2, E2, 2, L("偵測器與證據頭", "Detector and evidence head"), MODEL)
bx, bw, bh = C2 + 0.04, 1.08, 0.66; by = IMY + IMH - bh
bg.add_patch(FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0,rounding_size=0.05", fc=MODEL_BG, ec=MODEL, lw=0.9))
bg.text(bx + bw / 2, by + bh - 0.12, "CLIP ViT-L/14 + LoRA", ha="center", va="center", fontsize=F_TITLE - 0.5, color=INK, fontweight="bold")
for i, t in enumerate((L("r16：訓練 3.2M／306M 參數", "r16: 3.2 M of 306 M trained"), L("三類分數、16×16 證據圖", "3 class scores, 16×16 evidence"),
                       L("磨皮分數（判美顏時）", "smoothing score (if beautified)"))):
    bg.text(bx + bw / 2, by + bh - 0.27 - 0.13 * i, t, ha="center", va="center", fontsize=F_SMALL, color=MUTED)
# three class bars under the block
ab = ax_in(bx + 0.40, IMY + 0.02, bw - 0.44, 0.58)
for i, (k, c) in enumerate((("real", REAL), ("fake", FAKE), ("filter", FILT))):
    on = prob[k] >= 0.5
    ab.barh(2 - i, max(prob[k], 0.015), color=c if on else GRID, height=0.62, lw=0)
    ab.text(-0.05, 2 - i, L(CLS_ZH[k], CLS_EN[k]), ha="right", va="center", fontsize=F_SMALL, color=INK)
    ab.text(prob[k] + 0.04, 2 - i, f"{prob[k]:.2f}", ha="left", va="center", fontsize=F_SMALL, color=INK if on else MUTED)
ab.set_xlim(0, 1.3); ab.set_ylim(-0.6, 2.6); ab.axis("off")
caption(bx, IMY - 0.08, L("三類分數（softmax）\n判定＝最大者", "class scores (softmax)\ndecision = the largest"))
# the evidence map on the face
a2x = E2 - IMW - 0.02
a2 = ax_in(a2x, IMY, IMW, IMH); show(a2, img)
a2.imshow(e_up, cmap="magma", alpha=np.clip(e_up, 0, 1) * 0.85, vmin=0, vmax=1, interpolation="bilinear")
a2.contour(e_up, levels=[0.5], colors="white", linewidths=0.6)
caption(a2x, IMY - 0.08, L("證據頭：16×16 圖，雙線性放大\n亮＝證據強，白線＝0.5", "evidence head: 16×16 map,\nupsampled; bright = strong\nevidence, white line = 0.5"))
chevron((E2 + C3) / 2, YMID)

# ---- stage 3: part naming (code) ----
stage(C3, E3, 3, L("部位對應（程式）", "Part naming (code)"), CODE)
a3 = ax_in(C3 + 0.10, IMY, IMW, IMH); show(a3, img)
for k in ("eyes", "nose", "mouth", "skin", "contour"):
    cs, _ = cv2.findContours(M[k].astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cs:
        c = c[:, 0, :]
        if len(c) < 3:
            continue
        a3.plot(np.r_[c[:, 0], c[0, 0]], np.r_[c[:, 1], c[0, 1]], color="#ffd166" if k == named else "white", lw=1.5 if k == named else 0.45,
                alpha=1 if k == named else 0.6)
caption(C3 + 0.10, IMY - 0.08, L("五個部位遮罩由特徵點算出\n證據平均最高者點名：嘴巴 0.98\n（鼻 0.42、皮膚 0.27、\n眼 0.01、輪廓 0.04）",
                                 "five part masks from landmarks\nhighest mean evidence is named:\nmouth 0.98 (nose 0.42, skin 0.27,\neyes 0.01, contour 0.04)"))
chevron((E3 + C4) / 2, YMID)

# ---- stage 4: record -> sentences -> checks ----
stage(C4, E4, 4, L("程式寫句與查核", "Sentences, checks (code)"), CHECK)
cx, cw = C4 + 0.02, E4 - C4 - 0.02; cy = 0.78; ch = IMY + IMH - cy
bg.add_patch(FancyBboxPatch((cx, cy), cw, ch, boxstyle="round,pad=0,rounding_size=0.05", fc="white", ec=GRID, lw=0.8))
tx = cx + 0.07; ty = cy + ch - 0.07
bg.text(tx, ty, L("紀錄", "record"), ha="left", va="top", fontsize=F_SMALL, color=CODE, fontweight="bold"); ty -= 0.12
recl = [f"decision  {dec}", f"p         {prob['real']:.2f} / {prob['fake']:.2f} / {prob['filter']:.2f}",
        f"evidence  eyes {parts['eyes']:.2f}  nose {parts['nose']:.2f}", f"          mouth {parts['mouth']:.2f}  skin {parts['skin']:.2f}", f"named     {named}"]
for t in recl:
    bg.text(tx, ty, t, ha="left", va="top", fontsize=F_MONO, color=INK, family=MONO); ty -= 0.095
ty -= 0.03; bg.plot([tx, cx + cw - 0.07], [ty, ty], color=GRID, lw=0.6); ty -= 0.06
bg.text(tx, ty, L("句子：固定模板，數字從紀錄複製", "sentences from templates"), ha="left", va="top", fontsize=F_SMALL, color=CODE, fontweight="bold"); ty -= 0.12
for s in (S1, S2, S3):
    lines = textwrap.wrap(s, 22 if ZH else 33)
    bg.text(tx, ty, "✓", ha="left", va="top", fontsize=6, color=CHECK, fontweight="bold", family="DejaVu Sans")
    bg.text(tx + 0.11, ty, "\n".join(lines), ha="left", va="top", fontsize=F_SMALL, color=INK, linespacing=1.2)
    ty -= 0.085 * len(lines) + 0.045
ty -= 0.02; bg.plot([tx, cx + cw - 0.07], [ty, ty], color=GRID, lw=0.6); ty -= 0.06
bg.text(tx, ty, L("查核 H1–H6：分數對門檻・事實齊全\n不宣稱確定・分數不掛在部位上", "checks H1–H6: score vs threshold,\nall facts present, no certainty claim,\nno score attached to a part"),
        ha="left", va="top", fontsize=F_SMALL, color=CHECK, linespacing=1.25)
caption(cx, cy - 0.07, L(f"驗證：嘴巴從原圖還原 → 偽造分數 {rt['p_label_before']:.2f} → {rt['p_label_after_named_restored']:.2f}",
                         f"validation: mouth restored from the\noriginal, forgery score {rt['p_label_before']:.2f} → {rt['p_label_after_named_restored']:.2f}"))

# ---- legend and the example line (bottom) ----
lx = C1 + 0.10; ly = 0.27
for col, lab in ((MODEL, L("神經網路", "neural network")), (CODE, L("程式（固定規則）", "code (fixed rules)")), (CHECK, L("查核", "checks"))):
    bg.add_patch(Rectangle((lx, ly - 0.03), 0.14, 0.06, color=col, lw=0)); bg.text(lx + 0.18, ly, lab, ha="left", va="center", fontsize=F_SMALL, color=MUTED)
    lx += 0.18 + (0.09 if ZH else 0.045) * len(lab) + 0.16
bg.text(C1 + 0.10, 0.10, L("範例：FF++ 測試影格 454（真實）嘴巴換成另一個人的；部位級偽造測試集，模型未在此影格上訓練。",
                           "example: FF++ test frame 454 (genuine) with the mouth replaced from a donor; part-level forgery test set, not seen in training."),
        ha="left", va="center", fontsize=F_SMALL, color=MUTED)

stem = OUT / ("pipeline" if ZH else "pipeline_en")
fig.savefig(stem.with_suffix(".pdf")); fig.savefig(stem.with_suffix(".png"), dpi=300); fig.savefig(stem.with_suffix(".svg"))
print("wrote", stem.with_suffix(".png"), "named", named, "restoration", rt["p_label_before"], "->", rt["p_label_after_named_restored"])
