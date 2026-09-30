"""Build the final table from whatever scores_<model>.npz files exist (PRE_DECLARED §4-§5).

Robust to a model having failed: it simply does not appear. Recomputes every metric from the raw scores so the
table can never disagree with the stored predictions.

python aggregate.py  -> benchmark_table.md, benchmark_final.json
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent
UNI = Path(r"C:\My_Project\AIGC") / "results/research/ffpp_unified_20260925"
SEED = 20260925
PARAMS = {"xception": 21.86, "effnb4": 19.34, "spsl": 21.86, "f3net": 21.86, "ucf": 21.86,
          "recce": 47.69, "core": 21.86, "srm": 53.25, "sbi": 17.55, "univfd": 427.62, "npr": 1.44,
          "ours3_mnv4_10ep": 2.50, "ours3_mnv4_20ep": 2.50, "ours3_repvit_20ep": 5.67}


def video_ids():
    rows = [l.split("\t") for l in (UNI / "ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    filt = [r[2] for r in rows if r[1] == "2"]
    esc_man = Path(r"C:\My_Project\AIGC") / "ffpp_escape_cache" / "manifest.tsv"
    esc = [l.split("\t")[2] for l in esc_man.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return filt, esc


def boot_ci(vals, groups, n=2000):
    rng = np.random.default_rng(SEED)
    by = defaultdict(list)
    for i, g in enumerate(groups):
        by[g].append(i)
    keys = list(by)
    vals = np.asarray(vals, float)
    bs = [vals[np.concatenate([by[keys[k]] for k in rng.choice(len(keys), len(keys), True)])].mean() for _ in range(n)]
    return [round(float(np.percentile(bs, 2.5)) * 100, 2), round(float(np.percentile(bs, 97.5)) * 100, 2)]


def main():
    vid_filt, vid_esc = video_ids()
    res = {}
    for f in sorted(HERE.glob("scores_*.npz")):
        name = f.stem[len("scores_"):]
        z = np.load(f)
        sr, sf, sl, se = z["real"], z["fake"], z["filter"], z["escape"]
        t5 = float(np.percentile(sr, 95))
        r = {"params_M": PARAMS.get(name),
             "FA": round(float((sl > t5).mean() * 100), 2),
             "MISS": round(float((se <= t5).mean() * 100), 2),
             "clean_fake_recall": round(float((sf > t5).mean() * 100), 2),
             "auroc_real_vs_fake": round(float(roc_auc_score([0] * len(sr) + [1] * len(sf), np.concatenate([sr, sf]))), 4),
             "auroc_real_vs_filter": round(float(roc_auc_score([0] * len(sr) + [1] * len(sl), np.concatenate([sr, sl]))), 4),
             "rule": "P(fake) at 5% clean-real FPR"}
        r["FA_ci"] = boot_ci((sl > t5).astype(float), vid_filt[:len(sl)])
        r["MISS_ci"] = boot_ci((se <= t5).astype(float), vid_esc[:len(se)])
        # full sweep, for the dominance test
        ts = np.unique(np.concatenate([sr, sl, se]))
        step = max(1, len(ts) // 2000)
        ts = ts[::step]
        r["_curve"] = {"t": ts, "FA": np.array([(sl > t).mean() for t in ts]) * 100,
                       "MISS": np.array([(se <= t).mean() for t in ts]) * 100}
        res[name] = r

    # native-rule rows for ours, if the per-model json captured them
    for jf in sorted(HERE.glob("benchmark*.json")):
        try:
            d = json.loads(jf.read_text(encoding="utf-8"))
        except Exception:
            continue
        for k, v in d.items():
            if isinstance(v, dict) and "native_rule" in v and k in res:
                res[k]["native_rule"] = v["native_rule"]

    # B1 dominance against ours' deployed point
    ours = next((k for k in res if k.startswith("ours3") and "native_rule" in res[k]), None)
    b1 = None
    if ours:
        fa_o = res[ours]["native_rule"]["FA_filter_called_fake"]
        miss_o = res[ours]["native_rule"]["MISS_beautified_fake_called_real"]
        viol = {}
        for k, r in res.items():
            if k.startswith("ours3"):
                continue
            fa_c, miss_c = r["_curve"]["FA"], r["_curve"]["MISS"]
            dom = (fa_c <= fa_o + 1e-9) & (miss_c <= miss_o + 1e-9)
            if dom.any():
                i = int(np.where(dom)[0][int(np.argmin((fa_c + miss_c)[dom]))])
                viol[k] = {"FA": round(float(fa_c[i]), 2), "MISS": round(float(miss_c[i]), 2),
                           "t": float(r["_curve"]["t"][i])}
        b1 = {"ours": ours, "ours_FA": fa_o, "ours_MISS": miss_o, "n_violations": len(viol),
              "violations": viol,
              "verdict": "SUPPORTED (no binary model dominates on both axes)" if not viol
                         else f"REFUTED by {sorted(viol)}"}

    lines = ["| model | params (M) | FA % (filter called fake) | MISS % (beautified fake called real) | clean fake recall % | AUROC r/f |",
             "|---|---|---|---|---|---|"]
    for k in sorted(res, key=lambda x: (x.startswith("ours3"), res[x]["FA"])):
        r = res[k]
        star = " **(native rule)**" if "native_rule" in r else ""
        lines.append(f"| {k}{star} | {r['params_M']} | {r['FA']} {r['FA_ci']} | {r['MISS']} {r['MISS_ci']} | "
                     f"{r['clean_fake_recall']} | {r['auroc_real_vs_fake']} |")
        if "native_rule" in r:
            n = r["native_rule"]
            lines.append(f"| &nbsp;&nbsp;↳ *{k} at its deployed argmax rule* | {r['params_M']} | "
                         f"**{n['FA_filter_called_fake']:.2f}** | **{n['MISS_beautified_fake_called_real']:.2f}** | "
                         f"{n['fake_recall']:.2f} | — |")
    table = "\n".join(lines)
    if b1:
        table += f"\n\n**B1 dominance test**: ours at FA={b1['ours_FA']:.2f} / MISS={b1['ours_MISS']:.2f} — " \
                 f"{b1['n_violations']} of {len(res) - 1} binary models attain both. **{b1['verdict']}**"
    (HERE / "benchmark_table.md").write_text(table + "\n", encoding="utf-8")
    out = {k: {kk: vv for kk, vv in v.items() if kk != "_curve"} for k, v in res.items()}
    out["_B1"] = b1
    (HERE / "benchmark_final.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(table)


if __name__ == "__main__":
    main()
