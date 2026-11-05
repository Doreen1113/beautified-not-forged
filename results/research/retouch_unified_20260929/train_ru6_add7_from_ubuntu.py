"""RU6 (PRE_DECLARED Addendum 7) = RU5 + a consistency term: every forgery is also shown under one more, stronger random
colour look (more tint and grain) and its forged logit must stay the same; a genuine photograph and its own filtered
version must have the same forged logit too. Tag clipe6. Everything below is the RU5 description.

RU5 (PRE_DECLARED Addendum 6): two independent questions instead of one three-way softmax, and every kind of
beautification shown on genuine AND forged faces.

Why (validation evidence, leak_probe.py and the 2026-10-05 audit):
  * three-way softmax: a forgery that also carries beautification evidence loses probability to *filter*
    (self-blend forgery called fake 94.5 % -> 80.4 % once a commercial texture edit is added; P(fake) > P(real) stays 95 %);
  * colour filters never seen in training make genuine faces look forged (called fake 13.4 % -> 33.6 %);
  * commercial retouching only ever appeared on genuine faces in training.
Changes against RU4-CLIP (train_ru_clip.py --arm ru4 --head), everything else identical:
  1. heads: forged f and beautified b, each a sigmoid with binary cross-entropy. Targets: real (0,0), filter (0,1),
     fake (1, 1 if a beautification was applied on top else 0). For the existing evaluation code the model returns
     log[(1-f)(1-b), f, (1-f)b] as its first output, so softmax gives P(real), P(fake) = f, P(filter).
  2. random colour grading (random_grade) as a filter source and as a beautification applied on top of forgeries:
     random tone curves, colour matrix, saturation, contrast, fade, tint, vignette, grain.
  3. commercial edit on a forgery: a self-blend of a vendor original x0, plus the pixel-aligned photometric edit
     (component - x0) of one of that photograph's cleaned tone / texture components; label fake, beautified 1.

python train_ru5.py [--seed S] [--epochs 8] [--workers 12] [--max-steps N] [--no-grade] [--no-vendor-fake] [--softmax]
  -> checkpoints/.../ru_clipe5[variant]_s<seed>_eNN.pth (every epoch), train_ru_<tag>.csv, meta_ru_<tag>.json
"""
import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from sklearn.metrics import f1_score, roc_auc_score
from torch.utils.data import DataLoader

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from train_ru import BASE, UNI, CKPT, BATCH, SEED, remap, cap, crop, read_manifest, beautify, self_blend, sym_degrade  # noqa: E402
from train_ru3 import RUData3, to_t2, mask_loss, footprint, post_m, res_rand2, ORIG, OPS  # noqa: E402
from train_ru_clip import RUCLIP, ValClip  # noqa: E402
from ops import random_op_v2  # noqa: E402


# ---------------------------------------------------------------------------------------------- random colour grading
def random_grade(rgb, rng, strong=False):
    """A random global 'look' of the kind camera apps ship as filters. At least two of the components are applied."""
    x = rgb.astype(np.float32) / 255.0; h, w = x.shape[:2]
    on = rng.random(8) < np.array([0.6, 0.5, 0.6, 0.5, 0.35, 0.6, 0.3, 0.5] if strong else [0.6, 0.5, 0.6, 0.5, 0.35, 0.4, 0.3, 0.3])
    if on[:6].sum() < 2:
        on[rng.choice(6, 2, replace=False)] = True
    if on[0]:   # per-channel tone curve: gamma, gain, lift
        g = rng.uniform(0.7, 1.4, 3); gain = rng.uniform(0.88, 1.12, 3); lift = rng.uniform(-0.05, 0.05, 3)
        x = np.clip(x, 0, 1) ** g * gain + lift
    if on[1]:   # colour matrix close to identity (channel mixing)
        m = np.eye(3) + rng.normal(0, 0.07, (3, 3)); m /= m.sum(1, keepdims=True); x = x @ m.T.astype(np.float32)
    if on[2]:   # saturation
        gray = x.mean(2, keepdims=True); x = gray + (x - gray) * rng.uniform(0.45, 1.6)
    if on[3]:   # contrast about the mean
        mu = x.mean(); x = mu + (x - mu) * rng.uniform(0.78, 1.3)
    if on[4]:   # fade: lifted blacks, lowered whites
        lo = rng.uniform(0.0, 0.12); hi = rng.uniform(0.9, 1.0); x = lo + x * (hi - lo)
    if on[5]:   # tint (split toning): one colour for shadows, one for highlights
        lum = x.mean(2, keepdims=True); a = rng.uniform(0.03, 0.22 if strong else 0.12)
        x = x + a * ((1 - lum) * (rng.uniform(-1, 1, 3) * 0.5) + lum * (rng.uniform(-1, 1, 3) * 0.5)).astype(np.float32)
    if on[6]:   # vignette
        yy, xx = np.mgrid[0:h, 0:w]; r = np.hypot((yy - h / 2) / (h / 2), (xx - w / 2) / (w / 2))
        x = x * (1 - rng.uniform(0.1, 0.4) * np.clip(r - 0.4, 0, None)[..., None] ** 1.5).astype(np.float32)
    if on[7]:   # grain
        x = x + rng.normal(0, rng.uniform(0.008, 0.06 if strong else 0.03), (h, w, 1)).astype(np.float32)
    return np.clip(x * 255.0, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------------------------- data
class RUData5(RUData3):
    """RU4 mixture with (2) and (3) above. Returns the RU3 tuple plus zb, the forged / beautified targets per item."""

    def __init__(self, rows, size, seed, head_res=16, norm="clip", grade=True, vendor_fake=True):
        super().__init__(rows, size, seed, arm="ru4", head_res=head_res, norm=norm)
        self.grade, self.vendor_fake = grade, vendor_fake
        self.photometric = [r for r in self.single if OPS[int(np.argmax(r["pres"]))] in ("white", "smooth") and r["stem"] in self.lm_ffhq]

    def _vendor_triplet(self, v):
        """Component, its original at the same geometry, and the original's landmarks there."""
        im = np.array(Image.open(v["path"]).convert("RGB")); o = np.array(Image.open(ORIG / f"{v['stem']}.png").convert("RGB"))
        s = im.shape[0] / o.shape[0]
        if o.shape[:2] != im.shape[:2]:
            o = cv2.resize(o, (im.shape[1], im.shape[0]), interpolation=cv2.INTER_AREA)
        lm = self.lm_ffhq[v["stem"]].copy() * s; lm[:, 0] -= v["box"][0]; lm[:, 1] -= v["box"][1]
        c, x0 = crop(im, v["box"]), crop(o, v["box"])
        c2, lm2 = cap(c, lm); x02, _ = cap(x0)
        return c2, x02, lm2

    def _on_top(self, img, lm, rng, has_lm):
        """A beautification applied on top of a forgery: scripted / pilgram, landmark operation, or a random grade."""
        u = rng.random()
        if self.grade and u < 0.35:
            return random_grade(img, rng)
        if has_lm and u < 0.65:
            return random_op_v2(img, lm, rng)[0]
        return beautify(img, rng)

    def __getitem__(self, i):
        r = self.bases[i]
        rng = np.random.default_rng((self.seed * 1000003 + self.epoch * 100003 + i) % (2 ** 63))
        rgb, lm = self._base(r)
        z4 = np.zeros(4, np.float32)
        # ---- filter item: synthetic v2 0.25 | random grade 0.15 | vendor single 0.28 | composite 0.12 | observed 0.20
        u = rng.random(); filt_pres = z4.copy(); filt_q = z4.copy(); mq = 1.0; sep = False; mp = 1.0
        g0 = 0.15 if self.grade else 0.0
        if u < 0.25 + (0.15 - g0):
            filt, filt_pres, filt_q, _ = random_op_v2(rgb, lm, rng); fm = footprint(filt, rgb)
        elif u < 0.40:
            filt = random_grade(rgb, rng); fm = footprint(filt, rgb); mq = 0.0; mp = 0.0   # a colour look is none of the four operations
        elif u < 0.68:
            v = self.single[int(rng.integers(0, len(self.single)))]; filt, x0 = self._vendor_pair(v); filt_pres = v["pres"]; filt_q = v["q"]; fm = footprint(filt, x0); sep = True
        elif u < 0.80:
            v = self.vendor[int(rng.integers(0, len(self.vendor)))]; filt, x0 = self._vendor_pair(v); filt_pres = v["pres"]; fm = footprint(filt, x0); sep = True
            if v["q"] is None:
                mq = 0.0
            else:
                filt_q = v["q"]
        else:
            o = self.obs_filt[int(rng.integers(0, len(self.obs_filt)))]; filt = np.array(Image.open(o["path"]).convert("RGB")); sep = True
            filt_pres = o["pres"]; mq = 0.0; fm = None
        # ---- fake item: self-blend 0.35 | observed 0.25 | part edit 0.25 | commercial edit on a self-blend 0.15
        fsep = False; km = None; uf = rng.random(); fb = 0.0; v0 = 0.15 if self.vendor_fake else 0.0
        if uf < v0:
            v = self.photometric[int(rng.integers(0, len(self.photometric)))]; c, x0, vlm = self._vendor_triplet(v); f = None
            for _ in range(4):
                f = self_blend(x0, vlm, rng)
                if f is not None:
                    break
            if f is None:
                f = x0.copy()
            km = footprint(f, x0)
            fake = np.clip(f.astype(np.int16) + (c.astype(np.int16) - x0.astype(np.int16)), 0, 255).astype(np.uint8); fsep = True; fb = 1.0
        elif uf < v0 + 0.25:
            pf, p0 = self.parts[int(rng.integers(0, len(self.parts)))]
            fake = np.array(Image.open(pf).convert("RGB")); x0f = np.array(Image.open(p0).convert("RGB")); fsep = True
            km = footprint(fake, x0f)
            if rng.random() < 0.3:   # part edits can be beautified too (colour look only: keeps the footprint valid as the forged region)
                fake = random_grade(fake, rng) if self.grade else beautify(fake, rng); fb = 1.0
        elif uf < v0 + 0.50:
            o = self.obs_fake[int(rng.integers(0, len(self.obs_fake)))]; fake = np.array(Image.open(o["path"]).convert("RGB")); fsep = True
            if rng.random() < 0.5:
                fake = self._on_top(fake, None, rng, False); fb = 1.0
        else:
            fake = None
            for _ in range(4):
                fake = self_blend(rgb, lm, rng)
                if fake is not None:
                    break
            if fake is None:
                fake = rgb.copy()
            km = footprint(fake, rgb)
            if rng.random() < 0.5:
                fake = self._on_top(fake, lm, rng, True); fb = 1.0
        # ---- post-processing with masks (as RU3 / RU4)
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
        pair = random_grade(fake, rng, strong=True)   # RU6: the same forgery under one more colour look; its forged logit must not move
        x = torch.stack([to_t2(real, self.size, flip, self.norm), to_t2(fake, self.size, flip, self.norm), to_t2(filt, self.size, flip, self.norm),
                         to_t2(pair, self.size, flip, self.norm)])

        def mk(m):
            if m is None:
                return torch.zeros(self.head_res, self.head_res), 0.0
            t = cv2.resize(m, (self.head_res, self.head_res), interpolation=cv2.INTER_AREA)
            return torch.from_numpy(np.ascontiguousarray(t[:, ::-1] if flip else t)).float(), 1.0
        (m0, v0_), (m1, v1), (m2, v2) = mk(rm), mk(km), mk(fm)
        y = torch.tensor([0, 1, 2, 1])
        pres = torch.tensor(np.stack([z4, z4, filt_pres, z4])); mpres = torch.tensor([1.0, 0.0, mp, 0.0])
        q = torch.tensor(np.stack([z4, z4, filt_q, z4])); mq_t = torch.tensor([1.0, 0.0, mq, 0.0])
        zb = torch.tensor([[0.0, 0.0], [1.0, fb], [0.0, 1.0], [1.0, 1.0]])
        return x, y, pres, mpres, q, mq_t, torch.stack([m0, m1, m2, m1]), torch.tensor([v0_, v1, v2, v1]), zb, torch.tensor([0.0 if sep else 1.0])


# ---------------------------------------------------------------------------------------------- model
class RUCLIP5(RUCLIP):
    """RUCLIP with a forged / beautified head `fz` (two logits). First output: log of the joint (real, fake, filter)."""

    def __init__(self, head=True, r=16):
        super().__init__(head=head, r=r)
        self.fz = nn.Linear(self.vit.config.hidden_size, 2)
        del self.cls   # replaced by fz; the joint (real, fake, filter) is derived from it

    def forward(self, x):
        o = self.vit(pixel_values=x); f = o.pooler_output; z = self.fz(f).float()
        lf, lb = F.logsigmoid(z[:, 0]), F.logsigmoid(z[:, 1]); nf, nb = F.logsigmoid(-z[:, 0]), F.logsigmoid(-z[:, 1])
        joint = torch.stack([nf + nb, lf, nf + lb], 1)
        out = (joint, self.pres(f), self.q(f))
        if self.head:
            t = o.last_hidden_state[:, 1:, :]; ev = self.ev(t).transpose(1, 2).reshape(x.shape[0], 1, self.grid, self.grid)
            return out + (ev, z)
        return out + (None, z)

    def state_dict_trainable(self):
        return {k: v for k, v in self.state_dict().items() if ("A" in k.split(".")[-1] or "B" in k.split(".")[-1] or k.split(".")[0] in ("pres", "q", "ev", "fz"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=8); ap.add_argument("--workers", type=int, default=12); ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--seed", type=int, default=SEED); ap.add_argument("--wq", type=float, default=2.0); ap.add_argument("--wm", type=float, default=1.0)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--no-grade", action="store_true"); ap.add_argument("--no-vendor-fake", action="store_true")
    ap.add_argument("--softmax", action="store_true", help="ablation: RU5 data with the three-way softmax of RU4")
    ap.add_argument("--wc", type=float, default=1.0, help="weight of the forged-logit consistency term")
    a = ap.parse_args()
    torch.manual_seed(a.seed); np.random.seed(a.seed); CKPT.mkdir(parents=True, exist_ok=True)
    variant = ("x" if a.softmax else "") + ("g0" if a.no_grade else "") + ("v0" if a.no_vendor_fake else "")
    tag = f"clipe6{variant}_s{a.seed}"
    model = (RUCLIP(head=True) if a.softmax else RUCLIP5(head=True)).cuda()
    rows = read_manifest(HERE / "manifest_train.tsv"); vrows = read_manifest(HERE / "manifest_val.tsv")
    ds = RUData5(rows, 224, a.seed, head_res=model.grid, norm="clip", grade=not a.no_grade, vendor_fake=not a.no_vendor_fake)
    vf = [l.split("\t") for l in (UNI / "ffpp3_val.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    dl_vf = DataLoader(ValClip([dict(path=remap(r[0]), box=None, cls=int(r[1])) for r in vf]), batch_size=64, num_workers=4)
    dl_vv = DataLoader(ValClip(vrows), batch_size=64, num_workers=4)
    ntr = sum(p.numel() for p in model.trainable())
    print(f"[{tag}] bases {len(ds):,} | single {len(ds.single):,} | photometric {len(ds.photometric):,} | parts {len(ds.parts):,} | trainable {ntr / 1e6:.2f} M | "
          f"factorised {not a.softmax} grade {not a.no_grade} vendor-fake {not a.no_vendor_fake}", flush=True)
    opt = torch.optim.AdamW(model.trainable(), lr=a.lr, weight_decay=0.01)
    steps_ep = len(ds) // BATCH; total = steps_ep * a.epochs; warm = 200

    def lr_at(s):
        return a.lr * s / warm if s < warm else 0.5 * a.lr * (1 + math.cos(math.pi * (s - warm) / max(total - warm, 1)))

    def loss_fn(out, y, pres, mpres, q, mq, m, mm, zb, cm):
        lo, pr, qq = out[:3]
        l = F.cross_entropy(lo.float(), y) if a.softmax else F.binary_cross_entropy_with_logits(out[4], zb, reduction="none").sum(1).mean()
        lp = (F.binary_cross_entropy_with_logits(pr.float(), pres, reduction="none").mean(1) * mpres).sum() / mpres.sum().clamp(min=1)
        lq = ((qq.float() - q).abs().mean(1) * mq).sum() / mq.sum().clamp(min=1)
        lm = mask_loss(out[3], m, mm)
        z = out[4][:, 0].view(-1, 4)   # forged logit of (real, fake, filter, fake under one more look) per base photograph
        lc = F.smooth_l1_loss(z[:, 1], z[:, 3]) + (F.smooth_l1_loss(z[:, 0], z[:, 2], reduction="none") * cm).sum() / cm.sum().clamp(min=1)
        return l + lp + a.wq * lq + a.wm * lm + a.wc * lc, (float(l.detach()), float(lp.detach()), float(lq.detach()), float(lm.detach() + lc.detach()))

    def evaluate(dl):
        P, S, T = [], [], []; model.eval()
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            for x, y in dl:
                pr = torch.softmax(model(x.cuda())[0].float(), 1).cpu().numpy()
                P.extend(pr.argmax(1).tolist()); S.extend(pr[:, 1].tolist()); T.extend(y.tolist())
        return np.array(P), np.array(S), np.array(T)

    log, step = [], 0
    for ep in range(1, a.epochs + 1):
        ds.epoch = ep
        dl = DataLoader(ds, batch_size=BATCH, shuffle=True, num_workers=a.workers, pin_memory=True, drop_last=True, persistent_workers=False, prefetch_factor=3)
        model.train(); acc = np.zeros(5); n = 0; t0 = time.time()
        for batch in dl:
            for g in opt.param_groups:
                g["lr"] = lr_at(step)
            x = batch[0].flatten(0, 1).cuda(non_blocking=True); y, pres, mpres, q, mq, m, mm, zb = [t.flatten(0, 1).cuda() for t in batch[1:9]]; cm = batch[9].flatten().cuda()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss, parts = loss_fn(model(x), y, pres, mpres, q, mq, m, mm, zb, cm)
            opt.zero_grad(set_to_none=True); loss.backward(); torch.nn.utils.clip_grad_norm_(model.trainable(), 1.0); opt.step()
            acc += np.array([float(loss.detach())] + list(parts)); n += 1; step += 1
            if step % 200 == 0:
                print(f"  step {step}/{total} loss {acc[0] / n:.4f} (cls {acc[1] / n:.3f} pres {acc[2] / n:.3f} q {acc[3] / n:.3f} mask {acc[4] / n:.3f}) {(time.time() - t0) / n:.3f}s/it", flush=True)
            if a.max_steps and step >= a.max_steps:
                print(f"smoke test ok: {step} steps, {(time.time() - t0) / n:.3f}s/it", flush=True); return
        P, S, T = evaluate(dl_vf); mk = np.isin(T, [0, 1]); f1 = f1_score(T, P, average="macro"); auc = roc_auc_score((T[mk] == 1).astype(int), S[mk])
        Pv, _, Tv = evaluate(dl_vv); orig_real = float((Pv[Tv == 0] == 0).mean() * 100); filt_rec = float((Pv[Tv == 2] == 2).mean() * 100)
        log.append(dict(epoch=ep, loss=acc[0] / n, ffpp_val_f1=f1, ffpp_val_auc=auc, vendor_val_orig_real=orig_real, vendor_val_filter_recall=filt_rec, minutes=(time.time() - t0) / 60))
        print(f"[{tag}][{ep:02d}/{a.epochs}] loss {acc[0] / n:.4f} ffppF1 {f1:.4f} AUC {auc:.4f} orig->real {orig_real:.1f}% vendor filter recall {filt_rec:.1f}% ({(time.time() - t0) / 60:.1f} min)", flush=True)
        torch.save(model.state_dict_trainable(), CKPT / f"ru_{tag}_e{ep:02d}.pth")
        with open(HERE / f"train_ru_{tag}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(log[0])); w.writeheader(); w.writerows(log)
    (HERE / f"meta_ru_{tag}.json").write_text(json.dumps({"arm": "ru6", "wc": a.wc, "factorised": not a.softmax, "grade": not a.no_grade, "vendor_fake": not a.no_vendor_fake,
                                                         "epochs": a.epochs, "seed": a.seed, "trainable_M": ntr / 1e6}, indent=1))
    print(f"[{tag}] DONE", flush=True)


if __name__ == "__main__":
    main()
