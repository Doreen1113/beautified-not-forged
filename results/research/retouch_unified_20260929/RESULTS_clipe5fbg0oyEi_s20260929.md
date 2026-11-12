# RU clipe5fbg0oyEi_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 59.73, 'fake': 1.36, 'filter': 38.91} | pooled {'n': 26519, 'to_real': 59.8, 'to_fake': 5.41, 'to_filter': 34.79, 'balanced_acc': 47.94, 'paired_rank': 32.55}
Eq.4 {'TP': {'eye': 0.953, 'jaw': 0.042, 'white': 0.4, 'smooth': 0.052}, 'TN_same_image': {'eye': 0.582, 'jaw': 0.023, 'white': 0.043, 'smooth': 0.013}, 'AC': {'eye': 0.562, 'jaw': 0.002, 'white': 0.024, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.048, 'jaw': 0.96, 'white': 0.592, 'smooth': 0.965}
quantities {"eye": {"n": 6629, "spearman": 0.093, "mae": 0.4859, "pred_mean": 0.4401, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4772, "orig_pred_mean": 0.4332}, "jaw": {"n": 6630, "spearman": -0.024, "mae": 0.7096, "pred_mean": -0.6609, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4129, "orig_pred_mean": -0.6651}, "white": {"n": 6630, "spearman": -0.051, "mae": 0.5844, "pred_mean": 0.1449, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.5385, "orig_pred_mean": 0.1857}, "smooth": {"n": 6630, "spearman": 0.007, "mae": 0.4511, "pred_mean": -0.0546, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.5335, "orig_pred_mean": -0.1602}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 61.04 | 1.36 | 37.6 | 49.35 | 40.34 | 0.952 |
| EyeEnlarging_60 | 2209 | 58.99 | 1.95 | 39.07 | 50.08 | 45.7 | 0.951 |
| EyeEnlarging_90 | 2210 | 55.43 | 4.8 | 39.77 | 50.43 | 45.61 | 0.955 |
| FaceLifting_30 | 2210 | 62.35 | 1.22 | 36.43 | 48.76 | 31.06 | 0.041 |
| FaceLifting_60 | 2210 | 62.58 | 1.49 | 35.93 | 48.51 | 31.27 | 0.042 |
| FaceLifting_90 | 2210 | 62.44 | 1.99 | 35.57 | 48.33 | 32.74 | 0.043 |
| Whitening_30 | 2210 | 62.17 | 1.22 | 36.61 | 48.85 | 36.18 | 0.389 |
| Whitening_60 | 2210 | 62.04 | 1.54 | 36.43 | 48.76 | 39.23 | 0.401 |
| Whitening_90 | 2210 | 61.04 | 2.31 | 36.65 | 48.87 | 43.53 | 0.409 |
| Smoothing_30 | 2210 | 61.81 | 5.25 | 32.94 | 47.02 | 19.62 | 0.038 |
| Smoothing_60 | 2210 | 56.79 | 16.02 | 27.19 | 44.14 | 13.76 | 0.052 |
| Smoothing_90 | 2210 | 50.9 | 25.84 | 23.26 | 42.17 | 11.58 | 0.067 |

## FF++ / cross-dataset
{"indomain": {"real": 17.55, "fake": 64.63, "filter": 75.0}, "FA": 7.75, "real_to_filter": 79.26, "MISS": 5.03, "heldout13": {"filter": 71.05, "fake": 10.33, "paired_excess_pp": -8.21}, "cdf": {"auc": 0.858, "real_called_fake": 8.04}, "dfd": {"auc": 0.9349, "real_called_fake": 3.92}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
