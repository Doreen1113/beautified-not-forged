# RU clipe5fb_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 51.63, 'fake': 26.79, 'filter': 21.58} | pooled {'n': 26519, 'to_real': 50.04, 'to_fake': 29.47, 'to_filter': 20.49, 'balanced_acc': 49.45, 'paired_rank': 47.96}
Eq.4 {'TP': {'eye': 0.801, 'jaw': 0.513, 'white': 0.72, 'smooth': 0.714}, 'TN_same_image': {'eye': 0.019, 'jaw': 0.013, 'white': 0.025, 'smooth': 0.018}, 'AC': {'eye': 0.013, 'jaw': 0.006, 'white': 0.019, 'smooth': 0.012}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.219, 'jaw': 0.514, 'white': 0.261, 'smooth': 0.166}
quantities {"eye": {"n": 6629, "spearman": -0.005, "mae": 0.5532, "pred_mean": -0.3856, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4414, "orig_pred_mean": -0.4}, "jaw": {"n": 6630, "spearman": -0.002, "mae": 0.4064, "pred_mean": -0.1732, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.483, "orig_pred_mean": -0.177}, "white": {"n": 6630, "spearman": -0.048, "mae": 0.5709, "pred_mean": 0.4632, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4296, "orig_pred_mean": 0.4658}, "smooth": {"n": 6630, "spearman": -0.158, "mae": 0.5081, "pred_mean": -0.2171, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.531, "orig_pred_mean": -0.118}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 52.13 | 26.15 | 21.72 | 50.07 | 56.74 | 0.804 |
| EyeEnlarging_60 | 2209 | 51.74 | 26.71 | 21.55 | 49.98 | 52.94 | 0.801 |
| EyeEnlarging_90 | 2210 | 50.72 | 29.0 | 20.27 | 49.35 | 48.42 | 0.797 |
| FaceLifting_30 | 2210 | 52.85 | 24.93 | 22.22 | 50.32 | 55.41 | 0.508 |
| FaceLifting_60 | 2210 | 52.58 | 26.06 | 21.36 | 49.89 | 49.86 | 0.513 |
| FaceLifting_90 | 2210 | 51.9 | 27.87 | 20.23 | 49.32 | 48.96 | 0.519 |
| Whitening_30 | 2210 | 51.95 | 25.34 | 22.71 | 50.57 | 55.54 | 0.738 |
| Whitening_60 | 2210 | 51.36 | 26.29 | 22.35 | 50.39 | 52.67 | 0.719 |
| Whitening_90 | 2210 | 50.09 | 27.15 | 22.76 | 50.59 | 50.0 | 0.704 |
| Smoothing_30 | 2210 | 47.74 | 34.48 | 17.78 | 48.1 | 36.61 | 0.754 |
| Smoothing_60 | 2210 | 45.75 | 37.38 | 16.88 | 47.65 | 35.25 | 0.711 |
| Smoothing_90 | 2210 | 41.72 | 42.26 | 16.02 | 47.22 | 33.12 | 0.678 |

## FF++ / cross-dataset
{"indomain": {"real": 39.59, "fake": 96.49, "filter": 47.64}, "FA": 14.51, "real_to_filter": 47.64, "MISS": 3.22, "heldout13": {"filter": 43.16, "fake": 25.15, "paired_excess_pp": -4.48}, "cdf": {"auc": 0.8768, "real_called_fake": 26.01}, "dfd": {"auc": 0.9514, "real_called_fake": 8.8}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
