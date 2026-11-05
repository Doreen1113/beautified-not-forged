# RU clipe5y_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 85.48, 'fake': 0.63, 'filter': 13.89} | pooled {'n': 26519, 'to_real': 38.92, 'to_fake': 0.41, 'to_filter': 60.67, 'balanced_acc': 73.39, 'paired_rank': 93.94}
Eq.4 {'TP': {'eye': 0.208, 'jaw': 0.285, 'white': 0.339, 'smooth': 0.916}, 'TN_same_image': {'eye': 0.815, 'jaw': 0.93, 'white': 0.812, 'smooth': 0.491}, 'AC': {'eye': 0.2, 'jaw': 0.276, 'white': 0.263, 'smooth': 0.416}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.991, 'jaw': 0.976, 'white': 0.955, 'smooth': 0.993}
quantities {"eye": {"n": 6629, "spearman": 0.318, "mae": 0.0244, "pred_mean": 0.0056, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0097, "orig_pred_mean": 0.0013}, "jaw": {"n": 6630, "spearman": 0.109, "mae": 0.0189, "pred_mean": 0.0025, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0089, "orig_pred_mean": -0.0012}, "white": {"n": 6630, "spearman": -0.199, "mae": 0.4957, "pred_mean": 0.0614, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0074, "orig_pred_mean": 0.0025}, "smooth": {"n": 6630, "spearman": 0.139, "mae": 0.1079, "pred_mean": 0.08, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0198, "orig_pred_mean": -0.0036}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 62.44 | 0.5 | 37.06 | 61.58 | 95.09 | 0.069 |
| EyeEnlarging_60 | 2209 | 48.21 | 0.5 | 51.29 | 68.7 | 97.01 | 0.209 |
| EyeEnlarging_90 | 2210 | 37.47 | 0.45 | 62.08 | 74.1 | 98.05 | 0.345 |
| FaceLifting_30 | 2210 | 63.12 | 0.36 | 36.52 | 61.31 | 86.2 | 0.208 |
| FaceLifting_60 | 2210 | 55.66 | 0.36 | 43.98 | 65.05 | 90.54 | 0.279 |
| FaceLifting_90 | 2210 | 47.1 | 0.32 | 52.58 | 69.34 | 94.14 | 0.369 |
| Whitening_30 | 2210 | 57.29 | 0.41 | 42.31 | 64.21 | 86.95 | 0.157 |
| Whitening_60 | 2210 | 43.62 | 0.5 | 55.88 | 71.0 | 89.43 | 0.347 |
| Whitening_90 | 2210 | 32.85 | 0.68 | 66.47 | 76.29 | 93.55 | 0.514 |
| Smoothing_30 | 2210 | 16.88 | 0.27 | 82.85 | 84.48 | 97.42 | 0.776 |
| Smoothing_60 | 2210 | 1.4 | 0.14 | 98.46 | 92.29 | 99.5 | 0.983 |
| Smoothing_90 | 2210 | 1.04 | 0.41 | 98.55 | 92.33 | 99.41 | 0.99 |

## FF++ / cross-dataset
{"indomain": {"real": 80.32, "fake": 91.57, "filter": 84.5}, "FA": 7.14, "real_to_filter": 11.78, "MISS": 0.84, "heldout13": {"filter": 80.09, "fake": 11.4, "paired_excess_pp": 68.31}, "cdf": {"auc": 0.899, "real_called_fake": 18.65}, "dfd": {"auc": 0.9597, "real_called_fake": 4.93}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": true, "D2_heldout_excess>=30": true}}
