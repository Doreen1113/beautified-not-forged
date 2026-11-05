"""Second source of real app filters, genuine faces only (never used for training or selection of the RU line):
B-LFW (LFW faces under Instagram AR beauty filters, 112 px), its unfiltered LFW control (112 px) and FairBeauty validation
(FairFace faces under the same filters, 282 px). Fixed samples: every 4th B-LFW image, all controls, every 3rd FairBeauty.
Reports where genuine faces go (real / fake / filter) and the AUC of P(filter) between B-LFW and the LFW control.
Low resolution: read as a stress test, not as a headline.
python eval_insta.py [tag ...] -> eval_insta.json"""
import json, sys
from pathlib import Path
import numpy as np, torch
from PIL import Image
from sklearn.metrics import roc_auc_score
from torch.utils.data import DataLoader, Dataset
HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from leak_probe import load, summ
from train_ru3 import to_t2
E = Path(r"C:\My_Project\AIGC\external_data")
SETS = {"B-LFW (filtered genuine)": sorted((E / "blfw/B-LFW_extracted/B-LFW").glob("*.png"))[::4],
        "LFW control (unfiltered genuine)": sorted((E / "lfw_control_112").glob("*.png")),
        "FairBeauty (filtered genuine)": sorted((E / "fairbeauty/val_extracted/val_fair_beauty").glob("*/*.png"))[::3]}

class DS(Dataset):
    def __init__(self, ps, size, norm): self.ps, self.size, self.norm = ps, size, norm
    def __len__(self): return len(self.ps)
    def __getitem__(self, i): return to_t2(np.array(Image.open(self.ps[i]).convert("RGB")), self.size, False, self.norm), i

def main():
    tags = sys.argv[1:] or ["clipe4r_s20260929", "clipe5_s20260929"]
    f = HERE / "eval_insta.json"; out = json.loads(f.read_text()) if f.is_file() else {}
    for tag in tags:
        model, size, norm = load(tag); res = {}; PF = {}
        for name, ps in SETS.items():
            P = np.zeros((len(ps), 3), np.float32)
            with torch.no_grad():
                for x, i in DataLoader(DS(ps, size, norm), batch_size=64, num_workers=6):
                    with torch.autocast("cuda", dtype=torch.bfloat16): lo = model(x.cuda())[0]
                    P[i.numpy()] = torch.softmax(lo.float(), 1).cpu().numpy()
            res[name] = summ(P); PF[name] = P
        a, b = PF["LFW control (unfiltered genuine)"], PF["B-LFW (filtered genuine)"]
        res["AUC of P(filter), B-LFW vs LFW control"] = round(float(roc_auc_score(np.r_[np.zeros(len(a)), np.ones(len(b))], np.r_[a[:, 2], b[:, 2]])), 3)
        out[tag] = res; f.write_text(json.dumps(out, indent=1)); print(tag, json.dumps(res), flush=True); del model; torch.cuda.empty_cache()

if __name__ == "__main__":
    main()
