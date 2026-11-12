# RU clipe5mfp0_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 88.1, 'fake': 11.9, 'filter': 0.0} | pooled {'n': 26519, 'to_real': 78.94, 'to_fake': 21.06, 'to_filter': 0.0, 'balanced_acc': 50.0, 'paired_rank': 32.7}
Eq.4 {'TP': {'eye': 0.0, 'jaw': 0.0, 'white': 0.0, 'smooth': 0.0}, 'TN_same_image': {'eye': 1.0, 'jaw': 1.0, 'white': 1.0, 'smooth': 1.0}, 'AC': {'eye': 0.0, 'jaw': 0.0, 'white': 0.0, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 1.0, 'jaw': 1.0, 'white': 1.0, 'smooth': 1.0}
quantities {"eye": {"n": 6629, "spearman": -0.018, "mae": 0.0509, "pred_mean": -0.0243, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.017, "orig_pred_mean": -0.0246}, "jaw": {"n": 6630, "spearman": 0.009, "mae": 0.0225, "pred_mean": 0.0025, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0206, "orig_pred_mean": 0.0034}, "white": {"n": 6630, "spearman": 0.168, "mae": 0.5165, "pred_mean": 0.0123, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0198, "orig_pred_mean": 0.0132}, "smooth": {"n": 6630, "spearman": -0.082, "mae": 0.1642, "pred_mean": 0.0137, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0212, "orig_pred_mean": 0.0171}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 88.19 | 11.81 | 0.0 | 50.0 | 44.95 | 0.0 |
| EyeEnlarging_60 | 2209 | 88.09 | 11.91 | 0.0 | 50.0 | 45.81 | 0.0 |
| EyeEnlarging_90 | 2210 | 87.65 | 12.35 | 0.0 | 50.0 | 44.5 | 0.0 |
| FaceLifting_30 | 2210 | 88.69 | 11.31 | 0.0 | 50.0 | 43.05 | 0.0 |
| FaceLifting_60 | 2210 | 88.46 | 11.54 | 0.0 | 50.0 | 44.66 | 0.0 |
| FaceLifting_90 | 2210 | 87.6 | 12.4 | 0.0 | 50.0 | 43.91 | 0.0 |
| Whitening_30 | 2210 | 87.69 | 12.31 | 0.0 | 50.0 | 41.7 | 0.0 |
| Whitening_60 | 2210 | 86.33 | 13.67 | 0.0 | 50.0 | 36.06 | 0.0 |
| Whitening_90 | 2210 | 85.75 | 14.25 | 0.0 | 50.0 | 36.56 | 0.0 |
| Smoothing_30 | 2210 | 72.85 | 27.15 | 0.0 | 50.0 | 6.92 | 0.0 |
| Smoothing_60 | 2210 | 49.86 | 50.14 | 0.0 | 50.0 | 2.58 | 0.0 |
| Smoothing_90 | 2210 | 36.11 | 63.89 | 0.0 | 50.0 | 1.67 | 0.0 |

## FF++ / cross-dataset
{"indomain": {"real": 95.59, "fake": 91.16, "filter": 0.0}, "FA": 16.57, "real_to_filter": 0.0, "MISS": 5.25, "heldout13": {"filter": 0.0, "fake": 22.19, "paired_excess_pp": 0.0}, "cdf": {"auc": 0.8986, "real_called_fake": 11.73}, "dfd": {"auc": 0.9672, "real_called_fake": 1.75}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
