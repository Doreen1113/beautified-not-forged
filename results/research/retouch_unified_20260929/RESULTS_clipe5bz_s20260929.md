# RU clipe5bz_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 8.6, 'fake': 0.5, 'filter': 90.9} | pooled {'n': 26519, 'to_real': 23.47, 'to_fake': 0.52, 'to_filter': 76.01, 'balanced_acc': 42.55, 'paired_rank': 37.6}
Eq.4 {'TP': {'eye': 0.355, 'jaw': 0.999, 'white': 0.006, 'smooth': 0.0}, 'TN_same_image': {'eye': 0.0, 'jaw': 0.598, 'white': 0.001, 'smooth': 0.0}, 'AC': {'eye': 0.0, 'jaw': 0.598, 'white': 0.001, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.697, 'jaw': 0.001, 'white': 0.996, 'smooth': 1.0}
quantities {"eye": {"n": 6629, "spearman": 0.16, "mae": 0.8965, "pred_mean": 0.9144, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3763, "orig_pred_mean": 0.8085}, "jaw": {"n": 6630, "spearman": 0.066, "mae": 0.6386, "pred_mean": 0.6577, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4612, "orig_pred_mean": 0.6298}, "white": {"n": 6630, "spearman": 0.007, "mae": 0.8583, "pred_mean": -0.3336, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.5992, "orig_pred_mean": -0.3157}, "smooth": {"n": 6630, "spearman": 0.161, "mae": 0.144, "pred_mean": 0.2507, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.7082, "orig_pred_mean": 0.1996}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 8.46 | 0.45 | 91.09 | 50.09 | 61.4 | 0.353 |
| EyeEnlarging_60 | 2209 | 7.47 | 0.45 | 92.08 | 50.59 | 66.7 | 0.35 |
| EyeEnlarging_90 | 2210 | 6.97 | 0.45 | 92.58 | 50.84 | 70.09 | 0.362 |
| FaceLifting_30 | 2210 | 10.27 | 0.41 | 89.32 | 49.21 | 49.32 | 0.999 |
| FaceLifting_60 | 2210 | 10.59 | 0.41 | 89.0 | 49.05 | 53.08 | 0.999 |
| FaceLifting_90 | 2210 | 11.09 | 0.41 | 88.51 | 48.8 | 53.03 | 0.999 |
| Whitening_30 | 2210 | 13.67 | 0.45 | 85.88 | 47.49 | 31.04 | 0.004 |
| Whitening_60 | 2210 | 18.69 | 0.45 | 80.86 | 44.98 | 25.45 | 0.005 |
| Whitening_90 | 2210 | 23.67 | 0.45 | 75.88 | 42.49 | 22.26 | 0.01 |
| Smoothing_30 | 2210 | 35.57 | 0.63 | 63.8 | 36.45 | 11.65 | 0.0 |
| Smoothing_60 | 2210 | 63.85 | 0.77 | 35.38 | 22.24 | 3.98 | 0.0 |
| Smoothing_90 | 2210 | 71.4 | 0.86 | 27.74 | 18.42 | 3.17 | 0.0 |

## FF++ / cross-dataset
{"indomain": {"real": 0.46, "fake": 82.69, "filter": 84.57}, "FA": 13.98, "real_to_filter": 86.25, "MISS": 0.5, "heldout13": {"filter": 73.63, "fake": 25.68, "paired_excess_pp": -12.62}, "cdf": {"auc": 0.8167, "real_called_fake": 17.78}, "dfd": {"auc": 0.9324, "real_called_fake": 4.29}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
