# RU clipe5x_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 81.49, 'fake': 0.68, 'filter': 17.83} | pooled {'n': 26519, 'to_real': 33.09, 'to_fake': 0.52, 'to_filter': 66.38, 'balanced_acc': 74.28, 'paired_rank': 94.06}
Eq.4 {'TP': {'eye': 0.264, 'jaw': 0.308, 'white': 0.391, 'smooth': 0.952}, 'TN_same_image': {'eye': 0.771, 'jaw': 0.898, 'white': 0.82, 'smooth': 0.447}, 'AC': {'eye': 0.25, 'jaw': 0.295, 'white': 0.322, 'smooth': 0.406}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.987, 'jaw': 0.972, 'white': 0.926, 'smooth': 0.99}
quantities {"eye": {"n": 6629, "spearman": 0.341, "mae": 0.0231, "pred_mean": 0.0079, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0118, "orig_pred_mean": 0.0013}, "jaw": {"n": 6630, "spearman": 0.097, "mae": 0.0157, "pred_mean": 0.007, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.01, "orig_pred_mean": 0.0028}, "white": {"n": 6630, "spearman": -0.178, "mae": 0.4912, "pred_mean": 0.0622, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0092, "orig_pred_mean": 0.0076}, "smooth": {"n": 6630, "spearman": 0.27, "mae": 0.0948, "pred_mean": 0.0964, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0178, "orig_pred_mean": -0.002}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 52.9 | 0.5 | 46.61 | 64.39 | 95.11 | 0.105 |
| EyeEnlarging_60 | 2209 | 37.53 | 0.45 | 62.02 | 72.09 | 97.24 | 0.28 |
| EyeEnlarging_90 | 2210 | 28.73 | 0.54 | 70.72 | 76.45 | 97.69 | 0.405 |
| FaceLifting_30 | 2210 | 58.73 | 0.54 | 40.72 | 61.45 | 85.95 | 0.223 |
| FaceLifting_60 | 2210 | 50.59 | 0.5 | 48.91 | 65.54 | 90.77 | 0.305 |
| FaceLifting_90 | 2210 | 41.99 | 0.41 | 57.6 | 69.89 | 93.39 | 0.396 |
| Whitening_30 | 2210 | 51.67 | 0.77 | 47.56 | 64.86 | 87.96 | 0.188 |
| Whitening_60 | 2210 | 38.14 | 0.54 | 61.31 | 71.74 | 89.82 | 0.399 |
| Whitening_90 | 2210 | 28.28 | 0.72 | 71.0 | 76.58 | 93.85 | 0.586 |
| Smoothing_30 | 2210 | 7.92 | 0.5 | 91.58 | 86.88 | 98.05 | 0.869 |
| Smoothing_60 | 2210 | 0.41 | 0.27 | 99.32 | 90.75 | 99.59 | 0.993 |
| Smoothing_90 | 2210 | 0.23 | 0.54 | 99.23 | 90.7 | 99.28 | 0.995 |

## FF++ / cross-dataset
{"indomain": {"real": 77.2, "fake": 90.35, "filter": 86.63}, "FA": 6.23, "real_to_filter": 14.67, "MISS": 0.53, "heldout13": {"filter": 74.24, "fake": 16.26, "paired_excess_pp": 59.57}, "cdf": {"auc": 0.8982, "real_called_fake": 24.11}, "dfd": {"auc": 0.9592, "real_called_fake": 4.24}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
