"""fig_evidence: held-out part edits with GT footprint, evidence head map, Score-CAM on HYBPE, and the restored
counterfactual (CGD region restored) with the model's decision on it.

python docs/paper_v2/make_fig_evidence.py
"""
import json
import sys
from pathlib import Path

import cv2
import matplotlib
import numpy as np
import torch

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BASE = Path(r"C:\My_Project\AIGC")
sys.path.insert(0, str(BASE / "docs/paper_v2")); sys.path.insert(0, str(BASE / "results/research/cgd_20260927"))
import make_figures as MF  # noqa: E402
from eval_cgd_explain import CAM, TF, SIZE, dilate_t, footprint_gt, load_items, region_from_map  # noqa: E402
from train_cgd import CGDNet  # noqa: E402
from PIL import Image  # noqa: E402

CK = BASE / "checkpoints/research/cgd_20260927"
CLS = ["real", "fake", "filter"]


def load(arm):
    n = CGDNet(head=arm != "HYBPE"); n.load_state_dict(torch.load(CK / f"cgd_{arm}_s20260928.pth", map_location="cpu")); return n.cuda().eval()


def heat(im, m, alpha=0.45):
    hm = cv2.applyColorMap((np.clip(m, 0, 1) * 255).astype(np.uint8), cv2.COLORMAP_JET)[..., ::-1]
    return ((1 - alpha) * im + alpha * hm).astype(np.uint8)


def main():
    cgd, hyb = load("MASK"), load("HYBPE"); cam = CAM(hyb)
    rng = np.random.default_rng(11)
    picks = []
    for mech in ("donor", "sd"):
        items = load_items([mech]); rng.shuffle(items)
        for it in items:
            if it["part"] in [p["part"] for p in picks if p["mech"] == mech]:
                continue
            with torch.no_grad():   # keep the figure consistent with the table: correctly detected items only
                pp = torch.softmax(cgd(TF(Image.open(it["x"]).convert("RGB"))[None].cuda())[0], 1)[0]
                if pp.argmax().item() != 1 or pp[1].item() < 0.7:   # detected with margin; borderline cases are in the table
                    continue
            picks.append(it)
            if sum(p["mech"] == mech for p in picks) == 1:
                break
    fig, axes = plt.subplots(len(picks), 5, figsize=(7.1, 1.5 * len(picks)))
    for r, it in enumerate(picks):
        im = Image.open(it["x"]).convert("RGB"); im0 = Image.open(it["x0"]).convert("RGB").resize(im.size)
        x, x0 = TF(im)[None].cuda(), TF(im0)[None].cuda()
        gt = footprint_gt(im, im0); area = gt.mean().item()
        with torch.no_grad():
            lo, ev = cgd(x); p = torch.softmax(lo, 1)[0].cpu().numpy()
            e = torch.sigmoid(ev[0, 0]).float(); reg = dilate_t(region_from_map(e, area))
            xr = (1 - reg[None, None]) * x + reg[None, None] * x0
            pr = torch.softmax(cgd(xr)[0], 1)[0].cpu().numpy()
        sc = cam.scorecam(x, 1)
        S = (200, 240)
        base = np.array(im.resize(S))
        e_up = cv2.resize(torch.nn.functional.interpolate(e[None, None], size=(SIZE, SIZE), mode="bilinear")[0, 0].cpu().numpy(), S)
        sc_up = cv2.resize((sc / (sc.max() + 1e-8)).cpu().numpy(), S)
        gt_up = cv2.resize(gt.cpu().numpy(), S)
        rest = ((xr[0].cpu().permute(1, 2, 0).numpy() * 0.5 + 0.5) * 255).astype(np.uint8); rest = cv2.resize(rest, S)
        tiles = [(base, f"{it['mech']} {it['part']}"), (heat(base, gt_up), "GT footprint"), (heat(base, e_up), f"evidence head  ({CLS[p.argmax()]} {p.max():.2f})"),
                 (heat(base, sc_up), "Score-CAM (no head)"), (rest, f"region restored -> {CLS[pr.argmax()]} {pr.max():.2f}")]
        for c, (t, cap) in enumerate(tiles):
            ax = axes[r, c]; ax.imshow(t); ax.set_xticks([]); ax.set_yticks([])
            ax.set_xlabel(cap, fontsize=6.3)
            for s in ax.spines.values():
                s.set_visible(True); s.set_linewidth(0.5); s.set_color(MF.MUTED)
    fig.tight_layout(pad=0.3)
    MF.save(fig, "fig_evidence")
    json.dump([{k: str(v) for k, v in p.items()} for p in picks], open(MF.OUT / "fig_evidence_items.json", "w"), indent=1)
    print("fig_evidence done")


if __name__ == "__main__":
    main()
