# Adversarial review, 2026-10-12: exposure arms on the unseen retouching service

Claim reviewed: FINDINGS.md, section "2026-10-12 Commercial retouching: rerun with 15 detectors, and the exposure arms".
Everything below is from existing score files, the training code, and three new read-only scripts in this folder
(`review_scores.py`, `measure_smoothing.py`, `epoch_check.py`). Nothing was trained; no existing file was changed.

**Overall verdict: survives with rewording.** The 40 to 50 point drop on Smoothing is real, replicated on three seeds, and
robust to every threshold I tried. Four things in the current wording are wrong or unsupported: "retouching" (the effect
exists for one of four operations), "no commercial data" (true for pixels, not for the operator's strength ranges),
"transfer" (the scripted smoothing is the same operation at the same strength as the service's), and "15 detectors, 37–69%"
(13 detectors, 36–69%). There is also a replicated cost on untreated Celeb-DF-v2 that the section does not list.

---

## 1. Training-data leakage

Evidence (`retouch_unified_20260929/train_ru5.py`, `RUData5`, with `--ffpp-only --binary`):

- `self.bases` is reduced to `src == "ffpp_real"`; the logs print `bases 41,510` for all nine runs.
- Filter item: `u` in [0.40, 0.80) (the two commercial branches) is redrawn into [0, 0.40). Effective mixture:
  scripted single operation `random_op_v2` 50 %, `random_grade` 30 %, `obs_filt` 20 %.
- `obs_filt` (the `u >= 0.80` branch) is `src == "ffpp_filter"`: 41,512 pre-rendered files in `ffpp_filter_frames/train/`,
  built by `ffpp_unified_20260925/gen_filters.py` from FF++ train genuine frames: 14 pilgram colour filters and the project's
  own smoothing / whitening / eye / slimming at three strengths (26 kinds, about 1,600 each). No commercial image.
- Fake item: `vendor_fake` is forced off, `v0 = 0`; `uf` is set to 0.30 (FF++ forged frame) or 0.90 (self-blend of the FF++
  frame). The part-level and vendor branches are unreachable. In P2 half of the forged items get `_on_top`
  (grade 35 % / `random_op_v2` 30 % / `beautify` 35 %; for observed forgeries, which have no landmarks, grade 35 % / `beautify` 65 %).
- The vendor lists (`single 50,112`, `photometric 28,307`, `parts 61,510` in the log line) are loaded but never indexed.
- With `--binary` the loss is BCE on the forged logit only; the beautified, presence, quantity and map heads are unsupervised.

So no Tencent, Megvii, Alibaba or FFHQ **pixel** enters these arms. Three qualifications:

1. **The operator's strength ranges come from commercial renders.** `ops.py::random_op_v2` docstring: "log-uniform strengths
   spanning the TRAINING vendors' measured range (Tencent levels 30-90, Megvii medians) ... smoothing texture loss ~3..32 %
   (mix 0.03..0.4)". Tencent and Megvii are the two sister services of the test service in the same RetouchingFFHQ release,
   with the same four operations and the same level names. "No commercial data" is false at the level of hyper-parameters.
2. **The test service's edit magnitudes were on disk before those ranges were written.** `pairs_ali.tsv` / `measure_ali.log`
   (all 26,519 test pairs, per-level table; Smoothing_90 texture ratio 0.78) are dated 2026-09-29 00:28; `ops.py` is dated
   2026-09-30. The chosen smoothing range (3–32 % loss) brackets all three test levels (11 / 18 / 22 %). I cannot show the
   range was tuned on it, and the authors cannot show it was not.
3. `calib_ops.py` fits `EYE_CAL`, `JAW_CAL` on 120 untouched originals from `ffhq_originals/Part2`, i.e. test-service
   identities (the `random_op_v2` docstring says "Part7 only"). It only scales the quantity targets, which the binary arms do
   not use, and does not change any image. Harmless here; fix the docstring.

What a "beautified view" is in P1 / P2: an FF++ c23 training frame after exactly one of
(a) one scripted operation: eye enlarging, face slimming, whitening inside a feathered face hull, or bilateral smoothing
inside a feathered face hull with blend weight 0.03–0.4;
(b) a random global colour look (tone curve, colour matrix, saturation, contrast, fade, tint, vignette, grain; at least two);
(c) a pre-rendered version of another FF++ train frame: one of 14 Instagram-style colour filters or one of the four scripted
operations at three strengths;
and, on forged items in P2 only, also (d) `fasb.beautify`: global bilateral, global whitening, a pilgram filter, or both.

P0 against P1 / P2, other than beauty: nothing. Same 41,510 bases, 20,752 steps, three items per base, labels not-forged :
forged = 2 : 1. In P0 the third item is a second untreated copy of the genuine frame (same shared colour / JPEG transform,
its own random resize). All arms get label-symmetric Gaussian blur (sigma 0.6–2.0) or down-up scaling on half the triplets
(`sym_degrade`) and random JPEG (`post_m`).

Process defect: `train_ru5.py` is untracked in git (`??`), and the meta files of seeds 1 and 2 lack the `beauty`, `mil`,
`tune` keys that the current file writes, so the code that trained two of three seeds is not the file on disk and cannot be
audited. Seed 3 (2026-10-10) carries the keys and reproduces the result.

**Verdict: survives with rewording.** Allowed: "no image from any retouching service". Not allowed: "no commercial data"
without the sentence that the operator's strength ranges were set to cover those measured on two other services.

## 2. Is it a loss of sensitivity?

`review_scores.md` section 2 (sources: `celebdfb_v2_20260927/fair_cdfb.json`, `cdf_filteredff.json`, `dfd_filteredff.json`,
`dfd_v3.json`, `pair_filtered.json`, `pair_cdfb.json`, `select_*.json`). Seeds 1 / 2 / 3.

| metric | P0 | P1 | P2 |
|---|---|---|---|
| FF++ val AUC (selection) | .988 / .987 / .986 | .987 / .985 / .986 | .988 / .988 / .989 |
| Celeb-DF-v2 frame AUC, untreated | .889 / .897 / .905 | .859 / .870 / .880 | .877 / .877 / .885 |
| Celeb-DF-v2 video AUC, untreated | .938 / .938 / .940 | .900 / .910 / .922 | .917 / .920 / .935 |
| Celeb-DF-v2 miss at 5 % FPR, untreated | 40.9 / 37.8 / 35.2 | 48.8 / 44.8 / 40.9 | 46.2 / 43.1 / 39.7 |
| DFD v3 frame AUC | .943 / .944 / .944 | .942 / .938 / .937 | .938 / .938 / .936 |
| DFD miss at 5 % FPR, untreated | 20.9 / 19.4 / 18.3 | 20.7 / 22.1 / 22.0 | 21.1 / 21.6 / 22.8 |
| Celeb-DF-B AUC untreated | .927 / .937 / .944 | .928 / .931 / .939 | .929 / .933 / .935 |
| Celeb-DF-B AUC beautified | .860 / .883 / .883 | .844 / .851 / .864 | .879 / .893 / .877 |
| Celeb-DF-B miss rise, beauty only | +17.0 / +14.2 / +10.8 | +21.5 / +21.8 / +20.4 | +9.8 / +10.3 / +12.8 |
| Celeb-DF-v2 + 11 filters: miss | 47.9 / 42.2 / 43.5 | 65.4 / 62.5 / 57.2 | 46.6 / 46.1 / 38.8 |
| Celeb-DF-v2 + 11 filters: false alarm | 5.8 / 6.6 / 5.4 | 2.9 / 2.3 / 2.8 | 8.2 / 6.2 / 8.7 |
| DFD + 16 filters: false alarm | 4.7 / 5.4 / 4.2 | 4.2 / 3.9 / 3.8 | 6.9 / 7.4 / 8.8 |

Paired intervals (`pair_filtered.json`, video-cluster bootstrap), untreated Celeb-DF-v2 frame AUC:
P2 − P0 = −0.012 [−0.025, −0.000], −0.020 [−0.031, −0.010], −0.021 [−0.034, −0.008];
P1 − P0 = −0.027 [−0.040, −0.014], −0.025 [−0.040, −0.011] (seeds 2, 3; seed 1 not in the file, unpaired −0.030).
DFD: P2 − P0 = −0.005, −0.006, −0.008, upper bounds 0.002 / 0.000 / −0.001.

Reading: not a collapse of sensitivity (in-domain AUC equal, DFD within 0.8 point), but there is a cost the FINDINGS section
omits: **both exposure arms lose 1.2–3.0 points of untreated Celeb-DF-v2 frame AUC and 5–8 points of miss rate at 5 % FPR,
on every seed.** Plus the two costs already listed: P1 misses more forgeries once they are filtered (Celeb-DF-v2 57–65 % against 42–48 %, Celeb-DF-B beauty-only rise +20–22 against +11–17); P2 raises false alarms under colour filters by 2.0–4.6 points
(DFD) and up to 3.3 (Celeb-DF-v2). "No AUC change" in the section refers to the filtered AUC only and should say so.

**Verdict: survives, with the Celeb-DF-v2 cost stated next to the gain.**

## 3. Threshold artefact

`review_scores.md` section 3, from `ali_scores_<tag>.npz`.

Originals of the service above 0.5: P0 16.4 / 12.1 / 19.0 %, P1 11.4 / 10.4 / 8.3 %, P2 15.5 / 24.1 / 9.9 %.
The 5 %-FPR threshold is 0.954 / 0.977 / 0.976 for P0, 0.974 / 0.970 / 0.820 for P1, 0.984 / 0.998 / 0.836 for P2: all arms
operate in the upper tail on these stills, so the rule matters. Smoothing_90, share called fake, seeds 1 / 2 / 3:

| rule | P0 | P1 | P2 |
|---|---|---|---|
| 5 % FPR on service originals (the paper's) | 54.2 / 56.1 / 43.5 | 3.7 / 7.1 / 4.6 | 11.7 / 7.1 / 6.9 |
| 1 % FPR | 23.1 / 28.3 / 16.8 | 0.4 / 1.5 / 0.8 | 1.5 / 1.5 / 1.4 |
| 10 % FPR | 70.9 / 71.4 / 57.6 | 7.7 / 15.5 / 10.1 | 23.4 / 15.8 / 14.7 |
| fixed 0.5 | 80.0 / 75.5 / 71.2 | 9.4 / 16.0 / 8.5 | 33.1 / 37.7 / 14.5 |
| threshold = 95th pct of untreated Celeb-DF-v2 genuine frames | 57.2 / 56.8 / 41.8 | 1.2 / 2.7 / 1.7 | 9.5 / 11.1 / 3.2 |
| threshold = 95th pct of DFD genuine frames | 56.4 / 60.5 / 44.4 | 2.7 / 5.1 / 3.4 | 18.4 / 12.8 / 7.3 |
| AUROC, render vs originals | .891 / .893 / .839 | .479 / .600 / .575 | .695 / .629 / .635 |
| render scored above its own original | 98.5 / 99.0 / 97.0 | 43.5 / 67.5 / 64.3 | 84.1 / 72.4 / 75.5 |
| median logit shift | +5.2 / +7.1 / +4.3 | −0.2 / +0.7 / +0.4 | +1.8 / +1.5 / +0.9 |

No FF++ validation score file exists for these tags, so that transfer was not checked.

The effect holds under every rule. Three corrections follow from the same table:

- **It is a Smoothing result only.** At 5 % FPR, P0 itself is at the floor on the other nine cells:
  Whitening 30/60/90 4.5–7.5 %, FaceLifting 4.5–6.1 %, EyeEnlarging 4.8–5.9 % (AUROC 0.47–0.55). P1 / P2 change nothing
  there (4.2–6.5 %). The "all renders" figure (13.5 → 5.3) is the Smoothing cells diluted by nine null cells. Smoothing is
  dose-dependent in P0: level 30 / 60 / 90 = 12.6–17.0 / 29.6–40.8 / 43.5–56.1 %.
- **"Back to the 5 % floor" is true for P1, not for P2.** P2 still ranks smoothed renders above their originals in 72–84 %
  of pairs, AUROC 0.63–0.70, 6.9–11.7 % at the paper's rule (seed 1 interval [9.7, 14.3]), 14.5–37.7 % at 0.5.
- Under a fixed 0.5 threshold P2 seed 2 calls 24 % of untouched originals and 23–26 % of every render fake. The 5 %-FPR
  rule hides a calibration problem on FFHQ stills that all three arms have; the paper must say that the threshold is set on
  the service's own originals and give originals→fake at 0.5.

Free replication on two more services (`vendor_val_scores_*.npz`, held-out Tencent / Megvii renders, threshold = 95th pct of
816 held-out FFHQ originals): Megvii P0 37.6 / 34.2 / 26.9 % → P1 3.8 / 8.2 / 5.6 %, P2 7.8 / 6.1 / 6.2 %; Tencent P0
11.8 / 10.9 / 7.1 % → 5.7–7.6 %. Same direction. These two services are the ones the operator ranges were set on.

**Verdict: survives. Reword "retouching" to "skin smoothing", and "to the floor" to the numbers.**

## 4. In-distribution rather than transfer?

`measure_smoothing.md` (120 test identities, training geometry: crop, long side 512; hf = high-frequency energy relative to
the original, 1 = unchanged; medians).

| edit | hf face | hf background | hf at strong edges | hf in flat skin |
|---|---|---|---|---|
| service Smoothing_30 / 60 / 90 | 0.89 / 0.81 / 0.76 | 0.98 / 0.97 / 0.96 | 0.97 / 0.96 / 0.94 | 0.80 / 0.67 / 0.60 |
| scripted `op_smooth`, median of training range (mix 0.11) | 0.92 | 1.00 | 0.97 | 0.89 |
| scripted `op_smooth`, top of training range (mix 0.40) | 0.75 | 1.00 | 0.88 | 0.68 |
| global bilateral (9,50,50), in `beautify` | 0.55 | 0.58 | 0.93 | 0.33 |
| global Gaussian sigma 1.0 (`sym_degrade`, all arms incl. P0) | 0.53 | 0.51 | 0.52 | 0.52 |
| face-only Gaussian sigma 1.5 (no arm) | 0.41 | 1.00 | 0.38 | 0.43 |

- The service's smoothing is not Gaussian blur: it is confined to the face (background 0.96–0.98) and edge-preserving
  (edges 0.94–0.97, flat skin 0.60–0.80). Plain blur removes edges and background alike.
- A plain blur / JPEG augmentation does not do the same job, and this is already tested by the design: P0 trains with
  label-symmetric global Gaussian blur, down-up scaling and JPEG on half its triplets and still fires on 43–56 %.
- **The scripted smoothing is the same operation.** `op_smooth` is a bilateral filter blended inside a feathered face hull;
  at the top of its training range it gives face 0.75 / flat 0.68 / edges 0.88 / background 1.00 against the service's
  level 90 at 0.76 / 0.60 / 0.94 / 0.96. The training range (texture loss 3–32 %) covers the three test levels (11 / 18 / 22 %).
  What transfers is the implementation (a commercial pipeline on 1024-px FFHQ stills against an OpenCV bilateral on FF++
  video frames), not the kind or the strength of the edit.
- Which component carries it cannot be answered from existing arms. FF++-only arms with beautified views are all at the
  floor on Smoothing_90 (`review_scores.md` 4b): `clipe5f` 7.1 / 8.9, `clipe5fg0` (no colour grades) 3.6, `clipe5feb` 7.8,
  `clipe5mf` 5.3; FF++-only arms without them are not: `clipe5mfp0` 41.1. So colour grades are not needed. No arm has
  grades only, or scripted operations without smoothing, so "exposure to beautification in general" and "exposure to
  face-local smoothing" are not separated. The measurement above and the null result on the other three operations say it
  is the second.

**Verdict: "transfer from self-built edits to a commercial pipeline" fails as worded.** Allowed: transfer across
implementations and image domains of one operation, with matched strength. Required ablation before any broader wording:
P2 without `smooth` in `random_op_v2`, `beautify` and `obs_filt` (one seed is enough to decide).

## 5. Statistics and selection

- `exposure_ali.py`: draws resample the 2,210 identities with replacement and carry each identity's original and all its
  renders; the threshold is recomputed on the resampled originals inside each draw; both arms use the same draws; percentile
  interval over 1000 draws. Correct. The intervals cover identity sampling only; seed spread is larger for P0
  (43.5–56.1) than any single interval, so quote all three seeds, not one interval.
- Seeds: nine separate runs with their own logs and CSVs (first-epoch losses differ in every run); `torch.manual_seed` and
  the data generator both depend on the seed. Same seed across arms gives the same frame order, which is what a paired
  comparison wants. All share the CLIP initialisation, as usual.
- Checkpoint selection: `select_<tag>.json`, criterion `ffpp_auc` (FF++ validation AUC) for all nine. The training loop
  prints Tencent / Megvii validation rates each epoch but selection does not read them, and nothing reads the test service.
- Confound: P0 selects epochs 2 / 4 / 2, P1 7 / 8 / 4, P2 5 / 7 / 4, on validation AUC differences of 0.0003–0.002.
  Indirect evidence that epoch is not the cause: P0 seed 2 (epoch 4) 56.1 % against P1 / P2 seed 3 (epoch 4) 4.6 / 6.9 %;
  the Effort-scheme P0 arms select epochs 8 / 7 and score 56.9 / 63.2 %. Direct check (`epoch_check.py`, inference on
  existing per-epoch checkpoints, every 4th identity = 553, Smoothing_90 at 5 % FPR; the selected P0 seed 1 checkpoint gives
  50.5 on this subset against 54.2 on all 2,210):

  | arm, seed 1 | epoch 2 | epoch 5 | epoch 8 |
  |---|---|---|---|
  | P0 | 50.5 (selected) | 44.7 | 50.1 |
  | P1 | 7.8 | | 2.2 (selected epoch 7: 3.7 on the full set) |
  | P2 | 27.5 | 11.7 (selected, full set) | 9.4 |

  P0 at epoch 8, seeds 2 / 3: 46.5 / 43.8. So P0 is high at every epoch and the gap holds at matched epochs. But **P2 is
  epoch-dependent: 27.5 % at epoch 2 against 9–12 % from epoch 5 on.** The 7–12 % for P2 is a property of the later epochs
  that FF++ validation AUC happened to select (5 / 7 / 4), by margins of 0.0003–0.002; P1 does not have this dependence.
- The analysis is post hoc and Smoothing_90 is the worst of twelve cells. It is monotone in level and replicated, so this
  is a disclosure, not an objection.

**Verdict: survives.**

## 6. Other points

- **"Like 15 published detectors (37–69 %)" is wrong.** `published_ali.json`, Smoothing_90: 13 detectors lie in 36.3–68.7 %
  (EfficientNet-B4 36.3, RECCE 36.8, SBI 37.3 at the bottom; GenD 68.7 at the top), UnivFD is at 16.6 %, NPR is unusable
  (threshold 1.0, every score saturated). Write "13 of 15, 36–69 %; UnivFD 17 %; NPR saturated and excluded".
- Six of those thresholds are above 0.96 (SBI 0.9965, UCF 0.9942, EfficientNet-B4 0.990, RECCE 0.980, F3Net 0.972, SPSL 0.9605),
  and 1–46 % of untouched originals are above 0.5. The published detectors are measured in a saturated tail, on one shared crop
  (`boxes.json`, identical to ours), not each under its own preprocessing as Addendum 24 does for the video sets. State it.
- The comparison "P0 reproduces the published detectors" holds on Smoothing only; Effort and UnivFD also react to
  EyeEnlarging_90 (16.8 / 11.7 %), P0 does not (5.4–5.9 %).
- **The remedy is tied to the tuning scheme.** Same data rule inside Effort's scheme: 56.9 / 63.2 → 30.0 / 38.9, a 24–27
  point drop that leaves a third of smoothed faces accused. Two-epoch fine-tune of the released Effort checkpoint:
  55.3 → 52.7 (−2.7 [−3.7, −1.3]), i.e. nothing. The claim must be limited to LoRA trained from CLIP; "an exposure rule that
  fixes detectors" is not supported.
- Binary full-data control 5.2 / 9.1 against three-way 4.7 / 8.6 and 5.5 / 12.5: agreed that the third class is not what
  removes the accusation, on one seed of the control. The full-data models have seen Tencent / Megvii renders, so they are
  not evidence for the FF++-only claim.
- The full-data three-way models score smoothed renders *below* their originals (AUROC 0.32–0.40, paired 31–41 %); P1 / P2
  do not (0.48–0.70). Different mechanisms; do not present P1 / P2 as "the same thing with less data".
- Novelty. "Train on the corruption, become robust to the corruption" is standard, and the operation that moves is the one
  that was trained on at matched strength. The publishable parts are narrower: (i) the measurement that 13 detectors and an
  FF++-only CLIP baseline accuse 36–69 % of heavily smoothed genuine faces at 5 % FPR, with a dose response; (ii) global
  blur / JPEG augmentation does not prevent it while face-local scripted smoothing does; (iii) the class that receives the
  views decides which error is paid (P1: more misses under filters; P2: more false alarms under colour filters); (iv) the
  same rule does little under Effort's scheme. Sell those, not a method.

---

## Sentence allowed in the paper

> Trained on FaceForensics++ alone, our CLIP ViT-L/14 + LoRA baseline flags 43–56 % (three seeds) of the heaviest
> skin-smoothing renders of a retouching service it never saw, at the threshold that flags 5 % of that service's untouched
> originals; 13 of 15 published detectors flag 36–69 % under the same rule. Adding scripted beautified views of the FF++
> training frames, among them a face-local bilateral smoothing whose strength range was set to cover that measured on two
> other retouching services, lowers this to 4–7 % when the views are given to genuine faces only and to 7–12 % when given
> to both classes (paired differences −37 to −51 points, all intervals below zero). No image of any retouching service is
> used. The other three operations of the service (whitening, face slimming, eye enlarging) were not flagged above the 5 %
> floor by the baseline, so nothing is shown for them.

## Caveats that must accompany it

1. The result concerns smoothing; the pooled "all renders" number must not be the headline.
2. The scripted smoothing is the same kind of edit (face-masked, edge-preserving) at the same strength as the service's;
   the strength range was set from two sister services, and the test service's own measurements existed when it was set.
   Call it robustness across implementations and image domains, not transfer to an unseen kind of edit.
3. Cost: untreated Celeb-DF-v2 frame AUC falls by 0.012–0.021 (both classes) and 0.025–0.030 (genuine only) on every seed;
   genuine-only views raise the miss rate under filters by 14–20 points on Celeb-DF-v2; both-class views raise false alarms
   under colour filters by 2.0–4.6 points on DFD.
4. With views on both classes the smoothed render still scores above its original in 72–84 % of pairs (AUROC 0.63–0.70).
5. The threshold is set on the service's own originals; at 0.5 the three arms call 8–24 % of those originals fake.
6. LoRA from CLIP only. Under Effort's tuning scheme the same rule leaves 30–39 %; fine-tuning the released Effort
   checkpoint for two epochs leaves 53 %.
7. Post hoc analysis, not pre-registered; checkpoints selected on FF++ validation AUC; three seeds. For the both-class arm
   the rate depends on the epoch (27 % at epoch 2, 9–12 % from epoch 5, seed 1); the baseline is 44–50 % at every epoch checked.
8. Published detectors were scored on one shared crop, and six of them have 5 %-FPR thresholds above 0.96 on these stills.

## Before submission

- Run the ablation of point 4 (both-class arm without any smoothing in its views).
- Score every epoch of the nine runs on the service and report the curve, or fix the epoch in advance (`epoch_check.py` covers nine checkpoints on a quarter of the identities).
- Put `train_ru5.py` under version control and record the commit in each meta file.
- Correct the `random_op_v2` docstring ("Part7 only") or move `calib_ops.py` off the test originals.
- Add the per-operation, per-level table (`review_scores.md`, section 3) to the supplement in place of the pooled number.
