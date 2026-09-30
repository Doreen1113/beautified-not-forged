# sbifix verdict, FF++-side bars (PRE_DECLARED §4); F5/F6 need Celeb-DF-B and are judged separately

**R0'** SBI-F CDFv2 0.735 [0.7019, 0.7677] (official 0.817, SBI-L 0.620) >= 0.78: **False**; DFD 0.8856; at 5 % FPR FA 19.3 / MISS 20.22

| arm | CDFv2 | DFD | in-domain r/f/fl | FA / MISS | B1 dominated by | heldout-13 excess | F1 CDF>=0.79 | F2 DFD>=0.90 | F3 B1 | F4 >=80 |
|---|---|---|---|---|---|---|---|---|---|---|
| SUP-F | 0.7837 [0.7523, 0.8115] | 0.9125 [0.8771, 0.9434] | 80.7/95.02/88.37 | 4.86 / 0.47 | none (of 13) | 43.01 | False | True | True | True |
| HYB-F | 0.7795 [0.7455, 0.8084] | 0.8999 [0.8615, 0.9337] | 82.6/93.85/84.73 | 6.08 / 0.47 | none (of 13) | 39.36 | False | False | True | True |
| HYBD-F | 0.8074 [0.7776, 0.8358] | 0.8819 [0.8373, 0.922] | 81.61/91.84/83.74 | 5.24 / 0.84 | none (of 13) | 35.71 | True | False | True | True |
