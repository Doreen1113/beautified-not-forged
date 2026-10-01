"""Train / validation / test accuracy of the two main models (Ours = clipe4, Ours-lite = ru4e) on every data source, with
the preprocessing used for all reported test numbers (eval_ru.run: crop, resize, normalise; no cap).

Sources and partitions (no new data; all lists existed before this script):
  FF++ three-way   train: stratified sample of ffpp3_train.txt (2,000 per class; fakes 500 per method)
                   val:   ffpp3_val.txt (all)            test: ffpp3_test.txt (all)
  Commercial       train: manifest_train.tsv sample (2,000 originals, 2,000 renders, 2,000 cleaned components)
  (Tencent+Megvii) val:   manifest_val.tsv (held-out FFHQ bases of the two services; used for checkpoint selection)
                   test:  Alibaba, an unseen service (scores already computed by eval_ru.py, read from ali_scores_<tag>.npz)
  Part forgeries   train: 2,000 donor + 2,000 SD1.5 items of the training partition
                   test:  held-out donor / SD1.5 / SDXL items (all)
Side check: the training-time validation (ValDS / ValClip) caps the long side of a crop before resizing; eval_ru.run does
not. The vendor-validation originals are scored both ways to see whether this explains 78.7 vs 55.5 % (FINDINGS).

python split_eval.py  -> split_eval.json, split_eval_<tag>.npz
"""
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from sklearn.metrics import f1_score
from torch.utils.data import DataLoader, Dataset

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from train_ru import BASE, UNI, CKPT, read_manifest, remap, cap, crop  # noqa: E402
from train_ru3 import RUNet3, FLOOR, to_t2  # noqa: E402
from eval_ru import run  # noqa: E402

OPS = ["eye", "jaw", "white", "smooth"]; CLS = ["real", "fake", "filter"]; PE = BASE / "results/research/partedit_20260927"
RNG = np.random.default_rng(20260930)


def take(lst, n):
    return [lst[i] for i in sorted(RNG.choice(len(lst), size=min(n, len(lst)), replace=False))]


def ffpp_rows(name):
    r = [l.split("\t") for l in (UNI / name).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return [(remap(x[0]), None, int(x[1]), x[3]) for x in r]


def part_rows(name):
    r = [l.split("\t") for l in (PE / name).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return [(remap(x[0]), None, 1, x[3]) for x in r]


def vendor_rows(rows):
    out = []
    for r in rows:
        if r["src"] not in ("ffhq_orig", "tencent", "megvii", "vendor_single"):
            continue
        if r["src"] == "vendor_single":
            j = int(np.argmax(r["pres"]))
            if r["q"] is None or r["q"][j] < FLOOR[OPS[j]]:   # the cleaned components the models were trained on
                continue
            out.append((r["path"], r["box"], 2, "component"))
        else:
            out.append((r["path"], r["box"], r["cls"], {"ffhq_orig": "original", "tencent": "render", "megvii": "render"}[r["src"]]))
    return out


def build():
    S = {}
    tr = ffpp_rows("ffpp3_train.txt")
    fk = []
    for m in ("Deepfakes", "Face2Face", "FaceSwap", "NeuralTextures"):
        fk += take([x for x in tr if x[3] == m], 500)
    S["ffpp/train"] = take([x for x in tr if x[2] == 0], 2000) + fk + take([x for x in tr if x[2] == 2], 2000)
    S["ffpp/val"] = ffpp_rows("ffpp3_val.txt"); S["ffpp/test"] = ffpp_rows("ffpp3_test.txt")
    vt = vendor_rows(read_manifest(HERE / "manifest_train.tsv"))
    S["vendor/train"] = sum((take([x for x in vt if x[3] == k], 2000) for k in ("original", "render", "component")), [])
    S["vendor/val"] = vendor_rows(read_manifest(HERE / "manifest_val.tsv"))
    S["part/train"] = take(part_rows("manifest_train_donor.tsv"), 2000) + take(part_rows("manifest_train_sd.tsv"), 2000)
    S["part/test"] = sum((part_rows(f"manifest_test_{m}.tsv") for m in ("donor", "sd", "sdxl")), [])
    return S


class CapDS(Dataset):
    """Training-time validation preprocessing: cap(crop(.)) before the resize."""
    def __init__(self, items, size, norm):
        self.items, self.size, self.norm = items, size, norm

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        p, b = self.items[i]
        return to_t2(cap(crop(np.array(Image.open(p).convert("RGB")), b))[0], self.size, False, self.norm), i


@torch.no_grad()
def run_cap(model, items, size):
    P = np.zeros((len(items), 3), np.float32)
    for x, i in DataLoader(CapDS(items, size, model.norm), batch_size=48, num_workers=8):
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lo = model(x.cuda().to(memory_format=torch.channels_last))[0]
        P[i.numpy()] = torch.softmax(lo.float(), 1).cpu().numpy()
    return P


def summarise(am, y, kind):
    cm = np.zeros((3, 3), int)
    for t, p in zip(y, am):
        cm[t, p] += 1
    out = {"n": int(len(y)), "confusion": cm.tolist(), "recall": {CLS[i]: round(100 * cm[i, i] / cm[i].sum(), 2) for i in range(3) if cm[i].sum()}}
    if kind == "ffpp":
        out["macro_f1"] = round(100 * f1_score(y, am, average="macro"), 2)
    return out


def main():
    S = build()
    for k, v in S.items():
        print(k, len(v), {c: sum(1 for x in v if x[2] == i) for i, c in enumerate(CLS)}, flush=True)
    res = {"sizes": {k: len(v) for k, v in S.items()}}
    for name, tag in (("Ours", "clipe4_s20260929"), ("Ours-lite", "ru4e_effb4_s20260929")):
        if name == "Ours":
            from train_ru_clip import load_clip
            model = load_clip(tag, head=True); model.norm = "clip"; size = 224
        else:
            model = RUNet3("effb4", head=True); model.load_state_dict(torch.load(CKPT / f"ru_{tag}.pth", map_location="cpu")); model.norm = "half"; size = 380
        model = model.cuda().eval().to(memory_format=torch.channels_last)
        R = {}; dump = {}
        for k, items in S.items():
            P = run(model, [(p, b) for p, b, _, _ in items], size)[0]; am = P.argmax(1); y = np.array([x[2] for x in items])
            src = np.array([x[3] for x in items]); R[k] = summarise(am, y, k.split("/")[0])
            if k.startswith("vendor") or k.startswith("part"):
                R[k]["by_source"] = {s: {c: round(100 * float((am[src == s] == i).mean()), 2) for i, c in enumerate(CLS)} | {"n": int((src == s).sum())}
                                     for s in sorted(set(src))}
            dump[k.replace("/", "_") + "_P"] = P; dump[k.replace("/", "_") + "_y"] = y
            print(name, k, json.dumps(R[k]), flush=True)
        z = np.load(HERE / f"ali_scores_{tag}.npz"); g = z["group"]; am = z["P"].argmax(1); o = np.array([s.startswith("orig") for s in g])
        R["vendor/test"] = {"n": int(len(g)), "by_source": {"original": {c: round(100 * float((am[o] == i).mean()), 2) for i, c in enumerate(CLS)} | {"n": int(o.sum())},
                                                            "render": {c: round(100 * float((am[~o] == i).mean()), 2) for i, c in enumerate(CLS)} | {"n": int((~o).sum())}}}
        vv = [(p, b) for p, b, _, s in S["vendor/val"] if s == "original"]
        Pc = run_cap(model, vv, size).argmax(1)
        R["side_check_vendor_val_originals"] = {"eval_preprocessing_real": R["vendor/val"]["by_source"]["original"]["real"],
                                                "training_validation_preprocessing_real": round(100 * float((Pc == 0).mean()), 2), "n": len(vv)}
        print(name, "side check", R["side_check_vendor_val_originals"], flush=True)
        res[name] = R; np.savez(HERE / f"split_eval_{tag}.npz", **dump)
        del model; torch.cuda.empty_cache()
    (HERE / "split_eval.json").write_text(json.dumps(res, indent=1)); print("DONE")


if __name__ == "__main__":
    main()
