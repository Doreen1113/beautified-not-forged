# RU clipe5fbp0_s20260930

## Alibaba (blind)
orig real/fake/filter {'real': 58.37, 'fake': 14.03, 'filter': 27.6} | pooled {'n': 26519, 'to_real': 50.55, 'to_fake': 26.44, 'to_filter': 23.01, 'balanced_acc': 47.7, 'paired_rank': 38.54}
Eq.4 {'TP': {'eye': 0.752, 'jaw': 0.347, 'white': 0.734, 'smooth': 0.78}, 'TN_same_image': {'eye': 0.052, 'jaw': 0.026, 'white': 0.058, 'smooth': 0.028}, 'AC': {'eye': 0.037, 'jaw': 0.01, 'white': 0.043, 'smooth': 0.02}, 'table7_TP': {'eye': 0.519, 'jaw': 0.548, 'smooth': 0.861, 'white': 0.501}}
orig TN per op {'eye': 0.256, 'jaw': 0.672, 'white': 0.238, 'smooth': 0.332}
quantities {"eye": {"n": 6629, "spearman": -0.064, "mae": 0.5878, "pred_mean": -0.5073, "meas_mean": 0.0257, "crosstalk_abs_mean": 0.5286, "orig_pred_mean": -0.5151}, "jaw": {"n": 6630, "spearman": 0.001, "mae": 0.4071, "pred_mean": -0.2474, "meas_mean": 0.0199, "crosstalk_abs_mean": 0.5775, "orig_pred_mean": -0.2556}, "white": {"n": 6630, "spearman": -0.021, "mae": 0.6359, "pred_mean": 0.7139, "meas_mean": 0.5237, "crosstalk_abs_mean": 0.447, "orig_pred_mean": 0.7329}, "smooth": {"n": 6630, "spearman": -0.311, "mae": 0.6259, "pred_mean": -0.3675, "meas_mean": 0.1768, "crosstalk_abs_mean": 0.544, "orig_pred_mean": -0.181}}
bars {"R1_balanced>=75": false, "R2_TP>=table7_on_3of4_and_origTN>=0.8": false, "R3_to_fake<=5_pooled_and<=10_each": false, "R4_spearman>=0.6_all": false}

| group | n | ->real | ->fake | ->filter | balanced | rank | TP |
|---|---|---|---|---|---|---|---|
| EyeEnlarging_30 | 2210 | 57.69 | 14.34 | 27.96 | 50.18 | 51.13 | 0.754 |
| EyeEnlarging_60 | 2209 | 58.22 | 14.44 | 27.34 | 49.87 | 48.28 | 0.753 |
| EyeEnlarging_90 | 2210 | 57.92 | 15.48 | 26.61 | 49.5 | 46.45 | 0.75 |
| FaceLifting_30 | 2210 | 58.37 | 14.03 | 27.6 | 50.0 | 50.09 | 0.341 |
| FaceLifting_60 | 2210 | 58.33 | 14.34 | 27.33 | 49.87 | 47.65 | 0.348 |
| FaceLifting_90 | 2210 | 58.46 | 15.07 | 26.47 | 49.44 | 46.31 | 0.352 |
| Whitening_30 | 2210 | 56.52 | 15.66 | 27.83 | 50.11 | 47.96 | 0.748 |
| Whitening_60 | 2210 | 55.93 | 17.42 | 26.65 | 49.53 | 44.93 | 0.732 |
| Whitening_90 | 2210 | 53.48 | 19.82 | 26.7 | 49.55 | 45.88 | 0.723 |
| Smoothing_30 | 2210 | 46.92 | 34.93 | 18.14 | 45.27 | 20.9 | 0.693 |
| Smoothing_60 | 2210 | 27.42 | 64.12 | 8.46 | 40.43 | 8.24 | 0.795 |
| Smoothing_90 | 2210 | 17.38 | 77.65 | 4.98 | 38.69 | 4.62 | 0.852 |

## FF++ / cross-dataset
{"indomain": {"real": 35.11, "fake": 95.17, "filter": 42.86}, "FA": 26.75, "real_to_filter": 53.72, "MISS": 0.91, "heldout13": {"filter": 44.45, "fake": 28.27, "paired_excess_pp": -9.27}, "cdf": {"auc": 0.8968, "real_called_fake": 22.67}, "dfd": {"auc": 0.9533, "real_called_fake": 4.5}, "bars": {"D1_cdf>=0.78": true, "D1_dfd>=0.88": true, "D2_indomain>=80_each": false, "D2_heldout_excess>=30": false}}
