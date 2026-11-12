# Figures v8b (2026-10-22): the five figures of `main_v8.tex`, redesigned

New files only. `main_v8.tex` now includes `figs/fig_{teaser,exposure,bandenergy,sic_curve,twoaxis}_v8b.pdf`; the v7 / v8
figure files and their scripts are untouched (still copied by `build_v8.sh` so that `main_v7.tex` keeps building). Every v8b
figure is produced by `make_fig_<name>_v8b.py` from the result files listed below; no number is typed into a script. The
numbers are the ones already in the paper and were not changed.

Shared style: `figstyle.py` (fonts Arial/Helvetica, 8 / 7.5 / 7 pt at final size, no top or right spines, frameless legends,
house blue `#0F4D92` for ours, vector PDF plus 300 dpi PNG) plus the new `figstyle_v8b.py`, which adds the one family colour
figstyle lacked (generated-image detectors, Okabe-Ito sky blue `#56B4E9`), one marker per family (circle / diamond / square /
star, so the families stay apart in grey print), the ordered detector registry used by Figs. 1 and 5, and the bold `(a)(b)(c)`
panel tags. Families are coloured the same way in every figure: face-forgery CNNs grey, generated-image detectors sky blue,
CLIP-based detectors pink, ours blue. Outcome colours are never used for a family: red `#D55E00` = the accusation direction,
amber `#C98A00` = the evasion direction, green = genuine.

| Figure | File | Script | Size (in) | Data |
|---|---|---|---|---|
| Fig. 1 teaser | `figs/fig_teaser_v8b.{pdf,png}` | `make_fig_teaser_v8b.py` | 7.16 x 2.75 | `alipair_zeroshot_20260929/main_claim_A.json` (`rows[*].fa_s90_at_5pct`, `fa_ci`, `paired_up`), `celebdfb_v2_20260927/fair_cdfb.json` (`[*].d_miss_beauty_only`, `ci.d_miss_beauty_only`); crops `ffhq_originals/Part2/1700{1,2,3}.png`, `FFHQ_ali_process/Smoothing_90/17000/1700{1,2,3}.png` |
| Fig. 2 exposure | `figs/fig_exposure_v8b.{pdf,png}` | `make_fig_exposure_v8b.py` | 3.5 x 3.05 | `retouch_unified_20260929/p3_readout40.json` (`[P0..P3].smoothing90_at_5fpr[0]`, `miss_rise[2][0]` = bil21), asserted equal to `smooth_evasion2.json[tag].miss_rise[2][0]`; faces as fig_exposure_v7 |
| Fig. 3 band energy | `figs/fig_bandenergy_v8b.{pdf,png}` | `make_fig_bandenergy_v8b.py` | 3.5 x 2.45 | `retouch_unified_20260929/bandenergy_20261018/bandenergy.json` (`loss_per_form.ehf0.25_view`, `family`), `fa_parsed.json` (`published[*].fa`) |
| Fig. 4 SIC family | `figs/fig_sic_curve_v8b.{pdf,png}` | `make_fig_sic_curve_v8b.py` | 3.5 x 2.7 | `retouch_unified_20260929/readout46.json` (per arm `untreated_cdf_video_vs_binary.arm/ref`, `smoothing.fl12.fa`, `.miss_rise`), `smooth38.json` (`clipe5b_s20260929.forms.fl12.fa[0]` = reference FA 84.5), `SMOOTH38.md` (published fl12 FA), `compare_sota_clipe5b_s20260929.json` (`cdf.*.pub_video`) |
| Fig. 5 two axes | `figs/fig_twoaxis_v8b.{pdf,png}` | `make_fig_twoaxis_v8b.py` | 3.5 x 2.6 | `main_claim_A.json` (x, CI), `fair_cdfb.json` (y, CI, `auc_untreated` for marker area) |

All paths under `C:\My_Project\AIGC\results\research\`.

## Fig. 1, `fig_teaser_v8b` (full width)

What it shows: the two directions of the measurement at a glance. (a) three genuine FFHQ faces, untouched and smoothed by the
commercial service (the same central 640 x 640 crops as fig_teaser_v7, stems 17001-17003 = first three present in both folders).
(b) Direction A, one row per detector: share of the 2,210 Smoothing-90 renders accused at the threshold that accuses 5 % of
the originals, dot with 95 % interval, dashed line at the 5 % floor, and at the right edge the threshold-free reading (share of
pairs in which the render scores above its own original) in grey. (c) Direction B, same rows: beautification-only miss rise on
Celeb-DF-B (points), 95 % video-cluster intervals, dashed line at zero. NPR keeps its row with the note "scores saturate (n/a)".

Why this form: the v7 teaser used a ridge plot of score quantiles, which reads as a decorative texture and needed the caption
to explain what a quantile of a quantile means. The redesign shows the two quantities the paper's two main tables report, on
the same rows, so the reader sees "high on the left, above zero on the right" for every published detector and the two blue
stars low on both. Rows are in the paper's family order with thin separators between families; names once, on the left; the
family legend once, at the top; direction headers "Direction A: accusation" / "Direction B: escape" in bold above the panels;
no panel titles otherwise. Image tiles end exactly where the dot panels end, so the three blocks share one baseline.

## Fig. 2, `fig_exposure_v8b` (column)

Same 2 x 2 as v7 (rows: genuine faces receive smoothed views no / yes; columns: forged faces receive them no / yes; P0, P3, P1,
P2). Each cell: arm tag and its description, the two training views (a class that receives smoothing views is drawn smoothed,
two passes of `cv2.bilateralFilter(11, 70, 70)`, and carries a small "smoothed" chip), then two bars with the numbers printed:
FA (red, 0-70 % scale) and dMISS (diverging about zero, -45..+55 points; amber when positive = smoothed forgeries pass, red when
negative = the arm accuses every smoothed face). P1 is framed amber and tagged "evasion", P3 framed red and tagged "accusation".
The two error directions are drawn as arrows in the footer legend (red arrow = accusation, amber arrow = evasion). The sparkle
badge, the P2-sym box and the explanatory footer of the older versions are gone; the recipe sentence lives in the caption.

## Fig. 3, `fig_bandenergy_v8b` (column)

Same two panels as `bandenergy_20261018/make_fig_bandenergy.py`: (a) texture loss per form, ordered, mean and 95 % frame
bootstrap, hollow marker for the commercial S-90 (different source images); (b) FA of every published detector on every form
against that loss, family colours and markers from `figstyle_v8b`, strip numbers matching the rows of (a). Changes: panel tags
outside the axes instead of titles, the pooled Spearman written inside (b) in the empty band between forms 4 and 5, lighter
form guide lines, the 5 % FPR line labelled in the same band, legend in one row under the figure, y-label shortened so that
the (b) tag does not touch it.

## Fig. 4, `fig_sic_curve_v8b` (column)

Same data and encoding as `make_fig_sic_curve.py` (x = untreated Celeb-DF-v2 video AUC, y = face-local 0.12 FA on a log axis,
colour = miss rise on the smoothed forgeries, numbered arms with a key column, star = forgery head only, squares = published
CLIP detectors, dashed red line = the pre-declared 15 % bar). Changes: the script now calls `figstyle.apply()` (the old one did
not, so its fonts and spines differed from every other figure), the reference FA is read from `smooth38.json` instead of being
typed, labels are placed so that none crosses another or the bar line, the key is headed "trained models", the colour bar is
narrower, the published detectors use the CLIP family colour and marker of the other figures.

## Fig. 5, `fig_twoaxis_v8b` (column)

Same scatter as `make_fig_twoaxis_v8.py`. Changes: interval bars at 30 % opacity so the markers carry the figure; the region
left of the 5 % floor shaded; both guide lines labelled on the axes ("5% FPR floor", "no miss rise"); our two seeds as larger
stars with hand-placed bold labels; all other labels placed by `adjustText` (repelled from markers, from each other and from
the two fixed labels, thin grey leaders where a label had to move); family legend with the shared markers; axis titles name the
directions.

## Reference figures studied

Index `qwdwqfwq/topconf-paper-figure-gallery` (`data/figures.json`), five Figure-1s on detection / forensics / robustness,
downloaded to the session scratchpad (`figref/`): NeurIPS 2025 "AI-Generated Video Detection via Perceptual Straightening"
(`neurips2025-0082`), NeurIPS 2025 "Dual Data Alignment Makes AI-Generated Image Detector Easier Generalizable"
(`neurips2025-0410`), NeurIPS 2025 "PolyJuice: Black-Box, Universal Red Teaming for Synthetic Image Detectors"
(`neurips2025-1145`), ICLR 2024 "Poisoned Forgery Face: Backdoor Attacks on Face Forgery Detection" (`iclr2024-0807`), ICML 2026
"Suppress and Diversify: Refining Robust Pathways for Corruption Robustness" (`icml2026-0466`).

What makes them work, and what was carried over: every one reads left to right as input, mechanism, outcome, with real
photographs as the anchor on the left and a data panel (a score distribution, a scatter, a radar) as the evidence on the right;
two or three hues at most, one of them reserved for the class or method the paper is about (red for forged / attack, blue or
green for genuine), everything else grey; large sans-serif labels of a single size, a one-line takeaway per panel instead of
titles, equal panel heights and aligned baselines, and (a)(b) tags set outside the panels. The teaser here follows that
grammar: photographs left, the accusation panel in the middle, the escape panel right, one legend, one highlighted colour for
ours, no boxes around text.

## Build and check

`sh docs/paper_v2/build_v8.sh` (tectonic on gsplat-ubuntu) compiles `main_v8.tex` and `supplement_v8.tex` and copies the PDFs
back; the scp list carries the five v8b PDFs. If `main_v8.pdf` is open in a viewer on Windows the copy cannot overwrite it and
the script writes `main_v8_new.pdf` next to it (added 2026-10-22). Pages 1, 4, 5, 6 and 7 of the built PDF were rendered with
PyMuPDF and inspected after each of three rounds; the body ends on page 8 (references start on page 8), so the 8-page limit
holds. Known small things: the `(b)` tag of Fig. 1 sits far from its panel because the row names occupy that space; Fig. 4
keeps the numbered key (nine arms crowd the 0.90-0.95 band, direct labels did not fit).

## Fig. 2, `fig_method_v8b` (full width, method overview; added 2026-10-22)

Files: `figs_tikz/fig_method_v8b.tex` (TikZ, shared `figs_tikz/style.tex`: TeX Gyre Heros, 7 / 6.6 pt at final size, house blue
`#0F4D92` for ours, vermillion `#D55E00` = accusation, amber `#C98A00` = escape, greys otherwise), image assets by
`make_fig_method_v8b.py` (`figs_tikz/img/m8_*.png`), compiled with `sh docs/paper_v2/figs_tikz/build.sh fig_method_v8b`, copied to
`figs/fig_method_v8b.{pdf,png}` with `python docs/paper_v2/make_fig_method_v8b.py --copy`. Size 7.13 x 2.99 in. In `main_v8.tex`
it is `figure*` placed at the start of Sec. I, so it lands at the top of page 2 (`\label{fig:method}`), and Sec. IV opens with a
"System and training recipe" paragraph that describes exactly what (b) draws.

What it shows. (a) Measurement protocol, read left to right: three sources (retouching pair FFHQ 17005 original / Smoothing-90,
the first stem after the three of Fig. 1 present in both folders, same crop; Celeb-DF-B `id10_id11_0003__f05` untreated deepfake /
app preset; scripted smoothing as text) feed one block "17 published detectors" (11 / 4 / 2 + ours, 2 seeds), whose scores pass
one threshold node tau into the two readouts A (accusation, red) and B (escape, amber); the rule is spelled out once under them.
A strip at the bottom shows the 2 x 2 exposure design of Sec. III-C with P3 coloured as A and P1 as B. (b) Companion detector:
input (held-out part edit `ffpp_partedit/test/donor/682__f0867__nose.jpg`) into a CLIP ViT-L/14 drawn as blocks with a frozen
mark and blue LoRA chips, CLS token into the forged / beautified head (blue, the only head the decision reads) and the auxiliary
operation head (grey), patch tokens into the evidence head; outputs are the three class probabilities written from f and b
and the 16 x 16 evidence map of the main model (`clipe5_s20260929`, computed by the script, cached in
`figs/fig_method_v8b_ev.npz`; P(fake) = 1.00 on this item). Training-pool strip: one real training image per class and the
counts, with the recipe arrow "half beautified on top".

Facts checked against the sources before drawing:

| Drawn | Source |
|---|---|
| 2,210 pairs; 232 + 232 videos; 7 scripted forms; 11 CNN / 4 CLIP / 2 generated-image detectors; 5 % FPR on untreated genuine of the same source | `main_v8.tex` Sec. II, `docs/capstone/MAIN_CLAIMS_20261022.md` |
| P0..P3 cells, P1 = genuine-only smoothing (evasion), P3 = forged-only (accusation) | `main_v8.tex` Sec. III-C, `fig_exposure_v8b` |
| frozen ViT-L/14, LoRA r = 16 on q/k/v/out of all 24 blocks, 3.2 M of 306 M trained | `train_ru_clip.py` (`RUCLIP`, `LoRALinear`), log "trainable 3.16 M", paper Sec. IV |
| head `fz` = 2 logits on the pooled CLS feature; joint (real, fake, beautified) = ((1-f)(1-b), f, (1-f)b); `pres` 4 + `q` 4; `ev` linear 1024 -> 1 on 256 patch tokens = 16 x 16 | `train_ru5.py` `RUCLIP5.forward` |
| genuine: FF++ c23 frames 41,512, FFHQ 7,015 (train; + 816 val = the paper's 7,831) | `manifest_train.tsv` / `manifest_val.tsv` / `manifest_stats.json` |
| forged: FF++ forgeries 41,526, part-level edits 61,510, self-blends built online | `manifest_train.tsv`; `train_ru_clipe5_s20260929.log` "parts 61,510" |
| beautified: vendor renders 18,734 (Tencent 6,924 + Megvii 11,810), single operations 50,112, scripted ops and 14 colour filters on FF++ 41,512, colour grading online | `manifest_train.tsv`; the log's "single 50,112" is the cleaned set the loader uses (73,952 rows in the manifest before cleaning) |
| one genuine, one forged, one beautified item per step from one genuine frame; forged item beautified on top (self-blend and observed forgery p = 0.5, part edit 0.3 colour only, commercial edit on a self-blend always; about half overall) | `train_ru5.py` `RUData5.__getitem__` |

Space: the figure and the recipe paragraph pushed the conclusion onto page 9, so `fig_bandenergy_v8b` and `fig_sic_curve_v8b` moved
to the supplement (Figs. S-`fig:bandenergy`, new section "Texture loss and accusation, every form"; S-`fig:siccurve`, top of the
SIC section). The main text now points to them ("supplement, Fig. ..."); no findings text was cut and no number changed. After
the move the body ends on page 8 and the references start on page 8.

Review rounds: (1) first draft at 7.65 in wide with overflowing labels, serif digits from math mode, overlapping legend and
token labels; (2) widths rebalanced, labels shortened, math replaced by text italics; (3) grid labels and detector box fixed.
Known small things: the "11 face-forgery CNNs" line sits close to the right edge of its box; the tile images are small (about
0.4 in) by design.
