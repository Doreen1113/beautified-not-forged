"""Build the STANDARD Celeb-DF-v2 cross-dataset test set: official 518-video test list, 32 uniform frames per video.

Why this exists: the set this project has been using (`celebdf_holdout_mp035.txt`) holds **389 frames from 307
videos** -- roughly one frame per video, pre-filtered by a MediaPipe confidence of 0.35. Filtering on face-detector
confidence selects the easy frames, and a 389-frame sample has wide variance. Measured against it, our own runs of
the published checkpoints came out 7-9 AUC points above every published frame-level number for the same models
(our Xception CDFv2 0.8063 vs a published 0.737; our RECCE DFD 0.9060 vs 0.812), landing on the published
*video-level* band instead. Relative comparisons within that set stay valid, but no number from it can be placed
beside a published frame-level figure.

Convention followed here, as standardised by DeepfakeBench (NeurIPS'23 D&B) and used by Forensics Adapter (CVPR'25)
and FMSD (2026): official test split, **32 uniformly spaced frames per video**, face crop, frame-level AUC.
Frames where no face is found are recorded and skipped -- with the count reported, not silently dropped.

python build_cdf_standard.py [--frames 32] [--workers 8]
  -> Celeb-DF-v2/frames_std32/<label>/<video>__f<idx>.jpg
     splits/research/ffpp_benchmark_20260925/celebdf_std32.txt   (path, label, video_id)
     cdf_std32_manifest.json
"""
import argparse
import json
import sys
from multiprocessing import Pool
from pathlib import Path

BASE = Path(r"C:\My_Project\AIGC")
HERE = Path(__file__).resolve().parent
ROOT = BASE / "Celeb-DF-v2"
OUT_IMG = ROOT / "frames_std32"
OUT_SPLIT = BASE / "splits/research/ffpp_benchmark_20260925"
MARGIN = 1.3          # face-crop margin, matching this project's other extractions


def _init():
    global _lm
    sys.path.insert(0, str(BASE))
    import pipeline as P
    _lm = P._detect_landmarks


def work(job):
    import cv2
    import numpy as np
    from PIL import Image
    rel, label, n_frames = job
    src = ROOT / rel
    vid = rel.replace("/", "_").replace(".mp4", "")
    out_dir = OUT_IMG / ("fake" if label == 1 else "real")
    out_dir.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(src))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        cap.release()
        return {"video": vid, "label": label, "kept": 0, "err": "unreadable"}
    idxs = [int(round(i * (total - 1) / max(n_frames - 1, 1))) for i in range(n_frames)]
    kept, noface = [], 0
    for k, fi in enumerate(idxs):
        q = out_dir / f"{vid}__f{k:02d}.jpg"
        if q.exists():
            kept.append(str(q)); continue
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ok, frame = cap.read()
        if not ok:
            noface += 1; continue
        pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        lm = _lm(pil)
        if lm is None:
            noface += 1; continue
        h, w = frame.shape[:2]
        xs = [p.x * w for p in lm]; ys = [p.y * h for p in lm]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        side = max(max(xs) - min(xs), max(ys) - min(ys)) * MARGIN / 2
        x0, y0 = int(max(cx - side, 0)), int(max(cy - side, 0))
        x1, y1 = int(min(cx + side, w)), int(min(cy + side, h))
        if x1 - x0 < 32 or y1 - y0 < 32:
            noface += 1; continue
        Image.fromarray(cv2.cvtColor(frame[y0:y1, x0:x1], cv2.COLOR_BGR2RGB)).save(q, quality=95)
        kept.append(str(q))
    cap.release()
    return {"video": vid, "label": label, "kept": len(kept), "noface": noface, "paths": kept}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=32)
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    lst = [l.split() for l in (ROOT / "List_of_testing_videos.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
    # the official list uses 1 = real, 0 = fake; this project uses 1 = fake everywhere, so it is inverted here once
    jobs = [(rel, 0 if flag == "1" else 1, a.frames) for flag, rel in lst]
    print(f"videos {len(jobs)}  real {sum(1 for j in jobs if j[1] == 0)}  fake {sum(1 for j in jobs if j[1] == 1)}"
          f"  frames/video {a.frames}", flush=True)
    OUT_SPLIT.mkdir(parents=True, exist_ok=True)

    rows, report = [], []
    with Pool(a.workers, initializer=_init) as pool:
        for i, r in enumerate(pool.imap_unordered(work, jobs), 1):
            report.append({k: v for k, v in r.items() if k != "paths"})
            for p in r.get("paths", []):
                rows.append((p, r["label"], r["video"]))
            if i % 50 == 0:
                print(f"  {i}/{len(jobs)} videos, {len(rows):,} frames", flush=True)

    with open(OUT_SPLIT / "celebdf_std32.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("path\tlabel\tvideo_id\n")
        for p, l, v in rows:
            f.write(f"{p}\t{l}\t{v}\n")
    summ = {"n_videos": len(jobs), "n_frames": len(rows), "frames_per_video": a.frames,
            "n_real_frames": sum(1 for r in rows if r[1] == 0),
            "n_fake_frames": sum(1 for r in rows if r[1] == 1),
            "videos_with_zero_frames": [r["video"] for r in report if r["kept"] == 0],
            "total_noface_skipped": sum(r.get("noface", 0) for r in report),
            "convention": "DeepfakeBench standard: official 518-video test list, 32 uniform frames/video, "
                          "face crop margin 1.3, frame-level AUC"}
    (HERE / "cdf_std32_manifest.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summ.items() if k != "videos_with_zero_frames"}, indent=1), flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
