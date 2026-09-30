"""Why is flip_pred low? Compare restoration flip rates for: hard GT mask (compositing hull), diff mask |x-x0|>6 (true edit
footprint), diff mask dilated, predicted region area-matched to the diff mask, and full restoration. 600 items per mechanism."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from eval_cgd_explain import TF, SIZE, load_items, region_from_map  # noqa: E402
from train_cgd import CGDNet  # noqa: E402

BASE = Path(r"C:\My_Project\AIGC")


def main():
    net = CGDNet(head=True); net.load_state_dict(torch.load(BASE / "checkpoints/research/cgd_20260927/cgd_CGD_s20260928.pth", map_location="cpu"))
    net = net.cuda().eval()
    R = {}
    for mech in ("donor", "sd"):
        items = load_items([mech])[::6][:600]
        acc = {k: [] for k in ("gt_hard", "gt_diff", "gt_diff_dil", "pred_diffarea", "pred_diffarea_dil", "full", "area_hard", "area_diff", "diff_outside_hard")}
        n = 0
        for it in items:
            im = Image.open(it["x"]).convert("RGB"); im0 = Image.open(it["x0"]).convert("RGB").resize(im.size)
            x = TF(im)[None].cuda(); x0 = TF(im0)[None].cuda()
            with torch.no_grad():
                lo, ev = net(x)
            if lo.argmax().item() != 1:
                continue
            n += 1
            hard = torch.from_numpy(cv2.resize(np.load(it["m"])["m"].astype(np.float32), (SIZE, SIZE), interpolation=cv2.INTER_AREA) > 0.5).float().cuda()
            a, a0 = np.array(im).astype(np.float32), np.array(im0).astype(np.float32)
            diff = torch.from_numpy(cv2.resize((np.abs(a - a0).max(2) > 6).astype(np.float32), (SIZE, SIZE), interpolation=cv2.INTER_AREA) > 0.5).float().cuda()
            k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
            diff_dil = torch.from_numpy(cv2.dilate(diff.cpu().numpy().astype(np.uint8), k)).float().cuda()
            e = torch.sigmoid(ev[0, 0]).float()
            pred = region_from_map(e, diff.mean().item())
            pred_dil = torch.from_numpy(cv2.dilate(pred.cpu().numpy().astype(np.uint8), k)).float().cuda()

            def flips(mask):
                with torch.no_grad():
                    return net((1 - mask[None, None]) * x + mask[None, None] * x0)[0].argmax().item() != 1
            acc["gt_hard"].append(flips(hard)); acc["gt_diff"].append(flips(diff)); acc["gt_diff_dil"].append(flips(diff_dil))
            acc["pred_diffarea"].append(flips(pred)); acc["pred_diffarea_dil"].append(flips(pred_dil)); acc["full"].append(flips(torch.ones_like(hard)))
            acc["area_hard"].append(hard.mean().item()); acc["area_diff"].append(diff.mean().item())
            acc["diff_outside_hard"].append(((diff > 0) & (hard == 0)).float().sum().item() / max(1.0, diff.sum().item()))
        R[mech] = {"n": n, **{k: float(np.mean(v)) for k, v in acc.items()}}
        print(mech, json.dumps({k: round(v, 3) for k, v in R[mech].items()}), flush=True)
    json.dump(R, open(HERE / "diag_flip_ceiling.json", "w"), indent=1)


if __name__ == "__main__":
    main()
