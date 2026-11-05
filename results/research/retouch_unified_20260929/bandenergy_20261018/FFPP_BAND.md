# FF++ training forgeries vs their genuine source frames: low skin-relief band, high band, Laplacian (inside the face)

Median paired log-ratio (forged / genuine of the same video) [95% CI over videos]; share of videos where the forged frame is lower.
Negative low-band ratio = less skin relief, as under smoothing. Rows real_bil15 / real_fl06: genuine frames after our smoothing forms (reference).

| comparison | low band 0.02-0.12 | % lower | high band > 0.25 | % lower | |Laplacian| | % lower | n |
|---|---|---|---|---|---|---|---|
| Deepfakes | -0.0336 [-0.0697, 0.0067] | 55.5 | -1.0927 [-1.25, -0.9298] | 89.5 | -0.2601 [-0.2825, -0.2363] | 88.0 | 200 |
| Face2Face | -0.0071 [-0.0213, 0.0104] | 52.5 | 0.0006 [-0.0566, 0.1351] | 50.0 | -0.0658 [-0.0967, -0.0335] | 64.0 | 200 |
| FaceSwap | 0.0338 [-0.0196, 0.0695] | 47.5 | 0.8034 [0.5724, 0.9188] | 20.0 | 0.0554 [0.0252, 0.0969] | 39.0 | 200 |
| NeuralTextures | -0.0325 [-0.0475, -0.0154] | 61.0 | -0.6501 [-0.7191, -0.5947] | 94.5 | -0.1715 [-0.1973, -0.1533] | 97.5 | 200 |
| real_bil15 | -0.1832 [-0.1971, -0.1684] | 99.0 | -0.3609 [-0.4281, -0.2746] | 82.5 | -0.384 [-0.4064, -0.3621] | 100.0 | 200 |
| real_fl06 | -0.0571 [-0.0844, -0.0462] | 96.5 | -0.0715 [-0.1147, -0.0475] | 67.0 | -0.2235 [-0.258, -0.1901] | 100.0 | 200 |
