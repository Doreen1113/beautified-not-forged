# RU clipe5fbp0_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 4.39, 'fake': 19.37, 'filter': 76.24} | pooled {'n': 26519, 'to_real': 3.84, 'to_fake': 31.93, 'to_filter': 64.23, 'balanced_acc': 43.99, 'paired_rank': 42.87}
Eq.4 {'TP': {'eye': 0.038, 'jaw': 0.929, 'white': 0.254, 'smooth': 0.034}, 'TN_same_image': {'eye': 0.054, 'jaw': 0.7, 'white': 0.077, 'smooth': 0.036}, 'AC': {'eye': 0.001, 'jaw': 0.652, 'white': 0.018, 'smooth': 0.003}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.96, 'jaw': 0.074, 'white': 0.735, 'smooth': 0.989}
quantities {"eye": {"n": 6629, "spearman": -0.07, "mae": 0.4531, "pred_mean": -0.0285, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3876, "orig_pred_mean": -0.0249}, "jaw": {"n": 6630, "spearman": 0.004, "mae": 0.3402, "pred_mean": -0.1323, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4271, "orig_pred_mean": -0.1242}, "white": {"n": 6630, "spearman": 0.005, "mae": 0.5657, "pred_mean": 0.238, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.413, "orig_pred_mean": 0.2346}, "smooth": {"n": 6630, "spearman": 0.155, "mae": 0.4386, "pred_mean": 0.5137, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.5085, "orig_pred_mean": 0.2917}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 4.39 | 18.6 | 77.01 | 50.39 | 61.13 | 0.04 |
| EyeEnlarging_60 | 2209 | 4.07 | 18.83 | 77.09 | 50.43 | 60.82 | 0.038 |
| EyeEnlarging_90 | 2210 | 3.85 | 19.68 | 76.47 | 50.12 | 58.85 | 0.037 |
| FaceLifting_30 | 2210 | 4.25 | 19.0 | 76.74 | 50.25 | 59.07 | 0.928 |
| FaceLifting_60 | 2210 | 4.07 | 19.32 | 76.61 | 50.18 | 58.03 | 0.93 |
| FaceLifting_90 | 2210 | 4.21 | 19.68 | 76.11 | 49.93 | 57.62 | 0.928 |
| Whitening_30 | 2210 | 4.48 | 20.23 | 75.29 | 49.53 | 49.89 | 0.266 |
| Whitening_60 | 2210 | 4.98 | 22.85 | 72.17 | 47.97 | 42.85 | 0.26 |
| Whitening_90 | 2210 | 5.02 | 24.98 | 70.0 | 46.88 | 39.03 | 0.237 |
| Smoothing_30 | 2210 | 3.44 | 44.43 | 52.13 | 37.94 | 16.61 | 0.022 |
| Smoothing_60 | 2210 | 1.99 | 72.4 | 25.61 | 24.69 | 6.97 | 0.035 |
| Smoothing_90 | 2210 | 1.36 | 83.12 | 15.52 | 19.64 | 3.57 | 0.046 |

## FF++ / cross-dataset
{"indomain": {"real": 3.5, "fake": 94.78, "filter": 74.32}, "FA": 21.58, "real_to_filter": 88.37, "MISS": 0.03, "heldout13": {"filter": 69.76, "fake": 26.06, "paired_excess_pp": -18.61}, "cdf": {"auc": 0.8889, "real_called_fake": 23.86}, "dfd": {"auc": 0.9575, "real_called_fake": 6.78}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
