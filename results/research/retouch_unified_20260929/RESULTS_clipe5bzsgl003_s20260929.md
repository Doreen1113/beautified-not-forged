# RU clipe5bzsgl003_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 66.92, 'fake': 0.9, 'filter': 32.17} | pooled {'n': 26519, 'to_real': 41.39, 'to_fake': 0.85, 'to_filter': 57.76, 'balanced_acc': 62.79, 'paired_rank': 74.47}
Eq.4 {'TP': {'eye': 0.086, 'jaw': 0.851, 'white': 0.729, 'smooth': 0.378}, 'TN_same_image': {'eye': 0.05, 'jaw': 0.298, 'white': 0.098, 'smooth': 0.004}, 'AC': {'eye': 0.003, 'jaw': 0.246, 'white': 0.067, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.94, 'jaw': 0.133, 'white': 0.559, 'smooth': 0.997}
quantities {"eye": {"n": 6629, "spearman": -0.026, "mae": 0.7549, "pred_mean": 0.7373, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3138, "orig_pred_mean": 0.9229}, "jaw": {"n": 6630, "spearman": 0.033, "mae": 0.2974, "pred_mean": 0.2781, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.478, "orig_pred_mean": 0.2847}, "white": {"n": 6630, "spearman": -0.303, "mae": 0.5878, "pred_mean": 0.4531, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4494, "orig_pred_mean": 0.2356}, "smooth": {"n": 6630, "spearman": 0.305, "mae": 0.3733, "pred_mean": 0.527, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.4601, "orig_pred_mean": 0.1627}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 53.17 | 0.63 | 46.2 | 57.01 | 72.22 | 0.083 |
| EyeEnlarging_60 | 2209 | 46.58 | 0.68 | 52.74 | 60.28 | 77.09 | 0.085 |
| EyeEnlarging_90 | 2210 | 41.18 | 0.72 | 58.1 | 62.96 | 78.64 | 0.091 |
| FaceLifting_30 | 2210 | 58.14 | 0.45 | 41.4 | 54.62 | 64.16 | 0.858 |
| FaceLifting_60 | 2210 | 54.48 | 0.54 | 44.98 | 56.4 | 69.14 | 0.851 |
| FaceLifting_90 | 2210 | 52.17 | 0.45 | 47.38 | 57.6 | 72.08 | 0.844 |
| Whitening_30 | 2210 | 49.59 | 0.54 | 49.86 | 58.85 | 67.96 | 0.679 |
| Whitening_60 | 2210 | 40.14 | 0.72 | 59.14 | 63.49 | 73.53 | 0.733 |
| Whitening_90 | 2210 | 31.67 | 0.86 | 67.47 | 67.65 | 77.78 | 0.775 |
| Smoothing_30 | 2210 | 20.05 | 1.0 | 78.96 | 73.39 | 86.43 | 0.19 |
| Smoothing_60 | 2210 | 22.08 | 1.45 | 76.47 | 72.15 | 79.32 | 0.458 |
| Smoothing_90 | 2210 | 27.47 | 2.13 | 70.41 | 69.12 | 75.25 | 0.487 |

## FF++ / cross-dataset
{"indomain": {"real": 69.3, "fake": 94.93, "filter": 60.18}, "FA": 13.07, "real_to_filter": 18.31, "MISS": 0.72, "heldout13": {"filter": 69.07, "fake": 17.48, "paired_excess_pp": 50.76}, "cdf": {"auc": 0.8902, "real_called_fake": 25.47}, "dfd": {"auc": 0.9607, "real_called_fake": 6.68}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
