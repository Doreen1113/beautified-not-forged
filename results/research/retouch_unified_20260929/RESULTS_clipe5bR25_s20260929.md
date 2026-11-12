# RU clipe5bR25_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 98.37, 'fake': 1.04, 'filter': 0.59} | pooled {'n': 26519, 'to_real': 98.5, 'to_fake': 0.83, 'to_filter': 0.67, 'balanced_acc': 50.04, 'paired_rank': 34.19}
Eq.4 {'TP': {'eye': 0.759, 'jaw': 0.542, 'white': 1.0, 'smooth': 0.415}, 'TN_same_image': {'eye': 0.0, 'jaw': 0.0, 'white': 0.071, 'smooth': 0.0}, 'AC': {'eye': 0.0, 'jaw': 0.0, 'white': 0.071, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.332, 'jaw': 0.374, 'white': 0.0, 'smooth': 0.784}
quantities {"eye": {"n": 6629, "spearman": -0.028, "mae": 0.2165, "pred_mean": 0.164, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.357, "orig_pred_mean": 0.1462}, "jaw": {"n": 6630, "spearman": 0.019, "mae": 0.4938, "pred_mean": -0.4687, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.27, "orig_pred_mean": -0.4617}, "white": {"n": 6630, "spearman": 0.025, "mae": 0.7796, "pred_mean": -0.235, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.3262, "orig_pred_mean": -0.2951}, "smooth": {"n": 6630, "spearman": 0.191, "mae": 0.1909, "pred_mean": 0.2401, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3327, "orig_pred_mean": 0.2346}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 98.46 | 0.9 | 0.63 | 50.02 | 31.86 | 0.755 |
| EyeEnlarging_60 | 2209 | 98.46 | 0.86 | 0.68 | 50.04 | 30.06 | 0.76 |
| EyeEnlarging_90 | 2210 | 98.42 | 0.81 | 0.77 | 50.09 | 30.7 | 0.763 |
| FaceLifting_30 | 2210 | 98.6 | 0.95 | 0.45 | 49.93 | 34.37 | 0.546 |
| FaceLifting_60 | 2210 | 98.64 | 0.95 | 0.41 | 49.91 | 36.45 | 0.538 |
| FaceLifting_90 | 2210 | 98.6 | 0.9 | 0.5 | 49.95 | 38.17 | 0.542 |
| Whitening_30 | 2210 | 98.64 | 0.95 | 0.41 | 49.91 | 39.64 | 0.999 |
| Whitening_60 | 2210 | 98.46 | 0.9 | 0.63 | 50.02 | 43.44 | 1.0 |
| Whitening_90 | 2210 | 98.05 | 1.0 | 0.95 | 50.18 | 44.19 | 1.0 |
| Smoothing_30 | 2210 | 98.42 | 0.63 | 0.95 | 50.18 | 36.33 | 0.372 |
| Smoothing_60 | 2210 | 98.78 | 0.41 | 0.81 | 50.11 | 24.16 | 0.434 |
| Smoothing_90 | 2210 | 98.46 | 0.63 | 0.9 | 50.16 | 20.9 | 0.439 |

## FF++ / cross-dataset
{"indomain": {"real": 85.11, "fake": 95.4, "filter": 1.44}, "FA": 11.85, "real_to_filter": 1.82, "MISS": 8.44, "heldout13": {"filter": 1.6, "fake": 19.68, "paired_excess_pp": -0.22}, "cdf": {"auc": 0.899, "real_called_fake": 38.42}, "dfd": {"auc": 0.9601, "real_called_fake": 13.35}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
