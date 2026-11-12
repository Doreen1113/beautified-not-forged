"""Addendum 70: a browser-size model trained with the recipe the capstone claims (arm W of Addendum 58).

Data and targets: RUData7 with p_ar = 0 (clipe5 recipe + FairFace train originals as genuine bases), factorised forged /
beautified heads, presence, quantities, evidence map; exactly the RU5 loss of train_ru7w.py.
Backbone, input size, normalisation, optimiser (SAM) and lr schedule: those of the current browser model ru4e_effb4
(train_ru3.py), so that the two browser candidates differ in the training recipe only.

The network keeps the RUNet3 layout (backbone, cls, pres, q, ev) with cls = Linear(d, 2) holding the forged / beautified
logits; its first output is log[(1-f)(1-b), f, (1-f)b], so softmax gives P(real), P(fake) = f, P(filter) as for every
other RU model. Every epoch is saved; the epoch is chosen afterwards on validation only (C2, Addendum 5).

python train_ru7w_small.py [--arch effb4] [--seed S] [--epochs 12] [--workers 12] [--max-steps N]
  -> checkpoints/.../ru_ru7we_<arch>_s<seed>_eNN.pth, train_ru_ru7we_<arch>_s<seed>.csv, meta_ru_ru7we_<arch>_s<seed>.json
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np
import timm
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import f1_score, roc_auc_score
from torch.utils.data import DataLoader

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from train_ru import UNI, CKPT, ARCH, BATCH, LR, RHO, SEED, remap, read_manifest, ValDS  # noqa: E402
from train_sbifix import SAM  # noqa: E402
from train_ru3 import mask_loss  # noqa: E402
from train_ru7w import RUData7  # noqa: E402


class RUNet5(nn.Module):
    """RUNet3 layout with factorised forged / beautified logits in `cls` (2 outputs)."""

    def __init__(self, arch, head=True):
        super().__init__()
        self.backbone = timm.create_model(ARCH[arch][0], pretrained=True, num_classes=0); d = self.backbone.num_features
        self.cls, self.pres, self.q = nn.Linear(d, 2), nn.Linear(d, 4), nn.Linear(d, 4)
        self.head = head; self.ev = nn.Conv2d(d, 1, 1) if head else None

    def forward(self, x):
        fm = self.backbone.forward_features(x); f = fm.mean((2, 3)); z = self.cls(f).float()
        lf, lb, nf, nb = F.logsigmoid(z[:, 0]), F.logsigmoid(z[:, 1]), F.logsigmoid(-z[:, 0]), F.logsigmoid(-z[:, 1])
        joint = torch.stack([nf + nb, lf, nf + lb], 1)
        return joint, self.pres(f), self.q(f), (self.ev(fm) if self.head else None), z


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", default="effb4", choices=list(ARCH)); ap.add_argument("--epochs", type=int, default=12)
    ap.add_argument("--workers", type=int, default=12); ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--seed", type=int, default=SEED); ap.add_argument("--wq", type=float, default=2.0); ap.add_argument("--wm", type=float, default=1.0)
    a = ap.parse_args()
    torch.manual_seed(a.seed); np.random.seed(a.seed); CKPT.mkdir(parents=True, exist_ok=True)
    name, size = ARCH[a.arch]; tag = f"ru7we_{a.arch}_s{a.seed}"
    model = RUNet5(a.arch)
    with torch.no_grad():
        hr = int(model.backbone.forward_features(torch.zeros(1, 3, size, size)).shape[-1])
    model = model.cuda().to(memory_format=torch.channels_last)
    rows = read_manifest(HERE / "manifest_train.tsv"); vrows = read_manifest(HERE / "manifest_val.tsv")
    ds = RUData7(rows, size, a.seed, head_res=hr, norm="half", p_ar=0.0)
    vf = [l.split("\t") for l in (UNI / "ffpp3_val.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    dl_vf = DataLoader(ValDS([dict(path=remap(r[0]), box=None, cls=int(r[1])) for r in vf], size), batch_size=64, num_workers=4)
    dl_vv = DataLoader(ValDS(vrows, size), batch_size=64, num_workers=4)
    print(f"[{tag}] bases {len(ds):,} (FairFace {sum(r['src'] == 'ffair' for r in ds.bases):,}) | single {len(ds.single):,} | parts {len(ds.parts):,} | "
          f"grid {hr} | params {sum(p.numel() for p in model.parameters()):,}", flush=True)
    opt = SAM(model.parameters(), RHO)
    steps_ep = len(ds) // BATCH; total = steps_ep * a.epochs; decay_from = int(total * 0.75)

    def loss_fn(out, pres, mpres, q, mq, m, mm, zb):   # the RU5 loss of train_ru7w.py (factorised, not binary, no consistency)
        _, pr, qq, ev, z = out
        l = F.binary_cross_entropy_with_logits(z, zb, reduction="none").sum(1).mean()
        lp = (F.binary_cross_entropy_with_logits(pr.float(), pres, reduction="none").mean(1) * mpres).sum() / mpres.sum().clamp(min=1)
        lq = ((qq.float() - q).abs().mean(1) * mq).sum() / mq.sum().clamp(min=1)
        lm = mask_loss(ev, m, mm)
        return l + lp + a.wq * lq + a.wm * lm, (float(l.detach()), float(lp.detach()), float(lq.detach()), float(lm.detach()))

    def evaluate(dl):
        P, S, T = [], [], []; model.eval()
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            for x, y in dl:
                pr = torch.softmax(model(x.cuda().to(memory_format=torch.channels_last))[0].float(), 1).cpu().numpy()
                P.extend(pr.argmax(1).tolist()); S.extend(pr[:, 1].tolist()); T.extend(y.tolist())
        return np.array(P), np.array(S), np.array(T)

    log, step = [], 0
    for ep in range(1, a.epochs + 1):
        ds.epoch = ep
        dl = DataLoader(ds, batch_size=BATCH, shuffle=True, num_workers=a.workers, pin_memory=True, drop_last=True, persistent_workers=False, prefetch_factor=3)
        model.train(); acc = np.zeros(5); n = 0; t0 = time.time()
        for batch in dl:
            lr = LR if step < decay_from else LR * (total - step) / max(total - decay_from, 1)
            for g in opt.base.param_groups:
                g["lr"] = lr
            x = batch[0].flatten(0, 1).cuda(non_blocking=True).to(memory_format=torch.channels_last)
            pres, mpres, q, mq, m, mm, zb = [t.flatten(0, 1).cuda() for t in batch[2:9]]
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss, parts = loss_fn(model(x), pres, mpres, q, mq, m, mm, zb)
            loss.backward(); opt.first(); opt.base.zero_grad()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss_fn(model(x), pres, mpres, q, mq, m, mm, zb)[0].backward()
            opt.second(); opt.base.zero_grad()
            acc += np.array([float(loss.detach())] + list(parts)); n += 1; step += 1
            if step % 200 == 0 or (a.max_steps and step % 20 == 0):
                print(f"  step {step}/{total} loss {acc[0] / n:.4f} (fz {acc[1] / n:.3f} pres {acc[2] / n:.3f} q {acc[3] / n:.3f} mask {acc[4] / n:.3f}) "
                      f"{(time.time() - t0) / n:.3f}s/it mem {torch.cuda.max_memory_allocated() / 2 ** 30:.1f} GiB", flush=True)
            if a.max_steps and step >= a.max_steps:
                print(f"smoke test ok: {step} steps, {(time.time() - t0) / n:.3f}s/it, predicted {(time.time() - t0) / n * total / 3600:.1f} h for {a.epochs} epochs", flush=True)
                return
        P, S, T = evaluate(dl_vf); mk = np.isin(T, [0, 1]); f1 = f1_score(T, P, average="macro"); auc = roc_auc_score((T[mk] == 1).astype(int), S[mk])
        Pv, _, Tv = evaluate(dl_vv); orig_real = float((Pv[Tv == 0] == 0).mean() * 100); filt_rec = float((Pv[Tv == 2] == 2).mean() * 100)
        log.append(dict(epoch=ep, loss=acc[0] / n, ffpp_val_f1=f1, ffpp_val_auc=auc, vendor_val_orig_real=orig_real, vendor_val_filter_recall=filt_rec, minutes=(time.time() - t0) / 60))
        print(f"[{tag}][{ep:02d}/{a.epochs}] loss {acc[0] / n:.4f} ffppF1 {f1:.4f} AUC {auc:.4f} orig->real {orig_real:.1f}% vendor filter recall {filt_rec:.1f}% "
              f"({(time.time() - t0) / 60:.1f} min)", flush=True)
        torch.save(model.state_dict(), CKPT / f"ru_{tag}_e{ep:02d}.pth")
        with open(HERE / f"train_ru_{tag}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(log[0])); w.writeheader(); w.writerows(log)
    (HERE / f"meta_ru_{tag}.json").write_text(json.dumps({"addendum": 70, "arm": "ru7we", "arch": a.arch, "recipe": "W (Addendum 58: RUData7 p_ar=0)",
                                                         "optimiser": "SAM (train_ru3)", "epochs": a.epochs, "seed": a.seed, "grid": hr}, indent=1))
    print(f"[{tag}] DONE", flush=True)


if __name__ == "__main__":
    main()
