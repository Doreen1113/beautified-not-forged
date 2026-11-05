# RU clipe5fbp0F2_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 19.64, 'fake': 15.48, 'filter': 64.89} | pooled {'n': 26519, 'to_real': 16.12, 'to_fake': 24.28, 'to_filter': 59.59, 'balanced_acc': 47.35, 'paired_rank': 49.25}
Eq.4 {'TP': {'eye': 0.095, 'jaw': 0.942, 'white': 0.438, 'smooth': 0.027}, 'TN_same_image': {'eye': 0.032, 'jaw': 0.508, 'white': 0.056, 'smooth': 0.029}, 'AC': {'eye': 0.001, 'jaw': 0.477, 'white': 0.022, 'smooth': 0.002}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.909, 'jaw': 0.055, 'white': 0.562, 'smooth': 0.981}
quantities {"eye": {"n": 6629, "spearman": -0.09, "mae": 0.4418, "pred_mean": -0.0544, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3953, "orig_pred_mean": -0.0256}, "jaw": {"n": 6630, "spearman": 0.004, "mae": 0.3269, "pred_mean": -0.0835, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4306, "orig_pred_mean": -0.0706}, "white": {"n": 6630, "spearman": -0.046, "mae": 0.5765, "pred_mean": 0.2637, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4093, "orig_pred_mean": 0.2621}, "smooth": {"n": 6630, "spearman": 0.188, "mae": 0.4631, "pred_mean": 0.466, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.4634, "orig_pred_mean": 0.2191}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 17.6 | 14.98 | 67.42 | 51.27 | 65.52 | 0.095 |
| EyeEnlarging_60 | 2209 | 16.89 | 15.21 | 67.9 | 51.51 | 64.76 | 0.093 |
| EyeEnlarging_90 | 2210 | 15.48 | 17.1 | 67.42 | 51.27 | 63.48 | 0.096 |
| FaceLifting_30 | 2210 | 18.01 | 14.8 | 67.19 | 51.15 | 62.26 | 0.944 |
| FaceLifting_60 | 2210 | 18.05 | 15.75 | 66.2 | 50.65 | 59.43 | 0.943 |
| FaceLifting_90 | 2210 | 17.6 | 16.43 | 65.97 | 50.54 | 57.74 | 0.939 |
| Whitening_30 | 2210 | 19.32 | 16.15 | 64.52 | 49.82 | 51.65 | 0.441 |
| Whitening_60 | 2210 | 20.14 | 17.96 | 61.9 | 48.51 | 42.56 | 0.446 |
| Whitening_90 | 2210 | 20.09 | 20.41 | 59.5 | 47.31 | 40.0 | 0.427 |
| Smoothing_30 | 2210 | 14.3 | 30.5 | 55.2 | 45.16 | 38.39 | 0.021 |
| Smoothing_60 | 2210 | 9.14 | 50.68 | 40.18 | 37.65 | 25.38 | 0.026 |
| Smoothing_90 | 2210 | 6.88 | 61.45 | 31.67 | 33.39 | 19.84 | 0.033 |

## FF++ / cross-dataset
{"indomain": {"real": 11.47, "fake": 79.6, "filter": 68.09}, "FA": 19.6, "real_to_filter": 78.88, "MISS": 1.12, "heldout13": {"filter": 63.15, "fake": 25.53, "paired_excess_pp": -15.73}, "cdf": {"auc": 0.8646, "real_called_fake": 10.05}, "dfd": {"auc": 0.9516, "real_called_fake": 6.31}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
