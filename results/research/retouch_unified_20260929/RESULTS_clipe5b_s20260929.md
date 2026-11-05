# RU clipe5b_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 3.53, 'fake': 0.77, 'filter': 95.7} | pooled {'n': 26519, 'to_real': 4.45, 'to_fake': 0.57, 'to_filter': 94.98, 'balanced_acc': 49.64, 'paired_rank': 37.29}
Eq.4 {'TP': {'eye': 0.068, 'jaw': 0.981, 'white': 0.241, 'smooth': 0.017}, 'TN_same_image': {'eye': 0.016, 'jaw': 0.705, 'white': 0.018, 'smooth': 0.006}, 'AC': {'eye': 0.001, 'jaw': 0.693, 'white': 0.007, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.932, 'jaw': 0.02, 'white': 0.776, 'smooth': 0.985}
quantities {"eye": {"n": 6629, "spearman": 0.046, "mae": 0.3002, "pred_mean": 0.1634, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3761, "orig_pred_mean": 0.1282}, "jaw": {"n": 6630, "spearman": 0.032, "mae": 0.3037, "pred_mean": 0.2377, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.3657, "orig_pred_mean": 0.2177}, "white": {"n": 6630, "spearman": -0.013, "mae": 0.4859, "pred_mean": 0.3286, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.3527, "orig_pred_mean": 0.3163}, "smooth": {"n": 6630, "spearman": -0.02, "mae": 0.2982, "pred_mean": 0.3783, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3186, "orig_pred_mean": 0.3965}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 3.85 | 0.5 | 95.66 | 49.98 | 38.1 | 0.067 |
| EyeEnlarging_60 | 2209 | 3.89 | 0.45 | 95.65 | 49.98 | 39.47 | 0.068 |
| EyeEnlarging_90 | 2210 | 3.76 | 0.45 | 95.79 | 50.05 | 40.02 | 0.068 |
| FaceLifting_30 | 2210 | 4.25 | 0.63 | 95.11 | 49.71 | 33.03 | 0.982 |
| FaceLifting_60 | 2210 | 4.57 | 0.59 | 94.84 | 49.57 | 33.89 | 0.981 |
| FaceLifting_90 | 2210 | 4.48 | 0.59 | 94.93 | 49.62 | 34.59 | 0.981 |
| Whitening_30 | 2210 | 4.71 | 0.41 | 94.89 | 49.59 | 29.82 | 0.24 |
| Whitening_60 | 2210 | 5.43 | 0.72 | 93.85 | 49.07 | 27.38 | 0.242 |
| Whitening_90 | 2210 | 6.52 | 0.68 | 92.81 | 48.55 | 28.01 | 0.242 |
| Smoothing_30 | 2210 | 3.71 | 0.54 | 95.75 | 50.02 | 48.48 | 0.012 |
| Smoothing_60 | 2210 | 3.71 | 0.59 | 95.7 | 50.0 | 48.35 | 0.02 |
| Smoothing_90 | 2210 | 4.52 | 0.63 | 94.84 | 49.57 | 46.29 | 0.021 |

## FF++ / cross-dataset
{"indomain": {"real": 3.5, "fake": 95.72, "filter": 83.97}, "FA": 11.7, "real_to_filter": 84.42, "MISS": 0.47, "heldout13": {"filter": 73.4, "fake": 20.97, "paired_excess_pp": -11.02}, "cdf": {"auc": 0.9138, "real_called_fake": 29.06}, "dfd": {"auc": 0.9667, "real_called_fake": 6.94}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
