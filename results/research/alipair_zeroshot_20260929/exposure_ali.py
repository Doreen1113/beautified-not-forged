"""Exposure arms on the unseen retouching service (post hoc analysis of existing score files, 2026-10-12; not pre-registered).
Rule as in eval_published_ali.block: threshold = 95th percentile of P(fake) on the untouched originals; report the share of
retouched renders above it (all renders; Smoothing level 90). Paired bootstrap over identities (2,210 stems), 1000 draws,
threshold recomputed inside each draw, same draws for both arms."""
import json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; RU = HERE.parent / "retouch_unified_20260929"
ARMS = {"P0": "clipe5fbp0", "P1": "clipe5fbp1", "P2": "clipe5fb", "P2 no smoothing": "clipe5fbn", "P1 no smoothing": "clipe5fbp1n", "P2 smoothing only": "clipe5fbg0o", "P1 smoothing only": "clipe5fbg0p1o", "P0 Effort scheme": "clipe5fbp0E", "P2 Effort scheme": "clipe5fbE",
        "Effort fine-tuned P0": "clipe5fbp0Ei", "Effort fine-tuned P2": "clipe5fbEi", "P3 forged only": "clipe5fbp3",   # P3: Addendum 40
        "main": "clipe5", "binary control": "clipe5b", "SIC factorised": "clipe5z", "SIC binary": "clipe5bz"}   # Addendum 46
SEEDS = ["20260929", "20260930", "20261001"]


def load(tag):
    z = np.load(RU / f"ali_scores_{tag}.npz"); return z["P"][:, 1].astype(np.float64), z["group"], z["stem"]


def stats(s, g, idx_o, idx_r, idx_s):
    t = np.nanquantile(s[idx_o], 0.95)
    return (s[idx_r] > t).mean() * 100, (s[idx_s] > t).mean() * 100


def main():
    rng = np.random.default_rng(0); out = {}
    s0, g, st = load("clipe5fbp0_s20260929"); ids = np.unique(st); by = {k: np.where(st == k)[0] for k in ids}
    o = g == "orig_0"; sm = g == "Smoothing_90"
    draws = [np.concatenate([by[k] for k in rng.choice(ids, len(ids))]) for _ in range(1000)]

    def boot(sa, sb=None):
        R = []
        for d in draws:
            go = o[d]; gs = sm[d]
            a = stats(sa[d], None, go, ~go, gs)
            R.append(a if sb is None else np.subtract(stats(sb[d], None, go, ~go, gs), a))
        R = np.array(R); return [[round(float(np.percentile(R[:, j], q)), 2) for q in (2.5, 97.5)] for j in (0, 1)]

    for arm, tag in ARMS.items():
        for sd in SEEDS:
            f = RU / f"ali_scores_{tag}_s{sd}.npz"
            if not f.is_file():
                continue
            s, g2, st2 = load(f"{tag}_s{sd}"); assert (st2 == st).all() and (g2 == g).all()
            p = stats(s, None, o, ~o, sm); ci = boot(s)
            out[f"{arm} s{sd}"] = {"ret_fake_at_t": round(p[0], 2), "ci": ci[0], "smooth90_fake_at_t": round(p[1], 2), "smooth90_ci": ci[1]}
    for a, b in (("P0", "P1"), ("P0", "P2"), ("P0", "P2 smoothing only"), ("P2", "P2 smoothing only"), ("P0", "P1 smoothing only"), ("P0", "P2 no smoothing"), ("P2", "P2 no smoothing"), ("P0", "P1 no smoothing"), ("P1", "P1 no smoothing"), ("P0 Effort scheme", "P2 Effort scheme"), ("Effort fine-tuned P0", "Effort fine-tuned P2"), ("P0", "P3 forged only"), ("P2", "P3 forged only"),
                 ("main", "SIC factorised"), ("binary control", "SIC binary"), ("binary control", "SIC factorised")):   # Addendum 46
        for sd in SEEDS:
            fa, fb = (RU / f"ali_scores_{ARMS[x]}_s{sd}.npz" for x in (a, b))
            if not (fa.is_file() and fb.is_file()):
                continue
            sa = load(f"{ARMS[a]}_s{sd}")[0]; sb = load(f"{ARMS[b]}_s{sd}")[0]
            pa, pb = stats(sa, None, o, ~o, sm), stats(sb, None, o, ~o, sm); ci = boot(sa, sb)
            out[f"{b} minus {a} s{sd}"] = {"d_ret": round(pb[0] - pa[0], 2), "d_ret_ci": ci[0], "d_smooth90": round(pb[1] - pa[1], 2), "d_smooth90_ci": ci[1]}
    (HERE / "exposure_ali.json").write_text(json.dumps(out, indent=1))
    for k, v in out.items():
        print(k, v)


if __name__ == "__main__":
    main()
