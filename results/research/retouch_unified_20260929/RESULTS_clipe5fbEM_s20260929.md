# RU clipe5fbEM_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 66.92, 'fake': 14.03, 'filter': 19.05} | pooled {'n': 26519, 'to_real': 63.11, 'to_fake': 20.98, 'to_filter': 15.91, 'balanced_acc': 48.43, 'paired_rank': 38.74}
Eq.4 {'TP': {'eye': 0.963, 'jaw': 0.07, 'white': 0.412, 'smooth': 0.182}, 'TN_same_image': {'eye': 0.537, 'jaw': 0.013, 'white': 0.029, 'smooth': 0.005}, 'AC': {'eye': 0.526, 'jaw': 0.001, 'white': 0.019, 'smooth': 0.001}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.034, 'jaw': 0.928, 'white': 0.587, 'smooth': 0.922}
quantities {"eye": {"n": 6629, "spearman": 0.045, "mae": 0.4478, "pred_mean": 0.3689, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4666, "orig_pred_mean": 0.3761}, "jaw": {"n": 6630, "spearman": -0.026, "mae": 0.6338, "pred_mean": -0.5694, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4203, "orig_pred_mean": -0.5723}, "white": {"n": 6630, "spearman": -0.027, "mae": 0.6061, "pred_mean": 0.1116, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.5154, "orig_pred_mean": 0.1465}, "smooth": {"n": 6630, "spearman": -0.018, "mae": 0.5303, "pred_mean": -0.2473, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.4893, "orig_pred_mean": -0.3288}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 69.68 | 12.35 | 17.96 | 49.46 | 52.53 | 0.965 |
| EyeEnlarging_60 | 2209 | 69.08 | 12.22 | 18.7 | 49.82 | 57.97 | 0.964 |
| EyeEnlarging_90 | 2210 | 66.65 | 12.31 | 21.04 | 51.0 | 62.76 | 0.961 |
| FaceLifting_30 | 2210 | 69.5 | 12.81 | 17.69 | 49.32 | 41.45 | 0.067 |
| FaceLifting_60 | 2210 | 70.0 | 13.03 | 16.97 | 48.96 | 41.54 | 0.07 |
| FaceLifting_90 | 2210 | 69.14 | 14.03 | 16.83 | 48.89 | 40.79 | 0.075 |
| Whitening_30 | 2210 | 69.82 | 12.58 | 17.6 | 49.28 | 44.5 | 0.396 |
| Whitening_60 | 2210 | 68.14 | 14.07 | 17.78 | 49.37 | 44.89 | 0.411 |
| Whitening_90 | 2210 | 64.75 | 16.24 | 19.0 | 49.98 | 46.2 | 0.43 |
| Smoothing_30 | 2210 | 60.86 | 26.79 | 12.35 | 46.65 | 14.89 | 0.111 |
| Smoothing_60 | 2210 | 44.98 | 46.7 | 8.33 | 44.64 | 9.59 | 0.192 |
| Smoothing_90 | 2210 | 34.75 | 58.6 | 6.65 | 43.8 | 7.74 | 0.243 |

## FF++ / cross-dataset
{"indomain": {"real": 50.76, "fake": 81.96, "filter": 40.27}, "FA": 11.7, "real_to_filter": 44.22, "MISS": 4.91, "heldout13": {"filter": 40.88, "fake": 15.2, "paired_excess_pp": -3.34}, "cdf": {"auc": 0.8895, "real_called_fake": 8.9}, "dfd": {"auc": 0.969, "real_called_fake": 2.23}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
