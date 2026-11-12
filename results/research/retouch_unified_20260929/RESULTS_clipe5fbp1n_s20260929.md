# RU clipe5fbp1n_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 6.56, 'fake': 12.85, 'filter': 80.59} | pooled {'n': 26519, 'to_real': 6.86, 'to_fake': 23.84, 'to_filter': 69.31, 'balanced_acc': 44.36, 'paired_rank': 40.32}
Eq.4 {'TP': {'eye': 0.106, 'jaw': 0.933, 'white': 0.184, 'smooth': 0.052}, 'TN_same_image': {'eye': 0.049, 'jaw': 0.683, 'white': 0.065, 'smooth': 0.156}, 'AC': {'eye': 0.003, 'jaw': 0.637, 'white': 0.011, 'smooth': 0.009}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.894, 'jaw': 0.069, 'white': 0.803, 'smooth': 0.935}
quantities {"eye": {"n": 6629, "spearman": -0.074, "mae": 0.3812, "pred_mean": -0.1651, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4569, "orig_pred_mean": -0.1604}, "jaw": {"n": 6630, "spearman": 0.016, "mae": 0.3414, "pred_mean": -0.1888, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4661, "orig_pred_mean": -0.195}, "white": {"n": 6630, "spearman": 0.019, "mae": 0.5431, "pred_mean": 0.3525, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4188, "orig_pred_mean": 0.3364}, "smooth": {"n": 6630, "spearman": -0.035, "mae": 0.4763, "pred_mean": 0.5693, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.4392, "orig_pred_mean": 0.505}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 6.61 | 12.81 | 80.59 | 50.0 | 55.32 | 0.11 |
| EyeEnlarging_60 | 2209 | 6.52 | 12.63 | 80.85 | 50.13 | 57.76 | 0.105 |
| EyeEnlarging_90 | 2210 | 6.15 | 12.81 | 81.04 | 50.23 | 60.05 | 0.104 |
| FaceLifting_30 | 2210 | 7.1 | 12.85 | 80.05 | 49.73 | 51.81 | 0.935 |
| FaceLifting_60 | 2210 | 6.83 | 13.8 | 79.37 | 49.39 | 52.74 | 0.933 |
| FaceLifting_90 | 2210 | 6.47 | 14.25 | 79.28 | 49.34 | 51.76 | 0.932 |
| Whitening_30 | 2210 | 8.37 | 12.76 | 78.87 | 49.14 | 38.71 | 0.191 |
| Whitening_60 | 2210 | 10.0 | 13.89 | 76.11 | 47.76 | 33.39 | 0.185 |
| Whitening_90 | 2210 | 10.63 | 14.48 | 74.89 | 47.15 | 33.98 | 0.176 |
| Smoothing_30 | 2210 | 6.24 | 32.76 | 61.0 | 40.2 | 26.9 | 0.047 |
| Smoothing_60 | 2210 | 4.07 | 59.82 | 36.11 | 27.76 | 13.28 | 0.054 |
| Smoothing_90 | 2210 | 3.26 | 73.21 | 23.53 | 21.47 | 8.14 | 0.056 |

## FF++ / cross-dataset
{"indomain": {"real": 8.66, "fake": 95.61, "filter": 75.46}, "FA": 12.61, "real_to_filter": 79.48, "MISS": 0.06, "heldout13": {"filter": 73.94, "fake": 12.77, "paired_excess_pp": -5.54}, "cdf": {"auc": 0.8669, "real_called_fake": 25.76}, "dfd": {"auc": 0.9531, "real_called_fake": 5.72}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
