"""Statistical audit of the capstone main claims (2026-10-23). Companion of STAT_AUDIT_20261023.md.

Recomputes, from the stored per-image / per-frame scores only, every paired comparison that
docs/capstone/MAIN_CLAIMS_20261022.md reports, and the numbers the judge rehearsal (JUDGE_REHEARSAL_20261022.md) and
FINDINGS.md (Addendum 54 GPUPixel, Addendum 57 boundary, our escape route) lean on.

 1. Reproduction. Re-runs the logic of alipair_zeroshot_20260929/main_claim_A.py (2,000 pair draws, rng 0) and
    celebdfb_v2_20260927/fair_cdfb.py (1,000 video draws, rng 1) with the same draws, and checks every formatted cell of
    MAIN_CLAIMS against the recomputation (string match on the exact format make_main_claims.py writes).
 2. Inference. Paired cluster bootstrap with one set of resamples shared by every detector:
      A  cluster = FFHQ pair index (2,210), 10,000 draws
      B  cluster = Celeb-DF-B video (464), 5,000 draws; identity (58, Addendum 45 rule) 2,000 draws as sensitivity
    two-sided bootstrap p by percentile inversion, p = min(1, 2 min(#(d*<=0)+1, #(d*>=0)+1) / (B+1));
    z = estimate / bootstrap SE as a resolution aid when p sits at the floor; BH-FDR within each declared family
    (cross-checked against statsmodels); effect sizes: Cohen's h for proportions, delta d' = sqrt(2) Phi^-1(AUC) for AUC.
 3. Sensitivities and forking paths: all 12 Alibaba cells, 1 / 10 % FPR, tie-aware share, 1 - P(real) for ours,
    equal-data / binary-control arms, Pareto check over 3 x 3 axis pairs, compression-controlled escape route, GPUPixel
    and boundary probes with video-cluster CIs.
 4. Attribution (exploratory): main three-way model vs the binary control trained on the same data and vs P0 (FF++ only,
    no beautified view), same seed, 2,000 paired / video draws, on Alibaba Smoothing-90 and Celeb-DF-B.

Reads only. Writes nothing unless --json PATH is given.
    python stat_audit.py [--json PATH] [--fast]
"""
import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy.stats import norm

BASE = Path(r"C:\My_Project\AIGC")
ALI = BASE / "results/research/alipair_zeroshot_20260929"
RU = BASE / "results/research/retouch_unified_20260929"
CDFB = BASE / "results/research/celebdfb_v2_20260927"
SPLIT = BASE / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt"
MAIN_MD = BASE / "docs/capstone/MAIN_CLAIMS_20261022.md"

PUB = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter", "univfd", "npr", "gend", "dfdhr", "caddm", "laanetr"]
NAME = {"xception": "Xception", "effnb4": "EfficientNet-B4", "f3net": "F3Net", "spsl": "SPSL", "ucf": "UCF", "recce": "RECCE", "core": "CORE", "srm": "SRM", "sbi": "SBI",
        "effort": "Effort (2025)", "fadapter": "Forensics Adapter (2025)", "univfd": "UnivFD", "npr": "NPR", "gend": "GenD (2026)", "dfdhr": "DFD-HR (2026)", "caddm": "CADDM", "laanetr": "LAA-Net"}
FACE = [p for p in PUB if p not in ("univfd", "npr")]
REF = ["effort", "fadapter", "sbi", "dfdhr", "gend", "caddm"]
OURS_A = {"s1": "clipe5_s20260929", "s2": "clipe5_s20260930"}
OURS_B = {"s1": "RU-clipe5", "s2": "RU-clipe5-s2"}
FOLD = ["real", "real_beautified", "real_compressed", "synthesis", "synthesis_beautified", "synthesis_compressed"]
OPS = [f"{o}_{l}" for o in ("EyeEnlarging", "FaceLifting", "Smoothing", "Whitening") for l in (30, 60, 90)]
# equal-data / ablation arms on the commercial pairs (tags as in alipair_zeroshot_20260929/exposure_ali.py)
ARMS = {"binary control (full data)": "clipe5b", "P0 FF++-only, no beautified view": "clipe5fbp0", "P1 FF++-only, beautified genuine only": "clipe5fbp1",
        "P2 FF++-only, beautified both classes": "clipe5fb", "P2n both classes, no smoothing": "clipe5fbn", "P1n genuine only, no smoothing": "clipe5fbp1n",
        "P2o smoothing only, both classes": "clipe5fbg0o", "P1o smoothing only, genuine only": "clipe5fbg0p1o", "P3 beautified forgeries only": "clipe5fbp3"}
SEEDS = ["20260929", "20260930", "20261001"]

OUT = {"meta": {}, "repro": {}, "A": {}, "B": {}, "gpx": {}, "bdry": {}, "families": {}}


# ---------------------------------------------------------------- statistics helpers
def boot_p(d):
    d = np.asarray(d, float); B = d.size
    lo = (1 + np.count_nonzero(d <= 0)) / (B + 1); hi = (1 + np.count_nonzero(d >= 0)) / (B + 1)
    return float(min(1.0, 2 * min(lo, hi)))


def ci95(d):
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]


def bh(p):
    p = np.asarray(p, float); m = p.size
    if m == 0:
        return p
    o = np.argsort(p); q = p[o] * m / np.arange(1, m + 1); q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(m); out[o] = np.minimum(q, 1.0); return out


def cohen_h(p1, p2):   # proportions in [0, 1]
    return float(2 * math.asin(math.sqrt(min(max(p1, 0), 1))) - 2 * math.asin(math.sqrt(min(max(p2, 0), 1))))


def dprime(a):
    return float(math.sqrt(2) * norm.ppf(min(max(a, 1e-6), 1 - 1e-6)))


def size_label(e):
    e = abs(e); return "negligible" if e < 0.2 else "small" if e < 0.5 else "medium" if e < 0.8 else "large"


def auc(neg, pos):   # = sklearn roc_auc_score with pos labelled 1 (ties count 1/2)
    a = np.sort(neg); lo = np.searchsorted(a, pos, "left"); hi = np.searchsorted(a, pos, "right")
    return float((lo.sum() + 0.5 * (hi - lo).sum()) / (a.size * pos.size))


def comp(fam, label, est, draws, eff, n, **kw):
    p = boot_p(draws); se = float(np.std(draws, ddof=1)); z = est / se if se > 0 else float("inf") * np.sign(est)
    r = {"family": fam, "label": label, "est": float(est), "ci": ci95(draws), "p": p, "z": float(z), "p_norm": float(2 * norm.sf(abs(z))) if np.isfinite(z) else 0.0,
         "effect_std": float(eff), "effect_size": size_label(eff), "n_clusters": n, "B": int(len(draws))}
    r.update(kw); return r


def apply_bh(records, key="q"):
    fams = {}
    for r in records:
        fams.setdefault(r["family"], []).append(r)
    for f, rs in fams.items():
        q = bh([r["p"] for r in rs])
        for r, qq in zip(rs, q):
            r[key] = float(qq)
    return fams


def grade(r1, r2):
    """Evidence grade for one comparison measured in two seeds (light-result-analysis ladder, operationalised):
    strong = both seeds q < .01, same sign, CI excludes 0, |std effect| >= .5; moderate = both q < .05, same sign, |std| >= .2;
    weak = significant in one seed only, or |std| < .2, or a q in [.045, .055]; none = no seed significant or significant signs disagree."""
    s = [r["q"] < 0.05 and (r["ci"][0] > 0 or r["ci"][1] < 0) for r in (r1, r2)]
    sg = [np.sign(r["est"]) for r in (r1, r2)]
    if not any(s):
        return "none"
    if all(s) and sg[0] != sg[1]:
        return "none (seeds disagree)"
    border = any(0.045 <= r["q"] <= 0.055 for r in (r1, r2))
    e = min(abs(r1["effect_std"]), abs(r2["effect_std"]))
    if math.isnan(e):   # no standardised effect defined: grade on q and replication only
        return ("strong" if all(s) and max(r1["q"], r2["q"]) < 0.01 else "moderate" if all(s) and not border else "weak") + " (q only)"
    if all(s) and max(r1["q"], r2["q"]) < 0.01 and e >= 0.5 and not border:
        return "strong"
    if all(s) and e >= 0.2 and not border:
        return "moderate"
    return "weak"


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- direction A
def ali_load(name):
    if name in PUB:
        z = np.load(ALI / f"published_scores_{name}.npz"); return z["s"].astype(float), z["group"], z["stem"], None
    z = np.load(RU / f"ali_scores_{name}.npz"); P = z["P"].astype(float); return P[:, 1], z["group"], z["stem"], P


def ali_pair(s, g, st, op, P=None):
    o = dict(zip(st[g == "orig_0"], s[g == "orig_0"])); r = dict(zip(st[g == op], s[g == op]))
    k = sorted(set(o) & set(r)); so = np.array([o[x] for x in k]); sr = np.array([r[x] for x in k]); dec = None
    if P is not None:
        am = P.argmax(1); ao = dict(zip(st[g == "orig_0"], am[g == "orig_0"])); ar = dict(zip(st[g == op], am[g == op]))
        dec = (np.array([ao[x] for x in k]), np.array([ar[x] for x in k]))
    return k, so, sr, dec


def fa_draws(so, sr, I, q=0.95, chunk=1000):
    out = []
    for i in range(0, I.shape[0], chunk):
        J = I[i:i + chunk]; t = np.quantile(so[J], q, axis=1); out.append((sr[J] > t[:, None]).mean(1) * 100)
    return np.concatenate(out)


def direction_A(BA, md):
    log("== direction A ==")
    raw = {n: ali_load(n) for n in PUB}
    for s_, tag in OURS_A.items():
        raw[f"ours {s_}"] = ali_load(tag)
    D = {}
    for n, (s, g, st, P) in raw.items():
        D[n] = ali_pair(s, g, st, "Smoothing_90", P)
    keys = D["effort"][0]; assert all(d[0] == keys for d in D.values()); n = len(keys)
    OUT["A"]["n_pairs"] = n

    # -- 1. exact reproduction of main_claim_A.py (2,000 draws, rng 0, threshold fixed at the full-sample value)
    rng = np.random.default_rng(0); boots = np.array([rng.integers(0, n, n) for _ in range(2000)])
    rep = {}; up = {}
    for name in PUB + ["ours s1", "ours s2"]:
        _, so, sr, dec = D[name]; u = sr > so; t = np.quantile(so, 0.95); fa = sr > t
        up[name] = u[boots].mean(1) * 100; fab = fa[boots].mean(1) * 100
        row = {"paired_up": round(float(u.mean() * 100), 1), "paired_up_ci": [round(float(np.percentile(up[name], q)), 1) for q in (2.5, 97.5)],
               "fa_s90_at_5pct": round(float(fa.mean() * 100), 1), "fa_ci": [round(float(np.percentile(fab, q)), 1) for q in (2.5, 97.5)]}
        if dec is not None:
            ao, ar = dec
            row["native_orig"] = {c: round(float((ao == i).mean() * 100), 1) for i, c in enumerate(["real", "fake", "filter"])}
            row["native_s90"] = {c: round(float((ar == i).mean() * 100), 1) for i, c in enumerate(["real", "fake", "filter"])}
        rep[name] = row
    for o in ("ours s1", "ours s2"):
        rep[o]["paired_up_minus"] = {p: [round(float(np.percentile(up[o] - up[p], q)), 1) for q in (2.5, 97.5)] for p in PUB}
    js = json.loads((ALI / "main_claim_A.json").read_text())
    mism = []
    for name in PUB + ["ours s1", "ours s2"]:
        jn = name if name in PUB else name.replace("ours", "ours main")
        for k, v in rep[name].items():
            if js["rows"][jn].get(k) != v:
                mism.append(f"{name}.{k}: json {js['rows'][jn].get(k)} vs recomputed {v}")
    md_missing = []
    for p in PUB:
        r = rep[p]; line = f"| {NAME[p]} | {r['paired_up']} {r['paired_up_ci']} | {r['fa_s90_at_5pct']} {r['fa_ci']} |"
        if line not in md:
            md_missing.append(line)
    for o in ("ours s1", "ours s2"):
        r = rep[o]
        line = (f"| **我們（主模型 {o[-2:]}）** | **{r['paired_up']}** {r['paired_up_ci']} | **{r['fa_s90_at_5pct']}** {r['fa_ci']}；三類判定：原圖 real {r['native_orig']['real']}%，"
                f"磨皮後 filter {r['native_s90']['filter']}%、fake {r['native_s90']['fake']}% |")
        if line not in md:
            md_missing.append(line)
    n_hi = sum(rep[p]["paired_up"] >= 89 for p in PUB)
    n_sig = {o: sum(rep[o]["paired_up_minus"][p][1] < 0 for p in PUB) for o in ("ours s1", "ours s2")}
    n_sig_any = {o: sum((rep[o]["paired_up_minus"][p][1] < 0) or (rep[o]["paired_up_minus"][p][0] > 0) for p in PUB) for o in ("ours s1", "ours s2")}
    rl = f"17 個已發表偵測器裡 {n_hi} 個在 89% 以上的配對把磨皮真臉判得更假；我們 {rep['ours s1']['paired_up']}／{rep['ours s2']['paired_up']}%。配對差異的 CI 不含 0 的偵測器數：seed 1 對 {n_sig['ours s1']}/17，seed 2 對 {n_sig['ours s2']}/17"
    if rl not in md:
        md_missing.append(rl)
    OUT["repro"]["A"] = {"json_mismatches": mism, "md_lines_not_found": md_missing, "n_hi_89": n_hi, "n_ci_below0": n_sig, "n_ci_excl0_either_side": n_sig_any,
                         "npr_minus_ci": {o: rep[o]["paired_up_minus"]["npr"] for o in ("ours s1", "ours s2")}, "rows": rep}
    log(f"A repro: json mismatches {len(mism)}, MD lines not found {len(md_missing)}; CI excludes 0 either side {n_sig_any}")

    # -- 2. inference, 10,000 pair draws shared by all detectors; FA threshold re-estimated inside each draw
    rngA = np.random.default_rng(20261023); I = rngA.integers(0, n, size=(BA, n)).astype(np.int32)
    share, share_t, fa5, pt = {}, {}, {}, {}
    for name in PUB + ["ours s1", "ours s2"]:
        _, so, sr, _ = D[name]; u = (sr > so).astype(np.float32); ut = u + 0.5 * (sr == so)
        share[name] = u[I].mean(1) * 100; share_t[name] = ut[I].mean(1) * 100; fa5[name] = fa_draws(so, sr, I)
        pt[name] = {"share": float(u.mean() * 100), "share_ci": ci95(share[name]), "tie": float((sr == so).mean() * 100), "share_tieaware": float(ut.mean() * 100),
                    "fa5": float((sr > np.quantile(so, 0.95)).mean() * 100), "fa5_ci_threshold_resampled": ci95(fa5[name]),
                    "fa1": float((sr > np.quantile(so, 0.99)).mean() * 100), "fa10": float((sr > np.quantile(so, 0.90)).mean() * 100)}
    OUT["A"]["point"] = pt
    recs = []
    for s_ in ("s1", "s2"):
        o = f"ours {s_}"
        for p in PUB:
            est = pt[o]["share"] - pt[p]["share"]
            recs.append(comp(f"A_share_{s_}", f"{o} - {p} paired share", est, share[o] - share[p], cohen_h(pt[o]["share"] / 100, pt[p]["share"] / 100), n, seed=s_, ref=p, metric="paired share"))
    for s_ in ("s1", "s2"):
        o = f"ours {s_}"
        for p in PUB:
            est = pt[o]["share_tieaware"] - pt[p]["share_tieaware"]
            recs.append(comp(f"A_share_tie_{s_}", f"{o} - {p} tie-aware share", est, share_t[o] - share_t[p], cohen_h(pt[o]["share_tieaware"] / 100, pt[p]["share_tieaware"] / 100), n, seed=s_, ref=p, metric="tie-aware share"))
    for s_ in ("s1", "s2"):
        o = f"ours {s_}"
        for p in PUB:
            est = pt[o]["fa5"] - pt[p]["fa5"]
            recs.append(comp(f"A_fa5_{s_}", f"{o} - {p} FA@5%FPR", est, fa5[o] - fa5[p], cohen_h(pt[o]["fa5"] / 100, pt[p]["fa5"] / 100), n, seed=s_, ref=p, metric="FA at 5% FPR"))
    for p in PUB:   # published detectors against the no-effect value 50 %
        recs.append(comp("A_pub_vs50", f"{p} share - 50", pt[p]["share"] - 50, share[p] - 50, cohen_h(pt[p]["share"] / 100, 0.5), n, ref=p, metric="paired share vs 50"))
        recs.append(comp("A_pub_vs50_tie", f"{p} tie-aware share - 50", pt[p]["share_tieaware"] - 50, share_t[p] - 50, cohen_h(pt[p]["share_tieaware"] / 100, 0.5), n, ref=p, metric="tie-aware share vs 50"))
    recs.append(comp("A_seed", "ours s1 - s2 paired share", pt["ours s1"]["share"] - pt["ours s2"]["share"], share["ours s1"] - share["ours s2"],
                     cohen_h(pt["ours s1"]["share"] / 100, pt["ours s2"]["share"] / 100), n, metric="seed difference"))
    recs.append(comp("A_seed", "ours s1 - s2 FA@5%FPR", pt["ours s1"]["fa5"] - pt["ours s2"]["fa5"], fa5["ours s1"] - fa5["ours s2"],
                     cohen_h(pt["ours s1"]["fa5"] / 100, pt["ours s2"]["fa5"] / 100), n, metric="seed difference"))
    OUT["A"]["comparisons"] = recs
    # native three-way decision with CIs
    nat = {}
    for s_ in ("s1", "s2"):
        ao, ar = D[f"ours {s_}"][3]
        nat[s_] = {"orig_real": [float((ao == 0).mean() * 100)] + ci95(((ao == 0).astype(np.float32))[I[:2000]].mean(1) * 100),
                   "s90_filter": [float((ar == 2).mean() * 100)] + ci95(((ar == 2).astype(np.float32))[I[:2000]].mean(1) * 100),
                   "s90_fake": [float((ar == 1).mean() * 100)] + ci95(((ar == 1).astype(np.float32))[I[:2000]].mean(1) * 100),
                   "orig_filter": [float((ao == 2).mean() * 100)] + ci95(((ao == 2).astype(np.float32))[I[:2000]].mean(1) * 100)}
    OUT["A"]["native"] = nat

    # -- 3. sensitivity: every Alibaba cell (point + BH counts), 2,000 draws per cell
    cells = {}
    for op in OPS:
        dd = {nm: ali_pair(*raw[nm][:3], op) for nm in raw}
        kk = dd["effort"][0]; assert all(v[0] == kk for v in dd.values()); m = len(kk)
        Ic = np.random.default_rng(7).integers(0, m, size=(2000, m)).astype(np.int32)
        sh = {nm: ((v[2] > v[1]) + 0.5 * (v[2] == v[1])).astype(np.float32) for nm, v in dd.items()}
        bs = {nm: x[Ic].mean(1) * 100 for nm, x in sh.items()}
        pv = bh([boot_p(bs[p] - 50) for p in PUB]); above = [p for p, q in zip(PUB, pv) if q < 0.05 and sh[p].mean() > 0.5]
        beat = {}
        for s_ in ("s1", "s2"):
            o = f"ours {s_}"; qq = bh([boot_p(bs[o] - bs[p]) for p in PUB])
            beat[s_] = sum(q < 0.05 and sh[o].mean() < sh[p].mean() for p, q in zip(PUB, qq))
        fa = {nm: float((v[2] > np.quantile(v[1], 0.95)).mean() * 100) for nm, v in dd.items()}
        cells[op] = {"n": m, "pub_share_tieaware_median": float(np.median([sh[p].mean() * 100 for p in PUB])),
                     "pub_share_tieaware_range": [float(min(sh[p].mean() * 100 for p in PUB)), float(max(sh[p].mean() * 100 for p in PUB))],
                     "n_pub_sig_above50": len(above), "ours_share_tieaware": {s_: float(sh[f"ours {s_}"].mean() * 100) for s_ in ("s1", "s2")},
                     "n_pub_ours_sig_lower": beat, "pub_fa5_median": float(np.median([fa[p] for p in PUB])), "ours_fa5": {s_: fa[f"ours {s_}"] for s_ in ("s1", "s2")}}
    OUT["A"]["cells"] = cells
    log("A cells done")

    # -- 4. score definition for ours and equal-data arms (Smoothing-90)
    alt = {}
    for s_, tag in OURS_A.items():
        s, g, st, P = raw[f"ours {s_}"]; k, so, sr, _ = ali_pair(1 - P[:, 0], g, st, "Smoothing_90")
        alt[s_] = {"share_1-P(real)": float((sr > so).mean() * 100), "fa5_1-P(real)": float((sr > np.quantile(so, 0.95)).mean() * 100)}
    OUT["A"]["ours_score_1_minus_Preal"] = alt
    arms = {}
    I2 = I[:2000]
    for lab, tag in ARMS.items():
        for sd in SEEDS:
            f = RU / f"ali_scores_{tag}_s{sd}.npz"
            if not f.is_file():
                continue
            s, g, st, P = ali_load(f"{tag}_s{sd}"); k, so, sr, _ = ali_pair(s, g, st, "Smoothing_90")
            assert k == keys
            u = (sr > so).astype(np.float32)
            arms[f"{lab} s{sd}"] = {"share": float(u.mean() * 100), "share_ci": ci95(u[I2].mean(1) * 100), "fa5": float((sr > np.quantile(so, 0.95)).mean() * 100),
                                   "fa5_ci": ci95(fa_draws(so, sr, I2))}
    OUT["A"]["arms"] = arms
    log("A done")
    return pt, share, fa5


# ---------------------------------------------------------------- direction B
def b_stats(s, G, need_auc_c=True):
    gr = s[G[0]]; t = np.quantile(gr, 0.95)
    s0, sb, sc = s[G[3]], s[G[4]], s[G[5]]
    miss0 = float((s0 <= t).mean() * 100); miss_b = float((sb <= t).mean() * 100); miss_c = float((sc <= t).mean() * 100)
    r = {"auc_beautified": auc(s[G[1]], sb), "miss0": miss0, "miss_b": miss_b, "miss_c": miss_c, "fa_b": float((s[G[1]] > t).mean() * 100),
         "fa_c": float((s[G[2]] > t).mean() * 100), "d_miss": miss_b - miss0, "d_miss_c": miss_c - miss0, "d_miss_beauty_only": (miss_b - miss0) - (miss_c - miss0)}
    if need_auc_c:
        r["auc_compressed"] = auc(s[G[2]], sc)
    return r


def groups(idx, fcode):
    fc = fcode[idx]; return [idx[fc == k] for k in range(6)]


def direction_B(BB, BI, md):
    log("== direction B ==")
    rows = [l.split("\t") for l in SPLIT.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    path = np.array([r[0] for r in rows]); folder = np.array([r[3] for r in rows]); vid = np.array([r[2] for r in rows])
    fcode = np.array([FOLD.index(f) for f in folder]); allidx = np.arange(len(rows))
    names = PUB + [OURS_B["s1"], OURS_B["s2"]]
    S, PP = {}, {}
    for nm in names:
        z = np.load(CDFB / "scores_v3" / f"{nm}.npz"); assert (z["paths"] == path).all(), nm; PP[nm] = z["p"]; S[nm] = z["p"][:, 1].astype(float)
    G0 = groups(allidx, fcode)
    # point estimates, AUC cross-checked with sklearn
    from sklearn.metrics import roc_auc_score
    point = {nm: b_stats(S[nm], G0) for nm in names}
    for nm in names:
        point[nm]["auc_untreated"] = auc(S[nm][G0[0]], S[nm][G0[3]])
        g1, g4 = S[nm][G0[1]], S[nm][G0[4]]
        sk = roc_auc_score(np.r_[np.zeros(len(g1)), np.ones(len(g4))], np.r_[g1, g4]); assert abs(sk - point[nm]["auc_beautified"]) < 1e-9, nm
    OUT["B"]["point"] = point
    vids = sorted(set(vid)); vix = {v: np.where(vid == v)[0] for v in vids}

    # -- 1. exact reproduction of fair_cdfb.py (1,000 draws, rng 1)
    rng = np.random.default_rng(1)
    boots = [np.concatenate([vix[vids[j]] for j in rng.choice(len(vids), len(vids), True)]) for _ in range(1000)]
    bs = {nm: [] for nm in names}
    for b in boots:
        G = groups(b, fcode)
        for nm in names:
            bs[nm].append(b_stats(S[nm], G, need_auc_c=False))
    js = json.loads((CDFB / "fair_cdfb.json").read_text())
    rep, mism, other = {}, [], []
    for nm in names:
        r = {k: round(v, 4 if k.startswith("auc") else 2) for k, v in point[nm].items() if k in js[nm]}
        r["ci"] = {k: [round(float(np.percentile([x[k] for x in bs[nm]], q)), 4 if k.startswith("auc") else 2) for q in (2.5, 97.5)]
                   for k in ("auc_beautified", "d_miss_beauty_only", "fa_b", "miss_b")}
        r["auc_beautified_minus"], r["d_miss_beauty_only_minus"] = {}, {}
        for ref in REF:
            if ref != nm:
                d = np.array([x["auc_beautified"] for x in bs[nm]]) - np.array([x["auc_beautified"] for x in bs[ref]])
                r["auc_beautified_minus"][ref] = [round(float(np.percentile(d, 2.5)), 4), round(float(np.percentile(d, 97.5)), 4)]
                e = np.array([x["d_miss_beauty_only"] for x in bs[nm]]) - np.array([x["d_miss_beauty_only"] for x in bs[ref]])
                r["d_miss_beauty_only_minus"][ref] = [round(float(np.percentile(e, 2.5)), 2), round(float(np.percentile(e, 97.5)), 2)]
        rep[nm] = r
        used = {"auc_beautified", "d_miss_beauty_only", "fa_b"} | ({"auc_beautified_minus", "d_miss_beauty_only_minus"} if nm not in PUB else set())
        for k, v in r.items():
            if k == "ci":
                for kk in ("auc_beautified", "d_miss_beauty_only"):
                    if js[nm]["ci"].get(kk) != v[kk]:
                        mism.append(f"[used] {nm}.ci.{kk}: json {js[nm]['ci'].get(kk)} vs recomputed {v[kk]}")
                for kk in ("fa_b", "miss_b"):
                    if js[nm]["ci"].get(kk) != v[kk]:
                        other.append(f"{nm}.ci.{kk}: json {js[nm]['ci'].get(kk)} vs recomputed {v[kk]}")
            elif js[nm].get(k) != v:
                (mism if k in used else other).append(f"{'[used] ' if k in used else ''}{nm}.{k}: json {js[nm].get(k)} vs recomputed {v}")
    md_missing = []
    for nm in names:
        r = rep[nm]
        lab = NAME.get(nm) or ("**我們（主模型 s1）**" if nm == OURS_B["s1"] else "**我們（主模型 s2）**")
        if nm in PUB:
            line = f"| {lab} | {r['auc_beautified']:.3f} {r['ci']['auc_beautified']} | {r['d_miss_beauty_only']:+.1f} {r['ci']['d_miss_beauty_only']} | {r['fa_b']:.1f} |"
        else:
            line = f"| {lab} | **{r['auc_beautified']:.3f}** {r['ci']['auc_beautified']} | **{r['d_miss_beauty_only']:+.1f}** {r['ci']['d_miss_beauty_only']} | {r['fa_b']:.1f} |"
        if line not in md:
            md_missing.append(line)
    for s_ in ("s1", "s2"):
        r = rep[OURS_B[s_]]
        for key, lab in (("auc_beautified_minus", "美顏後 AUC"), ("d_miss_beauty_only_minus", "純美顏漏抓增加")):
            line = f"- {lab}，{s_}：" + "；".join(f"{NAME[k]} {v}" for k, v in r[key].items())
            if line not in md:
                md_missing.append(line)
    OUT["repro"]["B"] = {"json_mismatches_used_by_main_claims": mism, "json_mismatches_other_fields": other, "md_lines_not_found": md_missing}
    log(f"B repro: json mismatches used {len(mism)} / other {len(other)}, MD lines not found {len(md_missing)}")

    # -- 2. inference, 5,000 video draws shared by all detectors (threshold re-estimated inside each draw)
    rngB = np.random.default_rng(20261024)
    keys = ["auc_beautified", "auc_compressed", "d_miss_beauty_only", "fa_b", "fa_c", "miss_b", "miss0"]
    BD = {nm: {k: np.empty(BB) for k in keys} for nm in names}
    NAT = {s_: {k: np.empty(BB) for k in ("syn_filter", "synb_filter", "sync_filter", "real_fake", "realb_fake", "realc_fake")} for s_ in OURS_B}
    am = {s_: PP[OURS_B[s_]].argmax(1) for s_ in OURS_B}
    t0 = time.time()
    for i in range(BB):
        b = np.concatenate([vix[vids[j]] for j in rngB.choice(len(vids), len(vids), True)]); G = groups(b, fcode)
        for nm in names:
            r = b_stats(S[nm], G)
            for k in keys:
                BD[nm][k][i] = r[k]
        for s_ in OURS_B:
            a = am[s_]
            NAT[s_]["syn_filter"][i] = (a[G[3]] == 2).mean() * 100; NAT[s_]["synb_filter"][i] = (a[G[4]] == 2).mean() * 100; NAT[s_]["sync_filter"][i] = (a[G[5]] == 2).mean() * 100
            NAT[s_]["real_fake"][i] = (a[G[0]] == 1).mean() * 100; NAT[s_]["realb_fake"][i] = (a[G[1]] == 1).mean() * 100; NAT[s_]["realc_fake"][i] = (a[G[2]] == 1).mean() * 100
        if i and i % 1000 == 0:
            log(f"  B draw {i}/{BB}  {time.time() - t0:.0f}s")
    nv = len(vids)

    def bc(fam, s_, ref, key, ext=""):
        o = OURS_B[s_]; est = point[o][key] - point[ref][key]; d = BD[o][key] - BD[ref][key]
        if key == "auc_beautified":
            eff = dprime(point[o][key]) - dprime(point[ref][key])
        elif key == "d_miss_beauty_only":
            eff = (cohen_h(point[o]["miss_b"] / 100, point[o]["miss_c"] / 100)) - (cohen_h(point[ref]["miss_b"] / 100, point[ref]["miss_c"] / 100))
        elif key == "fa_b":
            eff = cohen_h(point[o][key] / 100, point[ref][key] / 100)
        else:
            eff = float("nan")
        return comp(fam, f"ours {s_} - {ref} {key}{ext}", est, d, eff, nv, seed=s_, ref=ref, metric=key)

    recs = []
    for s_ in ("s1", "s2"):
        for ref in REF:
            recs.append(bc(f"B_auc_{s_}", s_, ref, "auc_beautified"))
        for ref in REF:
            recs.append(bc(f"B_miss_{s_}", s_, ref, "d_miss_beauty_only"))
    for s_ in ("s1", "s2"):     # extended families: all 17 published (supports / refutes "highest of 17")
        for ref in PUB:
            recs.append(bc(f"Bx_auc_{s_}", s_, ref, "auc_beautified"))
            recs.append(bc(f"Bx_miss_{s_}", s_, ref, "d_miss_beauty_only"))
    for s_ in ("s1", "s2"):     # exploratory: accusation side of direction B, and AUC drop net of compression
        for ref in REF:
            recs.append(bc(f"Be_fab_{s_}", s_, ref, "fa_b"))
            o = OURS_B[s_]
            est = (point[o]["fa_b"] - point[o]["fa_c"]) - (point[ref]["fa_b"] - point[ref]["fa_c"])
            recs.append(comp(f"Be_fab_net_{s_}", f"ours {s_} - {ref} (FA_b - FA_c)", est, (BD[o]["fa_b"] - BD[o]["fa_c"]) - (BD[ref]["fa_b"] - BD[ref]["fa_c"]),
                             cohen_h(point[o]["fa_b"] / 100, point[o]["fa_c"] / 100) - cohen_h(point[ref]["fa_b"] / 100, point[ref]["fa_c"] / 100), nv, seed=s_, ref=ref, metric="FA_b - FA_c"))
            est = (point[o]["auc_beautified"] - point[o]["auc_compressed"]) - (point[ref]["auc_beautified"] - point[ref]["auc_compressed"])
            recs.append(comp(f"Be_aucdrop_{s_}", f"ours {s_} - {ref} (AUC_b - AUC_c)", est,
                             (BD[o]["auc_beautified"] - BD[o]["auc_compressed"]) - (BD[ref]["auc_beautified"] - BD[ref]["auc_compressed"]),
                             (dprime(point[o]["auc_beautified"]) - dprime(point[o]["auc_compressed"])) - (dprime(point[ref]["auc_beautified"]) - dprime(point[ref]["auc_compressed"])),
                             nv, seed=s_, ref=ref, metric="AUC_b - AUC_c"))
    for s_ in ("s1", "s2"):     # exploratory: absolute miss on beautified forgeries (judge rehearsal: DFD-HR 34.7 % < ours)
        o = OURS_B[s_]
        for ref in REF:
            recs.append(comp(f"Be_missb_{s_}", f"ours {s_} - {ref} miss_b", point[o]["miss_b"] - point[ref]["miss_b"], BD[o]["miss_b"] - BD[ref]["miss_b"],
                             cohen_h(point[o]["miss_b"] / 100, point[ref]["miss_b"] / 100), nv, seed=s_, ref=ref, metric="miss_b"))
    for p in PUB + [OURS_B["s1"], OURS_B["s2"]]:   # direction B itself: does beautification (net of re-encoding) raise each detector's miss?
        recs.append(comp("Bm_miss_vs0", f"{p} beauty-only miss rise vs 0", point[p]["d_miss_beauty_only"], BD[p]["d_miss_beauty_only"],
                         cohen_h(point[p]["miss_b"] / 100, point[p]["miss_c"] / 100), nv, ref=p, metric="d_miss_beauty_only vs 0"))
    for key in ("auc_beautified", "d_miss_beauty_only"):
        o1, o2 = OURS_B["s1"], OURS_B["s2"]
        recs.append(comp("B_seed", f"ours s1 - s2 {key}", point[o1][key] - point[o2][key], BD[o1][key] - BD[o2][key], float("nan"), nv, metric="seed difference"))
    OUT["B"]["comparisons"] = recs
    # marginal CIs (5,000 draws) and pre-declared bars T1 / T2 (Addendum 6)
    OUT["B"]["marginal"] = {nm: {k: [point[nm][k]] + ci95(BD[nm][k]) for k in keys} for nm in names}
    nat = {}
    for s_ in OURS_B:
        a = am[s_]; G = G0
        pt = {"syn_filter": (a[G[3]] == 2).mean() * 100, "synb_filter": (a[G[4]] == 2).mean() * 100, "sync_filter": (a[G[5]] == 2).mean() * 100,
              "real_fake": (a[G[0]] == 1).mean() * 100, "realb_fake": (a[G[1]] == 1).mean() * 100, "realc_fake": (a[G[2]] == 1).mean() * 100}
        nat[s_] = {k: [float(v)] + ci95(NAT[s_][k]) for k, v in pt.items()}
        nat[s_]["synb_minus_syn"] = [float(pt["synb_filter"] - pt["syn_filter"])] + ci95(NAT[s_]["synb_filter"] - NAT[s_]["syn_filter"])
        nat[s_]["synb_minus_sync"] = [float(pt["synb_filter"] - pt["sync_filter"])] + ci95(NAT[s_]["synb_filter"] - NAT[s_]["sync_filter"])
        nat[s_]["realb_minus_real_fake"] = [float(pt["realb_fake"] - pt["real_fake"])] + ci95(NAT[s_]["realb_fake"] - NAT[s_]["real_fake"])
    OUT["B"]["native_escape_route"] = nat
    log("B video bootstrap done")

    # -- 3. identity-cluster sensitivity (Addendum 45 rule: cluster = X of idX..., 2,000 draws)
    ident = np.array([v.split("_")[0] for v in vid]); ids = sorted(set(ident)); iix = {k: np.where(ident == k)[0] for k in ids}
    rngI = np.random.default_rng(45); sub = [OURS_B["s1"], OURS_B["s2"]] + REF
    ID = {nm: {k: np.empty(BI) for k in ("auc_beautified", "d_miss_beauty_only")} for nm in sub}
    for i in range(BI):
        b = np.concatenate([iix[ids[j]] for j in rngI.choice(len(ids), len(ids), True)]); G = groups(b, fcode)
        for nm in sub:
            r = b_stats(S[nm], G, need_auc_c=False); ID[nm]["auc_beautified"][i] = r["auc_beautified"]; ID[nm]["d_miss_beauty_only"][i] = r["d_miss_beauty_only"]
    idr = []
    for s_ in ("s1", "s2"):
        o = OURS_B[s_]
        for key, fam in (("auc_beautified", "Bid_auc"), ("d_miss_beauty_only", "Bid_miss")):
            for ref in REF:
                idr.append(comp(f"{fam}_{s_}", f"ours {s_} - {ref} {key} (identity)", point[o][key] - point[ref][key], ID[o][key] - ID[ref][key], float("nan"), len(ids), seed=s_, ref=ref, metric=key))
    OUT["B"]["identity_comparisons"] = idr
    OUT["B"]["n_identities"] = len(ids); OUT["B"]["n_videos"] = nv
    log("B identity bootstrap done")
    return point


# ---------------------------------------------------------------- GPUPixel (Add. 54) and boundary (Add. 57) probes
def probe(kind, forms, models, BP):
    m = json.loads((RU / f"{kind}38_list.json").read_text()); y = np.array(m["y"]); ok = np.array(m["lm_ok"]); vid = np.array(m["video"])
    vv = sorted(set(vid)); vix = {v: np.where(vid == v)[0] for v in vv}
    rng = np.random.default_rng(54 if kind == "gpx" else 57)
    draws = [np.concatenate([vix[vv[j]] for j in rng.choice(len(vv), len(vv), True)]) for _ in range(BP)]
    res = {}
    for nm in models:
        f = RU / f"{kind}38_{nm}.npz"
        if not f.is_file():
            continue
        z = np.load(f); u = z["untreated"].astype(float); arr = {c: z[c].astype(float) for c in forms}

        def fa(idx):
            gi = idx[ok[idx] & (y[idx] == 0)]; t = np.nanquantile(u[gi], 0.95); out = {}
            for c in forms:
                s = arr[c][gi]; s = s[~np.isnan(s)]; out[c] = float((s > t).mean() * 100)
            return out
        p = fa(np.arange(len(y))); B = [fa(d) for d in draws]
        res[nm] = {c: {"fa": p[c], "ci": ci95([b[c] for b in B])} for c in forms}
        res[nm]["_draws"] = {c: np.array([b[c] for b in B]) for c in forms}
    return res, len(vv)


def probes(BP):
    log("== GPUPixel / boundary probes ==")
    arms = ["clipe5_s20260929", "clipe5b_s20260929", "clipe5b_s20260930", "clipe5bzl0_s20260929", "clipe5bzsg_s20260929", "clipe5bzsg_s20260930"]
    g, nvg = probe("gpx", ["gpx0", "gpx9"], PUB + arms, BP)
    js = json.loads((RU / "gpx38.json").read_text())["rows"]
    mism = [f"{nm} {c}: {js[nm][c]['fa']} vs {round(g[nm][c]['fa'], 1)}" for nm in g for c in ("gpx0", "gpx9") if nm in js and js[nm][c]["fa"] != round(g[nm][c]["fa"], 1)]
    gp = {nm: {c: {"fa": v[c]["fa"], "ci": v[c]["ci"]} for c in ("gpx0", "gpx9")} for nm, v in g.items()}
    for nm, v in g.items():
        d = v["_draws"]["gpx9"] - v["_draws"]["gpx0"]; gp[nm]["gpx9_minus_gpx0"] = {"est": v["gpx9"]["fa"] - v["gpx0"]["fa"], "ci": ci95(d), "p": boot_p(d)}
        gp[nm]["gpx9_minus_15"] = {"p": boot_p(v["_draws"]["gpx9"] - 15)}
    face = [p for p in FACE if p in g]
    q15 = bh([gp[p]["gpx9_minus_15"]["p"] for p in face])
    OUT["gpx"] = {"rows": gp, "n_videos": nvg, "repro_mismatches": mism, "main_model_scored": "clipe5_s20260929" in g,
                  "pred1_point": sum(gp[p]["gpx9"]["fa"] > 15 for p in face), "pred1_ci_lower_gt15": sum(gp[p]["gpx9"]["ci"][0] > 15 for p in face),
                  "pred1_bh_sig_gt15": sum(q < 0.05 and gp[p]["gpx9"]["fa"] > 15 for p, q in zip(face, q15)), "n_face": len(face)}
    log(f"gpx: repro mismatches {len(mism)}, pred1 point {OUT['gpx']['pred1_point']}/15, CI-lower>15 {OUT['gpx']['pred1_ci_lower_gt15']}")
    b, nvb = probe("bdry", ["fe01", "ring", "whole"], PUB + ["clipe5_s20260929", "clipe5b_s20260929"], BP)
    js = json.loads((RU / "bdry38.json").read_text())["rows"]
    mism = [f"{nm} {c}: {js[nm][c]['fa']} vs {round(b[nm][c]['fa'], 1)}" for nm in b for c in ("fe01", "ring", "whole") if nm in js and js[nm][c]["fa"] != round(b[nm][c]["fa"], 1)]
    bp = {}
    for nm, v in b.items():
        D = v["_draws"]
        bp[nm] = {c: {"fa": v[c]["fa"], "ci": v[c]["ci"]} for c in ("fe01", "ring", "whole")}
        bp[nm]["ring_minus_fe01"] = {"est": v["ring"]["fa"] - v["fe01"]["fa"], "ci": ci95(D["ring"] - D["fe01"]), "p": boot_p(D["ring"] - D["fe01"])}
        bp[nm]["ring_minus_0.7fe01"] = {"est": v["ring"]["fa"] - 0.7 * v["fe01"]["fa"], "ci": ci95(D["ring"] - 0.7 * D["fe01"])}
        bp[nm]["whole_minus_fe01"] = {"est": v["whole"]["fa"] - v["fe01"]["fa"], "ci": ci95(D["whole"] - D["fe01"]), "p": boot_p(D["whole"] - D["fe01"])}
    face = [p for p in FACE if p in bp]
    qr = bh([bp[p]["ring_minus_fe01"]["p"] for p in face]); qw = bh([bp[p]["whole_minus_fe01"]["p"] for p in face])
    OUT["bdry"] = {"rows": bp, "n_videos": nvb, "repro_mismatches": mism,
                   "pred2_fails_robustly": sum(bp[p]["ring_minus_0.7fe01"]["ci"][1] < 0 for p in face),
                   "ring_below_fe01_bh": sum(q < 0.05 and bp[p]["ring_minus_fe01"]["est"] < 0 for p, q in zip(face, qr)),
                   "whole_below_fe01_by10_ci": sum(bp[p]["whole_minus_fe01"]["ci"][1] < -10 for p in face),
                   "whole_below_fe01_bh": sum(q < 0.05 and bp[p]["whole_minus_fe01"]["est"] < 0 for p, q in zip(face, qw)), "n_face": len(face)}
    log(f"bdry: repro mismatches {len(mism)}, pred2 fails robustly {OUT['bdry']['pred2_fails_robustly']}/15")


# ---------------------------------------------------------------- attribution: is it the third class?
def attribution(BAT):
    """Main three-way model vs the binary control trained on the same data (clipe5b) and vs P0 (FF++ only, no beautified view),
    same seed, same draws. Exploratory (post hoc): answers whether 'our three-class model' can be credited for A and B."""
    log("== attribution (main vs binary control vs P0) ==")
    rec = []
    for s_, sd in (("s1", "20260929"), ("s2", "20260930")):
        arms = {"main": f"clipe5_s{sd}", "binary": f"clipe5b_s{sd}", "P0": f"clipe5fbp0_s{sd}"}
        D = {k: ali_pair(*ali_load(v)[:3], "Smoothing_90") for k, v in arms.items()}
        n = len(D["main"][0]); assert all(D[k][0] == D["main"][0] for k in D)
        I = np.random.default_rng(int(sd)).integers(0, n, size=(BAT, n)).astype(np.int32)
        sh = {k: (v[2] > v[1]).astype(np.float32) for k, v in D.items()}; shb = {k: x[I].mean(1) * 100 for k, x in sh.items()}
        fab = {k: fa_draws(v[1], v[2], I) for k, v in D.items()}; fap = {k: float((v[2] > np.quantile(v[1], 0.95)).mean() * 100) for k, v in D.items()}
        for other in ("binary", "P0"):
            rec.append(comp(f"Att_A_share_{s_}", f"main - {other} paired share {s_}", float(sh["main"].mean() - sh[other].mean()) * 100, shb["main"] - shb[other],
                            cohen_h(sh["main"].mean(), sh[other].mean()), n, seed=s_, ref=other, metric="paired share", values={k: float(x.mean() * 100) for k, x in sh.items()}))
            rec.append(comp(f"Att_A_fa5_{s_}", f"main - {other} FA@5% {s_}", fap["main"] - fap[other], fab["main"] - fab[other],
                            cohen_h(fap["main"] / 100, fap[other] / 100), n, seed=s_, ref=other, metric="FA at 5% FPR", values=fap))
    rows = [l.split("\t") for l in SPLIT.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    path = np.array([r[0] for r in rows]); folder = np.array([r[3] for r in rows]); vid = np.array([r[2] for r in rows])
    fcode = np.array([FOLD.index(f) for f in folder]); vids = sorted(set(vid)); vix = {v: np.where(vid == v)[0] for v in vids}
    names = {"s1": {"main": "RU-clipe5", "binary": "RU-clipe5b", "P0": "RU-clipe5fbp0_s20260929"},
             "s2": {"main": "RU-clipe5-s2", "binary": "RU-clipe5b_s20260930", "P0": "RU-clipe5fbp0_s20260930"}}
    S = {}
    for s_ in names:
        for k, nm in names[s_].items():
            z = np.load(CDFB / "scores_v3" / f"{nm}.npz"); assert (z["paths"] == path).all(), nm; S[nm] = z["p"][:, 1].astype(float)
    G0 = groups(np.arange(len(rows)), fcode); pt = {nm: b_stats(S[nm], G0, need_auc_c=False) for nm in S}
    rng = np.random.default_rng(25); BD = {nm: {k: np.empty(BAT) for k in ("auc_beautified", "d_miss_beauty_only", "fa_b")} for nm in S}
    for i in range(BAT):
        G = groups(np.concatenate([vix[vids[j]] for j in rng.choice(len(vids), len(vids), True)]), fcode)
        for nm in S:
            r = b_stats(S[nm], G, need_auc_c=False)
            for k in BD[nm]:
                BD[nm][k][i] = r[k]
    for s_ in names:
        m = names[s_]["main"]
        for other in ("binary", "P0"):
            o = names[s_][other]
            for k in ("auc_beautified", "d_miss_beauty_only", "fa_b"):
                eff = dprime(pt[m][k]) - dprime(pt[o][k]) if k == "auc_beautified" else (cohen_h(pt[m][k] / 100, pt[o][k] / 100) if k == "fa_b" else float("nan"))
                rec.append(comp(f"Att_B_{k}_{s_}", f"main - {other} {k} {s_}", pt[m][k] - pt[o][k], BD[m][k] - BD[o][k], eff, len(vids), seed=s_, ref=other, metric=k,
                                values={"main": pt[m][k], other: pt[o][k]}))
    OUT["attribution"] = rec
    log("attribution done")


# ---------------------------------------------------------------- composite claim: "low on both axes"
def pareto(ptA, ptB):
    """Pareto front among the 17 published detectors and ours (one seed at a time), point estimates, for every pairing of a
    direction-A axis with a direction-B axis. Lower is better on every axis (AUC is negated)."""
    axesA = {"paired share (lower better)": "share", "tie-aware paired share (lower better)": "share_tieaware", "FA@5%FPR (lower better)": "fa5"}
    axesB = {"AUC_b (higher better)": ("auc_beautified", -1), "beauty-only miss rise (lower better)": ("d_miss_beauty_only", 1),
             "miss on beautified forgeries (lower better)": ("miss_b", 1)}
    res = {}
    for an, ka in axesA.items():
        for bn, (kb, sg) in axesB.items():
            for s_ in ("s1", "s2"):
                pts = {p: (ptA[p][ka], sg * ptB[p][kb]) for p in PUB}
                oa, ob = ptA[f"ours {s_}"][ka], sg * ptB[OURS_B[s_]][kb]
                pts["ours"] = (oa, ob)
                front = [k for k, (x, y) in pts.items() if not any((x2 <= x and y2 <= y) and (x2 < x or y2 < y) for k2, (x2, y2) in pts.items() if k2 != k)]
                dom = [k for k, (x, y) in pts.items() if k != "ours" and x <= oa and y <= ob]
                res[f"{an} x {bn} {s_}"] = {"front": front, "ours_dominated_by": dom}
    OUT["pareto"] = res


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--json"); ap.add_argument("--fast", action="store_true"); a = ap.parse_args()
    BA, BB, BI, BP = (2000, 2000, 2000, 1000) if a.fast else (10000, 5000, 2000, 2000)
    OUT["meta"] = {"draws": {"A_pairs": BA, "B_videos": BB, "B_identity": BI, "probes_video": BP}, "fast": a.fast, "python": sys.version.split()[0], "numpy": np.__version__}
    md = MAIN_MD.read_text(encoding="utf-8")
    ptA, _, _ = direction_A(BA, md)
    ptB = direction_B(BB, BI, md)
    probes(BP)
    pareto(ptA, ptB)
    attribution(BP)
    # families: BH within each declared family; global sensitivity over the 58 reported comparisons
    allrec = OUT["A"]["comparisons"] + OUT["B"]["comparisons"] + OUT["B"]["identity_comparisons"] + OUT["attribution"]
    fams = apply_bh(allrec)
    primary = [r for r in allrec if r["family"] in ("A_share_s1", "A_share_s2", "B_auc_s1", "B_auc_s2", "B_miss_s1", "B_miss_s2")]
    qg = bh([r["p"] for r in primary])
    for r, q in zip(primary, qg):
        r["q_global58"] = float(q); r["bonf_global58"] = float(min(1.0, r["p"] * len(primary)))
    qb = bh([r["p"] for r in primary if r["family"].startswith("B_")])
    for r, q in zip([r for r in primary if r["family"].startswith("B_")], qb):
        r["q_B24"] = float(q)
    try:
        from statsmodels.stats.multitest import multipletests
        for f, rs in fams.items():
            sm = multipletests([r["p"] for r in rs], method="fdr_bh")[1]; assert np.allclose(sm, [r["q"] for r in rs]), f
        OUT["meta"]["bh_crosscheck_statsmodels"] = "identical"
    except ImportError:
        OUT["meta"]["bh_crosscheck_statsmodels"] = "statsmodels unavailable"
    # grades for every paired (seed 1, seed 2) comparison
    grades = {}
    by = {}
    for r in allrec:
        if "seed" in r and "ref" in r:
            by.setdefault((r["family"].rsplit("_", 1)[0], r["ref"]), {})[r["seed"]] = r
    for (fam, ref), d in by.items():
        if "s1" in d and "s2" in d and not fam.startswith("Bid"):
            grades[f"{fam}:{ref}"] = grade(d["s1"], d["s2"])
    OUT["grades"] = grades
    OUT["families"] = {f: {"m": len(rs), "n_q_lt_05": sum(r["q"] < 0.05 for r in rs), "n_p_lt_05": sum(r["p"] < 0.05 for r in rs)} for f, rs in fams.items()}
    # console summary
    log("\n== primary families (as reported in MAIN_CLAIMS) ==")
    for r in primary:
        log(f"{r['family']:<11} {r['label']:<45} est {r['est']:+8.3f} CI [{r['ci'][0]:+.3f}, {r['ci'][1]:+.3f}] p {r['p']:.4f} z {r['z']:+7.2f} q {r['q']:.4f} "
            f"q58 {r['q_global58']:.4f} std {r['effect_std']:+.2f} ({r['effect_size']})")
    log("\n== grades (two seeds) =="); [log(f"{k:<28} {v}") for k, v in grades.items()]
    log("\n== family counts =="); [log(f"{k:<16} {v}") for k, v in OUT["families"].items()]
    if a.json:
        def strip(o):
            if isinstance(o, dict):
                return {k: strip(v) for k, v in o.items() if k != "_draws"}
            if isinstance(o, list):
                return [strip(v) for v in o]
            if isinstance(o, (np.floating, np.integer)):
                return o.item()
            return o
        Path(a.json).write_text(json.dumps(strip(OUT), indent=1, ensure_ascii=False), encoding="utf-8"); log(f"wrote {a.json}")


if __name__ == "__main__":
    main()
