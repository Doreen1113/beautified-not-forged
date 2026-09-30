"""Bars R0, L1-L3 and the SOTA check (PRE_DECLARED §4) for whichever sbiscale arms have a checkpoint.

python eval_cgd_detect.py -> eval_cgd_detect.json, VERDICT_detect.md
"""
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import timm
import torch
from PIL import Image
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

BASE = Path(r"C:\My_Project\AIGC")
HERE = Path(__file__).resolve().parent
SP = BASE / "splits/research/ffpp_benchmark_20260925"
UNI = BASE / "results/research/ffpp_unified_20260925"
BDIR = BASE / "results/research/ffpp_benchmark_20260925"
CK = BASE / "checkpoints/research/cgd_20260927"
import os
SEED_SFX = "_s" + os.environ.get("CGD_SEED", "20260928")   # CGD_SEED=20260929 evaluates the second seed
OUT_SFX = "" if SEED_SFX == "_s20260928" else SEED_SFX
sys.path.insert(0, str(HERE))
from train_cgd import CGDNet  # noqa: E402
MODEL, SIZE = "tf_efficientnet_b4.ap_in1k", 380
BINARY = ["xception", "effnb4", "spsl", "f3net", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter", "univfd", "npr"]
OFFICIAL_SBI = {"cdf": 0.817, "dfd": 0.918}
T = transforms.Compose([transforms.Resize((SIZE, SIZE)), transforms.ToTensor(), transforms.Normalize([0.5] * 3, [0.5] * 3)])


class DS(Dataset):
    def __init__(self, p):
        self.p = p

    def __len__(self):
        return len(self.p)

    def __getitem__(self, i):
        return T(Image.open(self.p[i]).convert("RGB")), i


def probs(m, paths, k):
    out = np.zeros((len(paths), k), np.float32)
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        for x, i in DataLoader(DS(paths), batch_size=96, num_workers=8):
            out[i.numpy()] = torch.softmax(m(x.cuda().to(memory_format=torch.channels_last)).float(), 1).cpu().numpy()
    return out


def rows(p, ncol=3):
    r = [l.split("\t") for l in Path(p).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return [x[0] for x in r], np.array([int(x[1]) for x in r]), [x[2] if len(x) > 2 else "" for x in r]


def boot(y, s, v, n=1000):
    rng = np.random.default_rng(1); by = defaultdict(list)
    for i, g in enumerate(v):
        by[g].append(i)
    k = list(by); r = []
    for _ in range(n):
        idx = np.concatenate([by[k[j]] for j in rng.choice(len(k), len(k), True)])
        if len(set(y[idx])) == 2:
            r.append(roc_auc_score(y[idx], s[idx]))
    return [round(float(np.percentile(r, 2.5)), 4), round(float(np.percentile(r, 97.5)), 4)]


def curve(sr, sl, se):
    ts = np.unique(np.concatenate([sr, sl, se])); ts = ts[::max(1, len(ts) // 3000)]
    return np.array([(sl > t).mean() * 100 for t in ts]), np.array([(se <= t).mean() * 100 for t in ts])


def main():
    cdf, dfd = rows(SP / "celebdf_std32v2.txt"), rows(SP / "dfd_std32v2.txt")
    tp, ty, _ = rows(UNI / "ffpp3_test.txt")
    esc = [l.split("\t")[0] for l in (BASE / "ffpp_escape_cache/manifest.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    ho = rows(UNI / "ffpp3_test_heldout_filter.txt")[0]
    R = {}
    for arm in ("HYBPE", "MASK", "MASKD", "CGD", "CGDD", "CGD-ZERO", "CGD-BLUR", "CGD-NOHOLD"):
        f = CK / f"cgd_{arm}{SEED_SFX}.pth"
        if not f.is_file() or not (HERE / f"meta_{arm}{SEED_SFX}.json").is_file():   # only finished runs
            continue
        k = 3
        net = CGDNet(head=arm != "HYBPE"); net.load_state_dict(torch.load(f, map_location="cpu"))
        net = net.cuda().eval().to(memory_format=torch.channels_last)
        m = lambda x, _n=net: _n(x)[0]
        r = {}
        for nm, (p, y, v) in (("cdf", cdf), ("dfd", dfd)):
            P = probs(m, p, k)
            r[nm] = {"auc": round(float(roc_auc_score(y, P[:, 1])), 4), "ci": boot(y, P[:, 1], v)}
        Pt, Pe, Ph = probs(m, tp, k), probs(m, esc, k), probs(m, ho, k)
        if True:
            am, ae, ah = Pt.argmax(1), Pe.argmax(1), Ph.argmax(1)
            r["indomain"] = {c: round(float((am[ty == i] == i).mean() * 100), 2) for i, c in enumerate(["real", "fake", "filter"])}
            r["FA"] = round(float((am[ty == 2] == 1).mean() * 100), 2)
            r["MISS"] = round(float((ae == 0).mean() * 100), 2)
            rf = float((am[ty == 0] == 2).mean() * 100)
            r["heldout13"] = {"filter": round(float((ah == 2).mean() * 100), 2), "fake": round(float((ah == 1).mean() * 100), 2),
                              "paired_excess_pp": round(float((ah == 2).mean() * 100) - rf, 2)}
        R[arm] = r; print(arm, json.dumps(r), flush=True)
        del m, net; torch.cuda.empty_cache()

    curves = {}
    for b in BINARY:
        z = np.load(BDIR / f"scores_{b}.npz"); curves[b] = curve(z["real"], z["filter"], z["escape"])
    for nm, fp in (("SBI-L", BASE / "results/research/sbiscale_20260926/scores_SBI-L.npz"), ("SBI-F", BASE / "results/research/sbifix_20260927/scores_SBI-F.npz")):
        if fp.is_file():
            z = np.load(fp); curves[nm] = curve(z["real"], z["filter"], z["escape"])
    for arm in list(R):
        if arm in R:
            R[arm]["b1_dominated_by"] = [b for b, (FA, MS) in curves.items()
                                         if ((FA <= R[arm]["FA"]) & (MS <= R[arm]["MISS"])).any()]
            R[arm]["b1_n_detectors"] = len(curves)

    V = ["# CGD detection bars D1-D5 (PRE_DECLARED §5); D5 needs Celeb-DF-B (score_cdfb.py --models CGD ...)", "",
         "| arm | CDFv2 | DFD | in-domain r/f/fl | FA / MISS | B1 dominated by | heldout-13 excess | D1 | D2 | D3 | D4 |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    base = R.get("HYBPE")
    for arm, x in R.items():
        d1 = base is not None and x["cdf"]["auc"] >= base["cdf"]["auc"] - 0.01
        d2 = base is not None and x["dfd"]["auc"] >= base["dfd"]["auc"] - 0.01
        d3 = all(v >= 80 for v in x["indomain"].values()); d4 = not x["b1_dominated_by"]
        x["bars"] = {"D1": d1, "D2": d2, "D3": d3, "D4": d4}
        V.append(f"| {arm} | {x['cdf']['auc']} {x['cdf']['ci']} | {x['dfd']['auc']} {x['dfd']['ci']} | "
                 f"{x['indomain']['real']}/{x['indomain']['fake']}/{x['indomain']['filter']} | {x['FA']} / {x['MISS']} | "
                 f"{x['b1_dominated_by'] or 'none'} (of {x['b1_n_detectors']}) | {x['heldout13']['paired_excess_pp']} | {d1} | {d2} | {d3} | {d4} |")
    (HERE / f"VERDICT_detect{OUT_SFX}.md").write_text("\n".join(V) + "\n", encoding="utf-8")
    json.dump(R, open(HERE / f"eval_cgd_detect{OUT_SFX}.json", "w"), indent=1)
    print("\n".join(V))


if __name__ == "__main__":
    main()
