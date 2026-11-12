"""Direction A of the two-direction main claim (2026-10-22): commercial skin smoothing (Alibaba Smoothing-90, pixel-aligned
pairs) makes published detectors score the genuine face as MORE forged than its own original. Per detector: paired share
(render scored above its own original), FA at the threshold of 5 % FPR on the originals, with 95 % bootstrap CIs over pairs
(unit = FFHQ index), and the paired difference of the share against our main model (same pairs, same resamples).
python main_claim_A.py -> main_claim_A.json, MAIN_CLAIM_A.md"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; RU = HERE.parent / "retouch_unified_20260929"
PUB = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter", "univfd", "npr", "gend", "dfdhr", "caddm", "laanetr"]
OURS = {"ours main s1": "clipe5_s20260929", "ours main s2": "clipe5_s20260930"}
OP = "Smoothing_90"; NB = 2000


def load(name):
    if name in OURS:
        z = np.load(RU / f"ali_scores_{OURS[name]}.npz"); s = z["P"][:, 1].astype(float); am = z["P"].argmax(1)
    else:
        z = np.load(HERE / f"published_scores_{name}.npz"); s = z["s"].astype(float); am = None
    g = z["group"]; st = z["stem"]
    o = {k: v for k, v in zip(st[g == "orig_0"], s[g == "orig_0"])}; r = {k: v for k, v in zip(st[g == OP], s[g == OP])}
    keys = sorted(set(o) & set(r)); so = np.array([o[k] for k in keys]); sr = np.array([r[k] for k in keys])
    dec = None
    if am is not None:
        ao = {k: v for k, v in zip(st[g == "orig_0"], am[g == "orig_0"])}; ar = {k: v for k, v in zip(st[g == OP], am[g == OP])}
        dec = (np.array([ao[k] for k in keys]), np.array([ar[k] for k in keys]))
    return keys, so, sr, dec


def main():
    data = {n: load(n) for n in PUB + list(OURS)}
    keys = data["effort"][0]; assert all(d[0] == keys for d in data.values()), "pair sets differ"
    n = len(keys); rng = np.random.default_rng(0); boots = [rng.integers(0, n, n) for _ in range(NB)]
    up = {}; res = {"n_pairs": n, "rows": {}}
    for name, (_, so, sr, dec) in data.items():
        u = sr > so; t = np.quantile(so, 0.95); fa = sr > t
        up[name] = np.array([u[b].mean() for b in boots]) * 100
        row = {"paired_up": round(float(u.mean() * 100), 1), "paired_up_ci": [round(float(np.percentile(up[name], q)), 1) for q in (2.5, 97.5)],
               "fa_s90_at_5pct": round(float(fa.mean() * 100), 1), "fa_ci": [round(float(np.percentile([fa[b].mean() * 100 for b in boots], q)), 1) for q in (2.5, 97.5)]}
        if dec is not None:
            ao, ar = dec; row["native_orig"] = {c: round(float((ao == i).mean() * 100), 1) for i, c in enumerate(["real", "fake", "filter"])}
            row["native_s90"] = {c: round(float((ar == i).mean() * 100), 1) for i, c in enumerate(["real", "fake", "filter"])}
        res["rows"][name] = row
    for o in OURS:
        res["rows"][o]["paired_up_minus"] = {p: [round(float(np.percentile(up[o] - up[p], q)), 1) for q in (2.5, 97.5)] for p in PUB}
    (HERE / "main_claim_A.json").write_text(json.dumps(res, indent=1))
    L = [f"# Direction A: commercial skin smoothing (Alibaba Smoothing-90), {n} pixel-aligned pairs; bootstrap over pairs (unit = FFHQ index)", "",
         "| detector | render scored above own original % [CI] | FA on smoothed genuine at 5 % FPR of originals % [CI] | native decision orig / S90 |", "|---|---|---|---|"]
    for name in PUB + list(OURS):
        r = res["rows"][name]; nat = f"{r['native_orig']} / {r['native_s90']}" if "native_orig" in r else ""
        L.append(f"| {name} | {r['paired_up']} {r['paired_up_ci']} | {r['fa_s90_at_5pct']} {r['fa_ci']} | {nat} |")
    L += ["", "Paired difference (ours minus published) of the share, 95 % CI; the interval excludes 0 = different at the pair level:"]
    for o in OURS:
        L.append(f"- {o}: " + "; ".join(f"{p} {res['rows'][o]['paired_up_minus'][p]}" for p in PUB))
    (HERE / "MAIN_CLAIM_A.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    main()
