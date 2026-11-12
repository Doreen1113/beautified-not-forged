# RU clipe5fbp0E_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 66.92, 'fake': 13.76, 'filter': 19.32} | pooled {'n': 26519, 'to_real': 58.63, 'to_fake': 27.39, 'to_filter': 13.98, 'balanced_acc': 47.33, 'paired_rank': 28.24}
Eq.4 {'TP': {'eye': 0.781, 'jaw': 0.32, 'white': 0.716, 'smooth': 0.743}, 'TN_same_image': {'eye': 0.064, 'jaw': 0.016, 'white': 0.046, 'smooth': 0.029}, 'AC': {'eye': 0.053, 'jaw': 0.006, 'white': 0.033, 'smooth': 0.022}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.225, 'jaw': 0.668, 'white': 0.261, 'smooth': 0.33}
quantities {"eye": {"n": 6629, "spearman": -0.015, "mae": 0.4114, "pred_mean": -0.1973, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4074, "orig_pred_mean": -0.1708}, "jaw": {"n": 6630, "spearman": 0.006, "mae": 0.3237, "pred_mean": 0.1019, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4281, "orig_pred_mean": 0.0757}, "white": {"n": 6630, "spearman": -0.014, "mae": 0.9603, "pred_mean": -0.4083, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.3722, "orig_pred_mean": -0.3996}, "smooth": {"n": 6630, "spearman": -0.269, "mae": 0.6431, "pred_mean": -0.4187, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3962, "orig_pred_mean": -0.1935}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 67.29 | 13.35 | 19.37 | 50.02 | 46.31 | 0.784 |
| EyeEnlarging_60 | 2209 | 67.45 | 13.99 | 18.56 | 49.62 | 43.87 | 0.781 |
| EyeEnlarging_90 | 2210 | 67.01 | 15.84 | 17.15 | 48.91 | 40.18 | 0.778 |
| FaceLifting_30 | 2210 | 68.1 | 13.57 | 18.33 | 49.5 | 41.06 | 0.325 |
| FaceLifting_60 | 2210 | 67.96 | 14.16 | 17.87 | 49.28 | 35.93 | 0.322 |
| FaceLifting_90 | 2210 | 68.33 | 15.57 | 16.11 | 48.39 | 31.0 | 0.314 |
| Whitening_30 | 2210 | 68.01 | 14.03 | 17.96 | 49.32 | 37.74 | 0.727 |
| Whitening_60 | 2210 | 67.38 | 16.43 | 16.2 | 48.44 | 30.09 | 0.719 |
| Whitening_90 | 2210 | 68.46 | 18.51 | 13.03 | 46.86 | 24.16 | 0.704 |
| Smoothing_30 | 2210 | 51.4 | 38.87 | 9.73 | 45.2 | 6.29 | 0.697 |
| Smoothing_60 | 2210 | 25.57 | 71.99 | 2.44 | 41.56 | 1.45 | 0.751 |
| Smoothing_90 | 2210 | 16.61 | 82.35 | 1.04 | 40.86 | 0.81 | 0.781 |

## FF++ / cross-dataset
{"indomain": {"real": 81.76, "fake": 87.01, "filter": 7.52}, "FA": 20.36, "real_to_filter": 11.7, "MISS": 5.38, "heldout13": {"filter": 7.83, "fake": 21.12, "paired_excess_pp": -3.87}, "cdf": {"auc": 0.9079, "real_called_fake": 12.44}, "dfd": {"auc": 0.9691, "real_called_fake": 5.99}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
