# RU clipe5fbp1_s20261001

## Alibaba (blind)
orig real/fake/filter {'real': 75.93, 'fake': 10.32, 'filter': 13.76} | pooled {'n': 26519, 'to_real': 76.46, 'to_fake': 10.85, 'to_filter': 12.7, 'balanced_acc': 49.47, 'paired_rank': 46.63}
Eq.4 {'TP': {'eye': 0.174, 'jaw': 0.753, 'white': 0.665, 'smooth': 0.405}, 'TN_same_image': {'eye': 0.098, 'jaw': 0.143, 'white': 0.098, 'smooth': 0.063}, 'AC': {'eye': 0.033, 'jaw': 0.084, 'white': 0.046, 'smooth': 0.023}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.836, 'jaw': 0.221, 'white': 0.338, 'smooth': 0.566}
quantities {"eye": {"n": 6629, "spearman": -0.049, "mae": 0.4147, "pred_mean": -0.0627, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.4462, "orig_pred_mean": -0.0051}, "jaw": {"n": 6630, "spearman": -0.018, "mae": 0.6126, "pred_mean": -0.5627, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.3721, "orig_pred_mean": -0.5674}, "white": {"n": 6630, "spearman": -0.044, "mae": 0.766, "pred_mean": -0.1444, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.4571, "orig_pred_mean": -0.1586}, "smooth": {"n": 6630, "spearman": -0.065, "mae": 0.4348, "pred_mean": -0.1831, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.4543, "orig_pred_mean": -0.1848}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 76.97 | 10.27 | 12.76 | 49.5 | 46.02 | 0.166 |
| EyeEnlarging_60 | 2209 | 77.68 | 10.59 | 11.72 | 48.98 | 41.06 | 0.168 |
| EyeEnlarging_90 | 2210 | 77.96 | 11.18 | 10.86 | 48.55 | 36.54 | 0.189 |
| FaceLifting_30 | 2210 | 76.65 | 10.32 | 13.03 | 49.64 | 46.33 | 0.762 |
| FaceLifting_60 | 2210 | 76.97 | 10.36 | 12.67 | 49.45 | 44.62 | 0.754 |
| FaceLifting_90 | 2210 | 76.61 | 11.27 | 12.13 | 49.18 | 43.03 | 0.743 |
| Whitening_30 | 2210 | 76.02 | 10.41 | 13.57 | 49.91 | 49.86 | 0.656 |
| Whitening_60 | 2210 | 76.33 | 11.18 | 12.49 | 49.36 | 46.63 | 0.658 |
| Whitening_90 | 2210 | 76.56 | 11.67 | 11.76 | 49.0 | 43.67 | 0.68 |
| Smoothing_30 | 2210 | 73.62 | 12.76 | 13.62 | 49.93 | 53.76 | 0.424 |
| Smoothing_60 | 2210 | 76.06 | 9.68 | 14.25 | 50.25 | 54.34 | 0.399 |
| Smoothing_90 | 2210 | 76.06 | 10.45 | 13.48 | 49.86 | 53.67 | 0.392 |

## FF++ / cross-dataset
{"indomain": {"real": 84.12, "fake": 95.21, "filter": 5.62}, "FA": 4.71, "real_to_filter": 7.45, "MISS": 31.94, "heldout13": {"filter": 8.05, "fake": 12.16, "paired_excess_pp": 0.6}, "cdf": {"auc": 0.88, "real_called_fake": 24.3}, "dfd": {"auc": 0.9486, "real_called_fake": 6.25}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
