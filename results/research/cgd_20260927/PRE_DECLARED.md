# PRE_DECLARED — Counterfactual-Grounded Detection (CGD)
`cgd_20260927` — written 2026-09-27 before any CGD model is trained. This is the method line for the paper; the
frontier / Celeb-DF-B results stand on their own and do not depend on it.

## 1. The idea (what is new)
Every edited training image in our corpus has a **pixel-aligned counterfactual**: the unedited frame it was made from.
For scripted filters, self-blends and the new part-level edits (§3) the edit mask is **exact**. Existing detectors
throw this away and explain themselves post hoc (Grad-CAM), which we showed is uninformative (centre prior) and
which cannot be verified. CGD uses the counterfactual **as a training signal for the explanation itself**:

* **Evidence head** $\hat m = g(f(x)) \in [0,1]^{H'\times W'}$ predicts the edited region (low-res mask).
* **Restoration-consistency loss.** Build two counterfactual images by soft compositing with the *predicted* mask,
  $x^{\uparrow} = (1-\hat m)\odot x + \hat m\odot x_0$ (predicted region restored to the original $x_0$) and
  $x^{\downarrow} = \hat m\odot x + (1-\hat m)\odot x_0$ (everything *except* the predicted region restored).
  Require $p_{y}(x^{\uparrow})$ to fall below $\tau$ (the edit is gone once the claimed region is undone) and
  $p_{y}(x^{\downarrow})$ to stay above $p_y(x)-\delta$ (the claimed region alone carries the decision).
  $\hat m$ receives gradient through the compositing, so the model learns a region that is **causally sufficient and
  necessary** for its own decision — faithful by construction, not by inspection.
* **Mask supervision** (BCE+Dice) where the mask is exact; restoration-consistency only (no mask target) for observed
  FF++ forgeries, whose target-video frame is only an approximate counterfactual.
* Three-way head as in HYB (real / fake / filter); the same backbone (EfficientNet-B4) and recipe as HYB-F.

Inference output: label, edit-region mask, and a **faithfulness score** = drop in $p_y$ when the predicted region is
replaced by a neutral fill — no counterfactual needed at test time. This is the structured explanation the project
promised (schema v2.1.0), produced by the detector itself.

## 2. Why a reviewer should care
1. A training objective that ties a detector's explanation to a counterfactual test, on a corpus where that test
   is exact — new for face forensics (mask heads exist; consistency through the classifier's own counterfactual
   does not).
2. Explanation quality becomes measurable without human raters: IoU against exact masks on held-out edits, and
   causal flip rates under restoration, against Grad-CAM/Grad-CAM++/Score-CAM and against a mask head trained
   without the consistency loss (the ablation that isolates the contribution).
3. It unifies the three-way detector (frontier result) with part-level explanation (fake) and type/region
   explanation (filter) in one lightweight model.

## 3. Data added (part-level edits with exact masks, `partedit_20260927`)
FF++ c23 train real frames (train partition only). Parts: eyes, nose, mouth. Two mechanisms so the evidence head
cannot key on one generator: **donor transplant** (landmark-aligned similarity warp from a different identity,
colour-matched, feathered) and **diffusion inpainting** (SD-1.5 inpainting restricted to the part mask at 512 px,
compositing keeps pixels outside the feathered mask bit-exact). Label **fake** (identity of the part is not the
subject's). Held-out: test-partition frames, same two mechanisms, plus a third mechanism never trained on
(decided and written down before generation starts: SDXL-inpainting) for the cross-mechanism claim.

## 4. Arms (identical data, backbone, recipe)
| arm | evidence head | restoration loss |
|---|---|---|
| HYB-F+PE | no | no — HYB-F recipe with part edits added to the fake pool (detection baseline) |
| MASK | yes, BCE+Dice | no — post-hoc-free but not counterfactually trained (explanation baseline) |
| **CGD** | yes | **yes** |
Post-hoc baselines on HYB-F+PE: Grad-CAM, Grad-CAM++, Score-CAM at the last conv block.

## 5. Bars (fixed now)
Detection must not regress (CGD vs HYB-F+PE): **D1** CDFv2 ≥ −0.01, **D2** DFD ≥ −0.01, **D3** FF++ in-domain each
≥ 80 %, **D4** B1 0/12, **D5** Celeb-DF-B E1 holds.
Explanation (held-out part edits, correctly detected only; 7×7 cell IoU and pixel IoU):
**E1** CGD IoU ≥ MASK IoU (consistency does not hurt localisation) and ≥ best post-hoc + 0.15;
**E2** restoration flip rate (restore predicted region → label leaves *fake*) ≥ 70 % for CGD, and ≥ MASK + 15 pp;
**E3** complement flip rate ≤ 20 % (the region is necessary); random area-matched region flip ≤ 20 %;
**E4** on the never-trained third mechanism, E1–E3 hold within 10 pp of the trained ones;
**E5** filter items: restoring the predicted region of a correctly classified filter image drops $p_{filter}$ by ≥ 0.3
(vs whole-frame background shortcut: the model must localise at least as well as the region-restoration table shows).
BUILD = D1–D5 and E1–E3 → second seed. Anything else: report as is.

## 6. Traps
* Part edits are visually detectable to humans in some cases; that is fine for fake, but **no part edit is ever labelled
  filter**.
* Observed FF++ forgeries: consistency loss only; no exact mask claimed.
* The restoration path uses $x_0$ at training time only; the faithfulness score at inference uses a neutral fill and is
  reported as an estimate, calibrated against true restoration on the test set.
* No Celeb-DF-B / CDFv2 / DFD frame enters any training or selection decision. HELDOUT-13 stays out.

## Addendum 1 (2026-09-28, after the novelty scan, before any CGD result is read)
**Prior art that bounds the claim.** The drop term with gradient through soft-mask compositing is GAIN (Li et al.,
CVPR 2018, arXiv:1802.10171; zero fill, optional mask L2); two-sided masked-in/masked-out training of a masker is
Dabkowski & Gal (NeurIPS 2017) and Phang et al. (arXiv:2010.09750); exact masks from pixel-aligned pairs incl. FaceApp
filters is DFFD (Dang et al., CVPR 2020); IoU-vs-exact-mask with Grad-CAM as baseline on inpainted faces is Țânțaru et
al. (WACV 2024, dolos); self-blend mask supervision of an attention head is LAA-Net (CVPR 2024); flip-rate faithfulness
for deepfake XAI is Tsigos et al. (ACM MAD'24). **What remains ours**: the counterfactual fill is the pixel-aligned
*original* through the *predicted* mask (both terms evaluated on in-distribution images), applied jointly to fake and
filter in a three-way detector, and the restoration-flip metric. "Faithful by construction" is withdrawn; the claim is
"trained to satisfy a restoration-counterfactual criterion, verified by held-out flip rates on an unseen editor".
**Ablation arms added (required, run after the three main arms; same recipe/seed):**
- **CGD-ZERO**: x0 replaced by zeros (= GAIN_ext with our head) — isolates the original-image fill.
- **CGD-BLUR**: x0 replaced by a Gaussian-blurred copy of x (Dabkowski/Fong-style fill).
- **CGD-NOHOLD**: drop term only (no x_dn term).
Bars unchanged; CGD must beat CGD-ZERO on E2/E3 by ≥ 10 pp for the fill to count as a contribution.
**Evaluation protocol (replaces the metric list in §5; bars keep their thresholds):** pixel IoU and F1 at fixed 0.5 +
pixel AUC; soft-GT cosine/SSIM against Gray(|x−x0|); energy-based pointing game (mass inside GT) with **centre-prior and
random-region controls** and bootstrap CIs; restoration curve (top-k saliency pixels restored to x0, AUC of P(true class))
with GT-mask restoration as ceiling; Adebayo parameter/label randomisation (SSIM/Spearman between trained and randomised
maps); part-level pointing (argmax cell inside edited part). Every saliency number is reported next to the best trivial
control. A patch-score localisation baseline (Țânțaru) is added to the post-hoc baselines.

## Addendum 2 (2026-09-28, after CGD seed-1 results, before CGD-D is trained)
**Bookkeeping error found by the pre-declared ceiling check.** The "exact mask" stored for part edits is the compositing
hull; the feathered composite changes pixels outside it (donor: 22.8 % of changed pixels lie outside the hull). Restoring the
hull flips only 19.6 % of detected donor edits, restoring the true footprint (|x−x0|>6 dilated by the feather width, 25 px at
native crop) flips 88.9 % ≈ full restoration 89.3 %. **Correction**: the GT mask for part edits is the footprint (training target
and evaluation), matching how filter masks were already defined. E2/E3 are evaluated on the predicted region area-matched to
the footprint and dilated by the same radius; every flip rate is reported next to the GT-footprint ceiling and as a fraction of
it. Thresholds unchanged (E2 ≥ 70 %, E3 ≤ 20 %).
**CGD seed-1 (hull-mask training, 43k part edits, no symmetric degradation) — reported as is**: CDFv2 0.794 [0.766, 0.821],
DFD 0.906, FF++ 83.1/89.1/87.2, FA/MISS 3.19/2.62, B1 0/13, Celeb-DF-B AUC 0.870 (untreated genuine→fake 50.7 %, ΔMISS +2.7
[0.9, 4.8]); explanation: donor IoU7 0.858 / px 0.687, flip(pred, dilated) 77 % (ceiling 89 %), complement 2.9 %, random 2.6 %;
SD detect 41 % (only 1.9k SD items seen), IoU7 0.674 / px 0.541, flip(pred, dilated) 46 % (ceiling 77 %); E5 Δp_filter 0.565.
**CGD-D** = CGD + footprint masks + full 61,510 part edits + symmetric degradation (`--degrade`, x and x0 degraded identically).
Compared against HYBPE / MASK trained on the same 61,510 items (Ubuntu). Bars as §5 with Addendum 1/2 protocol.

## Addendum 3 (2026-09-29, before MASK-D is trained) — combine the two components that worked
Findings so far: (i) exact-footprint mask supervision alone reaches the restoration ceiling (MASK); the consistency loss adds
nothing (CGD, CGD-D). (ii) Symmetric degradation removes the softness shortcut (HYBD: blurred genuine frames called fake
10 % vs 91–95 %; robustness sweep: real recall under blur σ1.5 79 % vs 2 % for HYB/MASK) and gives the best CDFv2 (0.807)
without a head. MASK-D = mask head + symmetric degradation, no consistency loss, 61.5k part edits, seed 20260928.
Bars: CDFv2 ≥ 0.80 and DFD ≥ 0.89 (within 0.02 of MASK/HYBD); blur probe (σ1.5 on FF++ reals) ≤ 15 % called fake; robustness
sweep real recall at blur σ1.5 ≥ 70 %; explanation within 3 pp of MASK on donor/SD flip and IoU7 ≥ 0.70; Celeb-DF-B E1 holds
and untreated genuine→fake ≤ 30 %. If met, MASK-D is the paper's final model (two seeds before that claim).
