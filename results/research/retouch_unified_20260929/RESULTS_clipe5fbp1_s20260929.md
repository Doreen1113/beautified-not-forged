# RU clipe5fbp1_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 9.64, 'fake': 12.94, 'filter': 77.42} | pooled {'n': 26519, 'to_real': 10.47, 'to_fake': 13.21, 'to_filter': 76.32, 'balanced_acc': 49.45, 'paired_rank': 47.69}
Eq.4 {'TP': {'eye': 0.047, 'jaw': 0.852, 'white': 0.163, 'smooth': 0.015}, 'TN_same_image': {'eye': 0.122, 'jaw': 0.763, 'white': 0.161, 'smooth': 0.085}, 'AC': {'eye': 0.007, 'jaw': 0.654, 'white': 0.022, 'smooth': 0.002}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.953, 'jaw': 0.144, 'white': 0.838, 'smooth': 0.981}
quantities {"eye": {"n": 6629, "spearman": -0.105, "mae": 0.3504, "pred_mean": -0.1265, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4561, "orig_pred_mean": -0.1233}, "jaw": {"n": 6630, "spearman": -0.002, "mae": 0.3574, "pred_mean": -0.1926, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4538, "orig_pred_mean": -0.1859}, "white": {"n": 6630, "spearman": 0.013, "mae": 0.5506, "pred_mean": 0.3011, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4032, "orig_pred_mean": 0.2938}, "smooth": {"n": 6630, "spearman": 0.053, "mae": 0.4939, "pred_mean": 0.6157, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.355, "orig_pred_mean": 0.5179}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 9.46 | 12.67 | 77.87 | 50.23 | 52.22 | 0.047 |
| EyeEnlarging_60 | 2209 | 9.55 | 12.95 | 77.5 | 50.04 | 54.19 | 0.047 |
| EyeEnlarging_90 | 2210 | 8.96 | 13.53 | 77.51 | 50.05 | 54.19 | 0.046 |
| FaceLifting_30 | 2210 | 9.59 | 12.62 | 77.78 | 50.18 | 51.63 | 0.856 |
| FaceLifting_60 | 2210 | 8.96 | 13.12 | 77.92 | 50.25 | 53.71 | 0.852 |
| FaceLifting_90 | 2210 | 8.87 | 14.07 | 77.06 | 49.82 | 54.41 | 0.848 |
| Whitening_30 | 2210 | 10.59 | 13.57 | 75.84 | 49.21 | 42.71 | 0.173 |
| Whitening_60 | 2210 | 11.95 | 13.76 | 74.3 | 48.44 | 39.91 | 0.166 |
| Whitening_90 | 2210 | 14.16 | 13.71 | 72.13 | 47.35 | 37.69 | 0.149 |
| Smoothing_30 | 2210 | 10.32 | 16.83 | 72.85 | 47.72 | 39.77 | 0.015 |
| Smoothing_60 | 2210 | 11.45 | 11.4 | 77.15 | 49.86 | 46.43 | 0.015 |
| Smoothing_90 | 2210 | 11.81 | 10.32 | 77.87 | 50.23 | 45.38 | 0.014 |

## FF++ / cross-dataset
{"indomain": {"real": 5.7, "fake": 96.59, "filter": 84.8}, "FA": 6.53, "real_to_filter": 82.52, "MISS": 1.75, "heldout13": {"filter": 78.72, "fake": 12.77, "paired_excess_pp": -3.8}, "cdf": {"auc": 0.8585, "real_called_fake": 28.79}, "dfd": {"auc": 0.9548, "real_called_fake": 8.0}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
