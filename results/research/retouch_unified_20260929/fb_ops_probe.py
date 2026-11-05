"""Addendum 55: operation head under combined (AR) beautification, FairBeauty controlled pairs.
python fb_ops_probe.py measure            -> fb_pairs_measured.tsv
python fb_ops_probe.py score <tag> ...    -> fb_ops_<tag>.npz
python fb_ops_probe.py analyse            -> fb_ops.json, FB_OPS.md"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
D = Path(r"C:\My_Project\AIGC\external_data\fairbeauty_pairs")
IDS = [l.split("\t")[0] for l in (D / "pairs.tsv").read_text(encoding="utf-8").splitlines()[1:]]
FMAP = {0: "Pretty", 1: "hary beauty", 2: "Shiny foxy", 3: "Caramel Macchiato", 4: "Cute baby face", 5: "Baby_cute_face", 6: "big city life",
        7: "Just Baby", 8: "Pretty", 9: "hary beauty", 10: "Shiny foxy"}; HELD = {"Baby_cute_face", "big city life", "Just Baby"}
OPS = ["eye", "jaw", "white", "smooth"]
# presence rule = half of the Alibaba level-30 median effect (pairs_ali.tsv); strict = the full level-30 median
THR = {"eye": ("eye_ratio", ">=", 1.006), "jaw": ("jaw_ratio", "<=", 0.993), "white": ("dL_skin", ">=", 0.90), "smooth": ("hf_ratio", "<=", 0.946)}
THR30 = {"eye": ("eye_ratio", ">=", 1.012), "jaw": ("jaw_ratio", "<=", 0.986), "white": ("dL_skin", ">=", 1.80), "smooth": ("hf_ratio", "<=", 0.893)}
COL = {"eye_ratio": 0, "jaw_ratio": 1, "dL_skin": 2, "hf_ratio": 3}


def measure():
    import cv2
    import measure_pairs as M
    rows = ["id\teye_ratio\tjaw_ratio\tdL_skin\thf_ratio"]
    for k, i in enumerate(IDS):
        o = cv2.imread(str(D / "orig" / f"{i}.png"))[..., ::-1]; r = cv2.imread(str(D / "filt" / f"{i}.png"))[..., ::-1]
        o, r = np.ascontiguousarray(o), np.ascontiguousarray(r); lo, lr = M.get_landmarks(o), M.get_landmarks(r)
        if lo is None or lr is None:
            rows.append(f"{i}\tnan\tnan\tnan\tnan"); continue
        jo, eo = M.geo(lo); jr, er = M.geo(lr)

        def hullstats(img, lm):   # each image with its own landmarks: the pairs are not pixel-aligned
            m = M.hull_mask(lm, *img.shape[:2]); L = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
            return float(L[m].mean()), float(np.abs(L - cv2.GaussianBlur(L, (0, 0), 3))[m].mean())
        Lo, ho = hullstats(o, lo); Lr, hr = hullstats(r, lr)
        rows.append(f"{i}\t{er / eo:.5f}\t{jr / jo:.5f}\t{Lr - Lo:.3f}\t{hr / max(ho, 1e-6):.5f}")
        if k % 500 == 0:
            print(k, len(IDS), flush=True)
    (HERE / "fb_pairs_measured.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")


class DS:
    def __init__(self, sub, size, norm):
        self.sub, self.size, self.norm = sub, size, norm

    def __len__(self):
        return len(IDS)

    def __getitem__(self, i):
        from PIL import Image
        from train_ru3 import to_t2
        return to_t2(np.array(Image.open(D / self.sub / f"{IDS[i]}.png").convert("RGB")), self.size, False, self.norm), i


def score(tags):
    import torch
    from torch.utils.data import DataLoader
    from leak_probe import load

    for tag in tags:
        model, size, norm = load(tag); out = {}
        for sub in ("orig", "filt"):
            P = np.zeros((len(IDS), 3), np.float32); R = np.zeros((len(IDS), 4), np.float32); Q = np.zeros((len(IDS), 4), np.float32)
            with torch.no_grad():
                for x, i in DataLoader(DS(sub, size, norm), batch_size=48, num_workers=6):
                    with torch.autocast("cuda", dtype=torch.bfloat16):
                        lo, pr, q = model(x.cuda())[:3]
                    i = i.numpy(); P[i] = torch.softmax(lo.float(), 1).cpu().numpy(); R[i] = torch.sigmoid(pr.float()).cpu().numpy(); Q[i] = q.float().cpu().numpy()
            out[f"P_{sub}"], out[f"R_{sub}"], out[f"Q_{sub}"] = P, R, Q
        np.savez(HERE / f"fb_ops_{tag}.npz", **out); print(tag, "scored", flush=True); del model; torch.cuda.empty_cache()


def analyse():
    from scipy.stats import spearmanr
    T = {l.split("\t")[0]: [float(x) for x in l.split("\t")[1:]] for l in (HERE / "fb_pairs_measured.tsv").read_text(encoding="utf-8").splitlines()[1:]}
    M = np.array([T[i] for i in IDS]); ok = ~np.isnan(M[:, 0])

    def gt(thr):
        G = np.zeros((len(IDS), 4), bool)
        for j, op in enumerate(OPS):
            c, s, v = thr[op]; x = M[:, COL[c]]; G[:, j] = (x >= v) if s == ">=" else (x <= v)
        return G
    G, G30 = gt(THR), gt(THR30); fl = np.array([FMAP[int(i.split("_")[0]) // 1000] for i in IDS]); held = np.isin(fl, list(HELD))
    res = {"n_measured": int(ok.sum()), "measured_presence_pct": {}, "models": {}}
    groups = {"all": ok, "held_out_filters": ok & held, "training_filters": ok & ~held, **{f: ok & (fl == f) for f in sorted(set(fl))}}
    for g, m in groups.items():
        res["measured_presence_pct"][g] = {"n": int(m.sum()), **{op: round(float(G[m, j].mean() * 100), 1) for j, op in enumerate(OPS)},
                                           "strict30": {op: round(float(G30[m, j].mean() * 100), 1) for j, op in enumerate(OPS)}}
    for f in sorted(HERE.glob("fb_ops_*.npz")):
        tag = f.stem[7:]; z = np.load(f); Rf, Ro, Qf = z["R_filt"], z["R_orig"], z["Q_filt"]; r = {}
        for g, m in groups.items():
            pf = Rf[m] >= 0.5; po = Ro[m] >= 0.5; gg = G[m]; row = {"n": int(m.sum())}
            for j, op in enumerate(OPS):
                tp = (pf[:, j] & gg[:, j]).sum()
                row[op] = {"head_on_render_pct": round(float(pf[:, j].mean() * 100), 1), "head_on_orig_pct": round(float(po[:, j].mean() * 100), 1),
                           "recall": round(float(tp / max(gg[:, j].sum(), 1)), 3), "precision": round(float(tp / max(pf[:, j].sum(), 1)), 3)}
            row["exact_four_bit_match_pct"] = round(float((pf == gg).all(1).mean() * 100), 1)
            if g == "all":
                row["quantity_spearman"] = {op: round(float(spearmanr(Qf[m, j], M[m, j]).correlation), 3) for j, op in enumerate(OPS)}
            r[g] = row
        res["models"][tag] = r
    (HERE / "fb_ops.json").write_text(json.dumps(res, indent=1))
    L = [f"# Addendum 55: operation head under Instagram AR filters (FairBeauty pairs, n measured {res['n_measured']})", "",
         "Measured presence % (rule: half of Alibaba level-30 median effect; strict = full level-30 median):", "",
         "| group | n | eye | jaw | white | smooth | strict eye/jaw/white/smooth |", "|---|---|---|---|---|---|---|"]
    for g, v in res["measured_presence_pct"].items():
        L.append(f"| {g} | {v['n']} | {v['eye']} | {v['jaw']} | {v['white']} | {v['smooth']} | {v['strict30']['eye']} / {v['strict30']['jaw']} / {v['strict30']['white']} / {v['strict30']['smooth']} |")
    for tag, r in res["models"].items():
        L += ["", f"## {tag}", "", "| group | op | head on render % | head on orig % | recall | precision |", "|---|---|---|---|---|---|"]
        for g in ["all", "held_out_filters", "training_filters"]:
            for op in OPS:
                v = r[g][op]; L.append(f"| {g} | {op} | {v['head_on_render_pct']} | {v['head_on_orig_pct']} | {v['recall']} | {v['precision']} |")
        L += ["", f"exact four-bit match (all): {r['all']['exact_four_bit_match_pct']} %; quantity Spearman: {r['all']['quantity_spearman']}"]
    (HERE / "FB_OPS.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    {"measure": lambda: measure(), "score": lambda: score(sys.argv[2:]), "analyse": lambda: analyse()}[sys.argv[1]]()
