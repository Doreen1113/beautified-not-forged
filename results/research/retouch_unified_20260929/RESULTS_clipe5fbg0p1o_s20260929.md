# RU clipe5fbg0p1o_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 4.25, 'fake': 32.26, 'filter': 63.48} | pooled {'n': 26519, 'to_real': 5.31, 'to_fake': 29.13, 'to_filter': 65.56, 'balanced_acc': 51.04, 'paired_rank': 46.6}
Eq.4 {'TP': {'eye': 0.058, 'jaw': 0.787, 'white': 0.238, 'smooth': 0.144}, 'TN_same_image': {'eye': 0.158, 'jaw': 0.712, 'white': 0.218, 'smooth': 0.076}, 'AC': {'eye': 0.003, 'jaw': 0.56, 'white': 0.058, 'smooth': 0.005}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.945, 'jaw': 0.211, 'white': 0.763, 'smooth': 0.99}
quantities {"eye": {"n": 6629, "spearman": -0.075, "mae": 0.5013, "pred_mean": -0.0946, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3729, "orig_pred_mean": -0.0548}, "jaw": {"n": 6630, "spearman": 0.014, "mae": 0.3292, "pred_mean": -0.0798, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4245, "orig_pred_mean": -0.0612}, "white": {"n": 6630, "spearman": -0.036, "mae": 0.6198, "pred_mean": 0.0588, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4298, "orig_pred_mean": 0.0551}, "smooth": {"n": 6630, "spearman": 0.294, "mae": 0.4728, "pred_mean": 0.6043, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3682, "orig_pred_mean": 0.3695}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 3.76 | 33.57 | 62.67 | 49.59 | 45.36 | 0.061 |
| EyeEnlarging_60 | 2209 | 3.76 | 35.58 | 60.66 | 48.59 | 43.98 | 0.057 |
| EyeEnlarging_90 | 2210 | 3.53 | 38.55 | 57.92 | 47.22 | 41.95 | 0.057 |
| FaceLifting_30 | 2210 | 3.89 | 33.08 | 63.03 | 49.78 | 48.01 | 0.785 |
| FaceLifting_60 | 2210 | 3.53 | 34.52 | 61.95 | 49.23 | 45.72 | 0.786 |
| FaceLifting_90 | 2210 | 3.26 | 36.83 | 59.91 | 48.21 | 45.14 | 0.79 |
| Whitening_30 | 2210 | 4.71 | 33.26 | 62.04 | 49.28 | 42.17 | 0.242 |
| Whitening_60 | 2210 | 4.84 | 34.34 | 60.81 | 48.67 | 40.18 | 0.242 |
| Whitening_90 | 2210 | 5.16 | 35.75 | 59.1 | 47.81 | 36.65 | 0.23 |
| Smoothing_30 | 2210 | 6.24 | 23.3 | 70.45 | 53.49 | 54.3 | 0.034 |
| Smoothing_60 | 2210 | 9.55 | 6.74 | 83.71 | 60.12 | 58.64 | 0.158 |
| Smoothing_90 | 2210 | 11.45 | 4.07 | 84.48 | 60.5 | 57.1 | 0.24 |

## FF++ / cross-dataset
{"indomain": {"real": 4.03, "fake": 97.17, "filter": 74.77}, "FA": 20.06, "real_to_filter": 81.61, "MISS": 0.81, "heldout13": {"filter": 62.23, "fake": 32.98, "paired_excess_pp": -19.38}, "cdf": {"auc": 0.8838, "real_called_fake": 44.62}, "dfd": {"auc": 0.9521, "real_called_fake": 17.49}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
