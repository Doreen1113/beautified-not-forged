"""Build the 2026-09-30 project-meeting deck (English, figure-first) from assets/*.png.

python docs/meeting_20260930/build_deck.py -> docs/meeting_20260930/meeting_20260930_v3.pptx (+ speaker_notes.md)
Layout follows the team's "84 Meeting" deck: white slides, serif titles top-left, a small blue section tag above the title,
tiny corner squares, a grey rounded block on the title and closing slides. Each content slide states its conclusion in the
title, shows one main figure or table, and ends with a one-line takeaway (conclusion first, evidence second).
"""
import json
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

H = Path(__file__).resolve().parent; A = H / "assets"
NUM = json.loads((A / "asset_numbers.json").read_text(encoding="utf-8"))

INK = RGBColor(0x1F, 0x2A, 0x37); MUTED = RGBColor(0x5F, 0x67, 0x73); BLUE = RGBColor(0x0F, 0x4D, 0x92)
RED = RGBColor(0xB6, 0x43, 0x42); GREEN = RGBColor(0x2F, 0x7D, 0x32); PILL = RGBColor(0xEF, 0xEF, 0xEF)
NOTE_BG = RGBColor(0xF1, 0xF5, 0xFA); OPEN_BG = RGBColor(0xFB, 0xEE, 0xEC); WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SERIF, SANS = "Cambria", "Calibri"
W, HH = 13.333, 7.5

prs = Presentation(); prs.slide_width = Inches(W); prs.slide_height = Inches(HH)
BLANK = prs.slide_layouts[6]


def text(slide, x, y, w, h, runs, size=16, font=SANS, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         italic=False, spacing=None):
    """runs: str, or list of paragraphs; a paragraph is a str or a list of (text, {bold,color,size,font,italic})."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = tb.text_frame
    tf.word_wrap = True; tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph(); p.alignment = align
        if spacing:
            p.space_after = Pt(spacing)
        for seg, opt in ([(para, {})] if isinstance(para, str) else para):
            r = p.add_run(); r.text = seg; f = r.font
            f.name = opt.get("font", font); f.size = Pt(opt.get("size", size)); f.bold = opt.get("bold", bold)
            f.italic = opt.get("italic", italic); f.color.rgb = opt.get("color", color)
    return tb


def box(slide, x, y, w, h, fill, radius=0.12, line=None):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    s.adjustments[0] = radius; s.fill.solid(); s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line; s.line.width = Pt(1)
    s.shadow.inherit = False
    return s


def square(slide, x, y, s=0.09, color=INK):
    r = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(s), Inches(s))
    r.fill.solid(); r.fill.fore_color.rgb = color; r.line.fill.background(); r.shadow.inherit = False


def corners(slide):
    for x, y in ((12.93, 0.3), (0.3, 7.1), (12.93, 7.1)):
        square(slide, x, y)


def picture(slide, name, x, y, w, h, align="center"):
    """Fit an asset into the (x, y, w, h) box, keeping its aspect ratio."""
    iw, ih = Image.open(A / name).size; r = iw / ih
    pw, ph = (w, w / r) if w / r <= h else (h * r, h)
    px = x + (w - pw) / 2 if align == "center" else x
    slide.shapes.add_picture(str(A / name), Inches(px), Inches(y + (h - ph) / 2), Inches(pw), Inches(ph))
    return px, y + (h - ph) / 2, pw, ph


def content(tag, title, notes=""):
    s = prs.slides.add_slide(BLANK); corners(s)
    text(s, 0.6, 0.32, 8, 0.3, f"[{tag}]", size=13, color=BLUE, font=SERIF, bold=True)
    text(s, 0.6, 0.62, 12.1, 0.6, title, size=26, font=SERIF, bold=True, anchor=MSO_ANCHOR.TOP)
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def takeaway(s, msg, y=6.45, bg=NOTE_BG, color=INK):
    box(s, 0.6, y, 12.1, 0.62, bg, radius=0.25)
    text(s, 0.85, y, 11.6, 0.62, msg, size=17, color=color, bold=True, anchor=MSO_ANCHOR.MIDDLE)


def caption(s, x, y, w, msg, size=12.5):
    text(s, x, y, w, 0.5, msg, size=size, color=MUTED, italic=True)


# ---------------------------------------------------------------------------- 1 title
s = prs.slides.add_slide(BLANK)
pill = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(-1.2), Inches(0.9), Inches(9.9), Inches(4.8))
pill.adjustments[0] = 0.5; pill.fill.solid(); pill.fill.fore_color.rgb = PILL; pill.line.fill.background(); pill.shadow.inherit = False
square(s, 8.45, 0.75); square(s, 0.55, 5.95)
text(s, 0.9, 1.75, 7.6, 1.8, ["Beautified Is Not Forged"], size=40, font=SERIF, bold=True)
text(s, 0.9, 2.75, 7.4, 1.0, "Separating Beautification from Face Forgery", size=20, font=SERIF, color=MUTED)
text(s, 0.9, 3.85, 7.4, 0.4, "Progress report  ·  30 September 2026  (revised 1 October)", size=15, color=INK)
text(s, 0.9, 4.35, 7.4, 0.4, "林沁瑩  陳柏融  游宸山", size=15, color=INK, align=PP_ALIGN.LEFT)

# ---------------------------------------------------------------------------- 2 summary (conclusion first)
e = {k: [round(v + 1e-9, 1) for v in vs] for k, vs in NUM["escape_split (total, reencode, beauty)"].items()}   # half-up, as in the paper
s = content("Summary", "Where we are, in one slide",
            "Conclusion first: three results we can defend and one open problem.")
cards = [(f"{e['Ours'][2]:+.1f} pp", "extra deepfakes let through\nbecause of beautification",
          f"SBI {e['SBI'][2]:+.1f}   Effort {e['Effort (CLIP)'][2]:+.1f}   Forensics Adapter {e['Forensics Adapter (CLIP)'][2]:+.1f}"),
         ("0.1%", "commercially retouched faces\ncalled fake (unseen service)", "published detectors: 9.5–14.8% at 5% FPR"),
         ("91%", "of detections removed by restoring\nthe region our model names", "ceiling (true edit region): 92%")]
for i, (big, lab, sub) in enumerate(cards):
    x = 0.6 + i * 4.1
    box(s, x, 1.75, 3.85, 2.75, NOTE_BG, radius=0.08)
    text(s, x + 0.3, 1.95, 3.3, 0.9, big, size=44, font=SERIF, bold=True, color=BLUE)
    text(s, x + 0.3, 2.95, 3.4, 0.8, lab, size=16, color=INK, bold=True)
    text(s, x + 0.3, 3.85, 3.4, 0.5, sub, size=12.5, color=MUTED)
text(s, 0.6, 4.8, 12.1, 0.5, [[("Forgery detection: ", {"bold": True}),
                                ("level with the two 2025 CLIP detectors (Celeb-DF-v2 0.954, DFD 0.983 video AUC) and clearly above SBI.", {})]],
     size=17)
text(s, 0.6, 5.3, 12.1, 0.5, [[("Explanation: ", {"bold": True}), ("one output per image with the label, the edit operations, the edited facial part and a sentence.", {})]],
     size=17)
takeaway(s, "Open: separating lightly retouched faces from their originals on an unseen service reaches 70% (target 75%).",
         bg=OPEN_BG, color=RED)

# ---------------------------------------------------------------------------- 3 agenda
s = prs.slides.add_slide(BLANK); corners(s)
text(s, 0.6, 0.6, 12.1, 0.8, "Agenda", size=32, font=SERIF, bold=True, align=PP_ALIGN.CENTER)
items = [("Problem", "why it matters, and why a real / fake detector fails on beautified faces"),
         ("Definitions", "real, filter and fake, decided by what an edit changes"),
         ("Method", "supervision from paired originals"),
         ("Results", "training / validation / test accuracy, forgery detection, commercial retouching"),
         ("Explanation", "what the system says, and how far it can be trusted"),
         ("Status & next steps", "targets met and missed, next two weeks")]
for i, (a, b) in enumerate(items):
    y = 1.6 + i * 0.85
    text(s, 2.4, y, 1.0, 0.8, f"{i + 1:02d}", size=34, font=SERIF, color=RGBColor(0xA8, 0xAE, 0xB6))
    text(s, 3.5, y + 0.12, 8.5, 0.6, [[(a, {"bold": True, "font": SERIF, "size": 21}), ("    " + b, {"color": MUTED, "size": 16})]])

# ---------------------------------------------------------------------------- 4 problem: why it matters (added 2026-10-01)
s = content("Problem", "Why it matters: both errors of a binary detector have a cost")
text(s, 0.6, 1.4, 12.1, 0.5, "Forgery detectors are used for content moderation, remote identity checks and fact-checking.",
     size=17, color=INK)
why = [("False accusation", "a genuine face called fake", RED, "≥ 14.5%",
        "of beautified genuine faces called fake by every one of 13 detectors, once at most 5% of beautified deepfakes may pass (FF++)",
        "Unseen commercial retouching: 36–63% of strongly smoothed genuine faces called fake (11 FF++ detectors, 5% FPR)"),
       ("Evasion", "a beauty filter hides a deepfake", BLUE, f"+{e['Effort (CLIP)'][2]:.0f} to +{e['SBI'][2]:.0f} pp",
        "more deepfakes pass after app beautification (Celeb-DF-B, re-encoding effect removed)",
        f"SBI +{e['SBI'][2]:.1f}   Forensics Adapter +{e['Forensics Adapter (CLIP)'][2]:.1f}   Effort +{e['Effort (CLIP)'][2]:.1f}")]
for i, (head, sub, c, big, lab, extra) in enumerate(why):
    x = 0.6 + i * 6.2
    box(s, x, 2.05, 5.9, 3.55, NOTE_BG, radius=0.06)
    text(s, x + 0.35, 2.2, 5.3, 0.5, [[(head, {"bold": True, "color": c, "font": SERIF, "size": 21}), ("   " + sub, {"color": MUTED, "size": 14})]])
    text(s, x + 0.35, 2.8, 5.3, 0.8, big, size=40, font=SERIF, bold=True, color=c)
    text(s, x + 0.35, 3.7, 5.2, 0.9, lab, size=15, bold=True)
    text(s, x + 0.35, 4.7, 5.2, 0.8, extra, size=13, color=MUTED)
text(s, 0.6, 5.75, 12.1, 0.4, "Retouching is common on social media, photo-sharing sites and even identification cards "
     "(Bharati et al., IEEE TIFS 2016).", size=13, color=MUTED, italic=True)
takeaway(s, "Both errors come from the two-label space: a threshold only trades one for the other, so we add a third label.")

# ---------------------------------------------------------------------------- 5 problem: teaser
s = content("Problem", "Binary detectors must accuse beautified faces or miss deepfakes")
picture(s, "fig_teaser.png", 0.6, 1.65, 12.1, 4.45)
takeaway(s, "Beautification changes how a face looks, not who is shown or what they do: it needs its own label, filter.")

# ---------------------------------------------------------------------------- 6 definitions (added 2026-10-01)
s = content("Definitions", "Three labels, decided by what an edit changes")
defs = [("real", GREEN, "the capture as recorded, including camera processing and compression"),
        ("filter", RGBColor(0xA8, 0x78, 0x1A), "still the captured person at the captured moment; only the appearance of "
                                                "their own face changed (tone, texture, smooth reshaping). Identity, expression, "
                                                "pose and speech unchanged"),
        ("fake", RED, "shows a person or an action that was not captured: face swap, reenactment, synthesis, or a facial "
                      "part from another person or generated")]
y = 1.5
for lab, c, d in defs:
    h = 1.05 if lab == "real" else 1.45
    box(s, 0.6, y, 4.75, h, NOTE_BG, radius=0.08)
    text(s, 0.85, y + 0.12, 4.3, h - 0.2, [[(lab, {"bold": True, "color": c, "font": SERIF, "size": 20})], d], size=13.5, spacing=2)
    y += h + 0.12
picture(s, "tab_labels.png", 5.6, 1.5, 7.1, 4.25)
takeaway(s, "Any fake edit makes the image fake. The tool does not decide: neural retouching is filter; reenactment keeps the identity but is fake.")

# ---------------------------------------------------------------------------- 5 problem: frontier
s = content("Problem", "No threshold of 13 published detectors reaches our pair of errors")
picture(s, "fig_frontier.png", 0.6, 1.5, 12.1, 4.75)
takeaway(s, "Every grey curve is one detector over all thresholds; none enters the box under our two models.")

# ---------------------------------------------------------------------------- 6 problem: escape caused by beautification
s = content("Problem", "Beautification alone lets deepfakes escape, even CLIP detectors")
picture(s, "escape_split.png", 0.6, 1.55, 8.3, 4.7)
text(s, 9.3, 1.9, 3.5, 4.2, [
    [("Celeb-DF-B", {"bold": True})], "third-party benchmark, app beautification, 232 genuine + 232 deepfake videos",
    [("How it is measured", {"bold": True})], "each binary detector at 5% FPR on untreated genuine frames; the re-encoding effect is removed with the compression-only videos",
    [("Ours", {"bold": True, "color": BLUE})], f"{e['Ours'][0]:+.1f} pp in total, all of it from re-encoding"],
     size=13.5, spacing=6)
takeaway(s, f"SBI loses {e['SBI'][2]:.1f} pp to beautification alone; our model loses nothing measurable.")

# ---------------------------------------------------------------------------- 7 problem: blur
b = NUM["blur_bars (sharp, blur)"]
s = content("Problem", "One more label is not enough: blurred real faces look forged")
picture(s, "blur_bars.png", 0.6, 1.5, 8.6, 4.8)
text(s, 9.55, 1.9, 3.3, 4.2, [
    [("Cause", {"bold": True})], "self-blending blurs one side of the blend, so the detector learns soft = fake",
    [("Fix", {"bold": True, "color": BLUE})], "apply the same blur or downscale to the real, filter and fake image of each training triplet",
    [("Caveat", {"bold": True, "color": RED})], "strong JPEG (q30) raises false alarms by 6 pp for Ours and 15 pp for Ours-lite"], size=13.5, spacing=6)
takeaway(s, f"Same 300 genuine frames: SBI calls {b['SBI'][1]:.0f}% fake after blur, our FF++-only model {b['three-way, FF++ only'][1]:.0f}%, Ours {b['Ours'][1]:.0f}%.")

# ---------------------------------------------------------------------------- 8 method overview
s = content("Method", "One model, three heads, trained on paired originals")
picture(s, "fig_overview.png", 0.5, 1.45, 12.3, 5.0)
takeaway(s, "Every edited training image has a pixel-aligned original, so its label and its edit region are exact.")

# ---------------------------------------------------------------------------- 9 method: decomposition
s = content("Method", "Key idea: split each commercial render into single operations")
picture(s, "fig_decomp.png", 0.6, 1.4, 12.1, 3.45)
picture(s, "eq_decomp.png", 0.6, 4.95, 6.4, 1.35, align="left")
text(s, 7.4, 5.0, 5.3, 1.4, [
    [("Why: ", {"bold": True}), ("commercial services apply four edits at once, and a model trained on renders learns only their co-occurrence.", {})],
    [("Result: ", {"bold": True}), ("50k single-operation training images from two services (after dropping edits below the measurement noise); the four parts recompose the render at 108 dB.", {})]],
     size=13.5, spacing=6)

# ---------------------------------------------------------------------------- results: train / val / test (added 2026-10-01)
s = content("Results", "Training, validation and test accuracy")
picture(s, "tab_splits.png", 0.6, 1.4, 12.1, 4.3)
text(s, 0.6, 5.8, 12.1, 0.5, "Recall per class (%). Training accuracy on a random sample of 2,000 images per row (4,000 part-level "
     "forgeries); validation and test on every image. Commercial test data: the unseen service.", size=12.5, color=MUTED, italic=True)
takeaway(s, "New finding: Ours keeps only 59.5% of its own training originals real, so the filter bias exists on training data.",
         bg=OPEN_BG, color=RED)

s = content("Results", "Checkpoints are chosen on validation; no test set is used")
picture(s, "fig_training.png", 0.6, 1.5, 12.1, 3.6)
text(s, 0.6, 5.25, 12.1, 0.9, [
    [("Selection rule: ", {"bold": True}), ("the epoch with the highest mean of FF++ validation macro-F1 and filter F1 on held-out "
                                            "Tencent / Megvii faces (star).", {})],
    [("Chosen: ", {"bold": True}), ("Ours epoch 4 of 8, Ours-lite epoch 12 of 12.", {})]], size=14, spacing=4)
takeaway(s, "Validation macro-F1 levels off after epoch 4 for Ours; training loss keeps falling.")

s = content("Results", "The train–test gap is in genuine frames")
picture(s, "fig_confusion.png", 0.6, 1.45, 7.4, 4.85, align="left")
text(s, 8.3, 1.75, 4.5, 4.4, [
    [("How to read", {"bold": True})], "FF++ c23, rows = true class, % of the row; top Ours, bottom Ours-lite",
    [("Genuine", {"bold": True, "color": RED})], "Ours 94.2 → 78.0 from training to test; at test 13.2% go to filter, 8.8% to fake",
    [("Fake and filter", {"bold": True, "color": GREEN})], "Ours stays within 2.1 points of training"], size=14, spacing=6)
takeaway(s, "Next: find why genuine faces drift to filter, on FF++ and on the commercial originals alike.")

# ---------------------------------------------------------------------------- 10 results: detection table
s = content("Results", "Detection: level with 2025 CLIP detectors, not broken by filters")
picture(s, "tab_detection.png", 0.6, 1.55, 12.1, 3.4)
text(s, 0.6, 5.15, 12.1, 1.1, [
    [("Paired bootstrap on the same frames: ", {"bold": True}),
     ("Ours − SBI is positive in all four settings; Ours − Effort and Ours − Forensics Adapter contain 0 in all eight (level, not better).", {})],
    [("FA at MISS≤5: ", {"bold": True}), ("beautified genuine faces a binary detector must accuse to keep beautified deepfakes under 5% (ours: no threshold, escape in parentheses).", {})]],
     size=13.5, spacing=6)
takeaway(s, "Claim: level with Effort and Forensics Adapter, above SBI, and beautification does not break it.")

# ---------------------------------------------------------------------------- 11 results: commercial retouching
s = content("Results", "Unseen retouching service: no false accusation, 70% separation")
picture(s, "fig_accuse.png", 0.6, 1.5, 5.4, 4.75)
picture(s, "retouch_balanced.png", 6.3, 1.5, 6.4, 4.75)
caption(s, 0.6, 6.05, 5.4, "retouched genuine faces called fake, 5% FPR on originals")
caption(s, 6.3, 6.05, 6.4, "2,210 FFHQ originals vs. their 26,519 Alibaba renders")
takeaway(s, "Ours sends 82% of retouched faces to filter, but also 42% of untouched originals.", y=6.5, bg=OPEN_BG, color=RED)

# ---------------------------------------------------------------------------- 12 explanation: what the system outputs
s = content("Explanation", "What the system outputs for one image")
picture(s, "system_output.png", 0.5, 1.4, 12.3, 4.75)
text(s, 0.6, 6.05, 12.1, 0.35, "Examples fixed in advance, wrong cases kept: one FF++ genuine frame, the four Alibaba edits of one face, "
     "one part forgery, one whole-face deepfake.", size=12, color=MUTED, italic=True)
takeaway(s, "Label, operations and facial part each come from one head; the sentence is a template, no language model.", y=6.5)

# ---------------------------------------------------------------------------- 13 explanation: how reliable the text is
s = content("Explanation", "How far each part of the sentence can be trusted")
picture(s, "tab_explain.png", 0.6, 1.55, 12.1, 3.6)
text(s, 0.6, 5.2, 12.1, 1.1, [
    [("Fixed today: ", {"bold": True}),
     ("the facial part used to be named by area share, so the large skin region almost always won (right part in 8–12%). "
      "Naming it by the mean evidence inside each part gives 98–99%; the map itself was right all along.", {})],
    [("Sentences are templates: ", {"bold": True}),
     ("379 test images give 14 distinct sentences (real 1, fake 4, filter 9); what differs per image is the numbers behind them.", {})]],
     size=13.5, spacing=4)
takeaway(s, "Where the forgery is: reliable. Which retouching operation: reliable for smoothing, weak for eyes and face shape.")

# ---------------------------------------------------------------------------- 14 explanation: examples
s = content("Explanation", "The evidence map marks the edited part")
picture(s, "fig_evidence.png", 0.6, 1.45, 12.1, 4.85)
takeaway(s, "Held-out part-level forgeries: input, true edit region, our map, Score-CAM, and the image after restoring the region.")

# ---------------------------------------------------------------------------- 13 explanation: faithfulness numbers
f = NUM["flip_bars"]
s = content("Explanation", "Restoring the named region removes 91% of detections")
picture(s, "flip_bars.png", 0.6, 1.5, 12.1, 4.75)
takeaway(s, f"Supervision with exact edit regions makes the difference: the same model without part-level edits reaches {min(f['head, no part edits']):.0f}–{max(f['head, no part edits']):.0f}%.")

# ---------------------------------------------------------------------------- 14 status: targets
s = content("Status", "Targets we set before training: five met, four missed")
picture(s, "tab_targets.png", 1.2, 1.55, 10.9, 3.9)
text(s, 0.6, 5.65, 12.1, 0.6, "No target was changed after seeing the test sets, and no model was re-tuned on them.", size=14, color=MUTED, italic=True)
takeaway(s, "Three of the four misses concern commercial retouching; the fourth is FF++ genuine recall (78.0 vs. 80).")

# ---------------------------------------------------------------------------- 15 status: done / next
s = content("Status", "Done and next")
cols = [("Done", GREEN, ["13 published detectors re-scored on the same frames",
                         "One model: detection + filter + evidence head",
                         "Text explanation from all three heads",
                         "Edge model: TFLite 18 MB, 9.7 ms on one CPU thread",
                         "Label definitions; train / val / test accuracy"]),
        ("Next two weeks", BLUE, ["Why 40–44% of untouched originals go to filter, training originals included",
                                  "Name an operation only when that head is reliable",
                                  "Explanations specific to each image instead of a fixed template"])]
for i, (head, c, lines) in enumerate(cols):
    x = 0.6 + i * 6.2
    box(s, x, 1.65, 5.9, 4.5, NOTE_BG, radius=0.06)
    text(s, x + 0.35, 1.85, 5.2, 0.5, head, size=21, font=SERIF, bold=True, color=c)
    for j, l in enumerate(lines):
        y = 2.55 + j * 0.72
        dot = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 0.4), Inches(y + 0.1), Inches(0.16), Inches(0.16))
        dot.fill.solid(); dot.fill.fore_color.rgb = c; dot.line.fill.background(); dot.shadow.inherit = False
        text(s, x + 0.75, y, 4.9, 0.8, l, size=15.5)

# ---------------------------------------------------------------------------- 17 thank you
s = prs.slides.add_slide(BLANK)
pill = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(-1.2), Inches(4.6), Inches(9.0), Inches(2.9))
pill.adjustments[0] = 0.5; pill.fill.solid(); pill.fill.fore_color.rgb = PILL; pill.line.fill.background(); pill.shadow.inherit = False
square(s, 7.9, 4.45); square(s, 0.55, 7.1)
text(s, 1.2, 5.3, 6.5, 1.2, "THANK YOU", size=48, font=SANS, bold=True, anchor=MSO_ANCHOR.MIDDLE)

from speaker_notes import NOTES  # noqa: E402
assert len(NOTES) == len(prs.slides), (len(NOTES), len(prs.slides))
md = ["# 講稿：專題進度報告 2026-09-30", ""]
for i, (sl, note) in enumerate(zip(prs.slides, NOTES), 1):
    sl.notes_slide.notes_text_frame.text = note.replace("\n", "")
    title = next((sh.text_frame.text for sh in sl.shapes if sh.has_text_frame and sh.text_frame.text.strip()
                  and not sh.text_frame.text.startswith("[")), "")
    md += [f"## {i}. {title.splitlines()[0] if title else ''}", "", note.replace("\n", ""), ""]
(H / "speaker_notes.md").write_text("\n".join(md), encoding="utf-8")
# presenter's own version (keeps personal marks such as pronunciation hints), same order and titles
user = json.loads((H / "notes_user_v4.json").read_text(encoding="utf-8"))
assert len(user) == len(prs.slides)
txt = ["講稿：專題進度報告 2026-09-30（2026-10-01 修訂版）", ""]
for i, (sl, note) in enumerate(zip(prs.slides, user), 1):
    title = next((sh.text_frame.text for sh in sl.shapes if sh.has_text_frame and sh.text_frame.text.strip()
                  and not sh.text_frame.text.startswith("[")), "")
    txt += [f"【第 {i} 頁】{title.splitlines()[0] if title else ''}", "", note, ""]
(H / "speaker_notes.txt").write_text("\n".join(txt), encoding="utf-8-sig")
out = H / "meeting_20260930_v4.pptx"; prs.save(out); print("saved", out, len(prs.slides), "slides")
