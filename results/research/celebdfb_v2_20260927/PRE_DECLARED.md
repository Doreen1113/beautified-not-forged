# PRE_DECLARED — Celeb-DF-B external beautification test, crop-consistent (v2)
`celebdfb_v2_20260927` — written 2026-09-27 before any frame of this round is extracted or scored.

## 1. Why
Celeb-DF-B (Libourel et al., IWBF 2024; **must be cited**) is the only third-party set that beautifies genuine and
deepfake videos with the same presets: exactly our two problems (beautified genuine → fake; beautified fake → real).
The new FF++-only line has never been scored on it. The 2026-09-03 frames (`celebdfb_external_20260903`) use YuNet
padding 0.2, which does not match the FF++ training extractor; the 2026-09-27 Celeb-DF-v2 diagnosis showed crop
mismatch costs 1–2 AUC points, so those frames are not reused. The 2026-09-05 retraction (raw ASR is meaningless when
untreated real frames are already called fake 87.7 % of the time) fixes the primary metric below.

## 2. Frames
All 6 folders × 232 videos (`real`, `real_beautified`, `real_compressed`, `synthesis`, `synthesis_beautified`,
`synthesis_compressed`). 32 uniformly spaced frame indices per video, 10–90 % of its length (the FF++ extractor's rule);
`extract_ffpp_protocol_frames.detect_and_crop` run **independently on every frame of every folder** (MediaPipe landmark
hull, MARGIN 0.35, JPEG q90) — what any deployed detector would receive. No-face frames are counted and skipped.
Held-out only: never trained on, never used to select a checkpoint, threshold or arm (`PROVENANCE.md`).

## 3. Metrics (fixed now)
Per model, frame-level, video-cluster bootstrap 95 % CIs (1,000 resamples, seed 1):
- **Protocol check** — AUC of P(fake), `real` vs `synthesis` (untreated).
- **Primary (paired, beautification-caused)**:
  - **ΔFA** = rate(`real_beautified` called fake) − rate(`real` called fake)
  - **ΔMISS** = rate(`synthesis_beautified` called real) − rate(`synthesis` called real)
  Compression analogues (ΔFA_c, ΔMISS_c) as the non-beautification control.
- **Raw plane** — FA = `real_beautified` called fake; MISS = `synthesis_beautified` called real.
Decision rules: three-way models use their native argmax (routed to *filter* = neither accused nor escaped; the
filter-routing rate is reported). Binary detectors: primary metrics at the threshold giving **5 % FPR on untreated
`real`**, which gives every binary detector the untreated operating point most favourable to it; the raw-plane
dominance test uses the full threshold sweep as in `ffpp_benchmark_20260925`.

## 4. Models
Ours: BASE (RepViT-M0.9 20 ep), RepViT 40 ep, HYB-L (sbiscale), and any sbiscale arm finished at scoring time.
Published: the 11 detectors of `ffpp_benchmark_20260925` with their official weights and preprocessing.

## 5. Claims this round can support (fixed now)
- **E1 (external frontier)**: a three-way model is not dominated on the raw (FA, MISS) plane by any threshold of any
  of the 11 binary detectors.
- **E2 (beautification sensitivity)**: the model's |ΔFA| and |ΔMISS| are both ≤ the median of the 11 binary
  detectors' values (at their 5 %-FPR point).
Either may fail; both are reported whatever happens. No threshold, bar or metric is changed after scoring.

## 6. Known limits written now
- Celeb-DF identities appear in no FF++ training data, but untreated Celeb-DF-v2 is a known weak spot for our line
  (AUC ~0.70–0.76); raw FA will be high for every FF++-trained model, which is why ΔFA is primary.
- `real/` is byte-identical to Celeb-DF-v2 Celeb-real (PROVENANCE); it overlaps Celeb-DF-v2 test videos, which is
  fine for a held-out test but means the untreated AUC is not an independent Celeb-DF-v2 measurement.

## Addendum 1 (2026-09-27) — written AFTER the v2 results were seen
**Observation**: v2 lost 57 % of frames in every treated folder (real_beautified 4,260 no-face vs real 212). Cause:
Celeb-DF-B treated videos are re-framed to portrait (e.g. 942×500 → 942×1674) with filter-tinted bars; MediaPipe's
landmarker misses the small face. Loss depends on the source aspect ratio, so treated and untreated subsets differ
in *which videos* they contain — the paired deltas of §3 compare unequal populations.
**Fix (v3)**: before `detect_and_crop`, trim rows/columns whose grey-level std < 10 (uniform bars), applied to all six
folders identically (`extract_cdfb_v3.py`). Face pixels are untouched. Metrics, models, rules and claims E1/E2 are
unchanged. **Both v2 and v3 are reported**; because this addendum follows the results, v3 is labelled as such.
**Known wording flaw in E2 (not changed)**: E2 compares |ΔFA|, |ΔMISS|; a large *negative* Δ (beautification lowering
accusation or escape) counts against it. E2 is evaluated exactly as written and the sign is reported next to it.
