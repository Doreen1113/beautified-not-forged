# RU clipe5awpb_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 0.05, 'fake': 0.72, 'filter': 99.23} | pooled {'n': 26519, 'to_real': 0.05, 'to_fake': 0.68, 'to_filter': 99.27, 'balanced_acc': 50.02, 'paired_rank': 34.4}
Eq.4 {'TP': {'eye': 0.183, 'jaw': 0.955, 'white': 0.9, 'smooth': 0.812}, 'TN_same_image': {'eye': 0.002, 'jaw': 0.008, 'white': 0.003, 'smooth': 0.006}, 'AC': {'eye': 0.001, 'jaw': 0.006, 'white': 0.002, 'smooth': 0.005}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.786, 'jaw': 0.041, 'white': 0.08, 'smooth': 0.134}
quantities {"eye": {"n": 6629, "spearman": -0.096, "mae": 0.9774, "pred_mean": -0.9505, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4997, "orig_pred_mean": -0.905}, "jaw": {"n": 6630, "spearman": -0.001, "mae": 0.7801, "pred_mean": -0.7588, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.5539, "orig_pred_mean": -0.7738}, "white": {"n": 6630, "spearman": -0.049, "mae": 0.5796, "pred_mean": 0.0202, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.7242, "orig_pred_mean": 0.0295}, "smooth": {"n": 6630, "spearman": 0.108, "mae": 0.4019, "pred_mean": 0.5105, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.6274, "orig_pred_mean": 0.4474}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": true, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 0.0 | 0.63 | 99.37 | 50.07 | 27.83 | 0.179 |
| EyeEnlarging_60 | 2209 | 0.0 | 0.68 | 99.32 | 50.05 | 31.1 | 0.179 |
| EyeEnlarging_90 | 2210 | 0.0 | 0.72 | 99.28 | 50.02 | 34.91 | 0.19 |
| FaceLifting_30 | 2210 | 0.0 | 0.54 | 99.46 | 50.11 | 27.42 | 0.957 |
| FaceLifting_60 | 2210 | 0.05 | 0.72 | 99.23 | 50.0 | 31.47 | 0.952 |
| FaceLifting_90 | 2210 | 0.05 | 0.77 | 99.19 | 49.98 | 34.03 | 0.955 |
| Whitening_30 | 2210 | 0.05 | 0.59 | 99.37 | 50.07 | 31.04 | 0.915 |
| Whitening_60 | 2210 | 0.0 | 0.5 | 99.5 | 50.14 | 39.77 | 0.901 |
| Whitening_90 | 2210 | 0.0 | 0.5 | 99.5 | 50.14 | 51.13 | 0.884 |
| Smoothing_30 | 2210 | 0.14 | 0.59 | 99.28 | 50.02 | 31.92 | 0.843 |
| Smoothing_60 | 2210 | 0.14 | 0.63 | 99.23 | 50.0 | 33.78 | 0.815 |
| Smoothing_90 | 2210 | 0.14 | 1.31 | 98.55 | 49.66 | 38.44 | 0.777 |

## FF++ / cross-dataset
{"indomain": {"real": 0.0, "fake": 96.74, "filter": 80.7}, "FA": 19.3, "real_to_filter": 80.4, "MISS": 0.0, "heldout13": {"filter": 72.11, "fake": 27.89, "paired_excess_pp": -8.29}, "cdf": {"auc": 0.9108, "real_called_fake": 39.5}, "dfd": {"auc": 0.9627, "real_called_fake": 11.18}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
