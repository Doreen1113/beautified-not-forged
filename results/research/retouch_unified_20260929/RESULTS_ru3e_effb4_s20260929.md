# RU ru3e_effb4_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 83.17, 'fake': 0.63, 'filter': 16.2} | pooled {'n': 26519, 'to_real': 37.31, 'to_fake': 0.49, 'to_filter': 62.19, 'balanced_acc': 73.0, 'paired_rank': 94.06}
Eq.4 {'TP': {'eye': 0.23, 'jaw': 0.284, 'white': 0.283, 'smooth': 0.951}, 'TN_same_image': {'eye': 0.809, 'jaw': 0.916, 'white': 0.762, 'smooth': 0.304}, 'AC': {'eye': 0.207, 'jaw': 0.251, 'white': 0.164, 'smooth': 0.266}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.989, 'jaw': 0.966, 'white': 0.961, 'smooth': 0.987}
quantities {"eye": {"n": 6629, "spearman": 0.468, "mae": 0.0254, "pred_mean": 0.0034, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0068, "orig_pred_mean": 0.0001}, "jaw": {"n": 6630, "spearman": 0.158, "mae": 0.0176, "pred_mean": 0.0032, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0059, "orig_pred_mean": 0.0003}, "white": {"n": 6630, "spearman": -0.168, "mae": 0.4994, "pred_mean": 0.0417, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.004, "orig_pred_mean": 0.0084}, "smooth": {"n": 6630, "spearman": 0.491, "mae": 0.0822, "pred_mean": 0.111, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0206, "orig_pred_mean": 0.0012}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 57.06 | 0.45 | 42.49 | 63.14 | 97.15 | 0.089 |
| EyeEnlarging_60 | 2209 | 42.6 | 0.41 | 56.99 | 70.4 | 98.91 | 0.242 |
| EyeEnlarging_90 | 2210 | 33.71 | 0.36 | 65.93 | 74.86 | 99.37 | 0.36 |
| FaceLifting_30 | 2210 | 62.53 | 0.41 | 37.06 | 60.43 | 84.46 | 0.217 |
| FaceLifting_60 | 2210 | 55.57 | 0.5 | 43.94 | 63.87 | 89.32 | 0.28 |
| FaceLifting_90 | 2210 | 49.64 | 0.41 | 49.95 | 66.88 | 93.03 | 0.355 |
| Whitening_30 | 2210 | 57.06 | 0.59 | 42.35 | 63.08 | 87.38 | 0.126 |
| Whitening_60 | 2210 | 45.84 | 0.68 | 53.48 | 68.64 | 89.66 | 0.286 |
| Whitening_90 | 2210 | 37.1 | 0.63 | 62.26 | 73.03 | 91.18 | 0.436 |
| Smoothing_30 | 2210 | 6.02 | 0.45 | 93.53 | 88.66 | 99.23 | 0.864 |
| Smoothing_60 | 2210 | 0.41 | 0.27 | 99.32 | 91.56 | 99.77 | 0.992 |
| Smoothing_90 | 2210 | 0.23 | 0.77 | 99.0 | 91.4 | 99.28 | 0.995 |

## FF++ / cross-dataset
{"indomain": {"real": 79.86, "fake": 94.0, "filter": 76.37}, "FA": 10.18, "real_to_filter": 13.6, "MISS": 0.31, "heldout13": {"filter": 43.09, "fake": 17.78, "paired_excess_pp": 29.49}, "cdf": {"auc": 0.8243, "real_called_fake": 29.92}, "dfd": {"auc": 0.9296, "real_called_fake": 7.47}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
