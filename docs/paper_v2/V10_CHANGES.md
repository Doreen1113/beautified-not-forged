# Paper v10 (2026-10-28): main_v10.tex, main_v10j.tex, supplement_v10.tex

Pipeline from v9 (every step is an exact-string script that aborts if a target is not found once; v9 files untouched):
1. `make_v10_humanize.py`: main_v9 -> main_v10, the 34 wording-only items of `HUMANIZER_AUDIT_V9_20261028.md`
   (academic-humanizer skill, audit mode). Cite keys, refs, labels, numbers and source comments verified identical.
2. `make_v10_review.py`: the pre-submission-reviewer findings of `REVIEW_V9_20261028.md` (0 CRITICAL, 9 MAJOR, 16 MINOR, 6/10):
   D1-1 reproduction contradiction (Sec. II now says fifteen of seventeen reproduce; Effort and DFD-HR used as released);
   D1-2 the sentence swallowed by a % comment on p. 8; D1-3 "(Addendum 56)" -> Sec. S-ar; D1-4 "every published detector" ->
   "every one of the seventeen we scored", "the one channel" -> "the one channel we tested" (abstract, Finding 7);
   D1-5 Table I caption names the training affinity (sister services of the same RetouchingFFHQ release, more data) and
   defines the bold, Sec. II says the same next to "No model was trained on this service"; D1-6 Table II bold restricted to AUC;
   D1-7 identity prior art extended with Identity-Driven DeepFake Detection (arXiv 2012.03930) and VIPGuard (arXiv 2505.19582),
   both verified on arXiv and added to refs_v8.bib; D1-8 Related Work opened with a leading sentence and split into four
   paragraphs, Sec. III-F split at the routed expert and at "The loss"; D1-10 "to all four cells"; D1-11 JPEG-view claim
   pointed at Sec. S-chain (P0 trains with blur and JPEG); D1-12 Concas et al. credited for their attribution; D1-13 running
   example returned to after Finding 2; D2-1 topic sentence of the AR paragraph; D2-4 "two of the four predictions held";
   D3-1..7 grammar items; D4-1 Fig. 2 and Fig. 5 referenced before they appear; D4-3 caption colour; D4-6 unused macros
   removed; D5-1 finding-first captions for Figs. 3 and 5.
   Not applied: D1-9 (venue form, see main_v10j below; repository anonymisation is the author's), D1-14 (abstract challenge
   sentence, page budget), D5-2 (Fig. 2 formula strip size, TikZ), D5-4 (Fig. 4 thumbnails).
3. `make_v10_figs.py`: Fig. 1 replaced by `figs/fig_teaser_v9.pdf` (`make_fig_teaser_v9.py`), a motivated example with real
   scores: FFHQ 17003 original vs Smoothing-90 render, and Celeb-DF-B id17_id35_0000 as recorded vs app preset, four CLIP
   detectors, each at its own 5 %-FPR threshold. The seventeen-detector dot panels of the old Fig. 1 are now Fig. 3
   (`figs/fig_dirs_v9.pdf`, `make_fig_dirs_v9.py`) in Sec. III-B. Fig. 5 is `fig_twoaxis_v10` (one marker size, stronger label
   repulsion, `make_fig_twoaxis_v10.py`). `make_tab_sic.py` now prints every negative cell with a true minus.
4. `main_v10j.tex`: the same text under `\documentclass[journal]{IEEEtran}` with Index Terms (TIFS form). `supplement_v10.tex`
   = supplement_v9 with the cross-reference target changed.

5. Figures (later the same day): Fig. 2 is `fig_method_v10` (figs_tikz/fig_method_v10.tex: 7.2 / 6.8 pt text, formula strip
   in ink; REVIEW_V9 D5-2); Fig. 4 is `fig_exposure_v10` (`make_fig_exposure_v10.py`: the thumbnails that were not visibly
   smoother are replaced by "clean only / smoothed views" chips and taller bars; D5-4).
6. Three files, one text: `main_v10.tex` (conference class, full text, 10 pages, body spills to p. 9), `main_v10j.tex`
   (`make_v10_journal.py`: journal class, Index Terms, author placeholder block for the single-blind venue, the abstract
   challenge sentence of D1-14) and `main_v10c.tex` (`make_v10_conf.py`: the IJCB cut, body ends exactly at the foot of p. 8;
   the seventeen-detector dot figure is dropped there because Tables I-II carry the numbers, and twelve prose / caption
   shortenings are listed in the script; no number changes).
7. Supplement S03 ruling applied (Table S-labels): "Age or gender editing" = forged (review if only texture changes);
   "Appearance-only attribute edit (pale skin, make-up by a generator)" = beautified. Adjudicated by the assistant under the
   standing authorisation; the authors may overrule.
8. arXiv package `arxiv_v10_pkg/` from `arxiv_v10/` (journal text, fontspec replaced by newtxtext, compiled with tectonic;
   see the v9 note on pdflatex).

9. Second-round review (`REVIEW_V10_20261028.md`: 0 CRITICAL / 3 MAJOR / 12 MINOR, 8/10) applied by `make_v10_round2.py`:
   MAJOR 1 the Sec. II reproduction sentence now states what Table S3 shows (eight CNNs within 0.035 frame AUC, Forensics
   Adapter and GenD reproduce their video AUC, CADDM and LAA-Net within 0.011 on their own crops, Effort and DFD-HR 0.02-0.03
   short, SBI / UnivFD / NPR no comparable number); MAJOR 2 every "Addendum N" and result-file name in the supplement replaced
   by the released-repository convention stated once at the top (small capitals = result file); MAJOR 3 Table II bolds 0.883
   (seed 2) and Table I bolds both "Ours" row names with no bold numbers. MINORs: Finding 1 names the NPR exception; "close to
   the 5 % floor" + comma; Concas attribution quoted; Sec. IV opening no longer restates Finding 6; present tense in Sec. III-G;
   EffNet-B4 expanded in the Fig. 5 caption; Fig. 1 "true class" labels in ink; Table S3 moved into the journal body
   (`main_v10j`, now 11 pages). `\oursB`/`\oursF` stay defined in the main file because xr-hyper reads supplement captions
   that use them (removing them breaks the build). Conference cut re-trimmed: body ends at the foot of p. 8, references start
   at the top of p. 9.

10. Round-3 polish (`make_v10_round3.py` and edits): fontspec replaced by `newtxtext` in main_v10 and supplement_v10 (every
    build is now pdfLaTeX-compatible; page ends re-checked: conference body still ends at the foot of p. 8); the hard-coded
    "Sec. III-C" removed from the Fig. 2 artwork; Finding 6 and Finding 7 split into two sentences each; the Sources, SIC and
    Both-axes paragraphs split at their seams; in the journal twin Fig. 1 is an ordinary `figure*` after the abstract and
    Tables S3 and S4 are in the body (`\cmark`/`\xmark` defined there for S4). Third-round review: `REVIEW_V10_R3_20261028.md`.

11. Round-3 review (`REVIEW_V10_R3_20261028.md`: 0 / 1 / 9, 9/10) applied by `make_v10_round4.py`: the supplement now has
    three twins (`supplement_v10`, `supplement_v10c`, `supplement_v10j`) so that each paper variant's cross-references resolve
    against its own file (the one MAJOR); the journal supplement replaces Tables S3/S4 by stubs pointing at the paper's
    Tables I/II; CADDM / LAA-Net check pointed at Sec. S-baselines and the long sentence split; release sentences name the
    per-detector result files and the pre-registration log; "Operation scores." paragraph lead; SIC sentence rephrased;
    "which" -> "that"; "--" legends in two captions; " ," residue and the internal names clipe7 / clipe5M removed from the
    supplement and Table S10; Fig. 1 has one shared 7 pt note. `build_v10_all.sh` builds the three pairs. Fourth-round review:
    `REVIEW_V10_R4_20261028.md`.

12. Round-4 review (`REVIEW_V10_R4_20261028.md`: 0 / 0 / 7, 9/10, "ready to submit after half a day") applied by
    `make_v10_round5.py` (now the step that writes the supplement twins): stray spaces before punctuation removed; Tables S24 /
    S25 carry descriptive row names instead of checkpoint keys; journal supplement references to the moved tables point at the
    paper; stub grammar; abstract challenge sentence made parallel (make_v10_journal.py). Fifth-round confirmation:
    `REVIEW_V10_R5_20261028.md`.

13. Round-5 review (`REVIEW_V10_R5_20261028.md`: 0 / 0 / 5, 9/10) applied by `make_v10_round6.py`: "(am. 4/5)" removed from
    Table S24; abstract shortened (225 words in the master, about 250 in the journal twin with its challenge sentence);
    "Table II compares this protocol with ..."; "still calls 94.8 % ... when the face is greyed out". Build order for any
    later change: make_v10_round*.py (in place) -> make_v10_round5.py (supplement twins) -> make_v10_conf.py ->
    make_v10_journal.py -> build_v10_all.sh -> arXiv sync. Sixth-round confirmation: `REVIEW_V10_R6_20261028.md`.

14. Round-6 review (`REVIEW_V10_R6_20261028.md`: 0 / 0 / 4, 9/10, "ready to submit after half an hour") applied by
    `make_v10_round7.py`: abstract 214 words in the master and 242 in the journal twin ("Fifteen of the seventeen", "Controlled
    training arms show that"); the IJCB CORE sentence carries its object again ("still accuses 54.8 % of the Smoothing-90
    renders"); three further IJCB-only shortenings (conclusion release sentence, Finding 2 tail, calibration-renders sentence)
    keep the body on p. 8 with the references starting on p. 8. Final state: every build clean (?? 0, Addendum 0, clipe 0,
    (am. 0); six review rounds, the last three with 0 MAJOR.

Open before submission: real author names (journal placeholder and arXiv), repository anonymisation (IJCB).

## Step 15 (2026-10-29): round 8, Addendum 63/64 closures in Limitations
`make_v10_round8.py` adds two sentences (one in the IJCB cut) to "Limitations and What We No Longer Claim" in main_v10, main_v10c
and main_v10j: the beautification-aware fusion moves misses into false alarms (CDFB_GATE.md), and the rPPG pulse has no
separation on Celeb-DF because the swaps inherit the driving video's pulse (CDFB_RPPG.md). Pre-registered reading rule of
Add. 64 ("(1) fails -> one sentence in the limitations"). Rebuilt all six PDFs (build_v10_all.sh): main_v10 10 pp (refs p9),
main_v10c 10 pp with the body ending on p. 8 (refs at the top of p. 9), main_v10j 11 pp; no undefined references. arXiv sources
re-synced from the journal pair (arxiv_v10/, externaldocument -> supplement_v10), rebuilt, tarballs repacked
(arxiv_v10_pkg/); ?? count 0 in both.

## Step 16 (2026-10-29): round 9, Addenda 65/68/69 (reference-conditioned beautification) in the identity subsection
`make_v10_round9.py` adds one paragraph after Finding 7 in main_v10 and main_v10j: a reference of the claimed person does not
catch the beautification itself (ICC 0.14 for our beautified score, 0.12-0.46 texture detectors, 0.06-0.32 skin texture and
colour; preset-only gain -0.002 [-0.015, 0.011]); face width is identity-stable (ICC 0.66) and gains +0.092 [0.067, 0.116]
on genuine videos narrowed by 2.25 % (short of the pre-declared +0.10); a 3DMM fit registers 0.2 % of the narrowing. Sources:
results/research/refcond_20261029/{REFCOND_65,GEO68,GEO3D_69}.md. Two bib entries added to refs_v8.bib and checked against
IEEE Xplore / DOAJ and dblp (rathgeb2020diff, tddfav2). The IJCB cut (main_v10c) carries a source comment only: the sentence
pushed its conclusion onto p. 9. Build: main_v10 11 pp (refs p9), main_v10c 10 pp with refs at the top of p. 9, main_v10j
11 pp (refs p10); ?? 0 in all three. arXiv sources not yet re-synced (waiting for the Addendum 67 readout).
