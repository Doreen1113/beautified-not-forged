# RU clipe5z_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 82.67, 'fake': 0.32, 'filter': 17.01} | pooled {'n': 26519, 'to_real': 34.77, 'to_fake': 0.26, 'to_filter': 64.96, 'balanced_acc': 73.98, 'paired_rank': 93.67}
Eq.4 {'TP': {'eye': 0.232, 'jaw': 0.312, 'white': 0.392, 'smooth': 0.858}, 'TN_same_image': {'eye': 0.792, 'jaw': 0.917, 'white': 0.816, 'smooth': 0.537}, 'AC': {'eye': 0.225, 'jaw': 0.301, 'white': 0.308, 'smooth': 0.409}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.988, 'jaw': 0.981, 'white': 0.936, 'smooth': 0.995}
quantities {"eye": {"n": 6629, "spearman": 0.432, "mae": 0.0264, "pred_mean": 0.0022, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0108, "orig_pred_mean": -0.0032}, "jaw": {"n": 6630, "spearman": 0.127, "mae": 0.0168, "pred_mean": 0.0055, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.01, "orig_pred_mean": 0.0004}, "white": {"n": 6630, "spearman": -0.2, "mae": 0.4876, "pred_mean": 0.0632, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0079, "orig_pred_mean": 0.0109}, "smooth": {"n": 6630, "spearman": 0.089, "mae": 0.1138, "pred_mean": 0.0724, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0168, "orig_pred_mean": -0.0055}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 54.57 | 0.27 | 45.16 | 64.07 | 95.05 | 0.087 |
| EyeEnlarging_60 | 2209 | 39.2 | 0.23 | 60.57 | 71.78 | 97.53 | 0.24 |
| EyeEnlarging_90 | 2210 | 30.32 | 0.23 | 69.46 | 76.22 | 98.37 | 0.369 |
| FaceLifting_30 | 2210 | 57.38 | 0.27 | 42.35 | 62.67 | 87.31 | 0.233 |
| FaceLifting_60 | 2210 | 48.33 | 0.27 | 51.4 | 67.2 | 92.76 | 0.313 |
| FaceLifting_90 | 2210 | 40.32 | 0.27 | 59.41 | 71.2 | 95.02 | 0.391 |
| Whitening_30 | 2210 | 51.27 | 0.32 | 48.42 | 65.7 | 84.84 | 0.198 |
| Whitening_60 | 2210 | 38.73 | 0.32 | 60.95 | 71.97 | 87.38 | 0.399 |
| Whitening_90 | 2210 | 29.1 | 0.36 | 70.54 | 76.77 | 92.53 | 0.579 |
| Smoothing_30 | 2210 | 19.77 | 0.23 | 80.0 | 81.5 | 95.84 | 0.69 |
| Smoothing_60 | 2210 | 3.67 | 0.23 | 96.11 | 89.55 | 98.91 | 0.94 |
| Smoothing_90 | 2210 | 4.62 | 0.18 | 95.2 | 89.1 | 98.55 | 0.944 |

## FF++ / cross-dataset
{"indomain": {"real": 84.73, "fake": 69.83, "filter": 86.4}, "FA": 5.24, "real_to_filter": 10.03, "MISS": 4.75, "heldout13": {"filter": 77.74, "fake": 14.21, "paired_excess_pp": 67.71}, "cdf": {"auc": 0.8197, "real_called_fake": 7.93}, "dfd": {"auc": 0.9387, "real_called_fake": 2.76}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
