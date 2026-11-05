"""v3 (2026-10-06): DFD standard test set rebuilt with a detection fallback so frames are no longer dropped.

Why v3 exists. `dfd_std32v2.txt` intended 332 videos x 32 uniform frames = 10,624 crops, but only 4,221 frames
from 235 videos came out (97 videos had zero frames, 54 a single frame). Diagnosis on 30 frames from zero-frame
videos (`diag_dfd.py`, 2026-10-06): every frame decoded fine (0 decode errors); the DFD clips are 1920x1080 and
the actor's face is only 88-164 px wide (5-8 % of the frame width). MediaPipe FaceLandmarker runs the *short-range*
BlazeFace detector internally and finds nothing on such frames -- 0/30 at the default confidence and still 0/30 with
min_face_detection_confidence=0.1. OpenCV YuNet found the face in 30/30 (score >= 0.92), and MediaPipe found full
landmarks in 30/30 once the YuNet region was upscaled 2x. So the dropout was a detector-scale failure, not a data
or decode problem, and it was biased: it removed the wide shots (street / cafe / hall / podium scenes) wholesale.

Recipe (unchanged from the rest of the project where possible):
  * same 332 videos (150 real / 182 fake .mp4 under DFD_c23), same 32 uniform indices as v2:
    round(i * (total-1) / 31), i = 0..31  (indices de-duplicated for clips shorter than 32 frames)
  * crop = landmark bounding box + 35 % margin per side, aspect kept (extract_ffpp_protocol_frames.MARGIN = 0.35)
  * tier 1 `mp_full`      : MediaPipe FaceLandmarker on the full frame (the v2 path)
  * tier 2 `mp_upscaled`  : YuNet locates the face; region (+50 % context) upscaled 2x; MediaPipe landmarks on that,
                            mapped back to full-frame coordinates; same 35 % crop from the ORIGINAL frame
  * tier 3 `box_only`     : YuNet box + 35 % margin directly (no landmarks)
  * `failed`              : no detector found a face (frame dropped, counted)
  * JPEG q95 -> FaceForensics_protocol_frames/dfd_std32v3/<video_id>__fNNNN.jpg

python build_dfd_standard_v3.py [--frames 32] [--workers 6]
  -> splits/research/ffpp_benchmark_20260925/dfd_std32v3.txt           (path, label, video_id)
     results/research/ffpp_benchmark_20260925/dfd_std32v3_manifest.json  (per-video counts by tier)
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")   # CPU only; the GPU is busy

BASE = Path(r"C:\My_Project\AIGC")
HERE = Path(__file__).resolve().parent
ROOT = BASE / "DFD_c23"
OUT_IMG = BASE / "FaceForensics_protocol_frames" / "dfd_std32v3"
OUT_SPLIT = BASE / "splits/research/ffpp_benchmark_20260925"
YUNET = BASE / "face_detection_yunet.onnx"
MARGIN = 0.35          # per side, fraction of landmark-bbox width / height (project standard)
CONTEXT = 0.50         # extra context around the YuNet box before the 2x upscale
UPSCALE = 2.0
JPEG_Q = 95
MIN_SIDE = 64

_lmk = None
_yunet = None


def _init():
    global _lmk, _yunet
    import cv2
    import mediapipe as mp  # noqa
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision
    sys.path.insert(0, str(BASE))
    import extract_ffpp_protocol_frames as base
    assert abs(base.MARGIN - MARGIN) < 1e-9, "crop margin drifted from the training extractor"
    with open(base.MODEL_PATH, "rb") as f:
        data = f.read()
    _lmk = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_buffer=data), num_faces=1))
    _yunet = cv2.FaceDetectorYN.create(str(YUNET), "", (320, 320), 0.5, 0.3, 5000)


def _landmarks(img_bgr):
    """Return (N,2) pixel landmarks in img coordinates, or None."""
    import cv2
    import mediapipe as mp
    import numpy as np
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    res = _lmk.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    if not res.face_landmarks:
        return None
    h, w = img_bgr.shape[:2]
    return np.array([[p.x * w, p.y * h] for p in res.face_landmarks[0]])


def _crop_box(frame, x0, y0, x1, y1):
    """35 % margin per side around (x0,y0,x1,y1), aspect kept, clamped to the frame."""
    h, w = frame.shape[:2]
    bw, bh = x1 - x0, y1 - y0
    x0 -= bw * MARGIN; x1 += bw * MARGIN
    y0 -= bh * MARGIN; y1 += bh * MARGIN
    x0, y0 = max(0, int(x0)), max(0, int(y0))
    x1, y1 = min(w, int(x1)), min(h, int(y1))
    if x1 <= x0 or y1 <= y0:
        return None
    return frame[y0:y1, x0:x1]


def _yunet_box(frame):
    import numpy as np
    _yunet.setInputSize((frame.shape[1], frame.shape[0]))
    _, faces = _yunet.detect(frame)
    if faces is None or len(faces) == 0:
        return None
    f = faces[int(np.argmax(faces[:, -1]))]        # highest-score face (MediaPipe num_faces=1 behaves alike)
    x, y, w, h = [float(t) for t in f[:4]]
    return x, y, w, h, float(f[-1])


def detect_and_crop_v3(frame):
    """Return (crop, tier). tier in {mp_full, mp_upscaled, box_only, failed}."""
    import cv2
    lm = _landmarks(frame)
    if lm is not None:
        c = _crop_box(frame, *lm.min(0), *lm.max(0))
        if c is not None:
            return c, "mp_full"
    yb = _yunet_box(frame)
    if yb is None:
        return None, "failed"
    x, y, w, h, _ = yb
    H, W = frame.shape[:2]
    sx0, sy0 = max(0, int(x - w * CONTEXT)), max(0, int(y - h * CONTEXT))
    sx1, sy1 = min(W, int(x + w * (1 + CONTEXT))), min(H, int(y + h * (1 + CONTEXT)))
    if sx1 > sx0 and sy1 > sy0:
        sub = frame[sy0:sy1, sx0:sx1]
        up = cv2.resize(sub, None, fx=UPSCALE, fy=UPSCALE, interpolation=cv2.INTER_CUBIC)
        lm = _landmarks(up)
        if lm is not None:
            lm = lm / UPSCALE
            lm[:, 0] += sx0; lm[:, 1] += sy0               # back to full-frame coordinates
            c = _crop_box(frame, *lm.min(0), *lm.max(0))   # crop from the ORIGINAL pixels, not the upscale
            if c is not None:
                return c, "mp_upscaled"
    c = _crop_box(frame, x, y, x + w, y + h)
    if c is not None:
        return c, "box_only"
    return None, "failed"


def work(job):
    import cv2
    rel, label, n_frames = job
    src = ROOT / rel
    vid = rel.replace("/", "_").replace(".mp4", "")
    OUT_IMG.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(src))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    rec = {"video": vid, "label": label, "total_frames": total, "requested": 0, "written": 0,
           "mp_full": 0, "mp_upscaled": 0, "box_only": 0, "failed": 0, "decode_fail": 0, "paths": []}
    if total <= 0:
        cap.release()
        rec["err"] = "unreadable"
        return rec
    idxs = sorted(set(int(round(i * (total - 1) / max(n_frames - 1, 1))) for i in range(n_frames)))
    rec["requested"] = len(idxs)
    for fi in idxs:
        q = OUT_IMG / f"{vid}__f{fi:04d}.jpg"
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ok, frame = cap.read()
        if not ok or frame is None:
            rec["decode_fail"] += 1
            continue
        crop, tier = detect_and_crop_v3(frame)
        if crop is None or crop.shape[0] < MIN_SIDE or crop.shape[1] < MIN_SIDE:
            rec["failed"] += 1
            continue
        cv2.imwrite(str(q), crop, [cv2.IMWRITE_JPEG_QUALITY, JPEG_Q])
        rec[tier] += 1
        rec["written"] += 1
        rec["paths"].append((str(q), fi, tier))
    cap.release()
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", type=int, default=32)
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    v2 = json.loads((HERE / "dfd_std32v2_manifest.json").read_text(encoding="utf-8"))
    jobs = [(f"real/{p.name}", 0, a.frames) for p in sorted((ROOT / "real").glob("*.mp4"))] + \
           [(f"fake/{p.name}", 1, a.frames) for p in sorted((ROOT / "fake").glob("*.mp4"))]
    assert len(jobs) == v2["n_videos"] == 332, (len(jobs), v2["n_videos"])
    # the v2 video set = videos that got frames in dfd_std32v2.txt + the videos v2 recorded as zero-frame
    v2_videos = set(v2["videos_with_zero_frames"])
    with open(OUT_SPLIT / "dfd_std32v2.txt", encoding="utf-8") as f:
        next(f)
        for line in f:
            v2_videos.add(line.rstrip("\n").split("\t")[2])
    disk = {j[0].replace("/", "_").replace(".mp4", "") for j in jobs}
    assert disk == v2_videos, f"video set differs from v2: +{sorted(disk - v2_videos)[:5]} -{sorted(v2_videos - disk)[:5]}"
    print(f"videos {len(jobs)}  real {sum(1 for j in jobs if j[1] == 0)}  fake {sum(1 for j in jobs if j[1] == 1)}"
          f"  frames/video {a.frames}", flush=True)
    OUT_SPLIT.mkdir(parents=True, exist_ok=True)

    rows, report = [], []
    with Pool(a.workers, initializer=_init) as pool:
        for i, r in enumerate(pool.imap_unordered(work, jobs), 1):
            paths = r.pop("paths")
            report.append(r)
            for p, fi, tier in paths:
                rows.append((p, r["label"], r["video"], fi, tier))
            if i % 25 == 0:
                print(f"  {i}/{len(jobs)} videos, {len(rows):,} frames", flush=True)

    rows.sort(key=lambda t: (t[1], t[2], t[3]))
    report.sort(key=lambda r: (r["label"], r["video"]))
    with open(OUT_SPLIT / "dfd_std32v3.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("path\tlabel\tvideo_id\n")
        for p, l, v, _, _ in rows:
            f.write(f"{p}\t{l}\t{v}\n")
    with open(OUT_SPLIT / "dfd_std32v3_tiers.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("path\tlabel\tvideo_id\tframe_idx\ttier\n")
        for p, l, v, fi, tier in rows:
            f.write(f"{p}\t{l}\t{v}\t{fi}\t{tier}\n")

    tiers = ["mp_full", "mp_upscaled", "box_only", "failed", "decode_fail"]
    written = [r["written"] for r in report]
    summ = {
        "n_videos": len(jobs), "n_videos_with_frames": sum(1 for w in written if w > 0),
        "n_frames_requested": sum(r["requested"] for r in report), "n_frames": len(rows),
        "n_real_frames": sum(1 for r in rows if r[1] == 0), "n_fake_frames": sum(1 for r in rows if r[1] == 1),
        "frames_per_video_target": a.frames,
        "frames_per_video_written": {"min": min(written), "median": sorted(written)[len(written) // 2],
                                     "max": max(written)},
        "by_tier": {t: sum(r[t] for r in report) for t in tiers},
        "videos_under_16_frames": [{"video": r["video"], "written": r["written"], "requested": r["requested"],
                                    "total_frames": r["total_frames"], "failed": r["failed"],
                                    "decode_fail": r["decode_fail"]} for r in report if r["written"] < 16],
        "crop": f"landmark bbox + {MARGIN:.2f} margin per side, aspect kept, JPEG q{JPEG_Q}; "
                f"fallback YuNet -> {UPSCALE:.0f}x upscale (+{CONTEXT:.0%} context) -> MediaPipe; else YuNet box + margin",
        "same_video_set_as_v2": sorted(r["video"] for r in report) == sorted(v2_videos),
        "per_video": report,
    }
    (HERE / "dfd_std32v3_manifest.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summ.items() if k not in ("per_video",)}, indent=1), flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
