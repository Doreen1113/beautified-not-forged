# Band-energy mechanism analysis (2026-10-18): does high-frequency texture loss explain the accusation of smoothed genuine faces?

Question. All 17 published detectors score skin-smoothed genuine faces as more forged (Addendum 38, `../SMOOTH38.md`). We asked whether one scalar image statistic, the loss of high-frequency (texture) energy inside the face, lines up with each detector's false-alarm rate (FA) across the seven Addendum-38 smoothing forms (bil9, bil15, bil21, median5, gblend, fl06, fl12) and the commercial Smoothing-90 renders.

**Answer: no.** The pre-stated statistic (E_hf at 0.25 cycles/pixel) has a pooled Spearman of +0.06 over 17 detectors x 7 forms (−0.01 on the plotted 8-form set) and explains 2.5% of the within-detector variance of logit(FA). The form that removes the most high-frequency energy (the 50% Gaussian blend) is the one accused least; a face-local bilateral filter with the same kernel as the whole-crop one, and the same in-face loss, is accused 28 points more (16/17 detectors). Mean absolute pixel change inside the face is the best of the three statistics (pooled Spearman +0.49, 12/17 detectors with rho >= 0.5, partial R2 0.27) but is still a partial account. What the matched comparisons show instead is that accusation follows (i) low-frequency flattening of skin (energy below ~0.12 c/px, the band an edge-preserving filter removes and a mild Gaussian blur does not) and (ii) spatial confinement of the smoothing to the face.

## What was computed

Frames. 400 genuine Celeb-DF-v2 frames with MediaPipe landmarks, drawn with seed 0 from the 1,348 genuine frames of the Addendum-38 list (`../smooth38_list.json`); the seven forms were read from the cached lossless renders under `N:\2603055\AIGC\smooth_probe_20261016\<form>\` (the same files every detector scored). Landmarks were re-detected on the untreated frame (0 failures). Commercial Smoothing-30/60/90: 200 FFHQ stems (seed 0) from `../../alipair_zeroshot_20260929/boxes.json`, read from the shared-box crops the detectors scored (`C:\My_Project\AIGC\alipair_crops\orig_0__<stem>.png` and `Smoothing_<lv>__<stem>.png`; 0 landmark failures).

Face region. The bounding box of the 478-landmark hull on the untreated frame, reused for every form of that frame (mean box 173 x 213 px on the ~330-px Celeb-DF frames; 727 x 884 px on the 960-px commercial crops). For the pixel-change and Laplacian statistics the hull mask itself was used.

Statistics (luminance = OpenCV grey of RGB):
- E_hf(t) = power at radial frequency r > t divided by total power, 2-D Hann window, DC removed; r in cycles/pixel (Nyquist 0.5). Pre-stated primary t = 0.25; also 0.15 and 0.35 (and 0.125 = a quarter of Nyquist). Texture loss of a form = mean over frames of −log(E_hf(form)/E_hf(untreated)); positive = energy lost. The binned radial spectrum (0.01 c/px bins) of every frame and form is saved so any band can be re-evaluated.
- (a) mean |x_s − x| over RGB inside the hull (8-bit units); (b) −log of the Laplacian-variance ratio inside the hull (sharpness loss).
- Each statistic at the stored resolution ("native") and after resizing the crop to a 256-px longer side ("view256", INTER_AREA). The 7 Celeb-DF forms are reported at native resolution (primary); the 960-px commercial crops are only comparable at view256, so every 8- and 10-form set uses view256.

FA. Parsed from the `| detector | AUC | miss | bil9 | ... |` table of `../SMOOTH38.md` (the number after " / " in each cell = false alarms on smoothed genuine frames at the 5%-FPR threshold set on untreated genuine frames), cross-checked cell by cell against `../smooth38.json` (0 mismatches); Smoothing-30/60/90 accusation at the 5%-FPR-on-originals threshold from `../../alipair_zeroshot_20260929/published_ali.json` (`by_op.Smoothing_90.fake_at_t`, the "smoothing-90 @5%FPR" column of `PUBLISHED_RESULTS.md`). NPR's commercial numbers are n/a in the paper (AUROC 0.40, inverted), so NPR is excluded wherever a commercial form is used. Saved as `fa_parsed.json` (also contains our own arms, 7 forms).

Analysis. Per detector: Spearman and Pearson of FA across forms (n = 7, 8, 10). Pooled: Spearman/Pearson over all detector x form points, and an OLS fixed-effects fit logit(FA) = a_detector + b * loss (FA clipped to [0.5, 99.5]%), reporting b, t and the partial R2 (share of within-detector variance explained). Bootstrap over frames (200 draws, every form's loss re-estimated, FA fixed) for CIs. Point sets: 7forms = Celeb-DF forms x 17 detectors (119 points); 8forms = + S-90, NPR excluded (128); 8forms_all = the plotted set, 17 detectors on the 7 forms + 16 on S-90 (135); 10forms = + S-30/S-60, NPR excluded (160).

## Texture loss per form

| form | E_hf 0.25 native [95% CI] | E_hf 0.25 view256 | E_hf 0.15 native | E_hf 0.35 native | Laplacian-var loss (hull) | mean abs change (hull, 8-bit) |
|---|---|---|---|---|---|---|
| Smoothing_30 (commercial) | 0.082 [0.069, 0.095] | 0.132 | 0.112 | 0.039 | 0.124 | 3.33 |
| Smoothing_60 (commercial) | 0.150 [0.120, 0.174] | 0.201 | 0.197 | 0.068 | 0.179 | 4.04 |
| Smoothing_90 (commercial) | 0.165 [0.117, 0.202] | 0.250 | 0.234 | 0.042 | 0.200 | 4.59 |
| fl06 | 0.185 [0.155, 0.216] | 0.144 | 0.258 | 0.245 | 0.285 | 1.52 |
| bil9 | 0.199 [0.162, 0.229] | 0.187 | 0.321 | 0.323 | 0.332 | 1.92 |
| median5 | 0.255 [0.225, 0.282] | 0.371 | 0.836 | 0.048 | 0.568 | 1.48 |
| bil15 | 0.699 [0.656, 0.745] | 0.582 | 0.685 | 0.681 | 0.759 | 3.77 |
| fl12 | 0.719 [0.674, 0.767] | 0.655 | 0.776 | 0.659 | 0.821 | 3.80 |
| gblend | 0.941 [0.927, 0.951] | 0.824 | 1.055 | 0.711 | 0.895 | 1.60 |
| bil21 | 0.942 [0.903, 0.985] | 0.780 | 1.055 | 0.800 | 1.140 | 5.64 |

The commercial native-resolution values are on a 960-px grid and are not comparable with the Celeb-DF rows; use view256. The order of the seven Celeb-DF forms is the same at both resolutions.

## Per-detector correlations (FA vs loss)

Seven Celeb-DF forms, native resolution (Spearman; n = 7, |rho| >= 0.79 needed for p < 0.05):

| detector | family | E_hf 0.25 | E_hf 0.15 | E_hf 0.35 | Laplacian | mean abs change |
|---|---|---|---|---|---|---|
| xception | cnn | −0.07 | −0.46 | 0.00 | −0.07 | +0.50 |
| effnb4 | cnn | +0.36 | −0.14 | +0.46 | +0.36 | +0.86 |
| f3net | cnn | +0.25 | −0.21 | +0.29 | +0.25 | +0.79 |
| spsl | cnn | −0.18 | −0.57 | −0.07 | −0.18 | +0.43 |
| ucf | cnn | −0.61 | −0.75 | −0.54 | −0.61 | −0.07 |
| recce | cnn | +0.25 | −0.21 | +0.29 | +0.25 | +0.79 |
| core | cnn | +0.32 | −0.14 | +0.39 | +0.32 | +0.82 |
| srm | cnn | −0.43 | −0.75 | −0.29 | −0.43 | +0.29 |
| sbi | cnn | +0.18 | −0.21 | +0.29 | +0.18 | +0.54 |
| caddm | cnn | +0.04 | −0.39 | +0.18 | +0.04 | +0.57 |
| laanetr | cnn | −0.04 | −0.45 | +0.14 | −0.04 | +0.50 |
| univfd | gen | +0.36 | −0.04 | +0.32 | +0.36 | +0.71 |
| npr | gen | +0.37 | +0.22 | +0.56 | +0.37 | +0.48 |
| effort | clip | +0.11 | −0.18 | +0.04 | +0.11 | +0.36 |
| fadapter | clip | −0.07 | −0.46 | 0.00 | −0.07 | +0.50 |
| gend | clip | −0.07 | −0.46 | 0.00 | −0.07 | +0.50 |
| dfdhr | clip | +0.04 | −0.39 | +0.18 | +0.04 | +0.57 |

The eight-form (view256) and Pearson versions are in `bandenergy_tables.md`; they do not change the picture (E_hf 0.25 Spearman between −0.60 and +0.21 for every detector).

## Pooled correlations and which statistic predicts best

| statistic | resolution | set | points | pooled Spearman [95% CI, frames] | pooled Pearson | mean per-detector Spearman | detectors rho >= 0.5 | FE slope (t) | FE partial R2 |
|---|---|---|---|---|---|---|---|---|---|
| E_hf 0.25 (primary) | native | 7forms | 119 | +0.058 [−0.113, +0.058] | +0.107 | +0.047 | 0/17 | +1.12 (1.6) | 0.025 |
| E_hf 0.25 | view256 | 8forms_all (figure) | 135 | −0.014 [−0.014, −0.014] | +0.069 | −0.036 | 0/17 | +1.17 (1.5) | 0.019 |
| E_hf 0.25 | view256 | 8forms (no NPR) | 128 | −0.038 | +0.058 | −0.057 | 0/16 | +1.10 (1.4) | 0.016 |
| E_hf 0.15 | native | 7forms | 119 | −0.288 [−0.288, −0.181] | −0.185 | −0.331 | 0/17 | −0.93 (−1.2) | 0.015 |
| E_hf 0.35 | native | 7forms | 119 | +0.140 [+0.140, +0.231] | +0.294 | +0.132 | 1/17 | +2.78 (3.5) | 0.110 |
| Laplacian-variance loss | native | 7forms | 119 | +0.058 | +0.104 | +0.047 | 0/17 | +1.23 (1.6) | 0.025 |
| Laplacian-variance loss | view256 | 8forms_all | 135 | +0.138 [+0.138, +0.263] | +0.203 | +0.130 | 0/17 | +1.88 (2.9) | 0.066 |
| **mean abs change (hull)** | native | 7forms | 119 | **+0.493 [+0.324, +0.493]** | +0.503 | +0.537 | 12/17 | +0.78 (6.2) | **0.274** |
| mean abs change (hull) | view256 | 8forms_all | 135 | +0.361 [+0.226, +0.405] | +0.426 | +0.411 | 5/17 | +0.66 (5.4) | 0.197 |
| E_hf 0.25 | view256 | 10forms (+S-30/60) | 160 | +0.201 | +0.250 | +0.209 | 0/16 | +2.45 (3.7) | 0.087 |
| mean abs change (hull) | view256 | 10forms | 160 | +0.398 | +0.399 | +0.424 | 6/16 | +0.66 (5.2) | 0.159 |

Ranking (all 72 combinations in `bandenergy.json["ranking"]`): mean absolute pixel change > E_hf 0.35 ≈ Laplacian > E_hf 0.25 > E_hf 0.15 (negative). Among the E_hf thresholds, 0.35 is the most predictive and 0.15 the least, but none reaches a pooled Spearman of 0.2 on the 7- or 8-form sets. The 10-form correlations are higher only because the three commercial doses (S-30 < S-60 < S-90 in both loss and FA) add a monotone series from one vendor.

Bootstrap note. The frame-bootstrap CIs of the Spearman statistics are degenerate ([x, x]) whenever the ordering of the forms by loss is stable across draws, because the pooled Spearman depends on the losses only through the form ranks; the Pearson and fixed-effects-slope CIs (also in `bandenergy.json`) are continuous. The CIs cover frame sampling only, not the uncertainty of the FA rates (their own CIs are in `fa_parsed.json`) nor the choice of forms.

## Threshold scan and matched-form contrasts (`bandenergy_extra.md`, `fig_bandenergy_supp.png`)

Scanning the threshold t from 0.02 to 0.45 c/px (7 forms, native): pooled Spearman +0.34 at t = 0.02, +0.31 for 0.03-0.10, −0.29 at 0.16, ~0 at 0.20-0.25, rising to +0.45 at 0.45; the FE partial R2 is largest for the lowest band ([0.02, 0.12): 0.30) and smallest between 0.15 and 0.30 (< 0.04). So it is the energy in the low band (periods longer than ~8 px: skin shading and pore-scale blotchiness), not the high band, that moves with accusation, and even that band explains under a third of the within-detector variance. Panel (a) of the supplementary figure shows why: the Gaussian blend and the d21 bilateral remove the same energy above 0.2 c/px, but only the bilateral filters (and the face-local ones) remove energy below 0.12 c/px; the 5x5 median removes a lot at 0.15-0.25 c/px and little elsewhere.

Matched-form contrasts (FA difference in points; 17 published detectors; Wilcoxon signed-rank):

| contrast | what differs | in-face loss a vs b (E_hf 0.25 / Laplacian / abs change) | detectors with dFA > 0 | median dFA | p |
|---|---|---|---|---|---|
| fl06 − bil9 | same bilateral kernel class (d 9, sigma ~48-50), face hull only vs whole crop | 0.18/0.28/1.5 vs 0.20/0.33/1.9 | 16/17 | +28.0 | 0.0005 |
| fl12 − bil15 | face-local bilateral (d ~19, sigma ~96) vs whole-crop (15, 80, 80) | 0.72/0.82/3.8 vs 0.70/0.76/3.8 | 16/17 | +18.3 | 0.0007 |
| fl12 − bil21 | face-local vs whole-crop (21, 100, 100), the latter removing more | 0.72/0.82/3.8 vs 0.94/1.14/5.6 | 14/17 | +9.0 | 0.009 |
| bil21 − gblend | edge-preserving bilateral vs uniform 50% Gaussian blend, same E_hf 0.25 loss | 0.94/1.14/5.6 vs 0.94/0.89/1.6 | 16/17 | +66.7 | 5e-05 |
| bil15 − gblend | bilateral that removes less high-frequency energy than the Gaussian blend | 0.70/0.76/3.8 vs 0.94/0.89/1.6 | 17/17 | +55.4 | 2e-05 |
| bil9 − median5 | bilateral that removes less high-frequency energy than the median | 0.20/0.33/1.9 vs 0.26/0.57/1.5 | 15/17 | +23.5 | 0.0002 |
| fl06 − median5 | face-local bilateral that removes less than the median | 0.18/0.28/1.5 vs 0.26/0.57/1.5 | 16/17 | +63.3 | 5e-05 |

The one detector against the direction in most rows is NPR, which is saturated (100% FA) on every whole-crop form. Our own arms (trained with smoothing exposure) have Spearman between −0.12 and +0.43 on the seven forms (`bandenergy_tables.md`); their FA is not a function of texture loss either.

## Figure

`fig_bandenergy.pdf` / `fig_bandenergy.png` (3.3 x 2.5 in, `make_fig_bandenergy.py`, style `docs/paper_v2/figstyle.py`): (a) texture loss (E_hf 0.25, view256, 95% frame-bootstrap CI) per form, ordered; the hollow marker is the commercial S-90 (different source images, 960-px crops resized); (b) FA of every published detector on every form against that loss (grey circles face-forgery CNNs, sky-blue triangles generated-image detectors UnivFD/NPR, pink squares CLIP-based; strip numbers match the rows of (a); dashed line = the 5% design FPR), pooled Spearman −0.01. Supplement `fig_bandenergy_supp.pdf/png` (7.16 x 2.6 in): (a) log power ratio form/untreated against radial frequency, (b) threshold scan, (c) the three main matched contrasts per detector. Palette: the project's fixed Okabe-Ito family colours (the dataviz validator could not be run, no node on this machine).

## Caveats

- Correlational, and the number of forms is small (7 or 8); a per-detector Spearman needs |rho| >= 0.79 to be significant at n = 7. The pooled fits treat detector x form points as independent although all detectors saw the same 1,348 frames.
- The forms differ in more than one property at once (kernel type, strength, spatial extent, whether the background is touched, and for S-90 the source images, resolution and threshold population), so the matched contrasts isolate one factor only approximately; the kernels in fl06/bil9 and fl12/bil15 are matched by construction (ops.op_smooth sets d = frac x jaw width and sigma = d x 80/15), not identical.
- The statistic is computed on the landmark-hull bounding box; for face-local forms the box corners are untouched, so their box-level E_hf loss slightly understates the in-face loss (the hull-masked Laplacian and pixel-change columns do not have this bias and give the same conclusions).
- "What the detectors see" depends on each model's input size (224-384 px); view256 is one representative choice. The native and view256 results agree in sign and ordering for the seven Celeb-DF forms.
- FA rates are taken as point estimates; their bootstrap CIs (from SMOOTH38) are 3-10 points wide and are stored in `fa_parsed.json` but not propagated.
- Frames with zero energy in a narrow band (1-9 of 400 for fl06/fl12 above 0.28 c/px) were excluded from that band in the scan only; the primary statistics have no such frames.

## Files (all under `C:\My_Project\AIGC\results\research\retouch_unified_20260929\bandenergy_20261018\`)

- `bandenergy.py` : statistics, FA parsing, analysis, tables (CPU; `--recompute` to redo the frame loop). Logs `run.log`, `run2.log`.
- `bandenergy_frames.npz` : per-frame statistics (keys `cdf_{native|view}_{form}_{ehf|rad|lapvar|mad}`, `ali_...` for the commercial pairs, frame stems/indices/videos, boxes, thresholds, radial bins).
- `fa_parsed.json` : FA per detector and form as parsed (with CIs, miss rise, class, commercial thresholds).
- `bandenergy.json` : loss per form, per-detector and pooled correlations, fixed-effects fits, bootstrap CIs, ranking, mean radial spectra. `bandenergy_tables.md`: the same as markdown.
- `bandenergy_extra.py` -> `bandenergy_extra.json`, `bandenergy_extra.md`, `fig_bandenergy_supp.{pdf,png}` : threshold/band scan, matched contrasts, spectra.
- `make_fig_bandenergy.py` -> `fig_bandenergy.{pdf,png}`.
- Inputs read only: `../smooth_probe38.py`, `../smooth38_list.json`, `../SMOOTH38.md`, `../smooth38.json`, `N:\2603055\AIGC\smooth_probe_20261016\`, `../../alipair_zeroshot_20260929/{boxes.json,published_ali.json}`, `C:\My_Project\AIGC\alipair_crops\`, `C:\My_Project\AIGC\face_landmarker.task`.
