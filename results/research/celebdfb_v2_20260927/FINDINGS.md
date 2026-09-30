# FINDINGS — Celeb-DF-B external beautification test (2026-09-27)
Libourel et al., IWBF 2024 (**cite**). 232 genuine + 232 deepfake videos, each also beautified (4 app presets) and
compressed. 32 frames/video, FF++ training crop. **v3 = Addendum 1 (bar trimming, written after v2 results);
v2 kept in `RESULTS.md`.** v3: 43,363 frames, no-face 2–3 % in every folder (v2 lost 57 % of treated frames).

## Headline (v3, `RESULTS_v3.md`)
**1. Beautification makes every published binary detector let more deepfakes through.** Escape rate
(synthesis called real, each detector at 5 % FPR on untreated real) before → after beautification:
SBI 44.3 → 79.8 % (**+35.5 pp** [30.7, 40.1]), SRM +17.0, CORE +13.8, SPSL +13.1, UCF +12.4, RECCE +11.8,
Xception +9.9, F3Net +6.8, EffB4 +3.4; median +11.8 pp. 9 / 11 significant. (Libourel reported the same direction on
video AUC for three detectors; this extends it to 11 at frame level.)
**2. Our three-way models do not.** ΔMISS: HYB-L **+1.5 [−0.3, 3.6]** (not significant), RepViT20 −11.8, RepViT40 −6.0.
**3. Accusation does not rise either**; beautified genuine faces are routed to *filter* (HYB-L 56.8 % of
real_beautified frames vs 7.4 % of untreated real).
**4. E1 holds for all three three-way models**: no threshold of any of the 11 binary detectors reaches both their FA
and MISS on the raw (beautified) plane.
**5. Untreated detection** (real vs synthesis AUC): SBI 0.875, **HYB-L 0.854**, UCF 0.841, CORE 0.821, Xception 0.811,
EffB4 0.811 … RepViT20 0.757, SBI-L (our reproduction) 0.745.

## What does not hold / must be said
- **E2 fails as written** for every three-way model — because their Δs are large and *negative* (fewer accusations,
  fewer escapes). The criterion used |Δ|; this is a wording flaw recorded before the result (Addendum 1) and not
  changed.
- **Native-rule false accusation on untreated Celeb-DF is high**: HYB-L calls 50.8 % of untreated genuine frames
  *fake* (binary detectors are held at 5 % by a threshold chosen on this very set — an oracle advantage we did not
  give ourselves). Domain gap, not a beautification effect; must be reported next to point 3.
- RepViT40 routes 41.5 % of *untreated* genuine Celeb frames to *filter* (corpus shortcut); HYB-L only 7.4 %.
- A beautified deepfake routed to *filter* (HYB-L 31.0 %) is flagged as edited but not identified as a forgery.
- `real/` = Celeb-DF-v2 Celeb-real; identities are not in FF++ training.

## Addendum (2026-09-27): per-preset breakdown and compression control
The extractor looked up fake-side presets under type "synthesis" while `annotation.csv` uses "fake"; `analyze_cdfb.py`
now maps them (no score changed). ΔMISS (pp) per preset — brown / california_dreamin / hawaii_grain / relax_you_pretty
— and compression-only:
- SBI +43.5 / +30.4 / +56.0 / +11.9; compression-only **+13.7** ⇒ beautification-attributable ≈ **+21.8** (still largest)
- UCF +19.4 / +3.2 / +41.1 / −14.2; compression +1.2
- HYB s1 +0.3 / **+10.1** / −4.8 / +0.1; s2 −1.1 / **+11.9** / −7.5 / +1.7; compression +0.9 / +1.8
- RepViT −7.5 / −5.5 / −23.0 / −11.2
**Failure case**: `california_dreamin` (warm colour grading) raises HYB's escape rate by 10–12 pp in both seeds; the
overall "+1.5, not significant" hides it. Grain-type `hawaii_grain` is the worst preset for binary detectors.
Paper claims corrected accordingly (`docs/paper_v2/main.tex`, Table `tab:preset`).
