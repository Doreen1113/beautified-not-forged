# Addendum 46 readout: smoothing-invariant consistency (SIC)

Bars on P(forged); point estimates decide; [95% CI]. (3') = miss rise <= max(P0 rise, 0) + 5. Primary arm clipe5z, secondary clipe5bz.

## clipe5z_s20260929 (SIC factorised (primary))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 5.6 [4.4408, 6.6296] | +3.6 [2.1006, 5.1079] | 27.0 | -23.4 [-26.3861, -20.3408] | 0.7886 |
| bil15 | 7.2 [5.7204, 8.6893] | +4.7 [2.7591, 6.8035] | 5.1 | -0.4 [-6.2898, 5.5573] | 0.7645 |
| bil21 | 6.8 [5.1796, 9.2665] | +2.5 [0.2757, 4.4869] | -16.0 | 18.5 [11.9787, 24.2187] | 0.7625 |
| median5 | 6.9 [5.5005, 8.6789] | -0.1 [-1.7158, 1.4844] | 19.2 | -19.3 [-22.1002, -16.6906] | 0.7788 |
| gblend | 5.6 [4.5419, 6.3144] | +3.0 [1.344, 3.8478] | 3.0 | 0.1 [-2.7882, 1.591] | 0.7956 |
| fl06 | 4.5 [3.3911, 5.78] | +5.9 [3.3768, 7.7231] | -42.1 | 48.0 [42.7533, 53.7241] | 0.7712 |
| fl12 | 4.3 [3.1359, 5.9054] | +10.2 [6.3786, 13.153] | -42.2 | 52.4 [47.3359, 58.5881] | 0.7313 |

```
{
 "commercial": {
  "smoothing90_accused": 7.6,
  "ci": [
   6.2443,
   9.0962
  ],
  "smoothing90_above_own": 72.0,
  "auroc_s90_vs_orig": 0.5888
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.8763,
  "ref": 0.956,
  "diff": -0.0797,
  "ci": [
   -0.1032,
   -0.0583
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9678,
  "ref": 0.9872,
  "diff": -0.0195,
  "ci": [
   -0.0335,
   -0.0072
  ]
 },
 "cdfb": {
  "auc_b": 0.8452,
  "ci": [
   0.8183,
   0.8701
  ],
  "main_auc_b": 0.866,
  "fa_b": 7.48,
  "d_miss_beauty_only": -0.81
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.6631,
   "ref": 0.8419,
   "diff": -0.1788,
   "ci": [
    -0.1922,
    -0.1639
   ]
  },
  "cdf": {
   "arm": 0.6054,
   "ref": 0.6466,
   "diff": -0.0413,
   "ci": [
    -0.0558,
    -0.0274
   ]
  }
 },
 "attribute": {
  "rule_amendment1": {
   "t_forged": 0.512,
   "orig_real": 82.71,
   "orig_forged": 0.27,
   "renders_beautified": 64.98,
   "renders_forged": 0.24,
   "balanced": 73.84,
   "by_op_level_beautified": {
    "EyeEnlarging_30": 45.2,
    "EyeEnlarging_60": 60.6,
    "EyeEnlarging_90": 69.5,
    "FaceLifting_30": 42.4,
    "FaceLifting_60": 51.4,
    "FaceLifting_90": 59.5,
    "Smoothing_30": 80.0,
    "Smoothing_60": 96.2,
    "Smoothing_90": 95.2,
    "Whitening_30": 48.5,
    "Whitening_60": 61.0,
    "Whitening_90": 70.6
   }
  },
  "native_argmax": {
   "orig": {
    "real": 82.67,
    "fake": 0.32,
    "filter": 17.01
   },
   "pooled": {
    "n": 26519,
    "to_real": 34.77,
    "to_fake": 0.26,
    "to_filter": 64.96,
    "balanced_acc": 73.98,
    "paired_rank": 93.67
   }
  },
  "presence": {
   "eq4": {
    "TP": {
     "eye": 0.232,
     "jaw": 0.312,
     "white": 0.392,
     "smooth": 0.858
    },
    "TN_same_image": {
     "eye": 0.792,
     "jaw": 0.917,
     "white": 0.816,
     "smooth": 0.537
    },
    "AC": {
     "eye": 0.225,
     "jaw": 0.301,
     "white": 0.308,
     "smooth": 0.409
    }
   },
   "orig_presence_TN_per_op": {
    "eye": 0.988,
    "jaw": 0.981,
    "white": 0.936,
    "smooth": 0.995
   },
   "orig_all_absent": 0.9
  },
  "vendor_val_log_tail": [
   "  }",
   " }",
   "}"
  ],
  "explain": {
   "donor": {
    "flip": 94.3,
    "iou7": 0.8324729237688032
   },
   "sd": {
    "flip": 93.1,
    "iou7": 0.8438418979862367
   },
   "sdxl": {
    "flip": 92.2,
    "iou7": 0.8160525274871817
   }
  }
 },
 "attribute_main_same_seed": {
  "rule_amendment1": {
   "t_forged": 0.6514,
   "orig_real": 78.69,
   "orig_forged": 0.36,
   "renders_beautified": 67.88,
   "renders_forged": 0.32,
   "balanced": 73.28,
   "by_op_level_beautified": {
    "EyeEnlarging_30": 46.6,
    "EyeEnlarging_60": 59.8,
    "EyeEnlarging_90": 69.8,
    "FaceLifting_30": 46.1,
    "FaceLifting_60": 53.7,
    "FaceLifting_90": 61.4,
    "Smoothing_30": 90.7,
    "Smoothing_60": 99.1,
    "Smoothing_90": 99.1,
    "Whitening_30": 51.8,
    "Whitening_60": 63.9,
    "Whitening_90": 72.5
   }
  },
  "native_argmax": {
   "orig": {
    "real": 78.37,
    "fake": 0.81,
    "filter": 20.81
   },
   "pooled": {
    "n": 26519,
    "to_real": 31.73,
    "to_fake": 0.55,
    "to_filter": 67.72,
    "balanced_acc": 73.45,
    "paired_rank": 92.94
   }
  },
  "presence": {
   "eq4": {
    "TP": {
     "eye": 0.196,
     "jaw": 0.322,
     "white": 0.375,
     "smooth": 0.943
    },
    "TN_same_image": {
     "eye": 0.766,
     "jaw": 0.916,
     "white": 0.8,
     "smooth": 0.433
    },
    "AC": {
     "eye": 0.185,
     "jaw": 0.311,
     "white": 0.297,
     "smooth": 0.384
    }
   },
   "orig_presence_TN_per_op": {
    "eye": 0.989,
    "jaw": 0.967,
    "white": 0.926,
    "smooth": 0.991
   },
   "orig_all_absent": 0.877
  },
  "vendor_val_log_tail": [
   "  }",
   " }",
   "}"
  ],
  "explain": {
   "donor": {
    "flip": 94.0,
    "iou7": 0.8331781113458491
   },
   "sd": {
    "flip": 93.6,
    "iou7": 0.8410225630161638
   },
   "sdxl": {
    "flip": 93.5,
    "iou7": 0.8310867794783112
   }
  }
 }
}
```

## clipe5z_s20260930 (not trained)

## clipe5bz_s20260929 (SIC binary (secondary))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 6.0 [4.7188, 6.9817] | +0.9 [-0.5125, 2.0354] | 27.0 | -26.1 [-28.9641, -23.401] | 0.7873 |
| bil15 | 7.0 [5.3644, 8.4537] | +3.1 [1.6404, 4.5243] | 5.1 | -2.1 [-7.6558, 3.3266] | 0.7561 |
| bil21 | 7.4 [5.3739, 9.4607] | +2.3 [0.529, 4.1765] | -16.0 | 18.4 [12.3836, 24.1398] | 0.7519 |
| median5 | 7.2 [5.5554, 8.9453] | -1.2 [-2.709, 0.0009] | 19.2 | -20.4 [-23.0863, -18.0386] | 0.7885 |
| gblend | 4.5 [3.9631, 5.3496] | +3.2 [2.2517, 4.3671] | 3.0 | 0.2 [-2.1523, 2.1169] | 0.7948 |
| fl06 | 4.9 [3.6737, 5.789] | +3.0 [1.3449, 4.1801] | -42.1 | 45.1 [39.9258, 50.6521] | 0.7904 |
| fl12 | 4.2 [3.163, 5.2037] | +7.8 [4.5518, 10.5895] | -42.2 | 50.0 [44.8675, 55.748] | 0.7494 |

```
{
 "commercial": {
  "smoothing90_accused": 7.1,
  "ci": [
   6.3348,
   8.4174
  ],
  "smoothing90_above_own": 70.0,
  "auroc_s90_vs_orig": 0.5686
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.8662,
  "ref": 0.956,
  "diff": -0.0898,
  "ci": [
   -0.1151,
   -0.0677
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9557,
  "ref": 0.9872,
  "diff": -0.0315,
  "ci": [
   -0.0495,
   -0.0176
  ]
 },
 "cdfb": {
  "auc_b": 0.8365,
  "ci": [
   0.8089,
   0.8624
  ],
  "main_auc_b": 0.866,
  "fa_b": 8.39,
  "d_miss_beauty_only": -2.44
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.7015,
   "ref": 0.8419,
   "diff": -0.1405,
   "ci": [
    -0.1538,
    -0.1267
   ]
  },
  "cdf": {
   "arm": 0.6619,
   "ref": 0.6466,
   "diff": 0.0152,
   "ci": [
    0.0014,
    0.0287
   ]
  }
 }
}
```

## clipe5bz_s20260930 (SIC binary (secondary))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 5.6 [4.5878, 7.4854] | -0.0 [-1.0719, 1.6098] | 26.7 | -26.8 [-30.1123, -23.7722] | 0.7791 |
| bil15 | 6.9 [5.57, 8.4493] | +2.3 [0.5527, 4.2783] | 6.1 | -3.8 [-9.732, 0.4602] | 0.7507 |
| bil21 | 7.4 [5.1509, 10.8951] | +2.2 [0.3293, 4.7745] | -11.8 | 14.0 [7.2653, 18.3891] | 0.7418 |
| median5 | 6.3 [5.1752, 8.2687] | -0.7 [-2.5442, 0.8257] | 18.0 | -18.6 [-21.7972, -16.1933] | 0.7767 |
| gblend | 4.7 [3.983, 5.6263] | +3.1 [1.7995, 4.6937] | 8.1 | -4.9 [-7.2725, -2.6789] | 0.7869 |
| fl06 | 4.7 [4.1362, 5.6444] | +1.5 [0.2298, 4.1309] | -37.7 | 39.2 [34.083, 46.4746] | 0.7831 |
| fl12 | 5.3 [4.417, 6.4323] | +6.3 [3.078, 10.0561] | -37.7 | 44.0 [38.1481, 51.2642] | 0.7333 |

```
{
 "commercial": {
  "smoothing90_accused": 7.6,
  "ci": [
   6.741,
   8.9604
  ],
  "smoothing90_above_own": 55.2,
  "auroc_s90_vs_orig": 0.521
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.8577,
  "ref": 0.9625,
  "diff": -0.1047,
  "ci": [
   -0.1326,
   -0.08
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9545,
  "ref": 0.9777,
  "diff": -0.0232,
  "ci": [
   -0.0405,
   -0.0094
  ]
 },
 "cdfb": {
  "auc_b": 0.8285,
  "ci": [
   0.8016,
   0.855
  ],
  "main_auc_b": 0.8828,
  "fa_b": 8.89,
  "d_miss_beauty_only": -4.11
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.7115,
   "ref": 0.8559,
   "diff": -0.1444,
   "ci": [
    -0.1577,
    -0.1319
   ]
  },
  "cdf": {
   "arm": 0.6637,
   "ref": 0.6976,
   "diff": -0.0338,
   "ci": [
    -0.0466,
    -0.0217
   ]
  }
 }
}
```

## clipe5bzl0_s20260929 (SIC binary, lambda 0 control (am. 2))

bars: 1_facelocal_fa<=15=False, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=True, 6_df40_reenactment_not_lower_by>0.030=True

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 2.2 [0.9906, 2.8669] | +23.7 [21.0705, 26.1451] | 27.0 | -3.3 [-6.1695, -0.5888] | 0.8633 |
| bil15 | 1.6 [0.5672, 2.277] | +32.3 [28.7445, 35.2795] | 5.1 | 27.2 [20.708, 33.3009] | 0.8318 |
| bil21 | 1.9 [0.5899, 3.2097] | +35.5 [32.021, 38.806] | -16.0 | 51.5 [44.4314, 57.7483] | 0.7978 |
| median5 | 4.4 [2.7546, 5.2158] | +12.0 [10.3797, 14.2218] | 19.2 | -7.3 [-9.2188, -4.4517] | 0.8668 |
| gblend | 5.0 [3.8918, 5.7251] | +5.9 [4.6608, 7.345] | 3.0 | 2.9 [0.4869, 5.02] | 0.8817 |
| fl06 | 53.9 [44.3567, 60.9245] | -35.2 [-41.0136, -30.6452] | -42.1 | 6.9 [1.9368, 11.8709] | 0.87 |
| fl12 | 91.8 [84.7311, 95.1071] | -40.1 [-47.1186, -34.7512] | -42.2 | 2.1 [-3.7084, 7.2204] | 0.7639 |

```
{
 "commercial": {
  "smoothing90_accused": 11.9,
  "ci": [
   10.4525,
   13.8462
  ],
  "smoothing90_above_own": 78.2,
  "auroc_s90_vs_orig": 0.6656
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.9428,
  "ref": 0.956,
  "diff": -0.0132,
  "ci": [
   -0.0255,
   -0.0018
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9748,
  "ref": 0.9872,
  "diff": -0.0125,
  "ci": [
   -0.0217,
   -0.0046
  ]
 },
 "cdfb": {
  "auc_b": 0.8908,
  "ci": [
   0.8688,
   0.9109
  ],
  "main_auc_b": 0.866,
  "fa_b": 6.83,
  "d_miss_beauty_only": 7.85
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.8349,
   "ref": 0.8419,
   "diff": -0.007,
   "ci": [
    -0.0143,
    0.0003
   ]
  },
  "cdf": {
   "arm": 0.6285,
   "ref": 0.6466,
   "diff": -0.0182,
   "ci": [
    -0.0262,
    -0.0104
   ]
  }
 }
}
```

## clipe5bzl0_s20260930 (not trained)

## clipe5bzl03_s20260929 (SIC binary, lambda 0.3 (am. 3))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 6.5 [5.0569, 7.7241] | +0.5 [-0.9235, 2.5749] | 27.0 | -26.5 [-29.3206, -23.3652] | 0.81 |
| bil15 | 8.1 [5.6453, 9.3752] | +5.1 [2.7509, 7.0658] | 5.1 | -0.1 [-6.0694, 5.5196] | 0.7743 |
| bil21 | 7.9 [5.4323, 9.6149] | +4.4 [1.9315, 6.3699] | -16.0 | 20.4 [13.631, 25.7184] | 0.768 |
| median5 | 7.3 [5.4347, 8.4241] | -2.5 [-4.3431, -0.9989] | 19.2 | -21.7 [-24.3531, -19.1637] | 0.8214 |
| gblend | 5.2 [4.1797, 5.7605] | +3.4 [2.0385, 4.3888] | 3.0 | 0.5 [-2.2946, 2.2092] | 0.8236 |
| fl06 | 4.7 [3.3204, 5.9206] | +5.7 [2.795, 7.8258] | -42.1 | 47.8 [42.6642, 53.3406] | 0.8094 |
| fl12 | 4.6 [3.0576, 5.7891] | +12.4 [8.4817, 15.6757] | -42.2 | 54.6 [49.4107, 60.3001] | 0.7608 |

```
{
 "commercial": {
  "smoothing90_accused": 9.9,
  "ci": [
   8.1448,
   12.0362
  ],
  "smoothing90_above_own": 68.6,
  "auroc_s90_vs_orig": 0.5787
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.8997,
  "ref": 0.956,
  "diff": -0.0563,
  "ci": [
   -0.0757,
   -0.0393
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9659,
  "ref": 0.9872,
  "diff": -0.0213,
  "ci": [
   -0.0352,
   -0.0101
  ]
 },
 "cdfb": {
  "auc_b": 0.8595,
  "ci": [
   0.8354,
   0.8826
  ],
  "main_auc_b": 0.866,
  "fa_b": 7.87,
  "d_miss_beauty_only": 1.27
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.7554,
   "ref": 0.8419,
   "diff": -0.0866,
   "ci": [
    -0.0985,
    -0.0745
   ]
  },
  "cdf": {
   "arm": 0.6442,
   "ref": 0.6466,
   "diff": -0.0024,
   "ci": [
    -0.0149,
    0.0095
   ]
  }
 }
}
```

## clipe5bzl03_s20260930 (not trained)

## clipe5bzl01_s20260929 (SIC binary, lambda 0.1 (am. 3))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=True, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 5.1 [3.9969, 6.9614] | +5.2 [2.7005, 7.4346] | 27.0 | -21.7 [-25.071, -18.6705] | 0.8323 |
| bil15 | 7.1 [5.3177, 8.8882] | +9.1 [6.682, 11.7204] | 5.1 | 3.9 [-1.9084, 9.679] | 0.791 |
| bil21 | 7.9 [6.1457, 10.8017] | +7.6 [5.1076, 10.2543] | -16.0 | 23.7 [17.274, 29.1549] | 0.7806 |
| median5 | 6.6 [5.354, 8.3029] | +0.5 [-1.0888, 2.1206] | 19.2 | -18.7 [-21.1655, -16.1266] | 0.8352 |
| gblend | 4.9 [4.0846, 6.7255] | +3.6 [1.8138, 4.6048] | 3.0 | 0.6 [-1.9384, 2.2676] | 0.8435 |
| fl06 | 4.3 [3.1542, 5.3692] | +8.2 [5.8505, 11.1791] | -42.1 | 50.4 [45.5076, 56.4484] | 0.8268 |
| fl12 | 3.3 [2.3001, 5.1338] | +18.6 [14.3795, 23.5066] | -42.2 | 60.8 [55.6353, 67.4491] | 0.7669 |

```
{
 "commercial": {
  "smoothing90_accused": 9.5,
  "ci": [
   8.1448,
   11.6742
  ],
  "smoothing90_above_own": 58.7,
  "auroc_s90_vs_orig": 0.5473
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.9214,
  "ref": 0.956,
  "diff": -0.0346,
  "ci": [
   -0.0525,
   -0.0191
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9738,
  "ref": 0.9872,
  "diff": -0.0134,
  "ci": [
   -0.0254,
   -0.0044
  ]
 },
 "cdfb": {
  "auc_b": 0.8818,
  "ci": [
   0.8601,
   0.9024
  ],
  "main_auc_b": 0.866,
  "fa_b": 7.45,
  "d_miss_beauty_only": 1.67
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.7605,
   "ref": 0.8419,
   "diff": -0.0814,
   "ci": [
    -0.0921,
    -0.0709
   ]
  },
  "cdf": {
   "arm": 0.6359,
   "ref": 0.6466,
   "diff": -0.0108,
   "ci": [
    -0.0225,
    -0.0001
   ]
  }
 }
}
```

## clipe5bzl01_s20260930 (not trained)

## clipe5bzsg_s20260929 (SIC binary, stop-gradient (am. 4))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 4.8 [3.5663, 6.4937] | +4.3 [2.7959, 6.1958] | 27.0 | -22.7 [-25.1086, -19.7001] | 0.8165 |
| bil15 | 5.8 [4.5914, 8.6285] | +5.7 [3.5252, 8.0325] | 5.1 | 0.6 [-4.5655, 6.2222] | 0.7897 |
| bil21 | 6.2 [4.379, 9.0208] | +5.5 [3.1433, 8.1428] | -16.0 | 21.6 [15.8476, 27.1924] | 0.7912 |
| median5 | 9.1 [6.9181, 12.6121] | -8.0 [-9.8096, -6.0971] | 19.2 | -27.2 [-29.817, -24.2896] | 0.8222 |
| gblend | 5.3 [4.6121, 7.1372] | -1.6 [-2.7336, 0.2954] | 3.0 | -4.6 [-6.7255, -2.2228] | 0.8335 |
| fl06 | 5.8 [4.9517, 7.6719] | +0.2 [-1.4079, 1.8016] | -42.1 | 42.3 [37.0731, 48.3646] | 0.8245 |
| fl12 | 4.4 [3.2598, 6.5506] | +9.7 [7.3277, 11.9429] | -42.2 | 51.9 [46.5473, 57.8519] | 0.7782 |

```
{
 "commercial": {
  "smoothing90_accused": 2.1,
  "ci": [
   1.5385,
   2.7149
  ],
  "smoothing90_above_own": 17.5,
  "auroc_s90_vs_orig": 0.3147
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.9072,
  "ref": 0.956,
  "diff": -0.0488,
  "ci": [
   -0.0682,
   -0.0324
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.986,
  "ref": 0.9872,
  "diff": -0.0012,
  "ci": [
   -0.0094,
   0.0063
  ]
 },
 "cdfb": {
  "auc_b": 0.8348,
  "ci": [
   0.8068,
   0.8631
  ],
  "main_auc_b": 0.866,
  "fa_b": 10.83,
  "d_miss_beauty_only": 3.17
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.7678,
   "ref": 0.8419,
   "diff": -0.0742,
   "ci": [
    -0.0867,
    -0.0619
   ]
  },
  "cdf": {
   "arm": 0.5994,
   "ref": 0.6466,
   "diff": -0.0472,
   "ci": [
    -0.0606,
    -0.0336
   ]
  }
 }
}
```

## clipe5bzsg_s20260930 (SIC binary, stop-gradient (am. 4))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 5.7 [4.4218, 7.0229] | +2.4 [1.0197, 3.873] | 26.7 | -24.3 [-27.785, -21.6943] | 0.7593 |
| bil15 | 6.3 [4.5309, 8.1239] | +4.2 [2.6217, 6.4845] | 6.1 | -1.8 [-7.3562, 2.555] | 0.7326 |
| bil21 | 7.3 [5.2209, 9.8498] | +3.6 [1.4881, 5.7616] | -11.8 | 15.4 [8.7523, 19.1041] | 0.7307 |
| median5 | 8.5 [6.8051, 10.7325] | -8.1 [-9.9739, -5.8253] | 18.0 | -26.1 [-29.0263, -23.2728] | 0.7774 |
| gblend | 5.6 [4.5703, 6.7552] | -0.1 [-0.9023, 1.3725] | 8.1 | -8.2 [-10.0077, -5.9306] | 0.776 |
| fl06 | 6.2 [4.845, 7.757] | -0.9 [-2.2224, 0.5817] | -37.7 | 36.8 [30.7924, 43.3809] | 0.7692 |
| fl12 | 5.5 [4.0607, 7.1772] | +6.1 [4.205, 7.8006] | -37.7 | 43.8 [37.7387, 50.2741] | 0.7204 |

```
{
 "commercial": {
  "smoothing90_accused": 12.3,
  "ci": [
   9.7285,
   14.3891
  ],
  "smoothing90_above_own": 92.2,
  "auroc_s90_vs_orig": 0.7374
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.8442,
  "ref": 0.9625,
  "diff": -0.1182,
  "ci": [
   -0.148,
   -0.0914
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9684,
  "ref": 0.9777,
  "diff": -0.0092,
  "ci": [
   -0.0206,
   0.0023
  ]
 },
 "cdfb": {
  "auc_b": 0.8044,
  "ci": [
   0.7746,
   0.8344
  ],
  "main_auc_b": 0.8828,
  "fa_b": 10.03,
  "d_miss_beauty_only": -0.99
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.746,
   "ref": 0.8559,
   "diff": -0.1099,
   "ci": [
    -0.1222,
    -0.0967
   ]
  },
  "cdf": {
   "arm": 0.5775,
   "ref": 0.6976,
   "diff": -0.1201,
   "ci": [
    -0.1332,
    -0.106
   ]
  }
 }
}
```

## clipe5fbzsg_s20260929 (FF++-only SIC binary, stop-gradient (am. 4/5))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 4.6 [3.503, 6.3413] | +3.9 [2.516, 6.0033] | 27.0 | -23.1 [-25.591, -20.0961] | 0.7671 |
| bil15 | 5.3 [4.1103, 7.8752] | +7.2 [5.2657, 9.3526] | 5.1 | 2.1 [-3.054, 7.4394] | 0.7284 |
| bil21 | 6.0 [4.5052, 8.0632] | +8.9 [6.8926, 11.4208] | -16.0 | 24.9 [18.9997, 30.5881] | 0.7182 |
| median5 | 10.9 [8.6516, 15.109] | -7.7 [-9.6266, -5.9797] | 19.2 | -26.9 [-29.5891, -24.2818] | 0.7568 |
| gblend | 5.4 [4.565, 6.8255] | +0.7 [-0.3247, 1.8606] | 3.0 | -2.2 [-4.6277, -0.4527] | 0.7759 |
| fl06 | 7.4 [6.4454, 9.4961] | -3.8 [-5.539, -2.5315] | -42.1 | 38.3 [32.3694, 44.1372] | 0.775 |
| fl12 | 6.8 [5.5873, 8.9037] | +4.8 [2.9549, 6.3998] | -42.2 | 47.0 [41.6885, 52.8148] | 0.7214 |

```
{
 "commercial": {
  "smoothing90_accused": 7.0,
  "ci": [
   5.7014,
   8.371
  ],
  "smoothing90_above_own": 78.4,
  "auroc_s90_vs_orig": 0.6219
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.8557,
  "ref": 0.956,
  "diff": -0.1003,
  "ci": [
   -0.1283,
   -0.0758
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.979,
  "ref": 0.9872,
  "diff": -0.0082,
  "ci": [
   -0.0191,
   0.0017
  ]
 },
 "cdfb": {
  "auc_b": 0.8292,
  "ci": [
   0.8011,
   0.8555
  ],
  "main_auc_b": 0.866,
  "fa_b": 9.55,
  "d_miss_beauty_only": 6.57
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.6741,
   "ref": 0.8419,
   "diff": -0.1678,
   "ci": [
    -0.1829,
    -0.1525
   ]
  },
  "cdf": {
   "arm": 0.6021,
   "ref": 0.6466,
   "diff": -0.0446,
   "ci": [
    -0.0605,
    -0.0298
   ]
  }
 }
}
```

## clipe5fbzsg_s20260930 (not trained)

## clipe5bzsgl03_s20260929 (SIC-sg binary, lambda 0.3 (am. 6))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 5.9 [4.6882, 7.2792] | +0.3 [-1.4058, 2.203] | 27.0 | -26.7 [-29.5798, -23.7484] | 0.7986 |
| bil15 | 8.1 [5.6424, 10.0866] | +3.9 [1.4053, 5.6352] | 5.1 | -1.3 [-7.0663, 4.0877] | 0.7653 |
| bil21 | 8.3 [5.9455, 10.6433] | +4.1 [1.1303, 6.3538] | -16.0 | 20.1 [13.8002, 25.5522] | 0.7563 |
| median5 | 9.6 [7.4466, 11.5582] | -8.3 [-10.3307, -5.9983] | 19.2 | -27.5 [-30.4435, -24.3171] | 0.8086 |
| gblend | 6.2 [4.4422, 7.1429] | +0.0 [-1.3371, 1.1263] | 3.0 | -3.0 [-5.6232, -1.1481] | 0.819 |
| fl06 | 6.0 [4.338, 7.3828] | -2.4 [-4.4944, -0.5232] | -42.1 | 39.8 [34.0511, 45.2235] | 0.8195 |
| fl12 | 4.2 [3.0229, 5.4574] | +9.5 [6.3981, 12.564] | -42.2 | 51.7 [46.0123, 57.5016] | 0.7594 |

```
{
 "commercial": {
  "smoothing90_accused": 12.8,
  "ci": [
   10.2715,
   16.6063
  ],
  "smoothing90_above_own": 86.8,
  "auroc_s90_vs_orig": 0.7629
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.8985,
  "ref": 0.956,
  "diff": -0.0575,
  "ci": [
   -0.0755,
   -0.0409
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9714,
  "ref": 0.9872,
  "diff": -0.0159,
  "ci": [
   -0.0276,
   -0.006
  ]
 },
 "cdfb": {
  "auc_b": 0.8395,
  "ci": [
   0.8123,
   0.8664
  ],
  "main_auc_b": 0.866,
  "fa_b": 11.68,
  "d_miss_beauty_only": 0.26
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.692,
   "ref": 0.8419,
   "diff": -0.1499,
   "ci": [
    -0.1623,
    -0.1374
   ]
  },
  "cdf": {
   "arm": 0.5685,
   "ref": 0.6466,
   "diff": -0.0781,
   "ci": [
    -0.0895,
    -0.0661
   ]
  }
 }
}
```

## clipe5bzsgl03_s20260930 (not trained)

## clipe5bzsgl01_s20260929 (SIC-sg binary, lambda 0.1 (am. 6))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=True, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 7.8 [5.5906, 8.9043] | -0.1 [-2.2721, 1.4389] | 27.0 | -27.1 [-30.2138, -24.4898] | 0.8412 |
| bil15 | 9.9 [6.4946, 11.7652] | +3.8 [1.137, 6.1388] | 5.1 | -1.3 [-6.3836, 3.9735] | 0.8019 |
| bil21 | 11.1 [7.3338, 13.912] | +1.8 [-0.8872, 5.2103] | -16.0 | 17.8 [12.2889, 23.7143] | 0.7948 |
| median5 | 9.6 [7.5289, 10.9925] | -6.3 [-8.2215, -4.4141] | 19.2 | -25.5 [-28.0921, -22.7821] | 0.8433 |
| gblend | 6.4 [4.5151, 7.3182] | +0.8 [-0.3512, 2.3832] | 3.0 | -2.1 [-4.4069, -0.1135] | 0.8497 |
| fl06 | 6.5 [4.7951, 7.3021] | +1.9 [-0.2561, 3.5852] | -42.1 | 44.0 [38.277, 49.4535] | 0.8407 |
| fl12 | 4.2 [2.8791, 5.3755] | +15.8 [12.7635, 18.3933] | -42.2 | 58.0 [52.4362, 63.4998] | 0.7783 |

```
{
 "commercial": {
  "smoothing90_accused": 10.5,
  "ci": [
   8.8235,
   11.9016
  ],
  "smoothing90_above_own": 43.1,
  "auroc_s90_vs_orig": 0.4484
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.9299,
  "ref": 0.956,
  "diff": -0.0261,
  "ci": [
   -0.0412,
   -0.0118
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9801,
  "ref": 0.9872,
  "diff": -0.0071,
  "ci": [
   -0.0182,
   0.0014
  ]
 },
 "cdfb": {
  "auc_b": 0.8706,
  "ci": [
   0.8474,
   0.8925
  ],
  "main_auc_b": 0.866,
  "fa_b": 7.07,
  "d_miss_beauty_only": 7.37
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.7743,
   "ref": 0.8419,
   "diff": -0.0676,
   "ci": [
    -0.0773,
    -0.0587
   ]
  },
  "cdf": {
   "arm": 0.6175,
   "ref": 0.6466,
   "diff": -0.0292,
   "ci": [
    -0.0406,
    -0.0184
   ]
  }
 }
}
```

## clipe5bzsgl01_s20260930 (SIC-sg binary, lambda 0.1 (am. 6))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 6.7 [5.3996, 8.5894] | +4.5 [2.3513, 6.6314] | 26.7 | -22.2 [-26.069, -19.1347] | 0.8249 |
| bil15 | 8.5 [6.545, 12.1696] | +8.5 [5.273, 11.1081] | 6.1 | 2.4 [-3.473, 6.3162] | 0.7845 |
| bil21 | 10.2 [7.2163, 14.6436] | +7.2 [3.4793, 10.009] | -11.8 | 19.0 [12.2171, 22.5761] | 0.7696 |
| median5 | 7.2 [6.1335, 9.4416] | -4.5 [-6.0745, -2.2207] | 18.0 | -22.4 [-25.2554, -19.561] | 0.837 |
| gblend | 5.4 [4.7902, 7.3283] | +0.9 [-0.395, 1.9923] | 8.1 | -7.2 [-9.3979, -5.4983] | 0.8449 |
| fl06 | 4.6 [3.7979, 6.0244] | +5.7 [3.7145, 7.6489] | -37.7 | 43.4 [37.4219, 50.0387] | 0.8223 |
| fl12 | 4.6 [3.5737, 6.4987] | +17.6 [14.6037, 20.8355] | -37.7 | 55.3 [49.2983, 62.119] | 0.7602 |

```
{
 "commercial": {
  "smoothing90_accused": 8.1,
  "ci": [
   6.9672,
   9.9095
  ],
  "smoothing90_above_own": 73.3,
  "auroc_s90_vs_orig": 0.6421
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.929,
  "ref": 0.9625,
  "diff": -0.0335,
  "ci": [
   -0.0497,
   -0.019
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9742,
  "ref": 0.9777,
  "diff": -0.0035,
  "ci": [
   -0.0118,
   0.0052
  ]
 },
 "cdfb": {
  "auc_b": 0.8678,
  "ci": [
   0.8436,
   0.8897
  ],
  "main_auc_b": 0.8828,
  "fa_b": 8.04,
  "d_miss_beauty_only": 3.19
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.7706,
   "ref": 0.8559,
   "diff": -0.0853,
   "ci": [
    -0.0947,
    -0.076
   ]
  },
  "cdf": {
   "arm": 0.6289,
   "ref": 0.6976,
   "diff": -0.0687,
   "ci": [
    -0.0781,
    -0.0597
   ]
  }
 }
}
```

## clipe5bzsgG_s20260929 (SIC-sg binary, Gaussian operator ablation (am. 7))

bars: 1_facelocal_fa<=15=False, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 0.7 [0.0733, 1.4578] | +21.7 [18.1961, 25.9056] | 27.0 | -5.3 [-9.7119, -0.7662] | 0.7413 |
| bil15 | 1.1 [0.2932, 2.2974] | +19.9 [16.5063, 23.4096] | 5.1 | 14.8 [8.6116, 21.1745] | 0.7026 |
| bil21 | 3.7 [1.8609, 6.7339] | +14.0 [11.2693, 16.6488] | -16.0 | 30.1 [23.9129, 35.7004] | 0.6936 |
| median5 | 5.6 [4.0426, 7.3784] | +4.0 [2.4573, 5.6095] | 19.2 | -15.2 [-17.6913, -12.4983] | 0.7534 |
| gblend | 4.4 [3.7374, 5.2565] | +1.5 [0.1133, 2.9413] | 3.0 | -1.4 [-4.1125, 0.6384] | 0.7943 |
| fl06 | 5.8 [4.5949, 7.6805] | +1.8 [0.0, 3.6618] | -42.1 | 44.0 [38.8876, 49.4897] | 0.7602 |
| fl12 | 19.5 [15.3951, 25.4723] | -13.5 [-15.9187, -10.9015] | -42.2 | 28.7 [23.3723, 34.3596] | 0.7049 |

```
{
 "commercial": {
  "smoothing90_accused": 3.5,
  "ci": [
   2.8959,
   4.2534
  ],
  "smoothing90_above_own": 21.9,
  "auroc_s90_vs_orig": 0.3542
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.8546,
  "ref": 0.956,
  "diff": -0.1014,
  "ci": [
   -0.128,
   -0.0759
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9713,
  "ref": 0.9872,
  "diff": -0.0159,
  "ci": [
   -0.0284,
   -0.0042
  ]
 },
 "cdfb": {
  "auc_b": 0.8192,
  "ci": [
   0.7899,
   0.8465
  ],
  "main_auc_b": 0.866,
  "fa_b": 8.92,
  "d_miss_beauty_only": -2.6
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.7822,
   "ref": 0.8419,
   "diff": -0.0597,
   "ci": [
    -0.0728,
    -0.0474
   ]
  },
  "cdf": {
   "arm": 0.5845,
   "ref": 0.6466,
   "diff": -0.0622,
   "ci": [
    -0.0768,
    -0.047
   ]
  }
 }
}
```

## clipe5bzsgG_s20260930 (SIC-sg binary, Gaussian operator ablation (am. 7))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 0.7 [0.0698, 1.5422] | +20.1 [17.4571, 23.0106] | 26.7 | -6.7 [-10.6049, -2.9888] | 0.7089 |
| bil15 | 1.3 [0.3577, 2.7646] | +17.9 [15.0652, 20.7459] | 6.1 | 11.8 [5.7694, 16.2493] | 0.7039 |
| bil21 | 3.9 [2.2362, 8.0333] | +10.5 [5.9638, 14.0888] | -11.8 | 22.3 [15.6166, 26.6109] | 0.7062 |
| median5 | 5.7 [4.3443, 7.5803] | +4.0 [2.6508, 5.4722] | 18.0 | -14.0 [-16.6265, -11.6574] | 0.7246 |
| gblend | 4.4 [3.5255, 5.4807] | +2.9 [1.9906, 4.0496] | 8.1 | -5.1 [-7.1485, -3.1806] | 0.7688 |
| fl06 | 5.9 [4.6076, 7.1938] | +3.2 [1.2815, 4.4749] | -37.7 | 40.9 [34.7211, 46.9711] | 0.7509 |
| fl12 | 14.5 [11.8828, 18.2116] | -9.3 [-11.6946, -7.1149] | -37.7 | 28.4 [21.836, 35.3626] | 0.7044 |

```
{
 "commercial": {
  "smoothing90_accused": 8.7,
  "ci": [
   7.4208,
   9.9095
  ],
  "smoothing90_above_own": 68.0,
  "auroc_s90_vs_orig": 0.5849
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.8476,
  "ref": 0.9625,
  "diff": -0.1149,
  "ci": [
   -0.1488,
   -0.085
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9597,
  "ref": 0.9777,
  "diff": -0.0179,
  "ci": [
   -0.033,
   -0.0045
  ]
 },
 "cdfb": {
  "auc_b": 0.8214,
  "ci": [
   0.7912,
   0.8493
  ],
  "main_auc_b": 0.8828,
  "fa_b": 12.52,
  "d_miss_beauty_only": -8.21
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.7837,
   "ref": 0.8559,
   "diff": -0.0722,
   "ci": [
    -0.0844,
    -0.0615
   ]
  },
  "cdf": {
   "arm": 0.576,
   "ref": 0.6976,
   "diff": -0.1216,
   "ci": [
    -0.136,
    -0.107
   ]
  }
 }
}
```

## clipe5bzsgh_s20260929 (SIC-h binary, one-sided consistency (am. 8))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=True, 5_cdfb_auc_b>=main=True, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 0.0 [0.0, 0.0] | +54.2 [47.7902, 60.1831] | 27.0 | 27.2 [20.1489, 33.2882] | 0.7956 |
| bil15 | 0.0 [0.0, 0.0] | +56.0 [49.1889, 62.4721] | 5.1 | 50.9 [41.6757, 59.4326] | 0.7275 |
| bil21 | 0.0 [0.0, 0.0] | +56.4 [49.3915, 62.7186] | -16.0 | 72.4 [62.782, 80.7672] | 0.6909 |
| median5 | 2.3 [1.2571, 3.3972] | +23.5 [20.9451, 25.8241] | 19.2 | 4.3 [1.4741, 6.8227] | 0.84 |
| gblend | 6.0 [4.7544, 6.9861] | +2.2 [0.8727, 3.831] | 3.0 | -0.7 [-3.0833, 1.3795] | 0.8709 |
| fl06 | 0.1 [0.0, 0.3645] | +54.3 [47.7411, 60.1161] | -42.1 | 96.5 [90.1875, 102.6026] | 0.6671 |
| fl12 | 0.1 [0.0, 0.236] | +56.5 [49.5009, 63.0082] | -42.2 | 98.7 [92.208, 105.4794] | 0.6029 |

```
{
 "commercial": {
  "smoothing90_accused": 9.2,
  "ci": [
   8.0079,
   10.724
  ],
  "smoothing90_above_own": 44.4,
  "auroc_s90_vs_orig": 0.4637
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.9537,
  "ref": 0.956,
  "diff": -0.0023,
  "ci": [
   -0.015,
   0.0091
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9798,
  "ref": 0.9872,
  "diff": -0.0074,
  "ci": [
   -0.016,
   -0.001
  ]
 },
 "cdfb": {
  "auc_b": 0.8799,
  "ci": [
   0.8564,
   0.9003
  ],
  "main_auc_b": 0.866,
  "fa_b": 7.07,
  "d_miss_beauty_only": 11.76
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.7941,
   "ref": 0.8419,
   "diff": -0.0478,
   "ci": [
    -0.0574,
    -0.0391
   ]
  },
  "cdf": {
   "arm": 0.6316,
   "ref": 0.6466,
   "diff": -0.015,
   "ci": [
    -0.026,
    -0.0041
   ]
  }
 }
}
```

## clipe5bzsgh_s20260930 (SIC-h binary, one-sided consistency (am. 8))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 0.0 [0.0, 0.0] | +45.8 [40.5022, 51.618] | 26.7 | 19.1 [12.9456, 25.0307] | 0.783 |
| bil15 | 0.0 [0.0, 0.0] | +47.0 [41.3384, 53.1934] | 6.1 | 40.9 [32.7129, 48.6045] | 0.7384 |
| bil21 | 0.0 [0.0, 0.0] | +47.0 [41.4948, 53.6653] | -11.8 | 58.8 [50.6921, 66.4905] | 0.7143 |
| median5 | 1.9 [1.0462, 2.8926] | +21.5 [19.4093, 25.1023] | 18.0 | 3.6 [0.6503, 7.3304] | 0.8084 |
| gblend | 5.6 [4.7301, 6.886] | +4.6 [3.4707, 6.155] | 8.1 | -3.5 [-5.6203, -1.169] | 0.8383 |
| fl06 | 0.1 [0.0, 0.2578] | +45.2 [39.984, 51.6603] | -37.7 | 82.8 [76.9402, 90.2098] | 0.6541 |
| fl12 | 0.0 [0.0, 0.0] | +47.3 [41.4033, 54.2986] | -37.7 | 85.0 [78.7338, 92.6862] | 0.6056 |

```
{
 "commercial": {
  "smoothing90_accused": 10.4,
  "ci": [
   8.0079,
   12.2624
  ],
  "smoothing90_above_own": 63.2,
  "auroc_s90_vs_orig": 0.5998
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.9288,
  "ref": 0.9625,
  "diff": -0.0336,
  "ci": [
   -0.0497,
   -0.0182
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9748,
  "ref": 0.9777,
  "diff": -0.0029,
  "ci": [
   -0.0127,
   0.0064
  ]
 },
 "cdfb": {
  "auc_b": 0.8598,
  "ci": [
   0.834,
   0.8828
  ],
  "main_auc_b": 0.8828,
  "fa_b": 6.66,
  "d_miss_beauty_only": 7.34
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.7751,
   "ref": 0.8559,
   "diff": -0.0808,
   "ci": [
    -0.0894,
    -0.072
   ]
  },
  "cdf": {
   "arm": 0.6064,
   "ref": 0.6976,
   "diff": -0.0912,
   "ci": [
    -0.1011,
    -0.0804
   ]
  }
 }
}
```

## clipe5bzsgl003_s20260929 (SIC-sg binary, lambda 0.03 (am. 9))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=True, 5_cdfb_auc_b>=main=True, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 7.4 [5.6823, 9.1823] | +0.9 [-1.0605, 3.2821] | 27.0 | -26.1 [-29.0422, -22.9033] | 0.8541 |
| bil15 | 9.6 [7.6251, 12.5005] | +6.1 [3.1031, 8.6657] | 5.1 | 1.0 [-4.5737, 5.8946] | 0.8043 |
| bil21 | 11.6 [8.7578, 15.874] | +6.0 [2.5861, 9.0016] | -16.0 | 22.0 [15.4597, 27.203] | 0.7879 |
| median5 | 10.3 [7.9738, 12.3937] | -6.0 [-8.0195, -4.068] | 19.2 | -25.3 [-27.8002, -22.6233] | 0.8555 |
| gblend | 6.9 [5.6009, 8.763] | -1.3 [-2.3593, 0.8344] | 3.0 | -4.2 [-6.4972, -2.0403] | 0.867 |
| fl06 | 5.0 [3.8491, 6.3989] | +9.9 [7.396, 12.0718] | -42.1 | 52.0 [46.3997, 57.9527] | 0.8384 |
| fl12 | 3.3 [2.2938, 4.6181] | +24.4 [21.1009, 28.1972] | -42.2 | 66.6 [61.3173, 72.7564] | 0.7706 |

```
{
 "commercial": {
  "smoothing90_accused": 11.2,
  "ci": [
   9.3665,
   13.7557
  ],
  "smoothing90_above_own": 51.7,
  "auroc_s90_vs_orig": 0.5105
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.946,
  "ref": 0.956,
  "diff": -0.01,
  "ci": [
   -0.0233,
   0.0018
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9789,
  "ref": 0.9872,
  "diff": -0.0083,
  "ci": [
   -0.0163,
   -0.0025
  ]
 },
 "cdfb": {
  "auc_b": 0.8857,
  "ci": [
   0.8633,
   0.9064
  ],
  "main_auc_b": 0.866,
  "fa_b": 7.16,
  "d_miss_beauty_only": 7.73
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.7501,
   "ref": 0.8419,
   "diff": -0.0918,
   "ci": [
    -0.102,
    -0.0822
   ]
  },
  "cdf": {
   "arm": 0.6206,
   "ref": 0.6466,
   "diff": -0.026,
   "ci": [
    -0.0364,
    -0.0151
   ]
  }
 }
}
```

## clipe5bzsgl003_s20260930 (SIC-sg binary, lambda 0.03 (am. 9))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=True, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 5.8 [4.8759, 7.2043] | +3.4 [1.6292, 6.1945] | 26.7 | -23.3 [-26.6676, -19.94] | 0.8411 |
| bil15 | 8.8 [6.9263, 11.3385] | +8.3 [6.1261, 11.4923] | 6.1 | 2.2 [-2.9016, 6.8723] | 0.7887 |
| bil21 | 11.6 [8.995, 15.5507] | +7.0 [4.3906, 10.3061] | -11.8 | 18.9 [12.6643, 22.629] | 0.7733 |
| median5 | 7.2 [5.7389, 9.3886] | -1.1 [-2.4034, 1.5487] | 18.0 | -19.1 [-21.4855, -15.8753] | 0.8392 |
| gblend | 5.0 [4.1124, 6.3555] | +2.2 [1.5978, 4.3448] | 8.1 | -5.8 [-7.3688, -3.0355] | 0.8505 |
| fl06 | 3.8 [2.5396, 5.4514] | +10.0 [8.3561, 14.0331] | -37.7 | 47.7 [42.3535, 54.7049] | 0.825 |
| fl12 | 3.5 [2.1288, 4.9037] | +20.4 [17.8222, 25.2071] | -37.7 | 58.1 [52.5828, 65.6714] | 0.7601 |

```
{
 "commercial": {
  "smoothing90_accused": 15.0,
  "ci": [
   12.6244,
   16.6063
  ],
  "smoothing90_above_own": 75.3,
  "auroc_s90_vs_orig": 0.6827
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.9331,
  "ref": 0.9625,
  "diff": -0.0293,
  "ci": [
   -0.0447,
   -0.0152
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9749,
  "ref": 0.9777,
  "diff": -0.0027,
  "ci": [
   -0.0114,
   0.0056
  ]
 },
 "cdfb": {
  "auc_b": 0.8763,
  "ci": [
   0.8532,
   0.8969
  ],
  "main_auc_b": 0.8828,
  "fa_b": 7.66,
  "d_miss_beauty_only": 4.45
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.7773,
   "ref": 0.8559,
   "diff": -0.0786,
   "ci": [
    -0.0872,
    -0.07
   ]
  },
  "cdf": {
   "arm": 0.5926,
   "ref": 0.6976,
   "diff": -0.105,
   "ci": [
    -0.1154,
    -0.0948
   ]
  }
 }
}
```

## clipe5bzxs_s20260929 (smoothing expert, trained on x_s only (Add. 48))

bars: 1_facelocal_fa<=15=False, 3_as_written=False, 3prime=False, 2_bil15_21_fa<=15_and_S90<=15=False, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 91.5 [85.3412, 95.861] | -51.3 [-57.4447, -44.7556] | 27.0 | -78.3 [-85.0384, -71.5907] | 0.7737 |
| bil15 | 93.5 [87.9705, 96.9915] | -51.2 [-57.4141, -44.7726] | 5.1 | -56.3 [-64.5401, -48.4063] | 0.738 |
| bil21 | 93.4 [86.6862, 96.8808] | -51.1 [-57.3174, -44.854] | -16.0 | -35.1 [-43.4247, -27.4717] | 0.7379 |
| median5 | 68.5 [58.0365, 77.1651] | -37.5 [-41.5933, -33.1494] | 19.2 | -56.7 [-61.3412, -51.741] | 0.7182 |
| gblend | 3.0 [1.9794, 4.0744] | +9.4 [7.6981, 10.8221] | 3.0 | 6.4 [3.7343, 8.4229] | 0.813 |
| fl06 | 10.8 [8.7704, 12.9815] | -9.6 [-11.6687, -7.6343] | -42.1 | 32.5 [27.099, 38.2078] | 0.8353 |
| fl12 | 16.4 [12.0495, 19.9877] | -11.2 [-13.7226, -8.053] | -42.2 | 31.0 [25.6771, 37.0889] | 0.7993 |

```
{
 "commercial": {
  "smoothing90_accused": 12.5,
  "ci": [
   11.0407,
   14.8416
  ],
  "smoothing90_above_own": 70.0,
  "auroc_s90_vs_orig": 0.6179
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.9037,
  "ref": 0.956,
  "diff": -0.0523,
  "ci": [
   -0.0773,
   -0.0276
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9776,
  "ref": 0.9872,
  "diff": -0.0096,
  "ci": [
   -0.0251,
   0.0028
  ]
 },
 "cdfb": {
  "auc_b": 0.8362,
  "ci": [
   0.8046,
   0.8641
  ],
  "main_auc_b": 0.866,
  "fa_b": 9.99,
  "d_miss_beauty_only": -0.21
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.5288,
   "ref": 0.8419,
   "diff": -0.3132,
   "ci": [
    -0.3306,
    -0.295
   ]
  },
  "cdf": {
   "arm": 0.5528,
   "ref": 0.6466,
   "diff": -0.0939,
   "ci": [
    -0.1111,
    -0.0768
   ]
  }
 }
}
```

## clipe5bzxs_s20260930 (smoothing expert, trained on x_s only (Add. 48))

bars: 1_facelocal_fa<=15=True, 3_as_written=False, 3prime=True, 2_bil15_21_fa<=15_and_S90<=15=False, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 70.0 [56.5776, 79.6474] | -51.8 [-55.7605, -47.1192] | 26.7 | -78.5 [-83.9486, -72.9746] | 0.8014 |
| bil15 | 76.6 [63.1646, 84.2408] | -52.4 [-56.6799, -47.264] | 6.1 | -58.5 [-65.4696, -51.9723] | 0.7518 |
| bil21 | 75.7 [60.4992, 83.7065] | -51.3 [-55.1304, -46.478] | -11.8 | -39.5 [-46.5353, -34.032] | 0.7443 |
| median5 | 59.2 [46.5583, 69.0462] | -42.3 [-45.7753, -37.9614] | 18.0 | -60.2 [-64.6926, -55.6577] | 0.7511 |
| gblend | 5.7 [4.4368, 6.6723] | +1.6 [0.7062, 2.8979] | 8.1 | -6.4 [-8.377, -4.5054] | 0.8009 |
| fl06 | 11.7 [9.304, 14.2286] | -13.6 [-15.7267, -10.0756] | -37.7 | 24.0 [18.1045, 31.9491] | 0.816 |
| fl12 | 13.6 [9.6159, 17.0827] | -6.3 [-9.4232, -2.6353] | -37.7 | 31.4 [24.4348, 39.1056] | 0.7697 |

```
{
 "commercial": {
  "smoothing90_accused": 12.8,
  "ci": [
   11.4921,
   14.6606
  ],
  "smoothing90_above_own": 68.8,
  "auroc_s90_vs_orig": 0.607
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.8796,
  "ref": 0.9625,
  "diff": -0.0829,
  "ci": [
   -0.1125,
   -0.0557
  ]
 },
 "untreated_dfd_video_vs_binary": null,
 "cdfb": {
  "auc_b": null,
  "ci": null,
  "main_auc_b": 0.8828,
  "fa_b": null,
  "d_miss_beauty_only": null
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.4679,
   "ref": 0.8559,
   "diff": -0.388,
   "ci": [
    -0.4057,
    -0.3696
   ]
  },
  "cdf": {
   "arm": 0.4716,
   "ref": 0.6976,
   "diff": -0.226,
   "ci": [
    -0.2415,
    -0.2108
   ]
  }
 }
}
```

## clipe5fbp0F2_s20260929 (P0 with Face2Face+FaceSwap forgeries only (Add. 49))

bars: 1_facelocal_fa<=15=False, 3_as_written=True, 3prime=True, 2_bil15_21_fa<=15_and_S90<=15=False, 4_untreated_video_not_lower_than_binary_by>0.010=False, 5_cdfb_auc_b>=main=True, 6_df40_reenactment_not_lower_by>0.030=False

| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |
|---|---|---|---|---|---|
| bil9 | 6.6 [4.4917, 8.3966] | +10.4 [8.0439, 13.1925] | 27.0 | -16.6 [-19.5186, -13.4407] | 0.816 |
| bil15 | 17.1 [12.1033, 23.5346] | +0.5 [-4.4637, 6.5208] | 5.1 | -4.6 [-10.0971, 1.52] | 0.7657 |
| bil21 | 38.3 [26.2909, 51.6718] | -18.9 [-24.7103, -11.5336] | -16.0 | -2.8 [-8.9709, 4.2401] | 0.7476 |
| median5 | 6.7 [5.2221, 8.3825] | +6.0 [3.8209, 7.5138] | 19.2 | -13.3 [-15.8798, -11.0474] | 0.815 |
| gblend | 6.5 [5.1122, 7.7391] | +1.1 [-0.1549, 2.8075] | 3.0 | -1.9 [-4.0501, 0.1796] | 0.845 |
| fl06 | 95.5 [92.9906, 97.5359] | -44.8 [-51.5745, -38.6623] | -42.1 | -2.6 [-8.3774, 3.2631] | 0.7814 |
| fl12 | 100.0 [100.0, 100.0] | -45.0 [-51.8406, -38.7381] | -42.2 | -2.8 [-8.6625, 3.2953] | 0.6008 |

```
{
 "commercial": {
  "smoothing90_accused": 33.5,
  "ci": [
   29.9989,
   37.7828
  ],
  "smoothing90_above_own": 94.3,
  "auroc_s90_vs_orig": 0.8047
 },
 "untreated_cdf_video_vs_binary": {
  "arm": 0.9177,
  "ref": 0.956,
  "diff": -0.0384,
  "ci": [
   -0.0651,
   -0.0183
  ]
 },
 "untreated_dfd_video_vs_binary": {
  "arm": 0.9838,
  "ref": 0.9872,
  "diff": -0.0034,
  "ci": [
   -0.015,
   0.0084
  ]
 },
 "cdfb": {
  "auc_b": 0.8682,
  "ci": [
   0.8408,
   0.8925
  ],
  "main_auc_b": 0.866,
  "fa_b": 4.59,
  "d_miss_beauty_only": 11.9
 },
 "df40_reenactment_vs_binary": {
  "ff": {
   "arm": 0.631,
   "ref": 0.8419,
   "diff": -0.211,
   "ci": [
    -0.2274,
    -0.1933
   ]
  },
  "cdf": {
   "arm": 0.5166,
   "ref": 0.6466,
   "diff": -0.13,
   "ci": [
    -0.1473,
    -0.1132
   ]
  }
 }
}
```

## clipe5fbp0F2_s20260930 (not trained)

## clipe5bzEsg_s20260929 (not trained)

## clipe5bzEsg_s20260930 (not trained)

**reading_clipe5z**: incomplete

**reading_clipe5bz**: negative: 3prime (clipe5bz_s20260929), 3prime (clipe5bz_s20260930), 4_untreated_video_not_lower_than_binary_by>0.010 (clipe5bz_s20260929), 4_untreated_video_not_lower_than_binary_by>0.010 (clipe5bz_s20260930), 5_cdfb_auc_b>=main (clipe5bz_s20260929), 5_cdfb_auc_b>=main (clipe5bz_s20260930), 6_df40_reenactment_not_lower_by>0.030 (clipe5bz_s20260929), 6_df40_reenactment_not_lower_by>0.030 (clipe5bz_s20260930)

**reading_clipe5bzl0**: incomplete

**reading_clipe5bzl03**: incomplete

**reading_clipe5bzl01**: incomplete

**reading_clipe5bzsg**: negative: 3prime (clipe5bzsg_s20260929), 3prime (clipe5bzsg_s20260930), 4_untreated_video_not_lower_than_binary_by>0.010 (clipe5bzsg_s20260929), 4_untreated_video_not_lower_than_binary_by>0.010 (clipe5bzsg_s20260930), 5_cdfb_auc_b>=main (clipe5bzsg_s20260929), 5_cdfb_auc_b>=main (clipe5bzsg_s20260930), 6_df40_reenactment_not_lower_by>0.030 (clipe5bzsg_s20260929), 6_df40_reenactment_not_lower_by>0.030 (clipe5bzsg_s20260930)

**reading_clipe5fbzsg**: incomplete

**reading_clipe5bzsgl03**: incomplete

**reading_clipe5bzsgl01**: negative: 3prime (clipe5bzsgl01_s20260929), 3prime (clipe5bzsgl01_s20260930), 4_untreated_video_not_lower_than_binary_by>0.010 (clipe5bzsgl01_s20260929), 4_untreated_video_not_lower_than_binary_by>0.010 (clipe5bzsgl01_s20260930), 5_cdfb_auc_b>=main (clipe5bzsgl01_s20260930), 6_df40_reenactment_not_lower_by>0.030 (clipe5bzsgl01_s20260929), 6_df40_reenactment_not_lower_by>0.030 (clipe5bzsgl01_s20260930)

**reading_clipe5bzsgG**: negative: 1_facelocal_fa<=15 (clipe5bzsgG_s20260929), 3prime (clipe5bzsgG_s20260929), 3prime (clipe5bzsgG_s20260930), 4_untreated_video_not_lower_than_binary_by>0.010 (clipe5bzsgG_s20260929), 4_untreated_video_not_lower_than_binary_by>0.010 (clipe5bzsgG_s20260930), 5_cdfb_auc_b>=main (clipe5bzsgG_s20260929), 5_cdfb_auc_b>=main (clipe5bzsgG_s20260930), 6_df40_reenactment_not_lower_by>0.030 (clipe5bzsgG_s20260929), 6_df40_reenactment_not_lower_by>0.030 (clipe5bzsgG_s20260930)

**reading_clipe5bzsgh**: negative: 3prime (clipe5bzsgh_s20260929), 3prime (clipe5bzsgh_s20260930), 4_untreated_video_not_lower_than_binary_by>0.010 (clipe5bzsgh_s20260930), 5_cdfb_auc_b>=main (clipe5bzsgh_s20260930), 6_df40_reenactment_not_lower_by>0.030 (clipe5bzsgh_s20260929), 6_df40_reenactment_not_lower_by>0.030 (clipe5bzsgh_s20260930)

**reading_clipe5bzsgl003**: negative: 3prime (clipe5bzsgl003_s20260929), 3prime (clipe5bzsgl003_s20260930), 4_untreated_video_not_lower_than_binary_by>0.010 (clipe5bzsgl003_s20260930), 5_cdfb_auc_b>=main (clipe5bzsgl003_s20260930), 6_df40_reenactment_not_lower_by>0.030 (clipe5bzsgl003_s20260929), 6_df40_reenactment_not_lower_by>0.030 (clipe5bzsgl003_s20260930)

**reading_clipe5bzxs**: incomplete (missing inputs: 4_untreated_video_not_lower_than_binary_by>0.010, 5_cdfb_auc_b>=main)

**reading_clipe5fbp0F2**: incomplete

**reading_clipe5bzEsg**: incomplete

