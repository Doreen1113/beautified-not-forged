# Beautification shift in CLIP feature space (Addendum 17; FF++ train for the subspace, FF++ val + held-out pilgram filters for evaluation)

## clipe5f_s20260929

Energy of training-available shifts in the first k directions: k=2: 0.7893, k=4: 0.8712, k=8: 0.8948, k=16: 0.9166, k=32: 0.9367, k=64: 0.9545, k=128: 0.9705

| held-out filter | n | cos(w, mean shift) | d logit genuine | d logit forged | shift energy in train V16 | shift / feature norm |
|---|---|---|---|---|---|---|
| brooklyn | 95 | 0.003 | +0.141 | -0.042 | 0.881 | 0.807 |
| clarendon | 99 | 0.068 | +1.896 | +0.399 | 0.859 | 0.823 |
| earlybird | 88 | 0.204 | +7.843 | +1.097 | 0.863 | 1.078 |
| inkwell | 95 | 0.085 | +0.860 | -0.254 | 0.627 | 0.318 |
| kelvin | 92 | 0.04 | +2.399 | -0.706 | 0.896 | 0.964 |
| lofi | 95 | 0.062 | +1.858 | +0.174 | 0.873 | 0.842 |
| mayfair | 94 | 0.328 | +5.636 | +1.797 | 0.831 | 0.664 |
| moon | 89 | 0.063 | +1.754 | -0.101 | 0.753 | 0.646 |
| perpetua | 107 | 0.093 | +0.994 | +0.215 | 0.769 | 0.372 |
| reyes | 104 | 0.016 | +0.758 | -0.266 | 0.887 | 0.904 |
| slumber | 101 | 0.001 | +0.428 | -0.276 | 0.87 | 0.795 |

| head | AUC clean | AUC filtered | FA clean | FA filtered | MISS clean | MISS filtered |
|---|---|---|---|---|---|---|
| original head | 0.987 | 0.953 | 5.1 | 21.5 | 5.9 | 5.9 |
| refit, erase k=0 | 0.985 | 0.916 | 5.1 | 15.8 | 6.4 | 16.6 |
| refit, erase k=2 | 0.933 | 0.907 | 5.1 | 18.5 | 26.5 | 15.1 |
| refit, erase k=4 | 0.937 | 0.877 | 5.1 | 18.1 | 24.6 | 20.0 |
| refit, erase k=8 | 0.932 | 0.844 | 5.1 | 18.3 | 22.7 | 27.6 |
| refit, erase k=16 | 0.927 | 0.836 | 5.1 | 17.5 | 23.4 | 28.4 |
| refit, erase k=32 | 0.919 | 0.804 | 5.1 | 19.2 | 28.0 | 32.1 |
| refit, erase k=64 | 0.928 | 0.798 | 5.1 | 27.5 | 24.6 | 28.7 |
| refit, erase k=128 | 0.907 | 0.792 | 5.1 | 23.0 | 26.8 | 30.2 |

## clipe5fg0_s20260929

Energy of training-available shifts in the first k directions: k=2: 0.6998, k=4: 0.7884, k=8: 0.8484, k=16: 0.888, k=32: 0.9173, k=64: 0.941, k=128: 0.9626

| held-out filter | n | cos(w, mean shift) | d logit genuine | d logit forged | shift energy in train V16 | shift / feature norm |
|---|---|---|---|---|---|---|
| brooklyn | 95 | 0.042 | +1.202 | -0.374 | 0.83 | 0.567 |
| clarendon | 99 | 0.079 | +1.247 | -0.507 | 0.714 | 0.317 |
| earlybird | 88 | 0.192 | +8.529 | +0.464 | 0.806 | 1.129 |
| inkwell | 95 | 0.051 | +0.999 | -0.554 | 0.739 | 0.426 |
| kelvin | 92 | 0.127 | +4.169 | -1.130 | 0.817 | 0.655 |
| lofi | 95 | -0.008 | +0.681 | -0.904 | 0.776 | 0.43 |
| mayfair | 94 | 0.342 | +6.041 | +0.794 | 0.808 | 0.615 |
| moon | 89 | 0.04 | +2.627 | -0.861 | 0.812 | 0.893 |
| perpetua | 107 | 0.129 | +0.717 | -0.181 | 0.609 | 0.179 |
| reyes | 104 | 0.025 | +0.994 | -0.399 | 0.86 | 0.749 |
| slumber | 101 | -0.017 | +0.493 | -0.579 | 0.785 | 0.425 |

| head | AUC clean | AUC filtered | FA clean | FA filtered | MISS clean | MISS filtered |
|---|---|---|---|---|---|---|
| original head | 0.985 | 0.955 | 5.1 | 21.1 | 6.8 | 5.1 |
| refit, erase k=0 | 0.979 | 0.910 | 5.1 | 16.6 | 8.9 | 13.8 |
| refit, erase k=2 | 0.874 | 0.889 | 5.1 | 17.2 | 35.5 | 16.3 |
| refit, erase k=4 | 0.879 | 0.873 | 5.1 | 20.8 | 31.6 | 17.8 |
| refit, erase k=8 | 0.886 | 0.872 | 5.1 | 23.0 | 33.1 | 16.3 |
| refit, erase k=16 | 0.885 | 0.871 | 5.1 | 24.0 | 31.6 | 15.9 |
| refit, erase k=32 | 0.867 | 0.850 | 5.1 | 21.5 | 34.8 | 20.2 |
| refit, erase k=64 | 0.849 | 0.834 | 5.1 | 22.1 | 36.5 | 21.6 |
| refit, erase k=128 | 0.844 | 0.826 | 5.1 | 22.5 | 34.8 | 20.4 |
