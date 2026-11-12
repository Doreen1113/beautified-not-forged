# Addendum 53: frozen ArcFace + LR (FF++ train, n 5996, C 21.5) on Celeb-DF probes, reference-free. Cell = AUC / recalibrated miss % (5% FPR on that condition's genuine)

| score | untreated | bil15 | bil21 | fl06 | fl12 |
|---|---|---|---|---|---|
| arcface_lr | 0.5928 / 93.1 | 0.53 / 95.1 | 0.5258 / 95.0 | 0.5761 / 93.6 | 0.5267 / 94.8 |
| clipe5b | 0.9244 / 33.8 | 0.8229 / 58.6 | 0.7776 / 62.9 | 0.8869 / 45.1 | 0.7507 / 73.7 |
| lambda0 | 0.9151 / 35.7 | 0.8563 / 50.5 | 0.8247 / 59.0 | 0.8742 / 49.5 | 0.7578 / 76.7 |
| fusion lambda0+arcface_lr | 0.8259 / 58.4 | 0.7568 / 68.7 | 0.7353 / 71.1 | 0.7936 / 67.9 | 0.6928 / 87.9 |
| effort | 0.8966 / 33.4 | 0.8124 / 58.8 | 0.7795 / 70.1 | 0.7626 / 74.1 | 0.663 / 77.6 |
