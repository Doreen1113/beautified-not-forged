# RU clipe5mf_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 1.58, 'fake': 18.64, 'filter': 79.77} | pooled {'n': 26519, 'to_real': 1.69, 'to_fake': 18.85, 'to_filter': 79.46, 'balanced_acc': 49.85, 'paired_rank': 55.49}
Eq.4 {'TP': {'eye': 0.0, 'jaw': 0.046, 'white': 0.079, 'smooth': 0.648}, 'TN_same_image': {'eye': 0.795, 'jaw': 0.84, 'white': 0.958, 'smooth': 0.911}, 'AC': {'eye': 0.0, 'jaw': 0.046, 'white': 0.079, 'smooth': 0.641}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 1.0, 'jaw': 0.972, 'white': 0.818, 'smooth': 0.987}
quantities {"eye": {"n": 6629, "spearman": -0.062, "mae": 0.0574, "pred_mean": -0.0217, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.067, "orig_pred_mean": -0.0266}, "jaw": {"n": 6630, "spearman": 0.009, "mae": 0.0662, "pred_mean": -0.0435, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0634, "orig_pred_mean": -0.0509}, "white": {"n": 6630, "spearman": 0.162, "mae": 0.4637, "pred_mean": 0.1162, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0519, "orig_pred_mean": 0.1194}, "smooth": {"n": 6630, "spearman": 0.41, "mae": 0.0946, "pred_mean": 0.1461, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0692, "orig_pred_mean": 0.0302}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 2.31 | 16.92 | 80.77 | 50.5 | 52.94 | 0.0 |
| EyeEnlarging_60 | 2209 | 1.86 | 16.57 | 81.58 | 50.9 | 58.24 | 0.0 |
| EyeEnlarging_90 | 2210 | 1.67 | 17.92 | 80.41 | 50.32 | 60.88 | 0.0 |
| FaceLifting_30 | 2210 | 2.67 | 16.79 | 80.54 | 50.39 | 48.37 | 0.044 |
| FaceLifting_60 | 2210 | 2.53 | 17.06 | 80.41 | 50.32 | 49.91 | 0.046 |
| FaceLifting_90 | 2210 | 2.17 | 18.46 | 79.37 | 49.8 | 51.2 | 0.049 |
| Whitening_30 | 2210 | 2.08 | 16.97 | 80.95 | 50.59 | 51.95 | 0.121 |
| Whitening_60 | 2210 | 1.81 | 17.83 | 80.36 | 50.3 | 60.5 | 0.078 |
| Whitening_90 | 2210 | 1.18 | 18.33 | 80.5 | 50.36 | 65.57 | 0.04 |
| Smoothing_30 | 2210 | 1.76 | 24.75 | 73.48 | 46.86 | 35.66 | 0.266 |
| Smoothing_60 | 2210 | 0.18 | 21.04 | 78.78 | 49.5 | 64.62 | 0.789 |
| Smoothing_90 | 2210 | 0.05 | 23.57 | 76.38 | 48.31 | 66.11 | 0.89 |

## FF++ / cross-dataset
{"indomain": {"real": 76.44, "fake": 94.16, "filter": 80.4}, "FA": 9.35, "real_to_filter": 16.03, "MISS": 0.91, "heldout13": {"filter": 70.9, "fake": 19.22, "paired_excess_pp": 54.87}, "cdf": {"auc": 0.8893, "real_called_fake": 16.42}, "dfd": {"auc": 0.9552, "real_called_fake": 4.03}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
