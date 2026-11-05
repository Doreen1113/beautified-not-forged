# RU clipe5kf_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 1.54, 'fake': 11.49, 'filter': 86.97} | pooled {'n': 26519, 'to_real': 1.49, 'to_fake': 14.2, 'to_filter': 84.31, 'balanced_acc': 48.67, 'paired_rank': 54.43}
Eq.4 {'TP': {'eye': 0.0, 'jaw': 0.054, 'white': 0.004, 'smooth': 0.56}, 'TN_same_image': {'eye': 0.925, 'jaw': 0.985, 'white': 0.957, 'smooth': 0.987}, 'AC': {'eye': 0.0, 'jaw': 0.054, 'white': 0.004, 'smooth': 0.56}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 1.0, 'jaw': 0.963, 'white': 0.994, 'smooth': 0.99}
quantities {"eye": {"n": 6629, "spearman": -0.012, "mae": 0.0745, "pred_mean": -0.0048, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0698, "orig_pred_mean": -0.0108}, "jaw": {"n": 6630, "spearman": 0.005, "mae": 0.0583, "pred_mean": 0.0438, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0706, "orig_pred_mean": 0.0397}, "white": {"n": 6630, "spearman": -0.1, "mae": 0.4975, "pred_mean": 0.0661, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.068, "orig_pred_mean": 0.0825}, "smooth": {"n": 6630, "spearman": 0.462, "mae": 0.1218, "pred_mean": 0.1087, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.089, "orig_pred_mean": -0.0179}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 2.22 | 10.27 | 87.51 | 50.27 | 56.76 | 0.0 |
| EyeEnlarging_60 | 2209 | 1.77 | 11.05 | 87.19 | 50.11 | 57.4 | 0.0 |
| EyeEnlarging_90 | 2210 | 1.36 | 12.44 | 86.2 | 49.61 | 56.33 | 0.0 |
| FaceLifting_30 | 2210 | 2.49 | 10.45 | 87.06 | 50.04 | 53.96 | 0.046 |
| FaceLifting_60 | 2210 | 2.4 | 10.86 | 86.74 | 49.89 | 55.07 | 0.054 |
| FaceLifting_90 | 2210 | 2.17 | 12.35 | 85.48 | 49.25 | 53.8 | 0.061 |
| Whitening_30 | 2210 | 2.4 | 10.32 | 87.29 | 50.16 | 53.14 | 0.005 |
| Whitening_60 | 2210 | 1.49 | 10.9 | 87.6 | 50.32 | 59.55 | 0.005 |
| Whitening_90 | 2210 | 0.77 | 11.31 | 87.92 | 50.47 | 64.37 | 0.002 |
| Smoothing_30 | 2210 | 0.81 | 18.1 | 81.09 | 47.06 | 46.47 | 0.195 |
| Smoothing_60 | 2210 | 0.0 | 22.94 | 77.06 | 45.04 | 51.13 | 0.677 |
| Smoothing_90 | 2210 | 0.0 | 29.41 | 70.59 | 41.81 | 45.11 | 0.808 |

## FF++ / cross-dataset
{"indomain": {"real": 72.19, "fake": 92.31, "filter": 78.19}, "FA": 10.33, "real_to_filter": 21.05, "MISS": 1.03, "heldout13": {"filter": 75.53, "fake": 17.78, "paired_excess_pp": 54.48}, "cdf": {"auc": 0.8598, "real_called_fake": 10.34}, "dfd": {"auc": 0.9605, "real_called_fake": 2.49}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
