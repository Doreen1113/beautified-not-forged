# main_v8.tex: changes against main_v7.tex (2026-10-22)

Paper type changed from "measurement + mechanism + method (SIC)" to an **analysis / evaluation paper** for arXiv + IJCB 2027,
following `docs/RESEARCH_CRITIQUE_20261021b.md` Sec. 9-10 and the benchmark-paper template (five pillars, six-part
introduction, bold Finding sentences). `main_v7.tex`, `refs_v6.bib`, `supplement_v7.tex`, `tables/` and `figs/` are untouched.
New files: `main_v8.tex`, this file. The supplement still needs a v8 pass (see "Supplement" below).

Word count (check_v8.py in the session scratchpad): prose 4,937 + tables 1,233 + captions 427 = 6,597 words. This is above
the 6,000 target; with six tables and five figure slots it will probably run to 8.5-9 pages in IEEEtran. Suggested cuts if
the compile overflows: Related Work (306 words) to half; Table 1 (prior-evaluation comparison) into the Introduction text;
the identity subsection (283 words) to one paragraph. No build was run (build_v7.sh targets v7 files; a build_v8.sh would
scp main_v8.tex, tables/tab_sic.tex, figs/fig_teaser_v7.pdf, fig_exposure_v7.pdf, fig_bandenergy.pdf, fig_sic_curve.pdf).

## Structure (new)

1. Introduction: running example (beautified selfie, Fig. 1), three prior evaluations + BIAS-ID, three RQs, five design
   properties, proposal, four contributions.
2. Measurement protocol: classes, one rule / both directions / paired reading / bootstrap units, six sources, what is NOT a
   clean source (FairBeauty / B-LFW), detector list, **Table 1** comparison with prior evaluations.
3. Findings 1-7, each a bold "Finding N" sentence with evidence before it.
4. Companion three-way detector.
5. Limitations and what we no longer claim.
6. Related work (short).
7. Conclusion.

## Cut from the main paper

| v7 content | v8 disposition |
|---|---|
| Sec. "Method" (architecture figure fig_arch_v7, training-data paragraph, SIC equation and bars) | Architecture and recipe compressed to one paragraph in Sec. 4; SIC described in words in Finding 6; equation and bars pointed to the supplement. fig_arch_v7 not used. |
| Sec. "Localisation and restoration of part-level forgeries" (sec:cgd, IoU7 0.83-0.84, flip 93.5-94.0 %) | Removed. One sentence in Sec. 5 says it is in the supplement (evidence map, restoration test). |
| Sec. "What did not work" (operator training, learned inverse, map-pooled decision, Effort fine-tuning, CADDM fusion) | Removed from main; stays in supplement Sec. S-negative. |
| Sec. "Untreated detection and DF40" as a separate results section | Folded into Sec. 4 (companion detector): untreated CDFv2/DFD paired CIs (Table 7), DF40 FS one sentence, DF40 FR under "Costs". EFS probe dropped from main. |
| Forgery-head-only model as the first row of every table (v6b/v7 convention) | Dropped. The three-way model (clipe5 s1/s2, the model of MAIN_CLAIMS) is the only "Ours" in Tables 2, 3, 7; the forgery-head-only model appears only where it is the control (Table 5 BCT row, Table 6 reference row, Finding 7 identity comparison). |
| Fig. "fig_accuse_v6b" (accused share per source) | Replaced by the two-axis scatter placeholder (Fig. 6) built from MAIN_CLAIMS tables A and B. |
| Table "tab_v6b_twosided_main" (13-column Celeb-DF-B + DFD table) | Replaced by Table 3 (Direction B, 5 columns from FAIR_cdfb.md); the DFD-filter columns are no longer in the main paper. |
| Table "tab_v6b_retouch_main" | Replaced by Table 2 (Direction A from MAIN_CLAIM_A.md with CIs, plus the three control operations from tab_v6b_perop). |
| Dose-response paragraph as its own subsection | Compressed to two sentences inside Finding 1. |
| "Smoothing views: what the exposure arms taught" (sec:chain) | Necessity (Add. 31) and sufficiency (Add. 32) kept as two sentences in Finding 3; P2-nosmooth / whole-crop asymmetry details to supplement. |
| Related work paragraph on explanations (GAIN, DOLOS, FakeVLM, maskers) | Removed (explanation material is out of the main paper). |
| Related work on adversarial / semantic attacks (StatAttack, AdvShadow, Fatima, Hosseini, Laidlaw, GAT, AVA) | Removed (the operator-training line is no longer in the main paper). |

## Moved to the supplement (pointer only in main)

- Evidence map, restoration test, IoU7 / flip numbers (S-tab:cgd_all).
- Negative-result arms (S-sec:negative, S-tab:negative, S-tab:operator).
- Full SIC family with symmetric-penalty variants (tab_sic_full), bars text, the SIC equation.
- DF40 full table, EFS probe (S-tab:v4df40full, S-tab:efs).
- Dose-response table (S-tab:dose), smooth38 table (S-tab:smooth38), per-operation table, AR table (S-tab:ar),
  deployable-threshold table (S-tab:deploy), exposure-arm tables (S-tab:exposure, S-tab:p3), identity bootstrap.
- Boundary-case table (S-tab:labels).

**Supplement labels referenced from main_v8.tex** (all exist in supplement_v7.tex): S-tab:labels, S-tab:identity,
S-tab:ar, S-tab:reproduce, S-tab:retouch (**does not exist in supplement_v7; v7 main had tab:retouch itself; either add the
retouch table to supplement_v8 or change the reference to tab_v6b_retouch_main inline**), S-tab:smooth38, S-tab:dose,
S-tab:exposure, S-tab:v4df40full. A supplement_v8.tex should add: the SIC equation and bars (from v7 Sec. 4.1), the retouch
median table, RECAL_MISS and BCT full tables, ID_REF / ICT_PROBE tables, SCE table, FB_OPS table.

## Claims weakened or rewritten, and why

| v7 claim | v8 wording | Reason (source) |
|---|---|---|
| "SIC ... removes the cue"; "keeps the separation that a threshold cannot recover" (v7 abstract, Sec. 5.5, conclusion) | Finding 6: SIC is a smoothing-conditional recalibration; it "moves the error but does not remove it"; "leaves separability where the view put it". | RECAL_MISS.md: lambda=0 + oracle conditional threshold has both-classes-smoothed AUC 0.832 / 0.764 vs SIC-sg 0.790 / 0.778 (lambda 1) and 0.802 / 0.778 (lambda 0.1); recalibrated miss lambda=0 57.4 / 76.7 vs SIC 64-73. Critique Sec. 11 item 1 rule: not >= 5 points better -> "recalibration". |
| "Method (SIC)" as a contribution | Contribution 3 is now two negative results (threshold cannot separate; training only trades). SIC is evidence, not a method. | Critique Sec. 9-10. |
| "at a penalty weight of 0.1 ... lowers the false alarm from 85 % to 4 %" (abstract headline) | Kept only inside Finding 6 with the trade-off stated in the same sentence. | tab_sic.tex (fl12 84.5 -> 4.2). |
| Two-direction claim stated only as "both errors counted" | Now the headline: Direction A (accusation, retouching pairs) and Direction B (escape, Celeb-DF-B), each its own table and Finding. | MAIN_CLAIMS_20261022.md. |
| "Our full-data models accuse 6.5-12.5 % of the renders" (forgery-head-only + full model pooled) | Only the three-way model is reported: 8.6 / 12.5 %, above own 32.5 / 41.3 %. | MAIN_CLAIM_A.md ours main s1 / s2. |
| Ours "above Effort on both sets" (forgery-head-only model, v7 Sec. 5.6) | Three-way model: "on par" with all four CLIP detectors; every paired interval contains zero (Table 7). | tab_v6b_reproduce.tex, "full model minus detector" block. |
| Smallest escape / "beautification-specific miss rise ours +6.7" as a win | "not the model with the smallest escape"; larger than DFD-HR and CADDM (CI excludes 0); smaller than FA, SBI, GenD (both seeds) and Effort (seed 1 only). | MAIN_CLAIMS Direction B paired-difference lines. |
| Mechanism "the cue is the beautification signature" as proven, incl. FF++ texture origin | Finding 4 keeps the band-energy contrasts; the FF++ origin is "a correlation and a plausible origin rather than a demonstration"; the F2F+FS-only arm is named as running and not reported. | FFPP_BAND.md (low band not reduced in training forgeries; UnivFD accuses without FF++); critique R7. |
| "ceiling" / "evidence erased" (new storyline of 10-21) | Not used. Finding 6 says "measured loss, not a bound"; shortcut saturation vs erased evidence "cannot be separated with these data". | Critique Sec. 2 item 2, Sec. 11 item 1. |
| Identity channel as contrast / fusion as method (IDEA storyline) | Finding 7, discussion level: stable AUC, moving operating point, relative error x4-10; ICT / ICT-Ref fail the other way; fusion "dominated by the identity distance alone and not reported as a method"; prior art cited. | ID_REF.md, ICT_PROBE.md, RECAL_MISS.md; critique Sec. 2 item 1 (fusion CRITICAL -> delete), Sec. 6 C4. |
| Routed expert (SCE) | One sentence in Finding 6: clears the accusation, miss +41-46, both-smoothed AUC below the untreated detector on 7/8 forms; "one seed; the second is running". | SCE_s2.md (seed 20260930); SCE.md holds identical content; seed 1 (cvlab-104) pending. |
| AR filters as a fourth source with numbers (v7 Sec. 5.1 "Instagram AR filters") | Moved to "What is not a clean source" with the pipeline-control evidence; no claim on AR filters. | FINDINGS 2026-10-22 16:40 (Addendum 56: FairFace originals real 18.2 %; grey-hull control cannot separate); MAIN_CLAIMS "不再主張". |
| Four operation scores as an explanation output | Sec. 4 costs + Sec. 5: reliable only for smoothing (vendor TP 0.94 vs 0.20-0.38; AR recall 0.003-0.24); "we no longer claim them". | READOUT46.md attribute_main_same_seed presence TP; FB_OPS.md. |
| LLM-rewritten explanations | Removed; one sentence in Sec. 5. | MAIN_CLAIMS "LLM 改寫解釋：與模板句無差異". |
| "P2 against P0 ... sits in between" | Kept, with "changes sign across seeds, so symmetric exposure is on average better than none but not reliably so". | FINDINGS 2026-10-11 third seed; S-sec:exposure Holm p. |
| Libourel et al. cited as having measured AUC drop only | Related work and Finding 2 now say Libourel reported the AUC drop for three detectors and that our one-rule reading adds that the drop is misses; two-classes-beautified AUC loss is framed as extending Libourel, not as new. | Critique Sec. 6 C2 (partial scoop), R2. |
| "v7 ... loses 0.07-0.19 of frame AUC beyond re-encoding" (first draft of v8) | Corrected to 0.04-0.17 from the AUC_c - AUC_b column. | tab_v6b_twosided_main.tex (SRM 0.035 .. LAA-Net 0.172). |

## Numbers in the main text and their sources (summary; every number also has a % comment in the .tex)

- Direction A (Table 2, Finding 1, Sec. 4): `results/research/alipair_zeroshot_20260929/MAIN_CLAIM_A.md` (main_claim_A.json);
  control operations from `tables/tab_v6b_perop.tex`; medians from `tables/tab_v6b_retouch_main.tex`.
- Direction B (Table 3, Finding 2, Sec. 4): `results/research/celebdfb_v2_20260927/FAIR_cdfb.md` (fair_cdfb.py);
  AUC_c - AUC_b from `tables/tab_v6b_twosided_main.tex`; paired CIs from `docs/capstone/MAIN_CLAIMS_20261022.md`.
- Skin-only smoothing and dose response: `retouch_unified_20260929/FINDINGS.md` Addenda 38, 39 (`tables/tab_v6b_smooth38.tex`, `tab_v6b_dose.tex`).
- Exposure (Table 4, Fig. 2, Finding 3): `tables/tab_v6_p3.tex`, `tab_exposure.tex`, `tab_v6b_tradeoff_main.tex`;
  FINDINGS.md Addenda 31, 32, 33, 40; supplement_v7 S-sec:exposure (Holm p).
- Band energy (Fig. 3, Finding 4): FINDINGS.md 2026-10-18 band-energy entry (BANDENERGY.md); `bandenergy_20261018/FFPP_BAND.md`.
- BCT / recalibration (Table 5, Finding 5): `retouch_unified_20260929/BCT.md`, `RECAL_MISS.md`.
- SIC (Table 6 = tables/tab_sic.tex, Fig. 4, Finding 6): `READOUT46.md`, FINDINGS.md 2026-10-19 20:30 family table, RECAL_MISS.md, `SCE_s2.md`.
- Identity (Finding 7): `ID_REF.md`, `ICT_PROBE.md`, RECAL_MISS.md, critique appendix (1-AUC ratios computed there).
- Companion (Table 7, Sec. 4): `tables/tab_v6b_reproduce.tex` (full-model paired block), `tab_v6b_df40_main.tex`,
  `tab_v6b_seeds.tex`, READOUT46.md attribute block, `FB_OPS.md`, `tab_v6b_ar.tex`, FINDINGS Addendum 56.
- Table 1 feature cells: `docs/literature/SCOOP_CHECK_A_beautification_20261020.md`, `SCOOP_CHECK_B_methods_20261020.md`.

## Numbers / items that could not be sourced (left as \todo{} or omitted)

1. `\todo{}` in the Introduction: a citable prevalence figure for "a large share of genuine faces are beautified before
   upload" (critique R10). No source in the project files; v7 asserted it without a citation.
2. The band-energy figure caption in v7 states pooled Spearman -0.01 while FINDINGS.md (BANDENERGY.md) states +0.06 for the
   energy-above-0.25 c/px measure. v8 uses +0.06 in the text (sourced) and removed the number from the caption. Verify which
   loss definition the figure plots before submission.
3. Finding 7 "relative error grows four to ten times" uses the 1-AUC ratios computed in RESEARCH_CRITIQUE_20261021b.md
   appendix (from ID_REF.md numbers), not a result file of its own.
4. DF40 face-swap comparison (Sec. 4) has no paired interval; stated as point estimates only.
5. Routed expert (SCE): only seed 20260930 is read; SCE.md and SCE_s2.md are byte-identical. Seed 1 pending.
6. F2F+FS-only training arm (Addendum 49): named as running, no number.
7. Teaser (Fig. 1) is reused from v7 with the forgery-head-only model as one of the two "ours" rows; if that model is no
   longer in the main paper, regenerate with the three-way model's two seeds (make_fig_teaser_v7.py, swap the clipe5b row).
8. Fig. 6 (two-axis scatter) is a placeholder box with the exact data listed; not drawn.
9. Checkpoint-selection criterion sentence in Sec. 4 ("balanced criterion that penalises originals sent to the beautified
   class") paraphrases supplement S-sec:prereg; the exact rule text is there.

## Bib entries to add to refs_v6.bib (cited in main_v8.tex, currently undefined)

Verified bibliographic data from `docs/literature/SCOOP_CHECK_C_identity_20261021.md` (references 3, 4, 17, 25).

```bibtex
@inproceedings{idreveal2021,
  author    = {Cozzolino, Davide and R{\"o}ssler, Andreas and Thies, Justus and Nie{\ss}ner, Matthias and Verdoliva, Luisa},
  title     = {{ID-Reveal}: Identity-aware DeepFake Video Detection},
  booktitle = {IEEE/CVF International Conference on Computer Vision (ICCV)},
  year      = {2021},
  note      = {arXiv:2012.02512}
}
@inproceedings{ict2022,
  author    = {Dong, Xiaoyi and Bao, Jianmin and Chen, Dongdong and Zhang, Ting and Zhang, Weiming and Yu, Nenghai and Chen, Dong and Wen, Fang and Guo, Baining},
  title     = {Protecting Celebrities from DeepFake with Identity Consistency Transformer},
  booktitle = {IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)},
  pages     = {9468--9478},
  year      = {2022}
}
@article{mirabet2025,
  author  = {Mirabet-Herranz, Nelida and Galdi, Chiara and Dugelay, Jean-Luc},
  title   = {Facial Biometrics in the Social Media Era: An In-Depth Analysis of the Challenge Posed by Beautification Filters},
  journal = {IEEE Transactions on Biometrics, Behavior, and Identity Science},
  volume  = {7},
  number  = {1},
  year    = {2025}
}
@article{yin2026,
  author  = {Yin, {\todo{first names}} and Jamaluddin, {\todo{first names}}},
  title   = {Identity-Referenced Two-Stage Deepfake Detection with Consistency-Gated Fusion},
  journal = {Journal of Information System and Technology Management},
  year    = {2026},
  doi     = {10.35631/jistm.1144053},
  note    = {abstract verified via OpenAlex; full text not obtained}
}
```

The ICT author list beyond the first three is as recorded in SCOOP_CHECK_C (CVF page not re-checked); the Yin \& Jamaluddin
entry needs first names and volume/pages from the journal page (DOI resolution returned 404 on 2026-10-21).

## Style self-check (check_v8.py)

Em-dashes 0; sentence-initial adverb+comma 0; self-addressed section openers 0; repeated 6-grams (>= 3) 0; hype adjectives 0;
"X, not Y" contrasts reduced from 10 to 4 (remaining: "the label follows what changed, not the tool"; "a fix ... has to be
bought ..."; the identity prior-art sentence; "erased ... beyond the shortcut"). Abstract: 244 words, four numbers
(89-99 %, 3-22 points, 9 %, 0.87). Introduction has no digit except in citations and "seventeen"/"fifteen"/"fourteen" as words.

## 2026-10-22 (later): cut to 8 body pages, float fix, supplement_v8, build_v8.sh

Build: `sh docs/paper_v2/build_v8.sh` (main_v8, supplement_v8, main_v8, supplement_v8 on gsplat-ubuntu). Result: main_v8.pdf 9 pages
(body ends on page 8, references start on page 8 and spill to page 9), supplement_v8.pdf 33 pages. Overfull boxes left: 1.5 pt (Table
II) and 2.1 pt (supplement Table S1); none above 10 pt. Pre-cut copy: main_v8_pre_cut_20261022.tex.bak.

Cuts (no number or claim changed): Table 1 (prior-evaluation comparison) moved to the supplement as Table S4 (one pointer sentence in
Sec. II); identity subsection compressed to one paragraph plus Finding 7 (same numbers, one sentence on fusion merged); Related Work
halved (Face X-ray / LSDA sentence dropped, so refs facexray, lsda no longer cited in main); teaser and Table II captions shortened
(the native-decision 98.8 / 99.2 % now appears only in Sec. IV); two Limitations sentences compressed. Float overlap on page 4
(Table IV wider than the column) fixed with adjustbox and a shorter header; Table VI (table*) and Table VII also wrapped.
Placeholder box replaced by figs/fig_twoaxis_v8.pdf (make_fig_twoaxis_v8.py, figstyle.py house style; x = main_claim_A.json
fa_s90_at_5pct with fa_ci, y = fair_cdfb.json d_miss_beauty_only with its CI, marker area = auc_untreated).

supplement_v8.tex (from supplement_v7.tex): externaldocument main_v8, refs_v8; title updated; M- labels remapped (sec:measure ->
sec:protocol, tab:twosided -> tab:dirB, tab:tradeoff -> tab:exposure, sec:mechanism -> supplement sec:probe); S-tab:retouch added as a
second label on the full retouch table (medians). New sections: S4 comparison table; S17 SIC rule (equation from v7), bars (Table
S24 from READOUT46.md bars lines), full family (tab_sic_full), recalibration control (Table S26, RECAL_MISS.md), routed expert
(Table S27, SCE_s2.md); S18 BCT for every detector (Table S28, BCT.md); S19 identity (Tables S29-S30, ID_REF.md, ICT_PROBE.md);
S8 operation head on AR filters (FB_OPS.md). Tables generated by make_tables_v8_supp.py (tables/tab_v8_*.tex, source comment in
each). Evidence-map / explanation section kept (main Sec. V points to it).

refs_v8.bib: yin2026 author names filled from OpenAlex (Zhen Yin; Robiatul A'dawiah Jamaluddin); volume / pages not available
(DOI and journal page return 404); a stray markdown fence at the end of the file removed. Prevalence \todo in the Introduction left.
