# RU clipe7_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 87.01, 'fake': 0.54, 'filter': 12.44} | pooled {'n': 26519, 'to_real': 38.7, 'to_fake': 0.61, 'to_filter': 60.68, 'balanced_acc': 74.12, 'paired_rank': 94.18}
Eq.4 {'TP': {'eye': 0.227, 'jaw': 0.316, 'white': 0.249, 'smooth': 0.916}, 'TN_same_image': {'eye': 0.799, 'jaw': 0.951, 'white': 0.779, 'smooth': 0.499}, 'AC': {'eye': 0.22, 'jaw': 0.308, 'white': 0.187, 'smooth': 0.426}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.987, 'jaw': 0.971, 'white': 0.972, 'smooth': 0.994}
quantities {"eye": {"n": 6629, "spearman": 0.396, "mae": 0.0241, "pred_mean": 0.0056, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0079, "orig_pred_mean": -0.0007}, "jaw": {"n": 6630, "spearman": 0.143, "mae": 0.017, "pred_mean": 0.0058, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0067, "orig_pred_mean": -0.0005}, "white": {"n": 6630, "spearman": -0.087, "mae": 0.4985, "pred_mean": 0.0396, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0069, "orig_pred_mean": 0.0066}, "smooth": {"n": 6630, "spearman": 0.247, "mae": 0.0974, "pred_mean": 0.0939, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0162, "orig_pred_mean": -0.0011}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 59.77 | 0.5 | 39.73 | 63.64 | 95.07 | 0.076 |
| EyeEnlarging_60 | 2209 | 45.36 | 0.5 | 54.14 | 70.85 | 97.37 | 0.236 |
| EyeEnlarging_90 | 2210 | 34.62 | 0.5 | 64.89 | 76.22 | 98.51 | 0.37 |
| FaceLifting_30 | 2210 | 62.4 | 0.36 | 37.24 | 62.4 | 85.25 | 0.247 |
| FaceLifting_60 | 2210 | 55.66 | 0.32 | 44.03 | 65.79 | 90.66 | 0.313 |
| FaceLifting_90 | 2210 | 47.65 | 0.27 | 52.08 | 69.82 | 93.17 | 0.389 |
| Whitening_30 | 2210 | 60.09 | 0.45 | 39.46 | 63.51 | 87.38 | 0.088 |
| Whitening_60 | 2210 | 46.33 | 0.68 | 52.99 | 70.27 | 91.9 | 0.236 |
| Whitening_90 | 2210 | 35.16 | 0.77 | 64.07 | 75.82 | 94.43 | 0.424 |
| Smoothing_30 | 2210 | 14.3 | 0.63 | 85.07 | 86.31 | 98.28 | 0.786 |
| Smoothing_60 | 2210 | 1.76 | 0.77 | 97.47 | 92.51 | 99.37 | 0.975 |
| Smoothing_90 | 2210 | 1.36 | 1.63 | 97.01 | 92.29 | 98.82 | 0.986 |

## FF++ / cross-dataset
{"indomain": {"real": 84.88, "fake": 91.31, "filter": 87.46}, "FA": 5.09, "real_to_filter": 9.27, "MISS": 0.91, "heldout13": {"filter": 72.72, "fake": 13.98, "paired_excess_pp": 63.45}, "cdf": {"auc": 0.9041, "real_called_fake": 12.81}, "dfd": {"auc": 0.9573, "real_called_fake": 1.8}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": true, "D2_heldout_excess>=30": true}}
