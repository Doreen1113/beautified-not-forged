# RU clipe_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 72.99, 'fake': 0.32, 'filter': 26.7} | pooled {'n': 26519, 'to_real': 26.22, 'to_fake': 0.2, 'to_filter': 73.58, 'balanced_acc': 73.44, 'paired_rank': 95.14}
Eq.4 {'TP': {'eye': 0.182, 'jaw': 0.321, 'white': 0.366, 'smooth': 0.925}, 'TN_same_image': {'eye': 0.753, 'jaw': 0.905, 'white': 0.798, 'smooth': 0.434}, 'AC': {'eye': 0.171, 'jaw': 0.305, 'white': 0.297, 'smooth': 0.37}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.994, 'jaw': 0.965, 'white': 0.924, 'smooth': 0.991}
quantities {"eye": {"n": 6629, "spearman": 0.365, "mae": 0.0271, "pred_mean": 0.0022, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0176, "orig_pred_mean": -0.0078}, "jaw": {"n": 6630, "spearman": 0.096, "mae": 0.0127, "pred_mean": 0.0132, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0166, "orig_pred_mean": 0.0088}, "white": {"n": 6630, "spearman": -0.175, "mae": 0.4907, "pred_mean": 0.056, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.015, "orig_pred_mean": 0.0088}, "smooth": {"n": 6630, "spearman": 0.074, "mae": 0.0984, "pred_mean": 0.1141, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0263, "orig_pred_mean": 0.01}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 44.66 | 0.27 | 55.07 | 64.18 | 95.77 | 0.046 |
| EyeEnlarging_60 | 2209 | 32.19 | 0.18 | 67.63 | 70.47 | 98.14 | 0.177 |
| EyeEnlarging_90 | 2210 | 23.71 | 0.14 | 76.15 | 74.73 | 98.73 | 0.323 |
| FaceLifting_30 | 2210 | 47.29 | 0.27 | 52.44 | 62.87 | 89.98 | 0.246 |
| FaceLifting_60 | 2210 | 39.46 | 0.27 | 60.27 | 66.79 | 94.12 | 0.315 |
| FaceLifting_90 | 2210 | 30.59 | 0.32 | 69.1 | 71.2 | 96.06 | 0.402 |
| Whitening_30 | 2210 | 40.9 | 0.18 | 58.91 | 66.11 | 87.85 | 0.175 |
| Whitening_60 | 2210 | 30.05 | 0.27 | 69.68 | 71.49 | 90.54 | 0.36 |
| Whitening_90 | 2210 | 20.23 | 0.23 | 79.55 | 76.42 | 94.25 | 0.562 |
| Smoothing_30 | 2210 | 5.16 | 0.05 | 94.8 | 84.05 | 97.06 | 0.801 |
| Smoothing_60 | 2210 | 0.32 | 0.0 | 99.68 | 86.49 | 99.68 | 0.986 |
| Smoothing_90 | 2210 | 0.14 | 0.23 | 99.64 | 86.47 | 99.5 | 0.989 |

## FF++ / cross-dataset
{"indomain": {"real": 87.23, "fake": 92.23, "filter": 86.93}, "FA": 4.1, "real_to_filter": 9.35, "MISS": 0.53, "heldout13": {"filter": 63.75, "fake": 12.16, "paired_excess_pp": 54.4}, "cdf": {"auc": 0.8831, "real_called_fake": 9.32}, "dfd": {"auc": 0.9534, "real_called_fake": 0.58}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": true, "D2_heldout_excess>=30": true}}
