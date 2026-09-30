"""Celeb-DF-B frames with the FF++ training crop (PRE_DECLARED §2) + Addendum 1 letterbox trim (v3).

python extract_cdfb_v2.py [--workers 4]
  -> external_data/celebdfb/frames_std32v2/<folder>/<video>__f<k>.jpg
     splits/research/celebdfb_v2_20260927/cdfb_std32v2.txt  (path, label, video_id, folder, preset)
     extract_manifest.json
"""
import argparse
import cv2
import numpy as np
import json
import sys
from multiprocessing import Pool
from pathlib import Path

BASE = Path(r"C:\My_Project\AIGC")
HERE = Path(__file__).resolve().parent
D = BASE / "external_data/celebdfb/Celeb-DF-B"
OUT = BASE / "external_data/celebdfb/frames_std32v3"
SPLIT = BASE / "splits/research/celebdfb_v2_20260927"
FOLDERS = ["real", "real_beautified", "real_compressed", "synthesis", "synthesis_beautified", "synthesis_compressed"]


def _init():
    global _crop
    sys.path.insert(0, str(BASE))
    import extract_ffpp_protocol_frames as e
    _crop = e.detect_and_crop


def unletterbox(fr, std_thr=10.0):
    """Addendum 1: trim uniform bars (Celeb-DF-B treated videos are re-framed to portrait; the bars are tinted by
    the filter, not black) before face detection. A row/column is a bar if its grey-level std is < std_thr."""
    g = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY).astype(np.float32)
    rows = g.std(axis=1) >= std_thr; cols = g.std(axis=0) >= std_thr
    if rows.sum() < 32 or cols.sum() < 32:
        return fr
    r0, r1 = rows.argmax(), len(rows) - rows[::-1].argmax(); c0, c1 = cols.argmax(), len(cols) - cols[::-1].argmax()
    return fr[r0:r1, c0:c1]


def work(job):
    import cv2
    import numpy as np
    folder, name, n = job
    vid = name[:-4]
    od = OUT / folder; od.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(D / folder / name))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        return {"folder": folder, "video": vid, "kept": [], "noface": 0, "err": "unreadable"}
    lo, hi = int(total * 0.10), int(total * 0.90)
    if hi - lo < n:
        lo, hi = 0, max(total - 1, 1)
    idxs = np.linspace(lo, max(hi - 1, lo), n).astype(int).tolist()
    kept, noface = [], 0
    for k, fi in enumerate(idxs):
        q = od / f"{vid}__f{k:02d}.jpg"
        if q.exists():
            kept.append(str(q)); continue
        cap.set(cv2.CAP_PROP_POS_FRAMES, fi)
        ok, fr = cap.read()
        c = _crop(unletterbox(fr)) if ok else None
        if c is None or c.shape[0] < 64 or c.shape[1] < 64:
            noface += 1; continue
        cv2.imwrite(str(q), c, [cv2.IMWRITE_JPEG_QUALITY, 90]); kept.append(str(q))
    cap.release()
    return {"folder": folder, "video": vid, "kept": kept, "noface": noface}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--workers", type=int, default=4); ap.add_argument("--frames", type=int, default=32)
    a = ap.parse_args()
    preset = {}
    for l in (D / "annotation.csv").read_text(encoding="utf-8").splitlines()[1:]:
        n, t, p = l.strip().split(";")
        preset[(n, t)] = p
    jobs = [(f, n.name, a.frames) for f in FOLDERS for n in sorted((D / f).glob("*.mp4"))]
    print(f"videos {len(jobs)}", flush=True)
    SPLIT.mkdir(parents=True, exist_ok=True)
    rows, rep = [], []
    with Pool(a.workers, initializer=_init) as pool:
        for i, r in enumerate(pool.imap_unordered(work, jobs), 1):
            side = "real" if r["folder"].startswith("real") else "synthesis"
            pr = preset.get((r["video"] + ".mp4", side), "")
            for p in r["kept"]:
                rows.append((p, 0 if side == "real" else 1, r["video"], r["folder"], pr))
            rep.append({"folder": r["folder"], "video": r["video"], "kept": len(r["kept"]), "noface": r["noface"]})
            if i % 100 == 0:
                print(f"  {i}/{len(jobs)} videos, {len(rows):,} frames", flush=True)
    rows.sort()
    with open(SPLIT / "cdfb_std32v3.txt", "w", encoding="utf-8", newline="\n") as f:
        f.write("path\tlabel\tvideo_id\tfolder\tpreset\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    summ = {"n_videos": len(jobs), "n_frames": len(rows),
            "per_folder": {fo: sum(1 for r in rows if r[3] == fo) for fo in FOLDERS},
            "noface_per_folder": {fo: sum(x["noface"] for x in rep if x["folder"] == fo) for fo in FOLDERS},
            "zero_frame_videos": [f"{x['folder']}/{x['video']}" for x in rep if x["kept"] == 0],
            "presets_seen": sorted({r[4] for r in rows})}
    (HERE / "extract_manifest_v3.json").write_text(json.dumps(summ, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in summ.items() if k != "zero_frame_videos"}, indent=1), "\nDONE", flush=True)


if __name__ == "__main__":
    main()
