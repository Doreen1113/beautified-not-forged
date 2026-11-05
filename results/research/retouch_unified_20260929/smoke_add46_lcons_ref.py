"""Addendum 46 smoke reference: L_cons = mean (z_f(x) - z_f(x_s))^2 on Addendum 46 training items (x, x_s exactly as
train_ru5 builds them, epoch 1) for trained models WITHOUT the consistency term, to give the smoke-run value a scale.
python smoke_add46_lcons_ref.py tag ... -> prints per tag L_cons, and the logit spread (sd of z_f over the same items)."""
import sys
from pathlib import Path

import numpy as np
import torch

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from train_ru import read_manifest  # noqa: E402
from train_ru5 import RUData5  # noqa: E402
from train_ru_clip import load_clip  # noqa: E402

N = 96
rows = read_manifest(HERE / "manifest_train.tsv")
ds = RUData5(rows, 224, 20260929, head_res=16, norm="clip", grade=True, vendor_fake=True, sym_smooth=True, cons=True); ds.epoch = 1
idx = np.random.default_rng(1).choice(len(ds), N, replace=False)
items = [ds[int(i)] for i in idx]
X = torch.cat([it[0] for it in items]); XS = torch.cat([it[9] for it in items])
for tag in sys.argv[1:]:
    m = load_clip(tag, head=True).cuda().eval(); z, zs = [], []
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        for k in range(0, len(X), 48):
            z.append(m(X[k:k + 48].cuda())[4][:, 0].float().cpu()); zs.append(m(XS[k:k + 48].cuda())[4][:, 0].float().cpu())
    z, zs = torch.cat(z), torch.cat(zs)
    print(f"{tag}: L_cons {float(((z - zs) ** 2).mean()):.4f} | sd(z_f) {float(z.std()):.3f} | items {len(z)}", flush=True)
    del m; torch.cuda.empty_cache()
