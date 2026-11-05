"""Edit-sensitivity as evidence (IDEATION B2; PRE_DECLARED Addendum 29; FF++ train for fitting, FF++ val + held-out filters for testing).

Observation: beautification moves a genuine face's forged logit far more than a forged face's (Addendum 17 A). Idea: use the
detector's response to K known probe edits as the feature: Delta_k = logit(edit_k(x)) - logit(x). Decision from
(logit(x), Delta_1..K) by a logistic head fitted on CLEAN FF++ train frames only. Tests on val: (i) AUC of the K-D rule on
clean frames and of -mean(Delta) alone; (ii) FA under the eleven held-out filters at the clean 5 %-FPR point, MISS under
filters; (iii) saturation control: Delta asymmetry inside each clean-logit decile.
Probe edits are fixed parameter settings of the operator (adv_beauty.apply, wide bounds): corner vignette, monochrome,
warm tone, cool tint field, smoothing, contrast.
python sensitivity_probe.py <tag> ...  -> sensitivity_probe.json, SENSITIVITY_PROBE.md
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
import adv_beauty as AB
from canon import ident
from leak_probe import build_a, load
from train_ru import UNI, remap
from train_ru3 import to_t2

NTR = 1000; NVA = 600; BS = 32


def probe_params(n, device):
    AB.WIDE = True; AB.INVERSE = False
    base = {k: torch.full((n, *s), ident(k), device=device) for k, s in (("gamma", (3, 1, 1)), ("gain", (3, 1, 1)), ("lift", (3, 1, 1)), ("M", (3, 3)), ("sat", (1, 1, 1)), ("con", (1, 1, 1)), ("field", (1, 4, 4)), ("tint", (3, 4, 4)))}
    base["M"] = torch.zeros(n, 3, 3, device=device); base["smooth"] = torch.full((n, 1, 1, 1), -6.0, device=device); base["grain"] = torch.full((n, 1, 1, 1), -6.0, device=device)
    P = {}
    u = {k: v.clone() for k, v in base.items()}; u["field"][:, 0, [0, -1], :] = -3.0; u["field"][:, 0, :, [0, -1]] = -3.0; P["vignette"] = u
    u = {k: v.clone() for k, v in base.items()}; u["sat"][:] = -8.0; P["monochrome"] = u
    u = {k: v.clone() for k, v in base.items()}; u["gain"][:, 0] = 1.5; u["gain"][:, 2] = -1.5; u["gamma"][:] = ident("gamma") - 0.8; P["warm"] = u
    u = {k: v.clone() for k, v in base.items()}; u["tint"][:, 0] = -2.0; u["tint"][:, 2] = 2.0; P["cool_tint"] = u
    u = {k: v.clone() for k, v in base.items()}; u["smooth"][:] = 3.0; P["smooth"] = u
    u = {k: v.clone() for k, v in base.items()}; u["con"][:] = 2.0; P["contrast"] = u
    return P


def logits(model, x):
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        return model(x)[4][:, 0].float()


def feats(model, xs):
    """xs: normalised batch on cuda -> (n, 1 + K): clean logit and Delta per probe edit."""
    z0 = logits(model, xs); x01 = AB.denorm(xs.float()).clamp(0, 1); P = probe_params(xs.shape[0], xs.device); noise = torch.zeros(xs.shape[0], 1, *xs.shape[-2:], device=xs.device)
    cols = [z0]
    for name, u in P.items():
        cols.append(logits(model, AB.renorm(AB.apply(x01, u, noise)).to(xs.dtype)) - z0)
    return torch.stack(cols, 1).cpu().numpy(), list(P)


def main():
    rng = np.random.default_rng(20261008)
    tr = [l.split("\t") for l in (UNI / "ffpp3_train.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    tr = [(remap(r[0]), int(r[1])) for r in tr if r[1] in ("0", "1")]; real = [r for r in tr if r[1] == 0]; fake = [r for r in tr if r[1] == 1]
    tr = [real[i] for i in rng.choice(len(real), NTR // 2, False)] + [fake[i] for i in rng.choice(len(fake), NTR // 2, False)]; ytr = np.array([r[1] for r in tr])
    A = build_a(); ya = np.array([0 if x[1] == "real" else 1 for x in A]); idx = np.concatenate([rng.choice(np.where(ya == 0)[0], NVA // 2, False), rng.choice(np.where(ya == 1)[0], NVA // 2, False)])
    A = [A[i] for i in idx]; yv = ya[idx]
    f = HERE / "sensitivity_probe.json"; out = json.loads(f.read_text()) if f.is_file() else {}
    for tag in sys.argv[1:]:
        model, size, norm = load(tag)
        def run(items, filt):
            F = []
            for i in range(0, len(items), BS):
                ims = [Image.open(x[0]).convert("RGB") for x in items[i:i + BS]]
                if filt:
                    ims = [getattr(pilgram, x[2])(im).convert("RGB") for im, x in zip(ims, items[i:i + BS])]
                xs = torch.stack([to_t2(np.array(im), size, False, norm) for im in ims]).cuda(); fe, names = feats(model, xs); F.append(fe)
            return np.concatenate(F), names
        Ftr, names = run(tr, False); Fv, _ = run(A, False); Fvf, _ = run(A, True)
        res = {"probes": names, "mean_delta_by_class": {}}
        for cond, F in (("clean", Fv), ("filtered", Fvf)):
            res["mean_delta_by_class"][cond] = {"genuine": [round(float(v), 2) for v in F[yv == 0, 1:].mean(0)], "forged": [round(float(v), 2) for v in F[yv == 1, 1:].mean(0)]}

        def evaluate(sc, sf):
            t = np.quantile(sc[yv == 0], 0.95)
            return {"auc_clean": round(float(roc_auc_score(yv, sc)), 4), "auc_filtered": round(float(roc_auc_score(yv, sf)), 4),
                    "fa_filtered": round(100 * float((sf[yv == 0] > t).mean()), 1), "miss_clean": round(100 * float((sc[yv == 1] <= t).mean()), 1), "miss_filtered": round(100 * float((sf[yv == 1] <= t).mean()), 1)}
        res["rules"] = {"logit only": evaluate(Fv[:, 0], Fvf[:, 0]), "-mean(Delta) only": evaluate(-Fv[:, 1:].mean(1), -Fvf[:, 1:].mean(1))}
        for name, cols in (("logit + mean(Delta)", None), ("logit + Delta_1..K", slice(0, None))):
            X = (lambda F: np.stack([F[:, 0], F[:, 1:].mean(1)], 1)) if cols is None else (lambda F: F)
            clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000)).fit(X(Ftr), ytr)
            res["rules"][name] = evaluate(clf.decision_function(X(Fv)), clf.decision_function(X(Fvf)))
            res["rules"][name]["coef"] = [round(float(c), 3) for c in clf[-1].coef_[0]]
        # saturation control: mean Delta per class inside deciles of the clean logit (pooled)
        dec = np.digitize(Fv[:, 0], np.quantile(Fv[:, 0], np.linspace(0.1, 0.9, 9))); ctrl = []
        for d in range(10):
            m = dec == d; g = m & (yv == 0); k = m & (yv == 1)
            ctrl.append({"decile": d, "n_genuine": int(g.sum()), "n_forged": int(k.sum()), "mean_delta_genuine": round(float(Fv[g, 1:].mean()), 2) if g.any() else None, "mean_delta_forged": round(float(Fv[k, 1:].mean()), 2) if k.any() else None})
        res["saturation_control"] = ctrl
        out[tag] = res; f.write_text(json.dumps(out, indent=1)); print(tag, json.dumps({k: v for k, v in res.items() if k != "saturation_control"}, indent=1), flush=True)
        del model; torch.cuda.empty_cache()
    L = ["# Edit-sensitivity as evidence (Addendum 29; fitted on FF++ train, tested on FF++ val + held-out filters)", ""]
    for tag, r in out.items():
        L += [f"## {tag}", "", "Mean Delta per probe edit (" + ", ".join(r["probes"]) + "):", f"- clean: genuine {r['mean_delta_by_class']['clean']['genuine']} forged {r['mean_delta_by_class']['clean']['forged']}",
              f"- filtered: genuine {r['mean_delta_by_class']['filtered']['genuine']} forged {r['mean_delta_by_class']['filtered']['forged']}", "",
              "| rule | AUC clean | AUC filtered | FA filtered | MISS clean → filtered |", "|---|---|---|---|---|"]
        L += [f"| {k} | {v['auc_clean']:.3f} | {v['auc_filtered']:.3f} | {v['fa_filtered']} | {v['miss_clean']} → {v['miss_filtered']} |" for k, v in r["rules"].items()]
        L += ["", "Saturation control (clean-logit deciles): mean Delta genuine / forged", "| decile | n gen / forged | Δ genuine | Δ forged |", "|---|---|---|---|"]
        L += [f"| {c['decile']} | {c['n_genuine']} / {c['n_forged']} | {c['mean_delta_genuine']} | {c['mean_delta_forged']} |" for c in r["saturation_control"]] + [""]
    (HERE / "SENSITIVITY_PROBE.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
