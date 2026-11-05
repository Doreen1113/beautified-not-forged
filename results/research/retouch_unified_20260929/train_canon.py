"""Train the canonicaliser (PRE_DECLARED Addendum 20) on FF++ train frames, self-supervised with the beautification operator.

Loss per batch: L1(canon(B(x0;u)), x0) for a random edit u drawn from the plausible pool (half) or from N(0,1) in the wide
bounds (half), plus L1(canon(x0), x0) so that an untreated frame is left alone. Validation on FF++ val frames: PSNR to the
original (i) before and after canonicalisation of random edits, (ii) of the eleven held-out pilgram filters (never used in
training: a generalisation check), (iii) identity PSNR on untreated frames.
python train_canon.py [--steps N] -> checkpoints/.../canon_s<seed>.pth, train_canon.log/json
"""
import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pilgram
import torch
import torch.nn.functional as F
from PIL import Image
from torch.utils.data import DataLoader, Dataset

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import adv_beauty as AB
from canon import Canon
from leak_probe import HELDOUT
from train_ru import CKPT, UNI, remap

R = 224


class Frames(Dataset):
    def __init__(self, paths, filt=None):
        self.paths, self.filt = paths, filt

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, i):
        im = Image.open(self.paths[i]).convert("RGB").resize((R, R), Image.BILINEAR)
        x0 = torch.from_numpy(np.asarray(im, np.float32) / 255.0).permute(2, 0, 1)
        if self.filt is None:
            return x0
        rng = np.random.default_rng(i); f = HELDOUT[int(rng.integers(0, len(HELDOUT)))]
        xf = torch.from_numpy(np.asarray(getattr(pilgram, f)(im).convert("RGB"), np.float32) / 255.0).permute(2, 0, 1)
        return x0, xf


def psnr(a, b):
    return (-10 * torch.log10(((a - b) ** 2).mean((1, 2, 3)) + 1e-10)).mean().item()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--steps", type=int, default=6000); ap.add_argument("--seed", type=int, default=20260929); ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args(); torch.manual_seed(a.seed); np.random.seed(a.seed)
    AB.WIDE = True; AB.load_prior(HERE / "fit_operator_prior_wide.npz", "cuda")
    tr = [remap(l.split("\t")[0]) for l in (UNI / "ffpp3_train.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip() and l.split("\t")[1] in ("0", "1")]
    va = [remap(l.split("\t")[0]) for l in (UNI / "ffpp3_val.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip() and l.split("\t")[1] in ("0", "1")]
    rng = np.random.default_rng(a.seed); va = [va[i] for i in rng.choice(len(va), 400, False)]
    dl = DataLoader(Frames(tr), batch_size=48, shuffle=True, num_workers=a.workers, drop_last=True, persistent_workers=True)
    dv = DataLoader(Frames(va, filt=True), batch_size=50, num_workers=0)
    net = Canon().cuda(); opt = torch.optim.AdamW(net.parameters(), lr=3e-4, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=3e-4, total_steps=a.steps, pct_start=0.1)
    log = []; step = 0; t0 = time.time(); run = 0.0

    def evaluate():
        net.eval(); P = {"edit_before": [], "edit_after": [], "photometric_before": [], "photometric_after": [], "filter_before": [], "filter_after": [], "identity": []}
        with torch.no_grad():
            for x0, xf in dv:
                x0, xf = x0.cuda(), xf.cuda(); torch.manual_seed(0); noise = torch.zeros(x0.shape[0], 1, R, R, device="cuda")
                u = {k: v.detach() for k, v in AB.prior_start(x0.shape[0], "cuda").items()}; xe = AB.apply(x0, u, noise)
                P["edit_before"].append(psnr(xe, x0)); P["edit_after"].append(psnr(net.canon01(xe), x0))
                up = dict(u, smooth=torch.full_like(u["smooth"], -6.0), grain=torch.full_like(u["grain"], -6.0)); xp = AB.apply(x0, up, noise)   # invertible part only
                P["photometric_before"].append(psnr(xp, x0)); P["photometric_after"].append(psnr(net.canon01(xp), x0))
                P["filter_before"].append(psnr(xf, x0)); P["filter_after"].append(psnr(net.canon01(xf), x0)); P["identity"].append(psnr(net.canon01(x0), x0))
        net.train(); return {k: round(float(np.mean(v)), 2) for k, v in P.items()}

    while step < a.steps:
        for x0 in dl:
            x0 = x0.cuda(non_blocking=True); n = x0.shape[0]; noise = torch.zeros(n, 1, R, R, device="cuda")
            with torch.no_grad():
                up = AB.prior_start(n // 2, "cuda"); ur = AB.init_params(n - n // 2, "cuda")
                u = {k: torch.cat([up[k].detach(), ur[k].detach()]) for k in up}
                xe = AB.apply(x0, u, noise)
            ye, ue = net.canon01(xe, return_params=True)
            lp = sum(F.mse_loss(torch.sigmoid(ue[k]), torch.sigmoid(u[k])) for k in ("gamma", "gain", "lift", "M", "sat", "con", "field", "tint"))   # parameter loss, effective scale
            loss = F.l1_loss(ye, x0) + 0.5 * F.l1_loss(net.canon01(x0), x0) + lp
            opt.zero_grad(); loss.backward(); opt.step(); sched.step(); step += 1; run = 0.98 * run + 0.02 * loss.item() if step > 1 else loss.item()
            if step % 200 == 0:
                print(f"  step {step}/{a.steps} loss {run:.4f} {(time.time() - t0) / step:.3f}s/it", flush=True)
            if step % 1000 == 0 or step == a.steps:
                ev = evaluate(); ev["step"] = step; log.append(ev); print(json.dumps(ev), flush=True)
            if step >= a.steps:
                break
    torch.save(net.state_dict(), CKPT / f"canon_s{a.seed}.pth"); (HERE / f"train_canon_s{a.seed}.json").write_text(json.dumps(log, indent=1)); print("DONE")


if __name__ == "__main__":
    main()
