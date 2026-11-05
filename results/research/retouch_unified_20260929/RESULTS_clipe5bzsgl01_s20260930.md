# RU clipe5bzsgl01_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 93.12, 'fake': 0.59, 'filter': 6.29} | pooled {'n': 26519, 'to_real': 83.32, 'to_fake': 0.55, 'to_filter': 16.13, 'balanced_acc': 54.92, 'paired_rank': 65.46}
Eq.4 {'TP': {'eye': 0.552, 'jaw': 0.594, 'white': 0.805, 'smooth': 0.1}, 'TN_same_image': {'eye': 0.03, 'jaw': 0.036, 'white': 0.097, 'smooth': 0.061}, 'AC': {'eye': 0.02, 'jaw': 0.021, 'white': 0.084, 'smooth': 0.001}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.55, 'jaw': 0.377, 'white': 0.11, 'smooth': 0.437}
quantities {"eye": {"n": 6629, "spearman": -0.006, "mae": 0.4998, "pred_mean": -0.4573, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.609, "orig_pred_mean": -0.4168}, "jaw": {"n": 6630, "spearman": 0.028, "mae": 0.2806, "pred_mean": -0.0102, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.6967, "orig_pred_mean": -0.0871}, "white": {"n": 6630, "spearman": -0.173, "mae": 0.8175, "pred_mean": 1.1577, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4047, "orig_pred_mean": 1.1701}, "smooth": {"n": 6630, "spearman": 0.012, "mae": 0.3165, "pred_mean": 0.2372, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.8149, "orig_pred_mean": -0.3201}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 94.12 | 0.45 | 5.43 | 49.57 | 49.84 | 0.538 |
| EyeEnlarging_60 | 2209 | 94.57 | 0.41 | 5.02 | 49.37 | 49.43 | 0.556 |
| EyeEnlarging_90 | 2210 | 94.89 | 0.5 | 4.62 | 49.16 | 49.37 | 0.561 |
| FaceLifting_30 | 2210 | 94.3 | 0.45 | 5.25 | 49.48 | 47.4 | 0.605 |
| FaceLifting_60 | 2210 | 94.89 | 0.45 | 4.66 | 49.19 | 46.15 | 0.594 |
| FaceLifting_90 | 2210 | 95.11 | 0.41 | 4.48 | 49.09 | 44.59 | 0.582 |
| Whitening_30 | 2210 | 92.81 | 0.45 | 6.74 | 50.23 | 68.55 | 0.835 |
| Whitening_60 | 2210 | 89.86 | 0.45 | 9.68 | 51.7 | 76.63 | 0.813 |
| Whitening_90 | 2210 | 84.03 | 0.63 | 15.34 | 54.52 | 83.53 | 0.768 |
| Smoothing_30 | 2210 | 75.11 | 0.68 | 24.21 | 58.96 | 83.21 | 0.192 |
| Smoothing_60 | 2210 | 46.92 | 0.77 | 52.31 | 73.01 | 93.53 | 0.061 |
| Smoothing_90 | 2210 | 43.21 | 0.95 | 55.84 | 74.77 | 93.26 | 0.047 |

## FF++ / cross-dataset
{"indomain": {"real": 68.62, "fake": 93.93, "filter": 47.49}, "FA": 13.07, "real_to_filter": 18.39, "MISS": 1.31, "heldout13": {"filter": 57.29, "fake": 21.5, "paired_excess_pp": 38.9}, "cdf": {"auc": 0.8641, "real_called_fake": 24.34}, "dfd": {"auc": 0.9525, "real_called_fake": 4.4}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
