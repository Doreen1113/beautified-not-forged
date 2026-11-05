# Paper v6 (2026-10-17): integration of Addenda 38-45

Files: `main_v6.tex` / `main_v6.pdf`, `supplement_v6.tex` / `supplement_v6.pdf`, `refs_v6.bib` (v5 + `openfilter2022`),
`make_tables_v6.py` (writes `tables/tab_v6_*.tex`, `figs/fig_accuse_v6.{pdf,png}`, `v6_numbers.json`), `build_v6.sh`.
v5 files are unchanged. No model was run; every new number is read from the Addendum 38-45 result files listed below, through
`make_tables_v6.py` (which asserts that every v5 trade-off cell it rebuilds is identical to `tab_v5_tradeoff_main.tex`, that the
oracle column of `ffpp_val_thr.json` equals the 5%-FPR column of the v5 service table, and that the heatmap reproduces the
published per-source values it was checked against).

Build: `sh docs/paper_v2/build_v6.sh` (tectonic on gsplat-ubuntu `~/paper_build/paper_v2`, order main, supplement, main,
supplement; PDFs copied back). `\ours` is now defined before `\externaldocument` in both files because supplement captions
containing `\ours{}` are read through the .aux.

Pages: main 10 (body pages 1-8, Conclusion ends in the right column of page 8, references pages 8-10; v5 body ended in the left
column of page 8 with references to page 9). Supplement 25 pages (v5: 21). Abstract 250 words (same counter as v5).

## Sources of the new numbers

| Addendum | Result file | Used for |
|---|---|---|
| 38 smoothed genuine / forged, 17 detectors + arms | `retouch_unified_20260929/smooth38.json`, `SMOOTH38.md` | Sec. V-A "Skin-only smoothing", V-D, Fig. 2 last column, Table S10 |
| 39 dose response | `retouch_unified_20260929/dose39.json`, `DOSE39.md` | Sec. V-B (rewritten), Table S11 |
| 40 forged-only P3 | `retouch_unified_20260929/p3_readout40.json`, `RESULTS_clipe5fbp3_s20260929.md`, score npz | Sec. V-C, Table V row P3, Table S15 |
| 41 DF40 entire-face synthesis | `df40_eval_20261012/df40_efs41.json`, `DF40_EFS41.md` | Sec. V-E "Entire-face synthesis", Table I, Table S24 |
| 42 second seeds variant / binary | `review_v4_exps_20261016/readout42.json`, `READOUT42.md`; `smooth_evasion2.json` (seed-2 miss rises) | Sec. V-D, V-E, Table V, Table S22 |
| 43 AR source | `review_v4_exps_20261016/ar_source.json`, `AR_SOURCE.md` | abstract, Sec. III sources, V-A "Instagram AR filters", Fig. 2, Table S8 |
| 44 FF++-validation threshold | `review_v4_exps_20261016/ffpp_val_thr.json`, `FFPP_VAL_THR.md` | Sec. III rule, V-A "A deployable threshold", Table IV last column, Fig. 2 (oracle values), Table S9 |
| 45 identity bootstrap | `review_v4_exps_20261016/identity_boot.json` (`category_changes`, rerun with second seeds), `IDENTITY_SUMMARY.md` (first run) | Sec. III, V-A (CADDM), V-E, Table S12 |

Formulas (all as in the addenda; `make_tables_v6.py` only reads them):
- Fig. 2 / `heatmap` in `v6_numbers.json`: oracle (per-source 5%-FPR) accused share of beautified genuine faces. Presets =
  `ffpp_val_thr.json` `Celeb-DF-B.<det>.real_beautified.oracle` (= FA_b of Table III); colour = `DFD + colour filters (full
  frame).<det>.genuine filtered.oracle`; service = `commercial retouching.<det>.Smoothing_90.oracle` (NPR n/a); AR =
  `ar_source.json` `fb|blfw.<det>.accused`; face-local = `smooth38.json` `<det>.forms.fl06.fa[0]`.
- Table IV last column: `ffpp_val_thr.json` `commercial retouching.<det>.Smoothing_90.deploy` (threshold = 95th percentile of
  P(fake) on 530 FF++ c23 validation genuine frames).
- Table V (`tab_v6_tradeoff_main.tex`): make_tables_v4 cell definitions (thresholdfree on `ali_scores_<tag>.npz`,
  `evasion_rec`, `video_auc`, `cdfb`, `df40_mean`), with P3 (`clipe5fbp3`) added and second seeds of `clipe5`, `clipe5y`,
  `clipe5b` read where the score files exist.
- Table S12: `identity_boot.json` `category_changes` (24 entries). The first run (`IDENTITY_SUMMARY.md`) had 20 of 456; the rerun
  drops the three "merged identities" entries (variant not usable, as declared) and adds seven entries for the second seeds.

## Changed claims (v5 -> v6)

| v5 | v6 |
|---|---|
| Three beautification sources plus one service; "AR filters were excluded because their capture pipeline leaks the label"; supplement "No claim is made on AR filters" | Fourth source: Instagram AR renders (FairBeauty 2,927 pairs, eight distinct filters; B-LFW 3,000 of 11,891 pairs). All 17 published detectors accuse FairBeauty renders, 16 accuse B-LFW (NPR saturates); JPEG-q90 control keeps 0.64-1.05 of the accused share except NPR; read as an upper bound because the AR capture path is confounded. AR pairs are still excluded as training data. |
| Mechanism section "Colour filters: a probe of one model" (radial overlay moves the logit of one FF++-only model) | Section "Dose response": for the four released CLIP detectors face-local smoothing (4/4) and whole-crop bilateral (4/4) push genuine frames toward forged with strength; a vignette alone does not (Effort, FA, GenD move toward genuine; DFD-HR passes with 3% of its gap). The one-model radial-overlay effect is stated as a property of that model. |
| Whole-crop smoothing only; "the smoothed forgeries are whole-crop filtered, not face-local" (limitation) | Face-local (skin-only) smoothing accused by all 17 (CLIP four 87.8-99.3% / 99.9-100%); P1-smooth misses rise 41.5 / 55.1 under it; the symmetric arms do not remove it (P2-sym 54.1 / 37.8 and 98.7 / 91.5%; variant 37.9 / 80.2%). |
| "The fourth cell, views on forged faces only, was not trained" | P3 (one seed): Smoothing-90 63.8% [59.0, 67.8], +9.6 [+6.0, +13.4] over P0; whole-crop FA 99.5 / 100% at mid / strong; sign rule complete (pre-declared reading (i) holds, (ii) does not). |
| "A threshold fixed on FF++ validation was not evaluated" | Evaluated: published detectors accuse 15.2-93.3% of Smoothing-90 at the deployable threshold; ours 0.1-0.5%; detector ranking not stable between rules (Spearman 0.29, 0.37). |
| "Bootstraps resample videos, not identities" | Identity-cluster bootstrap: 24 intervals change category, none a headline; six ours-minus-published filter AUC differences and eleven DF40 FF++-domain differences become ties; the 0.015 face-swap gap to GenD (FF++ domain) contains zero; CADDM's -2.9 contains zero; paired AUC_b claims of ours vs the CLIP four unchanged. |
| Variant: one seed; "fails (iv), main model stays"; miss rise +28.1 / +33.8 / +34.1; abstract "misses 28-34 points more" | Two seeds: outcome replicates (fails on both), reason does not (seed 1 fails (iv), seed 2 fails (ii) with Smoothing-90 17.8%); whole-crop FA removal replicates (1.0-1.7 and 3.8-8.4%); miss-rise cost does not (+34.1 vs +11.6 at the strong strength). "28-34" removed from the abstract and conclusion. |
| Binary control: one seed; "better on every untreated source, by 0.01-0.15" | Two seeds: better on Celeb-DF-v2 frames, Celeb-DF-B AUC_b and DF40 reenactment on both seeds; DFD and Celeb-DF-v2 video seed-dependent. |
| "DF40's entire-face-synthesis and attribute-editing sets were not scored"; Table I "not scored" | Entire-face synthesis scored as a descriptive probe (ours below Effort and GenD everywhere; three-way head calls 88-89% of ddim and 42-48% of SiT stills beautified); DF40 face-editing folders not available to us. |
| Contributions: measurement on presets, filters, service | Measurement on four sources with JPEG control, skin-only test, dose response and deployable threshold; four exposure arms; reference models weak on synthesis and accusing AR renders. |
| New honest limits | Our models accuse AR renders (main 75.1 / 86.7%; variant and binary 75.6-94.3% over two seeds), so the paper does not claim that training removes the accusation in general; symmetric arms do not remove skin-only false alarms (38-99%). |

Also: the evidence-map table (v5 Table VII) moved to the supplement (Table S31, caption now self-contained) to keep the body at 8
pages; the fusion paragraph and the explanations related-work paragraph were shortened; Limitations and Conclusion rewritten.

## Post hoc / declared status (stated in Sec. S1)

Descriptive (no bar): Addenda 38, 41. Pre-declared readings: 39, 40, 42, 43, 44. Amendment before scoring: B-LFW sample (43).
Correction after reading folders: FairBeauty has eight distinct filters, not eleven (43). Not declared: Spearman of B-LFW vs the
service (0.59, p = 0.013). Deviation: the "merged identities" variant of 45 was not usable and is not reported.

## Left inconsistent or open

- `IDENTITY_SUMMARY.md` (20 of 456) predates the rerun in `identity_boot.json` (24 changes); the total interval count of the rerun
  was not summarised, so the paper gives 20 of 456 for the first run and the list of 24 for the rerun.
- Rounding differences between FINDINGS.md and the score files used by the tables: P3 Celeb-DF-v2 video AUC 0.944 (FINDINGS) vs
  0.943 (Table V); P3 Smoothing-90 lower CI 59.1 vs 59.0; Effort vignette 0.8 median -0.21 vs -0.20; binary minus main DFD video
  +0.010 vs +0.009. The paper uses the table values.
- Table III (Celeb-DF-B / DFD) and Tables S5-S6 are still the v5 tables: no rows for the second seeds of the variant and the
  binary control, and no identity intervals for P0's paired AUC_b (the text says "video resampling" there).
- Not scored: P1 on the skin-only forms (only P1-smooth), the variant's second seed on the skin-only forms, the main model's
  second seed on the AR sources, P3 under Effort's scheme, P3 second and third seeds.
- The capstone Table IV still bolds the "main model - GenD, FS FF++" interval (video resampling); the capstone text states that it
  contains zero under identity resampling.
- `supplement_v6.tex:114` overfull by 2.1 pt (inherited from v5).

2026-10-17: the items above are resolved (or stated as not resolvable) in paper v6b; see `V6B_CHANGES.md`.
