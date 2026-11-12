# RU clipe5bzl03_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 18.33, 'fake': 0.5, 'filter': 81.18} | pooled {'n': 26519, 'to_real': 32.51, 'to_fake': 0.57, 'to_filter': 66.91, 'balanced_acc': 42.87, 'paired_rank': 35.17}
Eq.4 {'TP': {'eye': 0.176, 'jaw': 1.0, 'white': 0.008, 'smooth': 0.0}, 'TN_same_image': {'eye': 0.0, 'jaw': 0.85, 'white': 0.0, 'smooth': 0.0}, 'AC': {'eye': 0.0, 'jaw': 0.85, 'white': 0.0, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.895, 'jaw': 0.0, 'white': 0.998, 'smooth': 1.0}
quantities {"eye": {"n": 6629, "spearman": 0.087, "mae": 0.9829, "pred_mean": 1.0006, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.1801, "orig_pred_mean": 0.9124}, "jaw": {"n": 6630, "spearman": 0.005, "mae": 0.2494, "pred_mean": 0.2635, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4263, "orig_pred_mean": 0.2579}, "white": {"n": 6630, "spearman": -0.028, "mae": 0.6451, "pred_mean": -0.1093, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4948, "orig_pred_mean": -0.1105}, "smooth": {"n": 6630, "spearman": 0.21, "mae": 0.1876, "pred_mean": 0.0709, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.49, "orig_pred_mean": -0.0773}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 22.9 | 0.45 | 76.65 | 47.74 | 48.82 | 0.145 |
| EyeEnlarging_60 | 2209 | 22.5 | 0.45 | 77.05 | 47.93 | 49.37 | 0.176 |
| EyeEnlarging_90 | 2210 | 21.99 | 0.5 | 77.51 | 48.17 | 51.4 | 0.208 |
| FaceLifting_30 | 2210 | 27.24 | 0.36 | 72.4 | 45.61 | 36.11 | 1.0 |
| FaceLifting_60 | 2210 | 30.45 | 0.32 | 69.23 | 44.03 | 32.9 | 1.0 |
| FaceLifting_90 | 2210 | 34.03 | 0.27 | 65.7 | 42.26 | 29.14 | 1.0 |
| Whitening_30 | 2210 | 25.97 | 0.45 | 73.57 | 46.2 | 33.26 | 0.005 |
| Whitening_60 | 2210 | 26.43 | 0.45 | 73.12 | 45.97 | 35.59 | 0.006 |
| Whitening_90 | 2210 | 25.61 | 0.81 | 73.57 | 46.2 | 40.48 | 0.012 |
| Smoothing_30 | 2210 | 30.18 | 0.81 | 69.0 | 43.91 | 37.04 | 0.0 |
| Smoothing_60 | 2210 | 57.29 | 0.9 | 41.81 | 30.31 | 16.47 | 0.0 |
| Smoothing_90 | 2210 | 65.57 | 1.09 | 33.35 | 26.08 | 11.52 | 0.0 |

## FF++ / cross-dataset
{"indomain": {"real": 3.19, "fake": 90.52, "filter": 76.44}, "FA": 14.97, "real_to_filter": 82.52, "MISS": 1.78, "heldout13": {"filter": 64.82, "fake": 27.81, "paired_excess_pp": -17.7}, "cdf": {"auc": 0.8472, "real_called_fake": 23.1}, "dfd": {"auc": 0.9512, "real_called_fake": 6.52}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
