# Sources of the numbers in report.tex

Moved out of the report body on 2026-11-03 (r9). Labels are the LaTeX labels in report.tex; paths are relative to the repository. Since r9 the report has no fig:arch (fig_system), fig:twoaxis or tab:perop; their sources stay listed for the numbers quoted in the text.

- Table tab:audit, Figure fig:twoaxis: `results/research/alipair_zeroshot_20260929/main_claim_A.json`;
`results/research/celebdfb_v2_20260927/fair_cdfb.json`; forgery-head-only row
`smoothing90_thresholdfree.json` (row ``binary full''); GPUPixel `retouch_unified_20260929/GPX38.md`.
- Table tab:exposure, Figure fig:exposure: `docs/paper_v2/tables/tab_v4_tradeoff.tex`;
P3 `retouch_unified_20260929/p3_readout40.json`.
- Figure fig:context and the four repairs: `BDRY38.md`, `RECAL_MISS.md`, `SCE_s2.md`,
`CTX38.md` (all in `retouch_unified_20260929/`).
- Table tab:restore: `docs/paper_v2/tables/tab_cgd_explain_all.tex`; named-part test
`results/research/explain_vlm_20261012/HOLDOUT_FINAL.md` §3.
- Section sec:res-text, Table tab:vlm: `HOLDOUT_FINAL.md` §1, §2, §4, §5;
`HOLDOUT_V4_LORA.md`; `MATCHING_v4_LORA.md` §8; `nl_v5/GATE_V3_RESULTS.notes.md`,
`nl_v5/P3_RESULTS.notes.md`.
- Operations: `retouch_unified_20260929/ORACLE_OPS.md`, `XVENDOR_OPS.md`.
- Table tab:browser: `retouch_unified_20260929/PRE_DECLARED.md` Addendum 70 and its readout;
`fair_cdfb.json` rows `RU4e-effb4`, `RU-clipe5`.
- Figures fig:arch and fig:explain: drawn in TikZ (`docs/capstone/report_v3/figs/`); the record
of Figure fig:explain is `docs/demo_ru/test/fixture_t2.json`, id `ffhq_demo_edit:17042_nose`.
- Figure fig:output: `docs/demo_ru/test/take_screens.py`, shots `1366_example2`,
`1366_example3` (2026-10-29), cropped by `make_figs_r3.py`.
- Table tab:threeclass: `retouch_unified_20260929/RESULTS_clipe5_s20260929.md` and
`..._s20260930.md` (block ``FF++ / cross-dataset''); browser row `split_eval.json` (`Ours-lite`).
- Figure fig:perop, Table tab:perop: `alipair_zeroshot_20260929/published_ali.json`
(`by_op`, `fake_at_t`); routing and paired rank `RESULTS_clipe5_s20260929.md` (Alibaba table).
- Costs: `docs/paper_v2/tables/tab_v4_df40.tex`; `main_claim_A.json` (`native_orig`);
`fair_cdfb.json` (`native`).
