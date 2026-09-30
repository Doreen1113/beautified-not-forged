"""RU3 / RU3-E (PRE_DECLARED Addendum 3): RU2 with cleaned vendor components (--arm ru3) and an optional 12x12 evidence
head supervised by exact footprints from pixel-aligned pairs (--head).  Also provides the dataset for train_ru_clip.py.

python train_ru3.py --arch effb4 --arm ru3 [--head] [--epochs 12] [--workers 12] [--max-steps N] [--seed S]
  -> checkpoints/research/retouch_unified_20260929/ru_<tag>.pth  with tag = ru3[e]_<arch>_s<seed>
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

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from train_ru import (BASE, UNI, FASB, CKPT, ARCH, BATCH, LR, RHO, SEED, remap, cap, crop, read_manifest, ValDS)  # noqa: E402
from train_sbifix import sym_degrade, SAM  # noqa: E402
from sbi_faithful import self_blend  # noqa: E402
from sbi.sbi_generator import common_transforms  # noqa: E402
from fasb import beautify  # noqa: E402
from ops import random_op_v2, OPS  # noqa: E402

FLOOR = {"eye": 0.008, "jaw": 0.008, "white": 0.05, "smooth": 0.03}   # Addendum 3, from training-vendor distributions + calib residual
CLIP_MEAN, CLIP_STD = (0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711)
ORIG = BASE / "ffhq_originals/Part7"


def to_t2(rgb, size, flip, norm="half"):
    im = Image.fromarray(rgb).resize((size, size), Image.BILINEAR)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    x = torch.from_numpy(np.asarray(im, np.float32) / 255.0).permute(2, 0, 1)
    if norm == "clip":
        return (x - torch.tensor(CLIP_MEAN)[:, None, None]) / torch.tensor(CLIP_STD)[:, None, None]
    return (x - 0.5) / 0.5


def footprint(x, x0, thr=6, r_frac=25.0 / 380):
    """Exact edit footprint of x against its pixel-aligned original x0 (same shape), dilated by ~25 px at 380 px."""
    if x0.shape != x.shape:
        x0 = cv2.resize(x0, (x.shape[1], x.shape[0]), interpolation=cv2.INTER_AREA)
    d = (np.abs(x.astype(np.int16) - x0.astype(np.int16)).max(2) > thr).astype(np.uint8)
    k = max(3, int(round(r_frac * max(x.shape[:2]))) | 1)
    return cv2.dilate(d, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))).astype(np.float32)


def post_m(imgs, masks, rng):
    """shared_post with masks: identical common transform (colour + JPEG) and identical crop for all items and their masks."""
    s = int(rng.integers(0, 2 ** 31 - 1))
    out = [common_transforms(im, np.random.default_rng(s))[0] for im in imgs]
    h, w = out[0].shape[:2]
    t, b, l, r = (rng.uniform(0, 0.06, 4) * np.array([h, h, w, w])).astype(int)
    return [np.ascontiguousarray(im[t:h - b, l:w - r]) for im in out], [None if m is None else np.ascontiguousarray(m[t:h - b, l:w - r]) for m in masks]


def res_rand2(rgb, m, rng, p=0.5, lo=160, hi=512):
    h, w = rgb.shape[:2]
    if rng.random() >= p or max(h, w) <= lo:
        return rgb, m
    s = int(rng.integers(lo, min(hi, max(h, w)) + 1)); f = s / max(h, w); nw, nh = max(8, int(w * f)), max(8, int(h * f))
    return cv2.resize(rgb, (nw, nh), interpolation=cv2.INTER_AREA), (None if m is None else cv2.resize(m, (nw, nh), interpolation=cv2.INTER_AREA))


class RUData3(Dataset):
    def __init__(self, rows, size, seed, arm="ru3", head_res=12, norm="half", ffhq_repeat=3):
        self.size, self.seed, self.epoch, self.arm, self.head_res, self.norm = size, seed, 0, arm, head_res, norm
        z = np.load(FASB / "landmarks_train.npz"); self.lm_ffpp = {k: z[k] for k in z.files}
        zf = np.load(HERE / "ffhq_landmarks.npz"); self.lm_ffhq = {k: zf[k] for k in zf.files}
        self.ffpp_root = BASE / "FaceForensics_protocol_frames_dense/train/real"
        self.bases = [r for r in rows if r["src"] == "ffpp_real" and r["stem"] in self.lm_ffpp] + [r for r in rows if r["src"] == "ffhq_orig"] * ffhq_repeat
        self.vendor = [r for r in rows if r["src"] in ("tencent", "megvii")]
        single = [r for r in rows if r["src"] == "vendor_single"]
        if arm in ("ru3", "ru4"):
            single = [r for r in single if r["q"] is not None and r["q"][int(np.argmax(r["pres"]))] >= FLOOR[OPS[int(np.argmax(r["pres"]))]]]
        self.single = single
        self.obs_filt = [r for r in rows if r["src"] == "ffpp_filter"]; self.obs_fake = [r for r in rows if r["src"] == "ffpp_fake"]
        self.parts = []
        if arm == "ru4":   # part-level edits (train partition) with pixel-aligned originals -> exact footprints
            PE = BASE / "results/research/partedit_20260927"
            for mech in ("donor", "sd"):
                for l in (PE / f"manifest_train_{mech}.tsv").read_text(encoding="utf-8").splitlines()[1:]:
                    c = l.split("\t")
                    if len(c) > 5:
                        self.parts.append((remap(c[0]), remap(c[5])))

    def __len__(self):
        return len(self.bases)

    def _base(self, r):
        if r["src"] == "ffpp_real":
            return np.array(Image.open(self.ffpp_root / f"{r['stem']}.jpg").convert("RGB")), self.lm_ffpp[r["stem"]].copy()
        rgb = crop(np.array(Image.open(r["path"]).convert("RGB")), r["box"])
        lm = self.lm_ffhq[r["stem"]].copy(); lm[:, 0] -= r["box"][0]; lm[:, 1] -= r["box"][1]
        return cap(rgb, lm)

    def _vendor_pair(self, v):
        """Vendor image and its FFHQ original at the same geometry (both capped to 512)."""
        im = np.array(Image.open(v["path"]).convert("RGB")); o = np.array(Image.open(ORIG / f"{v['stem']}.png").convert("RGB"))
        if o.shape[:2] != im.shape[:2]:
            o = cv2.resize(o, (im.shape[1], im.shape[0]), interpolation=cv2.INTER_AREA)
        return cap(crop(im, v["box"]))[0], cap(crop(o, v["box"]))[0]

    def __getitem__(self, i):
        r = self.bases[i]
        rng = np.random.default_rng((self.seed * 1000003 + self.epoch * 100003 + i) % (2 ** 63))
        rgb, lm = self._base(r)
        z4 = np.zeros(4, np.float32)
        # ---- filter item: synthetic v2 0.30 | vendor single 0.30 | composite 0.15 | observed 0.25
        u = rng.random(); filt_pres = z4.copy(); filt_q = z4.copy(); mq = 1.0; sep = False; fm = None
        if u < 0.30:
            filt, filt_pres, filt_q, _ = random_op_v2(rgb, lm, rng); fm = footprint(filt, rgb)
        elif u < 0.60:
            v = self.single[int(rng.integers(0, len(self.single)))]; filt, x0 = self._vendor_pair(v); filt_pres = v["pres"]; filt_q = v["q"]; fm = footprint(filt, x0); sep = True
        elif u < 0.75:
            v = self.vendor[int(rng.integers(0, len(self.vendor)))]; filt, x0 = self._vendor_pair(v); filt_pres = v["pres"]; fm = footprint(filt, x0); sep = True
            if v["q"] is None:
                mq = 0.0
            else:
                filt_q = v["q"]
        else:
            o = self.obs_filt[int(rng.integers(0, len(self.obs_filt)))]; filt = np.array(Image.open(o["path"]).convert("RGB")); sep = True
            filt_pres = o["pres"]; mq = 0.0
        # ---- fake item
        fsep = False; km = None; uf = rng.random()
        if self.arm == "ru4" and uf >= 0.7:   # RU4: self-blend 0.4 | observed 0.3 | part edit 0.3 (exact footprint vs its original)
            pf, p0 = self.parts[int(rng.integers(0, len(self.parts)))]
            fake = np.array(Image.open(pf).convert("RGB")); x0f = np.array(Image.open(p0).convert("RGB")); fsep = True
            km = footprint(fake, x0f)
        elif uf < (0.4 if self.arm == "ru4" else 0.5):
            fake = None
            for _ in range(4):
                fake = self_blend(rgb, lm, rng)
                if fake is not None:
                    break
            if fake is None:
                fake = rgb.copy()
        else:
            o = self.obs_fake[int(rng.integers(0, len(self.obs_fake)))]; fake = np.array(Image.open(o["path"]).convert("RGB")); fsep = True
        if rng.random() < 0.5 and km is None:   # compositional beautification; part edits keep their exact footprint (no beautify)
            fake = beautify(fake, rng) if (fsep or rng.random() < 0.5) else random_op_v2(fake, lm, rng)[0]
        if not fsep:
            km = footprint(fake, rgb)
        # ---- post-processing with masks
        rm = np.zeros(rgb.shape[:2], np.float32)
        shared_i, shared_m = [rgb], [rm]
        if not sep:
            shared_i.append(filt); shared_m.append(fm)
        if not fsep:
            shared_i.append(fake); shared_m.append(km)
        outs, ms = post_m(shared_i, shared_m, rng); real, rm = outs[0], ms[0]; k = 1
        if not sep:
            filt, fm = outs[k], ms[k]; k += 1
        else:
            (filt,), (fm,) = post_m([filt], [fm], rng)
        if not fsep:
            fake, km = outs[k], ms[k]
        else:
            (fake,), (km,) = post_m([fake], [km], rng)
        real, rm = res_rand2(real, rm, rng); filt, fm = res_rand2(filt, fm, rng); fake, km = res_rand2(fake, km, rng)
        real, filt, fake = sym_degrade([real, filt, fake], rng)
        flip = bool(rng.random() < 0.5)
        x = torch.stack([to_t2(real, self.size, flip, self.norm), to_t2(fake, self.size, flip, self.norm), to_t2(filt, self.size, flip, self.norm)])
        def mk(m):
            if m is None:
                return torch.zeros(self.head_res, self.head_res), 0.0
            t = cv2.resize(m, (self.head_res, self.head_res), interpolation=cv2.INTER_AREA)
            return torch.from_numpy(np.ascontiguousarray(t[:, ::-1] if flip else t)).float(), 1.0
        (m0, v0), (m1, v1), (m2, v2) = mk(rm), mk(km), mk(fm)
        y = torch.tensor([0, 1, 2])
        pres = torch.tensor(np.stack([z4, z4, filt_pres])); mpres = torch.tensor([1.0, 0.0, 1.0])
        q = torch.tensor(np.stack([z4, z4, filt_q])); mq_t = torch.tensor([1.0, 0.0, mq])
        return x, y, pres, mpres, q, mq_t, torch.stack([m0, m1, m2]), torch.tensor([v0, v1, v2])


class RUNet3(nn.Module):
    def __init__(self, arch, head=False):
        super().__init__()
        self.backbone = timm.create_model(ARCH[arch][0], pretrained=True, num_classes=0); d = self.backbone.num_features
        self.cls, self.pres, self.q = nn.Linear(d, 3), nn.Linear(d, 4), nn.Linear(d, 4)
        self.head = head; self.ev = nn.Conv2d(d, 1, 1) if head else None

    def forward(self, x):
        fm = self.backbone.forward_features(x); f = fm.mean((2, 3))
        out = (self.cls(f), self.pres(f), self.q(f))
        return out + (self.ev(fm),) if self.head else out


def mask_loss(ev, m, mm):
    """BCE + Dice on the head grid, masked by mm; ev: (B,1,h,w) logits, m: (B,h,w)."""
    ev = F.interpolate(ev.float(), size=m.shape[-2:], mode="bilinear", align_corners=False)[:, 0]
    bce = F.binary_cross_entropy_with_logits(ev, m, reduction="none").mean((1, 2))
    p = torch.sigmoid(ev); dice = 1 - (2 * (p * m).sum((1, 2)) + 1) / (p.sum((1, 2)) + m.sum((1, 2)) + 1)
    return ((bce + dice) * mm).sum() / mm.sum().clamp(min=1)


def head_res(model, size):
    with torch.no_grad():
        return int(model.backbone.forward_features(torch.zeros(1, 3, size, size)).shape[-1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", default="effb4", choices=list(ARCH)); ap.add_argument("--arm", default="ru3", choices=["ru2", "ru3", "ru4"])
    ap.add_argument("--head", action="store_true"); ap.add_argument("--epochs", type=int, default=12); ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--max-steps", type=int, default=0); ap.add_argument("--seed", type=int, default=SEED); ap.add_argument("--wq", type=float, default=2.0)
    ap.add_argument("--wm", type=float, default=1.0)
    a = ap.parse_args()
    torch.manual_seed(a.seed); np.random.seed(a.seed); CKPT.mkdir(parents=True, exist_ok=True)
    name, size = ARCH[a.arch]; tag = f"{a.arm}{'e' if a.head else ''}_{a.arch}_s{a.seed}"
    model = RUNet3(a.arch, a.head); hr = head_res(model, size) if a.head else 12
    model = model.cuda().to(memory_format=torch.channels_last)
    rows = read_manifest(HERE / "manifest_train.tsv"); vrows = read_manifest(HERE / "manifest_val.tsv")
    ds = RUData3(rows, size, a.seed, arm=a.arm, head_res=hr)
    vf = [l.split("\t") for l in (UNI / "ffpp3_val.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    dl_vf = DataLoader(ValDS([dict(path=remap(r[0]), box=None, cls=int(r[1])) for r in vf], size), batch_size=64, num_workers=4)
    dl_vv = DataLoader(ValDS(vrows, size), batch_size=64, num_workers=4)
    print(f"[{tag}] bases {len(ds):,} | single {len(ds.single):,} (cleaned) | vendor {len(ds.vendor):,} | parts {len(ds.parts):,} | head {a.head} grid {hr} | params {sum(p.numel() for p in model.parameters()):,}", flush=True)
    opt = SAM(model.parameters(), RHO)
    steps_ep = len(ds) // BATCH; total = steps_ep * a.epochs; decay_from = int(total * 0.75)

    def loss_fn(out, y, pres, mpres, q, mq, m, mm):
        lo, pr, qq = out[:3]
        l = F.cross_entropy(lo.float(), y)
        lp = (F.binary_cross_entropy_with_logits(pr.float(), pres, reduction="none").mean(1) * mpres).sum() / mpres.sum().clamp(min=1)
        lq = ((qq.float() - q).abs().mean(1) * mq).sum() / mq.sum().clamp(min=1)
        lm = mask_loss(out[3], m, mm) if a.head else torch.zeros((), device=lo.device)
        return l + lp + a.wq * lq + a.wm * lm, (float(l.detach()), float(lp.detach()), float(lq.detach()), float(lm.detach()))

    def evaluate(dl):
        P, S, T = [], [], []; model.eval()
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            for x, y in dl:
                pr = torch.softmax(model(x.cuda().to(memory_format=torch.channels_last))[0].float(), 1).cpu().numpy()
                P.extend(pr.argmax(1).tolist()); S.extend(pr[:, 1].tolist()); T.extend(y.tolist())
        return np.array(P), np.array(S), np.array(T)

    best, log, step, out = -1.0, [], 0, CKPT / f"ru_{tag}.pth"
    for ep in range(1, a.epochs + 1):
        ds.epoch = ep
        dl = DataLoader(ds, batch_size=BATCH, shuffle=True, num_workers=a.workers, pin_memory=True, drop_last=True, persistent_workers=False, prefetch_factor=3)
        model.train(); acc = np.zeros(5); n = 0; t0 = time.time()
        for batch in dl:
            lr = LR if step < decay_from else LR * (total - step) / max(total - decay_from, 1)
            for g in opt.base.param_groups:
                g["lr"] = lr
            x = batch[0].flatten(0, 1).cuda(non_blocking=True).to(memory_format=torch.channels_last)
            y, pres, mpres, q, mq, m, mm = [t.flatten(0, 1).cuda() for t in batch[1:]]
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss, parts = loss_fn(model(x), y, pres, mpres, q, mq, m, mm)
            loss.backward(); opt.first(); opt.base.zero_grad()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss_fn(model(x), y, pres, mpres, q, mq, m, mm)[0].backward()
            opt.second(); opt.base.zero_grad()
            acc += np.array([float(loss.detach())] + list(parts)); n += 1; step += 1
            if step % 200 == 0:
                print(f"  step {step}/{total} loss {acc[0] / n:.4f} (ce {acc[1] / n:.3f} pres {acc[2] / n:.3f} q {acc[3] / n:.3f} mask {acc[4] / n:.3f}) {(time.time() - t0) / n:.3f}s/it", flush=True)
            if a.max_steps and step >= a.max_steps:
                print(f"smoke test ok: {step} steps, {(time.time() - t0) / n:.3f}s/it", flush=True); return
        P, S, T = evaluate(dl_vf); mk = np.isin(T, [0, 1]); f1 = f1_score(T, P, average="macro"); auc = roc_auc_score((T[mk] == 1).astype(int), S[mk])
        Pv, _, Tv = evaluate(dl_vv); f1v = f1_score((Tv == 2).astype(int), (Pv == 2).astype(int)); orig_real = float((Pv[Tv == 0] == 0).mean() * 100)
        crit = 0.5 * (f1 + f1v)
        log.append(dict(epoch=ep, loss=acc[0] / n, ffpp_val_f1=f1, ffpp_val_auc=auc, vendor_val_f1=f1v, vendor_val_orig_real=orig_real, minutes=(time.time() - t0) / 60))
        print(f"[{tag}][{ep:02d}/{a.epochs}] loss {acc[0] / n:.4f} ffppF1 {f1:.4f} AUC {auc:.4f} vendorF1 {f1v:.4f} orig->real {orig_real:.1f}% crit {crit:.4f} ({(time.time() - t0) / 60:.1f} min)", flush=True)
        if crit > best:
            best = crit; torch.save(model.state_dict(), out); print("  -> saved best", flush=True)
        with open(HERE / f"train_ru_{tag}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(log[0])); w.writeheader(); w.writerows(log)
    (HERE / f"meta_ru_{tag}.json").write_text(json.dumps({"arm": a.arm, "head": a.head, "arch": a.arch, "best": best, "epochs": a.epochs, "seed": a.seed, "n_single": len(ds.single)}, indent=1))
    print(f"[{tag}] best {best:.4f} -> {out}\nDONE", flush=True)


if __name__ == "__main__":
    main()
