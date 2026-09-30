# RU effb4_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 93.39, 'fake': 0.77, 'filter': 5.84} | pooled {'n': 26519, 'to_real': 61.25, 'to_fake': 0.63, 'to_filter': 38.13, 'balanced_acc': 66.14, 'paired_rank': 92.82}
Eq.4 {'TP': {'eye': 0.248, 'jaw': 0.089, 'white': 0.095, 'smooth': 0.928}, 'TN_same_image': {'eye': 0.915, 'jaw': 0.94, 'white': 0.842, 'smooth': 0.059}, 'AC': {'eye': 0.213, 'jaw': 0.06, 'white': 0.012, 'smooth': 0.008}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.982, 'jaw': 0.96, 'white': 0.987, 'smooth': 0.992}
quantities {"eye": {"n": 6629, "spearman": 0.457, "mae": 0.0227, "pred_mean": 0.007, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0073, "orig_pred_mean": 0.0005}, "jaw": {"n": 6630, "spearman": 0.097, "mae": 0.0179, "pred_mean": 0.0032, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.006, "orig_pred_mean": 0.0019}, "white": {"n": 6630, "spearman": -0.078, "mae": 0.5194, "pred_mean": 0.0112, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0049, "orig_pred_mean": 0.0045}, "smooth": {"n": 6630, "spearman": 0.683, "mae": 0.0665, "pred_mean": 0.1296, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0354, "orig_pred_mean": 0.0006}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 83.08 | 0.81 | 16.11 | 55.13 | 98.51 | 0.093 |
| EyeEnlarging_60 | 2209 | 66.27 | 1.0 | 32.73 | 63.44 | 98.82 | 0.256 |
| EyeEnlarging_90 | 2210 | 53.03 | 0.86 | 46.11 | 70.13 | 99.1 | 0.394 |
| FaceLifting_30 | 2210 | 89.73 | 0.63 | 9.64 | 51.9 | 88.64 | 0.068 |
| FaceLifting_60 | 2210 | 87.92 | 0.63 | 11.45 | 52.8 | 93.44 | 0.086 |
| FaceLifting_90 | 2210 | 85.7 | 0.63 | 13.67 | 53.91 | 95.43 | 0.114 |
| Whitening_30 | 2210 | 88.91 | 0.72 | 10.36 | 52.26 | 76.97 | 0.043 |
| Whitening_60 | 2210 | 84.62 | 0.81 | 14.57 | 54.37 | 79.64 | 0.086 |
| Whitening_90 | 2210 | 77.42 | 0.77 | 21.81 | 57.98 | 84.57 | 0.155 |
| Smoothing_30 | 2210 | 17.24 | 0.54 | 82.22 | 88.19 | 98.87 | 0.795 |
| Smoothing_60 | 2210 | 0.68 | 0.05 | 99.28 | 96.72 | 99.86 | 0.992 |
| Smoothing_90 | 2210 | 0.36 | 0.05 | 99.59 | 96.88 | 99.95 | 0.996 |

## FF++ / cross-dataset
{"indomain": {"real": 78.04, "fake": 93.27, "filter": 80.7}, "FA": 8.74, "real_to_filter": 15.88, "MISS": 0.41, "heldout13": {"filter": 48.78, "fake": 16.57, "paired_excess_pp": 32.9}, "cdf": {"auc": 0.8256, "real_called_fake": 23.67}, "dfd": {"auc": 0.9287, "real_called_fake": 8.64}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
