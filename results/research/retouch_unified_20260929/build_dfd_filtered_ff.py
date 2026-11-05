r"""DFD + sixteen fresh filters, filter applied to the FULL video frame before the face crop (PRE_DECLARED Addendum 23, validity fix).

`build_dfd_filtered.py` filtered the face crop, so a vignette was centred on the face. Here every standard frame is re-decoded
from its video, the face box is found by the same detector cascade as build_dfd_standard_v3 (deterministic), the filter is
applied to the whole 1920x1080 frame, and the same box is cropped. Same sixteen filters, same per-video assignment (seed
20261007 over the sorted video ids), so the two versions differ only in where the filter is applied. The untreated crop is
re-derived in the same pass and compared with the stored standard crop (shape must match) as a consistency check.
python build_dfd_filtered_ff.py [--workers 6]
  -> C:\My_Project\AIGC\dfd_filtered_ff\<stem>__<filter>.png, splits/.../dfd_std32v3_filteredff.txt, dfd_filtered_ff_manifest.json
"""
import argparse
import json
import os
import sys
from multiprocessing import Pool
from pathlib import Path

os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
B = Path(r"C:\My_Project\AIGC"); SP = B / "splits/research/ffpp_benchmark_20260925"; OUT = B / "dfd_filtered_ff"; HERE = Path(__file__).resolve().parent
P2 = ["amaro", "ashby", "charmes", "crema", "dogpatch", "ginza", "hefe", "helena", "juno", "ludwig", "poprocket", "sierra", "skyline", "sutro"]
SEPIA = (0.393, 0.769, 0.189, 0, 0.349, 0.686, 0.168, 0, 0.272, 0.534, 0.131, 0)
NAMES = P2 + ["grayscale", "sepia"]
_V = None; _box = {}


def _init():
    global _V
    sys.path.insert(0, str(B / "results/research/ffpp_benchmark_20260925"))
    import build_dfd_standard_v3 as V
    V._init(); orig = V._crop_box

    def rec(frame, x0, y0, x1, y1):   # same arithmetic as V._crop_box, but remember the integer box
        h, w = frame.shape[:2]; bw, bh = x1 - x0, y1 - y0
        a0, a1 = x0 - bw * V.MARGIN, x1 + bw * V.MARGIN; b0, b1 = y0 - bh * V.MARGIN, y1 + bh * V.MARGIN
        a0, b0 = max(0, int(a0)), max(0, int(b0)); a1, b1 = min(w, int(a1)), min(h, int(b1))
        out = orig(frame, x0, y0, x1, y1)
        if out is not None:
            _box["b"] = (a0, b0, a1, b1)
        return out
    V._crop_box = rec; _V = V


def apply_filter(name, im):
    import pilgram2
    if name == "grayscale":
        return im.convert("L").convert("RGB")
    if name == "sepia":
        return im.convert("RGB", SEPIA)
    return getattr(pilgram2, name)(im).convert("RGB")


def work(job):
    import cv2
    import numpy as np
    from PIL import Image
    vid, label, filt, items = job   # items: [(stored crop path, frame index)]
    rel = ("real/" if vid.startswith("real_") else "fake/") + vid.split("_", 1)[1] + ".mp4"
    cap = cv2.VideoCapture(str(B / "DFD_c23" / rel)); rows = []; bad = 0
    for path, fi in items:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi); ok, frame = cap.read()
        if not ok or frame is None:
            bad += 1; continue
        _box.pop("b", None); crop, tier = _V.detect_and_crop_v3(frame)
        if crop is None or "b" not in _box:
            bad += 1; continue
        x0, y0, x1, y1 = _box["b"]; st = cv2.imread(path)
        if st is None or st.shape[:2] != (y1 - y0, x1 - x0):
            bad += 1; continue
        full = apply_filter(filt, Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
        dst = OUT / f"{Path(path).stem}__{filt}.png"; full.crop((x0, y0, x1, y1)).save(dst)
        rows.append((str(dst), label, vid, filt, path))
    cap.release(); return vid, rows, bad, len(items)


def main():
    import numpy as np
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=6); ap.add_argument("--limit", type=int, default=0); a = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    t = [l.split("\t") for l in (SP / "dfd_std32v3_tiers.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    vids = sorted(set(r[2] for r in t)); rng = np.random.default_rng(20261007); vf = {v: NAMES[int(rng.integers(0, len(NAMES)))] for v in vids}
    old = {l.split("\t")[2]: l.split("\t")[3] for l in (SP / "dfd_std32v3_filtered.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()}
    assert all(old[v] == vf[v] for v in vids), "filter assignment differs from the crop-level version"
    by = {}
    for p, l, v, fi, _ in t:
        by.setdefault(v, [l, []])[1].append((p, int(fi)))
    jobs = [(v, by[v][0], vf[v], by[v][1]) for v in vids][: a.limit or None]
    rows, bad, n = [], 0, 0
    with Pool(a.workers, initializer=_init) as pool:
        for i, (vid, r, b, k) in enumerate(pool.imap_unordered(work, jobs), 1):
            rows += r; bad += b; n += k
            if i % 20 == 0:
                print(f"  {i}/{len(jobs)} videos, {len(rows):,} frames, {bad} mismatched", flush=True)
    rows.sort(key=lambda x: (x[1], x[2], x[0]))
    if not a.limit:
        (SP / "dfd_std32v3_filteredff.txt").write_text("path\tlabel\tvideo_id\tfilter\tsource\n" + "\n".join("\t".join(x) for x in rows) + "\n", encoding="utf-8")
        (HERE / "dfd_filtered_ff_manifest.json").write_text(json.dumps({"frames_requested": n, "frames_written": len(rows), "mismatched_or_failed": bad, "videos": len(jobs)}, indent=1))
    print("done", len(rows), "of", n, "frames;", bad, "mismatched or failed")


if __name__ == "__main__":
    main()
