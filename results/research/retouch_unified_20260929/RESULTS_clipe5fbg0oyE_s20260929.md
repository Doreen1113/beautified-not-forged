# RU clipe5fbg0oyE_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 66.2, 'fake': 9.23, 'filter': 24.57} | pooled {'n': 26519, 'to_real': 65.68, 'to_fake': 11.98, 'to_filter': 22.34, 'balanced_acc': 48.89, 'paired_rank': 34.71}
Eq.4 {'TP': {'eye': 0.952, 'jaw': 0.061, 'white': 0.449, 'smooth': 0.07}, 'TN_same_image': {'eye': 0.525, 'jaw': 0.016, 'white': 0.036, 'smooth': 0.009}, 'AC': {'eye': 0.507, 'jaw': 0.002, 'white': 0.025, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.043, 'jaw': 0.944, 'white': 0.552, 'smooth': 0.949}
quantities {"eye": {"n": 6629, "spearman": 0.078, "mae": 0.4657, "pred_mean": 0.4013, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4646, "orig_pred_mean": 0.3852}, "jaw": {"n": 6630, "spearman": -0.028, "mae": 0.6404, "pred_mean": -0.5762, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4204, "orig_pred_mean": -0.5868}, "white": {"n": 6630, "spearman": -0.034, "mae": 0.6287, "pred_mean": 0.0621, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.5207, "orig_pred_mean": 0.1057}, "smooth": {"n": 6630, "spearman": -0.024, "mae": 0.5265, "pred_mean": -0.2333, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.5034, "orig_pred_mean": -0.3012}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 66.74 | 9.37 | 23.89 | 49.66 | 41.97 | 0.954 |
| EyeEnlarging_60 | 2209 | 64.64 | 10.19 | 25.17 | 50.3 | 45.88 | 0.953 |
| EyeEnlarging_90 | 2210 | 61.58 | 11.9 | 26.52 | 50.97 | 48.08 | 0.95 |
| FaceLifting_30 | 2210 | 68.42 | 9.19 | 22.4 | 48.91 | 31.83 | 0.057 |
| FaceLifting_60 | 2210 | 68.01 | 10.14 | 21.86 | 48.64 | 30.61 | 0.06 |
| FaceLifting_90 | 2210 | 66.83 | 11.45 | 21.72 | 48.57 | 29.68 | 0.067 |
| Whitening_30 | 2210 | 68.55 | 8.6 | 22.85 | 49.14 | 38.76 | 0.436 |
| Whitening_60 | 2210 | 67.33 | 9.19 | 23.48 | 49.46 | 41.2 | 0.452 |
| Whitening_90 | 2210 | 64.71 | 10.9 | 24.39 | 49.91 | 44.03 | 0.459 |
| Smoothing_30 | 2210 | 67.29 | 12.85 | 19.86 | 47.65 | 21.81 | 0.06 |
| Smoothing_60 | 2210 | 63.8 | 17.65 | 18.55 | 46.99 | 22.13 | 0.069 |
| Smoothing_90 | 2210 | 60.23 | 22.35 | 17.42 | 46.43 | 20.54 | 0.08 |

## FF++ / cross-dataset
{"indomain": {"real": 48.1, "fake": 80.34, "filter": 40.5}, "FA": 12.61, "real_to_filter": 46.05, "MISS": 10.44, "heldout13": {"filter": 37.92, "fake": 20.29, "paired_excess_pp": -8.13}, "cdf": {"auc": 0.8901, "real_called_fake": 11.21}, "dfd": {"auc": 0.9654, "real_called_fake": 3.55}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
