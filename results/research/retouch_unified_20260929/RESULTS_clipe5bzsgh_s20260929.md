# RU clipe5bzsgh_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 64.03, 'fake': 1.18, 'filter': 34.8} | pooled {'n': 26519, 'to_real': 61.27, 'to_fake': 1.1, 'to_filter': 37.63, 'balanced_acc': 51.41, 'paired_rank': 51.57}
Eq.4 {'TP': {'eye': 0.359, 'jaw': 0.922, 'white': 0.053, 'smooth': 0.028}, 'TN_same_image': {'eye': 0.073, 'jaw': 0.501, 'white': 0.055, 'smooth': 0.014}, 'AC': {'eye': 0.017, 'jaw': 0.454, 'white': 0.003, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.696, 'jaw': 0.082, 'white': 0.939, 'smooth': 1.0}
quantities {"eye": {"n": 6629, "spearman": -0.13, "mae": 0.4804, "pred_mean": 0.4411, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3181, "orig_pred_mean": 0.3617}, "jaw": {"n": 6630, "spearman": -0.066, "mae": 0.2391, "pred_mean": 0.0223, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4458, "orig_pred_mean": 0.1348}, "white": {"n": 6630, "spearman": -0.043, "mae": 0.5098, "pred_mean": 0.4945, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.3217, "orig_pred_mean": 0.5318}, "smooth": {"n": 6630, "spearman": 0.158, "mae": 0.209, "pred_mean": 0.2442, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3862, "orig_pred_mean": 0.1399}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 56.38 | 0.86 | 42.76 | 53.98 | 61.27 | 0.382 |
| EyeEnlarging_60 | 2209 | 50.88 | 0.77 | 48.35 | 56.77 | 66.18 | 0.353 |
| EyeEnlarging_90 | 2210 | 47.19 | 0.95 | 51.86 | 58.53 | 67.78 | 0.343 |
| FaceLifting_30 | 2210 | 61.36 | 0.72 | 37.92 | 51.56 | 49.37 | 0.928 |
| FaceLifting_60 | 2210 | 60.27 | 0.81 | 38.91 | 52.06 | 52.71 | 0.914 |
| FaceLifting_90 | 2210 | 59.1 | 0.9 | 40.0 | 52.6 | 56.06 | 0.924 |
| Whitening_30 | 2210 | 61.9 | 0.95 | 37.15 | 51.17 | 47.44 | 0.065 |
| Whitening_60 | 2210 | 63.8 | 1.22 | 34.98 | 50.09 | 45.7 | 0.05 |
| Whitening_90 | 2210 | 66.56 | 1.27 | 32.17 | 48.69 | 44.43 | 0.043 |
| Smoothing_30 | 2210 | 64.8 | 1.49 | 33.71 | 49.46 | 46.65 | 0.007 |
| Smoothing_60 | 2210 | 71.67 | 1.45 | 26.88 | 46.04 | 41.13 | 0.036 |
| Smoothing_90 | 2210 | 71.36 | 1.81 | 26.83 | 46.02 | 40.09 | 0.042 |

## FF++ / cross-dataset
{"indomain": {"real": 72.42, "fake": 95.12, "filter": 47.57}, "FA": 12.84, "real_to_filter": 14.82, "MISS": 1.91, "heldout13": {"filter": 54.64, "fake": 16.87, "paired_excess_pp": 39.82}, "cdf": {"auc": 0.8978, "real_called_fake": 35.53}, "dfd": {"auc": 0.9612, "real_called_fake": 7.53}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
