# RU clipe7W_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 83.12, 'fake': 0.5, 'filter': 16.38} | pooled {'n': 26519, 'to_real': 33.38, 'to_fake': 0.47, 'to_filter': 66.16, 'balanced_acc': 74.89, 'paired_rank': 93.58}
Eq.4 {'TP': {'eye': 0.212, 'jaw': 0.403, 'white': 0.28, 'smooth': 0.947}, 'TN_same_image': {'eye': 0.745, 'jaw': 0.948, 'white': 0.726, 'smooth': 0.486}, 'AC': {'eye': 0.201, 'jaw': 0.392, 'white': 0.192, 'smooth': 0.443}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.986, 'jaw': 0.95, 'white': 0.967, 'smooth': 0.989}
quantities {"eye": {"n": 6629, "spearman": 0.384, "mae": 0.025, "pred_mean": 0.0042, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0107, "orig_pred_mean": 0.0005}, "jaw": {"n": 6630, "spearman": 0.179, "mae": 0.0132, "pred_mean": 0.0186, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0073, "orig_pred_mean": 0.0086}, "white": {"n": 6630, "spearman": -0.174, "mae": 0.5002, "pred_mean": 0.038, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0102, "orig_pred_mean": -0.0012}, "smooth": {"n": 6630, "spearman": 0.364, "mae": 0.0938, "pred_mean": 0.0935, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0185, "orig_pred_mean": 0.006}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 54.16 | 0.45 | 45.38 | 64.5 | 94.05 | 0.073 |
| EyeEnlarging_60 | 2209 | 40.88 | 0.36 | 58.76 | 71.19 | 96.47 | 0.211 |
| EyeEnlarging_90 | 2210 | 30.0 | 0.45 | 69.55 | 76.58 | 97.47 | 0.352 |
| FaceLifting_30 | 2210 | 54.71 | 0.27 | 45.02 | 64.32 | 87.62 | 0.319 |
| FaceLifting_60 | 2210 | 46.74 | 0.23 | 53.03 | 68.33 | 91.95 | 0.399 |
| FaceLifting_90 | 2210 | 38.46 | 0.23 | 61.31 | 72.47 | 93.96 | 0.491 |
| Whitening_30 | 2210 | 53.08 | 0.36 | 46.56 | 65.09 | 84.73 | 0.1 |
| Whitening_60 | 2210 | 41.4 | 0.59 | 58.01 | 70.81 | 88.12 | 0.274 |
| Whitening_90 | 2210 | 32.26 | 0.77 | 66.97 | 75.29 | 91.72 | 0.465 |
| Smoothing_30 | 2210 | 8.19 | 0.41 | 91.4 | 87.51 | 98.64 | 0.852 |
| Smoothing_60 | 2210 | 0.45 | 0.41 | 99.14 | 91.38 | 99.32 | 0.992 |
| Smoothing_90 | 2210 | 0.18 | 1.09 | 98.73 | 91.18 | 98.87 | 0.996 |

## FF++ / cross-dataset
{"indomain": {"real": 82.29, "fake": 93.04, "filter": 87.31}, "FA": 5.78, "real_to_filter": 11.09, "MISS": 0.72, "heldout13": {"filter": 72.34, "fake": 13.6, "paired_excess_pp": 61.25}, "cdf": {"auc": 0.8967, "real_called_fake": 12.18}, "dfd": {"auc": 0.9497, "real_called_fake": 2.44}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": true, "D2_heldout_excess>=30": true}}
