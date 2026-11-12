# RU clipe5af_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 1.86, 'fake': 11.18, 'filter': 86.97} | pooled {'n': 26519, 'to_real': 1.69, 'to_fake': 14.11, 'to_filter': 84.2, 'balanced_acc': 48.62, 'paired_rank': 53.36}
Eq.4 {'TP': {'eye': 0.0, 'jaw': 0.039, 'white': 0.005, 'smooth': 0.603}, 'TN_same_image': {'eye': 0.932, 'jaw': 0.981, 'white': 0.961, 'smooth': 0.984}, 'AC': {'eye': 0.0, 'jaw': 0.039, 'white': 0.005, 'smooth': 0.601}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 1.0, 'jaw': 0.971, 'white': 0.988, 'smooth': 0.991}
quantities {"eye": {"n": 6629, "spearman": 0.0, "mae": 0.0582, "pred_mean": 0.0043, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0659, "orig_pred_mean": 0.0003}, "jaw": {"n": 6630, "spearman": 0.023, "mae": 0.0805, "pred_mean": -0.0543, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0596, "orig_pred_mean": -0.0644}, "white": {"n": 6630, "spearman": -0.022, "mae": 0.516, "pred_mean": 0.0243, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0689, "orig_pred_mean": 0.0192}, "smooth": {"n": 6630, "spearman": 0.418, "mae": 0.1257, "pred_mean": 0.216, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0925, "orig_pred_mean": 0.0679}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 2.44 | 10.5 | 87.06 | 50.04 | 59.12 | 0.0 |
| EyeEnlarging_60 | 2209 | 1.99 | 10.96 | 87.05 | 50.04 | 59.89 | 0.0 |
| EyeEnlarging_90 | 2210 | 1.81 | 12.22 | 85.97 | 49.5 | 57.38 | 0.0 |
| FaceLifting_30 | 2210 | 2.85 | 10.5 | 86.65 | 49.84 | 57.01 | 0.033 |
| FaceLifting_60 | 2210 | 2.71 | 10.77 | 86.52 | 49.77 | 55.81 | 0.04 |
| FaceLifting_90 | 2210 | 2.35 | 11.27 | 86.38 | 49.71 | 54.05 | 0.044 |
| Whitening_30 | 2210 | 2.08 | 10.77 | 87.15 | 50.09 | 57.65 | 0.008 |
| Whitening_60 | 2210 | 1.4 | 10.9 | 87.69 | 50.36 | 61.86 | 0.005 |
| Whitening_90 | 2210 | 0.59 | 11.04 | 88.37 | 50.7 | 64.14 | 0.003 |
| Smoothing_30 | 2210 | 1.81 | 17.78 | 80.41 | 46.72 | 36.47 | 0.22 |
| Smoothing_60 | 2210 | 0.18 | 22.13 | 77.69 | 45.36 | 42.53 | 0.733 |
| Smoothing_90 | 2210 | 0.05 | 30.5 | 69.46 | 41.24 | 34.43 | 0.855 |

## FF++ / cross-dataset
{"indomain": {"real": 69.38, "fake": 92.91, "filter": 81.0}, "FA": 9.42, "real_to_filter": 23.86, "MISS": 0.66, "heldout13": {"filter": 80.62, "fake": 16.34, "paired_excess_pp": 56.76}, "cdf": {"auc": 0.8763, "real_called_fake": 10.08}, "dfd": {"auc": 0.9613, "real_called_fake": 2.54}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
