"""Structured, verifiable explanation for the RU models: label, class probabilities, per-operation presence, blind quantity
estimates in physical units, and a template sentence; on Alibaba pairs the measured edit is shown next to the estimate.
No language model: every number in the sentence is a model output that can be checked against the pair.

python explain_ru.py --arch effb4 [--arm ru1|ru2]  -> explain_ru_<tag>.json, docs/paper_v2/figs/fig_ru_output.{pdf,png}
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image

HERE = Path(__file__).resolve().parent; BASE = Path(r"C:\My_Project\AIGC")
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(BASE / "docs/paper_v2"))
from train_ru import RUNet, ARCH, CKPT, to_t, crop  # noqa: E402
import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import make_figures as MF  # noqa: E402

CLS = ["real", "fake", "filter"]; OPS = ["eye", "jaw", "white", "smooth"]
NAME = {"eye": "eyes enlarged", "jaw": "face slimmed", "white": "skin brightened", "smooth": "skin smoothed"}


def units(q):
    """q = (eye_ratio-1, 1-jaw_ratio, dL/20, 1-hf_ratio) -> human units."""
    return {"eye": f"{100 * q[0]:+.1f}% eye width", "jaw": f"{-100 * q[1]:+.1f}% jaw width", "white": f"{20 * q[2]:+.1f} L*",
            "smooth": f"{-100 * q[3]:+.0f}% skin texture"}


def explain(model, path, box, size, thr=0.5):
    x = to_t(crop(np.array(Image.open(path).convert("RGB")), box), size, False)[None].cuda()
    with torch.no_grad():
        lo, pr, q = model(x)
    p = torch.softmax(lo.float(), 1)[0].cpu().numpy(); r = torch.sigmoid(pr.float())[0].cpu().numpy(); q = q.float()[0].cpu().numpy()
    lab = CLS[int(p.argmax())]; u = units(q)
    ops = [o for j, o in enumerate(OPS) if r[j] >= thr]
    if lab == "real":
        text = "No manipulation detected."
    elif lab == "fake":
        text = "Forgery detected (identity or content changed)."
    else:
        parts = [NAME[o] for o in ops] or ["retouched (operation unclear)"]
        text = "Beautification filter, identity preserved: " + "; ".join(parts) + "."
    return {"image": str(path), "label": lab, "probabilities": {c: round(float(v), 3) for c, v in zip(CLS, p)},
            "operations": {o: round(float(r[j]), 3) for j, o in enumerate(OPS)}, "quantities": u, "q_raw": [round(float(v), 4) for v in q],
            "explanation": text}


def measured(orig, ret):
    sys.path.insert(0, str(HERE)); from measure_pairs import measure
    m = measure(orig, ret)
    return None if m is None else units([m["eye_ratio"] - 1, 1 - m["jaw_ratio"], m["dL_skin"] / 20, 1 - m["hf_ratio"]])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--arch", default="effb4"); ap.add_argument("--arm", default="ru1")
    ap.add_argument("--seed", type=int, default=20260929); a = ap.parse_args()
    tag = f"{a.arch}_s{a.seed}" if a.arm == "ru1" else f"{a.arm}_{a.arch}_s{a.seed}"; size = ARCH[a.arch][1]
    model = RUNet(a.arch); model.load_state_dict(torch.load(CKPT / f"ru_{tag}.pth", map_location="cpu")); model = model.cuda().eval()
    boxes = json.loads((HERE / "ffhq_boxes.json").read_text())
    O = BASE / "ffhq_originals/Part2"; A = BASE / "FFHQ_ali_process"
    ex = [("17024", None), ("17024", "Smoothing_90"), ("17024", "EyeEnlarging_90"), ("17024", "Whitening_90"), ("17024", "FaceLifting_90")]
    out = []; tiles = []
    for stem, grp in ex:
        op = O / f"{stem}.png"
        path = op if grp is None else A / grp / f"{(int(stem) // 1000) * 1000}" / f"{stem}.png"
        if not path.is_file():
            continue
        J = explain(model, path, boxes[stem], size); J["alibaba_group"] = grp or "original"
        J["measured_on_pair"] = None if grp is None else measured(op, path)
        out.append(J); tiles.append((path, boxes[stem], J))
    ff = [l.split("\t") for l in (BASE / "results/research/ffpp_unified_20260925/ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    fk = [r[0] for r in ff if r[1] == "1"][40]
    J = explain(model, fk, None, size); J["alibaba_group"] = "FF++ forgery"; J["measured_on_pair"] = None; out.append(J); tiles.append((fk, None, J))
    (HERE / f"explain_ru_{tag}.json").write_text(json.dumps(out, indent=1))
    fig, axes = plt.subplots(len(tiles), 2, figsize=(7.0, 1.05 * len(tiles)), gridspec_kw={"width_ratios": [1, 5.2]})
    for i, (p, b, J) in enumerate(tiles):
        im = crop(np.array(Image.open(p).convert("RGB")), b); axes[i, 0].imshow(im); axes[i, 0].set_xticks([]); axes[i, 0].set_yticks([])
        axes[i, 0].set_ylabel(J["alibaba_group"].replace("_", " ").replace("EyeEnlarging", "eye enl.").replace("FaceLifting", "lifting")
                              .replace("Whitening", "whitening").replace("Smoothing", "smoothing"), fontsize=6, rotation=0, ha="right", va="center")
        pr = J["probabilities"]; ops = J["operations"]
        lines = [f'{J["label"].upper():6s}  p(real, fake, filter) = {pr["real"]:.2f}, {pr["fake"]:.2f}, {pr["filter"]:.2f}',
                 "operation p:  " + "   ".join(f"{k} {v:.2f}" for k, v in ops.items()),
                 "> " + J["explanation"]]
        axes[i, 1].text(0.0, 0.5, "\n".join(lines), fontsize=6.2, family="monospace", va="center", transform=axes[i, 1].transAxes, wrap=True)
        axes[i, 1].axis("off")
    fig.tight_layout(pad=0.3); MF.save(fig, "fig_ru_output"); print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
