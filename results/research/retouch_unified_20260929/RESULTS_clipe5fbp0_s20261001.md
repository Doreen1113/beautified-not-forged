# RU clipe5fbp0_s20261001

## Alibaba (blind)
orig real/fake/filter {'real': 57.74, 'fake': 22.4, 'filter': 19.86} | pooled {'n': 26519, 'to_real': 50.25, 'to_fake': 32.12, 'to_filter': 17.63, 'balanced_acc': 48.89, 'paired_rank': 44.87}
Eq.4 {'TP': {'eye': 0.31, 'jaw': 0.765, 'white': 0.739, 'smooth': 0.467}, 'TN_same_image': {'eye': 0.062, 'jaw': 0.076, 'white': 0.069, 'smooth': 0.042}, 'AC': {'eye': 0.029, 'jaw': 0.047, 'white': 0.043, 'smooth': 0.022}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.694, 'jaw': 0.212, 'white': 0.265, 'smooth': 0.55}
quantities {"eye": {"n": 6629, "spearman": -0.055, "mae": 0.4469, "pred_mean": -0.1929, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4923, "orig_pred_mean": -0.1453}, "jaw": {"n": 6630, "spearman": -0.035, "mae": 0.6863, "pred_mean": -0.6475, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4043, "orig_pred_mean": -0.6402}, "white": {"n": 6630, "spearman": -0.059, "mae": 0.8312, "pred_mean": -0.2299, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.5067, "orig_pred_mean": -0.2396}, "smooth": {"n": 6630, "spearman": 0.024, "mae": 0.4587, "pred_mean": -0.1992, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.5361, "orig_pred_mean": -0.1879}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 58.82 | 21.18 | 20.0 | 50.07 | 57.04 | 0.293 |
| EyeEnlarging_60 | 2209 | 59.21 | 21.68 | 19.1 | 49.62 | 51.7 | 0.305 |
| EyeEnlarging_90 | 2210 | 58.51 | 23.94 | 17.56 | 48.85 | 45.61 | 0.33 |
| FaceLifting_30 | 2210 | 59.41 | 20.77 | 19.82 | 49.98 | 54.93 | 0.778 |
| FaceLifting_60 | 2210 | 59.41 | 21.58 | 19.0 | 49.57 | 51.83 | 0.765 |
| FaceLifting_90 | 2210 | 59.1 | 22.26 | 18.64 | 49.39 | 50.36 | 0.753 |
| Whitening_30 | 2210 | 56.79 | 22.67 | 20.54 | 50.34 | 57.78 | 0.736 |
| Whitening_60 | 2210 | 54.57 | 24.71 | 20.72 | 50.43 | 52.76 | 0.736 |
| Whitening_90 | 2210 | 52.9 | 26.29 | 20.81 | 50.48 | 50.16 | 0.746 |
| Smoothing_30 | 2210 | 42.76 | 40.81 | 16.43 | 48.28 | 34.39 | 0.446 |
| Smoothing_60 | 2210 | 24.03 | 64.71 | 11.27 | 45.7 | 18.96 | 0.47 |
| Smoothing_90 | 2210 | 17.47 | 74.84 | 7.69 | 43.92 | 12.94 | 0.485 |

## FF++ / cross-dataset
{"indomain": {"real": 67.33, "fake": 97.0, "filter": 17.78}, "FA": 27.36, "real_to_filter": 20.14, "MISS": 0.41, "heldout13": {"filter": 20.9, "fake": 31.69, "paired_excess_pp": 0.76}, "cdf": {"auc": 0.9052, "real_called_fake": 37.29}, "dfd": {"auc": 0.9552, "real_called_fake": 11.55}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
