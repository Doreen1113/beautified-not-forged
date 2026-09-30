# FINDINGS — cgd_20260927 (running log)

## HYBPE (detection baseline: HYB-F recipe + 61,510 part edits, no head) — 2026-09-28
CDFv2 **0.810** [0.781, 0.837], DFD 0.888 [0.848, 0.925]; FF++ 80.7/90.2/**76.8** (filter < 80); FA/MISS 8.89/1.62; B1 0/13;
HELDOUT-13 excess 39.2. Celeb-DF-B: untreated AUC 0.879, untreated genuine→fake 56.0 %, ΔMISS +1.3 [−0.3, 3.0], E1 holds.
Reading: part-level edits alone raise CDFv2 from 0.780 (HYB-F) to 0.810 — the largest single data effect in this line —
but cost in-domain filter recall (84.7 → 76.8) and raise FA (6.1 → 8.9). CGD seed-1 vs HYBPE: CDFv2 0.794 (D1 fail, −0.016;
CGD saw 43k vs 61k part edits), DFD 0.906 (D2 pass), filter recall 87.2 vs 76.8, FA 3.2 vs 8.9.

## HYBPE post-hoc explanation baselines (Addendum-2 protocol, n=1,200 per mechanism) — 2026-09-28
| method | donor IoU7 / px | donor flip pred / comp / rand / centre | SD IoU7 / px | SD flip pred / comp / rand / centre |
|---|---|---|---|---|
| Grad-CAM | 0.367 / 0.369 | 50.9 / 15.2 / 16.4 / 38.9 | 0.259 / 0.257 | 45.4 / 25.0 / 23.0 / 38.3 |
| Grad-CAM++ | 0.414 / 0.450 | 51.7 / 7.2 / 19.0 / 38.9 | 0.327 / 0.366 | 47.8 / 16.7 / 18.3 / 38.3 |
| Score-CAM | 0.408 / 0.448 | 56.5 / 5.9 / 17.1 / 38.9 | 0.334 / 0.379 | 52.4 / 15.4 / 19.6 / 38.3 |
Ceiling (restore GT footprint): donor 85.8 %, SD 85.2 %. Centre-prior IoU7: donor 0.313, SD 0.244. Detect rate donor 83.6 %, SD 74.3 %.
CGD seed-1 (hull-mask protocol, for orientation): donor IoU7 0.858 / px 0.687, flip(dilated) 77 %; SD 0.674 / 0.541, 46 %.
Re-evaluation of CGD under the Addendum-2 protocol running (explain_CGD_v2.log).

## CGD seed-1, Addendum-2 protocol (footprint GT, dilated regions, ceiling + controls) — 2026-09-28
| mech | detect | IoU7 / px | flip pred | ceiling (GT) | comp | rand | centre (flip / IoU7) |
|---|---|---|---|---|---|---|---|
| donor | 91.1 % | **0.759 / 0.742** | **89.4 %** | 90.0 % | 0.4 % | 15.9 % | 41.3 % / 0.309 |
| SD | 41.5 % | **0.614 / 0.598** | **75.2 %** | 79.8 % | 4.4 % | 21.1 % | 40.6 % / 0.245 |
vs best post-hoc on HYBPE (Score-CAM): donor IoU7 0.408 / flip 56.5 %; SD 0.334 / 52.4 %.
Bars: **E1 PASS** (+0.35 / +0.28 IoU7 over best post-hoc; MASK comparison pending), **E2 PASS** (89.4 / 75.2 ≥ 70; MASK+15 pending),
**E3** comp 0.4 / 4.4 PASS, random 15.9 PASS / 21.1 marginal FAIL on SD; **E5 PASS** (0.565); E4 pending (SDXL held-out set).
Caveats: CGD saw 43k part edits (1.9k SD) — SD detect rate 41.5 % vs HYBPE 74.3 %; CGD-D (61.5k) will settle this.

## MASK (mask head, BCE+Dice, no restoration loss; 61,510 part edits; Ubuntu) — 2026-09-28
Detection: CDFv2 **0.819** [0.792, 0.844] (best of all our models), DFD 0.908, FF++ 79.0/90.0/84.0, FA/MISS 6.99/2.06, B1 0/13,
HELDOUT-13 excess 40.7; Celeb-DF-B AUC 0.888, untreated genuine→fake 60.6 %, ΔMISS +1.4 [0.1, 2.8].
Explanation (Addendum-2 protocol): donor detect 90.3 %, IoU7 0.723 / px 0.715, flip 84.0 % (ceiling 84.7), comp 0.4 %, rand 17.0 %;
SD detect 82.1 %, IoU7 0.752 / px 0.704, flip 82.6 % (ceiling 83.2), comp 0.7 %, rand 17.9 %; E5 0.622.
**Reading**: with exact footprints, mask supervision alone reaches the restoration ceiling; CGD seed-1 (43k data) is +0.036 IoU7 /
+5 pp flip on donor but below MASK on SD (data). Bar "E2: CGD ≥ MASK + 15 pp" FAILS. The contribution that survives is the
exact-footprint supervision from pixel-aligned pairs (both heads ≫ post-hoc); the consistency loss must show its value where no
exact mask exists (observed FF++ forgeries with approximate counterfactuals) or be dropped. CGD-D (same 61.5k data) pending.

## Observed FF++ test forgeries, approximate counterfactual (target real frame), n=1,500 — 2026-09-28
Footprint-area regions: MASK flip pred 77.3 / comp 2.6 / random 78.1 / centre 78.6 (ceiling 80.6); CGD 79.7 / 3.8 / 85.9 / 83.9
(ceiling 87.5). **Uninformative**: for whole-face forgeries the footprint proxy covers most of the face (area clipped to 60 %), so
any large region restores the forgery. Re-run with a fixed 15 % area (ffpp_flip_*_a15.json) to separate predicted from random.
Fixed 15 % area: MASK pred 24.6 / rand 16.0 / centre 10.5 / comp 0.2; CGD pred 24.4 / rand 21.0 / centre 11.0 / comp 1.4.
Whole-face forgeries have no small sufficient region (consistent with the region-restoration table: forgery evidence is
diffuse); neither head localises them, and the consistency loss gives no measurable gain here either.
**Provisional conclusion (pending CGD-D, same data as MASK)**: the deliverable is the evidence head trained on exact footprints
from pixel-aligned pairs (≫ post-hoc, at the restoration ceiling on part edits); the restoration-consistency loss is a negative
ablation. Paper contribution wording to be changed accordingly; "CGD" retained as the round name only.

## CGD-D (footprint masks + full 61.5k part edits + symmetric degradation + consistency; resumed at epoch 10 without momentum) — detection, 2026-09-28
CDFv2 0.781 [0.751, 0.809], DFD 0.877 [0.833, 0.916]; FF++ 84.7/80.8/79.6; FA/MISS 6.16/5.12; B1 0/13; HELDOUT-13 excess 38.5.
Below MASK (0.819/0.908) and CGD (0.794/0.906): the symmetric degradation that helped HYBD (0.807) did not help here, and the
resume-without-momentum is a confound. Explanation/Celeb-DF-B pending. Not the headline model.
HYBPE Score-CAM at fixed 15 % area on observed FF++ forgeries: pred 21.6 / rand 13.7 / centre 8.1 / comp 0.1 (ceiling 80.7) — same picture as the heads: no small sufficient region for whole-face forgeries.
CGD-D explanation: donor detect 81.3 %, IoU7 0.722 / px 0.727, flip 88.4 % (ceiling 89.3), comp 0.7, rand 18.6, centre 51.1;
SD detect 61.0 %, IoU7 0.723 / px 0.687, flip 85.2 % (ceiling 86.1), comp 2.4, rand 22.7, centre 57.1; E5 0.596.
Celeb-DF-B: AUC 0.875, untreated genuine→fake **15.1 %** (lowest of all models; HYBD 28, MASK 60.6), beautified→fake 4.9 %,
untreated escape 20.1 % → beautified 13.9 % (ΔMISS −6.2), E1 holds.

## Final reading of the CGD line (2026-09-28)
All three evidence heads (MASK, CGD, CGD-D) reach the restoration ceiling on held-out part edits (flip 84–89 % vs ceilings 85–90 %,
complement ≤ 2.4 %, IoU7 0.72–0.76) against 0.41 / 56 % for the best post-hoc map on the same backbone. The consistency loss adds
nothing measurable (part edits: at ceiling with or without it; observed forgeries: no small sufficient region exists for any method).
Headline model of the line: **MASK** (CDFv2 0.819, DFD 0.908, B1 0/13, Celeb-DF-B 0.888, explanations at ceiling). Bars: E1 PASS
(all heads ≥ post-hoc + 0.15), E2 threshold PASS for every head but the "≥ MASK + 15 pp" clause FAILS by construction (ceiling),
E3 PASS (rand 15.9–22.7 marginal on SD), E5 PASS; E4 pending SDXL; D1 for CGD −0.016 vs HYBPE (data), MASK +0.009. Pre-registered
ablations CGD-ZERO / CGD-BLUR / CGD-NOHOLD are dropped: the quantity they ablate has no effect to explain.

## Completeness analyses (MASK) — 2026-09-29 (`eval_completeness.py`)
Per source recall on FF++ test: Deepfakes 98.9, Face2Face 94.8, FaceSwap 92.3, **NeuralTextures 73.9** (22.6 → real); filters:
pilgram 92.2, smoothing 92.9, whitening 88.6, slimming 78.7, **eye enlarging 36.8** (49.3 → real); real 79.2 (13.8 → fake, 7.1 → filter).
Robustness (300 reals / 300 fakes, real/fake recall %): HYB blur σ1.5 2/100, down×2 15/100, JPEG q30 76/74; **HYB-D** blur σ1.5
79/85, down×2 82/89, JPEG q30 72/83; MASK blur σ1.5 2/100, down×2 10/100. ⇒ MASK inherits the softness shortcut; MASK-D launched.
Latency (batch 1): RepViT-M0.9 224 px 4.72 M, CPU 28.3 ms, GPU 8.3 ms; EffB4 380 px 17.55 M, CPU 55.0 ms, GPU 10.7 ms; + evidence
head 17.56 M, CPU 62.1 ms, GPU 10.3 ms.
JSON output check: a mean-colour fill of the named region *raises* P(fake) (fill looks like an edit) → the inference-time
"faithfulness estimate" is dropped; faithfulness is an offline, counterfactual-verified property reported per model.
Video level (32-frame mean): MASK CDFv2 0.878 / DFD 0.866, HYBPE 0.871 / 0.853 (SBI 0.872 / 0.876). Celeb-DF-B untreated genuine
called fake: MASK 60.6 % (highest of our models; HYB 43–51, HYB-D 28, CGD-D 15.1) — the part-edit data sharpens the forgery
signal without removing the softness shortcut; MASK-D (Addendum 3) is the pending fix. Figures/tables integrated into
`docs/paper_v2` (Sec. VI-I, Tables III/V/VII/VIII, Figs. 8–9); `fig_robust` renamed `fig_robust_<ARM>` so a MASK-D sweep cannot
overwrite the MASK curve.

