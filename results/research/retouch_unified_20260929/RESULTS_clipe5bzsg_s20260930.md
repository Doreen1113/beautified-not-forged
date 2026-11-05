# RU clipe5bzsg_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 94.98, 'fake': 0.23, 'filter': 4.8} | pooled {'n': 26519, 'to_real': 90.38, 'to_fake': 0.27, 'to_filter': 9.34, 'balanced_acc': 52.27, 'paired_rank': 75.72}
Eq.4 {'TP': {'eye': 0.625, 'jaw': 0.07, 'white': 0.867, 'smooth': 0.269}, 'TN_same_image': {'eye': 0.059, 'jaw': 0.033, 'white': 0.22, 'smooth': 0.057}, 'AC': {'eye': 0.032, 'jaw': 0.003, 'white': 0.184, 'smooth': 0.015}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.423, 'jaw': 0.926, 'white': 0.085, 'smooth': 0.617}
quantities {"eye": {"n": 6629, "spearman": -0.089, "mae": 0.3807, "pred_mean": -0.307, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.5247, "orig_pred_mean": -0.2549}, "jaw": {"n": 6630, "spearman": 0.009, "mae": 0.3533, "pred_mean": -0.1672, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.5362, "orig_pred_mean": -0.2164}, "white": {"n": 6630, "spearman": -0.173, "mae": 0.7009, "pred_mean": 0.9352, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.3539, "orig_pred_mean": 0.8657}, "smooth": {"n": 6630, "spearman": -0.015, "mae": 0.4104, "pred_mean": -0.1796, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.7318, "orig_pred_mean": -0.2741}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 93.39 | 0.18 | 6.43 | 50.81 | 70.45 | 0.628 |
| EyeEnlarging_60 | 2209 | 93.48 | 0.18 | 6.34 | 50.77 | 74.45 | 0.623 |
| EyeEnlarging_90 | 2210 | 93.3 | 0.27 | 6.43 | 50.81 | 75.36 | 0.625 |
| FaceLifting_30 | 2210 | 93.62 | 0.18 | 6.2 | 50.7 | 64.28 | 0.073 |
| FaceLifting_60 | 2210 | 93.44 | 0.18 | 6.38 | 50.79 | 64.03 | 0.069 |
| FaceLifting_90 | 2210 | 93.53 | 0.18 | 6.29 | 50.74 | 65.54 | 0.068 |
| Whitening_30 | 2210 | 93.03 | 0.18 | 6.79 | 50.99 | 74.03 | 0.879 |
| Whitening_60 | 2210 | 91.76 | 0.23 | 8.01 | 51.6 | 77.6 | 0.865 |
| Whitening_90 | 2210 | 90.72 | 0.32 | 8.96 | 52.08 | 77.83 | 0.857 |
| Smoothing_30 | 2210 | 88.46 | 0.32 | 11.22 | 53.21 | 85.95 | 0.311 |
| Smoothing_60 | 2210 | 81.67 | 0.45 | 17.87 | 56.54 | 89.25 | 0.244 |
| Smoothing_90 | 2210 | 78.19 | 0.59 | 21.22 | 58.21 | 89.86 | 0.251 |

## FF++ / cross-dataset
{"indomain": {"real": 78.8, "fake": 80.39, "filter": 33.59}, "FA": 9.88, "real_to_filter": 14.59, "MISS": 7.47, "heldout13": {"filter": 42.25, "fake": 21.35, "paired_excess_pp": 27.66}, "cdf": {"auc": 0.7905, "real_called_fake": 17.94}, "dfd": {"auc": 0.9405, "real_called_fake": 2.07}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
