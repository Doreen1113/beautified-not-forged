"""Is a beautification a *common* shift of all patch tokens, and does a within-image (self-referenced) forgery feature survive it?
(PRE_DECLARED Addendum 23; post hoc, no training of the backbone; FF++ train for fitting, FF++ val + held-out filters for testing.)

For a trained detector we read the patch tokens of the last layer (16 x 16 for CLIP ViT-L/14 at 224 px).
  1. common-shift fraction: for a val frame and its held-out-filter copy, D_i = t_i(filtered) - t_i(clean) per token i;
     rho = ||mean_i D_i||^2 / mean_i ||D_i||^2 (1 = every token moves by the same vector, 0 = no common component).
  2. linear probes fitted on CLEAN FF++ train frames only (so any robustness is by construction, not by exposure):
       cls     pooled feature (what the detector's head reads)
       mean    mean of the patch tokens
       io      mean of the inner 8 x 8 tokens minus mean of the outer ring (within-image contrast: a common shift cancels exactly)
       std     per-dimension standard deviation of the tokens over positions (second-order, also shift-invariant)
       io+std  both
     evaluated on val: AUC clean / filtered, and at the 5 % FPR threshold on clean genuine val frames FA and MISS under the filters.
  3. the same probes fitted on clean + randomly graded train frames (exposure), for reference.
python token_probe.py <tag> ...  -> token_probe.json, TOKEN_PROBE.md
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
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from leak_probe import HELDOUT, build_a, load
from train_ru import UNI, remap
from train_ru3 import to_t2
from train_ru5 import random_grade

NTR = 2000; BS = 32; G = 16
INNER = np.zeros((G, G), bool); INNER[4:12, 4:12] = True; INNER = torch.tensor(INNER.reshape(-1))


def feats(model, x):
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        o = model.vit(pixel_values=x.cuda())
    t = o.last_hidden_state[:, 1:, :].float(); inner = INNER.to(t.device)
    return {"cls": o.pooler_output.float().cpu().numpy(), "mean": t.mean(1).cpu().numpy(), "io": (t[:, inner].mean(1) - t[:, ~inner].mean(1)).cpu().numpy(),
            "std": t.std(1).cpu().numpy()}, t


def batch(paths, size, norm, fn=None):
    out = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        if fn is not None:
            im = fn(im)
        out.append(to_t2(np.array(im), size, False, norm))
    return torch.stack(out)


def cat(ds):
    return {k: np.concatenate([d[k] for d in ds]) for k in ds[0]}


def main():
    rng = np.random.default_rng(20261008)
    tr = [l.split("\t") for l in (UNI / "ffpp3_train.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    tr = [(remap(r[0]), int(r[1])) for r in tr if r[1] in ("0", "1")]
    real = [r for r in tr if r[1] == 0]; fake = [r for r in tr if r[1] == 1]
    tr = [real[i] for i in rng.choice(len(real), NTR // 2, False)] + [fake[i] for i in rng.choice(len(fake), NTR // 2, False)]
    ytr = np.array([r[1] for r in tr])
    A = build_a(); yv = np.array([0 if x[1] == "real" else 1 for x in A]); fv = np.array([x[2] for x in A])
    f = HERE / "token_probe.json"; out = json.loads(f.read_text()) if f.is_file() else {}
    for tag in sys.argv[1:]:
        model, size, norm = load(tag); Ftr, Fgr, Fv, Fvf, rho = [], [], [], [], []
        for i in range(0, NTR, BS):
            ps = [p for p, _ in tr[i:i + BS]]; Ftr.append(feats(model, batch(ps, size, norm))[0])
            g = np.random.default_rng(7 + i); Fgr.append(feats(model, batch(ps, size, norm, fn=lambda im: Image.fromarray(random_grade(np.array(im), g))))[0])
        for i in range(0, len(A), BS):
            fc, tc = feats(model, batch([x[0] for x in A[i:i + BS]], size, norm))
            ff, tf = feats(model, torch.stack([to_t2(np.array(getattr(pilgram, x[2])(Image.open(x[0]).convert("RGB")).convert("RGB")), size, False, norm) for x in A[i:i + BS]]))
            D = tf - tc; rho.append((D.mean(1).pow(2).sum(1) / D.pow(2).sum(2).mean(1)).cpu().numpy()); Fv.append(fc); Fvf.append(ff)
        Ftr, Fgr, Fv, Fvf = cat(Ftr), cat(Fgr), cat(Fv), cat(Fvf); rho = np.concatenate(rho)
        res = {"common_shift_fraction": {"all": round(float(rho.mean()), 3), **{k: round(float(rho[fv == k].mean()), 3) for k in HELDOUT}}, "probes": {}}

        def evaluate(sc, sf):
            t = np.quantile(sc[yv == 0], 0.95)
            return {"auc_clean": round(float(roc_auc_score(yv, sc)), 4), "auc_filtered": round(float(roc_auc_score(yv, sf)), 4),
                    "fa_filtered": round(100 * float((sf[yv == 0] > t).mean()), 1), "miss_clean": round(100 * float((sc[yv == 1] <= t).mean()), 1),
                    "miss_filtered": round(100 * float((sf[yv == 1] <= t).mean()), 1)}
        for name, keys in (("cls", ["cls"]), ("mean", ["mean"]), ("io", ["io"]), ("std", ["std"]), ("io+std", ["io", "std"]), ("cls+io+std", ["cls", "io", "std"])):
            X = lambda d, keys=keys: np.concatenate([d[k] for k in keys], 1)
            for fit, (Xt, Yt) in (("clean", (X(Ftr), ytr)), ("clean+graded", (np.concatenate([X(Ftr), X(Fgr)]), np.concatenate([ytr, ytr])))):
                clf = make_pipeline(StandardScaler(), LogisticRegression(C=0.05, max_iter=3000)).fit(Xt, Yt)
                res["probes"][f"{name} | fit {fit}"] = evaluate(clf.decision_function(X(Fv)), clf.decision_function(X(Fvf)))
        out[tag] = res; f.write_text(json.dumps(out, indent=1)); print(tag, json.dumps(res, indent=1), flush=True)
        del model; torch.cuda.empty_cache()
    L = ["# Common token shift and self-referenced probes (Addendum 23; fitted on FF++ train, tested on FF++ val + held-out filters)", ""]
    for tag, r in out.items():
        L += [f"## {tag}", "", "Common-shift fraction rho per held-out filter: " + ", ".join(f"{k} {v}" for k, v in r["common_shift_fraction"].items()), "",
              "| probe | AUC clean | AUC filtered | FA filtered | MISS clean | MISS filtered |", "|---|---|---|---|---|---|"]
        L += [f"| {k} | {v['auc_clean']:.3f} | {v['auc_filtered']:.3f} | {v['fa_filtered']} | {v['miss_clean']} | {v['miss_filtered']} |" for k, v in r["probes"].items()] + [""]
    (HERE / "TOKEN_PROBE.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
