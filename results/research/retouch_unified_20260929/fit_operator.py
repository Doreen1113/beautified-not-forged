"""Fit the beautification operator to measured edits (PRE_DECLARED Addendum 17 B). No training.

Families (training split only): Tencent and Megvii retouching pairs (FFHQ original -> vendor output, manifest_train.tsv), the
training pilgram filters (fasb.PILGRAM_TRAIN) and random_grade looks on FF++ train frames. For every pair the parameters u of
adv_beauty.apply are fitted by Adam (grain fixed off, noise zero) from the identity point. Reported per family: PSNR before
and after the fit (what the operator explains; the residual of the vendor pairs is skin smoothing and geometry), the 1st /
50th / 99th percentile of each effective parameter, and a diagonal Gaussian (mu, sigma) of u in the unconstrained space.
python fit_operator.py  -> fit_operator.json, fit_operator_prior.npz, FIT_OPERATOR.md
"""
import json
import sys
from pathlib import Path

import numpy as np
import pilgram
import torch
import torch.nn.functional as F
from PIL import Image

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent / "fasb_20260926"))
import adv_beauty as AB
from train_ru import UNI, crop, read_manifest, remap
from train_ru3 import ORIG
from train_ru5 import random_grade
from fasb import PILGRAM_TRAIN   # after train_ru3, which puts the sbi package on the path

N_PER = 1000; R = 224; STEPS = 300; LR = 0.05
IDENT_FIELD = {False: 0.47, True: 0.318}   # identity of the luminance field under the two bound sets
IDENT = {"gamma": -0.405, "gain": 0.0, "lift": 0.0, "M": 0.0, "sat": 0.357, "con": 0.0, "field": 0.47, "tint": 0.0, "smooth": -6.0, "grain": -6.0}


def to_t(im):
    return torch.from_numpy(np.asarray(Image.fromarray(im).resize((R, R), Image.BILINEAR), np.float32) / 255.0).permute(2, 0, 1)


def vendor_pairs(rows, src, rng):
    rows = [r for r in rows if r["src"] == src]; rows = [rows[i] for i in rng.choice(len(rows), min(N_PER, len(rows)), False)]; X, Y = [], []
    for r in rows:
        y = np.array(Image.open(r["path"]).convert("RGB")); o = np.array(Image.open(ORIG / f"{r['stem']}.png").convert("RGB"))
        if o.shape[:2] != y.shape[:2]:
            o = np.asarray(Image.fromarray(o).resize((y.shape[1], y.shape[0]), Image.BOX))
        X.append(to_t(crop(o, r["box"]))); Y.append(to_t(crop(y, r["box"])))
    return torch.stack(X), torch.stack(Y)


def filter_pairs(frames, fam, rng):
    X, Y = [], []
    for p in frames:
        im = Image.open(p).convert("RGB"); a = np.array(im)
        b = random_grade(a, rng) if fam == "random_grade" else np.array(getattr(pilgram, PILGRAM_TRAIN[int(rng.integers(0, len(PILGRAM_TRAIN)))])(im).convert("RGB"))
        X.append(to_t(a)); Y.append(to_t(b))
    return torch.stack(X), torch.stack(Y)


def psnr(a, b):
    return (-10 * torch.log10(((a - b) ** 2).mean((1, 2, 3)) + 1e-10)).cpu().numpy()


def fit(X, Y):
    """Returns the fitted u (dict of tensors, detached), PSNR before, PSNR after."""
    X, Y = X.cuda(), Y.cuda(); n = X.shape[0]; noise = torch.zeros(n, 1, R, R, device="cuda")
    ident = dict(IDENT, field=IDENT_FIELD[AB.WIDE])
    u = {k: torch.full_like(v, ident[k]).requires_grad_(True) for k, v in AB.init_params(n, "cuda", 0.0).items()}
    opt = torch.optim.Adam([v for k, v in u.items() if k != "grain"], lr=LR)
    for _ in range(STEPS):
        opt.zero_grad(); loss = ((AB.apply(X, u, noise) - Y) ** 2).mean((1, 2, 3)).sum(); loss.backward(); opt.step()
    with torch.no_grad():
        return {k: v.detach() for k, v in u.items()}, psnr(X, Y), psnr(AB.apply(X, u, noise), Y)


def effective(u):
    s = torch.sigmoid
    bd = AB.bounds()
    return {"gamma": (0.6 + 1.0 * s(u["gamma"])).flatten(1), "gain": (0.8 + 0.4 * s(u["gain"])).flatten(1), "lift": (-0.08 + 0.16 * s(u["lift"])).flatten(1),
            "offdiag_M": (bd["M"] * torch.tanh(u["M"]) * (1 - torch.eye(3, device=u["M"].device))).abs().amax((1, 2))[:, None],
            "saturation": (1.7 * s(u["sat"])).flatten(1), "contrast": (0.7 + 0.7 * s(u["con"])).flatten(1),
            "field_min": (bd["fld0"] + bd["fld"] * s(u["field"])).amin((1, 2, 3))[:, None], "field_max": (bd["fld0"] + bd["fld"] * s(u["field"])).amax((1, 2, 3))[:, None],
            "tint_span": ((bd["tint0"] + bd["tint"] * s(u["tint"])).amax((2, 3)) - (bd["tint0"] + bd["tint"] * s(u["tint"])).amin((2, 3))).amax(1)[:, None],
            "smooth_weight": (bd["smooth"] * s(u["smooth"] - 1.0)).flatten(1)}


def main():
    wide = "--wide" in sys.argv; AB.WIDE = wide; sfx = "_wide" if wide else ""
    rng = np.random.default_rng(20261007); rows = read_manifest(HERE / "manifest_train.tsv")
    tr = [remap(l.split("\t")[0]) for l in (UNI / "ffpp3_train.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip() and l.split("\t")[1] == "0"]
    frames = [tr[i] for i in rng.choice(len(tr), N_PER, False)]
    fams = {"tencent": lambda: vendor_pairs(rows, "tencent", rng), "megvii": lambda: vendor_pairs(rows, "megvii", rng),
            "pilgram_train": lambda: filter_pairs(frames, "pilgram", rng), "random_grade": lambda: filter_pairs(frames, "random_grade", rng)}
    out = {}; US = {}
    for fam, mk in fams.items():
        X, Y = mk(); us, p0, p1 = [], [], []
        for i in range(0, X.shape[0], 50):
            u, a, b = fit(X[i:i + 50], Y[i:i + 50]); us.append(u); p0.append(a); p1.append(b)
        u = {k: torch.cat([x[k] for x in us]) for k in us[0]}; US[fam] = u; p0 = np.concatenate(p0); p1 = np.concatenate(p1)
        eff = effective(u); q = lambda t: [round(float(np.percentile(t.cpu().numpy(), p)), 3) for p in (1, 50, 99)]
        out[fam] = {"n": int(X.shape[0]), "psnr_before": round(float(p0.mean()), 2), "psnr_after": round(float(p1.mean()), 2),
                    "psnr_after_p10": round(float(np.percentile(p1, 10)), 2), "effective_p1_p50_p99": {k: q(v) for k, v in eff.items()}}
        print(fam, json.dumps(out[fam]), flush=True)
    (HERE / f"fit_operator{sfx}.json").write_text(json.dumps(out, indent=1))
    allu = {k: torch.cat([US[f][k] for f in US]) for k in US["tencent"]}
    np.savez(HERE / f"fit_operator_prior{sfx}.npz", **{f"mu_{k}": v.mean(0).cpu().numpy() for k, v in allu.items()}, **{f"sigma_{k}": v.std(0).cpu().numpy() for k, v in allu.items()},
             **{f"{fam}_{k}": v.cpu().numpy() for fam in US for k, v in US[fam].items()})
    L = ["# Operator fitted to measured edits (Addendum 17 B; training split only)", "", "| family | n | PSNR before | PSNR after | PSNR after, 10th pct |", "|---|---|---|---|---|"]
    L += [f"| {f} | {r['n']} | {r['psnr_before']} | {r['psnr_after']} | {r['psnr_after_p10']} |" for f, r in out.items()]
    keys = list(next(iter(out.values()))["effective_p1_p50_p99"]); L += ["", "Effective parameter, 1st / 50th / 99th percentile:", "", "| parameter | " + " | ".join(out) + " |", "|---|" + "---|" * len(out)]
    L += [f"| {k} | " + " | ".join("/".join(str(x) for x in out[f]["effective_p1_p50_p99"][k]) for f in out) + " |" for k in keys]
    (HERE / f"FIT_OPERATOR{sfx.upper()}.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
