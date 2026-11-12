"""Prepared demo cases with known answers and precomputed detector verdicts (2026-10-22).
Cases are drawn by a fixed seed from the held-out sources, never chosen by hand, and the page shows the source-level numbers
next to them (MAIN_CLAIMS_20261022.md) so a judge can see they are not cherry-picked.
  A  Alibaba Smoothing-90 pairs (FFHQ original + its commercial skin-smoothed render), genuine only.
  B  Celeb-DF-B: deepfake videos untreated vs beautified, and beautified genuine videos (local exhibition only: Celeb-DF
     forbids redistribution, so these files are NOT copied into the public demo; the page hides them when absent).
Verdict rule for every detector: the same one-rule threshold as the paper (5 % FPR on the untreated genuine faces of that
source). Ours also shows its native three-way decision.
python build_cases.py -> cases/cases.json, cases/*.jpg"""
import json
from pathlib import Path

import cv2
import numpy as np

B = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent; OUT = HERE / "cases"; OUT.mkdir(exist_ok=True)
ALI = B / "results/research/alipair_zeroshot_20260929"; RU = B / "results/research/retouch_unified_20260929"; CDFB = B / "results/research/celebdfb_v2_20260927"
DET = {"effort": "Effort (CVPR 2025)", "fadapter": "Forensics Adapter (CVPR 2025)", "dfdhr": "DFD-HR (2026)", "sbi": "SBI (CVPR 2022)"}
OURS = "clipe5_s20260929"; N_A, N_B, N_BG = 8, 6, 4; rng = np.random.default_rng(20261022)


def save(src, name, size=512):
    im = cv2.imread(str(src)); h, w = im.shape[:2]; s = size / max(h, w)
    im = cv2.resize(im, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA); cv2.imwrite(str(OUT / name), im, [cv2.IMWRITE_JPEG_QUALITY, 92]); return name


def ali_cases():
    S = {d: np.load(ALI / f"published_scores_{d}.npz") for d in DET}; z = np.load(RU / f"ali_scores_{OURS}.npz")
    def table(zz, s):
        g, st = zz["group"], zz["stem"]; return {k: v for k, v in zip(st[g == "orig_0"], s[g == "orig_0"])}, {k: v for k, v in zip(st[g == "Smoothing_90"], s[g == "Smoothing_90"])}
    T = {d: table(S[d], S[d]["s"].astype(float)) for d in DET}; T["ours"] = table(z, z["P"][:, 1].astype(float))
    am = z["P"].argmax(1); dec = table(z, am)
    keys = sorted(set.intersection(*[set(T[d][0]) & set(T[d][1]) for d in T]))
    thr = {d: float(np.quantile([T[d][0][k] for k in keys], 0.95)) for d in T}
    pick = sorted(rng.choice(keys, N_A, replace=False).tolist()); cases = []
    for k in pick:
        b = f"{(int(k) // 1000) * 1000}"; orig = B / "ffhq_originals/Part2" / f"{k}.png"; ren = B / "FFHQ_ali_process/Smoothing_90" / b / f"{k}.png"
        if not (orig.is_file() and ren.is_file()):
            continue
        c = {"id": f"A_{k}", "source": "Alibaba Smoothing-90 (commercial skin smoothing of a genuine FFHQ face)", "truth": "genuine, beautified (skin smoothing)",
             "public": False, "images": {"original": save(orig, f"A_{k}_orig.jpg"), "beautified": save(ren, f"A_{k}_s90.jpg")}, "verdicts": {}}
        for d in T:
            o, r = T[d]; c["verdicts"][d] = {"original": {"score": round(float(o[k]), 3), "called_fake": bool(o[k] > thr[d])},
                                            "beautified": {"score": round(float(r[k]), 3), "called_fake": bool(r[k] > thr[d])}}
        c["verdicts"]["ours"]["original"]["decision"] = ["real", "fake", "filter"][int(dec[0][k])]; c["verdicts"]["ours"]["beautified"]["decision"] = ["real", "fake", "filter"][int(dec[1][k])]
        cases.append(c)
    return cases, thr


def cdfb_cases():
    rows = [l.split("\t") for l in (B / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    path = np.array([r[0] for r in rows]); vid = np.array([r[2] for r in rows]); folder = np.array([r[3] for r in rows]); preset = np.array([r[4] for r in rows])
    S = {d: np.load(CDFB / f"scores_v3/{d}.npz")["p"][:, 1].astype(float) for d in DET}; P = np.load(CDFB / "scores_v3/RU-clipe5.npz")["p"]; S["ours"] = P[:, 1].astype(float)
    thr = {d: float(np.quantile(S[d][folder == "real"], 0.95)) for d in S}; am = P.argmax(1)
    def mid(idx):
        return idx[len(idx) // 2]
    cases = []
    for kind, fo, fb, n, truth in (("deepfake", "synthesis", "synthesis_beautified", N_B, "deepfake (identity swap), then beautified by a phone app"),
                                   ("genuine", "real", "real_beautified", N_BG, "genuine, then beautified by a phone app")):
        vids = sorted(set(vid[folder == fo]) & set(vid[folder == fb])); pick = sorted(rng.choice(vids, n, replace=False).tolist())
        for v in pick:
            i0 = mid(np.where((vid == v) & (folder == fo))[0]); i1 = mid(np.where((vid == v) & (folder == fb))[0])
            c = {"id": f"B_{kind}_{v}", "source": f"Celeb-DF-B ({kind} video" + (f", app preset {preset[i1]}" if preset[i1] and preset[i1] != "none" else "") + ")", "truth": truth, "public": False,
                 "images": {"original": save(path[i0], f"B_{kind}_{v}_orig.jpg"), "beautified": save(path[i1], f"B_{kind}_{v}_beaut.jpg")}, "verdicts": {}}
            for d in S:
                c["verdicts"][d] = {"original": {"score": round(float(S[d][i0]), 3), "called_fake": bool(S[d][i0] > thr[d])},
                                    "beautified": {"score": round(float(S[d][i1]), 3), "called_fake": bool(S[d][i1] > thr[d])}}
            c["verdicts"]["ours"]["original"]["decision"] = ["real", "fake", "filter"][int(am[i0])]; c["verdicts"]["ours"]["beautified"]["decision"] = ["real", "fake", "filter"][int(am[i1])]
            cases.append(c)
    return cases, thr


def main():
    a, ta = ali_cases(); b, tb = cdfb_cases()
    meta = {"detectors": {**DET, "ours": "Ours (CLIP ViT-L/14 LoRA, three-way)"}, "rule": "called fake = score above the threshold that accuses 5 % of the untreated genuine faces of the same source",
            "thresholds": {"alibaba": {k: round(v, 4) for k, v in ta.items()}, "celebdfb": {k: round(v, 4) for k, v in tb.items()}}, "seed": 20261022,
            "source_numbers": "docs/capstone/MAIN_CLAIMS_20261022.md", "cases": a + b}
    (OUT / "cases.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    for c in a + b:
        print(c["id"], {d: (int(v["original"]["called_fake"]), int(v["beautified"]["called_fake"])) for d, v in c["verdicts"].items()}, c["verdicts"]["ours"]["beautified"].get("decision"))


if __name__ == "__main__":
    main()
