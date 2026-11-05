"""Celeb-DF-B with ONE rule for every detector (PRE_DECLARED Addendum 6 of retouch_unified_20260929).

score = P(fake). Per detector: AUC on untreated / beautified / compression-only pairs; at the threshold of 5 % FPR on
untreated genuine frames, MISS (forgery not called fake) and FA (genuine called fake) per condition; the rise in MISS under
beautification, under re-encoding alone, and their difference, with 95 % video-cluster bootstrap intervals; and the paired
difference of the beautified-pair AUC against each reference detector. For three-way models the native decision is
reported too, with forgeries called filter counted as missed.

python fair_cdfb.py [name ...]  -> fair_cdfb.json, FAIR_cdfb.md   (default: every file in scores_v3/)
"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent; BASE = Path(r"C:\My_Project\AIGC")
SPLIT = BASE / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt"; NB = 1000
REF = ["effort", "fadapter", "sbi", "dfdhr", "gend", "caddm"]   # 2026-10-22: the three strongest 2026 detectors added as references
ORDER = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter", "univfd", "npr", "gend", "dfdhr", "caddm", "laanetr"]


def main():
    rows = [l.split("\t") for l in SPLIT.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    folder = np.array([r[3] for r in rows]); vid = np.array([r[2] for r in rows])
    vids = sorted(set(vid)); vix = {v: np.where(vid == v)[0] for v in vids}
    rng = np.random.default_rng(1); boots = [np.concatenate([vix[vids[j]] for j in rng.choice(len(vids), len(vids), True)]) for _ in range(NB)]

    def stats(s, idx):
        f = folder[idx]; x = s[idx]; g = lambda k: x[f == k]
        t = np.quantile(g("real"), 0.95)
        miss = lambda k: 100 * float((g(k) <= t).mean()); fa = lambda k: 100 * float((g(k) > t).mean())
        auc = lambda a, b: float(roc_auc_score(np.r_[np.zeros(len(g(a))), np.ones(len(g(b)))], np.r_[g(a), g(b)]))
        d = miss("synthesis_beautified") - miss("synthesis"); dc = miss("synthesis_compressed") - miss("synthesis")
        return {"auc_untreated": auc("real", "synthesis"), "auc_beautified": auc("real_beautified", "synthesis_beautified"),
                "auc_compressed": auc("real_compressed", "synthesis_compressed"), "miss0": miss("synthesis"), "miss_b": miss("synthesis_beautified"),
                "miss_c": miss("synthesis_compressed"), "fa_b": fa("real_beautified"), "fa_c": fa("real_compressed"),
                "d_miss": d, "d_miss_c": dc, "d_miss_beauty_only": d - dc}

    names = sys.argv[1:] or sorted(f.stem for f in (HERE / "scores_v3").glob("*.npz"))
    S = {n: np.load(HERE / "scores_v3" / f"{n}.npz")["p"] for n in set(names) | set(REF)}
    allidx = np.arange(len(rows)); out = {}
    bref = {r: [stats(S[r][:, 1], b) for b in boots] for r in REF}
    for n in names:
        p = S[n]; s = p[:, 1]; r = {k: round(v, 4 if k.startswith("auc") else 2) for k, v in stats(s, allidx).items()}
        bs = [stats(s, b) for b in boots]
        r["ci"] = {k: [round(float(np.percentile([x[k] for x in bs], q)), 4 if k.startswith("auc") else 2) for q in (2.5, 97.5)]
                   for k in ("auc_beautified", "d_miss_beauty_only", "fa_b", "miss_b")}
        r["auc_beautified_minus"] = {}; r["d_miss_beauty_only_minus"] = {}
        for ref in REF:
            if ref != n:
                d = np.array([x["auc_beautified"] for x in bs]) - np.array([x["auc_beautified"] for x in bref[ref]])
                r["auc_beautified_minus"][ref] = [round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)]
                e = np.array([x["d_miss_beauty_only"] for x in bs]) - np.array([x["d_miss_beauty_only"] for x in bref[ref]])
                r["d_miss_beauty_only_minus"][ref] = [round(float(np.percentile(e, 2.5)), 2), round(float(np.percentile(e, 97.5)), 2)]
        if p.shape[1] == 3:
            am = p.argmax(1)
            r["native"] = {f: {"real": round(100 * float((am[folder == f] == 0).mean()), 1), "fake": round(100 * float((am[folder == f] == 1).mean()), 1),
                               "filter": round(100 * float((am[folder == f] == 2).mean()), 1)} for f in sorted(set(folder))}
        out[n] = r; print(n, json.dumps({k: v for k, v in r.items() if k not in ("native",)}), flush=True)
    f = HERE / "fair_cdfb.json"; old = json.loads(f.read_text()) if f.is_file() else {}; old.update(out); f.write_text(json.dumps(old, indent=1))
    L = ["# Celeb-DF-B, one rule for every detector (score P(fake); threshold = 5 % FPR on untreated genuine frames; MISS = forgery not called fake)", "",
         "| detector | AUC untreated | AUC beautified [95 % CI] | AUC re-encoded | FA beautified genuine | MISS untreated -> beautified | rise from beautification alone [CI] |", "|---|---|---|---|---|---|---|"]
    for n in [x for x in ORDER if x in old] + sorted(x for x in old if x not in ORDER):
        r = old[n]
        L.append(f"| {n} | {r['auc_untreated']:.3f} | {r['auc_beautified']:.3f} {r['ci']['auc_beautified']} | {r['auc_compressed']:.3f} | {r['fa_b']:.1f} | "
                 f"{r['miss0']:.1f} -> {r['miss_b']:.1f} | {r['d_miss_beauty_only']:+.1f} {r['ci']['d_miss_beauty_only']} |")
    (HERE / "FAIR_cdfb.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
