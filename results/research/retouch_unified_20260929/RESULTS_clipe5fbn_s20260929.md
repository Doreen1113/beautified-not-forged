# RU clipe5fbn_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 5.25, 'fake': 17.87, 'filter': 76.88} | pooled {'n': 26519, 'to_real': 4.82, 'to_fake': 27.83, 'to_filter': 67.35, 'balanced_acc': 45.24, 'paired_rank': 44.04}
Eq.4 {'TP': {'eye': 0.057, 'jaw': 0.931, 'white': 0.365, 'smooth': 0.023}, 'TN_same_image': {'eye': 0.052, 'jaw': 0.603, 'white': 0.064, 'smooth': 0.103}, 'AC': {'eye': 0.001, 'jaw': 0.552, 'white': 0.016, 'smooth': 0.004}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.947, 'jaw': 0.067, 'white': 0.652, 'smooth': 0.978}
quantities {"eye": {"n": 6629, "spearman": -0.072, "mae": 0.4328, "pred_mean": 0.0694, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4209, "orig_pred_mean": 0.0487}, "jaw": {"n": 6630, "spearman": 0.003, "mae": 0.3794, "pred_mean": -0.172, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4403, "orig_pred_mean": -0.1557}, "white": {"n": 6630, "spearman": 0.006, "mae": 0.5554, "pred_mean": 0.2852, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4241, "orig_pred_mean": 0.2614}, "smooth": {"n": 6630, "spearman": -0.06, "mae": 0.406, "pred_mean": 0.3857, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.4335, "orig_pred_mean": 0.3307}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 4.62 | 15.88 | 79.5 | 51.31 | 63.33 | 0.057 |
| EyeEnlarging_60 | 2209 | 4.48 | 15.93 | 79.58 | 51.35 | 63.38 | 0.058 |
| EyeEnlarging_90 | 2210 | 4.25 | 16.38 | 79.37 | 51.24 | 62.96 | 0.058 |
| FaceLifting_30 | 2210 | 4.84 | 15.84 | 79.32 | 51.22 | 59.28 | 0.934 |
| FaceLifting_60 | 2210 | 4.71 | 16.83 | 78.46 | 50.79 | 58.85 | 0.932 |
| FaceLifting_90 | 2210 | 4.93 | 17.56 | 77.51 | 50.32 | 57.47 | 0.927 |
| Whitening_30 | 2210 | 5.57 | 16.61 | 77.83 | 50.47 | 48.46 | 0.37 |
| Whitening_60 | 2210 | 6.33 | 17.51 | 76.15 | 49.64 | 41.45 | 0.37 |
| Whitening_90 | 2210 | 7.29 | 18.37 | 74.34 | 48.73 | 36.9 | 0.355 |
| Smoothing_30 | 2210 | 4.84 | 37.24 | 57.92 | 40.52 | 23.35 | 0.016 |
| Smoothing_60 | 2210 | 3.53 | 66.47 | 30.0 | 26.56 | 8.87 | 0.023 |
| Smoothing_90 | 2210 | 2.49 | 79.28 | 18.24 | 20.68 | 4.16 | 0.029 |

## FF++ / cross-dataset
{"indomain": {"real": 1.44, "fake": 94.17, "filter": 80.62}, "FA": 16.26, "real_to_filter": 91.34, "MISS": 0.03, "heldout13": {"filter": 75.23, "fake": 21.2, "paired_excess_pp": -16.11}, "cdf": {"auc": 0.8651, "real_called_fake": 21.71}, "dfd": {"auc": 0.9597, "real_called_fake": 3.5}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
