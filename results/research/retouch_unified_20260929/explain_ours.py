"""Full structured explanation of the paper's main model (clipe4: CLIP ViT-L/14 + LoRA, three heads) in one output:
label and class probabilities (three-way head), which retouching operations are present (presence head), where the
evidence is (evidence head -> mean evidence inside each landmark facial part, top part; "whole face" when eyes, nose and
mouth all exceed 0.5), and a template sentence built only
from those outputs. No language model. The edit-magnitude head is not used (failed validation).

Examples are fixed in advance (not chosen by outcome): one FF++ genuine frame, the four Alibaba renders of FFHQ 17024 at
level 90 (one per operation), the held-out donor-nose part edit used in the paper figure, and one FF++ Deepfakes frame.

python explain_ours.py -> explain_ours.json, docs/meeting_20260930/assets/system_output.png
"""
import json
import textwrap
import sys
from pathlib import Path

import cv2
import matplotlib
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC")
for p in (HERE, B / "docs/paper_v2", B):
    sys.path.insert(0, str(p))
from train_ru3 import to_t2  # noqa: E402
from train_ru import crop  # noqa: E402
from train_ru_clip import load_clip  # noqa: E402
from occlusion_regions import region_masks  # noqa: E402
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402

CLS = ["real", "fake", "filter"]; OPS = ["eye", "contour", "tone", "texture"]
OP_TEXT = {"eye": "eyes enlarged", "contour": "face reshaped", "tone": "skin brightened", "texture": "skin smoothed"}
FACE = ["eyes", "nose", "mouth", "skin", "contour"]
AREA = 0.12
BOX = json.loads((HERE / "ffhq_boxes.json").read_text())
ALI = B / "FFHQ_ali_process"

EXAMPLES = [
    ("genuine (FF++)", B / "FaceForensics_protocol_frames/test/real/000__f0039.jpg", None, "real"),
    ("Alibaba: eye enlargement", ALI / "EyeEnlarging_90/17000/17024.png", BOX["17024"], "filter"),
    ("Alibaba: face lifting", ALI / "FaceLifting_90/17000/17024.png", BOX["17024"], "filter"),
    ("Alibaba: whitening", ALI / "Whitening_90/17000/17024.png", BOX["17024"], "filter"),
    ("Alibaba: smoothing", ALI / "Smoothing_90/17000/17024.png", BOX["17024"], "filter"),
    ("part-level forgery (nose)", B / "ffpp_partedit/test/donor/682__f0867__nose.jpg", None, "fake"),
    ("whole-face deepfake (FF++)", B / "FaceForensics_protocol_frames/test/Deepfakes/024_073__f0030.jpg", None, "fake"),
]


def explain(net, path, box):
    arr = crop(np.array(Image.open(path).convert("RGB")), box)
    x = to_t2(arr, 224, False, "clip")[None].cuda()
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        lo, pr, _q, ev = net(x)
    p = torch.softmax(lo.float(), 1)[0].cpu().numpy(); s = torch.sigmoid(pr.float())[0].cpu().numpy()
    e = torch.sigmoid(ev.float())[0, 0]
    up = F.interpolate(e[None, None], size=arr.shape[:2], mode="bilinear", align_corners=False)[0, 0].cpu().numpy()
    # rule B (eval_part_naming.py: right part in 97.7-99.0 % of held-out part edits): mean evidence inside each part
    parts = {}
    lm = get_landmarks(np.ascontiguousarray(arr))
    if lm is not None:
        M = region_masks(arr, np.asarray(lm, np.float32)[:, :2])
        parts = {k: round(float(up[M[k]].mean()) if M[k].any() else 0.0, 3) for k in FACE}
    lab = CLS[int(p.argmax())]; peak = float(up.max())
    top = max(parts, key=parts.get) if parts else None
    whole = bool(parts) and all(parts[k] >= 0.5 for k in ("eyes", "nose", "mouth"))
    named = ["whole face"] if whole else ([top] if top else [])
    ops = [o for j, o in enumerate(OPS) if s[j] >= 0.5]
    if lab == "real":
        text = "No manipulation detected."
    elif lab == "fake":
        text = ("Forgery detected; evidence across the whole face." if whole
                else (f"Forgery detected; evidence on the {top}." if top else "Forgery detected."))
    else:
        text = "Beautified, identity kept: " + (", ".join(OP_TEXT[o] for o in ops) if ops else "operation unclear") + "."
    out = {"image": str(path), "label": lab, "probabilities": {c: round(float(v), 3) for c, v in zip(CLS, p)},
           "operations": {o: round(float(s[j]), 3) for j, o in enumerate(OPS)},
           "evidence": {"peak": round(peak, 3), "mean_per_part": parts, "named_parts": named}, "explanation": text}
    return out, arr, up


def main():
    net = load_clip("clipe4_s20260929", head=True).cuda().eval()
    res, vis = [], []
    for name, path, box, truth in EXAMPLES:
        o, arr, up = explain(net, path, box); o["example"] = name; o["truth"] = truth; res.append(o); vis.append((arr, up))
        print(f"{name:30s} -> {o['label']:6s} {o['explanation']}", flush=True)
    (HERE / "explain_ours.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    fig_system(res, vis)


def fig_system(res, vis):
    col = {"real": "#2f7d32", "fake": "#B64342", "filter": "#8a6d00"}
    n = len(res); fig, axes = plt.subplots(2, n, figsize=(2.05 * n, 5.0), gridspec_kw={"height_ratios": [1, 1.02]})
    for i, (o, (arr, up)) in enumerate(zip(res, vis)):
        sq = cv2.resize(arr, (256, 256)); hm = cv2.resize(up, (256, 256))
        ax = axes[0, i]; ax.imshow(sq); ax.axis("off")
        ax.set_title(o["example"], fontsize=8.6, pad=4)
        ax = axes[1, i]; ax.imshow(sq)
        if o["label"] != "real":
            ax.imshow(hm, cmap="jet", alpha=0.45, vmin=0, vmax=1)
        ax.axis("off")
        ok = o["label"] == o["truth"]
        pr = o["probabilities"][o["label"]]
        ax.text(0.5, -0.08, f"{o['label']} {pr:.2f}" + ("" if ok else "   (wrong)"), transform=ax.transAxes, ha="center", va="top",
                fontsize=10, fontweight="bold", color=col[o["label"]])
        ops = o["operations"]
        ax.text(0.5, -0.24, f"eye {ops['eye']:.2f}  contour {ops['contour']:.2f}\ntone {ops['tone']:.2f}  texture {ops['texture']:.2f}",
                transform=ax.transAxes, ha="center", va="top", fontsize=7.4, color="#4d4d4d", linespacing=1.3)
        ax.text(0.5, -0.52, textwrap.fill(o["explanation"], 24), transform=ax.transAxes, ha="center", va="top", fontsize=8.4,
                color="#272727", style="italic", linespacing=1.25)
    fig.subplots_adjust(wspace=0.1, hspace=0.18, bottom=0.3)
    out = B / "docs/meeting_20260930/assets/system_output.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    for ext in ("pdf", "png"):   # supplement figure (replaces fig_output / fig_ru_output, which used older models and naming rule A)
        fig.savefig(B / f"docs/paper_v2/figs/fig_system_output.{ext}", dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig); print("->", out)


if __name__ == "__main__":
    main()
