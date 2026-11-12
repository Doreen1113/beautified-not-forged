"""Addendum 47: beautification-conditional threshold (BCT). Scores are never modified; the decision threshold is raised by a
shift learnt on FF++ validation GENUINE frames as a function of the full model's skin-smoothing estimate b(x).

python bct.py prep                 -> landmarks + renders of the 530 FF++ val genuine frames (7 forms), bct_ffval_list.json
python bct.py cov                  -> b(x) of clipe5_s20260929 on ffval / cdf probe / Alibaba pairs: bct_cov_<set>.npz
python bct.py score <name>         -> detector scores on the ffval renders: bct_ffval_<name>.npz (cdf scores: smooth38_<name>.npz)
python bct.py analyse              -> bct.json, BCT.md
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC")
sys.path.insert(0, str(HERE))
import smooth_probe38 as SP  # noqa: E402  (FORMS, apply, PUB, CLIP4, OURS)

FORMS = SP.FORMS; CONDS = ["untreated"] + FORMS
OUT = Path(r"N:\2603055\AIGC\smooth_probe_ffval_20261019")
COV_TAG = "clipe5_s20260929"
VAL = B / "results/research/ffpp_unified_20260925/ffpp3_val.txt"
ALI = HERE.parent / "alipair_zeroshot_20260929"
DETS = SP.PUB + ["clipe5b_s20260929", "clipe5_s20260929", "clipe5bzsg_s20260929", "clipe5bzsgl01_s20260929"]
NB = 300


def ffval_rows():
    r = [l.split("\t") for l in VAL.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return [x for x in r if x[1] == "0"]


def prep():
    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision
    r = ffval_rows(); lmk = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_buffer=open(B / "face_landmarker.task", "rb").read()), num_faces=1))
    for c in FORMS:
        (OUT / c).mkdir(parents=True, exist_ok=True)
    ok = np.zeros(len(r), bool); paths = {c: [] for c in CONDS}
    for i, x in enumerate(r):
        bgr = cv2.imread(x[0]); rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB); h, w = rgb.shape[:2]
        res = lmk.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
        lm = np.array([[q.x * w, q.y * h] for q in res.face_landmarks[0]], np.float32) if res.face_landmarks else None
        ok[i] = lm is not None; stem = Path(x[0]).stem; paths["untreated"].append(x[0])
        for c in FORMS:
            f = OUT / c / f"{stem}.png"
            if not f.is_file():
                cv2.imwrite(str(f), cv2.cvtColor(SP.apply(rgb, c, lm), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_PNG_COMPRESSION, 1])
            paths[c].append(str(f))
    meta = {"paths": paths, "video": [x[2] for x in r], "lm_ok": ok.tolist()}
    (HERE / "bct_ffval_list.json").write_text(json.dumps(meta)); print("prep done", len(r), "genuine frames; landmarks", int(ok.sum()), flush=True)


def _ours(tag):
    import torch
    from leak_probe import load; from train_ru3 import to_t2; from PIL import Image
    model, size, norm = load(tag)

    def run(paths):
        pf = np.zeros(len(paths), np.float32); ps = np.zeros(len(paths), np.float32); q = np.zeros(len(paths), np.float32)
        with torch.no_grad():
            for i in range(0, len(paths), 32):
                x = torch.stack([to_t2(np.array(Image.open(p).convert("RGB")), size, False, norm) for p in paths[i:i + 32]]).cuda()
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    o = model(x)
                pf[i:i + 32] = torch.softmax(o[0].float(), 1)[:, 1].cpu().numpy()
                ps[i:i + 32] = torch.sigmoid(o[1].float()[:, 3]).cpu().numpy(); q[i:i + 32] = o[2].float()[:, 3].cpu().numpy()
        return pf, ps, q
    return run


def cov():
    """b(x) of the full model on the three sets (and its own P(fake), which is the clipe5 score)."""
    run = _ours(COV_TAG)
    sets = {"ffval": json.loads((HERE / "bct_ffval_list.json").read_text())["paths"],
            "cdf": {c: json.loads((HERE / "smooth38_list.json").read_text())["paths"][c] for c in CONDS}}
    for name, P in sets.items():
        out = {}
        for c in CONDS:
            pf, ps, q = run(P[c]); out[f"pf_{c}"], out[f"ps_{c}"], out[f"q_{c}"] = pf, ps, q
        np.savez(HERE / f"bct_cov_{name}.npz", **out); print("cov", name, "done", flush=True)
    # Alibaba pairs with the same landmark-box crop that eval_ru.py uses for our models (ffhq_boxes.json)
    from train_ru import crop
    from PIL import Image
    boxes = json.loads((HERE / "ffhq_boxes.json").read_text()); orig = B / "ffhq_originals/Part2"; ali = B / "FFHQ_ali_process/Smoothing_90"
    stems = sorted(p.stem for p in orig.glob("*.png") if p.stem in boxes); items, grp, st = [], [], []
    for k in stems:
        pa = ali / f"{(int(k) // 1000) * 1000}" / f"{k}.png"
        if pa.is_file():
            items += [(orig / f"{k}.png", boxes[k]), (pa, boxes[k])]; grp += ["orig_0", "Smoothing_90"]; st += [k, k]
    import torch
    from leak_probe import load; from train_ru3 import to_t2
    model, size, norm = load(COV_TAG); n = len(items)
    pf = np.zeros(n, np.float32); ps = np.zeros(n, np.float32); q = np.zeros(n, np.float32)
    with torch.no_grad():
        for i in range(0, n, 32):
            x = torch.stack([to_t2(crop(np.array(Image.open(p).convert("RGB")), b), size, False, norm) for p, b in items[i:i + 32]]).cuda()
            with torch.autocast("cuda", dtype=torch.bfloat16):
                o = model(x)
            pf[i:i + 32] = torch.softmax(o[0].float(), 1)[:, 1].cpu().numpy(); ps[i:i + 32] = torch.sigmoid(o[1].float()[:, 3]).cpu().numpy(); q[i:i + 32] = o[2].float()[:, 3].cpu().numpy()
    g = np.array(grp); st = np.array(st)
    np.savez(HERE / "bct_cov_ali.npz", pf=pf, ps=ps, q=q, group=g, stem=st); print("cov ali done", n, flush=True)


def score(name):
    f = HERE / f"bct_ffval_{name}.npz"
    if f.is_file():
        print(name, "cached"); return
    P = json.loads((HERE / "bct_ffval_list.json").read_text())["paths"]; out = {}
    if name in SP.PUB:
        if name in ("effort", "fadapter", "gend", "dfdhr", "caddm", "laanetr"):
            sys.path.insert(0, str(B / "external_baselines")); import importlib; det = importlib.import_module(f"{name}_score").Detector()
        else:
            sys.path.insert(0, str(B / "results/research/external_baselines_20260905")); import zoo; det = zoo.ZOO[name]()
        for c in CONDS:
            out[c] = np.asarray(det.score(P[c]), np.float32)
    else:
        run = _ours(name)
        for c in CONDS:
            out[c] = run(P[c])[0]
    np.savez(f, **out); print(name, "done", flush=True)


def _ali_scores(name):
    f = ALI / f"published_scores_{name}.npz"
    if f.is_file():
        z = np.load(f); return z["s"].astype(float), z["group"], z["stem"]
    z = np.load(HERE / f"ali_scores_{name}.npz"); return z["P"][:, 1].astype(float), z["group"], z["stem"]


def analyse():
    cf = np.load(HERE / "bct_cov_ffval.npz"); cc = np.load(HERE / "bct_cov_cdf.npz"); ca = np.load(HERE / "bct_cov_ali.npz")
    meta = json.loads((HERE / "smooth38_list.json").read_text()); y = np.array(meta["y"]); vid = np.array(meta["video"])
    lf = np.array(json.loads((HERE / "bct_ffval_list.json").read_text())["lm_ok"]); lc = np.array(meta["lm_ok"])
    res = {}; rng = np.random.default_rng(0)
    # bins of b on the FF++ validation genuine renders (pooled over conditions; face-local forms need landmarks)
    COV = "ps"   # Amendment 1: presence probability, fixed bins
    b_f = np.concatenate([cf[f"{COV}_{c}"][lf] for c in CONDS]); edges = np.array([0.1, 0.5, 0.9])
    bin_of = lambda b: np.searchsorted(edges, b, side="right")
    for name in DETS:
        ff = HERE / f"bct_ffval_{name}.npz"; fc = HERE / f"smooth38_{name}.npz"
        if not (ff.is_file() and fc.is_file()):
            continue
        sf = np.load(ff); sc = np.load(fc)
        s_f = np.concatenate([sf[c][lf] for c in CONDS]); k_f = bin_of(b_f)
        q95 = np.array([np.nanquantile(s_f[k_f == k], 0.95) if (k_f == k).sum() >= 20 else np.nan for k in range(4)])
        q95 = np.where(np.isnan(q95), np.nanmin(q95), q95); delta = np.maximum.accumulate(q95 - q95[0])
        g0 = (y == 0) & lc; f0 = (y == 1) & lc
        t0 = np.nanquantile(sc["untreated"][g0], 0.95)
        r = {"delta": [round(float(v), 4) for v in delta], "t0": round(float(t0), 4), "fixed": {}, "bct": {}}
        for c in CONDS:
            s = sc[c].astype(float); b = cc[f"{COV}_{c}"]; thr = t0 + delta[bin_of(b)]
            r["fixed"][c] = {"fa": round(float((s[g0] > t0).mean() * 100), 1), "miss": round(float((s[f0] <= t0).mean() * 100), 1)}
            r["bct"][c] = {"fa": round(float((s[g0] > thr[g0]).mean() * 100), 1), "miss": round(float((s[f0] <= thr[f0]).mean() * 100), 1)}
        # commercial Smoothing-90: base threshold on the originals, shift from b of each image
        s_a, g_a, st_a = _ali_scores(name); ok = np.isin(g_a, ["orig_0", "Smoothing_90"]); s_a, g_a, st_a = s_a[ok], g_a[ok], st_a[ok]
        key = {(gg, ss): i for i, (gg, ss) in enumerate(zip(ca["group"], ca["stem"]))}
        idx = np.array([key.get((gg, ss), -1) for gg, ss in zip(g_a, st_a)]); ok2 = idx >= 0; s_a, g_a, idx = s_a[ok2], g_a[ok2], idx[ok2]
        b_a = ca[COV][idx]; o = g_a == "orig_0"; m = g_a == "Smoothing_90"; ta = np.nanquantile(s_a[o], 0.95); thr_a = ta + delta[bin_of(b_a)]
        r["commercial"] = {"fixed_s90": round(float((s_a[m] > ta).mean() * 100), 1), "bct_s90": round(float((s_a[m] > thr_a[m]).mean() * 100), 1),
                           "bct_orig_fa": round(float((s_a[o] > thr_a[o]).mean() * 100), 1), "n_pairs": int(m.sum())}
        res[name] = r; print(name, "fl12 FA", r["fixed"]["fl12"]["fa"], "->", r["bct"]["fl12"]["fa"], "miss", r["fixed"]["fl12"]["miss"], "->", r["bct"]["fl12"]["miss"],
                            "| S90", r["commercial"]["fixed_s90"], "->", r["commercial"]["bct_s90"], flush=True)
    (HERE / "bct.json").write_text(json.dumps({"edges": [round(float(e), 4) for e in edges], "detectors": res}, indent=1))
    L = ["# Addendum 47: beautification-conditional threshold (BCT)", "",
         "Fixed rule: fake iff s > t0 (t0 = 95th pct of untreated genuine, Celeb-DF-v2 probe). BCT: fake iff s > t0 + Delta(bin(b)), Delta learnt on",
         "FF++ validation genuine renders only (b = skin-smoothing presence probability of clipe5_s20260929, bins 0.1 / 0.5 / 0.9; Amendment 1). FA / miss in %, frames with landmarks.", "",
         "| detector | untreated FA fixed->BCT | fl06 FA | fl12 FA | bil15 FA | S-90 accused | fl12 miss | bil15 miss | untreated miss | Delta(bin4) |", "|---|---|---|---|---|---|---|---|---|---|"]
    for n, r in res.items():
        F = lambda c, k: f"{r['fixed'][c][k]} -> {r['bct'][c][k]}"
        L.append(f"| {n} | {F('untreated','fa')} | {F('fl06','fa')} | {F('fl12','fa')} | {F('bil15','fa')} | {r['commercial']['fixed_s90']} -> {r['commercial']['bct_s90']} | {F('fl12','miss')} | {F('bil15','miss')} | {F('untreated','miss')} | {r['delta'][-1]} |")
    (HERE / "BCT.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    {"prep": prep, "cov": cov, "score": lambda: score(sys.argv[2]), "analyse": analyse}[sys.argv[1]]()
