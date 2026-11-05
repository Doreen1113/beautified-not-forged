"""Post-hoc check of the canonicaliser (Addendum 20), FF++ val only: a trained detector with and without the canonicaliser in
front, on untreated val frames and on the same frames under the eleven held-out pilgram filters. Reports AUC and, at the 5 %
FPR threshold on untreated genuine frames (set separately for each variant), FA and MISS under the filters.
python canon_probe.py <detector tag> <canon checkpoint>  -> canon_probe.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pilgram
import torch
from PIL import Image
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from canon import Canon
from leak_probe import build_a, load
from train_ru3 import to_t2

BS = 32


def main():
    tag, ck = sys.argv[1], sys.argv[2]
    model, size, norm = load(tag); can = Canon().cuda().eval(); can.load_state_dict(torch.load(ck, map_location="cpu"))
    A = build_a(); y = np.array([0 if x[1] == "real" else 1 for x in A])
    S = {"plain": {"clean": [], "filtered": []}, "canon": {"clean": [], "filtered": []}}
    with torch.no_grad():
        for i in range(0, len(A), BS):
            xs = torch.stack([to_t2(np.array(Image.open(x[0]).convert("RGB")), size, False, norm) for x in A[i:i + BS]]).cuda()
            xf = torch.stack([to_t2(np.array(getattr(pilgram, x[2])(Image.open(x[0]).convert("RGB")).convert("RGB")), size, False, norm) for x in A[i:i + BS]]).cuda()
            for cond, x in (("clean", xs), ("filtered", xf)):
                for var, inp in (("plain", x), ("canon", can(x))):
                    with torch.autocast("cuda", dtype=torch.bfloat16):
                        z = model(inp)[4][:, 0].float()
                    S[var][cond].append(torch.sigmoid(z).cpu().numpy())
    out = {}
    for var in S:
        c = np.concatenate(S[var]["clean"]); f = np.concatenate(S[var]["filtered"]); t = np.quantile(c[y == 0], 0.95)
        out[var] = {"auc_clean": round(float(roc_auc_score(y, c)), 4), "auc_filtered": round(float(roc_auc_score(y, f)), 4),
                    "fa_clean": round(100 * float((c[y == 0] > t).mean()), 1), "fa_filtered": round(100 * float((f[y == 0] > t).mean()), 1),
                    "miss_clean": round(100 * float((c[y == 1] <= t).mean()), 1), "miss_filtered": round(100 * float((f[y == 1] <= t).mean()), 1)}
    p = HERE / "canon_probe.json"; d = json.loads(p.read_text()) if p.is_file() else {}; d[f"{tag}+{Path(ck).stem}"] = out; p.write_text(json.dumps(d, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
