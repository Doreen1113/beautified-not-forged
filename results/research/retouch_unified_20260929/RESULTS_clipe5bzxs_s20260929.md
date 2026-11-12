# RU clipe5bzxs_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 94.57, 'fake': 0.18, 'filter': 5.25} | pooled {'n': 26519, 'to_real': 92.25, 'to_fake': 0.12, 'to_filter': 7.62, 'balanced_acc': 51.19, 'paired_rank': 50.5}
Eq.4 {'TP': {'eye': 0.048, 'jaw': 0.421, 'white': 0.469, 'smooth': 0.0}, 'TN_same_image': {'eye': 0.215, 'jaw': 0.434, 'white': 0.54, 'smooth': 0.2}, 'AC': {'eye': 0.011, 'jaw': 0.203, 'white': 0.288, 'smooth': 0.0}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.959, 'jaw': 0.582, 'white': 0.54, 'smooth': 1.0}
quantities {"eye": {"n": 6629, "spearman": 0.115, "mae": 0.1896, "pred_mean": 0.1618, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4767, "orig_pred_mean": 0.152}, "jaw": {"n": 6630, "spearman": -0.016, "mae": 0.2982, "pred_mean": 0.2871, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4478, "orig_pred_mean": 0.2841}, "white": {"n": 6630, "spearman": 0.081, "mae": 0.5371, "pred_mean": 0.7661, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.3242, "orig_pred_mean": 0.7482}, "smooth": {"n": 6630, "spearman": 0.075, "mae": 0.3122, "pred_mean": 0.4763, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3956, "orig_pred_mean": 0.3972}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 94.89 | 0.09 | 5.02 | 49.89 | 46.47 | 0.053 |
| EyeEnlarging_60 | 2209 | 94.02 | 0.18 | 5.79 | 50.27 | 49.14 | 0.049 |
| EyeEnlarging_90 | 2210 | 92.76 | 0.14 | 7.1 | 50.93 | 53.48 | 0.043 |
| FaceLifting_30 | 2210 | 94.93 | 0.14 | 4.93 | 49.84 | 48.91 | 0.411 |
| FaceLifting_60 | 2210 | 94.43 | 0.09 | 5.48 | 50.11 | 54.03 | 0.424 |
| FaceLifting_90 | 2210 | 94.03 | 0.09 | 5.88 | 50.32 | 58.96 | 0.429 |
| Whitening_30 | 2210 | 95.61 | 0.09 | 4.3 | 49.52 | 45.02 | 0.528 |
| Whitening_60 | 2210 | 95.02 | 0.09 | 4.89 | 49.82 | 46.88 | 0.483 |
| Whitening_90 | 2210 | 93.57 | 0.09 | 6.33 | 50.54 | 53.87 | 0.397 |
| Smoothing_30 | 2210 | 91.95 | 0.09 | 7.96 | 51.36 | 48.01 | 0.0 |
| Smoothing_60 | 2210 | 85.61 | 0.18 | 14.21 | 54.48 | 49.1 | 0.0 |
| Smoothing_90 | 2210 | 80.23 | 0.18 | 19.59 | 57.17 | 52.1 | 0.0 |

## FF++ / cross-dataset
{"indomain": {"real": 60.56, "fake": 48.4, "filter": 45.97}, "FA": 9.27, "real_to_filter": 37.46, "MISS": 14.22, "heldout13": {"filter": 54.64, "fake": 14.67, "paired_excess_pp": 17.18}, "cdf": {"auc": 0.8422, "real_called_fake": 1.26}, "dfd": {"auc": 0.942, "real_called_fake": 0.26}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
