# RU ru2_repvit_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 43.44, 'fake': 0.86, 'filter': 55.7} | pooled {'n': 26519, 'to_real': 15.8, 'to_fake': 0.52, 'to_filter': 83.68, 'balanced_acc': 63.99, 'paired_rank': 95.09}
Eq.4 {'TP': {'eye': 0.099, 'jaw': 0.114, 'white': 0.152, 'smooth': 0.943}, 'TN_same_image': {'eye': 0.897, 'jaw': 0.926, 'white': 0.82, 'smooth': 0.208}, 'AC': {'eye': 0.05, 'jaw': 0.062, 'white': 0.046, 'smooth': 0.165}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.986, 'jaw': 0.977, 'white': 0.986, 'smooth': 0.976}
quantities {"eye": {"n": 6629, "spearman": 0.324, "mae": 0.026, "pred_mean": 0.0031, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0067, "orig_pred_mean": 0.0017}, "jaw": {"n": 6630, "spearman": 0.072, "mae": 0.0193, "pred_mean": 0.0013, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0056, "orig_pred_mean": -0.0001}, "white": {"n": 6630, "spearman": -0.05, "mae": 0.5159, "pred_mean": 0.0129, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0047, "orig_pred_mean": 0.0044}, "smooth": {"n": 6630, "spearman": 0.479, "mae": 0.0812, "pred_mean": 0.1191, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.031, "orig_pred_mean": 0.0027}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 26.56 | 0.45 | 72.99 | 58.64 | 97.19 | 0.046 |
| EyeEnlarging_60 | 2209 | 20.55 | 0.32 | 79.13 | 61.72 | 98.82 | 0.086 |
| EyeEnlarging_90 | 2210 | 15.61 | 0.32 | 84.07 | 64.19 | 99.23 | 0.165 |
| FaceLifting_30 | 2210 | 26.88 | 0.45 | 72.67 | 58.48 | 90.86 | 0.08 |
| FaceLifting_60 | 2210 | 22.81 | 0.45 | 76.74 | 60.52 | 94.52 | 0.114 |
| FaceLifting_90 | 2210 | 19.0 | 0.54 | 80.45 | 62.38 | 96.29 | 0.148 |
| Whitening_30 | 2210 | 25.38 | 0.54 | 74.07 | 59.19 | 85.77 | 0.061 |
| Whitening_60 | 2210 | 18.42 | 0.59 | 81.0 | 62.65 | 89.1 | 0.134 |
| Whitening_90 | 2210 | 13.26 | 0.63 | 86.11 | 65.2 | 91.45 | 0.261 |
| Smoothing_30 | 2210 | 1.04 | 0.41 | 98.55 | 71.43 | 99.59 | 0.843 |
| Smoothing_60 | 2210 | 0.09 | 0.36 | 99.55 | 71.92 | 99.64 | 0.989 |
| Smoothing_90 | 2210 | 0.05 | 1.13 | 98.82 | 71.56 | 98.64 | 0.998 |

## FF++ / cross-dataset
{"indomain": {"real": 79.33, "fake": 87.5, "filter": 63.6}, "FA": 15.58, "real_to_filter": 12.01, "MISS": 1.47, "heldout13": {"filter": 45.29, "fake": 22.19, "paired_excess_pp": 33.28}, "cdf": {"auc": 0.7717, "real_called_fake": 20.52}, "dfd": {"auc": 0.8923, "real_called_fake": 12.88}, "bars": {"D1_cdf>=0.78": false, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
