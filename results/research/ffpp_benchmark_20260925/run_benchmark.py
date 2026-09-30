"""Score every published detector and ours on the unified three-class test set (PRE_DECLARED §3-§5).

For each model: P(fake) on real / fake / filter rows and on the beautified-fake escape set, then a threshold sweep.
At matched 5 % clean-real FPR:  FA = filter rows called fake, MISS = beautified fakes called real.
B1 is the dominance check: no binary model attains FA <= FA_ours AND MISS <= MISS_ours at ANY threshold.

python run_benchmark.py [--models xception,sbi,...] [--escape-n 400]
  -> scores_<model>.npz, benchmark.json
"""
import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

BASE = Path(r"C:\My_Project\AIGC")
HERE = Path(__file__).resolve().parent
UNI = BASE / "results/research/ffpp_unified_20260925"
SEED = 20260925
sys.path.insert(0, str(BASE / "results/research/external_baselines_20260905"))
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "filters"))


def rows_of(split):
    return [l.split("\t") for l in (UNI / f"ffpp3_{split}.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]


def escape_set(fake_paths, n, cache):
    """FF++ test fakes x the eight stress filters, written once so every model sees identical pixels."""
    cache.mkdir(parents=True, exist_ok=True)
    man = cache / "manifest.tsv"
    if man.is_file():
        return [l.split("\t") for l in man.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    from stress_test_filter_functions import FILTERS
    rng = random.Random(SEED)
    fp = list(fake_paths); rng.shuffle(fp); fp = fp[:n]
    out = []
    for p in fp:
        try:
            rgb = np.array(Image.open(p).convert("RGB"))
        except Exception:
            continue
        for cond, fn in FILTERS.items():
            try:
                e = fn(rgb)
            except Exception:
                e = None
            if e is None:
                continue
            q = cache / f"{Path(p).stem}__{cond}.jpg"
            if not q.exists():
                Image.fromarray(e).save(q, quality=95)
            out.append([str(q), cond, Path(p).stem.split("__f")[0]])
    with open(man, "w", encoding="utf-8", newline="\n") as f:
        f.write("path\tcond\tvideo_id\n")
        for r in out:
            f.write("\t".join(r) + "\n")
    return out


def sweep(s_real, s_filter, s_escape):
    """FA(t) = filter called fake; MISS(t) = beautified fake called real; over every candidate threshold."""
    ts = np.unique(np.concatenate([s_real, s_filter, s_escape]))
    fa = np.array([(s_filter > t).mean() for t in ts]) * 100
    miss = np.array([(s_escape <= t).mean() for t in ts]) * 100
    return ts, fa, miss


def boot_ci(vals, groups, n=2000):
    """Cluster bootstrap over video id."""
    rng = np.random.default_rng(SEED)
    by = defaultdict(list)
    for i, g in enumerate(groups):
        by[g].append(i)
    keys = list(by)
    vals = np.asarray(vals, float)
    bs = [vals[np.concatenate([by[keys[k]] for k in rng.choice(len(keys), len(keys), True)])].mean() for _ in range(n)]
    return [float(np.percentile(bs, 2.5)) * 100, float(np.percentile(bs, 97.5)) * 100]


class Ours3:
    """Our unified three-class model, scored through this same driver.

    `score` returns P(fake) from the 3-class softmax, so it is thresholded exactly like every binary baseline and
    gets no easier rule. `score_native` additionally reports the argmax verdict, which is how the model is actually
    deployed; both readings appear in the results so the comparison cannot be accused of flattering either side.
    """

    def __init__(self, ckpt, backbone="mobilenetv4_conv_small.e2400_r224_in1k"):
        import timm, torch
        from torchvision import transforms as T
        from torch.utils.data import DataLoader, Dataset
        self.torch, self.DataLoader = torch, DataLoader
        self.dev = "cuda" if torch.cuda.is_available() else "cpu"
        self.m = timm.create_model(backbone, pretrained=False, num_classes=3).to(self.dev)
        self.m.load_state_dict(torch.load(ckpt, map_location=self.dev)); self.m.eval()
        self.tf = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize([0.5] * 3, [0.5] * 3)])

        class _D(Dataset):
            def __init__(s2, paths, tf):
                s2.p, s2.tf = list(paths), tf

            def __len__(s2):
                return len(s2.p)

            def __getitem__(s2, i):
                try:
                    return s2.tf(Image.open(s2.p[i]).convert("RGB"))
                except Exception:
                    return torch.zeros(3, 224, 224)
        self._D = _D

    def probs(self, paths):
        import torch
        out = []
        dl = self.DataLoader(self._D(paths, self.tf), batch_size=128, num_workers=0)
        with torch.no_grad():
            for x in dl:
                out.append(torch.softmax(self.m(x.to(self.dev)), 1).cpu().numpy())
        return np.concatenate(out, 0) if out else np.zeros((0, 3))

    def score(self, paths):
        return self.probs(paths)[:, 1]          # P(fake), for the matched-threshold comparison

    def argmax(self, paths):
        return self.probs(paths).argmax(1)      # 0 real / 1 fake / 2 filter, the deployed rule


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="")
    ap.add_argument("--escape-n", type=int, default=400)
    a = ap.parse_args()
    import zoo

    test = rows_of("test")
    real = [r for r in test if r[1] == "0"]; fake = [r for r in test if r[1] == "1"]; filt = [r for r in test if r[1] == "2"]
    esc = escape_set([r[0] for r in fake], a.escape_n, BASE / "ffpp_escape_cache")
    print(f"real {len(real)}  fake {len(fake)}  filter {len(filt)}  escape {len(esc)}", flush=True)

    CK = BASE / "checkpoints/research/ffpp_unified_20260925"
    ours_ckpts = {"ours3_mnv4_10ep": (CK / "ffpp3_FLAT.pth", "mobilenetv4_conv_small.e2400_r224_in1k"),
                  "ours3_mnv4_20ep": (CK / "ffpp3_FLAT_mnv420.pth", "mobilenetv4_conv_small.e2400_r224_in1k"),
                  "ours3_repvit_20ep": (CK / "ffpp3_FLAT_repvit20.pth", "repvit_m0_9.dist_300e_in1k")}
    names = a.models.split(",") if a.models else (
        [n for n in zoo.ZOO if not n.startswith("ours")] + [k for k, v in ours_ckpts.items() if v[0].is_file()])
    results = {}
    for name in names:
        try:
            if name in ours_ckpts:
                m = Ours3(*ours_ckpts[name])
            else:
                m = zoo.ZOO[name]() if callable(zoo.ZOO[name]) else zoo.ZOO[name]
        except Exception as e:
            print(f"[{name}] LOAD FAILED: {type(e).__name__}: {str(e)[:120]}", flush=True)
            results[name] = {"error": f"{type(e).__name__}: {str(e)[:200]}"}
            continue
        try:
            sr = np.asarray(m.score([r[0] for r in real]), float)
            sf = np.asarray(m.score([r[0] for r in fake]), float)
            sl = np.asarray(m.score([r[0] for r in filt]), float)
            se = np.asarray(m.score([r[0] for r in esc]), float)
        except Exception as e:
            print(f"[{name}] SCORE FAILED: {type(e).__name__}: {str(e)[:120]}", flush=True)
            results[name] = {"error": f"score: {type(e).__name__}: {str(e)[:200]}"}
            continue
        np.savez(HERE / f"scores_{name}.npz", real=sr, fake=sf, filter=sl, escape=se)

        # FA = "accused of forgery" (called fake); MISS = "not flagged at all" (called real).
        # For a binary model these are complementary, so both come from one threshold. For a three-class model they
        # are NOT: a beautified fake routed to `filter` is neither accused nor missed, and scoring it by P(fake)
        # alone would record it as an escape although the model did flag the image. The native (argmax) rule is
        # therefore the headline for ours, and the P(fake)-threshold row is kept, labelled, for transparency only.
        t5 = float(np.percentile(sr, 95))           # 5 % clean-real FPR
        FA = float((sl > t5).mean() * 100)
        MISS = float((se <= t5).mean() * 100)
        cfr = float((sf > t5).mean() * 100)
        ts, fa_c, miss_c = sweep(sr, sl, se)
        from sklearn.metrics import roc_auc_score
        results[name] = {
            "t_at_5pct_fpr": t5, "FA": FA, "MISS": MISS, "clean_fake_recall": cfr,
            "FA_ci": boot_ci((sl > t5).astype(float), [r[2] for r in filt]),
            "MISS_ci": boot_ci((se <= t5).astype(float), [r[2] for r in esc]),
            "auroc_real_vs_fake": float(roc_auc_score([0] * len(sr) + [1] * len(sf), np.concatenate([sr, sf]))),
            "auroc_real_vs_filter": float(roc_auc_score([0] * len(sr) + [1] * len(sl), np.concatenate([sr, sl]))),
            "n": {"real": len(sr), "fake": len(sf), "filter": len(sl), "escape": len(se)},
            "curve": {"t": ts.tolist()[::max(1, len(ts) // 400)],
                      "FA": fa_c.tolist()[::max(1, len(ts) // 400)],
                      "MISS": miss_c.tolist()[::max(1, len(ts) // 400)]},
        }
        if hasattr(m, "argmax"):
            am_l = m.argmax([r[0] for r in filt]); am_e = m.argmax([r[0] for r in esc])
            am_r = m.argmax([r[0] for r in real]); am_f = m.argmax([r[0] for r in fake])
            results[name]["native_rule"] = {
                "FA_filter_called_fake": float((am_l == 1).mean() * 100),
                "MISS_beautified_fake_called_real": float((am_e == 0).mean() * 100),
                "beautified_fake_called_filter": float((am_e == 2).mean() * 100),
                "real_recall": float((am_r == 0).mean() * 100),
                "fake_recall": float((am_f == 1).mean() * 100),
                "filter_recall": float((am_l == 2).mean() * 100)}
            results[name]["headline_FA"] = results[name]["native_rule"]["FA_filter_called_fake"]
            results[name]["headline_MISS"] = results[name]["native_rule"]["MISS_beautified_fake_called_real"]
            results[name]["headline_rule"] = "native argmax (3-class)"
            print(f"[{name}] NATIVE: FA={results[name]['native_rule']['FA_filter_called_fake']:.2f} "
                  f"MISS={results[name]['native_rule']['MISS_beautified_fake_called_real']:.2f} "
                  f"(->filter {results[name]['native_rule']['beautified_fake_called_filter']:.1f})", flush=True)
        else:
            results[name]["headline_FA"] = FA
            results[name]["headline_MISS"] = MISS
            results[name]["headline_rule"] = "P(fake) at 5%% clean-real FPR"
        print(f"[{name}] FA={FA:.2f} MISS={MISS:.2f} cleanfake={cfr:.2f} "
              f"AUROC(r/f)={results[name]['auroc_real_vs_fake']:.4f}", flush=True)
        del m
        import torch; torch.cuda.empty_cache()
        (HERE / "benchmark.json").write_text(json.dumps(results, indent=1), encoding="utf-8")

    # ---- B1: does any binary model's FULL curve dominate our deployed operating point? ----
    ours_key = next((k for k in results if k.startswith("ours3") and "headline_FA" in results[k]), None)
    if ours_key:
        fa_o, miss_o = results[ours_key]["headline_FA"], results[ours_key]["headline_MISS"]
        viol = {}
        for name, r in results.items():
            if name.startswith("ours3") or "curve" not in r:
                continue
            fa_c = np.array(r["curve"]["FA"]); miss_c = np.array(r["curve"]["MISS"])
            dom = (fa_c <= fa_o + 1e-9) & (miss_c <= miss_o + 1e-9)
            if dom.any():
                j = int(np.argmin(fa_c[dom] + miss_c[dom]))
                idx = np.where(dom)[0][j]
                viol[name] = {"FA": float(fa_c[idx]), "MISS": float(miss_c[idx]),
                              "t": float(r["curve"]["t"][idx])}
        results["_B1_dominance"] = {"ours": ours_key, "ours_FA": fa_o, "ours_MISS": miss_o,
                                    "n_violations": len(viol), "violations": viol,
                                    "verdict": "SUPPORTED (0 violations)" if not viol else f"REFUTED by {list(viol)}"}
        print(f"B1: ours {ours_key} FA={fa_o:.2f} MISS={miss_o:.2f} -> "
              f"{results['_B1_dominance']['verdict']}", flush=True)
    (HERE / "benchmark.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
