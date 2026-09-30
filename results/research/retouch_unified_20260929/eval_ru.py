"""RU evaluation (PRE_DECLARED §3-4): Alibaba blind test (routing, RetouchingFFHQ Eq.4 TP/TN/AC, paired rank, quantities vs
pair-measured ground truth), FF++ test / escape / held-out-13, CDFv2 and DFD frame AUC.

python eval_ru.py --arch effb4 [--seed 20260929] [--part ali|ffpp|all]  -> eval_ru_<tag>.json, RESULTS_<tag>.md
"""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader, Dataset

BASE = Path(os.environ.get("AIGC_BASE", r"C:\My_Project\AIGC")); HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from train_ru import RUNet, ARCH, to_t, crop, remap, CKPT  # noqa: E402
from train_ru3 import to_t2  # noqa: E402
UNI = BASE / "results/research/ffpp_unified_20260925"; SP = BASE / "splits/research/ffpp_benchmark_20260925"
OPS = ["eye", "jaw", "white", "smooth"]; ALI_OP = {"EyeEnlarging": 0, "FaceLifting": 1, "Whitening": 2, "Smoothing": 3}
TABLE7 = {"eye": 0.519, "jaw": 0.548, "smooth": 0.861, "white": 0.501}   # RetouchingFFHQ DenseNet121-MAM, Megvii->Alibaba, TP


class DS(Dataset):
    def __init__(self, items, size, norm="half"):
        self.items, self.size, self.norm = items, size, norm

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        p, b = self.items[i]
        return to_t2(crop(np.array(Image.open(p).convert("RGB")), b), self.size, False, self.norm), i


@torch.no_grad()
def run(model, items, size, bs=48):
    P = np.zeros((len(items), 3), np.float32); R = np.zeros((len(items), 4), np.float32); Q = np.zeros((len(items), 4), np.float32)
    for x, i in DataLoader(DS(items, size, getattr(model, "norm", "half")), batch_size=bs, num_workers=8):
        with torch.autocast("cuda", dtype=torch.bfloat16):
            lo, pr, q = model(x.cuda().to(memory_format=torch.channels_last))[:3]
        i = i.numpy(); P[i] = torch.softmax(lo.float(), 1).cpu().numpy(); R[i] = torch.sigmoid(pr.float()).cpu().numpy(); Q[i] = q.float().cpu().numpy()
    return P, R, Q


def eval_ali(model, size):
    boxes = json.loads((HERE / "ffhq_boxes.json").read_text())
    orig = BASE / "ffhq_originals/Part2"; ali = BASE / "FFHQ_ali_process"
    stems = sorted(p.stem for p in orig.glob("*.png") if p.stem in boxes)
    items, grp, stem_of = [], [], []
    for k in stems:
        items.append((str(orig / f"{k}.png"), boxes[k])); grp.append(("orig", 0)); stem_of.append(k)
    for t in ALI_OP:
        for lv in (30, 60, 90):
            for k in stems:
                p = ali / f"{t}_{lv}" / f"{(int(k) // 1000) * 1000}" / f"{k}.png"
                if p.is_file():
                    items.append((str(p), boxes[k])); grp.append((t, lv)); stem_of.append(k)
    P, R, Q = run(model, items, size)
    am = P.argmax(1); g = np.array([f"{a}_{b}" for a, b in grp]); st = np.array(stem_of); o = g == "orig_0"
    pf_orig = dict(zip(st[o], P[o, 2]))
    # measured ground truth quantities from pairs_ali.tsv (path -> q)
    gt = {}
    pf = HERE / "pairs_ali.tsv"
    if pf.is_file():
        for l in pf.read_text(encoding="utf-8").splitlines()[1:]:
            r = l.split("\t")
            if len(r) >= 7:
                gt[r[1]] = [float(r[3]) - 1, 1 - float(r[4]), float(r[5]) / 20, 1 - float(r[6])]
    res = {"n_orig": int(o.sum()), "orig": {c: round(float((am[o] == i).mean() * 100), 2) for i, c in enumerate(["real", "fake", "filter"])},
           "orig_presence_TN_per_op": {OPS[j]: round(float((R[o, j] < 0.5).mean()), 3) for j in range(4)},
           "orig_all_absent": round(float((R[o] < 0.5).all(1).mean()), 3), "by_group": {}, "quantities": {}}
    spec = 100 - res["orig"]["filter"]
    ret = ~o
    def block(m):
        f = float((am[m] == 2).mean() * 100); of = np.array([pf_orig[s] for s in st[m]])
        return {"n": int(m.sum()), "to_real": round(float((am[m] == 0).mean() * 100), 2), "to_fake": round(float((am[m] == 1).mean() * 100), 2),
                "to_filter": round(f, 2), "balanced_acc": round((f + spec) / 2, 2), "paired_rank": round(float(((P[m, 2] > of) + 0.5 * (P[m, 2] == of)).mean() * 100), 2)}
    res["pooled"] = block(ret)
    tp_op, tn_op, ac_op = {}, {}, {}
    for t, j in ALI_OP.items():
        m = np.array([a == t for a, _ in grp])
        pres = R[m] >= 0.5; tp_op[OPS[j]] = round(float(pres[:, j].mean()), 3)
        others = [k for k in range(4) if k != j]; tn_op[OPS[j]] = round(float((~pres[:, others]).all(1).mean()), 3)
        target = np.zeros(4, bool); target[j] = True; ac_op[OPS[j]] = round(float((pres == target).all(1).mean()), 3)
        for lv in (30, 60, 90):
            mm = g == f"{t}_{lv}"; b = block(mm); b["TP"] = round(float((R[mm, j] >= 0.5).mean()), 3); res["by_group"][f"{t}_{lv}"] = b
        # quantities on this op's pairs: predicted q[j] vs measured
        paths = [items[i][0] for i in np.where(m)[0]]; have = [i for i, p in zip(np.where(m)[0], paths) if p in gt]
        if have:
            pred = Q[have, j]; meas = np.array([gt[items[i][0]][j] for i in have])
            rho = spearmanr(pred, meas).correlation
            cross = np.abs(np.delete(Q[have], j, 1)).mean()
            res["quantities"][OPS[j]] = {"n": len(have), "spearman": round(float(rho), 3), "mae": round(float(np.abs(pred - meas).mean()), 4),
                                         "pred_mean": round(float(pred.mean()), 4), "meas_mean": round(float(meas.mean()), 4), "crosstalk_abs_mean": round(float(cross), 4),
                                         "orig_pred_mean": round(float(Q[o, j].mean()), 4)}
    res["eq4"] = {"TP": tp_op, "TN_same_image": tn_op, "AC": ac_op, "table7_TP": TABLE7}
    res["bars"] = {"R1_balanced>=75": res["pooled"]["balanced_acc"] >= 75,
                   "R2_TP>=table7_on_3of4_and_origTN>=0.8": sum(tp_op[k] >= TABLE7[k] for k in OPS) >= 3 and all(v >= 0.8 for v in res["orig_presence_TN_per_op"].values()),
                   "R3_to_fake<=5_pooled_and<=10_each": res["pooled"]["to_fake"] <= 5 and all(b["to_fake"] <= 10 for b in res["by_group"].values()),
                   "R4_spearman>=0.6_all": bool(res["quantities"]) and all(v["spearman"] >= 0.6 for v in res["quantities"].values())}
    np.savez(HERE / f"ali_scores_{model.tag}.npz", P=P, R=R, Q=Q, group=g, stem=st, path=np.array([it[0] for it in items]))
    return res


def rows(p):
    r = [l.split("\t") for l in Path(p).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return [(remap(x[0]), None) for x in r], np.array([int(x[1]) for x in r])


def eval_ffpp(model, size):
    tp, ty = rows(UNI / "ffpp3_test.txt"); P, R, Q = run(model, tp, size); am = P.argmax(1)
    res = {"indomain": {c: round(float((am[ty == i] == i).mean() * 100), 2) for i, c in enumerate(["real", "fake", "filter"])},
           "FA": round(float((am[ty == 2] == 1).mean() * 100), 2), "real_to_filter": round(float((am[ty == 0] == 2).mean() * 100), 2)}
    esc = [(remap(l.split("\t")[0]), None) for l in (BASE / "ffpp_escape_cache/manifest.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    Pe = run(model, esc, size)[0]; res["MISS"] = round(float((Pe.argmax(1) == 0).mean() * 100), 2)
    ho, _ = rows(UNI / "ffpp3_test_heldout_filter.txt"); Ph = run(model, ho, size)[0]; ah = Ph.argmax(1)
    res["heldout13"] = {"filter": round(float((ah == 2).mean() * 100), 2), "fake": round(float((ah == 1).mean() * 100), 2),
                        "paired_excess_pp": round(float((ah == 2).mean() * 100) - res["real_to_filter"], 2)}
    for nm, f in (("cdf", "celebdf_std32v2.txt"), ("dfd", "dfd_std32v2.txt")):
        r = [l.split("\t") for l in (SP / f).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
        items = [(remap(x[0]), None) for x in r]; y = np.array([int(x[1]) for x in r])
        Pc = run(model, items, size)[0]; res[nm] = {"auc": round(float(roc_auc_score(y, Pc[:, 1])), 4), "real_called_fake": round(float((Pc.argmax(1)[y == 0] == 1).mean() * 100), 2)}
        np.savez(HERE / f"{nm}_scores_{model.tag}.npz", P=Pc, y=y, path=np.array([it[0] for it in items]))
    res["bars"] = {"D1_cdf>=0.78": res["cdf"]["auc"] >= 0.78, "D1_dfd>=0.88": res["dfd"]["auc"] >= 0.88,
                   "D2_indomain>=80_each": all(v >= 80 for v in res["indomain"].values()), "D2_heldout_excess>=30": res["heldout13"]["paired_excess_pp"] >= 30}
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--arch", default="effb4"); ap.add_argument("--seed", type=int, default=20260929)
    ap.add_argument("--part", default="all"); ap.add_argument("--arm", default="ru1"); a = ap.parse_args()
    if a.arm in ("clip", "clipe", "clipe4"):
        from train_ru_clip import load_clip
        tag = f"{a.arm}_s{a.seed}"; size = 224; model = load_clip(tag, head=a.arm != "clip"); model.norm = "clip"
    elif a.arm in ("ru3", "ru3e", "ru4e"):
        from train_ru3 import RUNet3
        tag = f"{a.arm}_{a.arch}_s{a.seed}"; size = ARCH[a.arch][1]
        model = RUNet3(a.arch, head=a.arm.endswith("e")); model.load_state_dict(torch.load(CKPT / f"ru_{tag}.pth", map_location="cpu"))
    else:
        tag = (f"{a.arch}_s{a.seed}" if a.arm == "ru1" else f"{a.arm}_{a.arch}_s{a.seed}"); size = ARCH[a.arch][1]
        model = RUNet(a.arch); model.load_state_dict(torch.load(CKPT / f"ru_{tag}.pth", map_location="cpu"))
    model = model.cuda().eval().to(memory_format=torch.channels_last); model.tag = tag
    f = HERE / f"eval_ru_{tag}.json"; res = json.loads(f.read_text()) if f.is_file() else {}
    if a.part in ("ali", "all"):
        res["ali"] = eval_ali(model, size); print(json.dumps(res["ali"], indent=1), flush=True)
    if a.part in ("ffpp", "all"):
        res["ffpp"] = eval_ffpp(model, size); print(json.dumps(res["ffpp"], indent=1), flush=True)
    f.write_text(json.dumps(res, indent=1))
    L = [f"# RU {tag}", ""]
    if "ali" in res:
        A = res["ali"]; L += ["## Alibaba (blind)", f"orig real/fake/filter {A['orig']} | pooled {A['pooled']}", f"Eq.4 {A['eq4']}", f"orig TN per op {A['orig_presence_TN_per_op']}",
                              "quantities " + json.dumps(A["quantities"]), "bars " + json.dumps(A["bars"]), "", "| group | n | ->real | ->fake | ->filter | balanced | rank | TP |", "|---|---|---|---|---|---|---|---|"]
        L += [f"| {k} | {b['n']} | {b['to_real']} | {b['to_fake']} | {b['to_filter']} | {b['balanced_acc']} | {b['paired_rank']} | {b['TP']} |" for k, b in A["by_group"].items()]
    if "ffpp" in res:
        L += ["", "## FF++ / cross-dataset", json.dumps(res["ffpp"])]
    (HERE / f"RESULTS_{tag}.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("DONE")


if __name__ == "__main__":
    main()
