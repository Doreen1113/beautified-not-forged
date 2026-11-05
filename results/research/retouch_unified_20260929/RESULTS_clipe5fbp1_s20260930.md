# RU clipe5fbp1_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 53.76, 'fake': 11.31, 'filter': 34.93} | pooled {'n': 26519, 'to_real': 53.26, 'to_fake': 13.51, 'to_filter': 33.23, 'balanced_acc': 49.15, 'paired_rank': 46.45}
Eq.4 {'TP': {'eye': 0.841, 'jaw': 0.538, 'white': 0.682, 'smooth': 0.655}, 'TN_same_image': {'eye': 0.038, 'jaw': 0.022, 'white': 0.03, 'smooth': 0.028}, 'AC': {'eye': 0.029, 'jaw': 0.013, 'white': 0.018, 'smooth': 0.018}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.175, 'jaw': 0.488, 'white': 0.29, 'smooth': 0.293}
quantities {"eye": {"n": 6629, "spearman": -0.016, "mae": 0.5482, "pred_mean": -0.4357, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.5117, "orig_pred_mean": -0.4534}, "jaw": {"n": 6630, "spearman": -0.022, "mae": 0.355, "pred_mean": -0.1572, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.5704, "orig_pred_mean": -0.1534}, "white": {"n": 6630, "spearman": -0.037, "mae": 0.6237, "pred_mean": 0.7234, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4263, "orig_pred_mean": 0.7379}, "smooth": {"n": 6630, "spearman": -0.026, "mae": 0.5163, "pred_mean": -0.2893, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.6195, "orig_pred_mean": -0.3052}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 53.98 | 11.63 | 34.39 | 49.73 | 50.41 | 0.84 |
| EyeEnlarging_60 | 2209 | 54.1 | 11.82 | 34.09 | 49.58 | 48.55 | 0.843 |
| EyeEnlarging_90 | 2210 | 54.12 | 12.67 | 33.21 | 49.14 | 46.88 | 0.84 |
| FaceLifting_30 | 2210 | 54.84 | 11.45 | 33.71 | 49.39 | 47.81 | 0.532 |
| FaceLifting_60 | 2210 | 53.8 | 12.26 | 33.94 | 49.5 | 45.97 | 0.538 |
| FaceLifting_90 | 2210 | 53.67 | 13.35 | 32.99 | 49.03 | 45.29 | 0.543 |
| Whitening_30 | 2210 | 54.3 | 12.49 | 33.21 | 49.14 | 47.17 | 0.702 |
| Whitening_60 | 2210 | 53.35 | 12.13 | 34.52 | 49.8 | 49.21 | 0.681 |
| Whitening_90 | 2210 | 50.63 | 12.9 | 36.47 | 50.77 | 52.4 | 0.664 |
| Smoothing_30 | 2210 | 53.26 | 16.97 | 29.77 | 47.42 | 36.7 | 0.689 |
| Smoothing_60 | 2210 | 52.62 | 16.38 | 31.0 | 48.03 | 42.44 | 0.638 |
| Smoothing_90 | 2210 | 50.41 | 18.14 | 31.45 | 48.26 | 44.62 | 0.638 |

## FF++ / cross-dataset
{"indomain": {"real": 28.95, "fake": 96.42, "filter": 69.98}, "FA": 6.61, "real_to_filter": 58.28, "MISS": 5.34, "heldout13": {"filter": 63.22, "fake": 14.59, "paired_excess_pp": 4.94}, "cdf": {"auc": 0.8701, "real_called_fake": 27.34}, "dfd": {"auc": 0.9493, "real_called_fake": 9.33}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
