"""Review 2026-10-12: re-analysis of existing score files only (no model is run). Outputs review_scores.json / .md here."""
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import roc_auc_score
HERE = Path(__file__).resolve().parent; A = HERE.parent; R = A.parent; RU = R / "retouch_unified_20260929"
SEEDS = ["20260929", "20260930", "20261001"]; ARMS = {"P0": "clipe5fbp0", "P1": "clipe5fbp1", "P2": "clipe5fb"}
OPS = ["Smoothing", "Whitening", "FaceLifting", "EyeEnlarging"]; LV = (30, 60, 90)
out = {}; L = []


def P(*a):
    s = " ".join(str(x) for x in a); print(s); L.append(s)


def ali(tag):
    z = np.load(RU / f"ali_scores_{tag}.npz"); return z["P"][:, 1].astype(np.float64), z["group"], z["stem"]


def ext_thr(tag):
    t = {}
    f = RU / f"cdf_scores_{tag}.npz"
    if f.is_file():
        z = np.load(f); t["cdf_real_q95"] = float(np.quantile(z["P"][z["y"] == 0, 1], 0.95))
    f = RU / f"dfd_v3_scores_{tag}.npz"
    if f.is_file():
        z = np.load(f); t["dfd_real_q95"] = float(np.quantile(z["s"][z["y"] == 0], 0.95))
    return t


def logit(v):
    v = np.clip(v, 1e-7, 1 - 1e-7); return np.log(v / (1 - v))


def block(tag):
    s, g, st = ali(tag); o = g == "orig_0"; so = dict(zip(st[o], s[o])); r = {}
    th = {"fpr1": np.quantile(s[o], 0.99), "fpr5": np.quantile(s[o], 0.95), "fpr10": np.quantile(s[o], 0.90), "0.5": 0.5, **ext_thr(tag)}
    r["thr"] = {k: round(float(v), 4) for k, v in th.items()}
    r["orig_above"] = {k: round(float((s[o] > v).mean() * 100), 2) for k, v in th.items()}
    r["orig_q"] = [round(float(np.quantile(s[o], q)), 4) for q in (0.5, 0.9, 0.95, 0.99)]
    r["by"] = {}
    for op in OPS:
        for lv in LV:
            m = g == f"{op}_{lv}"
            d = {k: round(float((s[m] > v).mean() * 100), 2) for k, v in th.items()}
            d["auroc"] = round(float(roc_auc_score(np.r_[np.zeros(o.sum()), np.ones(m.sum())], np.r_[s[o], s[m]])), 4)
            base = np.array([so[k] for k in st[m]])
            d["paired_up"] = round(float((s[m] > base).mean() * 100), 2)
            d["med_dlogit"] = round(float(np.median(logit(s[m]) - logit(base))), 3)
            r["by"][f"{op}_{lv}"] = d
    return r


P("# 3. Threshold robustness on the unseen service (existing ali_scores)\n")
for arm, t in ARMS.items():
    for sd in SEEDS:
        out[f"{arm}_s{sd}"] = block(f"{t}_s{sd}")
P("## thresholds and originals above them (P(fake))\n| arm seed | orig median/q90/q95/q99 | orig>0.5 % | t(5%FPR) | CDFv2-genuine q95 -> orig above % | DFD-genuine q95 -> orig above % |\n|---|---|---|---|---|---|")
for k, v in out.items():
    P(f"| {k} | {v['orig_q']} | {v['orig_above']['0.5']} | {v['thr']['fpr5']} | {v['thr'].get('cdf_real_q95')} -> {v['orig_above'].get('cdf_real_q95')} | {v['thr'].get('dfd_real_q95')} -> {v['orig_above'].get('dfd_real_q95')} |")
for key, name in (("fpr5", "share above 5%-FPR threshold (service originals)"), ("fpr1", "1% FPR"), ("fpr10", "10% FPR"), ("0.5", "fixed 0.5"), ("cdf_real_q95", "threshold = q95 of untreated Celeb-DF-v2 genuine frames"),
                  ("dfd_real_q95", "threshold = q95 of DFD genuine frames"), ("auroc", "AUROC render vs originals"), ("paired_up", "paired: render scored more fake than its original, %"), ("med_dlogit", "median logit shift render - original")):
    P(f"\n## {name}: seeds 1/2/3\n| group | P0 | P1 | P2 |\n|---|---|---|---|")
    for op in OPS:
        for lv in LV:
            g = f"{op}_{lv}"; P(f"| {g} | " + " | ".join(" / ".join(str(out[f"{a}_s{sd}"]["by"][g].get(key)) for sd in SEEDS) for a in ARMS) + " |")
# ---- other arms: which component carries it
P("\n# 4b. Other existing arms, 5% FPR on service originals\n| tag | S30 | S60 | S90 | all renders | orig>0.5 | AUROC S90 | paired_up S90 | med dlogit S90 |\n|---|---|---|---|---|---|---|---|---|")
oth = {}
for f in sorted(RU.glob("ali_scores_clipe*.npz")):
    tag = f.stem.replace("ali_scores_", ""); b = block(tag); s, g, st = ali(tag); o = g == "orig_0"; t = np.quantile(s[o], 0.95)
    b["all"] = round(float((s[~o] > t).mean() * 100), 2); oth[tag] = b
    P(f"| {tag} | {b['by']['Smoothing_30']['fpr5']} | {b['by']['Smoothing_60']['fpr5']} | {b['by']['Smoothing_90']['fpr5']} | {b['all']} | {b['orig_above']['0.5']} | {b['by']['Smoothing_90']['auroc']} | {b['by']['Smoothing_90']['paired_up']} | {b['by']['Smoothing_90']['med_dlogit']} |")
out["other_arms"] = oth
# ---- vendor val (Tencent / Megvii held-out bases)
P("\n# 3d. Tencent / Megvii validation renders (vendor_val_scores), threshold = q95 of the 816 FFHQ Part7 validation originals\n| arm seed | orig>0.5 | tencent>t | megvii>t | AUROC tencent | AUROC megvii |\n|---|---|---|---|---|---|")
vv = {}
for arm, t in ARMS.items():
    for sd in SEEDS:
        f = RU / f"vendor_val_scores_{t}_s{sd}.npz"
        if not f.is_file():
            continue
        z = np.load(f); s = z["P"][:, 1]; src = z["src"]; o = src == "ffhq_orig"; th = np.quantile(s[o], 0.95); d = {"orig>0.5": round(float((s[o] > 0.5).mean() * 100), 2)}
        for v in ("tencent", "megvii"):
            m = src == v; d[v] = round(float((s[m] > th).mean() * 100), 2); d["auc_" + v] = round(float(roc_auc_score(np.r_[np.zeros(o.sum()), np.ones(m.sum())], np.r_[s[o], s[m]])), 4)
        vv[f"{arm}_s{sd}"] = d; P(f"| {arm} s{sd} | {d['orig>0.5']} | {d['tencent']} | {d['megvii']} | {d['auc_tencent']} | {d['auc_megvii']} |")
out["vendor_val"] = vv
# ---- 2. sensitivity
P("\n# 2. Does P1/P2 pay elsewhere? (existing JSON)\n")
cb = json.loads((R / "celebdfb_v2_20260927/fair_cdfb.json").read_text()); cff = json.loads((RU / "cdf_filteredff.json").read_text()); dff = json.loads((RU / "dfd_filteredff.json").read_text()); d3 = json.loads((RU / "dfd_v3.json").read_text())
rows = [("CDF-B AUC untreated", lambda t: cb[f"RU-{t}"]["auc_untreated"]), ("CDF-B AUC beautified", lambda t: cb[f"RU-{t}"]["auc_beautified"]), ("CDF-B AUC compressed", lambda t: cb[f"RU-{t}"]["auc_compressed"]), ("CDF-B miss untreated %", lambda t: cb[f"RU-{t}"]["miss0"]),
        ("CDF-B miss beautified %", lambda t: cb[f"RU-{t}"]["miss_b"]), ("CDF-B dMISS beauty-only", lambda t: cb[f"RU-{t}"]["d_miss_beauty_only"]), ("CDF-B FA beautified %", lambda t: cb[f"RU-{t}"]["fa_b"]),
        ("CDFv2 frame AUC", lambda t: cff[t]["auc_u"]), ("CDFv2 video AUC", lambda t: cff[t]["video_auc_u"]), ("CDFv2+11 filters AUC_f", lambda t: cff[t]["auc_f"]), ("CDFv2 miss untreated %", lambda t: cff[t]["miss_u"]), ("CDFv2 miss filtered %", lambda t: cff[t]["miss_f"]),
        ("CDFv2 FA untreated %", lambda t: cff[t]["fa_u"]), ("CDFv2 FA filtered %", lambda t: cff[t]["fa_f"]),
        ("DFDv3 frame AUC", lambda t: d3[t]["frame_auc"]), ("DFDv3 video AUC", lambda t: d3[t]["video_auc"]), ("DFD+16 filters AUC_f", lambda t: dff[t]["auc_f"]), ("DFD miss untreated %", lambda t: dff[t]["miss_u"]), ("DFD miss filtered %", lambda t: dff[t]["miss_f"]),
        ("DFD FA untreated %", lambda t: dff[t]["fa_u"]), ("DFD FA filtered %", lambda t: dff[t]["fa_f"]),
        ("FF++ test FA @0.5 %", lambda t: json.loads((RU / f"eval_ru_{t}.json").read_text())["ffpp"]["FA"]), ("FF++ test MISS @0.5 %", lambda t: json.loads((RU / f"eval_ru_{t}.json").read_text())["ffpp"]["MISS"]),
        ("FF++ val AUC, selected epoch", lambda t: max(e["ffpp_val_auc"] for e in json.loads((RU / f"select_{t}.json").read_text())["epochs"])),
        ("selected epoch", lambda t: json.loads((RU / f"select_{t}.json").read_text())["selected_epoch"])]
P("| metric | P0 s1/s2/s3 | P1 | P2 |\n|---|---|---|---|"); sens = {}
for name, fn in rows:
    cells = []
    for a, t in ARMS.items():
        vs = []
        for sd in SEEDS:
            try:
                vs.append(fn(f"{t}_s{sd}"))
            except (KeyError, FileNotFoundError):
                vs.append(None)
        sens[f"{name}|{a}"] = vs; cells.append(" / ".join("--" if v is None else str(v) if isinstance(v, int) else f"{v:.3f}" if abs(v) < 1.5 else f"{v:.1f}" for v in vs))
    P(f"| {name} | " + " | ".join(cells) + " |")
out["sensitivity"] = sens
(HERE / "review_scores.json").write_text(json.dumps(out, indent=1)); (HERE / "review_scores.md").write_text("\n".join(L) + "\n", encoding="utf-8")
