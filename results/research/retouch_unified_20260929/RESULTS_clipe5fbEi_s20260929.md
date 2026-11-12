# RU clipe5fbEi_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 59.23, 'fake': 2.35, 'filter': 38.42} | pooled {'n': 26519, 'to_real': 57.56, 'to_fake': 8.81, 'to_filter': 33.62, 'balanced_acc': 47.6, 'paired_rank': 33.25}
Eq.4 {'TP': {'eye': 0.952, 'jaw': 0.044, 'white': 0.398, 'smooth': 0.066}, 'TN_same_image': {'eye': 0.585, 'jaw': 0.022, 'white': 0.041, 'smooth': 0.011}, 'AC': {'eye': 0.564, 'jaw': 0.002, 'white': 0.023, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.047, 'jaw': 0.958, 'white': 0.593, 'smooth': 0.962}
quantities {"eye": {"n": 6629, "spearman": 0.094, "mae": 0.4901, "pred_mean": 0.4448, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4789, "orig_pred_mean": 0.4375}, "jaw": {"n": 6630, "spearman": -0.023, "mae": 0.7126, "pred_mean": -0.6644, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4151, "orig_pred_mean": -0.6687}, "white": {"n": 6630, "spearman": -0.05, "mae": 0.5827, "pred_mean": 0.1498, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.5412, "orig_pred_mean": 0.1897}, "smooth": {"n": 6630, "spearman": 0.004, "mae": 0.4535, "pred_mean": -0.0531, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.5401, "orig_pred_mean": -0.1598}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 60.36 | 2.17 | 37.47 | 49.52 | 43.71 | 0.951 |
| EyeEnlarging_60 | 2209 | 58.62 | 2.94 | 38.43 | 50.01 | 47.89 | 0.951 |
| EyeEnlarging_90 | 2210 | 54.25 | 6.92 | 38.82 | 50.2 | 47.15 | 0.954 |
| FaceLifting_30 | 2210 | 61.86 | 2.13 | 36.02 | 48.8 | 34.43 | 0.042 |
| FaceLifting_60 | 2210 | 61.86 | 2.35 | 35.79 | 48.69 | 34.55 | 0.044 |
| FaceLifting_90 | 2210 | 61.45 | 3.08 | 35.48 | 48.53 | 34.84 | 0.046 |
| Whitening_30 | 2210 | 61.72 | 2.31 | 35.97 | 48.78 | 38.64 | 0.387 |
| Whitening_60 | 2210 | 61.49 | 2.53 | 35.97 | 48.78 | 40.27 | 0.398 |
| Whitening_90 | 2210 | 59.86 | 3.62 | 36.52 | 49.05 | 43.1 | 0.407 |
| Smoothing_30 | 2210 | 59.14 | 9.1 | 31.76 | 46.67 | 17.19 | 0.042 |
| Smoothing_60 | 2210 | 49.91 | 26.74 | 23.35 | 42.46 | 10.0 | 0.067 |
| Smoothing_90 | 2210 | 40.23 | 41.86 | 17.92 | 39.75 | 7.24 | 0.089 |

## FF++ / cross-dataset
{"indomain": {"real": 16.41, "fake": 66.89, "filter": 71.81}, "FA": 12.77, "real_to_filter": 79.79, "MISS": 3.06, "heldout13": {"filter": 69.76, "fake": 12.77, "paired_excess_pp": -10.03}, "cdf": {"auc": 0.8613, "real_called_fake": 8.4}, "dfd": {"auc": 0.9355, "real_called_fake": 4.56}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
