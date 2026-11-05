# RU clipe5bzsgG_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 96.06, 'fake': 0.54, 'filter': 3.39} | pooled {'n': 26519, 'to_real': 95.93, 'to_fake': 0.51, 'to_filter': 3.56, 'balanced_acc': 50.08, 'paired_rank': 45.3}
Eq.4 {'TP': {'eye': 0.253, 'jaw': 0.862, 'white': 0.623, 'smooth': 0.924}, 'TN_same_image': {'eye': 0.003, 'jaw': 0.005, 'white': 0.007, 'smooth': 0.027}, 'AC': {'eye': 0.0, 'jaw': 0.002, 'white': 0.003, 'smooth': 0.021}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.744, 'jaw': 0.185, 'white': 0.361, 'smooth': 0.01}
quantities {"eye": {"n": 6629, "spearman": -0.044, "mae": 0.5847, "pred_mean": -0.5444, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.6329, "orig_pred_mean": -0.5302}, "jaw": {"n": 6630, "spearman": 0.005, "mae": 0.5301, "pred_mean": -0.4983, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.646, "orig_pred_mean": -0.5209}, "white": {"n": 6630, "spearman": -0.035, "mae": 0.6435, "pred_mean": -0.0364, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.7306, "orig_pred_mean": -0.0295}, "smooth": {"n": 6630, "spearman": -0.1, "mae": 0.7162, "pred_mean": 0.8755, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.4989, "orig_pred_mean": 1.0705}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 96.29 | 0.54 | 3.17 | 49.89 | 39.71 | 0.257 |
| EyeEnlarging_60 | 2209 | 96.42 | 0.63 | 2.94 | 49.78 | 36.26 | 0.252 |
| EyeEnlarging_90 | 2210 | 96.52 | 0.68 | 2.81 | 49.71 | 33.89 | 0.249 |
| FaceLifting_30 | 2210 | 96.06 | 0.5 | 3.44 | 50.02 | 45.79 | 0.855 |
| FaceLifting_60 | 2210 | 95.84 | 0.63 | 3.53 | 50.07 | 46.43 | 0.862 |
| FaceLifting_90 | 2210 | 96.06 | 0.5 | 3.44 | 50.02 | 43.71 | 0.87 |
| Whitening_30 | 2210 | 95.88 | 0.5 | 3.62 | 50.11 | 56.33 | 0.624 |
| Whitening_60 | 2210 | 95.34 | 0.63 | 4.03 | 50.32 | 57.6 | 0.621 |
| Whitening_90 | 2210 | 94.8 | 0.5 | 4.71 | 50.66 | 60.52 | 0.624 |
| Smoothing_30 | 2210 | 95.93 | 0.45 | 3.62 | 50.11 | 36.95 | 0.969 |
| Smoothing_60 | 2210 | 96.11 | 0.23 | 3.67 | 50.14 | 40.95 | 0.911 |
| Smoothing_90 | 2210 | 95.97 | 0.32 | 3.71 | 50.16 | 45.43 | 0.893 |

## FF++ / cross-dataset
{"indomain": {"real": 66.26, "fake": 76.89, "filter": 36.32}, "FA": 8.89, "real_to_filter": 29.1, "MISS": 13.38, "heldout13": {"filter": 31.91, "fake": 12.69, "paired_excess_pp": 2.81}, "cdf": {"auc": 0.7951, "real_called_fake": 14.87}, "dfd": {"auc": 0.9392, "real_called_fake": 4.19}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
