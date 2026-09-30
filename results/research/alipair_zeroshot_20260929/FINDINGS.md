# ALIPAIR-ZEROSHOT-20260929 — findings

Pre-declared rule (PRE_DECLARED.md): best model balanced < 60 % ⇒ same chance level as v8.17; the next stage must solve
commercial-beautification generalisation itself before anything else. **Outcome: that branch.** Best balanced accuracy is
54.5 % (SUP-F); every model is at 48–55 % (v8.17: 50.7–51.2 %). Excluding the 440 benchmark-locked originals changes
nothing (≤0.3 pp).

## Numbers (2,210 FFHQ originals × 12 Alibaba variants = 26,519 retouched; FF++ training crop, box shared per pair)
| model | orig real/fake/filter | retouched real/fake/filter | balanced | paired excess | paired rank |
|---|---|---|---|---|---|
| HYB | 33.8/16.7/49.5 | 23.3/22.1/54.7 | 52.6 | +5.2 | 69.2 |
| HYB-F | 28.2/22.1/49.6 | 19.2/28.0/52.8 | 51.6 | +3.2 | 65.7 |
| HYB-D | 31.7/26.3/42.0 | 21.1/33.6/45.3 | 51.7 | +3.4 | 64.4 |
| SUP-F | 36.8/5.7/57.5 | 24.3/9.1/66.5 | 54.5 | +9.1 | **79.8** |
| MASK | 16.7/**55.9**/27.4 | 12.0/59.4/28.6 | 50.6 | +1.2 | 60.9 |
| RepViT | 0.8/2.5/**96.7** | 1.0/6.4/92.6 | 47.9 | −4.1 | 48.4 |

## Reading
1. **Absolute recognition is at chance for every FF++-trained three-way model.** The unedited FFHQ originals are already
   routed away from *real* (real 0.8–36.8 %): RepViT calls 96.7 % of them *filter* (the v8.17 failure, again); MASK calls
   55.9 % of genuine FFHQ photographs *fake*. High-quality still photographs are out of the FF++ video-frame domain.
2. **Relative signal exists for some operations only.** Paired rank (retouched gets a higher p_filter than its own original):
   eye enlarging 82–97 %, whitening 72–89 %, face lifting 52–79 %, **smoothing 13–61 % — below 50 % for 5 of 6 models**.
3. **Commercial skin smoothing is accused as forgery.** Smoothing-90 routed to *fake*: MASK 85.8 %, HYB 50.2 %, SUP-F 27.3 %
   (originals 55.9 / 16.7 / 5.7 %). This is the softness shortcut (BLURPROBE) acting on real beautification — exactly the
   false accusation the three-way label space was meant to remove. It is invisible on Celeb-DF-B because those presets are
   photometric colour grades.
4. **Every addition made on FF++ in-domain numbers hurt here.** Ranking by paired rank: SUP-F (observed forgeries only)
   79.8 > HYB 69.2 > HYB-F 65.7 > HYB-D 64.4 > MASK 60.9. Self-blending, faithful blending, symmetric degradation, part
   edits and the evidence head each lowered commercial-retouching signal while raising FF++/CDF numbers.

## Consequence
The paper's "beautified genuine faces are not accused" claim holds for photometric app presets (Celeb-DF-B) and scripted
filters, and **fails for commercial skin smoothing** (accused as fake at up to 86 %). This must go into the paper as a
measured limitation at minimum. Literature (scan 2026-09-29): RetouchingFFHQ already reports Megvii→Alibaba cross-API
type/level; FRRffusion and MoFRR already restore Alibaba retouching; Re-Face chains detect→revert. Open: one lightweight
model separating forged / beautified / real with cross-vendor evaluation and continuous, verifiable explanation quantities.

## Published detectors on the same pairs (PRE_DECLARED_published.md, 2026-09-29)
Threshold per detector = 95th percentile of its P(fake) on the untouched originals (5 % FPR, chosen on the test originals:
favours the binary detectors). Nine FF++-trained published detectors call 9.5-13.9 % of commercially retouched genuine faces
fake and 36-63 % of Smoothing-90 (SBI 11.3 / 37.3 %, SRM 13.9 / 62.8 %); SBI scores 72 % of retouched faces as more fake than
their own original. At native 0.5 they already call 20-46 % of the untouched FFHQ originals fake. UnivFD / NPR (generic AIGI
detectors) barely respond to faces and are reported for completeness. Ours: FF++-only evidence-head model 9.9 / 35.8 % (same
behaviour as the published ones); RU2 s1/s2 3.6 / 3.4 % and 3.5 / 3.7 % (below its own base rate; AUROC of P(fake) retouched vs
original 0.38-0.39, i.e. retouching moves RU2 away from fake), native argmax 0.2 %. Paper: Fig. accuse + text in Sec. VI-D.
