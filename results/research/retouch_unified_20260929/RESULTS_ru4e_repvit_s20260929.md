# RU ru4e_repvit_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 50.63, 'fake': 0.27, 'filter': 49.1} | pooled {'n': 26519, 'to_real': 18.16, 'to_fake': 0.33, 'to_filter': 81.51, 'balanced_acc': 66.2, 'paired_rank': 94.79}
Eq.4 {'TP': {'eye': 0.161, 'jaw': 0.203, 'white': 0.278, 'smooth': 0.959}, 'TN_same_image': {'eye': 0.808, 'jaw': 0.861, 'white': 0.769, 'smooth': 0.196}, 'AC': {'eye': 0.099, 'jaw': 0.133, 'white': 0.15, 'smooth': 0.168}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.979, 'jaw': 0.961, 'white': 0.943, 'smooth': 0.976}
quantities {"eye": {"n": 6629, "spearman": 0.417, "mae": 0.0229, "pred_mean": 0.0076, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0107, "orig_pred_mean": 0.0048}, "jaw": {"n": 6630, "spearman": 0.15, "mae": 0.0183, "pred_mean": 0.0024, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0109, "orig_pred_mean": -0.0004}, "white": {"n": 6630, "spearman": -0.024, "mae": 0.5027, "pred_mean": 0.0532, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0061, "orig_pred_mean": 0.0117}, "smooth": {"n": 6630, "spearman": 0.547, "mae": 0.0752, "pred_mean": 0.1271, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.0233, "orig_pred_mean": 0.0003}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 28.91 | 0.36 | 70.72 | 60.81 | 96.74 | 0.079 |
| EyeEnlarging_60 | 2209 | 22.32 | 0.36 | 77.32 | 64.11 | 98.69 | 0.156 |
| EyeEnlarging_90 | 2210 | 17.65 | 0.36 | 81.99 | 66.45 | 99.0 | 0.247 |
| FaceLifting_30 | 2210 | 31.63 | 0.32 | 68.05 | 59.48 | 89.5 | 0.157 |
| FaceLifting_60 | 2210 | 26.47 | 0.32 | 73.21 | 62.06 | 93.35 | 0.2 |
| FaceLifting_90 | 2210 | 21.67 | 0.32 | 78.01 | 64.45 | 95.43 | 0.25 |
| Whitening_30 | 2210 | 29.82 | 0.32 | 69.86 | 60.38 | 85.7 | 0.141 |
| Whitening_60 | 2210 | 22.13 | 0.45 | 77.42 | 64.16 | 88.89 | 0.27 |
| Whitening_90 | 2210 | 16.11 | 0.27 | 83.62 | 67.26 | 91.81 | 0.425 |
| Smoothing_30 | 2210 | 1.18 | 0.14 | 98.69 | 74.79 | 99.77 | 0.887 |
| Smoothing_60 | 2210 | 0.09 | 0.14 | 99.77 | 75.34 | 99.55 | 0.991 |
| Smoothing_90 | 2210 | 0.0 | 0.59 | 99.41 | 75.16 | 99.1 | 0.997 |

## FF++ / cross-dataset
{"indomain": {"real": 70.14, "fake": 81.67, "filter": 67.48}, "FA": 15.58, "real_to_filter": 16.95, "MISS": 1.78, "heldout13": {"filter": 49.01, "fake": 23.63, "paired_excess_pp": 32.06}, "cdf": {"auc": 0.7559, "real_called_fake": 23.54}, "dfd": {"auc": 0.8918, "real_called_fake": 22.89}, "bars": {"D1_cdf>=0.78": false, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
