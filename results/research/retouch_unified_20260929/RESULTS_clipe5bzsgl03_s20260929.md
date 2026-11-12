# RU clipe5bzsgl03_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 99.5, 'fake': 0.36, 'filter': 0.14} | pooled {'n': 26519, 'to_real': 98.49, 'to_fake': 0.54, 'to_filter': 0.97, 'balanced_acc': 50.41, 'paired_rank': 39.98}
Eq.4 {'TP': {'eye': 0.809, 'jaw': 0.727, 'white': 0.999, 'smooth': 0.57}, 'TN_same_image': {'eye': 0.0, 'jaw': 0.0, 'white': 0.011, 'smooth': 0.0}, 'AC': {'eye': 0.0, 'jaw': 0.0, 'white': 0.011, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.238, 'jaw': 0.281, 'white': 0.0, 'smooth': 0.16}
quantities {"eye": {"n": 6629, "spearman": -0.027, "mae": 0.2532, "pred_mean": -0.0911, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.2621, "orig_pred_mean": -0.0962}, "jaw": {"n": 6630, "spearman": 0.087, "mae": 0.2406, "pred_mean": 0.1003, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.2508, "orig_pred_mean": 0.0537}, "white": {"n": 6630, "spearman": 0.199, "mae": 0.4964, "pred_mean": 0.1584, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.2663, "orig_pred_mean": 0.198}, "smooth": {"n": 6630, "spearman": 0.122, "mae": 0.2758, "pred_mean": 0.1949, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.25, "orig_pred_mean": -0.2566}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 99.59 | 0.36 | 0.05 | 49.95 | 23.98 | 0.799 |
| EyeEnlarging_60 | 2209 | 99.59 | 0.41 | 0.0 | 49.93 | 21.87 | 0.811 |
| EyeEnlarging_90 | 2210 | 99.64 | 0.36 | 0.0 | 49.93 | 21.72 | 0.816 |
| FaceLifting_30 | 2210 | 99.46 | 0.41 | 0.14 | 50.0 | 22.67 | 0.732 |
| FaceLifting_60 | 2210 | 99.59 | 0.36 | 0.05 | 49.95 | 19.73 | 0.726 |
| FaceLifting_90 | 2210 | 99.55 | 0.41 | 0.05 | 49.95 | 18.17 | 0.722 |
| Whitening_30 | 2210 | 99.32 | 0.45 | 0.23 | 50.04 | 41.79 | 0.999 |
| Whitening_60 | 2210 | 99.19 | 0.5 | 0.32 | 50.09 | 50.68 | 1.0 |
| Whitening_90 | 2210 | 98.19 | 0.68 | 1.13 | 50.5 | 60.02 | 0.998 |
| Smoothing_30 | 2210 | 98.1 | 0.54 | 1.36 | 50.61 | 57.96 | 0.588 |
| Smoothing_60 | 2210 | 95.52 | 0.86 | 3.62 | 51.74 | 69.46 | 0.561 |
| Smoothing_90 | 2210 | 94.12 | 1.18 | 4.71 | 52.28 | 71.72 | 0.562 |

## FF++ / cross-dataset
{"indomain": {"real": 88.75, "fake": 90.42, "filter": 5.47}, "FA": 9.27, "real_to_filter": 3.42, "MISS": 4.47, "heldout13": {"filter": 5.24, "fake": 17.02, "paired_excess_pp": 1.82}, "cdf": {"auc": 0.8369, "real_called_fake": 14.7}, "dfd": {"auc": 0.9491, "real_called_fake": 3.66}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
