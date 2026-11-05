# Paper v5 (2026-10-16): changes after REVIEW_V4_20261016.md

Files: `main_v5.tex` / `main_v5.pdf`, `supplement_v5.tex` / `supplement_v5.pdf`, `refs_v5.bib`, `make_tables_v5.py` (writes
`tables/tab_v5_*.tex` and `v5_numbers.json`), `make_fig_teaser_v5.py` (writes `figs/fig_teaser_v5.*`). v4 files are unchanged.
Build: tectonic on gsplat-ubuntu (`~/paper_build/paper_v2`), order main, supplement, main, supplement (`-k`, cross-references by
`xr-hyper`). No model was run. Every new number comes from existing score files through `make_tables_v5.py`.

Format: IEEEtran conference, anonymous ("Anonymous submission"). The CVPR 2027 author kit is not published (checked 2026-10-16:
`github.com/cvpr-org/author-kit` newest release is CVPR2026-v1; `cvpr.thecvf.com/Conferences/2027/AuthorGuidelines` returns 404), so
no CVPR version was made. Body: pages 1 to 8 (left column of page 8), references from the right column of page 8 to page 9.
Abstract: 250 words. Supplement: 21 pages.

## Review items fixed in the text

| Item | What changed |
|---|---|
| A1 | Classes defined by what changes (identity, expression, motion, speech, a facial feature replaced by new content); "generated content" clause removed; "the label follows what changed, not the tool"; own-part inpainting named as the unsettled case; stated that no identity/expression measurement exists. |
| A2 | Table I in the main text (6 rows, referenced by number); Table S1 extended to 17 rows with label, "what changes", scored or not; "not tested" for DF40 synthesis and editing replaced by "not scored (DF40 sets exist)". |
| A3 | Median paired logit shift with bootstrap CI and sign test for every detector and arm (Table IV, Table S13); text states that the full-data three-way models move scores toward genuine and that the 25-75% band admits a real shift. |
| A4 | New title; abstract leads with the two-sided measurement and smoothing; contributions recast as measurement + training lessons + reference models; three-way output reported as an attribute with error rates; Celeb-DF-B beautified-class rates added (S12). |
| A5 | One sentence: every detection number reads P(fake) only; pointer to S12. |
| B1 | Probe section renamed and narrowed to colour filters and one model of ours; "the damage has a measurable mechanism" removed from abstract and conclusion; Effort's opposite direction stated. |
| B2 | Reenactment paragraph descriptive, includes P1-smooth and seed ranges; cross-detector Spearman with p-values and Holm; correlation over our arms; mechanism sentence dropped. |
| B3 | Variant's +28.1/+33.8/+34.1 miss rise (43.5% to 77.6%) in abstract, Sec. V-D and conclusion, with the AUC-with-both-smoothed reading; Table V gains the "frame AUC, both smoothed" column for every arm. |
| B4 | "Necessary and sufficient" removed; P2-smooth flagged as carrying the form cue; sufficiency rests on P2-sym; necessity phrased "no other view substitutes, within the views we trained". |
| B5 | LSDA sentence rewritten as cross-method latent augmentation; the missing forged-only cell stated in text and limitations. |
| B6 | "Two tuning schemes" removed; "P1 was not trained under that scheme". |
| B7 | Abstract no longer quotes "21 points more"; text gives the P1-P0 differences (4.5-9.5). |
| B8 | Re-framing to portrait, 57% face loss and the post hoc bar trimming described in Sec. III and S1; FA under re-encoding and dFA_beauty added (main Table III, S5); additivity assumption and face-size confound stated. |
| B9 | CADDM: "its misses do not rise because the presets raise its scores for genuine frames too (13.8% false alarms)"; fusion motivation restricted to commercial smoothing (60.9% of pairs). |
| B10 | Sec. V-F renamed "Localisation and restoration"; "sufficient and necessary for the model's own decision" removed; text says any accurate segmenter would score similarly and lists what the test does not cover. |
| B11 | Service described as an analysis set (more than 60 checkpoints of ours and 17 published detectors scored; Smoothing-90 singled out post hoc; bars defined on it); limitation asks for a fresh source. |
| B12 | Dagger on every model trained on sister-service renders (Tables III, IV); training and test originals share no image (disjoint FFHQ index range; FFHQ has no identity labels); calibration script on 120 test originals disclosed (S1). |
| B13 | One sentence: the three null operations share service, encoder and resolution, so the accusation is not a pipeline artefact. |
| B15 | Flip minus ceiling unchanged (variant 0.0/+0.1/-0.1 vs main -0.1/-0.1/-0.1); "a ceiling-relative bar would have passed"; both models side by side. |
| C1 | DF40 face swap: on par with Forensics Adapter (both domains) and Effort (FF++ domain), 0.030 [0.018, 0.043] behind Effort (Celeb-DF domain), 0.015-0.042 behind GenD and DFD-HR. Abstract, contributions and conclusion no longer claim "on par on DF40". |
| C2 | "train" column in Table III; notation table footnote on training data; P0 given as the equal-data comparison next to the claim. |
| C3 | Every AUC labelled frame or video; Celeb-DF-B video AUC added (S5); CADDM compared with Libourel et al. at video level. |
| C4 | AUC_c and AUC_c - AUC_b in Table III; abstract quotes the beauty-only loss (0.07-0.09 for the CLIP detectors). |
| C5 | Paired AUC_b differences against Effort, Forensics Adapter, GenD, DFD-HR for both seeds and arms (Table S6); all intervals above zero. |
| C6 | Sec. III states the threshold is fitted per source, which no deployed detector can do; limitation added. |
| C8 | Table S2: weights, training data, input per detector; "fifteen face-forgery detectors and two general ones". |
| C9 | Effort reproduction gap stated next to the comparison; "keeps the best test-set AUC" now cites file and lines (Effort `DeepfakeBench/training/trainer/trainer.py` 377-390; Forensics Adapter `trainer/trainer.py` `save_best`, line 347). |
| C10 | Sec. III: bootstraps resample videos, not identities, so Celeb-DF/DFD intervals are optimistic. |
| D1 | P1-smooth: 96-100% bilateral, 75.1-83.6% median, 50.6-54.4% Gaussian blend (from tab_v4_evasion: untreated miss + rise per seed). The review's "78-84%" is 75-84% when seed 3 (37.1 + 38.0 = 75.1) is included. |
| D2 | "neither accuses nor is fooled" removed; "does not pass smoothed forgeries wholesale, but its misses rise by 8-21 points"; AUC both smoothed at or above P0. |
| D3 | Binary control better on every untreated source by 0.01-0.15 AUC including DF40 reenactment (-0.124, -0.145). Binary DFD frame AUC corrected from 0.967 to 0.961 (the value in Table III and in the current score files). |
| D4 | Erasure compared with the k=0 refit (15.8% to 18.3-19.2%; clean AUC 0.985 to 0.919-0.933); per-filter 17.5-27.5% only in S7. |
| D5 | Supplement DFD video AUC 0.978 (second seed 0.981), matching Table V. |
| D6 | 232 videos per condition; 231 with a face (230 for beautified genuine). |
| D7 | Draw counts per source, resampling unit, threshold re-estimated in every draw. |
| D8 | Holm over the nine exposure contrasts (S6) and over the four cross-detector correlations; general statement on uncorrected intervals. |
| D9 | "(pending)" removed; "we did not measure inference cost; 306M parameters, not meant for edge devices". |
| D10 | "adversarial and random training (seven variants)"; table caption marks random edits as a control; overview figure with "photograph" not used; "none ... trains against the edit with a class-controlled design". |
| F1 | Positioned as shortcut learning / class-dependent augmentation with measured error sign; alpha-blending ensemble discussed as prior art for fusion (main V-E, S10); joint detection-segmentation prior work cited. |
| F2 | All 17 detectors cited in the intro sentence and in every table row (tab_v5_* copies of the v4 tables with citations). |
| F3 | Added and verified: FakeVLM, Geirhos 2020, Balestriero 2022, Rathgeb 2019, Jain 2018, Hendrycks 2019, DeeperForensics-1.0, Nguyen 2019, HiFi-Net (see below). |
| F4 | DFD-HR full author list and pages; DF40 full author list; MIEA cited as arXiv. |
| G1 | Anonymous; "earlier version of this work" removed in both files. |
| G2 | Abstract 250 words; notation table (Table II); Table III without CIs; Table V reduced to 7 columns with the full version in S8 (Table S14). |
| G3 | Internal tags (RU1-RU5, SUP, HYB) replaced in tab_v5_alipair*.tex and tab_v5_cgd_explain_all.tex; supplement refers to paper sections by number (xr). |
| G4 | Teaser regenerated with the main model (v4 used the superseded RU-clipe4 checkpoint, found while fixing G4); caption says frames were selected where SBI errs and ours is correct, with benchmark rates. |
| G5 | Negative results moved to the end of Results as a 5-line summary; section titles are not sentences. |

## Left for experiments (not done; each needs new scoring, training or data)

A1 identity/expression/landmark measurement per edit family; A2 scoring DF40 entire-face-synthesis and face-editing sets;
B1 probe on released Effort/FA/GenD/DFD-HR weights, vignette dose response, smoothing shift; B3 face-local smoothing of forgeries
and the evasion test on the 17 published detectors; B5 forged-only arm P3 (3 seeds); B6 P1 under Effort's scheme; B8
face-size-matched Celeb-DF-B subset; B10 model-swap maps, maps on false positives and misses, non-oracle deletion curves;
B11 a fresh smoothing source; B14 seeds for the variant, binary control and a third main seed; C6 threshold fixed on FF++
validation for every detector; C7 own-crop scoring on the service; C10 identity-level bootstrap re-runs; D9 latency; E15 the
symmetric view in a non-CLIP pipeline; E16 training with DF40 reenactment data. Citations not added because they were not
verified in this round: SIDA, M2F2-Det, DD-VQA, FFAA, LipForensics, FTCN, AltFreezing, Dantcheva et al. 2012, Rathgeb et al. PRNU.

## Formulas of the numbers new in v5 (make_tables_v5.py)

Celeb-DF-B (`scores_v3/<name>.npz`, column 1 = P(fake); split `cdfb_std32v3.txt`; 1,000 draws of video ids with
`default_rng(1)`, identical to `fair_cdfb.py`; asserted to reproduce `fair_cdfb.json` point values and its Effort/FA paired intervals):
- t = 95th percentile of P(fake) on untreated genuine frames (`real`), re-estimated in each draw.
- FA_x = share of genuine frames of condition x with score > t; MISS_x = share of forged frames with score <= t.
- AUC_c - AUC_b = AUC(real_compressed vs synthesis_compressed) - AUC(real_beautified vs synthesis_beautified).
- dMISS_beauty = (MISS_b - MISS_0) - (MISS_c - MISS_0); dFA_beauty = FA_b - FA_c, CI = 2.5/97.5 percentiles over draws.
- Video AUC: mean frame score per (condition, video id), AUC over videos of the genuine vs forged condition.
- Paired AUC_b difference: AUC_b(model) - AUC_b(reference) on the same draw; CI = percentiles of the 1,000 differences.
- Exposure family: d = dMISS_beauty(arm x) - dMISS_beauty(arm y) on identical draws; p = max(2 min(P[d<=0], P[d>=0]), 1/1000);
  Holm over the nine contrasts (P1-P0, P2-P0, P2-P1 x three seeds).
- Videos per condition: unique video ids with at least one detected-face frame in the split.

Service, Smoothing-90 (`published_scores_<det>.npz` field `s`; `ali_scores_<tag>.npz` field `P[:,1]`):
- d_i = logit(P(fake) of the Smoothing_90 render of original i) - logit(P(fake) of original i), P clipped to [1e-7, 1-1e-7].
- median d with a 95% CI from 1,000 resamples of the 2,210 pairs (`default_rng(0)`); share d>0 asserted equal to `paired_up` of
  `smoothing90_thresholdfree.json`; two-sided binomial sign test on (#d>0, #d<0), ties dropped (`scipy.stats.binomtest`).

Cross-detector correlation (B2): Spearman (`scipy.stats.spearmanr`) over the 13 detectors present in both
`smoothing90_thresholdfree.json` and `df40_eval.json`, of `paired_up` and of `fa_s90` against DF40 mean reenactment video AUC
(`ff/FR`, `cdf/FR`); Holm over the four; repeated without CADDM. Over our seven FF++-only arms (seed 1): `paired_up` from
`ali_scores` (make_tables_v4.thresholdfree) against `ff/FR` (make_tables_v4.df40_mean).

DFD filter source for the two tags not in `dfd_filteredff.json` (P2-sym seed 1, the variant): make_tables_v4._filt_compute
(point values verified on Effort).

Trade-off table, "frame AUC, both smoothed": `auc_smoothed_both[2]` of the smoothed-forgery record (strong bilateral),
from `smooth_evasion2.json` or make_tables_v4.evasion_rec.

Values used in the text (from `v5_numbers.json`): beauty-only AUC loss Effort 0.075, FA 0.066, GenD 0.091, DFD-HR 0.077, ours
0.052/0.043; dFA_beauty DFD-HR +9.8 [6.5, 13.1], CADDM +9.9 [7.7, 12.1], GenD +3.6 [1.2, 6.6], ours +4.9 [2.8, 7.5]; CADDM video AUC
0.965 / 0.933 / 0.832; paired AUC_b main seed 1 vs Effort/FA/GenD/DFD-HR +0.059/+0.038/+0.059/+0.028 (lower bounds 0.030/0.013/
0.032/0.005), seed 2 +0.045 to +0.076, P0 +0.022 to +0.053; Holm-adjusted P1-P0 p = 0.009 in each seed, P2-P0 seed 3 p = 0.044;
Spearman 0.36 (p 0.23), 0.49 (0.09), 0.62 (0.024), 0.31 (0.30), Holm minimum 0.096, arms 0.25 (0.59); median logit shift
published +0.67 to +5.47, main -1.20 [-1.28, -1.12], seed 2 -0.53, variant -1.09, binary +0.41, P2-sym +0.09 [0.03, 0.12]
(p 3.2e-4) and +0.03 (p 0.07).

## Bibliography entries added or completed (verified 2026-10-16)

| Key | Source checked | Result |
|---|---|---|
| fakevlm2025 | NeurIPS 2025 proceedings page; arXiv 2503.14905; Crossref DOI 10.52202/085713-1974 | verified (pages omitted: proceedings and Crossref disagree) |
| geirhos2020 | Crossref, DOI 10.1038/s42256-020-00257-z | verified |
| balestriero2022 | NeurIPS 2022 proceedings page | verified |
| rathgeb2019 | Crossref, DOI 10.1109/ACCESS.2019.2948526 | verified |
| jain2018 | Crossref, DOI 10.1109/BTAS.2018.8698545 | verified |
| hendrycks2019 | ICLR 2019 virtual site; arXiv 1903.12261 | verified |
| deeperforensics2020 | CVF open access (pp. 2889-2898; IEEE gives 2886-2895) | verified |
| nguyen2019multitask | Crossref, DOI 10.1109/BTAS46853.2019.9185974 | verified |
| hifinet2023 | CVF open access; Crossref DOI 10.1109/CVPR52729.2023.00308 | verified |
| dfdhr2026 (completed) | CVF open access CVPR 2026 | authors Sun, Yan, Zhang, Yao, Ding; pp. 13984-13995 |
| df40 (completed) | NeurIPS 2024 D&B proceedings page; arXiv 2406.13495 | eleven authors, pp. 29387-29434 |
| miea2026 (changed) | arXiv 2609.02751 | authors verified; ACM MM 2026 claimed by the authors only (DOI not resolvable), cited as arXiv |
