"""Second beautification test source (PRE_DECLARED Addendum 14): the Celeb-DF-v2 standard frames (splits/research/
ffpp_benchmark_20260925/celebdf_std32v2.txt, 516 videos, genuine and deepfake) each get ONE of the eleven pilgram colour
filters that no RU model has ever trained on (same list as the FF++ held-out set), chosen per video by a fixed seed. The same
frame exists untreated, so every detector can be scored on the pair: AUC untreated vs filtered, and at 5 % FPR on untreated
genuine frames the rise in MISS (deepfakes not called fake) and in FA (genuine called fake). No re-encoding confound: the
filtered frame is saved as PNG from the untreated JPEG.
python build_cdf_filtered.py -> C:\My_Project\AIGC\cdf_filtered\<stem>__<filter>.png, splits/.../celebdf_std32v2_filtered.txt"""
import numpy as np, pilgram
from pathlib import Path
from PIL import Image
B = Path(r"C:\My_Project\AIGC"); SP = B / "splits/research/ffpp_benchmark_20260925"; OUT = B / "cdf_filtered"; OUT.mkdir(exist_ok=True)
HELD = ["brooklyn", "clarendon", "earlybird", "inkwell", "kelvin", "lofi", "mayfair", "moon", "perpetua", "reyes", "slumber"]
rows = [l.split("\t") for l in (SP / "celebdf_std32v2.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
vids = sorted(set(r[2] for r in rows)); rng = np.random.default_rng(20261006); vf = {v: HELD[int(rng.integers(0, len(HELD)))] for v in vids}
out = ["path\tlabel\tvideo_id\tfilter\tsource"]
for k, r in enumerate(rows):
    p = Path(r[0]); f = vf[r[2]]; dst = OUT / f"{p.stem}__{f}.png"
    if not dst.exists():
        getattr(pilgram, f)(Image.open(p).convert("RGB")).convert("RGB").save(dst)
    out.append(f"{dst}\t{r[1]}\t{r[2]}\t{f}\t{r[0]}")
    if k % 2000 == 0: print(k, flush=True)
(SP / "celebdf_std32v2_filtered.txt").write_text("\n".join(out) + "\n", encoding="utf-8"); print("done", len(rows), "frames", len(vids), "videos")
