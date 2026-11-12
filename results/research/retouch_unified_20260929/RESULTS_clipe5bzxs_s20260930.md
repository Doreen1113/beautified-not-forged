# RU clipe5bzxs_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 14.07, 'fake': 0.32, 'filter': 85.61} | pooled {'n': 26519, 'to_real': 12.96, 'to_fake': 0.35, 'to_filter': 86.69, 'balanced_acc': 50.54, 'paired_rank': 68.02}
Eq.4 {'TP': {'eye': 0.705, 'jaw': 0.047, 'white': 0.67, 'smooth': 0.982}, 'TN_same_image': {'eye': 0.0, 'jaw': 0.0, 'white': 0.0, 'smooth': 0.063}, 'AC': {'eye': 0.0, 'jaw': 0.0, 'white': 0.0, 'smooth': 0.063}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.245, 'jaw': 0.954, 'white': 0.338, 'smooth': 0.014}
quantities {"eye": {"n": 6629, "spearman": 0.017, "mae": 0.7071, "pred_mean": -0.6813, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.9331, "orig_pred_mean": -0.6635}, "jaw": {"n": 6630, "spearman": -0.028, "mae": 0.7352, "pred_mean": -0.7131, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.9246, "orig_pred_mean": -0.7041}, "white": {"n": 6630, "spearman": -0.063, "mae": 1.043, "pred_mean": 1.4747, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.6735, "orig_pred_mean": 1.54}, "smooth": {"n": 6630, "spearman": 0.056, "mae": 0.4176, "pred_mean": 0.5886, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.9366, "orig_pred_mean": 0.5393}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 13.17 | 0.27 | 86.56 | 50.48 | 65.88 | 0.729 |
| EyeEnlarging_60 | 2209 | 14.71 | 0.32 | 84.97 | 49.68 | 60.21 | 0.706 |
| EyeEnlarging_90 | 2210 | 15.43 | 0.32 | 84.25 | 49.32 | 57.94 | 0.679 |
| FaceLifting_30 | 2210 | 12.44 | 0.32 | 87.24 | 50.81 | 73.1 | 0.047 |
| FaceLifting_60 | 2210 | 12.04 | 0.32 | 87.65 | 51.02 | 69.8 | 0.047 |
| FaceLifting_90 | 2210 | 12.22 | 0.27 | 87.51 | 50.95 | 66.2 | 0.046 |
| Whitening_30 | 2210 | 11.31 | 0.32 | 88.37 | 51.38 | 71.76 | 0.714 |
| Whitening_60 | 2210 | 11.54 | 0.32 | 88.14 | 51.27 | 64.71 | 0.685 |
| Whitening_90 | 2210 | 13.44 | 0.36 | 86.2 | 50.29 | 59.12 | 0.613 |
| Smoothing_30 | 2210 | 11.0 | 0.41 | 88.6 | 51.49 | 78.55 | 0.987 |
| Smoothing_60 | 2210 | 12.94 | 0.5 | 86.56 | 50.48 | 75.88 | 0.983 |
| Smoothing_90 | 2210 | 15.29 | 0.5 | 84.21 | 49.3 | 73.03 | 0.976 |

## FF++ / cross-dataset
{"indomain": {"real": 12.54, "fake": 55.47, "filter": 49.54}, "FA": 13.07, "real_to_filter": 83.89, "MISS": 10.5, "heldout13": {"filter": 44.68, "fake": 22.72, "paired_excess_pp": -39.21}, "cdf": {"auc": 0.8234, "real_called_fake": 4.63}, "dfd": {"auc": 0.9328, "real_called_fake": 0.58}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
