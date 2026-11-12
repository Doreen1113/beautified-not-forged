# report_v3 changes

## r3 (2026-10-29): figures redrawn, system output and two result tables added

Reason: the figures carried from the paper were drawn for an IEEE column and scaled down to the report, so the text
ended at 5 to 7 pt; the old pipeline strip was a text dump; there was no architecture figure, no figure of the page's
output, no per-operation result and no three-class result.

Rules applied to every new figure: drawn at the print width (text width 14.66 cm), Times at 9 to 10 pt, nothing
scaled after drawing; diagrams in TikZ so the font is the document's; one message per figure; dashed reference lines
explained in the caption, not by in-plot labels that collide with marks.

- `figs/fig_system.html` -> `fig_system.pdf` (Figure 2, third version; the TikZ versions `fig_arch.tex` were rejected as
  "text boxes" and "too plain"): HTML/CSS layout rendered to a vector PDF by headless Chrome (`render_html_fig.py`,
  Arial embedded). Four tinted stage panels with chips, image tiles 2.2 cm, a gradient backbone shape, score bars, a
  callout on the named part, the sentence card with check pills, and a training strip showing the smoothing rule on a
  genuine and a forged frame (`make_tiles_train.py`, `ops.op_smooth`). Earlier description of the TikZ version: the system drawn
  from one held-out record with a real image at every stage (photo with landmarks, crop, backbone shape, class-score bars,
  16x16 map, map on the face, part masks, named part, the sentences and checks). Tiles from `make_tiles_arch.py`
  (`figs/arch_*.png`, numbers in `arch_numbers.tex`); labels are one or two words, the details are in the caption.
- `figs/fig_explain.html` -> `fig_explain.pdf` (Figure 4, third version): record / sentences / checks as three panels,
  each value in the sentences traced to the record by a coloured line, and a rejected sentence with the broken rule under
  each phrase. Record `docs/demo_ru/test/fixture_t2.json`, id `ffhq_demo_edit:17042_nose`.
- `figs/fig_output_a.png`, `fig_output_b.png` (new, Figure 5): the page's result card on example 2 (FF++ 454, mouth
  donor) and example 3 (FFHQ 17001 Alibaba Smoothing-90), cropped from `take_screens.py` shots of 2026-10-29
  (after the server mode was removed). Replaces `pipeline_en.pdf`.
- `figs/fig_exposure_r3.pdf` (Figure 3): the four exposure arms as two bar panels with 95 % intervals; replaces the
  2x2 pill layout (`fig_exposure_v10.pdf`).
- `figs/fig_perop.pdf` (new, Figure 7): accusation per operation and strength, five published detectors and both seeds
  (`alipair_zeroshot_20260929/published_ali.json`, `by_op.fake_at_t`).
- Table 2 (new): three-class recall and error directions on the FF++ test split, main model s1 / s2
  (`RESULTS_clipe5_s2026092{9,30}.md`) and the shipped browser model (`split_eval.json`, `Ours-lite` = ru4e).
  The candidate row is `\pending{}` until the Addendum 70 readout.
- Table 4 (new): per-operation and per-strength routing, paired rank and accusation of the main model
  (`RESULTS_clipe5_s20260929.md` Alibaba table + `published_ali.json`).
- New text: Sections 6.1 (three-class) and 6.3 (per operation); Appendix A lists the sources.
- Scripts: `make_figs_r3.py` (matplotlib figures and crops), `patch_r3.py` (report edits, backup `report_pre_r3.tex`).
- Build: 19 pages, no overfull boxes (`build.sh`, tectonic on gsplat-ubuntu).

Kept from the paper: `fig_teaser_v9` (Figure 1), `fig_twoaxis_v10` (Figure 6), `fig_context_v8b`, `fig_evidence`,
all readable at the report width (axis text 8 pt or more).

Still pending: Addendum 70 numbers (Tables 2 and 8, Section 6.8), member data, division of work, phone latency.

## r4 (2026-10-29, late): every remaining figure redrawn in the HTML design system

`make_html_figs.py` writes six HTML/SVG pages and renders them with `render_html_fig.py`: `fig_teaser` (Figure 1, images
from `published_scores_*.npz` / `celebdfb_v2 scores_v3`), `fig_exposure` (Figure 3, `p3_readout40.json`), `fig_twoaxis`
(Figure 6, `main_claim_A.json` + `fair_cdfb.json`, hand-placed labels with leader lines), `fig_perop` (Figure 7,
`published_ali.json`), `fig_context` (Figure 8, `bdry38.json`), `fig_evidence` (Figure 9, tiles exported from
`docs/paper_v2/figs/fig_evidence_tiles.npz`). Same panels, chips, palette and 8-9 pt Arial as Figures 2 and 4; the
matplotlib versions (`fig_teaser_v9`, `fig_exposure_r3`, `fig_twoaxis_v10`, `fig_context_v8b`, the first `fig_perop`
and `fig_evidence`) are no longer used by the report. Figure 5 (page screenshots) is unchanged.

## r5 (2026-10-30): Addendum 70 numbers, W shipped by decision

Table 2: shipped browser row = W (81.7 / 91.6 / 81.2), previous = ru4e. Table 8 (browser gate): all values filled, G1 marked
fail, DFD and FF++ false-alarm rows added; the result paragraph states the failed gate, the overlapping G1 intervals and the
user's decision. Figure 2 tiles and numbers from the W record; Figure 5 retaken with W and the smoothing-only sentence;
Section 4.5 says the sentence names smoothing only. Only the phone latency is still pending. 20 pages.

## r6 (2026-10-31): what the project did, stated; method figure; model inventory; no user study
- Section 7 rewritten as three paragraphs: research findings (two-direction audit, training cause, mechanism, VLM text
  carries no image information), method (paired-edit supervision with exact footprints, factorised heads, evidence head
  tested by restoration, sentences composed and checked by code), application (browser chain, known-answer cases, gate).
- Section 8 no longer carves the capstone into "the lab's parts" and "our parts"; one sentence states the paper overlap.
- Conclusion: the sentence about the stopped user study removed. The study is not mentioned anywhere in the report, the
  demo page, or the exhibition site (site/people.html removed, build_site.py no longer reads docs/capstone/human_study/).
- New Figure (fig_method.pdf, make_tiles_method.py + make_fig_method.py): the method on one page. Three supervision sources
  with real tiles (FF++ triplet 463__f0179; Tencent pair FFHQ 60002 split into eye/contour/tone/texture with footprints
  outlined; part-level forgery 682__f0867 nose with its mask), the backbone and three heads with the loss, the main
  model's (clipe4r s20260929) outputs on the forgery (forged 1.00, nose) and on an Alibaba EyeEnlarging_90 render
  (beautified 0.97, eyes; part named with the page's part masks), the three tests, the browser. 14.66 x 17.4 cm, [p].
- fig_system moved from Methods to Section 5.1 (the browser system), which now opens by saying what the page is.
- New Table (tab:models): every model in the report (main CLIP, browser shipped, browser small, the 17 published detectors)
  with parameters, where it runs and its role.
- Demo page: the RepViT model without an evidence head removed from the model menu (two models remain); an "What this
  page is" paragraph added to About (EN and ZH); README header rewritten (purpose, models, legacy line).

## r7 (2026-11-01): phone latency measured
- Section 6.8: the pending phone measurement replaced. bench.html (40 timed runs on the four examples after one warm-up,
  one WebAssembly thread): desktop headless Chrome median 0.51 s (P90 0.54); iPhone Safari iOS 26.2 median 0.59 s (P90
  0.79), model 0.43 s, 1024 px example 0.77 s, model download 52 s. Section 7 Application sentence updated. No pending
  values remain. Sources: docs/demo_ru/test/bench_desktop_effb4.json, bench_iphone_effb4_20261101.json.
- Small RepViT model added to Section 6.8: desktop 0.15 s, iPhone 0.19 s (P90 0.36), download 14 s.

## r8 (2026-11-03): the method drawn as what it is; one wrong model in the overview fixed
- The overview's main-model outputs were computed with clipe4r, not the report's main model clipe5 (seed 20260929, the
  checkpoint behind every table). make_tiles_method.py now loads clipe5 (RU5 output tuple); the outputs are unchanged in
  substance: forgery 1.00 / nose, Alibaba eye render 0.98 beautified / eyes (was 0.97).
- New Section 4.x "Splitting commercial renders into single operations" (sec:engine): motivation, the DIS flow / eye mask /
  residual low-pass split, exact footprints, 50,112 of 73,952 components kept. The method section had not described it.
- New Figure fig_engine (fig_engine.tex, make_tiles_engine.py, make_fig_engine.sh): the flow as arrows, the eye mask, the
  residual, the four components with footprints, on FFHQ 60002; the figure's components are checked bit-identical to
  decompose.py, reconstruction 108.1 dB.
- New Figure fig_model (fig_model.tex, make_tiles_model.py, make_fig_model.sh): CLIP ViT-L/14 with one Transformer block and
  the LoRA adapter enlarged, token shapes, the four heads (fz 1024->2, operations 1024->4, auxiliary amounts 1024->4,
  evidence 1024->1 per patch token) and the loss, from the code and the checkpoint (3,157,003 trained parameters).
- Training recipe corrected: one 1024->2 head gives f and b (not "two heads"); probabilities written with sigma(f); the
  auxiliary amount head is stated with its failed pre-declared R4 bar; optimiser and step size stated.
- fig_method: panel 4 "its heads", loss includes the amount term, browser latency 0.59 s iPhone / 0.51 s desktop, residual
  written as in the code.
- Report 25 pages, no undefined references or overfull boxes.

## r9 (2026-11-03): trimmed from 25 to 20 pages (backup report_pre_r9.tex)
- Compared with the 2025 winners (scratchpad dl/: 6-12 pages incl. cover; Trojan, Attention, Sports two-column 10 pt;
  VIS4GS, Omniverse one-column ACM 9 pt; QAOA, MBFF Chinese 12 pt). None of the six identified winners has a team section;
  three of the four MBFF reports do. The official format (12 pt, single column) is kept.
- Six of the 25 pages were figures pushed behind the references; floats now stay before Section 7 (placeins, relaxed
  float fractions).
- Removed: appendix "Sources of the Numbers" (now SOURCES.md); fig_system (its content is in fig_method, fig_model,
  fig_explain and the screenshots); fig_twoaxis (same numbers as the audit table); the per-operation routing table (three
  numbers kept in the text); subsection "Which operations can be named" (one sentence in Costs); latency detail; the team
  placeholder paragraph. Conclusion and the Application paragraph shortened. References at 10 pt.
- 20 pages: cover, 17 body, 2 references; 10 figures, 8 tables; no undefined references or overfull boxes.

## r10 (2026-11-03): IEEE two-column like the 2025 winners; no team section (backup report_pre_r10_onecol.tex)
- report.tex is now an IEEEtran conference paper (A4, 10 pt, two columns); cover.tex keeps the department cover in the
  official format; build.sh compiles both and merges them into report.pdf (cover + body pages 1-13). The abstract is
  abstract.tex, shared by both.
- Team Cooperation section and table removed (none of the six identified 2025 winners has one); the sentence on the
  overlap with the laboratory paper moved to the end of Important Contributions.
- Column figures redrawn at the column width 8.86 cm (make_html_figs.py COL): teaser and exposure with stacked panels,
  per-operation as a 2x2 grid, edge treatment narrowed; text sizes unchanged. Page-wide figures (method, engine, model,
  explain, screenshots, evidence) are figure* at the width they were drawn at (14.66 cm), not scaled. Screenshots cropped to
  photo, verdict and sentences (fig_output_*_crop.png).
- Tables: comparison, models, audit and blind matching in one column (short headers, meanings in captions); three-class,
  exposure arms, restoration and browser gate span both columns.
- 14 pages in all (cover 1, body 13 including 1.5 of references); no overfull boxes or undefined references.

## r11 (2026-11-03): figures redone for the two-column page (backup report_pre_r11.tex)
- New Figure 2 (make_fig_overview.py -> fig_overview): the method at the full text width 18.13 cm, half the height of the old
  full-page fig_method; images, a drawn ViT stack with LoRA and the four heads, the main model's outputs, and the three tests
  plus the iPhone timing as headline numbers; prose moved to the caption. The sentence in panel 3 is written by the
  project's composer (explain_v2_en.compose_en) from the main model's record and passes gate v3 (H1-H6, G7-G9) when the
  figure is built (figs/overview_sentence.json); the figure is not drawn if a check fails.
- All page-wide figures now at 18.13 cm, none scaled: fig_explain and fig_evidence re-laid out (evidence tiles 3.08 cm);
  fig_engine and fig_model gained a side card (checks and yield; loss and step) in place of the text under them; one
  screenshot (the Alibaba smoothing example) at the full width instead of two at 14.66 cm.
- Tables: all eight are one-column now (three-class transposed; exposure, restoration and browser gate with compact cells
  and meanings in the captions; gate values kept exact). Column floats may go here or at the bottom ([!htb]); two floats
  moved earlier in the source. No float after the references.
- Contributions: "two factorised heads" corrected to factorised class logits (one 1024->2 head); item (4) shortened.
- 12 pages in all (cover 1, body 11 including references); no overfull boxes or undefined references.

## r12 (2026-11-03): best values marked in the tables
- Tables III (three-class, best per row), IV (audit) and VI (restoration): best in bold, second underlined. Rule, stated in
  the captions: AUC and recall highest; accusation and error lowest; changes caused by beautification (miss rise) closest
  to 0; share above the own original closest to 50 (no effect); NPR, saturated, not ranked. 12 pages, no overfull boxes.
- Paper v10 (docs/paper_v2/main_v10.tex) Tables dirA and dirB: the same rule in bold only (dirB already bolded AUC);
  benchmark_release/reference copies updated the same way; `make_tables.py all --check` still matches every row (it drops
  	extbf). dirA tabcolsep 2.5 -> 2.3 pt for the bold digits.
- Final meeting deck: docs/meeting_20261103/final_meeting_20261103.pptx (16 slides, style of the 10/18 deck).

## r13 (2026-11-05): equal-data comparison
- Table IV gains "Ours, FF++ only" (clipe5f, seeds 1 and 2): trained on the FF++ c23 videos of Effort, Forensics Adapter,
  GenD and DFD-HR, no commercial renders or part edits (PRE_DECLARED Addendum on clipe5f). Celeb-DF-B AUC after
  beautification 0.872 / 0.870, miss rise +7.5 / +9.1 (fair_cdfb.json RU-clipe5f, RU-clipe5f-s2); accusation columns "--"
  as declared (no retouching data). One sentence in Section VI-B; the paired intervals vs Effort, Forensics Adapter and SBI
  exclude zero. Contribution (1) no longer says "for the first time". Table IV rows at 0.92 stretch, screenshot 0.86 width:
  12 pages.

## r14 (2026-11-05): true-footprint outline green in Fig. 6
- The true footprint in the evidence figure was sky blue (#56B4E9), easy to confuse with the cyan half-strength contour of
  the web page screenshot (Fig. 7). `make_tiles_evidence.py` redraws ev{0,1}_truth.png from fig_evidence_tiles.npz in green
  (0, 200, 83); drawing rule fitted to the old tiles (5 px anti-aliased contour on the 380 px crop, then LANCZOS to 360 px;
  mean abs. difference 0.009 of 255 with the old colour). Legend "green line: true footprint". Other tiles unchanged;
  figstyle.TRUTH (paper v10, website) unchanged. 12 pages, no warnings. Deck slide 14 rebuilt.

## r15 (2026-11-05): result-card screenshot shows a part-level forgery
- Fig. 8 now shows example 2 (FF++ test frame, mouth replaced with another test-video subject's; `ffpp_partedit/test`),
  cropped from `demo_ru/test/screens/1366_example2_full.png` (2026-10-31, current page) at box (178, 536, 1187, 1114),
  legends included -> `fig_output_a_crop.png`. It replaces example 3 (Alibaba Smoothing-90), whose evidence is spread over
  the whole face. Caption states the outline rules from `evidence_overlay.js` (yellow = top 12 % of the map, cyan = score
  >= 0.5; the page legend's "half strength" is the 0.5 score) and that the example was chosen to show the outlines, the
  restoration test (Table VI) measuring every held-out forgery. Section text updated. 12 pages, no warnings.
- Deck slide 15 uses the same crop (make_assets.py), caption and note updated.

## r16 (2026-11-05): teaser claim corrected
- Section I said "the same four detectors now let it through" for panel (b) of Fig. 1. The figure's own data
  (`make_html_figs.teaser`, Celeb-DF-B id17_id35 frame 05, thresholds at the 95th percentile of untreated genuine frames)
  show DFD-HR still at 0.74, above its 0.63 threshold: three of the four let the beautified swap through. Sentence
  corrected; the same wording fixed in the final deck (zh and en, slide 2 and its notes). 12 pages, no warnings.
