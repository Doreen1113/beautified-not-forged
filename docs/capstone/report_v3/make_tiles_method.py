"""Image tiles for the method-overview figure (figs/fig_method.html), the report's version of the paper's fig_overview
(docs/paper_v2/make_overview.py), at print resolution. Sources are the same real records:
  * FF++ triplet drawn on the fly: docs/paper_v2/make_pipeline.thumbs() (train frame, scripted beautification, self-blend).
  * Tencent render pair FFHQ 60002 and its four single-operation components with footprints: retouch_unified_20260929/decompose.py.
  * Part-level forgery with exact footprint: fig_evidence_items.json item 0 (FF++ test frame 682__f0867, nose from a donor).
  * Outputs of the paper's main model (CLIP ViT-L/14 + LoRA + evidence head, clipe5 seed 20260929) on that forgery and on an
    Alibaba EyeEnlarging_90 render (FFHQ 17024, a service never used in training): evidence overlays and the numbers.
Writes figs/method_*.png and figs/method_numbers.json.
python make_tiles_method.py"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

B = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent; OUT = HERE / "figs"
RU = B / "results/research/retouch_unified_20260929"
for p in (B / "docs/paper_v2", RU):
    sys.path.insert(0, str(p))
import make_pipeline as MP  # noqa: E402
import decompose as D  # noqa: E402

W, H = 300, 360          # tile pixels (printed at about 1.5 x 1.8 cm)
NN = (38, 166, 220)      # footprint colour (cyan-blue), same in the figure legend


def save(name, arr):
    Image.fromarray(np.ascontiguousarray(np.clip(arr, 0, 255).astype(np.uint8))).save(OUT / f"method_{name}.png", optimize=True)


def fit(im, w=W, h=H):
    return cv2.resize(np.ascontiguousarray(im), (w, h), interpolation=cv2.INTER_AREA)


def footprint_tile(m01, w=W, h=H):
    m = cv2.resize(m01.astype(np.float32), (w, h), interpolation=cv2.INTER_AREA) > 0.5
    rgb = np.full((h, w, 3), 236, np.uint8); rgb[m] = NN; return rgb


def heat(im, m, alpha=0.5):
    hm = cv2.applyColorMap((np.clip(m, 0, 1) * 255).astype(np.uint8), cv2.COLORMAP_JET)[..., ::-1]
    return ((1 - alpha) * im + alpha * hm).astype(np.uint8)


# ----------------------------------------------------------------------------- 1 FF++ triplet, on the fly
def ffpp_triplet():
    z = np.load(MP.BASE / "results/research/fasb_20260926/landmarks_train.npz")
    stem = sorted(z.files)[20000]
    rgb = cv2.imread(str(MP.BASE / "FaceForensics_protocol_frames_dense/train/real" / f"{stem}.jpg"))[..., ::-1].copy()
    rng = np.random.default_rng(7); sb = None
    while sb is None:
        sb = MP.self_blend(rgb, z[stem], rng)
    save("ffpp_real", fit(rgb)); save("ffpp_filter", fit(MP.beautify(rgb, np.random.default_rng(3)))); save("ffpp_fake", fit(sb))
    save("ffpp_fake_filter", fit(MP.beautify(sb, np.random.default_rng(3))))
    return stem


# ----------------------------------------------------------------------------- 2 Tencent pair -> single operations
def vendor():
    stem = "60002"
    row = [l.split("\t") for l in (RU / "pairs_tencent.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.split("\t")[0].endswith(f"{stem}.png")][0]
    O, R, comp, _ = D.decompose(row[0], row[1], stem)
    b = [int(v / 2) for v in json.loads((RU / "ffhq_boxes.json").read_text())[stem]]
    crop = lambda im: np.ascontiguousarray(im[b[1]:b[3], b[0]:b[2]])
    diff = lambda im: np.abs(crop(im).astype(np.float32) - crop(O).astype(np.float32))
    k = np.ones((9, 9), np.uint8)
    save("vendor_O", fit(crop(O))); save("vendor_R", fit(crop(R)))
    names = {"eye": "eye", "jaw": "contour", "white": "tone", "smooth": "texture"}
    for key, v in comp.items():
        dm = diff(v).mean(2); hi = max(float(np.percentile(dm, 99.5)), 1.0)      # each component scaled to its own 99.5th percentile
        d = np.clip(dm / hi * 255, 0, 255).astype(np.uint8)
        mag = np.ascontiguousarray(cv2.applyColorMap(d, cv2.COLORMAP_MAGMA)[..., ::-1])
        M = cv2.dilate((diff(v).max(2) > 6).astype(np.uint8), k)
        cs, _ = cv2.findContours(M, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        outlined = fit(mag); sx, sy = W / mag.shape[1], H / mag.shape[0]
        cs = [np.round(c.astype(np.float32) * [sx, sy]).astype(np.int32) for c in cs if cv2.contourArea(c) > 30]
        cv2.drawContours(outlined, cs, -1, NN, 4)                                   # exact footprint M as an outline
        save(f"comp_{names[key]}", outlined)
        save(f"comp_{names[key]}_M", footprint_tile(M))
        save(f"comp_{names[key]}_img", fit(crop(v)))
    return stem, sorted(names.values())


# ----------------------------------------------------------------------------- 3 part-level forgery with exact footprint
def part_edit():
    it = json.loads((B / "docs/paper_v2/figs/fig_evidence_items.json").read_text())[0]
    x = cv2.imread(it["x"])[..., ::-1].copy(); x0 = cv2.imread(it["x0"])[..., ::-1].copy()
    z = np.load(it["m"]); m = z[z.files[0]].astype(np.float32)
    if m.max() > 1: m = m / 255.0
    if m.shape[:2] != x.shape[:2]: m = cv2.resize(m, (x.shape[1], x.shape[0]), interpolation=cv2.INTER_NEAREST)
    S = min(x.shape[:2]); sq = lambda im: im[:S, :S]
    save("part_x", fit(sq(x), W, W)); save("part_x0", fit(sq(x0), W, W)); save("part_M", footprint_tile(sq(m) > 0.5, W, W))
    return it, x


# ----------------------------------------------------------------------------- 4 outputs of the main model
def main_model():
    import torch
    from train_ru_clip import load_clip
    from train_ru3 import CLIP_MEAN, CLIP_STD
    tag = "clipe5_s20260929"
    m = load_clip(tag, head=True).cuda().eval()
    mu, sd = torch.tensor(CLIP_MEAN).view(1, 3, 1, 1).cuda(), torch.tensor(CLIP_STD).view(1, 3, 1, 1).cuda()

    def run(rgb, size):
        im = Image.fromarray(rgb).resize((size, size), Image.BILINEAR)
        x01 = torch.from_numpy(np.asarray(im, np.float32) / 255.0).permute(2, 0, 1)[None]
        x = torch.nn.functional.interpolate(x01.cuda(), size=(224, 224), mode="bilinear", align_corners=False)
        with torch.no_grad():
            o = m((x - mu) / sd); lo, pr, ev = o[0], o[1], o[3]   # RU5: o[0] is the log of the joint (real, fake, filter)
        return torch.softmax(lo, 1)[0].cpu().numpy(), torch.sigmoid(pr)[0].cpu().numpy(), torch.sigmoid(ev[0, 0]).float().cpu().numpy()
    return tag, run


def part_means(rgb, ev):
    """mean evidence per landmark part (eyes, nose, mouth, skin, contour) as the page names it: occlusion_regions.region_masks
    on MediaPipe landmarks, evidence map resized to the image."""
    sys.path.insert(0, str(B)); sys.path.insert(0, str(B / "docs/capstone/src"))
    from occlusion_regions import region_masks
    from filters_v2.scale_normalized_filters import get_landmarks
    lm = np.asarray(get_landmarks(np.ascontiguousarray(rgb)), np.float32)[:, :2]
    M = region_masks(rgb, lm)
    e = cv2.resize(ev, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_LINEAR)
    out = {k: round(float(e[np.asarray(m) > 0].mean()), 3) for k, m in M.items() if np.asarray(m).sum() > 0}
    return out, max(out, key=out.get)


def outputs(run, it, x):
    S = min(x.shape[:2]); xs = x[:S, :S]
    p, pr, ev = run(x, 380)                       # as eval_cgd_explain.py: whole image at 380, then 224 inside
    base = fit(xs, W, W); save("out_fake_in", base); save("out_fake_ev", heat(base, cv2.resize(ev, (W, W), interpolation=cv2.INTER_LINEAR)))
    pm, named = part_means(x, ev)
    J = [j for j in json.loads((RU / "explain_ru_ru2_effb4_s20260929.json").read_text()) if j["alibaba_group"] == "EyeEnlarging_90"][0]
    b = json.loads((RU / "ffhq_boxes.json").read_text())["17024"]
    rgb = np.ascontiguousarray(cv2.imread(J["image"])[..., ::-1][b[1]:b[3], b[0]:b[2]])
    p2, pr2, ev2 = run(rgb, 224)
    base2 = fit(rgb); save("out_filter_in", base2); save("out_filter_ev", heat(base2, cv2.resize(ev2, (W, H), interpolation=cv2.INTER_LINEAR)))
    pm2, named2 = part_means(rgb, ev2)
    f = lambda a: [round(float(v), 3) for v in a]
    return {"fake": {"image": it["x"], "part": it["part"], "p_real_fake_filter": f(p), "ops_eye_contour_tone_texture": f(pr), "part_means": pm, "named": named},
            "filter": {"image": J["image"], "group": "EyeEnlarging_90", "p_real_fake_filter": f(p2), "ops_eye_contour_tone_texture": f(pr2), "part_means": pm2, "named": named2}}


if __name__ == "__main__":
    parts = sys.argv[1:] or ["ffpp", "vendor", "part", "model"]     # python make_tiles_method.py [ffpp vendor part model]
    if "ffpp" in parts: print("ffpp", ffpp_triplet())
    if "vendor" in parts: print("vendor", vendor())
    if "part" in parts or "model" in parts: it, x = part_edit()
    if "model" in parts:
        tag, run = main_model(); num = outputs(run, it, x); num["model"] = tag
        (OUT / "method_numbers.json").write_text(json.dumps(num, indent=1), encoding="utf-8"); print(json.dumps(num, indent=1))
    print("tiles:", len(list(OUT.glob("method_*.png"))))
