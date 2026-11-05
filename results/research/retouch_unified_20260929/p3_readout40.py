"""Addendum 40 read-out: P3 (forged-only exposure) against P0 / P1 / P2 of seed 20260929, with the pre-declared reading."""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; ALI = HERE.parent / "alipair_zeroshot_20260929"; DF = HERE.parent / "df40_eval_20261012"
S = "20260929"; ARMS = {"P0": "clipe5fbp0", "P1": "clipe5fbp1", "P2": "clipe5fb", "P3": "clipe5fbp3"}


def above_own(tag):
    z = np.load(HERE / f"ali_scores_{tag}.npz"); p = z["P"][:, 1]; g = z["group"]; st = z["stem"]
    o = {s: v for s, v, gg in zip(st, p, g) if gg == "orig_0"}; r = [(v, o[s]) for s, v, gg in zip(st, p, g) if gg == "Smoothing_90" and s in o]
    from sklearn.metrics import roc_auc_score
    a = np.array(r); return round(float((a[:, 0] > a[:, 1]).mean() * 100), 1), round(float(roc_auc_score(np.r_[np.zeros(len(a)), np.ones(len(a))], np.r_[a[:, 1], a[:, 0]])), 3)


def j(p):
    return json.loads(p.read_text()) if p.is_file() else {}


ex = j(ALI / "exposure_ali.json"); se = j(HERE / "smooth_evasion2.json"); cf = j(HERE / "cdf_filtered.json"); dv = j(HERE / "dfd_v3.json"); d40 = j(DF / "df40_eval.json")
names = {"P0": "P0", "P1": "P1", "P2": "P2", "P3": "P3 forged only"}; out = {}
for k, a in ARMS.items():
    t = f"{a}_s{S}"; r = {}
    e = ex.get(f"{names[k]} s{S}", {}); r["smoothing90_at_5fpr"] = [e.get("smooth90_fake_at_t")] + list(e.get("smooth90_ci", []))
    r["all_renders_at_5fpr"] = [e.get("ret_fake_at_t")] + list(e.get("ci", []))
    if (HERE / f"ali_scores_{t}.npz").is_file():
        r["smoothing90_above_own_original"], r["smoothing90_auroc_render_vs_original"] = above_own(t)
    s = se.get(t, {}); r["fa_smoothed_genuine_bil9_15_21_med5_gblend"] = s.get("fa_smoothed_genuine"); r["miss_rise"] = s.get("miss_rise"); r["auc_both_smoothed"] = s.get("auc_smoothed_both")
    r["cdf_video_auc_untreated"] = cf.get(t, {}).get("video_auc_u"); r["dfd_v3"] = {kk: vv for kk, vv in dv.get(t, {}).items() if "auc" in kk and not isinstance(vv, dict)} if dv.get(t) else None
    r["df40_mean"] = d40.get(t, {}).get("mean"); out[k] = r
d = ex.get(f"P3 forged only minus P0 s{S}", {}); out["P3_minus_P0_smoothing90"] = [d.get("d_smooth90")] + list(d.get("d_smooth90_ci", []))
d = ex.get(f"P3 forged only minus P2 s{S}", {}); out["P3_minus_P2_smoothing90"] = [d.get("d_smooth90")] + list(d.get("d_smooth90_ci", []))
p3, p0 = out["P3"], out["P0"]
try:
    s90 = p3["smoothing90_at_5fpr"][0]; ci = out["P3_minus_P0_smoothing90"]
    fa3, fa0 = p3["fa_smoothed_genuine_bil9_15_21_med5_gblend"], p0["fa_smoothed_genuine_bil9_15_21_med5_gblend"]
    if s90 <= 15:
        reading = "(ii) forged-side views alone remove the accusation; 'exposure sets the sign' is withdrawn"
    elif ci[2] > -5 and fa3[1] >= fa0[1] and fa3[2] >= fa0[2]:
        reading = "(i) sign rule complete: forged-only exposure keeps the accusation"
    else:
        reading = "(iii) partial"
except Exception as exc:   # an input is missing
    reading = f"not evaluable yet: {exc!r}"
out["reading"] = reading
(HERE / "p3_readout40.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))
