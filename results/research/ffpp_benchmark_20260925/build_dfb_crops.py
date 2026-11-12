r"""Celeb-DF-v2 and DFD test frames cropped by DeepfakeBench's own preprocessing (2026-10-08; audit items 6 and 8).

Every published detector in our comparison was trained and tested by its authors on DeepfakeBench crops (dlib frontal face
detector, 81-landmark predictor, five-point similarity alignment, scale 1.3, 256 x 256, 32 frames per video by np.linspace).
Our standard sets use our own crop (landmark box + 35 % margin, aspect kept), which is what OUR models were trained on. To
compare each detector under the preprocessing it was built for, this script produces the DeepfakeBench crop of the same
videos, with the alignment function imported from the benchmark's own preprocess.py (no re-implementation).

python build_dfb_crops.py cdf|dfd [--workers 6]
  -> C:\My_Project\AIGC\FaceForensics_protocol_frames\<set>_dfb32\<video_id>__fNNNN.png
     splits/research/ffpp_benchmark_20260925/<set>_dfb32.txt (path, label, video_id), <set>_dfb32_manifest.json
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
B = Path(r"C:\My_Project\AIGC"); SP = B / "splits/research/ffpp_benchmark_20260925"; HERE = Path(__file__).resolve().parent
PRE = B / "external_baselines/DeepfakeBench/preprocessing"
_det = _pred = _fn = None


def _init():
    global _det, _pred, _fn
    import dlib
    sys.path.insert(0, str(PRE)); cwd = os.getcwd(); os.chdir(PRE)
    try:
        import preprocess as P   # DeepfakeBench/preprocessing/preprocess.py
    finally:
        os.chdir(cwd)
    _fn = P.extract_aligned_face_dlib; _det = dlib.get_frontal_face_detector(); _pred = dlib.shape_predictor(str(PRE / "dlib_tools/shape_predictor_81_face_landmarks.dat"))


def jobs_for(name):
    if name == "cdf":
        root = B / "Celeb-DF-v2"
        lst = [l.split() for l in (root / "List_of_testing_videos.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
        return [(str(root / rel), 1 - int(lab), rel.replace("/", "_").replace(".mp4", "")) for lab, rel in lst]   # the list marks real as 1
    root = B / "DFD_c23"
    return [(str(p), 0, "real_" + p.stem) for p in sorted((root / "real").glob("*.mp4"))] + [(str(p), 1, "fake_" + p.stem) for p in sorted((root / "fake").glob("*.mp4"))]


def work(job):
    import cv2
    import numpy as np
    src, label, vid, out_dir = job
    cap = cv2.VideoCapture(src); total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); rows = []; miss = 0
    if total <= 0:
        return vid, label, rows, 0, 0
    idxs = sorted(set(np.linspace(0, total - 1, 32, endpoint=True, dtype=int).tolist()))
    for fi in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi); ok, frame = cap.read()
        if not ok or frame is None:
            miss += 1; continue
        crop, _, _ = _fn(_det, _pred, frame)
        if crop is None:
            miss += 1; continue
        q = Path(out_dir) / f"{vid}__f{fi:04d}.png"; cv2.imwrite(str(q), crop); rows.append(str(q))
    cap.release(); return vid, label, rows, miss, len(idxs)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("name", choices=["cdf", "dfd"]); ap.add_argument("--workers", type=int, default=6); ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args(); out = B / "FaceForensics_protocol_frames" / f"{a.name}_dfb32"; out.mkdir(parents=True, exist_ok=True)
    jobs = [(s, l, v, str(out)) for s, l, v in jobs_for(a.name)][: a.limit or None]
    rows, rep = [], []
    with Pool(a.workers, initializer=_init) as pool:
        for i, (vid, label, r, miss, n) in enumerate(pool.imap_unordered(work, jobs), 1):
            rows += [(p, label, vid) for p in r]; rep.append({"video": vid, "label": label, "requested": n, "written": len(r), "no_face_or_decode": miss})
            if i % 25 == 0:
                print(f"  {i}/{len(jobs)} videos, {len(rows):,} frames", flush=True)
    rows.sort(key=lambda t: (t[1], t[2], t[0]))
    if not a.limit:
        (SP / f"{a.name}_dfb32.txt").write_text("path\tlabel\tvideo_id\n" + "\n".join(f"{p}\t{l}\t{v}" for p, l, v in rows) + "\n", encoding="utf-8")
        (HERE / f"{a.name}_dfb32_manifest.json").write_text(json.dumps({"videos": len(jobs), "videos_with_frames": sum(1 for r in rep if r["written"]), "frames": len(rows),
            "frames_requested": sum(r["requested"] for r in rep), "no_face_or_decode": sum(r["no_face_or_decode"] for r in rep), "per_video": sorted(rep, key=lambda r: r["video"])}, indent=1))
    print("done", a.name, len(rows), "frames from", sum(1 for r in rep if r["written"]), "of", len(jobs), "videos; requested", sum(r["requested"] for r in rep))


if __name__ == "__main__":
    main()
