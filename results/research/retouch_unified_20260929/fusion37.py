"""Addendum 37: fusion of a texture-based and a boundary-based detector (released weights, no training).
Genuine-quantile normalisation per source; F_mean, F_min, F_prod; fixed pairs. python fusion37.py -> fusion37.json"""
import json
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent; R = HERE.parent
PAIRS = [("gend", "caddm"), ("dfdhr", "caddm"), ("effort", "caddm"), ("clipe5fbp0_s20260929", "caddm")]
RULES = {"mean": lambda a, b: (a + b) / 2, "min": np.minimum, "prod": lambda a, b: a * b}


def q(s, ref):
    r = np.sort(ref[~np.isnan(ref)]); return np.searchsorted(r, s, side="left") / len(r)


def vauc(s, y, v):
    k = ~np.isnan(s); s, y, v = s[k], y[k], v[k]; u, i = np.unique(v, return_inverse=True)
    return float(roc_auc_score(np.bincount(i, y) / np.bincount(i) > 0.5, np.bincount(i, s) / np.bincount(i)))


def ali(name):
    f = R / "alipair_zeroshot_20260929" / f"published_scores_{name}.npz"
    if f.is_file():
        z = np.load(f); return z["s"].astype(float), z["group"], z["stem"]
    z = np.load(HERE / f"ali_scores_{name}.npz"); return z["P"][:, 1].astype(float), z["group"], z["stem"]


def ali_stats(s, g, st):
    o = g == "orig_0"; m = g == "Smoothing_90"; so = dict(zip(st[o], s[o])); t = np.nanquantile(s[o], 0.95)
    return {"s90_at_5fpr": round(float((s[m] > t).mean() * 100), 1), "s90_above_own_original": round(float(np.mean([v > so[k] for v, k in zip(s[m], st[m])]) * 100), 1),
            "all_at_5fpr": round(float((s[~o] > t).mean() * 100), 1)}


def cdf(name):
    z = np.load(HERE / f"cdf_filtered_scores_{name}.npz"); return z["untreated"].astype(float), z["y"], z["video"]


def dfd(name):
    z = np.load(HERE / f"dfd_v3_scores_{name}.npz"); k = "s" if "s" in z else ("p" if "p" in z else z.files[0]); return z[k].astype(float), z["y"], z["video"]


def df40(name):
    f = R / "df40_eval_20261012" / f"scores_{name}.npz"
    return np.load(f)["s"].astype(float) if f.is_file() else None


def df40_stats(s, rows):
    FS = {"blendface", "e4s", "facedancer", "faceswap", "fsgan", "inswap", "mobileswap", "simswap", "uniface"}
    vid = np.array([f"{x[4]}|{x[3]}|{x[2]}" for x in rows]); uv, inv = np.unique(vid, return_inverse=True); k = ~np.isnan(s)
    v = np.bincount(inv[k], s[k], len(uv)) / np.maximum(np.bincount(inv[k], minlength=len(uv)), 1)
    dom = np.array([u.split("|")[0] for u in uv]); me = np.array([u.split("|")[1] for u in uv]); out = {}
    for d in ("ff", "cdf"):
        real = v[(dom == d) & (me == "real")]; per = {}
        for m in sorted(set(me[dom == d]) - {"real"}):
            f = v[(dom == d) & (me == m)]; per[m] = roc_auc_score(np.r_[np.zeros(len(real)), np.ones(len(f))], np.r_[real, f])
        out[f"{d}/FS"] = round(float(np.mean([a for m, a in per.items() if m in FS])), 3); out[f"{d}/FR"] = round(float(np.mean([a for m, a in per.items() if m not in FS])), 3)
    return out


def main():
    out = {}
    rows40 = [l.split("\t") for l in (R / "df40_eval_20261012/df40_eval_list.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    lab40 = np.array([x[3] for x in rows40]); dom40 = np.array([x[4] for x in rows40])
    for a, b in PAIRS:
        res = {}
        # retouching service
        sa, g, st = ali(a); sb, g2, st2 = ali(b)
        if not ((g == g2).all() and (st == st2).all()):   # our score files list the items in another order: align on (group, stem)
            idx = {(x, y_): i for i, (x, y_) in enumerate(zip(g2, st2))}; sb = sb[[idx[(x, y_)] for x, y_ in zip(g, st)]]
        o = g == "orig_0"
        qa, qb = q(sa, sa[o]), q(sb, sb[o]); res["retouch"] = {a: ali_stats(sa, g, st), b: ali_stats(sb, g, st), **{r: ali_stats(f(qa, qb), g, st) for r, f in RULES.items()}}
        # untreated Celeb-DF-v2 / DFD
        for nm, load in (("cdf", cdf), ("dfd", dfd)):
            try:
                sa, y, v = load(a); sb, y2, v2 = load(b)
            except FileNotFoundError as e:
                res[nm] = {"missing": str(e)[-60:]}; continue
            assert (v == v2).all(); gz = y == 0; qa, qb = q(sa, sa[gz]), q(sb, sb[gz])
            res[nm] = {a: round(vauc(sa, y, v), 3), b: round(vauc(sb, y, v), 3), **{r: round(vauc(f(qa, qb), y, v), 3) for r, f in RULES.items()}}
        # DF40
        sa, sb = df40(a), df40(b)
        if sa is None or sb is None:
            res["df40"] = {"missing": a if sa is None else b}
        else:
            qa, qb = np.zeros_like(sa), np.zeros_like(sb)
            for d in ("ff", "cdf"):
                m = dom40 == d; gz = m & (lab40 == "real"); qa[m] = q(sa[m], sa[gz]); qb[m] = q(sb[m], sb[gz])
            res["df40"] = {a: df40_stats(sa, rows40), b: df40_stats(sb, rows40), **{r: df40_stats(f(qa, qb), rows40) for r, f in RULES.items()}}
        out[f"{a}+{b}"] = res
        print(f"== {a} + {b}")
        for k, v in res.items():
            print("  ", k, json.dumps(v))
    (HERE / "fusion37.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
