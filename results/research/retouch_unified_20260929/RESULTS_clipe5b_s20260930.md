# RU clipe5b_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 91.4, 'fake': 0.59, 'filter': 8.01} | pooled {'n': 26519, 'to_real': 92.31, 'to_fake': 0.45, 'to_filter': 7.24, 'balanced_acc': 49.61, 'paired_rank': 39.88}
Eq.4 {'TP': {'eye': 0.94, 'jaw': 0.478, 'white': 0.789, 'smooth': 0.784}, 'TN_same_image': {'eye': 0.008, 'jaw': 0.003, 'white': 0.009, 'smooth': 0.003}, 'AC': {'eye': 0.007, 'jaw': 0.002, 'white': 0.008, 'smooth': 0.002}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.086, 'jaw': 0.511, 'white': 0.2, 'smooth': 0.15}
quantities {"eye": {"n": 6629, "spearman": -0.097, "mae": 0.5752, "pred_mean": -0.5418, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4732, "orig_pred_mean": -0.5349}, "jaw": {"n": 6630, "spearman": -0.004, "mae": 0.2769, "pred_mean": -0.1307, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.5645, "orig_pred_mean": -0.1206}, "white": {"n": 6630, "spearman": -0.075, "mae": 0.6546, "pred_mean": 0.8879, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.3529, "orig_pred_mean": 0.8726}, "smooth": {"n": 6630, "spearman": 0.005, "mae": 0.348, "pred_mean": -0.1264, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.6612, "orig_pred_mean": -0.1379}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 92.04 | 0.45 | 7.51 | 49.75 | 41.29 | 0.942 |
| EyeEnlarging_60 | 2209 | 92.44 | 0.5 | 7.06 | 49.53 | 40.09 | 0.94 |
| EyeEnlarging_90 | 2210 | 92.71 | 0.45 | 6.83 | 49.41 | 39.82 | 0.938 |
| FaceLifting_30 | 2210 | 92.17 | 0.45 | 7.38 | 49.68 | 39.77 | 0.476 |
| FaceLifting_60 | 2210 | 92.17 | 0.59 | 7.24 | 49.61 | 37.94 | 0.473 |
| FaceLifting_90 | 2210 | 92.58 | 0.5 | 6.92 | 49.46 | 39.19 | 0.485 |
| Whitening_30 | 2210 | 91.99 | 0.5 | 7.51 | 49.75 | 39.32 | 0.806 |
| Whitening_60 | 2210 | 91.86 | 0.54 | 7.6 | 49.8 | 39.82 | 0.786 |
| Whitening_90 | 2210 | 92.26 | 0.5 | 7.24 | 49.61 | 41.2 | 0.776 |
| Smoothing_30 | 2210 | 92.49 | 0.18 | 7.33 | 49.66 | 36.33 | 0.811 |
| Smoothing_60 | 2210 | 93.03 | 0.27 | 6.7 | 49.34 | 39.39 | 0.782 |
| Smoothing_90 | 2210 | 92.04 | 0.45 | 7.51 | 49.75 | 44.37 | 0.759 |

## FF++ / cross-dataset
{"indomain": {"real": 45.06, "fake": 96.17, "filter": 43.09}, "FA": 13.98, "real_to_filter": 41.87, "MISS": 2.69, "heldout13": {"filter": 38.91, "fake": 24.09, "paired_excess_pp": -2.96}, "cdf": {"auc": 0.9231, "real_called_fake": 34.42}, "dfd": {"auc": 0.9625, "real_called_fake": 6.62}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
