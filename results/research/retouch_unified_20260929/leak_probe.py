"""Does beautification evidence pull forgeries out of the fake class? VALIDATION DATA ONLY (PRE_DECLARED Addendum 6).

Audit of 2026-10-05: on Celeb-DF-B, 19.5 % of beautified deepfakes are called *filter* by clipe4 and were not counted as
missed. Two controlled probes on data no model selection has touched as a test set:

 A. Unseen colour filters on forgeries. FF++ validation frames (530 real, 529 observed forgeries); each gets one of the
    eleven pilgram filters that training never uses (fixed by a seed). Compared with the same frames unfiltered.
 B. Commercial retouching on forgeries. For the held-out Tencent / Megvii bases: the original x0, its single-operation
    component C (tone or texture, above the noise floor), a self-blend forgery F of x0, and F + (C - x0), i.e. the same
    commercial edit applied to the forged version of the same photograph (the components are pixel-aligned with x0, so
    the photometric edit transfers additively).

Per set: share called real / fake / filter (argmax), mean P(fake), and the share with P(fake) > P(real) (the forgery
decision that ignores the filter class).

python leak_probe.py [tag ...] -> leak_probe.json
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pilgram
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from train_ru import UNI, CKPT, read_manifest, remap, crop, self_blend  # noqa: E402
from train_ru3 import RUNet3, FLOOR, to_t2  # noqa: E402
B = Path(r"C:\My_Project\AIGC"); ORIG = B / "ffhq_originals/Part7"
HELDOUT = ["brooklyn", "clarendon", "earlybird", "inkwell", "kelvin", "lofi", "mayfair", "moon", "perpetua", "reyes", "slumber"]
OPS = ["eye", "jaw", "white", "smooth"]


def build_a():
    r = [l.split("\t") for l in (UNI / "ffpp3_val.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    rng = np.random.default_rng(20261005); out = []
    for p, y, *_ in r:
        if y == "2":
            continue
        out.append((remap(p), "real" if y == "0" else "fake", HELDOUT[int(rng.integers(0, len(HELDOUT)))]))
    return out


def build_b():
    lmz = np.load(HERE / "ffhq_landmarks.npz"); rows = []
    for v in read_manifest(HERE / "manifest_val.tsv"):
        if v["src"] != "vendor_single":
            continue
        j = int(np.argmax(v["pres"]))
        if OPS[j] not in ("white", "smooth") or v["q"] is None or v["q"][j] < FLOOR[OPS[j]] or v["stem"] not in lmz.files:
            continue
        rows.append((v["path"], v["box"], v["stem"], OPS[j]))
    return rows, lmz


class DSA(Dataset):
    def __init__(self, items, filt, size, norm):
        self.items, self.filt, self.size, self.norm = items, filt, size, norm

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        p, _, f = self.items[i]; im = Image.open(p).convert("RGB")
        if self.filt:
            im = getattr(pilgram, f)(im).convert("RGB")
        return to_t2(np.array(im), self.size, False, self.norm), i


class DSB(Dataset):
    """Returns the four versions of one base: x0, component, self-blend forgery, forgery + the component's edit."""
    def __init__(self, rows, lmz, size, norm):
        self.rows, self.lm, self.size, self.norm = rows, {k: lmz[k] for k in lmz.files}, size, norm

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        path, box, stem, _ = self.rows[i]
        c = np.array(Image.open(path).convert("RGB")); o = np.array(Image.open(ORIG / f"{stem}.png").convert("RGB")); s = c.shape[0] / o.shape[0]
        if o.shape[:2] != c.shape[:2]:
            o = cv2.resize(o, (c.shape[1], c.shape[0]), interpolation=cv2.INTER_AREA)
        c, x0 = crop(c, box), crop(o, box); lm = self.lm[stem].copy() * s; lm[:, 0] -= box[0]; lm[:, 1] -= box[1]
        rng = np.random.default_rng(20261005 + i); f = None
        for _ in range(6):
            f = self_blend(x0, lm, rng)
            if f is not None:
                break
        ok = f is not None
        if not ok:
            f = x0.copy()
        fd = np.clip(f.astype(np.int16) + (c.astype(np.int16) - x0.astype(np.int16)), 0, 255).astype(np.uint8)
        return torch.stack([to_t2(im, self.size, False, self.norm) for im in (x0, c, f, fd)]), i, ok


@torch.no_grad()
def predict(model, dl, n, k=1):
    P = np.zeros((n, k, 3), np.float32); OK = np.ones(n, bool)
    for batch in dl:
        x, i = batch[0], batch[1]
        if len(batch) == 3:
            OK[i.numpy()] = batch[2].numpy()
        b = x.shape[0]; x = x.view(-1, *x.shape[-3:]).cuda()
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lo = model(x)[0]
        P[i.numpy()] = torch.softmax(lo.float(), 1).cpu().numpy().reshape(b, k, 3)
    return P, OK


def summ(P):
    am = P.argmax(1)
    return {"n": int(len(P)), "real": round(100 * float((am == 0).mean()), 1), "fake": round(100 * float((am == 1).mean()), 1),
            "filter": round(100 * float((am == 2).mean()), 1), "mean_p_fake": round(float(P[:, 1].mean()), 3),
            "fake_over_real": round(100 * float((P[:, 1] > P[:, 0]).mean()), 1)}


def load(tag):
    if tag.startswith("clip"):
        from train_ru_clip import load_clip
        return load_clip(tag, head=True).cuda().eval(), 224, "clip"
    m = RUNet3("effb4", head=True); m.load_state_dict(torch.load(CKPT / f"ru_{tag}.pth", map_location="cpu")); return m.cuda().eval(), 380, "half"


def main():
    tags = sys.argv[1:] or ["clipe4_s20260929", "clipe4r_s20260929", "ru4e_effb4_s20260929"]
    A = build_a(); Brows, lmz = build_b(); ya = np.array([x[1] for x in A]); opb = np.array([x[3] for x in Brows])
    print(f"A: {len(A)} FF++ val frames ({int((ya == 'real').sum())} real, {int((ya == 'fake').sum())} fake) | B: {len(Brows)} components "
          f"({int((opb == 'white').sum())} tone, {int((opb == 'smooth').sum())} texture)", flush=True)
    f = HERE / "leak_probe.json"; out = json.loads(f.read_text()) if f.is_file() else {}
    for tag in tags:
        model, size, norm = load(tag); res = {"A_unseen_colour_filters": {}, "B_commercial_edit_on_forgery": {}}
        for filt in (False, True):
            P, _ = predict(model, DataLoader(DSA(A, filt, size, norm), batch_size=48, num_workers=6), len(A)); P = P[:, 0]
            for y in ("real", "fake"):
                res["A_unseen_colour_filters"][f"{y}{' + unseen filter' if filt else ''}"] = summ(P[ya == y])
        P, OK = predict(model, DataLoader(DSB(Brows, lmz, size, norm), batch_size=12, num_workers=6), len(Brows), k=4)
        for op in ("smooth", "white"):
            m = (opb == op) & OK; nm = {"smooth": "texture", "white": "tone"}[op]
            for k, lab in enumerate(("original", f"{nm} component (filter)", "self-blend forgery", f"forgery + {nm} edit")):
                res["B_commercial_edit_on_forgery"][f"{nm}: {lab}"] = summ(P[m, k])
        out[tag] = res; f.write_text(json.dumps(out, indent=1)); print(tag, json.dumps(res, indent=1), flush=True)
        del model; torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
