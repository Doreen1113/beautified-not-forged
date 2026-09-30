"""SBI-F / HYB-F: sbiscale recipe with faithful self-blending (sbifix PRE_DECLARED §2-3).

python train_sbiscale.py --arm {SBI,FASB,HYB} [--epochs 14] [--workers 7] [--max-steps N (smoke test)]
  -> checkpoints/research/sbiscale_20260926/sbiscale_<ARM>.pth, train_<ARM>.csv
"""
import argparse
import csv
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import timm
import torch
import torch.nn as nn
from PIL import Image
from sklearn.metrics import f1_score, roc_auc_score
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

import os
BASE = Path(os.environ.get("AIGC_BASE", r"C:\My_Project\AIGC"))
HERE = Path(__file__).resolve().parent
UNI = BASE / "results/research/ffpp_unified_20260925"
FASB = BASE / "results/research/fasb_20260926"
CKPT = BASE / "checkpoints/research/sbifix_20260927"
sys.path.insert(0, str(FASB)); sys.path.insert(0, str(BASE)); sys.path.insert(0, str(HERE))
from fasb import beautify  # noqa: E402
from sbi_faithful import jitter_one, make_triplet  # noqa: E402  faithful synthesis

MODEL, SIZE, BATCH, LR, RHO, SEED = "tf_efficientnet_b4.ap_in1k", 380, 16, 1e-3, 0.05, 20260928
NORM = transforms.Compose([transforms.ToTensor(), transforms.Normalize([0.5] * 3, [0.5] * 3)])


def sym_degrade(imgs, rng, p=0.5):
    """Same random blur or downscale-upscale applied to every image of the triplet, so softness carries no label
    information (probe 2026-09-28: FF++ reals downscaled x1.5 -> 60 % called fake; Celeb-DF genuine frames are soft)."""
    if rng.random() >= p:
        return imgs
    if rng.random() < 0.5:
        s = float(rng.uniform(0.6, 2.0))
        return [cv2.GaussianBlur(im, (0, 0), s) for im in imgs]
    f = float(rng.uniform(1.3, 3.0)); h, w = imgs[0].shape[:2]
    return [cv2.resize(cv2.resize(im, (max(8, int(w / f)), max(8, int(h / f))), interpolation=cv2.INTER_AREA), (w, h),
                       interpolation=cv2.INTER_LINEAR) for im in imgs]


def to_t(rgb, flip):
    im = Image.fromarray(rgb).resize((SIZE, SIZE), Image.BILINEAR)
    return NORM(im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im)


def remap(p):
    """Split files hold Windows paths; remap them when running on the Ubuntu box."""
    return p if os.name == "nt" else p.replace("C:\\My_Project\\AIGC", str(BASE)).replace("\\", "/")


def train_rows():
    r = [l.split("\t") for l in (UNI / "ffpp3_train.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return [remap(x[0]) for x in r if x[1] == "1"], [remap(x[0]) for x in r if x[1] == "2"]


class OnTheFly(Dataset):
    def __init__(self, arm, seed=SEED):
        self.seed = seed
        z = np.load(FASB / "landmarks_train.npz")
        self.stems = sorted(z.files); self.lm = {k: z[k] for k in self.stems}
        self.root = BASE / "FaceForensics_protocol_frames_dense/train/real"
        self.arm, self.epoch = arm, 0
        self.obs_fake, self.obs_filt = train_rows() if arm in ("HYB", "SUP", "HYBD") else ([], [])

    def __len__(self):
        return len(self.stems)

    def _obs(self, path, rng, beaut=False):
        rgb = np.array(Image.open(path).convert("RGB"))
        if beaut:
            rgb = beautify(rgb, rng)
        return jitter_one(rgb, rng)

    def __getitem__(self, i):
        stem = self.stems[i]
        rng = np.random.default_rng((self.seed * 1000003 + self.epoch * 100003 + i) % (2 ** 63))
        rgb = np.array(Image.open(self.root / f"{stem}.jpg").convert("RGB"))
        if self.arm == "HYBD":  # Addendum 2: HYB + symmetric degradation (blur/downscale shared by the whole triplet)
            real, filt, fake = make_triplet(rgb, self.lm[stem], rng, p_compose=0.5, binary=False)
            if rng.random() < 0.5:
                fake = self._obs(self.obs_fake[int(rng.integers(0, len(self.obs_fake)))], rng, beaut=rng.random() < 0.5)
            if rng.random() < 0.5:
                filt = self._obs(self.obs_filt[int(rng.integers(0, len(self.obs_filt)))], rng)
            real, filt, fake = sym_degrade([real, filt, fake], rng)
        elif self.arm == "SUP":   # Addendum 1: observed data only, same post-processing
            real = jitter_one(rgb, rng)
            fake = self._obs(self.obs_fake[int(rng.integers(0, len(self.obs_fake)))], rng, beaut=rng.random() < 0.5)
            filt = self._obs(self.obs_filt[int(rng.integers(0, len(self.obs_filt)))], rng)
        else:
            real, filt, fake = make_triplet(rgb, self.lm[stem], rng, p_compose=0.5, binary=self.arm == "SBI")
        if self.arm == "HYB":
            if rng.random() < 0.5:
                fake = self._obs(self.obs_fake[int(rng.integers(0, len(self.obs_fake)))], rng, beaut=rng.random() < 0.5)
            if rng.random() < 0.5:
                filt = self._obs(self.obs_filt[int(rng.integers(0, len(self.obs_filt)))], rng)
        flip = bool(rng.random() < 0.5)
        r, k = to_t(real, flip), to_t(fake, flip)
        return r, k, (to_t(filt, flip) if filt is not None else torch.zeros_like(r))


class ValDS(Dataset):
    def __init__(self, rows):
        self.rows = rows; self.tf = transforms.Compose([transforms.Resize((SIZE, SIZE)), NORM])

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        p, y = self.rows[i]
        return self.tf(Image.open(p).convert("RGB")), y


class SAM:
    """Sharpness-aware minimisation (Foret et al. 2021), wrapping SGD, as in the official SBI trainer."""

    def __init__(self, params, rho):
        self.params = [p for p in params if p.requires_grad]
        self.base = torch.optim.SGD(self.params, lr=LR, momentum=0.9); self.rho = rho; self.e = []

    @torch.no_grad()
    def first(self):
        g = torch.norm(torch.stack([p.grad.norm(2) for p in self.params if p.grad is not None]), 2)
        s = self.rho / (g + 1e-12); self.e = []
        for p in self.params:
            e = p.grad * s if p.grad is not None else None
            if e is not None:
                p.add_(e)
            self.e.append(e)

    @torch.no_grad()
    def second(self):
        for p, e in zip(self.params, self.e):
            if e is not None:
                p.sub_(e)
        self.base.step()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["SBI", "HYB", "SUP", "HYBD"])
    ap.add_argument("--epochs", type=int, default=14)
    ap.add_argument("--workers", type=int, default=7)
    ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--seed", type=int, default=SEED)
    a = ap.parse_args()
    torch.manual_seed(a.seed); np.random.seed(a.seed)
    sfx = f"_s{a.seed}"
    CKPT.mkdir(parents=True, exist_ok=True)
    ncls = 2 if a.arm == "SBI" else 3
    ds = OnTheFly(a.arm, a.seed)
    if a.arm in ("HYB", "SUP", "HYBD"):  # trap 1: observed rows must be train-partition rows
        tr = {remap(l.split("\t")[0]) for l in (UNI / "ffpp3_train.txt").read_text(encoding="utf-8").splitlines()[1:]}
        assert all(p in tr for p in ds.obs_fake + ds.obs_filt)
        print(f"[HYB] observed fake {len(ds.obs_fake):,} / filter {len(ds.obs_filt):,} (all in ffpp3_train)", flush=True)
    vr = [l.split("\t") for l in (UNI / "ffpp3_val.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    vr = [(remap(r[0]), 0 if r[1] == "0" else 1) for r in vr if r[1] in ("0", "1")] if ncls == 2 else [(remap(r[0]), int(r[1])) for r in vr]
    dl_va = DataLoader(ValDS(vr), batch_size=64, num_workers=4)

    model = timm.create_model(MODEL, pretrained=True, num_classes=ncls).cuda().to(memory_format=torch.channels_last)
    opt = SAM(model.parameters(), RHO)
    crit = nn.CrossEntropyLoss()
    steps_ep = len(ds) // BATCH; total = steps_ep * a.epochs; decay_from = int(total * 0.75)
    print(f"[{a.arm}] photos {len(ds):,}, steps/epoch {steps_ep}, total {total}, params "
          f"{sum(p.numel() for p in model.parameters()):,}", flush=True)

    def batch_xy(r, k, l):
        b = r.size(0)
        if ncls == 2:
            return torch.cat([r, k]), torch.cat([torch.zeros(b), torch.ones(b)]).long()
        return torch.cat([r, k, l]), torch.cat([torch.zeros(b), torch.ones(b), torch.full((b,), 2)]).long()

    best, rows, step, out = -1.0, [], 0, CKPT / f"sbifix_{a.arm}{sfx}.pth"
    for ep in range(1, a.epochs + 1):
        ds.epoch = ep
        dl = DataLoader(ds, batch_size=BATCH, shuffle=True, num_workers=a.workers, pin_memory=True, drop_last=True,
                        persistent_workers=False, prefetch_factor=4)
        model.train(); tot = n = 0; t0 = time.time()
        for r, k, l in dl:
            lr = LR if step < decay_from else LR * (total - step) / max(total - decay_from, 1)
            for g in opt.base.param_groups:
                g["lr"] = lr
            x, y = batch_xy(r, k, l)
            x = x.cuda(non_blocking=True).to(memory_format=torch.channels_last); y = y.cuda()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss = crit(model(x).float(), y)
            loss.backward(); opt.first(); opt.base.zero_grad()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                crit(model(x).float(), y).backward()
            opt.second(); opt.base.zero_grad()
            tot += float(loss.detach()) * y.size(0); n += y.size(0); step += 1
            if step % 200 == 0:
                print(f"  step {step}/{total} loss {tot / n:.4f} {(time.time() - t0) / (step - (ep - 1) * steps_ep):.3f}s/it",
                      flush=True)
            if a.max_steps and step >= a.max_steps:
                print(f"smoke test ok: {step} steps, {(time.time() - t0) / step:.3f}s/it"); return
        model.eval(); P, S, T = [], [], []
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            for x, y in dl_va:
                pr = torch.softmax(model(x.cuda().to(memory_format=torch.channels_last)).float(), 1).cpu().numpy()
                P.extend(pr.argmax(1).tolist()); S.extend(pr[:, 1].tolist()); T.extend(y.tolist())
        T, S = np.array(T), np.array(S); m = np.isin(T, [0, 1])
        auc = roc_auc_score((T[m] == 1).astype(int), S[m]); f1 = f1_score(T, P, average="macro")
        crit_val = f1 if a.arm in ("HYB", "SUP", "HYBD") else auc   # PRE_DECLARED §2 selection
        rows.append(dict(epoch=ep, loss=tot / n, val_auc=auc, val_macro_f1=f1, minutes=(time.time() - t0) / 60))
        print(f"[{a.arm}][{ep:02d}/{a.epochs}] loss={tot / n:.4f} valAUC={auc:.4f} valF1={f1:.4f} "
              f"({(time.time() - t0) / 60:.1f} min)", flush=True)
        if crit_val > best:
            best = crit_val; torch.save(model.state_dict(), out); print("  -> saved best", flush=True)
    with open(HERE / f"train_{a.arm}{sfx}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    (HERE / f"meta_{a.arm}{sfx}.json").write_text(json.dumps({"arm": a.arm, "best": best, "epochs": a.epochs}, indent=1))
    print(f"[{a.arm}] best {best:.4f} -> {out}\nDONE", flush=True)


if __name__ == "__main__":
    main()
