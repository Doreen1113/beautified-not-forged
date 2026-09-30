"""RU-CLIP (PRE_DECLARED Addendum 3): frozen CLIP ViT-L/14 (openai, 224 px) + LoRA (rank 16 on q/k/v/out of all 24 blocks)
+ the three RU heads on the CLS token (+ optional evidence head on the 16x16 patch tokens); RU3 data and mixture;
AdamW 1e-4, 200-step warm-up then cosine, 8 epochs, batch 16 photographs (48 images), bf16.

python train_ru_clip.py [--head] [--epochs 8] [--workers 12] [--max-steps N] [--seed S]
  -> checkpoints/research/retouch_unified_20260929/ru_clip[e]_s<seed>.pth (LoRA + heads only, base CLIP is not saved)
"""
import argparse
import csv
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import f1_score, roc_auc_score
from torch.utils.data import DataLoader, Dataset
from PIL import Image

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from train_ru import BASE, UNI, CKPT, BATCH, SEED, remap, cap, crop, read_manifest  # noqa: E402
from train_ru3 import RUData3, to_t2, mask_loss  # noqa: E402

CLIP_ID = "openai/clip-vit-large-patch14"


class LoRALinear(nn.Module):
    def __init__(self, base: nn.Linear, r=16, alpha=32):
        super().__init__()
        self.base = base; self.r = r; self.scale = alpha / r
        self.A = nn.Parameter(torch.randn(r, base.in_features) * (1 / math.sqrt(base.in_features)))
        self.B = nn.Parameter(torch.zeros(base.out_features, r))
        for p in self.base.parameters():
            p.requires_grad = False

    def forward(self, x):
        return self.base(x) + F.linear(F.linear(x, self.A), self.B) * self.scale


class RUCLIP(nn.Module):
    def __init__(self, head=False, r=16):
        super().__init__()
        from transformers import CLIPVisionModel
        self.vit = CLIPVisionModel.from_pretrained(CLIP_ID)
        for p in self.vit.parameters():
            p.requires_grad = False
        for layer in getattr(self.vit, "vision_model", self.vit).encoder.layers:   # transformers 5 has no vision_model wrapper
            at = layer.self_attn
            for nm in ("q_proj", "k_proj", "v_proj", "out_proj"):
                setattr(at, nm, LoRALinear(getattr(at, nm), r=r))
        d = self.vit.config.hidden_size
        self.cls, self.pres, self.q = nn.Linear(d, 3), nn.Linear(d, 4), nn.Linear(d, 4)
        self.head = head; self.ev = nn.Linear(d, 1) if head else None
        self.grid = self.vit.config.image_size // self.vit.config.patch_size

    def trainable(self):
        return [p for p in self.parameters() if p.requires_grad]

    def forward(self, x):
        o = self.vit(pixel_values=x); f = o.pooler_output
        out = (self.cls(f), self.pres(f), self.q(f))
        if self.head:
            t = o.last_hidden_state[:, 1:, :]; ev = self.ev(t).transpose(1, 2).reshape(x.shape[0], 1, self.grid, self.grid)
            return out + (ev,)
        return out

    def state_dict_trainable(self):
        return {k: v for k, v in self.state_dict().items() if ("A" in k.split(".")[-1] or "B" in k.split(".")[-1] or k.split(".")[0] in ("cls", "pres", "q", "ev"))}


def load_clip(tag, head=False):
    m = RUCLIP(head=head); sd = torch.load(CKPT / f"ru_{tag}.pth", map_location="cpu")
    missing, unexpected = m.load_state_dict(sd, strict=False)
    assert not unexpected, unexpected[:5]
    assert all(("A" not in k.split(".")[-1] and "B" not in k.split(".")[-1] and k.split(".")[0] not in ("cls", "pres", "q", "ev")) for k in missing), "trainable keys missing"
    return m


class ValClip(Dataset):
    def __init__(self, rows):
        self.rows = rows

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        r = self.rows[i]; rgb = cap(crop(np.array(Image.open(r["path"]).convert("RGB")), r["box"]))[0]
        return to_t2(rgb, 224, False, "clip"), r["cls"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--head", action="store_true"); ap.add_argument("--epochs", type=int, default=8); ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--max-steps", type=int, default=0); ap.add_argument("--seed", type=int, default=SEED); ap.add_argument("--wq", type=float, default=2.0)
    ap.add_argument("--wm", type=float, default=1.0); ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--arm", default="ru3", choices=["ru3", "ru4"])
    a = ap.parse_args()
    torch.manual_seed(a.seed); np.random.seed(a.seed); CKPT.mkdir(parents=True, exist_ok=True)
    tag = f"clip{'e' if a.head else ''}{'4' if a.arm == 'ru4' else ''}_s{a.seed}"
    model = RUCLIP(head=a.head).cuda()
    rows = read_manifest(HERE / "manifest_train.tsv"); vrows = read_manifest(HERE / "manifest_val.tsv")
    ds = RUData3(rows, 224, a.seed, arm=a.arm, head_res=model.grid, norm="clip")
    vf = [l.split("\t") for l in (UNI / "ffpp3_val.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    dl_vf = DataLoader(ValClip([dict(path=remap(r[0]), box=None, cls=int(r[1])) for r in vf]), batch_size=64, num_workers=4)
    dl_vv = DataLoader(ValClip(vrows), batch_size=64, num_workers=4)
    ntr = sum(p.numel() for p in model.trainable()); ntot = sum(p.numel() for p in model.parameters())
    print(f"[{tag}] bases {len(ds):,} | single {len(ds.single):,} | parts {len(ds.parts):,} | trainable {ntr / 1e6:.2f} M of {ntot / 1e6:.1f} M | head {a.head}", flush=True)
    opt = torch.optim.AdamW(model.trainable(), lr=a.lr, weight_decay=0.01)
    steps_ep = len(ds) // BATCH; total = steps_ep * a.epochs; warm = 200

    def lr_at(s):
        return a.lr * s / warm if s < warm else 0.5 * a.lr * (1 + math.cos(math.pi * (s - warm) / max(total - warm, 1)))

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
                pr = torch.softmax(model(x.cuda())[0].float(), 1).cpu().numpy()
                P.extend(pr.argmax(1).tolist()); S.extend(pr[:, 1].tolist()); T.extend(y.tolist())
        return np.array(P), np.array(S), np.array(T)

    best, log, step, out = -1.0, [], 0, CKPT / f"ru_{tag}.pth"
    for ep in range(1, a.epochs + 1):
        ds.epoch = ep
        dl = DataLoader(ds, batch_size=BATCH, shuffle=True, num_workers=a.workers, pin_memory=True, drop_last=True, persistent_workers=False, prefetch_factor=3)
        model.train(); acc = np.zeros(5); n = 0; t0 = time.time()
        for batch in dl:
            for g in opt.param_groups:
                g["lr"] = lr_at(step)
            x = batch[0].flatten(0, 1).cuda(non_blocking=True); y, pres, mpres, q, mq, m, mm = [t.flatten(0, 1).cuda() for t in batch[1:]]
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss, parts = loss_fn(model(x), y, pres, mpres, q, mq, m, mm)
            opt.zero_grad(set_to_none=True); loss.backward(); torch.nn.utils.clip_grad_norm_(model.trainable(), 1.0); opt.step()
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
            best = crit; torch.save(model.state_dict_trainable(), out); print("  -> saved best", flush=True)
        with open(HERE / f"train_ru_{tag}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(log[0])); w.writeheader(); w.writerows(log)
    (HERE / f"meta_ru_{tag}.json").write_text(json.dumps({"arm": "clip", "head": a.head, "best": best, "epochs": a.epochs, "seed": a.seed, "trainable_M": ntr / 1e6, "total_M": ntot / 1e6}, indent=1))
    print(f"[{tag}] best {best:.4f} -> {out}\nDONE", flush=True)


if __name__ == "__main__":
    main()
