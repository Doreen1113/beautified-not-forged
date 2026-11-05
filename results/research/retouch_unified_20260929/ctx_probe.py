"""Addendum 61: test-time context matching. If a detector reads "a face smoother than its context" (Addendum 57), then
smoothing the WHOLE crop of an already face-smoothed image removes the inconsistency for a beautified genuine face, while
a forgery keeps evidence that does not depend on that inconsistency. Rule: forged iff s(x) > t_A AND s(W(x)) > t_W, with
W = whole-crop bilateral at the fl12 interior strength (bdry_probe.render(..., "whole")).
Renders: fl12w = W applied to the fl12 PNG of every smooth38 frame (landmarks from the untreated frame).
python ctx_probe.py prep | score <name> ... | analyse"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE)); B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(B))
OUT = Path(r"N:\2603055\AIGC\smooth_probe_20261016"); FORMS = ["fl12w"]


def prep():
    import cv2
    from bdry_probe import render
    from filters_v2.scale_normalized_filters import get_landmarks
    m = json.loads((HERE / "smooth38_list.json").read_text()); P = {"untreated": m["paths"]["untreated"], "fl12w": []}; ok = []
    (OUT / "fl12w").mkdir(parents=True, exist_ok=True)
    for i, (p, pf) in enumerate(zip(m["paths"]["untreated"], m["paths"]["fl12"])):
        f = OUT / "fl12w" / f"{Path(p).stem}.png"
        if not f.is_file():
            rgb = np.ascontiguousarray(cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB)); lm = get_landmarks(rgb)
            fl = np.ascontiguousarray(cv2.cvtColor(cv2.imread(pf), cv2.COLOR_BGR2RGB))
            out = render(fl, lm, "whole") if lm is not None else fl
            cv2.imwrite(str(f), cv2.cvtColor(out, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_PNG_COMPRESSION, 1])
        ok.append(m["lm_ok"][i]); P["fl12w"].append(str(f))
        if i % 500 == 0:
            print(i, flush=True)
    (HERE / "ctx38_list.json").write_text(json.dumps({"paths": P, "y": m["y"], "video": m["video"], "lm_ok": ok})); print("prep done")


def score(names):
    import smooth_probe38 as S
    base = type(S.HERE)

    class Mapped(base):
        def __truediv__(self, k):
            return base.__truediv__(self, str(k).replace("smooth38", "ctx38"))
    S.HERE = Mapped(str(S.HERE)); S.FORMS = list(FORMS); S.DOSE = []
    for n in names:
        S.score(n)


def analyse():
    import smooth_probe38 as S
    m = json.loads((HERE / "ctx38_list.json").read_text()); y = np.array(m["y"]); ok = np.array(m["lm_ok"]); g0 = ok & (y == 0); f0 = ok & (y == 1)
    names = [n for n in S.PUB + list(S.OURS) if (HERE / f"ctx38_{n}.npz").is_file() and (HERE / f"bdry38_{n}.npz").is_file()]; rows = {}
    for n in names:
        s38 = np.load(HERE / f"smooth38_{n}.npz"); b38 = np.load(HERE / f"bdry38_{n}.npz"); c38 = np.load(HERE / f"ctx38_{n}.npz")
        u = s38["untreated"].astype(float); w = b38["whole"].astype(float); x = s38["fl12"].astype(float); xw = c38["fl12w"].astype(float)
        tA = np.nanquantile(u[g0], 0.95); tW = np.nanquantile(w[g0], 0.95)
        single_fa = float((x[g0] > tA).mean() * 100); single_miss_u = float((u[f0] <= tA).mean() * 100)
        joint = lambda a, b: (a > tA) & (b > tW)
        j_fa = float(joint(x, xw)[g0].mean() * 100); j_miss_fl12 = float((~joint(x, xw))[f0].mean() * 100); j_miss_u = float((~joint(u, w))[f0].mean() * 100)
        # matched-FA comparison on the fl12 frames: single score recalibrated to 5 % FA, joint rule with t_W swept to 5 % FA
        t5 = np.quantile(x[g0], 0.95); recal_miss = float((x[f0] <= t5).mean() * 100)
        cand = np.quantile(xw[g0 & (x > tA)], 0.95) if (g0 & (x > tA)).sum() > 20 else tW   # t_W so that joint FA on fl12 genuine is 5 %
        jm = (x > tA) & (xw > cand); j5_fa = float(jm[g0].mean() * 100); j5_miss = float((~jm)[f0].mean() * 100)
        rows[n] = {"single_fa_fl12": round(single_fa, 1), "joint_fa_fl12": round(j_fa, 1), "joint_miss_fl12": round(j_miss_fl12, 1),
                   "single_miss_untreated": round(single_miss_u, 1), "joint_miss_untreated": round(j_miss_u, 1),
                   "recal_miss_fl12_at5": round(recal_miss, 1), "joint_fa_at_matched": round(j5_fa, 1), "joint_miss_fl12_at_matched": round(j5_miss, 1)}
    face = [n for n in names if n in S.PUB and n not in ("univfd", "npr")]
    p1 = sum(rows[n]["joint_fa_fl12"] < 30 for n in face); p2 = sum(rows[n]["joint_miss_fl12_at_matched"] <= rows[n]["recal_miss_fl12_at5"] - 10 for n in face)
    res = {"rows": rows, "pred1_joint_fa_below_30": f"{p1}/{len(face)}", "pred2_beats_recalibration_by_10": f"{p2}/{len(face)}"}
    (HERE / "ctx38.json").write_text(json.dumps(res, indent=1))
    L = ["# Addendum 61: test-time context matching (forged iff s(x) > t_A and s(W(x)) > t_W; fl12 = face-local smoothing)", "",
         f"Prediction (1) joint FA on fl12 genuine < 30 %: {res['pred1_joint_fa_below_30']} (bar >= 10/15); (2) at matched 5 % FA on fl12 genuine, joint miss beats single-score recalibration by >= 10 points: {res['pred2_beats_recalibration_by_10']} (bar >= 8/15; kill < 5/15)", "",
         "| detector | single FA fl12 | joint FA fl12 | joint miss fl12 | miss untreated single -> joint | recal miss fl12 @5 | joint miss fl12 @matched FA (FA) |", "|---|---|---|---|---|---|---|"]
    for n, r in rows.items():
        L.append(f"| {n} | {r['single_fa_fl12']} | {r['joint_fa_fl12']} | {r['joint_miss_fl12']} | {r['single_miss_untreated']} -> {r['joint_miss_untreated']} | {r['recal_miss_fl12_at5']} | {r['joint_miss_fl12_at_matched']} ({r['joint_fa_at_matched']}) |")
    (HERE / "CTX38.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    {"prep": lambda: prep(), "score": lambda: score(sys.argv[2:]), "analyse": lambda: analyse()}[sys.argv[1]]()
