# Addendum 59: single-image detectability ceiling (dedicated EfficientNet-B0 per operation, Alibaba, identity-disjoint)

| operation | AUROC lossless [CI] | paired rank % | AUROC after JPEG q90 + resize 256 [CI] | paired rank % |
|---|---|---|---|---|
| EyeEnlarging_90 | 0.9332 [0.9217, 0.9429] | 100.0 | 0.8331 [0.817, 0.8511] | 99.4 |
| FaceLifting_90 | 0.9482 [0.9385, 0.957] | 100.0 | 0.8797 [0.8653, 0.8936] | 98.9 |
| Whitening_90 | 0.9801 [0.9734, 0.9856] | 100.0 | 0.9487 [0.9387, 0.9581] | 99.8 |
| Smoothing_90 | 0.9995 [0.9989, 1.0] | 100.0 | 0.9966 [0.9927, 0.9994] | 100.0 |

Cross-operation AUROC (rows: classifier trained on; columns: held-out renders of; diagonal = own operation):

| trained on / tested on | EyeEnlarging_90 | FaceLifting_90 | Whitening_90 | Smoothing_90 |
|---|---|---|---|---|
| EyeEnlarging_90 | 0.9332 | 0.7459 | 0.6938 | 0.6368 |
| FaceLifting_90 | 0.7175 | 0.9482 | 0.6758 | 0.7972 |
| Whitening_90 | 0.537 | 0.5626 | 0.9801 | 0.631 |
| Smoothing_90 | 0.4925 | 0.5245 | 0.4981 | 0.9995 |
