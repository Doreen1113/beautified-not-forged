"""Metrics and claims E1/E2 exactly as PRE_DECLARED §3/§5. Reads scores/*.npz.

python analyze_cdfb.py -> results.json, RESULTS.md
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

BASE = Path(r"C:\My_Project\AIGC")
HERE = Path(__file__).resolve().parent
import os
TAG = os.environ.get("CDFB_TAG", "v2")
SPLIT = BASE / f"splits/research/celebdfb_v2_20260927/cdfb_std32{TAG}.txt"
SC = "scores" if TAG == "v2" else f"scores_{TAG}"
PUBLISHED = ["xception", "effnb4", "spsl", "f3net", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter", "univfd", "npr"]
NB = 1000


def main():
    rows = [l.split("\t") for l in SPLIT.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    paths = [r[0] for r in rows]; folder = np.array([r[3] for r in rows]); vid = np.array([r[2] for r in rows])
    # annotation.csv types are real/fake (the extractor looked up "synthesis" and left fake-side presets empty)
    ann = {}
    for l in (BASE / "external_data/celebdfb/Celeb-DF-B/annotation.csv").read_text(encoding="utf-8").splitlines()[1:]:
        n_, t_, p_ = l.strip().split(";"); ann[(n_[:-4], t_)] = p_
    preset = np.array([r[4] or ann.get((r[2], "fake"), "") for r in rows])
    F = {f: np.where(folder == f)[0] for f in set(folder)}
    vids = sorted(set(vid)); vix = {v: np.where(vid == v)[0] for v in vids}  # same id across folders -> one cluster
    rng = np.random.default_rng(1); boots = [rng.choice(len(vids), len(vids), True) for _ in range(NB)]

    def rate(dec, f, idx=None):
        s = F[f] if idx is None else np.intersect1d(F[f], idx, assume_unique=False)
        return float(dec[s].mean() * 100) if len(s) else np.nan

    def metrics(called_fake, called_real, idx=None):
        return {"FA": rate(called_fake, "real_beautified", idx), "FA0": rate(called_fake, "real", idx),
                "MISS": rate(called_real, "synthesis_beautified", idx), "MISS0": rate(called_real, "synthesis", idx),
                "FAc": rate(called_fake, "real_compressed", idx), "MISSc": rate(called_real, "synthesis_compressed", idx)}

    def derive(m):
        m["dFA"] = m["FA"] - m["FA0"]; m["dMISS"] = m["MISS"] - m["MISS0"]
        m["dFA_c"] = m["FAc"] - m["FA0"]; m["dMISS_c"] = m["MISSc"] - m["MISS0"]
        return m

    def ci(called_fake, called_real):
        vals = defaultdict(list)
        for b in boots:
            idx = np.concatenate([vix[vids[j]] for j in b])
            # duplicates matter for a cluster bootstrap: use weights via repeated indices
            m = {}
            for key, f, dec in (("FA", "real_beautified", called_fake), ("FA0", "real", called_fake),
                                ("MISS", "synthesis_beautified", called_real), ("MISS0", "synthesis", called_real)):
                s = idx[folder[idx] == f]; m[key] = dec[s].mean() * 100
            vals["dFA"].append(m["FA"] - m["FA0"]); vals["dMISS"].append(m["MISS"] - m["MISS0"])
            vals["FA"].append(m["FA"]); vals["MISS"].append(m["MISS"])
        return {k: [round(float(np.percentile(v, 2.5)), 2), round(float(np.percentile(v, 97.5)), 2)] for k, v in vals.items()}

    R, curves = {}, {}
    und = np.concatenate([F["real"], F["synthesis"]]); yund = (folder[und] == "synthesis").astype(int)
    for f in sorted((HERE / SC).glob("*.npz")):
        n = f.stem; z = np.load(f); p = z["p"]
        assert list(z["paths"]) == paths, n
        binary = n in PUBLISHED or n in ("SBI-L", "SBI-F")
        pf = p[:, 1]
        r = {"kind": "binary" if binary else "three-way", "auc_untreated": round(float(roc_auc_score(yund, pf[und])), 4)}
        if binary:
            thr = float(np.quantile(pf[F["real"]], 0.95))   # 5 % FPR on untreated real
            cf, cr = pf > thr, pf <= thr
            r["threshold"] = thr
            s_rb, s_sb = pf[F["real_beautified"]], pf[F["synthesis_beautified"]]
            ts = np.unique(np.concatenate([s_rb, s_sb])); ts = ts[::max(1, len(ts) // 3000)]
            curves[n] = (np.array([(s_rb > t).mean() * 100 for t in ts]), np.array([(s_sb <= t).mean() * 100 for t in ts]))
        else:
            am = p.argmax(1); cf, cr = am == 1, am == 0
            r["to_filter"] = {fo: round(float((am[F[fo]] == 2).mean() * 100), 2) for fo in sorted(F)}
        m = derive(metrics(cf, cr)); r.update({k: round(v, 2) for k, v in m.items()}); r["ci"] = ci(cf, cr)
        r["per_preset"] = {}
        for pr in sorted(set(preset) - {""}):
            idx = np.where(preset == pr)[0]
            mm = derive(metrics(cf, cr, idx)); r["per_preset"][pr] = {k: round(v, 2) for k, v in mm.items() if k in ("dFA", "dMISS", "FA", "MISS")}
        R[n] = r

    pub = [n for n in PUBLISHED if n in R]
    med = {k: float(np.median([abs(R[n][k]) for n in pub])) for k in ("dFA", "dMISS")} if pub else {}
    for n, r in R.items():
        if r["kind"] != "three-way":
            continue
        r["E1_dominated_by"] = [b for b, (FA, MS) in curves.items() if b in PUBLISHED and ((FA <= r["FA"]) & (MS <= r["MISS"])).any()]
        r["E1"] = not r["E1_dominated_by"] and len(pub) == 11
        r["E2"] = bool(med) and abs(r["dFA"]) <= med["dFA"] and abs(r["dMISS"]) <= med["dMISS"]
    L = ["# Celeb-DF-B v2 — results (PRE_DECLARED metrics, nothing changed after scoring)", "",
         f"Frames: {len(paths):,}; published-detector medians |ΔFA| {med.get('dFA', float('nan')):.2f} / |ΔMISS| {med.get('dMISS', float('nan')):.2f}", "",
         "| model | kind | AUC untreated | FA0 → FA (ΔFA) | MISS0 → MISS (ΔMISS) | ΔFA_c / ΔMISS_c (compression) | E1 | E2 |",
         "|---|---|---|---|---|---|---|---|"]
    for n, r in sorted(R.items(), key=lambda kv: (kv[1]["kind"] != "three-way", kv[0])):
        L.append(f"| {n} | {r['kind']} | {r['auc_untreated']} | {r['FA0']} → {r['FA']} ({r['dFA']:+} {r['ci']['dFA']}) | "
                 f"{r['MISS0']} → {r['MISS']} ({r['dMISS']:+} {r['ci']['dMISS']}) | {r['dFA_c']:+} / {r['dMISS_c']:+} | "
                 f"{'' if r['kind'] == 'binary' else (str(r['E1']) + ' ' + str(r['E1_dominated_by']))} | {r.get('E2', '')} |")
    (HERE / ("RESULTS.md" if TAG == "v2" else f"RESULTS_{TAG}.md")).write_text("\n".join(L) + "\n", encoding="utf-8")
    json.dump(R, open(HERE / ("results.json" if TAG == "v2" else f"results_{TAG}.json"), "w"), indent=1)
    print("\n".join(L))


if __name__ == "__main__":
    main()
