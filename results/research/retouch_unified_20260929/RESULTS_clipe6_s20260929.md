# RU clipe6_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 81.27, 'fake': 0.54, 'filter': 18.19} | pooled {'n': 26519, 'to_real': 32.66, 'to_fake': 0.66, 'to_filter': 66.68, 'balanced_acc': 74.24, 'paired_rank': 94.45}
Eq.4 {'TP': {'eye': 0.253, 'jaw': 0.299, 'white': 0.298, 'smooth': 0.952}, 'TN_same_image': {'eye': 0.809, 'jaw': 0.919, 'white': 0.785, 'smooth': 0.504}, 'AC': {'eye': 0.243, 'jaw': 0.287, 'white': 0.225, 'smooth': 0.463}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.984, 'jaw': 0.978, 'white': 0.952, 'smooth': 0.987}
quantities {"eye": {"n": 6629, "spearman": 0.334, "mae": 0.026, "pred_mean": 0.0035, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0097, "orig_pred_mean": -0.0021}, "jaw": {"n": 6630, "spearman": 0.158, "mae": 0.0178, "pred_mean": 0.006, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0094, "orig_pred_mean": -0.0009}, "white": {"n": 6630, "spearman": -0.093, "mae": 0.4993, "pred_mean": 0.0444, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0083, "orig_pred_mean": 0.0084}, "smooth": {"n": 6630, "spearman": 0.259, "mae": 0.104, "pred_mean": 0.0827, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.02, "orig_pred_mean": 0.0018}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 52.67 | 0.45 | 46.88 | 64.34 | 95.77 | 0.1 |
| EyeEnlarging_60 | 2209 | 38.39 | 0.45 | 61.16 | 71.48 | 97.6 | 0.265 |
| EyeEnlarging_90 | 2210 | 29.5 | 0.59 | 69.91 | 75.86 | 98.3 | 0.395 |
| FaceLifting_30 | 2210 | 55.88 | 0.27 | 43.85 | 62.83 | 87.83 | 0.22 |
| FaceLifting_60 | 2210 | 47.78 | 0.32 | 51.9 | 66.86 | 93.24 | 0.299 |
| FaceLifting_90 | 2210 | 39.1 | 0.32 | 60.59 | 71.2 | 95.29 | 0.378 |
| Whitening_30 | 2210 | 51.72 | 0.45 | 47.83 | 64.82 | 86.4 | 0.124 |
| Whitening_60 | 2210 | 39.41 | 0.54 | 60.05 | 70.93 | 89.0 | 0.282 |
| Whitening_90 | 2210 | 29.19 | 1.04 | 69.77 | 75.79 | 93.19 | 0.487 |
| Smoothing_30 | 2210 | 7.69 | 0.59 | 91.72 | 86.76 | 98.55 | 0.867 |
| Smoothing_60 | 2210 | 0.36 | 0.95 | 98.69 | 90.25 | 99.41 | 0.994 |
| Smoothing_90 | 2210 | 0.23 | 1.99 | 97.78 | 89.8 | 98.87 | 0.996 |

## FF++ / cross-dataset
{"indomain": {"real": 80.32, "fake": 84.14, "filter": 76.37}, "FA": 15.05, "real_to_filter": 10.03, "MISS": 1.78, "heldout13": {"filter": 72.42, "fake": 20.74, "paired_excess_pp": 62.39}, "cdf": {"auc": 0.8624, "real_called_fake": 18.22}, "dfd": {"auc": 0.9507, "real_called_fake": 6.2}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
