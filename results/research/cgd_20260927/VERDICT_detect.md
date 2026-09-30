# CGD detection bars D1-D5 (PRE_DECLARED §5); D5 needs Celeb-DF-B (score_cdfb.py --models CGD ...)

| arm | CDFv2 | DFD | in-domain r/f/fl | FA / MISS | B1 dominated by | heldout-13 excess | D1 | D2 | D3 | D4 |
|---|---|---|---|---|---|---|---|---|---|---|
| HYBPE | 0.81 [0.7811, 0.8368] | 0.8876 [0.8482, 0.9252] | 80.7/90.21/76.82 | 8.89 / 1.62 | none (of 13) | 39.21 | True | True | False | True |
| MASK | 0.8193 [0.7916, 0.8444] | 0.9075 [0.8735, 0.94] | 79.03/89.95/83.97 | 6.99 / 2.06 | none (of 13) | 40.73 | True | True | False | True |
| MASKD | 0.8171 [0.7881, 0.8435] | 0.8963 [0.8565, 0.9325] | 82.75/81.32/79.71 | 5.47 / 4.78 | none (of 13) | 35.94 | True | True | False | True |
| CGD | 0.7944 [0.7657, 0.8211] | 0.9055 [0.8713, 0.9372] | 83.13/89.12/87.16 | 3.19 / 2.62 | none (of 13) | 43.69 | False | True | True | True |
| CGDD | 0.7809 [0.7509, 0.8092] | 0.8772 [0.833, 0.9164] | 84.65/80.81/79.64 | 6.16 / 5.12 | none (of 13) | 38.45 | False | False | False | True |
