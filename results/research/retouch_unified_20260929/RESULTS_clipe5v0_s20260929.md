# RU clipe5v0_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 83.8, 'fake': 0.41, 'filter': 15.79} | pooled {'n': 26519, 'to_real': 34.19, 'to_fake': 0.21, 'to_filter': 65.6, 'balanced_acc': 74.9, 'paired_rank': 94.69}
Eq.4 {'TP': {'eye': 0.308, 'jaw': 0.282, 'white': 0.321, 'smooth': 0.951}, 'TN_same_image': {'eye': 0.818, 'jaw': 0.896, 'white': 0.758, 'smooth': 0.454}, 'AC': {'eye': 0.285, 'jaw': 0.259, 'white': 0.215, 'smooth': 0.411}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.975, 'jaw': 0.979, 'white': 0.957, 'smooth': 0.989}
quantities {"eye": {"n": 6629, "spearman": 0.394, "mae": 0.0207, "pred_mean": 0.0139, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0107, "orig_pred_mean": 0.0028}, "jaw": {"n": 6630, "spearman": 0.055, "mae": 0.0176, "pred_mean": 0.0052, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0098, "orig_pred_mean": 0.0011}, "white": {"n": 6630, "spearman": -0.056, "mae": 0.4967, "pred_mean": 0.0441, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0097, "orig_pred_mean": 0.0084}, "smooth": {"n": 6630, "spearman": 0.331, "mae": 0.0987, "pred_mean": 0.0886, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0209, "orig_pred_mean": -0.0041}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 53.03 | 0.36 | 46.61 | 65.41 | 96.04 | 0.161 |
| EyeEnlarging_60 | 2209 | 39.25 | 0.23 | 60.53 | 72.37 | 97.78 | 0.32 |
| EyeEnlarging_90 | 2210 | 29.64 | 0.23 | 70.14 | 77.17 | 98.19 | 0.444 |
| FaceLifting_30 | 2210 | 58.64 | 0.27 | 41.09 | 62.65 | 87.26 | 0.209 |
| FaceLifting_60 | 2210 | 51.27 | 0.27 | 48.46 | 66.34 | 91.72 | 0.276 |
| FaceLifting_90 | 2210 | 43.08 | 0.36 | 56.56 | 70.39 | 94.48 | 0.361 |
| Whitening_30 | 2210 | 53.76 | 0.27 | 45.97 | 65.09 | 88.35 | 0.138 |
| Whitening_60 | 2210 | 40.95 | 0.23 | 58.82 | 71.52 | 90.14 | 0.318 |
| Whitening_90 | 2210 | 31.13 | 0.23 | 68.64 | 76.43 | 93.78 | 0.508 |
| Smoothing_30 | 2210 | 8.78 | 0.05 | 91.18 | 87.69 | 98.91 | 0.865 |
| Smoothing_60 | 2210 | 0.54 | 0.0 | 99.46 | 91.83 | 99.86 | 0.992 |
| Smoothing_90 | 2210 | 0.23 | 0.05 | 99.73 | 91.97 | 99.77 | 0.996 |

## FF++ / cross-dataset
{"indomain": {"real": 82.83, "fake": 89.88, "filter": 84.65}, "FA": 6.53, "real_to_filter": 11.4, "MISS": 1.12, "heldout13": {"filter": 73.1, "fake": 14.51, "paired_excess_pp": 61.7}, "cdf": {"auc": 0.8806, "real_called_fake": 16.87}, "dfd": {"auc": 0.9596, "real_called_fake": 2.86}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": true, "D2_heldout_excess>=30": true}}
