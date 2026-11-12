"""Fresh colour-filter test source (PRE_DECLARED Addendum 16): DFD v3 standard frames, one filter per video (seed 20261007)
from sixteen filters used neither in training nor in the Celeb-DF-v2 diagnosis: the fourteen pilgram2 filters absent from
pilgram, PIL grayscale (BT.601) and the standard sepia matrix. Filtered frame saved as PNG from the untreated JPEG.
python build_dfd_filtered.py -> C:\My_Project\AIGC\dfd_filtered\<stem>__<filter>.png, splits/.../dfd_std32v3_filtered.txt"""
import numpy as np, pilgram2
from pathlib import Path
from PIL import Image
B = Path(r"C:\My_Project\AIGC"); SP = B / "splits/research/ffpp_benchmark_20260925"; OUT = B / "dfd_filtered"; OUT.mkdir(exist_ok=True)
P2 = ["amaro", "ashby", "charmes", "crema", "dogpatch", "ginza", "hefe", "helena", "juno", "ludwig", "poprocket", "sierra", "skyline", "sutro"]
SEPIA = (0.393, 0.769, 0.189, 0, 0.349, 0.686, 0.168, 0, 0.272, 0.534, 0.131, 0)
FILT = {**{n: getattr(pilgram2, n) for n in P2}, "grayscale": lambda im: im.convert("L").convert("RGB"), "sepia": lambda im: im.convert("RGB", SEPIA)}
NAMES = P2 + ["grayscale", "sepia"]
rows = [l.split("\t") for l in (SP / "dfd_std32v3.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
vids = sorted(set(r[2] for r in rows)); rng = np.random.default_rng(20261007); vf = {v: NAMES[int(rng.integers(0, len(NAMES)))] for v in vids}
out = ["path\tlabel\tvideo_id\tfilter\tsource"]
for k, r in enumerate(rows):
    p = Path(r[0]); f = vf[r[2]]; dst = OUT / f"{p.stem}__{f}.png"
    if not dst.exists():
        FILT[f](Image.open(p).convert("RGB")).convert("RGB").save(dst)
    out.append(f"{dst}\t{r[1]}\t{r[2]}\t{f}\t{r[0]}")
    if k % 2000 == 0: print(k, flush=True)
(SP / "dfd_std32v3_filtered.txt").write_text("\n".join(out) + "\n", encoding="utf-8"); print("done", len(rows), "frames", len(vids), "videos")
