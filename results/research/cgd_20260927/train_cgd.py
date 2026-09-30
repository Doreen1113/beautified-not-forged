"""CGD training (PRE_DECLARED §1, §4). Three arms on identical data / backbone / recipe:

  HYBPE : HYB-F recipe + part edits in the fake pool, no evidence head           (detection baseline)
  MASK  : + evidence head trained with BCE+Dice on exact masks                    (explanation baseline)
  CGD   : + restoration-consistency loss through the classifier's own counterfactual

Per training photograph and step: real / filter / fake triplet. Filter = on-the-fly beautification (cf exact) or an
observed ffpp3_train filter frame (cf exact, mask = |x - x0| > 6). Fake = self-blend (cf exact, mask = blend mask),
part edit from partedit manifests (cf exact = source frame, mask exact), or observed FF++ forgery (cf approximate when
the target-video real frame exists, else none; never a mask target). Half of the fakes are beautified on top.
The common photometric jitter and crop are shared by x, x0 and the mask.

python train_cgd.py --arm CGD [--seed 20260928] [--workers 12]
  -> checkpoints/research/cgd_20260927/cgd_<ARM>_s<seed>.pth, train_<ARM>_s<seed>.csv
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
from torchvision import transforms

BASE = Path(os.environ.get("AIGC_BASE", r"C:\My_Project\AIGC"))
HERE = Path(__file__).resolve().parent
UNI = BASE / "results/research/ffpp_unified_20260925"
FASB = BASE / "results/research/fasb_20260926"
PE = BASE / "results/research/partedit_20260927"
CKPT = BASE / "checkpoints/research/cgd_20260927"
for p_ in (FASB, BASE, BASE / "results/research/sbifix_20260927"):
    sys.path.insert(0, str(p_))
from fasb import beautify  # noqa: E402
from sbi.sbi_generator import blend_mask, common_transforms, rand_affine, random_hull, source_transforms  # noqa: E402
from sbi_faithful import elastic_mask  # noqa: E402
from train_sbifix import sym_degrade  # noqa: E402  symmetric blur/downscale (sbifix Addendum 2)

MODEL, SIZE, BATCH, LR, RHO, SEED = "tf_efficientnet_b4.ap_in1k", 380, 16, 1e-3, 0.05, 20260928
TAU, DELTA, LAM_RES, LAM_MASK, LAM_AREA, N_RES = 0.3, 0.2, 1.0, 1.0, 0.02, 16
NORM = transforms.Normalize([0.5] * 3, [0.5] * 3)
REAL_DIRS = [BASE / "FaceForensics_protocol_frames/train/real", BASE / "FaceForensics_protocol_frames_dense/train/real"]


def remap(p):
    return p if os.name == "nt" else p.replace("C:\\My_Project\\AIGC", str(BASE)).replace("\\", "/")


def real_frame_for(path, y):
    b = os.path.basename(path)
    vid, fr = (b.split("__")[:2] if y == 2 else (b.split("_")[0], b.split("__")[1].replace(".jpg", "")))
    for R in REAL_DIRS:
        q = R / f"{vid}__{fr}.jpg"
        if q.is_file():
            return q
    return None


def self_blend_with_mask(img, lm, rng):
    m, _ = random_hull(lm, img.shape, rng)
    if m is None or m.sum() < 16:
        return None, None
    if rng.random() < 0.5:
        src, _ = source_transforms(img.copy(), rng); tgt = img
    else:
        tgt, _ = source_transforms(img.copy(), rng); src = img
    src, m, _ = rand_affine(src, m, rng)
    m = elastic_mask(m, rng)
    mb, _ = blend_mask(m, rng)
    if mb is None:
        return None, None
    mb = mb * float(rng.choice([0.25, 0.5, 0.75, 1.0, 1.0, 1.0]))
    out = np.clip(mb[..., None] * src.astype(np.float32) + (1 - mb[..., None]) * tgt.astype(np.float32), 0, 255).astype(np.uint8)
    return out, (mb > 0.05)


def diff_mask(x, x0, thr=6.0):
    return np.abs(x.astype(np.float32) - x0.astype(np.float32)).max(2) > thr


_K25 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))


def footprint(x, x0):
    """True edit footprint (Addendum 2): changed pixels dilated by the feather width, at native crop resolution."""
    return cv2.dilate(diff_mask(x, x0).astype(np.uint8), _K25).astype(bool)


def to_t(rgb, flip):
    im = Image.fromarray(rgb).resize((SIZE, SIZE), Image.BILINEAR)
    return NORM(transforms.functional.to_tensor(im.transpose(Image.FLIP_LEFT_RIGHT) if flip else im))


def mask_t(m, flip):
    if m is None:
        return torch.zeros(1, SIZE, SIZE)
    t = torch.from_numpy(cv2.resize(m.astype(np.float32), (SIZE, SIZE), interpolation=cv2.INTER_AREA))[None]
    return t.flip(-1) if flip else t


class Item:
    """One training image with its counterfactual bookkeeping."""

    def __init__(self, x, y, x0=None, m=None, exact=False, approx=False):
        self.x, self.y, self.x0, self.m, self.exact, self.approx = x, y, x0, m, exact, approx


def shared_jitter(items, rng):
    """Same common transform (colour + JPEG) and same crop for every image and mask of a photograph's items."""
    seed = int(rng.integers(0, 2 ** 31 - 1))
    h, w = items[0].x.shape[:2]
    t, b, l, r = (rng.uniform(0, 0.06, 4) * np.array([h, h, w, w])).astype(int)
    out = []
    for it in items:
        x = common_transforms(it.x, np.random.default_rng(seed))[0][t:h - b, l:w - r]
        x0 = None if it.x0 is None else common_transforms(it.x0, np.random.default_rng(seed))[0][t:h - b, l:w - r]
        m = None if it.m is None else it.m[t:h - b, l:w - r]
        out.append(Item(np.ascontiguousarray(x), it.y, None if x0 is None else np.ascontiguousarray(x0), m, it.exact, it.approx))
    return out


class OnTheFly(Dataset):
    def __init__(self, seed, degrade=False):
        self.degrade = degrade
        z = np.load(FASB / "landmarks_train.npz")
        self.stems = sorted(z.files); self.lm = None   # loaded lazily inside each worker (keeps the pickled dataset small)
        self.root = BASE / "FaceForensics_protocol_frames_dense/train/real"
        rows = [l.split("\t") for l in (UNI / "ffpp3_train.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
        self.obs_fake = [remap(r[0]) for r in rows if r[1] == "1"]
        self.obs_filt = [remap(r[0]) for r in rows if r[1] == "2"]
        self.seed, self.epoch = seed, 0
        self.pe = []
        self.reload_partedits()

    def reload_partedits(self):
        pe = []
        for mech in ("donor", "sd"):
            f = PE / f"manifest_train_{mech}.tsv"
            if f.is_file():
                for l in f.read_text(encoding="utf-8").splitlines()[1:]:
                    c = l.split("\t")
                    if len(c) >= 6:
                        pe.append((remap(c[0]), remap(c[4]), remap(c[5])))
        self.pe = pe

    def __len__(self):
        return len(self.stems)

    def _load(self, p):
        return np.array(Image.open(p).convert("RGB"))

    def _fit(self, x0, x):
        return x0 if x0.shape == x.shape else cv2.resize(x0, (x.shape[1], x.shape[0]), interpolation=cv2.INTER_LINEAR)

    def __getitem__(self, i):
        stem = self.stems[i]
        ep = self.epoch_shared.value if hasattr(self, "epoch_shared") else self.epoch
        rng = np.random.default_rng((self.seed * 1000003 + ep * 100003 + i) % (2 ** 63))
        if self.lm is None:
            z = np.load(FASB / "landmarks_train.npz"); self.lm = {k: z[k][:, :2].astype(np.float32) for k in z.files}
        img = self._load(self.root / f"{stem}.jpg"); lm = self.lm[stem]
        real = Item(img, 0, x0=img, m=np.zeros(img.shape[:2], bool), exact=True)
        # ---- filter
        if rng.random() < 0.5:
            fx = beautify(img, rng); filt = Item(fx, 2, x0=img, m=diff_mask(fx, img), exact=True)
        else:
            p = self.obs_filt[int(rng.integers(0, len(self.obs_filt)))]; fx = self._load(p)
            q = real_frame_for(p, 2); x0 = self._fit(self._load(q), fx) if q else None
            filt = Item(fx, 2, x0=x0, m=diff_mask(fx, x0) if x0 is not None else None, exact=x0 is not None)
        # ---- fake
        u = rng.random(); fake = None
        if u < 1 / 3 or (u < 2 / 3 and not self.pe):
            for _ in range(4):
                sb, mb = self_blend_with_mask(img, lm, rng)
                if sb is not None:
                    fake = Item(sb, 1, x0=img, m=mb, exact=True); break
        elif u < 2 / 3:
            p, mp, sp = self.pe[int(rng.integers(0, len(self.pe)))]
            fx = self._load(p); x0 = self._fit(self._load(sp), fx)
            fake = Item(fx, 1, x0=x0, m=footprint(fx, x0), exact=True)
        if fake is None:
            p = self.obs_fake[int(rng.integers(0, len(self.obs_fake)))]; fx = self._load(p)
            q = real_frame_for(p, 1)
            fake = Item(fx, 1, x0=self._fit(self._load(q), fx) if q else None, m=None, exact=False, approx=q is not None)
        if rng.random() < 0.5:                      # compositional: beautified forgery stays fake
            fake.x = beautify(fake.x, rng)
        if self.degrade:   # same blur/downscale on x AND x0 of every item, so restoration never re-introduces sharpness
            for it in (real, filt, fake):
                pair = sym_degrade([it.x] + ([it.x0] if it.x0 is not None else []), rng)
                it.x = pair[0]
                if it.x0 is not None:
                    it.x0 = pair[1]
        items = shared_jitter([real, filt, fake], rng)
        flip = bool(rng.random() < 0.5)
        X = torch.stack([to_t(it.x, flip) for it in items])
        X0 = torch.stack([to_t(it.x0 if it.x0 is not None else it.x, flip) for it in items])
        M = torch.stack([mask_t(it.m, flip) for it in items])
        has_cf = torch.tensor([it.x0 is not None for it in items])
        exact = torch.tensor([it.exact for it in items]); approx = torch.tensor([it.approx for it in items])
        return X, X0, M, torch.tensor([0, 2, 1]), has_cf, exact, approx


class ValDS(Dataset):
    def __init__(self, rows):
        self.rows = rows; self.tf = transforms.Compose([transforms.Resize((SIZE, SIZE)), transforms.ToTensor(), NORM])

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        p, y = self.rows[i]; return self.tf(Image.open(p).convert("RGB")), y


class CGDNet(nn.Module):
    def __init__(self, head):
        super().__init__()
        self.m = timm.create_model(MODEL, pretrained=True, num_classes=3)
        self.head = head
        if head:
            self.ev = nn.Conv2d(self.m.num_features, 1, 1)

    def forward(self, x):
        f = self.m.forward_features(x)
        lo = self.m.forward_head(f)
        return (lo, self.ev(f)) if self.head else (lo, None)


class SAM:
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


def dice(pred, tgt, eps=1.0):
    pred = pred.flatten(1); tgt = tgt.flatten(1)
    return 1 - (2 * (pred * tgt).sum(1) + eps) / (pred.sum(1) + tgt.sum(1) + eps)


def losses(net, arm, X, X0, M, Y, has_cf, exact, approx):
    lo, ev = net(X)
    out = {"ce": F.cross_entropy(lo, Y)}
    if not net.head:
        return out
    mh = torch.sigmoid(ev)                                       # (B,1,12,12)
    tgt = F.adaptive_avg_pool2d(M, mh.shape[-2:])
    if exact.any():
        out["mask"] = (F.binary_cross_entropy_with_logits(ev[exact].float(), tgt[exact].float())
                       + dice(mh[exact].float(), tgt[exact].float()).mean())
    if arm == "CGD" and has_cf.any():
        idx = torch.nonzero(has_cf & (Y != 0)).flatten()         # edited items with a counterfactual
        if len(idx) > N_RES:
            idx = idx[torch.randperm(len(idx), device=idx.device)[:N_RES]]
        if len(idx):
            mu = F.interpolate(mh[idx], size=X.shape[-2:], mode="bilinear", align_corners=False)
            x, x0, y = X[idx], X0[idx], Y[idx]
            x_up = (1 - mu) * x + mu * x0                          # claimed region restored -> edit should vanish
            x_dn = mu * x + (1 - mu) * x0                          # everything else restored -> edit should remain
            p_up = torch.softmax(net(x_up)[0], 1).gather(1, y[:, None])[:, 0]
            p_dn = torch.softmax(net(x_dn)[0], 1).gather(1, y[:, None])[:, 0]
            p_x = torch.softmax(lo[idx], 1).gather(1, y[:, None])[:, 0].detach()
            w = torch.where(approx[idx], 0.5, 1.0)
            out["res"] = (w * (F.relu(p_up - TAU) + F.relu(p_x - DELTA - p_dn))).mean()
            out["area"] = mh[idx].mean()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["HYBPE", "MASK", "CGD"])
    ap.add_argument("--epochs", type=int, default=14)
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--degrade", action="store_true", help="symmetric degradation (arm suffix D)")
    ap.add_argument("--resume-epoch", type=int, default=0, help="reload the saved checkpoint and continue from this epoch (optimizer state not restored)")
    a = ap.parse_args()
    torch.manual_seed(a.seed); np.random.seed(a.seed)
    CKPT.mkdir(parents=True, exist_ok=True)
    ds = OnTheFly(a.seed, degrade=a.degrade)
    arm_name = a.arm + ("D" if a.degrade else "")
    print(f"[{a.arm}] photos {len(ds):,} | observed fake {len(ds.obs_fake):,} filter {len(ds.obs_filt):,} | part edits {len(ds.pe):,}", flush=True)
    vr = [l.split("\t") for l in (UNI / "ffpp3_val.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    dl_va = DataLoader(ValDS([(remap(r[0]), int(r[1])) for r in vr]), batch_size=64, num_workers=4)
    net = CGDNet(head=a.arm != "HYBPE").cuda().to(memory_format=torch.channels_last)
    opt = SAM(net.parameters(), RHO)
    steps_ep = len(ds) // BATCH; total = steps_ep * a.epochs; decay_from = int(total * 0.75)
    out = CKPT / f"cgd_{arm_name}_s{a.seed}.pth"; best, rows, step = -1.0, [], 0
    start_ep = 1
    if a.resume_epoch:
        net.load_state_dict(torch.load(out, map_location="cpu")); start_ep = a.resume_epoch; step = (start_ep - 1) * steps_ep
        print(f"[{arm_name}] resumed weights from {out}, continuing at epoch {start_ep} (step {step})", flush=True)

    def total_loss(L):
        return L["ce"] + LAM_MASK * L.get("mask", 0) + LAM_RES * L.get("res", 0) + LAM_AREA * L.get("area", 0)

    # persistent workers: epoch-2 worker respawn hung on Windows (2026-09-28); the epoch index reaches workers through
    # a shared value so fresh randomness per epoch is kept. Part-edit manifests are read once at start.
    import multiprocessing as mp_
    ds.epoch_shared = mp_.Value("i", 0)
    dl = DataLoader(ds, batch_size=BATCH, shuffle=True, num_workers=a.workers, pin_memory=True, drop_last=True,
                    prefetch_factor=2, persistent_workers=True)
    for ep in range(start_ep, a.epochs + 1):
        ds.epoch_shared.value = ep
        net.train(); agg = {}; n = 0; t0 = time.time()
        for X, X0, M, Y, hc, ex, apx in dl:
            lr = LR if step < decay_from else LR * (total - step) / max(total - decay_from, 1)
            for g in opt.base.param_groups:
                g["lr"] = lr
            X, X0, M, Y = (t.flatten(0, 1).cuda(non_blocking=True) for t in (X, X0, M, Y))
            hc, ex, apx = (t.flatten().cuda() for t in (hc, ex, apx))
            X = X.to(memory_format=torch.channels_last)
            with torch.autocast("cuda", dtype=torch.bfloat16):
                L = losses(net, a.arm, X, X0, M, Y, hc, ex, apx); loss = total_loss(L)
            loss.backward(); opt.first(); opt.base.zero_grad()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                total_loss(losses(net, a.arm, X, X0, M, Y, hc, ex, apx)).backward()
            opt.second(); opt.base.zero_grad()
            for k, v in L.items():
                agg[k] = agg.get(k, 0.0) + float(v.detach())
            n += 1; step += 1
            if step % 200 == 0:
                print(f"  step {step}/{total} " + " ".join(f"{k}={v / n:.4f}" for k, v in agg.items()) + f" {(time.time() - t0) / n:.3f}s/it", flush=True)
            if a.max_steps and step >= a.max_steps:
                print(f"smoke ok {(time.time() - t0) / n:.3f}s/it"); return
        net.eval(); P, T = [], []
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            for x, y in dl_va:
                P.extend(net(x.cuda().to(memory_format=torch.channels_last))[0].float().argmax(1).cpu().tolist()); T.extend(y.tolist())
        f1 = f1_score(T, P, average="macro")
        rows.append(dict(epoch=ep, **{k: v / n for k, v in agg.items()}, val_macro_f1=f1, minutes=(time.time() - t0) / 60, n_partedits=len(ds.pe)))
        print(f"[{a.arm}][{ep:02d}/{a.epochs}] " + " ".join(f"{k}={v / n:.4f}" for k, v in agg.items()) + f" valF1={f1:.4f} pe={len(ds.pe):,} ({(time.time() - t0) / 60:.1f} min)", flush=True)
        if f1 > best:
            best = f1; torch.save(net.state_dict(), out); print("  -> saved best", flush=True)
    with open(HERE / f"train_{arm_name}_s{a.seed}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=sorted({k for r in rows for k in r})); w.writeheader(); w.writerows(rows)
    (HERE / f"meta_{arm_name}_s{a.seed}.json").write_text(json.dumps({"arm": a.arm, "best": best, "epochs": a.epochs}, indent=1))
    print(f"[{a.arm}] best {best:.4f} -> {out}\nDONE", flush=True)


if __name__ == "__main__":
    main()
