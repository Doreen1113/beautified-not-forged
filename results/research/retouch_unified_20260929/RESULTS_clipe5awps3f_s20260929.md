# RU clipe5awps3f_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 6.79, 'fake': 13.08, 'filter': 80.14} | pooled {'n': 26519, 'to_real': 4.95, 'to_fake': 15.78, 'to_filter': 79.27, 'balanced_acc': 49.56, 'paired_rank': 59.32}
Eq.4 {'TP': {'eye': 0.0, 'jaw': 0.066, 'white': 0.002, 'smooth': 0.678}, 'TN_same_image': {'eye': 0.892, 'jaw': 0.982, 'white': 0.934, 'smooth': 0.989}, 'AC': {'eye': 0.0, 'jaw': 0.066, 'white': 0.002, 'smooth': 0.678}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 1.0, 'jaw': 0.956, 'white': 0.996, 'smooth': 0.977}
quantities {"eye": {"n": 6629, "spearman": 0.085, "mae": 0.052, "pred_mean": 0.006, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0681, "orig_pred_mean": -0.001}, "jaw": {"n": 6630, "spearman": 0.013, "mae": 0.0535, "pred_mean": -0.0047, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.063, "orig_pred_mean": -0.0041}, "white": {"n": 6630, "spearman": 0.085, "mae": 0.4709, "pred_mean": 0.0958, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0523, "orig_pred_mean": 0.0966}, "smooth": {"n": 6630, "spearman": 0.3, "mae": 0.1278, "pred_mean": 0.0935, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0983, "orig_pred_mean": 0.0157}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 6.56 | 10.68 | 82.76 | 51.31 | 70.84 | 0.0 |
| EyeEnlarging_60 | 2209 | 5.52 | 10.46 | 84.02 | 51.94 | 73.16 | 0.0 |
| EyeEnlarging_90 | 2210 | 4.98 | 11.58 | 83.44 | 51.65 | 72.76 | 0.0 |
| FaceLifting_30 | 2210 | 8.28 | 10.45 | 81.27 | 50.56 | 63.35 | 0.059 |
| FaceLifting_60 | 2210 | 7.6 | 11.09 | 81.31 | 50.59 | 64.16 | 0.067 |
| FaceLifting_90 | 2210 | 6.56 | 12.17 | 81.27 | 50.56 | 63.8 | 0.071 |
| Whitening_30 | 2210 | 8.42 | 11.04 | 80.54 | 50.2 | 59.32 | 0.003 |
| Whitening_60 | 2210 | 5.93 | 11.9 | 82.17 | 51.02 | 64.41 | 0.001 |
| Whitening_90 | 2210 | 3.26 | 13.17 | 83.57 | 51.72 | 65.41 | 0.001 |
| Smoothing_30 | 2210 | 2.31 | 21.4 | 76.29 | 48.07 | 40.0 | 0.331 |
| Smoothing_60 | 2210 | 0.0 | 27.24 | 72.76 | 46.31 | 42.04 | 0.804 |
| Smoothing_90 | 2210 | 0.0 | 38.19 | 61.81 | 40.83 | 32.58 | 0.899 |

## FF++ / cross-dataset
{"indomain": {"real": 77.96, "fake": 91.7, "filter": 77.66}, "FA": 10.18, "real_to_filter": 17.63, "MISS": 1.09, "heldout13": {"filter": 77.74, "fake": 14.82, "paired_excess_pp": 60.11}, "cdf": {"auc": 0.8495, "real_called_fake": 11.71}, "dfd": {"auc": 0.9605, "real_called_fake": 2.33}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
