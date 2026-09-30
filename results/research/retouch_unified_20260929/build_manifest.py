"""Training / validation manifests for RU (PRE_DECLARED §1). Run after download_ffhq_part7, prep_ffhq and measure_pairs
(tencent, megvii) have finished.

Rows (TSV): path  cls  src  x0 y0 x1 y1  pres(4, '-' unknown)  q(4, '-' unknown)  stem
  cls 0 real / 1 fake / 2 filter;  src in {ffhq_orig, ffpp_real, tencent, megvii, ffpp_fake, ffpp_filter}
  box in the image's own pixel coordinates (Tencent 512 renders use the original's box / 2); '-' = whole image.
Vendor VALIDATION split: 10 % of the FFHQ Part7 base indices (deterministic hash) — their originals AND their Tencent/Megvii
renders go to manifest_val.tsv, never to train.

python build_manifest.py -> manifest_train.tsv, manifest_val.tsv, manifest_stats.json
"""
import ast
import hashlib
import json
import re
from pathlib import Path

import numpy as np

BASE = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent
UNI = BASE / "results/research/ffpp_unified_20260925"
OPS = ["eye", "jaw", "white", "smooth"]
NAME2OP = {"eye_enlarging": "eye", "face_reshaping_slim": "jaw", "whitening": "white", "smoothing": "smooth"}


def is_val(stem):
    return int(hashlib.md5(stem.encode()).hexdigest(), 16) % 10 == 0


def fmt(v):
    return "-" if v is None else " ".join(f"{x:.4f}" for x in v)


def read_pairs(name):
    f = HERE / f"pairs_{name}.tsv"
    if not f.is_file():
        return {}
    rows = [l.split("\t") for l in f.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    out = {}
    for r in rows:   # q = (eye_ratio-1, 1-jaw_ratio, dL/20, 1-hf_ratio)
        out[r[1]] = [float(r[3]) - 1, 1 - float(r[4]), float(r[5]) / 20, 1 - float(r[6])]
    return out


def main():
    boxes = json.loads((HERE / "ffhq_boxes.json").read_text())
    lm = np.load(HERE / "ffhq_landmarks.npz"); have_lm = set(lm.files)
    tr, va, stats = [], [], {}

    def add(row, stem):
        (va if is_val(stem) else tr).append(row)

    # FFHQ Part7 originals (real, and synthesis bases)
    n = 0
    for p in sorted((BASE / "ffhq_originals/Part7").glob("*.png")):
        if p.stem not in have_lm:
            continue
        b = boxes[p.stem]; add(f"{p}\t0\tffhq_orig\t{' '.join(map(str, b))}\t{fmt([0, 0, 0, 0])}\t{fmt([0, 0, 0, 0])}\t{p.stem}", p.stem); n += 1
    stats["ffhq_orig"] = n
    # Tencent (512) and Megvii (1024) composites, clean lists, measured q
    for src, root, scale in (("tencent", BASE / "FFHQ_four_process", 0.5), ("megvii", BASE / "FFHQ_megvii_four_process", 1.0)):
        q = read_pairs(src); n = m = 0
        for line in (root / "clean_output/clean_paths.txt").read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            stem = re.search(r"(\d{5})\.png$", line).group(1)
            if stem not in boxes:
                continue
            b = [int(round(v * scale)) for v in boxes[stem]]
            qq = q.get(line); m += qq is not None
            add(f"{line}\t2\t{src}\t{' '.join(map(str, b))}\t{fmt([1, 1, 1, 1])}\t{fmt(qq)}\t{stem}", stem); n += 1
        stats[src] = n; stats[src + "_with_q"] = m
    # RU2: vendor single-operation components (decompose.py), 512 px whole images -> box / 2
    n = m = 0
    for f in sorted(HERE.glob("decomp_*_[0-9].tsv")):
        for l in f.read_text(encoding="utf-8").splitlines()[1:]:
            r = l.split("	")
            if len(r) < 9:
                continue
            comp, orig, _, op = r[:4]; stem = Path(orig).stem
            if stem not in boxes:
                continue
            eye, jaw, dL, hf = map(float, r[4:8]); j = OPS.index(op)
            meas = [eye - 1, 1 - jaw, dL / 20, 1 - hf]; q = [0.0, 0.0, 0.0, 0.0]; q[j] = meas[j]
            pres = [0, 0, 0, 0]; pres[j] = 1
            b = [int(round(v * 0.5)) for v in boxes[stem]]
            add(f"{comp}	2	vendor_single	{' '.join(map(str, b))}	{fmt(pres)}	{fmt(q)}	{stem}", stem); n += 1
    stats["vendor_single"] = n
    # FF++ train rows (already face crops; landmarks cached for reals in fasb)
    rows = [l.split("\t") for l in (UNI / "ffpp3_train.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    c = {"0": 0, "1": 0, "2": 0}
    for r in rows:
        y = r[1]; c[y] += 1
        if y == "0":
            tr.append(f"{r[0]}\t0\tffpp_real\t-\t{fmt([0, 0, 0, 0])}\t{fmt([0, 0, 0, 0])}\t{Path(r[0]).stem}")
        elif y == "1":
            tr.append(f"{r[0]}\t1\tffpp_fake\t-\t-\t-\t{Path(r[0]).stem}")
        else:
            op = next((v for k, v in NAME2OP.items() if k in r[0]), None)
            pres = [0, 0, 0, 0]
            if op:
                pres[OPS.index(op)] = 1
            tr.append(f"{r[0]}\t2\tffpp_filter\t-\t{fmt(pres)}\t-\t{Path(r[0]).stem}")
    stats["ffpp_train"] = c
    hdr = "path\tcls\tsrc\tbox\tpres\tq\tstem\n"
    (HERE / "manifest_train.tsv").write_text(hdr + "\n".join(tr) + "\n", encoding="utf-8")
    (HERE / "manifest_val.tsv").write_text(hdr + "\n".join(va) + "\n", encoding="utf-8")
    stats["train_rows"], stats["val_rows"] = len(tr), len(va)
    (HERE / "manifest_stats.json").write_text(json.dumps(stats, indent=1)); print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
