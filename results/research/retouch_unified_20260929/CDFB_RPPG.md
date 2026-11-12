# Addendum 64: rPPG (POS, SNR) under real app presets, Celeb-DF-B, one score per video, zero training

videos {'real': 232, 'real_beautified': 232, 'real_compressed': 232, 'synthesis': 232, 'synthesis_beautified': 232, 'synthesis_compressed': 232}; dropped (landmarker < 90 % of frames) {'real': 19, 'real_beautified': 111, 'real_compressed': 113, 'synthesis': 20, 'synthesis_beautified': 116, 'synthesis_compressed': 112}

median SNR dB {'real': -4.06, 'real_beautified': -3.8, 'real_compressed': -4.11, 'synthesis': -3.97, 'synthesis_beautified': -3.96, 'synthesis_compressed': -4.06}

AUC untreated 0.514 | beautified 0.541 | compressed 0.512 | beauty-only dAUC +0.029

At the untreated 5 % FPR threshold: FA real/beaut/compr 5.2 / 0.8 / 3.4 (dFA beauty-only -2.5 [-6.4, +0.8]); miss syn/beaut/compr 97.2 / 93.1 / 94.2 (dMISS beauty-only -1.1 [-7.3, +5.3])

Spearman(-SNR, Effort) on untreated forgeries -0.018

Predictions: {"1_auc_untreated_ge_0.70": false, "1_kill_lt_0.60": true, "2_d_auc_beauty_only_ge_-0.05": true, "2_kill_lt_-0.10": false, "3_miss_rise_le5_fa_rise_le5": true, "4_spearman_vs_effort_lt_0.3": true}

Diagnostics (after the readout, not part of the rule):
- The pipeline does recover a pulse on untreated genuine video: 76.5 % of spectral peaks fall in 0.9-1.7 Hz (54-102 bpm);
  a uniform peak over 0.7-3 Hz would put 34.8 % there (histogram over 0.25-Hz bins from 0.7 Hz: 47, 63, 62, 13, 16, 5, 4, 3, 0).
- Swaps inherit the driving video's pulse: for 212 synthesis videos matched to their source genuine video (idA_idB_n -> idA_n),
  the peak frequencies agree within 0.1 Hz in 43.9 % of pairs, against 18.7 % (97.5th percentile 23.6 %) for shuffled partners.
  The ROI (outer cheeks, forehead) lies largely outside the swap mask, and the blending keeps the colour time course, so the
  pulse SNR carries no forgery information on this data; the rPPG detectors in the literature learn spatial inconsistency of the
  pulse, not its presence, and all of them train.
- Dropped videos: the re-encoded folders (beautified, compressed) lose about half of the videos at the 90 % landmark bar
  (median 272-274 landmarked frames of 300 against 299 for the untreated files; same frame counts, fps 30.1-30.4); the drop is
  the re-encoding, not the beautification (compressed drops as many). Prediction (1) rests on the untreated pair (212 + 212
  videos, 19 + 20 dropped) and is unaffected.
