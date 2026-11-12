"""Addendum 53: frozen ArcFace embedding + logistic regression trained on FF++ train frames, tested reference-free on the
Addendum 51 Celeb-DF probes under smoothing.  python ffpp_arcface_probe.py embed | analyse"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import id_ref_probe as P  # noqa: E402

LST = HERE.parent / "ffpp_unified_20260925/ffpp3_train.txt"; METH = ["Deepfakes", "Face2Face", "FaceSwap", "NeuralTextures"]


def embed():
    rows = [l.split("\t") for l in LST.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    rng = np.random.default_rng(0); pick = []
    for src, n in [("real", 3000)] + [(m, 750) for m in METH]:
        rs = [r for r in rows if r[3] == src]; byv = {}
        for r in rs:
            byv.setdefault(r[2], []).append(r)
        vids = list(byv); out = []
        while len(out) < n:   # round-robin over videos, one random frame each pass
            for v in rng.permutation(vids):
                out.append(byv[v][int(rng.integers(len(byv[v])))])
                if len(out) == n:
                    break
        pick += out
    a = P.app(); E = np.full((len(pick), 512), np.nan, np.float32)
    for i, r in enumerate(pick):
        img = cv2.imread(r[0]); e = P.embed_img(a, img) if img is not None else None
        if e is not None:
            E[i] = e
        if i % 1000 == 0:
            print(i, len(pick), flush=True)
    np.savez(HERE / "ffpp_arcface_emb.npz", E=E, y=np.array([int(r[1]) for r in pick]), src=np.array([r[3] for r in pick]), vid=np.array([r[2] for r in pick]))


def analyse():
    from sklearn.linear_model import LogisticRegressionCV
    from sklearn.metrics import roc_auc_score
    z = np.load(HERE / "ffpp_arcface_emb.npz"); ok = ~np.isnan(z["E"][:, 0]); X, Y = z["E"][ok], z["y"][ok]
    clf = LogisticRegressionCV(Cs=10, cv=5, max_iter=5000, scoring="roc_auc").fit(X, Y)
    m = json.loads((HERE / "smooth38_list.json").read_text()); t = np.load(HERE / "id_ref_emb.npz"); keep = t["keep"]; y = np.array(m["y"])[keep]
    dets = {"clipe5b": "clipe5b_s20260929", "lambda0": "clipe5bzl0_s20260929", "effort": "effort"}
    def rmiss(s):
        g = s[y == 0]; th = np.quantile(g, 0.95); return (s[y == 1] <= th).mean() * 100
    rk = lambda s: np.argsort(np.argsort(s)) / len(s)
    res = {"train_n": int(ok.sum()), "train_fail": int((~ok).sum()), "C": float(clf.C_[0]), "rows": {}}
    for c in P.CONDS:
        e = t[c]; good = ~np.isnan(e[:, 0]); s = np.full(len(y), np.nan); s[good] = clf.decision_function(e[good])
        assert good.all()
        r = {"arcface_lr": (roc_auc_score(y, s), rmiss(s))}
        for k, f in dets.items():
            d = np.load(HERE / f"smooth38_{f}.npz")[c][keep].astype(float); r[k] = (roc_auc_score(y, d), rmiss(d))
            if k == "lambda0":
                fu = rk(s) + rk(d); r["fusion lambda0+arcface_lr"] = (roc_auc_score(y, fu), rmiss(fu))
        res["rows"][c] = {k: [round(float(a), 4), round(float(b), 1)] for k, (a, b) in r.items()}
    (HERE / "ffpp_arcface.json").write_text(json.dumps(res, indent=1))
    names = list(res["rows"]["untreated"]); L = [f"# Addendum 53: frozen ArcFace + LR (FF++ train, n {res['train_n']}, C {res['C']:.3g}) on Celeb-DF probes, reference-free. Cell = AUC / recalibrated miss % (5% FPR on that condition's genuine)", "",
         "| score | " + " | ".join(P.CONDS) + " |", "|---" * (len(P.CONDS) + 1) + "|"]
    for n in names:
        L.append(f"| {n} | " + " | ".join(f"{res['rows'][c][n][0]} / {res['rows'][c][n][1]}" for c in P.CONDS) + " |")
    (HERE / "FFPP_ARCFACE.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    {"embed": embed, "analyse": analyse}[sys.argv[1]]()
