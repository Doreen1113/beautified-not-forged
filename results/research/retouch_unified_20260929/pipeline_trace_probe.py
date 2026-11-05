"""Exploratory (PRE_DECLARED Addendum 5): does P(filter) respond to re-encoding alone?

Every Alibaba render differs from its original over the whole face (median |render - original| inside the hull is 3-5
8-bit levels even for eye enlargement, a local warp), so a service's processing leaves a trace besides the named edit.
Control on VALIDATION data only: the 816 untouched FFHQ originals held out from the two training services go through
no-op round trips (JPEG at several qualities, a 2x down/up resample, both) and through the two models unchanged otherwise.
If a round trip moves untouched photographs to filter, part of the filter decision is a re-encoding detector.

python pipeline_trace_probe.py [tag ...]  -> pipeline_trace_probe.json
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from train_ru import CKPT, read_manifest, crop  # noqa: E402
from train_ru3 import RUNet3, to_t2  # noqa: E402


def jpeg(im, q):
    ok, enc = cv2.imencode(".jpg", im[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, q]); return cv2.imdecode(enc, cv2.IMREAD_COLOR)[..., ::-1]


def resamp(im, f=2.0):
    h, w = im.shape[:2]
    return cv2.resize(cv2.resize(im, (int(w / f), int(h / f)), interpolation=cv2.INTER_AREA), (w, h), interpolation=cv2.INTER_CUBIC)


def apply(name, im):
    if name == "untouched":
        return im
    if name.startswith("jpeg"):
        return jpeg(im, int(name[4:]))
    if name == "resample2x":
        return resamp(im)
    return jpeg(resamp(im), 90)   # resample2x+jpeg90


COND = ["untouched", "jpeg95", "jpeg90", "jpeg75", "jpeg50", "resample2x", "resample2x+jpeg90"]


class DS(Dataset):
    """The round trip is applied to the full photograph, as a service would, before the face crop."""
    def __init__(self, rows, fn, size, norm):
        self.rows, self.fn, self.size, self.norm = rows, fn, size, norm

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        r = self.rows[i]; im = np.ascontiguousarray(apply(self.fn, np.array(Image.open(r["path"]).convert("RGB"))))
        return to_t2(crop(im, r["box"]), self.size, False, self.norm), i


@torch.no_grad()
def run(model, rows, fn, size, norm):
    P = np.zeros((len(rows), 3), np.float32)
    for x, i in DataLoader(DS(rows, fn, size, norm), batch_size=32, num_workers=6):
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lo = model(x.cuda())[0]
        P[i.numpy()] = torch.softmax(lo.float(), 1).cpu().numpy()
    return P


def load(tag):
    if tag.startswith("clip"):
        from train_ru_clip import load_clip
        return load_clip(tag, head=True).cuda().eval(), 224, "clip"
    m = RUNet3("effb4", head=True); m.load_state_dict(torch.load(CKPT / f"ru_{tag}.pth", map_location="cpu")); return m.cuda().eval(), 380, "half"


def main():
    tags = sys.argv[1:] or ["clipe4_s20260929", "ru4e_effb4_s20260929"]
    rows = [r for r in read_manifest(HERE / "manifest_val.tsv") if r["src"] == "ffhq_orig"]
    f = HERE / "pipeline_trace_probe.json"; out = json.loads(f.read_text()) if f.is_file() else {}
    for tag in tags:
        model, size, norm = load(tag); res = {}; base = None
        for name in COND:
            P = run(model, rows, name, size, norm); am = P.argmax(1)
            if base is None:
                base = P
            res[name] = {"real": round(100 * float((am == 0).mean()), 1), "fake": round(100 * float((am == 1).mean()), 1),
                         "filter": round(100 * float((am == 2).mean()), 1), "mean_p_filter": round(float(P[:, 2].mean()), 3),
                         "p_filter_above_untouched": round(100 * float((P[:, 2] > base[:, 2]).mean()), 1)}
            print(tag, name, res[name], flush=True)
        out[tag] = {"n": len(rows), **res}; del model; torch.cuda.empty_cache()
        f.write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
