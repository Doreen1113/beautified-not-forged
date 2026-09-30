"""README media for the GitHub front page. Every frame is computed by the main model (clipe4: CLIP ViT-L/14 + LoRA).

  assets/readme/demo_system.gif        input -> evidence map -> decision and sentence, for the examples of explain_ours.py
  assets/readme/demo_counterfactual.gif part-level forgery -> named region -> region restored to the original -> new decision
  assets/readme/{teaser,overview,frontier,escape,evidence,flip}.png   paper / slide figures resized for the web

Counterfactual examples are fixed in advance: the paper's donor-nose item and the first SD "eyes" and SDXL "mouth" items
of the held-out test manifests. Restored region = the |M| highest-evidence pixels (M = true edit footprint), dilated by the
feather width, as in the paper's faithfulness test. Whatever the model decides after restoring is shown.

python docs/readme/make_media.py
"""
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image, ImageDraw, ImageFont

B = Path(r"C:\My_Project\AIGC"); RU = B / "results/research/retouch_unified_20260929"
OUT = B / "assets/readme"; OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(RU)); sys.path.insert(0, str(B / "docs/paper_v2")); sys.path.insert(0, str(B))
from explain_ours import EXAMPLES, explain  # noqa: E402
from train_ru3 import to_t2  # noqa: E402
from train_ru_clip import load_clip  # noqa: E402

CLS = ["real", "fake", "filter"]
COL = {"real": (47, 125, 50), "fake": (182, 67, 66), "filter": (138, 109, 0)}
INK, MUTED, BG = (31, 42, 55), (95, 103, 115), (255, 255, 255)
FONT = "C:/Windows/Fonts/arial.ttf"; FONTB = "C:/Windows/Fonts/arialbd.ttf"


def font(sz, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, sz)


def overlay(rgb, heat, alpha=0.45):
    hm = cv2.applyColorMap((np.clip(heat, 0, 1) * 255).astype(np.uint8), cv2.COLORMAP_JET)[..., ::-1]
    return (rgb * (1 - alpha) + hm * alpha).astype(np.uint8)


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            lines.append(cur); cur = w
    return lines + [cur]


def panel(img, title, label=None, prob=None, lines=(), sentence=None, S=300, W=660, H=360):
    """One GIF frame: image on the left, text on the right."""
    c = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(c)
    h, w = img.shape[:2]; sc = S / max(h, w); nw, nh = int(round(w * sc)), int(round(h * sc))   # keep aspect ratio
    c.paste(Image.fromarray(cv2.resize(img, (nw, nh))), (24 + (S - nw) // 2, 36 + (S - nh) // 2))
    d.text((24, 8), title, font=font(17, True), fill=INK)
    x = S + 48; y = 60
    if label:
        d.text((x, y), f"{label}", font=font(34, True), fill=COL[label]); d.text((x + d.textlength(label, font=font(34, True)) + 12, y + 12),
                                                                              f"p = {prob:.2f}", font=font(18), fill=MUTED)
        y += 60
    for l in lines:
        d.text((x, y), l, font=font(16), fill=MUTED); y += 24
    if sentence:
        y += 14
        for l in wrap(d, f"\u201c{sentence}\u201d", font(18, True), W - x - 20):
            d.text((x, y), l, font=font(18, True), fill=INK); y += 26
    return c


def save_gif(frames, durations, name):
    frames[0].save(OUT / name, save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
    print("->", OUT / name, f"{(OUT / name).stat().st_size / 1e6:.1f} MB")


def demo_system(net):
    frames, dur = [], []
    for name, path, box, truth in EXAMPLES:
        o, arr, up = explain(net, path, box)
        frames.append(panel(arr, name)); dur.append(700)
        ops = o["operations"]
        lines = [f"eye {ops['eye']:.2f}   contour {ops['contour']:.2f}", f"tone {ops['tone']:.2f}   texture {ops['texture']:.2f}"]
        if o["label"] != truth:
            lines.append(f"(wrong: this image is {truth})")
        img = overlay(arr, up) if o["label"] != "real" else arr
        frames.append(panel(img, name, o["label"], o["probabilities"][o["label"]], lines, o["explanation"])); dur.append(2600)
    save_gif(frames, dur, "demo_system.gif")


def predict(net, arr):
    x = to_t2(arr, 224, False, "clip")[None].cuda()
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        lo, _pr, _q, ev = net(x)
    return torch.softmax(lo.float(), 1)[0].cpu().numpy(), torch.sigmoid(ev.float())[0, 0]


def counterfactual_items():
    items = []
    for mech, part in (("donor", "nose"), ("sd", "eyes"), ("sdxl", "mouth")):
        rows = [l.split("\t") for l in (B / f"results/research/partedit_20260927/manifest_test_{mech}.tsv").read_text(encoding="utf-8").splitlines()[1:]]
        if mech == "donor":
            r = next(r for r in rows if "682__f0867__nose" in r[0])
        else:
            r = next(r for r in rows if r[6] == part)
        items.append((mech, part, Path(r[0]), Path(r[4]), Path(r[5])))
    return items


def demo_counterfactual(net):
    frames, dur = [], []
    for mech, part, pth, mpath, opath in counterfactual_items():
        x = np.array(Image.open(pth).convert("RGB")); x0 = np.array(Image.open(opath).convert("RGB").resize(x.shape[1::-1]))
        z = np.load(mpath); M = z[z.files[0]].astype(bool)
        if M.shape != x.shape[:2]:
            M = cv2.resize(M.astype(np.uint8), x.shape[1::-1], interpolation=cv2.INTER_NEAREST).astype(bool)
        p, e = predict(net, x)
        sentence = explain(net, pth, None)[0]["explanation"]   # the model's own sentence (rule B part naming)
        up = F.interpolate(e[None, None], size=x.shape[:2], mode="bilinear", align_corners=False)[0, 0].cpu().numpy()
        k = max(1, int(M.sum())); thr = np.sort(up.ravel())[-k]
        A = cv2.dilate((up >= thr).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))).astype(bool)
        xr = np.where(A[..., None], x0, x)
        pr, _ = predict(net, xr)
        lab, labr = CLS[int(p.argmax())], CLS[int(pr.argmax())]
        title = f"{'donor transplant' if mech == 'donor' else mech.upper() + ' inpainting'}: edited {part}"
        frames.append(panel(x, title, lab, p.max(), ["input"])); dur.append(1200)
        frames.append(panel(overlay(x, up), title, lab, p.max(), ["evidence map"], sentence)); dur.append(1800)
        cont = x.copy(); cnts, _ = cv2.findContours(A.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(cont, cnts, -1, (255, 255, 255), 3)
        frames.append(panel(cont, title, lab, p.max(), ["region to restore", "(pixels from the unedited original)"])); dur.append(1400)
        for t in (0.33, 0.66):
            frames.append(panel((x * (1 - t) + xr * t).astype(np.uint8), title, None, None, ["restoring ..."])); dur.append(250)
        frames.append(panel(xr, title, labr, pr.max(), ["after restoring the named region"],
                            "Decision removed." if labr != "fake" else "Decision kept (restoration did not flip it).")); dur.append(2600)
        print(mech, part, lab, round(float(p.max()), 3), "->", labr, round(float(pr.max()), 3))
    save_gif(frames, dur, "demo_counterfactual.gif")


def stills():
    import fitz
    for src, dst, w in (("docs/paper_v2/figs/fig_teaser.pdf", "teaser.png", 1600), ("docs/paper_v2/figs/fig_overview.pdf", "overview.png", 1600),
                        ("docs/paper_v2/figs/fig_frontier.pdf", "frontier.png", 1400), ("docs/paper_v2/figs/fig_evidence.pdf", "evidence.png", 1400)):
        pix = fitz.open(B / src)[0].get_pixmap(dpi=300); im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        im.thumbnail((w, 10000), Image.LANCZOS); im.save(OUT / dst, optimize=True)
    for src, dst in (("docs/meeting_20260930/assets/escape_split.png", "escape.png"), ("docs/meeting_20260930/assets/flip_bars.png", "flip.png"),
                     ("docs/meeting_20260930/assets/blur_bars.png", "blur.png"), ("docs/meeting_20260930/assets/system_output.png", "system_output.png")):
        im = Image.open(B / src).convert("RGB"); im.thumbnail((1400, 10000), Image.LANCZOS); im.save(OUT / dst, optimize=True)
    print("stills ->", OUT)


if __name__ == "__main__":
    stills()
    net = load_clip("clipe4_s20260929", head=True).cuda().eval()
    demo_system(net); demo_counterfactual(net)
