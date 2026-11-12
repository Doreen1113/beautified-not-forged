# RU clipe5M_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 80.36, 'fake': 0.54, 'filter': 19.1} | pooled {'n': 26519, 'to_real': 29.5, 'to_fake': 0.4, 'to_filter': 70.11, 'balanced_acc': 75.5, 'paired_rank': 94.8}
Eq.4 {'TP': {'eye': 0.341, 'jaw': 0.408, 'white': 0.36, 'smooth': 0.944}, 'TN_same_image': {'eye': 0.723, 'jaw': 0.891, 'white': 0.709, 'smooth': 0.404}, 'AC': {'eye': 0.302, 'jaw': 0.37, 'white': 0.236, 'smooth': 0.359}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.973, 'jaw': 0.949, 'white': 0.954, 'smooth': 0.991}
quantities {"eye": {"n": 6629, "spearman": 0.426, "mae": 0.0217, "pred_mean": 0.0103, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0117, "orig_pred_mean": 0.0009}, "jaw": {"n": 6630, "spearman": 0.153, "mae": 0.0157, "pred_mean": 0.0072, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0096, "orig_pred_mean": 0.001}, "white": {"n": 6630, "spearman": -0.107, "mae": 0.4921, "pred_mean": 0.0552, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0082, "orig_pred_mean": 0.0084}, "smooth": {"n": 6630, "spearman": 0.259, "mae": 0.0899, "pred_mean": 0.1082, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.02, "orig_pred_mean": 0.0009}}
bars {"R1_balanced>=75": true, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 46.61 | 0.41 | 52.99 | 66.94 | 95.86 | 0.182 |
| EyeEnlarging_60 | 2209 | 30.33 | 0.32 | 69.35 | 75.13 | 98.1 | 0.365 |
| EyeEnlarging_90 | 2210 | 22.85 | 0.23 | 76.92 | 78.91 | 98.6 | 0.476 |
| FaceLifting_30 | 2210 | 51.54 | 0.23 | 48.24 | 64.57 | 88.57 | 0.313 |
| FaceLifting_60 | 2210 | 43.17 | 0.27 | 56.56 | 68.73 | 94.25 | 0.408 |
| FaceLifting_90 | 2210 | 33.89 | 0.27 | 65.84 | 73.37 | 96.61 | 0.504 |
| Whitening_30 | 2210 | 48.96 | 0.36 | 50.68 | 65.79 | 86.43 | 0.161 |
| Whitening_60 | 2210 | 37.87 | 0.59 | 61.54 | 71.22 | 89.41 | 0.365 |
| Whitening_90 | 2210 | 28.87 | 0.68 | 70.45 | 75.68 | 92.53 | 0.554 |
| Smoothing_30 | 2210 | 8.78 | 0.32 | 90.9 | 85.9 | 98.6 | 0.851 |
| Smoothing_60 | 2210 | 0.59 | 0.36 | 99.05 | 89.97 | 99.55 | 0.988 |
| Smoothing_90 | 2210 | 0.5 | 0.72 | 98.78 | 89.84 | 99.14 | 0.993 |

## FF++ / cross-dataset
{"indomain": {"real": 79.18, "fake": 91.95, "filter": 87.01}, "FA": 6.46, "real_to_filter": 12.46, "MISS": 0.5, "heldout13": {"filter": 78.42, "fake": 15.58, "paired_excess_pp": 65.96}, "cdf": {"auc": 0.8915, "real_called_fake": 20.85}, "dfd": {"auc": 0.9588, "real_called_fake": 3.82}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
