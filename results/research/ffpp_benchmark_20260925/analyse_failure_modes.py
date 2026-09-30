"""What do the published detectors actually DO with a beautified face? (analysis, not a bar)

The benchmark table gives each model one (FA, MISS) point. This asks the structural questions behind it, which only
our paired data can answer:

 1. **Does beautification push a face toward `fake` or toward `real`?** For each model, the shift in its P(fake)
    between an unedited frame and the SAME frame beautified. A positive shift on genuine faces is the
    false-accusation mechanism; a negative shift on fakes is the escape mechanism. Same photograph both times, so
    the shift is caused by the edit and nothing else.
 2. **Is the FA/MISS trade-off structural?** For every model, the minimum achievable FA+MISS over all thresholds,
    and whether any threshold gets both low. A binary detector cannot: pushing the threshold down to catch
    beautified fakes must also flag beautified reals, because it moved the same scalar.
 3. **Which edit does the damage?** Per filter op, how much each model's score moves — so the paper can say which
    beautification operations actually break detectors, rather than treating "filters" as one undifferentiated thing.

python analyse_failure_modes.py -> failure_modes.json, failure_modes.md
"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
BASE = Path(r"C:\My_Project\AIGC")
UNI = BASE / "results/research/ffpp_unified_20260925"


def load_alignment():
    """filter row i <-> its source real frame; and the escape rows' condition labels."""
    frows = [l.split("\t") for l in (UNI / "filter_test.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    trows = [l.split("\t") for l in (UNI / "ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    real_paths = [r[0] for r in trows if r[1] == "0"]
    real_idx = {p: i for i, p in enumerate(real_paths)}
    # filter rows are emitted in the same order as ffpp3_test's label-2 block
    filt_paths = [r[0] for r in trows if r[1] == "2"]
    fpos = {r[0]: r for r in frows}
    pair_src, pair_op = [], []
    for p in filt_paths:
        r = fpos.get(p)
        pair_src.append(real_idx.get(r[5], -1) if r else -1)
        pair_op.append(r[3] if r else "?")
    esc = [l.split("\t") for l in (BASE / "ffpp_escape_cache/manifest.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return np.array(pair_src), np.array(pair_op, dtype=object), [e[1] for e in esc]


def main():
    pair_src, pair_op, esc_cond = load_alignment()
    out = {}
    for f in sorted(HERE.glob("scores_*.npz")):
        name = f.stem[len("scores_"):]
        z = np.load(f)
        sr, sf, sl, se = z["real"], z["fake"], z["filter"], z["escape"]
        ok = pair_src >= 0
        if len(sl) != len(pair_src):
            ok = ok[:len(sl)]
            src = pair_src[:len(sl)]
            ops = pair_op[:len(sl)]
        else:
            src, ops = pair_src, pair_op
        # 1) paired shift on genuine faces: same photograph, edited minus unedited
        shift = sl[ok] - sr[src[ok]]
        r = {"n_pairs": int(ok.sum()),
             "paired_shift_mean": round(float(shift.mean()), 4),
             "paired_shift_median": round(float(np.median(shift)), 4),
             "pct_pairs_pushed_toward_fake": round(float((shift > 0).mean() * 100), 2)}
        # per op
        per = {}
        for o in sorted(set(ops[ok])):
            s = shift[ops[ok] == o]
            if len(s):
                per[o] = {"n": int(len(s)), "mean_shift": round(float(s.mean()), 4),
                          "pct_toward_fake": round(float((s > 0).mean() * 100), 1)}
        r["per_op_shift"] = per
        # 2) structural trade-off: best achievable FA+MISS over all thresholds
        ts = np.unique(np.concatenate([sr, sl, se]))
        step = max(1, len(ts) // 3000)
        ts = ts[::step]
        fa = np.array([(sl > t).mean() for t in ts]) * 100
        ms = np.array([(se <= t).mean() for t in ts]) * 100
        j = int(np.argmin(fa + ms))
        r["best_sum"] = {"FA": round(float(fa[j]), 2), "MISS": round(float(ms[j]), 2),
                         "sum": round(float(fa[j] + ms[j]), 2), "t": float(ts[j])}
        r["min_FA_at_MISS_le_5"] = round(float(fa[ms <= 5].min()), 2) if (ms <= 5).any() else None
        r["min_MISS_at_FA_le_5"] = round(float(ms[fa <= 5].min()), 2) if (fa <= 5).any() else None
        # 3) escape mechanism: how much does beautification move a FAKE's score down
        per_c = {}
        for c in sorted(set(esc_cond[:len(se)])):
            m = np.array([x == c for x in esc_cond[:len(se)]])
            if m.any():
                per_c[c] = round(float(se[m].mean()), 4)
        r["escape_score_by_condition"] = per_c
        r["clean_fake_mean_score"] = round(float(sf.mean()), 4)
        out[name] = r

    lines = ["# Failure modes of published detectors under beautification",
             "",
             "Same photograph, edited or not, so every shift below is caused by the edit alone.",
             "",
             "| model | mean P(fake) shift when a GENUINE face is beautified | % of pairs pushed toward *fake* | "
             "best achievable FA+MISS (any threshold) | min FA at MISS<=5% | min MISS at FA<=5% |",
             "|---|---|---|---|---|---|"]
    for k in sorted(out, key=lambda x: -out[x]["paired_shift_mean"]):
        r = out[k]
        lines.append(f"| {k} | {r['paired_shift_mean']:+.4f} | {r['pct_pairs_pushed_toward_fake']} | "
                     f"{r['best_sum']['sum']} (FA {r['best_sum']['FA']} / MISS {r['best_sum']['MISS']}) | "
                     f"{r['min_FA_at_MISS_le_5']} | {r['min_MISS_at_FA_le_5']} |")
    lines += ["", "## Which beautification operation moves each detector most (mean P(fake) shift on genuine faces)", ""]
    ops = sorted({o for r in out.values() for o in r["per_op_shift"]})
    lines.append("| model | " + " | ".join(o.replace("pilgram:", "") for o in ops) + " |")
    lines.append("|---" * (len(ops) + 1) + "|")
    for k in sorted(out):
        row = [f"{out[k]['per_op_shift'].get(o, {}).get('mean_shift', float('nan')):+.3f}" for o in ops]
        lines.append(f"| {k} | " + " | ".join(row) + " |")
    (HERE / "failure_modes.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / "failure_modes.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print("\n".join(lines[:20]))
    print(f"\n[wrote] failure_modes.md / .json for {len(out)} models")


if __name__ == "__main__":
    main()
