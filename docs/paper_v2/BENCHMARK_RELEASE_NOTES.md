# Benchmark release notes (2026-10-16)

Package: `benchmark_release/` (repository root). It turns the measurement of the paper into something a reviewer or a
reader can run: frame lists, filter recipes with their seeds, face boxes, scripts, the 17 detector adapters, and the
scores behind every benchmark table. No image, video or model weight is included.

## What is released

| part | content | size |
|---|---|---|
| `lists/` | frame lists of the six sources (Celeb-DF-B 43,363 frames; Celeb-DF-v2 test 16,059; DFD 10,404; retouching pairs 28,729 crops; smoothed forgeries 4,016; DF40 194,522 frames / 6,149 videos), per-video filter assignments (Celeb-DF-v2: seed 20261006 over 11 pilgram filters; DFD: seed 20261007 over 16 filters), face boxes for every video frame (69,826 boxes with the frame count and frame index), the shared boxes of the 2,210 FFHQ originals, the 718 DF40 videos removed for FF++ training identities, the draw order of the paper's filter-source bootstrap, and `MANIFEST.json` with the SHA-256 of every list and id column | about 13 MB |
| `scores/` | P(fake) of the 17 published detectors and of six rows of our models (P0, P2-sym, the main model with two seeds, its symmetric-view variant, the binary control) on every source, aligned row-for-row with the lists and refusing any other list | about 14 MB |
| `results/` | the bootstrap outputs of the analysis scripts on the released scores | small |
| `scripts/` | `extract_frames.py` (frame indices, bar trimming, crops; with the released boxes, or re-detecting with `--detect`), `apply_filters.py` (full-frame filters, then the same box), `retouch_pairs.py` (shared-box crops; per-operation statistics, threshold-free reading, paired logit shift), `evasion.py` (five smoothings; miss rise and intervals), `one_rule.py` (Celeb-DF-B and the filter sources, video-cluster bootstrap), `df40.py`, `score.py` (any adapter on any source), `build_lists.py` (every derived list regenerated from its rule and seed), `make_tables.py`, `selftest.py`; every script has `--dry-run` | |
| `adapters/` | entry points of the 17 detectors (the paper's adapters, with the repository root made configurable), the interface, a registry, and a table of repositories, commits, download sources and SHA-256 of every weight file | |
| `reference/` | the paper's Tables III, IV, VI and two supplement tables as typeset, and the 20 cached score rows of the self-test | |

## What was verified before release

* `make_tables.py --check` regenerates Tables III (23 rows), IV (22 rows) and VI (12 rows) from the released scores; all
  57 rows equal the paper's cells and the three files are byte-identical to the typeset tables. From the bootstrap
  results, the supplement's two-sided table with intervals (21 rows: 17 detectors and 4 of our rows; the "FF++ only" row
  is not released) and the smoothed-forgery table (5 released rows) also match cell by cell.
* `selftest.py`: list hashes, alignment of all 116 score files, the one-rule scorer on 20 cached rows, and Effort's
  published numbers on every source (Table III Celeb-DF-B and DFD cells, the fair_cdfb.json intervals with 1,000 video
  draws, the FA_b - FA_c interval, Table IV, Table VI). Passes in about a minute.
* The analysis scripts reproduce the original records exactly: Celeb-DF-B (fair_cdfb.json, values and intervals), DFD
  filters (dfd_filteredff.json, including the intervals through the replayed draw sequence), the retouching block and
  the threshold-free Smoothing-90 statistics for all 17 detectors, the smoothed-forgery record and its paired
  differences, and DF40 (means, per-method AUC, intervals and paired differences).
* Face boxes: re-detecting every frame of the three video sources (MediaPipe 0.10.35, YuNet for DFD) gave a box of the
  stored crop's size for 69,826 of 69,826 frames, the same DFD detector tier and the same frame index. Crops cut with
  the released boxes are byte-identical to the paper's crops on samples of every source (320 crops), as are the
  full-frame filtered crops (239 crops, both filter sources) and the shared-box retouching crops (40 crops).
* `build_lists.py` regenerates both filter assignments from their seeds, the smoothed-forgery subset, the DF40 video
  table and its exclusions, and checks the Celeb-DF-B presets against the dataset's annotation file.
* The adapter path was exercised end to end with a stand-in detector (`score.py` -> `retouch_pairs.py` -> `make_tables.py`,
  extra row appended). The published detectors were not re-run for this release (the GPU was in use); their scores are
  the paper's.

## What is not released, and why

* **Videos, frames and images** of Celeb-DF-B, Celeb-DF-v2, DFD, FFHQ, RetouchingFFHQ and DF40: their owners' terms do
  not allow redistribution (Celeb-DF-v2 and FaceForensics++ require an access request; DF40 is CC BY-NC 4.0 with the
  FF++ and Celeb-DF terms for its real frames; Celeb-DF-B was given to us by its authors). We release the lists, boxes,
  recipes and scripts to rebuild every input from the originals.
* **Weights of the 17 published detectors**: each is the authors' checkpoint under the authors' terms; the adapters'
  README gives the source and SHA-256 of every file.
* **Weights of our models** and their training data and code: not part of the benchmark. Their scores are released so
  that our rows of the tables can be checked; whether to release the checkpoints is a separate decision.
* **Tables V and VII** (trade-off across our training arms; part-level localisation) read training arms and a
  localisation set outside the benchmark. Supplement tables that list arms other than the six released rows can be
  regenerated only for the released rows.
* **The DF40 list builder from the official protocol JSON files**: the released list is the paper's fixed list (written once before any
  detector was scored) with the machine-specific path prefix removed, hashed in `lists/MANIFEST.json`; the rule (all FF++
  domain test videos; at most 140 fake videos per method in the Celeb-DF domain, numpy default_rng(0); 718 mobileswap
  videos of FF++ training identities removed) is documented and checked by `build_lists.py`.
* **The crop-comparison runs of Table S-reproduce** (each DeepfakeBench baseline on its own crop): they need the
  DeepfakeBench-style crops of Celeb-DF-v2 and DFD, which are not part of the benchmark sources.

## Caveats a user should know

* The threshold is fitted per source on untreated genuine frames, which no deployed detector can do; Table IV also has
  threshold-free columns for this reason.
* Intervals resample videos (or originals), not identities.
* On the two filter sources the paper drew each detector's resamples in sequence from one shared generator. `one_rule.py
  --draws paper` replays it (positions of unreleased models consume their draws), `--draws fixed` gives every detector
  the same draws. Point values do not depend on this.
* Frame indices follow OpenCV's frame count and seeking; the box files record each video's frame count so a different
  decoder can be detected (`extract_frames.py` reports it).
* Celeb-DF-B's bar trimming was introduced after the first extraction was read (reported in the paper).
* The retouching service set is an analysis set, not a clean test: more than 60 of our checkpoints and all 17 published
  detectors were scored on it, and Smoothing-90 was singled out after reading it.

## Sentence for the reproducibility statement

> We release the benchmark as frame lists, per-video filter assignments with their seeds, face boxes, the scripts that
> rebuild every input from the original datasets and apply the one evaluation rule, adapters for the 17 published
> detectors with the SHA-256 of their released weights, and the per-frame scores behind every benchmark table; a
> self-test regenerates Tables III, IV and VI from these scores, and no video, image or model weight is redistributed.

(For the anonymous submission, host the package at an anonymised URL; the package itself contains no author name, user
name, e-mail address or machine path.)

## Publishing the package from this repository

The repository's root `.gitignore` is a whitelist (`/*`), so `benchmark_release/` is currently ignored, and the global
`*.txt` rule also hides `benchmark_release/requirements.txt`. To publish it, add these two lines to the root `.gitignore`
(nothing else inside the package is caught by the global rules; checked with `git check-ignore`):

```
!/benchmark_release/
!/benchmark_release/requirements.txt
```

The package has its own `.gitignore` for `config.json` (which holds local dataset paths), `work/` and `tables/`.

## Open licensing questions

1. **Celeb-DF-B**: no licence file; the authors shared it by a link that has expired and asked to be cited. May we
   publish per-frame scores, frame lists and face boxes derived from it, and how should others obtain the videos? Ask the
   authors before the camera-ready release.
2. **RetouchingFFHQ**: the terms of the release (and whether per-image scores and crop boxes of the Alibaba renders may be
   published) were not found in the project records. Check the dataset's terms or ask the authors.
3. **Scores derived from Celeb-DF-v2, FaceForensics++ / DFD and DF40**: the terms forbid redistributing the data; scores
   and boxes are derived metadata, commonly released, but the FF++ and Celeb-DF terms do not address them explicitly.
4. **DF40 source**: our copy came from Hugging Face re-uploads of the official files (the official Google Drive links
   were quota-blocked), verified by size and layout. The release points users to the official repository; whether to
   mention the re-uploads is a choice for the authors.
5. **Detector licences differ** (DeepfakeBench, Effort and Forensics Adapter CC BY-NC 4.0; GenD MIT; CADDM Apache-2.0;
   LAA-Net academic-only; DFD-HR's LICENSE and README disagree; NPR has no licence file). The adapters import the authors'
   code from their repositories and copy none of it, but `zoo_published.py` repeats the paper's preprocessing for the
   DeepfakeBench detectors and the release itself needs a licence of its own (e.g. CC BY-NC 4.0 to match the
   non-commercial terms around it).
6. **Our models' scores** are released; our weights are not. Decide whether the paper promises the weights.
