# RU ru3_effb4_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 76.65, 'fake': 0.41, 'filter': 22.94} | pooled {'n': 26519, 'to_real': 30.87, 'to_fake': 0.34, 'to_filter': 68.79, 'balanced_acc': 72.92, 'paired_rank': 94.86}
Eq.4 {'TP': {'eye': 0.231, 'jaw': 0.295, 'white': 0.276, 'smooth': 0.952}, 'TN_same_image': {'eye': 0.791, 'jaw': 0.912, 'white': 0.754, 'smooth': 0.295}, 'AC': {'eye': 0.204, 'jaw': 0.26, 'white': 0.166, 'smooth': 0.26}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.989, 'jaw': 0.959, 'white': 0.955, 'smooth': 0.985}
quantities {"eye": {"n": 6629, "spearman": 0.468, "mae": 0.0258, "pred_mean": 0.003, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0081, "orig_pred_mean": 0.0002}, "jaw": {"n": 6630, "spearman": 0.172, "mae": 0.0173, "pred_mean": 0.0034, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0069, "orig_pred_mean": 0.0007}, "white": {"n": 6630, "spearman": -0.148, "mae": 0.4983, "pred_mean": 0.053, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0034, "orig_pred_mean": 0.0118}, "smooth": {"n": 6630, "spearman": 0.524, "mae": 0.0865, "pred_mean": 0.1023, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0216, "orig_pred_mean": 0.0006}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 46.92 | 0.36 | 52.71 | 64.89 | 98.03 | 0.09 |
| EyeEnlarging_60 | 2209 | 34.0 | 0.32 | 65.69 | 71.37 | 99.12 | 0.236 |
| EyeEnlarging_90 | 2210 | 25.79 | 0.27 | 73.94 | 75.5 | 99.48 | 0.367 |
| FaceLifting_30 | 2210 | 53.62 | 0.36 | 46.02 | 61.54 | 87.69 | 0.231 |
| FaceLifting_60 | 2210 | 47.1 | 0.32 | 52.58 | 64.82 | 91.83 | 0.295 |
| FaceLifting_90 | 2210 | 41.18 | 0.32 | 58.51 | 67.78 | 94.1 | 0.361 |
| Whitening_30 | 2210 | 49.0 | 0.32 | 50.68 | 63.87 | 87.74 | 0.129 |
| Whitening_60 | 2210 | 38.87 | 0.54 | 60.59 | 68.82 | 90.18 | 0.273 |
| Whitening_90 | 2210 | 29.46 | 0.5 | 70.05 | 73.55 | 91.81 | 0.426 |
| Smoothing_30 | 2210 | 3.98 | 0.23 | 95.79 | 86.43 | 99.28 | 0.868 |
| Smoothing_60 | 2210 | 0.27 | 0.14 | 99.59 | 88.33 | 99.77 | 0.992 |
| Smoothing_90 | 2210 | 0.23 | 0.45 | 99.32 | 88.19 | 99.32 | 0.996 |

## FF++ / cross-dataset
{"indomain": {"real": 79.79, "fake": 93.68, "filter": 74.92}, "FA": 10.41, "real_to_filter": 13.98, "MISS": 0.59, "heldout13": {"filter": 44.38, "fake": 16.64, "paired_excess_pp": 30.4}, "cdf": {"auc": 0.832, "real_called_fake": 29.34}, "dfd": {"auc": 0.9379, "real_called_fake": 7.15}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
