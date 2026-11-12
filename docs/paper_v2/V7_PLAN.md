# v7 plan: one claim, three contributions (written 2026-10-18 02:50, before the SIC readout)

## The one sentence
Skin smoothing is a shortcut cue shared by every published deepfake detector; it comes from which class sees smoothing
during training; a class-symmetric smoothing view with a forgery-logit consistency loss (SIC) removes it without giving up
detection.

The third clause is conditional on Addendum 46 bars (readout46.py). If SIC fails a bar, the clause becomes "the sign of the
error is set by training exposure and no exposure alone removes the accusation; we release the benchmark" and the paper is a
measurement + mechanism paper (target IJCB / workshop, not CVPR main).

## Contributions (replace the three bullets in the Introduction)
1. **Finding.** 17 published detectors, 6 beautification sources, one rule. Every detector scores a skin-smoothed genuine
   face above the same face untouched (15/17 in 89–99 % of pairs); smoothing the skin alone suffices; the forgery logit of the
   CLIP detectors grows with smoothing strength. Fig. 1.
2. **Cause.** Holding architecture, data and recipe fixed, the class that receives smoothing views sets the sign of the error
   (2×2 exposure arms, three seeds on the key cells): genuine-only views let 96–100 % of smoothed forgeries through (an
   evasion route), forged-only views accuse smoothed genuine faces, symmetric views sit in between. Fig. 2.
3. **Method (SIC).** One smoothing operator drawn identically for both classes plus a paired consistency term on the forgery
   logit. Bars: skin-smoothing FA ≤ 15 %, miss rise ≤ P0 + 5, untreated AUC within CI of the binary control, DF40 within
   bars. Fig. 3, Tab. SIC.
4. **Benchmark release** (benchmark_release/): sources, one-rule scorer, paired reader.

## Outline (sections, each with one figure or one table, no number in prose that is not in a table)
1 Introduction (Fig. 1 teaser)
2 Related work (shorten to 0.5 col: beautification vs detectors; shortcut learning; class-dependent augmentation)
3 Problem and rule (Fig. protocol replaced by a half-column schematic; Tab. boundary cases stays)
4 Finding: every detector accuses smoothing (Tab. one-rule 17×6 heat table; dose response folded into Fig. 1 or supplement)
5 Cause: exposure sets the sign (Fig. 2; Tab. arms per seed)
6 Method: SIC (Fig. 3 arch; Tab. SIC vs binary control vs P2-sym on the six bars, two seeds)
7 Untreated detection (Tab. CDFv2 / DFD / DF40 vs SOTA; one paragraph)
8 Limitations (AR renders still accused unless SIC fixes them; reenactment; single-vendor ops)
9 Conclusion
Supplement: everything else (vendor per-op, evidence maps, restoration, negative results, VLM).

## Numbers that leave the main text
Abstract: at most four numbers (17 detectors; 15/17 at 89–99 %; FA before/after SIC; untreated AUC unchanged).
Intro: no number except "seventeen".
Sections 4–7: numbers only inside tables and figure captions.

## Pending inputs
- READOUT46.md (clipe5z s1, clipe5bz s1, s2 of each, λ=0 control). Chain: add46_chain.log.
- Fig. 1/2/3 v7 (agent in progress; FIGS_V7_NOTES.md).
