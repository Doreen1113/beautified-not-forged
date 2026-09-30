# PRE_DECLARED — faithful self-blending (fixing our SBI reproduction), then HYB on top
`sbifix_20260927` — written 2026-09-27 before any arm of this round is trained.

## 1. Why
`sbiscale_20260926` R0 failed: official SBI recipe in our pipeline gave CDFv2 0.620 vs the official checkpoint's
0.817 on the same frames. Training loss collapsed (0.146 after epoch 1, 0.019 at the end) while val AUC on genuine FF++
fakes stayed ~0.78 — the signature of a synthetic-data shortcut. A line-by-line comparison of `fasb.self_blend` /
`sbi/sbi_generator.py` with the official implementation (Shiohara & Yamasaki, CVPR'22, mapooon/SelfBlendedImages)
finds three deviations:
1. **JPEG/colour order.** Ours applies `common_transforms` (incl. JPEG q40–100) to the base *before* blending; the
   blended region then carries a displaced/destroyed 8×8 JPEG grid — a trivial cue no real deepfake has. Official:
   blend first, then the same common transforms on real and fake.
2. **Elastic warp target.** Ours warps the source *image*; official warps only the *mask*.
3. **Crop jitter.** Official re-crops with random margins at train time; ours uses the fixed extraction crop.
HYB-L inherits deviations 1–2 through its self-blend half, so the fix may improve it too.

## 2. Fix (`sbi_faithful.py`)
Self-blend: hull mask → one branch source-transformed → affine on source image+mask → **elastic on mask only** →
blend mask + ratio. Then **one common transform, identical parameters, applied to every image of the triplet**
(real, filter, fake), then **one identical random crop** (each side trims U(0, 6 %) of the image). Beautification
and composition unchanged (`fasb.beautify`, TRAIN-14 pilgram only). Observed HYB rows get their own common transform
and crop jitter.

## 3. Arms (recipe identical to sbiscale: EffB4-AP 380, SGD 1e-3 + SAM 0.05, 14 epochs, batch 16 photos, bf16)
| arm | where | data |
|---|---|---|
| **SBI-F** | Ubuntu RTX 6000 Ada | FF++ train real only, binary — the reproduction control |
| **HYB-F** | local RTX 6000 Ada | as HYB-L, self-blend half now faithful |
Seed 20260928 for both. Selection as sbiscale (SBI: val AUC real vs genuine FF++ fakes; HYB: val macro-F1).

## 4. Bars (fixed now)
- **Mechanism check M**: SBI-F final train loss > 2× SBI-L's (0.019) — the shortcut is gone. Reported either way.
- **R0'**: SBI-F CDFv2 ≥ 0.78 (official 0.817). Pass ⇒ our pipeline reproduces SBI.
- **HYB-F vs HYB-L** (HYB-L two-seed mean: CDFv2 0.764, DFD 0.915, FF++ in-domain each ≥ 84 %, B1 0/12):
  - **F1** CDFv2 ≥ 0.79 (mean + ~0.03, ≈ one CI half-width)
  - **F2** DFD ≥ 0.90
  - **F3** B1 on FF++: 0 of 12 (11 published + the better of SBI-L/SBI-F)
  - **F4** FF++ in-domain real / fake / filter each ≥ 80 %
  - **F5** Celeb-DF-B (v3 frames): E1 holds (0 / 11) and ΔMISS CI upper bound ≤ +5 pp
  - **F6** Celeb-DF-B untreated genuine called fake ≤ 42.9 % (HYB-L's better seed) — the weakness targeted
  BUILD = F1–F6 → second seed. **SOTA claim** additionally needs CDFv2 ≥ 0.817 and DFD ≥ 0.918.
  If F1 fails but F2–F6 pass, HYB-F is reported as "no gain" and HYB-L remains the method.

## 5. Traps
Same as sbiscale (train-partition assertion; cross-dataset sets never used for selection). Checkpoint paths carry the
arm and seed (the sbiscale overwrite incident). Sanity image grid of triplets is saved before training.

## Addendum 1 (2026-09-27, before SUP is trained; SBI-F / HYB-F running, no result seen)
**SUP-F** (Ubuntu, after SBI-F): identical recipe and post-processing, but fake = observed FF++ train forgery only
(50 % beautified on top) and filter = observed `ffpp3_train` filter frame only — no self-blending. It isolates what the
self-blend half of HYB contributes at fixed backbone/recipe (the missing cell of the ablation: RepViT supervised-only,
EffB4 self-blend-only (FASB-L), EffB4 both (HYB)). Reported as an ablation row; no bar attaches to it.

## Addendum 2 (2026-09-28, before HYBD is trained) — symmetric degradation arm
**Finding (probe, HYB-L seed 2, 300 FF++ test reals)**: JPEG q30 leaves the fake rate at 7.7 %, but downscale ×1.5 → 60 %,
×2 → 74 %, Gaussian blur σ1.5 → 95 % called *fake*; Celeb-DF genuine frames (47 % called fake) are softer than FF++
frames at the same crop size. Self-blending degrades one branch (SBI's source transform), so "soft region" became fake
evidence. Video-level aggregation does not remove the accusation (HYB-L 56.7 % at video level), so it is not frame noise.
**HYBD** = HYB-F + `sym_degrade`: with p=0.5 the same Gaussian blur (σ∈[0.6,2]) or downscale-upscale (×1.3–3) is
applied to all three images of the triplet (and to observed items), after synthesis and before the shared jitter.
Bars (fixed now): **F6'** Celeb-DF-B untreated genuine→fake ≤ 25 % (HYB-F 45.1 %); **F1'** CDFv2 ≥ 0.78 (HYB-F 0.7795);
F2–F5 as §4. Probe on FF++ test reals downscaled ×2: called fake ≤ 15 %. Reported either way.
