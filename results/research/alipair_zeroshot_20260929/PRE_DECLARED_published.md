# ALIPAIR-PUBLISHED-20260929 — published binary detectors on the Alibaba commercial-retouching pairs

**Question (descriptive, no model selection):** do published face-forgery detectors accuse commercially retouched genuine
faces? Same 2,210 FFHQ originals and 26,519 Alibaba renders (4 operations × 3 levels) as `results.json`; same FF++-style
crop (MediaPipe hull + 35 %, box computed on the original and shared by the pair); crops written once as PNG and fed to
every detector through its official preprocessing (`external_baselines_20260905/zoo.py`).

**Detectors:** Xception, EfficientNet-B4, F3Net, SPSL, UCF, RECCE, CORE, SRM (DeepfakeBench weights), SBI (official), UnivFD,
NPR. All FF++-trained except UnivFD/NPR (generic AIGI detectors, reported for completeness).

**Metrics (fixed now, before any detector is scored):**
- Operating point favourable to each binary detector: threshold t_d = 95th percentile of its P(fake) on the **untouched
  originals themselves** (5 % FPR on this test set). Report retouched → fake at t_d, per operation × level and pooled.
- Native threshold 0.5: originals → fake and retouched → fake.
- AUROC of P(fake), retouched vs originals (does retouching push the score toward fake?), and paired rate
  P(score(retouched) > score(original)).
- Our models on the same pairs, from the stored scores (`ali_scores_*.npz`, `probs_*.npz`): native argmax (as reported),
  and the same 5 %-FPR-on-originals rule applied to their P(fake), so every row is compared on one footing.

No bar: this is a baseline characterisation. Its result does not change any design (Alibaba closed for design decisions).
