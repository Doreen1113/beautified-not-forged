"""How often does the explanation sentence name the right facial part? Held-out part-level forgeries (donor / SD / SDXL,
every 4th item, true part from the file name: eyes / nose / mouth), main model clipe4, detected items only.

Rule A (used so far): top 12% of the evidence map, share of that region falling on each landmark part, top part.
Rule B: mean evidence inside each landmark part (eyes, nose, mouth, skin, contour), top part.
Decision fixed before running: switch the sentence to rule B only if it beats rule A on all three mechanisms.

python eval_part_naming.py -> part_naming.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC")
for p in (HERE, B / "docs/paper_v2", B):
    sys.path.insert(0, str(p))
from train_ru3 import to_t2  # noqa: E402
from train_ru_clip import load_clip  # noqa: E402
from occlusion_regions import region_masks  # noqa: E402
from filters_v2.scale_normalized_filters import get_landmarks  # noqa: E402

FACE = ["eyes", "nose", "mouth", "skin", "contour"]


def main():
    net = load_clip("clipe4_s20260929", head=True).cuda().eval()
    out = {}
    for mech in ("donor", "sd", "sdxl"):
        files = sorted((B / "ffpp_partedit/test" / mech).glob("*.jpg"))[::4]
        n = det = nolm = 0; hitA = hitB = 0; conf = {}
        for i in range(0, len(files), 32):
            batch = files[i:i + 32]; arrs = [np.array(Image.open(f).convert("RGB")) for f in batch]
            x = torch.stack([to_t2(a, 224, False, "clip") for a in arrs]).cuda()
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
                lo, _pr, _q, ev = net(x)
            lab = lo.float().argmax(1).cpu().numpy(); ev = torch.sigmoid(ev.float())
            for f, a, l, e in zip(batch, arrs, lab, ev):
                n += 1
                if l != 1:
                    continue
                lm = get_landmarks(np.ascontiguousarray(a))
                if lm is None:
                    nolm += 1; continue
                det += 1; truth = f.stem.split("__")[-1]
                up = F.interpolate(e[None], size=a.shape[:2], mode="bilinear", align_corners=False)[0, 0].cpu().numpy()
                M = region_masks(a, np.asarray(lm, np.float32)[:, :2])
                reg = up >= np.quantile(up, 0.88)
                shareA = {k: (reg & M[k]).sum() / max(1, reg.sum()) for k in FACE}
                densB = {k: float(up[M[k]].mean()) if M[k].any() else 0.0 for k in FACE}
                pa = max(shareA, key=shareA.get); pb = max(densB, key=densB.get)
                hitA += pa == truth; hitB += pb == truth; conf[f"{truth}->{pb}"] = conf.get(f"{truth}->{pb}", 0) + 1
        out[mech] = {"n": n, "detected_with_landmarks": det, "no_landmarks": nolm,
                     "ruleA_top1": round(100 * hitA / max(1, det), 1), "ruleB_top1": round(100 * hitB / max(1, det), 1),
                     "ruleB_confusion": dict(sorted(conf.items()))}
        print(mech, json.dumps(out[mech]), flush=True)
    out["decision"] = "rule B" if all(out[m]["ruleB_top1"] > out[m]["ruleA_top1"] for m in ("donor", "sd", "sdxl")) else "rule A"
    (HERE / "part_naming.json").write_text(json.dumps(out, indent=1)); print("decision:", out["decision"])


if __name__ == "__main__":
    main()
