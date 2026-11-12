"""Where does beautification move a CLIP forgery detector, and can that direction be removed? (PRE_DECLARED Addendum 17)

Post hoc, no training. For a checkpoint whose forged decision is a linear head on CLIP's pooled feature:
  1. shift subspace: on FF++ *train* frames, the feature shifts D = f(B(x)) - f(x) for training-available beautifications
     (the bounded operator of adv_beauty.py with random u, and random_grade); SVD of D gives directions V and the energy
     captured by the first k;
  2. mechanism: on FF++ *val* frames under the eleven held-out pilgram filters, per filter the mean shift, its cosine with
     the forged weight vector w, the mean change of the forged logit on genuine and forged frames, and how much of the
     shift energy lies inside V_k (does an unseen filter move the feature along the training-available directions?);
  3. erasure: project the features onto the complement of V_k, refit the forged logistic head on train features (clean and
     beautified), evaluate on val: AUC clean and filtered, and at the 5 % FPR threshold on clean genuine val frames the
     genuine-called-forged rate and the forged-missed rate under the held-out filters. k is chosen on val only.
python subspace_probe.py <tag> ...  -> subspace_probe.json, SUBSPACE_PROBE.md
"""
import json
import sys
from pathlib import Path

import numpy as np
import pilgram
import torch
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import adv_beauty as AB
from leak_probe import HELDOUT, build_a, load
from train_ru import UNI, remap
from train_ru3 import to_t2
from train_ru5 import random_grade

NTR = 1200; KS = [0, 2, 4, 8, 16, 32, 64, 128]; BS = 32


def feats(model, x):
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        return model.vit(pixel_values=x.cuda()).pooler_output.float().cpu().numpy()


def load_batch(paths, size, norm, fn=None):
    out = []
    for p in paths:
        im = np.array(Image.open(p).convert("RGB"))
        if fn is not None:
            im = fn(im)
        out.append(to_t2(im, size, False, norm))
    return torch.stack(out)


def main():
    rng = np.random.default_rng(20261007)
    tr = [l.split("\t") for l in (UNI / "ffpp3_train.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    tr = [(remap(r[0]), int(r[1])) for r in tr if r[1] in ("0", "1")]
    real = [r for r in tr if r[1] == 0]; fake = [r for r in tr if r[1] == 1]
    tr = [real[i] for i in rng.choice(len(real), NTR // 2, False)] + [fake[i] for i in rng.choice(len(fake), NTR // 2, False)]
    ytr = np.array([r[1] for r in tr], np.float32)
    A = build_a(); yv = np.array([0 if x[1] == "real" else 1 for x in A]); fv = np.array([x[2] for x in A])
    f = HERE / "subspace_probe.json"; out = json.loads(f.read_text()) if f.is_file() else {}
    for tag in sys.argv[1:]:
        model, size, norm = load(tag); w = model.fz.weight[0].detach().float().cpu().numpy(); b = float(model.fz.bias[0])
        # ---- 1. train features: clean, two operator draws, one random grade
        Ftr, Fop, Fgr = [], [], []
        for i in range(0, NTR, BS):
            x = load_batch([p for p, _ in tr[i:i + BS]], size, norm); Ftr.append(feats(model, x))
            for _ in range(2):
                torch.manual_seed(1000 + i)
                xa = AB.worst_case(None, x.cuda(), None, random_only=True); Fop.append(feats(model, xa))
            g = np.random.default_rng(7 + i)
            Fgr.append(feats(model, load_batch([p for p, _ in tr[i:i + BS]], size, norm, fn=lambda im: random_grade(im, g))))
        Ftr = np.concatenate(Ftr); Fop = np.concatenate(Fop); Fgr = np.concatenate(Fgr)
        D = np.concatenate([Fop - np.tile(Ftr, (2, 1)), Fgr - Ftr])
        U, S, Vt = np.linalg.svd(D, full_matrices=False); energy = np.cumsum(S ** 2) / np.sum(S ** 2)
        res = {"train_shift_energy_in_first_k": {str(k): round(float(energy[k - 1]), 4) for k in KS if k > 0}}
        # ---- 2. val features: clean and under the assigned held-out filter
        Fv, Fvf = [], []
        for i in range(0, len(A), BS):
            Fv.append(feats(model, load_batch([x[0] for x in A[i:i + BS]], size, norm)))
            Fvf.append(feats(model, torch.stack([to_t2(np.array(getattr(pilgram, x[2])(Image.open(x[0]).convert("RGB")).convert("RGB")), size, False, norm) for x in A[i:i + BS]])))
        Fv = np.concatenate(Fv); Fvf = np.concatenate(Fvf); Dv = Fvf - Fv
        V16 = Vt[:16].T; wn = w / np.linalg.norm(w); mech = {}
        for flt in HELDOUT:
            m = fv == flt; d = Dv[m]; md = d.mean(0)
            mech[flt] = {"n": int(m.sum()), "cos_w_meanshift": round(float(md @ wn / (np.linalg.norm(md) + 1e-9)), 3),
                         "d_logit_genuine": round(float((d[yv[m] == 0] @ w).mean()), 3), "d_logit_forged": round(float((d[yv[m] == 1] @ w).mean()), 3),
                         "energy_in_train_V16": round(float((np.linalg.norm(d @ V16, axis=1) ** 2).sum() / (np.linalg.norm(d, axis=1) ** 2).sum()), 3),
                         "shift_norm_over_feature_norm": round(float(np.linalg.norm(d, axis=1).mean() / np.linalg.norm(Fv[m], axis=1).mean()), 3)}
        res["heldout_filters"] = mech
        # ---- 3. erasure + refit
        def evaluate(score_clean, score_filt):
            t = np.quantile(score_clean[yv == 0], 0.95)
            return {"auc_clean": round(float(roc_auc_score(yv, score_clean)), 4), "auc_filtered": round(float(roc_auc_score(yv, score_filt)), 4),
                    "fa_clean": round(100 * float((score_clean[yv == 0] > t).mean()), 1), "fa_filtered": round(100 * float((score_filt[yv == 0] > t).mean()), 1),
                    "miss_clean": round(100 * float((score_clean[yv == 1] <= t).mean()), 1), "miss_filtered": round(100 * float((score_filt[yv == 1] <= t).mean()), 1)}
        res["original_head"] = evaluate(Fv @ w + b, Fvf @ w + b)
        Xtr = np.concatenate([Ftr, Fop, Fgr]); Ytr = np.concatenate([ytr, ytr, ytr, ytr]); res["erasure"] = {}
        for k in KS:
            P = np.eye(D.shape[1], dtype=np.float32) - (Vt[:k].T @ Vt[:k] if k > 0 else 0)
            clf = LogisticRegression(C=1.0, max_iter=2000).fit(Xtr @ P, Ytr)
            res["erasure"][str(k)] = evaluate(clf.decision_function(Fv @ P), clf.decision_function(Fvf @ P))
        out[tag] = res; f.write_text(json.dumps(out, indent=1)); print(tag, json.dumps(res, indent=1), flush=True)
        del model; torch.cuda.empty_cache()
    L = ["# Beautification shift in CLIP feature space (Addendum 17; FF++ train for the subspace, FF++ val + held-out pilgram filters for evaluation)", ""]
    for tag, res in out.items():
        L += [f"## {tag}", "", "Energy of training-available shifts in the first k directions: " + ", ".join(f"k={k}: {v}" for k, v in res["train_shift_energy_in_first_k"].items()), "",
              "| held-out filter | n | cos(w, mean shift) | d logit genuine | d logit forged | shift energy in train V16 | shift / feature norm |", "|---|---|---|---|---|---|---|"]
        L += [f"| {k} | {v['n']} | {v['cos_w_meanshift']} | {v['d_logit_genuine']:+.3f} | {v['d_logit_forged']:+.3f} | {v['energy_in_train_V16']} | {v['shift_norm_over_feature_norm']} |" for k, v in res["heldout_filters"].items()]
        L += ["", "| head | AUC clean | AUC filtered | FA clean | FA filtered | MISS clean | MISS filtered |", "|---|---|---|---|---|---|---|"]
        rows = [("original head", res["original_head"])] + [(f"refit, erase k={k}", v) for k, v in res["erasure"].items()]
        L += [f"| {n} | {v['auc_clean']:.3f} | {v['auc_filtered']:.3f} | {v['fa_clean']} | {v['fa_filtered']} | {v['miss_clean']} | {v['miss_filtered']} |" for n, v in rows] + [""]
    (HERE / "SUBSPACE_PROBE.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
