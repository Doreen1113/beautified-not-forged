# PRE_DECLARED — eleven published detectors on the unified three-class benchmark
`ffpp_benchmark_20260925` — written before any competitor is scored. No training; official weights only.

## 1. The question
A binary detector has no symbol for "a genuine face that was beautified". The claim under test is that this is not an
implementation gap but a structural one:

> **No threshold on any published binary detector attains both a lower-or-equal false-accusation rate and a
> lower-or-equal escape rate than the three-class model.**

Falsifiable: sweep every threshold of every model. One model dominating on both axes refutes it.

## 2. Test set — the same frames for everyone
`ffpp_unified_20260925/ffpp3_test.txt`: **1,316 real / 5,304 fake / 1,316 filter**, all from the 136 held-out FF++
test videos, video-ID disjoint from every training split. The filter frames are the *same photographs* as the real
frames, beautified — so every model is scored against its own paired control, not against another corpus.

Plus the escape set: the 400-frame beautified-fake set from `eval_ffpp3.py` P4 (FF++ test fakes × eight stress
filters), identical frames for all models.

## 3. Models
`external_baselines_20260905/zoo.py`, official checkpoints and official test-time preprocessing:
Xception, EfficientNet-B4, SPSL, F3Net, UCF, RECCE, CORE, SRM (DeepfakeBench weights), SBI, UnivFD, NPR.
Ours: `ffpp3_FLAT.pth` (2.50 M, FF++-only). Every model is scored by the same driver on the same file lists; only the
model's own preprocessing differs, as its authors specify.

## 4. Metrics — matched operating point, so calibration advantages nobody
For each model, the threshold t is set on the **real** rows so that clean-real FPR = **5.0 %**. At that t:
- **FA** = beautified genuine frames (the filter rows) scored above t, i.e. called fake — *false accusation*
- **MISS** = beautified fake frames scored below t, i.e. called real — *escape*
- **clean fake recall** = FF++ fake rows above t — a sanity check that the operating point is usable
Also reported per model: AUROC(real vs fake), AUROC(real vs filter), parameters, and the full FA/MISS curve over all t.

For **ours**, the three-class model, both readings are given: its **native rule** (argmax) and the same 5 % FPR point
on its P(fake) score, so it is never given an easier rule than the baselines.

## 5. Bars (fixed now)
**B1 — dominance.** Sweeping t over its full range for each of the eleven binary models, no model attains
`FA ≤ FA_ours` **and** `MISS ≤ MISS_ours` simultaneously. Reported as the count of models that violate this; the claim
requires **0 violations**.
**B2 — margin.** At matched 5 % FPR, ours has the lowest FA of all twelve models, and its MISS is within 5 pp of the
best binary model's MISS. (A three-class model is allowed to give up a little escape performance for a large FA gain;
it is not allowed to be worse on both.)
**B3 — the mechanism is the label space, not the backbone.** Our own binary arm — same backbone, same data, same
recipe, filters merged into *real* and into *fake* (two arms, trained for this) — must also fail B1 against the
three-class model. If our binary arm dominates, the gain is not the label space and the claim is withdrawn.

**Verdicts.** SUPPORTED = B1 (0 violations) + B2 + B3. WEAK = B1 holds but B2 or B3 fails → the effect is real but
smaller or differently caused than claimed; report as such. REFUTED = any binary model dominates on both axes.

## 6. Traps
1. Matched FPR is computed on the **real** rows only, never on the filter rows, or the metric becomes circular.
2. Each competitor uses its own preprocessing exactly as published; no re-tuning, no fine-tuning, no re-calibration
   beyond the single scalar threshold every model gets equally.
3. Ours is scored through the same driver as the others, from the checkpoint the bars were read from.
4. B3's two binary arms are trained in this round (same recipe as the baseline, only the label mapping differs);
   they are controls, not candidates.
5. CIs: cluster bootstrap over **video id**, 2,000 resamples, since frames within a video are not independent.
6. Bars fixed above; addenda dated.
