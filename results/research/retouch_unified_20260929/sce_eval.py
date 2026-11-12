"""Addendum 48: smoothing-conditional expert (SCE). Router p_s (clipe5 presence prob, Addendum 47 covariates), untreated detector A
(clipe5b_s20260929, scores from smooth38 / alipair / bct_ffval), smoothing expert B (clipe5bzxs_s20260929; its scores are produced
by smooth_probe38.py score, bct.py score, and the Alibaba pairs by eval_ru). Decision: p_s > 0.5 -> B against t_B, else A against t_A.
t_A: 95th pct of A on the test source's untreated genuine frames. t_B: 95th pct of B on the FF++ validation genuine renders of
the seven smoothing forms (bct_ffval_<B>.npz, forms only). Outputs sce.json, SCE.md.
python sce_eval.py [A_tag B_tag]"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
A = sys.argv[1] if len(sys.argv) > 2 else "clipe5b_s20260929"; Bt = sys.argv[2] if len(sys.argv) > 2 else "clipe5bzxs_s20260929"
FORMS = ["bil9", "bil15", "bil21", "median5", "gblend", "fl06", "fl12"]; CONDS = ["untreated"] + FORMS; NB = 1000


def boot_idx(vid, rng):
    uv = np.unique(vid); by = {k: np.where(vid == k)[0] for k in uv}
    return [np.concatenate([by[k] for k in rng.choice(uv, len(uv))]) for _ in range(NB)]


def main():
    meta = json.loads((HERE / "smooth38_list.json").read_text()); y = np.array(meta["y"]); vid = np.array(meta["video"]); lc = np.array(meta["lm_ok"])
    sa = np.load(HERE / f"smooth38_{A}.npz"); sb = np.load(HERE / f"smooth38_{Bt}.npz"); cov = np.load(HERE / "bct_cov_cdf.npz")
    fb = np.load(HERE / f"bct_ffval_{Bt}.npz"); lf = np.array(json.loads((HERE / "bct_ffval_list.json").read_text())["lm_ok"])
    tB = float(np.nanquantile(np.concatenate([fb[c][lf] for c in FORMS]), 0.95))
    g0 = (y == 0) & lc; f0 = (y == 1) & lc; tA = float(np.nanquantile(sa["untreated"][g0], 0.95))
    rng = np.random.default_rng(0); idx = boot_idx(vid, rng)
    res = {"t_A": round(tA, 4), "t_B": round(tB, 4), "forms": {}}

    def decide(c):
        ps = cov[f"ps_{c}"]; route = ps > 0.5
        return np.where(route, sb[c] > tB, sa[c] > tA), route

    base_miss = {}
    for c in CONDS:
        d, route = decide(c); dA = sa[c] > tA
        fa = d[g0].mean() * 100; miss = (~d[f0]).mean() * 100; faA = dA[g0].mean() * 100; missA = (~dA[f0]).mean() * 100
        if c == "untreated":
            base_miss["sce"], base_miss["A"] = miss, missA
        bs_fa = [d[g0][np.isin(np.where(g0)[0], ii)].mean() * 100 for ii in idx[:300]]
        res["forms"][c] = {"fa_sce": round(float(fa), 1), "fa_ci": [round(float(np.percentile(bs_fa, 2.5)), 1), round(float(np.percentile(bs_fa, 97.5)), 1)],
                           "miss_sce": round(float(miss), 1), "miss_rise_sce": round(float(miss - base_miss["sce"]), 1),
                           "fa_A": round(float(faA), 1), "miss_A": round(float(missA), 1), "miss_rise_A": round(float(missA - base_miss["A"]), 1),
                           "routed_to_B_pct": round(float(route[lc].mean() * 100), 1),
                           "auc_B_both_smoothed": round(float(_auc(sb[c][lc], y[lc])), 4), "auc_A_both_smoothed": round(float(_auc(sa[c][lc], y[lc])), 4)}
    # commercial Smoothing-90: A and B scores from eval_ru (ali_scores_<tag>.npz, P[:,1]); covariate from bct_cov_ali
    try:
        za = np.load(HERE / f"ali_scores_{A}.npz"); zb = np.load(HERE / f"ali_scores_{Bt}.npz"); ca = np.load(HERE / "bct_cov_ali.npz")
        key = {(g, s): i for i, (g, s) in enumerate(zip(ca["group"], ca["stem"]))}
        def pick(z):
            P = z["P"][:, 1].astype(float); g = z["group"]; st = z["stem"]; ok = np.array([(gg, ss) in key for gg, ss in zip(g, st)]); return P[ok], g[ok], np.array([key[(gg, ss)] for gg, ss in zip(g[ok], st[ok])])
        PA, gA, iA = pick(za); PB, gB, iB = pick(zb); o = gA == "orig_0"; m = gA == "Smoothing_90"
        ta = np.nanquantile(PA[o], 0.95); ps = ca["ps"][iA]; route = ps > 0.5
        # B's threshold on the service: its own 95th pct on originals that route to B is undefined (few); use t_B from FF++ val
        dec = np.where(route, PB > tB, PA > ta)
        res["commercial"] = {"s90_accused_sce": round(float(dec[m].mean() * 100), 1), "s90_accused_A": round(float((PA[m] > ta).mean() * 100), 1),
                             "orig_fa_sce": round(float(dec[o].mean() * 100), 1), "routed_s90_pct": round(float(route[m].mean() * 100), 1), "routed_orig_pct": round(float(route[o].mean() * 100), 1)}
    except FileNotFoundError as e:
        res["commercial"] = {"missing": str(e)[-80:]}
    (HERE / "sce.json").write_text(json.dumps(res, indent=1))
    L = [f"# SCE: router p_s (clipe5), A = {A}, B = {Bt}; t_A {res['t_A']}, t_B {res['t_B']} (FF++ val smoothed genuine)", "",
         "| form | routed to B % | FA A -> SCE | miss A -> SCE | miss rise A -> SCE | AUC both smoothed A / B |", "|---|---|---|---|---|---|"]
    for c, r in res["forms"].items():
        L.append(f"| {c} | {r['routed_to_B_pct']} | {r['fa_A']} -> {r['fa_sce']} {r['fa_ci']} | {r['miss_A']} -> {r['miss_sce']} | {r['miss_rise_A']} -> {r['miss_rise_sce']} | {r['auc_A_both_smoothed']} / {r['auc_B_both_smoothed']} |")
    L += ["", f"commercial: {json.dumps(res['commercial'])}"]
    (HERE / "SCE.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


def _auc(s, y):
    from sklearn.metrics import roc_auc_score
    k = ~np.isnan(s); return roc_auc_score(y[k], s[k])


if __name__ == "__main__":
    main()
