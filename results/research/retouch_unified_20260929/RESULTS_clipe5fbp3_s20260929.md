# RU clipe5fbp3_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 16.43, 'fake': 31.36, 'filter': 52.22} | pooled {'n': 26519, 'to_real': 12.62, 'to_fake': 45.12, 'to_filter': 42.25, 'balanced_acc': 45.02, 'paired_rank': 41.43}
Eq.4 {'TP': {'eye': 0.073, 'jaw': 0.925, 'white': 0.379, 'smooth': 0.046}, 'TN_same_image': {'eye': 0.05, 'jaw': 0.557, 'white': 0.072, 'smooth': 0.089}, 'AC': {'eye': 0.003, 'jaw': 0.513, 'white': 0.022, 'smooth': 0.007}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.927, 'jaw': 0.071, 'white': 0.608, 'smooth': 0.984}
quantities {"eye": {"n": 6629, "spearman": -0.076, "mae": 0.4878, "pred_mean": -0.0514, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3912, "orig_pred_mean": -0.0364}, "jaw": {"n": 6630, "spearman": 0.016, "mae": 0.3591, "pred_mean": -0.0608, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4309, "orig_pred_mean": -0.0576}, "white": {"n": 6630, "spearman": -0.047, "mae": 0.6367, "pred_mean": 0.0875, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4474, "orig_pred_mean": 0.1104}, "smooth": {"n": 6630, "spearman": 0.187, "mae": 0.5542, "pred_mean": 0.652, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.5134, "orig_pred_mean": 0.2763}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 15.11 | 30.09 | 54.8 | 51.29 | 65.45 | 0.071 |
| EyeEnlarging_60 | 2209 | 14.26 | 31.69 | 54.05 | 50.92 | 64.26 | 0.072 |
| EyeEnlarging_90 | 2210 | 12.71 | 34.03 | 53.26 | 50.52 | 60.14 | 0.077 |
| FaceLifting_30 | 2210 | 16.11 | 29.91 | 53.98 | 50.88 | 61.24 | 0.925 |
| FaceLifting_60 | 2210 | 15.88 | 30.14 | 53.98 | 50.88 | 58.12 | 0.928 |
| FaceLifting_90 | 2210 | 14.84 | 31.54 | 53.62 | 50.7 | 56.79 | 0.923 |
| Whitening_30 | 2210 | 16.2 | 32.9 | 50.9 | 49.34 | 45.84 | 0.394 |
| Whitening_60 | 2210 | 16.02 | 36.65 | 47.33 | 47.56 | 35.59 | 0.383 |
| Whitening_90 | 2210 | 14.71 | 42.71 | 42.58 | 45.18 | 29.82 | 0.359 |
| Smoothing_30 | 2210 | 10.0 | 61.4 | 28.6 | 38.19 | 14.57 | 0.031 |
| Smoothing_60 | 2210 | 3.67 | 86.56 | 9.77 | 28.78 | 3.62 | 0.049 |
| Smoothing_90 | 2210 | 1.99 | 93.85 | 4.16 | 25.97 | 1.67 | 0.06 |

## FF++ / cross-dataset
{"indomain": {"real": 9.57, "fake": 95.14, "filter": 44.15}, "FA": 46.81, "real_to_filter": 80.62, "MISS": 0.09, "heldout13": {"filter": 39.51, "fake": 51.9, "paired_excess_pp": -41.11}, "cdf": {"auc": 0.9024, "real_called_fake": 20.95}, "dfd": {"auc": 0.9612, "real_called_fake": 5.94}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
