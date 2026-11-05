"""Frame- and video-level AUC of every detector on an extra untreated test set given as a list file (path, label, group id)
with 95 % group-cluster bootstrap intervals and paired differences of our models against Effort / Forensics Adapter.
python extra_set_eval.py score <setname> <listfile> <name>   -> extra_scores_<setname>_<name>.npz
python extra_set_eval.py analyse <setname> <listfile>        -> extra_<setname>.json, EXTRA_<setname>.md
"""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC"); sys.path.insert(0, str(HERE))
from cdf_filtered_eval import OURS, PUB
NB = 1000


def rows(lf):
    r = [l.split("\t") for l in Path(lf).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return [x[0] for x in r], np.array([int(x[1]) for x in r]), np.array([x[2] for x in r])


def score(st, lf, name):
    f = HERE / f"extra_scores_{st}_{name}.npz"
    if f.is_file():
        print(st, name, "cached"); return
    paths, y, v = rows(lf); import torch
    if name in OURS:
        from leak_probe import load; from train_ru3 import to_t2; from PIL import Image
        model, size, norm = load(name); s = np.zeros(len(paths), np.float32)
        with torch.no_grad():
            for i in range(0, len(paths), 64):
                x = torch.stack([to_t2(np.array(Image.open(p).convert("RGB")), size, False, norm) for p in paths[i:i + 64]]).cuda()
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    lo = model(x)[0]
                s[i:i + 64] = torch.softmax(lo.float(), 1)[:, 1].cpu().numpy()
    else:
        if name in ("effort", "fadapter"):
            sys.path.insert(0, str(B / "external_baselines")); import importlib; det = importlib.import_module(f"{name}_score").Detector()
        else:
            sys.path.insert(0, str(B / "results/research/external_baselines_20260905")); import zoo; det = zoo.ZOO[name]()
        s = np.asarray(det.score(paths), np.float32)
    np.savez(f, s=s, y=y, video=v); print(st, name, "done", len(paths), "nan", int(np.isnan(s).sum()), flush=True)


def analyse(st, lf):
    from sklearn.metrics import roc_auc_score
    S = {}
    for n in PUB + list(OURS):
        f = HERE / f"extra_scores_{st}_{n}.npz"
        if f.is_file():
            z = np.load(f); m = ~np.isnan(z["s"]); S[n] = (z["s"][m], z["y"][m], z["video"][m])
    vids = sorted(set.union(*[set(t[2]) for t in S.values()])); rng = np.random.default_rng(1); draws = [rng.choice(len(vids), len(vids), True) for _ in range(NB)]
    def stat(t):
        s, y, v = t; by = defaultdict(list); lab = {}
        for i in range(len(s)): by[v[i]].append(s[i]); lab[v[i]] = y[i]
        ids = [k for k in vids if k in by]
        fa = lambda sel: roc_auc_score(np.concatenate([[lab[k]] * len(by[k]) for k in sel]), np.concatenate([by[k] for k in sel]))
        va = lambda sel: roc_auc_score([lab[k] for k in sel], [np.mean(by[k]) for k in sel]) if len(set(lab[k] for k in sel)) > 1 else float("nan")
        bf, bv = [], []
        for d in draws:
            sel = [vids[j] for j in d if vids[j] in by]; bf.append(fa(sel)); bv.append(va(sel))
        return float(fa(ids)), float(va(ids)), np.array(bf), np.array(bv)
    R = {n: stat(t) for n, t in S.items()}; out = {}
    for n, (fr, vi, bf, bv) in R.items():
        out[n] = {"frame": round(fr, 4), "video": round(vi, 4) if vi == vi else None, "frame_ci": [round(float(np.nanpercentile(bf, q)), 4) for q in (2.5, 97.5)], "video_ci": [round(float(np.nanpercentile(bv, q)), 4) for q in (2.5, 97.5)]}
        if n in OURS:
            out[n]["minus"] = {r: {"frame": [round(float(np.nanpercentile(bf - R[r][2], q)), 4) for q in (2.5, 97.5)], "video": [round(float(np.nanpercentile(bv - R[r][3], q)), 4) for q in (2.5, 97.5)]} for r in ("effort", "fadapter", "sbi") if r in R}
    (HERE / f"extra_{st}.json").write_text(json.dumps(out, indent=1))
    L = [f"# {st}: {len(vids)} groups; frame- and video-level AUC, group-cluster bootstrap", "", "| detector | frame AUC [CI] | video AUC [CI] | frame diff vs Effort / FA / SBI |", "|---|---|---|---|"]
    for n, r in out.items():
        m = r.get("minus", {}); L.append(f"| {OURS.get(n, n)} | {r['frame']:.3f} {r['frame_ci']} | {r['video']} {r['video_ci']} | {m.get('effort', {}).get('frame', '')} / {m.get('fadapter', {}).get('frame', '')} / {m.get('sbi', {}).get('frame', '')} |")
    (HERE / f"EXTRA_{st}.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    {"score": lambda: score(sys.argv[2], sys.argv[3], sys.argv[4]), "analyse": lambda: analyse(sys.argv[2], sys.argv[3])}[sys.argv[1]]()
