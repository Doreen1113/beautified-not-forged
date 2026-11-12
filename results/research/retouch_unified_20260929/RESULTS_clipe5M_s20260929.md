# RU clipe5M_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 83.8, 'fake': 0.63, 'filter': 15.57} | pooled {'n': 26519, 'to_real': 33.63, 'to_fake': 0.42, 'to_filter': 65.95, 'balanced_acc': 75.19, 'paired_rank': 95.29}
Eq.4 {'TP': {'eye': 0.23, 'jaw': 0.369, 'white': 0.368, 'smooth': 0.944}, 'TN_same_image': {'eye': 0.737, 'jaw': 0.918, 'white': 0.77, 'smooth': 0.441}, 'AC': {'eye': 0.21, 'jaw': 0.35, 'white': 0.282, 'smooth': 0.392}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.992, 'jaw': 0.961, 'white': 0.937, 'smooth': 0.993}
quantities {"eye": {"n": 6629, "spearman": 0.436, "mae": 0.0237, "pred_mean": 0.0062, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0118, "orig_pred_mean": -0.0013}, "jaw": {"n": 6630, "spearman": 0.155, "mae": 0.0131, "pred_mean": 0.0124, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0101, "orig_pred_mean": 0.0053}, "white": {"n": 6630, "spearman": -0.094, "mae": 0.4893, "pred_mean": 0.0599, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0094, "orig_pred_mean": 0.0117}, "smooth": {"n": 6630, "spearman": 0.345, "mae": 0.0892, "pred_mean": 0.1035, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0202, "orig_pred_mean": -0.0003}}
bars {"R1_balanced>=75": true, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 55.57 | 0.5 | 43.94 | 64.18 | 95.66 | 0.074 |
| EyeEnlarging_60 | 2209 | 39.61 | 0.45 | 59.94 | 72.18 | 97.83 | 0.238 |
| EyeEnlarging_90 | 2210 | 29.32 | 0.5 | 70.18 | 77.31 | 98.46 | 0.377 |
| FaceLifting_30 | 2210 | 57.38 | 0.36 | 42.26 | 63.35 | 90.27 | 0.282 |
| FaceLifting_60 | 2210 | 49.19 | 0.32 | 50.5 | 67.46 | 93.87 | 0.367 |
| FaceLifting_90 | 2210 | 40.18 | 0.36 | 59.46 | 71.94 | 95.34 | 0.458 |
| Whitening_30 | 2210 | 53.53 | 0.41 | 46.06 | 65.25 | 89.52 | 0.177 |
| Whitening_60 | 2210 | 39.64 | 0.54 | 59.82 | 72.12 | 90.54 | 0.37 |
| Whitening_90 | 2210 | 29.28 | 0.68 | 70.05 | 77.24 | 93.98 | 0.558 |
| Smoothing_30 | 2210 | 8.64 | 0.18 | 91.18 | 87.8 | 98.69 | 0.852 |
| Smoothing_60 | 2210 | 0.77 | 0.18 | 99.05 | 91.74 | 99.77 | 0.987 |
| Smoothing_90 | 2210 | 0.45 | 0.59 | 98.96 | 91.69 | 99.55 | 0.992 |

## FF++ / cross-dataset
{"indomain": {"real": 81.76, "fake": 90.35, "filter": 87.08}, "FA": 5.09, "real_to_filter": 11.4, "MISS": 0.56, "heldout13": {"filter": 78.72, "fake": 13.37, "paired_excess_pp": 67.32}, "cdf": {"auc": 0.8936, "real_called_fake": 16.77}, "dfd": {"auc": 0.9575, "real_called_fake": 3.07}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": true, "D2_heldout_excess>=30": true}}
