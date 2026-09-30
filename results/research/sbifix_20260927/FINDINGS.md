# FINDINGS — sbifix_20260927 (in progress)

## SBI-F (faithful blending, binary, Ubuntu) — 2026-09-27
- **Mechanism M: PASS** — training loss no longer collapses early (epoch 1 0.236 vs SBI-L 0.146; final 0.047 vs 0.019); val AUC 0.834 vs 0.79.
- **R0' FAIL**: CDFv2 **0.735** [0.702, 0.768] (SBI-L 0.620, official 0.817); DFD 0.886; at 5 % FPR FA 19.3 / MISS 20.2.
  The three deviations explain +0.115 of the 0.197 gap; remaining suspects: landmark model (MediaPipe vs dlib-81), face cropper.
- **Celeb-DF-B**: untreated AUC 0.852 (official 0.875); beautification ΔMISS **+36.8 pp [33.2, 40.8]** (official +35.5).
  SBI-L (flawed blending) +16.0 [13.5, 18.7]; HYB-L (same flawed blending, three-way) +1.5 / +1.3.
  ⇒ controlled replication: the binary self-blend objective opens the escape route in our own pipeline too.

## HYB-F (faithful blending, three-way, local) — 2026-09-27 — verdict per PRE_DECLARED §4: **NOT BUILD**
| bar | value | pass |
|---|---|---|
| F1 CDFv2 ≥ 0.79 | 0.7795 [0.746, 0.808] | FAIL (−0.0105) |
| F2 DFD ≥ 0.90 | 0.8999 [0.862, 0.934] | FAIL (−0.0001; not rounded) |
| F3 B1 0/12+ | none of 13 (11 published + SBI-L + SBI-F) | PASS |
| F4 in-domain ≥ 80 | 82.6 / 93.85 / 84.73 | PASS |
| F5 Celeb-DF-B E1 & ΔMISS CI ≤ +5 | E1 holds; +0.09 [−1.3, 1.65] | PASS |
| F6 Celeb-DF-B untreated genuine→fake ≤ 42.9 % | 45.09 % | FAIL |
HYB-L remains the method (PRE_DECLARED §4). HYB-F is reported as a row. Observations (not bars): Celeb-DF-B untreated AUC
0.874 (official SBI 0.875); california_dreamin failure case +5.3 pp (HYB-L +10.1/+11.9); beautified genuine → filter
71.8 % (HYB-L 55–57 %); HELDOUT-13 paired excess 39.4 pp (HYB-L 44.7–45.5; worse); FF++ FA/MISS 6.08 / 0.47.
**Same-pipeline control**: SBI-F (binary) ΔMISS +36.8 [33.2, 40.8] vs HYB-F (three-way) +0.1 [−1.3, 1.7]; per preset
SBI-F +25 to +45 on every preset.

## Official SBI code vs our faithful blend (2026-09-28, `external_baselines/SBI_official/`)
Same: one-sided source transform (colour + {downscale | sharpen}), affine on source+mask, elastic on mask, blend ratio
{0.25,0.5,0.75,1,1,1}, common transform after blending (RGBShift/HSV/BC p=0.3, JPEG 40–100 p=0.5), 8 frames × 100 epochs
≈ our 14 × 41,510 passes, SAM lr 1e-3, 380 px.
Different: (1) official blends on a wide-context crop (landmark box + 4×w/8, 2×h) then crops by the RetinaFace box with a
**random 5–20 % margin per side** at train (25 % at test); ours blends inside the 35 %-hull crop and trims 0–6 %.
(2) dlib-81 landmarks (25 % of the time 68) vs MediaPipe 478 for the hull. (3) official RandomDownScale is NEAREST ×2/×4
(harsher than ours) — the blur-shortcut candidate exists in the official recipe as well (probe running: `blur_probe.py`).
Remaining CDFv2 gap after our fixes: 0.735 vs 0.817; (1) is the prime suspect.

## Blur-shortcut probe, all detectors (2026-09-28, `blur_probe.py` / `blur_probe.json`; 300 FF++ test reals)
% of genuine frames called fake — ours at argmax, published at P(fake)>0.5:
| detector | orig | downscale ×2 | Gaussian σ1.5 | JPEG q30 |
|---|---|---|---|---|
| official SBI | 4.7 | 26.0 | **67.3** | 6.3 |
| Xception | 21.0 | 42.0 | 53.0 | 2.0 |
| EfficientNet-B4 | 19.0 | 41.7 | 56.7 | 9.3 |
| UCF | 19.7 | 36.0 | 42.3 | 4.0 |
| RepViT-S (ours, observed only) | 7.3 | 54.0 | 66.3 | 0.0 |
| HYB-L s2 | 6.3 | 74.3 | 95.3 | 7.7 |
| HYB-F | 8.3 | 67.7 | 91.0 | 11.3 |
| SBI-F (ours, binary self-blend) | 6.3 | 89.3 | 100.0 | 12.3 |
Softness is treated as forgery evidence by every FF++-trained detector; compression is not. Self-blend training makes it
worst (one-sided downscale in the source transform). This is the mechanism behind the untreated-Celeb-DF accusation
(Celeb-DF genuine frames are softer). HYBD (symmetric degradation) targets it; the same probe is a pre-declared check.

## HYBD (Addendum 2: symmetric degradation) — 2026-09-28, seed 20260928
CDFv2 **0.807** [0.778, 0.836] (frame; video 0.848), DFD 0.882 [0.837, 0.922] (video 0.851); FF++ 81.6/91.8/83.7; FA/MISS 5.24/0.84;
B1 0/13; HELDOUT-13 excess 35.7. Celeb-DF-B: untreated AUC **0.892** (official SBI 0.875), untreated genuine→fake **28.1 %**
(HYB-F 45.1), beautified genuine→fake 12.3 %, ΔMISS −1.4 [−3.3, +0.4], E1 holds.
Bars: F1' (CDFv2 ≥ 0.78) PASS; F6' (≤ 25 %) FAIL by 3.1 pp; F2 (DFD ≥ 0.90) FAIL (−0.018, inside CI). ⇒ NOT BUILD by rule;
reported as the variant with the best CDFv2 / Celeb-DF-B and halved accusation. Second seed (20260929) launched on Ubuntu.
Trade-off: DFD −0.02 to −0.03 and HELDOUT-13 excess −4 to −9 pp vs HYB-F/HYB-L.
- HYBD blur probe (Addendum 2 check, ≤ 15 % PASS): orig 5.3 / downscale ×2 **9.0** / blur σ1.5 **10.0** / JPEG q30 12.0 % called fake
  (HYB-F 8.3 / 67.7 / 91.0 / 11.3). Softness no longer carries label information; the residual 28 % Celeb-DF accusation is
  therefore not a softness effect (next suspects: colour/codec statistics, face scale).

## Residual Celeb-DF accusation probe (HYBD, 300 CDF genuine frames; `celeb_residual_probe.py`) — 2026-09-28
CDF real 32.2 % fake (subsample). Histogram-match to FF++: 25.6 % (but 62 % → filter); saturation ×1.3: 32.2; unsharp: 26.3;
crop tighter ×0.8: 41.1; looser ×1.25: 25.9 (64 % → filter, reflect padding). Laplacian var CDF 35 vs FF++ 79; mean RGB darker,
saturation higher. No single low-level factor explains the residual; treated as a domain gap (limitation). Side finding:
any whole-frame photometric change sends 60 %+ of genuine frames to *filter* — the scripted whole-frame filter shortcut.

## HYBD seed 2 (20260929) — 2026-09-28
CDFv2 **0.805** [0.775, 0.833] (seed 1: 0.807 — reproduced), DFD 0.890 (s1 0.882); FF++ 78.4/92.4/84.0 (real < 80: F4 fails
for this seed), FA/MISS 6.16/0.66, B1 0/13, HELDOUT-13 excess 38.4 (s1 35.7). Celeb-DF-B pending.
- HYBD seed 2 Celeb-DF-B: untreated AUC **0.891** (s1 0.892), untreated genuine→fake **27.5 %** (s1 28.1), beautified→fake 11.4,
  ΔMISS −1.8 [−3.6, −0.1], E1 holds. Two seeds agree on every Celeb-DF-B number; F6' (≤25 %) fails by 2.5–3.1 pp in both.
