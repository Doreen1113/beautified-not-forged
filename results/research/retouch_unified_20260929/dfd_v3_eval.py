"""DFD re-scored on the rebuilt frame list dfd_std32v3 (332 videos, 10,404 frames; see ffpp_benchmark_20260925/
build_dfd_standard_v3.py). One rule for all: score P(fake); frame AUC and video AUC (mean of frame scores) with 95 %
video-cluster bootstrap intervals, and paired intervals of ours minus each published detector on the same frames.
python dfd_v3_eval.py score <name> | analyse  -> dfd_v3_scores_<name>.npz, dfd_v3.json, DFD_V3.md"""
import json, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC"); SP = B / "splits/research/ffpp_benchmark_20260925"
sys.path.insert(0, str(HERE)); from cdf_filtered_eval import PUB, OURS

def rows():
    r = [l.split("\t") for l in (SP / "dfd_std32v3.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return [x[0] for x in r], np.array([int(x[1]) for x in r]), np.array([x[2] for x in r])

def score(name):
    f = HERE / f"dfd_v3_scores_{name}.npz"
    if f.is_file(): print(name, "cached"); return
    ps, y, v = rows(); import torch
    if name in OURS:
        from leak_probe import load; from train_ru3 import to_t2; from PIL import Image; from torch.utils.data import DataLoader, Dataset
        model, size, norm = load(name)
        class DS(Dataset):
            def __len__(self): return len(ps)
            def __getitem__(self, i): return to_t2(np.array(Image.open(ps[i]).convert("RGB")), size, False, norm), i
        s = np.zeros(len(ps), np.float32)
        with torch.no_grad():
            for x, i in DataLoader(DS(), batch_size=64, num_workers=0):
                with torch.autocast("cuda", dtype=torch.bfloat16): lo = model(x.cuda())[0]
                s[i.numpy()] = torch.softmax(lo.float(), 1)[:, 1].cpu().numpy()
    else:
        if name in ("effort", "fadapter", "gend", "dfdhr", "caddm", "laanetr"):
            sys.path.insert(0, str(B / "external_baselines")); import importlib; det = importlib.import_module(f"{name}_score").Detector()
        else:
            sys.path.insert(0, str(B / "results/research/external_baselines_20260905")); import zoo; det = zoo.ZOO[name]()
        s = np.asarray(det.score(ps), np.float32)
    np.savez(f, s=s, y=y, video=v); print(name, "done", len(ps), "nan", int(np.isnan(s).sum()), flush=True)

def analyse():
    from sklearn.metrics import roc_auc_score
    S = {n: np.load(HERE / f"dfd_v3_scores_{n}.npz") for n in PUB + list(OURS) if (HERE / f"dfd_v3_scores_{n}.npz").is_file()}
    y = next(iter(S.values()))["y"]; v = next(iter(S.values()))["video"]; vids = sorted(set(v)); vix = {k: np.where(v == k)[0] for k in vids}
    rng = np.random.default_rng(1); boots = [rng.choice(len(vids), len(vids), True) for _ in range(1000)]
    def frame(s, idx): return float(roc_auc_score(y[idx], s[idx]))
    def video(s, pick):
        yy = [y[vix[vids[j]]][0] for j in pick]; ss = [float(np.mean(s[vix[vids[j]]])) for j in pick]; return float(roc_auc_score(yy, ss))
    full = np.arange(len(y)); allv = list(range(len(vids))); out = {}
    for n, z in S.items():
        s = z["s"]; bf = [frame(s, np.concatenate([vix[vids[j]] for j in b])) for b in boots]; bv = [video(s, b) for b in boots]
        out[n] = {"frame_auc": round(frame(s, full), 4), "frame_ci": [round(float(np.percentile(bf, q)), 4) for q in (2.5, 97.5)],
                  "video_auc": round(video(s, allv), 4), "video_ci": [round(float(np.percentile(bv, q)), 4) for q in (2.5, 97.5)], "_bf": bf, "_bv": bv}
    for n in OURS:
        if n not in out: continue
        out[n]["minus"] = {}
        for ref in ("sbi", "effort", "fadapter"):
            if ref in out:
                df = np.array(out[n]["_bf"]) - np.array(out[ref]["_bf"]); dv = np.array(out[n]["_bv"]) - np.array(out[ref]["_bv"])
                out[n]["minus"][ref] = {"frame": [round(float(np.percentile(df, q)), 4) for q in (2.5, 97.5)], "video": [round(float(np.percentile(dv, q)), 4) for q in (2.5, 97.5)]}
    for r in out.values(): r.pop("_bf"); r.pop("_bv")
    (HERE / "dfd_v3.json").write_text(json.dumps(out, indent=1))
    L = ["# DFD, rebuilt list dfd_std32v3 (332 videos, 10,404 frames), one rule for all", "", "| detector | frame AUC [CI] | video AUC [CI] | paired video diff vs SBI / Effort / FA |", "|---|---|---|---|"]
    for n, r in out.items():
        m = r.get("minus", {}); L.append(f"| {OURS.get(n, n)} | {r['frame_auc']:.3f} {r['frame_ci']} | {r['video_auc']:.3f} {r['video_ci']} | {m.get('sbi', {}).get('video', '')} / {m.get('effort', {}).get('video', '')} / {m.get('fadapter', {}).get('video', '')} |")
    (HERE / "DFD_V3.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))

if __name__ == "__main__":
    {"score": lambda: score(sys.argv[2]), "analyse": analyse}[sys.argv[1]]()
