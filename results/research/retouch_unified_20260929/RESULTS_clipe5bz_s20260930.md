# RU clipe5bz_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 99.28, 'fake': 0.27, 'filter': 0.45} | pooled {'n': 26519, 'to_real': 99.27, 'to_fake': 0.29, 'to_filter': 0.43, 'balanced_acc': 49.99, 'paired_rank': 24.62}
Eq.4 {'TP': {'eye': 0.964, 'jaw': 0.667, 'white': 1.0, 'smooth': 0.985}, 'TN_same_image': {'eye': 0.0, 'jaw': 0.0, 'white': 0.0, 'smooth': 0.0}, 'AC': {'eye': 0.0, 'jaw': 0.0, 'white': 0.0, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.02, 'jaw': 0.428, 'white': 0.0, 'smooth': 0.002}
quantities {"eye": {"n": 6629, "spearman": -0.106, "mae": 0.3346, "pred_mean": -0.3081, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.2847, "orig_pred_mean": -0.2482}, "jaw": {"n": 6630, "spearman": 0.05, "mae": 0.2429, "pred_mean": -0.2225, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.3187, "orig_pred_mean": -0.237}, "white": {"n": 6630, "spearman": -0.271, "mae": 0.5015, "pred_mean": 0.5356, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.2281, "orig_pred_mean": 0.4984}, "smooth": {"n": 6630, "spearman": 0.167, "mae": 0.2192, "pred_mean": -0.02, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.4521, "orig_pred_mean": 0.1127}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 99.23 | 0.23 | 0.54 | 50.05 | 22.22 | 0.968 |
| EyeEnlarging_60 | 2209 | 99.23 | 0.23 | 0.54 | 50.05 | 20.76 | 0.962 |
| EyeEnlarging_90 | 2210 | 99.23 | 0.32 | 0.45 | 50.0 | 18.89 | 0.962 |
| FaceLifting_30 | 2210 | 99.28 | 0.32 | 0.41 | 49.98 | 21.2 | 0.651 |
| FaceLifting_60 | 2210 | 99.37 | 0.27 | 0.36 | 49.96 | 16.06 | 0.666 |
| FaceLifting_90 | 2210 | 99.46 | 0.23 | 0.32 | 49.93 | 13.14 | 0.684 |
| Whitening_30 | 2210 | 99.5 | 0.18 | 0.32 | 49.93 | 32.71 | 1.0 |
| Whitening_60 | 2210 | 99.55 | 0.23 | 0.23 | 49.89 | 34.37 | 1.0 |
| Whitening_90 | 2210 | 99.37 | 0.32 | 0.32 | 49.93 | 36.29 | 1.0 |
| Smoothing_30 | 2210 | 99.1 | 0.32 | 0.59 | 50.07 | 31.72 | 0.994 |
| Smoothing_60 | 2210 | 99.0 | 0.41 | 0.59 | 50.07 | 24.05 | 0.985 |
| Smoothing_90 | 2210 | 98.96 | 0.5 | 0.54 | 50.05 | 24.07 | 0.978 |

## FF++ / cross-dataset
{"indomain": {"real": 68.92, "fake": 83.58, "filter": 23.78}, "FA": 15.65, "real_to_filter": 14.67, "MISS": 5.19, "heldout13": {"filter": 28.19, "fake": 26.44, "paired_excess_pp": 13.52}, "cdf": {"auc": 0.8077, "real_called_fake": 18.05}, "dfd": {"auc": 0.9263, "real_called_fake": 5.83}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
