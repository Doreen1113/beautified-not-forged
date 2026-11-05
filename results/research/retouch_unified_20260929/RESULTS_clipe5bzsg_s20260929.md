# RU clipe5bzsg_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 99.37, 'fake': 0.14, 'filter': 0.5} | pooled {'n': 26519, 'to_real': 98.73, 'to_fake': 0.17, 'to_filter': 1.1, 'balanced_acc': 50.3, 'paired_rank': 53.92}
Eq.4 {'TP': {'eye': 0.874, 'jaw': 0.398, 'white': 0.994, 'smooth': 0.842}, 'TN_same_image': {'eye': 0.0, 'jaw': 0.0, 'white': 0.004, 'smooth': 0.0}, 'AC': {'eye': 0.0, 'jaw': 0.0, 'white': 0.004, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.135, 'jaw': 0.68, 'white': 0.001, 'smooth': 0.171}
quantities {"eye": {"n": 6629, "spearman": -0.04, "mae": 0.2548, "pred_mean": 0.0014, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.2934, "orig_pred_mean": -0.0186}, "jaw": {"n": 6630, "spearman": -0.004, "mae": 0.2611, "pred_mean": 0.0566, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.2854, "orig_pred_mean": 0.1005}, "white": {"n": 6630, "spearman": 0.168, "mae": 0.491, "pred_mean": 0.2648, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.2801, "orig_pred_mean": 0.2477}, "smooth": {"n": 6630, "spearman": 0.077, "mae": 0.2751, "pred_mean": 0.1899, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3075, "orig_pred_mean": -0.2156}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 99.5 | 0.14 | 0.36 | 49.93 | 36.74 | 0.873 |
| EyeEnlarging_60 | 2209 | 99.5 | 0.14 | 0.36 | 49.93 | 34.43 | 0.875 |
| EyeEnlarging_90 | 2210 | 99.5 | 0.14 | 0.36 | 49.93 | 33.1 | 0.875 |
| FaceLifting_30 | 2210 | 99.32 | 0.18 | 0.5 | 50.0 | 42.06 | 0.377 |
| FaceLifting_60 | 2210 | 99.41 | 0.18 | 0.41 | 49.95 | 41.4 | 0.398 |
| FaceLifting_90 | 2210 | 99.41 | 0.14 | 0.45 | 49.98 | 42.81 | 0.418 |
| Whitening_30 | 2210 | 99.19 | 0.14 | 0.68 | 50.09 | 58.05 | 0.996 |
| Whitening_60 | 2210 | 99.14 | 0.14 | 0.72 | 50.11 | 64.34 | 0.994 |
| Whitening_90 | 2210 | 98.91 | 0.14 | 0.95 | 50.23 | 69.55 | 0.991 |
| Smoothing_30 | 2210 | 98.91 | 0.18 | 0.9 | 50.2 | 62.42 | 0.851 |
| Smoothing_60 | 2210 | 96.61 | 0.32 | 3.08 | 51.29 | 79.19 | 0.844 |
| Smoothing_90 | 2210 | 95.34 | 0.27 | 4.39 | 51.94 | 82.9 | 0.831 |

## FF++ / cross-dataset
{"indomain": {"real": 88.45, "fake": 81.98, "filter": 6.16}, "FA": 11.32, "real_to_filter": 3.42, "MISS": 8.34, "heldout13": {"filter": 5.09, "fake": 21.81, "paired_excess_pp": 1.67}, "cdf": {"auc": 0.8496, "real_called_fake": 13.51}, "dfd": {"auc": 0.9606, "real_called_fake": 2.49}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
