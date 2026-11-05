"""Differentiable beautification operator and its worst-case search (PRE_DECLARED Addendum 15).

B(x; u): identity-preserving appearance edit of a face crop x in [0,1], parameters u unconstrained, every component bounded:
  tone      per-channel gamma [0.6, 1.6], gain [0.8, 1.2], lift [-0.08, 0.08]
  colour    3x3 matrix I + 0.15 tanh(.), rows normalised
  chroma    saturation [0, 1.7] (0 = monochrome), contrast [0.7, 1.4]
  field     smooth spatial gain, 4x4 control grid: luminance in [0.6, 1.25] times per-channel tint in [0.92, 1.08], bilinear
            (vignettes, light leaks, tint gradients)
  texture   blend toward a Gaussian-smoothed copy, weight [0, 0.4] (skin smoothing range of the commercial renders)
  grain     additive noise, amplitude [0, 0.05]
worst_case(): one signed-gradient ascent step on u from a random start (R+FGSM style), maximising the forged-logit loss.
"""
import torch
import torch.nn.functional as F

CLIP_MEAN = (0.48145466, 0.4578275, 0.40821073); CLIP_STD = (0.26862954, 0.26130258, 0.27577711)
WIDE = False    # Addendum 17 B: bounds widened where the fitted app filters / vendor edits hit the hand-set ones
PRIOR = None    # {name: (lo, hi, pool)}: per-element 0.5 / 99.5 percentiles and the pool of edits fitted to real retouching and filters


INVERSE = False   # canon.py: ranges wide enough to hold the inverse of any edit in the wide set (1/0.45 luminance, 1/0.19 saturation ...)


def bounds():
    if INVERSE:
        return {"M": 0.3, "tint0": 0.7, "tint": 0.7, "fld0": 0.45, "fld": 1.8, "smooth": 0.5, "sat": 5.5, "gam0": 0.5, "gam": 1.3, "gain0": 0.7, "gain": 0.6, "con0": 0.6, "con": 0.9}
    b = {"M": 0.25, "tint0": 0.88, "tint": 0.24, "fld0": 0.45, "fld": 0.95, "smooth": 0.5} if WIDE else {"M": 0.15, "tint0": 0.92, "tint": 0.16, "fld0": 0.6, "fld": 0.65, "smooth": 0.4}
    return dict(b, sat=1.7, gam0=0.6, gam=1.0, gain0=0.8, gain=0.4, con0=0.7, con=0.7)


def load_prior(path, device, fams=("tencent", "megvii", "pilgram_train", "random_grade")):
    """The plausible set (Addendum 18): per element of u, the 0.5th–99.5th percentile of the edits fitted by fit_operator.py to the
    four measured families, and the pool of fitted edits used as search starts. A Gaussian box was tried first and excluded
    monochrome (saturation floor 0.49); the percentile box keeps it (0.18)."""
    import numpy as np
    global PRIOR
    z = np.load(path); PRIOR = {}
    for k in ("gamma", "gain", "lift", "M", "sat", "con", "field", "tint", "smooth", "grain"):
        pool = np.concatenate([z[f"{f}_{k}"] for f in fams]).astype(np.float32)
        PRIOR[k] = (torch.tensor(np.percentile(pool, 0.5, axis=0), device=device, dtype=torch.float32)[None],
                    torch.tensor(np.percentile(pool, 99.5, axis=0), device=device, dtype=torch.float32)[None], torch.tensor(pool, device=device))


def init_params(n, device, scale=1.0):
    g = lambda *s: (torch.randn(n, *s, device=device) * scale).requires_grad_(True)
    return {"gamma": g(3, 1, 1), "gain": g(3, 1, 1), "lift": g(3, 1, 1), "M": g(3, 3), "sat": g(1, 1, 1), "con": g(1, 1, 1),
            "field": g(1, 4, 4), "tint": g(3, 4, 4), "smooth": g(1, 1, 1), "grain": g(1, 1, 1)}


def _blur(x, k=9, sigma=2.0):
    ax = torch.arange(k, device=x.device, dtype=x.dtype) - k // 2; w = torch.exp(-ax ** 2 / (2 * sigma ** 2)); w = w / w.sum()
    x = F.conv2d(F.pad(x, (k // 2, k // 2, 0, 0), mode="reflect"), w.view(1, 1, 1, k).repeat(3, 1, 1, 1), groups=3)
    return F.conv2d(F.pad(x, (0, 0, k // 2, k // 2), mode="reflect"), w.view(1, 1, k, 1).repeat(3, 1, 1, 1), groups=3)


def apply(x, u, noise):
    s = torch.sigmoid
    bd = bounds()
    x = x.clamp(1e-4, 1) ** (bd["gam0"] + bd["gam"] * s(u["gamma"])) * (bd["gain0"] + bd["gain"] * s(u["gain"])) + (-0.08 + 0.16 * s(u["lift"]))
    M = torch.eye(3, device=x.device)[None] + bd["M"] * torch.tanh(u["M"]); M = M / M.sum(2, keepdim=True)
    x = torch.einsum("nij,njhw->nihw", M, x)
    gray = x.mean(1, keepdim=True); x = gray + (x - gray) * (bd["sat"] * s(u["sat"]))
    mu = x.mean((1, 2, 3), keepdim=True); x = mu + (x - mu) * (bd["con0"] + bd["con"] * s(u["con"]))
    fld = (bd["fld0"] + bd["fld"] * s(u["field"])) * (bd["tint0"] + bd["tint"] * s(u["tint"]))   # luminance field x mild per-channel tint field
    x = x * F.interpolate(fld, size=x.shape[-2:], mode="bilinear", align_corners=True)
    x = x.clamp(0, 1); x = x + (bd["smooth"] * s(u["smooth"] - 1.0)) * (_blur(x) - x)
    x = x + (0.05 * s(u["grain"] - 1.0)) * noise
    return x.clamp(0, 1)


def apply_inverse(x, u):
    """Exact algebraic inverse of the invertible part of apply() (smoothing and grain excluded), components undone in reverse
    order: field, contrast, saturation, colour matrix, tone curve. Used by canon.py with u = the *estimated forward edit*."""
    s = torch.sigmoid; bd = bounds()
    fld = (bd["fld0"] + bd["fld"] * s(u["field"])) * (bd["tint0"] + bd["tint"] * s(u["tint"]))
    x = x / F.interpolate(fld, size=x.shape[-2:], mode="bilinear", align_corners=True)
    mu = x.mean((1, 2, 3), keepdim=True); x = mu + (x - mu) / (bd["con0"] + bd["con"] * s(u["con"]))
    gray = x.mean(1, keepdim=True); x = gray + (x - gray) / (bd["sat"] * s(u["sat"])).clamp_min(0.05)
    M = torch.eye(3, device=x.device)[None] + bd["M"] * torch.tanh(u["M"]); M = M / M.sum(2, keepdim=True)
    x = torch.einsum("nij,njhw->nihw", torch.linalg.inv(M), x)
    x = ((x - (-0.08 + 0.16 * s(u["lift"]))) / (bd["gain0"] + bd["gain"] * s(u["gain"]))).clamp(1e-4, 1) ** (1.0 / (bd["gam0"] + bd["gam"] * s(u["gamma"])))
    return x.clamp(0, 1)


def denorm(x):
    return x * torch.tensor(CLIP_STD, device=x.device).view(1, 3, 1, 1) + torch.tensor(CLIP_MEAN, device=x.device).view(1, 3, 1, 1)


def renorm(x):
    return (x - torch.tensor(CLIP_MEAN, device=x.device).view(1, 3, 1, 1)) / torch.tensor(CLIP_STD, device=x.device).view(1, 3, 1, 1)


def prior_box(u):
    """Clip every parameter to the plausible set (per-element percentile range of the fitted edits)."""
    return {k: (torch.max(torch.min(v, PRIOR[k][1]), PRIOR[k][0]) if k != "grain" else v) for k, v in u.items()}


def prior_start(n, device):
    """A coherent start: one fitted edit per sample drawn from the pool, with a little jitter."""
    idx = torch.randint(0, PRIOR["gamma"][2].shape[0], (n,), device=device)
    return {k: ((PRIOR[k][2][idx] + 0.05 * torch.randn(n, *PRIOR[k][2].shape[1:], device=device)) if k != "grain" else torch.randn(n, 1, 1, 1, device=device)).detach().requires_grad_(True)
            for k in PRIOR}


def worst_case(forged_logit_fn, x_norm, target, step=1.0, random_only=False, steps=1, k=0, prior=False):
    """x_norm: CLIP-normalised batch; target: forged label (0/1). Returns the beautified batch (normalised, detached).
    k > 0: worst-of-k random draws per sample, no gradient (Addendum 16 control). steps > 1: iterated ascent (PGD style).
    prior: the search starts from a measured edit and is projected after every step onto the percentile range of the measured
    edits (Addendum 18), so the worst case is the worst *plausible* beautification."""
    x = denorm(x_norm.float()).clamp(0, 1); u = init_params(x.shape[0], x.device); noise = torch.randn(x.shape[0], 1, *x.shape[-2:], device=x.device)
    if prior:
        assert PRIOR is not None, "load_prior() first"
        u = prior_start(x.shape[0], x.device)
    if k > 0:
        best = None
        with torch.no_grad():
            for _ in range(k):
                c = init_params(x.shape[0], x.device)
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    z = forged_logit_fn(renorm(apply(x, c, noise)))
                l = F.binary_cross_entropy_with_logits(z.float(), target, reduction="none")
                if best is None:
                    best, u = l, {a: b.detach() for a, b in c.items()}
                else:
                    m = l > best; best = torch.where(m, l, best)
                    u = {a: torch.where(m.view(-1, *[1] * (b.dim() - 1)), c[a].detach(), b) for a, b in u.items()}
    elif not random_only:
        for _ in range(steps):
            u = {a: b.detach().requires_grad_(True) for a, b in u.items()}
            with torch.autocast("cuda", dtype=torch.bfloat16):
                z = forged_logit_fn(renorm(apply(x, u, noise)))
            loss = F.binary_cross_entropy_with_logits(z.float(), target, reduction="sum")
            grads = torch.autograd.grad(loss, list(u.values()))
            u = {a: (b + step * g.sign()).detach() for (a, b), g in zip(u.items(), grads)}
            if prior:
                u = prior_box(u)
    with torch.no_grad():
        return renorm(apply(x, u, noise))
