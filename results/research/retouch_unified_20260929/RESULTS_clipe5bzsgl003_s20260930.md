# RU clipe5bzsgl003_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 92.53, 'fake': 0.45, 'filter': 7.01} | pooled {'n': 26519, 'to_real': 96.66, 'to_fake': 0.58, 'to_filter': 2.76, 'balanced_acc': 47.88, 'paired_rank': 21.99}
Eq.4 {'TP': {'eye': 0.501, 'jaw': 0.932, 'white': 0.322, 'smooth': 0.963}, 'TN_same_image': {'eye': 0.007, 'jaw': 0.033, 'white': 0.001, 'smooth': 0.004}, 'AC': {'eye': 0.005, 'jaw': 0.031, 'white': 0.001, 'smooth': 0.004}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.652, 'jaw': 0.043, 'white': 0.629, 'smooth': 0.061}
quantities {"eye": {"n": 6629, "spearman": 0.041, "mae": 1.5653, "pred_mean": -1.5396, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.5727, "orig_pred_mean": -1.6455}, "jaw": {"n": 6630, "spearman": 0.014, "mae": 0.8569, "pred_mean": -0.8347, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.7765, "orig_pred_mean": -0.8277}, "white": {"n": 6630, "spearman": 0.012, "mae": 0.7664, "pred_mean": -0.2118, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.9728, "orig_pred_mean": -0.1845}, "smooth": {"n": 6630, "spearman": 0.089, "mae": 0.3353, "pred_mean": 0.2339, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.7987, "orig_pred_mean": 0.5846}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 95.25 | 0.45 | 4.3 | 48.64 | 23.03 | 0.464 |
| EyeEnlarging_60 | 2209 | 96.11 | 0.5 | 3.4 | 48.19 | 20.42 | 0.506 |
| EyeEnlarging_90 | 2210 | 96.7 | 0.54 | 2.76 | 47.88 | 19.82 | 0.533 |
| FaceLifting_30 | 2210 | 94.66 | 0.5 | 4.84 | 48.92 | 29.48 | 0.935 |
| FaceLifting_60 | 2210 | 95.43 | 0.41 | 4.16 | 48.58 | 25.57 | 0.934 |
| FaceLifting_90 | 2210 | 95.97 | 0.45 | 3.57 | 48.28 | 22.81 | 0.926 |
| Whitening_30 | 2210 | 95.93 | 0.5 | 3.57 | 48.28 | 22.31 | 0.335 |
| Whitening_60 | 2210 | 97.51 | 0.45 | 2.04 | 47.51 | 19.77 | 0.319 |
| Whitening_90 | 2210 | 97.96 | 0.72 | 1.31 | 47.15 | 19.32 | 0.311 |
| Smoothing_30 | 2210 | 97.83 | 0.45 | 1.72 | 47.35 | 20.27 | 0.943 |
| Smoothing_60 | 2210 | 98.51 | 0.86 | 0.63 | 46.81 | 20.0 | 0.971 |
| Smoothing_90 | 2210 | 98.05 | 1.09 | 0.86 | 46.92 | 21.13 | 0.975 |

## FF++ / cross-dataset
{"indomain": {"real": 44.0, "fake": 94.76, "filter": 19.38}, "FA": 13.3, "real_to_filter": 43.77, "MISS": 2.47, "heldout13": {"filter": 12.31, "fake": 22.34, "paired_excess_pp": -31.46}, "cdf": {"auc": 0.8765, "real_called_fake": 29.01}, "dfd": {"auc": 0.9559, "real_called_fake": 7.84}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
