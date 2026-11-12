# RU clipe5bzsgh_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 94.89, 'fake': 0.54, 'filter': 4.57} | pooled {'n': 26519, 'to_real': 97.13, 'to_fake': 0.42, 'to_filter': 2.45, 'balanced_acc': 48.94, 'paired_rank': 29.44}
Eq.4 {'TP': {'eye': 0.914, 'jaw': 0.981, 'white': 0.638, 'smooth': 0.371}, 'TN_same_image': {'eye': 0.002, 'jaw': 0.005, 'white': 0.001, 'smooth': 0.0}, 'AC': {'eye': 0.002, 'jaw': 0.005, 'white': 0.001, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.102, 'jaw': 0.007, 'white': 0.36, 'smooth': 0.129}
quantities {"eye": {"n": 6629, "spearman": -0.163, "mae": 1.1476, "pred_mean": -1.1147, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.6181, "orig_pred_mean": -1.2113}, "jaw": {"n": 6630, "spearman": -0.069, "mae": 0.6425, "pred_mean": -0.6166, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.7467, "orig_pred_mean": -0.4965}, "white": {"n": 6630, "spearman": 0.064, "mae": 0.6779, "pred_mean": -0.0883, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.8793, "orig_pred_mean": 0.0889}, "smooth": {"n": 6630, "spearman": -0.165, "mae": 0.4493, "pred_mean": 0.4619, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.7263, "orig_pred_mean": 1.0896}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 96.43 | 0.41 | 3.17 | 49.3 | 29.41 | 0.915 |
| EyeEnlarging_60 | 2209 | 97.1 | 0.32 | 2.58 | 49.01 | 24.67 | 0.913 |
| EyeEnlarging_90 | 2210 | 97.74 | 0.32 | 1.95 | 48.69 | 21.95 | 0.914 |
| FaceLifting_30 | 2210 | 96.11 | 0.36 | 3.53 | 49.48 | 35.7 | 0.984 |
| FaceLifting_60 | 2210 | 96.65 | 0.27 | 3.08 | 49.25 | 32.53 | 0.981 |
| FaceLifting_90 | 2210 | 97.01 | 0.32 | 2.67 | 49.05 | 27.92 | 0.979 |
| Whitening_30 | 2210 | 96.88 | 0.36 | 2.76 | 49.1 | 32.31 | 0.647 |
| Whitening_60 | 2210 | 97.24 | 0.45 | 2.31 | 48.87 | 29.62 | 0.637 |
| Whitening_90 | 2210 | 97.15 | 0.63 | 2.22 | 48.82 | 30.95 | 0.63 |
| Smoothing_30 | 2210 | 96.97 | 0.5 | 2.53 | 48.98 | 33.26 | 0.553 |
| Smoothing_60 | 2210 | 98.05 | 0.54 | 1.4 | 48.42 | 27.74 | 0.295 |
| Smoothing_90 | 2210 | 98.19 | 0.59 | 1.22 | 48.33 | 27.19 | 0.265 |

## FF++ / cross-dataset
{"indomain": {"real": 74.47, "fake": 94.19, "filter": 18.84}, "FA": 9.42, "real_to_filter": 15.27, "MISS": 5.84, "heldout13": {"filter": 21.05, "fake": 18.09, "paired_excess_pp": 5.78}, "cdf": {"auc": 0.8696, "real_called_fake": 29.01}, "dfd": {"auc": 0.9565, "real_called_fake": 8.74}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
