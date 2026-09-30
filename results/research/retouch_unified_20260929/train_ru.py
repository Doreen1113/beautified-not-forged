"""RU: unified real / fake / filter detector with operation-presence and verifiable-quantity heads (PRE_DECLARED §2).

Every step draws BATCH base photographs (FF++ train reals, FFHQ Part7 originals) and builds a triplet per photograph:
  real   = the photograph
  filter = synthetic single op with continuous strength on the photograph (targets analytic, calibrated) | vendor composite
           (Tencent / Megvii, measured targets) | observed FF++ filter frame
  fake   = faithful self-blend of the photograph | observed FF++ forgery; beautified on top with p = 0.5
All items get the same resolution randomisation and (p = 0.5) the same symmetric degradation (HYB-D lesson).

python train_ru.py --arch effb4|repvit [--epochs 12] [--workers 12] [--max-steps N] [--seed S]
  -> checkpoints/research/retouch_unified_20260929/ru_<arch>_s<seed>.pth, train_ru_<arch>_s<seed>.{csv,log}, meta_*.json
"""
import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import timm
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from sklearn.metrics import f1_score, roc_auc_score
from torch.utils.data import DataLoader, Dataset

BASE = Path(os.environ.get("AIGC_BASE", r"C:\My_Project\AIGC"))
HERE = Path(__file__).resolve().parent
UNI = BASE / "results/research/ffpp_unified_20260925"
FASB = BASE / "results/research/fasb_20260926"
SBIFIX = BASE / "results/research/sbifix_20260927"
CKPT = BASE / "checkpoints/research/retouch_unified_20260929"
for p in (FASB, SBIFIX, BASE, HERE):
    sys.path.insert(0, str(p))
from fasb import beautify  # noqa: E402   scripted / pilgram beautification (FF++ line)
from sbi_faithful import self_blend, shared_post, jitter_one  # noqa: E402
from train_sbifix import sym_degrade, SAM  # noqa: E402
from ops import random_op, random_op_v2, OPS  # noqa: E402

ARCH = {"effb4": ("tf_efficientnet_b4.ap_in1k", 380), "repvit": ("repvit_m0_9.dist_300e_in1k", 224)}
BATCH, LR, RHO, SEED = 16, 1e-3, 0.05, 20260929
MEAN = STD = (0.5, 0.5, 0.5)


def remap(p):
    return p if os.name == "nt" else p.replace("C:\\My_Project\\AIGC", str(BASE)).replace("\\", "/")


def to_t(rgb, size, flip):
    im = Image.fromarray(rgb).resize((size, size), Image.BILINEAR)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    x = torch.from_numpy(np.asarray(im, np.float32) / 255.0).permute(2, 0, 1)
    return (x - 0.5) / 0.5


def res_rand(rgb, rng, p=0.5, lo=160, hi=512):
    """Resolution-shortcut control: with p, downscale the crop to a random long side in [lo, hi] (all classes alike)."""
    h, w = rgb.shape[:2]
    if rng.random() >= p or max(h, w) <= lo:
        return rgb
    s = int(rng.integers(lo, min(hi, max(h, w)) + 1)); f = s / max(h, w)
    return cv2.resize(rgb, (max(8, int(w * f)), max(8, int(h * f))), interpolation=cv2.INTER_AREA)


CAP = 512


def cap(rgb, lm=None):
    """Long side <= CAP (Tencent renders are 512 natively; FFHQ crops ~650): cheaper ops, one resolution regime."""
    h, w = rgb.shape[:2]; f = CAP / max(h, w)
    if f >= 1:
        return rgb, lm
    out = cv2.resize(rgb, (max(8, int(w * f)), max(8, int(h * f))), interpolation=cv2.INTER_AREA)
    return out, (None if lm is None else lm * f)


def crop(rgb, box):
    if box is None:
        return rgb
    x0, y0, x1, y1 = box; return np.ascontiguousarray(rgb[y0:y1, x0:x1])


def parse(v):
    return None if v == "-" else np.array([float(x) for x in v.split()], np.float32)


def read_manifest(f):
    rows = []
    for l in Path(f).read_text(encoding="utf-8").splitlines()[1:]:
        if not l.strip():
            continue
        p, c, s, b, pr, q, st = l.split("\t")
        rows.append(dict(path=remap(p), cls=int(c), src=s, box=None if b == "-" else [int(x) for x in b.split()], pres=parse(pr), q=parse(q), stem=st))
    return rows


class RUData(Dataset):
    def __init__(self, rows, size, seed, ffhq_repeat=3, arm="ru1"):
        self.size, self.seed, self.epoch, self.arm = size, seed, 0, arm
        z = np.load(FASB / "landmarks_train.npz"); self.lm_ffpp = {k: z[k] for k in z.files}
        zf = np.load(HERE / "ffhq_landmarks.npz"); self.lm_ffhq = {k: zf[k] for k in zf.files}
        self.ffpp_root = BASE / "FaceForensics_protocol_frames_dense/train/real"
        self.bases = [r for r in rows if r["src"] == "ffpp_real" and r["stem"] in self.lm_ffpp] + \
                     [r for r in rows if r["src"] == "ffhq_orig"] * ffhq_repeat
        self.vendor = [r for r in rows if r["src"] in ("tencent", "megvii")]
        self.single = [r for r in rows if r["src"] == "vendor_single"]
        self.obs_filt = [r for r in rows if r["src"] == "ffpp_filter"]
        self.obs_fake = [r for r in rows if r["src"] == "ffpp_fake"]

    def __len__(self):
        return len(self.bases)

    def _load(self, r):
        rgb = np.array(Image.open(r["path"]).convert("RGB")); return cap(crop(rgb, r["box"]))[0]

    def _base(self, r):
        if r["src"] == "ffpp_real":
            return np.array(Image.open(self.ffpp_root / f"{r['stem']}.jpg").convert("RGB")), self.lm_ffpp[r["stem"]].copy()
        rgb = np.array(Image.open(r["path"]).convert("RGB")); rgb = crop(rgb, r["box"])
        lm = self.lm_ffhq[r["stem"]].copy(); lm[:, 0] -= r["box"][0]; lm[:, 1] -= r["box"][1]
        rgb, lm = cap(rgb, lm)
        return rgb, lm

    def __getitem__(self, i):
        r = self.bases[i]
        rng = np.random.default_rng((self.seed * 1000003 + self.epoch * 100003 + i) % (2 ** 63))
        rgb, lm = self._base(r)
        # ---- filter item
        u = rng.random(); filt_pres = np.zeros(4, np.float32); filt_q = np.zeros(4, np.float32); mq = mp = 1.0; sep = False
        if self.arm == "ru2":   # Addendum 1: synthetic v2 0.30 | vendor single 0.30 | vendor composite 0.15 | observed 0.25
            cut = (0.30, 0.60, 0.75)
        else:
            cut = (0.40, 0.40, 0.70)
        if u < cut[0]:
            filt, filt_pres, filt_q, _ = (random_op_v2 if self.arm == "ru2" else random_op)(rgb, lm, rng)
        elif u < cut[1]:
            v = self.single[int(rng.integers(0, len(self.single)))]; filt = self._load(v); filt_pres = v["pres"]; filt_q = v["q"]; sep = True
        elif u < cut[2]:
            v = self.vendor[int(rng.integers(0, len(self.vendor)))]; filt = self._load(v); filt_pres = v["pres"]; sep = True
            if v["q"] is None:
                mq = 0.0
            else:
                filt_q = v["q"]
        else:
            o = self.obs_filt[int(rng.integers(0, len(self.obs_filt)))]; filt = np.array(Image.open(o["path"]).convert("RGB")); sep = True
            filt_pres = o["pres"]; mq = 0.0
        # ---- fake item
        if rng.random() < 0.5:
            fake = None
            for _ in range(4):
                fake = self_blend(rgb, lm, rng)
                if fake is not None:
                    break
            if fake is None:
                fake = rgb.copy()
            fsep = False
        else:
            o = self.obs_fake[int(rng.integers(0, len(self.obs_fake)))]; fake = np.array(Image.open(o["path"]).convert("RGB")); fsep = True
        if rng.random() < 0.5:
            op_fn = random_op_v2 if self.arm == "ru2" else random_op
            fake = beautify(fake, rng) if rng.random() < 0.5 else op_fn(fake, lm, rng)[0] if not fsep else beautify(fake, rng)
        # ---- shared / separate post, resolution and degradation
        real = rgb
        if sep:
            filt = jitter_one(filt, rng)
        if fsep:
            fake = jitter_one(fake, rng)
        items = shared_post([real] + ([] if sep else [filt]) + ([] if fsep else [fake]), rng)
        real = items[0]; k = 1
        if not sep:
            filt = items[k]; k += 1
        if not fsep:
            fake = items[k]
        real, filt, fake = [res_rand(x, rng) for x in (real, filt, fake)]
        real, filt, fake = sym_degrade([real, filt, fake], rng)
        flip = bool(rng.random() < 0.5)
        x = torch.stack([to_t(real, self.size, flip), to_t(fake, self.size, flip), to_t(filt, self.size, flip)])
        y = torch.tensor([0, 1, 2])
        pres = torch.tensor(np.stack([np.zeros(4, np.float32), np.zeros(4, np.float32), filt_pres]))
        mpres = torch.tensor([1.0, 0.0, mp])
        q = torch.tensor(np.stack([np.zeros(4, np.float32), np.zeros(4, np.float32), filt_q]))
        mq_t = torch.tensor([1.0, 0.0, mq])
        return x, y, pres, mpres, q, mq_t


class ValDS(Dataset):
    def __init__(self, rows, size):
        self.rows, self.size = rows, size

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        r = self.rows[i]; rgb = np.array(Image.open(r["path"]).convert("RGB")); rgb = cap(crop(rgb, r["box"]))[0]
        return to_t(rgb, self.size, False), r["cls"]


class RUNet(nn.Module):
    def __init__(self, arch):
        super().__init__()
        self.backbone = timm.create_model(ARCH[arch][0], pretrained=True, num_classes=0)
        d = self.backbone.num_features
        self.cls = nn.Linear(d, 3); self.pres = nn.Linear(d, 4); self.q = nn.Linear(d, 4)

    def forward(self, x):
        f = self.backbone(x)
        return self.cls(f), self.pres(f), self.q(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", default="effb4", choices=list(ARCH)); ap.add_argument("--epochs", type=int, default=12)
    ap.add_argument("--workers", type=int, default=12); ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--seed", type=int, default=SEED); ap.add_argument("--wq", type=float, default=2.0)
    ap.add_argument("--arm", default="ru1", choices=["ru1", "ru2"])
    a = ap.parse_args()
    torch.manual_seed(a.seed); np.random.seed(a.seed); CKPT.mkdir(parents=True, exist_ok=True)
    name, size = ARCH[a.arch]; tag = (f"{a.arch}_s{a.seed}" if a.arm == "ru1" else f"{a.arm}_{a.arch}_s{a.seed}")
    rows = read_manifest(HERE / "manifest_train.tsv"); vrows = read_manifest(HERE / "manifest_val.tsv")
    ds = RUData(rows, size, a.seed, arm=a.arm)
    vf = [l.split("\t") for l in (UNI / "ffpp3_val.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    val_ffpp = [dict(path=remap(r[0]), box=None, cls=int(r[1])) for r in vf]
    dl_vf = DataLoader(ValDS(val_ffpp, size), batch_size=64, num_workers=4)
    dl_vv = DataLoader(ValDS(vrows, size), batch_size=64, num_workers=4)
    print(f"[RU {a.arch}] bases {len(ds):,} (ffhq x3) | vendor {len(ds.vendor):,} | obs filter {len(ds.obs_filt):,} fake {len(ds.obs_fake):,} | "
          f"val ffpp {len(val_ffpp):,} vendor-val {len(vrows):,}", flush=True)
    model = RUNet(a.arch).cuda().to(memory_format=torch.channels_last)
    opt = SAM(model.parameters(), RHO)
    steps_ep = len(ds) // BATCH; total = steps_ep * a.epochs; decay_from = int(total * 0.75)
    print(f"steps/epoch {steps_ep}, total {total}, params {sum(p.numel() for p in model.parameters()):,}", flush=True)

    def loss_fn(out, y, pres, mpres, q, mq):
        lo, pr, qq = out
        l = F.cross_entropy(lo.float(), y)
        lp = (F.binary_cross_entropy_with_logits(pr.float(), pres, reduction="none").mean(1) * mpres).sum() / mpres.sum().clamp(min=1)
        lq = ((qq.float() - q).abs().mean(1) * mq).sum() / mq.sum().clamp(min=1)
        return l + lp + a.wq * lq, (float(l.detach()), float(lp.detach()), float(lq.detach()))

    def evaluate(dl):
        P, S, T = [], [], []
        model.eval()
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            for x, y in dl:
                pr = torch.softmax(model(x.cuda().to(memory_format=torch.channels_last))[0].float(), 1).cpu().numpy()
                P.extend(pr.argmax(1).tolist()); S.extend(pr[:, 1].tolist()); T.extend(y.tolist())
        return np.array(P), np.array(S), np.array(T)

    best, log, step, out = -1.0, [], 0, CKPT / f"ru_{tag}.pth"
    for ep in range(1, a.epochs + 1):
        ds.epoch = ep
        dl = DataLoader(ds, batch_size=BATCH, shuffle=True, num_workers=a.workers, pin_memory=True, drop_last=True,
                        persistent_workers=False, prefetch_factor=3)
        model.train(); acc = np.zeros(4); n = 0; t0 = time.time()
        for x, y, pres, mpres, q, mq in dl:
            lr = LR if step < decay_from else LR * (total - step) / max(total - decay_from, 1)
            for g in opt.base.param_groups:
                g["lr"] = lr
            x = x.flatten(0, 1).cuda(non_blocking=True).to(memory_format=torch.channels_last)
            y, pres, mpres, q, mq = [t.flatten(0, 1).cuda() for t in (y, pres, mpres, q, mq)]
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss, parts = loss_fn(model(x), y, pres, mpres, q, mq)
            loss.backward(); opt.first(); opt.base.zero_grad()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss_fn(model(x), y, pres, mpres, q, mq)[0].backward()
            opt.second(); opt.base.zero_grad()
            acc += np.array([float(loss)] + list(parts)); n += 1; step += 1
            if step % 200 == 0:
                print(f"  step {step}/{total} loss {acc[0] / n:.4f} (ce {acc[1] / n:.3f} pres {acc[2] / n:.3f} q {acc[3] / n:.3f}) "
                      f"{(time.time() - t0) / n:.3f}s/it", flush=True)
            if a.max_steps and step >= a.max_steps:
                print(f"smoke test ok: {step} steps, {(time.time() - t0) / n:.3f}s/it", flush=True); return
        P, S, T = evaluate(dl_vf); m = np.isin(T, [0, 1])
        f1 = f1_score(T, P, average="macro"); auc = roc_auc_score((T[m] == 1).astype(int), S[m])
        Pv, _, Tv = evaluate(dl_vv); f1v = f1_score((Tv == 2).astype(int), (Pv == 2).astype(int))   # vendor-val: retouched vs original
        fake_v = float((Pv == 1).mean() * 100)
        crit = 0.5 * (f1 + f1v)
        log.append(dict(epoch=ep, loss=acc[0] / n, ffpp_val_f1=f1, ffpp_val_auc=auc, vendor_val_f1=f1v, vendor_val_called_fake=fake_v, minutes=(time.time() - t0) / 60))
        print(f"[RU {a.arch}][{ep:02d}/{a.epochs}] loss {acc[0] / n:.4f} ffppF1 {f1:.4f} AUC {auc:.4f} vendorF1 {f1v:.4f} "
              f"vendor->fake {fake_v:.1f}% crit {crit:.4f} ({(time.time() - t0) / 60:.1f} min)", flush=True)
        if crit > best:
            best = crit; torch.save(model.state_dict(), out); print("  -> saved best", flush=True)
        with open(HERE / f"train_ru_{tag}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(log[0])); w.writeheader(); w.writerows(log)
    (HERE / f"meta_ru_{tag}.json").write_text(json.dumps({"arch": a.arch, "best": best, "epochs": a.epochs, "seed": a.seed}, indent=1))
    print(f"[RU {a.arch}] best {best:.4f} -> {out}\nDONE", flush=True)


if __name__ == "__main__":
    main()
