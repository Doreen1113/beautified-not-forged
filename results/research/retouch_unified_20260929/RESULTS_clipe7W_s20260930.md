# RU clipe7W_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 78.6, 'fake': 0.41, 'filter': 21.0} | pooled {'n': 26519, 'to_real': 29.04, 'to_fake': 0.3, 'to_filter': 70.66, 'balanced_acc': 74.83, 'paired_rank': 93.25}
Eq.4 {'TP': {'eye': 0.269, 'jaw': 0.402, 'white': 0.383, 'smooth': 0.924}, 'TN_same_image': {'eye': 0.723, 'jaw': 0.91, 'white': 0.76, 'smooth': 0.455}, 'AC': {'eye': 0.253, 'jaw': 0.386, 'white': 0.297, 'smooth': 0.396}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.976, 'jaw': 0.948, 'white': 0.937, 'smooth': 0.989}
quantities {"eye": {"n": 6629, "spearman": 0.412, "mae": 0.0211, "pred_mean": 0.011, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0103, "orig_pred_mean": 0.002}, "jaw": {"n": 6630, "spearman": 0.149, "mae": 0.0176, "pred_mean": 0.0047, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0093, "orig_pred_mean": -0.0015}, "white": {"n": 6630, "spearman": -0.099, "mae": 0.4868, "pred_mean": 0.0688, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0079, "orig_pred_mean": 0.0087}, "smooth": {"n": 6630, "spearman": 0.198, "mae": 0.0961, "pred_mean": 0.101, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0193, "orig_pred_mean": -0.0006}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 46.24 | 0.23 | 53.53 | 66.26 | 93.03 | 0.118 |
| EyeEnlarging_60 | 2209 | 32.37 | 0.18 | 67.45 | 73.23 | 96.27 | 0.279 |
| EyeEnlarging_90 | 2210 | 24.21 | 0.23 | 75.57 | 77.28 | 97.69 | 0.409 |
| FaceLifting_30 | 2210 | 50.23 | 0.32 | 49.46 | 64.23 | 84.57 | 0.318 |
| FaceLifting_60 | 2210 | 42.35 | 0.23 | 57.42 | 68.21 | 90.29 | 0.397 |
| FaceLifting_90 | 2210 | 33.3 | 0.18 | 66.52 | 72.76 | 93.62 | 0.491 |
| Whitening_30 | 2210 | 47.01 | 0.32 | 52.67 | 65.83 | 86.0 | 0.174 |
| Whitening_60 | 2210 | 35.11 | 0.41 | 64.48 | 71.74 | 89.5 | 0.391 |
| Whitening_90 | 2210 | 26.43 | 0.45 | 73.12 | 76.06 | 92.85 | 0.584 |
| Smoothing_30 | 2210 | 10.68 | 0.32 | 89.0 | 84.0 | 96.61 | 0.786 |
| Smoothing_60 | 2210 | 0.41 | 0.23 | 99.37 | 89.18 | 99.41 | 0.991 |
| Smoothing_90 | 2210 | 0.18 | 0.5 | 99.32 | 89.16 | 99.14 | 0.996 |

## FF++ / cross-dataset
{"indomain": {"real": 78.88, "fake": 91.29, "filter": 88.91}, "FA": 5.17, "real_to_filter": 15.2, "MISS": 0.53, "heldout13": {"filter": 76.22, "fake": 13.53, "paired_excess_pp": 61.02}, "cdf": {"auc": 0.8838, "real_called_fake": 9.75}, "dfd": {"auc": 0.9542, "real_called_fake": 2.65}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
