# Edit-sensitivity as evidence (Addendum 29; fitted on FF++ train, tested on FF++ val + held-out filters)

## clipe5f_s20260929

Mean Delta per probe edit (vignette, monochrome, warm, cool_tint, smooth, contrast):
- clean: genuine [1.9, 0.97, 0.09, 0.01, 0.52, 0.68] forged [-0.48, -0.68, -0.11, 0.16, -1.36, 0.17]
- filtered: genuine [1.54, -0.19, 0.32, -0.05, 0.79, 0.39] forged [-0.94, -0.79, -0.55, -0.35, -0.34, -0.35]

| rule | AUC clean | AUC filtered | FA filtered | MISS clean → filtered |
|---|---|---|---|---|
| logit only | 0.988 | 0.957 | 18.7 | 6.3 → 5.0 |
| -mean(Delta) only | 0.794 | 0.828 | 14.0 | 57.7 → 41.3 |
| logit + mean(Delta) | 0.986 | 0.955 | 19.3 | 5.7 → 5.0 |
| logit + Delta_1..K | 0.985 | 0.953 | 16.3 | 7.0 → 7.7 |

Saturation control (clean-logit deciles): mean Delta genuine / forged
| decile | n gen / forged | Δ genuine | Δ forged |
|---|---|---|---|
| 0 | 58 / 0 | 0.55 | None |
| 1 | 58 / 0 | 0.76 | None |
| 2 | 64 / 0 | 0.88 | None |
| 3 | 54 / 6 | 1.15 | 0.96 |
| 4 | 49 / 11 | 0.48 | 0.1 |
| 5 | 17 / 43 | -0.57 | -0.74 |
| 6 | 0 / 60 | None | -1.12 |
| 7 | 0 / 60 | None | -0.26 |
| 8 | 0 / 58 | None | -0.1 |
| 9 | 0 / 62 | None | -0.02 |

## clipe5fg0_s20260929

Mean Delta per probe edit (vignette, monochrome, warm, cool_tint, smooth, contrast):
- clean: genuine [3.95, 1.04, 0.02, 0.14, 0.25, 0.39] forged [-0.98, -0.94, -0.97, -0.13, -1.07, -0.25]
- filtered: genuine [3.27, -0.1, 1.02, 0.41, 1.07, 0.05] forged [-0.27, -0.73, -0.04, -0.04, -0.21, -0.21]

| rule | AUC clean | AUC filtered | FA filtered | MISS clean → filtered |
|---|---|---|---|---|
| logit only | 0.985 | 0.957 | 20.7 | 6.7 → 4.7 |
| -mean(Delta) only | 0.868 | 0.806 | 9.7 | 51.7 → 75.0 |
| logit + mean(Delta) | 0.984 | 0.956 | 19.7 | 6.7 → 5.0 |
| logit + Delta_1..K | 0.981 | 0.956 | 21.7 | 7.3 → 5.0 |

Saturation control (clean-logit deciles): mean Delta genuine / forged
| decile | n gen / forged | Δ genuine | Δ forged |
|---|---|---|---|
| 0 | 60 / 0 | 1.23 | None |
| 1 | 55 / 0 | 1.13 | None |
| 2 | 62 / 3 | 1.33 | 1.6 |
| 3 | 58 / 2 | 1.09 | 0.57 |
| 4 | 46 / 14 | 0.64 | 0.68 |
| 5 | 18 / 42 | -1.0 | -0.81 |
| 6 | 1 / 57 | -3.81 | -1.2 |
| 7 | 0 / 59 | None | -0.62 |
| 8 | 0 / 58 | None | -0.7 |
| 9 | 0 / 65 | None | -0.8 |
