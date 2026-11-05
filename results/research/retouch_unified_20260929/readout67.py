"""Addendum 67 readout (PRE_DECLARED.md): re-synthesis pseudo-forgeries. Arm A clipe5R25 vs clipe5, arm B clipe5bR25 vs clipe5b
(seed 20260929). Bars R1 / R2 / kill as written; helpers and draws as readout46 (1000 draws, rng 0).
python readout67.py -> readout67.json, READOUT67.md"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE)); R = HERE.parent
import readout46 as R46  # noqa: E402

ARMS = {"A": ("clipe5R25_s20260929", "clipe5_s20260929", "RU-clipe5R25_s20260929", "RU-clipe5"),
        "B": ("clipe5bR25_s20260929", "clipe5b_s20260929", "RU-clipe5bR25_s20260929", "RU-clipe5b")}


def df40_fs(a, b):
    """face-swap mean, same construction as R46.df40 (which returns reenactment)."""
    D = R / "df40_eval_20261012"; sys.path.insert(0, str(D)); import df40_eval as E
    from sklearn.metrics import roc_auc_score
    if not all((D / f"scores_{n}.npz").is_file() for n in (a, b)):
        return None
    r = E.rows(); vid = np.array([f"{x[4]}|{x[3]}|{x[2]}" for x in r]); uv, inv = np.unique(vid, return_inverse=True)
    vdom = np.array([u.split("|")[0] for u in uv]); vmeth = np.array([u.split("|")[1] for u in uv]); Vm = {}
    for n in (a, b):
        s = np.load(D / f"scores_{n}.npz")["s"].astype(np.float64); ok = ~np.isnan(s)
        Vm[n] = np.where(np.bincount(inv[ok], minlength=len(uv)) > 0, np.bincount(inv[ok], s[ok], len(uv)) / np.maximum(np.bincount(inv[ok], minlength=len(uv)), 1), np.nan)
    out = {}
    for d in ("ff", "cdf"):
        real = np.where((vdom == d) & (vmeth == "real"))[0]; vals = {}
        for n in (a, b):
            per = []
            for m in E.FS:
                f = np.where((vdom == d) & (vmeth == m))[0]
                if len(f):
                    s = np.concatenate([Vm[n][real], Vm[n][f]]); t = np.r_[np.zeros(len(real)), np.ones(len(f))]; k = ~np.isnan(s); per.append(roc_auc_score(t[k], s[k]))
            vals[n] = float(np.mean(per))
        out[d] = {"arm": round(vals[a], 4), "ref": round(vals[b], 4), "diff": round(vals[a] - vals[b], 4)}
    return out


def main():
    fc = json.loads((R / "celebdfb_v2_20260927/fair_cdfb.json").read_text()); res = {}
    L = ["# Addendum 67 readout: decoder re-synthesis as a pseudo-forgery (seed 20260929)", ""]
    for k, (t, c, nt, nc) in ARMS.items():
        r = {"tag": t, "comparator": c}
        r["df40_reenactment"] = R46.df40(t, c); r["df40_faceswap"] = df40_fs(t, c)
        a1, a0 = R46.ali(t), R46.ali(c); r["smoothing90"] = {"arm": a1, "ref": a0}
        r["cdfb_auc_beautified"] = {"arm": fc.get(nt, {}).get("auc_beautified"), "ref": fc.get(nc, {}).get("auc_beautified"),
                                    "arm_d_miss_beauty_only": fc.get(nt, {}).get("d_miss_beauty_only"), "ref_d_miss_beauty_only": fc.get(nc, {}).get("d_miss_beauty_only")}
        r["cdfv2_video"] = R46.paired_video(R46.load_cdf, t, c); r["dfd_video"] = R46.paired_video(R46.load_dfd, t, c)
        fr = r["df40_reenactment"]
        if fr:
            r["R1"] = all(fr[d]["diff"] >= 0.10 and fr[d]["ci"][0] > 0 for d in ("ff", "cdf")); r["kill_part"] = fr["cdf"]["diff"] < 0.05
        try:
            r["R2"] = {"s90<=ref+5": a1["smoothing90_accused"] <= a0["smoothing90_accused"] + 5,
                       "cdfb_beaut>=ref-0.02": r["cdfb_auc_beautified"]["arm"] >= r["cdfb_auc_beautified"]["ref"] - 0.02,
                       "cdfv2>=ref-0.01": r["cdfv2_video"]["diff"] >= -0.01, "dfd>=ref-0.01": r["dfd_video"]["diff"] >= -0.01,
                       "df40_fs>=ref-0.02": all(r["df40_faceswap"][d]["diff"] >= -0.02 for d in ("ff", "cdf"))}
        except (TypeError, KeyError) as e:
            r["R2"] = f"incomplete inputs: {e}"
        res[k] = r
        L += [f"## Arm {k}: {t} vs {c}", "", "```", json.dumps(r, indent=1), "```", ""]
    fr = [res[k].get("df40_reenactment") for k in res]
    res["verdict"] = {"R1_any": any(res[k].get("R1") for k in res),
                      "KILL": all(res[k].get("kill_part", False) for k in res) if all(fr) else "incomplete"}
    L += ["Verdict: " + json.dumps(res["verdict"])]
    (HERE / "readout67.json").write_text(json.dumps(res, indent=1)); (HERE / "READOUT67.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    main()
