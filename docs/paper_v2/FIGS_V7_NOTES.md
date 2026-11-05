# Figures v7 (2026-10-18): teaser, exposure 2x2, architecture

New files only; `main_v6b.tex` and every existing figure file are untouched. All three use the palette and type sizes of
`docs/paper_v2/figstyle.py` (the TikZ figure through `figs_tikz/style.tex`, which mirrors it). Every PNG was rendered at 300 dpi
and inspected; no overlaps or clipped text at the stated print size.

## Fig. 1 - teaser, `figs/fig_teaser_v7.{pdf,png}` (6.9 x 2.7 in), script `make_fig_teaser_v7.py`

Message: every published detector scores a skin-smoothed genuine face as more forged than the same face untouched.

* Left: three FFHQ originals and their commercial Smoothing-90 renders. Stems chosen deterministically as the first three in
  sorted order present in both folders: **17001, 17002, 17003** (`ffhq_originals/Part2/<stem>.png`,
  `FFHQ_ali_process/Smoothing_90/17000/<stem>.png`; the render folder is `index // 1000 * 1000`). Central 640 x 640 crop of
  the 1024 x 1024 aligned image (no landmark detector run).
* Right: one row per detector, 2,210 pairs each (`orig_0` vs `Smoothing_90`, paired by stem). Scores are mapped to their
  quantile among the originals (mid-rank empirical CDF), so every detector shares one 0-1 axis. The ridge (Gaussian KDE,
  reflected at 0 and 1, each row scaled to its own peak) shows **where the smoothed render lands among the untouched originals**;
  dot = median; dashed lines at the median original (0.5) and at the 5 %-FPR accusation point (0.95). The number at the right
  edge is the share of pairs in which the render scores above its own original (threshold-free; same quantity as the paper's
  "paired" column). The 5 %-FPR shares implied by the figure match the paper (e.g. CADDM 6.3 %, LAA-Net 17.2 %).
* Rows: 11 face-forgery CNNs (grey), UnivFD (generated-image detector, Okabe-Ito sky blue `#56B4E9`, a family figstyle has no
  colour for), 4 CLIP-based (figstyle CLIP), Ours binary = `clipe5b_s20260929`, Ours full = `clipe5_s20260929` (figstyle OURS,
  bold). Paper order inside each family.
* Data: `results/research/alipair_zeroshot_20260929/published_scores_<name>.npz` (`s`, `group`, `stem`) and
  `results/research/retouch_unified_20260929/ali_scores_clipe5{b,}_s20260929.npz` (`P[:, 1]`, `group`, `stem`).
* **NPR omitted** (16 published rows, not 17): its Alibaba scores exist but saturate - 40 % of the originals score exactly 1.0 and
  19 % of pairs are exact ties - so a quantile among the originals has no meaning for it; the paper already lists NPR as n/a /
  "scores everything at 1.0". Say so in the caption.
* `figs/fig_teaser_v7_diff.{pdf,png}` is the literal variant asked for (ridge of quantile(render) - quantile(original)). It is
  kept as an alternative only: that difference is bounded by 1 - quantile(original), so every detector shows the same plateau
  shape and the rows barely differ; the main file reads much more clearly. Both are produced by the same script.

## Fig. 2 - exposure 2x2, `figs/fig_exposure_v7.{pdf,png}` (3.3 x 3.2 in), script `make_fig_exposure_v7.py` (matplotlib)

* Grid: columns = forged faces receive smoothing views (no / yes), rows = genuine faces receive smoothing views (no / yes);
  cells P0 (top-left), P3 (top-right), P1 (bottom-left), P2 (bottom-right).
* Each cell: the two training views (genuine thumbnail, forged thumbnail); a class that receives smoothing views is drawn
  smoothed (two passes of `cv2.bilateralFilter(11, 70, 70)` on the 224 px thumbnail) with a sparkle badge; two bars: FA
  (accused share of Smoothing-90 renders, fake colour) and the change of MISS on strongly smoothed Celeb-DF-v2 forgeries
  (amber `#C98A00` of `style.tex`, zero marked, sign shown). P1 is framed in amber and tagged "evasion", P3 in the fake colour
  and tagged "accusation". Numbers copied from `figs_tikz/fig_exposure.tex`: FA 54.2 / 63.8 / 3.7 / 11.7 %, dMISS -16.0 / -38.5 /
  +51.2 / -26.5 pts (P0 / P3 / P1 / P2).
* Faces: genuine = `results/research/explain_vlm_20261012/ffhq_demo_edits_holdout/17083_x0.png`; forged = the Celeb-DF-B deepfake
  frame of fig_teaser_v6b (`external_data/celebdfb/frames_std32v3/synthesis/id52_id49_0000__f05.jpg`, same selection rule,
  re-implemented because importing `make_fig_teaser_v6b.py` would redraw that figure). No forgery is fabricated.
* The P2-sym box and the explanatory paragraph of the old figure are not drawn; only the one-line footer "FF++-only training,
  first seed; same architecture, data and recipe" remains. The P2-sym sentence belongs in the caption or text.

## Fig. 3 - architecture, `figs_tikz/fig_arch_v7.{tex,pdf,png}` (3.48 x 1.49 in), caption `figs_tikz/fig_arch_v7_caption.txt`

* Compiled with `sh docs/paper_v2/figs_tikz/build.sh fig_arch_v7` (tectonic on gsplat-ubuntu, PNG rendered locally).
* Two inputs (face crop x; x_s = x smoothed, dashed border, sparkle badge as in Fig. 2, "training only") -> one shared
  CLIP ViT-L/14 drawn as blocks 1, 2, ..., 24 with q k v o squares, each with a LoRA chip in the ours colour, and a frozen MLP slot;
  legend inside the box (frozen / LoRA r=16, 3.2 M trained of 306 M) -> CLS path to four thin head boxes with icons (forged z_f,
  beautified z_b, 4 operations present, 4 operation amounts) and the single label "decision P(fake) = sigma(z_f)";
  patch-token path -> linear 1024->1 -> 16 x 16 evidence map (`img/ev_grid.png`) <-> exact footprint (`img/footprint16.png`),
  BCE + Dice. Consistency: z_f(x) (solid) and z_f(x_s) (dashed) from the forged head, a brace labelled "training only", and
  `L_cons = lambda (z_f(x) - z_f(x_s))^2` on two lines. Thumbnails reused from `figs_tikz/img/` (made by `make_thumbs.py`).
* The long explanatory sentence of the old figure is in `fig_arch_v7_caption.txt` (proposed caption).

## Not done / caveats

* Fig. 1 uses a central crop, not the project's landmark crop (not needed for 1024 x 1024 FFHQ-aligned faces).
* Fig. 1 is 6.9 x 2.7 in rather than 2.6 in; 18 rows at 7.3 pt need the extra tenth of an inch.
* Fig. 3 is 3.48 in wide (IEEE column 3.5 in; it scales to 3.3 in at 95 % with 5.9 pt body text if the column is 3.3 in).
* None of the figures is referenced from `main_v6b.tex` yet; captions of Figs. 1 and 2 need rewriting around the new content
  (notes above give the quantities shown).
