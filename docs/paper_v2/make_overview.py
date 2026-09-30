"""fig_overview: system overview drawn as a left-to-right pipeline. Input data (an FF++ frame with its on-the-fly filter
and self-blend; a Tencent original/render pair) -> render decomposition (flow f -> eye / contour, residual P -> tone /
texture, real components shown as |component - original| with their footprint M) -> training pool -> backbone with the
three heads and their losses -> two real outputs of the paper's main model (CLIP ViT-L/14 + LoRA, evidence head,
clipe4_s20260929): a held-out donor-nose part edit and an unseen Alibaba eye-enlargement render, each with its evidence map.

python docs/paper_v2/make_overview.py
"""
import json
import sys
from pathlib import Path

import cv2
import matplotlib
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

B = Path(r"C:\My_Project\AIGC"); RU = B / "results/research/retouch_unified_20260929"; CGD = B / "results/research/cgd_20260927"
sys.path.insert(0, str(B / "docs/paper_v2")); sys.path.insert(0, str(RU))
import make_figures as MF  # noqa: E402
import make_pipeline as MP  # noqa: E402
import decompose as D  # noqa: E402

GREEN, AMBER, RED, BLUE = "#2f7d32", "#8a6d00", MF.C_SBI, MF.C_OURS
DATA_FC, DATA_EC, MODEL_FC = "#f2f2f2", "#9a9a9a", "#e7eef8"
TW, TH = 1.2, 1.44          # thumbnail size in axis units (1 unit = 0.25 in; axes 28.4 x 11.6 on 7.1 x 2.9 in)
FS = 6.0                    # base font size


def box(ax, x, y, w, h, fc, ec, lw=0.9, r=0.12, z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, zorder=z))


def txt(ax, x, y, s, fs=FS, c=None, ha="center", va="center", bold=False, it=False, z=6):
    ax.text(x, y, s, ha=ha, va=va, fontsize=fs, color=c or MF.INK, fontweight="bold" if bold else "normal",
            style="italic" if it else "normal", linespacing=1.2, zorder=z)


def arrow(ax, a, b, c=MF.MUTED, lw=0.8, rad=0.0, z=5):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=6, color=c, lw=lw, shrinkA=1.5, shrinkB=1.5,
                                 connectionstyle=f"arc3,rad={rad}", zorder=z))


def img(ax, im, x, y, w=TW, h=TH, ec=None, lw=1.1):
    ax.imshow(im, extent=(x, x + w, y, y + h), zorder=3, aspect="auto", interpolation="bilinear")
    if ec:
        ax.add_patch(plt.Rectangle((x, y), w, h, fill=False, ec=ec, lw=lw, zorder=4))


def heat(im, m, alpha=0.5):
    hm = cv2.applyColorMap((np.clip(m, 0, 1) * 255).astype(np.uint8), cv2.COLORMAP_JET)[..., ::-1]
    return ((1 - alpha) * im + alpha * hm).astype(np.uint8)


def mask_icon(m):
    """binary footprint -> small RGB tile, filled in the accent blue"""
    rgb = np.full(m.shape + (3,), 235, np.uint8); rgb[m > 0] = (15, 77, 146); return rgb


def vendor_thumbs():
    stem = "60002"
    row = [l.split("\t") for l in (RU / "pairs_tencent.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.split("\t")[0].endswith(f"{stem}.png")][0]
    O, R, comp, _ = D.decompose(row[0], row[1], stem)
    b = [int(v / 2) for v in json.loads((RU / "ffhq_boxes.json").read_text())[stem]]
    crop = lambda im: np.ascontiguousarray(im[b[1]:b[3], b[0]:b[2]])
    c = lambda im: cv2.resize(crop(im), (100, 120))
    diff = lambda im: np.abs(crop(im).astype(np.float32) - crop(O).astype(np.float32))
    d = lambda im: cv2.resize(np.clip(diff(im).mean(2) * 5, 0, 255).astype(np.uint8), (100, 120))
    k = np.ones((9, 9), np.uint8)
    fp = lambda im: cv2.resize(cv2.dilate((diff(im).max(2) > 6).astype(np.uint8), k), (50, 60), interpolation=cv2.INTER_AREA)
    return {"O": c(O), "R": c(R), **{"d_" + k_: cv2.applyColorMap(d(v), cv2.COLORMAP_MAGMA)[..., ::-1] for k_, v in comp.items()},
            **{"m_" + k_: mask_icon(fp(v)) for k_, v in comp.items()}}


def clip_model():
    """The paper's main model: RU CLIP ViT-L/14 + LoRA with evidence head (clipe4, seed 20260929)."""
    import torch
    sys.path.insert(0, str(RU))
    from train_ru_clip import load_clip
    from train_ru3 import CLIP_MEAN, CLIP_STD
    m = load_clip("clipe4_s20260929", head=True).cuda().eval()
    mu, sd = torch.tensor(CLIP_MEAN).view(1, 3, 1, 1).cuda(), torch.tensor(CLIP_STD).view(1, 3, 1, 1).cuda()

    def run(x01):   # x01: 1x3xHxW in [0, 1] -> (p_cls[3], p_pres[4], ev 16x16 in [0, 1])
        x = torch.nn.functional.interpolate(x01.cuda(), size=(224, 224), mode="bilinear", align_corners=False)
        with torch.no_grad():
            lo, pr, _, ev = m((x - mu) / sd)
        return torch.softmax(lo, 1)[0].cpu().numpy(), torch.sigmoid(pr)[0].cpu().numpy(), torch.sigmoid(ev[0, 0]).float().cpu().numpy()
    return run


def to01(rgb, size):
    import torch
    from PIL import Image
    im = Image.fromarray(rgb).resize((size, size), Image.BILINEAR)
    return torch.from_numpy(np.asarray(im, np.float32) / 255.0).permute(2, 0, 1)[None]


def evidence_overlay(base, ev):
    S = (base.shape[1], base.shape[0])
    return heat(base, cv2.resize(ev, S, interpolation=cv2.INTER_LINEAR))


def fake_example(run):
    """Held-out donor-nose part edit (item 0 of fig_evidence_items.json), prepared as the RUCLIPE4 arm of
    eval_cgd_explain.py: whole part-edit image at 380 px, then 224 px + CLIP normalisation inside the model wrapper."""
    it = json.loads((MF.OUT / "fig_evidence_items.json").read_text())[0]
    rgb = cv2.imread(it["x"])[..., ::-1].copy()
    p, pr, ev = run(to01(rgb, 380))
    base = cv2.resize(rgb, (100, 120))
    return base, evidence_overlay(base, ev), p, pr, it["part"]


def filter_example(run):
    """Alibaba EyeEnlarging_90 render of FFHQ 17024, cropped with ffhq_boxes.json as eval_ru.eval_ali does (224 px, CLIP)."""
    J = [j for j in json.loads((RU / "explain_ru_ru2_effb4_s20260929.json").read_text()) if j["alibaba_group"] == "EyeEnlarging_90"][0]
    b = json.loads((RU / "ffhq_boxes.json").read_text())["17024"]
    rgb = np.ascontiguousarray(cv2.imread(J["image"])[..., ::-1][b[1]:b[3], b[0]:b[2]])
    p, pr, ev = run(to01(rgb, 224))
    base = cv2.resize(rgb, (100, 120))
    return base, evidence_overlay(base, ev), p, pr


def main():
    t = MP.thumbs(); v = vendor_thumbs(); run = clip_model()
    fk_in, fk_ev, fk_p, fk_pr, fk_part = fake_example(run); fl_in, fl_ev, fl_p, fl_pr = filter_example(run)
    fig, ax = plt.subplots(figsize=(7.1, 2.9)); ax.set_xlim(0, 28.4); ax.set_ylim(0, 11.6); ax.axis("off")
    for x, s in ((2.4, "Input data"), (8.25, "Render decomposition"), (13.95, "Training pool"), (19.7, "Model"), (25.8, "Output")):
        txt(ax, x, 11.15, s, fs=7.0, bold=True)
    # ------------------------------------------------------------------ (1) input data
    y1 = 8.7
    txt(ax, 2.4, y1 + TH + 0.3, "FF++ frame, on the fly", fs=5.2, c=MF.MUTED)
    for k, (key, cap, col) in enumerate([("real", "real", GREEN), ("beaut", "filter", AMBER), ("sb", "fake", RED)]):
        x = 0.3 + k * 1.45; img(ax, t[key], x, y1, ec=col); txt(ax, x + TW / 2, y1 - 0.3, cap, fs=5.6, c=col, bold=True)
    y2 = 3.6
    txt(ax, 2.4, y2 + TH + 0.3, "Tencent render pair", fs=5.2, c=MF.MUTED)
    img(ax, v["O"], 0.5, y2, ec=GREEN); txt(ax, 0.5 + TW / 2, y2 - 0.3, "original (O)", fs=5.2)
    img(ax, v["R"], 2.9, y2, ec=AMBER); txt(ax, 2.9 + TW / 2, y2 - 0.3, "render (R)", fs=5.2)
    # ------------------------------------------------------------------ (2) render decomposition
    rows = [("eye", "eye", 7.3), ("jaw", "contour", 5.3), ("white", "tone", 3.3), ("smooth", "texture", 1.3)]   # row centres
    xt = 8.85                                   # component thumbnails
    box(ax, 5.15, 0.35, 6.4, 8.7, DATA_FC, DATA_EC, r=0.2, z=1)
    xn, yn = 5.85, 5.75                          # (O, R) node
    arrow(ax, (4.2, y2 + TH / 2), (xn - 0.5, yn - 0.1), rad=-0.15)
    box(ax, xn - 0.5, yn - 0.38, 1.0, 0.76, "white", DATA_EC); txt(ax, xn, yn, "(O, R)", fs=5.6)
    nx0, nx1 = 6.5, 8.15                        # flow / residual nodes
    for yc, lab in ((8.0, "flow $f$"), (3.7, "residual $P$")):
        box(ax, nx0, yc - 0.38, nx1 - nx0, 0.76, "white", DATA_EC); txt(ax, (nx0 + nx1) / 2, yc, lab, fs=5.6)
        arrow(ax, (xn + 0.5, yn + (0.25 if yc > yn else -0.25)), (nx0, yc))
    txt(ax, (nx0 + nx1) / 2 - 0.15, 8.8, r"$O(x{+}f)\approx R$", fs=4.8, c=MF.MUTED)
    txt(ax, (nx0 + nx1) / 2 - 0.4, 2.6, "$P = R - O(x{+}f)$", fs=4.8, c=MF.MUTED)
    for ya, yb, lab, (lx, ly, ha) in [(8.0, 7.3, "eyes", (8.8, 8.3, "right")), (8.0, 5.3, "rest", (8.45, 6.15, "right")),
                                       (3.7, 3.3, "low-pass", (8.8, 3.05, "right")), (3.7, 1.3, "high-pass", (8.45, 2.1, "right"))]:
        arrow(ax, (nx1, ya), (xt, yb)); txt(ax, lx, ly, lab, fs=4.8, c=MF.MUTED, ha=ha)
    for key, cap, yc in rows:
        img(ax, v["d_" + key], xt, yc - TH / 2, ec=AMBER, lw=0.9)
        txt(ax, xt + TW + 0.12, yc + 0.42, cap, fs=5.4, ha="left", bold=True, c=AMBER)
        img(ax, v["m_" + key], xt + TW + 0.12, yc - 0.68, w=0.6, h=0.72, ec=DATA_EC, lw=0.6)
        txt(ax, xt + TW + 0.8, yc - 0.32, "$M$", fs=5.2, ha="left", c=MF.MUTED)
    # ------------------------------------------------------------------ (3) training pool
    px, py, pw, ph = 12.0, 2.3, 3.9, 7.6
    box(ax, px, py, pw, ph, DATA_FC, DATA_EC, r=0.35, z=1)
    ys = [9.15, 7.45, 5.75, 4.05]
    arrow(ax, (4.75, y1 + TH / 2), (px, ys[0]))                                # FF++ triplet -> pool (above the block)
    arrow(ax, (11.6, 4.9), (px, ys[2] - 0.25))                                        # components -> pool
    items = [("FF++ triplets", "tri"), ("vendor renders", "pair"), ("single operations", "four"), ("part-level edits", "part")]
    for yc, (lab, ic) in zip(ys, items):
        xi = px + 0.3
        if ic == "tri":
            for j, c in enumerate((GREEN, AMBER, RED)):
                ax.add_patch(plt.Rectangle((xi + j * 0.26, yc - 0.2), 0.22, 0.4, fc=c, ec="none", zorder=3))
        elif ic == "pair":
            ax.add_patch(plt.Rectangle((xi, yc - 0.2), 0.3, 0.4, fc="white", ec=GREEN, lw=0.8, zorder=3))
            ax.add_patch(plt.Rectangle((xi + 0.42, yc - 0.2), 0.3, 0.4, fc="white", ec=AMBER, lw=0.8, zorder=3))
        elif ic == "four":
            for j in range(4):
                ax.add_patch(plt.Rectangle((xi + j * 0.2, yc - 0.2), 0.16, 0.4, fc="white", ec=AMBER, lw=0.7, zorder=3))
        else:
            ax.add_patch(plt.Rectangle((xi, yc - 0.2), 0.3, 0.4, fc="white", ec=RED, lw=0.8, zorder=3))
            ax.add_patch(plt.Rectangle((xi + 0.06, yc - 0.06), 0.14, 0.14, fc=BLUE, ec="none", zorder=4))
        txt(ax, px + 1.25, yc, lab, fs=5.6, ha="left")
    ax.plot([px + 0.3, px + pw - 0.3], [3.35, 3.35], color=DATA_EC, lw=0.6, zorder=2)
    txt(ax, px + pw / 2, 2.85, "exact footprint $M$", fs=5.0, c=MF.MUTED)
    # ------------------------------------------------------------------ (4) model
    bx, by, bw, bh = 16.55, 4.1, 2.6, 3.4
    arrow(ax, (px + pw, py + ph / 2), (bx, by + bh / 2), c=BLUE)
    box(ax, bx, by, bw, bh, MODEL_FC, BLUE, lw=1.0)
    txt(ax, bx + bw / 2, by + bh / 2, "backbone\nEffNet-B4 or\nCLIP ViT-L/14\n+ LoRA", fs=5.6, c=BLUE)
    hx, hw = 19.8, 3.2
    heads = [(8.55, 1.45, "three-way head", r"$\mathcal{L}_\mathrm{cls}$  CE"),
             (5.8, 1.7, "presence head\neye · contour\ntone · texture", r"$\mathcal{L}_\mathrm{pres}$  BCE"),
             (3.0, 1.45, "evidence head\n16 $\\times$ 16 map", r"$\mathcal{L}_\mathrm{ev}$  BCE + Dice vs $M$")]
    for yc, hh, lab, loss in heads:
        box(ax, hx, yc - hh / 2, hw, hh, "white", BLUE, lw=1.0)
        arrow(ax, (bx + bw, by + bh / 2), (hx, yc), c=BLUE)
        if lab.startswith("three"):
            txt(ax, hx + hw / 2, yc + 0.3, lab, fs=5.6)
            for dx, s, c in ((-1.0, "real", GREEN), (0.0, "fake", RED), (1.0, "filter", AMBER)):
                txt(ax, hx + hw / 2 + dx, yc - 0.3, s, fs=5.4, c=c, bold=True)
        else:
            txt(ax, hx + hw / 2, yc, lab, fs=5.6)
        txt(ax, hx + hw / 2, yc - hh / 2 - 0.42, loss, fs=5.2, c=BLUE)
    # ------------------------------------------------------------------ (5) output (one model: CLIP ViT-L/14 + LoRA, evidence head)
    ox, ew, eh = 24.2, 1.5, 1.8
    arrow(ax, (hx + hw, 5.8), (ox - 0.35, 5.8), c=BLUE)
    CLS = ["real", "fake", "filter"]; CCOL = {"real": GREEN, "fake": RED, "filter": AMBER}; OPS = ["eye", "contour", "tone", "texture"]
    for (yc, base, ev, p, pr, line2) in ((7.15, fk_in, fk_ev, fk_p, fk_pr, f"evidence: {fk_part}"),
                                          (2.35, fl_in, fl_ev, fl_p, fl_pr, "eyes enlarged")):
        cls = CLS[int(p.argmax())]; col = CCOL[cls]
        img(ax, base, ox, yc, w=ew, h=eh, ec=col); img(ax, ev, ox + ew + 0.3, yc, w=ew, h=eh, ec=col)
        txt(ax, ox + ew / 2, yc + eh + 0.25, "input", fs=5.0, c=MF.MUTED); txt(ax, ox + ew * 1.5 + 0.3, yc + eh + 0.25, "evidence map", fs=5.0, c=MF.MUTED)
        xc = ox + ew + 0.15
        txt(ax, xc, yc - 0.35, f"{cls} {p.max():.2f}", fs=6.0, c=col, bold=True)
        txt(ax, xc, yc - 0.8, line2, fs=5.4)
        txt(ax, xc, yc - 1.25, "  ".join(f"{o} {v:.2f}" for o, v in zip(OPS[:2], pr[:2])), fs=4.8, c=MF.MUTED)
        txt(ax, xc, yc - 1.65, "  ".join(f"{o} {v:.2f}" for o, v in zip(OPS[2:], pr[2:])), fs=4.8, c=MF.MUTED)
    MF.save(fig, "fig_overview")
    print("fake example  : p(real,fake,filter) =", np.round(fk_p, 3), "presence(eye,contour,tone,texture) =", np.round(fk_pr, 3))
    print("filter example: p(real,fake,filter) =", np.round(fl_p, 3), "presence(eye,contour,tone,texture) =", np.round(fl_pr, 3))


if __name__ == "__main__":
    main(); print("overview ok")
