# RU clipe5fbg0oy_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 19.59, 'fake': 7.87, 'filter': 72.53} | pooled {'n': 26519, 'to_real': 20.65, 'to_fake': 8.07, 'to_filter': 71.29, 'balanced_acc': 49.38, 'paired_rank': 48.91}
Eq.4 {'TP': {'eye': 0.062, 'jaw': 0.905, 'white': 0.432, 'smooth': 0.007}, 'TN_same_image': {'eye': 0.059, 'jaw': 0.535, 'white': 0.1, 'smooth': 0.057}, 'AC': {'eye': 0.002, 'jaw': 0.479, 'white': 0.036, 'smooth': 0.001}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.938, 'jaw': 0.089, 'white': 0.553, 'smooth': 0.991}
quantities {"eye": {"n": 6629, "spearman": -0.045, "mae": 0.4741, "pred_mean": 0.3586, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3732, "orig_pred_mean": 0.3517}, "jaw": {"n": 6630, "spearman": 0.012, "mae": 0.3268, "pred_mean": -0.0782, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4297, "orig_pred_mean": -0.0776}, "white": {"n": 6630, "spearman": -0.014, "mae": 0.5858, "pred_mean": 0.1985, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4094, "orig_pred_mean": 0.202}, "smooth": {"n": 6630, "spearman": -0.005, "mae": 0.3749, "pred_mean": 0.3419, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3861, "orig_pred_mean": 0.2383}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 18.37 | 7.74 | 73.89 | 50.68 | 59.48 | 0.062 |
| EyeEnlarging_60 | 2209 | 18.2 | 8.1 | 73.7 | 50.58 | 60.48 | 0.061 |
| EyeEnlarging_90 | 2210 | 16.97 | 8.24 | 74.8 | 51.13 | 62.94 | 0.062 |
| FaceLifting_30 | 2210 | 19.05 | 7.51 | 73.44 | 50.45 | 55.72 | 0.905 |
| FaceLifting_60 | 2210 | 19.46 | 7.92 | 72.62 | 50.05 | 54.8 | 0.905 |
| FaceLifting_90 | 2210 | 18.6 | 8.6 | 72.81 | 50.14 | 53.71 | 0.905 |
| Whitening_30 | 2210 | 20.45 | 7.83 | 71.72 | 49.59 | 45.45 | 0.443 |
| Whitening_60 | 2210 | 22.76 | 8.55 | 68.69 | 48.08 | 37.96 | 0.437 |
| Whitening_90 | 2210 | 24.03 | 8.87 | 67.1 | 47.29 | 37.04 | 0.418 |
| Smoothing_30 | 2210 | 22.26 | 6.74 | 71.0 | 49.23 | 41.31 | 0.006 |
| Smoothing_60 | 2210 | 23.98 | 6.92 | 69.1 | 48.28 | 41.13 | 0.008 |
| Smoothing_90 | 2210 | 23.62 | 9.77 | 66.61 | 47.04 | 36.88 | 0.006 |

## FF++ / cross-dataset
{"indomain": {"real": 22.19, "fake": 91.14, "filter": 62.92}, "FA": 11.47, "real_to_filter": 72.8, "MISS": 2.34, "heldout13": {"filter": 56.0, "fake": 20.9, "paired_excess_pp": -16.8}, "cdf": {"auc": 0.8693, "real_called_fake": 12.23}, "dfd": {"auc": 0.9508, "real_called_fake": 2.12}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
