# RU clipe4r_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 83.35, 'fake': 0.41, 'filter': 16.24} | pooled {'n': 26519, 'to_real': 32.26, 'to_fake': 0.23, 'to_filter': 67.51, 'balanced_acc': 75.63, 'paired_rank': 92.97}
Eq.4 {'TP': {'eye': 0.28, 'jaw': 0.394, 'white': 0.262, 'smooth': 0.958}, 'TN_same_image': {'eye': 0.76, 'jaw': 0.927, 'white': 0.707, 'smooth': 0.493}, 'AC': {'eye': 0.261, 'jaw': 0.371, 'white': 0.166, 'smooth': 0.457}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.983, 'jaw': 0.953, 'white': 0.98, 'smooth': 0.98}
quantities {"eye": {"n": 6629, "spearman": 0.356, "mae": 0.023, "pred_mean": 0.0079, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0095, "orig_pred_mean": 0.0002}, "jaw": {"n": 6630, "spearman": 0.122, "mae": 0.0174, "pred_mean": 0.0045, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0083, "orig_pred_mean": 0.0007}, "white": {"n": 6630, "spearman": -0.098, "mae": 0.4965, "pred_mean": 0.0414, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.009, "orig_pred_mean": 0.0056}, "smooth": {"n": 6630, "spearman": 0.184, "mae": 0.0965, "pred_mean": 0.1054, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0187, "orig_pred_mean": 0.0011}}
bars {"R1_balanced>=75": true, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 49.86 | 0.32 | 49.82 | 66.79 | 95.88 | 0.125 |
| EyeEnlarging_60 | 2209 | 35.85 | 0.32 | 63.83 | 73.79 | 97.69 | 0.294 |
| EyeEnlarging_90 | 2210 | 26.43 | 0.27 | 73.3 | 78.53 | 98.33 | 0.42 |
| FaceLifting_30 | 2210 | 54.66 | 0.36 | 44.98 | 64.37 | 88.01 | 0.306 |
| FaceLifting_60 | 2210 | 46.47 | 0.27 | 53.26 | 68.51 | 91.81 | 0.393 |
| FaceLifting_90 | 2210 | 38.05 | 0.27 | 61.67 | 72.72 | 95.25 | 0.483 |
| Whitening_30 | 2210 | 54.12 | 0.18 | 45.7 | 64.73 | 80.23 | 0.089 |
| Whitening_60 | 2210 | 42.58 | 0.18 | 57.24 | 70.5 | 82.13 | 0.239 |
| Whitening_90 | 2210 | 32.04 | 0.18 | 67.78 | 75.77 | 88.01 | 0.457 |
| Smoothing_30 | 2210 | 6.61 | 0.14 | 93.26 | 88.51 | 99.1 | 0.891 |
| Smoothing_60 | 2210 | 0.36 | 0.09 | 99.55 | 91.65 | 99.73 | 0.99 |
| Smoothing_90 | 2210 | 0.14 | 0.18 | 99.68 | 91.72 | 99.55 | 0.994 |

## FF++ / cross-dataset
{"indomain": {"real": 78.5, "fake": 91.52, "filter": 88.37}, "FA": 5.7, "real_to_filter": 11.47, "MISS": 0.34, "heldout13": {"filter": 58.74, "fake": 18.31, "paired_excess_pp": 47.27}, "cdf": {"auc": 0.8849, "real_called_fake": 22.28}, "dfd": {"auc": 0.9592, "real_called_fake": 4.5}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
