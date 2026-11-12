# RU clipe5fbn_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 56.15, 'fake': 15.57, 'filter': 28.28} | pooled {'n': 26519, 'to_real': 49.36, 'to_fake': 27.7, 'to_filter': 22.94, 'balanced_acc': 47.33, 'paired_rank': 39.98}
Eq.4 {'TP': {'eye': 0.761, 'jaw': 0.475, 'white': 0.789, 'smooth': 0.875}, 'TN_same_image': {'eye': 0.018, 'jaw': 0.011, 'white': 0.024, 'smooth': 0.02}, 'AC': {'eye': 0.013, 'jaw': 0.004, 'white': 0.02, 'smooth': 0.016}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.268, 'jaw': 0.541, 'white': 0.205, 'smooth': 0.138}
quantities {"eye": {"n": 6629, "spearman": -0.056, "mae": 0.5778, "pred_mean": -0.4977, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4422, "orig_pred_mean": -0.4896}, "jaw": {"n": 6630, "spearman": 0.005, "mae": 0.382, "pred_mean": -0.2138, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4971, "orig_pred_mean": -0.217}, "white": {"n": 6630, "spearman": -0.034, "mae": 0.5676, "pred_mean": 0.5192, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4193, "orig_pred_mean": 0.5249}, "smooth": {"n": 6630, "spearman": -0.182, "mae": 0.504, "pred_mean": -0.2595, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.5545, "orig_pred_mean": -0.1801}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 56.65 | 13.98 | 29.37 | 50.54 | 57.58 | 0.758 |
| EyeEnlarging_60 | 2209 | 56.59 | 14.35 | 29.06 | 50.39 | 54.41 | 0.762 |
| EyeEnlarging_90 | 2210 | 56.88 | 14.89 | 28.24 | 49.98 | 51.88 | 0.762 |
| FaceLifting_30 | 2210 | 57.33 | 14.03 | 28.64 | 50.18 | 52.74 | 0.472 |
| FaceLifting_60 | 2210 | 57.19 | 15.11 | 27.69 | 49.71 | 48.71 | 0.473 |
| FaceLifting_90 | 2210 | 56.38 | 16.24 | 27.38 | 49.55 | 45.77 | 0.479 |
| Whitening_30 | 2210 | 57.56 | 15.02 | 27.42 | 49.57 | 49.43 | 0.8 |
| Whitening_60 | 2210 | 56.2 | 16.83 | 26.97 | 49.34 | 48.48 | 0.791 |
| Whitening_90 | 2210 | 55.75 | 17.6 | 26.65 | 49.19 | 47.49 | 0.778 |
| Smoothing_30 | 2210 | 45.7 | 38.42 | 15.88 | 43.8 | 15.68 | 0.85 |
| Smoothing_60 | 2210 | 23.53 | 71.4 | 5.07 | 38.39 | 5.11 | 0.88 |
| Smoothing_90 | 2210 | 12.62 | 84.48 | 2.9 | 37.31 | 2.53 | 0.896 |

## FF++ / cross-dataset
{"indomain": {"real": 18.09, "fake": 95.06, "filter": 64.13}, "FA": 18.92, "real_to_filter": 73.86, "MISS": 0.81, "heldout13": {"filter": 58.66, "fake": 25.08, "paired_excess_pp": -15.2}, "cdf": {"auc": 0.8811, "real_called_fake": 20.46}, "dfd": {"auc": 0.9521, "real_called_fake": 2.07}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
