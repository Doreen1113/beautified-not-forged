"""Addendum 70 readout: the browser W model (ru7we_effb4_s20260929) against the pre-declared gate G1-G5, next to the
shipped browser model (ru4e_effb4_s20260929) where the same file holds it. Reads only files the evaluation chain wrote:
  G1  fair_cdfb.json [RU7We-effb4].d_miss_beauty_only            <= +11.0 points
  G2  eval_fairbeauty_pairs.json [tag].originals (called real)    >= 70 %
  G3  ali_scores_<tag>.npz: Smoothing-90 argmax fake <= 2 %; accused at 5 % FPR on the originals <= 15 %
  G4  eval_ru_<tag>.json ffpp.cdf.auc >= 0.8275, ffpp.dfd.auc >= 0.8952, ffpp.FA <= 13.7
  G5  ../cgd_20260927/explain_RU7WE_s20260929.json: restoration (flip_pred of the head's region) >= 80 %
python readout70.py -> readout70.json, readout70.log (stdout)"""
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; TAG = "ru7we_effb4_s20260929"; REF = "ru4e_effb4_s20260929"
GATE = {"G1_miss_rise_max": 11.0, "G2_fairface_real_min": 70.0, "G3_s90_fake_max": 2.0, "G3_s90_accused_max": 15.0,
        "G4_cdf_auc_min": 0.8275, "G4_dfd_auc_min": 0.8952, "G4_ffpp_fa_max": 13.7, "G5_restore_min": 80.0}


def J(p):
    p = Path(p); return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def ali(tag):
    f = HERE / f"ali_scores_{tag}.npz"
    if not f.is_file():
        return None
    z = np.load(f); P, g = z["P"], z["group"]; p = P[:, 1].astype(np.float64); o = g == "orig_0"; m = g == "Smoothing_90"
    t = float(np.nanquantile(p[o], 0.95))
    return {"smoothing90_argmax_fake": round(float((P[m].argmax(1) == 1).mean() * 100), 2), "smoothing90_accused_5fpr": round(float((p[m] > t).mean() * 100), 2),
            "originals_argmax": {c: round(float((P[o].argmax(1) == i).mean() * 100), 2) for i, c in enumerate(["real", "fake", "filter"])}}


def restore(arm, seed=20260929):
    R = J(HERE.parent / "cgd_20260927" / f"explain_{arm}_s{seed}.json")
    if not R:
        return None
    out = {}
    for mech, r in R.items():
        meth = {k: v for k, v in r.items() if isinstance(v, dict) and "flip_pred" in v}
        out[mech] = {"n_detected": r.get("n_detected"), "flip_ceiling_gt": r.get("flip_ceiling_gt"),
                     **{k: {"flip_pred": v.get("flip_pred"), "flip_comp": v.get("flip_comp"), "iou7": v.get("iou7")} for k, v in meth.items()}}
    return out


def main():
    fc = J(HERE.parent / "celebdfb_v2_20260927/fair_cdfb.json") or {}
    fb = J(HERE / "eval_fairbeauty_pairs.json") or {}
    ev = J(HERE / f"eval_ru_{TAG}.json") or {}
    sel = J(HERE / f"select_{TAG}.json")
    res = {"tag": TAG, "selected_epoch": sel and sel["selected_epoch"], "gate": GATE,
           "G1": {k: fc.get(k, {}).get("d_miss_beauty_only") for k in ("RU7We-effb4", "RU4e-effb4")},
           "G1_ci": {k: fc.get(k, {}).get("ci", {}).get("d_miss_beauty_only") for k in ("RU7We-effb4", "RU4e-effb4")},
           "G2": {k: (fb.get(k) or {}).get("originals") for k in (TAG, REF)},
           "G2_filtered_called_fake_5fpr": {k: (fb.get(k) or {}).get("filtered_called_fake_at_5pct_fpr_on_originals") for k in (TAG, REF)},
           "G3": {k: ali(k) for k in (TAG, REF)},
           "G4": {"cdf_auc": (ev.get("ffpp") or {}).get("cdf", {}).get("auc"), "dfd_auc": (ev.get("ffpp") or {}).get("dfd", {}).get("auc"),
                  "ffpp_FA": (ev.get("ffpp") or {}).get("FA"), "indomain": (ev.get("ffpp") or {}).get("indomain"), "real_to_filter": (ev.get("ffpp") or {}).get("real_to_filter")},
           "G5": {k: restore(k) for k in ("RU7WE", "RU4E")}}
    print(json.dumps(res, indent=1))
    v = {}
    g1 = res["G1"]["RU7We-effb4"]; v["G1"] = None if g1 is None else g1 <= GATE["G1_miss_rise_max"]
    g2 = res["G2"][TAG]; g2r = None if not g2 else (g2.get("real") if isinstance(g2, dict) else None)
    v["G2"] = None if g2r is None else g2r >= GATE["G2_fairface_real_min"]
    g3 = res["G3"][TAG]; v["G3"] = None if g3 is None else (g3["smoothing90_argmax_fake"] <= GATE["G3_s90_fake_max"] and g3["smoothing90_accused_5fpr"] <= GATE["G3_s90_accused_max"])
    g4 = res["G4"]; v["G4"] = None if g4["cdf_auc"] is None else (g4["cdf_auc"] >= GATE["G4_cdf_auc_min"] and g4["dfd_auc"] >= GATE["G4_dfd_auc_min"] and g4["ffpp_FA"] <= GATE["G4_ffpp_fa_max"])
    g5 = res["G5"]["RU7WE"]
    if g5:
        heads = [v_ for mn, mech in g5.items() if mn in ("donor", "sd", "sdxl") for k, v_ in mech.items()
                 if k == "evidence" and isinstance(v_, dict) and v_.get("flip_pred") is not None]   # fixed 2026-10-30: the key is "evidence"
        rest = float(np.mean([h["flip_pred"] for h in heads])) * 100 if heads else None
        res["G5_restoration_mean_pct"] = rest; v["G5"] = None if rest is None else rest >= GATE["G5_restore_min"]
    else:
        v["G5"] = None
    res["verdict"] = v; res["PASS"] = all(x is True for x in v.values())
    print("VERDICT", json.dumps(v), "PASS" if res["PASS"] else "FAIL/INCOMPLETE")
    (HERE / "readout70.json").write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
