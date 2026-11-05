# Paper v9 (2026-10-28): main_v9.tex, supplement_v9.tex

Generated from main_v8.tex / supplement_v8.tex by `make_v9_main.py` and `make_v9_supp.py` (every replacement is an exact
string match; the scripts fail if a target is not found exactly once). v8 files are untouched. Build: `sh build_v9.sh`
(tectonic on gsplat-ubuntu). Main text 8 body pages + references (10 pages total); supplement 36 pages.

## What changed against v8

### Consistency audit (`docs/CONSISTENCY_AUDIT_20261023.md`) applied
M01-M04 (abstract, contribution 4, "Both axes", conclusion): "only model low on both axes" removed; CADDM named as lower on
both raw axes; the published-detector comparison is written as an audit reference; the controlled comparison is P0 vs P2 and
the same-data forgery-head-only control. M05-M07 (abstract, contribution 2, Sec. III-D title and Finding 4): the cue is "a face
smoother than its own context", with the Addendum 57 ring / whole-crop numbers. M08 (FF++ origin): Addendum 49 result written
in, origin claim withdrawn. M09 (related work), M10 (sources sentence), M11 (release sentence: manifests, not sources),
M12 (opening example and "fifteen of seventeen"), M13 ("fourteen of them"), M14 (18.2 % attributed to the multi-operation arm),
M17 ("Four are real" + the 16.6 / 16.1 % beautified-class escape), M18 (what a detector must do), M19 (GPUPixel in the
limitations), M20 ("Four claims withdrawn" + the FF++ origin), M21 (SCE both seeds), M22 (Fig. 1 caption cross-reference),
M23 ("at the strongest level" removed), M24 ("eye enlarging", "app preset"), M25 (source comment). M15/M16 were already applied
in v8 (tab_sic.tex regenerated on 2026-10-23).
Supplement: S02 (new sections for Addenda 54, 49 and 62), S04, S05, S06, S07 (`\textsc{filter}` -> "the beautified class"),
S08 (SCE seed 1), S09 (Fig. S caption). S03 (age / attribute editing row) is left as in v8: it needs the author's ruling.

### New results written in
- Addendum 61 (CTX38.md): test-time context matching, killed; one sentence in Sec. III-F and the supplement section written on
  2026-10-27 (Sec. S "The face against its context"), whose frame source and ring description were corrected (Celeb-DF-v2 test
  frames, not Celeb-DF-B; band one tenth of the jaw width; ring range 7-51 % with CLIP detectors and SBI at 22-51 %).
- Addendum 62 (CDFB_ID.md): identity under real app presets. Finding 7 rewritten around it; abstract and contributions
  updated; new supplement section and `tables/tab_v9_cdfbid.tex` (generated from CDFB_ID.md). Predictions (1)(2) pass,
  (3)(4) fail; no fusion method is claimed.
- Addendum 54 (GPX38.md): GPUPixel; limitations paragraph and supplement section.
- Addendum 49: supplement section; Finding 4 paragraph.
- Addendum 48 seed 1 (SCE_s1.md): supplement routed-expert paragraph.

### Removed from the main text to stay at 8 body pages
Table VI of v8 (companion vs CLIP detectors, untreated) -> numbers kept in one sentence, table remains in the supplement as
Table S-reproduce. The "five properties" paragraph of the introduction, the dose sentences of Sec. III-A, the training-data
sentence of Sec. IV, the AR numbers in Sec. V, and the conclusion were shortened. No number was changed by the cuts.

### Other
- `refs_v8.bib` yin2026: volume 11, number 44, page 904 filled from Crossref (2026-10-28).
- The prevalence `\todo` in the introduction is resolved by not claiming a prevalence (no citable source).

## arXiv variant (`arxiv_v9/`, packages in `arxiv_v9_pkg/`)
`arxiv_v9/main_v9.tex` and `supplement_v9.tex` are the v9 sources with `fontspec` + `texgyretermes` replaced by
`\usepackage[T1]{fontenc}\usepackage{newtxtext}` (scratch script `arxiv_fonts.py`; `newtxmath` was dropped because it clashes
with `amssymb`), so they compile with pdflatex, which is what arXiv runs. They were compiled with tectonic (XeTeX engine, same
TeX Live packages) on gsplat-ubuntu: no errors, no undefined references, same page counts (10 / 36). A real pdflatex run was
not possible here (the local MiKTeX is missing DLLs; conda's texlive-core has no LaTeX packages), so the first arXiv upload
should be checked in arXiv's own log. `arxiv_main_v9.tar.gz` holds main_v9.tex, main_v9.bbl, tables/, figs/;
`arxiv_supplement_v9.tar.gz` adds supplement_v9.tex, its .bbl and main_v9.aux (needed by xr-hyper for the M- references;
if arXiv strips .aux, the supplement's cross-references to the paper print as ??).

## Still open before submission
- S03 ruling (age / attribute editing label).
- Anonymisation of the GitHub repository and of the released manifests; arXiv version needs author names.
- The third seed of the main model and Addendum 48 are not in the paper beyond what is listed above.
