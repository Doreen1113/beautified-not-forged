"""Instagram AR beauty filters on genuine faces, controlled: 2,927 FairBeauty images and their own FairFace originals,
same extractor (build_fairbeauty_pairs.py). Never used for training or selection. Per model: where originals and filtered
faces go; at the threshold of 5 % FPR on the originals (score P(fake)), share of filtered genuine faces called fake;
AUC of P(filter) and paired rank (filtered above its own original).
python eval_fairbeauty_pairs.py [tag ...] -> eval_fairbeauty_pairs.json, fairbeauty_scores_<tag>.npz"""
import json, sys
from pathlib import Path
import numpy as np, torch
from PIL import Image
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader, Dataset
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from leak_probe import load, summ
from train_ru3 import to_t2
D = Path(r"C:\My_Project\AIGC\external_data\fairbeauty_pairs")
IDS = [l.split("\t")[0] for l in (D / "pairs.tsv").read_text(encoding="utf-8").splitlines()[1:]]

class DS(Dataset):
    def __init__(self, sub, size, norm): self.sub, self.size, self.norm = sub, size, norm
    def __len__(self): return len(IDS)
    def __getitem__(self, i): return to_t2(np.array(Image.open(D / self.sub / f"{IDS[i]}.png").convert("RGB")), self.size, False, self.norm), i

def main():
    tags = sys.argv[1:] or ["clipe4r_s20260929", "clipe5_s20260929"]
    f = HERE / "eval_fairbeauty_pairs.json"; out = json.loads(f.read_text()) if f.is_file() else {}
    for tag in tags:
        model, size, norm = load(tag); P = {}
        for sub in ("orig", "filt"):
            p = np.zeros((len(IDS), 3), np.float32)
            with torch.no_grad():
                for x, i in DataLoader(DS(sub, size, norm), batch_size=64, num_workers=6):
                    with torch.autocast("cuda", dtype=torch.bfloat16): lo = model(x.cuda())[0]
                    p[i.numpy()] = torch.softmax(lo.float(), 1).cpu().numpy()
            P[sub] = p
        t = float(np.quantile(P["orig"][:, 1], 0.95))
        out[tag] = {"n_pairs": len(IDS), "originals": summ(P["orig"]), "filtered": summ(P["filt"]),
                    "filtered_called_fake_at_5pct_fpr_on_originals": round(100 * float((P["filt"][:, 1] > t).mean()), 1),
                    "auc_p_fake_originals_vs_filtered": round(float(roc_auc_score(np.r_[np.zeros(len(IDS)), np.ones(len(IDS))], np.r_[P["orig"][:, 1], P["filt"][:, 1]])), 3),
                    "auc_p_filter": round(float(roc_auc_score(np.r_[np.zeros(len(IDS)), np.ones(len(IDS))], np.r_[P["orig"][:, 2], P["filt"][:, 2]])), 3),
                    "paired_rank_p_filter": round(100 * float((P["filt"][:, 2] > P["orig"][:, 2]).mean()), 1)}
        FMAP = {0: "Pretty", 1: "hary beauty", 2: "Shiny foxy", 3: "Caramel Macchiato", 4: "Cute baby face", 5: "Baby_cute_face", 6: "big city life",
                7: "Just Baby", 8: "Pretty", 9: "hary beauty", 10: "Shiny foxy"}   # val_fair_beauty/filters.txt
        HELD = {"Baby_cute_face", "big city life", "Just Baby"}                      # never trained on (Addendum 8)
        fl = np.array([FMAP[int(i.split("_")[0]) // 1000] for i in IDS]); held = np.isin(fl, list(HELD)); am = P["filt"].argmax(1)
        out[tag]["by_filter"] = {f: {"n": int((fl == f).sum()), "held_out": f in HELD, "called_fake_at_5pct_fpr": round(100 * float((P["filt"][fl == f, 1] > t).mean()), 1),
                                     "argmax_fake": round(100 * float((am[fl == f] == 1).mean()), 1), "argmax_filter": round(100 * float((am[fl == f] == 2).mean()), 1)} for f in sorted(set(fl))}
        for nm, mk in (("held_out_filters", held), ("training_filters", ~held)):
            out[tag][nm] = {"n": int(mk.sum()), "called_fake_at_5pct_fpr": round(100 * float((P["filt"][mk, 1] > t).mean()), 1),
                            "argmax_fake": round(100 * float((am[mk] == 1).mean()), 1), "argmax_filter": round(100 * float((am[mk] == 2).mean()), 1)}
        np.savez(HERE / f"fairbeauty_scores_{tag}.npz", orig=P["orig"], filt=P["filt"], ids=np.array(IDS))
        f.write_text(json.dumps(out, indent=1)); print(tag, json.dumps(out[tag]), flush=True); del model; torch.cuda.empty_cache()

if __name__ == "__main__":
    main()
