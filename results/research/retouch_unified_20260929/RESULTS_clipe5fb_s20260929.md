# RU clipe5fb_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 71.99, 'fake': 17.42, 'filter': 10.59} | pooled {'n': 26519, 'to_real': 70.28, 'to_fake': 20.51, 'to_filter': 9.21, 'balanced_acc': 49.31, 'paired_rank': 40.17}
Eq.4 {'TP': {'eye': 0.911, 'jaw': 0.158, 'white': 0.917, 'smooth': 0.545}, 'TN_same_image': {'eye': 0.032, 'jaw': 0.003, 'white': 0.018, 'smooth': 0.007}, 'AC': {'eye': 0.03, 'jaw': 0.0, 'white': 0.014, 'smooth': 0.003}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.103, 'jaw': 0.843, 'white': 0.081, 'smooth': 0.368}
quantities {"eye": {"n": 6629, "spearman": 0.006, "mae": 0.3174, "pred_mean": -0.0453, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3102, "orig_pred_mean": -0.0199}, "jaw": {"n": 6630, "spearman": -0.021, "mae": 0.3069, "pred_mean": -0.0431, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.3147, "orig_pred_mean": -0.0394}, "white": {"n": 6630, "spearman": 0.085, "mae": 0.6491, "pred_mean": -0.0356, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.3141, "orig_pred_mean": -0.0765}, "smooth": {"n": 6630, "spearman": 0.135, "mae": 0.3317, "pred_mean": 0.1475, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3251, "orig_pred_mean": 0.0937}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 74.89 | 16.29 | 8.82 | 49.12 | 40.79 | 0.905 |
| EyeEnlarging_60 | 2209 | 75.1 | 16.43 | 8.47 | 48.94 | 37.6 | 0.91 |
| EyeEnlarging_90 | 2210 | 74.48 | 17.38 | 8.14 | 48.78 | 35.93 | 0.918 |
| FaceLifting_30 | 2210 | 74.71 | 16.02 | 9.28 | 49.34 | 41.52 | 0.157 |
| FaceLifting_60 | 2210 | 73.98 | 16.97 | 9.05 | 49.23 | 39.64 | 0.16 |
| FaceLifting_90 | 2210 | 73.89 | 17.42 | 8.69 | 49.05 | 39.07 | 0.158 |
| Whitening_30 | 2210 | 73.85 | 16.65 | 9.5 | 49.46 | 45.25 | 0.915 |
| Whitening_60 | 2210 | 73.26 | 16.97 | 9.77 | 49.59 | 44.34 | 0.918 |
| Whitening_90 | 2210 | 72.49 | 17.6 | 9.91 | 49.66 | 42.13 | 0.918 |
| Smoothing_30 | 2210 | 63.76 | 25.57 | 10.68 | 50.04 | 44.64 | 0.609 |
| Smoothing_60 | 2210 | 59.05 | 31.22 | 9.73 | 49.57 | 38.14 | 0.537 |
| Smoothing_90 | 2210 | 53.94 | 37.6 | 8.46 | 48.94 | 33.03 | 0.49 |

## FF++ / cross-dataset
{"indomain": {"real": 78.88, "fake": 96.38, "filter": 9.12}, "FA": 12.01, "real_to_filter": 9.8, "MISS": 3.41, "heldout13": {"filter": 8.28, "fake": 25.38, "paired_excess_pp": -1.52}, "cdf": {"auc": 0.8766, "real_called_fake": 26.02}, "dfd": {"auc": 0.9507, "real_called_fake": 5.78}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
