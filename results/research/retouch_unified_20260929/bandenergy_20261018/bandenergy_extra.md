### Threshold scan (7 Celeb-DF forms, 17 detectors): E_hf(t) loss as predictor of FA

| t (c/px) | pooled Spearman native | mean det. Spearman native | FE partial R2 native | pooled Spearman view256 | mean det. Spearman view256 | FE partial R2 view256 |
|---|---|---|---|---|---|---|
| 0.02 | +0.344 | +0.368 | 0.283 | +0.305 | +0.323 | 0.228 |
| 0.03 | +0.305 | +0.323 | 0.259 | +0.305 | +0.323 | 0.213 |
| 0.05 | +0.305 | +0.323 | 0.244 | +0.305 | +0.323 | 0.219 |
| 0.10 | +0.305 | +0.323 | 0.066 | +0.305 | +0.323 | 0.074 |
| 0.15 | -0.181 | -0.209 | 0.009 | -0.181 | -0.209 | 0.010 |
| 0.20 | -0.049 | -0.075 | 0.000 | -0.049 | -0.075 | 0.000 |
| 0.25 | +0.058 | +0.047 | 0.043 | -0.049 | -0.075 | 0.010 |
| 0.30 | +0.203 | +0.206 | 0.097 | -0.049 | -0.075 | 0.030 |
| 0.35 | +0.358 | +0.381 | 0.140 | +0.097 | +0.091 | 0.058 |
| 0.40 | +0.358 | +0.381 | 0.162 | +0.203 | +0.206 | 0.085 |
| 0.45 | +0.450 | +0.482 | 0.198 | +0.203 | +0.206 | 0.106 |

Best threshold by FE partial R2: native t=0.02 (R2 0.283, pooled rho +0.344); view256 t=0.02 (R2 0.228, pooled rho +0.305).

### Band scan (energy in [t, t+0.1)), native

| band | pooled Spearman | mean det. Spearman | FE partial R2 |
|---|---|---|---|
| [0.02, 0.12) | +0.450 | +0.482 | 0.302 |
| [0.03, 0.13) | +0.344 | +0.368 | 0.274 |
| [0.05, 0.15) | +0.305 | +0.323 | 0.256 |
| [0.10, 0.20) | +0.305 | +0.323 | 0.080 |
| [0.15, 0.25) | -0.181 | -0.209 | 0.033 |
| [0.20, 0.30) | -0.070 | -0.096 | 0.010 |
| [0.25, 0.35) | +0.018 | -0.005 | 0.016 |
| [0.30, 0.40) | +0.203 | +0.206 | 0.068 |
| [0.35, 0.45) | +0.203 | +0.206 | 0.105 |
| [0.40, 0.50) | +0.358 | +0.381 | 0.139 |

### Matched-form contrasts (FA difference in percentage points, 17 published detectors; Wilcoxon signed-rank)

| contrast | what differs | in-face loss a vs b (E_hf0.25 box / Laplacian hull / mean abs change hull) | detectors with dFA > 0 | median dFA | p | excl. NPR: n>0, median, p |
|---|---|---|---|---|---|---|
| fl06 - bil9 | same bilateral kernel class (d 9, sigma ~48-50), applied inside the face hull only vs the whole crop | 0.18/0.28/1.5 vs 0.20/0.33/1.9 | 16/17 | +28.0 | 0.0005 | 16/16, +30.5, 3.1e-05 |
| fl12 - bil21 | face-local bilateral (d ~19, sigma ~96) vs whole-crop bilateral (21, 100, 100) | 0.72/0.82/3.8 vs 0.94/1.14/5.6 | 14/17 | +9.0 | 0.0092 | 14/16, +9.1, 0.0013 |
| fl12 - bil15 | face-local bilateral (d ~19, sigma ~96) vs whole-crop bilateral (15, 80, 80) | 0.72/0.82/3.8 vs 0.70/0.76/3.8 | 16/17 | +18.3 | 0.00066 | 16/16, +19.2, 3.1e-05 |
| bil21 - gblend | edge-preserving bilateral vs uniform 50% Gaussian blend with the same E_hf(0.25) loss | 0.94/1.14/5.6 vs 0.94/0.89/1.6 | 16/17 | +66.7 | 4.6e-05 | 15/16, +67.5, 6.1e-05 |
| bil15 - gblend | edge-preserving bilateral that removes LESS high-frequency energy than the Gaussian blend | 0.70/0.76/3.8 vs 0.94/0.89/1.6 | 17/17 | +55.4 | 1.5e-05 | 16/16, +55.8, 3.1e-05 |
| bil9 - median5 | bilateral that removes LESS high-frequency energy than the 5x5 median | 0.20/0.33/1.9 vs 0.26/0.57/1.5 | 15/17 | +23.5 | 0.00015 | 14/16, +26.0, 0.00031 |
| fl06 - median5 | face-local bilateral that removes LESS high-frequency energy than the 5x5 median | 0.18/0.28/1.5 vs 0.26/0.57/1.5 | 16/17 | +63.3 | 4.6e-05 | 16/16, +64.8, 3.1e-05 |
