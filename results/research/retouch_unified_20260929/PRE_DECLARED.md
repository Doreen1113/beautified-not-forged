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

## Addendum 5 (2026-10-05, before the RU4-CLIP re-runs are trained) — checkpoint selection defect
**Evidence (training / validation only; no test set involved).** `split_eval.py` (2026-10-01) showed that clipe4 keeps only
59.5 % of its own *training* FFHQ originals real. The training log explains it. The selection criterion of every RU arm is
0.5 x (FF++ val macro-F1 + vendor-val F1 of the *filter* class), and the vendor validation set has 10,579 filter items and
816 originals, so that F1 hardly changes when originals are called filter. Back-computing filter recall from the logged F1
and originals->real gives, for clipe4 (epoch: originals->real / filter recall / balanced): e3 82.6 / 82.7 / 82.7,
**e4 57.2 / 93.4 / 75.3 (selected)**, e5 83.7 / 85.5 / 84.6, e6 78.1 / 89.8 / 83.9, e7 80.8 / 89.4 / 85.1, e8 78.7 / 90.0 / 84.3.
The criterion selected the epoch with the lowest specificity of epochs 3-8. Only the selected epoch was saved, so the other
epochs cannot be evaluated. For the other arms the two criteria pick epochs with similar validation behaviour (clipe s1
e7 vs e8, clipe s2 e4 vs e8: originals->real 72.4 vs 77.2; ru4e e12 vs e11: 81.1 vs 85.8).

**Re-run (declared before training).** RU4-CLIP exactly as Addendum 4 (data, mixture, LoRA, optimiser, 8 epochs; no change
to the recipe), tag `clipe4r`, seeds 20260929 and 20260930, **every epoch saved**. The checkpoint of each seed is chosen
afterwards by `select_epoch.py` on validation data only, with the evaluation preprocessing (`eval_ru.run`):
  **C2 = 0.5 x (FF++ val macro-F1 + vendor-val balanced accuracy)**,
vendor-val balanced accuracy = mean of (filter items called filter, originals not called filter) on the held-out Tencent /
Megvii bases: 816 originals, 2,136 renders and the 5,684 components above the noise floor (the cleaning used for training).
Ties go to the earlier epoch. No test set, no Alibaba image and no cross-dataset number enters the choice.

**Reporting.** Each selected checkpoint reads Alibaba once and is evaluated on everything clipe4 was (FF++, CDFv2, DFD,
Celeb-DF-B, held-out part edits, paired tests vs SBI / Effort / Forensics Adapter). Seed 20260929 becomes the paper's main
model whichever seed tests better; seed 20260930 is reported next to it. The earlier clipe4 checkpoint stays in the
supplement as "selected by filter F1". All bars of section 4 and Addenda 1-4 are unchanged (R1 >= 75 %, R2, R3, R4, D1, D2,
C1-C4, E1) and a miss is reported.

**Expectation, written before the runs (not a bar).** Vendor-val originals->real rises to roughly 78-85 %. On Alibaba the
AUROC of P(filter) has been 0.80-0.82 for every arm trained with components, so balanced accuracy is expected to stay at
70-74 % and R1 to be missed again; what should change is the operating point (originals->filter well under 42 %, renders->filter
lower than 82 %). If cross-dataset AUC or E1 get worse at the selected epoch, that is reported as the cost.

**Exploratory analyses (post hoc on existing Alibaba scores, labelled as such in the paper; no model or rule is chosen from
them):** detection rate as a function of the measured edit magnitude (pairs_ali.tsv), and image statistics of the untouched
originals that receive a high P(filter).

## Addendum 6 (2026-10-05 22:00, before RU5 is trained) — fair metric, and two questions instead of one softmax
**Metric correction (applies to every model, old and new).** Until today MISS for a three-way model counted only
forgeries called *real*; forgeries called *filter* were counted nowhere, and binary detectors have no such bin. From now
on every detector is scored by one rule: score = P(fake); AUC on untreated, beautified and compression-only pairs; and at
the threshold of 5 % FPR on untreated genuine frames, MISS = forgeries not called fake and FA = genuine frames called
fake. The native three-way decision is reported next to it with forgeries called filter counted as missed. Under this
rule on Celeb-DF-B the old main model's beautification-only rise in MISS is +11.0 pp (Effort +11.0, Forensics Adapter
+15.2, SBI +21.8) and its AUC falls from 0.937 to 0.843 (Forensics Adapter 0.909 -> 0.828, Effort 0.909 -> 0.807). The
claims "not affected by beautification" and "a third class removes the effect" are withdrawn.

**Validation evidence for the cause (`leak_probe.py`, FF++ val and held-out Tencent / Megvii bases only).** clipe4r s1:
self-blend forgery called fake 94.5 %; with the photograph's own commercial texture edit added 80.4 % (19.6 % to filter)
while P(fake) > P(real) stays at 95.1 %. Genuine FF++ val frames called fake 13.4 %; with a colour filter never used in
training 33.6 % (forgeries with the same filters: 97.0 %).

**RU5 (`train_ru5.py`), declared before training.** RU4-CLIP recipe with three changes: (1) forged and beautified are two
sigmoid heads (binary cross-entropy each; fake + beautification on top is (1,1)); (2) random colour grading as a filter
source and on top of forgeries; (3) the pixel-aligned photometric edit of a commercial component added to a self-blend of
its own original, labelled fake. Ablations, each one change removed: `--softmax`, `--no-grade`, `--no-vendor-fake`.
Seeds 20260929 (main) and 20260930. Every epoch saved; epoch chosen by C2 (Addendum 5) on validation data.
**Validation bars (leak_probe.py; a miss is reported):** V1 forgery + commercial texture edit called fake >= 90 %;
V2 genuine + unseen colour filter called fake <= 20 % with forgery + unseen filter called fake >= 93 %; V3 FF++ val
macro-F1 >= 0.85 and vendor-val balanced accuracy >= 84 %. The eleven held-out pilgram filters are from now on
development data, not test data.
**Test (read once per selected checkpoint, same rule for all 13 detectors):** T1 Celeb-DF-B AUC on beautified pairs
above Forensics Adapter (0.828) and Effort (0.807) with a paired video-cluster interval that excludes 0; T2
beautification-only rise in MISS at 5 % FPR <= 5 pp with FA on beautified genuine frames <= 10 %; T3 CDFv2 / DFD video
AUC not below clipe4r by more than 0.01; T4 the Alibaba, E1 and R bars as before. Celeb-DF-B is not used for any choice.

## Addendum 7 (2026-10-06 02:40, before RU6 is trained) — consistency of the forged logit
**RU5 seed 20260929 (epoch 6 by C2), validation:** V1 PASS (forgery + commercial texture edit called fake 94.9 %), V2a PASS
(genuine + unseen colour filter called fake 15.1 %), V2b FAIL (forgery + unseen filter called fake 90.0 %, bar 93),
V3 PASS (0.872, 85.3 %). **Test, one rule for all:** Celeb-DF-B AUC on beautified pairs 0.866 [0.841, 0.890]; paired
difference to Forensics Adapter [+0.013, +0.064], to Effort [+0.030, +0.089] (T1 PASS); beautification-only rise in MISS
+6.7 pp [4.0, 9.5] (T2 FAIL on the 5 pp bar; Effort +11.0, Forensics Adapter +15.2, clipe4r +14.8 / +11.6); FA on
beautified genuine 9.5 % (pass); CDFv2 / DFD frame AUC 0.891 / 0.956 (T3 pass at frame level); Alibaba balanced 73.45 %
(R1 FAIL), originals -> filter 20.8 %. Per preset the AUC still falls by 0.04-0.11 (brown -0.105, hawaii_grain -0.087),
about as much as for Effort and Forensics Adapter: RU5 improves the fixed-threshold escape, not the separability.
**RU6 (`train_ru6.py`), declared before training:** RU5 plus (a) a fourth item per photograph, the forgery under one more
random colour look with stronger tint and grain, labelled (forged, beautified) = (1, 1); (b) a smooth-L1 consistency term
on the forged logit between the forgery and that fourth item, and between a genuine photograph and its own filtered
version when the filter was applied to that photograph (weight 1). Seed 20260929; epoch by C2; same validation bars V1-V3
and test bars T1-T4 as Addendum 6. RU6 replaces RU5 as the main model only if it passes V2b and lowers the
beautification-only rise in MISS without lowering the beautified-pair AUC; otherwise RU5 stays and RU6 is an ablation row.

## Addendum 8 (2026-10-06 10:00, before any model sees AR filters) — Instagram AR beauty filters
**Finding (test-only data, `eval_fairbeauty_pairs.py`, `fairbeauty_baselines.py`):** on 2,927 FairFace validation faces and
their FairBeauty versions (8 Instagram AR beauty filters), at 5 % FPR on the untouched originals, the share of filtered
GENUINE faces called fake is 10.7-41.5 % for the eight FF++ CNN detectors and SBI, 63.9 % Forensics Adapter, 67.7 % Effort,
78.4 % clipe4r, 75.1 % RU5. RU5 also calls 26.1 % of the untouched FairFace originals fake. No RU training source contains
AR filters or in-the-wild still photographs of this kind.
**Data split, fixed now.** FairBeauty TRAIN with FairFace train originals (padding 1.25), same extractor, every 2nd file,
filters Pretty / hary beauty / Shiny foxy / Caramel Macchiato / Cute baby face -> training (filter items (0,1), originals
real items). Filters Baby_cute_face / big city life / Just Baby are never trained on. Test sets: FairBeauty validation pairs
(all 8 filters; the 3 held-out filters reported separately as "unseen AR filters"), B-LFW with the LFW control. Neither is
used for any choice. FairFace validation originals are not used for training.
**RU7 = RU6 + AR pairs** (`train_ru7.py`): FairFace train originals join the real bases (landmarks cached), their FairBeauty
versions join the filter sources. AR filters cannot be transferred onto forgeries (no pixel alignment), so they appear on
genuine faces only; the risk that AR evidence is learnt as "genuine" is measured on Celeb-DF-B beautified deepfakes (T2).
**Bars (test, read once per selected checkpoint):** A1 FairBeauty val, held-out filters: filtered genuine called fake at
5 % FPR on originals <= 15 % (RU5: 75.1 % on all filters); A2 untouched FairFace val originals called fake (argmax) <= 10 %;
A3 B-LFW filtered genuine called fake (argmax) <= 20 %; T1-T4 and the Alibaba bars unchanged. Validation bars V1-V3 unchanged,
plus V4: FairBeauty TRAIN held-out-filter faces are not available for validation, so V4 uses the 5 training filters on
held-out FairFace train ids (10 % by hash): called fake <= 10 %.

## Addendum 9 (2026-10-06 12:00) — equal-data binary control and verdicts on RU6
**RU6 (consistency term) is not adopted:** Celeb-DF-B beautified AUC 0.877, beauty-only rise +5.6 pp, but FF++ fake recall
84.1 %, FA 15.1 %, CDFv2 0.862 (T3 fail). It stays as an ablation row. **RU5 seed 20260930** (epoch by C2): AUC-b 0.883,
+8.4 pp, Alibaba balanced 75.42 % (R1 pass for the first time; seed 1 73.45 %). Seed spread of AUC-b is 0.017.
**Binary control, declared now (`train_ru5.py --binary`, tag clipe5b):** exactly the RU5 data and mixture, one forged /
not-forged logit, no beautified, presence or evidence supervision. If it matches RU5 on T1-T2 within the seed spread, the
paper attributes the gain to the beautification-aware training data, not to the filter class or the heads, and says so.
**Claims policy:** cross-dataset AUC against Effort / Forensics Adapter is reported with the training data of every model
listed; no superiority claim is made across unequal data. Method claims rest only on equal-data controls.

## Addendum 10 (2026-10-06 14:00, before RU7 is trained) — ablation verdicts; RU7 is built on RU5
**Ablations of RU5, seed 20260929, same rule (Celeb-DF-B AUC-b / beauty-only rise in MISS / V1):** full RU5 0.866 / +6.7 / 94.9
(seed 2: 0.883 / +8.4 / 95.9); without random colour grading 0.863 / **+14.4** / 95.0; without the commercial edit on
forgeries 0.877 / +2.7 / **79.3**; three-way softmax on the same data 0.885 / +8.8 / 95.7. Reading: the random colour
grading carries the reduction of the escape on Celeb-DF-B; the commercial edit on forgeries fixes only the leak it targets
(V1) and is not shown to help Celeb-DF-B; the two-sigmoid head is not shown to matter (within the seed spread of 0.017).
**RU7 = RU5 + AR pairs (not RU6, which Addendum 9 rejected).** `train_ru5.py --ar`, tag clipe7: 22k FairFace train originals
(ids with md5 % 10 != 0) join the genuine bases; the filter item is replaced by a FairBeauty image of one of the five
training filters with probability 0.2 (no footprint, no operation targets). Seeds 20260929 then 20260930. Bars A1-A3, V4,
T1-T4 as in Addendum 8.

## Addendum 11 (2026-10-06 14:20) — FF++-only control (equal training data with the published baselines)
`train_ru5.py --ffpp-only`, tag clipe5f: the RU5 recipe restricted to the FF++ c23 training videos that Effort, Forensics
Adapter, GenD and DFD-HR train on. Genuine bases: FF++ real frames only. Filter items: scripted landmark / skin operations,
random colour grading, the precomputed FF++ filter frames. Fake items: self-blend 0.5, observed FF++ forgeries 0.5. No
FFHQ, no commercial renders or components, no part-level edits, no FairBeauty. Epoch chosen by FF++ validation macro-F1
alone (no commercial validation data). Seed 20260929. Reported next to the baselines as the equal-data row for T1-T3; the
Alibaba, AR-filter and part-level results of this model are reported as "no such training data".

Addendum 9, selection rule added 2026-10-06 14:40 before the binary control is evaluated: it has no filter output, so its epoch is the one with the highest FF++ validation AUC of P(fake) (real vs fake frames).

## Addendum 12 (2026-10-06 19:20, before RU8 is trained) — RU7 verdict; AR evidence on forgeries
**RU7 seed 20260929 (epoch 6 by C2).** AR bars: A1 PASS (held-out filters, filtered genuine called fake at 5 % FPR 0.1 %; RU5
75.1 %), A2 PASS (FairFace val originals called fake 0.3 %; RU5 26.1 %), A3 PASS (B-LFW called fake 0.0 %). Every FairBeauty
image, trained or held-out filter, is called filter (100.0 %). **T2 FAIL and worse than RU5:** Celeb-DF-B beauty-only rise in
MISS +17.2 pp [14.2, 21.0] (RU5 +6.7); natively 26.6 % of beautified deepfakes are called filter (RU5 16.6 %). AUC-b 0.869,
CDFv2 0.904, DFD 0.957, FF++ FA 5.1 %, Alibaba balanced 74.1 %. The risk named in Addendum 8 happened: filter evidence seen
only on genuine faces is learnt as evidence against forgery. RU7 is not adopted.
**Caveat on A1-A3:** 100 % on held-out filters and on B-LFW may be the OpenFilter capture pipeline (all FairBeauty and B-LFW
images are produced by the same emulator pipeline) and not the filters. Control to run: FairBeauty images with the face hull
greyed out, against FairFace originals treated the same way; if they are still called filter, A1-A3 measure the pipeline.
**RU8 = RU7 + AR-filtered faces that are forged** (`--ar --ar-fake 0.15`, tag clipe8): with probability 0.15 the fake item
is a self-blend of a FairBeauty training image (five training filters), labelled (forged, beautified) = (1, 1), footprint
exact. Seed 20260929. Adopted only if A1-A3 stay passed and the beauty-only rise in MISS returns to RU5's level or below
(<= 8.4 pp) with AUC-b not below 0.866.

## Addendum 13 (2026-10-06 19:50) — AR result is a pipeline shortcut; equal-data ablation of the colour grading
**Control (`ar_pipeline_control.py`, 599 FairBeauty val pairs, RU7):** with the whole face hull greyed out, 94.8 % of the
filtered images are still called filter (originals treated the same way: 0.0 %); with everything outside the hull greyed,
43.7 %. RU7 reads the OpenFilter capture pipeline in the background, not the face edit. A1-A3 are therefore NOT evidence of
AR-filter recognition, and the accusation rates of the published detectors on FairBeauty (10.7-78.4 %) are confounded with
the same pipeline: FairBeauty and B-LFW can only be reported as 'AR filter plus capture pipeline'. No AR claim is made until
a source with a no-filter pass through the same pipeline, or filters applied by us, is available.
**Declared now, before training:** clipe5fg0 = FF++-only control without the random colour grading (seed 20260929; epoch
by FF++ val macro-F1); clipe5f seed 20260930. Claim under test: in the equal-data setting the colour grading on genuine and
forged faces is what lowers the beauty-only rise in MISS (clipe5f +7.5 pp; expectation for clipe5fg0: above +11 pp).

## Addendum 14 (2026-10-06 19:30, before any model is scored on it) — second beautification test source
Celeb-DF-v2 standard frames (516 videos) under one of the eleven pilgram colour filters never used in RU training, one filter
per video, seed 20261006, saved as PNG from the untreated frame (no re-encoding confound). Metrics as for Celeb-DF-B, one
rule for all 13 published detectors and ours: AUC filtered-pair, and at 5 % FPR on untreated genuine frames the rise in
MISS and in FA. These filters were development data for V2 (FF++ validation), so this set tests transfer of the
colour-look invariance to a different dataset, not to unseen filters; the paper says so. Bars: none (reporting only).

Addendum 13 result (2026-10-06 21:30): expectation met. clipe5fg0 (no colour grading) beauty-only rise +14.1 pp [10.7, 17.8]
vs clipe5f +7.5 / +9.1 (two seeds); AUC-b 0.849 vs 0.872 / 0.870. The equal-data claim of Addendum 11 stands on two seeds.

## Addendum 15 (2026-10-07, before training) — worst-case beautification training
**Evidence for the design (test-set diagnosis, so the test set below is no longer clean for this purpose and is labelled
so).** On Celeb-DF-v2 + held-out colour filters the damage is concentrated in four of eleven filters: earlybird and mayfair
(vignette / radial light overlay) raise P(fake) of genuine frames by +0.2..+0.7 for every model; inkwell and moon
(monochrome) lower P(fake) of forgeries by 0.1-0.25. Seven pure colour looks change AUC by less than 0.06. The hand-written
random grading (Addendum 6) has a weak vignette and no full desaturation.
**Method (`adv_beauty.py`, `train_ru5.py --adv worst`).** A differentiable beautification operator B(x; u) (tone curve,
colour matrix, saturation down to monochrome, contrast, a smooth 4x4 spatial luminance and tint field, smoothing, grain; all
bounded) and, at every step, one signed-gradient ascent step on u from a random start that maximises the forged-logit loss
of the genuine and forged items; the model is then trained to keep the forged label on these views (beautified target 1).
Control `--adv random`: the same operator with random u, no ascent. Both in the FF++-only setting first (tags clipe5af,
clipe5rf), seed 20260929, epoch by FF++ val macro-F1.
**Bars.** M1 Celeb-DF-B (still clean for this purpose): AUC-b above clipe5f's two seeds (0.872 / 0.870) by more than the
seed spread, i.e. >= 0.890, and beauty-only rise in MISS <= 7.5 pp. M2 Celeb-DF-v2 filtered (diagnosed, development-level):
AUC-f >= 0.84 (clipe5f 0.797; Forensics Adapter 0.790). M3 CDFv2 / DFD v3 untreated AUC not below clipe5f by more than
0.01. M4 worst > random on M1 and M2, otherwise the paper credits the operator family and not the search.
A fresh colour-filter test source that this design has not seen is needed for the final claim; it will be built from DFD
v3 with filters not in pilgram's list.

## Addendum 16 (2026-10-07, written while clipe5af / clipe5rf are still training; no result of either has been read)
**Prior art (literature check of this date, `docs/COMPETITORS_20261006.md` section "worst-case beautification").** Closest:
Fatima et al. arXiv 2512.22303 (worst-of-K random counter-forensic transforms, selection without gradient); Hsiung et al.
CVPR 2023 (adversarial training over composite semantic perturbations, general vision); Hou et al. CVPR 2023 and AdvShadow
ICASSP 2024 (gradient-optimised natural appearance attacks on forgery detectors, attack only); Saeed et al. 2509.07178
(fine-tuning on fixed enhanced samples). The paper may not claim the first adversarial augmentation for forgery detection,
nor the first two-sided beautification finding (Libourel 2024, Concas 2025).
**Added control: worst-of-K.** `train_ru5.py --adv worstk`: K = 4 random draws of u, keep per sample the one with the
highest forged-logit loss, no gradient (tag clipe5kf). M4 is extended: the gradient search is credited only if clipe5af
beats both clipe5rf and clipe5kf on M1 and on the fresh source below; if it only matches clipe5kf the paper says
"worst-case selection in a bounded beautification space" and reports both.
**Single-step overfitting probe (`adv_probe.py`, FF++ val frames only).** For each checkpoint: accuracy of the forged
decision (P(forged) > 0.5) on genuine and forged val frames under no edit, a random u, the 1-step search, and a 10-step
search (step 0.3 per step). Catastrophic overfitting is flagged when accuracy under 10 steps is more than 30 pp below
accuracy under 1 step for the worst-case model.
**Fresh colour-filter source (`build_dfd_filtered.py`).** DFD v3 (332 videos, 10,404 frames) with one filter per video,
seed 20261007, from sixteen filters that are in neither the training lists nor the Celeb-DF-v2 diagnosis: the fourteen
pilgram2 filters absent from pilgram (amaro, ashby, charmes, crema, dogpatch, ginza, hefe, helena, juno, ludwig,
poprocket, sierra, skyline, sutro), PIL grayscale (BT.601) and the standard sepia matrix. Same metrics as Addendum 14.
No design decision may be taken from per-filter results on this source.
**Bar M5 (fresh source).** clipe5af AUC-filtered exceeds clipe5f's with a paired video-cluster bootstrap interval that
excludes 0, and is not below Effort's and Forensics Adapter's. Reported whatever the outcome.

## Addendum 17 (2026-10-07, before running) — representation-level analysis and two refinements of the robust objective
**Framing.** The method is robust risk minimisation over a structured perturbation set: min_θ E[ℓ(f(x),y) + max_{u∈U} ℓ(f(B(x;u)),y)],
with U the bounded identity-preserving beautification space of `adv_beauty.py` instead of an Lp ball, the inner max by
signed-gradient ascent, applied to genuine and forged faces with the forged label kept. Everything below serves that one claim.
**A. Shift-subspace probe (`subspace_probe.py`, post hoc, no training).** On FF++ train frames the feature shifts caused by
training-available beautifications (operator random draws, random_grade) are decomposed by SVD; on FF++ val frames under the
eleven held-out pilgram filters we report, per filter, the cosine between the mean shift and the forged weight vector, the mean
logit change on genuine and forged frames, and the shift energy inside the training subspace. Then the training subspace
(first k directions) is projected out and the forged logistic head is refitted; k is chosen on FF++ val only (lowest
genuine-called-forged rate under the held-out filters subject to clean AUC within 0.01 of the refit without erasure). Outcome
rules: if erasure with the chosen k lowers FA under held-out filters by >= 10 pp on val for the FF++-only checkpoint, it becomes a
candidate component and is then tested once on the test sources together with the trained arms; otherwise it is reported as an
analysis only. The mechanism numbers are reported whatever they show.
**B. Data-driven bounds and a plausibility prior (`fit_operator.py`, no training).** The operator parameters u are fitted by
gradient descent to (original, retouched) pairs of the Tencent and Megvii training split and to (frame, training colour filter)
pairs of FF++ train frames. Reported: PSNR of the fit per family (how much of a commercial edit the operator explains; the
residual is skin smoothing and geometry), the per-parameter 1st–99th percentile range, and a diagonal Gaussian (mu, sigma) in
the unconstrained parameter space. Planned use (next training round, Addendum 18): U restricted to the fitted range, and the
ascent objective ℓ(f(B(x;u)),y) − λ‖(u−mu)/sigma‖² so the worst case stays plausible. The current hand-set bounds are not changed
for the arms already training.
**C. Multi-step ascent.** If `adv_probe.py` shows the 1-step model collapsing under 10 steps (Addendum 16 rule), a 3-step arm
(step 0.4) is added to the next round. Round-2 arms are chosen before any test-source number of round 1 is read; the test
sources (Celeb-DF-B, DFD v3 + sixteen filters) are read once per arm.

## Addendum 18 (2026-10-07, before any round-1 arm result is read) — round 2 arms, bars, order
**What has been read so far.** The thirteen published detectors and the six existing RU checkpoints on the fresh source
(`DFD_FILTERED.md`): all baselines lose AUC under the sixteen filters (Effort 0.939→0.904, Forensics Adapter 0.940→0.907,
SBI 0.829→0.803; Effort's MISS +12.3 pp); the FF++-only control loses 0.018 (0.943→0.925) and beats Effort with a paired CI
that excludes 0 [0.003, 0.038], ties Forensics Adapter [−0.0001, 0.037]; random grading helps on this source as on
Celeb-DF-v2 (clipe5f − clipe5fg0 [0.004, 0.027]); the binary control (full data, forged head only) is the best detector on
every metric (0.961→0.949), as it already was on CDFv2 (0.914), DFD v3 and Celeb-DF-B (0.896) before this source existed.
RU5 s1 shows a large MISS rise at the fixed threshold (+12.0) with an unchanged AUC (0.927): a uniform downward shift of
its scores under filters, consistent with the class-imbalanced frequency of random grading in RU5's sampling (filter items
graded 15–37 %, forged items 13–18 %, genuine items never) teaching a grade→not-forged association. Hypothesis, to be tested
by the arms below, in which both genuine and forged items receive the beautified view at every step. None of clipe5af /
clipe5rf / clipe5kf has been read.
**Round-2 arms (`train_ru5.py`; adversarial views on genuine and forged items at every step; selection on val only).**
- R2-1 `--ffpp-only --adv worst --adv-wide --adv-prior 2.5`: equal data, bounds widened to the fitted 99th percentiles,
  search confined to mu ± 2.5 sigma of the edits fitted to Tencent / Megvii / training colour filters (`fit_operator_prior_wide.npz`,
  random start from the fitted Gaussian, projection after each step). Selection ffpp_f1. Seeds 20260929, then 20260930.
- R2-2 R2-1 with `--adv-steps 3` (step 0.4): run only if `adv_probe.py` flags the 1-step model (Addendum 16 rule) or if
  R2-1 misses M1/M5 by less than the seed spread.
- R2-3 `--binary --adv worst --adv-wide --adv-prior 2.5`: full data, forged head only; the main-detector candidate.
  Selection ffpp_auc (as clipe5b). Two seeds.
- R2-4 `--detach-heads --adv worst --adv-wide --adv-prior 2.5`: full data, three-way output kept but the beautified,
  presence, quantity and evidence heads read detached features. Tests whether the 0.02 AUC cost of the factorised model
  (RU5 vs binary control on every source) is multi-task interference. Selection C2. One seed; second if within 0.005 of
  R2-3 on untreated DFD v3 and CDFv2.
**Bars.** FF++-only arms: M1–M5 of Addenda 15–16 unchanged (M5 on the fresh source: AUC-filtered above clipe5f's 0.925 with a
paired CI excluding 0, not below Effort 0.904 / Forensics Adapter 0.907). Full-data arms: untreated AUC on CDFv2 and DFD v3
not below the binary control by more than 0.005; filtered AUC on the fresh source above the binary control's 0.949 with a
paired CI excluding 0, or on Celeb-DF-B AUC-b above 0.896 with the CI excluding 0, and not below on the other. R2-4 passes
only if it also keeps the part-edit explanation bar (flip rate within 2 pp of the ceiling on donor_v2 / SD / SDXL).
**Order.** Ubuntu: clipe5kf (running next) → R2-1 s1 → R2-3 s1 → R2-4. Local: clipe5af (running) → R2-3 s2 → R2-1 s2.
Each test source is read once per arm, after selection. Any arm that fails is reported in the paper's ablation table.
**Amendment (same day, before any round-1 arm result).** The plausible set is not the Gaussian box mu ± 2.5 sigma: on the
narrow-bound fit that box gives a saturation floor of 0.49 and excludes monochrome, which the measured app filters reach
(0.18) and which the Celeb-DF-v2 diagnosis found damaging. The set is the per-element 0.5th–99.5th percentile range of the
edits fitted to the four measured families (`adv_beauty.load_prior`), and each search starts from one measured edit drawn
from that pool (jitter 0.05) rather than from N(0, 1). Flag `--adv-prior` (boolean), tag letter `p` unchanged. The round-2
tags are therefore clipe5awpf / clipe5awpb / clipe5awpd (seeds as in the order above).

## Addendum 19 (2026-10-07 16:10) — round-1 verdict for the 1-step CE arm, and the consistency arm
**Round-1 numbers read (Celeb-DF-B, Celeb-DF-v2 filters; the fresh DFD source not yet).** clipe5af (FF++-only, worst case,
1 step, CE on the label): Celeb-DF-B AUC-b 0.864 [0.837, 0.887], beauty-only rise +8.2 (clipe5f 0.872 / +7.5; bar M1 ≥ 0.890
and ≤ 7.5: **fail**); Celeb-DF-v2 filtered AUC-f 0.810 (bar M2 ≥ 0.84: **fail**; vs clipe5f [−0.010, +0.035]); untreated
CDFv2 AUC 0.876 vs clipe5f 0.898 (bar M3, drop ≤ 0.01: **fail**); the random-operator control clipe5rf reaches AUC-b
0.876 / +7.9, so M4 (worst > random) **fails** on M1. `adv_probe.py`: the 1-step model's genuine accuracy under the operator
is 71.5 % at one step and 25.0 % at ten (46.5 pp apart; Addendum 16 flag at 30 pp → the 3-step arm R2-2 is triggered).
**What the probe shows about why.** The operator's worst case is far more damaging for genuine faces than for forged ones
(base model: genuine 96 → 8.5 %, forged 93.5 → 74 %). Training on the label loss of those views therefore spends most of its
signal on "edited genuine stays genuine"; the 1-step model gains on genuine faces under edits (71.5 % at one step) but loses
on forged faces under random edits (89.5 → 79.5 %), i.e. it learnt that a heavily edited face is less likely forged. This
is the same error transfer as in Addendum 18 (grading frequency), now produced by the adversarial objective itself.
**New arm R2-5 (`--adv-obj kl`, tag letter t): consistency instead of the label.** The edited view must keep the clean
prediction: loss = CE(clean) + β·KL(Bern(p_clean) ‖ Bern(q_edited)) with gradient through both (TRADES form), β = 1, and
the search maximises the same KL (BCE with the clean probability as soft target). Both classes are then penalised for *any*
movement of the forgery score under an edit, which is the property the paper claims. Plausible set and wide bounds as
R2-1; FF++-only; one step; selection ffpp_f1. Designed after the round-1 test numbers above were read; Celeb-DF-B and the
DFD source are therefore read-once test sources for it but not blind to the fact that the CE objective failed.
**Order from here.** Ubuntu: R2-1 (running) → R2-5 → R2-2 (3-step CE). Local: R2-3 s2 (binary, full data; started 09:00,
kept) → R2-1 s2. Carrying a configuration to full data is decided by validation only: lowest genuine-called-forged rate under
the held-out FF++ val filters (`leak_probe`) with clean val AUC within 0.005 of clipe5f, plus the probe; not by test numbers.

## Addendum 20 (2026-10-07 18:30, before training) — estimate-and-invert canonicalisation
**Round-1 result that motivates it.** All three operator arms (random, worst of 4, 1-step search) are indistinguishable
from the random-grading baseline under beautification and lose 0.02–0.04 untreated AUC on CDFv2 (FINDINGS, round 1). Making
the classifier invariant by training on edited views costs clean accuracy and does not transfer to real filters.
**Mechanism.** Remove the global photometric edit before detection instead of asking the detector to ignore it. A ResNet-18
estimator E (`canon.py`) predicts the parameters of the invertible part of the operator (tone, colour matrix, saturation,
contrast, luminance/tint field; smoothing and grain off) and the detector reads B(x; E(x)). E is trained alone
(`train_canon.py`, FF++ train frames, 6,000 steps) to undo random edits (half drawn from the measured-edit pool, half from
the wide bounds) and to leave untreated frames unchanged; it never sees a test source or a held-out filter. Validation
(FF++ val only): PSNR to the original before/after canonicalisation for random edits and, as a generalisation check, for the
eleven held-out pilgram filters; identity PSNR on untreated frames. E is frozen when the detector trains.
**Arms.** C1 `--canon` FF++-only, no operator views (tag clipe5cf): does canonicalisation alone help? C2 `--canon --adv
random --adv-wide --adv-prior` (clipe5crwpf): canonicalisation plus plausible random views, so the detector also sees the
residual the inverse cannot remove. Selection ffpp_f1. Bars M1–M5 unchanged; in addition the untreated CDFv2 AUC must stay
within 0.01 of clipe5f (the failure of round 1). Celeb-DF-B and the fresh DFD source are read once per arm.
**Expectations written down.** Colour looks and vignettes should be largely undone (the operator reproduces app filters at
40 dB); monochrome and smoothing cannot be, so Celeb-DF-B presets with grain/smoothing are where this will fall short.

## Addendum 21 (2026-10-07 20:15, before training) — where does the full-data detection win come from?
**Fact already on file (`compare_sota_clipe5b_s20260929.json`).** The full-data binary model beats Effort and Forensics
Adapter at frame level with paired CIs excluding 0 on both standard sets: CDFv2 0.914 (vs Effort [0.010, 0.058], vs FA
[0.006, 0.045]); DFD 0.967 (vs Effort [0.011, 0.054], vs FA [0.009, 0.042]); video-level CIs include 0. The FF++-only
three-way model does not (CDFv2 [−0.006, 0.042] / [−0.009, 0.033]). The difference is some mix of (a) the binary head,
(b) FFHQ stills and commercial renders (external real data), (c) the 61,510 part-level forgeries synthesised on FF++ train
frames with exact footprints (no external face data; SD 1.5 inpainting and donor transplants).
**Arms (binary head, FF++ real data only, selection ffpp_auc as clipe5b).** D1 `--binary --ffpp-only` (clipe5fb): the
equal-data binary baseline. D2 `--binary --ffpp-only --ffpp-parts` (clipe5feb): D1 plus the part-level
forgeries (fake item: self-blend 0.35, observed FF++ forgery 0.35, part edit 0.30). Seeds 20260929 first, 20260930 if D2 passes.
**Bar.** D2 beats Effort and Forensics Adapter at frame level on CDFv2 and DFD with paired CIs excluding 0, and D1 does not;
then the paper may claim that exact-footprint part-level synthesis improves cross-dataset detection with the same real
data. If D1 already passes, the claim is about the training recipe, not the synthesis. If neither passes, the full-data win
is attributed to external real data and reported as such. Beautification metrics are reported for both arms as well.

## Addendum 22 (2026-10-07 22:40, agreed with the user) — stop rule and standing adversarial review
**Stop rule for the operator-training line.** Four label-loss arms have failed M1–M3. R2-5 (consistency objective) and R2-2
(three steps) are the last two arms of this line. If neither passes M1 and M5 with untreated CDFv2 within 0.01 of clipe5f,
the line is closed: no further variants, and the paper reports it as a negative result with the probe analysis.
**Adversarial review.** After every round, an independent reviewer session that is given the code and result files but not
the conclusions checks evaluation leaks, selection on test data, statistics and claims. A result enters the paper only
after that review. First review: when R2-5, the full-data binary arm and D2 have been evaluated.

## Addendum 23 (2026-10-08 01:30, before running) — is a beautification a common shift of all patch tokens?
**Results read since Addendum 22.** R2-5 (consistency objective, clipe5awptf): Celeb-DF-B AUC-b 0.856, beauty-only rise
+13.0: fails M1. Full-data binary + plausible worst case (clipe5awpb, seed 20260930): 0.942 / 0.892, rise +9.7, against the
binary control's 0.949 / 0.896, +7.0: no gain. Five of the six operator arms have failed; R2-2 (3 steps) is the last.
**Reading of the failures.** The operator's random 4 x 4 luminance / tint field puts smooth colour inconsistencies inside
the face crop, and training the detector to ignore them removes a real forgery cue (colour mismatch between the inner face
and its surroundings), which is the cue Celeb-DF-v2 forgeries carry; hence the 0.02–0.04 loss on untreated CDFv2 and none
on DFD. Invariance by exposure trades forgery evidence for robustness because the two share directions (Addendum 17 A).
This reading is a hypothesis; it has not been tested directly.
**Hypothesis (structural, not by exposure).** A global edit moves every patch token of an image by nearly the same vector;
a forgery is a difference *between* regions of the same image. If so, a forgery score that reads only within-image
contrasts of the tokens (inner region minus outer ring; dispersion over positions) is invariant to the common shift by
construction and keeps the forgery evidence. `token_probe.py` measures (1) the common-shift fraction rho of the held-out
filters on FF++ val, (2) linear probes fitted on clean train frames only: pooled feature vs within-image contrast features.
**Decision rule.** If rho >= 0.6 on average and a contrast probe fitted on clean frames lowers FA under the held-out
filters by >= 8 pp relative to the pooled-feature probe fitted on the same frames, at clean AUC within 0.02, a detector
with a self-referenced head is trained (Addendum 24, to be written before training). Otherwise the hypothesis is recorded
as rejected. Validation data only.
**Validity note on the two synthetic filter sources.** In `cdf_filtered` and `dfd_filtered` the filter is applied to the
face crop, not to the full frame before cropping; a vignette is then centred on the face, which is harsher than what a
filter on a whole photograph produces (in Celeb-DF-B the presets were applied to the whole video). To be rebuilt with the
filter on the full frame; until then the two sources are reported with this caveat.

## Addendum 24 (2026-10-08 02:10, before any score on the new crops) — each baseline under its own preprocessing
**Why.** Audit items 6 and 8: all thirteen baselines were scored on our crop (landmark box + 35 % margin), but ten of them
(the eight DeepfakeBench CNNs, Effort, Forensics Adapter) were trained on DeepfakeBench crops (dlib, five-point alignment,
scale 1.3, 256 px). Our re-runs of Effort and Forensics Adapter on our crop give video-level AUC 0.930 / 0.945 on CDFv2,
below the numbers their papers report, so the frame-level win of our binary model (Addendum 21) may be a crop effect.
**What is built.** `ffpp_benchmark_20260925/build_dfb_crops.py`: the DeepfakeBench crop of the same Celeb-DF-v2 test videos
(518 in the official list) and the same 332 DFD videos, 32 frames per video by np.linspace, with the alignment function
imported from the benchmark's own preprocess.py. `dfb_crop_eval.py` scores the ten baselines and our models on it.
**Rule for the claim (written before any score).** The comparison that counts is each detector under its own
preprocessing: ours on our crop against a baseline on the DeepfakeBench crop, paired over the videos both frame sets
contain. (a) If our full-data binary model still beats Effort and Forensics Adapter at frame level on both sets with
intervals excluding 0, the detection claim stands. (b) If the intervals include 0, the paper says "on par" and the earlier
frame-level win is reported as a crop effect. (c) If a baseline is better with an interval excluding 0, the paper says so.
Our models' scores on the DeepfakeBench crop and the baselines' on our crop are both reported, so the size of the crop
effect is visible for every detector. The beautification sources keep our crop for now; if (b) or (c) holds, they are
re-scored with the DeepfakeBench crop for the ten baselines before any beautification claim is finalised.
**Caveat known in advance.** Our DFD set is 332 of the 3,431 DFD videos, so no DFD number of ours is comparable to a
published DFD number; only detectors run by us on the same videos are compared. SBI uses its own RetinaFace pipeline and is
not covered by this addendum.

## Addendum 25 (2026-10-08 03:00, before training) — the attribution the paper's thesis needs: who gets the beautified views
**Calibration read first.** `docs/literature/TOP_VENUE_STANDARDS_20261007.md` (full texts of Effort, Forensics Adapter,
SBI, LSDA, ProDet, DFD-HR, GenD, the CVPR 2026 MID-FFD and DeepfakeImpact papers, the NeurIPS 2025 Moiré benchmark, and
others). Its conclusions for this project: the beautification measurement is of an accepted contribution type and is
unoccupied at the top venues; our detector is a baseline at parity, not a state-of-the-art claim; the 0.04–0.07 AUC kept
under beautification is the only method-side result on an open axis, and it counts only if an ablation attributes it to a
named ingredient and the ingredient also moves other detectors.
**Gap found in our own ablations.** Every model we have trained, including the "no grading" control, shows the scripted
operations and 14 colour filters on genuine faces (as the filter item) and on half of the forgeries. The comparison
"beautification in training on nobody / on genuine faces only / on both classes" has never been run, although it is the
thesis of the paper (a beautified face is not a forged one, and a beautified forgery is still forged).
**Arms (binary head, FF++ real data only, no operator views, selection ffpp_auc, seed 20260929; second seed for all three
if P2 differs from P0).** `train_ru5.py --binary --ffpp-only --beauty X`:
- P0 `--beauty none` (clipe5fbp0): genuine, forged, and a second untreated genuine copy in place of the beautified item;
  no forgery is beautified. Item count and class balance as in P2.
- P1 `--beauty real` (clipe5fbp1): beautified genuine faces as now; no forgery is beautified.
- P2 `--beauty both` (clipe5fb = D1 of Addendum 21): beautified genuine faces and beautified forgeries.
**Predictions written before training.** H1: P2 has a higher AUC on beautified Celeb-DF-B pairs and a smaller
beautification-specific rise in MISS than P0, paired video-cluster intervals excluding 0. H2: P1 lowers the false alarms
on beautified genuine faces relative to P0 but raises the misses on beautified forgeries (it learns that beautification
means genuine), so P1 is worse than P2 on AUC-b. H3: untreated CDFv2 / DFD AUC of P2 within 0.01 of P0.
**What follows.** H1 and H2 hold: the paper's method claim is the symmetric exposure, stated as a training rule that is
independent of the architecture, and the next arm applies the same rule to Effort's adapter and to a CNN (plug-in table).
H1 fails: the margin over Effort and Forensics Adapter is not attributable to the exposure rule; it is reported as a
property of the base recipe (CLIP + LoRA + self-blending + symmetric degradation) and the paper makes no method claim on
robustness. Either way the three arms go into the ablation table. Test sources read once per arm: Celeb-DF-B, DFD with
full-frame filters, and the commercial pairs; filtered CDFv2 as the development source.

## Addendum 26 (2026-10-08 15:20, before training) — plug-in test: the exposure rule inside Effort's tuning scheme
**Why.** Seed 1 of Addendum 25 gives P1 < P0 < P2 as predicted (FINDINGS 14:30). A training rule is a contribution only if
it is not tied to our model, so it is applied to Effort's own parameter-efficient scheme: the SVD-residual tuning of every
self-attention projection from the released Effort code (`effort_tune.py`, copied with attribution; 0.21 M trainable
parameters, plain cross-entropy as in the released detector), on the same frozen CLIP ViT-L/14, in our pipeline, FF++ only,
binary head. Arms: E0 `--tune effort --binary --ffpp-only --beauty none` (clipe5fbp0E), E2 `--tune effort --binary --ffpp-only`
(clipe5fbE). Seed 20260929; selection ffpp_auc.
**Prediction.** E2 − E0 on Celeb-DF-B: AUC-b positive and beauty-only MISS rise negative with paired intervals excluding 0,
untreated AUC within 0.01; the same ordering on the full-frame DFD filters. If it holds, the paper states the rule as
architecture-independent and reports the LoRA and Effort-scheme pairs side by side. If E2 ≤ E0, the rule is reported as
specific to our LoRA recipe and the method claim is narrowed accordingly. Not a comparison with the released Effort
checkpoint (different training data pipeline); only E2 vs E0 is interpreted.

## Addendum 27 (2026-10-08 16:00, before running) — decision from the spatial structure of the evidence map
**Idea.** Forgery and beautification overlap in feature direction (Addendum 17 A) but differ in spatial structure: a forgery is
local (replaced region, blending boundary), a beautification is global or follows the skin. Every detector in the comparison
pools the image into one vector, which merges "strong local evidence" with "weak evidence everywhere". A decision read from
the spatial concentration of a footprint-supervised evidence map would be insensitive to global edits by construction, and
the region it points to is the decision itself.
**Falsification first (`evidence_probe.py`, FF++ val + held-out filters, models that already have the evidence head:
clipe5f, clipe5).** Statistics of the 16 x 16 map: mean, max, top-5 % mean, concentration (share of mass in the top 10 %
cells), max minus mean; each used as a forgery score. Pass: a concentration-type statistic has FA under the filters at least
8 pp below the pooled logit's at the same clean operating point, with clean AUC within 0.03 of it, and filters raise the
map mean of genuine faces more than its max. Fail: filters raise max and concentration of genuine faces as much as the
mean, or the statistics have no clean discriminative power. On a fail the idea is recorded and dropped. Caveat known in
advance: the current heads were trained only on part-level footprints (eyes / nose / mouth) and never saw full-face swaps
with a mask, so a pass here is a lower bound on what a head designed for this would do, and a fail is not final for a head
trained with whole-face footprints (SBI self-blends have exact masks too).

## Addendum 28 (2026-10-08 16:45, before training) — forgery decision pooled from a forgery-evidence map
**From the probe (Addendum 27).** The structural statistic of the evidence map keeps its AUC under unseen filters where the
pooled logit does not, but the current map is an edit localiser (the beautified item's own footprint is its target) trained on
part-level footprints only, so it has little power on whole-face forgeries. Two changes follow directly.
**Design (`--mil`).** (1) Map target: exact mask on every forgery that has one (self-blend mask, part-edit footprint; observed
FF++ forgeries keep no mask term), **zero map on every beautified and genuine item** (the beautification footprint is no
longer a target). (2) Decision: the forged logit is the mean of the top 5 % cells of the map logits (multiple-instance pooling),
not a linear head on the pooled feature; the beautified logit stays on the pooled feature. Everything else as RU5 FF++-only
(three items per base, same heads, same selection ffpp_f1). The forged decision therefore has to come from concentrated
local evidence; evidence spread over the whole face does not add up.
**Arms.** M2 `--ffpp-only --mil` (clipe5mf): beautified views on both classes. M0 `--ffpp-only --mil --beauty none` (clipe5mfp0):
no beautified views, to see whether the pooling alone removes the exposure dependence. Seed 20260929; second seed if M2 passes.
**Bars (Celeb-DF-B read once per arm).** B1: M2 vs clipe5f (same data, pooled decision) AUC-b higher with paired interval
excluding 0, beauty-only MISS rise lower with interval excluding 0; untreated Celeb-DF-B and CDFv2 AUC within 0.01. B2: on
the full-frame DFD filters the same direction. B3 (mechanism): on FF++ val the map mean of genuine faces under the held-out
filters stays below −2 logits (it is +1.9 now). M0 vs M2 is reported whatever it shows; if M0 ≈ M2 the pooling, not the
exposure, carries the robustness, which would change the paper's method statement.
**Prior work to cite if it works.** Multiple-instance pooling for forgery (Li et al. "Sharp MIL" 2021; Zhao et al. "multi-attentional"
2021) and footprint supervision (Face X-ray, our part edits); the new element is the combination with a zero target on
benign edits and the decision taken from the map. Both to be verified on primary pages before writing.

## Addendum 29 (2026-10-08 17:40, before running) — edit-sensitivity as evidence (IDEATION_20261008 B2), falsification first
**Idea.** The detector's response to a known probe edit is class-dependent (genuine faces move far more than forgeries,
Addendum 17 A). Use the responses Delta_k to K fixed probe edits (operator settings: corner vignette, monochrome, warm tone,
cool tint field, smoothing, contrast) together with the clean logit as the decision features, fitted on clean FF++ train
frames only. No retraining of the backbone.
**Pass (FF++ val, 600 frames; `sensitivity_probe.py`).** (i) the K-D rule keeps clean AUC >= 0.98 and -mean(Delta) alone
has AUC >= 0.85; (ii) under the eleven held-out filters FA at the clean 5 %-FPR point < 10 % (pooled logit 21.5 %) with MISS
not above the pooled logit's; (iii) the Delta asymmetry holds inside every clean-logit decile (not a ceiling effect).
Fail on any of the three; the result is recorded either way. Closest prior: ODIN (input-perturbation response for
out-of-distribution detection); to be cited if the idea survives.

## Addendum 30 (2026-10-11 15:30, before training) — the exposure rule applied to the released Effort checkpoint (plug-in on published weights)
**Why.** The paper's robust finding is that a detector's beautification error is set by training exposure (Addendum 25,
three seeds, two schemes). If that is right, a short fine-tuning of a *published* detector with class-balanced beautified
views must shrink its miss rise under beautification without touching its untreated accuracy. That is the standard form
of a method contribution (a plug-in table) and the released checkpoints are the fairest baselines there are.
**Arms (`--tune effort --init effort --binary --ffpp-only`, `effort_init.py` loads the released weights; forged logit =
head[1] − head[0], verified against the official scorer).** A2 both-class exposure (clipe5fbEi), A0 no beautified views
(clipe5fbp0Ei, the control that separates "fine-tuned on our FF++ pipeline" from "exposure"). 2 epochs, lr 2e-5, otherwise
the FF++-only triplet recipe; selection ffpp_auc. Seed 20260929, second seed if A2 passes.
**Bars (Celeb-DF-B read once per arm; the released Effort scored on the same frames is the reference: AUC untreated 0.909,
AUC-b 0.807, beauty-only rise +11.0).** A2: AUC-b above 0.807 and rise below +11.0, both paired intervals excluding 0;
untreated Celeb-DF-B AUC and untreated CDFv2 / DFD AUC (own crop) within 0.01 of the released checkpoint. A0 reported
alongside; the exposure effect is A2 − A0 with intervals. If A2 passes and A0 does not, the rule is a working plug-in; if
both pass equally, fine-tuning on our pipeline, not exposure, is the cause; if A2 hurts untreated AUC by more than 0.01 the
plug-in is reported as a trade-off. SBI and Forensics Adapter follow the same protocol if Effort passes.

## Addendum 31 (2026-10-12, written before training): is it the smoothing in the views?

Background (post hoc, FINDINGS 2026-10-12): FF++-only arms without beautified views (P0) accuse 43-56% of the Smoothing-90
renders of the unseen service at the 5%-FPR threshold of its originals; P1 gives 4-7%, P2 7-12%. The adversarial review
found that the scripted smoothing is the same kind of edit as the service's at the same strength.

Arms: P2n = P2 with `--no-smooth`, P1n = P1 with `--no-smooth` (tags clipe5fbn, clipe5fbp1n). `--no-smooth` removes skin
smoothing from every beautified view: the smoothing draw of `random_op_v2` is redrawn among eye / jaw / whitening, the
scripted beautify keeps only whitening and the colour look, and the pre-rendered FF++ filter frames whose file name
contains "smooth" are dropped (4,646 of 41,512). Colour grades, pilgram filters and the label-symmetric degradation
(blur, down-up scaling, JPEG) stay. Everything else as P1 / P2: same bases, steps, 8 epochs, checkpoint by FF++ validation
AUC. Seeds: P2n 20260929 and 20260930, P1n 20260929.

Measure: share of Smoothing-90 renders above the 95th percentile of the originals (as `exposure_ali.py`), paired with P0
and with P2 / P1 of the same seed, bootstrap over identities; and the same per epoch for all eight epochs of P2n seed 1.

Readings fixed in advance:
- P2n >= 30% on both seeds: the effect is exposure to smoothing itself. The paper says so; the claim is that the
  default FF++ training lacks the edit, and that blur / JPEG do not substitute for it.
- P2n <= 15% on both seeds: exposure to other beautifications is enough; the claim extends to an edit the views never
  contained, and that is stated with these numbers.
- In between or seeds disagree: reported as partial, no general claim.
Costs reported alongside in every case: untreated Celeb-DF-v2 and DFD AUC, miss and false-alarm rise on the two filter
sources and Celeb-DF-B, against P0 / P2 of the same seed.

## Addendum 32 (2026-10-13, written before training): smoothing as the only beautified view

Background: Addendum 31 showed that smoothing in the views is necessary for removing the false accusation of commercially
smoothed faces, and the no-smoothing arms still pay the untreated Celeb-DF-v2 cost of P1 / P2. Question: is smoothing
sufficient, and does it avoid that cost?

Arms: P2o = both classes, P1o = genuine only, with `--only-smooth` (tags clipe5fbg0o, clipe5fbg0p1o): every beautified
view is skin smoothing (the scripted face-local bilateral operation at its usual strength range, the plain bilateral
entry of the scripted beautify, and the pre-rendered FF++ smoothing frames); no colour grade, no pilgram filter, no
whitening, eye or jaw edit. Everything else as P1 / P2. Seeds 20260929 and 20260930 for P2o, 20260929 for P1o.
Checkpoint by FF++ validation AUC.

Bars, against P0 of the same seed, all must hold on both P2o seeds for the positive reading:
(a) Smoothing-90 on the unseen service <= 15% at the 5%-FPR threshold of its originals;
(b) untreated Celeb-DF-v2 video AUC not lower by more than 0.010, and untreated DFD video AUC not lower by more than 0.010;
(c) Celeb-DF-B: AUC under beautification not lower than P0 by more than 0.010.
Reported regardless: miss and false-alarm rises on the two filter sources (no gain is expected there, since the views
contain no colour look), and the same numbers for P1o.
Readings: (a)+(b)+(c) -> targeted exposure removes the smoothing accusation without the cost of general beautified views;
(a) only -> sufficient but not free, the cost is stated; (a) fails -> smoothing alone is not sufficient and the other views
matter in combination.

## Addendum 33 (2026-10-13, written before training): replication of the smoothing-only, genuine-only arm

Observation (one seed, 20260929, post hoc): P1o, smoothing as the only beautified view and given to genuine faces only,
has Smoothing-90 on the unseen service 0.7%; Celeb-DF-B AUC under beautification 0.887 and beauty-only miss rise +8.6
(P0 0.860, +17.0; P2 0.879, +9.8; P1 0.844, +21.5); DF40 reenactment 0.871 / 0.673 (P0 0.906 / 0.692); untreated
Celeb-DF-v2 video AUC 0.922 (P0 0.938). It looks like the best operating point of all arms, on one seed, found after
looking at many arms. It is treated as a hypothesis.

Replication: P1o with seeds 20260930 and 20261001 (P0, P1, P2 exist for both). Same recipe, checkpoint by FF++ validation
AUC. No other change.

Bars on the two new seeds, each against P0 of the same seed; the claim needs both seeds:
(a) Smoothing-90 on the unseen service <= 15%;
(b) Celeb-DF-B beauty-only miss rise lower than P0's, paired video-cluster interval below zero, and AUC under
    beautification not lower than P0's by more than 0.005;
(c) DF40 reenactment video AUC not lower than P0's by more than 0.040 in either domain;
(d) untreated Celeb-DF-v2 and DFD video AUC not lower than P0's by more than 0.020.
Also reported, no bar: miss and false-alarm rises on the two colour-filter sources (the views contain no colour look, so
no gain is expected; a loss against P0 is reported as a cost), and the same four quantities against P2.
Readings: all four on both seeds -> P1o is reported as the recommended recipe with these numbers and costs; (a) and (b)
only -> a fix for smoothing with a stated cost on reenactment / untreated detection; anything else -> seed 20260929 was
luck and is reported as such.

### Addendum 33, check (e), added 2026-10-13 before any smoothed-forgery score was computed
The threshold-free view (`../alipair_zeroshot_20260929/smoothing90_thresholdfree.json`) shows that P1o scores a smoothed
genuine render below its own original in 97% of pairs (AUROC 0.095): it may have learned "smoothed = genuine". If so, a
forger can smooth a deepfake to pass. Test (`smooth_evasion.py`): Celeb-DF-v2 test frames, bilateral filter on the whole
crop at the three scripted strengths, threshold at 5% FPR on untreated genuine frames.
Bar (e): at every strength, the miss rise of P1o on smoothed forgeries is not higher than that of P0 of the same seed by
more than 5 points (paired interval over videos must not lie wholly above +5). Applies to all three P1o seeds.
If (e) fails, P1o is not recommended whatever (a)-(d) say, and the paper reports it as the shortcut it is: removing the
false accusation by teaching the detector that smoothing means genuine opens an evasion route. The same table is reported
for P0, P1, P2, P2 without smoothing, P2 smoothing only, the full-data models, and is the reason P2-type exposure (both
classes) exists.

## Addendum 34 (2026-10-13, written before training): class-symmetric smoothing view

Flaw (FINDINGS 2026-10-13): the smoothing form differs between classes in every both-class arm (face-local on genuine,
whole-crop bilateral on forged frames without landmarks), and the models learned the form as a class cue.

Arm P2oy (`--only-smooth --sym-smooth`, tag clipe5fbg0oy): smoothing is the only beautified view; a smoothed view is
drawn the same way wherever landmarks exist: with probability 0.5 the face-local scripted smoothing, otherwise the
whole-crop bilateral at one of three strengths; forged frames without landmarks receive the whole-crop form. No
pre-rendered smoothing frames. Both forms therefore occur in both classes; their proportions are not identical (genuine
0.5 / 0.5; forged with landmarks 0.33 / 0.67; forged without landmarks 0 / 1), which is stated. Seeds 20260929, 20260930.
Checkpoint by FF++ validation AUC. Everything else as P2.

Evaluation, `smooth_evasion.py` extended with two smoothing forms no arm has seen (a 5x5 median filter; a 50% blend with
a Gaussian blur of sigma 2), and the unseen service. All against P0 of the same seed, both seeds required:
(a) Smoothing-90 on the unseen service: <= 15% at the 5%-FPR threshold, AND renders scored above their own original in
    no more than 75% and no less than 25% of pairs (neither accused nor used as a genuine cue);
(b) smoothed genuine Celeb-DF-v2 frames: false alarms <= 15% at every strength of the whole-crop bilateral and for the
    two unseen forms;
(c) smoothed forged Celeb-DF-v2 frames: miss rise not higher than P0's by more than 5 points at every strength and form;
(d) costs reported, no bar: untreated Celeb-DF-v2 / DFD video AUC, Celeb-DF-B, DF40 reenactment and face swap.
Readings: (a)+(b)+(c) on both seeds -> a symmetric smoothing view removes the false accusation without opening the
evasion route, with costs (d); (a) without (b) or (c) -> still a shortcut of some form, reported as such; (a) fails ->
the earlier low numbers depended on the asymmetry.

## Addendum 35 (2026-10-13, written before training): the symmetric smoothing view as a recipe for other detectors

If Addendum 34 passes (a)+(b)+(c) on both seeds, the claim must not rest on one training scheme. Arms, FF++ only, binary,
`--only-smooth --sym-smooth`:
- E1: Effort scheme from CLIP (`--tune effort`), seed 20260929, tag clipe5fbg0oyE; reference clipe5fbp0E_s20260929.
- E2: released Effort checkpoint fine-tuned 2 epochs, lr 2e-5 (`--tune effort --init effort --epochs 2 --lr 2e-5`),
  seed 20260929, tag clipe5fbg0oyEi; reference clipe5fbp0Ei_s20260929 (same fine-tune without beautified views) and the
  released Effort scorer itself.
Same bars (a)-(c) as Addendum 34, each against its own reference; costs (d) reported. Readings: both pass -> the recipe is
reported as scheme-independent; one passes -> reported per scheme; neither -> the LoRA result stands alone and is said so.
Queued behind Addendum 34 on the same GPU; evaluated by the same chain.

## Addendum 36 (2026-10-13, written before training): the main model with a class-symmetric smoothing view

The main model (three-way, full data, clipe5_s20260929) carries the class-asymmetric smoothing view (FINDINGS 2026-10-13):
whole-crop-smoothed genuine frames are called forged 35 / 80 / 90%. Arm: same recipe as clipe5 with `--sym-smooth`
(tag clipe5y, seed 20260929): the scripted smoothing drawn for a genuine view is, with probability 0.5, the whole-crop
bilateral filter instead of the face-local operation; the pre-rendered FF++ smoothing frames are dropped; vendor
renders, part edits, colour grades and everything else unchanged. Checkpoint by the main model's rule (C2 on validation).
Evaluation: the full main-model chain (run_add6_eval: FF++ validation, vendor validation, explanation IoU/flip, Celeb-DF-B,
filter sources, DFD, commercial retouching, DF40, smooth_evasion).
Replacement rule, all against clipe5_s20260929: it becomes the paper's main model if (i) whole-crop-smoothed genuine
Celeb-DF-v2 false alarms <= 15% at every strength, (ii) commercial Smoothing-90 <= 15% with renders above own original in
[25, 75]%, (iii) untreated Celeb-DF-v2 and DFD video AUC not lower by more than 0.010, (iv) explanation flip rate on the
three part-forgery mechanisms not lower by more than 1.0 point, (v) Celeb-DF-B AUC under beautification not lower by more
than 0.010. Otherwise the current main model stays and the asymmetry is stated as a limitation with these numbers.
Queued behind Addendum 35.

## Addendum 37 (2026-10-14, written before any fused score was computed): score fusion of a texture-based and a boundary-based detector

Observation: CADDM (boundary / identity cue) scores a commercially smoothed render above its own original in 60.9% of
pairs, the texture-reliant detectors in 89-99%; GenD and DFD-HR are the strongest on DF40 reenactment. Their errors may
not overlap. No training; released weights only.

Normalisation, fixed: each detector's score is replaced by its genuine-quantile in the same source, q = share of that
source's untreated genuine frames (for the retouching service: its untouched originals) with a lower score. This uses the
same reference population as the one-rule threshold and nothing else.
Fusions, fixed: F_mean = (q_a + q_b) / 2; F_min = min(q_a, q_b); F_prod = q_a * q_b.
Pairs, fixed: (GenD, CADDM), (DFD-HR, CADDM), (Effort, CADDM), and (ours P0 seed 20260929, CADDM). No other pair, weight
or rule is tried; LAA-Net is not used because its crop differs.
Measured with the same rules as everywhere else, per fusion and pair, against each member alone:
(1) retouching service: Smoothing-90 above the 5%-FPR threshold; renders above own original;
(2) untreated Celeb-DF-v2 and DFD video AUC; (3) Celeb-DF-B AUC under beautification and beauty-only miss rise;
(4) DF40 face swap and reenactment video AUC (after CADDM is scored there).
Reading: a fusion is reported as useful only if, for the same pair and rule, (1) Smoothing-90 <= half of the texture
member's rate AND (4) reenactment video AUC within 0.03 of the texture member in both domains AND (2) untreated video AUC
not below the better member by more than 0.01. One of three rules meeting this for at least two of the three published
pairs counts; anything else is reported as: fusion moves the operating point along the same trade-off.
Expected obstacle, stated in advance: if CADDM does not fire on reenactment either, a smoothed genuine face and a
reenacted face look the same to the pair (texture fires, boundary silent) and no fusion rule can separate them.

## Addendum 38 (2026-10-16, written before any detector was scored on the new images): smoothed forgeries and smoothed genuine faces for all 17 published detectors (review v4, B3 / E1)

Question: does the pattern seen in our arms (no exposure: accuse smoothed genuine faces; genuine-only exposure: pass smoothed
forgeries) appear in published detectors, and does face-local smoothing behave like whole-crop smoothing?
Frames: the `smooth_evasion.py` list (Celeb-DF-v2 test, our crop, every 4th of the 32 frames per video; 4,016 frames).
Forms: the five of `smooth_evasion.py` (bilateral (9,50,50), (15,80,80), (21,100,100) on the whole crop; 5x5 median; 50%
blend with a Gaussian blur of sigma 2) plus two face-local forms: `ops.op_smooth` with frac 0.06 and frac 0.12, mix 1.0
(bilateral inside the feathered convex hull of the 478 MediaPipe FaceLandmarker points, detected on the crop itself).
Frames where FaceLandmarker finds no face are left out of the face-local statistics (untreated and treated alike, same
subset); their number is reported. Treated crops are written once as lossless PNG and every model reads the same files;
untreated crops are the original JPEGs.
Detectors: the 17 published detectors through the adapters used for every other table (`cdf_filtered_eval.py` loaders),
released weights, no change. Ours, rescored on the same files for the two new forms: P0 (three seeds), P2 (two), P1
smoothing only (seed 1), P2 symmetric (two), main model clipe5 s1, symmetric-view variant clipe5y, binary control clipe5b.
Sanity check fixed in advance: for our models the five old forms must reproduce `smooth_evasion2_*.npz` (frame AUC within
0.003); otherwise the file path is wrong and nothing is reported.
Rule: threshold = 95th percentile of P(fake) on untreated genuine frames. Per detector and form: untreated miss, miss rise on
smoothed forgeries, false alarms on smoothed genuine frames, both with 95% video-cluster bootstrap intervals (1000 draws,
rng 0, the same draws for every detector), frame AUC with both classes smoothed, share of forged frames whose score falls
and of genuine frames whose score rises.
Classification per detector and form, fixed: "accuses" if the lower bound of the false-alarm interval is above 5.0%;
"lets through" if the lower bound of the miss-rise interval is above 0; otherwise "neither". Descriptive, no bar.
Expectation stated in advance (P0 behaves like this): FF++-trained published detectors accuse whole-crop-smoothed genuine
frames at mid / strong strength and do not let smoothed forgeries through. The face-local forms are the new information.
NPR is reported but flagged (its scores saturate on our crops).

## Addendum 39 (2026-10-16, written before scoring): dose response of the four released CLIP detectors (review v4, B1)

Detectors: Effort, Forensics Adapter, GenD, DFD-HR (released FF++ weights, the same adapters). Frames: the genuine frames of
the Addendum 38 list. Edits, each at increasing strength on the crop:
(a) radial luminance vignette, the vignette term of `train_ru5.random_grade`: x * (1 - s * clip(r - 0.4, 0)^1.5), r = distance
    from the crop centre normalised to 1 at the edge midpoints, s in {0.1, 0.2, 0.4, 0.6, 0.8};
(b) face-local skin smoothing, `ops.op_smooth` frac in {0.03, 0.06, 0.09, 0.12}, mix 1.0 (frames with landmarks); the three
    whole-crop bilateral strengths of Addendum 38 are reported alongside.
Per detector and level: mean P(fake); share above the 95th percentile of the untreated genuine frames; median shift of the
detector's own forged-minus-genuine logit (z1 - z0 at its final 2-way linear layer, read by a forward hook) with a 95%
video-cluster interval; share of frames whose logit rises; the shift in units of the untreated forged-minus-genuine gap of
mean logits on the same list; and the share of the feature shift that lies along the head direction, mean |cos(df, w1 - w0)|,
where df is the change of the input of that layer (pooled feature for Effort, GenD (after its L2 normalisation), DFD-HR; the
192-d penultimate activation of the MLP head for Forensics Adapter, which has no linear head on a pooled feature).
Reading, fixed: a detector shows a dose response to an edit if the mean logit shift does not decrease from one level to the
next by more than 0.1 and the median shift at the top level has an interval above 0. The mechanism section may extend
"genuine pushed along the forged direction" to skin smoothing for published detectors only if smoothing (b) shows a dose
response in at least three of the four; otherwise the mechanism claim stays limited to colour filters with a vignette.

## Addendum 40 (2026-10-16, written before training): forged-only exposure (P3), the missing cell of the exposure design (review v4, B5)

Arm P3: `train_ru5.py --binary --ffpp-only --beauty fake` (new option, tag clipe5fbp3_s20260929). The genuine item receives no
beautified view (a second untreated copy, exactly as P0); forged items receive the beautified views of P2 with the same
probability and operators (50% of self-blends and of observed FF++ forgeries; random grade, landmark operation or scripted
beautify). Everything else as P0 / P1 / P2. Seed 20260929, Ubuntu, checkpoint by FF++ validation AUC (SEL=ffpp_auc).
Evaluation: the chain of the other exposure arms (run_add6_eval with SEL=ffpp_auc; Celeb-DF-B; Celeb-DF-v2 and DFD filter
sources, crop and full frame; DFD v3; DF40; `smooth_evasion.py` and the Addendum 38 forms; the unseen service: Smoothing-90
above the 5%-FPR threshold of the originals and renders above their own original).
Prediction from "exposure sets the sign": forged-only views teach "beautified = forged".
Readings, against P0 and P2 of seed 20260929:
(i) P3's Smoothing-90 rate is not below P0's by more than 5 points (paired interval not wholly below -5) AND its false alarms
    on mid and strong whole-crop-smoothed genuine frames are not lower than P0's -> the sign rule is complete: genuine-only
    lowers accusation and opens evasion, forged-only keeps the accusation, both classes in between;
(ii) P3's Smoothing-90 rate <= 15% -> forged-side views alone remove the accusation; "exposure sets the sign" is wrong as
    stated and is withdrawn;
(iii) anything else -> partial, reported with the numbers.
One seed; whatever the reading, the paper states it is one seed. Costs reported: untreated Celeb-DF-v2 / DFD video AUC,
Celeb-DF-B, DF40 face swap and reenactment.

## Addendum 41 (2026-10-16, written before scoring): DF40 entire-face synthesis as a measured class-boundary probe (review v4, A2), descriptive

On disk: DF40 entire-face synthesis sd2.1, DiT, SiT, ddim, pixart (3,000 images each, the subsets kept by the earlier
production line, which trained on them; no RU / CLIP model and no published detector here saw them) and StyleGAN3 (DF40
release, 31,885). DF40 face editing (e4e, StyleCLIP, CollabDiff, StarGANv2) is listed in `DF40_all.json` but its images
were never downloaded; it is not scored in this round. The `stargan/` folder is not DF40 and is not used.
Sample: per method and domain (ff / cdf), up to 300 images, numpy default_rng(0) over sorted paths.
Models: main (clipe5_s20260929), symmetric-view variant (clipe5y_s20260929), binary control (clipe5b_s20260929), Effort,
Forensics Adapter, GenD, DFD-HR. Label under the definition: forged.
Measured: share above the 95th percentile of the same-domain DF40 real frames (`df40_eval_list.txt`, existing scores), frame
AUC against those frames; for the main model also its native decision (real / forged / beautified shares).
Descriptive, no bar. Confound stated in advance: the synthesised images are generator stills, the real frames H.264 video
frames, so "called forged" mixes format and synthesis.

## Addendum 42 (2026-10-16, written before training): second seeds of the symmetric-view variant and the binary control (review v4, B14)

Arms, Ubuntu, current `train_ru5.py` (md5 59747c4c..., identical on both machines), seed 20260930:
- clipe5y_s20260930: `train_ru5.py --sym-smooth --seed 20260930` (Addendum 36 recipe), checkpoint by C2 on validation (main-model rule).
- clipe5b_s20260930: `train_ru5.py --binary --seed 20260930` (Addendum 9 recipe), checkpoint by FF++ validation AUC (as seed 1).
Caveat stated in advance: clipe5b seed 1 was trained on 2026-10-06 with the code of that day; options added since
(Addenda 25-41) default to the old behaviour, so the recipe is the same, but this is checked only through the log header.
Evaluation: clipe5y by the Addendum 36 chain (run_add6_eval + smooth_evasion + filter sources + DFD v3 + Celeb-DF-B + DF40);
clipe5b by the Addendum 9 chain (run_add6_eval with SEL=ffpp_auc) plus the same extra sources. The main model's seed 2
(clipe5_s20260930) is scored on smooth_evasion if it has not been, so every comparison is within seed.
Reported, per seed, with paired differences (video-cluster bootstrap, 1000 draws, rng 0, same draws for both models):
(A) Addendum 36 criteria (i)-(v) for clipe5y_s20260930 against clipe5_s20260930, and whether the verdict of seed 1
    ((iv) fails, the main model stays) replicates;
(B) binary minus main (clipe5b - clipe5, same seed): untreated Celeb-DF-v2 and DFD frame AUC, Celeb-DF-B AUC under
    beautification, DF40 reenactment video AUC (ff / cdf); seed 1 found binary >= main on all of these (review D3).
Reading: a seed-1 finding is called replicated if the seed-2 paired interval has the same sign category (above 0, below 0,
or containing 0); otherwise it is reported as seed-dependent with both numbers. No bar is changed.

## Addendum 43 (2026-10-16, written before any model is scored on the new pairs): Instagram AR filters as a fourth beautification source for the measurement (review v4, E14 / B11)

Code and outputs: `../review_v4_exps_20261016/` (`build_blfw_pairs.py`, `ar_source.py`).
Sources, genuine faces only, paired render vs its own original:
(A) FairBeauty controlled pairs (`external_data/fairbeauty_pairs`, 2,927 pairs, built 2026-10-06 by `build_fairbeauty_pairs.py`:
    FairFace validation original vs the same face under one of 11 Instagram AR beauty filters (OpenFilter), both cut by the
    project extractor). Each original occurs once, so the bootstrap unit is the pair.
(B) B-LFW (OpenFilter, 12,000 renders, 8 filters, 112x112 ArcFace-aligned). The renders follow the order of LFW `pairs.txt`
    (lfw.bin order; first four renders checked by eye against Abel_Pacheco 1/4 and Akhmed_Zakayev 1/3). `pairs.txt` from the
    scikit-learn mirror (figshare 5976006, md5 9f1ba174...), saved in `external_data/lfw_pairs_txt/`. The original of render k
    is LFW image k of that order, warped onto the render's frame by a similarity transform fitted (RANSAC) between MediaPipe
    FaceLandmarker points of the original and of the render (render upsampled x2 for detection), output 112x112 lossless PNG.
    Registration check, fixed: normalised cross-correlation of Sobel gradient magnitude (grey, Gaussian sigma 1) between the
    warped original and its render must exceed the 99th percentile of the same statistic for the warped original against a
    render of a different identity (one random mismatch per render, rng 0); renders failing detection or the check are
    dropped and counted. The bootstrap unit is the LFW identity (person name), because photos and persons recur.
Capture-pipeline caveat, stated in advance: the renders went through the AR engine's capture and re-encoding (B-LFW also
through lfw.bin's alignment and JPEG), the originals did not. A detector that keys on that pipeline separates renders from
originals regardless of beautification, so every number here is "AR-filter pipeline output vs original": an upper bound on
the beauty-specific effect. RU7 (Addendum 13) showed a model can learn this pipeline from such pairs. These sources were
excluded from training for that reason; here they are test-only for detectors that never saw them, which is legitimate as
long as the caveat is stated. Sensitivity, fixed: FairBeauty with both sides re-encoded as JPEG q90 (same size) and scored
again; if a detector's accused share falls by more than half, it is flagged as pipeline-dominated on this source.
Models: the 17 published detectors (adapters of `cdf_filtered_eval.py`, released weights) and ours: main (clipe5_s20260929),
symmetric-view variant (clipe5y_s20260929), binary control (clipe5b_s20260929); the Addendum 42 seeds when they exist.
Score P(fake). One rule: threshold = 95th percentile of the originals of the same source (5% FPR on its untreated side).
Measured per source and model, 95% bootstrap CI (1000 draws, rng 0, threshold re-estimated in each draw, same draws for every
model): accused share (renders above the threshold); AUROC renders vs originals; share of pairs with render > own original;
per filter (descriptive); paired differences ours minus Effort, FA, GenD, DFD-HR on all three.
Classification per model and source: "accuses" if the lower bound of the accused share is above 5.0%; "ranks renders above
originals" if the lower bound of the paired share is above 50%. Reading for the paper: the accusation of beautified genuine
faces is said to replicate on AR filters if at least 12 of the 17 published detectors "accuse" on both sources; consistency
with the commercial source is summarised by the Spearman correlation over the 17 detectors between the FairBeauty accused
share and the commercial Smoothing-90 accused share (both at their own 5%-FPR rule), reported, no bar.

## Addendum 44 (2026-10-16, written before scoring FF++ validation): one deployable threshold per detector (review v4, C6)

Threshold per model = 95th percentile of P(fake) on the 530 genuine frames of FF++ c23 validation (`ffpp3_val.txt`, label 0,
project crops); no test source is used. The 17 published detectors and ours (main, symmetric variant, binary control, both
seeds where they exist) are scored on these frames with the same adapters. At this fixed threshold, next to each source's own
5%-FPR rule, report FA (genuine called fake) and MISS (forgeries not called fake) on: Celeb-DF-B (six folders), Celeb-DF-v2 and
DFD with held-out colour filters (crop and full frame), the commercial service (originals, Smoothing-90 and all renders),
DF40 (real; face swap; reenactment; per domain), FairBeauty and B-LFW (originals, renders), and untreated Celeb-DF-v2 / DFD.
Intervals: cluster bootstrap within each source with the threshold fixed (1000 draws, rng 0); the threshold's own uncertainty
is reported as its 95% interval over a video bootstrap of FF++ validation. Descriptive, no bar. Also reported: Spearman
correlation over the 17 published detectors between oracle and deployable accused shares on commercial Smoothing-90 and on
FairBeauty, i.e. whether the ranking of detectors survives a deployable rule.

## Addendum 45 (2026-10-16, written before any re-run): identity-cluster bootstrap (review v4, C10)

Re-run, unchanged except for the resampling unit, the paired analyses: Celeb-DF-B (`fair_cdfb.py` statistics), Celeb-DF-v2 and
DFD with held-out colour filters (crop and full frame, `cdf_filtered_eval.py` statistics), DF40 (`df40_eval.py` paired
differences). Identity: Celeb-DF / Celeb-DF-B `idX` of the file name; for a forged video `idX_idY_k` the cluster is X (the
scene person whose video was altered), and X and Y are additionally merged into one cluster when the check of connected
components leaves at least 10 clusters (reported both ways); Celeb-DF YouTube-real videos are their own cluster each. DFD:
actor id (first id for forged videos, same merging rule). FF++ / DF40-ff: the first three-digit id. DF40-cdf: video ids are
renumbered by DF40 and carry no identity, so it stays video-clustered (stated). Same 1000 draws, rng 0, identity draws shared
by all detectors. Report: every interval of the existing tables under video and identity resampling, and the list of
intervals that change category (contains 0 vs excludes 0; for accused shares, contains 5.0 vs excludes it).

### Addendum 43, amendment (2026-10-16 17:30, before any model was scored on B-LFW)
Scoring 11,891 B-LFW pairs (23,782 images) for 20 models does not fit the day on the shared machine. B-LFW is scored on a
fixed random sample of 3,000 of the 11,891 registered pairs (numpy default_rng(0), choice without replacement, then sorted;
`external_data/blfw_pairs/pairs_sample3000.tsv`), bootstrap unit still the LFW identity. B-LFW is scored before the FairBeauty
JPEG-q90 sensitivity run. Registration result (before any score): 12,000 renders, 24 without a detectable face, 85 failing the
NCC check (match median 0.90 against mismatch median 0.09, threshold 0.33), 11,891 kept, 7,632 distinct originals, 4,254 identities.

## Addendum 46 (2026-10-17 20:30, written before any full training run): smoothing-invariant consistency (SIC), the method candidate for the binary main detector

Context (decision taken by the first author's assistant, 2026-10-17): the paper's main detector becomes the binary
(forged-only head) full-data model; the three-way output is reported as an attribute head. Addendum 38 found that every
published detector (17/17) and every arm we trained either accuses skin-smoothed genuine faces (face-local smoothing: all
17 published, 13.9-100% false alarms; binary control 51.6 / 84.5% at frac 0.06 / 0.12) or lets smoothed forgeries through
(genuine-only views). The class-symmetric view (Addenda 34, 36) removed the whole-crop accusation but not the face-local one,
and cost 8-34 points of miss rise. SIC asks the detector directly for the invariance: the forged logit must not move when
the skin is smoothed, whatever the class.

Arm SIC, tag clipe5bz (`train_ru5.py --binary --smooth-consistency 1.0 --seed S`; md5 of `train_ru5.py` e8f02e56..., diff
against the previous version in `train_ru5_add46.diff`, previous file kept as `train_ru5_pre_add46.py.bak`; ops.py unchanged,
md5 4a208e7b...). Everything as the binary control clipe5b (full data, forged head, 8 epochs, checkpoint by FF++ validation
AUC, SEL=ffpp_auc) except three ingredients:
1. class-symmetric smoothing view (the `--sym-smooth` logic of Addendum 36, implied by the option): the scripted smoothing
   drawn for a beautified view is, with probability 0.5, the whole-crop bilateral filter; pre-rendered FF++ smoothing frames
   dropped;
2. evidence head supervised (mask loss, weight 1.0, targets as in clipe5); the beautified, presence and quantity heads stay
   unsupervised as in clipe5b;
3. paired consistency: for every item of every triplet (genuine, beautified genuine, forged; self-blends, observed FF++
   forgeries, part edits, vendor renders alike) a smoothed copy x_s of the final training image (after all augmentation,
   pixel-aligned, same flip) is built with probability 1.0 by the same operator for both classes: `ops.op_smooth`
   (face-local bilateral in the feathered hull of the 478 landmarks) with frac ~ U[0.03, 0.14] and mix ~ U[0.3, 1.0] when the
   item shares the base frame's landmarks (they are carried through the shared crop and the resize), otherwise the whole-crop
   bilateral at one of (9,50,50) / (15,80,80) / (21,100,100). L = BCE(z_f(x), forged) + L_mask([x; x_s], [footprint; same
   footprint]) + lambda * mean over items of (z_f(x) - z_f(x_s))^2, lambda = 1.0, gradient through both sides, x_s carries no
   label of its own. lambda is fixed here and is not tuned on any test source; no other lambda is trained in this addendum.

Measured before this addendum was written (training data path only, no checkpoint kept, no test source read):
`smoke_add46_data.py` on 150 training items: the main item stream is bit-identical with and without the option (150/150);
x_s differs from x for every item (mean |dx| 0.8 / 2.4 / 2.4 grey levels for genuine / beautified / forged items); the
montage `smoke_add46_montage.png` shows the face-local difference confined to the face after the crop and resize; x_s form
shares: genuine items 100% face-local; beautified genuine 43% face-local, 57% whole-crop; forged 40% face-local, 60% whole-crop
(whole-crop where no landmarks are carried: vendor renders, observed FF++ frames, part edits). The shares differ across item
roles; the consistency term has no class target, so the form cannot become a class cue through it, but the paper states the
shares. A 20-step local smoke run (warm-up, LR <= 1e-5) showed all terms finite and 23.9 GiB peak memory; the trend of L_cons
is checked on the first 300 steps of the Ubuntu smoke run and reported with the results.

Confounds stated in advance: (a) SIC differs from clipe5b in three ingredients, so SIC vs clipe5b does not isolate the
consistency term; if the result is positive, attribution needs clipe5bz with lambda = 0 (same code path, view and evidence
supervision only), named here as the required follow-up control and not run before the readout. (b) The training operator
contains the test operators of bars (1) and (2, whole-crop part): bilateral 9 / 15 / 21 and face-local frac 0.06 / 0.12 with
mix 1.0 lie inside the training ranges. Those bars therefore test the invariance on unseen images and identities, not on
unseen smoothing forms. Unseen forms are median 5x5, the 50% Gaussian blend (smooth_evasion.py; reported, no bar) and the
commercial Smoothing-90 renders (bar 2). The paper must say this next to any claim.

Seeds 20260929 and 20260930, sequential on gsplat-ubuntu (`run_add46_queue.sh`: 300-step smoke, then seed 1, then seed 2).
Evaluation by `run_add46_chain.sh` (local): run_add6_eval with SEL=ffpp_auc (selection, leak probe, eval_ru including the
commercial service and untreated Celeb-DF-v2 / DFD scores, Celeb-DF-B v3 + fair_cdfb, vendor validation, compare_sota,
part-forgery explanation), smooth_evasion.py (whole-crop and unseen forms), smooth_probe38.py (the Addendum 38 face-local
forms on the same PNG files), the four held-out colour-filter sources (crop and full frame), DFD v3, DF40, exposure_ali-style
commercial statistics, and `readout46.py`. The binary control clipe5b_s20260930 is also scored on the Addendum 38 forms (it
had not been), so every comparison is within seed.

Bars, both seeds, each against the named reference of the same seed; point estimates decide, 95% intervals are reported
(video-cluster bootstrap, 1000 draws, rng 0, same draws for both models; commercial: identity bootstrap as exposure_ali.py):
(1) face-local smoothing, Addendum 38 forms fl06 and fl12: false alarms on smoothed genuine Celeb-DF-v2 frames <= 15% at the
    5%-FPR threshold of untreated genuine frames (absolute; binary control seed 1: 51.6 / 84.5%).
(2) whole-crop bilateral 15 and 21: false alarms <= 15% (absolute), and commercial Smoothing-90 accused <= 15% at the 5%-FPR
    threshold of the service's originals.
(3) smoothed-forgery miss rise not more than 5 points above P0's (clipe5fbp0 of the same seed) at each form, as in Addendum
    34 (c); descriptive: frame AUC with both classes smoothed.
(4) untreated Celeb-DF-v2 and DFD video AUC not lower than clipe5b (same seed) by more than 0.010 (clipe5b: 0.956 / 0.987
    seed 1, 0.963 / 0.978 seed 2).
(5) Celeb-DF-B AUC under beautification not lower than the current main model clipe5 of the same seed (0.866 seed 1, 0.883
    seed 2; fair_cdfb.json).
(6) DF40 reenactment video AUC (mean over reenactment methods) not lower than clipe5b by more than 0.030 in either domain
    (clipe5b ff / cdf: 0.842 / 0.647 seed 1, 0.856 / 0.698 seed 2).

Feasibility of (3), computed before training from existing files: P0 calls every face-local-smoothed frame forged (false
alarms 95.8 / 100%), so its smoothed-forgery miss is 0 and its miss rise equals minus its untreated miss: fl06 / fl12 -42.1 /
-42.2 (seed 1), -37.7 / -37.7 (seed 2); bil21 -16.0 / -11.8. Bar (3) as written then requires SIC's smoothed-forgery miss to
be at most its untreated miss minus 37.1 (seed 1) / 32.7 (seed 2) points, which for a detector at the binary control's
untreated miss (36.5 / 35.4) means missing no smoothed forgery at all, at a threshold where bar (1) lets at least 85% of
smoothed genuine frames pass. A reference that accuses every smoothed face cannot be beaten on misses by one that does not;
this is the defect already met in Addendum 34 (c). Bar (3) as written is evaluated and reported at all seven forms. The
reading below uses (3'), fixed here before any SIC number exists: SIC miss rise <= max(P0 miss rise, 0) + 5 at each of the
seven forms (bil9, bil15, bil21, median5, gblend, fl06, fl12), i.e. against P0 where P0 itself lets smoothed forgeries
through, and against "no rise" where P0's negative rise comes from accusing everything smoothed. The tolerance stays 5 points.

Reading, fixed: (1)+(2)+(3')+(4)+(5)+(6) on both seeds -> the method claim "the first detector that is not fooled by skin
smoothing at any tested strength while matching the strongest untreated detector" may be made with the stated costs, with
confound (b) stated next to it, and with attribution to the consistency term only after the lambda = 0 control;
(1)+(2)+(4) on both seeds only -> partial, stated with the failing bars and numbers; anything else -> negative result,
stated. The outcome under bar (3) as written is reported in the same table.
Comparison row, fixed: the 17 published detectors' face-local numbers of SMOOTH38.md / smooth38.json (false alarms, miss
rise, AUC with both classes smoothed, per form), unchanged and not rescored.

### Addendum 46, amendment 1 (2026-10-17 20:40, written before any epoch of any Addendum 46 run exists): primary arm is the factorised model

Change of arm specification from the coordinator: the system must keep three classes and the four operation scores, so the
primary SIC arm is not binary.
- Primary arm, tag clipe5z (`train_ru5.py --smooth-consistency 1.0 --seed S`): the full-data factorised model exactly as
  clipe5 (forged logit + beautified logit with BCE, presence and quantity heads, evidence head; same data, 8 epochs), with
  the class-symmetric smoothing view (`--sym-smooth`, implied) and the paired consistency term of ingredient 3 applied to the
  forged logit only, lambda = 1.0. x_s gets no forged / beautified / presence / quantity target; its evidence target is the
  footprint of x. Checkpoint by the main model's rule (C2 on validation, select_epoch default), as clipe5 and clipe5y.
- Secondary arm, tag clipe5bz: the binary arm defined above, for the detection-only comparison; checkpoint by FF++ validation
  AUC.
- Code: `train_ru5.py` md5 242e4753... (supersedes e8f02e56... quoted above; the only change is the factorised loss branch
  and the option no longer requiring --binary; the data path is unchanged, so the smoke check above holds for both arms).
  The 20-step local smoke run of clipe5z: all terms finite, 23.9 GiB peak (`smoke_clipe5z_local.log`). In clipe5z's step
  log the second slot is L_cons; the presence loss is not printed.
- Queue on gsplat-ubuntu: 400-step smoke of clipe5z (L_cons trend across the end of warm-up), then clipe5z s20260929 ->
  clipe5bz s20260929 -> clipe5z s20260930 -> clipe5bz s20260930.
- Bars (1)-(6) and (3') unchanged, applied to the forged logit P(forged) = sigmoid(z_f) of each arm (which is what every
  scorer reads as P(fake): the softmax of the joint log-probabilities returns sigmoid(z_f) exactly). The reading is made per
  arm; clipe5z is the arm the method claim refers to, clipe5bz is reported next to it.
- Decision rule of clipe5z in the system, fixed: forged if P(forged) > t_f, t_f = 95th percentile of P(forged) on the 530
  genuine frames of FF++ c23 validation (the Addendum 44 deployable rule; training-side data only); otherwise beautified if
  sigmoid(z_b) > 0.5 (z_b the beautified logit; sigmoid(z_b) = P(filter) / (1 - P(fake)) of the joint), otherwise real.
  The four operation scores are the presence head's sigmoids, reported for beautified decisions.
- Additionally reported for clipe5z against clipe5 of the same seed, no bar: on the unseen commercial service, originals
  called real and renders called beautified under the rule above and under the native argmax, balanced accuracy, renders
  called forged; per-operation hit rates of the presence head (eval_ru `eq4` TP / same-image TN / exact-set accuracy) and
  the presence true-negative rate on originals; vendor validation (eval_vendor_val); explanation IoU / flip on the part
  forgeries (eval_cgd_explain).
- Queue note (2026-10-17 20:45, operational, no result read): the first launch of `run_add46_queue.sh` deadlocked on its own
  pgrep pattern before running anything; its script was truncated in place so it can never start a run, and the same queue
  was relaunched as `run_add46_queue2.sh` (identical runs and order, wait pattern `python -u train_ru[5]`).

### Addendum 46, Amendment 2 (2026-10-17 21:05 TST, before any epoch of clipe5z has been evaluated)
Bar (3) as first written compares the miss rise with P0's; at the face-local forms P0's miss rise is negative because P0
accuses every smoothed face, so (3) is unsatisfiable there together with (1). The operative bar is (3'):
miss rise at each form <= max(P0's rise, 0) + 5 points. (3) is still computed and shown.
Control for crediting the consistency term: clipe5bz with lambda = 0 (symmetric view + evidence head, binary, no L_cons),
seed 20260929, tag clipe5bzl0, queued fifth after the four runs; the SIC claim about L_cons needs clipe5bz to beat this
control on bars (1)-(2) at the trained forms, else the gain is attributed to the view + head.
Statement required next to any SIC claim: bilateral 9/15/21 and face-local 0.06/0.12 lie inside the training operator
ranges; median 5x5, Gaussian blend and the commercial renders are the unseen forms.

### Addendum 46, Amendment 3 (2026-10-18 06:45 TST, written after the clipe5z s1 readout and before any run with lambda < 1)
Readout of clipe5z_s20260929 (READOUT46.md): bars (1) and (2) pass (face-local FA 4.3-4.5 %, bilateral 5.6-7.2 %, commercial
Smoothing-90 7.6 %), bars (3'), (4), (5), (6) fail (miss rise +5.9 / +10.2 at fl06 / fl12; CDFv2 video 0.876 vs binary 0.956 and
vs the full model 0.947; Celeb-DF-B 0.845 vs 0.866; DF40 reenactment -0.18 / -0.04). lambda = 1 removes the accusation and
costs detection; the symmetric view alone (clipe5y, lambda = 0 equivalent for the factorised arm) keeps detection (0.954) and
accuses 38 / 80 % at fl06 / fl12. The trade-off between these two points is unmeasured.
New arms (binary, --sym-smooth implied, seed 20260929, everything else as clipe5bz): clipe5bzl03 (--smooth-consistency 0.3
--tag-suffix l03) and clipe5bzl01 (--smooth-consistency 0.1 --tag-suffix l01). Bars (1)-(6) and (3') unchanged.
Reporting rule, fixed now: all four lambda values (0 = clipe5bzl0 control, 0.1, 0.3, 1) are reported in one table. The SIC
claim is made at the smallest lambda that passes (1) and (2) at the trained forms; bars (3')-(6) are judged at that lambda;
a second seed of that lambda is trained before any claim. If no lambda passes (1)-(2) while (4)-(6) hold, SIC is reported
as a trade-off curve, not as a fix. The factorised arm (clipe5z) is not re-run at other lambdas unless the binary arm
passes.
Code change: train_ru5.py gains --tag-suffix (string appended to the variant letters; nothing else touched), md5 now
890deeb641707c14edfd004279643ebc (was 242e47530e987f8b69d7a467578fc49a; backup train_ru5.py.bak_am3). The lambda = 0 control
of Amendment 2 is trained with --tag-suffix l0 so that its files carry the tag clipe5bzl0 that readout46.py expects (without
the suffix the variant logic would have named it clipe5by).
Scheduling: clipe5z s2 trains on the local GPU (started 04:23 TST, script md5 242e4753..., identical training path); the
Ubuntu queue after clipe5bz s1 becomes l0 -> l03 -> l01 -> clipe5bz s2 (run_add46_queue3.sh). The three earlier queue loops
on Ubuntu (run_add46_queue.sh, run_add46_queue2.sh, run_add46_ctrl_queue.sh) must be stopped before queue3 starts or they
would retrain clipe5z s2 and the control under the old names.

### Addendum 46, Amendment 4 (2026-10-18 07:40 TST, written before any run of the arm): stop-gradient consistency (SIC-sg)
Why: in clipe5z s1 the symmetric penalty (z_f(x) - z_f(x_s))^2 pulls the clean logit toward the smoothed one. For forgeries
whose cue is texture loss, z_f(x_s) < z_f(x), so the clean forgery score is pushed down: FF++ in-domain forgery recall
90.9 -> 69.8 %, CDFv2 video 0.947 -> 0.876. The accusation axis was fixed by the other half of the same gradient (smoothed
genuine pulled to the clean genuine score).
Arm clipe5bzsg: clipe5bz (binary, symmetric view, evidence head, lambda = 1, seed 20260929) with the clean logit detached in
the consistency term, lk = mean (stopgrad[z_f(x)] - z_f(x_s))^2 (`--cons-stopgrad --tag-suffix sg`). Only the smoothed view
is pulled toward the clean score of the same item; the clean path is trained by the forged BCE alone, as in the binary
control. Prediction written down now: bars (4)-(6) (untreated CDFv2 / DFD video, Celeb-DF-B, DF40 reenactment) within the
binary control's band; bars (1)-(2) pass if the smoothed view learns to match the clean score; bar (3') holds because
smoothed forgeries are pulled up to their clean score. If (1)-(2) fail while (4)-(6) hold, the stop-gradient removed the
mechanism that fixed the accusation and lambda alone cannot recover it; then the Amendment 3 curve is the result.
Bars, forms, rule, control: unchanged from Addendum 46 and Amendments 2-3; the lambda = 0 control (clipe5bzl0) is the
control for this arm too. Second seed trained before any claim. Code: train_ru5.py md5 40167a99bc21026f7649c1a1b5a9cc20
(flag + one `.detach()`, meta records `cons_stopgrad`); default off, so the queued Ubuntu runs are unchanged.
Scheduling: the local clipe5z s2 run (factorised, lambda = 1) was stopped at step 14,400 / 31,272 to free the local GPU
for this arm; no checkpoint of it is evaluated; it is restarted only if the factorised arm is needed. Smoke: 30 steps
under the tag clipe5bzsgsmoke, files deleted afterwards.

### Addendum 46, Amendment 5 (2026-10-18 10:30 TST): third machine and activation checkpointing
cvlab-103 (NTHU CV lab; 2 x RTX 4090 24 GB; data mirrored from gsplat-ubuntu to /mnt/sdb/doreen071/AIGC_sbifix, same Python
3.11 package versions, torch 2.7.1+cu126) joins the two RTX 6000 Ada boxes. The training step peaks at 23.9 GiB, so runs on
the 4090s use `--grad-ckpt` (HF gradient checkpointing of the ViT encoder, use_reentrant=False): the forward and backward
values are the same, only activations are recomputed; batch size, seeds, data order and every loss stay as declared.
train_ru5.py md5 after the flag: see add46_chain.log / queue logs (the flag defaults off). Runs planned there: the second
seed of SIC-sg (clipe5bzsg_s20260930) and the FF++-only SIC-sg arm (clipe5fbzsg_s20260929), both from Amendment 4's list;
their 30-step smoke on the 4090 (memory, loss terms) is logged before the full runs.
Note (Amendment 5, 2026-10-18 11:28): the Addendum 46 guard in train_ru5.py rejected --ffpp-only; relaxed so the FF++-only SIC-sg arm of Amendment 4 can run (md5 29770a8f47d0718340ebb1da7e8e06cd; nothing else changed; the guard change does not affect any full-data run).
Note (2026-10-18 11:50 TST, Amendment 2 control as actually run): clipe5bzl0 was launched with `--smooth-consistency 0`, which
takes the plain binary code path of train_ru5.py (forged BCE only; no x_s copy, no evidence-map loss). It therefore controls the
symmetric smoothing view alone, not "view + evidence head" as Amendment 2 wrote. It is kept and labelled "symmetric view, forgery
head only, no map, no L_cons"; the map loss is shared by clipe5bz and clipe5bzsg, so the view-only control still separates the
consistency term from the view. If a view+map control is needed, it is a new arm (lambda = 0 through the cons path), not a
relabelling of this one.
Note (2026-10-18 12:58 TST): at lambda = 0 the variant logic names the control clipe5byl0 (letter y, not z). Its meta, csv and the eight epoch files were copied on Ubuntu to the clipe5bzl0 names that readout46.py and the chains expect; contents identical, originals kept.

### Addendum 46, Amendment 6 (2026-10-18 17:20 TST, after the clipe5bzsg s1 and clipe5bzl0 s1 readouts, before any run of the new arms)
Readouts. SIC-sg s1 (stop-gradient, lambda = 1): bars (1) and (2) pass (fl06 5.8 %, fl12 4.4 %, bilateral 4.8-6.2 %, median 9.1 %,
Gaussian blend 5.3 %, commercial Smoothing-90 2.1 %); (3') fails at fl12 only (+9.7 vs 5); (4) CDFv2 video 0.907 vs 0.956
(fails), DFD 0.986 vs 0.987 (within band); (5) Celeb-DF-B 0.835 vs 0.866 (fails); (6) DF40 reenactment ff 0.768 vs 0.842
(fails), cdf 0.599 vs 0.647. Against the symmetric penalty (clipe5z s1: CDFv2 0.876, DF40 ff 0.663) the stop-gradient
recovers part of the detection loss but not all of it: the smoothed branch's gradient still moves the shared LoRA weights.
lambda = 0 control (clipe5bzl0, symmetric view, no map, no L_cons): fl06 53.9 %, fl12 91.8 %, Smoothing-90 11.9 %; CDFv2 0.943,
DFD 0.975, Celeb-DF-B 0.891, DF40 ff 0.835. So the view alone keeps detection and does not remove the face-local accusation;
the consistency term removes it and costs detection. The credit for bars (1)-(2) goes to L_cons; the cost on (4)-(6) too.
New arms (binary, stop-gradient, seed 20260929, everything else as clipe5bzsg): clipe5bzsgl03 (--smooth-consistency 0.3
--cons-stopgrad --tag-suffix sgl03) and clipe5bzsgl01 (0.1, --tag-suffix sgl01). Same bars; the Amendment 3 claim rule applies
to the stop-gradient family too (smallest lambda passing (1)-(2), then (3')-(6) judged there, second seed before any claim).
If no lambda passes (1)-(2) while (4)-(6) hold, the paper reports SIC as a measured trade-off curve (FA against untreated AUC),
with both families and the lambda = 0 control on the curve. Local GPU: clipe5bzsgl03 starts now; clipe5bzsgl01 follows.

### Addendum 46, Amendment 7 (2026-10-18 17:28 TST, written before any run of the arm): blur ablation of the consistency operator
Question: does the consistency term remove the accusation because the view is skin smoothing, or would any blur of the same
support do? Arm clipe5bzsgG: clipe5bzsg (binary, stop-gradient, lambda = 1, seed 20260929) with the operator of x_s replaced
by a Gaussian blur of the same spatial support and kernel scale (face-local: same feathered hull, same mix, sigma = d / 4
where d is the bilateral diameter drawn as before; whole-crop: sigma = d / 4 for d in 9 / 15 / 21). Nothing else changes.
Prediction written now (from the band-energy analysis of 2026-10-18 and Addendum 31/32): the Gaussian view does not remove the
face-local or commercial accusation (bars (1)-(2) fail) and costs little detection; if it does remove it, the mechanism is
blur after all and the paper's mechanism section must be rewritten. Bars and claim rule unchanged. Code: train_ru5.py
--cons-op gauss, md5 b6c6cbfbaafaf12abf23c552925ea3d7 (new function op_gauss_facelocal, cons_op threaded to the dataset and meta; default bilateral, so
every other run is unchanged). Runs on cvlab-103 GPU0 after clipe5bzsg s2 finishes; 30-step smoke first.

### Addendum 46, Amendment 8 (2026-10-18 21:05 TST, written before any run of the arm): one-sided consistency (SIC-h)
Readouts so far: SIC-sg s2 repeats s1 on the accusation bars (FA 5.5-8.5 %, Smoothing-90 12.3 %) and on the detection cost
(CDFv2 0.844 vs 0.963 binary, DF40 ff 0.746 vs 0.856; s1: 0.907 vs 0.956, 0.768 vs 0.842). The cost is reproducible; its size
varies with the seed. Reasoning for the new arm: the squared penalty asks the smoothed FORGERY to keep the clean forgery
score, i.e. to be detected through the smoothing that removes its texture cue; that demand is not needed for the accusation
axis (which only needs smoothed GENUINE faces not to rise) and is the likely source of the cost. Arm clipe5bzsgh: clipe5bzsg
with lk = mean relu(z_f(x_s) - sg[z_f(x)])^2 (penalise a rise of the forged logit under smoothing, allow a fall; stop-gradient
on the clean side; --cons-hinge --tag-suffix sgh), lambda = 1, seed 20260929. The symmetric view's forged BCE on smoothed
forgeries still asks them to be called fake, so the evasion bar (3') stays the guard. Prediction written now: bars (1)-(2)
pass; (3') fails or is borderline at fl12 (smoothed forgeries may fall); (4)-(6) closer to the control than SIC-sg. Code md5
23e79f441b5f717d90ef63e97f2502e9 (one flag, one line in the loss; default off). Runs on the local GPU after clipe5bzsgl03 finishes.

### Addendum 46, Amendment 9 (2026-10-18 21:06 TST, written after the lambda 0.3 readout, before any run at lambda 0.03)
The accusation bars pass at lambda 1 and 0.3 with the same FA (4-10 %), while the detection cost falls with lambda. To locate the
knee, one more point on the stop-gradient family: clipe5bzsgl003 (--smooth-consistency 0.03 --cons-stopgrad --tag-suffix sgl003,
seed 20260929). Same bars and claim rule (smallest lambda passing (1)-(2); (3')-(6) judged there; second seed before a claim).
No code change (md5 23e79f441b5f717d90ef63e97f2502e9). Runs on the local GPU after clipe5bzsgh.

Note (2026-10-19 06:15 TST, incident): the local clipe5bzsgl03 run crashed at 17:57 on 10-18, forty minutes after train_ru5.py was
edited for Amendment 7. On Windows the DataLoader workers are spawned, so they re-import the edited module while the
dataset object pickled from the main process predates the edit (no `cons_op` attribute). The run is restarted unchanged
(same arguments, same seed, same code as every other arm in its family); its first 2,900 steps are discarded. Rule from now on:
never edit train_ru5.py while a Windows run is active; copy the script under a new name for new arms if needed. The
Amendment 8 and 9 arms that were queued behind it on the local GPU move to cvlab-103 (both GPUs idle since 04:13).

### Addendum 47 (2026-10-19 16:40 TST, written before any analysis is run): beautification-conditional threshold (BCT)
Motivation. Fifteen training arms (Addendum 46, Amendments 1-9) show that changing the detector's weights to ignore skin
smoothing either costs untreated detection (symmetric and stop-gradient penalties, every lambda) or opens an evasion route
(one-sided penalty, genuine-only exposure). The cue is real forgery evidence, so the weights cannot discard it for free.
BCT leaves the scores untouched and conditions the decision on an estimate of how much the face was smoothed.
Method. b(x) = the skin-smoothing quantity output of the full model (clipe5_s20260929, q[3] in OPS order; its presence
probability sigmoid(pres[3]) is the secondary covariate). For a detector d with score s_d(x): base threshold t_d = 95th
percentile of s_d on the test source's untreated genuine frames (the paper's rule, unchanged). Shift: on FF++ validation
GENUINE frames (530, FaceForensics_protocol_frames/val/real, never used for training or model selection) rendered with the
seven Addendum 38 forms plus untreated, b is binned into deciles (bin edges from these frames), and
Delta_d(k) = Q95[s_d | bin k] - Q95[s_d | bin 1], made non-decreasing in k by a running maximum, Delta_d(1) = 0.
Decision: fake iff s_d(x) > t_d + Delta_d(bin(b(x))). Nothing is fitted on Celeb-DF-v2, Celeb-DF-B, DFD, DF40 or the
commercial renders. Applied to the 17 published detectors (their Addendum 38 scores) and to ours (binary control clipe5b,
main clipe5, SIC-sg).
Readout (same quantities as Addendum 46): FA and miss rise per form on the Celeb-DF-v2 probe frames at the new rule;
commercial Smoothing-90 accused share (b from the renders); bars (1), (2), (3') as declared; bars (4)-(6) are unchanged by
construction (scores and AUCs are not modified) and are stated, not re-measured. Untreated FA at the new rule is reported
(it may exceed 5 % where untreated genuine faces have b > bin 1: that is a cost to report, not to hide).
Predictions written now: (a) for the CLIP detectors and ours, face-local and commercial FA fall below 15 % (the shift is
learnt on the same forms); (b) the miss rise on smoothed forgeries grows by about the same amount that FA falls (the
threshold is raised for forgeries too), so bar (3') is the deciding one; (c) median and Gaussian-blend forms, whose b is
small for the estimator, are helped least. Scripts: bct.py (prep / score / analyse), outputs bct_*.npz, BCT.md. Renders on
N:\2603055\AIGC\smooth_probe_ffval_20261019. Frames and forms are fixed before scoring; no form or bin rule is changed after
reading the results.

### Addendum 47, Amendment 1 (2026-10-19 22:50 TST, after reading BCT.md v1)
Result of the declared rule: Delta is 0 for 18 of 21 detectors (BCT.md v1), so the rule changed nothing. Cause, read from the
calibration data only: the quantity output q[3] is NEGATIVE for whole-crop bilateral renders (median -0.05 to -0.10; it was
trained on face-local smoothing), so decile bin 1 of b is made of bilateral renders whose scores are already high, and
Delta relative to bin 1 vanishes. The presence probability sigmoid(pres[3]), declared as the secondary covariate, is
monotone across every smoothing form (FF++ val medians: untreated 0.01, bilateral 0.99-1.00, median 0.97, face-local 1.00;
Gaussian blend 0.29, which is not skin smoothing). v2, declared now and run once: covariate = presence probability; four
fixed bins [0, 0.1), [0.1, 0.5), [0.5, 0.9), [0.9, 1]; reference = bin 1 (untreated-like); Delta(k) = Q95[s | bin k] -
Q95[s | bin 1] on FF++ val genuine renders, non-decreasing. Everything else (t0 per test source, bars, untreated FA/miss
reported) unchanged. v1 stays in the record as BCT_v1.md.

### Addendum 48 (2026-10-21 14:30 TST, written before any run): smoothing-conditional expert (SCE), a routed detector
Problem it answers. Addendum 46 shows every single-model constraint pays with untreated detection or with evasion; Addendum 47
shows a threshold rule cannot separate smoothed genuine from smoothed forged faces because the untreated detector's scores
coincide under smoothing. SCE keeps the untreated detector untouched and adds a second detector trained for smoothed inputs.
Components. (A) the forgery-head-only reference model clipe5b (unchanged weights); (B) the smoothing expert clipe5bzxs: the same
recipe and data, every training item replaced by its smoothed copy x_s (one operator, one strength distribution, both
classes; forged BCE + map loss; no consistency term; train_ru5b.py --train-on-xs); (R) the router, the full model's
skin-smoothing presence probability p_s (sigmoid(pres[3]) of clipe5_s20260929), which is 0.01 on untreated frames and
0.97-1.00 on every smoothing form in the Addendum 47 data. Decision: if p_s > 0.5 use B's score against t_B, else A's score
against t_A. t_A = the paper's rule (5 % FPR on the test source's untreated genuine). t_B = 95th percentile of B's score on
FF++ validation GENUINE frames under the seven smoothing forms (calibration data of Addendum 47, never a test source).
Bars: the six of Addendum 46 (+ 3'). Predictions written now: (4)-(6) pass by construction up to routing errors on untreated
frames (p_s > 0.5 on about 1 % of untreated frames); (1)-(2) pass if B's separation under smoothing is at least that of the
view-only control (AUC both-smoothed 0.76-0.87); (3') is the deciding bar and will likely fail at the strong face-local form
(miss rise bounded by B's TPR at 5 % FPR under smoothing), but by far less than the threshold rule (78-100 %). Readout: as
Addendum 46, plus B's own AUC under both-classes smoothing per form, and the routing error rates. Evaluation script
sce_eval.py (to be written before B finishes; it reads smooth38_clipe5b, the new smooth38_clipe5bzxs, and the Addendum 47
covariates). Second seed before any claim.
Hardware note. The arm trains on cvlab-104 (Quadro RTX 8000, no bf16) in fp32 (train_ru5b.py --precision fp32, grad-ckpt);
every other arm used bf16 autocast. Precision is recorded in the meta file; if the expert's untreated FF++ validation AUC is
within 0.01 of the bf16 reference run of the same recipe, precision is treated as immaterial, else a bf16 re-run on the local
GPU is required before comparison.

### Addendum 49 (2026-10-21 14:30 TST, written before the run): is the cue taught by the texture-poor forgeries?
Finding of 2026-10-21 (FFPP_BAND.md): Deepfakes and NeuralTextures training frames have 17-26 % less fine texture inside the
face than their source frames (face-local smoothing: 20 %); Face2Face has 7 % less, FaceSwap 6 % more. Hypothesis: a
detector trained without Deepfakes and NeuralTextures accuses smoothed genuine faces less. Arm clipe5fbp0F2: the FF++-only,
no-view arm P0 (--ffpp-only --binary --beauty none) with the observed forgeries restricted to Face2Face and FaceSwap
(train_ru5b.py --ffpp-methods Face2Face,FaceSwap --tag-suffix F2), seed 20260929; self-blends unchanged. Readout: Smoothing-90
accused and paired share, face-local FA (smooth38), untreated CDFv2 / DFD video AUC, against P0 s1 (54.2 % accused, 97-99 %
paired). Prediction written now: the accusation falls but does not vanish (self-blends also carry a blended boundary), by at
least 15 points if the training forgeries are the origin; if it does not fall, the origin is the self-blend or the generic
forgery boundary, and the paper says so. One seed, exploratory, reported in the mechanism section with that status.

### Addendum 50 (2026-10-21 14:30 TST, written before the run): SIC-sg under Effort's tuning scheme (plug-in test)
Arm clipe5bzEsg: clipe5bzsg (binary, stop-gradient, lambda 1, seed 20260929) with --tune effort (SVD-residual tuning of the
attention projections as in the released Effort code, Addendum 26) in place of LoRA. Bars as Addendum 46 with the reference
the Effort-scheme binary arm of Addendum 35 where scored, else the LoRA reference. Prediction: bars (1)-(2) pass (the view
removed the whole-crop accusation under Effort's scheme in Addendum 35; the face-local one is the open case); cost pattern as
in the LoRA family. Trains on cvlab-104 in fp32 (same note as Addendum 48).

### Addendum 51 (2026-10-21 evening TST, written before any embedding is computed): is identity evidence untouched by smoothing?
Motivation (idea-generation pass, Light-skills light-idea-generation, "which forgery evidence can smoothing not touch by
definition?"). Observed today from the existing smooth38 scores: with BOTH classes smoothed, every one of the 17 published
detectors and every arm of ours loses separability (bil15 AUC drop 0.08-0.27; best 0.79). Smoothing preserves identity by the
paper's own definition of beautification, and an identity swap changes identity by definition. Hypothesis: a reference-assisted
identity score keeps its separation under smoothing where texture-based detectors lose it.
Design (exploratory, zero training, CPU). Probes: the smooth38 frames of Celeb-real (genuine) and Celeb-synthesis (forged) test
videos (YouTube-real excluded: no identity reference exists), conditions untreated, bil15, bil21, fl06, fl12 (the same PNGs every
detector read). Reference per identity: InsightFace buffalo_l (ArcFace R50) mean embedding of 5 frames from each of up to 4
Celeb-real videos of the claimed identity that are NOT in List_of_testing_videos.txt; claimed identity = the target id (first id
in idT_idS_xxxx, the id in idX_xxxx). Score = 1 - cos(probe, reference). Readout: AUC per condition (identity-cluster bootstrap
over target ids), the same AUC for clipe5b_s20260929 and Effort on the same probe subset, and rank-average fusion.
Prediction written now: identity AUC drops by at most 0.03 from untreated to bil15 and fl12, while clipe5b and Effort drop by
>= 0.08 on the same subset. Kill criterion: identity AUC drops by more than 0.05 under bil15 or fl12 (then smoothing also damages
identity evidence and the ceiling claim of the paper widens to it). Known limits stated now: the identity route needs a reference
of the claimed person and is blind to reenactment (Face2Face, NeuralTextures keep identity); it is a complementary channel, not a
replacement. Script id_ref_probe.py.
Amendment 1 to Addendum 51 (written after the scoop check SCOOP_CHECK_C, before the embeddings finished and before any score
was read). Added readouts: (a) miss at 5 % FPR, threshold = 95th percentile of each score on untreated genuine probes, held
fixed across conditions (both directions: false alarm on smoothed genuine and miss on smoothed forged); (b) median identity
distance per class per condition, so a homogenization shift of forged probes toward the reference (OpenFilter, NeurIPS 2022) is
seen separately from the genuine shift (Mirabet-Herranz, TBIOM 2025). Positioning fixed now: identity evidence is a known
channel (ID-Reveal, ICT-Ref, Yin & Jamaluddin 2026); the claim at stake is only its behaviour under smoothing.

### Addendum 52 (2026-10-21 night TST, written before any published identity detector is run): published identity detectors under smoothing
Reviewer-required baseline for Addendum 51 (SCOOP_CHECK_C). Detectors: ICT and ICT-Ref (Dong et al. CVPR 2022, released code and
weights, unchanged); ID-Reveal (Cozzolino et al. ICCV 2021) only if its released weights and preprocessing run on our sparse
frames, else reported as not run with the reason. Probes: exactly the Addendum 51 probe set (smooth38 Celeb-real / Celeb-synthesis
frames; conditions untreated, bil15, bil21, fl06, fl12; the same PNGs). ICT-Ref reference set: frames of the same non-test
Celeb-real videos used by Addendum 51 (same identities, same videos), processed by ICT's own pipeline. Readouts identical to
Addendum 51 (AUC with identity-cluster bootstrap of the drop, 5 % FPR threshold fixed on untreated genuine, per-class medians).
Prediction written now: ICT-Ref drops by at most 0.03 AUC (identity evidence), plain ICT (no reference) drops more than ICT-Ref
but less than the texture detectors; at the fixed threshold both accuse smoothed genuine faces more than at untreated. If ICT-Ref
drops > 0.05, the identity result of Addendum 51 is specific to ArcFace distance and the paper says so.

### Addendum 53 (2026-10-21 night TST, written before any FF++ embedding is computed): does a frozen recognition embedding carry smoothing-robust forgery evidence WITHOUT a reference?
Synthesis of Addenda 51-52: the smoothing-robust signal was ArcFace distance to a reference; forgery-trained identity models (ICT)
were not robust. Question: is the robustness a property of the recognition-trained representation itself (usable reference-free)?
Design (exploratory, zero fine-tuning). Frozen InsightFace buffalo_l ArcFace R50 embedding (512-d, normalised) of FF++ c23 TRAIN
frames: 3,000 genuine + 750 per manipulation (Deepfakes, Face2Face, FaceSwap, NeuralTextures), seed 0, one frame per video
sampled uniformly then frames, untreated only. Logistic regression (C chosen by 5-fold CV on the train sample only). Test: the
Addendum 51 Celeb-DF probes (Celeb-real vs Celeb-synthesis, all five conditions, embeddings already computed). Readouts as
RECAL_MISS.md: AUC per condition with drop, miss at 5 % FPR re-set on that condition's genuine frames; compared with clipe5b,
lambda=0 and Effort on the same probes.
Prediction written now: untreated AUC is low (0.60-0.75, recognition features are not trained for forgery) but its drop under
bil15 / fl12 is <= 0.03. Decision rule: if the drop is <= 0.03 AND a rank fusion with lambda=0 lowers lambda=0's recalibrated miss
at bil15 and fl12 by >= 5 points each without raising untreated miss by > 2 points, a recognition-anchored reference-free detector
becomes method candidate A2 (trained arm pre-declared separately). Otherwise A2 is dropped.
Amendment to Addenda 48 and 50 (2026-10-21 night, before any result of either arm): Addendum 50 (SIC on Effort tuning) is
withdrawn at step ~2,000 of 31,272 on cvlab-104 (projected 69 h in fp32): RECAL_MISS.md showed SIC's gain equals a
smoothing-conditional threshold, so its plug-in generality no longer bears on any claim. The freed time goes to the second seed
of the Addendum 48 expert, trained LOCALLY in bf16 (as every other arm): clipe5bzxs_s20260930 (train_ru5b.py --binary
--smooth-consistency 1.0 --train-on-xs --tag-suffix xs --seed 20260930). Seed 20260929 continues on cvlab-104 in fp32; the
precision note of Addendum 48 applies to comparing the two.

### Addendum 54 (2026-10-21 night TST, written before any GPUPixel render is scored): does a deployed open-source beauty engine reproduce the measurement?
Benchmark track (SPRINT_PLAN_20261021.md): the releasable smoothing operator. GPUPixel (pixpark/gpupixel, Apache-2.0, commit
ef552bf8, 2026-09-26) BeautyFaceFilter skin smoothing, ported to numpy from the shaders (BoxBlur radius 4 x texel spacing 4 ->
5 taps at 0, +-6, +-14 px weights 1/9, 2/9; BoxHighPass delta 7.07 clamped to [0,1]; unit shader kMin = (1 - v/(v+0.1)) * p *
blurAlpha with the red-channel skin gate p; sharpen 0, whiten 0; 8-bit intermediate framebuffers, clamp-to-edge). Not yet
validated bit-exact against the compiled library (stated as a limitation until done). Forms gpx3 / gpx6 / gpx9 = blurAlpha 0.3 /
0.6 / 0.9 (the demo slider 3/6/9 of 10), whole crop, both classes, the smooth38 frames (Celeb-DF-v2 test, 4,016). Scored by the
17 published detectors and our arms with the smooth38 code unchanged.
Predictions written now: (1) at the untreated 5 % FPR threshold, false alarm on gpx9 genuine frames exceeds 15 % for at least
10 of the 15 face detectors (the accusation reproduces on a deployed engine); (2) AUC with both classes smoothed falls
monotonically with blurAlpha for at least 12 of 15; (3) the ordering of detectors by gpx9 false alarm correlates with their
bil15 false alarm (Spearman >= 0.5). Kill: if (1) fails, the paper's accusation claim is restricted to our scripted forms and the
benchmark track loses its releasable operator.
Amendment 1 to Addendum 54 (before any render was scored; only 2 crops inspected visually): applied at native crop size
(150-440 px) the engine's fixed +-14 px taps produce ghosting no deployed app shows, because the engine assumes camera-resolution
faces. Forms are therefore rendered at camera scale (shorter side resized to 512 px, cubic up / area down, smooth, area back to
the crop size). The resize round trip itself removes texture (|Laplacian| 3.91 -> 3.44 on one crop), so a null form gpx0 (the
same round trip, blurAlpha 0) is added and every gpx effect is read against gpx0 as well as against untreated; prediction (1)
is evaluated for gpx9 against the untreated threshold AND reported with gpx0's false alarm next to it.

### Addendum 55 (2026-10-22 00:40 TST, written before any operation score is read on AR renders): what does the operation head identify when several operations are applied at once?
Question raised at the 2026-10-18 meeting (senior lab member): the four-operation head has only ever been scored on
single-operation commercial renders (Alibaba, one operation per image). Instagram AR beauty filters apply several at once.
Data: FairBeauty controlled pairs (2,927, Addendum 43 (A)), genuine only, never trained on by the main model; the three
held-out filters are the strictest subset for clipe7. Ground truth per pair measured with measure_pairs.py quantities, each
image with its own landmarks (the pairs are not pixel-aligned): eye_ratio, jaw_ratio, dL_skin, hf_ratio. Presence rule fixed
now = half of the Alibaba level-30 median effect (pairs_ali.tsv, read before this addendum): eye present if eye_ratio >= 1.006,
slimming present if jaw_ratio <= 0.993, whitening present if dL_skin >= +0.90, smoothing present if hf_ratio <= 0.946. The
rule is coarse (level 30 is near the pairs' own noise), so the readout also reports agreement at the stricter full level-30
medians (1.012 / 0.986 / 1.80 / 0.893).
Models: clipe5_s20260929 (paper main), clipe7_s20260929 (AR-trained, shortcut known). Readouts per filter and pooled: measured
presence rates (what the filter does), head presence rates (sigmoid >= 0.5) on renders and on originals, per-operation
precision / recall against the measured truth, exact four-bit match, and Spearman of the quantity head against the measured
quantity per operation.
Predictions written now: (1) smoothing is the only operation with recall >= 0.7 on AR renders for clipe5; eye and slimming
recall < 0.5 (AR geometry is subtle and differs from the training vendors); (2) false presence on originals < 10 % per
operation for both models; (3) clipe7 recall is higher but its precision is not (it flags operations the filter did not
apply, consistent with the pipeline shortcut). Exploratory, no bar; the result goes to the capstone report as the answer to
the meeting question and bounds what the explanation may name under combined filters.

### Addendum 56 (2026-10-22 TST, written before any multi-operation arm is trained): multi-operation beautification on both classes (RU9), with its ablations and a plug-in arm
Designed with the Light-skills research-plan procedure (fair control, falsifiable hypothesis, single-component ablations,
negative control). Motivation: the main model clipe5 accuses Instagram AR-filtered genuine faces (FairBeauty 75.1 %, B-LFW
94.3 % at 5 % FPR on originals; FINDINGS 10-16) and recognises only smoothing among the four operations (Alibaba TP 6-56 %
for eye / jaw / white at levels 30-90). Measured today (Addendum 55, before any model score on AR renders was read):
AR filters combine operations, smoothing 97 % and eye enlarging 81 % of renders, whitening 3-89 % by filter, slimming 9 %.
Correction of an earlier oral statement: clipe5 training is not single-operation only; 12 % of its genuine filter items are
vendor composites (Megvii four-process). What it has never seen is a combination including geometric operations on FORGED
faces, nor a scripted combination with controlled strengths.
Hypothesis H1: adding scripted multi-operation beautification (mo_chain.py: GPUPixel-style thin face and big eye, ported
GPUPixel smoothing, whitening; random non-empty subset; strengths calibrated to Alibaba levels 30-90 and above) to both
classes lowers the accusation of AR-filtered genuine faces and raises eye / jaw recognition, without raising the escape of
beautified forgeries.
Arms (train_ru6.py = train_ru5b.py + --multi-op / --multi-k1; everything else as the control, same steps, same data, bf16, local):
 M    clipe5M_s20260929: main recipe (as clipe5) + --multi-op 0.5 --tag-suffix M. Second seed s20260930 before any claim.
 M1   clipe5M1_s20260929: + --multi-op 0.5 --multi-k1 --tag-suffix M1 (same operators, never combined): isolates composition.
 C    clipe5_s20260929 / s20260930 (existing control, single-operation recipe).
 EM   clipe5fbEM_s20260929: the Effort-tuning FF++-only binary arm clipe5fbE (existing, two seeds) + --multi-op 0.5
      --tag-suffix M: plug-in test on another tuning scheme, against its own existing control.
No arm reads FairBeauty, B-LFW, Alibaba, Celeb-DF-B or any test split.
Primary endpoint (decides H1): FairBeauty accused at 5 % FPR on its own originals (eval_fairbeauty_pairs.py), M vs C, paired
over the 2,927 pairs, both seeds. Success: M lower than C by >= 20 points in both seeds, AND the face-hull-greyed negative
control (ar_pipeline_control.py) calls <= 20 % of greyed renders filter (so the change is read from the face, not the
pipeline; RU7 was 94.8 %). Strong success: M <= 10 %. Failure (H1 rejected): drop < 10 points in either seed.
Secondary: B-LFW accused (ar_source.py), same rule; operation recognition on FairBeauty (fb_ops_probe.py, eye recall vs
measured presence; on Alibaba eval_ru.py TP for eye / jaw at level 60); M1 vs M on the same endpoints (composition is credited
only if M beats M1 by >= 10 points on the primary endpoint); EM vs clipe5fbE on FairBeauty (plug-in credited if >= 20 points).
Guardrails (any breach is reported and blocks adoption as the capstone model): Celeb-DF-B beauty-only rise in MISS <= C + 3 pp;
CDFv2 and DFD video AUC >= C - 0.01; Alibaba balanced >= C - 2; FF++ FA <= C + 2; untreated FFHQ originals called filter
<= C + 5 pp.
Test-source statement: GPUPixel smoothing is now a training operator, so the Addendum 54 GPUPixel forms are not an unseen
source for these arms; unseen beautification sources for them are Alibaba, FairBeauty, B-LFW and Celeb-DF-B only.
Amendment 1 to Addendum 56 (2026-10-22 13:00, before any FairBeauty score of any Addendum 56 arm was read): (i) clipe5M
s20260930 died at step ~2,200 (DataLoader MemoryError, host RAM, four evaluations running); restarted from scratch with 6
DataLoader workers instead of 12 (per-item seeds, the data stream does not depend on the worker count). (ii) The EM arm runs on
gsplat-ubuntu (bf16), where the Addendum 56 script is saved as train_ru9.py because train_ru6.py there is the Addendum 7 RU6
script (kept unchanged; a copy is saved locally as train_ru6_add7_from_ubuntu.py). Same md5 as the local train_ru6.py.

### Addendum 57 (2026-10-23 09:30 TST, written before any render is scored): is the cue the smoothing BOUNDARY rather than the smoothness?
Evidence so far: face-local smoothing accuses 28 points more than whole-crop at the same kernel; bilateral accuses 67 points
more than Gaussian at equal energy loss (bandenergy_20261018); Addendum 49 (clipe5fbp0F2) shows that removing the texture-poor
Deepfakes / NeuralTextures forgeries from training does not change the accusation at all (face-local FA 95.5 / 100 % vs 95.8 /
100 %), so the cue is not taught by those families; every detector's training forgeries carry a blended boundary. Hypothesis:
detectors read the transition between the smoothed interior and the untouched exterior as a blending boundary.
Design (zero training, bdry_probe.py): the smooth38 frames, bilateral strength fixed at frac 0.12 (fl12), six forms that differ
only at the hull edge: hard (no feather), fe01 (= fl12), fe05, fe15 (feather 0.15 w), whole (no boundary), ring (smoothing only
in a 0.10-jaw-width band at the edge, interior untouched). Scored by the 17 published detectors and our arms with the smooth38
code. Readout: FA on smoothed genuine frames at the untreated 5 % FPR threshold, and AUC with both classes treated.
Predictions written now (15 face detectors): (1) FA falls monotonically from hard to fe15 for >= 10/15; (2) ring-only, which
smooths almost no skin, keeps >= 70 % of the fe01 accusation for >= 10/15; (3) whole-crop sits >= 10 points below fe01 for
>= 10/15 (already known for fl forms; here at equal interior strength). If (1) and (2) hold, the signal is the boundary and
Addendum 58 (training views without a boundary vs with) follows; if (2) fails (ring accuses little) the cue is the interior
smoothness and the boundary story is dropped.

### Addendum 58 (2026-10-23 evening TST, written before training): close the in-the-wild genuine-photo gap (arm W)
Diagnosis (Addenda 55-56, ar_pipeline_control): the main model calls plain FairFace validation ORIGINALS real only 23.2 %
(fake 26.1 %, beautified 50.6 %); Alibaba FFHQ originals are called beautified 20.8 %. Its genuine bases are FF++ video frames
and FFHQ portraits only, so ordinary still photos are out of distribution before any filter is applied. Project precedent:
adding CelebA genuine stills moved CelebA real recall from 4.1 % to 99.6 % (v8.3 -> v8.4).
Arm W = clipe5 recipe + FairFace TRAIN originals as additional genuine BASES (RUData7 with p_ar = 0: no FairBeauty render
is ever read; ids with md5 % 10 == 0 held out as in Addendum 8). Every base produces a genuine view, a self-blend forgery and
a beautified view, so the new photos enter all three classes symmetrically; the existing symmetric resize / JPEG
randomisation applies to all items. Script train_ru7w.py (= train_ru6.py + --ar-p), tag clipe7W_s20260929, gsplat-ubuntu,
bf16, same steps as clipe5. Second seed before any claim.
Primary endpoints (control clipe5 s1 / s2): (P1) FairFace VALIDATION originals called real (eval_fairbeauty_pairs) >= 70 %
(control 23.2); (P2) FairBeauty renders accused at 5 % FPR on their originals <= control - 20 points (control 75.1 / s2 n/a).
Secondary: Alibaba originals called beautified <= 10 % (control 20.8 / 19.6); ar_pipeline_control (face hull greyed).
Guardrails: Celeb-DF-B beauty-only rise in MISS <= control + 3 pp; CDFv2 and DFD video AUC >= control - 0.01; Alibaba balanced
>= control - 2; FF++ FA <= control + 2. Failure: P1 < 50 % or P2 drop < 10 points. Known limits stated now: FairFace train
and validation are image-disjoint but not identity-checked; the improvement on FairBeauty can still be pipeline-confounded,
so P2 is read together with the grey-face control.

### Addendum 59 (2026-10-23 evening TST, written before training): is single-image naming of eye / slimming / whitening impossible, or did our models fail to learn it?
Evidence so far: six approaches (vendor-supervised operation heads RU2-RU5, quantity head, artifact classifier v3-v6, P1-B1,
RU9 multi-operation views) never recognised eye enlarging, slimming or whitening; detectability.json shows the edit moves a
face's filter score by about 1 SD of the spread between untouched photos (smoothing 3-4 SD). Hypothesis H0: at vendor
strengths these three edits leave no single-image signal that a learned detector can find.
Oracle test (oracle_ops.py): per operation (Alibaba level 90; smoothing as positive control), a dedicated EfficientNet-B0
trained to separate the render from untouched originals in the most favourable setting (same vendor and level, lossless PNG,
384 px crop, identity-disjoint 70/30 split by FFHQ index, both sides of every training face used). Readouts: unpaired AUROC on
held-out faces (bootstrap CI), paired rank, and the same after JPEG q90 + resize to 256 px.
Decision rule written now: if lossless AUROC < 0.90 for an operation, single-image naming of it is reported as infeasible at
vendor strength (the paper and capstone state it as a finding, with this number). If lossless AUROC >= 0.95, a trace exists
that our models did not learn: the operation becomes a fixable target (next step: the same dedicated head inside the system),
and the JPEG number decides whether it survives sharing. Between 0.90 and 0.95: report as weak. Prediction: eye, slimming,
whitening < 0.90; smoothing >= 0.98.
Amendment 1 to Addendum 59 (written after the per-operation AUROCs were read, before any cross-operation score): specificity
check. Each dedicated classifier is applied to the held-out renders of the OTHER three operations (same 663 held-out faces,
same originals). If a classifier separates other operations' renders from originals with AUROC >= 0.85, it reads a shared
vendor/processing fingerprint, and its own-operation AUROC is NOT evidence of operation-specific detectability. An operation
counts as single-image detectable only if own AUROC >= 0.90 AND every cross AUROC < 0.75. Post hoc by construction (the
own-operation numbers were already read); reported as such.

### Addendum 60 (2026-10-23 night TST, written before training): do dedicated operation classifiers transfer ACROSS vendors?
Addendum 59 found within-vendor single-image signal for whitening (0.980, specific) and eye enlarging (0.933, marginally
specific), not for slimming (non-specific). The capstone system can use a dedicated classifier only if it transfers to a
vendor it never saw. Design (xvendor_ops.py): per operation (eye, white; jaw and smooth reported as reference), a dedicated
EfficientNet-B0 trained on the TRAINING vendors only: FFHQ Part7 originals (7,015 training indices) against the Megvii +
Tencent single-operation components of the same op (vendor_single/<vendor>/<op>, 512 px; originals brought to the same 512 px
scale before the same box crop, so resolution cannot separate the classes); tested on Alibaba (never trained on; FFHQ Part2,
other identities): renders at levels 30 / 60 / 90 vs the 2,210 untouched originals, and on the other operations' Alibaba
level-90 renders (specificity). Readouts: AUROC per level with bootstrap CI, paired rank, cross-operation AUROC, JPEG q90.
Decision rule: an operation is adopted as a capstone operation head if Alibaba level-90 AUROC >= 0.85 AND every cross-operation
AUROC < 0.70; level 60 >= 0.75 is reported as the usable strength. Otherwise the capstone states "detectable within a vendor,
does not transfer". Prediction: whitening transfers (>= 0.85), eye does not (< 0.80).

### Addendum 61 (2026-10-27 19:30 TST, written before any fl12w render is scored): test-time context matching
Mechanism (Addendum 57): detectors accuse a face that is smoother than its own context (ring-only 12 %, whole-crop far below
face-local). Method under test, zero training: score the image and its whole-crop-smoothed copy W(x) (bdry_probe "whole"
operator at the fl12 interior strength); call forged only if both exceed their thresholds (t_A = 5 % FPR on untreated genuine,
t_W = 5 % FPR on W(untreated genuine)). A beautified genuine face loses the inconsistency under W and should drop below t_W;
a forgery should keep evidence that does not depend on the face-context texture contrast.
Readouts (ctx_probe.py, 17 published + 4 of ours, smooth38 frames): FA on fl12 genuine (single vs joint), miss on fl12
forged, miss on untreated forged (cost), and the decisive comparison at matched 5 % FA on fl12 genuine: joint rule (t_W swept)
vs single-score recalibration (RECAL_MISS.md).
Predictions written now: (1) joint FA on fl12 genuine < 30 % for >= 10/15 face detectors; (2) at matched FA, joint miss on
fl12 forged is at least 10 points below recalibrated single-score miss for >= 8/15. Kill: (2) holds for < 5/15, in which case
context matching is a recalibration in disguise and is reported as such (one paragraph). If (2) passes, the next step is the
same rule inside our three-way system and on Celeb-DF-B / Alibaba.
Note: this is the second test-time idea after the smoothing-response probe (10-21, dropped); the difference is the operator
(context matching, not re-smoothing the face) and the mechanism evidence behind it.
Readout (2026-10-27 20:05 TST, CTX38.md): (1) 10/15 (bar met exactly); (2) 0/15 -> KILL. Joint miss at matched FA equals
single-score recalibration within a few points for every detector, and the second gate raises the miss on untreated
forgeries by 20-35 points. Context matching is a recalibration in disguise; reported as one paragraph. No follow-up inside
our system or on Celeb-DF-B / Alibaba (the conditional next step does not trigger).


### Addendum 62 (2026-10-28 01:10 TST, written before any Celeb-DF-B frame is embedded): identity evidence under real app presets, and a reference-conditioned detector
Why: Addendum 51 showed on scripted smoothing that the only evidence smoothing leaves separable is identity (ArcFace distance to a
reference of the claimed person: AUC 0.996 -> 0.98, recalibrated miss 7-22 % against 59-74 % for texture detectors), but that its
operating point moves (genuine distance 0.25 -> 0.32/0.38). Prior art (ID-Reveal, ICT-Ref, Yin & Jamaluddin 2026) uses identity
references but none measured beautification (SCOOP_CHECK_C). This addendum tests the finding on real app presets (Celeb-DF-B,
Libourel et al.) and asks whether a reference-conditioned rule beats the best texture detector on both directions.
Data: Celeb-DF-B frames_std32v3, six folders (real, real_beautified, real_compressed, synthesis, synthesis_beautified,
synthesis_compressed; 231 videos each, 58 claimed identities). Claimed identity = the first id in the video name (as in Addendum
51, where this convention gave AUC 0.996). References: ArcFace buffalo_l mean embedding of 5 frames from up to 4 Celeb-real videos
of the claimed identity that are NOT among the 231 Celeb-DF-B real videos (non-test-list videos preferred; every identity has
at least one spare video). Probe score = 1 - cos(frame embedding, reference). Texture scores: the existing per-frame files
celebdfb_v2_20260927/scores_v3/<detector>.npz, aligned by path. Rule: threshold at 5 % FPR on untreated genuine frames (real);
Direction A = FA on real_beautified minus FA on real_compressed; Direction B = miss on synthesis_beautified minus miss on
synthesis_compressed (the compression control of fair_cdfb.py). CIs: video-cluster bootstrap, 2,000 draws.
Predictions written now:
(1) Identity video-level AUC on the beautified pair (real_beautified vs synthesis_beautified) is at least the untreated AUC
    minus 0.03. Kill: drop > 0.05 -> identity does not survive app presets; the line closes.
(2) At a threshold matched to 5 % FA on real_beautified genuine frames (the recalibration reading), identity misses at most 15 %
    of synthesis_beautified, while every texture detector in scores_v3 misses at least 40 % under the same matching.
(3) Reference-conditioned rule = rank-mean fusion of a texture detector's quantile (against untreated genuine) and the identity
    quantile, read at the untreated 5 % FPR threshold: for BOTH pairs Effort + identity and ours (clipe5 s1) + identity, the
    beauty-only accusation is at most 10 points and the beauty-only miss rise at most 5 points (Effort alone: +11.0 miss rise,
    fair_cdfb.json). Bar: both pairs. A second, declared variant: a gate that trusts identity alone when the reference distance
    is below the untreated genuine 95th percentile (call genuine) and otherwise the fusion; reported beside, not instead.
(4) Operating-point shift reproduces: identity alone at the untreated threshold accuses real_beautified by at least 10 points
    more than real_compressed.
Reading rules: (1) and (2) pass and (3) passes -> the paper gains a method section (reference-conditioned detection under
beautification) with the reference requirement and the reenactment blind spot as stated limits. (1) and (2) pass, (3) fails ->
identity is reported as the one channel beautification leaves, needing a beautification-aware threshold; no method claim.
(1) fails -> one paragraph, line closed. ICT-Ref on the same frames (ict_probe.py infrastructure) is a follow-up comparison, not
a condition. No training anywhere in this addendum; nothing is tuned on Celeb-DF-B.
Readout (2026-10-28 02:55 TST, CDFB_ID.md): (1) PASS (vAUC 1.000 in all three conditions), (2) PASS (0.6 % vs 46-72 %), (3) FAIL (Effort+identity miss rise +8.5 > 5; ours+identity passes; gate passes but equals identity alone), (4) FAIL narrowly (+8.5 [6.4, 10.6] < 10). Declared reading: identity is the channel beautification leaves, needs a beautification-aware threshold; no fusion-method claim.


### Addendum 63 (2026-10-28 13:05 TST, written before any gate score is computed): a beautification-aware reference gate
Why: Addendum 62 found that identity against a reference keeps its separation under real app presets while every texture
detector loses most of its, and that a fixed rank-mean fusion failed its bar on one pair (Effort + identity: miss rise +8.5 > 5)
while a hard gate that trusts identity whenever it says genuine passed every bar but equals identity alone. The data say the
weight on identity should rise with the amount of beautification. No prior reference-conditioned detector (ID-Reveal, ICT-Ref,
VIPGuard, Yin & Jamaluddin 2026) conditions its fusion on beautification. This addendum tests that one rule.
Design (cdfb_gate_probe.py; no training, nothing tuned on Celeb-DF-B):
  b  = the beautified logit of our three-way model, recovered from the saved three-way probabilities of scores_v3/RU-clipe5.npz
       as p_beautified / (p_real + p_beautified) (= sigma(z_b) by the model's factorisation); this is the model's own estimate
       of "how beautified is this face", available at test time without any reference.
  w  = quantile of b among the untreated genuine frames (real folder), clipped to [0, 1]; no free parameter.
  q_tex, q_id = quantiles of the texture score and of the identity distance among the untreated genuine frames (as in Add. 62).
  gate score   = w * q_id + (1 - w) * q_tex.                                       (soft, beautification-aware)
  Comparators: the texture detector alone, identity alone, the Add. 62 fixed fusion (w = 0.5), the Add. 62 hard gate.
  Pairs: Effort, Forensics Adapter, GenD, ours (clipe5 s1) each + identity. Rule, folders, CIs, matched-FA reading: as Add. 62.
Predictions written now:
(1) For all four pairs the beautification-only accusation rise is at most 10 points and the beautification-only miss rise at
    most 5 points (the bar the fixed fusion failed on Effort).
(2) For all four pairs the untreated video AUC of the gate is at least that of the texture detector alone, and the beautified
    video AUC is at least 0.98 (identity alone: 1.000).
(3) At the threshold matched to 5 % FA on beautified genuine frames, the gate misses at most 15 % of beautified forgeries for
    all four pairs (texture alone: 46-72 %).
(4) The gate is not identity alone: on untreated frames its miss rate at the 5 % FPR threshold differs from identity's by more
    than the bootstrap interval half-width, OR its score correlates with the texture score at Spearman > 0.5 on untreated
    forgeries. (A gate that collapses onto identity has no content beyond Add. 62.)
Reading rules: (1)-(3) pass and (4) holds -> a method paragraph: "beautification-aware reference gate", with the reference
requirement and the reenactment blind spot as limits, and the planned Add. 64 test on a mixed population (swaps + reenactment,
untreated + smoothed) as the condition for calling it a method in the paper. Any of (1)-(3) fails -> reported as a negative
result beside Add. 62; no method claim. (4) fails -> the gate is identity in disguise; no method claim.
Readout (2026-10-28 13:20 TST, CDFB_GATE.md): (1) FAIL on all four pairs: the beautification-only accusation rises by +11.5 to
+17.1 points (the weight rises on beautified genuine faces too, and identity's own operating point moves), while the miss falls
(-5.4 to -10.4); (2) FAIL: beautified vAUC 0.968-0.987 (bar 0.98 met only by ours); (3) FAIL by one pair (Effort 15.3 > 15; the
other three 10.1-14.4); (4) PASS (Spearman 0.90-0.93 with texture on untreated forgeries; not identity in disguise). Reading rule:
negative result beside Add. 62; no method claim. The soft gate is the fifth closure of the same bound: conditioning the fusion on
the beautification estimate moves the error from misses to false alarms, because the estimate rises on beautified genuine faces
exactly as on beautified forgeries. KILLED.


### Addendum 64 (2026-10-28 13:40 TST, written before any pulse trace is extracted): a reference-free channel that beautification may leave, remote photoplethysmography
Why: every texture channel loses its separation under skin smoothing (Add. 38-63); identity keeps it but needs a reference and
is blind to reenactment. Skin smoothing is a spatial operation on texture; the remote pulse signal (rPPG) is a temporal change of
the mean skin colour over a region, which a bilateral or guided filter preserves by construction (it averages within the region;
it does not alter the region mean's time course). Prior work reads rPPG as deepfake evidence (Ciftci et al. FakeCatcher 2020;
Qi et al. DeepRhythm 2020; Hernandez-Ortega et al. DeepFakesON-Phys 2020) but none measured it under beautification; it needs
no reference and is not identity-based, so it could cover reenactment too. This addendum asks only whether the channel survives
beautification; no detector is trained.
Design (cdfb_rppg_probe.py, zero training): the 1,392 Celeb-DF-B videos (30 fps), frames 0-299 (10 s) of each; MediaPipe
FaceLandmarker per frame; ROI = left cheek + right cheek + forehead polygons from fixed landmark indices; per-frame mean RGB of
the ROI; POS (Wang et al. 2017, 1.6-s windows, overlap-add), band-pass 0.7-3 Hz; score = pulse-band SNR (power within +-0.1 Hz
of the spectral peak over the remaining power in 0.7-3 Hz, in dB), the standard rPPG quality measure; higher = more genuine, so
the forgery score is -SNR. Rule, folders, 5 % FPR threshold on untreated genuine, compression control, video bootstrap: as Add. 62
(the unit is the video; one score per video). Videos in which the landmarker fails on more than 10 % of frames are dropped and
counted.
Predictions written now:
(1) Untreated video AUC (real vs synthesis) of -SNR is at least 0.70. Kill: below 0.60 -> the channel is too weak on this
    data to be worth anything; the line closes with one sentence.
(2) The beautification-only AUC change (beautified-pair AUC minus compressed-pair AUC) is at least -0.05: the presets do not
    erase the pulse signal. Kill: below -0.10.
(3) At the untreated 5 % FPR threshold, the beautification-only miss rise is at most 5 points and the beautification-only
    accusation rise at most 5 points (the texture detectors: miss +3 to +22; identity: accusation +8.5).
(4) The channel is complementary to texture: Spearman between -SNR and Effort's score on untreated forgeries is below 0.3.
Reading rules: (1) and (2) pass -> rPPG is reported as a second channel that beautification leaves, reference-free, and the
fusion rPPG + texture becomes the next pre-registered method candidate (Add. 65) with the same bars as Add. 63 (1)-(3) plus a
reenactment population. (1) passes and (2) fails -> smoothing erases the pulse too; closure number six. (1) fails -> rPPG is
too weak here (expected for compressed, re-encoded video); one sentence in the limitations, no further work on it.
Readout (2026-10-29 01:00 TST, CDFB_RPPG.md): (1) FAIL and KILL: untreated video AUC of -SNR is 0.514 (bar 0.70, kill below
0.60); median SNR -4.1 dB on genuine and -4.0 dB on swaps. (2) PASS (beauty-only dAUC +0.029), (3) PASS (dFA -2.5, dMISS -1.1,
both CIs cover 0), (4) PASS (Spearman -0.02 with Effort); the three passes are moot because the channel has no separation to
lose. Diagnostics: the pulse is recovered (76.5 % of genuine peaks at 54-102 bpm against 34.8 % for a uniform peak) and the swaps
inherit it from the driving video (peak agreement with the source video 43.9 % against 18.7 % for shuffled partners), so the
pulse SNR is not forgery evidence on Celeb-DF; the published rPPG detectors learn spatial inconsistency of the pulse and all
train. Reading rule: (1) fails -> one sentence in the limitations, no further work on rPPG. KILLED. Sixth closure; the second
reference-free channel tried after texture.

## Addendum 67 (2026-10-29, written before any re-synthesised frame is used in training): decoder re-synthesis as a pseudo-forgery

Ideation: Agent4Sci-style harness, literature review of 2026-10-29 (`../refcond_20261029/LIT_20261029.md`). Readings this
addendum rests on: (1) the main model loses DF40 reenactment (video AUC 0.718 / 0.502, FF++ / Celeb-DF domain; reenactment
frames called real 49-51 %, beautified 21-33 %), and the loss follows smoothing exposure (2026-10-13 entries); (2) DF40's
reenactment generators render every pixel at about 256 px with no blending boundary (DF40 appendix, "resolution gap"), so
nothing in our forged items (self-blends, observed FF++ swaps, part edits) shows the model a face that is decoder-rendered
everywhere, while the beautified items teach that a smooth, warped face is not forged; (3) Rajan et al. (ICLR 2025, "aligned
datasets") label autoencoder reconstructions of real images as fake so that a detector learns decoder traces with content and
size fixed. Their evidence is latent-diffusion images, not reenactment: untested here.

**Change.** With probability 0.25 the forged item of a training step is the FLUX.1-VAE reconstruction of that step's own base
frame (`resynth_precompute.py`, stored losslessly at the base frame's size; same geometry, so the genuine and forged items are a
pixel-aligned pair, as in GenD's paired sampling), beautified on top with probability 0.5 like a self-blend (so both classes still
receive beautified views; Finding 3). Everything else is the paper's recipe (`train_ru5.py --resynth 0.25`). The FLUX VAE is used
because no DF40, Celeb-DF or FF++ generator decodes with it; the SD VAE decodes several DF40 entire-face-synthesis methods and would
inflate those rows.

**Arms.** A: three-way recipe + re-synthesis, seed 20260929 (`clipe5R25`, Ubuntu). B: forged-head-only control + re-synthesis
(`--binary --resynth 0.25`, `clipe5bR25`, local GPU). Comparators: `clipe5_s20260929` and `clipe5b_s20260929`, the same recipe
without re-synthesis. Checkpoint chosen on validation data only by C2 (Addendum 5), as for every arm; DF40, Celeb-DF-B and the
commercial pairs are read once, after selection.

**Primary endpoint.** DF40 reenactment video AUC (mean over the 12 methods, `../df40_eval_20261012`), FF++ and Celeb-DF
domains, arm minus its comparator, paired bootstrap as in df40_eval.
R1: gain >= +0.10 in both domains with the interval above 0, for A or B.
R2 (costs, all must hold for the arm that passes R1): Smoothing-90 accused at the 5 % threshold <= comparator + 5 points;
Celeb-DF-B AUC under the presets >= comparator - 0.02; untreated Celeb-DF-v2 and DFD video AUC >= comparator - 0.01; DF40 face
swap >= comparator - 0.02.
Kill: gain < +0.05 in the Celeb-DF domain for both arms closes re-synthesis.
Reported regardless: DF40 entire-face synthesis (with the note that FLUX is not their decoder), the predicted-class table on
reenactment frames (`diag3way.py`), and the FFHQ-originals-called-beautified rate.
A second seed only if R1 and R2 pass.

## Addendum 70 (2026-10-29 evening, written before training): a browser model trained with the recipe the capstone claims
Audit finding (2026-10-29, `celebdfb_v2_20260927/fair_cdfb.json`): the browser default model `ru4e_effb4_s20260929`
(RU4 recipe, beautification on genuine faces only) has a Celeb-DF-B beautification-only miss rise of +23.9 [20.2, 27.7]
points, above every one of the 17 published detectors (largest: SBI +21.8), and calls 40.3 % of untreated Celeb-DF-B
genuine frames fake; the main model clipe5 has +6.7 / +8.4 and 16.0 / 19.3 %. The capstone report states that the system is
built on the both-class recipe, and the page runs a model trained without it. This is a deployment fix, not a research claim:
nothing from it enters the paper.
Model: tag `ru7we_effb4_s20260929`. Data and targets of arm W (Addendum 58: clipe5 recipe, RUData7 with p_ar = 0, FairFace
train originals as additional genuine bases; factorised forged / beautified heads, presence, quantities, evidence map);
backbone, input size (380), normalisation, optimiser (SAM, lr schedule) and 12 epochs of the current browser model
`ru4e_effb4` (train_ru3.py), so that the two browser candidates differ in the training recipe only. Script
`train_ru7w_small.py`, gsplat-ubuntu, every epoch saved; the epoch is chosen by C2 on validation only (select_epoch logic,
Addendum 5). One seed.
Acceptance gate (read once on the chosen epoch; all must hold to replace ru4e_effb4 as the browser default):
G1 Celeb-DF-B beautification-only miss rise <= +11.0 points (Effort, fair_cdfb.json) - the reason for the change.
G2 FairFace validation originals called real >= 70 % (eval_fairbeauty_pairs; the Addendum 58 bar).
G3 Alibaba Smoothing-90 called fake (native rule) <= 2 %, and accused at the 5 % FPR threshold on originals <= 15 %.
G4 guardrails against ru4e_effb4: Celeb-DF-v2 frame AUC >= 0.8275 and DFD >= 0.8952 (ru4e - 0.02); FF++ false alarm
   <= 13.7 % (ru4e + 2).
G5 the evidence head: on the held-out part-level forgeries, restoring the named region removes >= 80 % of detections.
If any fails: ru4e_effb4 stays, the page and the report state its escape rate, and no variant is trained to pass the gate
(Celeb-DF-B and Alibaba are not used for selection or retraining).

### Addendum 67 readout (2026-10-30, seed 20260929; `readout67.py`, `readout67.log`) — KILLED

Both arms fail R1 (DF40 reenactment AUC rises by >= 0.02 with the 95 % paired interval above 0). The pseudo-forgery
makes the target gap worse, not better: arm A (clipe5R25 vs clipe5) DF40 reenactment AUC 0.7179 -> 0.6565 on the FF++
genuine set, diff -0.061 [-0.073, -0.050]; on the CDF genuine set 0.502 -> 0.471, diff -0.031 [-0.040, -0.021].
Arm B (clipe5bR25 vs clipe5b, binary) 0.8419 -> 0.6867, diff -0.155 [-0.168, -0.142]; CDF 0.6466 -> 0.6279.
Face-swap AUC also falls (A: 0.9515 -> 0.9291 FF, 0.9053 -> 0.8836 CDF; B: 0.9686 -> 0.9255 FF). Video-level
Celeb-DF-v2 AUC A 0.9468 -> 0.9364, diff -0.010 [-0.021, -0.0003]; B -0.006 [-0.018, +0.006]. Celeb-DF-B
beautification-only miss rise A 6.66 -> 8.41 points, B 6.99 -> 11.16. The one movement in the intended direction is
Smoothing-90 accusation (A 8.6 -> 3.2 %, B 9.1 -> 3.8 %), which R1 does not score and which comes with a worse escape.
R2 (DFD) was not computed: the kill rule (R1 fails in both arms) applies before it, so `dfd_v3_eval.py` was not run.

Reading. The idea failed, not the engineering: 48,527 re-synthesised frames were produced, both arms trained to
completion and every metric came from the registered scripts. A FLUX-VAE round trip labelled "forged" teaches the
model a decoder texture that DF40 reenactment frames do not carry (their AUC falls, so the added positives dilute the
real forgery signal rather than add to it), and the same dilution costs 2-4 points on face swaps. The only fair
variant, a VAE closer to the DF40 generators, is the SD VAE that several DF40 whole-face methods decode with, so it
would measure leakage rather than generalisation; no variant is registered. The line is closed; no second seed.

### Addendum 70 readout (2026-10-30; `readout70.py`, `readout70.json`, `readout70.log`) — gate FAILED on G1

Selected epoch 11 of 12 by C2 on validation (`select_ru7we_effb4_s20260929.json`, run on gsplat-ubuntu after the local
run stalled at 2 epochs in 6.5 h; epochs 1-3 matched the local values to the third decimal). Gate, W model vs the
shipped ru4e:
- G1 Celeb-DF-B beautification-only miss rise +19.1 [16.2, 22.1] (bar <= +11.0): FAIL. ru4e +23.9 [20.2, 27.7]; the
  intervals overlap, so W is not shown to be better on G1.
- G2 FairFace validation originals called real 95.7 % (bar >= 70): PASS. ru4e 23.2 %.
- G3 Smoothing-90 argmax fake 0.95 %, accused at 5 % FPR 7.3 % (bars <= 2 / <= 15): PASS. ru4e 0.41 / 6.3 %.
- G4 CDFv2 frame AUC 0.849, DFD 0.917, FF++ false alarm 7.1 % (bars 0.8275 / 0.8952 / 13.7): PASS.
- G5 restoration 91.5 % (donor 92.1, SD-1.5 91.2, SDXL 91.1; ceilings 91.3-92.0; bar >= 80): PASS. ru4e 87.4 %.
FF++ test recall real / forged / beautified 81.7 / 91.6 / 81.2; Alibaba originals real 82.7 %.
Pre-declared consequence: ru4e stays the page model and no variant is trained to pass G1. The readout script first
reported G5 as missing because it looked for a key "head" instead of "evidence"; fixed and re-run, no number changed.
Reading: adding FairFace originals fixes the browser model's out-of-distribution genuine photographs (23 -> 96 %) at
no cost elsewhere, but the EfficientNet-B4 student still lets beautified deepfakes through about twice as often as
the CLIP model (+19 vs +7 to +8 points); the symmetric recipe does not transfer its escape result to the small
backbone. Whether to deviate and ship W anyway is the user's product decision, recorded here when made.

### Addendum 70 deviation (2026-10-30, user decision)

The gate failed on G1, so the pre-declared consequence was to keep ru4e. The user chose to ship W anyway, recorded here
as a deviation from the pre-declared rule. Reason: W is no worse than ru4e on any gate item and much better on ordinary
photographs. ru4e on the FairFace validation originals (measured 2026-10-30 for this decision, `eval_fairbeauty_pairs.json`,
first measurement for ru4e): real 29.2 %, fake 35.8 %, beautified 35.0 %; W: real 95.7 %, fake 0.8 %, beautified 3.5 %.
(Correction: in the first message to the user the 23.2 % in the report table was attributed to ru4e; it is the CLIP model.)
The report states that the gate failed on G1, that the G1 intervals of W and ru4e overlap, and that W is shipped by
decision. ONNX: docs/demo_ru/models/ru7we_effb4.onnx (66.97 MB, sha256 3346379f..., 50/50 decision and named-part
agreement with PyTorch, max |d out| 3.8e-4); ru4e_effb4.onnx kept for rollback. Page tests after the swap: T2 sentences
50/50, JS masks 50/50, evidence path 19/20 (the one difference is a rounding boundary: nose mean evidence 0.995 shown as
1.00 by the browser and 0.99 by Python; decision and named part agree on 20/20).
