"""SIC tables from results/research/retouch_unified_20260929/readout46.json.
tables/tab_sic.tex: main-text subset (stop-gradient family, controls, ablations); tables/tab_sic_full.tex: every arm (supplement).
Columns: FA on face-local 0.06 / 0.12 and whole-crop bilateral 15, commercial Smoothing-90 accused, miss rise at face-local 0.12,
untreated CDFv2 / DFD video AUC, Celeb-DF-B AUC, DF40 reenactment (ff), bars passed. python docs/paper_v2/make_tab_sic.py"""
import json
from pathlib import Path

H = Path(__file__).resolve().parent; R = H.parents[1] / "results/research/retouch_unified_20260929"
d = json.loads((R / "readout46.json").read_text(encoding="utf-8"))
# 2026-10-23 correction (CONSISTENCY_AUDIT_20261023 #1): the reference's Smoothing-90 cell was typed as 40.6; under the
# column's own rule (5 % FPR on the untouched originals, readout46.ali) the forgery-head-only reference (clipe5b s1) is 9.1.
import sys as _sys; _sys.path.insert(0, str(R)); import readout46 as _r46
REF_S90 = _r46.ali("clipe5b_s20260929")["smoothing90_accused"]
LABEL = {"clipe5bzl0": "symmetric view only ($\\lambda=0$)", "clipe5bzsgl003": "SIC, $\\lambda=0.03$", "clipe5bzsgl01": "SIC, $\\lambda=0.1$",
         "clipe5bzsgl03": "SIC, $\\lambda=0.3$", "clipe5bzsg": "SIC, $\\lambda=1$", "clipe5bzsgh": "one-sided penalty", "clipe5bzsgG": "Gaussian view (ablation)",
         "clipe5fbzsg": "SIC, $\\lambda=1$, FF++ only", "clipe5bzl01": "symmetric penalty, $\\lambda=0.1$", "clipe5bzl03": "symmetric penalty, $\\lambda=0.3$",
         "clipe5bz": "symmetric penalty, $\\lambda=1$", "clipe5z": "symmetric penalty, full model, $\\lambda=1$"}
ORDER = list(LABEL)
MAIN = {"clipe5bzl0", "clipe5bzsgl003", "clipe5bzsgl01", "clipe5bzsgl03", "clipe5bzsg", "clipe5bzsgh", "clipe5bzsgG", "clipe5fbzsg"}
SEED = {"20260929": "1", "20260930": "2", "20261001": "3"}


def f(x, nd=1):
    return "--" if x is None else (f"$-${-x:.{nd}f}" if x < 0 else f"{x:.{nd}f}")


rows, arms, ref = [], [], None
for tag, r in sorted(d.items(), key=lambda kv: (ORDER.index(kv[0].rsplit("_s", 1)[0]) if kv[0].rsplit("_s", 1)[0] in ORDER else 99, kv[0])):
    if not isinstance(r, dict) or not r.get("smoothing"):
        continue
    arm, seed = tag.rsplit("_s", 1); sm = r["smoothing"]
    fa = lambda k: sm.get(k, {}).get("fa"); mr = lambda k: sm.get(k, {}).get("miss_rise")
    cdf = r.get("untreated_cdf_video_vs_binary") or {}; dfd = r.get("untreated_dfd_video_vs_binary") or {}; cb = r.get("cdfb") or {}; df40 = (r.get("df40_reenactment_vs_binary") or {}).get("ff") or {}
    nb = sum(1 for k, v in r.get("bars", {}).items() if v and k != "3_as_written"); tot = sum(1 for k in r.get("bars", {}) if k != "3_as_written")
    rows.append((LABEL.get(arm, arm), SEED.get(seed, seed), f(fa("fl06")), f(fa("fl12")), f(fa("bil15")), f(r.get("commercial", {}).get("smoothing90_accused")),
                 f(mr("fl12")), f(cdf.get("arm"), 3), f(dfd.get("arm"), 3), f(cb.get("auc_b"), 3), f(df40.get("arm"), 3), f"{nb}/{tot}"))
    arms.append(arm)
    if seed == "20260929":
        ref = (cdf.get("ref"), dfd.get("ref"), cb.get("main_auc_b"), df40.get("ref"))


def emit(rows_, path):
    L = [r"\begin{tabular}{@{}lcccccccccccc@{}}", r"\toprule",
         r"Model & seed & \multicolumn{3}{c}{smoothed genuine accused (\%)} & S-90 & $\Delta$miss & \multicolumn{2}{c}{untreated video AUC} & Celeb-DF-B & DF40 FR & bars \\",
         r" & & fl 0.06 & fl 0.12 & bil 15 & acc.\ \% & fl 0.12 & CDFv2 & DFD & AUC & ff & passed \\", r"\midrule",
         " & ".join(["forgery head only, no rule", "1", "51.6", "84.5", "35.5", f(REF_S90), "$-$34.0", f(ref[0], 3), f(ref[1], 3), f(ref[2], 3), f(ref[3], 3), "--"]) + r" \\", r"\midrule"]
    L += [" & ".join(row) + r" \\" for row in rows_]
    L += [r"\bottomrule", r"\end{tabular}"]
    (H / path).write_text("\n".join(L) + "\n", encoding="utf-8"); print(path, len(rows_), "rows")


emit([r for r, a in zip(rows, arms) if a in MAIN], "tables/tab_sic.tex")
emit(rows, "tables/tab_sic_full.tex")
