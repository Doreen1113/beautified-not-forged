# RU clipe4_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 57.87, 'fake': 0.27, 'filter': 41.86} | pooled {'n': 26519, 'to_real': 17.55, 'to_fake': 0.12, 'to_filter': 82.33, 'balanced_acc': 70.23, 'paired_rank': 94.77}
Eq.4 {'TP': {'eye': 0.212, 'jaw': 0.35, 'white': 0.569, 'smooth': 0.961}, 'TN_same_image': {'eye': 0.622, 'jaw': 0.77, 'white': 0.798, 'smooth': 0.257}, 'AC': {'eye': 0.181, 'jaw': 0.304, 'white': 0.456, 'smooth': 0.228}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.977, 'jaw': 0.953, 'white': 0.819, 'smooth': 0.985}
quantities {"eye": {"n": 6629, "spearman": 0.333, "mae": 0.0286, "pred_mean": 0.0005, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0195, "orig_pred_mean": -0.0074}, "jaw": {"n": 6630, "spearman": 0.03, "mae": 0.0219, "pred_mean": 0.0001, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0188, "orig_pred_mean": -0.0031}, "white": {"n": 6630, "spearman": -0.121, "mae": 0.4698, "pred_mean": 0.1032, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0127, "orig_pred_mean": 0.0262}, "smooth": {"n": 6630, "spearman": 0.351, "mae": 0.0874, "pred_mean": 0.107, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0278, "orig_pred_mean": 0.0012}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 29.64 | 0.14 | 70.23 | 64.18 | 94.75 | 0.085 |
| EyeEnlarging_60 | 2209 | 20.64 | 0.18 | 79.18 | 68.66 | 97.15 | 0.217 |
| EyeEnlarging_90 | 2210 | 14.71 | 0.23 | 85.07 | 71.6 | 98.19 | 0.335 |
| FaceLifting_30 | 2210 | 32.22 | 0.09 | 67.69 | 62.92 | 89.12 | 0.278 |
| FaceLifting_60 | 2210 | 25.38 | 0.09 | 74.52 | 66.33 | 93.17 | 0.348 |
| FaceLifting_90 | 2210 | 19.59 | 0.09 | 80.32 | 69.23 | 95.34 | 0.423 |
| Whitening_30 | 2210 | 28.05 | 0.14 | 71.81 | 64.97 | 88.87 | 0.398 |
| Whitening_60 | 2210 | 20.86 | 0.23 | 78.91 | 68.53 | 90.59 | 0.578 |
| Whitening_90 | 2210 | 14.8 | 0.27 | 84.93 | 71.54 | 93.98 | 0.731 |
| Smoothing_30 | 2210 | 4.43 | 0.05 | 95.52 | 76.83 | 96.47 | 0.888 |
| Smoothing_60 | 2210 | 0.18 | 0.0 | 99.82 | 78.98 | 99.86 | 0.996 |
| Smoothing_90 | 2210 | 0.05 | 0.0 | 99.95 | 79.05 | 99.73 | 0.999 |

## FF++ / cross-dataset
{"indomain": {"real": 77.96, "fake": 88.88, "filter": 89.21}, "FA": 3.95, "real_to_filter": 13.22, "MISS": 0.62, "heldout13": {"filter": 64.74, "fake": 10.41, "paired_excess_pp": 51.52}, "cdf": {"auc": 0.8876, "real_called_fake": 18.98}, "dfd": {"auc": 0.9484, "real_called_fake": 3.87}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
