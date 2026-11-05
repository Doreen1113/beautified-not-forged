# RU clipe5fb_s20261001

## Alibaba (blind)
orig real/fake/filter {'real': 71.86, 'fake': 12.17, 'filter': 15.97} | pooled {'n': 26519, 'to_real': 71.33, 'to_fake': 12.75, 'to_filter': 15.91, 'balanced_acc': 49.97, 'paired_rank': 47.34}
Eq.4 {'TP': {'eye': 0.194, 'jaw': 0.735, 'white': 0.611, 'smooth': 0.244}, 'TN_same_image': {'eye': 0.126, 'jaw': 0.223, 'white': 0.129, 'smooth': 0.084}, 'AC': {'eye': 0.035, 'jaw': 0.136, 'white': 0.054, 'smooth': 0.022}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.808, 'jaw': 0.243, 'white': 0.391, 'smooth': 0.737}
quantities {"eye": {"n": 6629, "spearman": -0.045, "mae": 0.3983, "pred_mean": -0.126, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4581, "orig_pred_mean": -0.0879}, "jaw": {"n": 6630, "spearman": -0.025, "mae": 0.6588, "pred_mean": -0.6193, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.3609, "orig_pred_mean": -0.6209}, "white": {"n": 6630, "spearman": -0.081, "mae": 0.6793, "pred_mean": -0.0006, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4728, "orig_pred_mean": -0.0035}, "smooth": {"n": 6630, "spearman": -0.021, "mae": 0.4396, "pred_mean": -0.1691, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.467, "orig_pred_mean": -0.1709}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 73.94 | 10.68 | 15.38 | 49.71 | 45.97 | 0.177 |
| EyeEnlarging_60 | 2209 | 74.65 | 10.86 | 14.49 | 49.26 | 42.64 | 0.188 |
| EyeEnlarging_90 | 2210 | 74.89 | 11.76 | 13.35 | 48.69 | 37.65 | 0.216 |
| FaceLifting_30 | 2210 | 74.34 | 11.04 | 14.62 | 49.32 | 44.93 | 0.752 |
| FaceLifting_60 | 2210 | 73.85 | 11.09 | 15.07 | 49.55 | 40.88 | 0.731 |
| FaceLifting_90 | 2210 | 73.62 | 12.13 | 14.25 | 49.14 | 39.05 | 0.721 |
| Whitening_30 | 2210 | 73.48 | 11.0 | 15.52 | 49.78 | 50.9 | 0.61 |
| Whitening_60 | 2210 | 72.62 | 12.17 | 15.2 | 49.62 | 49.73 | 0.611 |
| Whitening_90 | 2210 | 72.08 | 12.58 | 15.34 | 49.68 | 50.9 | 0.612 |
| Smoothing_30 | 2210 | 66.06 | 15.75 | 18.19 | 51.11 | 54.71 | 0.243 |
| Smoothing_60 | 2210 | 64.3 | 16.11 | 19.59 | 51.81 | 56.02 | 0.238 |
| Smoothing_90 | 2210 | 62.17 | 17.87 | 19.95 | 51.99 | 54.71 | 0.251 |

## FF++ / cross-dataset
{"indomain": {"real": 87.61, "fake": 95.51, "filter": 8.66}, "FA": 10.33, "real_to_filter": 5.09, "MISS": 4.38, "heldout13": {"filter": 10.64, "fake": 21.43, "paired_excess_pp": 5.55}, "cdf": {"auc": 0.8846, "real_called_fake": 19.96}, "dfd": {"auc": 0.9535, "real_called_fake": 2.81}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
