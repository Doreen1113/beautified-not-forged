# RU clipe5bzl01_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 64.25, 'fake': 0.68, 'filter': 35.07} | pooled {'n': 26519, 'to_real': 70.18, 'to_fake': 0.6, 'to_filter': 29.22, 'balanced_acc': 47.08, 'paired_rank': 39.81}
Eq.4 {'TP': {'eye': 0.094, 'jaw': 0.998, 'white': 0.014, 'smooth': 0.0}, 'TN_same_image': {'eye': 0.001, 'jaw': 0.948, 'white': 0.0, 'smooth': 0.001}, 'AC': {'eye': 0.0, 'jaw': 0.948, 'white': 0.0, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.983, 'jaw': 0.002, 'white': 0.996, 'smooth': 1.0}
quantities {"eye": {"n": 6629, "spearman": 0.242, "mae": 0.8292, "pred_mean": 0.8426, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.1765, "orig_pred_mean": 0.6846}, "jaw": {"n": 6630, "spearman": 0.014, "mae": 0.2036, "pred_mean": 0.206, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.3801, "orig_pred_mean": 0.1748}, "white": {"n": 6630, "spearman": -0.287, "mae": 0.5647, "pred_mean": 0.0122, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4161, "orig_pred_mean": -0.1095}, "smooth": {"n": 6630, "spearman": 0.078, "mae": 0.171, "pred_mean": 0.0956, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3318, "orig_pred_mean": 0.2431}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 69.59 | 0.41 | 30.0 | 47.47 | 40.57 | 0.058 |
| EyeEnlarging_60 | 2209 | 71.98 | 0.41 | 27.61 | 46.27 | 37.37 | 0.096 |
| EyeEnlarging_90 | 2210 | 73.53 | 0.5 | 25.97 | 45.45 | 35.11 | 0.129 |
| FaceLifting_30 | 2210 | 69.37 | 0.36 | 30.27 | 47.6 | 42.06 | 0.998 |
| FaceLifting_60 | 2210 | 69.14 | 0.41 | 30.45 | 47.69 | 43.39 | 0.999 |
| FaceLifting_90 | 2210 | 70.86 | 0.41 | 28.73 | 46.83 | 43.12 | 0.999 |
| Whitening_30 | 2210 | 68.46 | 0.45 | 31.09 | 48.01 | 38.55 | 0.006 |
| Whitening_60 | 2210 | 72.04 | 0.54 | 27.42 | 46.18 | 36.97 | 0.013 |
| Whitening_90 | 2210 | 72.71 | 0.68 | 26.61 | 45.77 | 34.98 | 0.023 |
| Smoothing_30 | 2210 | 63.89 | 0.95 | 35.16 | 50.04 | 46.52 | 0.0 |
| Smoothing_60 | 2210 | 69.23 | 1.0 | 29.77 | 47.35 | 41.0 | 0.0 |
| Smoothing_90 | 2210 | 71.36 | 1.04 | 27.6 | 46.27 | 38.05 | 0.0 |

## FF++ / cross-dataset
{"indomain": {"real": 25.53, "fake": 92.04, "filter": 62.77}, "FA": 13.15, "real_to_filter": 62.61, "MISS": 0.75, "heldout13": {"filter": 60.18, "fake": 21.28, "paired_excess_pp": -2.43}, "cdf": {"auc": 0.8701, "real_called_fake": 21.85}, "dfd": {"auc": 0.9517, "real_called_fake": 6.78}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
