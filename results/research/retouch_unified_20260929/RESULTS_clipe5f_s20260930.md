# RU clipe5f_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 3.44, 'fake': 15.93, 'filter': 80.63} | pooled {'n': 26519, 'to_real': 2.86, 'to_fake': 17.67, 'to_filter': 79.47, 'balanced_acc': 49.42, 'paired_rank': 56.93}
Eq.4 {'TP': {'eye': 0.0, 'jaw': 0.021, 'white': 0.003, 'smooth': 0.631}, 'TN_same_image': {'eye': 0.949, 'jaw': 0.982, 'white': 0.973, 'smooth': 0.994}, 'AC': {'eye': 0.0, 'jaw': 0.021, 'white': 0.003, 'smooth': 0.631}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 1.0, 'jaw': 0.986, 'white': 0.993, 'smooth': 0.982}
quantities {"eye": {"n": 6629, "spearman": 0.086, "mae": 0.061, "pred_mean": -0.0289, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0446, "orig_pred_mean": -0.0354}, "jaw": {"n": 6630, "spearman": -0.025, "mae": 0.0492, "pred_mean": -0.0218, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0449, "orig_pred_mean": -0.0235}, "white": {"n": 6630, "spearman": -0.028, "mae": 0.5244, "pred_mean": 0.011, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.047, "orig_pred_mean": 0.0125}, "smooth": {"n": 6630, "spearman": 0.468, "mae": 0.1228, "pred_mean": 0.0709, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0592, "orig_pred_mean": -0.0331}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 3.71 | 14.39 | 81.9 | 50.64 | 64.25 | 0.0 |
| EyeEnlarging_60 | 2209 | 3.12 | 14.03 | 82.84 | 51.11 | 69.06 | 0.0 |
| EyeEnlarging_90 | 2210 | 2.44 | 13.98 | 83.57 | 51.47 | 70.59 | 0.0 |
| FaceLifting_30 | 2210 | 4.43 | 14.71 | 80.86 | 50.11 | 56.15 | 0.019 |
| FaceLifting_60 | 2210 | 4.3 | 14.12 | 81.58 | 50.48 | 56.47 | 0.021 |
| FaceLifting_90 | 2210 | 4.3 | 14.84 | 80.86 | 50.11 | 57.13 | 0.023 |
| Whitening_30 | 2210 | 3.89 | 14.89 | 81.22 | 50.3 | 55.48 | 0.004 |
| Whitening_60 | 2210 | 2.4 | 15.93 | 81.67 | 50.52 | 61.13 | 0.003 |
| Whitening_90 | 2210 | 1.76 | 16.88 | 81.36 | 50.36 | 65.02 | 0.001 |
| Smoothing_30 | 2210 | 3.76 | 24.07 | 72.17 | 45.77 | 32.53 | 0.238 |
| Smoothing_60 | 2210 | 0.18 | 25.02 | 74.8 | 47.08 | 50.63 | 0.778 |
| Smoothing_90 | 2210 | 0.05 | 29.19 | 70.77 | 45.07 | 44.71 | 0.876 |

## FF++ / cross-dataset
{"indomain": {"real": 82.67, "fake": 91.48, "filter": 81.31}, "FA": 5.47, "real_to_filter": 12.69, "MISS": 1.34, "heldout13": {"filter": 77.05, "fake": 13.6, "paired_excess_pp": 64.36}, "cdf": {"auc": 0.8756, "real_called_fake": 10.66}, "dfd": {"auc": 0.9533, "real_called_fake": 3.44}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": true, "D2_heldout_excess>=30": true}}
