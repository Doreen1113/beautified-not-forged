"""RU5 (PRE_DECLARED Addendum 6): two independent questions instead of one three-way softmax, and every kind of
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
import copy
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
from ops import random_op_v2, op_smooth, hull_mask, JAW_LEFT, JAW_RIGHT  # noqa: E402


# ---------------------------------------------------------------------------------------------- random colour grading
def random_grade(rgb, rng):
    """A random global 'look' of the kind camera apps ship as filters. At least two of the components are applied."""
    x = rgb.astype(np.float32) / 255.0; h, w = x.shape[:2]
    on = rng.random(8) < np.array([0.6, 0.5, 0.6, 0.5, 0.35, 0.4, 0.3, 0.3])
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
        lum = x.mean(2, keepdims=True); a = rng.uniform(0.03, 0.12)
        x = x + a * ((1 - lum) * (rng.uniform(-1, 1, 3) * 0.5) + lum * (rng.uniform(-1, 1, 3) * 0.5)).astype(np.float32)
    if on[6]:   # vignette
        yy, xx = np.mgrid[0:h, 0:w]; r = np.hypot((yy - h / 2) / (h / 2), (xx - w / 2) / (w / 2))
        x = x * (1 - rng.uniform(0.1, 0.4) * np.clip(r - 0.4, 0, None)[..., None] ** 1.5).astype(np.float32)
    if on[7]:   # grain
        x = x + rng.normal(0, rng.uniform(0.008, 0.03), (h, w, 1)).astype(np.float32)
    return np.clip(x * 255.0, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------------------------- data
def op_gauss_facelocal(rgb, lm, rng, frac, mix):
    """Amendment 7 ablation: the face-local operator of op_smooth with the bilateral filter replaced by a Gaussian blur of the
    same kernel scale (sigma = d / 4), blended inside the same feathered hull with the same mix. Uniform blur, not edge-preserving."""
    h, w = rgb.shape[:2]; m = hull_mask(lm, h, w)
    jaw_w = float(np.linalg.norm(lm[JAW_LEFT] - lm[JAW_RIGHT])); d = int(np.clip(round(frac * jaw_w), 5, 45)) | 1
    sm = cv2.GaussianBlur(rgb, (0, 0), max(0.8, d / 4.0))
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), max(2.0, 0.01 * w))[..., None] * mix
    return np.clip(rgb * (1 - a) + sm * a, 0, 255).astype(np.uint8)


class RUData5(RUData3):
    """RU4 mixture with (2) and (3) above. Returns the RU3 tuple plus zb, the forged / beautified targets per item."""

    def __init__(self, rows, size, seed, head_res=16, norm="clip", grade=True, vendor_fake=True, ffpp_only=False, ffpp_parts=False, beauty="both", mil=False, no_smooth=False, only_smooth=False, sym_smooth=False, cons=False, cons_op="bilateral", resynth=0.0):
        super().__init__(rows, size, seed, arm="ru4", head_res=head_res, norm=norm)
        self.resynth = resynth   # Addendum 67: probability that the forged item is the FLUX-VAE re-synthesis of the base frame (resynth_precompute.py)
        self.cons_op = cons_op   # Amendment 7: bilateral (SIC) or gauss (ablation)
        self.cons = cons   # Addendum 46: also return x_s, a skin-smoothed copy of every item (pixel-aligned, same flip)
        self.mil = mil   # Addendum 28: the beautified item's map target is zero (forgery-evidence map, not edit map)
        self.no_smooth = no_smooth   # Addendum 31: no skin smoothing in any beautified view
        self.only_smooth = only_smooth   # Addendum 32: skin smoothing is the only beautified view (use with grade=False)
        self.sym_smooth = sym_smooth   # Addendum 34: the same two smoothing forms for genuine and forged faces; no pre-rendered frames
        if sym_smooth and not only_smooth:   # Addendum 36: full views, smoothing made class-symmetric; no pre-rendered smoothing frames
            self.obs_filt = [r for r in self.obs_filt if "smooth" not in Path(r["path"]).name.lower()]
        if only_smooth:
            assert not no_smooth and not grade
            self.obs_filt = [r for r in self.obs_filt if "smooth" in Path(r["path"]).name.lower()]
        if no_smooth:
            self.obs_filt = [r for r in self.obs_filt if "smooth" not in Path(r["path"]).name.lower()]
        self.beauty = beauty   # Addendum 25: "both" = beautification on genuine and forged faces; "real" = on genuine only; "none" = nowhere; "fake" = on forged only (Addendum 40, P3)
        self.grade, self.vendor_fake, self.ffpp_only, self.ffpp_parts = grade, vendor_fake and not ffpp_only, ffpp_only, ffpp_parts
        if ffpp_only:   # equal-data control: FF++ c23 training videos only (no FFHQ, no commercial renders, no part-level edits)
            self.bases = [r for r in self.bases if r["src"] == "ffpp_real"]
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

    def _rop(self, img, lm, rng):
        """random_op_v2; under no_smooth the smoothing operation is redrawn."""
        if self.sym_smooth and self.only_smooth and rng.random() < 0.5:   # whole-crop bilateral, the form the forged side receives without landmarks
            from fasb import BEAUTIFY
            pres = np.zeros(4, np.float32); pres[3] = 1.0
            return BEAUTIFY[0](img, rng), pres, np.zeros(4, np.float32), "smooth"
        while True:
            o = random_op_v2(img, lm, rng)
            if self.only_smooth and o[3] != "smooth":
                continue
            if self.sym_smooth and not self.only_smooth and o[3] == "smooth" and rng.random() < 0.5:   # Addendum 36
                from fasb import BEAUTIFY
                return BEAUTIFY[0](img, rng), o[1], np.zeros(4, np.float32), "smooth"
            if not (self.no_smooth and o[3] == "smooth"):
                return o

    def _beaut(self, img, rng):
        """Scripted beautification; under no_smooth only the two entries without a bilateral filter (whiten, colour look)."""
        if self.only_smooth:
            from fasb import BEAUTIFY
            return BEAUTIFY[0](img, rng)
        if self.no_smooth:
            from fasb import BEAUTIFY
            return BEAUTIFY[int(rng.integers(1, 3))](img, rng)
        return beautify(img, rng)

    def _on_top(self, img, lm, rng, has_lm):
        """A beautification applied on top of a forgery: scripted / pilgram, landmark operation, or a random grade."""
        u = rng.random()
        if self.grade and u < 0.35:
            return random_grade(img, rng)
        if has_lm and u < 0.65:
            return self._rop(img, lm, rng)[0]
        return self._beaut(img, rng)

    def __getitem__(self, i):
        r = self.bases[i]
        rng = np.random.default_rng((self.seed * 1000003 + self.epoch * 100003 + i) % (2 ** 63))
        rgb, lm = self._base(r)
        z4 = np.zeros(4, np.float32)
        # ---- filter item: synthetic v2 0.25 | random grade 0.15 | vendor single 0.28 | composite 0.12 | observed 0.20
        u = rng.random(); filt_pres = z4.copy(); filt_q = z4.copy(); mq = 1.0; sep = False; mp = 1.0
        g0 = 0.15 if self.grade else 0.0
        if self.sym_smooth and self.only_smooth and u >= 0.40:   # no pre-rendered smoothing frames: every genuine view comes from _rop
            u = float(rng.uniform(0.0, 0.40))
        if self.ffpp_only and 0.40 <= u < 0.80:   # commercial sources removed: redraw among scripted operation / colour look
            u = float(rng.uniform(0.0, 0.40))
        if u < 0.25 + (0.15 - g0):
            filt, filt_pres, filt_q, _ = self._rop(rgb, lm, rng); fm = footprint(filt, rgb)
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
        if self.beauty in ("none", "fake"):   # the third item is a second untreated copy of the genuine frame: same item count and class balance
            filt = rgb.copy(); fm = np.zeros(rgb.shape[:2], np.float32); filt_pres = z4.copy(); filt_q = z4.copy(); mq = 0.0; mp = 0.0; sep = False
        # ---- fake item: self-blend 0.35 | observed 0.25 | part edit 0.25 | commercial edit on a self-blend 0.15
        fsep = False; km = None; uf = rng.random(); fb = 0.0; v0 = 0.15 if self.vendor_fake else 0.0
        rs = self.resynth > 0 and rng.random() < self.resynth and r["src"] in ("ffpp_real", "ffhq_orig")
        if self.ffpp_only and self.ffpp_parts:   # Addendum 21: self-blend 0.35 | observed 0.35 | part-level edit on FF++ frames 0.30
            uf = 0.30 if uf < 0.35 else (0.90 if uf < 0.70 else v0 + 0.10)
        elif self.ffpp_only:   # self-blend 0.5 | observed FF++ forgery 0.5
            uf = 0.30 if uf < 0.5 else 0.90
        if rs:   # Addendum 67: re-synthesised copy of this very frame (paired with the genuine item), beautified on top with p 0.5 like a self-blend
            fake = np.array(Image.open(BASE / "resynth_flux" / r["src"] / f"{r['stem']}.png").convert("RGB"))
            if fake.shape[:2] != rgb.shape[:2]:
                fake = cv2.resize(fake, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_AREA)
            km = footprint(fake, rgb)
            if rng.random() < 0.5 and self.beauty in ("both", "fake"):
                fake = self._on_top(fake, lm, rng, True); fb = 1.0
        elif uf < v0:
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
            if rng.random() < 0.3 and self.beauty in ("both", "fake"):   # part edits can be beautified too (colour look only: keeps the footprint valid as the forged region)
                fake = random_grade(fake, rng) if self.grade else self._beaut(fake, rng); fb = 1.0
        elif uf < v0 + 0.50:
            o = self.obs_fake[int(rng.integers(0, len(self.obs_fake)))]; fake = np.array(Image.open(o["path"]).convert("RGB")); fsep = True
            if rng.random() < 0.5 and self.beauty in ("both", "fake"):
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
            if rng.random() < 0.5 and self.beauty in ("both", "fake"):
                fake = self._on_top(fake, lm, rng, True); fb = 1.0
        # ---- post-processing with masks (as RU3 / RU4)
        rm = np.zeros(rgb.shape[:2], np.float32)
        shared_i, shared_m = [rgb], [rm]
        if not sep:
            shared_i.append(filt); shared_m.append(fm)
        if not fsep:
            shared_i.append(fake); shared_m.append(km)
        st_post = copy.deepcopy(rng.bit_generator.state) if self.cons else None
        outs, ms = post_m(shared_i, shared_m, rng); real, rm = outs[0], ms[0]; k = 1
        if not sep:
            filt, fm = outs[k], ms[k]; k += 1
        else:
            (filt,), (fm,) = post_m([filt], [fm], rng)
        if not fsep:
            fake, km = outs[k], ms[k]
        else:
            (fake,), (km,) = post_m([fake], [km], rng)
        sh0 = [real.shape[:2], filt.shape[:2], fake.shape[:2]]
        real, rm = res_rand2(real, rm, rng); filt, fm = res_rand2(filt, fm, rng); fake, km = res_rand2(fake, km, rng)
        real, filt, fake = sym_degrade([real, filt, fake], rng)
        flip = bool(rng.random() < 0.5)
        x = torch.stack([to_t2(real, self.size, flip, self.norm), to_t2(fake, self.size, flip, self.norm), to_t2(filt, self.size, flip, self.norm)])
        xs = self._smoothed_views(i, rgb, lm, st_post, sh0, [real, filt, fake], [False, sep, fsep], flip) if self.cons else None

        def mk(m):
            if m is None:
                return torch.zeros(self.head_res, self.head_res), 0.0
            t = cv2.resize(m, (self.head_res, self.head_res), interpolation=cv2.INTER_AREA)
            return torch.from_numpy(np.ascontiguousarray(t[:, ::-1] if flip else t)).float(), 1.0
        (m0, v0_), (m1, v1), (m2, v2) = mk(rm), mk(km), mk(fm)
        if self.mil:
            m2, v2 = torch.zeros(self.head_res, self.head_res), 1.0
        y = torch.tensor([0, 1, 2])
        pres = torch.tensor(np.stack([z4, z4, filt_pres])); mpres = torch.tensor([1.0, 0.0, mp])
        q = torch.tensor(np.stack([z4, z4, filt_q])); mq_t = torch.tensor([1.0, 0.0, mq])
        zb = torch.tensor([[0.0, 0.0], [1.0, fb], [0.0, 0.0 if self.beauty in ("none", "fake") else 1.0]])
        if self.cons:
            return x, y, pres, mpres, q, mq_t, torch.stack([m0, m1, m2]), torch.tensor([v0_, v1, v2]), zb, xs
        return x, y, pres, mpres, q, mq_t, torch.stack([m0, m1, m2]), torch.tensor([v0_, v1, v2]), zb

    def _smoothed_views(self, i, rgb, lm, st_post, sh0, items, separate, flip, return_np=False):
        """Addendum 46: x_s for each final item (real, filt, fake), pixel-aligned with it. Items that share the base geometry
        (not separate) carry the base landmarks through the shared crop of post_m (offsets re-drawn from a copy of the rng
        state, so the main stream is untouched) and the resize of res_rand2: face-local ops.op_smooth, frac U[0.03, 0.14],
        mix U[0.3, 1.0]. Items without landmarks (vendor renders, observed FF++ frames, part edits): whole-crop bilateral at one
        of the three scripted strengths. Own rng stream; the operator is applied with probability 1.0 to every item."""
        rs = np.random.default_rng((self.seed * 9000011 + self.epoch * 900007 + i) % (2 ** 63))
        r2 = np.random.default_rng(); r2.bit_generator.state = st_post; r2.integers(0, 2 ** 31 - 1)   # same draws as post_m
        h0, w0 = rgb.shape[:2]; t_, b_, l_, r_ = (r2.uniform(0, 0.06, 4) * np.array([h0, h0, w0, w0])).astype(int)
        out, forms = [], []
        for im, sep_, (hb, wb) in zip(items, separate, sh0):
            if sep_ or lm is None:
                d = [(9, 50, 50), (15, 80, 80), (21, 100, 100)][int(rs.integers(0, 3))]
                if self.cons_op == "gauss":
                    s_ = cv2.GaussianBlur(im, (0, 0), d[0] / 4.0); forms.append(f"gauss{d[0]}")
                else:
                    s_ = cv2.bilateralFilter(im, *d); forms.append(f"bil{d[0]}")
            else:
                l2 = np.array(lm, np.float32).copy(); l2[:, 0] = (l2[:, 0] - l_) * im.shape[1] / wb; l2[:, 1] = (l2[:, 1] - t_) * im.shape[0] / hb
                fr_, mx_ = float(rs.uniform(0.03, 0.14)), float(rs.uniform(0.3, 1.0))
                if self.cons_op == "gauss":
                    s_ = op_gauss_facelocal(im, l2, rs, fr_, mx_); forms.append("face-local-gauss")
                else:
                    s_ = op_smooth(im, l2, rs, frac=fr_, mix=mx_)[0]; forms.append("face-local")
            out.append(s_)
        if return_np:
            return out, forms
        real_s, filt_s, fake_s = out
        return torch.stack([to_t2(real_s, self.size, flip, self.norm), to_t2(fake_s, self.size, flip, self.norm), to_t2(filt_s, self.size, flip, self.norm)])


class RUData7(RUData5):
    """RU7 (PRE_DECLARED Addendum 8): RU5 plus Instagram AR beauty filters. FairFace TRAIN originals (in-the-wild stills)
    join the genuine bases; with probability p_ar the filter item of a triplet is replaced by a FairBeauty image (5 training
    filters; 3 filters are never read). AR filters are not pixel-aligned with their originals, so the replaced item has no
    footprint and no operation targets. FairFace ids with hash % 10 == 0 are held out for validation (V4)."""

    def __init__(self, *a, p_ar=0.2, p_arfake=0.0, **k):
        super().__init__(*a, **k); self.p_arfake = p_arfake
        import hashlib
        self.p_ar = p_ar; D = BASE / "external_data/fairbeauty_train_pairs"; self.ar_dir = D
        z = np.load(D / "orig_landmarks.npz"); self.lm_ff = {s: z[s] for s in z.files}
        stems = [l.split("	")[0] for l in (D / "pairs.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
        keep = [s for s in stems if s in self.lm_ff and int(hashlib.md5(s.split("_")[0].encode()).hexdigest(), 16) % 10 != 0]
        self.ar = keep; self.n_core = len(self.bases)
        f = D / "filt_landmarks.npz"; self.lm_arf = {}
        if p_arfake > 0:   # RU8: self-blends of AR-filtered faces = forged AND beautified, so AR evidence also appears on forgeries
            zf = np.load(f); self.lm_arf = {s: zf[s] for s in zf.files}; self.arf = [s for s in keep if s in self.lm_arf]
        self.bases = self.bases + [dict(src="ffair", stem=s) for s in keep]

    def _base(self, r):
        if r["src"] == "ffair":
            return cap(np.array(Image.open(self.ar_dir / "orig" / f"{r['stem']}.png").convert("RGB")), self.lm_ff[r["stem"]].copy())
        return super()._base(r)

    def __getitem__(self, i):
        x, y, pres, mpres, q, mq, m, mm, zb = super().__getitem__(i)
        rng = np.random.default_rng((self.seed * 7000003 + self.epoch * 700001 + i) % (2 ** 63))
        if rng.random() < self.p_ar:
            s = self.ar[int(rng.integers(0, len(self.ar)))]; im = np.array(Image.open(self.ar_dir / "filt" / f"{s}.png").convert("RGB"))
            (im,), _ = post_m([im], [None], rng); im, _ = res_rand2(im, None, rng); (im,) = sym_degrade([im], rng)
            x[2] = to_t2(im, self.size, bool(rng.random() < 0.5), self.norm)
            pres[2] = 0; mpres[2] = 0.0; q[2] = 0; mq[2] = 0.0; m[2] = 0; mm[2] = 0.0
        if self.p_arfake > 0 and rng.random() < self.p_arfake:
            s = self.arf[int(rng.integers(0, len(self.arf)))]; b0, lm = cap(np.array(Image.open(self.ar_dir / "filt" / f"{s}.png").convert("RGB")), self.lm_arf[s].copy()); f = None
            for _ in range(4):
                f = self_blend(b0, lm, rng)
                if f is not None:
                    break
            if f is not None:
                km = footprint(f, b0); (f,), (km,) = post_m([f], [km], rng); f, km = res_rand2(f, km, rng); (f,) = sym_degrade([f], rng)
                flip = bool(rng.random() < 0.5); x[1] = to_t2(f, self.size, flip, self.norm)
                t = cv2.resize(km, (self.head_res, self.head_res), interpolation=cv2.INTER_AREA)
                m[1] = torch.from_numpy(np.ascontiguousarray(t[:, ::-1] if flip else t)).float(); mm[1] = 1.0; zb[1] = torch.tensor([1.0, 1.0])
        return x, y, pres, mpres, q, mq, m, mm, zb


# ---------------------------------------------------------------------------------------------- model
class RUCLIP5(RUCLIP):
    """RUCLIP with a forged / beautified head `fz` (two logits). First output: log of the joint (real, fake, filter)."""

    def __init__(self, head=True, r=16, detach=False, canon=None, tune="lora", mil=0.0):
        super().__init__(head=head, r=r, tune=tune)
        self.fz = nn.Linear(self.vit.config.hidden_size, 2); self.detach = detach; self.mil = mil
        del self.cls   # replaced by fz; the joint (real, fake, filter) is derived from it
        self.canon = None
        if canon is not None:   # Addendum 20: frozen estimate-and-invert canonicaliser in front of the backbone (True = weights come with the checkpoint)
            from canon import Canon
            self.canon = Canon()
            if canon is not True:
                self.canon.load_state_dict(torch.load(canon, map_location="cpu"))
            for p_ in self.canon.parameters():
                p_.requires_grad_(False)
            self.canon.eval()

    def forward(self, x):
        if self.canon is not None:
            with torch.no_grad():
                x = self.canon(x)
        o = self.vit(pixel_values=x); f = o.pooler_output; z = self.fz(f).float()
        fd = f.detach() if self.detach else f   # Addendum 18: auxiliary heads read the features without shaping them
        if self.detach:
            z = torch.stack([z[:, 0], self.fz(fd).float()[:, 1]], 1)
        lf, lb = F.logsigmoid(z[:, 0]), F.logsigmoid(z[:, 1]); nf, nb = F.logsigmoid(-z[:, 0]), F.logsigmoid(-z[:, 1])
        joint = torch.stack([nf + nb, lf, nf + lb], 1)
        out = (joint, self.pres(fd), self.q(fd))
        if self.head:
            t = o.last_hidden_state[:, 1:, :]; t = t.detach() if self.detach else t
            ev = self.ev(t).transpose(1, 2).reshape(x.shape[0], 1, self.grid, self.grid)
            if self.mil:   # Addendum 28: forged logit = mean of the top cells of the evidence map (multiple-instance pooling)
                k = max(1, int(round(self.mil * self.grid * self.grid))); zm = ev.float().flatten(1).topk(k, dim=1).values.mean(1)
                z = torch.stack([zm, z[:, 1]], 1); lf, nf = F.logsigmoid(z[:, 0]), F.logsigmoid(-z[:, 0]); joint = torch.stack([nf + nb, lf, nf + lb], 1); out = (joint,) + out[1:]
            return out + (ev, z)
        return out + (None, z)

    def train(self, mode=True):   # the canonicaliser (BatchNorm) stays frozen in eval mode whatever the detector does
        super().train(mode)
        if getattr(self, "canon", None) is not None:
            self.canon.eval()
        return self

    def state_dict_trainable(self):
        return {k: v for k, v in self.state_dict().items() if ("A" in k.split(".")[-1] or "B" in k.split(".")[-1] or k.split(".")[0] in ("pres", "q", "ev", "fz", "canon") or "_residual" in k)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=8); ap.add_argument("--workers", type=int, default=12); ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--seed", type=int, default=SEED); ap.add_argument("--wq", type=float, default=2.0); ap.add_argument("--wm", type=float, default=1.0)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--no-grade", action="store_true"); ap.add_argument("--no-vendor-fake", action="store_true")
    ap.add_argument("--softmax", action="store_true", help="ablation: RU5 data with the three-way softmax of RU4")
    ap.add_argument("--adv", choices=["none", "worst", "random", "worstk"], default="none", help="Addendum 15: worst-case (or random, as control) beautification of the real and fake items")
    ap.add_argument("--ar-fake", type=float, default=0.0, help="RU8: probability that the fake item is a self-blend of an AR-filtered face")
    ap.add_argument("--adv-wide", action="store_true", help="Addendum 17 B: operator bounds widened to the fitted 99th percentiles")
    ap.add_argument("--adv-prior", action="store_true", help="Addendum 18: start the search from a measured edit and confine it to the percentile range of the measured edits")
    ap.add_argument("--adv-steps", type=int, default=1, help="Addendum 17 C: ascent steps (step 0.4 when > 1)")
    ap.add_argument("--adv-obj", choices=["ce", "kl"], default="ce", help="Addendum 19: ce = label loss on the edited view (Madry); kl = TRADES-style consistency with the clean prediction")
    ap.add_argument("--adv-beta", type=float, default=1.0, help="Addendum 19: weight of the consistency term (kl only)")
    ap.add_argument("--detach-heads", action="store_true", help="Addendum 18: beautified / presence / quantity / evidence heads read detached features")
    ap.add_argument("--canon", default="", help="Addendum 20: path of a trained canonicaliser (canon.py) placed in front of the backbone, frozen")
    ap.add_argument("--ffpp-only", action="store_true", help="equal-data control: FF++ c23 only")
    ap.add_argument("--mil", type=float, default=0.0, help="Addendum 28: forged logit pooled from the top <mil> fraction of evidence-map cells; the beautified item gets a zero map target")
    ap.add_argument("--init", choices=["clip", "effort"], default="clip", help="Addendum 30: start from the released Effort checkpoint (requires --tune effort)")
    ap.add_argument("--epochs-override", type=int, default=0)
    ap.add_argument("--tune", choices=["lora", "effort"], default="lora", help="Addendum 26: backbone tuning scheme (effort = SVD residual of the self-attention projections, as in the released Effort code)")
    ap.add_argument("--sym-smooth", action="store_true", help="Addendum 34: with --only-smooth, the same smoothing forms on both classes")
    ap.add_argument("--only-smooth", action="store_true", help="Addendum 32: skin smoothing is the only beautified view (implies --no-grade)")
    ap.add_argument("--no-smooth", action="store_true", help="Addendum 31: remove skin smoothing from every beautified view")
    ap.add_argument("--beauty", choices=["both", "real", "none", "fake"], default="both", help="Addendum 25: which class receives beautified training views (fake: forged only, Addendum 40)")
    ap.add_argument("--ffpp-parts", action="store_true", help="Addendum 21: with --ffpp-only, add the part-level forgeries synthesised on FF++ train frames")
    ap.add_argument("--ar", action="store_true", help="RU7: add FairFace train originals and FairBeauty AR-filter images (Addendum 8)")
    ap.add_argument("--binary", action="store_true", help="control: same data, forged head only (no beautified / presence / evidence supervision)")
    ap.add_argument("--smooth-consistency", type=float, default=0.0, help="Addendum 46 (SIC): class-symmetric smoothing view (--sym-smooth) plus "
                    "LAMBDA * mean (z_f(x) - z_f(x_s))^2 over every item, x_s = skin-smoothed copy; factorised (clipe5z) or with --binary (clipe5bz, evidence head supervised); variant letter z")
    ap.add_argument("--cons-op", choices=["bilateral", "gauss"], default="bilateral", help="Amendment 7: operator of the consistency view (gauss = ablation with a uniform blur of the same support and scale)")
    ap.add_argument("--cons-hinge", action="store_true", help="Amendment 8: one-sided consistency, penalise only a RISE of z_f under smoothing (relu(z_f(x_s) - sg[z_f(x)])^2); implies stop-gradient")
    ap.add_argument("--cons-stopgrad", action="store_true", help="Addendum 46 am. 4: the clean logit z_f(x) is detached in the consistency term, so only the smoothed view is pulled toward the clean score")
    ap.add_argument("--grad-ckpt", action="store_true", help="activation checkpointing in the ViT encoder (same maths, less memory; for 24 GB cards)")
    ap.add_argument("--resynth", type=float, default=0.0, help="Addendum 67: probability that the forged item is the FLUX-VAE re-synthesis of the base frame (variant R<100p>)")
    ap.add_argument("--tag-suffix", default="", help="Addendum 46 am. 3: appended to the variant letters (l0 / l01 / l03 = lambda of --smooth-consistency)")
    a = ap.parse_args()
    if a.smooth_consistency:
        assert a.adv == "none" and not a.softmax and not a.only_smooth and not a.ar and not a.mil and not a.detach_heads, "Addendum 46 arms: full-data RU5 recipe, or FF++-only with --ffpp-only (Amendment 4)"
        a.sym_smooth = True
    if a.only_smooth:
        a.no_grade = True
    torch.manual_seed(a.seed); np.random.seed(a.seed); CKPT.mkdir(parents=True, exist_ok=True)
    variant = {"none": "", "worst": "a", "random": "r", "worstk": "k"}[a.adv] + ("w" if a.adv_wide else "") + ("p" if a.adv_prior else "") + (f"s{a.adv_steps}" if a.adv_steps > 1 else "") + ("t" if a.adv_obj == "kl" else "") + ("m" if a.mil > 0 else "") + ("d" if a.detach_heads else "") + ("c" if a.canon else "") + ("f" if a.ffpp_only else "") + ("e" if a.ffpp_parts else "") + ("x" if a.softmax else "") + ("b" if a.binary else "") + ("g0" if a.no_grade else "") + ("v0" if a.no_vendor_fake else "") + {"both": "", "real": "p1", "none": "p0", "fake": "p3"}[a.beauty] + ("n" if a.no_smooth else "") + ("o" if a.only_smooth else "") + ("y" if a.sym_smooth and not a.smooth_consistency else "") + ("z" if a.smooth_consistency else "") + ("E" if a.tune == "effort" else "") + ("i" if a.init == "effort" else "") + (f"R{int(round(100 * a.resynth))}" if a.resynth > 0 else "")
    tag = f"clipe{(8 if a.ar_fake > 0 else 7) if a.ar else 5}{variant}{a.tag_suffix}_s{a.seed}"
    model = (RUCLIP(head=True) if a.softmax else RUCLIP5(head=True, detach=a.detach_heads, canon=a.canon or None, tune=a.tune, mil=a.mil)).cuda()
    if a.grad_ckpt:
        model.vit.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False}); print("gradient checkpointing on", flush=True)
    if a.init == "effort":
        assert a.tune == "effort"; from effort_init import load_released_effort; load_released_effort(model)
    if a.adv != "none":
        import adv_beauty as AB
        AB.WIDE = a.adv_wide
        if a.adv_prior:
            AB.load_prior(HERE / ("fit_operator_prior_wide.npz" if a.adv_wide else "fit_operator_prior.npz"), "cuda")
    rows = read_manifest(HERE / "manifest_train.tsv"); vrows = read_manifest(HERE / "manifest_val.tsv")
    ds = (RUData7 if a.ar else RUData5)(rows, 224, a.seed, head_res=model.grid, norm="clip", grade=not a.no_grade, vendor_fake=not a.no_vendor_fake, **({"ffpp_only": True} if a.ffpp_only else {}), **({"ffpp_parts": True} if a.ffpp_parts else {}), **({"beauty": a.beauty} if a.beauty != "both" else {}), **({"mil": True} if a.mil > 0 else {}), **({"no_smooth": True} if a.no_smooth else {}), **({"only_smooth": True} if a.only_smooth else {}), **({"sym_smooth": True} if a.sym_smooth else {}), **({"cons": True, "cons_op": a.cons_op} if a.smooth_consistency else {}), **({"p_arfake": a.ar_fake} if a.ar else {}), **({"resynth": a.resynth} if a.resynth > 0 else {}))
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

    def loss_fn(out, y, pres, mpres, q, mq, m, mm, zb):
        lo, pr, qq = out[:3]
        if a.smooth_consistency:   # Addendum 46: out covers [x; x_s]; forged BCE on x, evidence map on both (x_s target = x footprint), consistency of z_f
            n = y.shape[0]; zf = out[4][:, 0].float(); lk = ((torch.relu(zf[n:] - zf[:n].detach())) ** 2).mean() if a.cons_hinge else (((zf[:n].detach() if a.cons_stopgrad else zf[:n]) - zf[n:]) ** 2).mean()
            lm = mask_loss(out[3], torch.cat([m, m]), torch.cat([mm, mm]))
            if a.binary:   # clipe5bz: forged BCE only (plus evidence map and consistency)
                lc = F.binary_cross_entropy_with_logits(zf[:n], zb[:, 0])
                return lc + a.wm * lm + a.smooth_consistency * lk, (float(lc.detach()), float(lk.detach()), 0.0, float(lm.detach()))
            # clipe5z: every clipe5 term on x (forged + beautified BCE, presence, quantities), evidence on [x; x_s], consistency on the forged logit only
            l = F.binary_cross_entropy_with_logits(out[4][:n], zb, reduction="none").sum(1).mean()
            lp = (F.binary_cross_entropy_with_logits(pr[:n].float(), pres, reduction="none").mean(1) * mpres).sum() / mpres.sum().clamp(min=1)
            lq = ((qq[:n].float() - q).abs().mean(1) * mq).sum() / mq.sum().clamp(min=1)
            return l + lp + a.wq * lq + a.wm * lm + a.smooth_consistency * lk, (float(l.detach()), float(lk.detach()), float(lq.detach()), float(lm.detach()))
        if a.binary:   # control: one forged / not-forged logit, nothing else is supervised
            return F.binary_cross_entropy_with_logits(out[4][:, 0], zb[:, 0]), (0.0, 0.0, 0.0, 0.0)
        l = F.cross_entropy(lo.float(), y) if a.softmax else F.binary_cross_entropy_with_logits(out[4], zb, reduction="none").sum(1).mean()
        lp = (F.binary_cross_entropy_with_logits(pr.float(), pres, reduction="none").mean(1) * mpres).sum() / mpres.sum().clamp(min=1)
        lq = ((qq.float() - q).abs().mean(1) * mq).sum() / mq.sum().clamp(min=1)
        lm = mask_loss(out[3], m, mm)
        return l + lp + a.wq * lq + a.wm * lm, (float(l.detach()), float(lp.detach()), float(lq.detach()), float(lm.detach()))

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
            x = batch[0].flatten(0, 1).cuda(non_blocking=True); y, pres, mpres, q, mq, m, mm, zb = [t.flatten(0, 1).cuda() for t in batch[1:9]]
            if a.smooth_consistency:
                x = torch.cat([x, batch[9].flatten(0, 1).cuda(non_blocking=True)])
            with torch.autocast("cuda", dtype=torch.bfloat16):
                out = model(x); loss, parts = loss_fn(out, y, pres, mpres, q, mq, m, mm, zb)
            if a.adv != "none":   # beautified views of the genuine and forged items: forged label unchanged, beautified = 1
                import adv_beauty as AB
                sel = y != 2; tgt = zb[sel][:, 0]; zc = out[4][sel][:, 0].float()
                # kl: the search maximises KL(Bern(p_clean) || Bern(q_edited)), which is the BCE with the clean probability as soft target
                search_tgt = torch.sigmoid(zc).detach() if a.adv_obj == "kl" else tgt
                model.eval()   # no dropout in the search
                xa = AB.worst_case(lambda v: model(v)[4][:, 0], x[sel], search_tgt, step=0.4 if a.adv_steps > 1 else 1.0, random_only=a.adv == "random", steps=a.adv_steps,
                                   k=4 if a.adv == "worstk" else 0, prior=a.adv_prior)
                model.train()
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    za = model(xa)[4].float()
                if a.adv_obj == "kl":   # TRADES: the edited view must keep the clean prediction, gradient through both; beautified head still supervised
                    pc = torch.sigmoid(zc)
                    kl = pc * (F.logsigmoid(zc) - F.logsigmoid(za[:, 0])) + (1 - pc) * (F.logsigmoid(-zc) - F.logsigmoid(-za[:, 0]))
                    loss = loss + a.adv_beta * kl.mean() + F.binary_cross_entropy_with_logits(za[:, 1], torch.ones_like(tgt))
                else:
                    loss = loss + F.binary_cross_entropy_with_logits(za, torch.stack([tgt, torch.ones_like(tgt)], 1), reduction="none").sum(1).mean()
            opt.zero_grad(set_to_none=True); loss.backward(); torch.nn.utils.clip_grad_norm_(model.trainable(), 1.0); opt.step()
            acc += np.array([float(loss.detach())] + list(parts)); n += 1; step += 1
            if step % 200 == 0:
                print(f"  step {step}/{total} loss {acc[0] / n:.4f} (cls {acc[1] / n:.3f} {'cons' if a.smooth_consistency else 'pres'} {acc[2] / n:.3f} q {acc[3] / n:.3f} mask {acc[4] / n:.3f}) {(time.time() - t0) / n:.3f}s/it", flush=True)
            if a.max_steps and a.smooth_consistency:   # smoke test: per-step terms
                print(f"  smoke step {step} loss {float(loss.detach()):.4f} cls {parts[0]:.4f} cons {parts[1]:.5f} mask {parts[3]:.4f} max_mem {torch.cuda.max_memory_allocated() / 2 ** 30:.1f} GiB", flush=True)
            if a.max_steps and step >= a.max_steps:
                print(f"smoke test ok: {step} steps, {(time.time() - t0) / n:.3f}s/it", flush=True); return
        P, S, T = evaluate(dl_vf); mk = np.isin(T, [0, 1]); f1 = f1_score(T, P, average="macro"); auc = roc_auc_score((T[mk] == 1).astype(int), S[mk])
        Pv, _, Tv = evaluate(dl_vv); orig_real = float((Pv[Tv == 0] == 0).mean() * 100); filt_rec = float((Pv[Tv == 2] == 2).mean() * 100)
        log.append(dict(epoch=ep, loss=acc[0] / n, **({"l_cons": acc[2] / n} if a.smooth_consistency else {}), ffpp_val_f1=f1, ffpp_val_auc=auc, vendor_val_orig_real=orig_real, vendor_val_filter_recall=filt_rec, minutes=(time.time() - t0) / 60))
        print(f"[{tag}][{ep:02d}/{a.epochs}] loss {acc[0] / n:.4f} ffppF1 {f1:.4f} AUC {auc:.4f} orig->real {orig_real:.1f}% vendor filter recall {filt_rec:.1f}% ({(time.time() - t0) / 60:.1f} min)", flush=True)
        torch.save(model.state_dict_trainable(), CKPT / f"ru_{tag}_e{ep:02d}.pth")
        with open(HERE / f"train_ru_{tag}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(log[0])); w.writeheader(); w.writerows(log)
    (HERE / f"meta_ru_{tag}.json").write_text(json.dumps({"arm": "ru7" if a.ar else "ru5", "factorised": not a.softmax, "binary": a.binary, "mil": a.mil, "beauty": a.beauty, "no_smooth": a.no_smooth, "only_smooth": a.only_smooth, "sym_smooth": a.sym_smooth, "smooth_consistency": a.smooth_consistency, "cons_stopgrad": a.cons_stopgrad, "cons_hinge": a.cons_hinge, "cons_op": a.cons_op, "grad_ckpt": a.grad_ckpt, "tune": a.tune, "grade": not a.no_grade, "vendor_fake": not a.no_vendor_fake,
                                                         "epochs": a.epochs, "seed": a.seed, "trainable_M": ntr / 1e6}, indent=1))
    print(f"[{tag}] DONE", flush=True)


if __name__ == "__main__":
    main()
