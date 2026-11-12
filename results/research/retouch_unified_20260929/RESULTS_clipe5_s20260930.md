# RU clipe5_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 79.82, 'fake': 0.54, 'filter': 19.64} | pooled {'n': 26519, 'to_real': 29.09, 'to_fake': 0.44, 'to_filter': 70.47, 'balanced_acc': 75.42, 'paired_rank': 94.3}
Eq.4 {'TP': {'eye': 0.289, 'jaw': 0.367, 'white': 0.384, 'smooth': 0.952}, 'TN_same_image': {'eye': 0.747, 'jaw': 0.9, 'white': 0.752, 'smooth': 0.428}, 'AC': {'eye': 0.266, 'jaw': 0.346, 'white': 0.281, 'smooth': 0.389}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.979, 'jaw': 0.959, 'white': 0.948, 'smooth': 0.987}
quantities {"eye": {"n": 6629, "spearman": 0.395, "mae": 0.0231, "pred_mean": 0.0078, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0104, "orig_pred_mean": 0.0004}, "jaw": {"n": 6630, "spearman": 0.106, "mae": 0.0171, "pred_mean": 0.0057, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0093, "orig_pred_mean": 0.0008}, "white": {"n": 6630, "spearman": -0.082, "mae": 0.4864, "pred_mean": 0.0602, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0092, "orig_pred_mean": 0.0072}, "smooth": {"n": 6630, "spearman": 0.243, "mae": 0.0937, "pred_mean": 0.1002, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0189, "orig_pred_mean": 0.0015}}
bars {"R1_balanced>=75": true, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 48.37 | 0.32 | 51.31 | 65.84 | 94.64 | 0.127 |
| EyeEnlarging_60 | 2209 | 32.78 | 0.45 | 66.77 | 73.57 | 97.51 | 0.31 |
| EyeEnlarging_90 | 2210 | 24.52 | 0.41 | 75.07 | 77.71 | 98.46 | 0.429 |
| FaceLifting_30 | 2210 | 51.04 | 0.32 | 48.64 | 64.5 | 88.94 | 0.284 |
| FaceLifting_60 | 2210 | 42.67 | 0.45 | 56.88 | 68.62 | 92.13 | 0.365 |
| FaceLifting_90 | 2210 | 35.07 | 0.41 | 64.52 | 72.44 | 95.07 | 0.452 |
| Whitening_30 | 2210 | 46.56 | 0.45 | 52.99 | 66.67 | 86.65 | 0.174 |
| Whitening_60 | 2210 | 34.8 | 0.59 | 64.62 | 72.49 | 88.94 | 0.396 |
| Whitening_90 | 2210 | 26.2 | 0.68 | 73.12 | 76.74 | 92.31 | 0.581 |
| Smoothing_30 | 2210 | 6.47 | 0.36 | 93.17 | 86.76 | 98.1 | 0.866 |
| Smoothing_60 | 2210 | 0.41 | 0.23 | 99.37 | 89.86 | 99.55 | 0.993 |
| Smoothing_90 | 2210 | 0.18 | 0.59 | 99.23 | 89.8 | 99.28 | 0.996 |

## FF++ / cross-dataset
{"indomain": {"real": 76.9, "fake": 92.25, "filter": 86.25}, "FA": 6.46, "real_to_filter": 14.06, "MISS": 0.59, "heldout13": {"filter": 77.05, "fake": 15.05, "paired_excess_pp": 62.99}, "cdf": {"auc": 0.887, "real_called_fake": 22.19}, "dfd": {"auc": 0.9543, "real_called_fake": 6.36}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
