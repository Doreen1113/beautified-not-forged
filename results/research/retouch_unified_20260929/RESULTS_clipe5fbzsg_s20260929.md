# RU clipe5fbzsg_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 31.99, 'fake': 9.59, 'filter': 58.42} | pooled {'n': 26519, 'to_real': 33.26, 'to_fake': 9.76, 'to_filter': 56.98, 'balanced_acc': 49.28, 'paired_rank': 44.92}
Eq.4 {'TP': {'eye': 0.03, 'jaw': 0.898, 'white': 0.206, 'smooth': 0.027}, 'TN_same_image': {'eye': 0.085, 'jaw': 0.762, 'white': 0.11, 'smooth': 0.054}, 'AC': {'eye': 0.002, 'jaw': 0.682, 'white': 0.021, 'smooth': 0.002}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.968, 'jaw': 0.114, 'white': 0.817, 'smooth': 0.958}
quantities {"eye": {"n": 6629, "spearman": -0.016, "mae": 0.4921, "pred_mean": 0.4067, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3175, "orig_pred_mean": 0.4169}, "jaw": {"n": 6630, "spearman": 0.026, "mae": 0.3035, "pred_mean": -0.0689, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.3839, "orig_pred_mean": -0.074}, "white": {"n": 6630, "spearman": -0.059, "mae": 0.5442, "pred_mean": 0.2204, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.3745, "orig_pred_mean": 0.246}, "smooth": {"n": 6630, "spearman": -0.086, "mae": 0.3912, "pred_mean": -0.1004, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3886, "orig_pred_mean": -0.0405}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 33.89 | 8.64 | 57.47 | 49.52 | 49.25 | 0.03 |
| EyeEnlarging_60 | 2209 | 34.09 | 9.01 | 56.9 | 49.24 | 48.64 | 0.029 |
| EyeEnlarging_90 | 2210 | 33.48 | 9.82 | 56.7 | 49.14 | 47.87 | 0.029 |
| FaceLifting_30 | 2210 | 34.39 | 8.55 | 57.06 | 49.32 | 46.43 | 0.897 |
| FaceLifting_60 | 2210 | 34.93 | 9.0 | 56.06 | 48.82 | 44.66 | 0.898 |
| FaceLifting_90 | 2210 | 35.34 | 8.69 | 55.97 | 48.78 | 43.39 | 0.9 |
| Whitening_30 | 2210 | 34.16 | 8.28 | 57.56 | 49.57 | 46.22 | 0.19 |
| Whitening_60 | 2210 | 36.15 | 8.91 | 54.93 | 48.26 | 42.26 | 0.204 |
| Whitening_90 | 2210 | 36.7 | 9.41 | 53.89 | 47.74 | 39.68 | 0.223 |
| Smoothing_30 | 2210 | 30.5 | 10.36 | 59.14 | 50.36 | 47.56 | 0.029 |
| Smoothing_60 | 2210 | 28.28 | 12.44 | 59.28 | 50.43 | 42.76 | 0.028 |
| Smoothing_90 | 2210 | 27.19 | 14.03 | 58.78 | 50.18 | 40.27 | 0.024 |

## FF++ / cross-dataset
{"indomain": {"real": 38.15, "fake": 86.39, "filter": 53.65}, "FA": 13.07, "real_to_filter": 56.61, "MISS": 1.31, "heldout13": {"filter": 50.38, "fake": 19.98, "paired_excess_pp": -6.23}, "cdf": {"auc": 0.7942, "real_called_fake": 9.68}, "dfd": {"auc": 0.9356, "real_called_fake": 3.71}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
