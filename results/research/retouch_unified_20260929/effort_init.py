"""Load the released Effort checkpoint (effort_clip_L14_trainOn_FaceForensic.pth) into RUCLIP5(tune="effort") (Addendum 30).
Key map: module.backbone.<x> -> vit.vision_model.<x> (or vit.<x> under transformers 5); the two-way head becomes the forged logit
fz[0] = head[1] - head[0] (softmax P(fake) == sigmoid of that difference); the beautified logit fz[1] stays at its random init."""
import os
from pathlib import Path
import torch
CKPT = Path(os.environ.get("AIGC_BASE", r"C:\My_Project\AIGC")) / "external_baselines/Effort/DeepfakeBench/training/weights/effort_clip_L14_trainOn_FaceForensic.pth"


def load_released_effort(model, path=CKPT):
    sd = torch.load(path, map_location="cpu"); sd = sd.get("state_dict", sd)
    own = model.state_dict(); pre = "vit.vision_model." if any(k.startswith("vit.vision_model.") for k in own) else "vit."
    new = {}
    for k, v in sd.items():
        if k.startswith("module.backbone."):
            new[pre + k[len("module.backbone."):]] = v
    hw, hb = sd["module.head.weight"], sd["module.head.bias"]
    fzw = own["fz.weight"].clone(); fzb = own["fz.bias"].clone(); fzw[0] = hw[1] - hw[0]; fzb[0] = hb[1] - hb[0]; new["fz.weight"] = fzw; new["fz.bias"] = fzb
    missing, unexpected = model.load_state_dict(new, strict=False)
    assert not unexpected, unexpected[:5]
    bad = [k for k in missing if "vit." in k and not any(t in k for t in ("U_r", "V_r", "S_r"))]
    assert not bad, bad[:5]
    return len(new)
