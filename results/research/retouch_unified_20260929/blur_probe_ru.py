"""Blur probe for the paper's two models (clipe4 = Ours, ru4e = Ours-lite) on the SAME 300 FF++ test genuine frames and the
same four conditions as sbifix_20260927/blur_probe.py and cgd_20260927/blur_probe_cgd.py (rows[r1=='0'][::4][:300]).
Preprocessing = eval_ru.DS (to_t2 without crop box, since ffpp3_test frames are already face crops).
Reported: % of genuine frames with argmax = fake.

python blur_probe_ru.py -> blur_probe_ru.json
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from train_ru3 import RUNet3, to_t2  # noqa: E402
from train_ru_clip import load_clip  # noqa: E402

B = Path(r"C:\My_Project\AIGC"); CK = B / "checkpoints/research/retouch_unified_20260929"
rows = [l.split("\t") for l in (B / "results/research/ffpp_unified_20260925/ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:]]
ff = [np.array(Image.open(r[0]).convert("RGB")) for r in rows if r[1] == "0"][::4][:300]


def down(a, f):
    h, w = a.shape[:2]; s = cv2.resize(a, (max(8, int(w / f)), max(8, int(h / f))), interpolation=cv2.INTER_AREA)
    return cv2.resize(s, (w, h), interpolation=cv2.INTER_LINEAR)


conds = {"orig": ff, "down2": [down(a, 2) for a in ff], "blur1.5": [cv2.GaussianBlur(a, (0, 0), 1.5) for a in ff],
         "jpeg30": [cv2.imdecode(cv2.imencode(".jpg", a[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 30])[1], 1)[..., ::-1] for a in ff]}


def models():
    m = load_clip("clipe4_s20260929", head=True); yield "Ours (clipe4)", m, 224, "clip"
    del m; torch.cuda.empty_cache()
    m = RUNet3("effb4", head=True); m.load_state_dict(torch.load(CK / "ru_ru4e_effb4_s20260929.pth", map_location="cpu"))
    yield "Ours-lite (ru4e)", m, 380, "half"


out = {}
for name, net, size, norm in models():
    net = net.cuda().eval(); r = {}
    for k, ims in conds.items():
        P = []
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            for i in range(0, len(ims), 32):
                x = torch.stack([to_t2(np.ascontiguousarray(a), size, False, norm) for a in ims[i:i + 32]]).cuda()
                P.append(torch.softmax(net(x)[0].float(), 1).cpu())
        P = torch.cat(P).numpy(); r[k] = round(float((P.argmax(1) == 1).mean() * 100), 1)
    out[name] = r; print(name, r, flush=True)
(HERE / "blur_probe_ru.json").write_text(json.dumps(out, indent=1))
