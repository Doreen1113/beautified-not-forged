# RU clipe5bzl0_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 5.93, 'fake': 1.0, 'filter': 93.08} | pooled {'n': 26519, 'to_real': 7.57, 'to_fake': 0.76, 'to_filter': 91.67, 'balanced_acc': 49.3, 'paired_rank': 37.73}
Eq.4 {'TP': {'eye': 0.352, 'jaw': 0.991, 'white': 0.105, 'smooth': 0.043}, 'TN_same_image': {'eye': 0.009, 'jaw': 0.574, 'white': 0.01, 'smooth': 0.002}, 'AC': {'eye': 0.001, 'jaw': 0.567, 'white': 0.001, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.656, 'jaw': 0.01, 'white': 0.91, 'smooth': 0.98}
quantities {"eye": {"n": 6629, "spearman": 0.019, "mae": 0.2888, "pred_mean": 0.1155, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3489, "orig_pred_mean": 0.0876}, "jaw": {"n": 6630, "spearman": 0.028, "mae": 0.2273, "pred_mean": 0.0537, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.3615, "orig_pred_mean": 0.0457}, "white": {"n": 6630, "spearman": -0.001, "mae": 0.4884, "pred_mean": 0.2542, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.3445, "orig_pred_mean": 0.2458}, "smooth": {"n": 6630, "spearman": 0.004, "mae": 0.3599, "pred_mean": 0.4746, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.2777, "orig_pred_mean": 0.4813}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 7.06 | 0.95 | 91.99 | 49.46 | 35.02 | 0.358 |
| EyeEnlarging_60 | 2209 | 6.7 | 0.91 | 92.39 | 49.66 | 35.45 | 0.352 |
| EyeEnlarging_90 | 2210 | 7.01 | 0.72 | 92.26 | 49.59 | 37.26 | 0.347 |
| FaceLifting_30 | 2210 | 8.19 | 0.77 | 91.04 | 48.98 | 31.9 | 0.991 |
| FaceLifting_60 | 2210 | 8.28 | 0.81 | 90.9 | 48.91 | 31.61 | 0.99 |
| FaceLifting_90 | 2210 | 8.14 | 0.81 | 91.04 | 48.98 | 33.19 | 0.991 |
| Whitening_30 | 2210 | 7.56 | 0.63 | 91.81 | 49.36 | 35.95 | 0.097 |
| Whitening_60 | 2210 | 7.56 | 0.72 | 91.72 | 49.32 | 38.89 | 0.107 |
| Whitening_90 | 2210 | 7.06 | 0.68 | 92.26 | 49.59 | 42.87 | 0.11 |
| Smoothing_30 | 2210 | 7.42 | 0.59 | 91.99 | 49.46 | 42.1 | 0.023 |
| Smoothing_60 | 2210 | 7.6 | 0.5 | 91.9 | 49.41 | 43.98 | 0.043 |
| Smoothing_90 | 2210 | 8.28 | 1.0 | 90.72 | 48.82 | 44.57 | 0.062 |

## FF++ / cross-dataset
{"indomain": {"real": 5.85, "fake": 97.12, "filter": 77.81}, "FA": 15.27, "real_to_filter": 78.57, "MISS": 0.22, "heldout13": {"filter": 69.45, "fake": 22.8, "paired_excess_pp": -9.12}, "cdf": {"auc": 0.8995, "real_called_fake": 34.2}, "dfd": {"auc": 0.9603, "real_called_fake": 10.86}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
