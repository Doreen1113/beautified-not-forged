"""Addendum 51: is identity evidence untouched by smoothing? (exploratory, zero training, CPU)
Probes: smooth38 frames of Celeb-real / Celeb-synthesis test videos, conditions below (the PNGs every detector read).
Reference per claimed identity: ArcFace (InsightFace buffalo_l) mean embedding of 5 frames from each of up to 4 Celeb-real
videos of that identity outside List_of_testing_videos.txt. Score = 1 - cos(probe, reference).
python id_ref_probe.py embed   -> id_ref_emb.npz
python id_ref_probe.py analyse -> id_ref.json, ID_REF.md"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC"); CDF = B / "Celeb-DF-v2"
CONDS = ["untreated", "bil15", "bil21", "fl06", "fl12"]; NREF_VID, NREF_FR = 4, 5


def claimed(video):
    m = re.match(r"(?:Celeb-real_|Celeb-synthesis_)?(id\d+)", video.split("/")[-1]); return m.group(1) if m else None


def app():
    from insightface.app import FaceAnalysis
    a = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"], providers=["CPUExecutionProvider"])
    a.prepare(ctx_id=-1, det_size=(320, 320)); return a


def embed_img(a, bgr):
    fs = a.get(bgr)
    if not fs:
        return None
    f = max(fs, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])); e = f.normed_embedding; return e / np.linalg.norm(e)


def embed():
    m = json.loads((HERE / "smooth38_list.json").read_text()); vid = m["video"]
    keep = [i for i, v in enumerate(vid) if not v.startswith("YouTube") and claimed(v)]
    print("probes", len(keep), flush=True); a = app()
    test = {l.split()[1].strip() for l in (CDF / "List_of_testing_videos.txt").read_text().splitlines() if l.strip()}
    ids = sorted({claimed(vid[i]) for i in keep}); ref = {}
    for k in ids:
        vids = sorted(p for p in (CDF / "Celeb-real").glob(f"{k}_*.mp4") if f"Celeb-real/{p.name}" not in test)[:NREF_VID]; es = []
        for p in vids:
            cap = cv2.VideoCapture(str(p)); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            for t in np.linspace(0, n - 1, NREF_FR + 2)[1:-1].astype(int):
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(t)); ok, fr = cap.read()
                e = embed_img(a, fr) if ok else None
                if e is not None:
                    es.append(e)
            cap.release()
        if es:
            r = np.mean(es, 0); ref[k] = r / np.linalg.norm(r)
        print(k, len(vids), len(es), flush=True)
    E = {c: np.full((len(keep), 512), np.nan, np.float32) for c in CONDS}
    for c in CONDS:
        for j, i in enumerate(keep):
            img = cv2.imread(m["paths"][c][i]); e = embed_img(a, img) if img is not None else None
            if e is not None:
                E[c][j] = e
            if j % 500 == 0:
                print(c, j, flush=True)
    np.savez(HERE / "id_ref_emb.npz", keep=np.array(keep), ref_ids=np.array(list(ref)), ref=np.stack(list(ref.values())), **E)


def analyse():
    from sklearn.metrics import roc_auc_score
    m = json.loads((HERE / "smooth38_list.json").read_text()); z = np.load(HERE / "id_ref_emb.npz"); keep = z["keep"]
    y = np.array(m["y"])[keep]; vid = np.array(m["video"])[keep]; cl = np.array([claimed(v) for v in vid])
    R = dict(zip(z["ref_ids"], z["ref"])); has = np.array([c in R for c in cl])
    dets = {"clipe5b": "smooth38_clipe5b_s20260929.npz", "effort": "smooth38_effort.npz", "gend": "smooth38_gend.npz", "sbi": "smooth38_sbi.npz"}
    S = {}
    for c in CONDS:
        e = z[c]; S[("identity", c)] = np.array([1 - float(e[j] @ R[cl[j]]) if has[j] and not np.isnan(e[j, 0]) else np.nan for j in range(len(keep))])
        for d, f in dets.items():
            S[(d, c)] = np.load(HERE / f)[c][keep].astype(float)
    ok = has & np.all([~np.isnan(S[("identity", c)]) for c in CONDS], 0) & np.all([~np.isnan(S[(d, c)]) for d in dets for c in CONDS], 0)
    rk = lambda s: np.argsort(np.argsort(s[ok])) / ok.sum()
    for c in CONDS:
        S[("fusion clipe5b+identity", c)] = np.full(len(keep), np.nan); S[("fusion clipe5b+identity", c)][ok] = rk(S[("identity", c)]) + rk(S[("clipe5b", c)])
    tg = cl[ok]; ut = np.unique(tg); rng = np.random.default_rng(0); by = {t: np.where(tg == t)[0] for t in ut}
    BS = [np.concatenate([by[t] for t in rng.choice(ut, len(ut))]) for _ in range(500)]
    res = {"n": int(ok.sum()), "n_genuine": int((y[ok] == 0).sum()), "n_forged": int((y[ok] == 1).sum()), "detect_fail_pct": {c: round(float(np.isnan(z[c][:, 0]).mean() * 100), 2) for c in CONDS}, "auc": {}}
    for name in ["identity"] + list(dets) + ["fusion clipe5b+identity"]:
        res["auc"][name] = {}
        for c in CONDS:
            s = S[(name, c)][ok]; yy = y[ok]; a = roc_auc_score(yy, s)
            d0 = S[(name, "untreated")][ok]; bs = []
            for ii in BS:
                if len(np.unique(yy[ii])) == 2:
                    bs.append(roc_auc_score(yy[ii], s[ii]) - roc_auc_score(yy[ii], d0[ii]))
            res["auc"][name][c] = {"auc": round(float(a), 4), "drop_vs_untreated_ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]}
    res["op5"] = {}; res["median_dist"] = {}
    yy = y[ok]
    for name in ["identity"] + list(dets) + ["fusion clipe5b+identity"]:
        t = np.quantile(S[(name, "untreated")][ok][yy == 0], 0.95); res["op5"][name] = {}
        for c in CONDS:
            s = S[(name, c)][ok]; res["op5"][name][c] = {"fa": round(float((s[yy == 0] > t).mean() * 100), 1), "miss": round(float((s[yy == 1] <= t).mean() * 100), 1)}
    for c in CONDS:
        s = S[("identity", c)][ok]; res["median_dist"][c] = {"genuine": round(float(np.median(s[yy == 0])), 4), "forged": round(float(np.median(s[yy == 1])), 4)}
    (HERE / "id_ref.json").write_text(json.dumps(res, indent=1))
    L = [f"# Addendum 51: identity evidence under smoothing (Celeb-DF-v2 test, Celeb-real vs Celeb-synthesis, n {res['n']}: {res['n_genuine']} genuine / {res['n_forged']} forged)", "",
         f"face detection failure %: {res['detect_fail_pct']}", "", "AUC per condition; brackets = 95% CI of (AUC under condition - AUC untreated), bootstrap over claimed identities.", "",
         "| score | " + " | ".join(CONDS) + " |", "|---" * (len(CONDS) + 1) + "|"]
    for name, r in res["auc"].items():
        L.append(f"| {name} | " + " | ".join(f"{r[c]['auc']} {r[c]['drop_vs_untreated_ci'] if c != 'untreated' else ''}" for c in CONDS) + " |")
    L += ["", "False alarm / miss at the untreated 5% FPR threshold (held fixed):", "", "| score | " + " | ".join(CONDS) + " |", "|---" * (len(CONDS) + 1) + "|"]
    for name, r in res["op5"].items():
        L.append(f"| {name} | " + " | ".join(f"{r[c]['fa']} / {r[c]['miss']}" for c in CONDS) + " |")
    L += ["", "Median identity distance (genuine / forged): " + json.dumps(res["median_dist"])]
    (HERE / "ID_REF.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    {"embed": embed, "analyse": analyse}[sys.argv[1]]()
