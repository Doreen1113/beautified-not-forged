# RU clipe5rf_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 3.8, 'fake': 12.85, 'filter': 83.35} | pooled {'n': 26519, 'to_real': 3.03, 'to_fake': 16.75, 'to_filter': 80.22, 'balanced_acc': 48.44, 'paired_rank': 49.49}
Eq.4 {'TP': {'eye': 0.0, 'jaw': 0.011, 'white': 0.005, 'smooth': 0.548}, 'TN_same_image': {'eye': 0.974, 'jaw': 0.986, 'white': 0.987, 'smooth': 0.997}, 'AC': {'eye': 0.0, 'jaw': 0.011, 'white': 0.005, 'smooth': 0.548}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 1.0, 'jaw': 0.993, 'white': 0.993, 'smooth': 0.993}
quantities {"eye": {"n": 6629, "spearman": 0.029, "mae": 0.0872, "pred_mean": -0.0444, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0683, "orig_pred_mean": -0.0584}, "jaw": {"n": 6630, "spearman": 0.017, "mae": 0.0644, "pred_mean": 0.0274, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0722, "orig_pred_mean": 0.0236}, "white": {"n": 6630, "spearman": -0.158, "mae": 0.5255, "pred_mean": 0.0288, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0751, "orig_pred_mean": 0.0487}, "smooth": {"n": 6630, "spearman": 0.333, "mae": 0.1274, "pred_mean": 0.1328, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.1375, "orig_pred_mean": 0.0135}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 4.43 | 11.54 | 84.03 | 50.34 | 51.49 | 0.0 |
| EyeEnlarging_60 | 2209 | 3.71 | 11.63 | 84.65 | 50.65 | 54.78 | 0.0 |
| EyeEnlarging_90 | 2210 | 3.35 | 12.08 | 84.57 | 50.61 | 56.02 | 0.0 |
| FaceLifting_30 | 2210 | 4.8 | 11.45 | 83.76 | 50.2 | 46.97 | 0.009 |
| FaceLifting_60 | 2210 | 4.43 | 12.13 | 83.44 | 50.04 | 47.15 | 0.01 |
| FaceLifting_90 | 2210 | 4.16 | 13.76 | 82.08 | 49.37 | 45.07 | 0.013 |
| Whitening_30 | 2210 | 4.75 | 11.9 | 83.35 | 50.0 | 47.17 | 0.006 |
| Whitening_60 | 2210 | 3.3 | 12.35 | 84.34 | 50.5 | 55.02 | 0.004 |
| Whitening_90 | 2210 | 1.95 | 13.35 | 84.71 | 50.68 | 62.13 | 0.004 |
| Smoothing_30 | 2210 | 1.45 | 21.13 | 77.42 | 47.04 | 45.79 | 0.166 |
| Smoothing_60 | 2210 | 0.05 | 30.36 | 69.59 | 43.12 | 45.48 | 0.671 |
| Smoothing_90 | 2210 | 0.0 | 39.28 | 60.72 | 38.69 | 36.83 | 0.808 |

## FF++ / cross-dataset
{"indomain": {"real": 82.37, "fake": 92.19, "filter": 73.18}, "FA": 10.26, "real_to_filter": 11.4, "MISS": 1.16, "heldout13": {"filter": 71.58, "fake": 18.62, "paired_excess_pp": 60.18}, "cdf": {"auc": 0.8725, "real_called_fake": 11.57}, "dfd": {"auc": 0.9657, "real_called_fake": 2.17}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
