# RU clipe5g0_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 82.13, 'fake': 0.59, 'filter': 17.29} | pooled {'n': 26519, 'to_real': 34.03, 'to_fake': 0.32, 'to_filter': 65.65, 'balanced_acc': 74.18, 'paired_rank': 92.75}
Eq.4 {'TP': {'eye': 0.223, 'jaw': 0.343, 'white': 0.302, 'smooth': 0.957}, 'TN_same_image': {'eye': 0.771, 'jaw': 0.933, 'white': 0.789, 'smooth': 0.469}, 'AC': {'eye': 0.211, 'jaw': 0.33, 'white': 0.238, 'smooth': 0.432}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.989, 'jaw': 0.963, 'white': 0.957, 'smooth': 0.987}
quantities {"eye": {"n": 6629, "spearman": 0.337, "mae": 0.0231, "pred_mean": 0.0076, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0106, "orig_pred_mean": 0.0028}, "jaw": {"n": 6630, "spearman": 0.133, "mae": 0.0218, "pred_mean": -0.0, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0096, "orig_pred_mean": -0.0056}, "white": {"n": 6630, "spearman": -0.095, "mae": 0.4948, "pred_mean": 0.0519, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0085, "orig_pred_mean": 0.0087}, "smooth": {"n": 6630, "spearman": 0.268, "mae": 0.0976, "pred_mean": 0.091, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0184, "orig_pred_mean": 0.0037}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 54.48 | 0.32 | 45.2 | 63.96 | 93.94 | 0.076 |
| EyeEnlarging_60 | 2209 | 40.38 | 0.32 | 59.3 | 71.01 | 96.6 | 0.231 |
| EyeEnlarging_90 | 2210 | 30.41 | 0.41 | 69.19 | 75.95 | 97.42 | 0.363 |
| FaceLifting_30 | 2210 | 56.97 | 0.27 | 42.76 | 62.74 | 86.09 | 0.254 |
| FaceLifting_60 | 2210 | 48.96 | 0.32 | 50.72 | 66.72 | 90.05 | 0.338 |
| FaceLifting_90 | 2210 | 40.14 | 0.23 | 59.64 | 71.17 | 93.35 | 0.436 |
| Whitening_30 | 2210 | 55.25 | 0.23 | 44.52 | 63.62 | 83.53 | 0.127 |
| Whitening_60 | 2210 | 42.62 | 0.45 | 56.92 | 69.82 | 84.82 | 0.295 |
| Whitening_90 | 2210 | 32.67 | 0.54 | 66.79 | 74.75 | 89.37 | 0.485 |
| Smoothing_30 | 2210 | 5.84 | 0.36 | 93.8 | 88.26 | 98.6 | 0.885 |
| Smoothing_60 | 2210 | 0.36 | 0.09 | 99.55 | 91.13 | 99.77 | 0.992 |
| Smoothing_90 | 2210 | 0.27 | 0.36 | 99.37 | 91.04 | 99.46 | 0.995 |

## FF++ / cross-dataset
{"indomain": {"real": 77.05, "fake": 91.76, "filter": 88.37}, "FA": 4.64, "real_to_filter": 15.05, "MISS": 0.5, "heldout13": {"filter": 64.74, "fake": 11.47, "paired_excess_pp": 49.69}, "cdf": {"auc": 0.8894, "real_called_fake": 17.41}, "dfd": {"auc": 0.955, "real_called_fake": 3.44}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
