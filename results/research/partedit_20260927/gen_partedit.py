"""Large-scale part-edit generation (PRE_DECLARED cgd §3). Resumable; writes a TSV manifest + one .npz mask per image.

python gen_partedit.py --partition train --mech donor --n 41510       # one random part per photograph
python gen_partedit.py --partition train --mech sd    --n 20000
python gen_partedit.py --partition test  --mech donor --all-parts     # every part for every test real frame
python gen_partedit.py --partition test  --mech sd    --all-parts

Outputs: ffpp_partedit/<partition>/<mech>/<stem>__<part>.jpg (+ masks/<same>.npz), manifest_<partition>_<mech>.tsv
Test-partition landmarks are computed here (train ones come from fasb landmarks_train.npz).
"""
import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import part_edit_gen as G  # noqa: E402

BASE = Path(r"C:\My_Project\AIGC")
OUT = BASE / "ffpp_partedit"
TEST_REAL = BASE / "FaceForensics_protocol_frames/test/real"


def items(partition, all_parts, n, rng):
    if partition == "train":
        stems = list(G.STEMS)
        src = lambda s: (G.REAL / f"{s}.jpg", G.LM[s][:, :2].astype(np.float32))
    else:
        stems = sorted(p.stem for p in TEST_REAL.glob("*.jpg"))
        src = lambda s: (TEST_REAL / f"{s}.jpg", None)
    rng.shuffle(stems)
    if not all_parts:
        stems = stems[:n]
    for s in stems:
        parts = ("eyes", "nose", "mouth") if all_parts else (["eyes", "nose", "mouth"][int(rng.integers(0, 3))],)
        for part in parts:
            yield s, part, src(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--partition", required=True, choices=["train", "test"])
    ap.add_argument("--mech", required=True, choices=["donor", "sd", "sdxl"])
    ap.add_argument("--n", type=int, default=10 ** 9)
    ap.add_argument("--all-parts", action="store_true")
    ap.add_argument("--seed", type=int, default=20260927)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed + {"donor": 0, "sd": 1, "sdxl": 2}[a.mech] + (0 if a.partition == "train" else 7))
    od = OUT / a.partition / a.mech; (od / "masks").mkdir(parents=True, exist_ok=True)
    man = HERE / f"manifest_{a.partition}_{a.mech}.tsv"
    done = set()
    if man.is_file():
        done = {l.split("\t")[0] for l in man.read_text(encoding="utf-8").splitlines()[1:]}
    else:
        man.write_text("path\tlabel\tvideo_id\tsource\tmask_path\tsrc_frame\tpart\tdonor\n", encoding="utf-8")
    f = open(man, "a", encoding="utf-8", newline="\n")
    n_ok = n_fail = 0
    for stem, part, (path, lm) in items(a.partition, a.all_parts, a.n, rng):
        outp = od / f"{stem}__{part}.jpg"
        if str(outp) in done:
            continue
        img = np.array(Image.open(path).convert("RGB"))
        if lm is None:
            lm = G.get_landmarks(np.ascontiguousarray(img))
            if lm is None:
                n_fail += 1; continue
            lm = np.asarray(lm, np.float32)[:, :2]
        if a.mech == "donor":
            out, m, donor = G.donor_edit(img, lm, part, rng)
        elif a.mech == "sd":
            out, m = G.inpaint_edit(img, lm, part, rng); donor = "sd15-inpaint"
        else:
            out, m = G.inpaint_edit(img, lm, part, rng, xl=True); donor = "sdxl-inpaint"
        if out is None:
            n_fail += 1; continue
        cv2.imwrite(str(outp), out[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 90])
        np.savez_compressed(od / "masks" / f"{stem}__{part}.npz", m=m)
        vid = stem.split("__")[0]
        f.write("\t".join([str(outp), "1", vid, f"partedit:{a.mech}:{part}", str(od / "masks" / f"{stem}__{part}.npz"),
                           str(path), part, str(donor)]) + "\n"); f.flush()
        n_ok += 1
        if n_ok % 200 == 0:
            print(f"  {a.partition}/{a.mech}: {n_ok:,} ok, {n_fail} rejected", flush=True)
    print(f"DONE {a.partition}/{a.mech}: {n_ok:,} written, {n_fail} rejected", flush=True)


if __name__ == "__main__":
    main()
