# RU clipe5fbE_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 67.96, 'fake': 12.76, 'filter': 19.28} | pooled {'n': 26519, 'to_real': 63.26, 'to_fake': 22.19, 'to_filter': 14.55, 'balanced_acc': 47.64, 'paired_rank': 32.67}
Eq.4 {'TP': {'eye': 0.768, 'jaw': 0.292, 'white': 0.725, 'smooth': 0.784}, 'TN_same_image': {'eye': 0.063, 'jaw': 0.021, 'white': 0.048, 'smooth': 0.03}, 'AC': {'eye': 0.05, 'jaw': 0.006, 'white': 0.032, 'smooth': 0.022}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.238, 'jaw': 0.694, 'white': 0.255, 'smooth': 0.326}
quantities {"eye": {"n": 6629, "spearman": -0.011, "mae": 0.4174, "pred_mean": -0.2318, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4056, "orig_pred_mean": -0.2125}, "jaw": {"n": 6630, "spearman": 0.002, "mae": 0.3168, "pred_mean": 0.0721, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4288, "orig_pred_mean": 0.0466}, "white": {"n": 6630, "spearman": -0.007, "mae": 0.9617, "pred_mean": -0.4115, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.3692, "orig_pred_mean": -0.4062}, "smooth": {"n": 6630, "spearman": -0.197, "mae": 0.5862, "pred_mean": -0.3612, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3845, "orig_pred_mean": -0.2087}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 68.28 | 12.08 | 19.64 | 50.18 | 52.74 | 0.771 |
| EyeEnlarging_60 | 2209 | 68.13 | 12.81 | 19.06 | 49.89 | 48.85 | 0.768 |
| EyeEnlarging_90 | 2210 | 68.19 | 13.48 | 18.33 | 49.52 | 45.27 | 0.765 |
| FaceLifting_30 | 2210 | 68.69 | 12.26 | 19.05 | 49.88 | 46.7 | 0.298 |
| FaceLifting_60 | 2210 | 69.05 | 12.67 | 18.28 | 49.5 | 41.15 | 0.295 |
| FaceLifting_90 | 2210 | 69.23 | 13.85 | 16.92 | 48.82 | 36.18 | 0.283 |
| Whitening_30 | 2210 | 69.5 | 12.13 | 18.37 | 49.55 | 44.55 | 0.73 |
| Whitening_60 | 2210 | 70.41 | 13.21 | 16.38 | 48.55 | 35.14 | 0.724 |
| Whitening_90 | 2210 | 70.77 | 15.48 | 13.76 | 47.24 | 28.64 | 0.722 |
| Smoothing_30 | 2210 | 59.82 | 30.36 | 9.82 | 45.27 | 7.51 | 0.724 |
| Smoothing_60 | 2210 | 43.98 | 52.76 | 3.26 | 41.99 | 3.21 | 0.797 |
| Smoothing_90 | 2210 | 33.08 | 65.16 | 1.76 | 41.24 | 2.08 | 0.832 |

## FF++ / cross-dataset
{"indomain": {"real": 84.8, "fake": 82.33, "filter": 7.67}, "FA": 11.4, "real_to_filter": 10.33, "MISS": 8.25, "heldout13": {"filter": 7.14, "fake": 13.83, "paired_excess_pp": -3.19}, "cdf": {"auc": 0.8975, "real_called_fake": 7.08}, "dfd": {"auc": 0.9707, "real_called_fake": 3.23}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
