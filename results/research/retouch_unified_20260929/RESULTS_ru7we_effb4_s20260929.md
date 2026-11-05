# RU ru7we_effb4_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 82.71, 'fake': 0.54, 'filter': 16.74} | pooled {'n': 26519, 'to_real': 37.95, 'to_fake': 0.51, 'to_filter': 61.55, 'balanced_acc': 72.4, 'paired_rank': 93.64}
Eq.4 {'TP': {'eye': 0.214, 'jaw': 0.26, 'white': 0.289, 'smooth': 0.958}, 'TN_same_image': {'eye': 0.814, 'jaw': 0.916, 'white': 0.798, 'smooth': 0.352}, 'AC': {'eye': 0.195, 'jaw': 0.237, 'white': 0.199, 'smooth': 0.32}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.989, 'jaw': 0.973, 'white': 0.956, 'smooth': 0.984}
quantities {"eye": {"n": 6629, "spearman": 0.475, "mae": 0.0259, "pred_mean": 0.0025, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0059, "orig_pred_mean": -0.0011}, "jaw": {"n": 6630, "spearman": 0.135, "mae": 0.017, "pred_mean": 0.0039, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0055, "orig_pred_mean": 0.0008}, "white": {"n": 6630, "spearman": -0.175, "mae": 0.5036, "pred_mean": 0.0421, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0035, "orig_pred_mean": 0.006}, "smooth": {"n": 6630, "spearman": 0.492, "mae": 0.0918, "pred_mean": 0.0946, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0209, "orig_pred_mean": -0.0}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 58.82 | 0.32 | 40.86 | 62.06 | 97.04 | 0.08 |
| EyeEnlarging_60 | 2209 | 44.59 | 0.27 | 55.14 | 69.2 | 98.55 | 0.215 |
| EyeEnlarging_90 | 2210 | 35.02 | 0.27 | 64.71 | 73.98 | 98.91 | 0.347 |
| FaceLifting_30 | 2210 | 63.39 | 0.36 | 36.24 | 59.75 | 82.96 | 0.196 |
| FaceLifting_60 | 2210 | 57.38 | 0.32 | 42.31 | 62.78 | 88.42 | 0.26 |
| FaceLifting_90 | 2210 | 50.32 | 0.45 | 49.23 | 66.25 | 92.26 | 0.324 |
| Whitening_30 | 2210 | 58.64 | 0.45 | 40.9 | 62.08 | 87.01 | 0.129 |
| Whitening_60 | 2210 | 45.57 | 0.63 | 53.8 | 68.53 | 89.39 | 0.289 |
| Whitening_90 | 2210 | 35.57 | 0.77 | 63.67 | 73.46 | 91.95 | 0.45 |
| Smoothing_30 | 2210 | 5.48 | 0.63 | 93.89 | 88.58 | 98.51 | 0.886 |
| Smoothing_60 | 2210 | 0.41 | 0.63 | 98.96 | 91.11 | 99.64 | 0.991 |
| Smoothing_90 | 2210 | 0.18 | 0.95 | 98.87 | 91.06 | 99.0 | 0.996 |

## FF++ / cross-dataset
{"indomain": {"real": 81.69, "fake": 91.63, "filter": 81.16}, "FA": 7.07, "real_to_filter": 11.09, "MISS": 0.91, "heldout13": {"filter": 57.52, "fake": 12.31, "paired_excess_pp": 46.43}, "cdf": {"auc": 0.8485, "real_called_fake": 16.24}, "dfd": {"auc": 0.9166, "real_called_fake": 3.97}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": true, "D2_heldout_excess>=30": true}}
