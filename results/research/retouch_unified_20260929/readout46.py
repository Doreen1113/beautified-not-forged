"""Addendum 46 readout (PRE_DECLARED.md, Addendum 46 + amendment 1): SIC arms clipe5z (factorised, primary) and clipe5bz
(binary, secondary), seeds 20260929 / 20260930. Bars (1), (2), (3) as written, (3'), (4), (5), (6) on the forged score
P(forged) = sigmoid(z_f); for clipe5z also the attribute head against clipe5 of the same seed (no bar).
Statistics: point estimates decide; 95% intervals from 1000 video-cluster draws (rng 0, the same draws for every model;
commercial service: identity draws, rng 0). Inputs are the files the chains write; a missing input is reported as such.
python readout46.py -> readout46.json, READOUT46.md"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

B = Path(r"C:\My_Project\AIGC"); R = B / "results/research"; HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
SEEDS = ["20260929", "20260930"]; NB = 1000
FORMS = ["bil9", "bil15", "bil21", "median5", "gblend", "fl06", "fl12"]
ARMS = {"clipe5z": "SIC factorised (primary)", "clipe5bz": "SIC binary (secondary)", "clipe5bzl0": "SIC binary, lambda 0 control (am. 2)", "clipe5bzl03": "SIC binary, lambda 0.3 (am. 3)", "clipe5bzl01": "SIC binary, lambda 0.1 (am. 3)", "clipe5bzsg": "SIC binary, stop-gradient (am. 4)", "clipe5fbzsg": "FF++-only SIC binary, stop-gradient (am. 4/5)", "clipe5bzsgl03": "SIC-sg binary, lambda 0.3 (am. 6)", "clipe5bzsgl01": "SIC-sg binary, lambda 0.1 (am. 6)", "clipe5bzsgG": "SIC-sg binary, Gaussian operator ablation (am. 7)", "clipe5bzsgh": "SIC-h binary, one-sided consistency (am. 8)", "clipe5bzsgl003": "SIC-sg binary, lambda 0.03 (am. 9)", "clipe5bzxs": "smoothing expert, trained on x_s only (Add. 48)", "clipe5fbp0F2": "P0 with Face2Face+FaceSwap forgeries only (Add. 49)", "clipe5bzEsg": "SIC-sg under Effort tuning (Add. 50)"}
CDFB = {"clipe5_s20260929": "RU-clipe5", "clipe5_s20260930": "RU-clipe5-s2"}


def ci(a):
    return [round(float(np.percentile(a, 2.5)), 4), round(float(np.percentile(a, 97.5)), 4)]


# ---------------------------------------------------------------- smoothing (Addendum 38 files, all seven forms)
META = json.loads((HERE / "smooth38_list.json").read_text())
Y = np.array(META["y"]); V = np.array(META["video"]); OK = np.array(META["lm_ok"])
_uv = np.unique(V); _by = {k: np.where(V == k)[0] for k in _uv}; _rng = np.random.default_rng(0)
DRAWS = [np.concatenate([_by[k] for k in _rng.choice(_uv, len(_uv))]) for _ in range(NB)]


def s38(tag):
    f = HERE / f"smooth38_{tag}.npz"
    return None if not f.is_file() else {c: np.load(f)[c].astype(np.float64) for c in ["untreated"] + FORMS}


def smooth_stats(S, idx):
    """fa (%) and miss rise (pp) per form at the 5%-FPR threshold of untreated genuine frames; frames with landmarks only."""
    i = idx[OK[idx]]; y = Y[i]; g, f = y == 0, y == 1; u = S["untreated"][i]; t = np.quantile(u[g], 0.95); m0 = (u[f] <= t).mean() * 100
    out = {}
    for c in FORMS:
        s = S[c][i]; out[c] = ((s[g] > t).mean() * 100, (s[f] <= t).mean() * 100 - m0)
    return out


def smoothing(tag, p0):
    S, P = s38(tag), s38(p0)
    if S is None:
        return None
    a = smooth_stats(S, np.arange(len(Y))); bs = [smooth_stats(S, d) for d in DRAWS]
    r = {}
    for c in FORMS:
        r[c] = {"fa": round(a[c][0], 1), "fa_ci": ci([b[c][0] for b in bs]), "miss_rise": round(a[c][1], 1), "miss_rise_ci": ci([b[c][1] for b in bs]),
                "auc_both_smoothed": round(float(roc_auc_score(Y, S[c])), 4)}
    r["auc_untreated"] = round(float(roc_auc_score(Y, S["untreated"])), 4)
    if P is not None:
        ap = smooth_stats(P, np.arange(len(Y))); bp = [smooth_stats(P, d) for d in DRAWS]
        for c in FORMS:
            r[c]["p0_miss_rise"] = round(ap[c][1], 1); r[c]["p0_fa"] = round(ap[c][0], 1)
            r[c]["minus_p0"] = round(a[c][1] - ap[c][1], 1); r[c]["minus_p0_ci"] = ci([b[c][1] - q[c][1] for b, q in zip(bs, bp)])
    return r


# ---------------------------------------------------------------- commercial service
def ali(tag):
    f = HERE / f"ali_scores_{tag}.npz"
    if not f.is_file():
        return None
    z = np.load(f); P, Rr, g, st = z["P"], z["R"], z["group"], z["stem"]; p = P[:, 1].astype(np.float64)
    o = g == "orig_0"; m = g == "Smoothing_90"; so = dict(zip(st[o], p[o])); ids = np.unique(st); by = {k: np.where(st == k)[0] for k in ids}
    rng = np.random.default_rng(0); draws = [np.concatenate([by[k] for k in rng.choice(ids, len(ids))]) for _ in range(NB)]

    def acc(d):
        t = np.nanquantile(p[d][o[d]], 0.95); return (p[d][m[d]] > t).mean() * 100
    t = np.nanquantile(p[o], 0.95)
    return {"smoothing90_accused": round(float((p[m] > t).mean() * 100), 1), "ci": ci([acc(d) for d in draws]),
            "smoothing90_above_own": round(100 * float(np.mean([a > so[k] for a, k in zip(p[m], st[m])])), 1),
            "auroc_s90_vs_orig": round(float(roc_auc_score(np.r_[np.zeros(o.sum()), np.ones(m.sum())], np.r_[p[o], p[m]])), 4)}


def attribute(tag):
    """clipe5z decision rule of amendment 1 on the commercial service: forged if P(forged) > t_f (FF++-val genuine 95th pct),
    else beautified if sigmoid(z_b) > 0.5, else real; plus the native argmax and eval_ru's presence-head numbers."""
    f = HERE / f"ali_scores_{tag}.npz"; fv = R / "review_v4_exps_20261016/scores" / f"ffval_{tag}.npz"; fe = HERE / f"eval_ru_{tag}.json"
    if not (f.is_file() and fe.is_file()):
        return None
    z = np.load(f); P, g = z["P"].astype(np.float64), z["group"]; o = g == "orig_0"; r = ~o
    out = {}
    if fv.is_file():
        tf = float(np.nanquantile(np.load(fv)["s"].astype(np.float64), 0.95)); pf = P[:, 1]; pb = P[:, 2] / np.clip(1 - pf, 1e-9, None)
        dec = np.where(pf > tf, 1, np.where(pb > 0.5, 2, 0))
        rule = {"t_forged": round(tf, 4), "orig_real": round(float((dec[o] == 0).mean() * 100), 2), "orig_forged": round(float((dec[o] == 1).mean() * 100), 2),
                "renders_beautified": round(float((dec[r] == 2).mean() * 100), 2), "renders_forged": round(float((dec[r] == 1).mean() * 100), 2)}
        rule["balanced"] = round((rule["orig_real"] + rule["renders_beautified"]) / 2, 2)
        rule["by_op_level_beautified"] = {k: round(float((dec[g == k] == 2).mean() * 100), 1) for k in sorted(set(g)) if k != "orig_0"}
        out["rule_amendment1"] = rule
    e = json.loads(fe.read_text())["ali"]
    out["native_argmax"] = {"orig": e["orig"], "pooled": e["pooled"]}
    out["presence"] = {"eq4": {k: e["eq4"][k] for k in ("TP", "TN_same_image", "AC")}, "orig_presence_TN_per_op": e["orig_presence_TN_per_op"], "orig_all_absent": e["orig_all_absent"]}
    vv = HERE / f"vendor_val_{tag}.log"
    out["vendor_val_log_tail"] = vv.read_text(encoding="utf-8", errors="replace").strip().splitlines()[-3:] if vv.is_file() else None
    fx = R / "cgd_20260927" / f"explain_RUCLIPE{tag.split('_s')[0][5:].upper()}_s{tag.split('_s')[1]}.json"
    if fx.is_file():
        d = json.loads(fx.read_text()); out["explain"] = {m: {"flip": round(100 * d[m]["evidence"]["flip_pred"], 1), "iou7": d[m]["evidence"].get("iou7")} for m in ("donor", "sd", "sdxl") if m in d}
    return out


# ---------------------------------------------------------------- untreated CDF-v2 / DFD video AUC (as readout42)
def vauc(y, s, v):
    by = defaultdict(list); yy = {}
    for a, b, c in zip(y, s, v):
        by[c].append(b); yy[c] = a
    k = list(by); return roc_auc_score([yy[x] for x in k], [np.mean(by[x]) for x in k])


def paired_video(load, a, b):
    try:
        ya, sa, v = load(a); yb, sb, vb = load(b)
    except FileNotFoundError:
        return None
    assert list(v) == list(vb)
    vs = sorted(set(v)); ix = {k: np.where(v == k)[0] for k in vs}; rng = np.random.default_rng(0); d = []
    for _ in range(NB):
        pick = rng.choice(len(vs), len(vs), True); ii = np.concatenate([ix[vs[j]] for j in pick])
        vv = np.concatenate([[f"{n}"] * len(ix[vs[j]]) for n, j in enumerate(pick)])
        d.append(vauc(ya[ii], sa[ii], vv) - vauc(yb[ii], sb[ii], vv))
    ea, eb = vauc(ya, sa, v), vauc(yb, sb, v)
    return {"arm": round(ea, 4), "ref": round(eb, 4), "diff": round(ea - eb, 4), "ci": ci(d)}


def load_cdf(tag):
    from compare_sbi import rows
    y, v = rows("celebdf_std32v2.txt"); return np.asarray(y), np.load(HERE / f"cdf_scores_{tag}.npz")["P"][:, 1].astype(np.float64), np.asarray(v)


def load_dfd(tag):
    z = np.load(HERE / f"dfd_v3_scores_{tag}.npz"); return z["y"], z["s"].astype(np.float64), z["video"]


# ---------------------------------------------------------------- DF40 reenactment (as df40_eval.analyse, paired)
def df40(a, b):
    D = R / "df40_eval_20261012"; sys.path.insert(0, str(D)); import df40_eval as E
    if not all((D / f"scores_{n}.npz").is_file() for n in (a, b)):
        return None
    r = E.rows(); vid = np.array([f"{x[4]}|{x[3]}|{x[2]}" for x in r]); uv, inv = np.unique(vid, return_inverse=True)
    vdom = np.array([u.split("|")[0] for u in uv]); vmeth = np.array([u.split("|")[1] for u in uv]); Vm = {}
    for n in (a, b):
        s = np.load(D / f"scores_{n}.npz")["s"].astype(np.float64); ok = ~np.isnan(s)
        num = np.bincount(inv[ok], s[ok], len(uv)); den = np.bincount(inv[ok], minlength=len(uv)); Vm[n] = np.where(den > 0, num / np.maximum(den, 1), np.nan)
    rng = np.random.default_rng(0); groups = {}
    for d in ("ff", "cdf"):
        real = np.where((vdom == d) & (vmeth == "real"))[0]
        for m in sorted(set(vmeth[vdom == d]) - {"real"}):
            groups[(d, m)] = (real, np.where((vdom == d) & (vmeth == m))[0])
    draws = {k: [(rng.integers(0, len(x), len(x)), rng.integers(0, len(y), len(y))) for _ in range(NB)] for k, (x, y) in groups.items()}

    def auc(v, x, y):
        s = np.concatenate([v[x], v[y]]); t = np.r_[np.zeros(len(x)), np.ones(len(y))]; k = ~np.isnan(s); return roc_auc_score(t[k], s[k])

    def fr(n, i=None):
        per = {k: (auc(Vm[n], x, y) if i is None else auc(Vm[n], x[draws[k][i][0]], y[draws[k][i][1]])) for k, (x, y) in groups.items()}
        return {d: float(np.mean([v for (dd, m), v in per.items() if dd == d and m not in E.FS])) for d in ("ff", "cdf")}
    pa, pb = fr(a), fr(b); bs = [(fr(a, i), fr(b, i)) for i in range(NB)]
    return {d: {"arm": round(pa[d], 4), "ref": round(pb[d], 4), "diff": round(pa[d] - pb[d], 4), "ci": ci([x[d] - y[d] for x, y in bs])} for d in ("ff", "cdf")}


def main():
    fc = json.loads((R / "celebdfb_v2_20260927/fair_cdfb.json").read_text())
    out = {}; L = ["# Addendum 46 readout: smoothing-invariant consistency (SIC)", "",
                   "Bars on P(forged); point estimates decide; [95% CI]. (3') = miss rise <= max(P0 rise, 0) + 5. Primary arm clipe5z, secondary clipe5bz.", ""]
    for arm, lab in ARMS.items():
        for s in SEEDS:
            t = f"{arm}_s{s}"; b, m, p0 = f"clipe5b_s{s}", f"clipe5_s{s}", f"clipe5fbp0_s{s}"
            if not (HERE / f"meta_ru_{t}.json").is_file():
                out[t] = {"status": "not trained"}; continue
            r = {"label": lab}
            sm = smoothing(t, p0); r["smoothing"] = sm; al = ali(t); r["commercial"] = al
            r["untreated_cdf_video_vs_binary"] = paired_video(load_cdf, t, b) if (HERE / f"cdf_scores_{t}.npz").is_file() else None
            r["untreated_dfd_video_vs_binary"] = paired_video(load_dfd, t, b) if (HERE / f"dfd_v3_scores_{t}.npz").is_file() else None
            cd = fc.get(f"RU-{t}", {}); r["cdfb"] = {"auc_b": cd.get("auc_beautified"), "ci": cd.get("ci", {}).get("auc_beautified"), "main_auc_b": fc.get(CDFB[m], {}).get("auc_beautified"),
                                                     "fa_b": cd.get("fa_b"), "d_miss_beauty_only": cd.get("d_miss_beauty_only")}
            r["df40_reenactment_vs_binary"] = df40(t, b)
            if arm == "clipe5z":
                r["attribute"] = attribute(t); r["attribute_main_same_seed"] = attribute(m)
            v = {}
            if sm:
                v["1_facelocal_fa<=15"] = all(sm[c]["fa"] <= 15 for c in ("fl06", "fl12"))
                v["3_as_written"] = all(sm[c].get("minus_p0", 99) <= 5 for c in FORMS) if "minus_p0" in sm["bil9"] else None
                v["3prime"] = all(sm[c]["miss_rise"] <= max(sm[c]["p0_miss_rise"], 0) + 5 for c in FORMS) if "p0_miss_rise" in sm["bil9"] else None
            if sm and al:
                v["2_bil15_21_fa<=15_and_S90<=15"] = all(sm[c]["fa"] <= 15 for c in ("bil15", "bil21")) and al["smoothing90_accused"] <= 15
            if r["untreated_cdf_video_vs_binary"] and r["untreated_dfd_video_vs_binary"]:
                v["4_untreated_video_not_lower_than_binary_by>0.010"] = r["untreated_cdf_video_vs_binary"]["diff"] >= -0.010 and r["untreated_dfd_video_vs_binary"]["diff"] >= -0.010
            if r["cdfb"]["auc_b"] is not None and r["cdfb"]["main_auc_b"] is not None:
                v["5_cdfb_auc_b>=main"] = r["cdfb"]["auc_b"] >= r["cdfb"]["main_auc_b"]
            if r["df40_reenactment_vs_binary"]:
                v["6_df40_reenactment_not_lower_by>0.030"] = all(r["df40_reenactment_vs_binary"][d]["diff"] >= -0.030 for d in ("ff", "cdf"))
            r["bars"] = v; out[t] = r
    # reading per arm, both seeds
    for arm in ARMS:
        ts = [f"{arm}_s{s}" for s in SEEDS]
        if not all("bars" in out.get(t, {}) for t in ts):
            out[f"reading_{arm}"] = "incomplete"; continue
        need = ["1_facelocal_fa<=15", "2_bil15_21_fa<=15_and_S90<=15", "3prime", "4_untreated_video_not_lower_than_binary_by>0.010", "5_cdfb_auc_b>=main", "6_df40_reenactment_not_lower_by>0.030"]
        ok = lambda keys: all(out[t]["bars"].get(k) is True for t in ts for k in keys)
        if any(k not in out[t]["bars"] for t in ts for k in need):
            out[f"reading_{arm}"] = "incomplete (missing inputs: " + ", ".join(sorted({k for t in ts for k in need if k not in out[t]["bars"]})) + ")"
        elif ok(need):
            out[f"reading_{arm}"] = "all six bars ((3') for (3)) on both seeds: method claim allowed with stated costs, confound (b), and the lambda = 0 control pending"
        elif ok(need[:2] + need[3:4]):
            out[f"reading_{arm}"] = "partial: (1)+(2)+(4) on both seeds; failing: " + ", ".join(sorted({k for t in ts for k in need if out[t]["bars"].get(k) is not True}))
        else:
            out[f"reading_{arm}"] = "negative: " + ", ".join(sorted({f"{k} ({t})" for t in ts for k in need if out[t]["bars"].get(k) is not True}))
    (HERE / "readout46.json").write_text(json.dumps(out, indent=1))
    for t, r in out.items():
        if isinstance(r, str):
            L += [f"**{t}**: {r}", ""]; continue
        L += [f"## {t} ({r.get('label', r.get('status'))})", ""]
        if "bars" not in r:
            continue
        L.append("bars: " + ", ".join(f"{k}={v}" for k, v in r["bars"].items())); L.append("")
        if r["smoothing"]:
            L += ["| form | FA % [CI] | miss rise [CI] | P0 rise | minus P0 [CI] | AUC both smoothed |", "|---|---|---|---|---|---|"]
            for c in FORMS:
                q = r["smoothing"][c]
                L.append(f"| {c} | {q['fa']} {q['fa_ci']} | {q['miss_rise']:+.1f} {q['miss_rise_ci']} | {q.get('p0_miss_rise')} | {q.get('minus_p0')} {q.get('minus_p0_ci')} | {q['auc_both_smoothed']} |")
            L.append("")
        L += ["```", json.dumps({k: v for k, v in r.items() if k not in ("smoothing", "bars", "label")}, indent=1), "```", ""]
    (HERE / "READOUT46.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    main()
