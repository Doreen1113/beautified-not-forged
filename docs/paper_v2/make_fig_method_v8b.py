"""Image assets of fig_method_v8b (the method overview of main_v8.tex). The figure itself is TikZ: figs_tikz/fig_method_v8b.tex,
compiled by `sh docs/paper_v2/figs_tikz/build.sh fig_method_v8b` and copied to figs/fig_method_v8b.{pdf,png} by this script's
--copy step. No number is computed here; the counts printed in the figure are verified in FIGURES_V8B.md against
results/research/retouch_unified_20260929/manifest_train.tsv and train_ru_clipe5_s20260929.log.

python docs/paper_v2/make_fig_method_v8b.py              (thumbnails + evidence map of the main model, needs CUDA for the map)
python docs/paper_v2/make_fig_method_v8b.py --no-model   (thumbnails only; evidence map from the cache figs/fig_method_v8b_ev.npz)
python docs/paper_v2/make_fig_method_v8b.py --copy       (copy figs_tikz/fig_method_v8b.{pdf,png} to figs/)

Thumbnails (figs_tikz/img/m8_*.png):
  (a) m8_orig / m8_s90  : ffhq_originals/Part2/17005.png and FFHQ_ali_process/Smoothing_90/17000/17005.png, the central crop of
                          make_fig_teaser_v8b.py ([200:840, 192:832]); 17005 is the first stem after the three of Fig. 1 present in both folders, so no
                          face is shown twice in the paper.
      m8_cdf / m8_cdfb  : Celeb-DF-B frame id10_id11_0003__f05, folder synthesis (untreated deepfake) and synthesis_beautified
                          (same video, app preset), frames_std32v3 (splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt).
  (b) m8_x / m8_ev      : held-out part-level forgery ffpp_partedit/test/donor/682__f0867__nose.jpg (the first item of
                          figs/fig_evidence_items.json) and the 16 x 16 evidence map of the paper's main model (clipe5_s20260929,
                          main_model.MAIN_TAG) on it, sigmoid, bilinear upsampling, figstyle.overlay.
      m8_gen / m8_fake / m8_beau : one training item per class, rows of manifest_train.tsv in file order: ffhq_orig row 40
                          (60057, genuine), ffpp_fake row 5000 (Deepfakes 463_464__f0210, forged), megvii row 2000 (61334,
                          beautified, commercial render); adults with a neutral background, picked from a contact sheet.
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

B = Path(r"C:\My_Project\AIGC"); P = B / "docs/paper_v2"; IMG = P / "figs_tikz/img"; RU = B / "results/research/retouch_unified_20260929"
CACHE = P / "figs/fig_method_v8b_ev.npz"
PART = B / "ffpp_partedit/test/donor/682__f0867__nose.jpg"


def sq(a, n=256):
    """Centre square crop and resize to n x n."""
    h, w = a.shape[:2]; s = min(h, w); y, x = (h - s) // 2, (w - s) // 2
    return np.array(Image.fromarray(a[y:y + s, x:x + s]).resize((n, n), Image.LANCZOS))


def save(a, name):
    Image.fromarray(np.asarray(a, np.uint8)).save(IMG / f"{name}.png"); print("wrote", IMG / f"{name}.png", a.shape)


def thumbs():
    o = np.array(Image.open(B / "ffhq_originals/Part2/17005.png").convert("RGB"))[200:840, 192:832]
    s = np.array(Image.open(B / "FFHQ_ali_process/Smoothing_90/17000/17005.png").convert("RGB"))[200:840, 192:832]
    save(sq(o, 320), "m8_orig"); save(sq(s, 320), "m8_s90")
    F = B / "external_data/celebdfb/frames_std32v3"
    for folder, nm in (("synthesis", "m8_cdf"), ("synthesis_beautified", "m8_cdfb")):
        save(sq(np.array(Image.open(F / folder / "id10_id11_0003__f05.jpg").convert("RGB")), 256), nm)
    rows = [l.split("\t") for l in (RU / "manifest_train.tsv").read_text(encoding="utf-8").splitlines()[1:]]
    by = {}
    for r in rows:
        by.setdefault(r[2], []).append(r)
    for src, k, nm in (("ffhq_orig", 40, "m8_gen"), ("ffpp_fake", 5000, "m8_fake"), ("megvii", 2000, "m8_beau")):
        r = by[src][k]; a = np.array(Image.open(r[0]).convert("RGB"))
        if r[3] != "-":   # FFHQ rows carry the face box; FF++ frames are already face crops
            x0, y0, x1, y1 = [int(v) for v in r[3].split()]; a = a[y0:y1, x0:x1]
        save(sq(a, 224), nm); print("  from", r[0])


def evidence(use_model):
    sys.path.insert(0, str(RU)); sys.path.insert(0, str(P))
    import figstyle as FS
    arr = np.array(Image.open(PART).convert("RGB"))
    if use_model:
        import torch
        import torch.nn.functional as F
        from train_ru3 import to_t2
        from train_ru_clip import load_clip
        from main_model import MAIN_TAG
        net = load_clip(MAIN_TAG, head=True).cuda().eval()
        x = to_t2(arr, 224, False, "clip")[None].cuda()
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            out = net(x)
        lo, ev = out[0], out[3]
        p = torch.softmax(lo.float(), 1)[0].cpu().numpy()
        e16 = torch.sigmoid(ev.float())[0, 0].cpu().numpy()
        np.savez(CACHE, e16=e16, p=p, tag=MAIN_TAG); print("model", MAIN_TAG, "P(real, fake, beautified) =", np.round(p, 4))
    z = np.load(CACHE); e16 = z["e16"]
    import torch
    import torch.nn.functional as F
    up = F.interpolate(torch.from_numpy(e16)[None, None], size=arr.shape[:2], mode="bilinear", align_corners=False)[0, 0].numpy()
    save(sq(arr, 256), "m8_x")
    save(sq((FS.overlay(arr, up) * 255).astype(np.uint8), 256), "m8_ev")
    # the raw 16 x 16 grid, nearest-neighbour, for the map icon
    import matplotlib.pyplot as plt
    g = (plt.get_cmap(FS.MAP_CMAP)(np.clip(e16, 0, 1))[..., :3] * 255).astype(np.uint8)
    save(np.array(Image.fromarray(g).resize((256, 256), Image.NEAREST)), "m8_grid")


if __name__ == "__main__":
    if "--copy" in sys.argv:
        for ext in ("pdf", "png"):
            shutil.copy(P / f"figs_tikz/fig_method_v8b.{ext}", P / f"figs/fig_method_v8b.{ext}"); print("copied", ext)
    else:
        thumbs(); evidence("--no-model" not in sys.argv)
