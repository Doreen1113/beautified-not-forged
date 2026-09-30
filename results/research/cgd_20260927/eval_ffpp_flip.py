"""Where the consistency loss should matter: observed FF++ test forgeries (no exact mask). Counterfactual = the target
video's genuine frame at the same index (approximate alignment; resized to the fake crop). Footprint = |x-x0|>thr dilated,
which for real forgeries is a loose proxy — so flip rates are reported against the same-footprint ceiling and controls.

python eval_ffpp_flip.py --arm MASK [--n 1500] -> ffpp_flip_<ARM>.json
"""
import argparse
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from eval_cgd_explain import CAM, TF, SIZE, dilate_t, footprint_gt, region_from_map, centre_prior  # noqa: E402
from train_cgd import CGDNet, remap  # noqa: E402

BASE = Path(r"C:\My_Project\AIGC")
UNI = BASE / "results/research/ffpp_unified_20260925"
TEST_REAL = BASE / "FaceForensics_protocol_frames/test/real"


def items(n, seed=0):
    rows = [l.split("\t") for l in (UNI / "ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    out = []
    for p, y, v, src in rows:
        if y != "1":
            continue
        b = os.path.basename(p); vid, fr = b.split("_")[0], b.split("__")[1].replace(".jpg", "")
        q = TEST_REAL / f"{vid}__{fr}.jpg"
        if q.is_file():
            out.append({"x": remap(p), "x0": str(q), "method": src.split(":")[0]})
    rng = np.random.default_rng(seed); rng.shuffle(out)
    return out[:n]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--arm", required=True); ap.add_argument("--n", type=int, default=1500); ap.add_argument("--seed", type=int, default=20260928); ap.add_argument("--area", type=float, default=0.0, help="fixed region area fraction (0 = footprint area)")
    a = ap.parse_args()
    net = CGDNet(head=a.arm != "HYBPE"); net.load_state_dict(torch.load(BASE / f"checkpoints/research/cgd_20260927/cgd_{a.arm}_s{a.seed}.pth", map_location="cpu"))
    net = net.cuda().eval(); cam = CAM(net)
    methods = ["evidence"] if net.head else ["scorecam"]
    rng = np.random.default_rng(0)
    acc = {m: {"flip_pred": [], "flip_comp": [], "flip_rand": [], "flip_centre": [], "iou7_vs_footprint": []} for m in methods}
    ceil, per_method = [], {}
    n_det = 0; its = items(a.n)
    for it in its:
        im = Image.open(it["x"]).convert("RGB"); im0 = Image.open(it["x0"]).convert("RGB").resize(im.size)
        x, x0 = TF(im)[None].cuda(), TF(im0)[None].cuda()
        with torch.no_grad():
            lo, ev = net(x)
        if lo.argmax().item() != 1:
            continue
        n_det += 1
        gt = footprint_gt(im, im0); area = a.area if a.area > 0 else float(np.clip(gt.mean().item(), 0.05, 0.6))
        with torch.no_grad():
            c = net((1 - gt[None, None]) * x + gt[None, None] * x0)[0].argmax().item() != 1
        ceil.append(c); per_method.setdefault(it["method"], []).append(c)
        for m in methods:
            e = torch.sigmoid(ev[0, 0]).float() if m == "evidence" else cam.scorecam(x, 1)
            reg = dilate_t(region_from_map(e, area))
            s = int(np.sqrt(area) * SIZE); yy, xx = rng.integers(0, SIZE - s + 1, 2)
            rnd = torch.zeros(SIZE, SIZE, device="cuda"); rnd[yy:yy + s, xx:xx + s] = 1
            with torch.no_grad():
                def dec(mask):
                    return net((1 - mask[None, None]) * x + mask[None, None] * x0)[0].argmax().item() != 1
                acc[m]["flip_pred"].append(dec(reg)); acc[m]["flip_comp"].append(dec(1 - reg))
                acc[m]["flip_rand"].append(dec(dilate_t(rnd))); acc[m]["flip_centre"].append(dec(dilate_t(centre_prior(area))))
                from eval_cgd_explain import iou7
                acc[m]["iou7_vs_footprint"].append(iou7(reg, gt))
    R = {"n_items": len(its), "n_detected": n_det, "flip_ceiling_footprint": float(np.mean(ceil)),
         "ceiling_per_method": {k: float(np.mean(v)) for k, v in per_method.items()},
         **{m: {k: float(np.mean(v)) for k, v in d.items()} for m, d in acc.items()}}
    print(json.dumps(R), flush=True)
    sfx = "_a%02d" % int(a.area * 100) if a.area else ""
    json.dump(R, open(HERE / f"ffpp_flip_{a.arm}_s{a.seed}{sfx}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
