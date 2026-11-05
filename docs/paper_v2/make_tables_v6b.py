r"""Tables, numbers and figures for paper v6b (2026-10-17): the v6 tables with (1) the full-data model trained with the forgery head
only (clipe5b, two seeds; \oursB{}) as the first, detection-reference row and the full model with three classes and operation
scores (clipe5; \oursF{}) beside it, (2) the second
seeds of the symmetric-view variant (clipe5y_s20260930) and of clipe5b added where the scores exist, (3) identity-cluster
intervals added to the Celeb-DF-B supplement tables, and (4) the dose table at three decimals. No model is run; every number is
read from an existing score or result file or recomputed from score files with the code of the script that first produced it.
v6 files are left untouched; this script writes tables/tab_v6b_*.tex, figs/fig_accuse_v6b.{pdf,png} and v6b_numbers.json.
Changes and formulas: V6B_CHANGES.md.

python docs/paper_v2/make_tables_v6b.py
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import make_tables_v4 as v4   # noqa: E402
import make_tables_v5 as v5   # noqa: E402
import make_tables_v6 as v6   # noqa: E402
import figstyle as FS          # noqa: E402

BASE = Path(r"C:\My_Project\AIGC"); R = BASE / "results/research"; OUT = HERE / "tables"
RU = R / "retouch_unified_20260929"; RV = R / "review_v4_exps_20261016"; DF40 = R / "df40_eval_20261012"; ALI = R / "alipair_zeroshot_20260929"
CDFB = R / "celebdfb_v2_20260927"
sys.path.insert(0, str(RV))
import identity_boot as IB    # noqa: E402  (clusters / draws_of only; nothing is rerun)

PUB = v4.PUB; CITE = v6.CITE; NUM = {}
OB, OA, OY, S2 = r"\oursB{}", r"\oursF{}", r"\oursF{}, sym.\ view", r"\quad second seed"
# (key, label, Celeb-DF-B score name, tag)
OURS = [("B1", OB, "RU-clipe5b", "clipe5b_s20260929"), ("B2", S2, "RU-clipe5b_s20260930", "clipe5b_s20260930"),
        ("M1", OA, "RU-clipe5", "clipe5_s20260929"), ("M2", S2, "RU-clipe5-s2", "clipe5_s20260930"),
        ("Y1", OY, "RU-clipe5y_s20260929", "clipe5y_s20260929"), ("Y2", S2, "RU-clipe5y_s20260930", "clipe5y_s20260930")]
DAG = r"$^\dagger$"


def jl(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def tabular(spec, lines, name):
    (OUT / name).write_text("\n".join([rf"\begin{{tabular}}{{{spec}}}", r"\toprule"] + lines + [r"\bottomrule", r"\end{tabular}"]) + "\n", encoding="utf-8")


def label(ln):
    return ln.split(" & ")[0] if (ln.rstrip().endswith(r"\\") and " & " in ln) else None


def relabel_reorder(src, dst, ren, order=None, drop=(), extra=None):
    """Copy tables/<src> to tables/<dst>: row labels renamed by `ren` (exact label match), rows whose new label is in `drop` removed,
    and the blocks headed by the labels in `order` (a head line plus the `\\quad second seed` lines right after it) rewritten
    in that order, in place of the region they occupied. `extra` maps a head label to lines appended to its block."""
    L = []
    for ln in (OUT / src).read_text(encoding="utf-8").splitlines():
        lab = label(ln)
        if lab is not None and lab in ren:
            ln = ren[lab] + ln[len(lab):]; lab = ren[lab]
        if lab is not None and lab in drop:
            continue
        L.append(ln)
    if order:
        heads = [i for i, ln in enumerate(L) if label(ln) in order]
        assert sorted(label(L[i]) for i in heads) == sorted(order), (dst, [label(L[i]) for i in heads], order)
        blocks = {}
        for i in heads:
            j = i + 1
            while j < len(L) and (label(L[j]) or "").startswith(r"\quad second seed"):
                j += 1
            blocks[label(L[i])] = (i, j)
        lo, hi = min(b[0] for b in blocks.values()), max(b[1] for b in blocks.values())
        covered = sum(b[1] - b[0] for b in blocks.values()); assert covered == hi - lo, (dst, "blocks not contiguous", lo, hi, covered)
        new = []
        for h in order:
            a, b = blocks[h]; new += L[a:b] + ((extra or {}).get(h, []))
        L = L[:lo] + new + L[hi:]
    (OUT / dst).write_text("\n".join(L) + "\n", encoding="utf-8")


# ======================================================================== 1. Celeb-DF-B with identity intervals ===========================
OURS_CDFB6B = [("binary s1", "RU-clipe5b"), ("binary s2", "RU-clipe5b_s20260930"), ("main s1", "RU-clipe5"), ("main s2", "RU-clipe5-s2"),
               ("variant", "RU-clipe5y_s20260929"), ("variant s2", "RU-clipe5y_s20260930"), ("FF++ only three-way", "RU-clipe5f"),
               ("P0 s1", "RU-clipe5fbp0_s20260929"), ("P2 sym s1", "RU-clipe5fbg0oy_s20260929"), ("P2 sym s2", "RU-clipe5fbg0oy_s20260930")]


def cdfb_identity(names):
    """Identity-cluster draws exactly as identity_boot.cdfb (identity = Celeb-DF celebrity of the scene, YouTube-real videos alone;
    default_rng(0)); per draw: AUC_b, FA_b, FA_c at the 95th percentile of untreated genuine frames of the draw."""
    rows = [l.split("\t") for l in (BASE / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    folder = np.array([r[3] for r in rows]); vid = np.array([r[2] for r in rows])
    draws, n_units = IB.draws_of(IB.clusters(vid, False), np.random.default_rng(0))

    def st(s, idx):
        f = folder[idx]; x = s[idx]; g = lambda k: x[f == k]; t = np.quantile(g("real"), 0.95)
        return (float(roc_auc_score(np.r_[np.zeros(len(g("real_beautified"))), np.ones(len(g("synthesis_beautified")))], np.r_[g("real_beautified"), g("synthesis_beautified")])),
                100 * float((g("real_beautified") > t).mean()), 100 * float((g("real_compressed") > t).mean()))
    out = {}
    for n in names:
        s = np.load(CDFB / "scores_v3" / f"{n}.npz")["p"][:, 1]   # same dtype handling as identity_boot.py (no cast)
        out[n] = np.array([st(s, b) for b in draws])
    return out, n_units


def cdfb_tables():
    import os, pickle
    cache = Path(os.environ["V6B_CACHE"]) if os.environ.get("V6B_CACHE") else None
    names = v5.REF4 + [n for _, n in OURS_CDFB6B]
    if cache and cache.is_file():
        rec, paired, ID, n_units = pickle.loads(cache.read_bytes())
    else:
        v5.OURS_CDFB = OURS_CDFB6B
        rec, paired = v5.cdfb_all()   # video draws (rng 1) as in v5; asserts agreement with fair_cdfb.json
        ID, n_units = cdfb_identity(names)
        if cache:
            cache.write_bytes(pickle.dumps((rec, paired, ID, n_units)))
    ib = jl(RV / "identity_boot.json")["Celeb-DF-B"]["paired_auc_beautified"]
    pid = {}
    for lab, n in OURS_CDFB6B:
        pid[lab] = {}
        for ref in v5.REF4:
            d = ID[n][:, 0] - ID[ref][:, 0]; pid[lab][ref] = [round(float(np.percentile(d, q)), 4) for q in (2.5, 97.5)]
            k = f"{n} - {ref}"
            if k in ib:   # the six full-data models are in identity_boot.json: the recomputation must reproduce them
                assert np.allclose(pid[lab][ref], ib[k]["identity"], atol=1e-4), (k, pid[lab][ref], ib[k]["identity"])
    for n in names:
        if n in rec:
            d = ID[n][:, 1] - ID[n][:, 2]; rec[n]["dfa_beauty_ci_identity"] = [round(float(np.percentile(d, q)), 2) for q in (2.5, 97.5)]
    NUM["cdfb_rec"] = {n: rec[n] for n in rec if n.startswith("RU-")}; NUM["cdfb_paired_video"] = paired; NUM["cdfb_paired_identity"] = pid
    NUM["cdfb_identity_units"] = n_units
    # --- main Table III (point values)
    dfd = jl(RU / "dfd_filteredff.json")
    L = [r" & & \multicolumn{7}{c}{Celeb-DF-B, app presets (frame level)} & \multicolumn{4}{c}{DFD + 16 held-out filters (frame level)} \\",
         r"\cmidrule(lr){3-9}\cmidrule(lr){10-13}",
         r"Detector & train & AUC & AUC$_c$ & AUC$_b$ & AUC$_c{-}$AUC$_b$ & $\Delta$MISS$_\text{beauty}$ & FA$_b$ & $\Delta$FA$_\text{beauty}$ & AUC & AUC$_f$ & $\Delta$MISS & $\Delta$FA \\", r"\midrule"]

    def row(lab, tr, n, k):
        r = rec[n]; q = dfd[k]
        return " & ".join([lab, tr, v5.f3(r["auc_u"]), v5.f3(r["auc_c"]), v5.f3(r["auc_b"]), f"{r['auc_loss_beauty']:.3f}", f"{r['dmiss_beauty']:+.1f}", f"{r['fa_b']:.1f}",
                           f"{r['dfa_beauty']:+.1f}", v5.f3(q["auc_u"]), v5.f3(q["auc_f"]), f"{q['d_miss']:+.1f}", f"{q['d_fa']:+.1f}"]) + r" \\"
    for k in PUB:
        L.append(row(CITE[k], v5.TRAIN[k], k, k))
    L.append(r"\midrule")
    L.append(row("P0", "FF++", "RU-clipe5fbp0_s20260929", "clipe5fbp0_s20260929")); L.append(row("P2-sym", "FF++", "RU-clipe5fbg0oy_s20260929", "clipe5fbg0oy_s20260929"))
    for key, lab, n, k in OURS:
        L.append(row(lab + DAG, "FF++, FFHQ", n, k))
    tabular("@{}ll ccccccc cccc@{}", L, "tab_v6b_twosided_main.tex")
    # v6 rows that exist in both versions must be unchanged
    old = {label(l): l for l in (OUT / "tab_v5_twosided_main.tex").read_text(encoding="utf-8").splitlines() if label(l)}
    new = {label(l): l for l in L if label(l)}
    for o, nn in ((r"\ours{}$^\dagger$", OA + DAG), (r"binary control$^\dagger$", OB + DAG), (r"\quad \ours{} variant$^\dagger$", OY + DAG), ("P0", "P0"), ("SBI~\\cite{sbi}", "SBI~\\cite{sbi}")):
        assert old[o].split(" & ")[1:] == new[nn].split(" & ")[1:], (o, old[o], new[nn])
    # --- supplement: Celeb-DF-B per detector with video and identity intervals of dFA_beauty
    L = [r" & \multicolumn{3}{c}{frame AUC} & \multicolumn{3}{c}{video AUC} & \multicolumn{4}{c}{false alarms (\%)} \\",
         r"\cmidrule(lr){2-4}\cmidrule(lr){5-7}\cmidrule(lr){8-11}",
         r"Detector & untreated & re-encoded & beautified & untreated & re-encoded & beautified & FA$_c$ & FA$_b$ & $\Delta$FA$_\text{beauty}$ [video CI] & [identity CI] \\", r"\midrule"]
    lab = dict(CITE); lab.update({n: l for _, l, n, _ in OURS}); lab.update({"RU-clipe5f": "FF++-only three-way", "RU-clipe5fbp0_s20260929": "P0",
                                                                           "RU-clipe5fbg0oy_s20260929": "P2-sym", "RU-clipe5fbg0oy_s20260930": S2})
    for n in PUB + [n for _, _, n, _ in OURS] + ["RU-clipe5f", "RU-clipe5fbp0_s20260929", "RU-clipe5fbg0oy_s20260929", "RU-clipe5fbg0oy_s20260930"]:
        if n in ("RU-clipe5b", "RU-clipe5f"):
            L.append(r"\midrule")
        r = rec[n]; ic = r.get("dfa_beauty_ci_identity")
        L.append(" & ".join([lab[n], v5.f3(r["auc_u"]), v5.f3(r["auc_c"]), v5.f3(r["auc_b"]), v5.f3(r["video_auc_u"]), v5.f3(r["video_auc_c"]), v5.f3(r["video_auc_b"]),
                             f"{r['fa_c']:.1f}", f"{r['fa_b']:.1f}", f"{r['dfa_beauty']:+.1f} [{r['dfa_beauty_ci'][0]:+.1f}, {r['dfa_beauty_ci'][1]:+.1f}]",
                             f"[{ic[0]:+.1f}, {ic[1]:+.1f}]" if ic else "--"]) + r" \\")
    tabular("@{}l ccc ccc cccc@{}", L, "tab_v6b_cdfb_extra.tex")
    # --- supplement: paired AUC_b, video and identity intervals
    P = [r"Model & resampling & Effort & Forensics Adapter & GenD & DFD-HR \\", r"\midrule"]
    pl = {"binary s1": OB, "binary s2": S2, "main s1": OA, "main s2": S2, "variant": OY, "variant s2": S2, "FF++ only three-way": "FF++-only three-way",
          "P0 s1": "P0", "P2 sym s1": "P2-sym", "P2 sym s2": S2}
    for k, v in paired.items():
        if k == "FF++ only three-way":
            P.append(r"\midrule")
        P.append(" & ".join([pl[k], "video"] + [f"{v[r][0]:+.3f} [{v[r][1]:+.3f}, {v[r][2]:+.3f}]" for r in v5.REF4]) + r" \\")
        P.append(" & ".join(["", "identity"] + [f"[{pid[k][r][0]:+.3f}, {pid[k][r][1]:+.3f}]" for r in v5.REF4]) + r" \\")
    tabular("@{}l l cccc@{}", P, "tab_v6b_cdfb_paired.tex")
    return rec, paired, pid


# ======================================================================== 2. supplement two-sided table (all three sources) ===============
def twosided_full():
    import make_tables_v3 as v3
    ren = {r"\ours{}, FF++ only": "FF++-only three-way", r"\ours{} (full data, three-way)": OA, r"\quad symmetric-view variant": OY, "same data, forged head only": OB}
    relabel_reorder("tab_v5_twosided_full.tex", "tab_v6b_twosided_full.tex", ren, order=[OB, OA, OY],
                    extra={OB: [v3.row_twosided(S2, "RU-clipe5b_s20260930", "clipe5b_s20260930")], OY: [v3.row_twosided(S2, "RU-clipe5y_s20260930", "clipe5y_s20260930")]})
    t = (OUT / "tab_v6b_twosided_full.tex").read_text(encoding="utf-8"); assert v3.PEND not in t


# ======================================================================== 3. main commercial table ============================================
def retouch_main():
    th = jl(RV / "ffpp_val_thr.json")["sources"]["commercial retouching"]
    z = np.load(RU / "ali_scores_clipe5b_s20260930.npz"); s = z["P"][:, 1].astype(np.float64)
    tf = v4.thresholdfree(s, z["group"], z["stem"]); q = v5.paired_shift(z["P"][:, 1], z["group"], z["stem"], np.random.default_rng(0))
    b2 = " & ".join([S2 + DAG, f"{tf['paired_up']:.1f}", f"{tf['med_orig']:.2f} $\\rightarrow$ {tf['med_s90']:.2f}",
                     f"{q['median_dlogit']:+.2f} [{q['ci'][0]:+.2f}, {q['ci'][1]:+.2f}]", f"{tf['fa_s90']:.1f}", f"{th['clipe5b_s20260930']['Smoothing_90']['deploy']:.1f}"]) + r" \\"
    NUM["s90_binary_s2"] = {"thresholdfree": tf, "paired_shift": q}
    ren = {r"\ours{}$^\dagger$": OA + DAG, r"\quad \ours{} variant$^\dagger$": OY + DAG, r"binary control$^\dagger$": OB + DAG}
    relabel_reorder("tab_v6_retouch_main.tex", "tab_v6b_retouch_main.tex", ren, order=[OB + DAG, OA + DAG, OY + DAG], extra={OB + DAG: [b2]})


# ======================================================================== 4. trade-off tables ==================================================
def tradeoff():
    ren = {r"\ours{}": OA, r"\ours{} variant": OY, "binary control": OB}
    for s, d in (("tab_v6_tradeoff_main.tex", "tab_v6b_tradeoff_main.tex"), ("tab_v6_tradeoff.tex", "tab_v6b_tradeoff.tex")):
        relabel_reorder(s, d, ren, order=[OB, OA, OY])


# ======================================================================== 5. DF40 main table ==================================================
def df40_main():
    d = jl(DF40 / "df40_eval.json"); c = lambda t: [f"{d[t]['mean'][k][0]:.3f}" for k in ("ff/FS", "ff/FR", "cdf/FS", "cdf/FR")]
    old = (OUT / "tab_v5_df40_main.tex").read_text(encoding="utf-8").splitlines()
    head = old[:old.index(r"\midrule", 5) + 1]   # header through the first \midrule after the column labels
    pub = [l for l in old if label(l) and label(l).split("~")[0] in ("eight CNNs (range)", "Effort", "Forensics Adapter", "GenD", "DFD-HR", "CADDM")]
    L = head[2:] + pub + [r"\midrule"] + [" & ".join([lab] + c(t)) + r" \\" for _, lab, _, t in OURS] + \
        [" & ".join(["P0"] + c("clipe5fbp0_s20260929")) + r" \\", " & ".join(["P2-sym"] + c("clipe5fbg0oy_s20260929")) + r" \\"]
    tabular("@{}l cc cc@{}", L, "tab_v6b_df40_main.tex")
    o = {label(l): l.split(" & ")[1:] for l in old if label(l)}; n = {label(l): l.split(" & ")[1:] for l in L if label(l)}
    assert o[r"\ours{}"] == n[OA] and o["binary control"] == n[OB] and o[r"\quad \ours{} variant"] == n[OY] and o["P0"] == n["P0"], "DF40 main table changed"


# ======================================================================== 6. supplement relabels =============================================
def supplement_relabels():
    # AR, deploy, smoothing forms, EFS
    relabel_reorder("tab_v6_ar.tex", "tab_v6b_ar.tex", {r"\ours{}$^\dagger$": OA + DAG, r"\ours{} variant$^\dagger$": OY + DAG, r"binary control$^\dagger$": OB + DAG},
                    order=[OB + DAG, OA + DAG, OY + DAG])
    relabel_reorder("tab_v6_deploy.tex", "tab_v6b_deploy.tex", {r"\ours{}$^\dagger$": OA + DAG, r"\ours{} variant$^\dagger$": OY + DAG, r"binary control$^\dagger$": OB + DAG},
                    order=[OB + DAG, OA + DAG, OY + DAG])
    relabel_reorder("tab_v6_smooth38.tex", "tab_v6b_smooth38.tex", {r"\ours{}$^\dagger$": OA + DAG, r"\ours{} variant$^\dagger$": OY + DAG, r"binary control$^\dagger$": OB + DAG},
                    order=[OB + DAG, OA + DAG, OY + DAG])
    relabel_reorder("tab_v6_efs.tex", "tab_v6b_efs.tex", {r"\ours{}$^\dagger$": OA + DAG, r"\ours{} variant$^\dagger$": OY + DAG, r"binary control$^\dagger$": OB + DAG},
                    order=[OB + DAG, OA + DAG, OY + DAG])
    t = (OUT / "tab_v6b_efs.tex").read_text(encoding="utf-8").replace(r"\multicolumn{7}{@{}l}{\ours{}, native three-way decision", r"\multicolumn{7}{@{}l}{\oursF{}, native three-way decision")
    (OUT / "tab_v6b_efs.tex").write_text(t, encoding="utf-8")
    # second-seed table: (A) the variant against the attribute-head model, (B) ours minus the attribute-head model
    t = (OUT / "tab_v6_seeds.tex").read_text(encoding="utf-8")
    t = t.replace(r"(A) symmetric-view variant against \ours{}, same seed", r"(A) symmetric-view variant against \oursF{}, same seed")
    t = t.replace(r"(B) binary control minus \ours{}, same seed", r"(B) \oursB{} minus \oursF{}, same seed").replace("(main ", "(three-way ")
    t = re.sub(r"vs (\d)", r"vs \1", t)
    (OUT / "tab_v6b_seeds.tex").write_text(t, encoding="utf-8")
    # commercial, all detectors; paired shift; smoothed forgeries; per operation; full-frame filters
    relabel_reorder("tab_v5_retouch_full.tex", "tab_v6b_retouch_full.tex",
                    {r"\ours{}, three-way, full data": OA, r"\ours{}, symmetric-view variant": OY, r"\ours{}, binary control": OB}, order=[OB, OA, OY])
    t = (OUT / "tab_v6b_retouch_full.tex").read_text(encoding="utf-8")
    t = t.replace(r"{\ours{}, FF++ only, exposure arms (seed 1)}", "{FF++-only exposure arms (seed 1)}").replace(r"{\ours{} pipeline, FF++ only, Effort's tuning scheme (seed 1)}", "{FF++ only, Effort's tuning scheme (seed 1)}")
    (OUT / "tab_v6b_retouch_full.tex").write_text(t, encoding="utf-8")
    q = NUM["s90_binary_s2"]["paired_shift"]
    pf = lambda p: rf"${p / 10 ** int(np.floor(np.log10(p))):.1f}\times10^{{{int(np.floor(np.log10(p)))}}}$" if p >= 1e-10 else r"$<10^{-10}$"
    b2 = " & ".join([S2, f"{q['n_up']} / {q['n_down']} / {q['n_tie']}", f"{q['median_dlogit']:+.2f} [{q['ci'][0]:+.2f}, {q['ci'][1]:+.2f}]", pf(q["sign_p"])]) + r" \\"
    relabel_reorder("tab_v5_shift_all.tex", "tab_v6b_shift_all.tex", {r"\ours{} three-way, full data": OA, r"\quad symmetric-view variant": OY, r"\ours{} binary control": OB},
                    order=[OB, OA, OY], extra={OB: [b2]})
    e = jl(RU / "smooth_evasion2.json")

    def ev(lab, tag):
        o = v4.evasion_rec(tag, e)
        return " & ".join([lab, f"{o['miss_untreated']:.1f}"] + [v4.ci(m, 1, plus=True) for m in o["miss_rise"]] + [f"{v:.1f}" for v in o["fa_smoothed_genuine"]] + [f"{o['auc_smoothed_both'][2]:.3f}"]) + r" \\"
    relabel_reorder("tab_v4_evasion.tex", "tab_v6b_evasion.tex", {r"\ours{}, three-way, full data": OA, r"\ours{}, symmetric-view variant": OY, r"\ours{}, binary control": OB},
                    order=[OB, OA, OY], extra={OB: [ev(S2, "clipe5b_s20260930")], OA: [ev(S2, "clipe5_s20260930")], OY: [ev(S2, "clipe5y_s20260930")]})
    relabel_reorder("tab_v5_perop.tex", "tab_v6b_perop.tex", {r"\ours{}, three-way, full data": OA, r"\ours{}, symmetric-view variant": OY, r"\ours{}, binary control": OB,
                                                              r"\ours{}, FF++ only, P0": "P0", r"\ours{}, FF++ only, P2 symmetric smoothing": "P2-sym"}, order=[OB, OA, OY])
    relabel_reorder("tab_v5_fullframe.tex", "tab_v6b_fullframe.tex", {r"\ours{}": OA, r"\ours{}, FF++ only": "FF++-only three-way", "binary control": OB}, order=[OB, OA, "FF++-only three-way"])
    relabel_reorder("tab_negative.tex", "tab_v6b_negative.tex", {"full data, binary (reference)": OB + " (reference)", "full data, binary, operator search": OB + ", operator search"})
    t = (OUT / "tab_v4_fusion.tex").read_text(encoding="utf-8").replace(r"{\ours{} P0 (FF++ only, no beautified views) with CADDM", "{P0 (FF++ only, no beautified views) with CADDM")
    (OUT / "tab_v6b_fusion.tex").write_text(t, encoding="utf-8")
    # three-way native decision and explanation tables: these are results of the attribute-head model
    for s, d, pairs in (("tab_v5_alipair.tex", "tab_v6b_alipair.tex", [(r"\textbf{\ours{}} (CLIP ViT-L/14 + LoRA)", r"\textbf{\oursF{}} (CLIP ViT-L/14 + LoRA)"),
                                                                         (r"\ours{}-lite (EfficientNet-B4)", r"\oursF{}, EfficientNet-B4 (browser)")]),
                        ("tab_v5_alipair_all.tex", "tab_v6b_alipair_all.tex", [(r"main model (\ours{})", r"\oursF{}")]),
                        ("tab_v5_cgd_explain_all.tex", "tab_v6b_cgd_explain_all.tex", [(r"\ours{} (CLIP ViT-L/14 + LoRA)", r"\oursF{} (CLIP ViT-L/14 + LoRA)"),
                                                                                       (r"\ours{}-lite (EffNet-B4)", r"\oursF{}, EffNet-B4 (browser)")])):
        t = (OUT / s).read_text(encoding="utf-8")
        for a, b in pairs:
            assert a in t, (s, a); t = t.replace(a, b)
        assert r"\ours{}" not in t, (d, "unrelabelled \\ours{}")
        (OUT / d).write_text(t, encoding="utf-8")


def df40_full():
    """tab_v5_df40_full with the ours block reordered, second seeds added (df40_eval.json), and two paired blocks: \\ours{} minus the
    four CLIP detectors and minus \\oursF{} (video / identity intervals of identity_boot.json; the Celeb-DF domain has no identity
    labels and keeps video units), and the v5 block of \\oursF{} minus each detector (df40_eval.json, video intervals)."""
    d = jl(DF40 / "df40_eval.json"); ib = jl(RV / "identity_boot.json")["DF40"]["paired"]; K = ("ff/FS", "ff/FR", "cdf/FS", "cdf/FR")
    cell = lambda t: [f"{d[t]['mean'][k][0]:.3f} [{d[t]['mean'][k][1]:.3f}, {d[t]['mean'][k][2]:.3f}]" for k in K]
    ren = {r"\ours{}, three-way, full data": OA, r"\ours{}, symmetric-view variant": OY, r"\ours{}, binary control": OB, r"\ours{}, FF++ only, three-way": "FF++-only three-way"}
    src = (OUT / "tab_v5_df40_full.tex").read_text(encoding="utf-8").splitlines()
    cut = next(i for i, l in enumerate(src) if l.startswith(r"\multicolumn{5}{@{}l}{paired difference"))
    tmp = src[:cut - 1] + [r"\bottomrule", r"\end{tabular}"]   # drop the v5 paired block, rebuilt below
    (OUT / "_tmp_df40.tex").write_text("\n".join(tmp) + "\n", encoding="utf-8")
    relabel_reorder("_tmp_df40.tex", "_tmp_df40b.tex", ren, order=[OB, OA, OY],
                    extra={OB: [" & ".join([S2] + cell("clipe5b_s20260930")) + r" \\"], OY: [" & ".join([S2] + cell("clipe5y_s20260930")) + r" \\"]})
    L = (OUT / "_tmp_df40b.tex").read_text(encoding="utf-8").splitlines()[:-2]
    (OUT / "_tmp_df40.tex").unlink(); (OUT / "_tmp_df40b.tex").unlink()
    f = lambda e, m: f"[{e[m][0]:+.3f}, {e[m][1]:+.3f}]"
    for sd, tag, ref3 in (("first seed", "clipe5b_s20260929", "clipe5_s20260929"), ("second seed", "clipe5b_s20260930", "clipe5_s20260930")):
        L += [r"\midrule", rf"\multicolumn{{5}}{{@{{}}l}}{{paired difference, \oursB{{}} ({sd}) minus; video / identity interval}} \\"]
        for ref, lab in (("effort", CITE["effort"]), ("fadapter", CITE["fadapter"]), ("gend", CITE["gend"]), ("dfdhr", CITE["dfdhr"]), (ref3, OA + " (same seed)")):
            e = ib[f"{tag} - {ref}"]
            L.append(" & ".join([r"\quad " + lab] + [f"{e[k]['diff']:+.3f} {f(e[k], 'video')} {f(e[k], 'identity')}" if k.startswith("ff") else f"{e[k]['diff']:+.3f} {f(e[k], 'video')}" for k in K]) + r" \\")
    L += [r"\midrule", r"\multicolumn{5}{@{}l}{paired difference, \oursF{} (first seed) minus; video interval} \\"]
    pm = d["paired_main_minus"]
    for ref, lab in (("effort", CITE["effort"]), ("fadapter", CITE["fadapter"]), ("gend", CITE["gend"]), ("dfdhr", CITE["dfdhr"])):
        L.append(" & ".join([r"\quad " + lab] + [f"{pm[ref][k][0]:+.3f} [{pm[ref][k][1]:+.3f}, {pm[ref][k][2]:+.3f}]" for k in K]) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_v6b_df40_full.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    old = [l for l in src if l.startswith(r"\quad Effort~")][0]; new = [l for l in L if l.startswith(r"\quad Effort~")][-1]
    assert old.split(" & ")[1:] == new.split(" & ")[1:], (old, new)


def reproduce():
    """tab_v5_reproduce plus our two full-data models on our crop and the paired frame / video differences against the four CLIP
    detectors on their DeepfakeBench crops (dfb_crop_eval.json, first seed; the second seeds were not run through that script)."""
    j = jl(R / "ffpp_benchmark_20260925/dfb_crop_eval.json"); src = (OUT / "tab_v5_reproduce.tex").read_text(encoding="utf-8").splitlines()
    L = src[:-2]; a = lambda dset, t, m: j[dset]["auc"][f"{t}|{m}"]
    for lab, t in ((OB, "clipe5b_s20260929"), (OA, "clipe5_s20260929")):
        if lab == OB:
            L.append(r"\midrule")
        L.append(" & ".join([lab + DAG, "--", f"{a('cdf', t, 'dfb')['frame']:.3f} / {a('cdf', t, 'ours')['frame']:.3f}", "--",
                             f"{a('cdf', t, 'dfb')['video']:.3f} / {a('cdf', t, 'ours')['video']:.3f}", "--", f"{a('dfd', t, 'dfb')['frame']:.3f} / {a('dfd', t, 'ours')['frame']:.3f}"]) + r" \\")
    for lab, t in ((OB, "clipe5b_s20260929"), (OA, "clipe5_s20260929")):
        L += [r"\midrule", rf"\multicolumn{{7}}{{@{{}}l}}{{{lab} (our crop) minus the detector (its DFB crop), 95\% video interval}} \\"]
        for ref in ("effort", "fadapter", "gend", "dfdhr"):
            p = lambda dset, m: j[dset]["paired"][f"{t}|ours minus {ref}|dfb"][m]
            L.append(" & ".join([r"\quad " + CITE[ref], "", f"[{p('cdf', 'frame')[0]:+.3f}, {p('cdf', 'frame')[1]:+.3f}]", "",
                                 f"[{p('cdf', 'video')[0]:+.3f}, {p('cdf', 'video')[1]:+.3f}]", "", f"[{p('dfd', 'frame')[0]:+.3f}, {p('dfd', 'frame')[1]:+.3f}]"]) + r" \\")
    L += src[-2:]
    (OUT / "tab_v6b_reproduce.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def identity_table():
    i = jl(RV / "identity_summary.json"); ib = jl(RV / "identity_boot.json")
    assert {(c["source"], c["quantity"]) for c in i["changed"]} == {(c["source"], c["quantity"]) for c in ib["category_changes"]}
    sub = [("clipe5_s20260929", OA), ("clipe5_s20260930", OA + " s2"), ("clipe5b_s20260929", OB), ("clipe5b_s20260930", OB + " s2"),
           ("clipe5y_s20260929", "sym.\\ view"), ("clipe5y_s20260930", "sym.\\ view s2"), ("clipe5f_s20260929", "FF++-only three-way")]

    def nice(q):
        for a, b in sub:
            q = q.replace(a, "\x00" + b + "\x01")
        return q.replace("_", r"\_").replace("\x00", "").replace("\x01", "")
    L = [r"Source & quantity & estimate & video CI & identity CI & change \\", r"\midrule"]
    for c in ib["category_changes"]:
        L.append(" & ".join([c["source"], nice(c["quantity"]), f"{c['estimate']:+.4f}" if abs(c["estimate"]) < 1 else f"{c['estimate']:+.2f}",
                             f"[{c['video'][0]:+.3f}, {c['video'][1]:+.3f}]", f"[{c['identity'][0]:+.3f}, {c['identity'][1]:+.3f}]",
                             f"{c['categories']['video']} $\\rightarrow$ {c['categories']['identity']}"]) + r" \\")
    tabular("@{}l l c c c l@{}", L, "tab_v6b_identity.tex")
    NUM["identity"] = {"n_intervals": i["n_intervals"], "n_changed": len(i["changed"]), "widening": i["widening"], "units": i["units"]}


def dose():
    """tab_v6_dose with the medians and intervals at three decimals (dose39.json stores three), so that the Effort vignette-0.8 median
    (-0.2052 from smooth38_effort.npz) is not rounded twice."""
    d = jl(RU / "dose39.json")
    lv = [("vig010", "vignette 0.1"), ("vig080", "vignette 0.8"), ("fl03", "face-local 0.03"), ("fl12", "face-local 0.12"), ("bil9", r"bil.\ light"), ("bil21", r"bil.\ strong")]
    L = [r"Detector (gap) & " + " & ".join(b for _, b in lv) + r" & dose response \\", r"\midrule"]
    for k in ("effort", "fadapter", "gend", "dfdhr"):
        r = d[k]; cells = []
        for a, _ in lv:
            x = r["levels"][a]; m = x["median_dlogit"]
            cells.append(f"{m[0]:+.3f} [{m[1]:+.3f}, {m[2]:+.3f}] / {x['dlogit_over_gap']:.2f}")
        dtxt = " / ".join("yes" if r[f"dose_response_{f}"] else "no" for f in ("vignette", "face_local_smoothing", "whole_crop_bilateral"))
        L.append(" & ".join([f"{v6.SHORT[k]} ({r['gap_forged_minus_genuine_logit']:.2f})"] + cells + [dtxt]) + r" \\")
    tabular("@{}l " + "c" * len(lv) + " c@{}", L, "tab_v6b_dose.tex")


# ======================================================================== 7. figure 2 ==========================================================
OURS_FIG = [("Ours, forgery head only", "clipe5b_s20260929"), ("Ours, full model", "clipe5_s20260929"), ("Full model, sym. view", "clipe5y_s20260929")]


def fig_accuse():
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize
    v6.OURS_FIG = [("Ours (main)", "clipe5_s20260929"), ("Ours variant", "clipe5y_s20260929"), ("Binary control", "clipe5b_s20260929")]
    cols, keys, M0 = v6.heat_values()   # v6 values and its cross-checks
    order = [keys.index(t) for _, t in OURS_FIG]; M = np.vstack([M0[:len(v6.ORDER)], M0[order]])
    keys = v6.ORDER + [t for _, t in OURS_FIG]
    NUM["heatmap"] = {"columns": [c.replace("\n", " ") for c, _ in cols], "rows": keys, "values": [[None if np.isnan(x) else round(float(x), 1) for x in r] for r in M]}
    FS.apply(); labels = [v6.SHORT[k] for k in v6.ORDER] + [l for l, _ in OURS_FIG]
    fig, ax = plt.subplots(figsize=(FS.COL, 3.45), layout="constrained")
    cmap = plt.get_cmap(FS.SEQ_CMAP).copy(); cmap.set_bad(FS.LIGHT); norm = Normalize(0, 100)
    ax.imshow(np.ma.masked_invalid(M), cmap=cmap, norm=norm, aspect="auto", interpolation="nearest")
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]; txt = "n/a" if np.isnan(v) else f"{v:.0f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=FS.FS_NOTE, color="white" if (not np.isnan(v) and v > 55) else FS.INK)
    ax.set_xticks(range(M.shape[1])); ax.set_xticklabels([c for c, _ in cols], fontsize=FS.FS_NOTE, linespacing=0.95)
    ax.xaxis.tick_top(); ax.tick_params(axis="x", length=0, pad=1.5)
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=FS.FS_NOTE); ax.tick_params(axis="y", length=0, pad=1.5)
    for i, k in enumerate(keys):
        ax.get_yticklabels()[i].set_color(FS.OURS if i >= len(v6.ORDER) else FS.INK)
    ax.get_yticklabels()[len(v6.ORDER)].set_fontweight("bold")
    for y in (10.5, 12.5, 16.5):
        ax.axhline(y, color="white", lw=1.6)
    ax.axvline(4.5, color="white", lw=1.6)
    for s in ax.spines.values():
        s.set_visible(False)
    FS.save(fig, HERE / "figs" / "fig_accuse_v6b")


if __name__ == "__main__":
    cdfb_tables(); twosided_full(); retouch_main(); tradeoff(); df40_main(); supplement_relabels(); df40_full(); reproduce(); identity_table(); dose(); fig_accuse()
    names = sorted(p.name for p in OUT.glob("tab_v6b_*.tex"))
    for n in names:
        v6.check(n)
    (HERE / "v6b_numbers.json").write_text(json.dumps(NUM, indent=1, default=str), encoding="utf-8")
    print("computed (not read):", {k: sorted(v) for k, v in v4.COMPUTED.items()})
