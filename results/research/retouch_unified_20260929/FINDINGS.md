# RU-20260929 — findings

## RU1-EffB4 (seed 20260929; FF++ c23 + FFHQ Part7 originals + Tencent/Megvii four-op composites + parametric single-op filters)

Training: 12 epochs × 22.3 min on the Ubuntu box; best epoch 12 (FF++ val macro-F1 0.864, vendor-val F1 0.991, vendor-val →fake 0.1 %).

### Bars (PRE_DECLARED §4)
| bar | value | verdict |
|---|---|---|
| R1 Alibaba balanced ≥ 75 % | 66.1 % | FAIL |
| R2 TP ≥ Table 7 on ≥3/4 ops, original TN ≥ .80 | TP eye .248 / lift .089 / white .095 / smooth .928 (Table 7: .519/.548/.501/.861); original TN .96–.99 | FAIL (1/4) |
| R3 retouched → fake ≤ 5 % pooled, ≤ 10 % per cell | 0.63 % pooled, max 1.0 % | **PASS** |
| R4 Spearman ≥ .6 all four | smooth .683, eye .457, lift .097, white −.078 | FAIL |
| D1 CDFv2 ≥ .78 / DFD ≥ .88 / Celeb-DF-B ≥ .85 / escape Δ in ±3 / B1 0/13 | .826 / .929 / .904 / +1.5 [−0.5, 3.5] / 0 of 13 | **PASS** |
| D2 FF++ recall ≥ 80 % per class; held-out-11 excess ≥ 30 pp | real 78.0 / fake 93.3 / filter 80.7; excess 32.9 | FAIL (real by 2.0 pp) |

### Alibaba (blind, never trained)
Originals: real 93.4 %, fake 0.8 %, filter 5.8 % (FF++-only models: real 0.8–36.8 %, fake up to 55.9 %).
Retouched → fake 0.63 % (FF++-only models: 6.4–59.4 %, smoothing-90 up to 85.8 %).
Paired rank 92.8 % (FF++-only best 79.8 %): eye 98.5–99.1, lift 88.6–95.4, white 77.0–84.6, smooth 98.9–99.95.
Absolute routing to *filter*: smooth 82–99.6 %, eye 16–46 %, lift 10–14 %, white 10–22 %.

### Deepfake side (same frames as every other detector)
| | CDFv2 frame | CDFv2 video | DFD frame | DFD video |
|---|---|---|---|---|
| official SBI | 0.817 | 0.872 | 0.918 | 0.876 |
| RU1-EffB4 | 0.826 | 0.874 | 0.929 | **0.906** |
| RU1 − SBI, paired video-cluster bootstrap 95 % CI | [−0.023, +0.039] | [−0.025, +0.029] | [−0.011, +0.034] | **[+0.007, +0.051]** |
CDFv2 genuine → fake 23.7 % (MASK 63.5 %); DFD 8.6 % (MASK 44.1 %).
Celeb-DF-B: untreated AUC 0.904 (SBI 0.875, MASK-D 0.894); untreated genuine → fake 21.2 %, beautified 12.6 %; escape 6.6 → 8.1 %
(ΔMISS +1.5 [−0.5, 3.5]); per preset ΔMISS brown −1.8, california_dreamin +8.5, hawaii_grain −4.0, relax_you_pretty +3.1.

Note: a first run of compare_sbi.py loaded `cdfstd_sbi.npz` (v1 frame list, same length) instead of `cdfstd_v2_sbi.npz` and
showed SBI at 0.8265 / 0.9028; fixed before any number was used. Paper tables always used the v2 scores.

### Reading
Vendor supervision fixes the two failures of the FF++ line on commercial retouching: untouched photographs are recognised
as real and commercially smoothed faces are no longer accused. It also makes the deepfake side better, not worse: RU1 ties
the official SBI on CDFv2 and beats it on DFD at video level, and has the best untreated Celeb-DF-B AUC of every model.
What it does not do is call single commercial operations *filter* in absolute terms, except smoothing. Diagnosis and the
RU2 design are in PRE_DECLARED Addendum 1 (composite-only vendor data → co-occurrence; synthetic ops far stronger than
the training vendors).

### In-vendor held-out check (Tencent/Megvii validation bases, never trained; `eval_vendor_val.py`)
Originals → real 94.98 %; composites → filter Tencent 100.0 % / Megvii 99.62 %; single-op components → filter 37.07 %.

| component | n | → filter | TP (op present) | same-image TN | Spearman q |
|---|---|---|---|---|---|
| tencent_eye | 795 | 62.26 | 0.394 | 0.794 | 0.397 |
| megvii_eye | 1317 | 28.7 | 0.069 | 0.809 | 0.178 |
| tencent_jaw | 795 | 4.15 | 0.039 | 0.945 | -0.02 |
| megvii_jaw | 1316 | 6.61 | 0.058 | 0.932 | 0.063 |
| tencent_white | 796 | 8.04 | 0.034 | 0.964 | 0.011 |
| megvii_white | 1315 | 5.7 | 0.02 | 0.954 | 0.06 |
| tencent_smooth | 792 | 95.08 | 0.944 | 0.033 | 0.383 |
| megvii_smooth | 1317 | 94.53 | 0.935 | 0.055 | 0.464 |

Reading: even on the training vendors, RU1 recognises a single operation only when it is smoothing (94–95 % → filter);
a Tencent whitening component with ΔL ≈ 20 is called *real* 90 % of the time. The single-operation failure on Alibaba is
therefore not a vendor gap: with four operations always co-occurring, texture loss alone separates the class and the
other three are never learnt. This is the RU2 hypothesis, measured before RU2 finishes.

## RU2-EffB4 (seed 20260929; + vendor single-op components, light parametric strengths; PRE_DECLARED Addendum 1)

| bar | RU1 | RU2 s1 | verdict (RU2) |
|---|---|---|---|
| R1 Alibaba balanced ≥ 75 % | 66.1 | **72.7** | FAIL (−2.3 pp) |
| R2 TP ≥ Table 7 on ≥3/4, orig TN ≥ .80 | eye .25 / lift .09 / white .10 / smooth .93 | eye .23 / lift .25 / white .20 / smooth .95; orig TN .97–.99 | FAIL (1/4) |
| R3 retouched → fake ≤ 5 / ≤ 10 per cell | 0.63 / 1.0 | 0.32 / 0.54 | **PASS** |
| R4 Spearman ≥ .6 all | .46 / .10 / −.08 / .68 | .43 / .16 / −.17 / .47 | FAIL |
| D1 CDFv2 / DFD / Celeb-DF-B / escape Δ / B1 | .826 / .929 / .904 / +1.5 / 0 | .822 / **.938** / .902 / +2.3 [0.2, 4.5] / – | CDFv2, DFD, Celeb pass; escape Δ within ±3 |
| D2 FF++ per class ≥ 80; held-out excess ≥ 30 | 78.0/93.3/80.7; 32.9 | 79.4/93.6/75.8; 31.2 | FAIL (real −0.6, filter −4.2) |

Alibaba absolute routing to *filter* (RU1 → RU2): eye 16–46 → **53–74 %**, lift 10–14 → **46–59 %**, white 10–22 → **49–67 %**,
smooth 82–100 → 97–100 %; originals → filter 5.8 → 22.8 % (real 93.4 → 76.8 %). Paired rank 92.8 → 94.2 %.
DFD vs SBI now significant at frame level too: frame 0.938 vs 0.918, CI [+0.0004, +0.042]; video 0.913 vs 0.876, CI [+0.014, +0.062].
CDFv2 tie (0.822 / 0.868 vs 0.817 / 0.872). Celeb-DF-B untreated genuine → fake 25.2 %.

Reading: single-operation vendor components do what the diagnosis predicted for the class head: eye enlargement, lifting and
whitening are now routed to *filter* 3–5× more often on an unseen vendor. The price is specificity on untouched photographs
(22.8 % called filter), so balanced accuracy rises 6.6 pp but stops 2.3 pp short of the bar. The presence and quantity heads
did not follow the class head: per-op TP stays at .20–.25 and the blind quantities do not rank the Alibaba edit except for
eye width and smoothing (ρ ≈ .43–.47).

## RU2 seed 2 and the secondary threshold analysis (Addendum 2)
RU2 s2: Alibaba balanced 70.9 % (s1 72.7), originals → real 66.6 %, retouched → fake 0.25 %, paired rank 94.3 %; eye 61–80 %,
lift 56–67 %, white 59–75 %, smooth 99–100 % routed to filter. FF++ 80.4 / 92.9 / 76.1; CDFv2 0.817; DFD 0.934 (video 0.914,
vs SBI CI [+0.016, +0.062]); Celeb-DF-B 0.899, untreated genuine → fake 22.6 %, ΔMISS +2.8 [0.4, 4.9].
In-vendor (held-out Tencent/Megvii bases): single-op presence TP eye .75–.84, lift .69–.86 (RU1 .04–.39); originals → real
73.4 / 63.5 % (RU1 95.0); quantity ρ −.02 to .41 in-vendor ⇒ the quantity head fails before any vendor shift.
Vendor-val threshold applied to Alibaba (secondary): balanced RU1 67.8, RU2 s1 71.8, RU2 s2 69.6 — all < 75. Threshold-free
AUROC of p(filter), originals vs retouched: 0.749 / 0.800 / 0.796.

## Verdict of the RU line (2026-09-29)
Alibaba has now scored four models; it is closed for design decisions. What stands, both RU2 seeds: commercial retouching is
no longer accused (0.25–0.32 % vs up to 86 % for FF++-only models), retouched-vs-untouched balanced accuracy 71–73 % (FF++-only
48–55 %), AUROC 0.80, and the forgery side improves (DFD video AUC above official SBI for RU1 and both RU2 seeds; CDFv2 tie;
Celeb-DF-B 0.90). What fails: the 75 % bar (by 2–4 pp, also with a vendor-val threshold) and the verifiable-quantity head
(R4, both seeds; weak even in-vendor). Headline model: RU2 (pre-registered improvement arm, two seeds); RU1 is its ablation.

## RU2-RepViT (edge, seed 20260929)
Alibaba balanced 64.0 % (RU1-RepViT 65.1), originals -> filter 55.7 % (RU1-RepViT 5.9), retouched -> fake 0.52 %, paired rank 95.1 %;
FF++ 79.3 / 87.5 / 63.6; CDFv2 0.772; DFD 0.892; Celeb-DF-B 0.872. TFLite: 18.06 MB, G1-G4 pass, 200/200 decisions, 11.7 ms / image
(1 thread). The single-operation components cost the 4.7 M model most of its specificity; RU1-RepViT stays the edge model and the
browser demo (docs/demo_ru) was set back to RU1-RepViT after the automatic swap.

## RU-CLIP-E seed 1 (frozen CLIP ViT-L/14 + LoRA r16 + three heads + evidence head, RU3 data; Addendum 3)
Trainable 3.16 M of 306.3 M; 8 epochs x 22 min; best epoch 7 (FF++ val F1 0.891, vendor-val F1 0.943, originals -> real 75.4 %).
| bar | value | verdict |
|---|---|---|
| C1 CDFv2 frame >= Effort-on-our-frames - 0.01 = 0.871 | 0.878 (video 0.931; Effort 0.881 / 0.930, FA 0.887 / 0.945) | PASS |
| C2 Celeb-DF-B escape delta <= +3 pp | +2.6 [0.3, 5.1] | PASS (point estimate; CI reaches 5.1) |
| C3 Alibaba retouched -> fake <= 5 % | 0.18 % | PASS |
| C4 / R1 Alibaba balanced >= 75 % | 74.59 % | FAIL by 0.41 pp |
| D1 DFD / Celeb-DF-B | 0.957 frame, 0.981 video (Effort 0.935/0.957, FA 0.942/0.959); Celeb-DF-B 0.929 (SOTA 0.909) | PASS, above both SOTA |
| D2 FF++ per class >= 80 | real 76.7 / fake 94.6 / filter 87.9 | FAIL (real) |
| B1 | dominated by none of 15 | PASS |
vs SBI paired CI: CDFv2 frame [+0.034, +0.091], video [+0.034, +0.085]; DFD frame [+0.019, +0.064], video [+0.071, +0.136].
Untreated Celeb-DF-B genuine -> fake 15.4 %; CDFv2 genuine -> fake 17.0 %; DFD 2.6 %. Held-out-11 paired excess 41.8 pp.
Seed 2 (20260930) launched 22:45.
Evidence head of RU-CLIP-E on held-out part edits (eval_cgd_explain, RUCLIPE): detect rate donor 55.9 % / SD 17.7 % / SDXL 26.0 %
(MASK ~80 / 60 / 65), IoU7 0.48 / 0.38 / 0.45, flip 78.8 / 53.9 / 68.9 vs ceilings 89.4 / 69.1 / 78.3, complement 2.5 / 14.4 / 8.4.
E1 FAIL: expected, the RU pool contains no part-level edits (MASK trained on 61.5k of them); the head is supervised on
filters, self-blends and vendor components. On filters it is strong: restoring its region drops p_filter by 0.79 (E5).
Consequence: a truly unified final model needs the part edits in the RU pool (RU4 = RU3-E + part edits), to be launched once
a GPU frees up.

## RU-CLIP-E seed 2 (20260930): reproduces
CDFv2 0.883 frame / 0.942 video (>= Effort 0.881/0.930; FA 0.887/0.945); DFD 0.953 / 0.971; Celeb-DF-B 0.928, untreated genuine -> fake
8.9 %, escape delta +1.4 [-1.2, 4.2]; Alibaba balanced 73.4 % (R1 FAIL), retouched -> fake 0.2 %; FF++ 87.2 / 92.2 / 86.9 (D2 PASS);
held-out-11 excess 54.4 pp; B1 0/15. Two-seed ranges: CDFv2 0.878-0.883, DFD 0.953-0.957, Celeb-DF-B 0.928-0.929, escape +1.4..+2.6.

## RU3 / RU3-E (EffB4, component cleaning; RU3-E adds the evidence head) — 2026-09-30
RU3-E: Alibaba balanced 73.0 % (R1 FAIL), originals -> real 83.2 % (RU2 66-77 %), retouched -> fake 0.49 %, paired rank 94.1 %;
CDFv2 0.824 / 0.874, DFD 0.930 / 0.915; FF++ 79.9 / 94.0 / 76.4; held-out excess 29.5. Evidence head on part edits: IoU7 0.28-0.42,
flip 40-61 % vs ceilings 64-82 % (E1 FAIL, no part edits in the pool -> RU4). Cleaning restored specificity but the sensitivity
on single operations dropped in proportion; balanced accuracy did not move. RU3 (no head): Alibaba balanced 72.92 % (R1 FAIL), originals -> real 76.65 %, retouched -> fake 0.34 %, paired rank 94.9 %;
FF++ 79.8 / 93.7 / 74.9, FA 10.4, MISS 0.6; CDFv2 0.832 / video 0.878, DFD 0.938 / video 0.918 (vs SBI 0.876, paired CI [+0.021, +0.064]);
Celeb-DF-B untreated AUC 0.906, escape +3.9 pp, FA -11.4 pp; held-out excess 30.4 (D2 pass). Vendor-val (RU3-E): originals -> real 82.5 %,
components -> filter 85.9 %, TP eye .84/.74 jaw .75/.92 white .75/.46 smooth .99/.96 (tencent/megvii); Spearman 0.10-0.46 (R4 FAIL).
Reading: cleaning the component pool moves specificity on untouched originals (RU2 66-77 -> RU3-E 83 %) at no cost on forgery detection,
but Alibaba balanced accuracy stays at 73 % in every EffB4 arm (RU2 72.7, RU3 72.9, RU3-E 73.0): the residual is single-operation
sensitivity at the light strengths Alibaba uses, not specificity. Three EffB4 arms and two CLIP seeds all land in 72.7-74.6 %.
Bug fixed on the way: `eval_vendor_val.py` loaded RUNet3 checkpoints into RUNet (unexpected `ev.*` keys); it now wraps RUNet3.

## RU4 + CLIP-L/14 LoRA (clipe4, seed 20260929): the unified model — 2026-09-30
Data = RU3-E pool + 61,510 FF++ train part-level edits with exact footprints (fake draw: self-blend 0.4 / observed 0.3 / part 0.3).
**E1 PASS** on held-out part edits (eval_cgd_explain, detected items): donor IoU7 0.832, flip 91.7 % (ceiling 91.9); SD 0.845 / 91.5 %
(91.6); SDXL 0.827 / 90.9 % (91.2). Complement flip 0.1-0.5 %, random 11-15 %, centre prior 42-52 %. Filter restoration E5 0.81.
RU3-E CLIP without part edits was 0.38-0.48 / 54-79 %, so the head learned the footprint from the training part edits and it
transfers to the held-out SD / SDXL / donor mechanisms.
Detection: CDFv2 0.888 frame / 0.954 video, DFD 0.948 / 0.983 (paired vs official SBI: CDFv2 video [+0.059, +0.105], DFD video
[+0.074, +0.139]); top of the video-level table (Forensics Adapter 0.887 / 0.945 / 0.942 / 0.959, Effort 0.881 / 0.930 / 0.935 / 0.957).
FF++ 78.0 / 88.9 / 89.2 (D2 fail on real and fake), FA 3.95 (lowest of any RU arm), MISS 0.62, held-out filter excess +51.5.
Alibaba (one read): balanced **70.2 %** (R1 FAIL, RU3 CLIP 74.6 / 73.4): retouched -> filter 82.3 % (up from 71.4), originals -> real
57.9 % (down from 77.4); per level 30/60/90: eye 70/79/85, jaw 68/75/80, white 72/79/85, smooth 96/100/100; retouched -> fake 0.12 %
(R3 pass). Vendor-val originals -> real 78.7 %, so the specificity loss is specific to the unseen-vendor originals, not to FFHQ
originals in general. Secondary threshold (Addendum 2, t* from vendor-val only) gives 72.4 %; AUROC(p_filter) 0.807, so no
threshold reaches 75 %. Presence-head Eq.4 TP eye .21 / jaw .35 / white .57 / smooth .96 (R2 FAIL; routing recall above Table 7 on
all four ops, presence head below it on three).
Celeb-DF-B (v3 split): untreated AUC 0.937 (best of all models; Effort / Forensics Adapter 0.909), escape 6.83 -> 9.70 % (+2.87 [1.15, 4.84], inside the 3 pp bar: C2 PASS), false accusation 16.9 -> 18.4 % (+1.5, CI includes zero).

## RU4 + evidence head, EfficientNet-B4 (ru4e, seed 20260929) — 2026-09-30 09:21
Same RU4 data as clipe4 on the 17.6 M backbone (12 epochs, Ubuntu). **E1 PASS on the second backbone**: donor IoU7 0.804, flip 87.8 %
(ceiling 87.8); SD 0.820 / 87.4 % (87.6); SDXL 0.812 / 86.9 % (87.2); complement <=0.4 %, random 15-17 %. Detection: CDFv2 0.848
(RU3 0.832), DFD 0.915 (RU3 0.938; real called fake 16.2 %), FF++ 74.2 / 93.3 / 76.4 (D2 fail), FA 11.7, MISS 0.5, held-out excess 32.2.
Alibaba (one read): balanced 72.6 % (R1 FAIL), originals -> real 81.0 %, retouched -> filter 63.8 %, retouched -> fake 0.33 % (R3 pass).
Unlike the CLIP variant, the part edits did not cost specificity on the unseen vendor's originals (81 % vs RU3-E 83 %), and the
balanced accuracy stays where every EffB4 arm sits (72.6-73.0). Celeb-DF-B (v3): untreated AUC 0.899, false accusation 40.3 -> 21.9 % (the head model calls 40 % of untreated Celeb-DF-B genuine
frames fake, cf. RU3-E 26.9 %), escape 3.43 -> 7.27 % (+3.85 [2.22, 5.54], outside the 3 pp band that applies to the CLIP arm).
Video-level: CDFv2 0.910, DFD 0.909 (RU3 0.878 / 0.918). Secondary threshold t* 0.719 from vendor-val: Alibaba 71.7 %
(originals -> filter 6.0 %, retouched -> filter 49.4 %). Reading: on EffB4 the part edits buy CDFv2 (+0.016 frame, +0.032 video)
and the explanation, and cost DFD (-0.023) and genuine-frame specificity on Celeb-DF-B; on CLIP they cost nothing on the
forgery side. The unified CLIP model is the paper's headline model; RU4-E is its small-backbone replicate of the E1 result.

## Correction and paired test against the CLIP-based detectors (2026-09-30 evening)
`compare_sota.py` (paired video-cluster bootstrap, 1,000 resamples, duplicated videos kept as separate clusters):
clipe4 minus SBI excludes zero everywhere (CDFv2 frame [+0.042, +0.100], video [+0.052, +0.115]; DFD frame [+0.006, +0.057],
video [+0.065, +0.151]). clipe4 minus Effort: CDFv2 frame [-0.018, +0.033], video [-0.003, +0.051]; DFD frame [-0.018, +0.039],
video [-0.0001, +0.050]. clipe4 minus Forensics Adapter: CDFv2 frame [-0.022, +0.022], video [-0.012, +0.031]; DFD frame
[-0.028, +0.030], video [-0.005, +0.055]. **The main model is level with Effort and Forensics Adapter, not above them;** the
paper must not say "highest" or "passes". Corrections to earlier entries: FF++ in-domain for clipe4 misses the 80 % bar on
genuine only (78.0); fake is 88.9. Beautified genuine Celeb-DF-B frames routed to filter by clipe4: 36.9 % (not 46 %).
Compression-only control on Celeb-DF-B: clipe4 dMISS_c +3.43 of +2.87 total, so beautification beyond re-encoding is -0.6 pp
(SBI 21.8, Effort 11.0, Forensics Adapter 15.3). Presence head vs RetouchingFFHQ Table 7: above on smoothing (.96 vs .86)
and whitening (.57 vs .50), below on eye (.21 vs .52) and lifting (.35 vs .55).

**Correction (same evening), specificity of clipe4.** `eval_vendor_val.py --arm clipe4`: held-out Tencent/Megvii originals
real 55.5 %, filter 44.4 % (clipe s1/s2 25.1/28.2 % filter; ru3e 17.0 %; ru4e 20.2 %; RU1 4.2 %). The earlier statement
"vendor-val originals -> real 78.7 %, so the specificity loss is specific to the unseen vendor" used the training-log
metric (`orig->real` printed by train_ru_clip.py from ValClip) and is wrong: the loss appears on training-vendor
originals as well. The training-log and eval-script numbers disagree (78.7 vs 55.5 on nominally the same split), so the
checkpoint criterion used a different preprocessing than the evaluation. To investigate (ValClip crop vs eval_ru DS crop);
all reported numbers come from the eval scripts.

## Blur probe for Ours / Ours-lite (2026-09-30, `blur_probe_ru.py`)
Same 300 FF++ test genuine frames and conditions as sbifix/blur_probe.py; % called fake (argmax).
Ours (clipe4): orig 9.7, down2 12.0, blur1.5 14.3, jpeg30 15.7. Ours-lite (ru4e): orig 11.3, down2 15.3, blur1.5 16.7,
jpeg30 26.0. Reference (same frames): official SBI blur1.5 67.3 (thr 0.5), Xception 53.0, EfficientNet-B4 56.7, UCF 42.3,
FF++-only three-way HYB 91-95, HYB-D 10.0. The blur shortcut stays removed in both paper models; Ours-lite has a new
weakness under strong JPEG (26 % of genuine frames called fake at q30, vs 12 % for HYB-D).

## Explanation text: part naming was wrong, map was right (2026-09-30, `eval_part_naming.py`)
Held-out part-level forgeries (every 4th item; 831-924 detected per mechanism), main model clipe4. Naming the edited part
from the evidence map: rule A (share of the top-12 % region on each landmark part; used by cgd explain_json.py and the
supplement's fig_output) names the right part in 11.9 / 7.9 / 8.8 % (donor / SD / SDXL) because the large skin mask
always wins. Rule B (mean evidence inside each part) names it in 99.0 / 98.5 / 97.7 %. Decision rule fixed before the run
(switch only if B beats A on all three) -> rule B. The map was faithful all along; the sentence built from it was not.
The supplement's structured-output figure (fig_output, MASK model, rule A) must be regenerated with rule B.

## Sentence variety of the explanation (2026-09-30, `sentence_stats.py`)
379 fixed test images (100 FF++ genuine, 100 FF++ forgeries, 80 Alibaba renders, 99 part forgeries balanced over
eyes / mouth / nose): 14 distinct sentences. real: 1 sentence (fixed template). fake: 4 (eyes / nose / mouth / whole
face); part forgeries named 29 eyes, 29 mouth, 26 nose; whole-face FF++ forgeries 54 % "whole face", the rest a single
part (not verifiable, no ground truth for whole-face swaps). filter: 9 (combinations of the four operations, or
"operation unclear"); 11 of 80 single-operation Alibaba renders get all four operations named (presence head over-fires).
The per-image structured output (probabilities, four operation scores, per-part evidence, the map) is what varies; the
sentence is a template over it. No language model is used.

