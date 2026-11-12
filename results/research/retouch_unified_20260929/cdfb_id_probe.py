"""Addendum 62: identity evidence under real app presets (Celeb-DF-B) and a reference-conditioned rule. No training.
References: ArcFace buffalo_l mean embedding of 5 frames from up to 4 Celeb-real videos of the claimed identity that are not among
the Celeb-DF-B real videos. Probe score = 1 - cos(frame, reference). Texture scores: celebdfb_v2_20260927/scores_v3/<det>.npz.
python cdfb_id_probe.py embed    -> cdfb_id_emb.npz      (GPU if CUDAExecutionProvider is present)
python cdfb_id_probe.py analyse  -> cdfb_id.json, CDFB_ID.md"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC"); CDF = B / "Celeb-DF-v2"
F = B / "external_data/celebdfb/frames_std32v3"; SC = B / "results/research/celebdfb_v2_20260927/scores_v3"
FOLDERS = ["real", "real_beautified", "real_compressed", "synthesis", "synthesis_beautified", "synthesis_compressed"]
NREF_VID, NREF_FR, NBOOT = 4, 5, 2000
TEX = {"effort": "effort", "fadapter": "fadapter", "gend": "gend", "dfdhr": "dfdhr", "sbi": "sbi", "caddm": "caddm", "xception": "xception",
       "ours": "RU-clipe5", "ours_s2": "RU-clipe5-s2"}


def claimed(video):
    return video.split("_")[0]


def app():
    import onnxruntime as ort
    from insightface.app import FaceAnalysis
    gpu = "CUDAExecutionProvider" in ort.get_available_providers()
    a = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"],
                     providers=["CUDAExecutionProvider", "CPUExecutionProvider"] if gpu else ["CPUExecutionProvider"])
    a.prepare(ctx_id=0 if gpu else -1, det_size=(320, 320)); print("insightface on", "GPU" if gpu else "CPU", flush=True); return a


def embed_img(a, bgr):
    fs = a.get(bgr)
    if not fs:
        return None
    f = max(fs, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1])); e = f.normed_embedding; return e / np.linalg.norm(e)


def frames():
    out = []
    for d in FOLDERS:
        for p in sorted((F / d).iterdir()):
            out.append((d, p.name.split("__f")[0], str(p)))
    return out


def embed():
    fr = frames(); print("frames", len(fr), flush=True); a = app()
    cdfb_real = {v for d, v, _ in fr if d == "real"}
    test = {l.split()[1].strip().split("/")[-1][:-4] for l in (CDF / "List_of_testing_videos.txt").read_text().splitlines() if l.strip()}
    ids = sorted({claimed(v) for _, v, _ in fr}, key=lambda s: int(s[2:])); ref = {}; refvids = {}
    for k in ids:
        cand = [p for p in sorted((CDF / "Celeb-real").glob(f"{k}_*.mp4")) if p.stem not in cdfb_real]
        cand = [p for p in cand if p.stem not in test] + [p for p in cand if p.stem in test]   # non-test first
        vids = cand[:NREF_VID]; es = []
        for p in vids:
            cap = cv2.VideoCapture(str(p)); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            for t in np.linspace(0, n - 1, NREF_FR + 2)[1:-1].astype(int):
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(t)); ok, im = cap.read()
                e = embed_img(a, im) if ok else None
                if e is not None:
                    es.append(e)
            cap.release()
        if es:
            r = np.mean(es, 0); ref[k] = r / np.linalg.norm(r); refvids[k] = [p.stem for p in vids]
        print(k, len(vids), len(es), flush=True)
    E = np.full((len(fr), 512), np.nan, np.float32)
    for j, (d, v, path) in enumerate(fr):
        im = cv2.imread(path); e = embed_img(a, im) if im is not None else None
        if e is not None:
            E[j] = e
        if j % 2000 == 0:
            print(j, flush=True)
    np.savez(HERE / "cdfb_id_emb.npz", folder=np.array([d for d, _, _ in fr]), video=np.array([v for _, v, _ in fr]), path=np.array([p for _, _, p in fr]),
             ref_ids=np.array(list(ref)), ref=np.stack(list(ref.values())), emb=E)
    (HERE / "cdfb_id_refvids.json").write_text(json.dumps(refvids, indent=1)); print("embed done", flush=True)


def boot_ci(stat, vids, n=NBOOT, seed=0):
    """video-cluster bootstrap of a statistic computed from a boolean/float array indexed by frame; stat(idx) -> float"""
    rng = np.random.default_rng(seed); uv = np.unique(vids); byv = {v: np.flatnonzero(vids == v) for v in uv}; out = []
    for _ in range(n):
        pick = rng.choice(uv, len(uv)); idx = np.concatenate([byv[v] for v in pick]); out.append(stat(idx))
    return [float(np.nanpercentile(out, 2.5)), float(np.nanpercentile(out, 97.5))]


def analyse():
    from sklearn.metrics import roc_auc_score
    z = np.load(HERE / "cdfb_id_emb.npz"); fold = z["folder"]; vid = z["video"]; path = z["path"]; E = z["emb"]
    R = dict(zip(z["ref_ids"], z["ref"])); cl = np.array([claimed(v) for v in vid])
    ident = np.array([1 - float(E[j] @ R[cl[j]]) if cl[j] in R and not np.isnan(E[j, 0]) else np.nan for j in range(len(vid))])
    scores = {"identity": ident}
    for name, key in TEX.items():
        f = SC / f"{key}.npz"
        if not f.is_file():
            continue
        q = np.load(f); m = {Path(p).name + "|" + Path(p).parent.name: i for i, p in enumerate(q["paths"].tolist())}
        s = np.full(len(vid), np.nan)
        for j in range(len(vid)):
            k = Path(path[j]).name + "|" + fold[j]
            if k in m:
                s[j] = q["p"][m[k], 1]
        if np.isfinite(s).mean() > 0.95:
            scores[name] = s
        else:
            print("skip", name, "aligned", np.isfinite(s).mean())
    sel = {d: fold == d for d in FOLDERS}
    res = {"n": {d: int(sel[d].sum()) for d in FOLDERS}, "identity_detect_fail_pct": float(np.isnan(ident[sel["real"]]).mean() * 100), "rows": {}}

    def fa(s, mask, t):
        v = s[mask]; v = v[np.isfinite(v)]; return float((v > t).mean() * 100)

    def miss(s, mask, t):
        v = s[mask]; v = v[np.isfinite(v)]; return float((v <= t).mean() * 100)

    def vauc(s, g, f_):
        """video-level AUC: mean frame score per video"""
        a, b = [], []
        for v in np.unique(vid[g]):
            x = s[g & (vid == v)]; x = x[np.isfinite(x)]
            if len(x): a.append(x.mean())
        for v in np.unique(vid[f_]):
            x = s[f_ & (vid == v)]; x = x[np.isfinite(x)]
            if len(x): b.append(x.mean())
        return float(roc_auc_score([0] * len(a) + [1] * len(b), a + b))

    def fusion(a, b):
        """rank-mean of quantiles against untreated genuine (higher = more forged)"""
        ga, gb = np.sort(a[sel["real"] & np.isfinite(a)]), np.sort(b[sel["real"] & np.isfinite(b)])
        qa = np.searchsorted(ga, a) / len(ga); qb = np.searchsorted(gb, b) / len(gb); return (qa + qb) / 2

    def gate(tex, idn):
        """trust identity alone when it says genuine (below the untreated-genuine 95th percentile); otherwise the fusion"""
        t_id = np.nanquantile(idn[sel["real"]], 0.95); fu = fusion(tex, idn); out = fu.copy(); out[idn <= t_id] = np.minimum(fu[idn <= t_id], 0.5); return out

    cands = dict(scores)
    for name in ("effort", "ours", "fadapter", "gend"):
        if name in scores:
            cands[f"fusion_{name}+identity"] = fusion(scores[name], ident); cands[f"gate_{name}+identity"] = gate(scores[name], ident)
    for name, s in cands.items():
        t = np.nanquantile(s[sel["real"]], 0.95); r = {}
        for d in FOLDERS:
            r[("fa_" if d.startswith("real") else "miss_") + d] = (fa if d.startswith("real") else miss)(s, sel[d], t)
        r["d_fa_beauty_only"] = r["fa_real_beautified"] - r["fa_real_compressed"]; r["d_miss_beauty_only"] = r["miss_synthesis_beautified"] - r["miss_synthesis_compressed"]
        both = sel["real_beautified"] | sel["real_compressed"]
        r["ci_d_fa_beauty_only"] = boot_ci(lambda idx: fa(s[idx], sel["real_beautified"][idx], t) - fa(s[idx], sel["real_compressed"][idx], t), vid, seed=1) if True else None
        bothf = sel["synthesis_beautified"] | sel["synthesis_compressed"]
        r["ci_d_miss_beauty_only"] = boot_ci(lambda idx: miss(s[idx], sel["synthesis_beautified"][idx], t) - miss(s[idx], sel["synthesis_compressed"][idx], t), vid, seed=2)
        r["vauc_untreated"] = vauc(s, sel["real"], sel["synthesis"]); r["vauc_beautified"] = vauc(s, sel["real_beautified"], sel["synthesis_beautified"])
        r["vauc_compressed"] = vauc(s, sel["real_compressed"], sel["synthesis_compressed"])
        # recalibration reading: threshold matched to 5 % FA on real_beautified genuine
        t5 = np.nanquantile(s[sel["real_beautified"]], 0.95); r["miss_beautified_at_matched_5fa"] = miss(s, sel["synthesis_beautified"], t5)
        res["rows"][name] = {k: (round(v, 2) if isinstance(v, float) else v) for k, v in r.items()}
    # predictions
    I = res["rows"]["identity"]; tex = [n for n in scores if n != "identity"]
    p1 = I["vauc_beautified"] >= I["vauc_untreated"] - 0.03; kill1 = I["vauc_beautified"] < I["vauc_untreated"] - 0.05
    p2 = I["miss_beautified_at_matched_5fa"] <= 15 and all(res["rows"][n]["miss_beautified_at_matched_5fa"] >= 40 for n in tex)
    p3 = all(f"fusion_{n}+identity" in res["rows"] and res["rows"][f"fusion_{n}+identity"]["d_fa_beauty_only"] <= 10 and res["rows"][f"fusion_{n}+identity"]["d_miss_beauty_only"] <= 5 for n in ("effort", "ours"))
    p4 = I["d_fa_beauty_only"] >= 10
    res["predictions"] = {"1_identity_vauc_drop_le_0.03": bool(p1), "1_kill_drop_gt_0.05": bool(kill1), "2_recal_identity_le15_texture_ge40": bool(p2),
                          "3_fusion_both_pairs_fa_le10_miss_le5": bool(p3), "4_operating_point_shift_ge10": bool(p4)}
    (HERE / "cdfb_id.json").write_text(json.dumps(res, indent=1))
    L = ["# Addendum 62: identity under real app presets (Celeb-DF-B), reference-conditioned rule", "",
         f"frames {res['n']}; identity detect-fail on real {res['identity_detect_fail_pct']:.1f} %", "",
         "Predictions: " + json.dumps(res["predictions"]), "",
         "| score | vAUC untreated / beautified / compressed | FA real / beaut / compr | beauty-only dFA [CI] | miss syn / beaut / compr | beauty-only dMISS [CI] | miss beaut @5% FA on beaut genuine |",
         "|---|---|---|---|---|---|---|"]
    for n, r in res["rows"].items():
        L.append(f"| {n} | {r['vauc_untreated']:.3f} / {r['vauc_beautified']:.3f} / {r['vauc_compressed']:.3f} | {r['fa_real']:.1f} / {r['fa_real_beautified']:.1f} / {r['fa_real_compressed']:.1f} | "
                 f"{r['d_fa_beauty_only']:+.1f} [{r['ci_d_fa_beauty_only'][0]:+.1f}, {r['ci_d_fa_beauty_only'][1]:+.1f}] | {r['miss_synthesis']:.1f} / {r['miss_synthesis_beautified']:.1f} / {r['miss_synthesis_compressed']:.1f} | "
                 f"{r['d_miss_beauty_only']:+.1f} [{r['ci_d_miss_beauty_only'][0]:+.1f}, {r['ci_d_miss_beauty_only'][1]:+.1f}] | {r['miss_beautified_at_matched_5fa']:.1f} |")
    (HERE / "CDFB_ID.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    {"embed": embed, "analyse": analyse}[sys.argv[1]]()
