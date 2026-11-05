# RU clipe5fbg0o_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 61.67, 'fake': 13.39, 'filter': 24.93} | pooled {'n': 26519, 'to_real': 63.16, 'to_fake': 12.74, 'to_filter': 24.1, 'balanced_acc': 49.58, 'paired_rank': 49.96}
Eq.4 {'TP': {'eye': 0.827, 'jaw': 0.533, 'white': 0.762, 'smooth': 0.647}, 'TN_same_image': {'eye': 0.027, 'jaw': 0.013, 'white': 0.022, 'smooth': 0.014}, 'AC': {'eye': 0.023, 'jaw': 0.007, 'white': 0.017, 'smooth': 0.009}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.181, 'jaw': 0.482, 'white': 0.213, 'smooth': 0.263}
quantities {"eye": {"n": 6629, "spearman": -0.064, "mae": 0.5756, "pred_mean": -0.4717, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4639, "orig_pred_mean": -0.4753}, "jaw": {"n": 6630, "spearman": -0.0, "mae": 0.3913, "pred_mean": -0.2089, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.5135, "orig_pred_mean": -0.2164}, "white": {"n": 6630, "spearman": -0.043, "mae": 0.5587, "pred_mean": 0.4449, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4693, "orig_pred_mean": 0.4096}, "smooth": {"n": 6630, "spearman": -0.038, "mae": 0.6145, "pred_mean": -0.3968, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.557, "orig_pred_mean": -0.402}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 62.49 | 12.17 | 25.34 | 50.2 | 54.77 | 0.824 |
| EyeEnlarging_60 | 2209 | 62.43 | 12.9 | 24.67 | 49.87 | 52.33 | 0.83 |
| EyeEnlarging_90 | 2210 | 61.99 | 13.85 | 24.16 | 49.62 | 49.1 | 0.826 |
| FaceLifting_30 | 2210 | 63.89 | 11.58 | 24.52 | 49.8 | 52.04 | 0.53 |
| FaceLifting_60 | 2210 | 63.3 | 12.62 | 24.07 | 49.57 | 48.12 | 0.532 |
| FaceLifting_90 | 2210 | 63.17 | 13.67 | 23.17 | 49.12 | 45.84 | 0.538 |
| Whitening_30 | 2210 | 63.76 | 11.76 | 24.48 | 49.77 | 54.19 | 0.777 |
| Whitening_60 | 2210 | 63.85 | 11.81 | 24.34 | 49.71 | 52.96 | 0.767 |
| Whitening_90 | 2210 | 62.49 | 12.4 | 25.11 | 50.09 | 53.08 | 0.743 |
| Smoothing_30 | 2210 | 64.21 | 12.17 | 23.62 | 49.34 | 44.66 | 0.666 |
| Smoothing_60 | 2210 | 64.84 | 12.35 | 22.81 | 48.94 | 46.04 | 0.643 |
| Smoothing_90 | 2210 | 61.54 | 15.61 | 22.85 | 48.96 | 46.38 | 0.633 |

## FF++ / cross-dataset
{"indomain": {"real": 38.83, "fake": 93.93, "filter": 50.08}, "FA": 14.44, "real_to_filter": 52.05, "MISS": 4.5, "heldout13": {"filter": 44.45, "fake": 24.24, "paired_excess_pp": -7.6}, "cdf": {"auc": 0.8822, "real_called_fake": 20.82}, "dfd": {"auc": 0.9442, "real_called_fake": 6.68}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
