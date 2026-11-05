"""Celeb-DF-v2 under held-out colour filters (PRE_DECLARED Addendum 14), one rule for every detector.

Scores the 13 published detectors (loaders exactly as in fairbeauty_baselines.py / score_cdfb.py) and our checkpoints on the
untreated standard frames and on their filtered copies (build_cdf_filtered.py). Published detectors: P(fake) = their score;
ours: softmax P(fake). Per detector: AUC untreated and filtered (genuine vs deepfake), threshold at 5 % FPR on untreated
genuine frames, rise in MISS (deepfakes not called fake) and in FA (genuine called fake), with 95 % video-cluster bootstrap
intervals; video-level AUC (mean of frame scores) for both conditions.

python cdf_filtered_eval.py score <name>      -> cdf_filtered_scores_<name>.npz (one detector per process)
python cdf_filtered_eval.py analyse           -> cdf_filtered.json, CDF_FILTERED.md
"""
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC"); SP = B / "splits/research/ffpp_benchmark_20260925"
PUB = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter", "univfd", "npr", "gend", "dfdhr", "caddm", "laanetr"]
OURS = {"clipe5y_s20260929": "Ours, symmetric smoothing view", "clipe5y_s20260930": "Ours, symmetric smoothing view s2 (Addendum 42)", "clipe5b_s20260930": "binary control s2 (Addendum 42)", "clipe5fbg0oyE_s20260929": "Effort scheme, symmetric smoothing", "clipe5fbg0oyEi_s20260929": "released Effort fine-tuned, symmetric smoothing", "clipe5fbg0oy_s20260929": "P2 symmetric smoothing s1", "clipe5fbg0oy_s20260930": "P2 symmetric smoothing s2", "clipe5fbg0p1o_s20260930": "P1 smoothing only s2", "clipe5fbg0p1o_s20261001": "P1 smoothing only s3", "clipe5fbg0o_s20260929": "P2 smoothing only s1", "clipe5fbg0o_s20260930": "P2 smoothing only s2", "clipe5fbg0p1o_s20260929": "P1 smoothing only s1", "clipe5fbn_s20260929": "P2 no smoothing s1", "clipe5fbn_s20260930": "P2 no smoothing s2", "clipe5fbp1n_s20260929": "P1 no smoothing s1", "clipe4r_s20260929": "Ours (RU4 re-run)", "clipe5_s20260929": "Ours RU5 s1", "clipe5_s20260930": "Ours RU5 s2",
        "clipe5b_s20260929": "binary control", "clipe5f_s20260929": "FF++-only control", "clipe5fg0_s20260929": "FF++-only, no colour grading", "clipe5af_s20260929": "FF++-only + worst-case beautification",
        "clipe5rf_s20260929": "FF++-only + random operator", "clipe5kf_s20260929": "FF++-only + worst-of-4 operator", "clipe8_s20260929": "RU8",
        "clipe5awpf_s20260929": "FF++-only + plausible worst case (R2-1 s1)", "clipe5awpf_s20260930": "FF++-only + plausible worst case (R2-1 s2)",
        "clipe5awpb_s20260929": "binary + plausible worst case (R2-3 s1)", "clipe5awpb_s20260930": "binary + plausible worst case (R2-3 s2)",
        "clipe5awpd_s20260929": "detached heads + plausible worst case (R2-4)",
        "clipe5awptf_s20260929": "FF++-only + plausible worst case, consistency objective (R2-5)", "clipe5awps3f_s20260929": "FF++-only + plausible worst case, 3 steps (R2-2)",
        "clipe5fb_s20260929": "FF++-only, forged head only (D1)", "clipe5feb_s20260929": "FF++-only + part-level forgeries, forged head only (D2)", "clipe5feb_s20260930": "D2 seed 2",
        "clipe5fbp0_s20260929": "FF++-only binary, no beautified views (P0)", "clipe5fbp3_s20260929": "FF++-only binary, beautified forged only (P3, Addendum 40)", "clipe5fbp1_s20260929": "FF++-only binary, beautified genuine only (P1)",
        "clipe5fbp0_s20260930": "P0 seed 2", "clipe5fbp1_s20260930": "P1 seed 2", "clipe5fb_s20260930": "D1 / P2 seed 2", "clipe5fbp0_s20261001": "P0 seed 3", "clipe5fb_s20261001": "P2 seed 3", "clipe5fbp1_s20261001": "P1 seed 3",
        "clipe5fbp0E_s20260929": "Effort tuning, FF++-only binary, no beautified views (E0)", "clipe5fbE_s20260929": "Effort tuning, FF++-only binary, both classes (E2)", "clipe5fbp0E_s20260930": "E0 seed 2", "clipe5fbE_s20260930": "E2 seed 2", "clipe5fbEi0_s20260929": "released Effort, mapped, untuned", "clipe5fbEi_s20260929": "released Effort + 2 epochs, both-class exposure (A2)", "clipe5fbp0Ei_s20260929": "released Effort + 2 epochs, no beautified views (A0)",
        "clipe5mf_s20260929": "FF++-only, map-pooled forged decision (M2)", "clipe5mfp0_s20260929": "FF++-only, map-pooled decision, no beautified views (M0)", "clipe5mf_s20260930": "M2 seed 2"}
OURS.update({"clipe5bzl0_s20260929": "SIC binary, lambda 0 control (Addendum 46 am. 2)", "clipe5bzl03_s20260929": "SIC binary, lambda 0.3 (am. 3)", "clipe5bzl01_s20260929": "SIC binary, lambda 0.1 (am. 3)", "clipe5bzsg_s20260929": "SIC binary, stop-gradient (am. 4)", "clipe5bzsg_s20260930": "SIC binary, stop-gradient s2 (am. 4)", "clipe5fbzsg_s20260929": "FF++-only SIC-sg (am. 4/5)", "clipe5bzsgl03_s20260929": "SIC-sg lambda 0.3 (am. 6)", "clipe5bzsgl01_s20260929": "SIC-sg lambda 0.1 (am. 6)", "clipe5bzsgG_s20260929": "SIC-sg Gaussian ablation (am. 7)", "clipe5bzsgh_s20260929": "SIC-h one-sided (am. 8)", "clipe5bzsgl003_s20260929": "SIC-sg lambda 0.03 (am. 9)", "clipe5bzsgl01_s20260930": "SIC-sg lambda 0.1 s2 (am. 6)", "clipe5bzsgl003_s20260930": "SIC-sg lambda 0.03 s2", "clipe5bzsgh_s20260930": "SIC-h one-sided s2", "clipe5bzsgG_s20260930": "SIC-sg Gaussian ablation s2", "clipe5bzxs_s20260929": "smoothing expert (Add. 48)", "clipe5fbp0F2_s20260929": "P0 F2F+FS only (Add. 49)", "clipe5bzEsg_s20260929": "SIC-sg Effort tuning (Add. 50)", "clipe5z_s20260929": "SIC factorised s1 (Addendum 46)", "clipe5bz_s20260929": "SIC binary s1 (Addendum 46)", "clipe5z_s20260930": "SIC factorised s2 (Addendum 46)", "clipe5bz_s20260930": "SIC binary s2 (Addendum 46)"})   # Addendum 46
# FSRC=dfd switches to the fresh source of Addendum 16 (DFD v3 + sixteen filters); default is Celeb-DF-v2 (Addendum 14)
SRC = os.environ.get("FSRC", "cdf"); LIST = {"cdf": "celebdf_std32v2_filtered.txt", "dfd": "dfd_std32v3_filtered.txt", "dfdff": "dfd_std32v3_filteredff.txt", "cdfff": "celebdf_std32v2_filteredff.txt"}[SRC]
PRE = {"cdf": "cdf_filtered", "dfd": "dfd_filtered", "dfdff": "dfd_filteredff", "cdfff": "cdf_filteredff"}[SRC]; REFS = ["clipe5f_s20260929", "effort", "fadapter"]


def rows():
    r = [l.split("\t") for l in (SP / LIST).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return [x[4] for x in r], [x[0] for x in r], np.array([int(x[1]) for x in r]), np.array([x[2] for x in r]), np.array([x[3] for x in r])


def score(name):
    f = HERE / f"{PRE}_scores_{name}.npz"
    if f.is_file():
        print(name, "cached"); return
    pu, pf, y, v, flt = rows(); import torch
    reuse = None   # a full-frame source shares its untreated frames with the crop-level one: reuse those scores, matched by source path
    base = {"dfdff": ("dfd_filtered", "dfd_std32v3_filtered.txt"), "cdfff": ("cdf_filtered", "celebdf_std32v2_filtered.txt")}.get(SRC)
    g = HERE / f"{base[0]}_scores_{name}.npz" if base else None
    if base and g.is_file():
        old = [l.split("	")[4] for l in (SP / base[1]).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
        m = dict(zip(old, np.load(g)["untreated"])); reuse = np.array([m[q] for q in pu], np.float32)
    if name in OURS:
        sys.path.insert(0, str(HERE)); from leak_probe import load; from train_ru3 import to_t2; from PIL import Image
        from torch.utils.data import DataLoader, Dataset
        model, size, norm = load(name)

        class DS(Dataset):
            def __init__(self, ps): self.ps = ps
            def __len__(self): return len(self.ps)
            def __getitem__(self, i): return to_t2(np.array(Image.open(self.ps[i]).convert("RGB")), size, False, norm), i
        out = []
        for ps in ((pf,) if reuse is not None else (pu, pf)):
            P = np.zeros(len(ps), np.float32)
            with torch.no_grad():
                for x, i in DataLoader(DS(ps), batch_size=64, num_workers=0):
                    with torch.autocast("cuda", dtype=torch.bfloat16):
                        lo = model(x.cuda())[0]
                    P[i.numpy()] = torch.softmax(lo.float(), 1)[:, 1].cpu().numpy()
            out.append(P)
        su, sf = (reuse, out[0]) if reuse is not None else out
    else:
        if name in ("effort", "fadapter", "gend", "dfdhr", "caddm", "laanetr"):
            sys.path.insert(0, str(B / "external_baselines")); import importlib; det = importlib.import_module(f"{name}_score").Detector()
        else:
            sys.path.insert(0, str(B / "results/research/external_baselines_20260905")); import zoo; det = zoo.ZOO[name]()
        s = np.asarray(det.score(([] if reuse is not None else pu) + pf), np.float32); su, sf = (reuse, s) if reuse is not None else (s[:len(pu)], s[len(pu):])
    np.savez(f, untreated=su, filtered=sf, y=y, video=v, filt=flt); print(name, "done", len(pu), "frames; nan", int(np.isnan(su).sum()), int(np.isnan(sf).sum()), flush=True)


def analyse():
    from sklearn.metrics import roc_auc_score
    out = {}; rng = np.random.default_rng(1); refb = {}
    for ref in REFS:   # bootstrap draws are identical for every detector (same seed, same videos), so differences are paired
        f = HERE / f"{PRE}_scores_{ref}.npz"
        if f.is_file():
            z = np.load(f); v0 = z["video"]; vs = sorted(set(v0)); vx = {k: np.where(v0 == k)[0] for k in vs}; r0 = np.random.default_rng(7)
            refb[ref] = [float(roc_auc_score(z["y"][b], z["filtered"][b])) for b in (np.concatenate([vx[vs[j]] for j in r0.choice(len(vs), len(vs), True)]) for _ in range(500))]
    for name in PUB + list(OURS):
        f = HERE / f"{PRE}_scores_{name}.npz"
        if not f.is_file():
            continue
        z = np.load(f); su, sf, y, v = z["untreated"], z["filtered"], z["y"], z["video"]
        vids = sorted(set(v)); vix = {k: np.where(v == k)[0] for k in vids}
        boots = [np.concatenate([vix[vids[j]] for j in rng.choice(len(vids), len(vids), True)]) for _ in range(500)]

        def vauc(s, idx):
            by = defaultdict(list); yy = {}
            for i in idx:
                by[v[i]].append(s[i]); yy[v[i]] = y[i]
            ks = list(by); return float(roc_auc_score([yy[k] for k in ks], [np.mean(by[k]) for k in ks]))

        def st(idx):
            t = np.quantile(su[idx][y[idx] == 0], 0.95); g = y[idx] == 0; k = ~g
            return {"auc_u": float(roc_auc_score(y[idx], su[idx])), "auc_f": float(roc_auc_score(y[idx], sf[idx])),
                    "miss_u": 100 * float((su[idx][k] <= t).mean()), "miss_f": 100 * float((sf[idx][k] <= t).mean()),
                    "fa_u": 100 * float((su[idx][g] > t).mean()), "fa_f": 100 * float((sf[idx][g] > t).mean())}
        a = st(np.arange(len(y))); bs = [st(b) for b in boots]
        r = {k: round(vv, 4 if k.startswith("auc") else 2) for k, vv in a.items()}
        r["d_miss"] = round(a["miss_f"] - a["miss_u"], 2); r["d_fa"] = round(a["fa_f"] - a["fa_u"], 2)
        r["ci"] = {"auc_f": [round(float(np.percentile([x["auc_f"] for x in bs], q)), 4) for q in (2.5, 97.5)],
                   "d_miss": [round(float(np.percentile([x["miss_f"] - x["miss_u"] for x in bs], q)), 2) for q in (2.5, 97.5)],
                   "d_fa": [round(float(np.percentile([x["fa_f"] - x["fa_u"] for x in bs], q)), 2) for q in (2.5, 97.5)]}
        r0 = np.random.default_rng(7); mine = [float(roc_auc_score(y[b], sf[b])) for b in (np.concatenate([vix[vids[j]] for j in r0.choice(len(vids), len(vids), True)]) for _ in range(500))]
        r["auc_f_minus"] = {ref: [round(float(np.percentile(np.array(mine) - np.array(rb), q)), 4) for q in (2.5, 97.5)] for ref, rb in refb.items() if ref != name}
        r["video_auc_u"] = round(vauc(su, np.arange(len(y))), 4); r["video_auc_f"] = round(vauc(sf, np.arange(len(y))), 4)
        out[name] = r; print(name, json.dumps(r), flush=True)
    (HERE / f"{PRE}.json").write_text(json.dumps(out, indent=1))
    L = [({"cdf": "# Celeb-DF-v2 under eleven held-out colour filters", "cdfff": "# Celeb-DF-v2 under eleven held-out colour filters, filter on the full frame before the crop (Addendum 23)"}[SRC] if SRC in ("cdf", "cdfff") else ("# DFD v3 under sixteen fresh filters (Addendum 16), filter on the face crop" if SRC == "dfd" else "# DFD v3 under sixteen fresh filters, filter on the full frame before the crop (Addendum 23)")) + ", one rule for all (score P(fake); threshold 5 % FPR on untreated genuine)", "",
         "| detector | AUC untreated | AUC filtered [CI] | video AUC u -> f | MISS u -> f (rise [CI]) | FA u -> f (rise [CI]) |", "|---|---|---|---|---|---|"]
    for n, r in out.items():
        L.append(f"| {OURS.get(n, n)} | {r['auc_u']:.3f} | {r['auc_f']:.3f} {r['ci']['auc_f']} | {r['video_auc_u']:.3f} -> {r['video_auc_f']:.3f} | "
                 f"{r['miss_u']:.1f} -> {r['miss_f']:.1f} ({r['d_miss']:+.1f} {r['ci']['d_miss']}) | {r['fa_u']:.1f} -> {r['fa_f']:.1f} ({r['d_fa']:+.1f} {r['ci']['d_fa']}) |")
    (HERE / f"{PRE.upper()}.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    {"score": lambda: score(sys.argv[2]), "analyse": analyse}[sys.argv[1]]()
