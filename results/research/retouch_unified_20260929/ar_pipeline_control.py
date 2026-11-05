"""Is the AR-filter result of RU7 the filter or the OpenFilter capture pipeline? (PRE_DECLARED Addendum 12 control.)
600 FairBeauty validation pairs (every 4th of the 2,927, first 600). For originals and filtered versions: the image as is,
the image with the whole face hull replaced by mid-grey (only background / hair / pipeline traces remain), and the image
with everything OUTSIDE the hull replaced by grey (face only). If 'face hull greyed' filtered images are still called filter
while greyed originals are not, the model reads the pipeline, not the face edit.
python ar_pipeline_control.py [tag] -> ar_pipeline_control.json"""
import json, sys
from pathlib import Path
import cv2, numpy as np, torch
from PIL import Image
HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(HERE)); sys.path.insert(0, str(B))
from leak_probe import load, summ
from train_ru3 import to_t2
from filters_v2.scale_normalized_filters import get_landmarks
D = B / "external_data/fairbeauty_pairs"; IDS = [l.split("\t")[0] for l in (D / "pairs.tsv").read_text(encoding="utf-8").splitlines()[1:]][::4][:600]

def variants(a):
    lm = get_landmarks(a)
    if lm is None: return None
    m = np.zeros(a.shape[:2], np.uint8); cv2.fillConvexPoly(m, cv2.convexHull(lm.astype(np.float32)).astype(np.int32), 1); m = m.astype(bool)
    g = a.copy(); g[m] = 128; f = a.copy(); f[~m] = 128
    return a, g, f

def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "clipe7_s20260929"; model, size, norm = load(tag); P = {k: [] for k in ("orig", "filt")}
    for i in IDS:
        vo = variants(np.array(Image.open(D / "orig" / f"{i}.png").convert("RGB"))); vf = variants(np.array(Image.open(D / "filt" / f"{i}.png").convert("RGB")))
        if vo is None or vf is None: continue
        for k, v in (("orig", vo), ("filt", vf)):
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
                lo = model(torch.stack([to_t2(x, size, False, norm) for x in v]).cuda())[0]
            P[k].append(torch.softmax(lo.float(), 1).cpu().numpy())
    out = {"n": len(P["orig"])}
    for k in P:
        A = np.stack(P[k])
        for j, nm in enumerate(("as is", "face hull greyed", "outside hull greyed")): out[f"{k} | {nm}"] = summ(A[:, j])
    f = HERE / "ar_pipeline_control.json"; d = json.loads(f.read_text()) if f.is_file() else {}; d[tag] = out; f.write_text(json.dumps(d, indent=1))
    for k, v in out.items(): print(k, v if not isinstance(v, dict) else {x: v[x] for x in ("real", "fake", "filter")})

if __name__ == "__main__":
    main()
