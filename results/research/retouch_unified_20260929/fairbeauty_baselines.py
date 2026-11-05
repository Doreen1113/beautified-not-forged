"""Published detectors on the FairBeauty controlled pairs (external_data/fairbeauty_pairs: orig = FairFace val face,
filt = same face under an Instagram AR beauty filter; all genuine). Loaders are reused unchanged:
  zoo.ZOO[name]().score(paths)                        (external_baselines_20260905/zoo.py; DeepfakeBench family, sbi, univfd, npr)
  effort_score.Detector().score / fadapter_score.Detector().score   (external_baselines/, as in sota_baselines_20260929/score_sota.py)

python fairbeauty_baselines.py score <name>     # one detector per process -> fairbeauty_baselines_scores_<name>.npz
python fairbeauty_baselines.py analyse          # -> fairbeauty_baselines.json / .md
"""
import json
import sys
from pathlib import Path

import numpy as np

B = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent; D = B / "external_data/fairbeauty_pairs"
DET = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter", "univfd", "npr"]


def ids():
    return [l.split("\t")[0] for l in (D / "pairs.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]


def score(name):
    import torch
    f = HERE / f"fairbeauty_baselines_scores_{name}.npz"
    if f.is_file():
        print(name, "cached", flush=True); return
    I = ids(); po = [str(D / "orig" / f"{i}.png") for i in I]; pf = [str(D / "filt" / f"{i}.png") for i in I]
    if name in ("effort", "fadapter"):
        sys.path.insert(0, str(B / "external_baselines")); import importlib
        det = importlib.import_module(f"{name}_score").Detector()
    else:
        sys.path.insert(0, str(B / "results/research/external_baselines_20260905")); import zoo
        det = zoo.ZOO[name]()
    s = np.asarray(det.score(po + pf), np.float32); n = len(I)
    np.savez(f, orig=s[:n], filt=s[n:], ids=np.array(I))
    print(name, "done", n, "pairs; nan orig/filt", int(np.isnan(s[:n]).sum()), int(np.isnan(s[n:]).sum()),
          "| missing/unexpected keys", len(getattr(det, "missing", getattr(det, "missing_keys", []))),
          len(getattr(det, "unexpected", getattr(det, "unexpected_keys", []))), flush=True)


def block(o, f):
    from sklearn.metrics import roc_auc_score
    ok = ~(np.isnan(o) | np.isnan(f)); o, f = o[ok], f[ok]; t = float(np.quantile(o, 0.95))
    return {"n_pairs": int(ok.sum()), "n_nan_dropped": int((~ok).sum()), "t_5pct_fpr_on_originals": round(t, 4),
            "fa_filtered_at_5pct_fpr": round(100 * float((f > t).mean()), 1),
            "orig_above_t": round(100 * float((o > t).mean()), 1),
            "auc_orig_vs_filt": round(float(roc_auc_score(np.r_[np.zeros(len(o)), np.ones(len(f))], np.r_[o, f])), 3),
            "mean_s_orig": round(float(o.mean()), 3), "mean_s_filt": round(float(f.mean()), 3),
            "orig_fake_at_0.5": round(100 * float((o > 0.5).mean()), 1), "filt_fake_at_0.5": round(100 * float((f > 0.5).mean()), 1),
            "paired_rank": round(100 * float((f > o).mean()), 1)}


def analyse():
    out = {"published": {}, "ours_from_eval_fairbeauty_pairs_json": {}, "not_run": {}}
    for d in DET:
        f = HERE / f"fairbeauty_baselines_scores_{d}.npz"
        if not f.is_file():
            out["not_run"][d] = "no score file (see log)"; continue
        z = np.load(f); assert list(z["ids"]) == ids(); out["published"][d] = block(z["orig"], z["filt"])
    ours = json.loads((HERE / "eval_fairbeauty_pairs.json").read_text())
    for k, v in ours.items():
        out["ours_from_eval_fairbeauty_pairs_json"][k] = {
            "n_pairs": v["n_pairs"], "fa_filtered_at_5pct_fpr": v["filtered_called_fake_at_5pct_fpr_on_originals"],
            "auc_orig_vs_filt": v["auc_p_fake_originals_vs_filtered"], "mean_s_orig": v["originals"]["mean_p_fake"],
            "mean_s_filt": v["filtered"]["mean_p_fake"], "paired_rank": None}
        g = HERE / f"fairbeauty_scores_{k}.npz"      # per-image probs saved by eval_fairbeauty_pairs.py: recompute on P(fake)
        if g.is_file():
            z = np.load(g); out["ours_from_eval_fairbeauty_pairs_json"][k]["recomputed_from_npz"] = block(z["orig"][:, 1], z["filt"][:, 1])
            out["ours_from_eval_fairbeauty_pairs_json"][k]["paired_rank"] = out["ours_from_eval_fairbeauty_pairs_json"][k]["recomputed_from_npz"]["paired_rank"]
    (HERE / "fairbeauty_baselines.json").write_text(json.dumps(out, indent=1))
    L = ["| detector | FA_filtered @5% FPR on originals | AUC orig vs filt | mean s orig | mean s filt | paired rank (filt > orig) | filt >0.5 | orig >0.5 |", "|---|---|---|---|---|---|---|---|"]
    for k, v in out["published"].items():
        L.append(f"| {k} | {v['fa_filtered_at_5pct_fpr']} | {v['auc_orig_vs_filt']} | {v['mean_s_orig']} | {v['mean_s_filt']} | {v['paired_rank']} | {v['filt_fake_at_0.5']} | {v['orig_fake_at_0.5']} |")
    for k, v in out["ours_from_eval_fairbeauty_pairs_json"].items():
        L.append(f"| ours {k} | {v['fa_filtered_at_5pct_fpr']} | {v['auc_orig_vs_filt']} | {v['mean_s_orig']} | {v['mean_s_filt']} | {v['paired_rank']} | {v.get('recomputed_from_npz', {}).get('filt_fake_at_0.5', 'n/a')} | {v.get('recomputed_from_npz', {}).get('orig_fake_at_0.5', 'n/a')} |")
    (HERE / "fairbeauty_baselines.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    if sys.argv[1] == "score":
        score(sys.argv[2])
    else:
        analyse()
