# RU clipe5fg0_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 35.07, 'fake': 31.0, 'filter': 33.94} | pooled {'n': 26519, 'to_real': 24.23, 'to_fake': 28.57, 'to_filter': 47.2, 'balanced_acc': 56.63, 'paired_rank': 70.04}
Eq.4 {'TP': {'eye': 0.194, 'jaw': 0.176, 'white': 0.036, 'smooth': 0.767}, 'TN_same_image': {'eye': 0.8, 'jaw': 0.908, 'white': 0.815, 'smooth': 0.952}, 'AC': {'eye': 0.189, 'jaw': 0.176, 'white': 0.036, 'smooth': 0.766}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.981, 'jaw': 0.853, 'white': 0.953, 'smooth': 0.971}
quantities {"eye": {"n": 6629, "spearman": 0.158, "mae": 0.0482, "pred_mean": -0.0156, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0361, "orig_pred_mean": -0.0324}, "jaw": {"n": 6630, "spearman": -0.022, "mae": 0.0304, "pred_mean": 0.0059, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0388, "orig_pred_mean": 0.0035}, "white": {"n": 6630, "spearman": -0.007, "mae": 0.5038, "pred_mean": 0.0403, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0366, "orig_pred_mean": 0.0475}, "smooth": {"n": 6630, "spearman": 0.446, "mae": 0.0993, "pred_mean": 0.1311, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0467, "orig_pred_mean": 0.011}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 32.31 | 24.12 | 43.57 | 54.82 | 78.73 | 0.077 |
| EyeEnlarging_60 | 2209 | 25.8 | 23.77 | 50.43 | 58.25 | 83.43 | 0.192 |
| EyeEnlarging_90 | 2210 | 20.95 | 24.03 | 55.02 | 60.54 | 85.48 | 0.312 |
| FaceLifting_30 | 2210 | 38.42 | 24.93 | 36.65 | 51.36 | 61.33 | 0.164 |
| FaceLifting_60 | 2210 | 36.24 | 25.38 | 38.37 | 52.22 | 63.26 | 0.177 |
| FaceLifting_90 | 2210 | 34.52 | 26.47 | 39.0 | 52.53 | 63.71 | 0.187 |
| Whitening_30 | 2210 | 33.89 | 28.14 | 37.96 | 52.01 | 64.03 | 0.046 |
| Whitening_60 | 2210 | 29.73 | 29.73 | 40.54 | 53.3 | 64.07 | 0.035 |
| Whitening_90 | 2210 | 22.76 | 32.71 | 44.52 | 55.29 | 65.52 | 0.027 |
| Smoothing_30 | 2210 | 14.84 | 38.1 | 47.06 | 56.56 | 58.1 | 0.413 |
| Smoothing_60 | 2210 | 1.0 | 30.95 | 68.05 | 67.06 | 77.33 | 0.923 |
| Smoothing_90 | 2210 | 0.27 | 34.52 | 65.2 | 65.63 | 75.48 | 0.967 |

## FF++ / cross-dataset
{"indomain": {"real": 68.62, "fake": 92.84, "filter": 84.95}, "FA": 8.13, "real_to_filter": 24.54, "MISS": 0.56, "heldout13": {"filter": 57.37, "fake": 18.47, "paired_excess_pp": 32.83}, "cdf": {"auc": 0.8802, "real_called_fake": 18.31}, "dfd": {"auc": 0.9527, "real_called_fake": 3.82}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
