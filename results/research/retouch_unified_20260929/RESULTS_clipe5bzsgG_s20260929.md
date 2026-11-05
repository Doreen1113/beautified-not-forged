# RU clipe5bzsgG_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 4.48, 'fake': 0.41, 'filter': 95.11} | pooled {'n': 26519, 'to_real': 10.31, 'to_fake': 0.33, 'to_filter': 89.36, 'balanced_acc': 47.12, 'paired_rank': 31.98}
Eq.4 {'TP': {'eye': 0.509, 'jaw': 0.99, 'white': 0.86, 'smooth': 0.176}, 'TN_same_image': {'eye': 0.0, 'jaw': 0.089, 'white': 0.007, 'smooth': 0.001}, 'AC': {'eye': 0.0, 'jaw': 0.088, 'white': 0.006, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.59, 'jaw': 0.013, 'white': 0.165, 'smooth': 0.984}
quantities {"eye": {"n": 6629, "spearman": 0.03, "mae": 0.8146, "pred_mean": 0.831, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.352, "orig_pred_mean": 0.8525}, "jaw": {"n": 6630, "spearman": 0.022, "mae": 0.3049, "pred_mean": 0.2715, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.5236, "orig_pred_mean": 0.2439}, "white": {"n": 6630, "spearman": -0.092, "mae": 0.5374, "pred_mean": 0.1436, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.5324, "orig_pred_mean": 0.1751}, "smooth": {"n": 6630, "spearman": 0.126, "mae": 0.3917, "pred_mean": -0.1582, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.4082, "orig_pred_mean": -0.4883}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 4.84 | 0.36 | 94.8 | 49.84 | 47.1 | 0.492 |
| EyeEnlarging_60 | 2209 | 4.66 | 0.36 | 94.98 | 49.93 | 50.23 | 0.51 |
| EyeEnlarging_90 | 2210 | 4.71 | 0.36 | 94.93 | 49.91 | 50.77 | 0.524 |
| FaceLifting_30 | 2210 | 5.43 | 0.41 | 94.16 | 49.53 | 35.52 | 0.989 |
| FaceLifting_60 | 2210 | 6.11 | 0.27 | 93.62 | 49.25 | 32.26 | 0.991 |
| FaceLifting_90 | 2210 | 6.38 | 0.32 | 93.3 | 49.1 | 31.83 | 0.99 |
| Whitening_30 | 2210 | 7.29 | 0.32 | 92.4 | 48.64 | 27.35 | 0.866 |
| Whitening_60 | 2210 | 9.91 | 0.32 | 89.77 | 47.33 | 21.86 | 0.863 |
| Whitening_90 | 2210 | 13.17 | 0.32 | 86.52 | 45.7 | 19.3 | 0.85 |
| Smoothing_30 | 2210 | 10.95 | 0.41 | 88.64 | 46.77 | 28.71 | 0.07 |
| Smoothing_60 | 2210 | 23.39 | 0.27 | 76.33 | 40.61 | 21.13 | 0.212 |
| Smoothing_90 | 2210 | 26.88 | 0.27 | 72.85 | 38.87 | 17.74 | 0.247 |

## FF++ / cross-dataset
{"indomain": {"real": 31.23, "fake": 80.37, "filter": 54.1}, "FA": 12.16, "real_to_filter": 61.85, "MISS": 5.0, "heldout13": {"filter": 49.01, "fake": 17.86, "paired_excess_pp": -12.84}, "cdf": {"auc": 0.807, "real_called_fake": 15.85}, "dfd": {"auc": 0.955, "real_called_fake": 1.75}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
