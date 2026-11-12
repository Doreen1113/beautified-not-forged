"""Addendum 46 smoke check of the data path (no training): x_s differs from x, the main item stream is bit-identical with and
without --smooth-consistency, share of face-local vs whole-crop x_s per item role, and a montage for checking by eye that the
face-local hull sits on the face after the shared crop / resize.
python smoke_add46_data.py [N] -> smoke_add46_data.json, smoke_add46_montage.png"""
import json
import sys
from collections import Counter
from pathlib import Path

import cv2
import numpy as np
import torch

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from train_ru import read_manifest  # noqa: E402
from train_ru5 import RUData5  # noqa: E402
from train_ru3 import to_t2, CLIP_MEAN, CLIP_STD  # noqa: E402

N = int(sys.argv[1]) if len(sys.argv) > 1 else 150


class Rec(RUData5):
    def _smoothed_views(self, i, rgb, lm, st_post, sh0, items, separate, flip, return_np=False):
        out, forms = super()._smoothed_views(i, rgb, lm, st_post, sh0, items, separate, flip, return_np=True)
        self.last = (items, out, forms)
        real_s, filt_s, fake_s = out
        return torch.stack([to_t2(real_s, self.size, flip, self.norm), to_t2(fake_s, self.size, flip, self.norm), to_t2(filt_s, self.size, flip, self.norm)])


def main():
    rows = read_manifest(HERE / "manifest_train.tsv")
    kw = dict(head_res=16, norm="clip", grade=True, vendor_fake=True, sym_smooth=True)
    dc = Rec(rows, 224, 20260929, cons=True, **kw); d0 = RUData5(rows, 224, 20260929, **kw); dc.epoch = d0.epoch = 1
    rng = np.random.default_rng(0); idx = rng.choice(len(dc), N, replace=False)
    same, forms, diffs, tile = 0, {r: Counter() for r in ("real", "filt", "fake")}, {r: [] for r in ("real", "filt", "fake")}, []
    for k, i in enumerate(idx):
        a = dc[int(i)]; b = d0[int(i)]
        same += int(all(torch.equal(u, v) for u, v in zip(a[:9], b)))
        items, out, fm = dc.last
        for role, im, sm, f in zip(("real", "filt", "fake"), items, out, fm):
            forms[role][f] += 1; diffs[role].append(float(np.abs(im.astype(np.int16) - sm.astype(np.int16)).mean()))
        dt = (a[9] - a[0]).abs().mean(dim=(1, 2, 3))   # tensor-level difference, CLIP-normalised units
        assert (dt > 0).all(), (i, dt)
        if k < 6:   # x | x_s | |diff| x8 for the genuine item (face-local when landmarks were carried)
            im, sm = items[0], out[0]; dd = np.clip(np.abs(im.astype(np.int16) - sm.astype(np.int16)) * 8, 0, 255).astype(np.uint8)
            tile.append(np.concatenate([cv2.resize(z, (224, 224)) for z in (im, sm, dd)], 1))
    cv2.imwrite(str(HERE / "smoke_add46_montage.png"), cv2.cvtColor(np.concatenate(tile, 0), cv2.COLOR_RGB2BGR))
    res = {"n_items": N, "main_stream_identical": f"{same}/{N}", "x_s_forms": {r: dict(c) for r, c in forms.items()},
           "mean_abs_pixel_diff": {r: [round(float(np.mean(v)), 2), round(float(np.min(v)), 2), round(float(np.max(v)), 2)] for r, v in diffs.items()}}
    (HERE / "smoke_add46_data.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
