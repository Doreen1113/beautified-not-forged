"""AR-filter training pairs (PRE_DECLARED Addendum 8). Runs on the Ubuntu box (AIGC_BASE set).
FairBeauty TRAIN (FairFace train faces under 8 Instagram AR beauty filters; folder = filter, see filters.txt) paired with
the FairFace train originals (HuggingFaceM4/FairFace, padding 1.25). Both sides are cropped by the project's extractor
(MediaPipe landmark box + 35 %). Every 2nd FairBeauty file in sorted order. Filters 'Baby_cute_face', 'big city life' and
'Just Baby' are NEVER written to the training pairs: they are the held-out AR filters (tested on FairBeauty val / B-LFW).
-> external_data/fairbeauty_train_pairs/{orig,filt}/<stem>.png, pairs.tsv (stem, filter, heights)"""
import os, sys, io
from pathlib import Path
import numpy as np, pyarrow.parquet as pq
from PIL import Image
from huggingface_hub import hf_hub_download, list_repo_files
B = Path(os.environ["AIGC_BASE"]); sys.path.insert(0, str(B))
from filters_v2.scale_normalized_filters import get_landmarks
E = B / "external_data"; FB = E / "fairbeauty/train_fair_beauty"; FF = E / "fairface_train/1.25"; OUT = E / "fairbeauty_train_pairs"
HELD = {"Baby_cute_face", "big city life", "Just Baby"}
FF.mkdir(parents=True, exist_ok=True); (OUT / "orig").mkdir(parents=True, exist_ok=True); (OUT / "filt").mkdir(exist_ok=True)
if not (FF / "_done").exists():
    for fn in sorted(f for f in list_repo_files("HuggingFaceM4/FairFace", repo_type="dataset") if f.startswith("1.25/train")):
        t = pq.read_table(hf_hub_download("HuggingFaceM4/FairFace", fn, repo_type="dataset"), columns=["image"])
        for c in t.column("image").to_pylist():
            (FF / c["path"]).write_bytes(c["bytes"])
        print("shard", fn, t.num_rows, flush=True)
    (FF / "_done").write_text("ok")
fmap = {}
for l in (FB / "filters.txt").read_text().splitlines():
    if ":" in l:
        k, v = l.split(":", 1); fmap[k.strip()] = v.strip()
def crop(a):
    lm = get_landmarks(a)
    if lm is None: return None
    h, w = a.shape[:2]; x0, y0 = lm.min(0); x1, y1 = lm.max(0); bw, bh = x1 - x0, y1 - y0
    return a[max(0, int(y0 - .35 * bh)):min(h, int(y1 + .35 * bh)), max(0, int(x0 - .35 * bw)):min(w, int(x1 + .35 * bw))]
files = sorted(FB.glob("*/*.png"))[::2]; rows = []; miss = [0, 0, 0, 0]
for k, f in enumerate(files):
    filt = fmap.get(f.parent.name, "?")
    if filt in HELD or filt == "?": miss[0] += 1; continue
    sid = f.stem.split("_")[0]; o = FF / f"{sid}.jpg"
    if not o.is_file(): miss[1] += 1; continue
    cf = crop(np.array(Image.open(f).convert("RGB"))); co = crop(np.array(Image.open(o).convert("RGB")))
    if cf is None: miss[2] += 1; continue
    if co is None: miss[3] += 1; continue
    Image.fromarray(cf).save(OUT / "filt" / f"{f.stem}.png"); Image.fromarray(co).save(OUT / "orig" / f"{f.stem}.png"); rows.append((f.stem, filt, cf.shape[0], co.shape[0]))
    if k % 2000 == 0: print(k, len(rows), miss, flush=True)
(OUT / "pairs.tsv").write_text("stem\tfilter\tfilt_h\torig_h\n" + "\n".join("\t".join(map(str, r)) for r in rows))
print("pairs", len(rows), "| held-out filter skipped / no original / no face filt / no face orig:", miss, flush=True)
