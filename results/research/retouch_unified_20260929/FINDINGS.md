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

## FFHQ still photos with scripted edits: the demo check (2026-09-30, `docs/demo/make_samples.py`)
50 FFHQ faces never used in training (Part2, after the 8 page examples), 512 px, page crop (landmark box + 35 %). Strengths:
upper end of the random_op_v2 training ranges (eye x1.25, slim 0.065, white 0.33, smooth frac 0.08 + blend 0.4). Forgeries:
donor transplant of nose / mouth from the next FFHQ face (partedit donor algorithm). Accuracy, Ours-lite / Ours (clipe4):
genuine 76 / 56 %, eyes 56 / 72, slim 84 / 90, white 96 / 100, smooth 70 / 38 (called FAKE: 11 / 28 of 50), nose 64 / 92,
mouth 38 / 60. Readings: (1) part-forgery detection drops from 98-99 % on FF++ frames to 38-92 % on FFHQ stills, much more
for Ours-lite; (2) the main model's genuine-to-filter problem (42 % on Alibaba originals) shows again (22/50); (3) scripted
smoothing at the corner of the training range is called fake by the main model in 56 % of faces, unlike Alibaba smoothing
(0.1 % retouched -> fake): the scripted bilateral smoothing is more forgery-like than the commercial one. A first version of
the page examples used out-of-range strengths from the old v1 generator (smoothing blend 1.0 -> called fake 0.98); replaced
by the rule above before publishing. Page examples (Ours-lite): 4 of 8 right.


## Train / validation / test accuracy of the two main models (2026-10-01, `split_eval.py` -> `split_eval.json`)
Same preprocessing as every reported test number (`eval_ru.run`). Training rows: random samples (2,000 per row, FF++ fakes
500 per method, 4,000 part-level forgeries, seed 20260930); validation and test: every image. Test FF++ recalls reproduce
the published 77.96 / 88.88 / 89.21 exactly, vendor-val originals reproduce eval_vendor_val (55.51 real / 44.36 filter).

| | Ours train / val / test | Ours-lite train / val / test |
|---|---|---|
| FF++ real | 94.2 / 80.9 / 78.0 | 96.9 / 78.5 / 74.2 |
| FF++ fake | 89.6 / 90.7 / 88.9 | 94.0 / 92.6 / 93.3 |
| FF++ filter | 91.3 / 90.0 / 89.2 | 83.3 / 75.1 / 76.4 |
| FF++ macro-F1 | 91.8 / 87.2 / 82.4 | 91.4 / 81.9 / 81.0 |
| commercial originals -> real (test = Alibaba) | 59.5 / 55.5 / 57.9 | 89.6 / 79.3 / 81.0 |
| commercial renders -> filter | 99.9 / 100.0 / 82.3 | 99.8 / 100.0 / 63.8 |
| cleaned components -> filter | 94.8 / 94.2 / - | 88.7 / 87.9 / - |
| part-level forgeries -> fake | 91.8 / - / 89.3 | 93.8 / - / 92.5 |

**Finding:** Ours keeps only 59.5 % of its *training* FFHQ originals real (40 % -> filter), the same as on validation
(55.5) and the unseen service (57.9). The specificity loss is not a generalisation failure; it is present on training
images. Likely cause to test next: weak single-operation components are near-identical to their originals but labelled
filter. Ours-lite keeps 89.6 % of training originals real.

**78.7 vs 55.5 resolved:** clipe4's checkpoint is epoch 4 of 8 (criterion 0.9107 = meta best); its log at epoch 4 says
originals -> real 57.2 %. 78.7 % is the epoch-8 log line, not the saved model. With the training-validation preprocessing
(cap before resize) the saved checkpoint gives 56.9 % (eval script 55.5 %). ru4e: epoch 12 of 12, 81.3 % vs 79.3 %.

Paper: Table II (data and accuracy per partition), Sec. V-A, supplement Fig. S6 (curves, `make_fig_training.py`) and
Fig. S7 (FF++ confusion matrices); label definitions rewritten by what an edit changes (Sec. III-A, Table I).

## Checkpoint selection defect, and what limits the unseen-service result (2026-10-05)
**1. Selection defect (validation evidence only; PRE_DECLARED Addendum 5).** Every RU arm chose its epoch by
0.5 x (FF++ val macro-F1 + vendor-val F1 of the filter class). Vendor val has 10,579 filter items and 816 originals, so that
F1 barely reacts to originals called filter. For clipe4 the rule picked epoch 4, where originals->real is 57.2 %, against
78-84 % at epochs 3 and 5-8 (filter recall 93.4 % vs 83-90 %; vendor balanced accuracy 75.3 vs 82.7-85.1). Only the selected
epoch was saved. The 41.9 % (Alibaba) / 44.4 % (vendor val) / 40 % (training) originals->filter of the paper's main model are
therefore to a large part an operating point chosen by an insensitive metric. Other arms: the two rules pick epochs with
similar validation behaviour (ru4e e12 vs e11: originals->real 81.1 vs 85.8).
**Action:** re-runs `clipe4r` (same recipe, seeds 20260929 local / 20260930 Ubuntu, every epoch saved), epoch chosen by
`select_epoch.py` with C2 = 0.5 x (FF++ val macro-F1 + vendor-val balanced accuracy); evaluation chain `run_add5_eval.sh`.
Results go below when the runs finish.

**2. Why 70 % and not more (exploratory, post hoc on existing Alibaba scores; `detectability.py` -> `detectability.json`).**
Spread of logit P(filter) across the 2,210 untouched originals: SD 1.38 (Ours), 1.01 (Ours-lite). Mean shift of the same face
after the edit, in units of that SD, with paired rank and AUROC against all originals (Ours):

| operation (levels 30 / 60 / 90) | shift / SD | paired rank % | AUROC |
|---|---|---|---|
| eye enlargement | 0.75 / 1.02 / 1.32 | 94.8 / 97.1 / 98.2 | 0.69 / 0.75 / 0.80 |
| face lifting | 0.79 / 1.03 / 1.29 | 89.1 / 93.2 / 95.3 | 0.68 / 0.73 / 0.78 |
| whitening | 0.96 / 1.39 / 1.88 | 88.9 / 90.6 / 94.0 | 0.72 / 0.77 / 0.84 |
| smoothing | 3.10 / 4.19 / 4.18 | 96.5 / 99.9 / 99.7 | 0.93 / 0.99 / 0.99 |

The edit raises the filter score of its own face in 89-98 % of pairs, but for three of the four operations the rise is about
one standard deviation of the variation between untouched photographs, so a single image cannot be separated from the
population of originals (AUROC = Phi(d'/sqrt 2) predicts 0.70 for d' = 0.75 and 0.82 for 1.3, as measured). Smoothing is 3-4 SD.
The measured edits are small: eye width +1.2 / 2.1 / 3.0 %, jaw width -1.4 / 2.0 / 2.5 % (measurement offset 0.9 %), skin
lightness +1.8 / 4.2 / 6.7 L.
**Not explained by edit size:** detection does not grow with the measured magnitude. Whitening renders in the two highest
lightness quintiles (dL 12 and 29) are sent to filter 52.5 / 63.1 % of the time, the three lowest (dL 0.6-5.4) 90-95 %; renders
with overall |render - original| above 12 levels are detected least (60 %, AUROC 0.63). High-frequency energy falls by 2-3 %
in the low-dL whitening renders and rises by 2-6 % in the high-dL ones, and the smoothing-presence head fires on 74 % of
non-smoothing renders (TN_same_image 0.257), so the three-way decision on this service leans on texture change more than on
tone or geometry. Image statistics of the originals called filter (lightness, high-frequency energy, sharpness, chroma, face
size) do not explain which originals are called filter (AUROC 0.47-0.58). Ours and Ours-lite agree weakly on originals
(Spearman 0.46; both filter 13.0 %, Ours only 28.8 %, lite only 5.6 %).

**3. Re-encoding control (`pipeline_trace_probe.py`, validation originals only).** Every Alibaba render differs from its
original over the whole face (median 3-5 levels even for eye enlargement), so the service leaves a processing trace. A no-op
round trip of the 816 held-out originals does not move them to filter for clipe4: untouched 44.4 % filter; JPEG q95 / q90 /
q75 / q50: 46.2 / 46.8 / 40.7 / 31.2 %; 2x resample 42.9 %; resample + JPEG q90 45.3 %. The filter decision of the main model
is not a re-encoding detector. ru4e: untouched 20.0 % filter; the six round trips 18.0-21.1 %.

## 2026-10-06: RU5 result, and a failure on real Instagram AR filters (`eval_insta.py`, uncontrolled first look)
RU5 seed 20260929: see PRE_DECLARED Addendum 7 (T1 pass, T2 fail at +6.7 pp, per-preset AUC drop unchanged).
**Instagram AR beauty filters (OpenFilter): genuine faces are called fake.** B-LFW (112 px, tight crops): clipe4r 99.4 % fake,
RU5 98.3 % fake. FairBeauty validation (282 px): 92.7 % / 89.7 % fake, 6.3 % / 10.2 % filter. The LFW control on disk
(112 px, different framing, 2,000 images) goes 90-93 % to *filter* and 3-6 % to fake, so low resolution alone does not
explain the fake calls, but the control is not the same crop and FairBeauty has no control on disk: this is NOT yet a
controlled measurement. To do before any claim: FairFace validation originals as the matched control, the same crop for
both, the 13 baselines on the same images at a fixed FPR on the originals. If it holds, AR filters that re-render the
face are outside what the present training covers, and "beautified is not forged" cannot be claimed for them.

## 2026-10-06: Instagram AR beauty filters, controlled (FairBeauty vs its FairFace originals, 2,927 pairs, same extractor)
Share of AR-filtered GENUINE faces called fake at the threshold of 5 % FPR on the untouched originals (score P(fake)):
SPSL 10.7, EffNet-B4 22.0, SBI 22.8, Xception 24.3, CORE 25.2, F3Net 26.1, SRM 26.8, UCF 37.3, RECCE 41.5, UnivFD 63.3,
Forensics Adapter 63.9, Effort 67.7, NPR 70.4, **RU5 75.1, clipe4r 78.4**. AUC of P(fake) originals vs filtered: Effort
0.905, Forensics Adapter 0.877, ours 0.945. Our models are the most affected of all fifteen; the stronger a detector is
on cross-dataset forgery detection, the more it accuses AR-filtered faces. Native argmax: RU5 calls 93.1 % of filtered
faces fake and 6.7 % filter; 26.1 % of the untouched FairFace originals are called fake as well. Files:
`eval_fairbeauty_pairs.json`, `fairbeauty_baselines.json`. Single run, no intervals yet. FairBeauty validation and B-LFW
stay test-only; AR filters are not covered by any training source of the RU line.

## 2026-10-06 17:55: equal-data binary control (Addendum 9) — the filter class does not help forgery detection
clipe5b (RU5 data and mixture, one forged logit, no beautified / presence / evidence supervision; epoch 4 by FF++ val AUC),
one rule for all on Celeb-DF-B: AUC untreated 0.949, beautified 0.896 [0.874, 0.915], beauty-only rise in MISS +7.0 pp
[4.7, 9.0], FA beautified genuine 7.4 %; CDFv2 frame AUC 0.914, DFD 0.967. RU5 with all heads: 0.866 / 0.883 beautified
(two seeds), +6.7 / +8.4 pp, CDFv2 0.891 / 0.887, DFD 0.956 / 0.954. The binary control is at least as good on every
forgery-detection number, so per Addendum 9 the gain over clipe4r is attributed to the beautification-aware training data
(random colour grading on genuine and forged faces), not to the filter class or the heads. Ablations (Addendum 10) agree:
removing the colour grading returns the escape to +14.4 pp. What the heads add is the second output (beautified or not),
the operation names and the evidence map; they cost about 0.02 AUC on CDFv2 in this single-seed comparison.

## 2026-10-06 19:50: RU7 (AR pairs) — solved on paper, shortcut in fact; and it raises the escape
See PRE_DECLARED Addenda 12-13. FairBeauty val: filtered genuine called fake 75.1 % (RU5) -> 0.1 % (RU7), held-out filters
included; originals called fake 26.1 % -> 0.3 %. But with the face hull greyed out 94.8 % of filtered images are still called
filter: the model reads the capture pipeline. Cost on Celeb-DF-B: beauty-only rise in MISS +6.7 -> +17.2 pp, 26.6 % of
beautified deepfakes called filter. Third appearance of a corpus shortcut on the filter side in this project (v8 Layer2,
artifact classifier, now AR pairs). FF++-only control (clipe5f): AUC-b 0.872, +7.5 pp, CDFv2 0.899, DFD 0.959, paired
interval above Forensics Adapter [+0.020, +0.068] and Effort [+0.041, +0.092]; Alibaba balanced 50.0 % (no retouching data).

## 2026-10-06 20:30: donor part-edit test set rebuilt without training donors (`partedit_20260927/gen_test_donor_v2.py`)
The original donor set drew every donor face from FF++ TRAIN real frames (pool hard-wired to landmarks_train.npz; the
same-video guard compared to an empty string and never fired); 1,023 (donor frame, part) pairs were identical to training
rows. donor_v2: same 1,316 test targets x 3 parts, donors from the 1,316 FF++ test real frames (136 videos), donor video !=
target video, seed 20261006; 0 donor frames in training, 0 pair overlap. Manifest manifest_test_donor_v2.tsv; images
ffpp_partedit/test/donor_v2. The explanation harness is queued on it for RU5 (two seeds), clipe4r, Ours-lite and the
binary control; the paper's donor column will be replaced by donor_v2. SD / SDXL columns were never affected.

## 2026-10-06 20:50: DFD test list rebuilt (`ffpp_benchmark_20260925/build_dfd_standard_v3.py` -> dfd_std32v3)
Cause of the 60 % frame dropout: MediaPipe FaceLandmarker on full 1920x1080 frames cannot see faces of 88-164 px (wide
shots: 97 videos had zero frames, all wide-shot scenes; close-ups were complete), so the v2 set was biased toward close-up
scenes. v3 adds a YuNet detection + 2x upscale before the landmarker: 332/332 videos, 10,404 frames (real 4,652 / fake
5,752), median 32 per video, 281 videos complete; 1.3 % of frames use the detector box only, 1.4 % failed (actor ~25 px
tall). Every DFD number in the paper (video AUC 0.976-0.983) must be re-scored on v3; scoring is queued for the 13
published detectors and our models (`dfd_v3_eval.py`).

## 2026-10-06 21:30: equal-data controls (Addenda 11, 13) — the colour-grading recipe is the cause, and it holds with FF++ only
Celeb-DF-B, one rule for all (AUC beautified pairs / beauty-only rise in MISS / FA on beautified genuine at 5 % FPR):
Effort 0.807 / +11.0 / 5.4; Forensics Adapter 0.828 / +15.2 / 7.9;
**FF++-only RU5 recipe, seed 1: 0.872 [0.846, 0.894] / +7.5 [4.8, 10.5] / 7.8; seed 2: 0.870 [0.843, 0.892] / +9.1 [6.2, 12.3] / 7.5**
(paired AUC-b difference to Forensics Adapter +0.020..+0.068 and +0.016..+0.067; to Effort larger);
**FF++-only without the random colour grading: 0.849 [0.820, 0.876] / +14.1 [10.7, 17.8] / 7.2** (difference to Forensics
Adapter [-0.007, +0.049], not separated). Validation: genuine + unseen colour filter called fake 15.1 / 26.6 % with / without
the grading. CDFv2 frame AUC 0.899 / 0.876 (two seeds) and 0.880 without grading; DFD 0.959 / 0.953 / 0.953.
Reading: with exactly the baselines' training data, showing random colour looks on genuine AND forged faces lowers the
beautification-only escape by about half and raises the beautified-pair AUC by 0.02-0.04 over the 2025 CLIP detectors,
without changing cross-dataset AUC; removing that one ingredient removes the gain. Two seeds agree. The equal-data claim is
supported; the full-data models add the retouching recognition, not detection.

## 2026-10-07: second beautification source (Celeb-DF-v2 + held-out colour filters, Addendum 14) and DFD v3 — partial replication only
**Celeb-DF-v2 filtered, one rule for all** (frame AUC untreated -> filtered [CI]; rise in MISS at 5 % FPR; FA on filtered genuine):
SBI 0.817 -> 0.729, +8.5, 9.1; Effort 0.881 -> 0.788 [0.753, 0.820], +16.8, 6.2; Forensics Adapter 0.887 -> 0.790 [0.757, 0.822], +12.1, 10.2.
clipe4r 0.889 -> 0.838 [0.811, 0.869], +0.9, 10.4; RU5 s1 0.891 -> 0.849, +14.5, 5.1; RU5 s2 0.887 -> 0.843, +8.4, 6.7;
binary control 0.914 -> 0.863 [0.838, 0.885], +13.9, 5.2; **FF++-only 0.898 -> 0.797 [0.760, 0.833], +3.2, 16.4;
FF++-only without colour grading 0.880 -> 0.779 [0.748, 0.814], +5.2, 15.6.**
Reading. (a) The problem replicates on a second source: every published detector loses AUC under colour filters, the 2025
CLIP detectors about 0.09-0.10. (b) The full-data models keep a higher filtered AUC (0.84-0.86 vs 0.79), but clipe4r, which
has no colour grading, does so too, so on this source the advantage comes from the wider training data, not from the
grading. (c) **The equal-data claim does NOT replicate here:** the FF++-only model's filtered AUC equals Forensics
Adapter's (0.797 vs 0.790, intervals overlap), the grading adds 0.018, and it accuses 16 % of filtered genuine Celeb-DF
frames. The Celeb-DF-B result (0.872 / 0.870 vs 0.828, two seeds) stands, but the paper cannot say the recipe fixes
beautification under equal data in general; it can say it does on Celeb-DF-B app presets and not on colour LUTs applied to
Celeb-DF-v2. Rise-in-MISS and FA trade against each other across models at a fixed threshold, so the filtered-pair AUC is
the comparable number.
**DFD v3 (332 videos, 10,404 frames):** video AUC Effort 0.973, Forensics Adapter 0.984, SBI 0.879; ours 0.978 (clipe4r),
0.978 / 0.981 (RU5), 0.987 (binary control), 0.986 (FF++-only). All paired intervals against Effort and Forensics Adapter
contain 0 or touch it: level. Against SBI all intervals exclude 0.
**donor_v2 (no training donors):** flip 94.0 / 90.8 % vs ceiling 94.1 / 90.7 % (RU5 two seeds), 87.6 vs 87.5 (clipe4r),
87.9 vs 88.0 (Ours-lite); IoU7 0.81-0.83; random region 9-15 %. The explanation result is unchanged by the leak fix.

## 2026-10-07 Search-strength probe on the baselines (Addendum 16, FF++ val frames only, `adv_probe.json`)
200 genuine + 200 forged FF++ val frames; accuracy of the forged decision under the bounded beautification operator.

| model | edit | genuine acc (mean P(forged)) | forged acc (mean P(forged)) |
|---|---|---|---|
| FF++-only (clipe5f) | none | 96.0 (0.058) | 93.5 (0.924) |
| | random draw | 71.0 (0.340) | 89.5 (0.888) |
| | worst of 4 draws | 41.0 (0.575) | 83.0 (0.818) |
| | 1-step search | 8.5 (0.895) | 74.0 (0.733) |
| | 10-step search | 0.0 (1.000) | 20.0 (0.242) |
| FF++-only, no grading (clipe5fg0) | none / random / worst of 4 / 1-step / 10-step | 92.5 / 65.5 / 39.0 / 7.0 / 0.0 | 94.5 / 89.0 / 79.5 / 66.0 / 9.0 |
| binary control, full data (clipe5b) | none / random / worst of 4 / 1-step / 10-step | 83.5 / 47.5 / 21.5 / 7.0 / 0.0 | 95.5 / 94.0 / 93.5 / 85.5 / 26.5 |

Reading: (1) inside the bounded operator a single gradient step is far stronger than a random draw or the worst of four
draws, so the three training arms (random, worst-of-4, gradient) differ in what they expose the model to. (2) The damage is
asymmetric in the same direction as on the test sets: genuine faces are pushed to "forged" much more easily than forgeries
are pushed to "genuine". (3) Hand-written random grading in training (clipe5f vs clipe5fg0) gives almost no protection
against the searched edit, and the full-data binary control is no better on genuine faces. Caveat: the 10-step edit sits at
the corners of the bounds; whether such views still look like plausible beautification is checked by eye, not measured.

## 2026-10-07 Shift-subspace probe (Addendum 17 A, `subspace_probe.py`, `SUBSPACE_PROBE.md`; FF++ val + held-out filters only)
**Mechanism, measured.** For the FF++-only checkpoint (clipe5f), the two vignette filters move the pooled CLIP feature of a
genuine frame by +7.8 (earlybird) and +5.6 (mayfair) forged-logits on average; the other nine held-out filters move it by
+0.1 to +2.4. The cosine between the mean shift and the forged weight vector is 0.20 / 0.33 for the two vignette filters and
0.00–0.09 for the rest. earlybird's shift norm is 1.08 times the feature norm itself. Forged frames are moved far less
(−0.7 to +1.8). The same pattern holds for the no-grading checkpoint (+8.5 / +6.0; cos 0.19 / 0.34). This is the
quantitative form of "a radial luminance overlay reads as forgery evidence": the filter's shift has a component along the
forged direction that is 3–10 times that of a pure colour look.
**Unseen filters move along training-available directions.** 63–90 % of every held-out filter's shift energy lies inside
the 16-dimensional subspace spanned by the shifts of the training-available beautifications (operator draws, random
grading). The directions were seen; the magnitude and combination were not.
**Linear erasure does not work (negative, reported as analysis).** Projecting the training shift subspace out of the
feature and refitting the forged head costs clean AUC immediately (k=2: 0.987 → 0.933; MISS clean 6 → 26 %) and does not
lower the genuine-called-forged rate under held-out filters (17.5–27.5 % vs 21.5 % for the original head). The dominant
shift directions carry forgery evidence too: forgery and beautification are entangled in the same few directions of the
fine-tuned representation, so the separation has to be learned during training, which is what the worst-case arm does.
The refit without erasure (k=0) is itself worse than the trained head on filtered frames (AUC 0.916 vs 0.953), so the
refitting procedure is not the explanation for the erasure results. Addendum 17 A rule: < 10 pp FA reduction → analysis only.

## 2026-10-07 Operator fitted to measured edits (Addendum 17 B, `fit_operator.py`, `FIT_OPERATOR.md`; training split only)
1,000 pairs per family, Adam on the operator parameters from the identity point, grain off.

| family | PSNR before → after the fit | reading |
|---|---|---|
| training pilgram filters on FF++ frames | 21.0 → 39.8 dB | the operator reproduces app colour filters almost exactly |
| random_grade | 24.2 → 48.3 dB | same family, sanity check |
| Tencent retouching (FFHQ pairs) | 21.4 → 28.6 dB | 7 dB of a commercial edit is tone, colour and smoothing; the residual is geometry (slimming, eye enlargement), which a photometric operator cannot express |
| Megvii retouching | 29.1 → 30.6 dB | a subtle edit, mostly geometry and local smoothing |

Caveat: on the vendor pairs the fitted smoothing weight also absorbs the misalignment caused by the geometric edit, so
the smoothing percentiles for Tencent / Megvii (median 0.28 / 0.22) are upper estimates.
**The hand-set bounds clip real filters.** For the app-filter family the 99th percentile sits at the bound in four of ten
effective parameters: colour-matrix off-diagonal 0.149 (bound 0.15), tint span 0.157 (bound 0.16), luminance field
0.62–1.24 (bounds 0.60–1.25), smoothing 0.39 for Tencent (bound 0.40). Saturation reaches 0.17 (near monochrome), gamma
0.66–1.34, contrast 0.77–1.29, all inside the bounds. For the next round the bounds are widened where the data hit them
(colour matrix 0.25, tint ±0.12, field 0.45–1.40, smoothing 0.5) and the fitted diagonal Gaussian (`fit_operator_prior.npz`)
is available as the plausibility prior of Addendum 17 B. The arms already training keep the current bounds.

## 2026-10-07 Fresh colour-filter source: DFD v3 + sixteen filters never used in training or diagnosis (Addendum 16, `DFD_FILTERED.md`, `dfd_filtered.json`)
332 videos / 10,404 frames, one filter per video (seed 20261007) from fourteen pilgram2 filters absent from pilgram, BT.601
grayscale and the standard sepia matrix. One rule for all: P(fake), threshold at 5 % FPR on untreated genuine frames,
video-cluster bootstrap. Paired AUC differences use identical bootstrap draws.

| detector | AUC untreated → filtered | MISS rise [CI] | FA rise [CI] |
|---|---|---|---|
| Effort | 0.939 → 0.904 | +12.3 [8.3, 15.7] | −0.5 |
| Forensics Adapter | 0.940 → 0.907 | +7.0 [4.1, 10.6] | +2.9 [0.7, 5.6] |
| SBI | 0.829 → 0.803 | +4.4 [1.4, 6.7] | +0.8 |
| UnivFD | 0.840 → 0.793 | −15.6 | +17.1 [12.6, 21.6] |
| nine CNN baselines | −0.01 to −0.05 AUC | | |
| Ours RU4 re-run (clipe4r) | 0.942 → 0.928 | +2.5 [−0.3, 5.5] | +0.9 [−1.5, 3.1] |
| Ours RU5 s1 / s2 | 0.942 → 0.927 / 0.945 → 0.927 | **+12.0** [8.7, 15.5] / +8.1 [5.1, 11.3] | −1.9 / −0.4 |
| binary control (same data) | **0.961 → 0.949** | +5.2 [3.0, 8.0] | −0.6 |
| FF++-only control | 0.943 → 0.925 | +1.2 [−1.2, 4.0] | +4.1 [2.0, 6.5] |
| FF++-only, no grading | 0.938 → 0.910 | +0.2 | +7.0 [4.3, 9.0] |

Readings. (1) The two-sided damage replicates on a source nobody tuned on: every published detector loses AUC; Effort's
miss rate rises 12 points at its deployment threshold; UnivFD's false alarms on genuine faces rise 17 points. (2) Equal
data: the FF++-only model beats Effort under the filters with a paired CI excluding 0 ([0.003, 0.038]) and ties Forensics
Adapter ([−0.0001, 0.037]); on filtered Celeb-DF-v2 it was level with both. Random grading helps again ([0.004, 0.027]
over the no-grading control). (3) The binary control trained on our full data is the best detector on every metric, as on
CDFv2, DFD v3 and Celeb-DF-B: the factorised three-way output costs about 0.02 AUC and is not a detection contribution.
(4) RU5 s1's AUC is unchanged under the filters while its miss rate at the fixed threshold rises 12 points: the filters
shift its scores down for genuine and forged frames alike (FA −1.9). The fixed-threshold metric is sensitive to a uniform
shift that AUC cannot see; both are reported. Hypothesis recorded in Addendum 18 (class-imbalanced frequency of random
grading in RU5's sampling), tested by the round-2 arms. (5) Video-level untreated AUC: ours 0.978–0.987, Effort 0.973,
Forensics Adapter 0.984: level, as before.

## 2026-10-07 Round 1 of worst-case beautification training: the 1-step label-loss arm fails its bars (Addenda 15–16, 19)
FF++-only, seed 20260929, selection ffpp_f1 (epoch 6). One rule, same bootstrap draws as the baselines.

| | Celeb-DF-B AUC-b / beauty-only rise | CDFv2 untreated / filtered | DFD fresh untreated / filtered | probe: genuine acc 1-step / 10-step |
|---|---|---|---|---|
| FF++-only, random grading (clipe5f) | 0.872 / +7.5 | 0.898 / 0.797 | 0.943 / 0.925 | 8.5 / 0.0 |
| + worst case, 1 step, CE (clipe5af) | 0.864 / +8.2 | **0.876** / 0.810 | 0.946 / 0.928 | 71.5 / 25.0 |
| + random operator (clipe5rf) | 0.876 / +7.9 | pending | pending | 39.5 / 0.5 |
| Effort / Forensics Adapter | 0.807 / +11.0, 0.828 / +15.2 | 0.881 / 0.788, 0.887 / 0.790 | 0.939 / 0.904, 0.940 / 0.907 | |

Bars: M1 (AUC-b ≥ 0.890, rise ≤ 7.5) fail; M2 (CDFv2 filtered ≥ 0.84) fail; M3 (untreated drop ≤ 0.01) fail on CDFv2
(−0.022); M4 (worst > random) fail on Celeb-DF-B; M5 (fresh source, above clipe5f with CI excluding 0) fail
([−0.007, +0.014]), although it beats Forensics Adapter there ([0.0006, 0.044]). Overfitting flag triggered (46.5 pp between
1 and 10 steps). The model did become robust to the operator (genuine accuracy under the 1-step search 8.5 → 71.5 %), so
the search works against the operator; the robustness does not transfer to the real presets and filters, and the clean
accuracy on CDFv2 pays for it. The probe also shows the mechanism: forged accuracy under random edits fell from 89.5 to
79.5 %, i.e. the label loss on edited views, dominated by the much easier attacks on genuine faces, taught "heavily edited →
less likely forged". Next arms (pre-declared in Addenda 18–19): the search confined to measured edits (R2-1, running), the
consistency objective that penalises any movement of the forgery score on both classes (R2-5), and three steps (R2-2).

**Round 1 complete (17:55).** Worst-of-4 control (clipe5kf): Celeb-DF-B AUC-b 0.867 / beauty-only +12.9, CDFv2 untreated
0.860 / filtered 0.804. Random operator on the fresh source: 0.952 / 0.927 (vs clipe5f [−0.007, +0.011]). The three
operator arms (random, worst of 4, 1-step search) are statistically indistinguishable from each other and from the
random-grading baseline under beautification (AUC-b 0.864–0.876 vs 0.872; filtered CDFv2 0.804–0.810 vs 0.797; fresh DFD
0.927–0.928 vs 0.925), and all three lose 0.02–0.04 untreated AUC on CDFv2 (0.860–0.876 vs 0.898) while DFD is unchanged.
Conclusion of round 1: with a label loss on edited views, the operator family as a training augmentation adds nothing
over random colour grading and costs CDFv2; the search direction is not what limits it. Round 2 (plausible range,
consistency objective, three steps) is running; a different mechanism, estimate-and-invert canonicalisation, is
pre-declared in Addendum 20.

## 2026-10-07 Estimate-and-invert canonicalisation: negative (Addendum 20, `train_canon.py`, `canon_probe.py`; FF++ val only)
The exact algebraic inverse of the operator restores a synthetically edited frame to 53–58 dB when the true parameters are
given, so the family is invertible. Estimating the parameters from a single image is the bottleneck: after 6,000 steps the
estimator raises the PSNR of random photometric edits from 25.9 to 26.7 dB and of the held-out filters from 21.0 to
22.7 dB, and moves untreated frames to 34.4 dB. Put in front of the FF++-only detector without retraining, it does not help:
FA under the held-out filters 21.5 → 23.6 %, filtered AUC 0.953 → 0.948. The detector arms C1 / C2 of Addendum 20 are
not run; a module that cannot undo the edit on validation data has no claim to test data. Reading: a face image alone does
not determine its colour transform (a warm look and a warm scene are the same pixels), so blind inversion recovers only the
extreme looks, which the detector already survives.

**R2-1 (search confined to measured edits, wide bounds; clipe5awpf, 21:44): fails.** Celeb-DF-B AUC-b 0.869 [0.843, 0.890],
beauty-only rise +15.1 (worse than clipe5f's +7.5); CDFv2 untreated 0.874 / filtered 0.819 (dMISS +5.5, dFA +3.1); fresh DFD
0.946 / 0.930. M1, M2, M3 fail. Four operator arms with a label loss (random, worst of 4, 1-step, plausible 1-step) now
agree: filtered-frame AUC moves by +0.01 to +0.02, untreated CDFv2 falls by 0.02–0.04, Celeb-DF-B does not improve. The
second seed of R2-1 is cancelled; the local GPU runs the detection-gain decomposition of Addendum 21 instead. R2-5
(consistency objective) and R2-2 (3 steps) continue on Ubuntu as declared.

## 2026-10-08 Round 2, continued: the consistency arm fails; the full-data binary arm gains nothing under beautification but replicates the detection win
| | Celeb-DF-B AUC / AUC-b / beauty-only rise | CDFv2 untreated / filtered | CDFv2 frame vs Effort, vs FA (paired CI) | DFD frame vs Effort, vs FA |
|---|---|---|---|---|
| FF++-only baseline (clipe5f) | 0.938 / 0.872 / +7.5 | 0.898 / 0.797 | | |
| R2-5 consistency objective, FF++-only (clipe5awptf) | 0.924 / 0.856 / +13.0 | **0.849** / 0.807 | | |
| full-data binary control (clipe5b, seed 20260929) | 0.949 / 0.896 / +7.0 | 0.914 / 0.863 | [0.010, 0.058], [0.006, 0.045] | [0.011, 0.054], [0.009, 0.042] |
| full-data binary + plausible worst case (clipe5awpb, seed 20260930) | 0.942 / 0.892 / +9.7 | 0.911 / 0.876 | [0.009, 0.053], [0.003, 0.044] | [0.009, 0.050], [0.006, 0.038] |

**R2-5 fails** M1 and M3; the consistency term costs 0.05 untreated AUC on CDFv2, the largest loss of any arm.
**The full-data operator arm** does not beat the binary control on Celeb-DF-B (0.892 vs 0.896) and gains 0.013 on the
filtered Celeb-DF-v2 development source; it fails its bar (Addendum 18).
**Replication of the detection result.** With a different seed (and the operator views added), the full-data binary recipe
again beats Effort and Forensics Adapter at frame level on both standard sets, all four paired intervals excluding 0
(CDFv2 0.911, DFD 0.963; video level 0.954 / 0.970, intervals include 0). Two seeds now agree. Which ingredient produces
it is the question of Addendum 21 (D1 / D2, training).
**State of the operator-training line.** Six arms run, six fail (random, worst of 4, 1-step, plausible 1-step, consistency,
full-data). R2-2 (3 steps) is the last arm under the stop rule of Addendum 22.

## 2026-10-08 Common token shift and self-referenced probes: hypothesis rejected (Addendum 23, `token_probe.py`, `TOKEN_PROBE.md`; FF++ val only)
FF++-only model (clipe5f). The common-shift fraction of the held-out filters is 0.47 on average (0.37–0.53 per filter),
below the 0.6 of the decision rule: about half of a filter's effect on the patch tokens is *not* a shift shared by all
positions. Linear probes fitted on clean train frames only:

| probe | AUC clean | AUC filtered | FA filtered | MISS filtered |
|---|---|---|---|---|
| pooled feature | 0.985 | 0.878 | 1.7 | 67.3 |
| mean of patch tokens | 0.986 | 0.931 | 25.1 | 7.9 |
| inner minus outer tokens | 0.983 | 0.921 | 19.6 | 11.5 |
| dispersion over positions | 0.985 | 0.906 | 11.1 | 20.4 |
| pooled feature, fitted on clean + graded | 0.987 | 0.963 | 16.8 | 6.8 |

Within-image contrast features are not invariant to the filters (FA 11–20 %), and with exposure to graded frames the pooled
feature is the best probe (0.963). A head refitted on clean frames only fails in the opposite direction from the trained
head (misses 67 % of filtered forgeries instead of accusing genuine faces), which shows again that the direction of the
error under a filter is set by what the head saw in training, not by the representation. Decision rule not met; no
self-referenced detector is trained. For the full-data binary model the last-layer patch tokens receive no supervision
(rho 0.03), so its numbers carry no information about the hypothesis.
**Tally for 2026-10-07/08.** Operator training with a label loss (4 arms), with a consistency loss (1), on full data (1),
estimate-and-invert canonicalisation, linear subspace erasure and self-referenced token features: nine attempts at
robustness beyond random colour grading, none passes. What does hold, with two seeds and paired intervals: random grading
on both classes halves the beautification-specific rise in misses on Celeb-DF-B (14.1 → 7.5 / 9.1) and the FF++-only model
keeps 0.04–0.065 more AUC under app presets than Effort and Forensics Adapter.

## 2026-10-08 DFD + sixteen fresh filters with the filter on the full frame (Addendum 23 validity fix; `DFD_FILTEREDFF.md`)
Same videos, frames, filters and assignment as the crop-level version; the filter is applied to the 1920x1080 frame and the
same box is cropped (10,404 / 10,404 frames, boxes identical). This version supersedes the crop-level one in the paper.

| detector | AUC untreated | AUC filtered, crop-level → full-frame | MISS rise, full-frame [CI] | FA rise, full-frame [CI] |
|---|---|---|---|---|
| Effort | 0.939 | 0.904 → 0.905 | +15.1 [11.1, 18.6] | -2.3 [-3.1, -1.4] |
| Forensics Adapter | 0.940 | 0.907 → 0.924 | +8.0 [5.6, 11.2] | -0.6 |
| SBI | 0.829 | 0.803 → 0.810 | +4.5 [2.7, 6.3] | +0.4 |
| UnivFD | 0.840 | 0.793 → 0.801 | -10.2 | +11.6 [8.0, 15.7] |
| FF++-only (clipe5f) | 0.943 | 0.925 → 0.932 | -0.3 [-2.7, 2.7] | +3.4 [2.1, 5.0] |
| FF++-only, no grading | 0.938 | 0.910 → 0.917 | -1.7 | +7.4 [5.3, 9.1] |
| full-data binary (clipe5b) | 0.961 | 0.949 → 0.952 | +4.2 [2.1, 6.7] | +0.2 |
| RU5 s1 / s2 | 0.942 / 0.945 | 0.927 → 0.931 (both) | +8.9 / +4.4 | -1.0 / +0.3 |

Readings. (1) Where the filter is applied matters little for most detectors (+0.00 to +0.01 AUC) and noticeably for
Forensics Adapter (+0.017): the face-centred vignette of the crop-level version hurt it more than a full-frame filter does.
The crop-level numbers overstated its loss. (2) The damage remains: every published detector still loses AUC, Effort's miss
rate at its fixed threshold rises by 15 points, UnivFD's false alarms by 12. (3) Equal data: the FF++-only model beats
Effort ([0.010, 0.044]) and is level with Forensics Adapter ([-0.009, 0.025]); the earlier borderline reading against
Forensics Adapter on the crop-level version is now clearly a tie. Random grading still helps ([0.005, 0.026] over no
grading). (4) The full-data binary model beats both ([0.009, 0.031] over clipe5f; [0.012, 0.044] over Forensics Adapter).
(5) All four operator arms remain indistinguishable from the baseline. Celeb-DF-v2's crop-level version is still to be rebuilt.

## 2026-10-08 Each detector under its own preprocessing (Addendum 24; `ffpp_benchmark_20260925/DFB_CROP_EVAL.md`)
DeepfakeBench crops (dlib, five-point alignment, scale 1.3, 256 px, 32 frames) of the same Celeb-DF-v2 (516 common videos)
and DFD (332) videos, scored by the ten baselines trained on that crop and by our models. On its own crop Forensics
Adapter reproduces its paper almost exactly (CDFv2 frame 0.899 / video 0.956 vs published 0.900 / 0.957); Effort does not
(0.879 / 0.927 vs 0.901 / 0.956; GenD's re-run of the released weights gives 0.932 too). The eight CNNs gain 0.00–0.05 on
their own crop. Our models lose 0.00–0.02 on the DeepfakeBench crop (they were trained on ours).
**Verdict under the pre-declared rule (ours on our crop vs each baseline on its own crop, paired intervals).** Full-data
binary model: beats Effort at frame and video level on both sets (CDFv2 [0.010, 0.059] / [0.002, 0.055]; DFD [0.013, 0.045]
/ [0.006, 0.040]); against Forensics Adapter it is on par on CDFv2 ([−0.007, 0.034] frame, [−0.022, 0.020] video) and ahead
at frame level only on DFD ([0.008, 0.036]; video [−0.004, 0.018]). Outcome (b) of Addendum 24 for Forensics Adapter: the
paper says "on par with Forensics Adapter, above Effort", and the earlier frame-level win over Forensics Adapter on CDFv2 is
reported as a crop effect. The FF++-only models are on par with both (all intervals include 0).

## 2026-10-08 Where the full-data detection margin comes from (Addendum 21): not from the part-level forgeries
FF++-only binary (D1 = P2, clipe5fb): CDFv2 frame 0.877, DFD 0.951; with the 61,510 part-level forgeries (D2, clipe5feb):
0.884 / 0.956. Neither beats Effort or Forensics Adapter with an interval excluding 0 (D2 vs Effort on DFD [0.001, 0.042]
is the only one that does, and it does not on CDFv2). The full-data binary model (0.914 / 0.967) therefore owes its margin
to the external real data (FFHQ stills, commercial renders) and not to the synthesised forgeries; the paper attributes it so.
D2 does lower the beautification-specific miss rise relative to D1 on Celeb-DF-B (−3.2 pp [−5.5, −0.9]) at equal AUC-b.

## 2026-10-08 Who gets the beautified views (Addendum 25, seed 1; `celebdfb_v2_20260927/pair_cdfb.json`)
| arm | Celeb-DF-B AUC untreated / AUC-b | beauty-only MISS rise [CI] | FA on beautified genuine | CDFv2 untreated / filtered |
|---|---|---|---|---|
| P0 no beautified views | 0.927 / 0.860 | +17.0 [13.8, 20.6] | 5.1 | 0.889 / 0.772 |
| P2 both classes (= D1) | 0.929 / 0.879 | +9.8 [7.3, 13.0] | 5.6 | 0.877 / 0.810 |
| Effort / Forensics Adapter | 0.909 / 0.807, 0.909 / 0.828 | +11.0, +15.2 | 5.4, 7.9 | |

Paired, P2 minus P0: AUC-b +0.020 [0.007, 0.032]; beauty-only rise −7.2 pp [−9.4, −5.1]; untreated AUC +0.002 [−0.007,
0.010]. **H1 holds and H3 holds on Celeb-DF-B** (CDFv2 untreated 0.877 vs 0.889 is a 0.012 drop, at the edge of the 0.01
bound; DFD 0.951 vs 0.958). Without any beautified training view the FF++-only CLIP model is *worse* than Effort under the
presets (+17.0 vs +11.0 rise), so the margin our models show over the two CLIP baselines comes from the exposure rule, not
from LoRA or the backbone. P1 (genuine faces only) is being evaluated; second seeds of all three arms are training.

## 2026-10-08 14:30 Exposure ablation complete for seed 1 (Addendum 25): P1 < P0 < P2, as predicted
| arm (FF++ only, binary) | Celeb-DF-B AUC-b | beauty-only MISS rise [CI] | FA beautified genuine | CDFv2 untreated / filtered, MISS rise | DFD full-frame filtered, MISS rise |
|---|---|---|---|---|---|
| P0 none | 0.860 | +17.0 [13.8, 20.6] | 5.1 | 0.889 / 0.772, +4.4 | 0.924, +9.3 |
| P1 genuine faces only | **0.844** | **+21.5** [17.6, 25.4] | 4.6 | 0.859 / 0.752, **+24.0** | 0.905, +11.3 |
| P2 both classes | **0.879** | **+9.8** [7.3, 13.0] | 5.6 | 0.877 / 0.810, +3.2 | 0.929, +2.5 |

Paired: P1 − P0 rise +4.5 pp [1.5, 7.6] (AUC-b −0.016 [−0.038, 0.004]); P2 − P1 AUC-b +0.036 [0.017, 0.055], rise −11.7 pp
[−14.5, −8.8]; untreated AUC equal across the three ([−0.009, 0.010]). **H2 holds**: beautifying only genuine faces in
training teaches "beautified means genuine" and makes beautified forgeries escape *more* than with no beautification at all
(on Celeb-DF-v2 filters its miss rise is +24 points, the largest of any model we trained). This is the mechanism behind
the asymmetric exposure effects seen earlier (Addenda 18, 19) and the reason the rule has to be stated as symmetric.
Caveat for H3: P2's untreated CDFv2 AUC is 0.877 vs P0's 0.889 (−0.012, at the edge of the 0.01 bound; DFD −0.005); on the
DeepfakeBench crop the three arms are within 0.005 of each other on DFD and P2 is 0.019 below P0 on CDFv2. Second seeds
of all three arms are training.

**Operator-training line closed (Addendum 22).** R2-2 (three-step search, plausible set): Celeb-DF-B AUC-b 0.859 / rise +9.0,
untreated CDFv2 0.849 (−0.049 vs clipe5f): fails M1 and M3. Seven arms, seven failures; the line is reported as a negative
result with the probe evidence that the search itself worked (genuine accuracy under the operator 8.5 → 71–77 %).

## 2026-10-08 16:20 Evidence-map statistics as the decision (Addendum 27 probe, `EVIDENCE_PROBE.md`): fails the bar, but the structure is there
Existing heads (trained on part-level footprints and on the footprint of *every* edit, beautification included). Under the
held-out filters the map of a genuine face lights up everywhere (mean logit −8.3 → +1.9; max −5.9 → +3.9): the head is an
edit localiser, not a forgery localiser, because the beautified training item hands it the beautification's own footprint as
target. Yet the structural statistic max − mean keeps its AUC under the filters (clipe5f 0.877 → 0.871; clipe5 0.896 → 0.890)
while the pooled logit drops (0.987 → 0.953) and the mean collapses (0.867 → 0.265), and its false-alarm rate under the
filters is 8.5 % / 4.3 % against 21.5 % / 11.9 % for the pooled logit. Fail on the pre-declared clean-AUC bound (0.88–0.90 vs
0.97–0.99): a map trained on eyes / nose / mouth footprints has no concentrated evidence for whole-face swaps, so misses
rise (28 → 46 %). Reading: the decision statistic is filter-robust as predicted; the map it reads is not yet a forgery map.
Next (Addendum 28, to be written): a head whose target is zero on every beautification and the exact mask on every forgery
(self-blend masks, part footprints, FF++ masks where available), with the decision pooled from the map's top cells.

## 2026-10-08 18:00 Edit-sensitivity as evidence (Addendum 29 probe, `SENSITIVITY_PROBE.md`): rejected
The class asymmetry of the response to probe edits exists on average (clean genuine +0.1 to +3.9 logits under a corner
vignette, forged −0.5 to −1.0) but the saturation control shows it is a ceiling effect: inside the clean-logit deciles where
both classes occur (deciles 3–5) genuine and forged frames move by the same amount (1.15 vs 0.96; 0.48 vs 0.10; −0.57 vs
−0.74). Accordingly the response alone discriminates weakly (AUC 0.79 / 0.87) and adding it to the logit does not lower
the false alarms under the held-out filters (16.3–21.7 % vs 18.7–20.7 % for the logit alone). Fails (ii) and (iii); dropped.

## 2026-10-09 00:30 Exposure rule: second seed and the Effort-scheme plug-in (Addenda 25–26; `pair_cdfb.log`)
| pair (Celeb-DF-B, paired video-cluster bootstrap) | AUC-b difference | beauty-only MISS-rise difference | untreated AUC difference |
|---|---|---|---|
| P2 − P0, seed 1 | +0.020 [0.007, 0.032] | −7.2 [−9.4, −5.1] | +0.002 [−0.007, 0.010] |
| P2 − P0, seed 2 | +0.010 [−0.000, 0.020] | −4.0 [−6.1, −2.0] | −0.003 [−0.010, 0.003] |
| P1 − P0, seed 2 | −0.032 [−0.053, −0.012] | +7.5 [4.4, 10.8] | −0.006 |
| P2 − P1, seed 2 | +0.042 [0.025, 0.060] | −11.5 [−14.5, −8.9] | +0.002 |
| E2 − E0 (Effort's SVD-residual tuning, 0.21 M params) | +0.007 [−0.000, 0.014] | −4.6 [−6.4, −3.2] | −0.004 [−0.009, 0.000] |

The ordering P1 < P0 < P2 replicates on the second seed and inside Effort's tuning scheme. The robust effect is on the
miss rate at the deployment threshold (−4 to −7 pp against no exposure, −11 to −12 pp against genuine-only exposure, every
interval excluding 0); the AUC-b gain over no exposure is +0.01 to +0.02 and excludes 0 in one of three pairs. The
genuine-only arm is reliably the worst (AUC-b −0.016 / −0.032, rise +4.5 / +7.5). Effort's scheme is less exposure-sensitive
than LoRA to begin with (E0 rise +10.1 vs P0 +14 / +17), so the rule adds less there; it still adds in the same direction.
Absolute numbers, seed 2: P0 0.883 / +14.2, P1 0.851 / +21.8, P2 0.893 / +10.3; E0 0.882 / +10.1, E2 0.889 / +5.5
(Effort's released checkpoint on the same frames: 0.807 / +11.0).

**Map-pooled arms (Addendum 28) not yet interpretable: evaluation bug.** The reloaded checkpoint is built without the `mil`
flag, so every harness read the unsupervised pooled head (val AUC 0.29) instead of the map-pooled logit (training-time
val AUC 0.986; `EVIDENCE_PROBE.md` for clipe5mf: top-5 % cells AUC 0.983 clean / 0.956 filtered). Loader fix and
re-evaluation follow; no verdict yet.

## 2026-10-10 Map-pooled decision (Addendum 28), re-evaluated with the loader fixed: fails B1; Effort-scheme plug-in seed 2 replicates
| arm (FF++ only) | Celeb-DF-B AUC untreated / AUC-b | beauty-only MISS rise [CI] | FA beautified genuine | DFD full-frame filters AUC-f |
|---|---|---|---|---|
| three-way, pooled decision (clipe5f) | 0.938 / 0.872 | +7.5 [4.8, 10.5] | 7.8 | 0.932 |
| M2 map-pooled, both classes exposed | 0.937 / 0.877 | **+14.9** [12.0, 18.3] | 5.0 | 0.924 |
| M0 map-pooled, no exposure | 0.942 / 0.891 | +14.7 [11.4, 17.9] | 4.4 | 0.932 |

Paired: M2 − clipe5f AUC-b +0.005 [−0.005, 0.016], MISS rise +7.5 pp [5.5, 9.4] (worse); M2 − M0 AUC-b −0.013, rise +0.2
[−2.1, +3.0]. Fails B1. The mechanism check B3 passes (map mean of genuine faces under the held-out filters −10.2 logits
with the zero target; FA under the filters 14.7 % vs 21.5 % for the pooled head), so the map is now a forgery map and the
decision read from it accuses fewer beautified genuine faces; but beautified forgeries escape it more, and with the decision
pooled from the map the exposure rule stops mattering (M0 ≈ M2) without reaching the exposed pooled model's miss rate. Reading:
concentrated local evidence is also what app presets wash out of a forgery; the pooled feature keeps global cues that
survive. Dropped as the method; reported as an analysis (a decision rule that trades false alarms for misses).
**E seed 2:** E2 − E0 rise −5.2 [−6.7, −3.6], AUC-b +0.004 [−0.003, 0.011], untreated −0.005 [−0.010, −0.001]: the plug-in
replicates on the miss rate, with no AUC-b gain. Two seeds for each of the three LoRA arms and the two Effort-scheme arms are
now on file. **Method-exploration budget closed (Addendum 22 rule extended): eleven mechanisms tested since 10/07, none
beats the exposure rule; the paper's method section is the rule, its ablation and the negative results.**

## 2026-10-11 WildDeepfake subset: not usable as a test set
The 800 test frames on disk come from only 6 sequences (4 genuine, 2 forged): every video-level AUC is 1.0 or undefined and
the frame-level intervals span 0.3–0.5 (e.g. P2 0.617 [0.169, 0.834]). Dropped; the full WildDeepfake test set (around 700
sequences) would have to be obtained for a usable number. `EXTRA_wdf.md` kept for the record only.

## 2026-10-11 Exposure ablation, third seed: the "both classes beats no exposure" half does not replicate
| arm | Celeb-DF-B AUC-b, seeds 1 / 2 / 3 (mean) | beauty-only MISS rise, seeds 1 / 2 / 3 (mean ± sd) |
|---|---|---|
| P0 no beautified views | 0.860 / 0.883 / 0.883 (0.875) | +17.0 / +14.2 / +10.8 (14.0 ± 3.1) |
| P1 genuine faces only | 0.844 / 0.851 / 0.864 (0.853) | +21.5 / +21.8 / +20.4 (21.2 ± 0.7) |
| P2 both classes | 0.879 / 0.893 / 0.877 (0.883) | +9.8 / +10.3 / +12.8 (11.0 ± 1.6) |

Paired, seed 3: P2 − P0 rise **+2.0 [0.1, 4.0]** (worse), AUC-b −0.006 [−0.020, +0.007]; P1 − P0 rise +9.5 [6.7, 12.4], AUC-b
−0.020 [−0.039, −0.002]; P2 − P1 rise −7.5 [−10.0, −5.1]. Across three seeds: P1 is the worst in every seed with every
interval excluding 0 (rise +4.5 / +7.5 / +9.5 over P0; +11.7 / +11.5 / +7.5 over P2). P2 over P0 is −7.2 / −4.0 / +2.0 on
the rise and +0.020 / +0.010 / −0.006 on AUC-b: a positive trend on average that is inside the seed-to-seed spread of P0
itself (sd 3.1). **The claim is narrowed accordingly**: beautifying only genuine faces in training reliably makes beautified
forgeries escape (the recipe a "filter-robust real class" would suggest, and the direction of Saeed et al.'s fine-tuning on
enhanced samples); giving the views to both classes is on average better than none but not reliably so. The no-exposure
LoRA model already keeps more AUC under app presets than Effort's released checkpoint (0.860–0.883 vs 0.807) and the
Effort-scheme no-exposure model does too (0.882–0.886), so most of the margin over the two CLIP baselines is the base recipe
(self-blends, symmetric degradation, selection on validation), not the exposure rule. The paper's method claim is therefore
a *warning* with evidence (what not to do), plus the measurement; no "our rule beats SOTA" statement.

## 2026-10-11 19:50 Exposure rule applied to the released Effort checkpoint (Addendum 30): a trade-off, not a free gain
Mapped released weights, untuned (reference): Celeb-DF-B AUC 0.909 / AUC-b 0.808 / beauty-only rise +11.2 (the released
scorer gives 0.909 / 0.807 / +11.0: the mapping is exact). Two epochs of fine-tuning on our FF++ triplet pipeline:

| arm | AUC untreated | AUC-b | beauty-only MISS rise | FA on beautified genuine | CDFv2 untreated (own crop) | DFD full-frame filters, MISS rise |
|---|---|---|---|---|---|---|
| reference | 0.909 | 0.808 | +11.2 | 4.7 | 0.886 | +13.1 |
| A0: no beautified views | 0.903 | 0.805 | +5.8 [2.6, 8.8] | 9.4 | 0.866 | +8.1 |
| A2: both classes | 0.895 | 0.803 | +2.7 [−0.3, 5.8] | 10.3 | 0.861 | +7.2 |

Paired vs reference: A2 rise −8.5 [−10.4, −6.6], AUC-b −0.005 [−0.014, +0.005], untreated −0.014 [−0.022, −0.007];
A0 rise −5.4 [−7.3, −3.7], AUC-b −0.003, untreated −0.006 [−0.013, +0.001]; A2 − A0 rise −3.1 [−3.7, −2.2], untreated
−0.008 [−0.011, −0.006]. **Bars fail**: AUC-b does not rise, untreated AUC falls by more than 0.01 on CDFv2 (−0.025) and on
Celeb-DF-B for A2. Reading: fine-tuning moves Effort's operating point rather than its separability; the miss rise shrinks
because scores move up for everything (false alarms on beautified genuine faces double from 4.7 to 10.3 %), and the
exposure rule adds 3 points of that on top of what fine-tuning alone does. A plug-in that keeps AUC and trades errors is
a calibration result, not a method result; reported as such. Forensics Adapter and SBI are not run (rule of Addendum 30).

## 2026-10-11 Exposure arms on the two colour-filter sources (`pair_filtered.json`): the direction of the error moves, separability does not
Paired, both-class minus no exposure (P2 − P0), full-frame filters:

| source | tuning, seed | MISS-rise difference | FA-rise difference | AUC-filtered difference | untreated AUC difference |
|---|---|---|---|---|---|
| DFD, 16 filters | LoRA s1 / s2 / s3 | −6.8 / −5.4 / −9.1 (all intervals < 0) | +2.0 / +2.0 / +4.6 (all > 0) | +0.004 / +0.001 / −0.006 (n.s.) | −0.005 / −0.006 / −0.008 |
| DFD, 16 filters | Effort scheme s1 / s2 | −5.7 / −5.0 (< 0) | +3.0 / +2.3 (> 0) | +0.006 / +0.006 (> 0) | +0.002 / +0.003 |
| Celeb-DF-v2, 11 filters | LoRA s1 / s2 / s3 | −6.7 / −1.4 (n.s.) / −9.2 | +2.4 / −0.4 (n.s.) / +3.3 | −0.004 / −0.008 / +0.002 (n.s.) | −0.012 / −0.020 / −0.021 (< 0) |
| Celeb-DF-v2, 11 filters | Effort scheme s1 / s2 | −9.9 / −7.1 (< 0) | +3.5 / +3.1 (> 0) | −0.005 / −0.007 (n.s.) | −0.012 / −0.011 (< 0) |

Genuine-only minus none (P1 − P0), LoRA s2 / s3: Celeb-DF-v2 MISS rise +13.3 / +8.0, FA rise −4.3 / −2.6, AUC-f −0.038 / −0.017;
DFD MISS rise +2.1 / +0.5, AUC-f −0.017 / −0.019.
Reading. On colour filters the effect of both-class exposure on the miss rise is consistent (9 of 10 cells with intervals
below 0, 5 to 10 points) and it is paid for in false alarms (2 to 5 points) with the filtered AUC unchanged: exposure moves
the detector's errors under beautification from misses toward false alarms; it does not make genuine and forged faces more
separable. Genuine-only exposure moves them the other way and also costs AUC. Together with the released-Effort fine-tune
(same pattern) this is one statement: **training exposure sets where a detector's beautification errors fall, not how many
there are in AUC terms**. LoRA pays 0.012–0.021 untreated AUC on Celeb-DF-v2 for both-class exposure; the Effort scheme
pays 0.011–0.012 there and nothing on DFD.

## 2026-10-11 22:00 GenD (WACV 2026) added to the measurement; DFD-HR scoring in progress
Official weights (CLIP ViT-L/14 variant), adapter `external_baselines/gend_score.py`; reproduces the paper on DeepfakeBench-style
crops with 32 frames (Celeb-DF-v2 video AUC 0.960 vs 0.960 published).

| source | GenD | Effort | Forensics Adapter | ours, FF++ only | ours, three-way full data |
|---|---|---|---|---|---|
| Celeb-DF-B AUC untreated / AUC-b | 0.924 / 0.807 | 0.909 / 0.807 | 0.909 / 0.828 | 0.938 / 0.872 | 0.938 / 0.866 |
| Celeb-DF-B beauty-only MISS rise | +12.0 [8.2, 15.6] | +11.0 | +15.2 | +7.5 | +6.7 |
| Celeb-DF-B FA on beautified genuine | 9.9 | 5.4 | 7.9 | 7.8 | 9.5 |
| Celeb-DF-v2 filters AUC untreated / filtered | 0.891 / 0.856 | 0.881 / 0.813 | 0.887 / 0.814 | 0.898 / 0.851 | 0.891 / 0.873 |
| Celeb-DF-v2 filters MISS rise / FA rise | −10.1 / +9.9 | +23.3 / −2.8 | +11.9 / +2.5 | −3.5 / +7.2 | +7.3 / −0.4 |
| DFD filters AUC untreated / filtered | 0.934 / 0.925 | 0.939 / 0.905 | 0.940 / 0.924 | 0.943 / 0.932 | 0.942 / 0.931 |

GenD is the third 2025–26 CLIP detector that loses 0.12 AUC under app presets (0.924 → 0.807; level with Effort, CI
[−0.024, 0.024]); the damage under presets is not specific to one tuning scheme. On colour filters GenD is the most robust
published detector in AUC (0.856 on Celeb-DF-v2, level with our FF++-only model) and its errors fall on the other side from
Effort's: false alarms +9.9, misses −10.1. Two published CLIP detectors with the same backbone err in opposite directions
under the same filters, which is the exposure finding seen across independently trained models (GenD trains with paired
real/fake data and its own augmentations).

## 2026-10-12 DFD-HR (CVPR 2026) added; the measurement now has fifteen detectors, four of them 2025–26 CLIP methods
Official weights, adapter `external_baselines/dfdhr_score.py`. Celeb-DF-v2 on DeepfakeBench-style crops: frame 0.886 / video
0.951 (published 0.910 / 0.960; not fully reproduced, same order of gap as Effort). Under beautification: Celeb-DF-B AUC
0.938 → 0.838, beauty-only MISS rise +3.6 [0.6, 6.8], FA on beautified genuine 14.6 % (the highest of the CLIP detectors);
Celeb-DF-v2 filters (full frame) 0.879 → 0.824, MISS +8.0, FA +1.6; DFD filters 0.943 → 0.928, MISS +9.1.
All four CLIP detectors lose 0.08–0.12 AUC under app presets (Effort 0.102, Forensics Adapter 0.081, GenD 0.117, DFD-HR
0.100) against 0.066–0.072 for our models; their errors fall on different sides (DFD-HR and GenD accuse beautified genuine
faces, Effort and Forensics Adapter let beautified deepfakes through).
Paper v3 and supplement v3 regenerated with fifteen detectors; the main table now reads the full-frame filter sources
(it was still reading the crop-level files; text and table now agree).

## 2026-10-12 Commercial retouching: rerun with 15 detectors, and the exposure arms (post hoc, not pre-registered)

Files: `../alipair_zeroshot_20260929/published_ali.json`, `PUBLISHED_RESULTS.md`, `exposure_ali.py`, `exposure_ali.json`.
Rule: threshold = 95th percentile of P(fake) on the 2,210 untouched originals of the unseen service; share of the 26,519
renders above it, and of the Smoothing-90 renders.

Published detectors (released weights): 7.3-16.8% of all renders, 16.6-68.7% of Smoothing-90 (NPR excluded, scores collapse).
The two newest CLIP detectors are the worst: GenD 16.8 / 68.7, DFD-HR 15.7 / 64.9; Effort 14.8 / 43.2; Forensics Adapter 10.2 / 39.7.

Ours, current models: three-way full data 4.7 / 8.6 (seed 2: 5.5 / 12.5); binary control, same data 5.2 / 9.1.
The superseded clipe4 was 2.7 / 1.4; the paper must quote the current model.
The binary control equals the three-way model, so the third class is not what removes the false alarms.

Exposure arms, FF++ only, no commercial data in training, three seeds (paired bootstrap over identities, 1000 draws):

| arm | all renders | Smoothing-90 |
|---|---|---|
| P0, no beautified views | 13.5 / 13.7 / 10.9 | 54.2 / 56.1 / 43.5 |
| P1, genuine only | 5.3 / 5.7 / 5.4 | 3.7 / 7.1 / 4.6 |
| P2, both classes | 5.9 / 5.3 / 5.4 | 11.7 / 7.1 / 6.9 |
| P0, Effort scheme | 13.4 / 14.6 | 56.9 / 63.2 |
| P2, Effort scheme | 8.6 / 10.1 | 30.0 / 38.9 |
| released Effort fine-tuned 2 epochs, P0 / P2 | 14.4 / 13.3 | 55.3 / 52.7 |

P2 minus P0 on Smoothing-90: -42.5 [-46.0, -38.8], -49.0 [-53.6, -44.6], -36.6 [-40.1, -33.3]. P1 minus P0: -50.5, -49.0, -38.9,
all intervals below zero. Effort scheme: -27.0 [-31.7, -24.3], -24.3 [-27.1, -21.5].

Reading: P0 reproduces the published detectors (10.9-13.7 / 43.5-56.1 against 10-17 / 37-69), so the false accusation of
commercially retouched faces is what FF++ training gives by default. Scripted beautification on FF++ frames alone brings the
rate back to the 5% floor on a service the model never saw. This is the first place where the exposure variable changes an
error rate by tens of points with every seed agreeing, and it is a transfer from self-built edits to a commercial pipeline.
Known costs from the earlier tables: P1 raises the miss rate under filters; P2 raises false alarms under vignette colour
filters by 2.0-4.6 points with no AUC change. Two-epoch fine-tuning of the released Effort checkpoint does not move it.
Status: exploratory until the adversarial review (Addendum 22) has attacked it.

## 2026-10-12 Adversarial review of the exposure result on commercial retouching (Addendum 22)

Review: `../alipair_zeroshot_20260929/review_20261012/REVIEW.md`. Verdict: survives with rewording. Corrections to the
section above:
- The effect is on skin smoothing only. On the other nine operation-by-level cells (whitening, face slimming, eye
  enlarging) P0 is already at 4.5-7.5%; the pooled 13.5 -> 5.3 is smoothing diluted. Report per operation and level.
- Not "transfer from self-built edits": the service's smoothing is face-local and edge-preserving, and the scripted
  smoothing is the same kind of edit at the same strength (high-frequency energy on flat skin 0.60 vs 0.68; a global
  Gaussian 0.52 everywhere). Its strength range was set to cover two other services, and the test service's measurements
  existed when the range was set. Wording: robustness across implementations and image domains. No service image is used.
- "Back to the floor" holds for P1 only. P2 still scores the render above its own original in 72-84% of pairs
  (AUROC 0.63-0.70; P0 0.84-0.89, P1 0.48-0.60).
- Missing cost: untreated Celeb-DF-v2 frame AUC, P2 minus P0 = -0.012, -0.020, -0.021 (intervals below zero);
  P1 minus P0 = -0.030, -0.027, -0.025. Untreated miss at 5% FPR +5 to +8 points.
- Holds under every threshold rule tried (1%, 10% FPR, fixed 0.5, threshold from Celeb-DF-v2 genuine frames).
- Plain blur / down-up scaling / JPEG do not prevent it: P0 already trains with them.
- Epoch dependence: P2 seed 1 is 27.5% at epoch 2, 11.7% at the selected epoch 5, 9.4% at epoch 8; P0 is 45-50% at every
  epoch; all epochs chosen on FF++ validation AUC.
- "15 detectors 37-69%" corrected to 13 of 15 in 36.3-68.7%; UnivFD 16.6%; NPR saturated.
- LoRA-from-CLIP specific: Effort scheme leaves 30-39%, released-Effort fine-tune 53%.
- Process: `train_ru5.py` is untracked in git; seed 1-2 meta files lack the beauty key (seed 3 has it and reproduces).
Required before the claim enters the paper: a both-class arm with no smoothing in its views (Addendum 31), the per-epoch
curve, the per-operation table, the corrected `random_op_v2` docstring, and `train_ru5.py` under version control.

## 2026-10-13 Addendum 31 result: the effect is exposure to smoothing itself

`../alipair_zeroshot_20260929/exposure_ali.json`. Smoothing-90 renders above the 5%-FPR threshold of the originals:
P2 without smoothing in its views 55.3% [51.9, 58.6] (seed 1) and 67.2% [64.1, 70.1] (seed 2); P1 without smoothing 55.9%.
Against P0 of the same seed: +1.2 [-2.2, 4.0], +11.1 [7.0, 14.8], +1.8 [-1.8, 5.2]. Against P2 / P1 with smoothing:
+43.7, +60.1, +52.3, intervals far above zero. Smoothing levels 30 / 60 follow (seed 1: 15.1 / 38.8 against P0 17.0 / 40.8).
Pre-declared reading 1 holds on both seeds (>= 30%): colour grades, pilgram filters, whitening, eye and jaw edits in the
views do nothing for smoothing; blur, down-up scaling and JPEG (present in every arm) do nothing either.
Claim allowed: an FF++-trained detector treats skin smoothing as forgery evidence, and only smoothing in the training views
removes that. No claim of generalisation to edits the views did not contain.
Side observation (not pre-registered): the no-smoothing arms still lose untreated Celeb-DF-v2 AUC against P0
(video 0.913 / 0.924 against 0.938 / 0.938; P2 0.917 / 0.920), so that cost comes from the other beautified views, not from
smoothing. Addendum 32 tests smoothing as the only view.

## 2026-10-13 DF40 held-out (pre-declared in `../df40_eval_20261012/PRE_DECLARED.md`): the main model fails on reenactment

`../df40_eval_20261012/DF40_EVAL.md`, video-level AUC, mean over methods, FF++ domain / Celeb-DF domain.
Face swap (9 methods): main 0.952 / 0.905, Effort 0.944 / 0.935, Forensics Adapter 0.948 / 0.897, GenD 0.966 / 0.947.
Reenactment (12 methods): main 0.718 / 0.502, seed 2 0.780 / 0.559, Effort 0.808 / 0.710, Forensics Adapter 0.828 / 0.665,
GenD 0.935 / 0.828. Paired main minus GenD on reenactment: -0.218 [-0.233, -0.203] and -0.326 [-0.343, -0.308].
On Celeb-DF-domain tpsm, danet, mcnet, facevid2vid the main model is at 0.27-0.37, below chance.
Diagnostic (`diag3way.py`, 1,200 frames per cell): reenactment frames are called real 49-51%, beautified 21-33%, forged
18-29%; face-swap frames forged 70-74%.
Our own arms order the same way on reenactment: P0 (FF++ only, binary, no beautified views) 0.906 / 0.692; three-way FF++
only 0.809 / 0.637; binary full data 0.842 / 0.647; P2 0.809 / 0.644; three-way full data 0.718 / 0.502.
Reading: every addition made for the beautification problem (beautified views, the third class, external genuine data,
part-level synthesis) lowers detection of whole-face neural rendering, which has no blending boundary and a smooth
texture. The full-data model cannot be presented as a reference detector for forgeries in general. The claim "on par with
Effort and Forensics Adapter" holds for Celeb-DF-v2 and DFD and for DF40 face swap, and fails for DF40 reenactment.
DF40 reals are the FF++ and Celeb-DF-v2 test reals; DFD-HR, CADDM and LAA-Net not yet scored on this set.
Follow-up (post hoc, queued): P2 without smoothing, P1, second seeds, and the smoothing-only arms on the same list, to see
whether the reenactment loss follows smoothing exposure.

## 2026-10-13 Addendum 32 result: smoothing alone is sufficient but not free

Smoothing-only views, both classes (P2o): Smoothing-90 on the unseen service 2.3% [1.7, 2.9] and 5.3% [4.4, 7.0];
genuine only (P1o) 0.7%. Against P0: -51.9 [-56.1, -48.3], -50.7 [-55.3, -46.5], -53.5. Bar (a) met on both seeds.
Bar (b) fails: untreated Celeb-DF-v2 video AUC 0.904 / 0.926 against P0 0.938 / 0.938 (-0.034, -0.012); untreated DFD
0.967 / 0.966 against 0.981 / 0.979 (-0.014, -0.013). Bar (c), Celeb-DF-B, is being scored.
Pre-declared reading: "(a) only" = sufficient but not free. The side hypothesis of the previous section (that the cost
comes from the other views and smoothing is free) is wrong: every kind of beautified view tried costs 0.01-0.03 of
untreated Celeb-DF-v2 AUC (P2 0.917 / 0.920, no smoothing 0.913 / 0.924, smoothing only 0.904 / 0.926, P1 0.900 / 0.910).
DF40 reenactment for these arms is queued.

## 2026-10-13 The reenactment loss follows smoothing exposure (DF40, post hoc extension)

Video AUC on DF40 reenactment, FF++ domain / Celeb-DF domain, seed 20260929 (seed 20260930 where scored):
P0 0.906 / 0.692 (0.877 / 0.720); P2 without smoothing 0.858 / 0.705; P2 0.809 / 0.644 (0.785 / 0.643);
P2 smoothing only 0.779 / 0.593; P1 0.807 / 0.569. Face swap moves little (0.94-0.98 / 0.88-0.94).
Smoothing-90 false accusation on the unseen service for the same arms: 54.2, 55.3, 11.7, 2.3, 3.7.
The two columns are ordered oppositely: the arms that stop accusing smoothed genuine faces are the arms that lose
neural-rendered reenactment. Views without smoothing cost 0.05 in the FF++ domain and nothing in the Celeb-DF domain;
adding smoothing costs a further 0.05-0.08 / 0.06-0.11.
Addendum 32 bar (c): Celeb-DF-B AUC under beautification, smoothing only 0.865 / 0.870 against P0 0.860 / 0.883; seed 2 is
0.013 lower, bar not met. Final reading of Addendum 32: (a) only.
Second seed of the smoothing-only arm and DFD-HR on DF40 still running; one seed for the no-smoothing arm on DF40.

## 2026-10-13 17 detectors; threshold-free view; the genuine-only arms are an evasion route

CADDM and LAA-Net (own crop rebuilt inside ours) scored on every source. Celeb-DF-B AUC untreated -> beautified:
CADDM 0.886 -> 0.762 (Libourel et al. report 0.91 -> 0.76 for it), LAA-Net 0.889 -> 0.698, the largest drop of the 17.
Threshold-free view of commercial Smoothing-90 (`../alipair_zeroshot_20260929/smoothing90_thresholdfree.json`): share of
renders scored above their own original, and median P(fake) original -> render. 15 of 17 published detectors: 89-99%
(GenD 98.5%, 0.23 -> 0.92; DFD-HR 99.0%; SBI 96.2%, 0.21 -> 0.99; LAA-Net 89.2%, 0.23 -> 0.97, hidden at the 5%-FPR rule by
a threshold of 0.992). Exceptions: CADDM 60.9% (boundary / identity cue, not texture), NPR saturated at 1.0.
Ours: P0 97.0-99.0%; P2 84.1%; P2 without smoothing 98.6%; P2 smoothing only 27.3%; P1 43.5%; P1 smoothing only 2.6%
(AUROC 0.095). The paper should lead with this column; the 5%-FPR column understates detectors that are near saturation
on the service's stills.

Smoothed forgeries (`smooth_evasion.py`, Addendum 33 check (e), Celeb-DF-v2 frames, whole-crop bilateral at three
strengths, threshold 5% FPR on untreated genuine): P1 smoothing only misses 100% of smoothed forgeries at every strength
(rise +56.4 [49.9, 63.7], against P0 +29 / +51 / +72 points higher), forged score falls in 100% of frames, false alarms on
smoothed genuine 0.0%. P1 (all views, genuine only) the same (+46 to +51, ~100% missed). Check (e) fails: the
genuine-only arms learned "smoothed = genuine". Their low false-accusation numbers and the good Celeb-DF-B numbers of
P1 smoothing only are that shortcut. Not recommended; reported as an evasion route. Addendum 33 seeds are moot for the
recommendation and are kept only as documentation.

Second flaw found by the same test, in our own pipeline: the both-class arms call a whole-crop bilateral filter on a
GENUINE frame forged (P2 smoothing only 47.8 / 82.3 / 88.3%; full-data main model 34.9 / 79.8 / 90.1%; P2 3.0 / 31.8 /
49.1%; P0 0.8 / 16.8 / 39.6%). Cause: in `RUData5` the genuine side receives face-local smoothing (`op_smooth`) and
pre-rendered frames, while the forged side without landmarks receives only the whole-crop bilateral (`_beaut`). The form of
the smoothing is class-predictive, so the model learned "whole-crop bilateral = forged". This is a class-asymmetric
augmentation, the kind of shortcut this project has documented three times before. It affects every both-class arm and
the main model. Addendum 34 makes the smoothing view class-symmetric.

## 2026-10-13 Addendum 33 closed: the genuine-only shortcut replicates on three seeds

P1 smoothing only, seeds 20260929 / 20260930 / 20261001 (`smooth_evasion2_*.npz`): commercial Smoothing-90 0.7 / 1.0 / 0.9%
at the 5%-FPR rule, and miss rise on bilateral-smoothed Celeb-DF-v2 forgeries +56 / +59 / +59 (light), +56 / +60 / +63
(strong), every interval above +50; on the two smoothing forms no arm has seen, median 5x5 +40 / +39 / +38 and a 50%
Gaussian blend +11 / +14 / +14, against P0 of seed 3 +12.6 and +5.6. False alarms on smoothed genuine frames 0.0%. The
shortcut generalises across smoothing forms. Bar (e) fails on all seeds; (a)-(d) are not evaluated for a recommendation.

## 2026-10-13 Addendum 34, seed 1 (seed 2 core evaluation running)

Class-symmetric smoothing view, both classes, seed 20260929. (a) commercial Smoothing-90 5.9% at 5% FPR, renders above
their own original 37.8% (seed 2: 6.1%, 52.8%): pass on both seeds. (b) smoothed genuine Celeb-DF-v2 false alarms
2.4 / 5.0 / 6.1 / 4.5 / 3.6% across five smoothing forms: pass. (c) miss rise on smoothed forgeries +14.8 / +14.5 / +14.6 /
+7.6 / +9.1 against P0 +27.0 / +5.1 / -16.0 / +19.2 / +3.0: fails the pre-declared "not more than 5 above P0" at mid,
strong and the Gaussian blend. The reference itself is a shortcut in the other direction (P0's miss falls under strong
smoothing because it accuses everything smoothed, false alarms 39.6%); the bar did not anticipate that and is not
changed. Descriptive: AUC on smoothed frames (both classes smoothed) 0.835 / 0.796 / 0.767 / 0.829 / 0.850 against P0
0.848 / 0.776 / 0.747 / 0.852 / 0.868. The symmetric arm is the only one that is neither accusing nor fooled by
smoothing; its cost is a uniform 8-15 point miss rise under heavy smoothing and (seed 1) untreated Celeb-DF-v2 video AUC
0.863 against 0.883 frame-level in this test. Paper wording: (a)+(b) met, (c) not met as written, with this explanation.

## 2026-10-13 DF40 complete for 12 published detectors
DFD-HR on DF40 (video AUC, mean over methods): face swap 0.982 / 0.940, reenactment 0.932 / 0.698 (ff / cdf). GenD 0.966 /
0.947 and 0.935 / 0.828 remains the strongest on reenactment; both are the two worst on commercial smoothing (renders
scored above own original 98.5% / 99.0%). The trade-off is visible across published detectors, not only in our arms.

## 2026-10-13 Addendum 34 closed on two seeds: (a)+(b) met, (c) not met as written

Seed 20260930: (a) commercial Smoothing-90 6.1%, renders above own original 52.8%; (b) smoothed-genuine false alarms
2.2 / 4.2 / 5.7 / 4.5 / 3.0%; (c) miss rise +19.0 / +20.6 / +17.5 / +9.0 / +12.7 against P0 +26.7 / +6.1 / -11.8 / +18.0 /
+8.1: mid, strong and the Gaussian blend exceed P0 by more than 5. Same pattern as seed 1. AUC with both classes smoothed
0.849 / 0.809 / 0.796 / 0.853 / 0.865 against P0 0.852 / 0.781 / 0.736 / 0.855 / 0.871. Celeb-DF-B seed 1: AUC under
beautification 0.866 (P0 0.860), beauty-only miss rise +14.2 (P0 +17.0), false alarms 5.5%.
Reading for the paper: the class-symmetric smoothing view removes the false accusation of smoothed genuine faces (both
commercial and scripted, including two unseen forms) without the genuine-only shortcut; smoothed forgeries are missed
8-20 points more often than untreated ones at every strength, where the no-exposure baseline instead accuses everything
smoothed. The pre-declared bar (c) compared against that baseline and is reported as not met. Next: the same view in the
full-data three-way model (Addendum 36), since the main model carries the asymmetry.

Correction (2026-10-13): the "renders above their own original" figures quoted for the symmetric arm in the two
Addendum 34 sections above (37.8% and 52.8%) were computed over ALL renders of the service, not over Smoothing-90. The
Smoothing-90 figures, which are what bar (a) names, are 53.7% (seed 20260929) and 51.8% (seed 20260930). Bar (a) is met
either way (band 25-75%). `docs/paper_v2/tables/tab_v4_retouch.tex` and `tab_v4_tradeoff.tex` carry the correct values.

## 2026-10-14 Addendum 35: the symmetric smoothing view under the Effort scheme

Effort scheme from CLIP (clipe5fbg0oyE, seed 20260929) against its reference clipe5fbp0E: (b) smoothed genuine
Celeb-DF-v2 false alarms 2.0 / 4.2 / 6.1 / 7.3 / 4.3% (reference 3.6 / 35.4 / 75.1 / 4.8 / 7.6): met. (a) commercial
Smoothing-90 14.5% at 5% FPR (reference 56.9%) but renders above own original 88.4% (band 25-75%): not met. (c) miss rise
+22.4 / +25.0 / +24.9 / +5.8 / +7.2 against +19.0 / -11.3 / -32.2 / +11.2 / -2.1: not met as written (same cause as in
Addendum 34). Released Effort fine-tuned two epochs (clipe5fbg0oyEi): commercial Smoothing-90 39.9%, above own original
96.6% (reference 55.3%, 98.5%): (a) not met.
Pre-declared reading: neither passes -> the LoRA result stands alone. The view removes the accusation of scripted
smoothing under both schemes and of the commercial service only under LoRA; under the Effort scheme the commercial renders
are still ranked above their originals. The recipe is not scheme-independent.

## 2026-10-14 Addendum 37: fusing a texture-based detector with CADDM (released weights, no training)

`fusion37.json`. CADDM alone on DF40: face swap 0.869 / 0.788, reenactment 0.794 / 0.542 (ff / cdf).
Mean of genuine-quantile scores, texture member -> fusion:
- GenD + CADDM: commercial Smoothing-90 68.7 -> 28.7%; untreated Celeb-DF-v2 video AUC 0.954 -> 0.970, DFD 0.977 -> 0.964;
  DF40 reenactment 0.935 -> 0.942 (ff), 0.828 -> 0.761 (cdf); face swap 0.966 -> 0.955, 0.947 -> 0.914.
- DFD-HR + CADDM: 64.9 -> 25.0%; 0.943 -> 0.963, 0.976 -> 0.964; reenactment 0.932 -> 0.942, 0.698 -> 0.673.
- Effort + CADDM: 43.2 -> 24.6%; 0.930 -> 0.965, 0.972 -> 0.966; reenactment 0.808 -> 0.881, 0.710 -> 0.686.
- ours P0 + CADDM: 54.2 -> 24.4%; 0.938 -> 0.961, 0.981 -> 0.969; reenactment 0.906 -> 0.939, 0.692 -> 0.678.
Min and product rules cut the accusation further (20-24%) and lose more reenactment in the Celeb-DF domain (0.66-0.73).
Pre-declared reading: no rule meets all three conditions for two published pairs. GenD fails the reenactment condition in
the Celeb-DF domain (-0.067); DFD-HR and ours fail the untreated condition on DFD by 0.002 (-0.012 against a bar of 0.010);
Effort fails the halving condition by 3 points. Reported as: fusion moves the operating point; it is not a way out of the
trade-off.
What it does show, descriptive: the accusation of smoothed genuine faces falls by 43-62% without training; untreated
Celeb-DF-v2 AUC of the fusion exceeds both members in all four pairs (+0.016 to +0.035 over the better member);
FF++-domain reenactment is kept or improved in all four; the loss is in Celeb-DF-domain reenactment, where CADDM is at
0.542, and on DFD, where CADDM is 0.06 below the texture members. Renders are still ranked above their own originals in
87-92% of pairs under the mean rule: the fusion lowers the rate at a threshold, not the ordering.

## 2026-10-14 Addendum 36: the main model retrained with the class-symmetric smoothing view (clipe5y, seed 20260929)

Against the current main model clipe5_s20260929:
(i) whole-crop-smoothed genuine Celeb-DF-v2 false alarms 1.0 / 1.6 / 1.7% (was 34.9 / 79.8 / 90.1%): met.
(ii) commercial Smoothing-90 8.1% at 5% FPR, renders above own original 30.0% (was 8.6%, 32.5%): met.
(iii) untreated video AUC Celeb-DF-v2 0.954 (0.947), DFD 0.983 (0.978): met, both higher.
(iv) explanation flip rate donor / SD / SDXL 92.6 / 92.2 / 91.9 (94.0 / 93.6 / 93.5): lower by 1.4 / 1.4 / 1.6, bar 1.0:
     NOT met. The ceiling fell by the same amount (92.6 / 92.1 / 92.0), IoU7 unchanged (0.836 / 0.843 / 0.833).
(v) Celeb-DF-B: scoring in progress.
Also: validation C2 0.871 (0.862); untouched originals of the unseen service called beautified 13.9% (20.8%); frame AUC
with both classes smoothed 0.878 / 0.831 / 0.796 / 0.880 / 0.878 (0.803 / 0.740 / 0.688 / 0.819 / 0.855); miss rise on
smoothed forgeries +28.1 / +33.8 / +34.1 / +12.8 / +3.8 (the old model's -25 to -44 came from accusing everything smoothed).
Pre-declared replacement rule: (iv) fails, so the current main model stays and the asymmetry is stated as a limitation.
The retrained model is reported next to it in every table as the symmetric-view variant; it is not called the main model.

## 2026-10-14 Corrections found while merging the paper (v4), and the remaining Addendum 36 numbers

- Addendum 36 (v): Celeb-DF-B AUC under beautification 0.868 against 0.866: met. Verdict unchanged ((iv) fails).
- DF40 for the symmetric-view variant clipe5y: face swap 0.952 / 0.909, reenactment 0.738 / 0.539 (current main model
  0.952 / 0.905 and 0.718 / 0.502). The reenactment failure is not caused by the asymmetry.
- DF40 for the FF++-only symmetric arm: reenactment 0.871 / 0.796 (FF++ domain, two seeds). P0's third seed is 0.633 in the
  Celeb-DF domain, so P0 spans 0.633-0.720 there; the "further 0.06-0.11" cost quoted earlier for that domain is within the
  seed spread and is withdrawn. The FF++-domain ordering stands.
- "The other three operations are at the 5% floor" holds for our P0 arms, not for every published detector: thirteen of
  sixteen usable detectors are at 3.7-8.1% on whitening, face slimming and eye enlarging at level 90; Effort is at
  9.6-16.8%, UnivFD 11.7% on eye enlarging, DFD-HR 7.7-9.6%.
- Bar (c) of Addendum 34 on the Gaussian blend: seed 2 exceeds P0 by 4.6, not by more than 5; mid and strong bilateral
  exceed on both seeds. Verdict unchanged.
- Miss rise of the symmetric arm under smoothing: 7.6 to 20.6 points over forms and seeds.
- Fusion, product rule: 23.7-27.6% (the "20-24%" quoted above is the minimum rule only).
- GenD and DFD-HR are the highest among the CLIP detectors on "renders above own original"; SRM is higher (99.3%).

## 2026-10-14 Smoothness probe (`../smoothness_probe_20261014/PROBE.md`): no feature-level handle

Hand-designed high-frequency ratios (flat skin / edges, face / background, two bands, colour-noise) on 7,000 images.
Commercially smoothed genuine vs DF40 reenactment separates at AUROC 1.000, but untouched originals vs reenactment also
1.000: the separation is stills (1024 px PNG) vs frames (256 px, H.264), 4-7x in absolute edge energy, not removed by a
common 224 px crop. The feature that encodes the hypothesis (flat-skin vs edge energy) separates a render from its own
original at 0.854: it is a smoothing detector and would accuse, not excuse. Within Celeb-DF, reenactment frames are softer
than genuine ones everywhere in the crop, background included, so "face rendered, background untouched" does not hold.
Pre-declared rule (A >= 0.80 and B <= 0.70 and domain control): B 0.925 and D fail. Direction closed. Paper: one sentence
in Limitations that smoothing and neural rendering show no simple single-image statistic that separates them.

## 2026-10-16 Addendum 44: one deployable threshold per detector (`../review_v4_exps_20261016/FFPP_VAL_THR.md`, `ffpp_val_thr.json`)

Threshold = 95th percentile of P(fake) on the 530 genuine FF++ c23 validation frames (133 videos); no test source used. Cells:
deployable rate [95% cluster CI, threshold fixed] / the source's own 5%-FPR (oracle) rate. FF++ validation also selected our
checkpoints, so our thresholds are, if anything, favourable to us; the threshold's own interval over val videos is wide for
some detectors (ours s1 0.65 [0.51, 0.87], s2 0.94 [0.57, 0.97], SBI 0.29 [0.18, 0.53]), and that is part of the finding.
- Calibration drift on untreated genuine frames is large and detector-specific: SBI calls 38.5% of Celeb-DF-B genuine frames,
  42.7% of DFD and 45.3% of the service's FFHQ originals fake; CADDM 32.9% and LAA-Net 30.9% of the FFHQ originals; our main
  model s1 10.4% (Celeb-DF-B) / 13.2% (Celeb-DF-v2) but 0.4% of the FFHQ originals; s2 4.4 / 5.8 / 0.1%.
- Commercial Smoothing-90 (deployable / oracle): GenD 67.4 / 68.7, DFD-HR 56.2 / 64.9, Effort 31.1 / 43.2, FA 32.5 / 39.7,
  SBI 93.3 / 37.3, LAA-Net 81.0 / 17.2, CADDM 42.3 / 6.3; ours main 0.5 / 8.6 (s2 0.1 / 12.5), symmetric 0.1 / 8.1, binary
  0.2 / 9.1. At a deployable threshold our models accuse almost no commercially smoothed still, the published detectors
  15-93%. Confound stated: our models saw FFHQ originals and two other vendors' renders in training; the published ones saw
  neither, so this is partly "trained on stills of this kind".
- FairBeauty AR renders (deployable / oracle): every detector except NPR accuses more at the deployable rule than or about as
  much as at the oracle (DFD-HR 93.4 / 85.9, GenD 87.3 / 75.6, Effort 75.1 / 67.8, ours main 90.6 / 75.1, binary 82.3 / 79.0;
  NPR 7.0 / 70.4 because its scores saturate). Our main model also calls 19.1% of the untouched FairFace originals fake.
- Celeb-DF-B beautified genuine (deployable / oracle): published 0.1-23.2 / 1.8-14.6; ours s1 16.3 / 9.5, s2 5.7 / 6.7,
  binary 10.5 / 7.4. Beautified forgeries missed: ours s1 28.5 / 40.7 (lower than every published detector at either rule).
- DF40-cdf genuine frames at the deployable rule: DFD-HR 26.6%, GenD 16.6%, FA 14.5%, ours s1 11.6%, binary 5.3%.
- Ranking of the 17 published detectors, oracle vs deployable accused share (Spearman): commercial Smoothing-90 0.29
  (p 0.25), FairBeauty 0.37 (p 0.15), Celeb-DF-B beautified genuine 0.53 (p 0.03). The detector ranking by "accusation of
  beautified faces" is not stable under a change of the threshold rule; the threshold-free paired statistic is the one to lead
  with, as the review says.

## 2026-10-16 Addendum 45: identity-cluster bootstrap (`../review_v4_exps_20261016/IDENTITY_SUMMARY.md`, `identity_boot.json`)

Units: Celeb-DF-B 464 videos -> 58 identities; Celeb-DF-v2 filtered 516 -> 124 (59 celebrities + 65 YouTube-real singletons);
DFD 332 -> 28 actors; DF40-ff 140 identities (DF40-cdf has no identity, kept video). Same statistics, 1000 draws, rng 0 in both
modes. Deviation from the pre-declaration, stated: the "merged X/Y" variant is not usable on Celeb-DF (the swap graph joins all
59 celebrities into 4 components holding every forged video, so draws lose a class); it is reported only where >= 10 clusters
hold forged videos (none of the sources qualifies).
Result: of 456 intervals, 20 change category (contains the null vs excludes it), almost all from "excludes 0" to "contains 0"
at the edge; identity intervals are 0.91x (Celeb-DF-B, narrower because genuine and forged videos of a person move together),
1.06-1.09x (Celeb-DF-v2), 1.00-1.01x (DFD) and 1.30x (DF40-ff, max 2.8x) the width of the video intervals. Changes that touch
the paper:
- Celeb-DF-B: none of our paired AUC_b claims changes. Ours minus Effort / FA / GenD / DFD-HR, identity CI: s1 +0.059
  [0.033, 0.085] / +0.038 [0.016, 0.059] / +0.059 [0.036, 0.081] / +0.028 [0.008, 0.048]; s2 +0.075 [0.052, 0.101] / +0.055
  [0.034, 0.074] / +0.075 [0.053, 0.097] / +0.045 [0.026, 0.063]. This also answers review C5 (paired AUC_b intervals, both
  seeds, exclude 0 under either unit). Binary minus main s1 +0.030 [0.018, 0.042]. CADDM's beauty-only miss change -2.9
  goes from "below 0" to "contains 0".
- Celeb-DF-v2 filtered: main s1 minus GenD AUC_f +0.032, [0.003, 0.060] -> [-0.001, 0.063] (crop); binary and symmetric minus
  GenD (full frame) likewise lose significance; every other ours-minus-published AUC_f interval keeps its category. The
  miss rise under filters of SRM, EffNet-B4 (full frame) and the FF++-only control becomes "contains 0".
- DFD filtered: main s1 minus FA AUC_f +0.020, [0.000, 0.042] -> [-0.004, 0.041].
- DF40-ff: main s1 minus GenD face swap -0.015 [-0.023, -0.007] -> [-0.030, 0.001]; main s2 minus Effort face swap +0.015
  and reenactment -0.028 both -> contain 0; binary s1 minus Effort reenactment +0.034 -> contains 0.
Reading: identity clustering does not change any headline; it removes "significant" from five marginal ours-vs-published
differences (four of them against GenD / FA, all near the boundary) and from three DF40-ff comparisons. Those must be worded
as ties.

## 2026-10-16 Addendum 41: DF40 entire-face synthesis as a class-boundary probe (`../df40_eval_20261012/DF40_EFS41.md`, `df40_efs41.py`), descriptive

Face editing is not on disk and is not scored: `external_data/df40/dataset_json/DF40_all.json` lists e4e (29,126 paths),
styleclip (3,824), CollabDiff (1,993) and starganv2 (3,000), but no folder of any of them exists on C: or N: (checked
2026-10-16 19:50); the `stargan/` folder is not DF40. Scored: sd2.1, DiT, SiT, ddim, pixart, StyleGAN3, 300 per method and
domain (rng 0). Cell = share above the 95th percentile of same-domain DF40 real frames, ff / cdf:

| model | sd2.1 | DiT | SiT | ddim | pixart | StyleGAN3 |
|---|---|---|---|---|---|---|
| Effort | 99.0 / 87.0 | 55.0 / 33.3 | 66.7 / 48.7 | 65.3 / 42.3 | 98.7 / 98.3 | 99.7 / 97.0 |
| Forensics Adapter | 76.0 / 49.0 | 30.0 / 15.0 | 42.7 / 20.3 | 25.0 / 8.3 | 49.0 / 59.0 | 100.0 / 61.3 |
| GenD | 97.7 / 78.0 | 36.3 / 14.3 | 46.7 / 23.3 | 49.7 / 23.3 | 94.3 / 94.0 | 99.7 / 96.3 |
| DFD-HR | 98.3 / 81.7 | 43.0 / 11.7 | 51.0 / 22.0 | 43.0 / 15.0 | 98.3 / 93.3 | 99.7 / 73.0 |
| ours main s1 | 72.0 / 56.3 | 17.7 / 12.3 | 13.3 / 13.3 | 5.3 / 2.0 | 57.7 / 62.7 | 95.3 / 47.3 |
| symmetric-view s1 | 46.0 / 37.7 | 15.7 / 13.7 | 13.0 / 14.0 | 4.7 / 0.3 | 48.7 / 39.0 | 55.7 / 5.3 |
| binary control s1 | 92.0 / 73.0 | 17.0 / 12.7 | 17.0 / 15.3 | 7.7 / 2.7 | 82.0 / 82.3 | 99.3 / 50.7 |

Main model, native three-way decision: ddim is called beautified on 88-89% of images (forged 7-8%), SiT 42-48% beautified,
DiT 30-37% beautified and 34-40% real; sd2.1, pixart and StyleGAN3 are mostly called forged (66-97%).
Reading (descriptive, no bar): entire-face synthesis is where our models are weakest relative to the released CLIP detectors
(every method, both domains, ours below Effort and GenD), and the three-way head files smooth diffusion stills (ddim, SiT)
as beautified rather than forged. That is the class-boundary failure the review asked us to measure: the definition says
forged, the model's "beautified" class absorbs synthesised faces with smooth skin. The symmetric-view variant is the
weakest on this probe (StyleGAN3/cdf 5.3%). Confound as declared: generator stills vs H.264 frames. Closed.

## 2026-10-16 Addendum 43: Instagram AR filters as a fourth source (`../review_v4_exps_20261016/AR_SOURCE.md`, `ar_source.json`)

FairBeauty: 2,927 pairs (unit = pair). B-LFW: 3,000 of 11,891 registered pairs (amendment; 2,016 LFW identities in the sample,
unit = identity). Threshold = 95th percentile of the source's originals, re-estimated per draw. Correction to the
pre-declaration text: FairBeauty's 11 render folders hold 8 distinct filters (folders 8-10 repeat Pretty / hary beauty /
Shiny foxy, folder 10 has one pair); per-filter numbers in `ar_source.json` are by folder.

| model | FB accused % [CI] | FB AUROC | FB render>orig % | FB-JPEGq90 accused | B-LFW accused % [CI] | B-LFW AUROC | B-LFW render>orig % |
|---|---|---|---|---|---|---|---|
| Xception | 24.3 [21.7, 28.3] | 0.793 | 85.7 | 18.9 | 53.3 [49.4, 57.2] | 0.876 | 95.1 |
| EfficientNet-B4 | 22.0 [19.6, 24.2] | 0.751 | 83.1 | 18.1 | 39.9 [36.0, 43.8] | 0.859 | 96.3 |
| F3Net | 26.1 [23.3, 29.6] | 0.751 | 83.3 | 17.1 | 49.0 [45.9, 53.4] | 0.869 | 95.3 |
| SPSL | 10.7 [9.1, 13.2] | 0.691 | 77.2 | 10.3 | 12.0 [10.5, 14.3] | 0.684 | 82.1 |
| UCF | 37.3 [32.8, 41.1] | 0.820 | 90.4 | 29.3 | 71.5 [68.5, 73.7] | 0.926 | 97.8 |
| RECCE | 41.5 [38.8, 44.6] | 0.815 | 89.8 | 28.7 | 78.4 [75.2, 80.5] | 0.941 | 97.9 |
| CORE | 25.2 [23.4, 28.1] | 0.776 | 86.5 | 18.4 | 58.8 [56.5, 62.5] | 0.885 | 95.3 |
| SRM | 26.8 [24.1, 29.7] | 0.787 | 85.6 | 17.1 | 58.1 [55.1, 61.1] | 0.895 | 96.7 |
| SBI | 22.8 [20.2, 24.9] | 0.671 | 70.0 | 20.0 | 35.4 [33.3, 38.2] | 0.745 | 81.9 |
| UnivFD | 63.3 [59.5, 66.5] | 0.900 | 97.2 | 54.7 | 48.6 [45.9, 52.3] | 0.855 | 96.6 |
| NPR | 70.4 [63.8, 78.5] | 0.960 | 97.0 | 4.5 | 0.0 [0.0, 0.0] | 0.468 | 2.8 |
| Effort | 67.8 [64.2, 70.5] | 0.905 | 96.0 | 66.1 | 74.7 [71.8, 76.6] | 0.942 | 98.6 |
| Forensics Adapter | 63.9 [61.8, 66.4] | 0.877 | 95.3 | 66.9 | 76.9 [75.1, 79.1] | 0.925 | 98.9 |
| GenD | 75.6 [73.4, 78.8] | 0.949 | 97.8 | 74.0 | 96.6 [95.7, 97.8] | 0.992 | 99.9 |
| DFD-HR | 85.9 [83.8, 87.8] | 0.966 | 98.8 | 87.1 | 95.3 [94.2, 96.2] | 0.988 | 99.7 |
| CADDM | 15.4 [13.1, 17.9] | 0.700 | 76.4 | 10.4 | 35.8 [32.9, 39.9] | 0.807 | 86.2 |
| LAA-Net | 27.6 [24.7, 30.1] | 0.667 | 68.9 | 20.3 | 48.4 [45.5, 50.4] | 0.779 | 80.7 |
| ours main s1 | 75.1 [72.7, 77.6] | 0.945 | 98.4 | 64.3 | 86.7 [83.5, 88.9] | 0.975 | 99.4 |
| symmetric-view s1 | 77.4 [75.5, 79.6] | 0.950 | 98.6 | 67.3 | 93.6 [91.7, 95.1] | 0.988 | 99.8 |
| binary control s1 | 79.0 [76.2, 81.4] | 0.954 | 98.6 | 73.4 | 89.0 [87.5, 91.6] | 0.978 | 99.4 |

Paired, ours main s1 minus Effort / FA / GenD / DFD-HR, accused share: FairBeauty +7.4 [+4.4, +11.5] / +11.2 [+8.2, +14.2] /
-0.5 [-3.9, +2.5] / -10.7 [-13.2, -7.8]; B-LFW +11.9 [+8.2, +15.4] / +9.8 [+6.1, +12.2] / -9.9 [-13.2, -7.8] / -8.6 [-11.8, -6.3].

Reading against the pre-declared rule:
- "Accuses" (lower bound > 5.0%): 17/17 published detectors on FairBeauty, 16/17 on B-LFW (NPR: 0.0%, its scores saturate
  on 112x112 renders and it ranks the originals above the renders, 2.8%); 16 accuse on both sources >= 12, so **the
  accusation of beautified genuine faces replicates on Instagram AR filters**. "Ranks renders above originals": 17/17 and 16/17.
- Pipeline sensitivity (FairBeauty, both sides JPEG q90): only NPR loses more than half its accused share (0.064x); every
  other detector keeps 0.64-1.05x, ours 0.86-0.93x. The effect is not mainly JPEG recompression, but the AR engine's own
  capture path is still confounded with the beautification (stated caveat: these numbers are an upper bound on the
  beauty-specific effect).
- Consistency with the commercial source: Spearman over the 17, FairBeauty accused vs commercial Smoothing-90 accused,
  rho 0.145 (p 0.58), reported, no bar. Not pre-declared, also computed: B-LFW vs commercial rho 0.591 (p 0.013). Which
  detectors accuse most depends on the source; that every detector accuses does not.
- Our models are not exempt: on AR renders they accuse as much as the strongest CLIP detectors (above Effort and FA, tied
  with GenD on FairBeauty, below DFD-HR), unlike on the commercial service where they accuse almost nothing (Addendum 44).
  The paper cannot say our training removes the accusation of beautified faces in general; it removes it on the
  commercial vendor family it saw (FFHQ originals + Tencent/Megvii renders), not on AR filters.
Addendum 42 seeds are added below when scored (the 42 chain runs `ar_source.py score fb|fbj|blfw` for them and re-analyses).

## 2026-10-16 Addendum 38: smoothed forgeries and smoothed genuine faces, 17 published detectors and our arms (`SMOOTH38.md`, `smooth38.json`, `smooth_probe38.py`)

Celeb-DF-v2 test, our crop, every 4th frame: 4,016 frames (1,348 genuine, 2,668 forged, 513 videos). FaceLandmarker found a
face on every frame, so the face-local forms use all frames (0 left out). Threshold = 95th percentile of untreated genuine.
Sanity check passed: every one of our 12 arms reproduces `smooth_evasion2_*.npz` on the five old forms (max |frame AUC
difference| 0.0000 <= 0.003). Cells: false alarms on smoothed genuine % (miss rise on smoothed forgeries, pp); class A =
accuses, L = lets through, A+L = both, - = neither.

| model | bil9 | bil15 | bil21 | median5 | gblend | face-local 0.06 | face-local 0.12 |
|---|---|---|---|---|---|---|---|
| Effort | 5.8 (+12.0) L | 27.1 (-9.1) A | 54.5 (-27.4) A | 11.3 (-2.0) A | 9.3 (-9.4) A | 87.8 (-40.9) A | 99.9 (-41.3) A |
| Forensics Adapter | 27.7 (-16.4) A | 59.9 (-29.6) A | 75.3 (-35.3) A | 18.8 (-8.2) A | 10.5 (-5.2) A | 95.8 (-42.8) A | 100.0 (-42.9) A |
| GenD | 32.6 (-24.9) A | 81.7 (-38.4) A | 93.7 (-39.5) A | 28.7 (-20.0) A | 18.4 (-14.8) A | 96.1 (-39.9) A | 100.0 (-39.9) A |
| DFD-HR | 21.7 (-13.4) A | 79.8 (-41.3) A | 96.5 (-45.5) A | 17.8 (-7.8) A | 19.2 (-16.7) A | 99.3 (-45.7) A | 100.0 (-45.7) A |
| CADDM | 10.8 (+16.9) A+L | 61.4 (-32.9) A | 82.6 (-48.2) A | 4.5 (+26.2) L | 6.4 (+0.1) A | 88.5 (-54.8) A | 99.9 (-57.3) A |
| UCF | 63.4 (-58.5) A | 24.3 (+3.3) A | 12.8 (+16.9) A+L | 23.1 (-23.3) A | 19.4 (-21.6) A | 89.3 (-72.2) A | 98.4 (-73.7) A |
| UnivFD | 7.9 (+2.9) A+L | 40.8 (-27.3) A | 71.4 (-57.0) A | 8.2 (+2.8) A+L | 3.0 (+8.4) L | 13.9 (-17.6) A | 55.2 (-54.6) A |
| other 10 published (range) | 27-100 A | 63-100 A | 61-100 A | 14-92 A | 8-99 A | 64-100 A | 78-100 A |
| P0 s1 / s2 / s3 | 0.8 / 1.6 / 2.3 L | 16.8 / 18.2 / 11.3 A(+L) | 39.6 / 42.9 / 25.2 A | 1.5 / 1.9 / 3.0 L | 5.5 / 4.4 / 4.9 L | 95.8 / 95.8 / 96.3 A | 100 / 100 / 100 A |
| P1 smoothing only s1 | 0.0 (+56.4) L | 0.0 (+56.4) L | 0.0 (+56.4) L | 0.4 (+40.0) L | 4.0 (+10.8) L | 0.4 (+41.5) L | 0.0 (+55.1) L |
| P2 s1 / s2 | 3.0 / 2.7 L | 31.8 / 21.1 A | 49.1 / 36.1 A | 2.5 / 3.1 L | 3.3 / 4.5 L | 38.6 / 34.4 A | 74.5 / 77.6 A |
| P2 symmetric s1 / s2 | 2.4 / 2.2 L | 5.0 / 4.2 L | 6.1 / 5.7 L | 4.5 / 4.5 L | 3.6 / 3.0 L | 54.1 / 37.8 A | 98.7 / 91.5 A |
| P3 forged only s1 | 59.6 (-34.6) A | 99.5 (-38.4) A | 100.0 (-38.5) A | 18.8 (-9.3) A | 6.2 (+3.2) L | 98.1 (-38.5) A | 100.0 (-38.5) A |
| main s1 | 34.9 (-25.1) A | 79.8 (-42.3) A | 90.1 (-44.3) A | 8.1 (+4.5) A+L | 5.2 (+5.4) L | 5.8 (+17.6) L | 44.5 (-14.1) A |
| symmetric-view s1 | 1.0 (+28.1) L | 1.6 (+33.8) L | 1.7 (+34.1) L | 2.4 (+12.8) L | 5.3 (+3.8) L | 37.9 (-24.9) A | 80.2 (-36.9) A |
| binary control s1 | 9.9 (+0.7) A | 35.5 (-15.4) A | 45.6 (-15.0) A | 4.7 (+11.9) L | 5.4 (+6.2) L | 51.6 (-32.0) A | 84.5 (-34.0) A |

Published detectors, classes per form: bil9 accuses 14 + both 2 + lets through 1 (Effort); bil15 accuses 17; bil21 accuses 16
+ both 1 (UCF); median5 accuses 15 + both 1 + lets through 1 (CADDM); gblend accuses 16 + lets through 1 (UnivFD); **both
face-local forms: accuses 17/17**. NPR saturates (100% false alarms at every whole-crop strength), flagged as declared.

Reading (descriptive, against the stated expectation):
- The expectation holds: the FF++-trained published detectors accuse whole-crop-smoothed genuine frames at mid / strong
  strength (17/17 and 17/17 counting "both") and almost never let smoothed forgeries through (only UCF at bil21, CADDM and
  UnivFD at mild forms, Effort at bil9). Our P0 behaves the same, as predicted.
- New: face-local skin smoothing (bilateral inside the face hull, background untouched) is accused by all 17 published
  detectors, more often than whole-crop smoothing at matched visible strength (CLIP four: 88-99% at frac 0.06, 100% at
  0.12; UnivFD is the mildest at 13.9%). Smoothing the skin alone is enough to be called forged; the background is not
  what carries the signal.
- Our arms keep the exposure sign: genuine-only exposure (P1) lets every form through with no false alarms; forged-only (P3)
  accuses every form; P0 / P2 / both-class views sit in between. The symmetric arms (P2 symmetric, symmetric-view variant)
  remove the accusation for every whole-crop form but **not** for face-local smoothing (38-99% false alarms) - the
  smoothing view they were trained with does not cover skin-only smoothing. The main model is the odd one: it accuses
  whole-crop bilateral strongly (35-90%) but passes face-local 0.06 (5.8%, miss rise +17.6) and accuses face-local 0.12 at
  44.5%; this is the only model in the table whose face-local false alarms are below its whole-crop ones.
- Separability with both classes smoothed (AUC): published 0.42-0.89 depending on form, collapsing toward 0.5 at bil21 for
  most CNNs; ours P2 / symmetric / binary keep 0.75-0.89 except face-local 0.12 (0.55-0.78).

## 2026-10-16 Addendum 39: dose response of the four released CLIP detectors (`DOSE39.md`, `dose39.json`)

Genuine Celeb-DF-v2 frames of the Addendum 38 list (1,348; 1000 video-cluster draws). Cells: median logit shift
(z1 - z0) [95% CI] / shift in units of the detector's forged-minus-genuine gap / mean |cos(dF, w1 - w0)|.

| detector (gap) | vignette 0.1 | vignette 0.8 | face-local 0.03 | face-local 0.12 | bil9 | bil21 | dose: vignette / face-local / bilateral |
|---|---|---|---|---|---|---|---|
| Effort (2.30) | -0.08 [-0.09,-0.06] / -0.03 / 0.04 | -0.21 [-0.25,-0.16] / -0.09 / 0.04 | +2.40 [2.20,2.56] / 1.04 / 0.17 | +4.33 [4.18,4.43] / 1.88 / 0.18 | +0.69 / 0.30 / 0.05 | +2.28 / 0.99 / 0.10 | no / yes / yes |
| Forensics Adapter (3.82) | -0.08 / -0.02 / 0.42 | -0.36 [-0.43,-0.30] / -0.09 / 0.44 | +4.59 [4.33,4.87] / 1.20 / 0.64 | +9.79 [9.52,10.00] / 2.56 / 0.69 | +1.80 / 0.47 / 0.56 | +4.73 / 1.24 / 0.63 | no / yes / yes |
| GenD (2.89) | -0.07 / -0.03 / 0.05 | -0.36 [-0.44,-0.28] / -0.13 / 0.06 | +3.38 [3.21,3.60] / 1.17 / 0.22 | +5.53 [5.29,5.70] / 1.91 / 0.27 | +1.82 / 0.63 / 0.12 | +4.49 / 1.55 / 0.22 | no / yes / yes |
| DFD-HR (2.05) | -0.00 [-0.01,+0.01] / 0.00 / 0.05 | +0.07 [+0.04,+0.10] / 0.03 / 0.05 | +3.96 [3.81,4.08] / 1.93 / 0.33 | +6.06 [5.95,6.18] / 2.96 / 0.39 | +0.90 / 0.44 / 0.12 | +3.45 / 1.68 / 0.27 | yes (marginal) / yes / yes |

Shares rising: face-local >= 97.9% at every level for all four; vignette 18-60%. Share above the 5%-FPR threshold:
face-local 0.03 already 61-89%, 0.12 99.9-100%.
Reading against the rule: **face-local skin smoothing shows a dose response in 4/4** (and whole-crop bilateral in 4/4), so
the mechanism section may extend "genuine pushed along the forged direction" to skin smoothing for the published CLIP
detectors. The weakest face-local level (frac 0.03) already moves genuine frames by 1.0-1.9 forged-genuine gaps, i.e.
past the forged mean. The vignette alone does not: Effort, FA and GenD move the other way (genuine looks more genuine,
-0.2 to -0.4 logit at strength 0.8); DFD-HR passes the rule only formally (mean shifts -0.01 to -0.07 with the top-level
median +0.07, 3% of its gap). So for published detectors the colour-filter / vignette part of the mechanism is not
supported by the vignette term in isolation; smoothing is the operative edit. The feature shift is mostly off the head
direction (|cos| 0.04-0.39) except for Forensics Adapter's 192-d head input (0.42-0.69), as expected for a small MLP input.

## 2026-10-16 Addendum 40: forged-only exposure (P3, `clipe5fbp3_s20260929`), the missing cell (`p3_readout40.json`, `RESULTS_clipe5fbp3_s20260929.md`)

Trained on Ubuntu (`train_ru5.py --binary --ffpp-only --beauty fake`, seed 20260929), checkpoint by FF++ val AUC, evaluated by
the exposure-arm chain (`run_add40_chain.sh`); the DFD crop filter source, missing from that chain, was scored separately
(`FSRC=dfd`) and re-analysed. Seed 20260929 throughout; one seed.

| arm (views go to) | Smoothing-90 accused % [CI] | S-90 > own original % | smoothed-genuine FA bil9 / bil15 / bil21 / med5 / gblend | face-local FA 0.06 / 0.12 | CDF-B FA beautified genuine / miss change beautified forged | CDF-v2 filters FA_f crop (d_miss) | DFD filters FA_f crop (d_miss) |
|---|---|---|---|---|---|---|---|
| P0 (none) | 54.2 [50.5, 58.3] | 98.5 | 0.8 / 16.8 / 39.6 / 1.5 / 5.5 | 95.8 / 100 | 5.1 / +23.3 | 18.8 (+4.4) | 5.8 (+8.5) |
| P1 (genuine only) | 3.7 [2.9, 4.4] | 43.5 | 0.0 / 0.0 / 0.0 / 0.7 / 4.7 | 0.4 / 0.0 (P1 smoothing only) | 4.6 / +26.7 | 2.8 (+24.0) | 3.4 (+15.2) |
| P2 (both) | 11.7 [9.7, 14.3] | 84.1 | 3.0 / 31.8 / 49.1 / 2.5 / 3.3 | 38.6 / 74.5 | 5.6 / +13.9 | 10.8 (+3.2) | 6.9 (+3.8) |
| **P3 (forged only)** | **63.8 [59.1, 67.8]** | 99.2 | **59.6 / 99.5 / 100.0 / 18.8 / 6.2** | 98.1 / 100 | **24.6 / +1.0** | **47.2 (-25.1)** | **23.2 (-6.6)** |

P3 minus P0, Smoothing-90: **+9.6 [+6.0, +13.4]**; P3 minus P2: +52.1 [+47.5, +55.8].
Reading against the pre-declared rule: (i) requires the P3-P0 interval not wholly below -5 (it is wholly above 0) and P3's
false alarms on mid and strong whole-crop-smoothed genuine frames not lower than P0's (99.5 vs 16.8, 100.0 vs 39.6). Both
hold; (ii) does not (63.8 > 15). **Reading (i): the sign rule is complete** - genuine-only views lower the accusation and
open evasion, forged-only views keep (here raise) the accusation and close evasion, both classes sit in between. P3 is the
mirror image of P1 on every beautification source: smoothed / filtered / beautified forgeries are caught more often than
untreated ones (miss change -25.1 Celeb-DF-v2 filters, -6.6 DFD filters, +1.0 Celeb-DF-B vs +23.3 for P0), and the price is
paid by genuine faces (Celeb-DF-B beautified genuine called fake 24.6% vs 5.1%, Celeb-DF-v2 filtered genuine 47.2% vs 18.8%).
One seed, stated.
Costs (untreated): Celeb-DF-v2 video AUC 0.944 (P0 0.938, P2 0.918); DFD v3 video AUC 0.982 (P0 0.981); Celeb-DF-B untreated
AUC 0.943, beautified 0.857 (P0 0.927 / 0.860); DF40 face swap ff / cdf 0.970 / 0.937, reenactment ff / cdf 0.870 / 0.753
(P0 0.981 / 0.925, 0.906 / 0.692; P2 0.942 / 0.907, 0.809 / 0.644). P3 costs nothing on untreated detection; it is the
best of the four arms on DF40-cdf reenactment, consistent with "the reenactment loss follows smoothing exposure of genuine
faces" (2026-10-13 entry), which P3 never receives. Commercial service (blind): balanced 45.0, Smoothing-90 sent to forged
93.9% by the native decision.

## 2026-10-17 Addendum 42: second seeds of the symmetric-view variant and the binary control (`../review_v4_exps_20261016/READOUT42.md`, `readout42.json`)

clipe5y_s20260930 (`--sym-smooth`, C2 selection, epoch 5) and clipe5b_s20260930 (`--binary`, FF++ val AUC selection), trained
on Ubuntu, evaluated by `run_add42_chain.sh` (run_add6_eval + smooth_evasion + four filter sources + DFD v3 + DF40 + Celeb-DF-B
+ AR sources + FF++-val thresholds; identity bootstrap and readout rerun at the end). All comparisons within seed, paired
video-cluster bootstrap (1000 draws, rng 0).

(A) Addendum 36 replacement criteria, symmetric-view variant vs main, same seed:

| criterion | seed 20260929 | seed 20260930 | replicated |
|---|---|---|---|
| (i) smoothed-genuine FA bil9/15/21 <= 15 | 1.0 / 1.6 / 1.7 (main 34.9 / 79.8 / 90.1): met | 3.8 / 5.9 / 8.4 (main 22.0 / 84.1 / 96.1): met | yes |
| (ii) commercial S-90 <= 15, above own in [25, 75] | 8.1, 30.0: met | **17.8**, 46.2 (main 12.5, 41.3): **not met** | no |
| (iii) CDF-v2 / DFD video AUC not lower by > 0.010 | +0.007 [+0.000, +0.015] / +0.006 [-0.000, +0.012]: met | +0.007 [-0.002, +0.016] / +0.006 [+0.002, +0.012]: met | yes |
| (iv) explanation flip not lower by > 1.0 | 92.6 / 92.2 / 91.9 vs 94.0 / 93.6 / 93.5: **not met** | 93.6 / 93.0 / 92.6 vs 90.9 / 90.4 / 90.2: met | no |
| (v) Celeb-DF-B AUC_b not lower by > 0.010 | 0.868 vs 0.866: met | 0.888 vs 0.883: met | yes |

Seed-1 verdict "(iv) fails, the main model stays" replicates as an outcome (seed 2 also fails the rule, so the main model
stays) but not in its reason: seed 2 fails (ii) and passes (iv). The flip-rate cost of the symmetric view is therefore
seed noise (seed 2 the variant is 2.4-2.7 points higher), while the cost on commercial Smoothing-90 is seed-dependent
(8.1 vs 8.6 on seed 1, 17.8 vs 12.5 on seed 2). The one effect that holds on both seeds is the intended one: the symmetric
view removes the accusation of whole-crop-smoothed genuine frames (FA <= 8.4% vs 22-96%) at no cost to untreated detection.

(B) Binary control minus main, same seed (pre-declared list):

| quantity | seed 20260929 | seed 20260930 | category s1 / s2 |
|---|---|---|---|
| CDF-v2 frame AUC | +0.023 [+0.011, +0.034] | +0.036 [+0.023, +0.048] | above / above: replicated |
| CDF-v2 video AUC | +0.009 [-0.004, +0.024] | +0.017 [+0.003, +0.031] | contains 0 / above: seed-dependent |
| DFD frame AUC | +0.020 [+0.013, +0.028] | +0.006 [-0.000, +0.012] | above / contains 0: seed-dependent |
| DFD video AUC | +0.010 [+0.003, +0.017] | -0.003 [-0.011, +0.005] | above / contains 0: seed-dependent |
| Celeb-DF-B AUC under beautification | +0.030 [+0.014, +0.045] | +0.021 [+0.009, +0.034] | above / above: replicated |
| DF40-ff reenactment (video AUC mean) | +0.124 [+0.113, +0.135] | +0.076 [+0.066, +0.086] | above / above: replicated |
| DF40-cdf reenactment | +0.145 [+0.133, +0.157] | +0.139 [+0.128, +0.150] | above / above: replicated |

Reading: review D3's "binary >= main" replicates on Celeb-DF-v2 frames, Celeb-DF-B under beautification and both DF40
reenactment domains (the large ones, +0.08 to +0.15); on DFD the advantage is seed-dependent (seed 2 ties), and on
Celeb-DF-v2 video it appears only on seed 2. No bar changed.

Seed 2 on the other review_v4 sources (for Addenda 43 and 44, now in `AR_SOURCE.md` and `FFPP_VAL_THR.md`):
- AR filters, accused share at 5% FPR of originals: symmetric s2 FairBeauty 75.6, JPEG-q90 71.8, B-LFW 94.3; binary s2 82.1 /
  73.2 / 90.3 (seed 1: 77.4 / 67.3 / 93.6 and 79.0 / 73.4 / 89.0). The Addendum 43 picture holds on seed 2: our models
  accuse AR renders as much as GenD and more than Effort / FA.
- Deployable FF++-val threshold, commercial Smoothing-90: main s2 0.1%, symmetric s2 0.1%, binary s2 0.1% (oracle 12.5 / 17.8 / 6.5).
- Main seed 2 was scored on `smooth_evasion` (within-seed comparisons above) but not on the AR sources (not in the chain).

## 2026-10-17 Addendum 46 (SIC) launched: smoke checks only, no result read

Arms clipe5z (factorised, primary) and clipe5bz (binary, secondary), seeds 20260929 / 20260930, sequential on gsplat-ubuntu
(`run_add46_queue2.sh`), evaluated locally by `run_add46_chain.sh` -> `readout46.py`. Code `train_ru5.py` md5 242e4753
(`train_ru5_add46.diff`). Checks before the full runs:
- data path (`smoke_add46_data.json`, 150 items): main item stream bit-identical with and without the option; x_s differs from
  x for every item; x_s face-local for 100% of genuine items, 43% of beautified and 40% of forged items (whole-crop otherwise);
  the montage shows the face-local change confined to the face.
- 400-step smoke of clipe5z on Ubuntu (0.61 s/it, 23.9 GiB): L_cons per 50-step window 0.060 / 0.039 / 0.012 / 0.024 / 0.028 /
  0.040 / 0.041 / 0.036 while the label loss fell 1.38 -> 1.03; not monotone: it falls during warm-up and settles near 0.04 as
  the forged logit starts to separate the classes. Scale (`smoke_add46_lcons_ref.log`): on the same kind of training items,
  models trained without the term have L_cons 45.6 (clipe5b), 31.5 (clipe5), 24.6 (clipe5y), i.e. an rms change of the forged
  logit of 5-7 under smoothing, about one standard deviation of the logit over items.

## 2026-10-17 Rounding note and paper v6b presentation (no new result)

Four numbers were quoted with different last digits here and in paper v6 because a value already rounded to four (or three)
decimals was rounded again. Recomputed from the score files with the code that first produced them
(`make_tables_v4.video_auc`, the bootstrap of `../alipair_zeroshot_20260929/exposure_ali.py`, `smooth_probe38.analyse`,
`../review_v4_exps_20261016/readout42.paired`), stated to three decimals here and in paper v6b:

| quantity | full precision | three decimals | earlier here / in v6 |
|---|---|---|---|
| P3 untreated Celeb-DF-v2 video AUC (`cdf_filtered_scores_clipe5fbp3_s20260929.npz`) | 0.943486 | **0.943** | 0.944 (Addendum 40 entry, from the stored 0.9435) / 0.943 |
| P3 Smoothing-90 accused at the 5%-FPR rule, 95% CI over originals | 63.7557 [59.0498, 67.7839] | **63.756 [59.050, 67.784]** | 63.8 [59.1, 67.8] / 63.8 [59.0, 67.8] |
| Effort, vignette 0.8, median logit shift on genuine frames (`smooth38_effort.npz`) | -0.205236 | **-0.205** | -0.21 / -0.20 |
| binary minus main, DFD video AUC, seed 20260929 (`dfd_v3_scores_*.npz`) | +0.009487 | **+0.009** | +0.010 (Addendum 42 table, from the stored 0.0095) / +0.009 |

Same kind of discrepancy found while checking: Forensics Adapter, face-local 0.03, median logit shift is stored as 4.585 in
`dose39.json` (Addendum 39 table +4.59, paper v6 +4.58); paper v6b states +4.585 and prints the dose table at three decimals. No
reading or bar changes.

Paper v6b (`docs/paper_v2/main_v6b.tex`, `docs/paper_v2/V6B_CHANGES.md`): the full-data model trained with the forgery head only
(clipe5b, two seeds) is the first, detection-reference row of every detection table, and the full model (clipe5, three classes +
operation scores) is reported beside it. The system still outputs three classes and four operation scores, with the forgery
decision read from the forged logit; the explanation results are those of the full model's evidence head. The ordering was chosen
after both seeds were read. `../review_v4_exps_20261016/IDENTITY_SUMMARY.md` was regenerated from `identity_boot.json` with the
interval set of `identity_boot.py`: 24 of 563 intervals change category (the first-run summary, 20 of 456, is kept as
`IDENTITY_SUMMARY_firstrun_20261016.md`).


## 2026-10-18 Addendum 46 first readout: SIC removes the skin-smoothing accusation and costs detection (`READOUT46.md`)
clipe5z_s20260929 (factorised, lambda = 1, C2-selected epoch): face-local smoothing FA 4.5 / 4.3 % (fl06 / fl12; the binary
control accuses 51.6 / 84.5 %, the symmetric-view model 37.9 / 80.2 %), bilateral 5.6-7.2 %, median 6.9, Gaussian blend 5.6,
commercial Smoothing-90 7.6 % [6.2, 9.1] at the 5 %-FPR rule: bars (1) and (2) pass. Costs: miss rise +5.9 / +10.2 at fl06 /
fl12 (bar 3' fails by 0.9 and 5.2 points); CDFv2 video 0.876 vs 0.956 binary / 0.947 full / 0.954 symmetric view (bar 4
fails); Celeb-DF-B 0.845 vs 0.866 (bar 5 fails); DF40 reenactment -0.18 ff / -0.04 cdf vs binary (bar 6 fails); FF++
in-domain forgery recall 69.8 % vs 90.9 % for the full model. Attribute heads unchanged (balanced 74.0 vs 73.3; presence
TP eye .23 / jaw .31 / white .39 / smooth .86; part-forgery IoU 0.82-0.84).
Reading: the consistency term at lambda = 1 makes the forgery logit smoothing-invariant and with it removes part of the
forgery signal itself (texture loss is a real cue on FF++ c23 and on swaps). The symmetric view alone (lambda = 0) keeps
detection and still accuses. The trade-off between the two is the open quantity; Amendment 3 trains the binary arm at
lambda 0.3 and 0.1 next to the lambda 0 control, with the claim rule fixed before the runs.

## 2026-10-18 Band-energy analysis (`bandenergy_20261018/BANDENERGY.md`): high-frequency loss does not explain the accusation
400 genuine Celeb-DF frames, seven Addendum 38 forms plus commercial Smoothing-90 (200 FFHQ pairs). The hypothesis "FA tracks
the high-frequency energy removed inside the face" fails: pooled Spearman between texture loss (E_hf, r > 0.25 c/px) and FA
is +0.06 (7 forms x 17 detectors); Gaussian blend removes the most energy (0.94) and is accused least (3-35 %), face-local
0.12 removes less (0.72) and is accused ~100 %. What does track FA: (i) spatial confinement to the face (fl06 vs bil9, same
kernel: +28 points, 16/17 detectors, p = 5e-4); (ii) edge-preserving flattening vs uniform blur at equal energy loss (bil21
vs gblend: +67 points, 16/17); (iii) only the low band 0.02-0.12 c/px correlates (rho +0.45), which bilateral and face-local
forms remove and Gaussian blend does not; (iv) mean absolute pixel change in the hull is the best single statistic (rho
+0.49, 12/17 detectors >= 0.5). Reading for the paper: the shared cue is the beautification signature itself (skin flattened
with edges kept, inside the face), not blur; this is consistent with Addendum 31/32 (Gaussian blur and JPEG views do not
remove the accusation) and strengthens the case that the operator in the training view has to be skin smoothing. Figures
fig_bandenergy.{pdf,png} (main or supplement) and fig_bandenergy_supp.

## 2026-10-18 SIC-sg seed 1 and the lambda = 0 control (`READOUT46.md`)
Stop-gradient SIC (clipe5bzsg s1): face-local FA 5.8 / 4.4 % (binary control 51.6 / 84.5), whole-crop bilateral 4.8-6.2 %,
median 9.1 %, Gaussian blend 5.3 %, commercial Smoothing-90 2.1 % [1.5, 2.7] (binary control 40.6 %); smoothed-forgery miss
rise +0.2 at fl06, +9.7 at fl12 (bar 3' fails at fl12). Untreated: CDFv2 video 0.907 vs 0.956 (symmetric-penalty SIC 0.876),
DFD 0.986 vs 0.987 (within band), Celeb-DF-B 0.835 vs 0.866, DF40 reenactment ff 0.768 vs 0.842 (symmetric 0.663), cdf 0.599
vs 0.647. The view-only control (lambda = 0) keeps detection (CDFv2 0.943, DFD 0.975, Celeb-DF-B 0.891, DF40 ff 0.835) and
still accuses face-local smoothing (53.9 / 91.8 %). Reading: the consistency term is both the cure and the cost; the
stop-gradient halves the cost but does not remove it. Next: lambda 0.3 / 0.1 on the stop-gradient family (Amendment 6) and
the running seed 2 and FF++-only arms.

## 2026-10-18 evening: SIC-sg seed 2, AR filters, Amendments 7-8
SIC-sg s2 (clipe5bzsg_s20260930): FA bil 5.7-7.3 %, median 8.5, gblend 5.6, fl06 6.2, fl12 5.5, Smoothing-90 12.3 % (bars 1-2 pass);
miss rise fl12 +6.1 (3' fails by 1.1); CDFv2 video 0.844 vs 0.963 binary s2, DFD 0.968 vs 0.978, Celeb-DF-B 0.804, DF40 ff
0.746 vs 0.856, cdf 0.578 vs 0.698 (4-6 fail). Two seeds agree: the accusation is removed, detection pays 0.05-0.12 CDFv2.
AR filters (ar_source.py, FairBeauty 2,927 pairs, accused at 5 % FPR): SIC-sg s1 67.7 % (binary control 79.0, main 75.1,
lambda-0 control 83.3, SIC factorised 44.1; Effort 67.8, Forensics Adapter 63.9, GenD 75.6, DFD-HR 85.9). SIC lowers the AR
accusation by 11 points against its control but leaves it at Effort's level: AR renders stay a limitation.
Amendment 7 (Gaussian operator ablation, clipe5bzsgG) training on cvlab-103 GPU0; Amendment 8 (one-sided consistency,
clipe5bzsgh) queued on the local GPU after clipe5bzsgl03.

## 2026-10-18 22:30 symmetric-penalty lambda 0.3 and binary lambda 1 readouts (`READOUT46.md`)
clipe5bzl03 (symmetric penalty, lambda 0.3): FA fl06 4.7 / fl12 4.6 / bil15 8.1 / Smoothing-90 9.9 (bars 1-2 pass); miss rise fl12
+12.4; CDFv2 video 0.900 vs 0.956, DFD 0.966, Celeb-DF-B 0.860 vs 0.866, DF40 ff 0.755 vs 0.842 (4-6 fail). clipe5bz
(symmetric, lambda 1, binary): FA 4.9 / 4.2 / 7.0 / 7.1; CDFv2 0.866, DFD 0.956, Celeb-DF-B 0.837, DF40 ff 0.702.
Reading: from lambda 1 to 0.3 the accusation stays at 4-10 % (the fix saturates early) while the detection cost shrinks
(CDFv2 0.866 -> 0.900, DF40 0.702 -> 0.755). The curve is steep in FA and shallow in cost at small lambda; lambda 0.1 (Ubuntu,
training) and a lambda 0.03 point (Amendment 9) locate where FA starts to return.

## 2026-10-19 morning readouts (`READOUT46.md`): lambda 0.1 (both families), FF++-only SIC-sg, Gaussian ablation
lambda 0.1, symmetric penalty (clipe5bzl01): FA fl06 4.3 / fl12 3.3 / bil15 7.1 / Smoothing-90 9.5; miss rise fl12 +18.6; CDFv2
0.921 vs 0.956, DFD 0.974, Celeb-DF-B 0.882 (> main 0.866, bar 5 passes), DF40 ff 0.760 vs 0.842.
lambda 0.1, stop-gradient (clipe5bzsgl01): FA 6.5 / 4.2 / 9.9 / 10.5; miss rise fl12 +15.8; CDFv2 0.930, DFD 0.980, Celeb-DF-B
0.871 (passes), DF40 ff 0.774. Bars 1, 2, 5 pass; 3', 4 (-0.026), 6 (-0.07) fail.
Curve so far (stop-gradient family, CDFv2 / DF40 ff / fl12 FA / fl12 miss rise): lambda 0: 0.943 / 0.835 / 91.8 / -40;
0.1: 0.930 / 0.774 / 4.2 / +16; 1: 0.907 / 0.768 / 4.4 / +10. The accusation is removed at every lambda >= 0.1; the detection
cost shrinks with lambda but DF40 reenactment stays -0.06 to -0.07 and the smoothed-forgery miss rise grows as lambda falls.
FF++-only SIC-sg (clipe5fbzsg): FA 7.4 / 6.8 / 5.3 / 7.0 (bars 1-2 pass with FF++ training data only); CDFv2 0.856, DFD 0.979,
DF40 ff 0.674 (the reference in the readout is the full-data binary; the fair reference is the FF++-only P2 arm, to be added
to the table).
Gaussian-operator ablation (clipe5bzsgG, Amendment 7): whole-crop FA 0.7-3.7, Smoothing-90 3.5, fl06 5.8 but fl12 19.5 (bar 1
fails); miss rise on bilateral forms +14 to +22 (evasion opens); CDFv2 0.855, DF40 ff 0.782. Reading: a uniform blur of the same
support removes most of the accusation on whole-crop forms but not on strong face-local smoothing, and it teaches the model to
let bilaterally smoothed forgeries through; the skin-smoothing operator does both without the evasion. Prediction of Amendment 7
held on the face-local form and on evasion, not on the whole-crop forms.
Incident: the local clipe5bzsgl03 run crashed on 10-18 17:57 after the Amendment 7 edit (Windows spawn re-import); restarted
10-19 06:15. Running now: sgl03 (local), sgh and sgl003 (cvlab-103), sgl01 s2 (Ubuntu); clipe5bz s2 trained, evaluating.

## 2026-10-19 20:30 the complete Addendum 46 family (READOUT46.md, 15 arms)
| arm | fl06 FA | fl12 FA | S-90 | miss rise fl12 | CDFv2 video | DFD | Celeb-DF-B | DF40 FR | bars |
|---|---|---|---|---|---|---|---|---|---|
| view only (lambda 0) | 53.9 | 91.8 | 11.9 | -40.1 | 0.943 | 0.975 | 0.891 | 0.835 | 1,3' fail |
| symmetric 0.3 / 0.1 | 4.7 / 4.3 | 4.6 / 3.3 | 9.9 / 9.5 | +12 / +19 | 0.900 / 0.921 | 0.966 / 0.974 | 0.860 / 0.882 | 0.755 / 0.761 | 3',4,6 fail (5 passes at 0.1) |
| symmetric 1 (s1 / s2) | 4.9 / 4.7 | 4.2 / 5.3 | 7.1 / 7.6 | +8 / +6 | 0.866 / 0.858 | 0.956 / 0.955 | 0.837 / 0.829 | 0.702 / 0.712 | 3',4,5,6 fail |
| stop-grad 1 (s1 / s2) | 5.8 / 6.2 | 4.4 / 5.5 | 2.1 / 12.3 | +10 / +6 | 0.907 / 0.844 | 0.986 / 0.968 | 0.835 / 0.804 | 0.768 / 0.746 | 3',4,5,6 fail |
| stop-grad 0.3 | 6.0 | 4.2 | 12.8 | +9.5 | 0.899 | 0.971 | 0.840 | 0.692 | 3',4,5,6 fail |
| stop-grad 0.1 (s1 / s2) | 6.5 / 4.6 | 4.2 / 4.6 | 10.5 / 8.1 | +16 / +18 | 0.930 / 0.929 | 0.980 / 0.974 | 0.871 / 0.868 | 0.774 / 0.771 | 3',4,6 fail |
| stop-grad 0.03 | 5.0 | 3.3 | 11.2 | +24 | 0.946 (-0.010, passes) | 0.979 | 0.886 (passes) | 0.750 | 3',6 fail |
| one-sided (hinge) | 0.1 | 0.1 | 9.2 | +56 | 0.954 (passes) | 0.980 | 0.880 (passes) | 0.794 | 3',6 fail |
| Gaussian view (ablation) | 5.8 | 19.5 | 3.5 | -13.5 (bil +14..22) | 0.855 | 0.971 | 0.819 | 0.782 | 1,3',4,5,6 fail |
| FF++-only stop-grad 1 | 7.4 | 6.8 | 7.0 | +4.8 | 0.856 | 0.979 | 0.829 | 0.674 | (full-data reference; FF++-only reference to add) |
| reference: forgery head only (s1 / s2) | 51.6 | 84.5 | 40.6 | - | 0.956 / 0.963 | 0.987 / 0.978 | 0.866 | 0.842 / 0.856 | - |
Reading. (1) Every consistency arm with lambda >= 0.03 removes the accusation (fl FA 3-7 %, S-90 2-13 %). (2) The cost has two
faces that trade against each other along lambda: at large lambda the smoothed forgery is pulled up to its clean score and
untreated detection falls (CDFv2 -0.05 to -0.10); at small lambda untreated detection is kept (lambda 0.03: -0.010; hinge: -0.002)
but the smoothed forgery's score falls with the genuine one and the miss rise grows (+24 at 0.03, +56 one-sided). (3) DF40
reenactment is 0.06-0.09 below the reference at every lambda, including 0.03, and is the one bar no arm passes; its seed spread
is 0.014 (reference) so this is a real cost. (4) The Gaussian view fails bar (1) on strong face-local smoothing and opens the
bilateral evasion; the skin-smoothing operator is necessary. (5) No arm passes all six bars; the family is a measured
three-way trade-off (false alarm, smoothed-forgery miss, untreated detection), reported as such. Addendum 47 (BCT) tests
whether a decision rule that leaves the weights alone reaches a better point.

## 2026-10-19 23:00 Addendum 47 (BCT): a threshold rule cannot separate smoothed forgeries from smoothed genuine faces
v1 (quantity covariate, decile bins) changed nothing (Delta ~ 0 for 18/21 detectors): the quantity head is negative on
whole-crop bilateral renders, so the reference bin was already smoothed. Amendment 1 switched to the presence probability
(monotone across forms: untreated 0.01, every smoothing form 0.97-1.00) with four fixed bins.
v2 result (BCT.md): the rule removes the accusation for the CLIP detectors and ours (Effort fl12 99.9 -> 0.0, Forensics
Adapter 100 -> 0.0, DFD-HR 100 -> 0.6, GenD 100 -> 11.7, CADDM 99.9 -> 0.0, binary control 84.5 -> 0.1; untreated FA and
miss unchanged by construction) and at the same time lets 78-100 % of smoothed forgeries through (fl12 miss 0 -> 100 for
Effort, FA, CADDM, SBI, ours; bil15 miss -> 94-100). Commercial Smoothing-90 accused 43 -> 21 (Effort), 65 -> 37 (DFD-HR),
51.6 -> 0.0 (Xception). Reading: for these detectors the scores of smoothed genuine faces and smoothed forgeries coincide
(AUC with both classes smoothed, SMOOTH38: see next line), so any threshold that clears the genuine faces clears the
forgeries; the accusation and the evasion are the same distribution read from two sides. Only a training-time change can
keep a separation under smoothing, and SIC does (AUC both smoothed 0.72-0.83) at the untreated cost measured in Addendum 46.
BCT is therefore a negative result that completes the argument, not a method to ship.

## 2026-10-21 Do FF++ training forgeries carry the smoothing signature? (`bandenergy_20261018/FFPP_BAND.md`, exploratory)
200 FF++ c23 training videos, one genuine frame and one frame of each manipulation of the same target video, statistics inside
the face (hull box). Median paired log-ratio forged / genuine [95% CI]: low skin-relief band 0.02-0.12 c/px: Deepfakes -0.034
[-0.070, +0.007], Face2Face -0.007, FaceSwap +0.034, NeuralTextures -0.033 [-0.048, -0.015]; reference, genuine under bil15 -0.183,
under face-local 0.06 -0.057. High band > 0.25 c/px: Deepfakes -1.09, NeuralTextures -0.65 (lower in 90-95 % of videos),
Face2Face 0.00, FaceSwap +0.80. Mean |Laplacian| in the hull: Deepfakes -0.26, NeuralTextures -0.17 (lower in 88-98 %),
Face2Face -0.07, FaceSwap +0.06; face-local smoothing -0.22, bil15 -0.38.
Reading: half of the FF++ forged training data (Deepfakes, NeuralTextures) has less fine texture inside the face than its
source frame, by about as much as the face-local smoothing we test (Laplacian -17 to -26 % vs -20 %), while FaceSwap is sharper.
This gives a plausible training-side origin for 'smoothed skin inside the face means forged'. The low skin-relief band that
best predicts the accusation across forms is NOT reduced in the training forgeries (at most -0.03 against -0.06 to -0.18 for our
smoothing), so the band result of 2026-10-18 describes how detectors respond, not a copy of a training-data feature. Paper
wording: origin plausible and partly supported (texture loss inside the face in two of four manipulations), not proven.

## 2026-10-21 Addendum 51: identity evidence under smoothing (ID_REF.md, id_ref.json)
Celeb-DF-v2 test, Celeb-real 836 vs Celeb-synthesis 2,668 frames, ArcFace R50 distance to the claimed person's non-test videos.
- Pre-declared prediction PASSES: identity AUC 0.996 -> 0.984 (bil15) / 0.982 (fl12), drop CI within 0.03; clipe5b / Effort /
  GenD / SBI drop 0.07-0.35 on the same frames. Kill criterion (> 0.05) not triggered; bil21 drop 0.033.
- But identity is NOT operating-point invariant: genuine median distance 0.246 -> 0.318 (bil15) / 0.383 (bil21); forged stays
  0.63-0.66 (no homogenization toward the reference). At the untreated 5 % FPR threshold, smoothed genuine are accused 19-40 %.
- Rank fusion clipe5b + identity: accusation 15-23 % (clipe5b alone 43-88 %), miss 6-11 % (clipe5b 2-34 %).
- Limits: identity channel is prior art (ID-Reveal, ICT-Ref, Yin & Jamaluddin 2026; SCOOP_CHECK_C); swaps with a reference only,
  blind to reenactment; Celeb-DF swaps are identity-easy (0.996). Not yet compared with ICT-Ref under the same smoothing.
- Finding for the paper: smoothing erases texture evidence (all 17 detectors) but leaves identity evidence separable; only its
  operating point moves.

## 2026-10-21 decisive control requested by the independent re-critique (RESEARCH_CRITIQUE_20261021b.md): RECAL_MISS.md
Both classes smoothed, threshold re-set at 5 % FPR on that condition's genuine frames (oracle smoothing-conditional threshold).
- lambda=0 (view only) misses 57.4 % (bil15) / 76.7 % (fl12); SIC-sg s1 64.5 / 64.0, s2 73.0 / 72.8; SIC sym 69-72 / 69-73;
  reference clipe5b 52-63 / 74-75. SIC is NOT >= 5 points better than lambda=0 + conditional threshold (worse at bil15, mixed at
  fl12 across seeds). Verdict per the re-critique rule: SIC's gain is the operating point (one threshold works), not separation;
  (the phrase "keeps the separation" was not found in BCT.md; any such wording in the paper must be removed); SIC is reported as a recalibration-equivalent trade-off, the paper becomes an analysis paper.
- lambda=0 itself loses 0.061 (bil15) / 0.129 (fl12) AUC although it saw smoothed views in training: information loss is real
  beyond the shortcut; "ceiling" is allowed only as "measured loss", not as a proven bound.
- At recalibrated 5 % FPR every published detector misses 67-100 % of smoothed forgeries (bil15/fl12); ours 52-77 %.
- Identity (ArcFace, Addendum 51 subset) recalibrated miss: 7.0 (bil15) / 22.1 (bil21) / 7.5 (fl12) vs clipe5b 58.6 / 62.9 / 73.7
  on the same frames. Fusion (clipe5b+identity) is dominated by identity alone at every condition (AUC and miss): fusion dropped.

## 2026-10-21 Addendum 52: published identity detectors under smoothing (ICT_PROBE.md, ict_probe.json)
Same 3,504 probes as Addendum 51 (836 Celeb-real / 2,668 Celeb-synthesis), ICT official weights unchanged, ICT alignment failure 0 % in
every condition. ICT-Ref reference = Addendum 51 non-test Celeb-real videos (54 ids, 1,080 frames) through ICT's own alignment.
- AUC untreated -> bil15 / bil21 / fl06 / fl12: ICT 0.790 -> 0.679 / 0.666 / 0.752 / 0.698; ICT-Ref 0.863 -> 0.781 / 0.755 / 0.836 / 0.783
  (drop CI bil15 [-0.107, -0.060], fl12 [-0.102, -0.057]); ICT-Ref with the released ref.pkl (provenance unknown) 0.933 -> 0.880 / 0.840 / 0.919 / 0.888;
  ArcFace identity 0.996 -> 0.984 / 0.963 / 0.995 / 0.982.
- Pre-declared prediction "ICT-Ref drops by at most 0.03": FAILS (only fl06, -0.028). The stated consequence applies: ICT-Ref drops > 0.05
  under bil15, bil21 and fl12, so the Addendum 51 identity result is specific to ArcFace distance to the claimed person, and the paper says so.
- "Plain ICT drops more than ICT-Ref but less than texture detectors": partly. More than ICT-Ref in all four conditions (point estimates, CIs
  overlap); less than texture detectors only for face-local smoothing (fl12 -0.09 vs -0.17 to -0.30), not for bilateral (bil15 -0.11, inside
  the texture range -0.08 to -0.13).
- "At the fixed threshold both accuse smoothed genuine more": FAILS. ICT false alarm falls (5.0 -> 2.3-4.7 %); ICT-Ref 2.9-7.2 %. ICT fails in
  the other direction: smoothing pulls forged faces toward genuine (miss ICT 65 -> 74-88 %, ICT-Ref 47 -> 55-70 %), whereas texture detectors
  accuse smoothed genuine faces (41-100 %).
- ID-Reveal not run: it needs 3DDFA 3DMM coefficients of consecutive 25 fps frames (100-frame windows; 3DDFA extractor not in the repo); our
  probes are 32 sparse frames per video with per-frame smoothing, so the Addendum 51 PNGs cannot be its input.

## 2026-10-21 reference-free temporal identity dispersion (exploratory, no addendum; zero training)
Per-video mean pairwise ArcFace distance across the smooth38 frames (446 Celeb videos, median 8 frames): AUC 0.58-0.60 in every
condition (clipe5b video mean 0.80-0.97). Swaps are identity-stable across frames; dispersion carries almost no evidence. Dropped.
Synthesis with Addendum 52: the smoothing-robust signal is specifically a recognition-trained embedding (ArcFace) compared with a
reference of the claimed person. Forgery-trained identity models (ICT, ICT-Ref, any reference) lose 0.08 AUC like texture
detectors and fail in the opposite direction (smoothed forgeries pass). Reference-free identity does not work here.

## 2026-10-21 Addendum 53 (FFPP_ARCFACE.md): frozen ArcFace + LR, reference-free -> A2 DROPPED
Trained on 5,996 FF++ train frames, tested on the Addendum 51 Celeb-DF probes: AUC 0.593 untreated, 0.53 under bil15/fl12
(drop 0.07, > 0.03), recalibrated miss 93-95 %; fusion with lambda=0 makes lambda=0 worse at every condition. Prediction's drop
bound fails; decision rule -> A2 dropped. The recognition embedding carries no usable forgery evidence without a reference: the
smoothing robustness of Addendum 51 comes from comparing against the claimed person, not from the representation alone.
(Also 2026-10-21 night: Addendum 50 withdrawn; expert seed 2 started locally, see the amendment in PRE_DECLARED.md.)

## 2026-10-22 Addendum 55 (FB_OPS.md): operation head under Instagram AR filters (combined operations)
Measured on 2,919 FairBeauty pairs: AR filters smooth 96.6 %, enlarge eyes 80.5 %, whiten 3-89 % by filter, slim 8.5 %.
clipe5 (paper main) recognises almost none of it: recall eye 0.003, jaw 0.03, white 0.18, smooth 0.24 (precision for smooth
0.95); exact four-bit match 1.9 %; quantity Spearman |rho| <= 0.16; false presence on originals 3-18 %. Prediction (1)
(smoothing recall >= 0.7) FAILS, worse than predicted; (2) false presence < 10 % holds for eye / jaw / smooth, fails for white
(18 %). clipe7 (AR-trained): recall eye 0.51, white 0.92, smooth 1.00 but precision jaw 0.08, white 0.40 (flags operations
the filter did not apply), consistent with prediction (3) and the known pipeline shortcut. Answer to the meeting question:
under combined real-app filters the main model's operation names carry no information beyond "smoothed, sometimes".
Process note: the cvlab-104 chain waited on the withdrawn Addendum 50 arm and on xs s1 before F2; restarted in order F2, xs s1
(run_add48_104_chain2.sh). xs s2 probes were skipped (model not registered in smooth_probe38); registered and rerun.

## 2026-10-22 Addendum 48 seed 2 (SCE_s2.md): the smoothing expert does not separate smoothed faces better
Expert B = clipe5bzxs_s20260930 (trained only on smoothed copies, bf16 local); A = clipe5b_s20260930. AUC with both classes
smoothed, A / B: bil15 0.843 / 0.752, bil21 0.810 / 0.744, fl06 0.879 / 0.816, fl12 0.748 / 0.770; untreated 0.917 / 0.813.
The expert is worse than the untreated detector at its own job except at fl12. Routed (SCE): accusation cleared (fl06 51.2 ->
2.1 %, fl12 79.9 -> 1.3 %, commercial Smoothing-90 6.5 -> 0.2 %) but miss rises 30-46 points at the strong forms. Bars (1)-(2)
of Addendum 48 (B's separation at least the view-only control 0.76-0.87) FAIL for seed 2; (3') fails as predicted. Seed 1
(cvlab-104, fp32) pending. Reading: consistent with the measured ceiling; training on smoothed inputs does not recover evidence.

## 2026-10-22 Addendum 56 seed 1, first readouts (before FairBeauty): commercial and FF++ only
clipe5M s1 vs clipe5 s1 / s2: Alibaba originals called filter 15.6 % vs 20.8 / 19.6; balanced 75.2 vs 73.5 / 75.4 (inside the
seed spread); level-60 TP eye 0.24 vs 0.19 / 0.31, jaw 0.37 vs 0.32 / 0.37, white 0.37 vs 0.39 / 0.40; FF++ FA 5.1 vs 4.3 / 6.5;
CDFv2 frame 0.894 vs 0.891 / 0.887, DFD 0.958 vs 0.956 / 0.954; video AUC vs Effort / FA CIs unchanged. No change beyond the
seed spread on commercial single-operation sources. Primary endpoint (FairBeauty) pending. Seed 2 restarted (DataLoader
MemoryError at step 2,200 with four evaluations running; 6 workers).

## 2026-10-22 16:40 Addendum 56 primary endpoint, seed 1: H1 REJECTED
FairBeauty accused at 5 % FPR on originals: clipe5M s1 78.1 % (held-out filters 76.3 %) vs control clipe5 s1 75.1 %. The
pre-declared failure rule (drop < 10 points in either seed) is met; multi-operation beautification on both classes does not
lower the AR-filter accusation. Filtered renders are still argmax fake 93.4 %. Pipeline control (ar_pipeline_control, 599
pairs): FairFace ORIGINALS are called real only 18.2 % by clipe5M (fake 28.0 %, filter 53.8 %); with the face hull greyed,
originals 100 % fake and renders 99.5 % fake, so the grey control cannot separate filter from pipeline for this model. As
Addendum 13 stated, FairBeauty / B-LFW cannot isolate the filter (no no-filter pass through the OpenFilter pipeline); they are
dropped as the target endpoint. The remaining Addendum 56 arms (M1, M s2, EM) are completed and reported as declared.
Clean real-app evidence that remains (Celeb-DF-B, with its own compression control; RESULTS_v3.md): published detectors barely
accuse beautified genuine frames (median |dFA| 1.6) but let beautified deepfakes escape (dMISS Effort +23.7, Forensics Adapter
+15.5, SBI +36.8 / +16.0, CORE +13.8); the beautification-aware three-way models +1.4 to +4.2 (clipe5 family +7.0 / +6.7 / +8.4).

## 2026-10-22 17:00 two-direction main claim with paired intervals (docs/capstone/MAIN_CLAIMS_20261022.md, generated)
A (alipair main_claim_A.py, 2,210 pairs, bootstrap over pairs): 15/17 published detectors score the Smoothing-90 render above
its own original in 89-99 % of pairs; ours 32.5 / 41.3 % (two seeds); paired difference excludes 0 against 16/17 (NPR
saturated). FA at 5 % FPR of originals: published 17-69 % (NPR 0, CADDM 6.3), ours 8.6 / 12.5.
B (celebdfb fair_cdfb.py with dfdhr / gend / caddm added as references): AUC after beautification ours 0.866 / 0.883, highest;
paired CI excludes 0 against all six references in both seeds. Beauty-only miss rise ours +6.7 / +8.3: significantly smaller
than Forensics Adapter, SBI, GenD (and Effort in s1; s2 CI [-5.8, 0.5]); significantly LARGER than DFD-HR (+3.6) and CADDM
(-2.9). The paper and capstone must not claim the smallest escape; they claim the highest beautified AUC and the only model
that is low on BOTH the accusation (A) and the escape (B) axes.

## 2026-10-23 overnight readouts
- Addendum 49 (clipe5fbp0F2, FF++-only without Deepfakes / NeuralTextures): face-local FA fl06 95.5 %, fl12 100 % (P0 s1/s2:
  95.8 / 100, 95.8 / 100); untreated AUC 0.857 vs 0.883 / 0.892. The prediction (>= 15-point fall) FAILS: the texture-poor
  families do not teach the cue. The origin is the self-blend / generic blended boundary. Texture correlation (FFPP_BAND) stays
  descriptive; the paper's F4 must not attribute the cue to Deepfakes/NT.
- Addendum 56 complete: FairBeauty accused M s1 78.1, M s2 67.6, M1 (pending), EM 67.6 vs controls clipe5 75.1, clipe5fbE 69.7 / 75.0.
  All within seed spread; H1 rejected as declared on 10-22.
- Addendum 48 seed 1 (cvlab-104, fp32) scored; SCE readout to be added with sce_eval.py (seed 2 already failed bars 1-2).
- Addendum 57 launched (boundary vs smoothness, zero training).

## 2026-10-23 Addendum 57 (BDRY38.md): the cue is NOT the boundary line; it is a smooth face inside a textured context
Same bilateral strength inside the hull, only the edge treatment changes; FA on smoothed genuine frames at the untreated 5 % FPR.
- Prediction (2) FAILS decisively: smoothing only a ring at the hull edge (interior untouched) is accused 7-50 % (median about
  12 %) against 92-100 % for the full face-local form, for 13 of 15 face detectors. The exceptions are the two boundary /
  landmark-artifact detectors: CADDM 94 %, LAA-Net 65 %. Per the pre-declared rule the boundary-line story is dropped, and
  Addendum 58 (boundary-free training views) is not run.
- (1) holds 14/15 but the effect is small (fe01 -> fe15: 99 -> 93 typical); (3) holds 11/15: smoothing the WHOLE crop
  (face and context alike) is accused much less (UCF 13.6, Effort 30.3, FA 59.3 vs 98-100 face-local).
- Reading: the accused pattern is region-level, a face that is smoother than its own context. The smoothed interior is
  necessary (ring fails) and a matching context removes much of it (whole). This is the face-versus-context texture
  inconsistency that face-swap detectors are built to find; face-local beautification reproduces it by construction. It
  explains why a threshold cannot separate the two and why every training-side fix trades.
- Both-classes AUC: ring keeps separability (e.g. Effort 0.861 vs 0.876 untreated); hard / fe01 lose the most; whole loses
  less than face-local for the CLIP detectors (Effort 0.760, GenD 0.750, DFD-HR 0.724 vs 0.65-0.66 face-local).

## 2026-10-23 Addendum 54 readout (GPX38.md): a second, open-source beauty engine reproduces direction A
GPUPixel skin smoothing (ported shader, camera scale), FA on smoothed genuine Celeb-DF-v2 frames at the untreated 5 % FPR.
Null form gpx0 (resize round trip only) 2.4-4.9 % for every published detector, so the effect is the smoothing.
Prediction (1) PASS 14/15 face detectors above 15 % at gpx9 (SBI 78.9, Effort 57.7, FA 72.8, GenD 84.5, DFD-HR 87.2, CADDM 42.5,
LAA-Net 70.7, Xception 37.4); (2) monotone AUC 11/15 (bar 12, FAIL by one); (3) Spearman of detector ranking with bil15 FA 0.243
(bar 0.5, FAIL: the accusation reproduces, the ordering of detectors does not). Our beautification-trained arms 17.1-24.6 %.
This removes the "single commercial source" objection for direction A (not bit-exact to the compiled library; stated).
Our own escape route (Celeb-DF-B, native three-way decision, main model s1 / s2): beautified deepfakes called "beautified"
16.6 / 16.1 % against 3.6 / 3.9 % for the same deepfakes untreated, i.e. beautification moves about 12.5 points of forgeries
into the beautified class. This must be stated wherever the three-way output is presented.

## 2026-10-23 Addendum 59 (ORACLE_OPS.md): the single-image ceiling is NOT where we thought, pending a specificity check
Dedicated EfficientNet-B0 per operation, Alibaba level 90, identity-disjoint 70/30 (663 test faces), lossless / after JPEG
q90 + resize 256: eye 0.933 [0.922, 0.943] / 0.833; slimming 0.948 [0.939, 0.957] / 0.880; whitening 0.980 [0.973, 0.986] /
0.949; smoothing 0.9995 / 0.997. The pre-declared prediction (eye, slimming, whitening < 0.90) FAILS. By the declared rule:
whitening >= 0.95 is a fixable target; eye and slimming fall in the 0.90-0.95 "weak" band. BEFORE any claim: the classifiers
may read the vendor's processing fingerprint rather than the operation (Addendum 59 amendment 1: cross-operation matrix).

## 2026-10-23 CORRECTION: the forgery-head-only reference accuses 9.1 % (not 40.6 %) of commercial Smoothing-90 renders
docs/paper_v2/make_tab_sic.py typed the reference row's S-90 cell as 40.6; the column's rule (5 % FPR on the untouched
originals, readout46.ali) gives 9.1 % for clipe5b_s20260929 (6.5 % for s20260930; smoothing90_thresholdfree.json "binary
full" 9.1; SCE.md "s90_accused_A" 9.1). The source of 40.6 was not found. The entries of 2026-10-18 / 10-19 above that quote
"binary control 40.6 %" are wrong. Consequence: SIC (2-13 %) does not remove a commercial accusation the reference already
lacks; SIC's effect is on the face-local forms only. Table regenerated from data; main_v8.tex Sec. III-F sentence rewritten.
Found by the light-consistency audit (docs/CONSISTENCY_AUDIT_20261023.md, item 1).

## 2026-10-23 Addendum 59 specificity check (ORACLE_OPS.md cross matrix): eye enlarging and whitening ARE single-image detectable
Cross-operation AUROC (classifier trained on row, tested on held-out renders of column):
eye 0.933 own | 0.746 / 0.694 / 0.637 on slimming / whitening / smoothing renders -> passes (own >= 0.90, all cross < 0.75; marginal)
slimming 0.948 own | 0.718 / 0.676 / 0.797 -> FAILS specificity (0.797 on smoothing renders: it partly reads a shared texture change)
whitening 0.980 own | 0.537 / 0.563 / 0.631 -> passes clearly; survives JPEG q90 + resize 256 at 0.949
smoothing 0.9995 own | 0.49-0.52 cross -> specific
Reading: within one vendor, whitening and eye enlarging leave a single-image signal that a dedicated classifier finds and our
general operation head does not. Slimming cannot be separated from a shared processing change. This reverses the 10-23 claim
"only smoothing is recognisable in principle" for whitening and (weakly) eye enlarging, within vendor. Cross-vendor transfer is
the open question (Addendum 60).

## 2026-10-27 weekend readouts
- Addendum 58 (W: FairFace in-the-wild genuine bases): P1 PASSES strongly: FairFace validation originals called real 95.9 / 96.0 %
  (control 23.2); P2 FAILS in the wrong direction: FairBeauty renders accused 99.3 / 98.6 % (control 75.1). Guardrails pass
  (Celeb-DF-B beauty-only miss rise +8.6 / +3.6 vs +6.7; CDFv2 0.897 / 0.884 vs 0.891 / 0.887; DFD 0.950 / 0.954 vs 0.956 / 0.954;
  Alibaba balanced 74.9 / 74.8; FF++ FA 5.8 / 5.2). Alibaba originals called beautified 16.4 / 21.0 (bar <= 10 not met).
  Grey-face control: W calls greyed originals fake 87-94 %, so it reads the face. Reading: the model now recognises in-the-wild
  stills as genuine, and everything that went through the OpenFilter emulator pipeline as not genuine; FairBeauty was declared
  a confounded source before this arm. By the declared rule the arm FAILS as an AR-filter fix; as a system model for ordinary
  photographs it is the first arm that passes P1 with no guardrail cost (product decision, not a claim).
- Addendum 60 (cross-vendor dedicated classifiers, trained on Megvii + Tencent, tested on Alibaba): white 0.690, eye 0.722,
  jaw 0.703 at level 90 (bars 0.85 FAIL); smoothing 0.999 PASS. Within-vendor signal (Addendum 59: white 0.980, eye 0.933)
  does not transfer across engines. Closure: only smoothing is recognisable across vendors; the other three operations leave
  engine-specific traces.
- Recipe transfer (Addendum 35 arms, Alibaba Smoothing-90 accused at 5 % FPR): Effort tuning scheme from CLIP 56.9 / 63.2 ->
  14.5 with the symmetric smoothing view; released Effort checkpoint fine-tuned 2 epochs 55.3 -> 39.9. LoRA FF++-only
  54.2 -> 5.9 / 6.1. The recipe lowers the accusation under every tuning scheme tested; the fine-tune of the released
  checkpoint least (2 epochs).
- Human study pilot (old A4 page, Sheet trials tab, 13 participants, one submitted twice): pooled accuracy C0 35/57 = 61 %,
  C1 33/54 = 61 %, C2 33/57 = 58 %. Design had the source leak and 6/3/3 split; pilot only, excluded from the counted study
  per Amendment 5. Descriptively: no sign that any explanation changed accuracy.

## 2026-10-27 Addendum 61 readout (CTX38.md): test-time context matching is a recalibration in disguise. KILLED
Rule: forged iff s(x) > t_A and s(W(x)) > t_W, W = whole-crop bilateral at the fl12 interior strength, no training.
Prediction (1) joint FA on face-locally smoothed genuine frames < 30 %: 10/15 face detectors (bar 10/15, met exactly;
single-score FA was 92-100 % for every one of them, so the rule does clear the accusation). Prediction (2), the one that
decides: at matched 5 % FA on the same smoothed genuine frames, joint miss beats single-score recalibration by >= 10 points
for 0/15 (kill bar < 5/15). The joint rule's miss at matched FA is within a few points of RECAL_MISS for every detector
(Effort 86.5 vs 84.0, Forensics Adapter 89.2 vs 87.6, GenD 90.2 vs 90.8, DFD-HR 90.7 vs 93.5, Xception 93.8 vs 90.7), and
the second gate costs untreated detection too (miss on untreated forgeries Effort 41.3 -> 76.5, SBI 62.3 -> 95.5,
Xception 77.7 -> 97.9). Ours (clipe5 s1): 44.5 -> 10.3 FA, miss at matched FA 90.9 vs 84.4 recalibrated; same picture.
Reading: once a smoothed genuine face and a smoothed forgery both sit above the first threshold, the detector's score on
the context-matched copy carries no extra separation between them; a forgery's evidence that survives whole-crop smoothing
is not larger than a genuine face's. This is the fourth independent closure of the same ceiling (SIC = recalibration,
Addendum 46; routing clears accusation at +30-46 miss, Addendum 48; threshold alone, RECAL_MISS; now test-time context
matching). The mechanism of Addendum 57 explains the accusation but does not give a free inference-time fix. One
paragraph in the paper (Sec. "what does not fix it"); no further test-time ideas without a new signal.

## 2026-10-28 Addendum 62 readout (CDFB_ID.md, cdfb_id.json): identity survives real app presets; fusion bar missed for the Effort pair
Celeb-DF-B frames_std32v3, 43,363 frames, identity detect-fail 0 %. References = 4 Celeb-real videos per claimed identity outside
the 231 Celeb-DF-B real videos (id42 has 1, id44 has 2).
(1) PASS: identity video AUC 1.000 untreated / 1.000 beautified / 1.000 compressed (texture detectors drop 0.04-0.12; ours 0.98 ->
    0.92 / 0.94). Kill not triggered.
(2) PASS: at a threshold matched to 5 % FA on beautified genuine frames, identity misses 0.6 % of beautified deepfakes; every texture
    detector misses 46-72 % (ours 51.1 / 46.2, Effort 51.9, GenD 61.9, SBI 69.6, CADDM 72.1).
(3) FAIL by the declared bar: fusion ours+identity meets it (beauty-only FA +7.7, miss rise +2.9) but Effort+identity does not
    (miss rise +8.5 [5.4, 11.5] > 5). The declared gate variant (identity says genuine -> genuine) meets both bars for all four
    pairs (FA +8.0 to +8.4, miss rise -0.3), but its misses equal identity alone: the gate is identity doing the work.
(4) FAIL narrowly: identity alone at the untreated threshold accuses beautified genuine +8.5 [6.4, 10.6] points more than
    compressed (bar 10); the operating-point shift of Addendum 51 reproduces in direction, not at the declared size.
Reading (declared rule "(1)(2) pass, (3) fails"): identity is the one channel the presets leave intact, and it needs a
beautification-aware threshold; no method claim for the fusion. Limits that bound the claim: Celeb-DF synthesis is identity swap
with the claimed person's reference available (identity AUC 1.000 says the benchmark is identity-easy, as ICT-Ref's 94 % frame AUC
on CDF2 already showed); reenactment and attribute edits keep identity and are invisible to this channel by construction (not measured here; without a reference the channel is useless, AUC 0.59, FFPP_ARCFACE.md);
prior art (ID-Reveal, ICT-Ref, Yin & Jamaluddin 2026) uses the same channel without measuring beautification.

## 2026-10-28 paper v9 built (docs/paper_v2/main_v9.tex, supplement_v9.tex, V9_CHANGES.md)
main_v8 -> main_v9 by make_v9_main.py (24 + 13 exact-string edits, v8 untouched): CONSISTENCY_AUDIT_20261023 M01-M25 and
S02-S09 applied (S03 left for the author's ruling); Addenda 48 (both seeds), 49, 54, 57, 61, 62 written in; Finding 4 retitled
"a face smoother than its context"; Finding 7 rewritten on CDFB_ID.md (identity vAUC 1.000 under presets, miss 0.6 % at 5 % FA
on beautified genuine vs 46-72 % for texture detectors; fusion not claimed); "only model low on both axes" removed, companion
written as an audit reference with the forgery-head-only control. Table VI (companion vs CLIP, untreated) moved to the
supplement to stay at 8 body pages (references start at the top of page 9). New supplement table tables/tab_v9_cdfbid.tex.
yin2026 bib entry completed from Crossref (vol. 11, no. 44, p. 904). Build: sh docs/paper_v2/build_v9.sh (tectonic, XeTeX);
an arXiv upload still needs a pdflatex-compatible font setup (fontspec is XeTeX-only) and real author names.

## 2026-10-28 paper v10 (docs/paper_v2/main_v10.tex, main_v10j.tex, V10_CHANGES.md)
v9 + academic-humanizer audit (34 wording items, HUMANIZER_AUDIT_V9_20261028.md) + pre-submission-reviewer findings
(REVIEW_V9_20261028.md: 0 CRITICAL / 9 MAJOR / 16 MINOR, score 6/10; all MAJORs applied except venue form, which is the
journal twin main_v10j.tex). New Fig. 1 = motivated example with real scores (FFHQ 17003 pair; Celeb-DF-B id17_id35_0000,
four CLIP detectors at their own 5 %-FPR thresholds; make_fig_teaser_v9.py); the 17-detector dot panels moved to Fig. 3
(fig_dirs_v9). Two prior-art citations added after verification on arXiv (Identity-Driven DeepFake Detection 2012.03930;
VIPGuard 2505.19582). No number changed. Conference build spills ~1/3 page past p. 8; journal build has no limit.

## 2026-10-28 (later) paper v10 three builds + arXiv package
main_v10c.tex = IJCB cut (body ends on p. 8, dot figure dropped, 12 prose/caption shortenings, no number changed);
main_v10j.tex = journal (TIFS) twin with Index Terms, author placeholder, abstract challenge sentence; Fig. 2 -> fig_method_v10
(larger text), Fig. 4 -> fig_exposure_v10 (chips instead of thumbnails); supplement S03 ruling applied; bib provenance notes
stripped from the printed references; arxiv_v10_pkg/ built from the journal text with newtxtext. Second-round review running
(REVIEW_V10_20261028.md).

## 2026-10-28 (evening) paper v10 round-2 review applied
REVIEW_V10_20261028.md: 0 CRITICAL / 3 MAJOR / 12 MINOR, 8/10 (from 6/10). All three MAJORs fixed by make_v10_round2.py
(Sec. II reproduction sentence now literal to Table S3; supplement notebook pointers replaced by the released-file
convention; Table I/II bold consistent with captions) plus the actionable MINORs. Builds: main_v10c (IJCB, body ends p. 8),
main_v10j (TIFS, 11 pages, Table S3 in the body), supplement_v10 (36 pages), arxiv_v10_pkg (newtxtext). Left for the authors:
names, repository anonymisation.

## 2026-10-28 (night) paper v10 rounds 3-4
Round 3 (REVIEW_V10_R3): 0 / 1 / 9, 9/10; the MAJOR (journal supplement cross-referenced the conference twin) fixed with
per-variant supplement twins (supplement_v10c / supplement_v10j; build_v10_all.sh); all nine MINORs applied (make_v10_round4.py).
Fonts: newtxtext everywhere (pdfLaTeX-compatible). Conference body still ends on p. 8; journal 11 pages; arXiv package
rebuilt from the journal pair. Round 4 review running (REVIEW_V10_R4).

## 2026-10-28 (late) paper v10 rounds 5-6
Round 4: 0/0/7 (6 fixed); round 5: 0/0/5 (4 fixed, make_v10_round6.py); every build clean (?? 0, Addendum 0, clipe 0, (am. 0 in all
six PDFs and the arXiv pair). Remaining for the authors only: names, repository anonymisation. Round 6 confirmation running.

## 2026-10-28 (final) paper v10: six review rounds closed
Round 6 (REVIEW_V10_R6): 0/0/4, three actionable applied (make_v10_round7.py); abstracts 214 / 242 words; IJCB body ends on
p. 8; all six PDFs and the arXiv pair clean. Submission-ready except author names and repository anonymisation.

## 2026-10-28 Addendum 63 readout (CDFB_GATE.md): beautification-aware reference gate, KILLED
Soft gate w = quantile of the model's own beautified logit, score = w * q_identity + (1 - w) * q_texture, four pairs. Miss on
beautified swaps falls (dMISS -5 to -10, matched-FA miss 10-15 %) but the beautification-only accusation rises +11.5 to +17.1
(bar 10) because w rises on beautified genuine faces as on beautified forgeries; beautified vAUC 0.968-0.987. Predictions (1)(2)(3)
fail, (4) holds. Fifth closure of the operating-point bound (threshold, routing, SIC, context matching, beautification-aware
fusion). Identity alone remains the only score whose separation does not move; the paper's method claim stays off.

## 2026-10-29 Addendum 64 readout (CDFB_RPPG.md): rPPG pulse SNR, KILLED
Zero-training POS pulse SNR over cheeks + forehead, one score per Celeb-DF-B video (300 frames). Untreated video AUC 0.514
(kill bar 0.60); median SNR about -4 dB on genuine and swaps alike. The pulse is there (76.5 % of genuine peaks at 54-102 bpm)
and the swaps inherit it from the driving video (peak agreement 43.9 % vs 18.7 % chance), so presence of a pulse is not forgery
evidence; beautification leaves it (dAUC +0.03, FA/miss unchanged), which is consistent with the spatial-filter argument but
moot. Re-encoded folders lose half the videos at the 90 % landmark bar (re-encoding, not beautification). Sixth closure.
Reference-free channels tried: texture (bounded by smoothing), pulse presence (no signal); identity (reference-conditioned) stays
the only channel whose separation survives the presets.

## 2026-10-29 paper v10 round 8
Add. 63/64 closures written into Limitations of all three variants (make_v10_round8.py); six PDFs and the arXiv pair rebuilt
clean; IJCB body still ends on p. 8. Submission state unchanged otherwise (author names, repository anonymisation remain).

## 2026-10-29 benchmark release 1.1.0 (paper v10)
benchmark_release/ now carries the seven smoothing forms and the GPUPixel engine for all 17 detectors (landmarks released;
regeneration byte-identical on a 60-frame sample), regenerates and checks every v10 benchmark table (nine tables, zero
differing cells), a leaderboard with a submission checker, and the governance files (licence, citation, datasheet, hosting
matrix, Croissant, pre-registration logs). Archive 33.8 MB, 245 files. Open: the hosted tier (HOSTING.md).

## 2026-10-29 DF40 reenactment: class collision or blindness? (`../df40_eval_20261012/diag_1mreal.py`, post hoc, no decision)
Main model (clipe5 seed 1), full three-way probabilities on the DF40 list, video AUC mean over methods. Reenactment, FF++ domain:
P(fake) 0.718, 1 - P(real) 0.686, P(beautified) 0.457; argmax on reenactment frames real 53 % / fake 27 % / beautified 20 %
(genuine: 73 / 8 / 19). Celeb-DF domain: P(fake) 0.502, 1 - P(real) 0.631, P(beautified) 0.638; argmax real 49 / fake 17 /
beautified 33 % (genuine 63 / 17 / 20). Face swap: 1 - P(real) 0.936 / 0.943 vs P(fake) 0.952 / 0.905.
Reading: in the FF++ domain the loss is blindness (reenactment is called real; reading "not real" does not help). In the Celeb-DF
domain about a third of the loss is a collision with the beautified class (0.50 -> 0.63 when beautified counts as manipulated),
still far from GenD's 0.83, and reading beautified as manipulated would re-open Direction A. The literature review's "class-boundary
collision" explains part of the Celeb-DF gap, not the gap. Addendum 67 (decoder re-synthesis) targets the blindness part.


## 2026-10-29 20:40 GPUPixel (Addendum 54 sources) scored on the main model
`gpx_probe.py score clipe5_s20260929 clipe5_s20260930` + `analyse` (GPX38.md). gpx9 at the untreated 5 % FPR threshold: FA 13.7 / 13.1 %, miss 45.8 / 41.3 %, AUC both smoothed 0.804 / 0.817, recalibrated miss 65.1 / 59.6 %. Face detectors: 14/15 above 15 % (Effort 57.7, SBI 78.9, GenD 84.5); UnivFD 12.4 and SRM 12.5 are lower with AUC 0.62 / 0.66. FA is not monotone for ours (gpx6 18.4 / 18.2 -> gpx9 13.7 / 13.1). Descriptive; no bar was declared for our rows. Capstone open item 5 closed.

## Addendum 67: decoder re-synthesis as a pseudo-forgery (2026-10-30) — killed

Hypothesis: adding FLUX-VAE reconstructions of genuine frames as forged training items (p = 0.25) closes the DF40
reenactment gap. Result: the opposite. DF40 reenactment AUC falls in both arms (three-way 0.718 -> 0.657, diff -0.061
[-0.073, -0.050]; binary 0.842 -> 0.687), face-swap AUC falls 2-4 points, Celeb-DF-v2 video AUC -0.010 [-0.021,
-0.0003], Celeb-DF-B beautification escape worsens (6.7 -> 8.4 points). Smoothing-90 accusation falls to 3.2 %, the
only movement in the intended direction, and it is not what the addendum scored. Decoder texture is not the cue that
DF40 reenactment carries; the pseudo-positives dilute the real signal. Closed without a second seed (`readout67.log`,
PRE_DECLARED Addendum 67 readout).

## Addendum 70: browser W model (2026-10-30) — gate failed on G1

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
