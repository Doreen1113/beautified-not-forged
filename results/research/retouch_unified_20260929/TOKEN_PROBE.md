# Common token shift and self-referenced probes (Addendum 23; fitted on FF++ train, tested on FF++ val + held-out filters)

## clipe5f_s20260929

Common-shift fraction rho per held-out filter: all 0.474, brooklyn 0.533, clarendon 0.499, earlybird 0.425, inkwell 0.372, kelvin 0.515, lofi 0.519, mayfair 0.483, moon 0.429, perpetua 0.414, reyes 0.525, slumber 0.496

| probe | AUC clean | AUC filtered | FA filtered | MISS clean | MISS filtered |
|---|---|---|---|---|---|
| cls | fit clean | 0.985 | 0.878 | 1.7 | 6.4 | 67.3 |
| cls | fit clean+graded | 0.987 | 0.963 | 16.8 | 4.9 | 6.8 |
| mean | fit clean | 0.986 | 0.931 | 25.1 | 6.4 | 7.9 |
| mean | fit clean+graded | 0.987 | 0.947 | 25.1 | 4.9 | 5.5 |
| io | fit clean | 0.983 | 0.921 | 19.6 | 7.2 | 11.5 |
| io | fit clean+graded | 0.983 | 0.940 | 24.0 | 5.3 | 6.8 |
| std | fit clean | 0.985 | 0.906 | 11.1 | 7.2 | 20.4 |
| std | fit clean+graded | 0.984 | 0.928 | 19.8 | 6.8 | 9.5 |
| io+std | fit clean | 0.984 | 0.920 | 14.3 | 6.4 | 16.3 |
| io+std | fit clean+graded | 0.984 | 0.936 | 19.6 | 6.2 | 7.8 |
| cls+io+std | fit clean | 0.986 | 0.932 | 4.9 | 5.9 | 34.6 |
| cls+io+std | fit clean+graded | 0.986 | 0.956 | 17.7 | 5.5 | 7.2 |

## clipe5b_s20260929

Common-shift fraction rho per held-out filter: all 0.034, brooklyn 0.03, clarendon 0.021, earlybird 0.047, inkwell 0.036, kelvin 0.043, lofi 0.019, mayfair 0.047, moon 0.037, perpetua 0.044, reyes 0.026, slumber 0.022

| probe | AUC clean | AUC filtered | FA filtered | MISS clean | MISS filtered |
|---|---|---|---|---|---|
| cls | fit clean | 0.981 | 0.961 | 10.6 | 9.1 | 8.7 |
| cls | fit clean+graded | 0.980 | 0.963 | 9.1 | 6.6 | 9.6 |
| mean | fit clean | 0.981 | 0.963 | 16.6 | 4.9 | 5.7 |
| mean | fit clean+graded | 0.980 | 0.963 | 14.2 | 5.9 | 6.4 |
| io | fit clean | 0.982 | 0.954 | 14.3 | 6.8 | 8.3 |
| io | fit clean+graded | 0.983 | 0.954 | 13.8 | 7.6 | 8.7 |
| std | fit clean | 0.980 | 0.955 | 10.2 | 8.7 | 10.4 |
| std | fit clean+graded | 0.978 | 0.954 | 10.8 | 8.7 | 10.0 |
| io+std | fit clean | 0.983 | 0.957 | 13.4 | 6.6 | 7.8 |
| io+std | fit clean+graded | 0.982 | 0.958 | 13.6 | 6.6 | 7.8 |
| cls+io+std | fit clean | 0.983 | 0.963 | 12.1 | 7.4 | 7.0 |
| cls+io+std | fit clean+graded | 0.981 | 0.962 | 9.8 | 6.2 | 7.9 |
