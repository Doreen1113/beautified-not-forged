"""Controlled pairs for the Instagram AR-filter test: FairBeauty validation image and its own FairFace original (padding
1.25), each cropped by the SAME extractor used for every test set of this project (MediaPipe landmark box + 35 % per side,
aspect kept). Fixed sample: every 3rd FairBeauty file in sorted order. Pairs where either face is not found are dropped
and counted. python build_fairbeauty_pairs.py -> external_data/fairbeauty_pairs/{orig,filt}/<id>.png, pairs.tsv"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B))
from filters_v2.scale_normalized_filters import get_landmarks
E = B / "external_data"; OUT = E / "fairbeauty_pairs"; (OUT / "orig").mkdir(parents=True, exist_ok=True); (OUT / "filt").mkdir(exist_ok=True)

def crop(a):
    lm = get_landmarks(a)
    if lm is None: return None
    h, w = a.shape[:2]; x0, y0 = lm.min(0); x1, y1 = lm.max(0); bw, bh = x1 - x0, y1 - y0
    return a[max(0, int(y0 - .35 * bh)):min(h, int(y1 + .35 * bh)), max(0, int(x0 - .35 * bw)):min(w, int(x1 + .35 * bw))]

files = sorted((E / "fairbeauty/val_extracted/val_fair_beauty").glob("*/*.png"))[::3]; rows = []; miss = [0, 0, 0]
for k, f in enumerate(files):
    sid = f.stem.split("_")[0]; o = E / f"fairface_val/1.25/{sid}.jpg"
    if not o.is_file(): miss[0] += 1; continue
    cf = crop(np.array(Image.open(f).convert("RGB"))); co = crop(np.array(Image.open(o).convert("RGB")))
    if cf is None: miss[1] += 1; continue
    if co is None: miss[2] += 1; continue
    Image.fromarray(cf).save(OUT / "filt" / f"{f.stem}.png"); Image.fromarray(co).save(OUT / "orig" / f"{f.stem}.png"); rows.append((f.stem, cf.shape[0], co.shape[0]))
    if k % 500 == 0: print(k, len(rows), miss, flush=True)
(OUT / "pairs.tsv").write_text("id\tfilt_h\torig_h\n" + "\n".join(f"{a}\t{b}\t{c}" for a, b, c in rows), encoding="utf-8")
print("pairs", len(rows), "of", len(files), "| no original / no face in filtered / no face in original:", miss, "| median crop height filt", int(np.median([r[1] for r in rows])), "orig", int(np.median([r[2] for r in rows])))
