"""Review 2026-10-12, point 5: is the P0 vs P1/P2 gap an artefact of the selected epoch (P0 selects epochs 2/4/2, P1/P2 4-8)?
Inference only, existing per-epoch checkpoints. Subset: every 4th identity of the unseen service (553), originals +
Smoothing_60 / Smoothing_90. Loading in threads (the machine is shared; worker processes starve).
The selected checkpoint of P0 seed 1 is rescored on the same subset as a sanity check against ali_scores_*.npz.
python epoch_check.py  -> epoch_check.json, epoch_scores_<key>.npz (this folder only)"""
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import torch
from PIL import Image
HERE = Path(__file__).resolve().parent; RU = HERE.parent.parent / "retouch_unified_20260929"; sys.path.insert(0, str(RU))
from train_ru import BASE, CKPT, crop  # noqa: E402
from train_ru3 import to_t2  # noqa: E402
from train_ru_clip import load_clip  # noqa: E402
GROUPS = ["Smoothing_60", "Smoothing_90"]
JOBS = ["clipe5fbp0_s20260929", "clipe5fbp0_s20260929_e08", "clipe5fb_s20260929_e02", "clipe5fbp1_s20260929_e02", "clipe5fbp0_s20260929_e05",
        "clipe5fbp0_s20260930_e08", "clipe5fbp0_s20261001_e08", "clipe5fb_s20260929_e08", "clipe5fbp1_s20260929_e08"]


def main():
    boxes = json.loads((RU / "ffhq_boxes.json").read_text()); orig = BASE / "ffhq_originals/Part2"; ali = BASE / "FFHQ_ali_process"
    stems = sorted(p.stem for p in orig.glob("*.png") if p.stem in boxes)[::4]; items, g, st = [], [], []
    for k in stems:
        items.append((str(orig / f"{k}.png"), boxes[k])); g.append("orig_0"); st.append(k)
    for grp in GROUPS:
        for k in stems:
            p = ali / grp / f"{(int(k) // 1000) * 1000}" / f"{k}.png"
            if p.is_file():
                items.append((str(p), boxes[k])); g.append(grp); st.append(k)
    g = np.array(g); st = np.array(st); o = g == "orig_0"
    with ThreadPoolExecutor(6) as ex:
        X = list(ex.map(lambda it: to_t2(crop(np.array(Image.open(it[0]).convert("RGB")), it[1]), 224, False, "clip"), items))
    X = torch.stack(X); print("loaded", X.shape, flush=True)
    f = HERE / "epoch_check.json"; out = json.loads(f.read_text()) if f.is_file() else {}
    for key in JOBS:
        if key in out or not (CKPT / f"ru_{key}.pth").is_file():
            continue
        m = load_clip(key, head=True).cuda().eval(); s = []
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            for i in range(0, len(X), 48):
                s.append(torch.softmax(m(X[i:i + 48].cuda())[0].float(), 1)[:, 1].cpu().numpy())
        s = np.concatenate(s).astype(np.float64); np.savez(HERE / f"epoch_scores_{key}.npz", s=s, group=g, stem=st)
        t = np.quantile(s[o], 0.95); r = {"n_id": int(o.sum()), "t5": round(float(t), 4), "orig>0.5": round(float((s[o] > 0.5).mean() * 100), 2)}
        for grp in GROUPS:
            r[grp] = round(float((s[g == grp] > t).mean() * 100), 2)
        out[key] = r; print(key, r, flush=True); f.write_text(json.dumps(out, indent=1)); del m; torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
