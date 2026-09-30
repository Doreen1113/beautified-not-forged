"""Published detectors on the Alibaba pairs (PRE_DECLARED_published.md).

python eval_published_ali.py crops      # write shared-box PNG crops once (C:/My_Project/AIGC/alipair_crops)
python eval_published_ali.py score      # score every detector (cached per detector)
python eval_published_ali.py analyse    # -> published_ali.json, PUBLISHED_RESULTS.md
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.metrics import roc_auc_score

B = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent
CROPS = B / "alipair_crops"; OPS = ["EyeEnlarging", "FaceLifting", "Whitening", "Smoothing"]; LV = (30, 60, 90)
DET = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter", "univfd", "npr"]


def items():
    boxes = json.loads((HERE / "boxes.json").read_text()); out = []
    for k in sorted(boxes):
        out.append((B / "ffhq_originals/Part2" / f"{k}.png", k, "orig_0"))
        for t in OPS:
            for lv in LV:
                p = B / "FFHQ_ali_process" / f"{t}_{lv}" / f"{(int(k) // 1000) * 1000}" / f"{k}.png"
                if p.is_file():
                    out.append((p, k, f"{t}_{lv}"))
    return out, boxes


def crops():
    it, boxes = items(); CROPS.mkdir(exist_ok=True); n = 0
    for p, k, g in it:
        q = CROPS / f"{g}__{k}.png"
        if not q.is_file():
            Image.open(p).convert("RGB").crop(tuple(boxes[k])).save(q); n += 1
    print("crops written", n, "total", len(it), flush=True)


def listing():
    it, _ = items()
    return [str(CROPS / f"{g}__{k}.png") for _, k, g in it], np.array([g for _, _, g in it]), np.array([k for _, k, _ in it])


def score():
    sys.path.insert(0, str(B / "results/research/external_baselines_20260905")); import zoo
    import torch
    paths, g, st = listing()
    for d in DET:
        f = HERE / f"published_scores_{d}.npz"
        if f.is_file():
            print(d, "cached", flush=True); continue
        m = zoo.ZOO[d](); s = np.asarray(m.score(paths), np.float32)
        np.savez(f, s=s, group=g, stem=st); print(d, "done", int(np.isnan(s).sum()), "nan", flush=True)
        del m; torch.cuda.empty_cache()


def block(s, g, st):
    o = g == "orig_0"; so = dict(zip(st[o], s[o])); t = float(np.nanquantile(s[o], 0.95)); r = ~o
    res = {"t_5fpr_orig": round(t, 4), "orig_fake_at_0.5": round(float((s[o] > 0.5).mean() * 100), 2),
           "ret_fake_at_0.5": round(float((s[r] > 0.5).mean() * 100), 2), "ret_fake_at_t": round(float((s[r] > t).mean() * 100), 2),
           "auroc_ret_vs_orig": round(float(roc_auc_score(r.astype(int), s)), 4),
           "paired_up": round(float(np.mean([v > so[k] for v, k in zip(s[r], st[r])]) * 100), 2), "by_op": {}}
    for op in OPS:
        for lv in LV:
            m = g == f"{op}_{lv}"
            res["by_op"][f"{op}_{lv}"] = {"fake_at_t": round(float((s[m] > t).mean() * 100), 2), "fake_at_0.5": round(float((s[m] > 0.5).mean() * 100), 2)}
    return res


def analyse():
    out = {}
    for d in DET:
        z = np.load(HERE / f"published_scores_{d}.npz"); out[d] = block(z["s"], z["group"], z["stem"])
    # ours: FF++-only (probs_*.npz, same item order) and RU (ali_scores_*.npz)
    for n in ("SUP-F", "MASK"):
        z = np.load(HERE / f"probs_{n}.npz"); st = np.array([Path(p).stem for p in z["path"]])
        out[f"ours {n}"] = block(z["p"][:, 1], z["group"], st); am = z["p"].argmax(1); r = z["group"] != "orig_0"
        out[f"ours {n}"]["ret_fake_native_argmax"] = round(float((am[r] == 1).mean() * 100), 2)
    RU = B / "results/research/retouch_unified_20260929"
    for tag, lab in (("effb4_s20260929", "ours RU1"), ("ru2_effb4_s20260929", "ours RU2 s1"), ("ru2_effb4_s20260930", "ours RU2 s2"),
                     ("clipe4_s20260929", "ours main"), ("ru4e_effb4_s20260929", "ours lite")):
        z = np.load(RU / f"ali_scores_{tag}.npz"); P, g, st = z["P"], z["group"], z["stem"]
        out[lab] = block(P[:, 1], g, st); r = g != "orig_0"
        out[lab]["ret_fake_native_argmax"] = round(float((P[r].argmax(1) == 1).mean() * 100), 2)
    (HERE / "published_ali.json").write_text(json.dumps(out, indent=1))
    L = ["# Published detectors vs ours on Alibaba commercial retouching (PRE_DECLARED_published.md)", "",
         "| detector | originals->fake @0.5 | retouched->fake @0.5 | retouched->fake @5%FPR-on-originals | smoothing-90 @5%FPR | AUROC ret vs orig | paired: ret scored more fake |",
         "|---|---|---|---|---|---|---|"]
    for k, v in out.items():
        L.append(f"| {k} | {v['orig_fake_at_0.5']} | {v['ret_fake_at_0.5']} | {v['ret_fake_at_t']} | {v['by_op']['Smoothing_90']['fake_at_t']} | "
                 f"{v['auroc_ret_vs_orig']} | {v['paired_up']} |")
    (HERE / "PUBLISHED_RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    {"crops": crops, "score": score, "analyse": analyse}[sys.argv[1]]()
