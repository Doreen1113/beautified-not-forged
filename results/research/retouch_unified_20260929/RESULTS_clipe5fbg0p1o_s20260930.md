# RU clipe5fbg0p1o_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 59.5, 'fake': 24.34, 'filter': 16.15} | pooled {'n': 26519, 'to_real': 61.64, 'to_fake': 21.89, 'to_filter': 16.47, 'balanced_acc': 50.16, 'paired_rank': 48.16}
Eq.4 {'TP': {'eye': 0.86, 'jaw': 0.524, 'white': 0.738, 'smooth': 0.57}, 'TN_same_image': {'eye': 0.024, 'jaw': 0.009, 'white': 0.017, 'smooth': 0.008}, 'AC': {'eye': 0.02, 'jaw': 0.004, 'white': 0.012, 'smooth': 0.006}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.142, 'jaw': 0.499, 'white': 0.248, 'smooth': 0.257}
quantities {"eye": {"n": 6629, "spearman": 0.003, "mae": 0.7522, "pred_mean": -0.6344, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4942, "orig_pred_mean": -0.6683}, "jaw": {"n": 6630, "spearman": 0.009, "mae": 0.3611, "pred_mean": 0.0613, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.6147, "orig_pred_mean": 0.0424}, "white": {"n": 6630, "spearman": -0.072, "mae": 0.6453, "pred_mean": 0.724, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.471, "orig_pred_mean": 0.7297}, "smooth": {"n": 6630, "spearman": 0.116, "mae": 0.3279, "pred_mean": 0.0666, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.8037, "orig_pred_mean": -0.1083}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 59.1 | 24.25 | 16.65 | 50.25 | 49.48 | 0.858 |
| EyeEnlarging_60 | 2209 | 58.31 | 24.99 | 16.7 | 50.28 | 50.75 | 0.863 |
| EyeEnlarging_90 | 2210 | 56.7 | 26.74 | 16.56 | 50.21 | 46.97 | 0.858 |
| FaceLifting_30 | 2210 | 59.91 | 23.98 | 16.11 | 49.98 | 45.45 | 0.519 |
| FaceLifting_60 | 2210 | 59.82 | 24.93 | 15.25 | 49.55 | 44.52 | 0.529 |
| FaceLifting_90 | 2210 | 58.64 | 26.38 | 14.98 | 49.41 | 43.03 | 0.526 |
| Whitening_30 | 2210 | 59.41 | 24.62 | 15.97 | 49.91 | 42.17 | 0.745 |
| Whitening_60 | 2210 | 57.78 | 26.15 | 16.06 | 49.96 | 42.69 | 0.743 |
| Whitening_90 | 2210 | 56.38 | 27.19 | 16.43 | 50.14 | 43.35 | 0.726 |
| Smoothing_30 | 2210 | 65.11 | 19.46 | 15.43 | 49.64 | 44.66 | 0.634 |
| Smoothing_60 | 2210 | 74.21 | 8.46 | 17.33 | 50.59 | 59.05 | 0.545 |
| Smoothing_90 | 2210 | 74.3 | 5.57 | 20.14 | 51.99 | 65.75 | 0.53 |

## FF++ / cross-dataset
{"indomain": {"real": 52.74, "fake": 95.98, "filter": 31.16}, "FA": 19.76, "real_to_filter": 34.42, "MISS": 22.94, "heldout13": {"filter": 31.46, "fake": 31.53, "paired_excess_pp": -2.96}, "cdf": {"auc": 0.8947, "real_called_fake": 38.76}, "dfd": {"auc": 0.9518, "real_called_fake": 8.96}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
