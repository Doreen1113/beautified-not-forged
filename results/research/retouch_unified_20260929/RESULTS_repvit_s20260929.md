# RU repvit_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 92.76, 'fake': 1.36, 'filter': 5.88} | pooled {'n': 26519, 'to_real': 62.85, 'to_fake': 1.09, 'to_filter': 36.06, 'balanced_acc': 65.09, 'paired_rank': 92.59}
Eq.4 {'TP': {'eye': 0.121, 'jaw': 0.106, 'white': 0.092, 'smooth': 0.924}, 'TN_same_image': {'eye': 0.907, 'jaw': 0.945, 'white': 0.82, 'smooth': 0.083}, 'AC': {'eye': 0.083, 'jaw': 0.069, 'white': 0.009, 'smooth': 0.037}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.985, 'jaw': 0.951, 'white': 0.98, 'smooth': 0.989}
quantities {"eye": {"n": 6629, "spearman": 0.382, "mae": 0.0258, "pred_mean": 0.0031, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.0104, "orig_pred_mean": 0.0004}, "jaw": {"n": 6630, "spearman": 0.074, "mae": 0.0179, "pred_mean": 0.003, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.0092, "orig_pred_mean": 0.002}, "white": {"n": 6630, "spearman": -0.04, "mae": 0.5137, "pred_mean": 0.0181, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.0058, "orig_pred_mean": 0.0053}, "smooth": {"n": 6630, "spearman": 0.687, "mae": 0.0673, "pred_mean": 0.1304, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.032, "orig_pred_mean": -0.0002}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 86.61 | 1.27 | 12.13 | 53.12 | 92.94 | 0.048 |
| EyeEnlarging_60 | 2209 | 78.68 | 1.27 | 20.05 | 57.09 | 95.56 | 0.11 |
| EyeEnlarging_90 | 2210 | 68.24 | 1.18 | 30.59 | 62.35 | 96.11 | 0.205 |
| FaceLifting_30 | 2210 | 88.37 | 1.49 | 10.14 | 52.13 | 86.95 | 0.088 |
| FaceLifting_60 | 2210 | 87.01 | 1.45 | 11.54 | 52.83 | 91.4 | 0.105 |
| FaceLifting_90 | 2210 | 85.48 | 1.36 | 13.17 | 53.64 | 93.35 | 0.124 |
| Whitening_30 | 2210 | 87.47 | 1.31 | 11.22 | 52.67 | 81.09 | 0.043 |
| Whitening_60 | 2210 | 81.67 | 1.31 | 17.01 | 55.57 | 85.93 | 0.081 |
| Whitening_90 | 2210 | 74.12 | 1.27 | 24.62 | 59.37 | 88.76 | 0.152 |
| Smoothing_30 | 2210 | 15.84 | 0.72 | 83.44 | 88.78 | 99.41 | 0.785 |
| Smoothing_60 | 2210 | 0.5 | 0.18 | 99.32 | 96.72 | 99.82 | 0.99 |
| Smoothing_90 | 2210 | 0.18 | 0.27 | 99.55 | 96.83 | 99.77 | 0.998 |

## FF++ / cross-dataset
{"indomain": {"real": 76.06, "fake": 86.43, "filter": 74.54}, "FA": 12.77, "real_to_filter": 15.2, "MISS": 1.38, "heldout13": {"filter": 50.23, "fake": 18.39, "paired_excess_pp": 35.03}, "cdf": {"auc": 0.7787, "real_called_fake": 15.9}, "dfd": {"auc": 0.9046, "real_called_fake": 11.45}, "bars": {"D1_cdf>=0.78": false, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": true}}
