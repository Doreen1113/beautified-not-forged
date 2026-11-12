# RU clipe5fbE_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 63.8, 'fake': 13.39, 'filter': 22.81} | pooled {'n': 26519, 'to_real': 59.64, 'to_fake': 21.28, 'to_filter': 19.08, 'balanced_acc': 48.13, 'paired_rank': 36.88}
Eq.4 {'TP': {'eye': 0.962, 'jaw': 0.081, 'white': 0.432, 'smooth': 0.172}, 'TN_same_image': {'eye': 0.505, 'jaw': 0.012, 'white': 0.028, 'smooth': 0.004}, 'AC': {'eye': 0.493, 'jaw': 0.001, 'white': 0.02, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.034, 'jaw': 0.912, 'white': 0.571, 'smooth': 0.921}
quantities {"eye": {"n": 6629, "spearman": 0.069, "mae": 0.49, "pred_mean": 0.4288, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4739, "orig_pred_mean": 0.4248}, "jaw": {"n": 6630, "spearman": -0.025, "mae": 0.6313, "pred_mean": -0.5635, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4397, "orig_pred_mean": -0.5722}, "white": {"n": 6630, "spearman": -0.023, "mae": 0.5834, "pred_mean": 0.1884, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.5251, "orig_pred_mean": 0.2211}, "smooth": {"n": 6630, "spearman": -0.025, "mae": 0.5214, "pred_mean": -0.231, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.5163, "orig_pred_mean": -0.3044}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 66.02 | 12.44 | 21.54 | 49.36 | 50.07 | 0.963 |
| EyeEnlarging_60 | 2209 | 64.46 | 12.77 | 22.77 | 49.98 | 53.33 | 0.962 |
| EyeEnlarging_90 | 2210 | 61.13 | 14.52 | 24.34 | 50.77 | 56.29 | 0.961 |
| FaceLifting_30 | 2210 | 66.38 | 12.76 | 20.86 | 49.02 | 40.34 | 0.076 |
| FaceLifting_60 | 2210 | 66.52 | 13.12 | 20.36 | 48.78 | 39.66 | 0.08 |
| FaceLifting_90 | 2210 | 65.48 | 14.12 | 20.41 | 48.8 | 36.65 | 0.086 |
| Whitening_30 | 2210 | 66.15 | 12.35 | 21.49 | 49.34 | 43.55 | 0.416 |
| Whitening_60 | 2210 | 64.62 | 13.71 | 21.67 | 49.43 | 43.76 | 0.431 |
| Whitening_90 | 2210 | 61.99 | 15.79 | 22.22 | 49.7 | 45.48 | 0.448 |
| Smoothing_30 | 2210 | 57.15 | 28.05 | 14.8 | 45.99 | 15.38 | 0.12 |
| Smoothing_60 | 2210 | 43.35 | 46.38 | 10.27 | 43.73 | 10.05 | 0.173 |
| Smoothing_90 | 2210 | 32.49 | 59.32 | 8.19 | 42.69 | 8.01 | 0.223 |

## FF++ / cross-dataset
{"indomain": {"real": 46.96, "fake": 83.47, "filter": 41.72}, "FA": 12.84, "real_to_filter": 47.87, "MISS": 3.94, "heldout13": {"filter": 43.39, "fake": 15.58, "paired_excess_pp": -4.48}, "cdf": {"auc": 0.8859, "real_called_fake": 9.01}, "dfd": {"auc": 0.9688, "real_called_fake": 3.18}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
