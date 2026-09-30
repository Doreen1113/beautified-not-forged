# RU ru2_effb4_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 66.56, 'fake': 0.27, 'filter': 33.17} | pooled {'n': 26519, 'to_real': 24.89, 'to_fake': 0.25, 'to_filter': 74.86, 'balanced_acc': 70.85, 'paired_rank': 94.25}
Eq.4 {'TP': {'eye': 0.234, 'jaw': 0.325, 'white': 0.329, 'smooth': 0.975}, 'TN_same_image': {'eye': 0.722, 'jaw': 0.829, 'white': 0.667, 'smooth': 0.258}, 'AC': {'eye': 0.164, 'jaw': 0.233, 'white': 0.13, 'smooth': 0.242}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.983, 'jaw': 0.951, 'white': 0.932, 'smooth': 0.964}
quantities {"eye": {"n": 6629, "spearman": 0.37, "mae": 0.0248, "pred_mean": 0.0048, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0103, "orig_pred_mean": 0.003}, "jaw": {"n": 6630, "spearman": 0.132, "mae": 0.0183, "pred_mean": 0.0023, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0092, "orig_pred_mean": 0.0003}, "white": {"n": 6630, "spearman": -0.231, "mae": 0.5036, "pred_mean": 0.0339, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0057, "orig_pred_mean": 0.009}, "smooth": {"n": 6630, "spearman": 0.409, "mae": 0.0858, "pred_mean": 0.11, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0292, "orig_pred_mean": 0.0008}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 38.6 | 0.23 | 61.18 | 64.0 | 96.83 | 0.109 |
| EyeEnlarging_60 | 2209 | 27.66 | 0.18 | 72.16 | 69.49 | 98.55 | 0.231 |
| EyeEnlarging_90 | 2210 | 20.23 | 0.14 | 79.64 | 73.23 | 98.91 | 0.361 |
| FaceLifting_30 | 2210 | 43.8 | 0.23 | 55.97 | 61.4 | 85.88 | 0.258 |
| FaceLifting_60 | 2210 | 38.19 | 0.23 | 61.58 | 64.21 | 89.73 | 0.322 |
| FaceLifting_90 | 2210 | 32.94 | 0.27 | 66.79 | 66.81 | 92.58 | 0.394 |
| Whitening_30 | 2210 | 40.32 | 0.27 | 59.41 | 63.12 | 87.96 | 0.198 |
| Whitening_60 | 2210 | 31.18 | 0.41 | 68.42 | 67.62 | 89.73 | 0.33 |
| Whitening_90 | 2210 | 24.21 | 0.41 | 75.38 | 71.11 | 91.9 | 0.459 |
| Smoothing_30 | 2210 | 1.22 | 0.14 | 98.64 | 82.74 | 99.82 | 0.934 |
| Smoothing_60 | 2210 | 0.23 | 0.09 | 99.68 | 83.26 | 99.73 | 0.994 |
| Smoothing_90 | 2210 | 0.09 | 0.41 | 99.5 | 83.17 | 99.32 | 0.997 |

## FF++ / cross-dataset
{"indomain": {"real": 80.4, "fake": 92.89, "filter": 76.06}, "FA": 9.95, "real_to_filter": 13.91, "MISS": 0.5, "heldout13": {"filter": 48.02, "fake": 15.88, "paired_excess_pp": 34.11}, "cdf": {"auc": 0.817, "real_called_fake": 25.02}, "dfd": {"auc": 0.9342, "real_called_fake": 7.79}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
