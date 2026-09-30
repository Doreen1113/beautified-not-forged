# Orphan & Unverifiable Register — v8.11 Production Release

> A running list of artifacts that either (a) exist on disk with no traceable provenance, or
> (b) are confirmed stale/mismatched relative to what they appear to represent. Nothing here
> is deleted or moved. This register exists so future release passes don't have to
> rediscover these from scratch.

## 1. Orphan checkpoint: `shufflenet_v2_layer2_v815a_v814clean.pth`

- **Location**: `c:\My_Project\AIGC\shufflenet_v2_layer2_v815a_v814clean.pth`
- **Size**: 10,321,836 bytes (per Stage A listing)
- **File mtime**: 2026-08-12 10:37 (per Stage A listing)
- **Finding**: A repo-wide grep across `.py`/`.md`/`.json`/`.yaml`/`.yml`/`.txt` for this
  exact filename returned **zero matches** in both the Stage A pass and this Stage A.5 pass.
  No training script loads it, no eval script references it, no doc mentions it by name.
- **Best-guess origin** (not confirmed): the filename pattern (`v815a_v814clean`) suggests it
  is a v8.15a dual-head pilot variant, backbone-initialized from a "cleaned" version of the
  v8.14 checkpoint — consistent with the two sibling files that ARE referenced
  (`shufflenet_v2_layer2_v815a_v812.pth`, `shufflenet_v2_layer2_v815a_v814.pth`, both loaded
  by `train_v815a_v812.log`/`train_v815a_v814.log`-adjacent training runs per Stage A's
  results/ listing). A `train_v815a_v814clean.log` and `train_v815a_v814clean_log.csv` DO
  exist in `results/` (confirmed in Stage A's results/ listing) — meaning a training run
  producing this checkpoint almost certainly happened, but no downstream script (eval,
  mining, or documentation) ever consumed the resulting `.pth` file afterward.
- **Disposition**: **Must NOT be deleted.** Status: orphan, awaiting human decision on
  whether to (a) formally document it as an abandoned dual-head variant, (b) re-run the
  corresponding eval to give it a documented result, or (c) explicitly mark it for archival
  in a future Stage C pass. Not part of the v8.11 production release scope in any capacity.

## 2. Historical misreport risk: `shufflenet_v2_layer2_v811c.pth`

- **Location**: `c:\My_Project\AIGC\shufflenet_v2_layer2_v811c.pth`
- **Incident** (per TODO.md's own 2026-08-11 entry, read in Stage A and re-confirmed this
  pass): this checkpoint's results were **previously mistakenly reported as v8.11's final
  numbers** in an earlier internal report, before the mix-up was caught. The root cause was
  the same class of bug flagged elsewhere in this register (Item 4 below): scripts that
  accept a weights path as a parameter but wrote to a fixed output filename regardless of
  which weights were actually loaded.
- **Current status**: the underlying bug (fixed output filenames) has been fixed in
  `AIGuard/stress_test_v811_pipeline.py`, `AIGuard/eval_robustness.py`, and
  `AIGuard/stress_test_layer1.py` (auto-naming by loaded weights, per TODO.md). However,
  **the same class of risk still exists** for `eval_v811_gates.py` and
  `AIGuard/eval_ali_ood_v811.py`, which still default silently to `v811c` and do not
  auto-name their outputs by loaded weights — confirmed by reading both scripts in this pass
  (see `RELEASE_MANIFEST.json`'s `provenance_status_justification` and
  `REPRODUCTION_COMMANDS.md`'s warning banner).
  > ⚠️ **2026-08-26 append-only annotation**: the "still exists" statement above is **out of
  > date**. `eval_v811_gates.py` and `AIGuard/eval_ali_ood_v811.py` were changed to fail-closed
  > (explicit weights required, outputs named by loaded weights) during the 2026-08-13 P0 repair,
  > and v811d results were re-run and archived. One further silent-default script remained on
  > 2026-08-26: `eval_df40_benchmark.py` (positional args, default `v811c`) — the DF40 sanity
  > benchmark was re-run this day with explicit v8.17 weights
  > (`results/research/remeasure_sweep_20260826/`); `generate_v811_confusion_matrix.py` was
  > changed the same day to name its output by loaded weights.
- **Disposition**: **Forbidden as production evidence.** Any result file confirmed (by
  reading its own header/content) to have loaded `shufflenet_v2_layer2_v811c.pth` or
  `shufflenet_v2_layer1_v811c.pth` must be excluded from `RELEASE_RESULTS.md`'s scored
  tables — see the two concrete instances found and excluded in this pass:
  - `results/v811_gates_output.txt` (header explicitly reads "Layer1:
    ...shufflenet_v2_layer1_v811c.pth")
  - `results/ali_ood_v811_output.txt` (header explicitly reads "Layer1:
    C:\My_Project\AIGC\shufflenet_v2_layer1_v811c.pth")

## 3. Undated / no-checkpoint-provenance results (UNVERIFIABLE)

| Result | Why UNVERIFIABLE | Disposition |
|---|---|---|
| Alibaba OOD filter recall = 98.1% (20,743/21,151), quoted in CLAUDE.md and TODO.md for v8.11d | No archived result file found anywhere under `results/` matching this figure. The only Alibaba OOD file present (`ali_ood_v811_output.txt`) is confirmed Layer1c-era (97.8%), not v811d. | Must not be used in formal tables as file-backed evidence. Narrative-only claim. See `REPRODUCTION_COMMANDS.md` for the exact command that would produce the missing evidence. |
| True Test paired balanced accuracy = 81.1%, the Freeze Gate's "Paired filter" metric | `eval_truetest_paired.py` prints to stdout only; no `--output`/file-write mechanism found in this pass, and no matching file exists under `results/`. | Must not be used in formal tables as file-backed evidence, despite the script itself being confirmed correct (defaults to v811d/v811). |
| True Test filter-recall-by-type breakdown (smoothing 100% / whitening 95.2% / eye_enlarging 82.3% / face_reshaping 96.8%), quoted in CLAUDE.md | `eval_truetest_filter_bytype_v811.py` confirmed to default correctly to v811d/v811, but no output file from it was located under `results/`. A related-but-distinct metric (Filter XAI's `final_filter_accuracy`, n=98-100/type, self-built paired GT, not True Test) IS file-backed — see `RELEASE_RESULTS.md`. Do not conflate the two. | Must not be used in formal tables as file-backed evidence for the True Test figure specifically. |
| `results/v811_confusion_matrix.json` | File mtime (2026-08-03) **predates the creation of `shufflenet_v2_layer1_v811d.pth` itself** (2026-08-10, per TODO.md's own version history). Content cross-check confirms it matches v811c-era numbers (94.0% filter recall), not v811d's 93.6%. The producing script (`generate_v811_confusion_matrix.py`) is itself correct (dynamically reads `pl.LAYER1_WEIGHTS_PATH`) — the *artifact on disk* is simply stale relative to what its filename implies. | Excluded from `RELEASE_RESULTS.md`. Flagged for regeneration in a future pass (regeneration itself is out of scope for this read-only release documentation task). |
| `results/xai_evidence_v1_20260812.jsonl`, `results/xai_evidence_heatmaps_20260812/`, `results/gt_vs_gradcam/` figures pre-2026-08-13 (if any existed) | Carried over from Stage A's `RESULTS_PROVENANCE.md` as UNVERIFIABLE by filename alone. This pass independently confirmed the *current* `gt_vs_gradcam/` PNGs (dated 2026-08-13 11:00) ARE v8.11d/v811 (see Item 4 below) — that specific UNVERIFIABLE flag from Stage A is now resolved to VERIFIED for the gt_vs_gradcam figures specifically. `xai_evidence_v1_20260812.jsonl` was not re-investigated in this pass and remains UNVERIFIABLE per Stage A's finding. | gt_vs_gradcam figures: now production_evidence (see Item 4). `xai_evidence_v1_20260812.jsonl`: still UNVERIFIABLE, not upgraded. |

> ⚠️ **2026-08-21 annotation (APPEND-ONLY, F2 audit — no row above deleted or reworded):**
> This section's file mtime is **2026-08-13 11:42** (confirmed via filesystem stat during the
> F2 audit). The P0 Evaluation Integrity Repair that closes the first three rows of this
> table ran **later the same day**: `alibaba_filter_ood_v811d_layer2v811_20260813.json` was
> written at **12:07**, `truetest_paired_v811d_layer2v811_20260813_provenance.json` and
> `truetest_filter_bytype_v811d_layer2v811_20260813_provenance.json` at **12:35**, and
> `EVALUATION_INTEGRITY_REPAIR.md` itself at **12:38** — all after this register was last
> saved. This table was simply never revisited after the repair landed; it is not a
> disagreement about facts, it is a stale snapshot. Status of each row, checked against the
> file that now exists and against `RELEASE_RESULTS.md`'s official table:
> - **Row 1 (Alibaba OOD 98.1%)** — RESOLVED. `alibaba_filter_ood_v811d_layer2v811_20260813.json`
>   exists, its `provenance` block cites Layer1d/Layer2-v811 SHA256 hashes matching
>   `RELEASE_RESULTS.md`, and its `overall.recall_pct` is 98.071 (20,743/21,151) — the exact
>   figure now cited in the official table. Independently re-verified (re-read the JSON, not
>   just the claim) during this audit — see `results/research/f1f2_audit_20260821/F1F2_AUDIT_FINDINGS.md`.
> - **Row 2 (True Test paired balanced accuracy 81.1%)** — RESOLVED, same repair pass, file
>   `truetest_paired_v811d_layer2v811_20260813_provenance.json` + console log, per
>   `RELEASE_RESULTS.md` row and `EVALUATION_INTEGRITY_REPAIR.md`'s gap #2.
> - **Row 3 (True Test filter-recall-by-type)** — RESOLVED, same repair pass, file
>   `truetest_filter_bytype_v811d_layer2v811_20260813_provenance.json` + console log.
> - **Row 4 (`v811_confusion_matrix.json`, stale) and Row 5 (XAI pre-2026-08-13 files)** —
>   unaffected by the repair, still accurate as written above.
> `RELEASE_RESULTS.md` is the authoritative, currently-accurate document for these three
> numbers; this register's rows above are kept verbatim as the historical UNVERIFIABLE-state
> record, not because they are still true today.

## 4. Overwritten Layer1c `gt_vs_gradcam` visualization — historical incident, not restorable

- **What happened** (per TODO.md's 2026-08-13 provenance-correction entry, read in Stage A
  and re-confirmed this pass): `results/gt_vs_gradcam/gt_vs_gradcam_eye_enlarging.png` and
  `gt_vs_gradcam_face_reshaping.png` were originally generated on 2026-08-02, when
  `pipeline.py`'s `LAYER1_WEIGHTS_PATH` could only have pointed at
  `shufflenet_v2_layer1_v811c.pth` (v811d did not exist yet — created 2026-08-10). This was
  discovered during a provenance audit on 2026-08-13. `generate_gt_vs_gradcam_figures.py` was
  re-run to produce the correct v8.11d/v811 versions.
- **Process failure, explicitly self-recorded in TODO.md**: the re-run **overwrote the
  original Layer1c-era files in place**, violating the project's own stated convention of
  never overwriting existing results (always using a new filename). `results/gt_vs_gradcam/`
  was never tracked in git, so the Layer1c-era originals are **permanently unrecoverable**.
  TODO.md records this honestly, without concealment.
- **Impact assessment** (per TODO.md, not re-derived in this pass): assessed as low — these
  are visualization aids with no quantified number depending on them, and the new (Layer1d)
  versions are visually consistent with what the Layer1c versions were understood to show
  (whitening hot-region concentrated near the upper-face/forehead, consistent with the same
  day's whitening peak-position diagnostic finding).
- **Disposition for this release**: the **current** PNGs (`gt_vs_gradcam_eye_enlarging.png`,
  `gt_vs_gradcam_face_reshaping.png`, mtime 2026-08-13 11:00) are confirmed v8.11d/v811
  production evidence (their producing script `import pipeline as pl` directly, guaranteeing
  they reflect whatever `pipeline.py` points to at generation time, which on 2026-08-13 is
  confirmed to be v811d/v811). **They may be cited as production Filter XAI evidence.**
  However: **no strict before/after (Layer1c vs Layer1d) visual comparison is possible any
  longer**, and no report or paper section should claim to present such a comparison — only
  a single-checkpoint (v8.11d) visualization is available going forward. This is recorded
  here as a historical incident, not as a currently-open problem requiring action.

## Summary table

| Item | Type | Disposition | Blocks production release? |
|---|---|---|---|
| `shufflenet_v2_layer2_v815a_v814clean.pth` | Orphan checkpoint | Do not delete; awaiting human decision | No — not in production scope |
| `shufflenet_v2_layer2_v811c.pth` (and Layer1c) | Historical misreport risk | Forbidden as production evidence; live footgun in 2 still-unfixed scripts (⚠️ 2026-08-26: both since fixed fail-closed; see Item 2 annotation) | No, but flagged as an active process risk for future re-runs |
| Alibaba OOD 98.1% (v8.11d) | Undated/no-file UNVERIFIABLE result **(⚠️ 2026-08-21: RESOLVED same-day 12:07, see annotation above and Item 3 row 1)** | ~~Excluded from scored tables~~ **Now file-backed, included in `RELEASE_RESULTS.md`'s official table** | No — release ships with this gap disclosed, not hidden |
| True Test paired balanced accuracy 81.1% | No-archived-file UNVERIFIABLE result **(⚠️ 2026-08-21: RESOLVED same-day 12:35, see annotation above)** | ~~Excluded from scored tables~~ **Now file-backed, included in `RELEASE_RESULTS.md`'s official table** | No — same as above |
| True Test filter-recall-by-type | No-archived-file UNVERIFIABLE result **(⚠️ 2026-08-21: RESOLVED same-day 12:35, see annotation above)** | ~~Excluded from scored tables~~ **Now file-backed, included in `RELEASE_RESULTS.md`'s official table** | No — same as above |
| `results/v811_confusion_matrix.json` | Stale/pre-dates checkpoint | Excluded, flagged for regeneration | No |
| `gt_vs_gradcam/*.png` (current) | Resolved from UNVERIFIABLE (Stage A) to VERIFIED (this pass) | Included as production evidence | No |
| Overwritten Layer1c `gt_vs_gradcam` originals | Unrecoverable historical incident | Recorded, not actionable | No |
