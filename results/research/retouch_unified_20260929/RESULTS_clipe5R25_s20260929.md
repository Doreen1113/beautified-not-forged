# RU clipe5R25_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 85.93, 'fake': 1.0, 'filter': 13.08} | pooled {'n': 26519, 'to_real': 38.47, 'to_fake': 0.89, 'to_filter': 60.64, 'balanced_acc': 73.78, 'paired_rank': 91.65}
Eq.4 {'TP': {'eye': 0.222, 'jaw': 0.283, 'white': 0.286, 'smooth': 0.955}, 'TN_same_image': {'eye': 0.825, 'jaw': 0.944, 'white': 0.799, 'smooth': 0.484}, 'AC': {'eye': 0.216, 'jaw': 0.276, 'white': 0.213, 'smooth': 0.444}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.987, 'jaw': 0.979, 'white': 0.967, 'smooth': 0.989}
quantities {"eye": {"n": 6629, "spearman": 0.304, "mae": 0.0228, "pred_mean": 0.0085, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0087, "orig_pred_mean": 0.0045}, "jaw": {"n": 6630, "spearman": 0.146, "mae": 0.0184, "pred_mean": 0.0034, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0083, "orig_pred_mean": -0.0018}, "white": {"n": 6630, "spearman": -0.108, "mae": 0.494, "pred_mean": 0.0492, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.008, "orig_pred_mean": 0.0071}, "smooth": {"n": 6630, "spearman": 0.309, "mae": 0.1009, "pred_mean": 0.086, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0206, "orig_pred_mean": -0.0004}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 61.81 | 1.04 | 37.15 | 62.03 | 90.68 | 0.08 |
| EyeEnlarging_60 | 2209 | 46.94 | 1.0 | 52.06 | 69.49 | 94.88 | 0.23 |
| EyeEnlarging_90 | 2210 | 36.52 | 1.04 | 62.44 | 74.68 | 96.24 | 0.357 |
| FaceLifting_30 | 2210 | 64.62 | 0.77 | 34.62 | 60.77 | 79.93 | 0.206 |
| FaceLifting_60 | 2210 | 55.93 | 0.81 | 43.26 | 65.09 | 86.79 | 0.281 |
| FaceLifting_90 | 2210 | 47.38 | 0.72 | 51.9 | 69.41 | 90.68 | 0.362 |
| Whitening_30 | 2210 | 59.05 | 1.36 | 39.59 | 63.26 | 83.48 | 0.099 |
| Whitening_60 | 2210 | 45.38 | 1.4 | 53.21 | 70.07 | 87.83 | 0.274 |
| Whitening_90 | 2210 | 32.85 | 1.67 | 65.48 | 76.2 | 91.99 | 0.485 |
| Smoothing_30 | 2210 | 10.5 | 0.41 | 89.1 | 88.01 | 97.78 | 0.872 |
| Smoothing_60 | 2210 | 0.5 | 0.14 | 99.37 | 93.14 | 99.86 | 0.995 |
| Smoothing_90 | 2210 | 0.18 | 0.32 | 99.5 | 93.21 | 99.64 | 0.997 |

## FF++ / cross-dataset
{"indomain": {"real": 83.43, "fake": 86.07, "filter": 85.79}, "FA": 5.32, "real_to_filter": 9.19, "MISS": 1.38, "heldout13": {"filter": 79.79, "fake": 10.11, "paired_excess_pp": 70.6}, "cdf": {"auc": 0.8777, "real_called_fake": 20.83}, "dfd": {"auc": 0.9534, "real_called_fake": 7.0}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": true, "D2_heldout_excess>=30": true}}
