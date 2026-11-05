"""Addendum 63: beautification-aware reference gate on Celeb-DF-B. Reuses the embeddings and alignment of cdfb_id_probe.py
(cdfb_id_emb.npz); b = beautified logit of the three-way model recovered from scores_v3/RU-clipe5.npz; no training, no tuning.
python cdfb_gate_probe.py  -> cdfb_gate.json, CDFB_GATE.md"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import cdfb_id_probe as P  # noqa: E402

z = np.load(HERE / "cdfb_id_emb.npz"); fold = z["folder"]; vid = z["video"]; path = z["path"]; E = z["emb"]
R = dict(zip(z["ref_ids"], z["ref"])); cl = np.array([P.claimed(v) for v in vid])
ident = np.array([1 - float(E[j] @ R[cl[j]]) if cl[j] in R and not np.isnan(E[j, 0]) else np.nan for j in range(len(vid))])
sel = {d: fold == d for d in P.FOLDERS}


def aligned(key, col):
    q = np.load(P.SC / f"{key}.npz"); m = {Path(p).name + "|" + Path(p).parent.name: i for i, p in enumerate(q["paths"].tolist())}
    s = np.full(len(vid), np.nan)
    for j in range(len(vid)):
        k = Path(path[j]).name + "|" + fold[j]
        if k in m:
            s[j] = col(q["p"][m[k]])
    assert np.isfinite(s).mean() > 0.95, key
    return s


tex = {n: aligned(P.TEX[n], lambda p: p[1]) for n in ("effort", "fadapter", "gend", "ours")}
b = aligned(P.TEX["ours"], lambda p: p[2] / max(p[0] + p[2], 1e-9))   # sigma(z_b): beautified / (real + beautified)


def quant(x):
    g = np.sort(x[sel["real"] & np.isfinite(x)]); return np.searchsorted(g, x) / len(g)


w = np.clip(quant(b), 0, 1); q_id = quant(ident)


def fa(s, mask, t):
    v = s[mask]; v = v[np.isfinite(v)]; return float((v > t).mean() * 100)


def miss(s, mask, t):
    v = s[mask]; v = v[np.isfinite(v)]; return float((v <= t).mean() * 100)


def vauc(s, g, f_):
    a, c = [], []
    for v in np.unique(vid[g]):
        x = s[g & (vid == v)]; x = x[np.isfinite(x)]
        if len(x): a.append(x.mean())
    for v in np.unique(vid[f_]):
        x = s[f_ & (vid == v)]; x = x[np.isfinite(x)]
        if len(x): c.append(x.mean())
    return float(roc_auc_score([0] * len(a) + [1] * len(c), a + c))


def row(s):
    t = np.nanquantile(s[sel["real"]], 0.95); r = {}
    for d in P.FOLDERS:
        r[("fa_" if d.startswith("real") else "miss_") + d] = (fa if d.startswith("real") else miss)(s, sel[d], t)
    r["d_fa_beauty_only"] = r["fa_real_beautified"] - r["fa_real_compressed"]; r["d_miss_beauty_only"] = r["miss_synthesis_beautified"] - r["miss_synthesis_compressed"]
    r["ci_d_fa_beauty_only"] = P.boot_ci(lambda idx: fa(s[idx], sel["real_beautified"][idx], t) - fa(s[idx], sel["real_compressed"][idx], t), vid, seed=1)
    r["ci_d_miss_beauty_only"] = P.boot_ci(lambda idx: miss(s[idx], sel["synthesis_beautified"][idx], t) - miss(s[idx], sel["synthesis_compressed"][idx], t), vid, seed=2)
    r["ci_miss_untreated"] = P.boot_ci(lambda idx: miss(s[idx], sel["synthesis"][idx], t), vid, seed=3)
    r["vauc_untreated"] = vauc(s, sel["real"], sel["synthesis"]); r["vauc_beautified"] = vauc(s, sel["real_beautified"], sel["synthesis_beautified"])
    r["vauc_compressed"] = vauc(s, sel["real_compressed"], sel["synthesis_compressed"])
    t5 = np.nanquantile(s[sel["real_beautified"]], 0.95); r["miss_beautified_at_matched_5fa"] = miss(s, sel["synthesis_beautified"], t5)
    return {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}


res = {"w_summary": {d: round(float(np.nanmean(w[sel[d]])), 3) for d in P.FOLDERS}, "rows": {}}
res["rows"]["identity"] = row(ident)
for n, s in tex.items():
    q_t = quant(s)
    res["rows"][n] = row(s)
    res["rows"][f"fusion_{n}+identity"] = row((q_t + q_id) / 2)
    g = w * q_id + (1 - w) * q_t
    res["rows"][f"gate_{n}+identity"] = row(g)
    f_u = sel["synthesis"] & np.isfinite(g) & np.isfinite(s)
    res["rows"][f"gate_{n}+identity"]["spearman_vs_texture_untreated_forged"] = round(float(spearmanr(g[f_u], s[f_u]).correlation), 3)
I = res["rows"]["identity"]; pairs = list(tex)
G = {n: res["rows"][f"gate_{n}+identity"] for n in pairs}
p1 = all(G[n]["d_fa_beauty_only"] <= 10 and G[n]["d_miss_beauty_only"] <= 5 for n in pairs)
p2 = all(G[n]["vauc_untreated"] >= res["rows"][n]["vauc_untreated"] and G[n]["vauc_beautified"] >= 0.98 for n in pairs)
p3 = all(G[n]["miss_beautified_at_matched_5fa"] <= 15 for n in pairs)
hw = (I["ci_miss_untreated"][1] - I["ci_miss_untreated"][0]) / 2
p4 = all(abs(G[n]["miss_synthesis"] - I["miss_synthesis"]) > hw or G[n]["spearman_vs_texture_untreated_forged"] > 0.5 for n in pairs)
res["predictions"] = {"1_all_pairs_fa_le10_miss_le5": bool(p1), "2_vauc_ge_texture_and_beaut_ge_0.98": bool(p2), "3_matched_miss_le15": bool(p3), "4_not_identity_alone": bool(p4)}
(HERE / "cdfb_gate.json").write_text(json.dumps(res, indent=1))
L = ["# Addendum 63: beautification-aware reference gate on Celeb-DF-B (w = quantile of the model's own beautified logit)", "",
     "mean w per folder: " + json.dumps(res["w_summary"]), "", "Predictions: " + json.dumps(res["predictions"]), "",
     "| score | vAUC untr / beaut / compr | FA real / beaut / compr | dFA beauty-only [CI] | miss syn / beaut / compr [CI untr] | dMISS beauty-only [CI] | miss beaut @5% FA on beaut genuine | Spearman vs texture (untr. forged) |",
     "|---|---|---|---|---|---|---|---|"]
for n, r in res["rows"].items():
    L.append(f"| {n} | {r['vauc_untreated']:.3f} / {r['vauc_beautified']:.3f} / {r['vauc_compressed']:.3f} | {r['fa_real']:.1f} / {r['fa_real_beautified']:.1f} / {r['fa_real_compressed']:.1f} | "
             f"{r['d_fa_beauty_only']:+.1f} [{r['ci_d_fa_beauty_only'][0]:+.1f}, {r['ci_d_fa_beauty_only'][1]:+.1f}] | {r['miss_synthesis']:.1f} [{r['ci_miss_untreated'][0]:.1f}, {r['ci_miss_untreated'][1]:.1f}] / {r['miss_synthesis_beautified']:.1f} / {r['miss_synthesis_compressed']:.1f} | "
             f"{r['d_miss_beauty_only']:+.1f} [{r['ci_d_miss_beauty_only'][0]:+.1f}, {r['ci_d_miss_beauty_only'][1]:+.1f}] | {r['miss_beautified_at_matched_5fa']:.1f} | {r.get('spearman_vs_texture_untreated_forged', '')} |")
(HERE / "CDFB_GATE.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))
