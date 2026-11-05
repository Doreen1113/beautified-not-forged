# RU clipe5f_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 4.98, 'fake': 15.93, 'filter': 79.1} | pooled {'n': 26519, 'to_real': 4.18, 'to_fake': 16.78, 'to_filter': 79.04, 'balanced_acc': 49.97, 'paired_rank': 56.21}
Eq.4 {'TP': {'eye': 0.0, 'jaw': 0.119, 'white': 0.003, 'smooth': 0.643}, 'TN_same_image': {'eye': 0.824, 'jaw': 0.98, 'white': 0.901, 'smooth': 0.97}, 'AC': {'eye': 0.0, 'jaw': 0.119, 'white': 0.003, 'smooth': 0.643}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 1.0, 'jaw': 0.902, 'white': 0.994, 'smooth': 0.981}
quantities {"eye": {"n": 6629, "spearman": -0.05, "mae": 0.077, "pred_mean": -0.0473, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0491, "orig_pred_mean": -0.0467}, "jaw": {"n": 6630, "spearman": 0.024, "mae": 0.0449, "pred_mean": -0.0084, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0534, "orig_pred_mean": -0.0103}, "white": {"n": 6630, "spearman": 0.103, "mae": 0.5089, "pred_mean": 0.03, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0515, "orig_pred_mean": 0.0293}, "smooth": {"n": 6630, "spearman": 0.267, "mae": 0.1021, "pred_mean": 0.1415, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0692, "orig_pred_mean": 0.0605}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 6.15 | 13.76 | 80.09 | 50.5 | 57.29 | 0.0 |
| EyeEnlarging_60 | 2209 | 5.25 | 13.08 | 81.67 | 51.28 | 62.27 | 0.0 |
| EyeEnlarging_90 | 2210 | 4.62 | 13.57 | 81.81 | 51.35 | 65.14 | 0.0 |
| FaceLifting_30 | 2210 | 6.92 | 14.34 | 78.73 | 49.82 | 49.86 | 0.113 |
| FaceLifting_60 | 2210 | 6.2 | 14.66 | 79.14 | 50.02 | 52.26 | 0.119 |
| FaceLifting_90 | 2210 | 6.24 | 14.93 | 78.82 | 49.86 | 52.87 | 0.125 |
| Whitening_30 | 2210 | 5.57 | 14.84 | 79.59 | 50.25 | 55.88 | 0.004 |
| Whitening_60 | 2210 | 4.3 | 14.84 | 80.86 | 50.88 | 61.58 | 0.003 |
| Whitening_90 | 2210 | 2.31 | 15.29 | 82.4 | 51.65 | 65.14 | 0.002 |
| Smoothing_30 | 2210 | 2.4 | 23.12 | 74.48 | 47.69 | 42.92 | 0.267 |
| Smoothing_60 | 2210 | 0.14 | 22.85 | 77.01 | 48.96 | 56.7 | 0.782 |
| Smoothing_90 | 2210 | 0.05 | 26.11 | 73.85 | 47.37 | 52.67 | 0.882 |

## FF++ / cross-dataset
{"indomain": {"real": 77.36, "fake": 91.95, "filter": 80.85}, "FA": 7.67, "real_to_filter": 18.16, "MISS": 1.16, "heldout13": {"filter": 75.68, "fake": 17.4, "paired_excess_pp": 57.52}, "cdf": {"auc": 0.8986, "real_called_fake": 11.71}, "dfd": {"auc": 0.9587, "real_called_fake": 2.97}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
