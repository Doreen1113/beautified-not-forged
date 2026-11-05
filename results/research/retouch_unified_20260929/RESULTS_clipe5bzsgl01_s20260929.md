# RU clipe5bzsgl01_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 31.0, 'fake': 0.41, 'filter': 68.6} | pooled {'n': 26519, 'to_real': 43.99, 'to_fake': 0.52, 'to_filter': 55.49, 'balanced_acc': 43.44, 'paired_rank': 37.09}
Eq.4 {'TP': {'eye': 0.008, 'jaw': 0.975, 'white': 0.115, 'smooth': 0.503}, 'TN_same_image': {'eye': 0.027, 'jaw': 0.907, 'white': 0.037, 'smooth': 0.046}, 'AC': {'eye': 0.001, 'jaw': 0.884, 'white': 0.004, 'smooth': 0.031}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.993, 'jaw': 0.027, 'white': 0.946, 'smooth': 1.0}
quantities {"eye": {"n": 6629, "spearman": -0.005, "mae": 1.0577, "pred_mean": 1.0696, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3593, "orig_pred_mean": 1.0991}, "jaw": {"n": 6630, "spearman": 0.079, "mae": 0.4606, "pred_mean": -0.3913, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.585, "orig_pred_mean": -0.4675}, "white": {"n": 6630, "spearman": -0.151, "mae": 0.503, "pred_mean": 0.4037, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.5131, "orig_pred_mean": 0.4058}, "smooth": {"n": 6630, "spearman": 0.119, "mae": 0.2184, "pred_mean": 0.1185, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.4955, "orig_pred_mean": 0.1457}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 37.01 | 0.27 | 62.71 | 47.06 | 44.21 | 0.007 |
| EyeEnlarging_60 | 2209 | 37.08 | 0.32 | 62.61 | 47.0 | 43.3 | 0.007 |
| EyeEnlarging_90 | 2210 | 37.74 | 0.45 | 61.81 | 46.6 | 42.47 | 0.009 |
| FaceLifting_30 | 2210 | 40.36 | 0.18 | 59.46 | 45.43 | 39.16 | 0.974 |
| FaceLifting_60 | 2210 | 44.43 | 0.18 | 55.38 | 43.39 | 37.08 | 0.976 |
| FaceLifting_90 | 2210 | 48.42 | 0.14 | 51.45 | 41.42 | 33.69 | 0.976 |
| Whitening_30 | 2210 | 43.48 | 0.36 | 56.15 | 43.78 | 32.81 | 0.101 |
| Whitening_60 | 2210 | 46.97 | 0.54 | 52.49 | 41.94 | 31.13 | 0.118 |
| Whitening_90 | 2210 | 48.51 | 0.68 | 50.81 | 41.11 | 30.23 | 0.127 |
| Smoothing_30 | 2210 | 40.81 | 0.9 | 58.28 | 44.84 | 42.81 | 0.235 |
| Smoothing_60 | 2210 | 51.04 | 0.9 | 48.05 | 39.73 | 34.39 | 0.615 |
| Smoothing_90 | 2210 | 52.08 | 1.27 | 46.65 | 39.03 | 33.85 | 0.659 |

## FF++ / cross-dataset
{"indomain": {"real": 4.41, "fake": 93.93, "filter": 78.88}, "FA": 12.23, "real_to_filter": 85.79, "MISS": 0.28, "heldout13": {"filter": 71.96, "fake": 18.54, "paired_excess_pp": -13.83}, "cdf": {"auc": 0.872, "real_called_fake": 21.5}, "dfd": {"auc": 0.9626, "real_called_fake": 6.2}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
