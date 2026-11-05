"""Regenerate the held-out donor part-edit TEST set with donors drawn ONLY from FF++ TEST real frames.

Audit finding (2026-10-06): manifest_test_donor.tsv transplants eyes/nose/mouth from donor frames that all come from
FF++ TRAINING videos (part_edit_gen.donor_edit samples donors from G.STEMS = fasb landmarks_train.npz, i.e.
FaceForensics_protocol_frames_dense/train/real), and its "never same video" guard compares against "" so it never
fires. 3,758/3,758 donor frames are in ffpp3_train.txt and 1,023 (donor frame, part) pairs are identical to rows of
manifest_train_donor.tsv.

This script keeps the SAME edit (imports part_edit_gen.donor_edit / part_mask unchanged) and only swaps the donor pool:
  * donor pool  = ffpp3_test.txt rows with label 0 (FaceForensics_protocol_frames/test/real, 1,316 frames / 136 videos)
  * donor video != target video (enforced by restricting G.STEMS per target before the call)
  * same target frames and parts, in the same order, as manifest_test_donor.tsv (3,948 items) -> directly comparable
  * deterministic: np.random.default_rng(20261006)
  * landmarks for test real frames computed once with the same MediaPipe get_landmarks() the original used on the fly,
    cached to landmarks_test_real.npz next to this script (new file; the original had no test landmark cache)

Outputs: C:\\My_Project\\AIGC\\ffpp_partedit\\test\\donor_v2\\<stem>__<part>.jpg (+ masks\\<same>.npz)
         results/research/partedit_20260927/manifest_test_donor_v2.tsv   (same 8 columns as the original manifest)
Verification + a 3x3 contact sheet (donor_v2_examples.jpg) are run at the end (--verify-only to run just those).

python gen_test_donor_v2.py            # CPU only
"""
import argparse
import csv
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import part_edit_gen as G  # noqa: E402  (loads landmarks_train.npz at import; not used for donors here)

BASE = Path(r"C:\My_Project\AIGC")
TEST_REAL = BASE / "FaceForensics_protocol_frames/test/real"
OUT = BASE / "ffpp_partedit/test/donor_v2"
SPLIT_DIR = BASE / "results/research/ffpp_unified_20260925"
MAN_OLD = HERE / "manifest_test_donor.tsv"
MAN_NEW = HERE / "manifest_test_donor_v2.tsv"
MAN_TRAIN = HERE / "manifest_train_donor.tsv"
LM_CACHE = HERE / "landmarks_test_real.npz"
SHEET = HERE / "donor_v2_examples.jpg"
SEED = 20261006


def read_tsv(p):
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def stem_of(path_str):
    return Path(path_str).stem


def test_real_stems():
    rows = read_tsv(SPLIT_DIR / "ffpp3_test.txt")
    stems = sorted(stem_of(r["path"]) for r in rows if r["label"] == "0")
    for s in stems:
        assert (TEST_REAL / f"{s}.jpg").is_file(), s
    return stems


def build_landmark_cache(stems):
    if LM_CACHE.is_file():
        d = np.load(LM_CACHE)
        if set(d.files) >= set(stems):
            return {s: d[s] for s in stems}
    print(f"computing MediaPipe landmarks for {len(stems)} test real frames ...", flush=True)
    lm = {}
    for i, s in enumerate(stems):
        img = np.ascontiguousarray(np.array(Image.open(TEST_REAL / f"{s}.jpg").convert("RGB")))
        l = G.get_landmarks(img)
        if l is not None:
            lm[s] = np.asarray(l, np.float32)[:, :2]
        if (i + 1) % 200 == 0:
            print(f"  {i + 1}/{len(stems)}", flush=True)
    np.savez_compressed(LM_CACHE, **lm)
    print(f"landmarks: {len(lm)} ok, {len(stems) - len(lm)} failed -> {LM_CACHE}", flush=True)
    return lm


def generate():
    t0 = time.time()
    old = read_tsv(MAN_OLD)
    assert len(old) == 3948, len(old)
    pool = test_real_stems()
    lm = build_landmark_cache(pool)
    pool = [s for s in pool if s in lm]  # donors need landmarks too
    print(f"donor pool: {len(pool)} test real frames / {len({s.split('__')[0] for s in pool})} videos", flush=True)

    # Redirect part_edit_gen's donor source (module globals used inside donor_edit) to the TEST pool.
    # The edit itself (affine on part landmarks, colour match, feathered blend, part_mask) is untouched.
    G.load = lambda stem: (np.array(Image.open(TEST_REAL / f"{stem}.jpg").convert("RGB")), lm[stem])

    (OUT / "masks").mkdir(parents=True, exist_ok=True)
    done = set()
    if MAN_NEW.is_file():
        done = {r["path"] for r in read_tsv(MAN_NEW)}
    else:
        MAN_NEW.write_text("path\tlabel\tvideo_id\tsource\tmask_path\tsrc_frame\tpart\tdonor\n", encoding="utf-8")
    rng = np.random.default_rng(SEED)
    n_ok = n_fail = n_skip = 0
    with open(MAN_NEW, "a", encoding="utf-8", newline="\n") as f:
        for r in old:
            stem, part, vid = stem_of(r["src_frame"]), r["part"], r["video_id"]
            assert stem.split("__")[0] == vid
            outp = OUT / f"{stem}__{part}.jpg"
            if str(outp) in done:
                n_skip += 1
                continue  # NB: rng stream then differs from a fresh run; delete the manifest for a clean rerun
            if stem not in lm:
                n_fail += 1; print(f"  no landmarks for target {stem}", flush=True); continue
            img = np.array(Image.open(TEST_REAL / f"{stem}.jpg").convert("RGB"))
            G.STEMS = [s for s in pool if s.split("__")[0] != vid]  # donor video != target video
            out, m, donor = G.donor_edit(img, lm[stem], part, rng)
            if out is None:
                n_fail += 1; print(f"  donor_edit failed for {stem} {part}", flush=True); continue
            assert donor.split("__")[0] != vid
            mp = OUT / "masks" / f"{stem}__{part}.npz"
            cv2.imwrite(str(outp), out[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 90])
            np.savez_compressed(mp, m=m)
            f.write("\t".join([str(outp), "1", vid, f"partedit:donor:{part}", str(mp),
                               str(TEST_REAL / f"{stem}.jpg"), part, donor]) + "\n"); f.flush()
            n_ok += 1
            if n_ok % 500 == 0:
                print(f"  donor_v2: {n_ok:,} ok, {n_fail} failed  ({time.time() - t0:.0f}s)", flush=True)
    print(f"DONE donor_v2: {n_ok:,} written, {n_fail} failed, {n_skip} skipped (already present); "
          f"{time.time() - t0:.0f}s", flush=True)


def verify():
    new = read_tsv(MAN_NEW)
    old = read_tsv(MAN_OLD)
    train_stems = {stem_of(r["path"]) for r in read_tsv(SPLIT_DIR / "ffpp3_train.txt")}
    test_real = set(test_real_stems())
    train_pairs = {(r["donor"], r["part"]) for r in read_tsv(MAN_TRAIN)}
    donors = [r["donor"] for r in new]
    rep = {
        "rows": len(new),
        "per_part": {p: sum(r["part"] == p for r in new) for p in ("eyes", "nose", "mouth")},
        "donor_in_ffpp3_train": sum(d in train_stems for d in donors),
        "donor_not_in_test_real": sum(d not in test_real for d in donors),
        "donor_video_eq_target_video": sum(r["donor"].split("__")[0] == r["video_id"] for r in new),
        "donor_part_pairs_in_manifest_train_donor": sum((r["donor"], r["part"]) in train_pairs for r in new),
        "unique_donor_frames": len(set(donors)),
        "unique_donor_videos": len({d.split("__")[0] for d in donors}),
        "same_targets_and_parts_as_old": [(stem_of(r["src_frame"]), r["part"]) for r in new]
                                          == [(stem_of(r["src_frame"]), r["part"]) for r in old],
        "files_missing": sum(not Path(r["path"]).is_file() or not Path(r["mask_path"]).is_file() for r in new),
    }
    for k, v in rep.items():
        print(f"{k}: {v}")

    # 3x3 contact sheet: each cell = target | mask overlay | edited (deterministic pick)
    rng = np.random.default_rng(SEED)
    pick = [new[i] for i in rng.choice(len(new), 9, replace=False)]
    cells = []
    for r in pick:
        tgt = np.array(Image.open(r["src_frame"]).convert("RGB"))
        ed = np.array(Image.open(r["path"]).convert("RGB"))
        m = np.load(r["mask_path"])["m"]
        ov = tgt.copy(); ov[m] = (0.4 * ov[m] + 0.6 * np.array([255, 60, 60])).astype(np.uint8)
        tiles = [cv2.resize(t, (160, 192), interpolation=cv2.INTER_AREA) for t in (tgt, ov, ed)]
        cell = np.concatenate(tiles, 1)
        hdr = np.full((22, cell.shape[1], 3), 255, np.uint8)
        cv2.putText(hdr, f"{stem_of(r['src_frame'])} {r['part']} <- {r['donor']}", (4, 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (30, 30, 30), 1, cv2.LINE_AA)
        cells.append(np.concatenate([hdr, cell], 0))
    rows = [np.concatenate(cells[i:i + 3], 1) for i in range(0, 9, 3)]
    top = np.full((24, rows[0].shape[1], 3), 255, np.uint8)
    cv2.putText(top, "donor_v2: target | GT mask | edited   (donors = FF++ test real frames only)", (6, 17),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (30, 30, 30), 1, cv2.LINE_AA)
    cv2.imwrite(str(SHEET), np.concatenate([top] + rows, 0)[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(f"contact sheet -> {SHEET}")
    return rep


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify-only", action="store_true")
    a = ap.parse_args()
    if not a.verify_only:
        generate()
    verify()
