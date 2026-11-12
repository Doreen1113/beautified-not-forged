# Smoothing: service vs scripted vs blur (medians over identities; hf = high-frequency energy ratio to the original, 1 = unchanged)

| edit | n | hf_face@512 | hf_bg@512 | hf_edges@512 | hf_flat@512 | dL | mad_face@512 | mad_bg@512 | hf_face@224 | hf_bg@224 | hf_edges@224 | hf_flat@224 | mad_face@224 | mad_bg@224 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| service Smoothing_30 | 120 | 0.89 | 0.979 | 0.967 | 0.802 | -0.047 | 2.7 | 1.5 | 0.909 | 0.982 | 0.989 | 0.807 | 2.277 | 1.046 |
| service Smoothing_60 | 120 | 0.812 | 0.968 | 0.957 | 0.668 | 0.496 | 3.564 | 1.634 | 0.842 | 0.971 | 0.993 | 0.693 | 2.973 | 1.164 |
| service Smoothing_90 | 120 | 0.759 | 0.957 | 0.941 | 0.601 | 0.677 | 4.148 | 1.759 | 0.798 | 0.961 | 0.981 | 0.64 | 3.468 | 1.263 |
| scripted op_smooth frac .055 mix .11 (median of training range) | 120 | 0.924 | 0.999 | 0.968 | 0.888 | -0.45 | 0.592 | 0.013 | 0.942 | 0.999 | 0.983 | 0.904 | 0.556 | 0.015 |
| scripted op_smooth frac .055 mix .40 (top of training range) | 120 | 0.751 | 0.999 | 0.88 | 0.676 | -0.386 | 1.615 | 0.015 | 0.811 | 0.999 | 0.937 | 0.718 | 1.316 | 0.017 |
| scripted op_smooth frac .08 mix 1.0 (outside training range) | 120 | 0.345 | 0.999 | 0.523 | 0.251 | -0.087 | 5.63 | 0.017 | 0.459 | 0.999 | 0.66 | 0.341 | 4.798 | 0.02 |
| scripted global bilateral (9,50,50) [beautify] | 120 | 0.553 | 0.58 | 0.934 | 0.329 | 0.023 | 2.534 | 2.658 | 0.761 | 0.75 | 0.983 | 0.589 | 1.466 | 1.529 |
| scripted global bilateral (21,100,100) [beautify] | 120 | 0.385 | 0.387 | 0.663 | 0.243 | 0.082 | 4.869 | 5.095 | 0.507 | 0.488 | 0.8 | 0.345 | 4.035 | 3.927 |
| global Gaussian sigma 1.0 [sym_degrade, all arms incl. P0] | 120 | 0.527 | 0.514 | 0.521 | 0.523 | 0.002 | 2.118 | 2.582 | 0.812 | 0.786 | 0.779 | 0.816 | 0.95 | 1.071 |
| global Gaussian sigma 2.0 [sym_degrade, all arms incl. P0] | 120 | 0.305 | 0.269 | 0.249 | 0.337 | -0.017 | 3.762 | 4.249 | 0.568 | 0.528 | 0.485 | 0.607 | 2.391 | 2.62 |
| face-only Gaussian sigma 1.5 (not in any arm) | 120 | 0.411 | 0.997 | 0.376 | 0.434 | -0.115 | 2.826 | 0.016 | 0.696 | 0.999 | 0.644 | 0.711 | 1.605 | 0.018 |
| JPEG q60 (not smoothing; reference) | 120 | 0.909 | 0.935 | 0.94 | 0.851 | -0.034 | 2.796 | 2.927 | 1.003 | 0.998 | 0.995 | 1.007 | 1.614 | 1.558 |
