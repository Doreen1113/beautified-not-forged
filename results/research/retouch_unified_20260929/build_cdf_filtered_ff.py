r"""Celeb-DF-v2 + eleven held-out filters, filter applied to the FULL frame before the face crop (Addendum 23 validity fix;
companion of build_dfd_filtered_ff.py). Every standard frame (celebdf_std32v2.txt, 516 videos x 32 frames, frame k of 32 ->
index round(k*(total-1)/31)) is re-decoded, the MediaPipe landmark box with the 35 % margin is recomputed exactly as in
extract_ffpp_protocol_frames.detect_and_crop, the filter is applied to the whole frame and the same box is cropped. Same
per-video filter assignment as build_cdf_filtered.py (seed 20261006 over the sorted video ids). The untreated recrop must
match the stored crop's shape, otherwise the frame is dropped and counted.
python build_cdf_filtered_ff.py [--workers 6] [--limit N]
  -> C:\My_Project\AIGC\cdf_filtered_ff\<stem>__<filter>.png, splits/.../celebdf_std32v2_filteredff.txt, cdf_filtered_ff_manifest.json
"""
import argparse
import json
import os
import re
import sys
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
B = Path(r"C:\My_Project\AIGC"); SP = B / "splits/research/ffpp_benchmark_20260925"; OUT = B / "cdf_filtered_ff"; HERE = Path(__file__).resolve().parent
HELD = ["brooklyn", "clarendon", "earlybird", "inkwell", "kelvin", "lofi", "mayfair", "moon", "perpetua", "reyes", "slumber"]
_E = None


def _init():
    global _E
    sys.path.insert(0, str(B)); import extract_ffpp_protocol_frames as E; _E = E


def box_of(frame):
    """The integer crop box that extract_ffpp_protocol_frames.detect_and_crop would use (same arithmetic), or None."""
    import cv2
    import mediapipe as mp
    import numpy as np
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    res = _E._get_landmarker().detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    if not res.face_landmarks:
        return None
    h, w = frame.shape[:2]; lm = np.array([[p.x * w, p.y * h] for p in res.face_landmarks[0]])
    x0, y0 = lm.min(axis=0); x1, y1 = lm.max(axis=0); bw, bh = x1 - x0, y1 - y0
    x0 -= bw * _E.MARGIN; x1 += bw * _E.MARGIN; y0 -= bh * _E.MARGIN; y1 += bh * _E.MARGIN
    x0, y0 = max(0, int(x0)), max(0, int(y0)); x1, y1 = min(w, int(x1)), min(h, int(y1))
    return None if x1 <= x0 or y1 <= y0 else (x0, y0, x1, y1)


def work(job):
    import cv2
    import pilgram
    from PIL import Image
    vid, label, filt, items = job
    rel = vid.replace("_", "/", 1) + ".mp4"   # "Celeb-real_id0_0000" -> "Celeb-real/id0_0000.mp4"
    cap = cv2.VideoCapture(str(B / "Celeb-DF-v2" / rel)); total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); rows = []; bad = 0
    for path, k in items:
        fi = int(round(k * (total - 1) / 31)); cap.set(cv2.CAP_PROP_POS_FRAMES, fi); ok, frame = cap.read()
        if not ok or frame is None:
            bad += 1; continue
        bx = box_of(frame); st = cv2.imread(path)
        if bx is None or st is None or st.shape[:2] != (bx[3] - bx[1], bx[2] - bx[0]):
            bad += 1; continue
        full = getattr(pilgram, filt)(Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))).convert("RGB")
        dst = OUT / f"{Path(path).stem}__{filt}.png"; full.crop(bx).save(dst); rows.append((str(dst), label, vid, filt, path))
    cap.release(); return vid, rows, bad, len(items)


def main():
    import numpy as np
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=6); ap.add_argument("--limit", type=int, default=0); a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    std = [l.split("\t") for l in (SP / "celebdf_std32v2.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    vids = sorted(set(r[2] for r in std)); rng = np.random.default_rng(20261006); vf = {v: HELD[int(rng.integers(0, len(HELD)))] for v in vids}
    old = {l.split("\t")[2]: l.split("\t")[3] for l in (SP / "celebdf_std32v2_filtered.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()}
    assert all(old[v] == vf[v] for v in vids), "filter assignment differs from the crop-level version"
    by = {}
    for p, l, v in std:
        k = int(re.search(r"__f(\d+)\.jpg$", p).group(1)); by.setdefault(v, [l, []])[1].append((p, k))
    jobs = [(v, by[v][0], vf[v], by[v][1]) for v in vids][: a.limit or None]
    rows, bad, n = [], 0, 0
    with Pool(a.workers, initializer=_init) as pool:
        for i, (vid, r, b, k) in enumerate(pool.imap_unordered(work, jobs), 1):
            rows += r; bad += b; n += k
            if i % 25 == 0:
                print(f"  {i}/{len(jobs)} videos, {len(rows):,} frames, {bad} dropped", flush=True)
    rows.sort(key=lambda x: (x[1], x[2], x[0]))
    if not a.limit:
        (SP / "celebdf_std32v2_filteredff.txt").write_text("path\tlabel\tvideo_id\tfilter\tsource\n" + "\n".join("\t".join(x) for x in rows) + "\n", encoding="utf-8")
        (HERE / "cdf_filtered_ff_manifest.json").write_text(json.dumps({"frames_requested": n, "frames_written": len(rows), "dropped": bad, "videos": len(jobs)}, indent=1))
    print("done", len(rows), "of", n, "frames;", bad, "dropped")


if __name__ == "__main__":
    main()
