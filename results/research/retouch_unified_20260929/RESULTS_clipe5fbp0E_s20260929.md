# RU clipe5fbp0E_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 62.08, 'fake': 13.57, 'filter': 24.34} | pooled {'n': 26519, 'to_real': 53.22, 'to_fake': 27.16, 'to_filter': 19.62, 'balanced_acc': 47.64, 'paired_rank': 31.92}
Eq.4 {'TP': {'eye': 0.959, 'jaw': 0.08, 'white': 0.428, 'smooth': 0.299}, 'TN_same_image': {'eye': 0.507, 'jaw': 0.014, 'white': 0.034, 'smooth': 0.004}, 'AC': {'eye': 0.493, 'jaw': 0.001, 'white': 0.023, 'smooth': 0.001}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.04, 'jaw': 0.918, 'white': 0.566, 'smooth': 0.928}
quantities {"eye": {"n": 6629, "spearman": 0.064, "mae": 0.4762, "pred_mean": 0.4138, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4621, "orig_pred_mean": 0.404}, "jaw": {"n": 6630, "spearman": -0.019, "mae": 0.6037, "pred_mean": -0.5271, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4328, "orig_pred_mean": -0.5404}, "white": {"n": 6630, "spearman": -0.032, "mae": 0.5986, "pred_mean": 0.1495, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.5137, "orig_pred_mean": 0.1828}, "smooth": {"n": 6630, "spearman": -0.028, "mae": 0.5229, "pred_mean": -0.233, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.4725, "orig_pred_mean": -0.2987}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 62.85 | 13.48 | 23.67 | 49.66 | 44.75 | 0.959 |
| EyeEnlarging_60 | 2209 | 61.07 | 14.21 | 24.72 | 50.19 | 48.64 | 0.958 |
| EyeEnlarging_90 | 2210 | 57.51 | 16.2 | 26.29 | 50.97 | 49.98 | 0.958 |
| FaceLifting_30 | 2210 | 63.71 | 14.03 | 22.26 | 48.96 | 35.14 | 0.076 |
| FaceLifting_60 | 2210 | 63.48 | 14.52 | 21.99 | 48.83 | 33.98 | 0.08 |
| FaceLifting_90 | 2210 | 62.4 | 15.61 | 21.99 | 48.83 | 32.04 | 0.086 |
| Whitening_30 | 2210 | 63.21 | 13.71 | 23.08 | 49.37 | 39.64 | 0.419 |
| Whitening_60 | 2210 | 61.45 | 15.84 | 22.71 | 49.19 | 39.48 | 0.427 |
| Whitening_90 | 2210 | 58.1 | 18.28 | 23.62 | 49.64 | 41.95 | 0.438 |
| Smoothing_30 | 2210 | 47.24 | 38.87 | 13.89 | 44.78 | 9.77 | 0.168 |
| Smoothing_60 | 2210 | 22.58 | 70.63 | 6.79 | 41.22 | 4.48 | 0.317 |
| Smoothing_90 | 2210 | 15.02 | 80.54 | 4.43 | 40.05 | 3.26 | 0.411 |

## FF++ / cross-dataset
{"indomain": {"real": 39.44, "fake": 87.58, "filter": 44.83}, "FA": 20.59, "real_to_filter": 53.5, "MISS": 2.75, "heldout13": {"filter": 45.06, "fake": 21.12, "paired_excess_pp": -8.44}, "cdf": {"auc": 0.8975, "real_called_fake": 13.25}, "dfd": {"auc": 0.9685, "real_called_fake": 7.21}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
