# RU ru4e_effb4_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 81.04, 'fake': 0.36, 'filter': 18.6} | pooled {'n': 26519, 'to_real': 35.86, 'to_fake': 0.33, 'to_filter': 63.81, 'balanced_acc': 72.61, 'paired_rank': 93.85}
Eq.4 {'TP': {'eye': 0.232, 'jaw': 0.284, 'white': 0.295, 'smooth': 0.957}, 'TN_same_image': {'eye': 0.792, 'jaw': 0.903, 'white': 0.754, 'smooth': 0.284}, 'AC': {'eye': 0.206, 'jaw': 0.246, 'white': 0.168, 'smooth': 0.253}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.984, 'jaw': 0.966, 'white': 0.954, 'smooth': 0.982}
quantities {"eye": {"n": 6629, "spearman": 0.446, "mae": 0.0255, "pred_mean": 0.0033, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0071, "orig_pred_mean": 0.0001}, "jaw": {"n": 6630, "spearman": 0.169, "mae": 0.0174, "pred_mean": 0.0034, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0065, "orig_pred_mean": 0.0004}, "white": {"n": 6630, "spearman": -0.208, "mae": 0.4985, "pred_mean": 0.0444, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0041, "orig_pred_mean": 0.0096}, "smooth": {"n": 6630, "spearman": 0.472, "mae": 0.0838, "pred_mean": 0.1091, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0218, "orig_pred_mean": 0.0006}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 54.66 | 0.27 | 45.07 | 63.23 | 97.1 | 0.089 |
| EyeEnlarging_60 | 2209 | 41.1 | 0.32 | 58.58 | 69.99 | 98.87 | 0.244 |
| EyeEnlarging_90 | 2210 | 32.62 | 0.36 | 67.01 | 74.21 | 99.1 | 0.363 |
| FaceLifting_30 | 2210 | 60.09 | 0.32 | 39.59 | 60.5 | 84.28 | 0.219 |
| FaceLifting_60 | 2210 | 53.89 | 0.32 | 45.79 | 63.6 | 89.43 | 0.286 |
| FaceLifting_90 | 2210 | 48.6 | 0.32 | 51.09 | 66.24 | 92.74 | 0.345 |
| Whitening_30 | 2210 | 55.2 | 0.36 | 44.43 | 62.92 | 86.52 | 0.145 |
| Whitening_60 | 2210 | 43.62 | 0.36 | 56.02 | 68.71 | 88.64 | 0.293 |
| Whitening_90 | 2210 | 35.25 | 0.54 | 64.21 | 72.8 | 90.9 | 0.448 |
| Smoothing_30 | 2210 | 4.75 | 0.23 | 95.02 | 88.21 | 99.55 | 0.883 |
| Smoothing_60 | 2210 | 0.36 | 0.14 | 99.5 | 90.45 | 99.86 | 0.991 |
| Smoothing_90 | 2210 | 0.18 | 0.41 | 99.41 | 90.41 | 99.23 | 0.996 |

## FF++ / cross-dataset
{"indomain": {"real": 74.24, "fake": 93.27, "filter": 76.44}, "FA": 11.7, "real_to_filter": 14.13, "MISS": 0.5, "heldout13": {"filter": 46.28, "fake": 18.39, "paired_excess_pp": 32.15}, "cdf": {"auc": 0.8475, "real_called_fake": 42.37}, "dfd": {"auc": 0.9152, "real_called_fake": 16.22}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
