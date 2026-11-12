# RU clipe4r_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 89.55, 'fake': 0.63, 'filter': 9.82} | pooled {'n': 26519, 'to_real': 40.35, 'to_fake': 0.48, 'to_filter': 59.18, 'balanced_acc': 74.68, 'paired_rank': 95.48}
Eq.4 {'TP': {'eye': 0.218, 'jaw': 0.247, 'white': 0.253, 'smooth': 0.964}, 'TN_same_image': {'eye': 0.861, 'jaw': 0.947, 'white': 0.824, 'smooth': 0.525}, 'AC': {'eye': 0.207, 'jaw': 0.233, 'white': 0.181, 'smooth': 0.493}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.99, 'jaw': 0.983, 'white': 0.986, 'smooth': 0.983}
quantities {"eye": {"n": 6629, "spearman": 0.28, "mae": 0.0218, "pred_mean": 0.011, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0096, "orig_pred_mean": 0.0046}, "jaw": {"n": 6630, "spearman": 0.144, "mae": 0.0177, "pred_mean": 0.0117, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0086, "orig_pred_mean": 0.0015}, "white": {"n": 6630, "spearman": -0.024, "mae": 0.4981, "pred_mean": 0.0465, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0104, "orig_pred_mean": 0.0064}, "smooth": {"n": 6630, "spearman": 0.139, "mae": 0.0982, "pred_mean": 0.0965, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0202, "orig_pred_mean": 0.0025}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 64.3 | 0.72 | 34.98 | 62.58 | 96.63 | 0.067 |
| EyeEnlarging_60 | 2209 | 48.89 | 0.54 | 50.57 | 70.37 | 97.92 | 0.222 |
| EyeEnlarging_90 | 2210 | 37.65 | 0.54 | 61.81 | 75.99 | 98.46 | 0.365 |
| FaceLifting_30 | 2210 | 66.74 | 0.63 | 32.62 | 61.4 | 89.21 | 0.171 |
| FaceLifting_60 | 2210 | 58.24 | 0.68 | 41.09 | 65.63 | 93.87 | 0.24 |
| FaceLifting_90 | 2210 | 50.23 | 0.81 | 48.96 | 69.57 | 96.06 | 0.329 |
| Whitening_30 | 2210 | 64.3 | 0.54 | 35.16 | 62.67 | 89.59 | 0.081 |
| Whitening_60 | 2210 | 50.14 | 0.45 | 49.41 | 69.8 | 90.93 | 0.239 |
| Whitening_90 | 2210 | 37.51 | 0.63 | 61.86 | 76.02 | 93.76 | 0.439 |
| Smoothing_30 | 2210 | 5.7 | 0.09 | 94.21 | 92.19 | 99.59 | 0.9 |
| Smoothing_60 | 2210 | 0.36 | 0.0 | 99.64 | 94.91 | 99.91 | 0.995 |
| Smoothing_90 | 2210 | 0.14 | 0.05 | 99.82 | 95.0 | 99.86 | 0.997 |

## FF++ / cross-dataset
{"indomain": {"real": 75.15, "fake": 94.19, "filter": 86.93}, "FA": 7.67, "real_to_filter": 11.09, "MISS": 0.34, "heldout13": {"filter": 59.12, "fake": 20.44, "paired_excess_pp": 48.03}, "cdf": {"auc": 0.8889, "real_called_fake": 31.34}, "dfd": {"auc": 0.9542, "real_called_fake": 7.58}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
