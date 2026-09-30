# RU ru2_effb4_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 76.79, 'fake': 0.45, 'filter': 22.76} | pooled {'n': 26519, 'to_real': 31.48, 'to_fake': 0.32, 'to_filter': 68.2, 'balanced_acc': 72.72, 'paired_rank': 94.18}
Eq.4 {'TP': {'eye': 0.227, 'jaw': 0.252, 'white': 0.199, 'smooth': 0.953}, 'TN_same_image': {'eye': 0.834, 'jaw': 0.926, 'white': 0.759, 'smooth': 0.336}, 'AC': {'eye': 0.2, 'jaw': 0.221, 'white': 0.09, 'smooth': 0.299}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.987, 'jaw': 0.967, 'white': 0.973, 'smooth': 0.982}
quantities {"eye": {"n": 6629, "spearman": 0.432, "mae": 0.0264, "pred_mean": 0.0022, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0062, "orig_pred_mean": 0.0001}, "jaw": {"n": 6630, "spearman": 0.159, "mae": 0.0187, "pred_mean": 0.0019, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0051, "orig_pred_mean": 0.0002}, "white": {"n": 6630, "spearman": -0.169, "mae": 0.5092, "pred_mean": 0.0219, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0029, "orig_pred_mean": 0.0065}, "smooth": {"n": 6630, "spearman": 0.468, "mae": 0.0939, "pred_mean": 0.093, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0216, "orig_pred_mean": 0.0003}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 47.1 | 0.36 | 52.53 | 64.89 | 97.87 | 0.093 |
| EyeEnlarging_60 | 2209 | 34.09 | 0.32 | 65.6 | 71.42 | 99.09 | 0.226 |
| EyeEnlarging_90 | 2210 | 25.79 | 0.23 | 73.98 | 75.61 | 99.28 | 0.361 |
| FaceLifting_30 | 2210 | 53.67 | 0.32 | 46.02 | 61.63 | 86.79 | 0.186 |
| FaceLifting_60 | 2210 | 47.96 | 0.27 | 51.76 | 64.5 | 90.81 | 0.25 |
| FaceLifting_90 | 2210 | 41.09 | 0.27 | 58.64 | 67.94 | 93.85 | 0.32 |
| Whitening_30 | 2210 | 50.54 | 0.41 | 49.05 | 63.14 | 85.7 | 0.078 |
| Whitening_60 | 2210 | 41.13 | 0.41 | 58.46 | 67.85 | 87.87 | 0.189 |
| Whitening_90 | 2210 | 32.94 | 0.54 | 66.52 | 71.88 | 90.18 | 0.33 |
| Smoothing_30 | 2210 | 3.17 | 0.27 | 96.56 | 86.9 | 99.46 | 0.871 |
| Smoothing_60 | 2210 | 0.18 | 0.09 | 99.73 | 88.48 | 99.77 | 0.993 |
| Smoothing_90 | 2210 | 0.09 | 0.41 | 99.5 | 88.37 | 99.5 | 0.996 |

## FF++ / cross-dataset
{"indomain": {"real": 79.41, "fake": 93.61, "filter": 75.76}, "FA": 10.26, "real_to_filter": 14.44, "MISS": 0.5, "heldout13": {"filter": 45.67, "fake": 17.33, "paired_excess_pp": 31.23}, "cdf": {"auc": 0.8216, "real_called_fake": 27.9}, "dfd": {"auc": 0.9376, "real_called_fake": 7.42}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
