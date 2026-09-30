# RU clipe_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 77.42, 'fake': 0.36, 'filter': 22.22} | pooled {'n': 26519, 'to_real': 28.42, 'to_fake': 0.18, 'to_filter': 71.41, 'balanced_acc': 74.59, 'paired_rank': 93.82}
Eq.4 {'TP': {'eye': 0.274, 'jaw': 0.375, 'white': 0.408, 'smooth': 0.958}, 'TN_same_image': {'eye': 0.73, 'jaw': 0.892, 'white': 0.772, 'smooth': 0.424}, 'AC': {'eye': 0.258, 'jaw': 0.356, 'white': 0.321, 'smooth': 0.391}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.979, 'jaw': 0.955, 'white': 0.93, 'smooth': 0.99}
quantities {"eye": {"n": 6629, "spearman": 0.379, "mae": 0.0235, "pred_mean": 0.0073, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0125, "orig_pred_mean": 0.0005}, "jaw": {"n": 6630, "spearman": 0.137, "mae": 0.0151, "pred_mean": 0.0081, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0104, "orig_pred_mean": 0.0022}, "white": {"n": 6630, "spearman": -0.164, "mae": 0.4843, "pred_mean": 0.0821, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0088, "orig_pred_mean": 0.0134}, "smooth": {"n": 6630, "spearman": 0.284, "mae": 0.0939, "pred_mean": 0.097, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0197, "orig_pred_mean": -0.001}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 45.88 | 0.23 | 53.89 | 65.84 | 95.93 | 0.12 |
| EyeEnlarging_60 | 2209 | 30.74 | 0.23 | 69.04 | 73.41 | 97.78 | 0.292 |
| EyeEnlarging_90 | 2210 | 23.8 | 0.18 | 76.02 | 76.9 | 98.39 | 0.411 |
| FaceLifting_30 | 2210 | 50.54 | 0.23 | 49.23 | 63.51 | 87.49 | 0.289 |
| FaceLifting_60 | 2210 | 42.76 | 0.23 | 57.01 | 67.4 | 92.13 | 0.376 |
| FaceLifting_90 | 2210 | 34.07 | 0.23 | 65.7 | 71.74 | 94.48 | 0.458 |
| Whitening_30 | 2210 | 45.57 | 0.27 | 54.16 | 65.97 | 85.43 | 0.208 |
| Whitening_60 | 2210 | 34.25 | 0.14 | 65.61 | 71.7 | 86.29 | 0.418 |
| Whitening_90 | 2210 | 27.29 | 0.14 | 72.58 | 75.18 | 90.5 | 0.599 |
| Smoothing_30 | 2210 | 5.79 | 0.09 | 94.12 | 85.95 | 98.01 | 0.881 |
| Smoothing_60 | 2210 | 0.18 | 0.0 | 99.82 | 88.8 | 99.77 | 0.994 |
| Smoothing_90 | 2210 | 0.14 | 0.18 | 99.68 | 88.73 | 99.59 | 0.998 |

## FF++ / cross-dataset
{"indomain": {"real": 76.67, "fake": 94.63, "filter": 87.92}, "FA": 5.55, "real_to_filter": 16.49, "MISS": 0.16, "heldout13": {"filter": 58.28, "fake": 18.01, "paired_excess_pp": 41.79}, "cdf": {"auc": 0.8781, "real_called_fake": 16.98}, "dfd": {"auc": 0.9569, "real_called_fake": 2.6}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
