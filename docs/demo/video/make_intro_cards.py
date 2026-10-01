"""Still cards of the introduction video (1280 x 720), drawn from the paper / slide figures. Every number is the one in the
paper or in docs/meeting_20260930/assets/asset_numbers.json.

python docs/demo/video/make_intro_cards.py -> docs/demo/video/cards/NN_name.png + cards.json (card durations)
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

B = Path(r"C:\My_Project\AIGC"); A = B / "docs/meeting_20260930/assets"; R = B / "assets/readme"
OUT = Path(__file__).resolve().parent / "cards"; OUT.mkdir(exist_ok=True)
W, H = 1280, 720
INK, MUTED, BLUE, RED, GREEN, BG, BAR = (29, 31, 36), (98, 102, 111), (15, 77, 146), (179, 52, 43), (47, 125, 79), (255, 255, 255), (22, 27, 36)
F = "C:/Windows/Fonts/"


def font(name, size):
    return ImageFont.truetype(F + name, size)


SERIF_B, SERIF, SANS, SANS_B = "cambriab.ttf", "cambria.ttc", "calibri.ttf", "calibrib.ttf"


def wrap(d, text, fnt, width):
    out, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= width:
            cur = t
        else:
            out.append(cur); cur = w
    return out + [cur]


def fit(img, w, h):
    r = min(w / img.width, h / img.height); return img.resize((int(img.width * r), int(img.height * r)), Image.LANCZOS)


def card(name, tag, title, fig=None, caption=None, secs=7.0, figbox=(60, 150, 1160, 470)):
    c = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(c)
    for x, y in ((W - 34, 22), (22, H - 34), (W - 34, H - 34)):
        d.rectangle([x, y, x + 10, y + 10], fill=INK)
    if tag:
        d.text((60, 40), f"[{tag}]", font=font(SERIF_B, 22), fill=BLUE)
    y = 72
    for l in wrap(d, title, font(SERIF_B, 38), W - 120):
        d.text((60, y), l, font=font(SERIF_B, 38), fill=INK); y += 48
    if fig:
        im = fit(Image.open(fig).convert("RGB"), figbox[2], figbox[3] - max(0, y - 130))
        c.paste(im, (figbox[0] + (figbox[2] - im.width) // 2, max(figbox[1], y + 14)))
    if caption:
        d.rectangle([0, H - 96, W, H], fill=BAR)
        yy = H - 84
        for l in wrap(d, caption, font(SANS, 25), W - 120)[:2]:
            d.text((60, yy), l, font=font(SANS, 25), fill=(240, 240, 240)); yy += 32
    c.save(OUT / f"{name}.png"); return {"file": f"cards/{name}.png", "secs": secs}


def title_card():
    c = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(c)
    d.rounded_rectangle([-200, 150, 900, 560], radius=205, fill=(239, 239, 239))
    d.rectangle([860, 138, 870, 148], fill=INK); d.rectangle([40, 600, 50, 610], fill=INK)
    d.text((90, 225), "Beautified Is Not Forged", font=font(SERIF_B, 56), fill=INK)
    d.text((90, 305), "Separating Beautification from Face Forgery", font=font(SERIF, 32), fill=MUTED)
    d.text((90, 400), "Qin-Ying Lin, Bo-Rong Chen, Chen-Shan Yu", font=font(SANS, 26), fill=INK)
    d.text((90, 445), "system introduction and live demo", font=font(SANS, 22), fill=MUTED)
    c.save(OUT / "00_title.png"); return {"file": "cards/00_title.png", "secs": 4.5}


def text_card(name, tag, title, lines, secs):
    c = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(c)
    for x, y in ((W - 34, 22), (22, H - 34), (W - 34, H - 34)):
        d.rectangle([x, y, x + 10, y + 10], fill=INK)
    d.text((60, 40), f"[{tag}]", font=font(SERIF_B, 22), fill=BLUE)
    d.text((60, 72), title, font=font(SERIF_B, 38), fill=INK)
    y = 170
    for head, body, col in lines:
        d.ellipse([62, y + 9, 78, y + 25], fill=col)
        d.text((100, y), head, font=font(SANS_B, 28), fill=INK); y += 38
        for l in wrap(d, body, font(SANS, 24), W - 200):
            d.text((100, y), l, font=font(SANS, 24), fill=MUTED); y += 31
        y += 18
    c.save(OUT / f"{name}.png"); return {"file": f"cards/{name}.png", "secs": secs}


def transition_card():
    c = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(c)
    for x, y in ((W - 34, 22), (22, H - 34), (W - 34, H - 34)):
        d.rectangle([x, y, x + 10, y + 10], fill=INK)
    t = "Live demo"; f = font(SERIF_B, 64); d.text(((W - d.textlength(t, font=f)) / 2, 270), t, font=f, fill=INK)
    for i, l in enumerate(["Ours-lite (17.6 M parameters), the browser-sized version of the model,",
                           "runs entirely on the device: nothing is uploaded."]):
        f2 = font(SANS, 28); d.text(((W - d.textlength(l, font=f2)) / 2, 370 + 40 * i), l, font=f2, fill=MUTED)
    c.save(OUT / "05_demo.png"); return {"file": "cards/05_demo.png", "secs": 3.5}


def end_card():
    c = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(c)
    d.rounded_rectangle([-200, 380, 820, 680], radius=150, fill=(239, 239, 239))
    d.text((60, 90), "Try it", font=font(SERIF_B, 44), fill=INK)
    d.text((60, 160), "doreen1113.github.io/beautified-not-forged/docs/demo", font=font(SANS_B, 30), fill=BLUE)
    d.text((60, 215), "Code, paper draft and slides", font=font(SERIF_B, 30), fill=INK)
    d.text((60, 260), "github.com/Doreen1113/beautified-not-forged", font=font(SANS_B, 28), fill=BLUE)
    d.text((110, 490), "Thank you", font=font(SANS_B, 52), fill=INK)
    c.save(OUT / "99_end.png"); return {"file": "cards/99_end.png", "secs": 5.0}


def main():
    seq = [title_card(),
           card("01_problem", "Problem", "A real / fake detector must accuse beautified faces or let beautified deepfakes through",
                R / "teaser.png", "Beautified genuine face: SBI says fake (false accusation). Beautified deepfake: SBI says real (escape). "
                "Our model says filter and fake.", 8.5),
           card("02_escape", "Problem", "Beautification alone lets deepfakes escape, even 2025 CLIP detectors",
                A / "escape_split.png", "Celeb-DF-B, re-encoding effect removed: SBI +21.8 pp, Forensics Adapter +15.3, Effort +11.0. "
                "Ours: -0.6 pp.", 7.5),
           card("03_method", "Method", "One model, three heads, trained on images paired with their originals",
                R / "overview.png", "A third label, filter (identity kept). Every edited training image has its original, "
                "so the label and the exact edited region are known.", 8.5),
           card("04_decomp", "Method", "Commercial retouching renders, split into single operations",
                A / "fig_decomp.png", "Optical flow gives eye and contour edits; the colour residual gives tone and texture. "
                "About 50 k single-operation training images from two services.", 8.0),
           transition_card(),
           card("06_results", "Results", "Detection level with 2025 CLIP detectors, and not broken by beautification",
                A / "tab_detection.png", "Video AUC 0.954 on Celeb-DF-v2 and 0.983 on DFD (paired tests: level with Effort and "
                "Forensics Adapter, above SBI). Beautified deepfakes: +2.9 pp vs +15 to +36 pp.", 9.0),
           card("07_evidence", "Explanation", "Restoring the region the model names removes 91 % of its detections",
                A / "flip_bars.png", "The true edited region removes 92 %; a random region 11-15 %. The part is named "
                "correctly in 98-99 % of held-out part forgeries.", 8.0),
           text_card("08_limits", "Limitations", "What does not work yet", [
               ("Unseen retouching services", "Retouched vs. untouched photos: 70 % balanced accuracy (target 75 %); "
                "42 % of untouched originals are called filter.", RED),
               ("Which operation", "Smoothing is named reliably; eye enlargement and face reshaping are often missed.", RED),
               ("Still photos", "Part forgeries on high-quality FFHQ photos: 60-92 % detected (main model), 38-64 % (Ours-lite).", RED),
               ("How much", "Edit strengths could not be estimated; the sentence is a template, no language model.", MUTED)], 10.0),
           end_card()]
    (OUT / "cards.json").write_text(json.dumps(seq, indent=1)); print(json.dumps(seq, indent=1))


if __name__ == "__main__":
    main()
