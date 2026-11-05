# RU clipe5y_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 88.91, 'fake': 0.18, 'filter': 10.9} | pooled {'n': 26519, 'to_real': 40.07, 'to_fake': 0.15, 'to_filter': 59.79, 'balanced_acc': 74.44, 'paired_rank': 95.36}
Eq.4 {'TP': {'eye': 0.296, 'jaw': 0.295, 'white': 0.24, 'smooth': 0.905}, 'TN_same_image': {'eye': 0.83, 'jaw': 0.941, 'white': 0.767, 'smooth': 0.463}, 'AC': {'eye': 0.286, 'jaw': 0.286, 'white': 0.167, 'smooth': 0.381}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.98, 'jaw': 0.97, 'white': 0.981, 'smooth': 0.994}
quantities {"eye": {"n": 6629, "spearman": 0.233, "mae": 0.0287, "pred_mean": 0.0008, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.011, "orig_pred_mean": -0.0035}, "jaw": {"n": 6630, "spearman": 0.129, "mae": 0.0209, "pred_mean": 0.002, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0097, "orig_pred_mean": -0.0043}, "white": {"n": 6630, "spearman": -0.093, "mae": 0.4971, "pred_mean": 0.0405, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0102, "orig_pred_mean": 0.0029}, "smooth": {"n": 6630, "spearman": 0.13, "mae": 0.0999, "pred_mean": 0.1006, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0243, "orig_pred_mean": -0.0013}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 61.13 | 0.14 | 38.73 | 63.92 | 97.01 | 0.13 |
| EyeEnlarging_60 | 2209 | 43.87 | 0.09 | 56.04 | 72.57 | 98.66 | 0.314 |
| EyeEnlarging_90 | 2210 | 33.67 | 0.14 | 66.2 | 77.65 | 98.96 | 0.444 |
| FaceLifting_30 | 2210 | 65.75 | 0.09 | 34.16 | 61.63 | 90.09 | 0.222 |
| FaceLifting_60 | 2210 | 58.1 | 0.18 | 41.72 | 65.41 | 94.14 | 0.29 |
| FaceLifting_90 | 2210 | 49.37 | 0.14 | 50.5 | 69.8 | 96.38 | 0.374 |
| Whitening_30 | 2210 | 63.76 | 0.09 | 36.15 | 62.63 | 88.08 | 0.073 |
| Whitening_60 | 2210 | 49.86 | 0.14 | 50.0 | 69.55 | 89.55 | 0.224 |
| Whitening_90 | 2210 | 37.87 | 0.27 | 61.86 | 75.48 | 93.28 | 0.423 |
| Smoothing_30 | 2210 | 16.74 | 0.27 | 82.99 | 86.04 | 98.55 | 0.735 |
| Smoothing_60 | 2210 | 0.5 | 0.05 | 99.46 | 94.28 | 99.77 | 0.986 |
| Smoothing_90 | 2210 | 0.18 | 0.18 | 99.64 | 94.37 | 99.86 | 0.995 |

## FF++ / cross-dataset
{"indomain": {"real": 84.5, "fake": 89.72, "filter": 79.64}, "FA": 10.79, "real_to_filter": 8.97, "MISS": 0.97, "heldout13": {"filter": 70.67, "fake": 17.17, "paired_excess_pp": 61.7}, "cdf": {"auc": 0.9007, "real_called_fake": 17.55}, "dfd": {"auc": 0.9591, "real_called_fake": 2.97}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
