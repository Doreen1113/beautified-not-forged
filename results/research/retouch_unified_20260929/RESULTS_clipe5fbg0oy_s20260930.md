# RU clipe5fbg0oy_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 56.79, 'fake': 11.99, 'filter': 31.22} | pooled {'n': 26519, 'to_real': 56.41, 'to_fake': 12.98, 'to_filter': 30.61, 'balanced_acc': 49.7, 'paired_rank': 50.36}
Eq.4 {'TP': {'eye': 0.804, 'jaw': 0.329, 'white': 0.659, 'smooth': 0.367}, 'TN_same_image': {'eye': 0.095, 'jaw': 0.034, 'white': 0.071, 'smooth': 0.026}, 'AC': {'eye': 0.078, 'jaw': 0.013, 'white': 0.052, 'smooth': 0.011}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.211, 'jaw': 0.68, 'white': 0.314, 'smooth': 0.511}
quantities {"eye": {"n": 6629, "spearman": -0.02, "mae": 0.6023, "pred_mean": -0.5176, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4326, "orig_pred_mean": -0.534}, "jaw": {"n": 6630, "spearman": -0.012, "mae": 0.3517, "pred_mean": -0.0269, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.5079, "orig_pred_mean": -0.0267}, "white": {"n": 6630, "spearman": -0.089, "mae": 0.5726, "pred_mean": 0.5029, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4343, "orig_pred_mean": 0.5072}, "smooth": {"n": 6630, "spearman": -0.033, "mae": 0.4531, "pred_mean": -0.1761, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.5691, "orig_pred_mean": -0.2032}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 55.84 | 12.71 | 31.45 | 50.11 | 55.0 | 0.803 |
| EyeEnlarging_60 | 2209 | 55.14 | 13.67 | 31.19 | 49.99 | 53.26 | 0.804 |
| EyeEnlarging_90 | 2210 | 54.89 | 15.34 | 29.77 | 49.28 | 50.23 | 0.805 |
| FaceLifting_30 | 2210 | 55.57 | 12.22 | 32.22 | 50.5 | 55.09 | 0.328 |
| FaceLifting_60 | 2210 | 54.98 | 13.03 | 31.99 | 50.39 | 53.76 | 0.329 |
| FaceLifting_90 | 2210 | 54.89 | 14.16 | 30.95 | 49.87 | 53.33 | 0.329 |
| Whitening_30 | 2210 | 56.74 | 12.67 | 30.59 | 49.68 | 48.24 | 0.684 |
| Whitening_60 | 2210 | 56.97 | 13.3 | 29.73 | 49.25 | 44.43 | 0.659 |
| Whitening_90 | 2210 | 56.47 | 14.16 | 29.37 | 49.07 | 46.18 | 0.634 |
| Smoothing_30 | 2210 | 58.96 | 11.45 | 29.59 | 49.19 | 47.15 | 0.389 |
| Smoothing_60 | 2210 | 59.19 | 10.54 | 30.27 | 49.53 | 49.91 | 0.354 |
| Smoothing_90 | 2210 | 57.33 | 12.44 | 30.23 | 49.5 | 47.78 | 0.359 |

## FF++ / cross-dataset
{"indomain": {"real": 39.29, "fake": 94.33, "filter": 45.36}, "FA": 17.17, "real_to_filter": 51.14, "MISS": 2.59, "heldout13": {"filter": 41.95, "fake": 28.27, "paired_excess_pp": -9.19}, "cdf": {"auc": 0.8888, "real_called_fake": 21.06}, "dfd": {"auc": 0.9427, "real_called_fake": 4.93}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
