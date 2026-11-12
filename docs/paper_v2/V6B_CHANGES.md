# Paper v6b (2026-10-17): v6 with the forgery-head-only model as the detection reference row

Files: `main_v6b.tex` / `main_v6b.pdf`, `supplement_v6b.tex` / `supplement_v6b.pdf` (bibliography `refs_v6.bib`),
`make_tables_v6b.py` (writes `tables/tab_v6b_*.tex`, `figs/fig_accuse_v6b.{pdf,png}`, `v6b_numbers.json`),
`make_fig_teaser_v6b.py` (`figs/fig_teaser_v6b.{pdf,png}`), `build_v6b.sh`. v6 files are unchanged. No model was run.

Build: `sh docs/paper_v2/build_v6b.sh`. The Celeb-DF-B bootstraps take about ten minutes; set `V6B_CACHE=<file>.pkl` to reuse them.
Pages: main 10 (body pages 1-8, Conclusion ends in the right column of page 8, references pages 9-10); supplement 27.

## Presentation

- Rows are `\oursB{}` = "Ours, forgery head only" (clipe5b, Table II: "full data, P2 views, forgery head only (binary)") and
  `\oursF{}` = "Ours, full model" (clipe5, Table II: "three classes + operations, evidence map"); the variant is
  "`\oursF{}`, sym. view". `\oursB{}` is the first row of every detection table and of Fig. 2 and has its own row in the teaser.
- Wording: the system outputs three classes and four operation scores; the forgery decision is read from z_f alone; the
  forgery-head-only model shows what the forged head reaches without the shared beautified head; the beautified class and the
  operation scores are attributes reported separately. Reason (Sec. IV Model): better than or equal to the full model on every
  untreated source and on Celeb-DF-B on both seeds (readout42 B block, identity_boot DF40 / filter paired blocks: no interval below
  zero), the shared head costs reenactment. The ordering was chosen after both seeds were read (stated in Sec. IV and S1).
- Explanation results (Sec. V-F, Tables S30-S31, Fig. S2) are attributed to the full model's evidence head; the
  forgery-head-only model has none.
- Abstract unchanged (it does not name a main model; "our full-data models ... 75-94% of AR renders" still covers 75.1-94.3).

## Items of the v6 "left inconsistent" list

| v6 item | v6b |
|---|---|
| IDENTITY_SUMMARY (20 of 456) predates identity_boot.json (24 changes) | `summarize_identity.py` now tests exactly the interval set of `identity_boot.py` and asserts that its list equals `category_changes`; regenerated: **24 of 563**, widening 0.86 / 1.06-1.08 / 1.00 / 1.30. First run kept as `IDENTITY_SUMMARY_firstrun_20261016.md/.json`. Paper quotes 24 of 563 (Sec. V-E, S9, Table S12 caption) |
| Rounding differences with FINDINGS | recomputed: P3 CDF video AUC 0.943486; P3 Smoothing-90 63.7557 [59.0498, 67.7839]; Effort vignette-0.8 median -0.205236; binary-main DFD video +0.009487. Paper: 63.756 [59.050, 67.784] (Sec. V-C), 0.943, dose table at three decimals (-0.205), +0.009 (Table S22). Dated note appended to FINDINGS.md. Also found: FA face-local 0.03 median 4.585 (FINDINGS 4.59, v6 4.58) -> paper +4.585 |
| Table III and S5-S6 without second seeds / P0 identity intervals | Table III: rows for `\oursB{}` s1/s2, `\oursF{}` s1/s2, variant s1/s2 (DFD from `dfd_filteredff.json`). S5 (`tab_v6b_cdfb_extra`): second-seed rows + identity interval of dFA_beauty. S6 (`tab_v6b_cdfb_paired`): video and identity interval for every model incl. P0, FF++-only three-way, P2-sym; the identity draws are those of `identity_boot.py` (rng 0) and reproduce its six full-data entries (asserted). P0 identity lower bounds >= 0.006, all our models >= 0.008 |
| Capstone Table IV bolds an interval whose identity CI contains zero | capstone Table IV rebuilt; bold only where the video interval excludes zero and, where identities can be resampled (DF40 FF++ domain, Celeb-DF-B), the identity interval too. "full model - GenD, FS FF++" no longer bold |
| supplement overfull 2.1 pt (line 118, inherited) | not changed |

## New or moved numbers (all from existing files)

| Number | Source |
|---|---|
| `\oursB{}` second seed: Celeb-DF-B 0.955 / 0.939 / 0.904, dMISS_beauty +5.7, FA_b 8.3, dFA +3.2 [+1.7, +4.8]; DFD 0.951 / 0.938 / +3.8 / +1.1 | `celebdfb_v2_20260927/fair_cdfb.json` RU-clipe5b_s20260930; `dfd_filteredff.json` |
| `\oursB{}` second seed Smoothing-90: above own 68.2, median shift +0.19 [+0.16, +0.19], 1508/694/8, accused 6.5, FF++-val thr. 0.1 | `ali_scores_clipe5b_s20260930.npz` via `make_tables_v4.thresholdfree`, `make_tables_v5.paired_shift`; `ffpp_val_thr.json` |
| teaser: forgery-head-only model accuses 7.4%, misses 36.6% of beautified deepfakes; decisions on the four frames real/real/fake/fake (threshold 0.9916) | `scores_v3/RU-clipe5b.npz`, `make_fig_teaser_v6b.py` |
| AR: `\oursB{}` 79.0 / 82.1 (FairBeauty), 89.0 / 90.3 (B-LFW); paired minus Effort +11.3 [+7.6, +15.1], minus FA +15.1 [+11.8, +18.1], minus GenD +3.4 [-0.6, +6.2] and -7.5 [-9.3, -5.1] (B-LFW), minus DFD-HR -6.8 / -6.2; FairFace originals at the FF++-val threshold 6.5 / 13.3 | `ar_source.json`, `AR_SOURCE.md`, `ffpp_val_thr.json` |
| whole-crop smoothed genuine FA: `\oursB{}` 9.9 / 35.5 / 45.6 (s1), 2.2 / 9.3 / 17.2 (s2) | `smooth_evasion2.json` (s2 computed by `make_tables_v4.evasion_rec`) |
| CDF-v2 / DFD: `\oursB{}` frame 0.914 / 0.961 (s2 0.923 / 0.951); paired vs CLIP four (DFB crop) | `ffpp_benchmark_20260925/dfb_crop_eval.json`; `readout42.json` (s2); Table S3 lower blocks |
| DF40 `\oursB{}` 0.969 / 0.842 / 0.926 / 0.647 and 0.961 / 0.856 / 0.924 / 0.698; paired vs CLIP four and vs `\oursF{}` with video / identity intervals | `df40_eval.json`; `identity_boot.json` DF40 paired (Table S23) |
| EFS `\oursB{}` sd2.1 92.0 / 73.0 | `df40_efs41.json` |
| Celeb-DF-B preset cost beyond re-encoding `\oursB{}` 0.038 / 0.035; dFA 2.3 [1.2, 3.8] / 3.2 | `fair_cdfb.json`, Table S5 |
| deploy: `\oursB{}` CDF-B untreated 7.7%, service originals 0.1% | `ffpp_val_thr.json` (Table S9) |

## Text trimmed to keep the body at 8 pages

Related work (smartphone-threshold sentence), Sec. III (Celeb-DF-B source description, service description, deployable-threshold
sentence, inpainting boundary sentence), Sec. V-B (the history of the one-model radial-overlay probe now one sentence; details stay in
S10), V-C (Holm and Effort-scheme sentences), V-D (chain intro, P2-sym bars, variant paragraph), V-E (detection and DF40 paragraphs),
V-F, V-G, Limitations, Conclusion. The AR paragraph no longer gives the variant's AR numbers (Table S8 has them). Teaser at 0.79
text width (v6: 0.84). Table II: first column widened, rows reworded.

## Not resolved

- Second seeds not run through `dfb_crop_eval.py`, so the own-crop paired intervals (Table S3, capstone Table IV) are first seed only.
- Skin-only smoothing (`smooth38`) has no second seed of `\oursB{}` or `\oursF{}`; P1 not scored on it (as in v6).
- No identity intervals exist for the own-crop Celeb-DF-v2 / DFD comparisons; there the bold rule uses the video interval.
