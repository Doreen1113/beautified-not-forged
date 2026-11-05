# Addendum 55: operation head under Instagram AR filters (FairBeauty pairs, n measured 2919)

Measured presence % (rule: half of Alibaba level-30 median effect; strict = full level-30 median):

| group | n | eye | jaw | white | smooth | strict eye/jaw/white/smooth |
|---|---|---|---|---|---|---|
| all | 2919 | 80.5 | 8.5 | 39.1 | 96.6 | 76.7 / 6.8 / 35.3 / 93.5 |
| held_out_filters | 881 | 80.0 | 9.8 | 20.3 | 98.0 | 76.2 / 7.6 / 16.6 / 94.8 |
| training_filters | 2038 | 80.8 | 8.0 | 47.2 | 96.0 | 77.0 / 6.5 / 43.4 / 92.9 |
| Baby_cute_face | 294 | 75.9 | 8.8 | 54.4 | 99.3 | 70.7 / 6.8 / 43.5 / 98.3 |
| Caramel Macchiato | 295 | 90.2 | 10.8 | 57.6 | 100.0 | 87.1 / 8.5 / 55.9 / 99.0 |
| Cute baby face | 298 | 73.5 | 7.4 | 88.6 | 99.0 | 68.8 / 6.4 / 85.2 / 98.7 |
| Just Baby | 293 | 82.3 | 9.2 | 3.1 | 98.0 | 79.2 / 6.5 / 2.7 / 97.6 |
| Pretty | 566 | 81.4 | 7.4 | 29.7 | 97.0 | 76.5 / 6.4 / 25.1 / 93.8 |
| Shiny foxy | 295 | 86.1 | 6.1 | 57.3 | 96.9 | 83.4 / 4.4 / 53.6 / 95.6 |
| big city life | 294 | 82.0 | 11.2 | 3.4 | 96.6 | 78.6 / 9.5 / 3.4 / 88.4 |
| hary beauty | 584 | 76.4 | 8.4 | 32.5 | 91.1 | 73.3 / 6.7 / 28.4 / 84.6 |

## clipe5_s20260929

| group | op | head on render % | head on orig % | recall | precision |
|---|---|---|---|---|---|
| all | eye | 0.4 | 3.2 | 0.003 | 0.667 |
| all | jaw | 2.1 | 6.8 | 0.032 | 0.131 |
| all | white | 12.7 | 18.2 | 0.176 | 0.543 |
| all | smooth | 24.8 | 6.9 | 0.243 | 0.946 |
| held_out_filters | eye | 0.6 | 3.1 | 0.004 | 0.6 |
| held_out_filters | jaw | 2.7 | 7.0 | 0.047 | 0.167 |
| held_out_filters | white | 13.3 | 16.0 | 0.156 | 0.239 |
| held_out_filters | smooth | 21.3 | 6.8 | 0.212 | 0.973 |
| training_filters | eye | 0.3 | 3.2 | 0.003 | 0.714 |
| training_filters | jaw | 1.8 | 6.7 | 0.025 | 0.108 |
| training_filters | white | 12.4 | 19.1 | 0.18 | 0.684 |
| training_filters | smooth | 26.3 | 6.9 | 0.257 | 0.937 |

exact four-bit match (all): 1.9 %; quantity Spearman: {'eye': 0.014, 'jaw': 0.024, 'white': 0.038, 'smooth': -0.164}

## clipe5M_s20260929

| group | op | head on render % | head on orig % | recall | precision |
|---|---|---|---|---|---|
| all | eye | 3.7 | 5.9 | 0.036 | 0.778 |
| all | jaw | 10.0 | 21.9 | 0.116 | 0.099 |
| all | white | 19.7 | 19.2 | 0.265 | 0.525 |
| all | smooth | 52.7 | 14.2 | 0.529 | 0.969 |
| held_out_filters | eye | 6.0 | 6.6 | 0.061 | 0.811 |
| held_out_filters | jaw | 16.7 | 23.5 | 0.116 | 0.068 |
| held_out_filters | white | 25.3 | 17.9 | 0.285 | 0.229 |
| held_out_filters | smooth | 62.2 | 14.6 | 0.628 | 0.989 |
| training_filters | eye | 2.7 | 5.6 | 0.025 | 0.745 |
| training_filters | jaw | 7.2 | 21.2 | 0.117 | 0.13 |
| training_filters | white | 17.3 | 19.7 | 0.261 | 0.713 |
| training_filters | smooth | 48.6 | 14.0 | 0.485 | 0.959 |

exact four-bit match (all): 2.5 %; quantity Spearman: {'eye': 0.056, 'jaw': -0.004, 'white': -0.002, 'smooth': -0.061}

## clipe5M_s20260930

| group | op | head on render % | head on orig % | recall | precision |
|---|---|---|---|---|---|
| all | eye | 1.2 | 7.5 | 0.011 | 0.765 |
| all | jaw | 15.8 | 27.2 | 0.177 | 0.096 |
| all | white | 46.7 | 23.5 | 0.534 | 0.447 |
| all | smooth | 56.5 | 15.0 | 0.563 | 0.963 |
| held_out_filters | eye | 1.5 | 7.5 | 0.014 | 0.769 |
| held_out_filters | jaw | 21.7 | 26.3 | 0.198 | 0.089 |
| held_out_filters | white | 46.9 | 23.2 | 0.603 | 0.262 |
| held_out_filters | smooth | 62.0 | 15.2 | 0.623 | 0.985 |
| training_filters | eye | 1.0 | 7.6 | 0.01 | 0.762 |
| training_filters | jaw | 13.2 | 27.6 | 0.166 | 0.1 |
| training_filters | white | 46.6 | 23.7 | 0.521 | 0.528 |
| training_filters | smooth | 54.1 | 15.0 | 0.536 | 0.952 |

exact four-bit match (all): 2.9 %; quantity Spearman: {'eye': -0.003, 'jaw': -0.019, 'white': -0.138, 'smooth': -0.158}

## clipe7_s20260929

| group | op | head on render % | head on orig % | recall | precision |
|---|---|---|---|---|---|
| all | eye | 52.1 | 0.0 | 0.512 | 0.792 |
| all | jaw | 40.5 | 0.5 | 0.365 | 0.077 |
| all | white | 91.1 | 0.1 | 0.921 | 0.395 |
| all | smooth | 99.9 | 0.1 | 0.999 | 0.966 |
| held_out_filters | eye | 44.7 | 0.0 | 0.444 | 0.794 |
| held_out_filters | jaw | 35.1 | 0.7 | 0.314 | 0.087 |
| held_out_filters | white | 88.1 | 0.0 | 0.922 | 0.213 |
| held_out_filters | smooth | 99.9 | 0.2 | 0.999 | 0.98 |
| training_filters | eye | 55.3 | 0.0 | 0.541 | 0.791 |
| training_filters | jaw | 42.8 | 0.4 | 0.393 | 0.073 |
| training_filters | white | 92.3 | 0.1 | 0.921 | 0.47 |
| training_filters | smooth | 100.0 | 0.0 | 0.999 | 0.96 |

exact four-bit match (all): 7.7 %; quantity Spearman: {'eye': 0.091, 'jaw': 0.045, 'white': -0.028, 'smooth': -0.043}
