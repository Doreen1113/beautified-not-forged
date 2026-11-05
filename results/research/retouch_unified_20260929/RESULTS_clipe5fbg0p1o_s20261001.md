# RU clipe5fbg0p1o_s20261001

## Alibaba (blind)
orig real/fake/filter {'real': 53.08, 'fake': 19.14, 'filter': 27.78} | pooled {'n': 26519, 'to_real': 56.05, 'to_fake': 17.17, 'to_filter': 26.78, 'balanced_acc': 49.5, 'paired_rank': 50.6}
Eq.4 {'TP': {'eye': 0.223, 'jaw': 0.723, 'white': 0.708, 'smooth': 0.55}, 'TN_same_image': {'eye': 0.082, 'jaw': 0.104, 'white': 0.099, 'smooth': 0.029}, 'AC': {'eye': 0.029, 'jaw': 0.056, 'white': 0.058, 'smooth': 0.012}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.794, 'jaw': 0.255, 'white': 0.278, 'smooth': 0.55}
quantities {"eye": {"n": 6629, "spearman": -0.06, "mae": 0.427, "pred_mean": -0.1544, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4266, "orig_pred_mean": -0.085}, "jaw": {"n": 6630, "spearman": -0.015, "mae": 0.5823, "pred_mean": -0.5275, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.3607, "orig_pred_mean": -0.5196}, "white": {"n": 6630, "spearman": -0.031, "mae": 0.6902, "pred_mean": -0.033, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4518, "orig_pred_mean": -0.0411}, "smooth": {"n": 6630, "spearman": -0.093, "mae": 0.3774, "pred_mean": -0.0884, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.4436, "orig_pred_mean": -0.1052}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 52.4 | 19.41 | 28.19 | 50.21 | 50.95 | 0.21 |
| EyeEnlarging_60 | 2209 | 53.24 | 20.05 | 26.71 | 49.46 | 45.68 | 0.219 |
| EyeEnlarging_90 | 2210 | 52.81 | 22.53 | 24.66 | 48.44 | 40.45 | 0.24 |
| FaceLifting_30 | 2210 | 53.03 | 18.73 | 28.24 | 50.23 | 53.87 | 0.741 |
| FaceLifting_60 | 2210 | 53.21 | 18.96 | 27.83 | 50.02 | 51.02 | 0.722 |
| FaceLifting_90 | 2210 | 52.67 | 20.72 | 26.61 | 49.41 | 48.71 | 0.708 |
| Whitening_30 | 2210 | 52.67 | 19.64 | 27.69 | 49.96 | 52.26 | 0.701 |
| Whitening_60 | 2210 | 52.81 | 20.41 | 26.79 | 49.5 | 48.55 | 0.71 |
| Whitening_90 | 2210 | 52.67 | 20.77 | 26.56 | 49.39 | 46.33 | 0.714 |
| Smoothing_30 | 2210 | 58.01 | 15.52 | 26.47 | 49.35 | 51.04 | 0.516 |
| Smoothing_60 | 2210 | 69.59 | 5.02 | 25.38 | 48.8 | 58.01 | 0.563 |
| Smoothing_90 | 2210 | 69.46 | 4.3 | 26.24 | 49.23 | 60.27 | 0.571 |

## FF++ / cross-dataset
{"indomain": {"real": 67.25, "fake": 95.98, "filter": 21.81}, "FA": 17.4, "real_to_filter": 23.48, "MISS": 34.19, "heldout13": {"filter": 23.63, "fake": 27.89, "paired_excess_pp": 0.15}, "cdf": {"auc": 0.9024, "real_called_fake": 45.17}, "dfd": {"auc": 0.9532, "real_called_fake": 7.95}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
