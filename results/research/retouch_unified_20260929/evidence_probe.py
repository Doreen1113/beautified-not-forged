"""Does beautification raise the footprint-supervised evidence map diffusely while forgery raises it locally? (Addendum 27, post hoc,
FF++ val + held-out colour filters; no training.)

For a model with an evidence head (16 x 16 logits trained against exact footprints), per frame: mean, max, mean of the top 5 %
cells, concentration (share of the sigmoid mass in the top 10 % of cells), and the pooled-feature forged logit. Reported:
distribution shift of each statistic under the held-out filters for genuine and forged frames, and each statistic used as a
forgery score: AUC clean / filtered and FA / MISS under the filters at the 5 % FPR threshold set on clean genuine frames.
python evidence_probe.py <tag> ...  -> evidence_probe.json, EVIDENCE_PROBE.md
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
from leak_probe import build_a, load
from train_ru3 import to_t2

BS = 32


def stats(ev, z):
    """ev: (n, 256) logits; z: (n,) forged logit."""
    p = torch.sigmoid(ev); k5 = max(1, ev.shape[1] // 20); k10 = max(1, ev.shape[1] // 10)
    top5 = ev.topk(k5, dim=1).values.mean(1); conc = p.topk(k10, dim=1).values.sum(1) / p.sum(1).clamp_min(1e-6)
    return {"ev_mean": ev.mean(1), "ev_max": ev.amax(1), "ev_top5": top5, "ev_conc": conc, "ev_max_minus_mean": ev.amax(1) - ev.mean(1), "pooled_logit": z}


def main():
    A = build_a(); y = np.array([0 if x[1] == "real" else 1 for x in A])
    f = HERE / "evidence_probe.json"; out = json.loads(f.read_text()) if f.is_file() else {}
    for tag in sys.argv[1:]:
        model, size, norm = load(tag); S = {"clean": {}, "filtered": {}}
        with torch.no_grad():
            for i in range(0, len(A), BS):
                xs = torch.stack([to_t2(np.array(Image.open(x[0]).convert("RGB")), size, False, norm) for x in A[i:i + BS]]).cuda()
                xf = torch.stack([to_t2(np.array(getattr(pilgram, x[2])(Image.open(x[0]).convert("RGB")).convert("RGB")), size, False, norm) for x in A[i:i + BS]]).cuda()
                for cond, x in (("clean", xs), ("filtered", xf)):
                    with torch.autocast("cuda", dtype=torch.bfloat16):
                        o = model(x)
                    st = stats(o[3].float().flatten(1), o[4][:, 0].float())
                    for k, v in st.items():
                        S[cond].setdefault(k, []).append(v.cpu().numpy())
        S = {c: {k: np.concatenate(v) for k, v in d.items()} for c, d in S.items()}
        res = {}
        for k in S["clean"]:
            c, fl = S["clean"][k], S["filtered"][k]; t = np.quantile(c[y == 0], 0.95)
            res[k] = {"genuine_clean_mean": round(float(c[y == 0].mean()), 3), "genuine_filtered_mean": round(float(fl[y == 0].mean()), 3),
                      "forged_clean_mean": round(float(c[y == 1].mean()), 3), "forged_filtered_mean": round(float(fl[y == 1].mean()), 3),
                      "auc_clean": round(float(roc_auc_score(y, c)), 4), "auc_filtered": round(float(roc_auc_score(y, fl)), 4),
                      "fa_filtered": round(100 * float((fl[y == 0] > t).mean()), 1), "miss_clean": round(100 * float((c[y == 1] <= t).mean()), 1), "miss_filtered": round(100 * float((fl[y == 1] <= t).mean()), 1)}
        out[tag] = res; f.write_text(json.dumps(out, indent=1)); print(tag, json.dumps(res, indent=1), flush=True)
        del model; torch.cuda.empty_cache()
    L = ["# Evidence-map statistics as forgery scores (Addendum 27; FF++ val, held-out pilgram filters)", ""]
    for tag, r in out.items():
        L += [f"## {tag}", "", "| statistic | genuine clean → filtered | forged clean → filtered | AUC clean | AUC filtered | FA filtered | MISS clean → filtered |", "|---|---|---|---|---|---|---|"]
        L += [f"| {k} | {v['genuine_clean_mean']} → {v['genuine_filtered_mean']} | {v['forged_clean_mean']} → {v['forged_filtered_mean']} | {v['auc_clean']:.3f} | {v['auc_filtered']:.3f} | {v['fa_filtered']} | {v['miss_clean']} → {v['miss_filtered']} |" for k, v in r.items()] + [""]
    (HERE / "EVIDENCE_PROBE.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
