r"""Each detector under the preprocessing it was built for (2026-10-08; audit items 6 and 8; PRE_DECLARED Addendum 24).

Scores detectors on the DeepfakeBench crops of Celeb-DF-v2 and DFD (build_dfb_crops.py) and sets them beside the scores on
our crops (already on file: retouch_unified_20260929/cdf_filtered_scores_<name>.npz['untreated'], dfd_v3_scores_<name>.npz).
Reported per dataset and detector: frame- and video-level AUC on both crops with 95 % video-cluster bootstrap intervals,
and the paired difference "ours on our crop minus baseline on its DeepfakeBench crop" (bootstrap over the videos both
frame sets contain; each detector keeps its own frames of a resampled video).

python dfb_crop_eval.py score <set> <name>     -> dfb_scores_<set>_<name>.npz  (one detector per process)
python dfb_crop_eval.py analyse                -> dfb_crop_eval.json, DFB_CROP_EVAL.md
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC"); SP = B / "splits/research/ffpp_benchmark_20260925"; RU = B / "results/research/retouch_unified_20260929"
PUB = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "effort", "fadapter", "gend", "dfdhr", "caddm", "laanetr"]   # trained on DeepfakeBench crops
OURS = ["clipe5b_s20260929", "clipe5awpb_s20260930", "clipe5f_s20260929", "clipe5_s20260929", "clipe5feb_s20260929", "clipe5fb_s20260929", "clipe5fbp0_s20260929", "clipe5fbp1_s20260929", "clipe5fb_s20260930", "clipe5fbp0_s20260930", "clipe5fbp1_s20260930", "clipe5fbp0E_s20260929", "clipe5fbE_s20260929", "clipe5mf_s20260929", "clipe5mfp0_s20260929", "clipe5mf_s20260930", "clipe5fbp0_s20261001", "clipe5fb_s20261001", "clipe5fbp1_s20261001", "clipe5fbp0E_s20260930", "clipe5fbE_s20260930", "clipe5fbEi0_s20260929", "clipe5fbEi_s20260929", "clipe5fbp0Ei_s20260929"]
NB = 1000


def score(st, name):
    f = HERE / f"dfb_scores_{st}_{name}.npz"
    if f.is_file():
        print(st, name, "cached"); return
    r = [l.split("\t") for l in (SP / f"{st}_dfb32.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    paths = [x[0] for x in r]; y = np.array([int(x[1]) for x in r]); v = np.array([x[2] for x in r]); import torch
    if name in PUB:
        if name in ("effort", "fadapter", "gend", "dfdhr", "caddm", "laanetr"):
            sys.path.insert(0, str(B / "external_baselines")); import importlib; det = importlib.import_module(f"{name}_score").Detector()
        else:
            sys.path.insert(0, str(B / "results/research/external_baselines_20260905")); import zoo; det = zoo.ZOO[name]()
        s = np.asarray(det.score(paths), np.float32)
    else:
        sys.path.insert(0, str(RU)); from leak_probe import load; from train_ru3 import to_t2; from PIL import Image
        model, size, norm = load(name); s = np.zeros(len(paths), np.float32)
        with torch.no_grad():
            for i in range(0, len(paths), 64):
                x = torch.stack([to_t2(np.array(Image.open(p).convert("RGB")), size, False, norm) for p in paths[i:i + 64]]).cuda()
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    lo = model(x)[0]
                s[i:i + 64] = torch.softmax(lo.float(), 1)[:, 1].cpu().numpy()
    np.savez(f, s=s, y=y, video=v); print(st, name, "done", len(paths), "frames; nan", int(np.isnan(s).sum()), flush=True)


def ours_crop(st, name):
    """(s, y, video) on our own crop, from the files written by retouch_unified_20260929."""
    if st == "cdf":
        f = RU / f"cdf_filtered_scores_{name}.npz"
        if not f.is_file():
            return None
        z = np.load(f); return z["untreated"], z["y"], z["video"]
    f = RU / f"dfd_v3_scores_{name}.npz"
    if not f.is_file():
        return None
    z = np.load(f); k = "s" if "s" in z else ("p" if "p" in z else z.files[0]); return z[k], z["y"], z["video"]


def analyse():
    from sklearn.metrics import roc_auc_score
    out = {}
    for st in ("cdf", "dfd"):
        S = {}
        for name in PUB + OURS:
            a = ours_crop(st, name); f = HERE / f"dfb_scores_{st}_{name}.npz"; b = None
            if f.is_file():
                z = np.load(f); b = (z["s"], z["y"], z["video"])
            for crop, t in (("ours", a), ("dfb", b)):
                if t is not None:
                    s, y, v = t; m = ~np.isnan(s); S[(name, crop)] = (s[m], y[m], v[m])
        if not S:
            continue
        vids = sorted(set.intersection(*[set(t[2]) for t in S.values()])); rng = np.random.default_rng(1)
        draws = [rng.choice(len(vids), len(vids), True) for _ in range(NB)]

        def stat(t):
            s, y, v = t; by = defaultdict(list); lab = {}
            for i in range(len(s)):
                by[v[i]].append(s[i]); lab[v[i]] = y[i]
            fa = lambda ids: roc_auc_score(np.concatenate([[lab[k]] * len(by[k]) for k in ids]), np.concatenate([by[k] for k in ids]))
            va = lambda ids: roc_auc_score([lab[k] for k in ids], [np.mean(by[k]) for k in ids])
            bf = np.array([fa([vids[j] for j in d]) for d in draws]); bv = np.array([va([vids[j] for j in d]) for d in draws])
            return {"frame": float(fa(vids)), "video": float(va(vids)), "n_frames": int(sum(len(by[k]) for k in vids))}, bf, bv
        R = {}; BT = {}
        for key, t in S.items():
            r, bf, bv = stat(t); BT[key] = (bf, bv)
            R[f"{key[0]}|{key[1]}"] = {**{k: round(v, 4) if isinstance(v, float) else v for k, v in r.items()},
                                         "frame_ci": [round(float(np.percentile(bf, q)), 4) for q in (2.5, 97.5)], "video_ci": [round(float(np.percentile(bv, q)), 4) for q in (2.5, 97.5)]}
        D = {}
        for o in OURS:
            if (o, "ours") not in BT:
                continue
            for p in PUB:
                for crop in ("dfb", "ours"):
                    if (p, crop) in BT:
                        D[f"{o}|ours minus {p}|{crop}"] = {"frame": [round(float(np.percentile(BT[(o, 'ours')][0] - BT[(p, crop)][0], q)), 4) for q in (2.5, 97.5)],
                                                             "video": [round(float(np.percentile(BT[(o, 'ours')][1] - BT[(p, crop)][1], q)), 4) for q in (2.5, 97.5)]}
        out[st] = {"n_videos_common": len(vids), "auc": R, "paired": D}
    (HERE / "dfb_crop_eval.json").write_text(json.dumps(out, indent=1))
    L = ["# Each detector on our crop and on the DeepfakeBench crop (dlib, five-point alignment, scale 1.3, 256 px); videos common to all frame sets", ""]
    for st, r in out.items():
        L += [f"## {st} ({r['n_videos_common']} videos)", "", "| detector | frame AUC, our crop [CI] | frame AUC, DFB crop [CI] | video AUC, our crop | video AUC, DFB crop |", "|---|---|---|---|---|"]
        for name in PUB + OURS:
            a = r["auc"].get(f"{name}|ours"); b = r["auc"].get(f"{name}|dfb")
            if a or b:
                g = lambda x, k: "-" if x is None else f"{x[k]:.3f}" + (f" {x[k + '_ci']}" if k == "frame" else "")
                L.append(f"| {name} | {g(a, 'frame')} | {g(b, 'frame')} | {g(a, 'video')} | {g(b, 'video')} |")
        L += ["", "Paired difference, ours on our crop minus baseline (95 % interval; frame / video):", "", "| ours | baseline | vs baseline on DFB crop | vs baseline on our crop |", "|---|---|---|---|"]
        for o in OURS:
            for p in ("effort", "fadapter", "gend", "dfdhr"):
                a = r["paired"].get(f"{o}|ours minus {p}|dfb"); b = r["paired"].get(f"{o}|ours minus {p}|ours")
                if a or b:
                    g = lambda x: "-" if x is None else f"{x['frame']} / {x['video']}"
                    L.append(f"| {o} | {p} | {g(a)} | {g(b)} |")
        L.append("")
    (HERE / "DFB_CROP_EVAL.md").write_text("\n".join(L), encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    {"score": lambda: score(sys.argv[2], sys.argv[3]), "analyse": analyse}[sys.argv[1]]()
