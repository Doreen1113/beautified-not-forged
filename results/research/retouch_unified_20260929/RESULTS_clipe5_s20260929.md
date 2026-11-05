# RU clipe5_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 78.37, 'fake': 0.81, 'filter': 20.81} | pooled {'n': 26519, 'to_real': 31.73, 'to_fake': 0.55, 'to_filter': 67.72, 'balanced_acc': 73.45, 'paired_rank': 92.94}
Eq.4 {'TP': {'eye': 0.196, 'jaw': 0.322, 'white': 0.375, 'smooth': 0.943}, 'TN_same_image': {'eye': 0.766, 'jaw': 0.916, 'white': 0.8, 'smooth': 0.433}, 'AC': {'eye': 0.185, 'jaw': 0.311, 'white': 0.297, 'smooth': 0.384}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.989, 'jaw': 0.967, 'white': 0.926, 'smooth': 0.991}
quantities {"eye": {"n": 6629, "spearman": 0.311, "mae": 0.0224, "pred_mean": 0.0099, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0115, "orig_pred_mean": 0.0026}, "jaw": {"n": 6630, "spearman": 0.088, "mae": 0.0172, "pred_mean": 0.0046, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.011, "orig_pred_mean": 0.0017}, "white": {"n": 6630, "spearman": -0.13, "mae": 0.4889, "pred_mean": 0.0658, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0091, "orig_pred_mean": 0.016}, "smooth": {"n": 6630, "spearman": 0.213, "mae": 0.1048, "pred_mean": 0.0819, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0181, "orig_pred_mean": -0.005}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 52.94 | 0.54 | 46.52 | 62.85 | 92.42 | 0.062 |
| EyeEnlarging_60 | 2209 | 39.7 | 0.54 | 59.76 | 69.47 | 96.33 | 0.194 |
| EyeEnlarging_90 | 2210 | 29.77 | 0.54 | 69.68 | 74.44 | 97.56 | 0.333 |
| FaceLifting_30 | 2210 | 53.53 | 0.41 | 46.06 | 62.63 | 84.12 | 0.242 |
| FaceLifting_60 | 2210 | 45.97 | 0.36 | 53.67 | 66.43 | 89.77 | 0.319 |
| FaceLifting_90 | 2210 | 38.33 | 0.41 | 61.27 | 70.23 | 93.73 | 0.405 |
| Whitening_30 | 2210 | 47.87 | 0.59 | 51.54 | 65.36 | 85.38 | 0.184 |
| Whitening_60 | 2210 | 35.79 | 0.63 | 63.57 | 71.38 | 87.6 | 0.386 |
| Whitening_90 | 2210 | 26.88 | 0.81 | 72.31 | 75.75 | 92.17 | 0.555 |
| Smoothing_30 | 2210 | 8.87 | 0.63 | 90.5 | 84.84 | 97.6 | 0.843 |
| Smoothing_60 | 2210 | 0.68 | 0.36 | 98.96 | 89.07 | 99.41 | 0.991 |
| Smoothing_90 | 2210 | 0.45 | 0.77 | 98.78 | 88.98 | 99.19 | 0.994 |

## FF++ / cross-dataset
{"indomain": {"real": 82.67, "fake": 90.86, "filter": 86.7}, "FA": 4.33, "real_to_filter": 11.4, "MISS": 0.91, "heldout13": {"filter": 80.78, "fake": 10.03, "paired_excess_pp": 69.38}, "cdf": {"auc": 0.891, "real_called_fake": 18.94}, "dfd": {"auc": 0.9558, "real_called_fake": 4.82}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": true, "D2_heldout_excess>=30": true}}
