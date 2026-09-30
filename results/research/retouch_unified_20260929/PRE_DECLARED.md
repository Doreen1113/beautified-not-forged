# RU-20260929 — Unified real / forged / beautified detector with verifiable beautification quantities, cross-vendor

**Why this line** (`alipair_zeroshot_20260929/FINDINGS.md`): every FF++-only three-way model is at chance on Alibaba commercial
retouching (balanced 48–55 %), calls up to 56 % of untouched FFHQ photographs *fake* and up to 86 % of commercially smoothed
faces *fake*. Every FF++ in-domain improvement lowered commercial-retouching signal. The filter class has so far been defined
by our own scripts; this line trains on real vendor retouching and tests on an unseen vendor.

**Prior art (scan 2026-09-29, verified)**: RetouchingFFHQ (ACM MM 2023) trains 4 × 4-way level heads on Megvii single+multi
subsets and reports Megvii→Alibaba *TP only* (DenseNet121-MAM: eye .519 / face .548 / smooth .861 / white .501, sum .607);
no TN cross-API, no deepfake class, no quantities. FRRffusion / MoFRR restore Alibaba retouching with diffusion (125M+).
Re-Face chains label → SD reversal. Open: one lightweight model separating forged / beautified / real, cross-vendor, with
continuous, verifiable explanation quantities. That is what this line builds. No claim of "first to detect retouching
cross-API" or "first to restore".

## 1. Data (fixed before training)
| Role | Source | Count | Notes |
|---|---|---|---|
| real | FFHQ originals Part7 (indices 60002–69999, HF `marcosv/ffhq-dataset`) ∩ Tencent∪Megvii clean lists | ≈7.8k | 1024², also base images for synthesis |
| real | FF++ c23 train genuine frames (dense, cached landmarks) | 41.5k | as HYB |
| filter (vendor) | Tencent quad composite `FFHQ_four_process` clean | 7,730 | 512², all four ops at 30/60/90 (`four_process.txt`) |
| filter (vendor) | Megvii quad composite `FFHQ_megvii_four_process` clean | 13,139 | 1024², all four ops, levels unknown |
| filter (synthetic) | on-the-fly single-op with continuous strength on FFHQ Part7 + FF++ reals | ∞ | smoothing / whitening / eye enlarging / **face slimming (correct direction, verified by jaw-width ratio < 1)**; photometric pilgram presets as before |
| filter (observed) | FF++ train filter frames (scripted + pilgram) | 41.5k | as HYB |
| fake | FF++ c23 train forgeries; faithful self-blends of FF++ reals **and of FFHQ Part7 originals**; compositional (fake + beautify) | | FFHQ-domain fakes so "high-quality still ⇒ not fake" cannot be learnt |
| **test, never trained** | Alibaba single-op `FFHQ_ali_process` (indices 17001–19999, 2,210 originals × 12) + FFHQ Part2 originals | 28,729 | vendor, base images and indices disjoint from all training |
| test | CDFv2 std32, DFD std32, Celeb-DF-B v3, FF++ test / escape / held-out-13 | | unchanged harnesses |

Base-index disjointness: training FFHQ indices ⊂ [60002, 69999]; test ⊂ [17001, 19999]. Content-key audit (decoded SHA256)
of Part7 vs Part2 and vs Alibaba will be run before training (expected 0).

**Resolution shortcut control**: sources differ in native size (Tencent 512, others 1024, FF++ crops ~256). Every training image,
regardless of class, is pre-downscaled to a random size in [384, 1024] on its long side with p = 0.5 before cropping, and the
symmetric degradation of HYB-D (blur / down-up, same for all items) is applied with p = 0.5. Face crop = FF++ extractor
(landmark hull + 35 % margin); for vendor pairs the box is computed on the original and shared.

## 2. Model
Backbone A: EfficientNet-B4 AdvProp, 380 px (comparable with the FF++ line). Backbone B: RepViT-M0.9, 224 px (edge, 4.7 M).
Heads on pooled features: (i) three-way real / fake / filter (CE); (ii) presence of the 4 operations (BCE, supervised where
known: originals 0000, vendor quad 1111, synthetic one-hot, FF++ scripted filters by name, pilgram 0000 with class filter,
fakes masked); (iii) **quantities** q = (eye_ratio − 1, 1 − jaw_ratio, ΔL_skin / 20, 1 − hf_ratio), masked L1 where measured:
synthetic (analytic from the applied warp / photometric change), Tencent and Megvii (measured on the pair with
`measure_pairs.py`), originals (0). Recipe: SGD 1e-3 + SAM ρ 0.05, 14 epochs, batch 48 images (3 classes × 16), bf16, model
selection on FF++ val macro-F1 + Tencent/Megvii **validation split** presence-F1 (10 % of vendor base indices held out from
training; never Alibaba).

## 3. Evaluation on Alibaba (blind; the pair is used only to compute ground truth, never given to the model)
- Retouched vs original: balanced accuracy of class *filter* vs not; paired excess; paired rank P(p_filter(ret) > p_filter(orig)).
- RetouchingFFHQ Eq. 4 per operation: TP (performed op predicted present), TN (non-performed ops predicted absent on the same
  image, and all four absent on originals), AC (exact match). Reported against Table 7 of RetouchingFFHQ with the caveat that
  our vendor training pool is quad-composite only (theirs includes Megvii single/dual/triple).
- Accusation: retouched images routed to *fake* (per op × level) and originals routed to *fake*.
- Quantities: Spearman ρ and MAE between the blind prediction and the pair-measured value, on the pairs of the matching
  operation (eye_ratio on EyeEnlarging, jaw_ratio on FaceLifting, hf_ratio on Smoothing, ΔL on Whitening), plus the
  cross-talk (predicted quantity of non-applied ops ≈ 0).

## 4. Bars (pre-registered; a miss is reported, never re-tuned)
- **R1** Alibaba balanced accuracy ≥ 75 % (chance-level baselines 48–55 %).
- **R2** Per-op TP ≥ RetouchingFFHQ DenseNet121-MAM Table 7 on ≥ 3 of 4 ops **with** per-op TN on originals ≥ 0.80.
- **R3** Alibaba retouched → fake ≤ 5 % pooled and ≤ 10 % at every op × level (currently 27–86 % for smoothing-90).
- **R4** Quantities: Spearman ≥ 0.6 for each of the four matched (op, quantity) pairs; cross-talk |q̂| median ≤ 0.02.
- **D1** Deepfake side not sacrificed: CDFv2 frame AUC ≥ 0.78, DFD ≥ 0.88, Celeb-DF-B untreated AUC ≥ 0.85, escape change under
  beautification within [−3, +3] pp, B1 dominance 0/13.
- **D2** FF++ test recall ≥ 80 % per class; held-out-13 paired excess ≥ 30 pp.
- Edge (RepViT): same bars minus 0.05 AUC / 5 pp; CPU latency ≤ 40 ms.

## 5. What would falsify the line
If R1 fails for both backbones, vendor-quad + parametric-synthetic supervision does not transfer to an unseen vendor and the
paper reports commercial retouching as an open limitation with these numbers. If R1 passes but R3 fails, the softness shortcut
survives vendor supervision and the accusation analysis becomes the finding.

## Addendum 1 (2026-09-29, after RU1-EffB4 Alibaba evaluation, before RU2 is trained)

**RU1-EffB4 result (bars as declared):** R1 FAIL (balanced 66.1 % < 75), R2 FAIL (TP beats Table 7 on smoothing only: .928 vs
.861; eye .248 / lift .089 / white .095; original TN .96–.99), **R3 PASS** (retouched→fake 0.63 %, ≤1 % in every cell;
originals→fake 0.8 %, originals→real 93.4 %), R4 FAIL (Spearman smooth .683, eye .457, lift .097, white −.078). Paired rank
92.8 % (eye 98–99, lift 89–95, white 77–85, smooth 99–100): the relative signal is strong; absolute recognition of the
three non-smoothing operations is low. RU1 is reported as is.

**Diagnosis (from training data only):** (i) every vendor training image is a four-operation composite, so the model learnt
co-occurrence (on single-op smoothing it predicts the other three ops present; same-image TN .059); (ii) the parametric ops
were far stronger than the training vendors: measured eye change ≈ +4.7 % vs Tencent +0.0–2.2 %, jaw ≈ −5 % vs −0.8–2.6 %,
ΔL ≈ 25 vs Megvii median 2.4, texture loss 46–72 % vs Tencent/Megvii 13–15 %.
**Disclosure:** the per-group medians of the *Alibaba* pair measurements were printed during this diagnosis. They are not used
for any RU2 choice: every RU2 range below is set from Tencent levels and Megvii medians. Alibaba remains never-trained.

**RU2 changes (everything else identical to RU1):**
1. *Vendor single-operation components* (`decompose.py`): each Tencent/Megvii render is split into four single-op images in
   the original's geometry: eye (DIS flow inside the eye regions), jaw (flow elsewhere), white (low-pass photometric
   residual, σ = 6 px at 512), smooth (high-pass residual). By construction the parts recompose the render exactly (108 dB).
   Each component carries a one-hot presence label and its own `measure_pairs` quantities.
2. *Light synthetic strengths* (`ops.random_op_v2`, log-uniform, calibrated on FFHQ Part7 only): eye +0.3–4.6 %, jaw
   −0.3–4 %, ΔL ≈ 0.5–33, texture loss ≈ 3–32 %.
3. *Filter-item mixture*: synthetic v2 0.30, vendor single components 0.30, vendor composites 0.15, observed FF++ filters 0.25.
4. Composite presence stays 1111; quantity targets for components are measured, masked where measurement failed.
Bars R1–R4, D1–D2 unchanged. Seeds: EffB4 20260929, then a second seed if R1 passes. Model selection unchanged (FF++ val F1 +
vendor-val F1; vendor-val now also contains the components of held-out base indices).

## Addendum 2 (2026-09-29, after RU2 seeds 1–2; before any threshold is computed)

**RU2 result:** R1 FAIL in both seeds (balanced 72.7 / 70.9 %), R3 PASS (→fake 0.32 / 0.25 %), R2 and R4 FAIL. In-vendor held-out:
single-op presence TP rose from .04–.39 (RU1) to .69–.86 for eye/lift, but originals → real fell from 95.0 to 73.4 / 63.5 %;
blind quantities rank the measured edit weakly even in-vendor (ρ −.02 to .41), so R4 is a failure of the quantity head, not a
vendor gap. Paired rank on Alibaba is 94.2 / 94.3 %: the separation exists, the argmax operating point moved.

**Secondary analysis (declared now, reported as secondary, never replaces R1):** a single threshold t* on p(filter) is chosen per
model on the **vendor validation split only** (Tencent/Megvii held-out base indices: originals as negatives, composites and
single-op components as positives) by maximising balanced accuracy, and applied unchanged to Alibaba. Reported: Alibaba
balanced accuracy, originals → filter, retouched → filter per operation, retouched → fake (unchanged by construction only if
the fake decision stays argmax; here the rule is: fake if p(fake) is the argmax, else filter if p(filter) ≥ t*, else real).
Also reported, threshold-free and descriptive: Alibaba AUROC of p(filter), originals vs retouched. Bar for the secondary
analysis: balanced ≥ 75 % (same number as R1). Applied to RU1, RU2 s1, RU2 s2.

## Addendum 3 (2026-09-29 evening, before RU3 / RU3-E / RU-CLIP are trained) — top-venue arms

Context: docs/RESEARCH_PLAN_20260930_topvenue.md. Alibaba is re-opened under a rule: one evaluation per pre-registered arm,
all design choices from training-vendor data only.

**RU3 = RU2 with component cleaning.** Diagnosis (training vendors only): of the 82,395 single-operation components, the
component's own quantity is below the measurement noise floor for ~25–35 % (eye/jaw p25 ≈ 0.000–0.006 with calib residual
σ ≈ 0.008; Megvii smooth p10 = −0.09; Tencent white p10 = −0.09). Labelling near-unedited images *filter* teaches
"untouched → filter", which is what RU2 does (originals → filter 23–33 % on Alibaba; vendor-val originals → real 63–73 %).
Rule: keep a component only if its own q ≥ floor: eye 0.008, jaw 0.008, white 0.05 (ΔL ≥ 1), smooth 0.03. Everything
else identical to RU2 (mixture, strengths, recipe, 12 epochs, seed 20260929).
Bars: R1 ≥ 75 %, R3 ≤ 5 % (≤ 10 % per cell), D1 CDFv2 ≥ 0.80 / DFD ≥ 0.90 / Celeb-DF-B ≥ 0.88 / escape Δ ≤ +3 pp / B1 0/13,
vendor-val originals → real ≥ 85 %.

**RU3-E = RU3 + evidence head** (1×1 conv on the backbone feature map, 12×12 at 380 px, BCE+Dice, weight 1.0), supervised by
the exact footprint M = dilate(|x − x0| > 6, 25 px at 380) wherever x0 exists: synthetic ops (x0 = base), self-blends (x0 =
base), vendor components and composites (x0 = the FFHQ original at the same geometry), FF++ scripted filter frames (no: their
originals are not loaded in this pipeline → masked), observed forgeries (masked), reals (empty target).
Bars: as RU3, plus E1 on the held-out part edits (donor / SD / SDXL): flip ≥ 80 % and within 5 pp of the GT-footprint ceiling,
IoU7 ≥ 0.65 (eval_cgd_explain protocol).

**RU-CLIP = frozen CLIP ViT-L/14 (openai, 224 px) + LoRA (rank 16, q/k/v/out in all 24 blocks) + the three RU heads on the
CLS token; RU3 data and mixture; AdamW 1e-4 (LoRA + heads), cosine, 8 epochs, batch 16 photographs (48 images), bf16.**
Inference parameters ≈ 304 M (reported as such). Bars: C1 CDFv2 frame AUC ≥ (official Effort on our frames) − 0.01, C2
Celeb-DF-B escape Δ ≤ +3 pp, C3 Alibaba retouched → fake ≤ 5 %, C4 R1 ≥ 75 %, D2 as before. If Effort's weights cannot be
obtained, C1 becomes ≥ 0.87 (its published frame AUC 0.882 minus the frame-set uncertainty we measured for other detectors).

**SOTA baselines (Effort, Forensics Adapter): descriptive, no bar.** Scored on CDFv2 std32, DFD std32, Celeb-DF-B v3, FF++
escape set, Alibaba pairs, with their official preprocessing; compared with their published numbers first.

## Addendum 4 (2026-09-29 23:30, before RU4 is trained) — the unified model
RU-CLIP-E's evidence head fails E1 on part-level edits because the RU pool has none (detect rate 18–56 %). **RU4 = RU3-E data +
the 61,510 training part-level edits (donor transplant, SD-1.5 inpaint) as fake items with their exact footprints** (fake mixture:
self-blend 0.40 / observed 0.30 / part edit 0.30; everything else as RU3-E). Two backbones: EfficientNet-B4 (ru4e) and CLIP
ViT-L/14 + LoRA (clipe4). Bars: E1 (donor / SD / SDXL flip ≥ 80 % and within 5 pp of the ceiling, IoU7 ≥ 0.65) plus all RU3
bars (R1 ≥ 75 %, R3, D1/D2, C1–C4 for the CLIP variant). Seeds 20260929; a second seed if the bars pass.

**RU4 result, CLIP variant (clipe4, seed 20260929, evaluated 2026-09-30 05:26; one Alibaba read):** E1 PASS on all three
held-out editors (flip 91.7 / 91.5 / 90.9 % vs ceilings 91.9 / 91.6 / 91.2; IoU7 0.832 / 0.845 / 0.827). D1 PASS (CDFv2 0.888,
DFD 0.948), C1 PASS (video AUC above Effort and Forensics Adapter on both sets), C3 PASS (retouched -> fake 0.12 %), R3 PASS.
R1 FAIL (balanced 70.2 %; originals -> real 57.9 %), R2 FAIL, R4 FAIL, D2 FAIL (FF++ real 78.0, fake 88.9). C2 PASS (Celeb-DF-B escape +2.87 pp [1.15, 4.84]; untreated AUC 0.937). Per the bars a second seed is not triggered by R1; the E1 pass is a single seed.
**RU4 result, EffB4 variant (ru4e, 09:21):** E1 PASS (flip 87.8 / 87.4 / 86.9 vs ceilings 87.8 / 87.6 / 87.2; IoU7 0.80-0.82), D1 PASS (0.848 / 0.915), R3 PASS; R1 FAIL (72.6 %), R2 / R4 / D2 FAIL. E1 therefore holds on two backbones with the same data.
