# RU clipe5feb_s20260929

## Alibaba (blind)
orig real/fake/filter {'real': 52.22, 'fake': 33.57, 'filter': 14.21} | pooled {'n': 26519, 'to_real': 51.14, 'to_fake': 35.5, 'to_filter': 13.36, 'balanced_acc': 49.58, 'paired_rank': 49.39}
Eq.4 {'TP': {'eye': 0.897, 'jaw': 0.194, 'white': 0.931, 'smooth': 0.524}, 'TN_same_image': {'eye': 0.037, 'jaw': 0.008, 'white': 0.046, 'smooth': 0.016}, 'AC': {'eye': 0.03, 'jaw': 0.0, 'white': 0.035, 'smooth': 0.003}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.119, 'jaw': 0.822, 'white': 0.074, 'smooth': 0.418}
quantities {"eye": {"n": 6629, "spearman": 0.006, "mae": 0.3401, "pred_mean": 0.0293, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.3349, "orig_pred_mean": 0.0589}, "jaw": {"n": 6630, "spearman": -0.006, "mae": 0.3357, "pred_mean": -0.1459, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.341, "orig_pred_mean": -0.1471}, "white": {"n": 6630, "spearman": 0.039, "mae": 0.7265, "pred_mean": -0.1254, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.3319, "orig_pred_mean": -0.1578}, "smooth": {"n": 6630, "spearman": 0.06, "mae": 0.3214, "pred_mean": 0.1493, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.3498, "orig_pred_mean": 0.17}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 55.88 | 30.36 | 13.76 | 49.77 | 53.71 | 0.893 |
| EyeEnlarging_60 | 2209 | 56.41 | 30.78 | 12.81 | 49.3 | 51.0 | 0.898 |
| EyeEnlarging_90 | 2210 | 54.48 | 33.17 | 12.35 | 49.07 | 47.92 | 0.901 |
| FaceLifting_30 | 2210 | 54.48 | 31.22 | 14.3 | 50.04 | 54.32 | 0.194 |
| FaceLifting_60 | 2210 | 54.93 | 31.45 | 13.62 | 49.7 | 52.13 | 0.192 |
| FaceLifting_90 | 2210 | 53.35 | 32.9 | 13.76 | 49.77 | 50.36 | 0.195 |
| Whitening_30 | 2210 | 54.07 | 31.4 | 14.52 | 50.16 | 54.89 | 0.931 |
| Whitening_60 | 2210 | 53.39 | 32.44 | 14.16 | 49.98 | 52.24 | 0.932 |
| Whitening_90 | 2210 | 52.99 | 33.76 | 13.26 | 49.52 | 50.0 | 0.93 |
| Smoothing_30 | 2210 | 45.66 | 39.95 | 14.39 | 50.09 | 47.78 | 0.567 |
| Smoothing_60 | 2210 | 41.4 | 45.52 | 13.08 | 49.43 | 41.76 | 0.532 |
| Smoothing_90 | 2210 | 36.7 | 52.99 | 10.32 | 48.05 | 36.56 | 0.473 |

## FF++ / cross-dataset
{"indomain": {"real": 73.1, "fake": 97.04, "filter": 11.4}, "FA": 15.88, "real_to_filter": 11.85, "MISS": 2.25, "heldout13": {"filter": 11.85, "fake": 25.61, "paired_excess_pp": 0.0}, "cdf": {"auc": 0.8844, "real_called_fake": 34.2}, "dfd": {"auc": 0.9557, "real_called_fake": 13.25}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
