# RU clipe5awpf_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 1.95, 'fake': 13.57, 'filter': 84.48} | pooled {'n': 26519, 'to_real': 1.99, 'to_fake': 16.95, 'to_filter': 81.06, 'balanced_acc': 48.29, 'paired_rank': 51.6}
Eq.4 {'TP': {'eye': 0.0, 'jaw': 0.056, 'white': 0.003, 'smooth': 0.59}, 'TN_same_image': {'eye': 0.915, 'jaw': 0.986, 'white': 0.945, 'smooth': 0.989}, 'AC': {'eye': 0.0, 'jaw': 0.056, 'white': 0.003, 'smooth': 0.59}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 1.0, 'jaw': 0.958, 'white': 0.994, 'smooth': 0.99}
quantities {"eye": {"n": 6629, "spearman": -0.015, "mae": 0.0777, "pred_mean": -0.0249, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0932, "orig_pred_mean": -0.0315}, "jaw": {"n": 6630, "spearman": 0.027, "mae": 0.0698, "pred_mean": 0.0634, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0871, "orig_pred_mean": 0.0603}, "white": {"n": 6630, "spearman": 0.059, "mae": 0.4648, "pred_mean": 0.1263, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0774, "orig_pred_mean": 0.1193}, "smooth": {"n": 6630, "spearman": 0.29, "mae": 0.1592, "pred_mean": 0.0669, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.151, "orig_pred_mean": -0.0371}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 2.85 | 12.9 | 84.25 | 49.89 | 57.9 | 0.0 |
| EyeEnlarging_60 | 2209 | 2.13 | 13.63 | 84.25 | 49.88 | 58.24 | 0.0 |
| EyeEnlarging_90 | 2210 | 1.76 | 16.02 | 82.22 | 48.87 | 55.25 | 0.0 |
| FaceLifting_30 | 2210 | 3.39 | 12.53 | 84.07 | 49.8 | 55.57 | 0.053 |
| FaceLifting_60 | 2210 | 3.12 | 12.94 | 83.94 | 49.73 | 55.48 | 0.056 |
| FaceLifting_90 | 2210 | 2.99 | 13.57 | 83.44 | 49.48 | 53.33 | 0.059 |
| Whitening_30 | 2210 | 3.21 | 12.9 | 83.89 | 49.71 | 52.85 | 0.005 |
| Whitening_60 | 2210 | 2.4 | 13.71 | 83.89 | 49.71 | 58.64 | 0.003 |
| Whitening_90 | 2210 | 1.22 | 13.89 | 84.89 | 50.2 | 64.75 | 0.002 |
| Smoothing_30 | 2210 | 0.86 | 21.22 | 77.92 | 46.72 | 38.78 | 0.221 |
| Smoothing_60 | 2210 | 0.0 | 26.52 | 73.48 | 44.5 | 38.37 | 0.72 |
| Smoothing_90 | 2210 | 0.0 | 33.57 | 66.43 | 40.97 | 30.05 | 0.829 |

## FF++ / cross-dataset
{"indomain": {"real": 74.16, "fake": 94.06, "filter": 80.7}, "FA": 9.73, "real_to_filter": 18.39, "MISS": 0.72, "heldout13": {"filter": 76.52, "fake": 16.34, "paired_excess_pp": 58.13}, "cdf": {"auc": 0.8745, "real_called_fake": 14.16}, "dfd": {"auc": 0.9573, "real_called_fake": 4.56}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
