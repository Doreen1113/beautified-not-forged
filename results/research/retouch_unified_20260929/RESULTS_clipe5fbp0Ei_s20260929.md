# RU clipe5fbp0Ei_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 58.55, 'fake': 2.67, 'filter': 38.78} | pooled {'n': 26519, 'to_real': 56.49, 'to_fake': 9.83, 'to_filter': 33.68, 'balanced_acc': 47.45, 'paired_rank': 32.76}
Eq.4 {'TP': {'eye': 0.952, 'jaw': 0.044, 'white': 0.398, 'smooth': 0.073}, 'TN_same_image': {'eye': 0.583, 'jaw': 0.022, 'white': 0.041, 'smooth': 0.011}, 'AC': {'eye': 0.562, 'jaw': 0.002, 'white': 0.023, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.048, 'jaw': 0.958, 'white': 0.592, 'smooth': 0.963}
quantities {"eye": {"n": 6629, "spearman": 0.094, "mae": 0.4949, "pred_mean": 0.451, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4794, "orig_pred_mean": 0.4427}, "jaw": {"n": 6630, "spearman": -0.022, "mae": 0.7132, "pred_mean": -0.6651, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.417, "orig_pred_mean": -0.6699}, "white": {"n": 6630, "spearman": -0.05, "mae": 0.5821, "pred_mean": 0.1518, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.5431, "orig_pred_mean": 0.1917}, "smooth": {"n": 6630, "spearman": -0.004, "mae": 0.4545, "pred_mean": -0.0563, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.5422, "orig_pred_mean": -0.1588}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 59.77 | 2.62 | 37.6 | 49.41 | 43.19 | 0.952 |
| EyeEnlarging_60 | 2209 | 57.81 | 3.3 | 38.89 | 50.05 | 46.88 | 0.95 |
| EyeEnlarging_90 | 2210 | 53.62 | 7.51 | 38.87 | 50.04 | 46.06 | 0.953 |
| FaceLifting_30 | 2210 | 61.22 | 2.62 | 36.15 | 48.69 | 33.82 | 0.043 |
| FaceLifting_60 | 2210 | 61.09 | 2.71 | 36.2 | 48.71 | 33.96 | 0.043 |
| FaceLifting_90 | 2210 | 60.9 | 3.48 | 35.61 | 48.42 | 33.94 | 0.045 |
| Whitening_30 | 2210 | 60.81 | 2.67 | 36.52 | 48.87 | 37.92 | 0.385 |
| Whitening_60 | 2210 | 60.36 | 3.12 | 36.52 | 48.87 | 39.8 | 0.401 |
| Whitening_90 | 2210 | 59.1 | 4.43 | 36.47 | 48.85 | 43.3 | 0.407 |
| Smoothing_30 | 2210 | 57.87 | 10.32 | 31.81 | 46.51 | 17.22 | 0.044 |
| Smoothing_60 | 2210 | 47.96 | 29.64 | 22.4 | 41.81 | 9.95 | 0.073 |
| Smoothing_90 | 2210 | 37.38 | 45.52 | 17.1 | 39.16 | 7.06 | 0.102 |

## FF++ / cross-dataset
{"indomain": {"real": 16.26, "fake": 70.66, "filter": 71.2}, "FA": 13.75, "real_to_filter": 79.18, "MISS": 3.03, "heldout13": {"filter": 69.0, "fake": 13.98, "paired_excess_pp": -10.18}, "cdf": {"auc": 0.8661, "real_called_fake": 9.62}, "dfd": {"auc": 0.9386, "real_called_fake": 5.51}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
