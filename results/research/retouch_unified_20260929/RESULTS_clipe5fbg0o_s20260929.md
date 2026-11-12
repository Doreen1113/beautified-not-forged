# RU clipe5fbg0o_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 19.73, 'fake': 29.1, 'filter': 51.18} | pooled {'n': 26519, 'to_real': 19.61, 'to_fake': 23.71, 'to_filter': 56.68, 'balanced_acc': 52.75, 'paired_rank': 62.41}
Eq.4 {'TP': {'eye': 0.065, 'jaw': 0.841, 'white': 0.276, 'smooth': 0.014}, 'TN_same_image': {'eye': 0.123, 'jaw': 0.681, 'white': 0.153, 'smooth': 0.09}, 'AC': {'eye': 0.007, 'jaw': 0.574, 'white': 0.043, 'smooth': 0.003}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.942, 'jaw': 0.182, 'white': 0.718, 'smooth': 0.982}
quantities {"eye": {"n": 6629, "spearman": -0.072, "mae": 0.4604, "pred_mean": -0.0974, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3714, "orig_pred_mean": -0.0797}, "jaw": {"n": 6630, "spearman": 0.009, "mae": 0.3516, "pred_mean": -0.182, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.4049, "orig_pred_mean": -0.1763}, "white": {"n": 6630, "spearman": -0.035, "mae": 0.6079, "pred_mean": 0.1208, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4005, "orig_pred_mean": 0.1288}, "smooth": {"n": 6630, "spearman": 0.039, "mae": 0.3666, "pred_mean": 0.355, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3629, "orig_pred_mean": 0.2528}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 18.37 | 24.66 | 56.97 | 52.89 | 68.51 | 0.065 |
| EyeEnlarging_60 | 2209 | 18.06 | 26.35 | 55.59 | 52.21 | 65.93 | 0.063 |
| EyeEnlarging_90 | 2210 | 16.88 | 28.51 | 54.62 | 51.72 | 63.03 | 0.066 |
| FaceLifting_30 | 2210 | 18.1 | 24.93 | 56.97 | 52.89 | 68.46 | 0.836 |
| FaceLifting_60 | 2210 | 17.65 | 26.02 | 56.33 | 52.58 | 65.97 | 0.84 |
| FaceLifting_90 | 2210 | 16.97 | 27.38 | 55.66 | 52.24 | 64.3 | 0.845 |
| Whitening_30 | 2210 | 19.86 | 23.17 | 56.97 | 52.89 | 62.33 | 0.267 |
| Whitening_60 | 2210 | 21.99 | 23.67 | 54.34 | 51.58 | 56.29 | 0.279 |
| Whitening_90 | 2210 | 22.44 | 24.57 | 52.99 | 50.9 | 52.04 | 0.283 |
| Smoothing_30 | 2210 | 20.63 | 20.32 | 59.05 | 53.93 | 60.72 | 0.012 |
| Smoothing_60 | 2210 | 22.17 | 16.29 | 61.54 | 55.18 | 62.08 | 0.016 |
| Smoothing_90 | 2210 | 22.17 | 18.64 | 59.19 | 54.0 | 59.28 | 0.014 |

## FF++ / cross-dataset
{"indomain": {"real": 26.67, "fake": 95.04, "filter": 57.83}, "FA": 18.31, "real_to_filter": 61.09, "MISS": 2.0, "heldout13": {"filter": 49.54, "fake": 28.8, "paired_excess_pp": -11.55}, "cdf": {"auc": 0.8635, "real_called_fake": 32.59}, "dfd": {"auc": 0.9459, "real_called_fake": 8.11}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
