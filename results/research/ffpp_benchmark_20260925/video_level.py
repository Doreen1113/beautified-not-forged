"""Video-level (32-frame mean) AUC on the v2 CDFv2 / DFD sets for every model, next to frame-level. Ours are scored
here (per-frame probs saved to ours_frames_<name>_<set>.npz); published detectors reuse cdfstd_v2_*.npz / cdfstd_dfdv2_*.npz.

python video_level.py -> video_level.json / video_level.md
"""
import json
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
SETS = {"cdf": SP / "celebdf_std32v2.txt", "dfd": SP / "dfd_std32v2.txt"}
PUB = {"xception": "cdfstd_v2_{}.npz", "effnb4": "cdfstd_v2_{}.npz", "f3net": "cdfstd_v2_{}.npz", "spsl": "cdfstd_v2_{}.npz",
       "ucf": "cdfstd_v2_{}.npz", "recce": "cdfstd_v2_{}.npz", "core": "cdfstd_v2_{}.npz", "srm": "cdfstd_v2_{}.npz", "sbi": "cdfstd_v2_{}.npz",
       "effort": "cdfstd_v2_{}.npz", "fadapter": "cdfstd_v2_{}.npz"}
OURS = {"HYB-L-s2": (BASE / "checkpoints/research/sbiscale_20260926/sbiscale_HYB_s20260927.pth", "tf_efficientnet_b4.ap_in1k", 380, 3),
        "HYB-F": (BASE / "checkpoints/research/sbifix_20260927/sbifix_HYB_s20260928.pth", "tf_efficientnet_b4.ap_in1k", 380, 3),
        "SBI-F": (BASE / "checkpoints/research/sbifix_20260927/sbifix_SBI_s20260928.pth", "tf_efficientnet_b4.ap_in1k", 380, 2),
        "SUP-F": (BASE / "checkpoints/research/sbifix_20260927/sbifix_SUP_s20260928.pth", "tf_efficientnet_b4.ap_in1k", 380, 3),
        "HYBD-F": (BASE / "checkpoints/research/sbifix_20260927/sbifix_HYBD_s20260928.pth", "tf_efficientnet_b4.ap_in1k", 380, 3),
        "HYBD-F-s2": (BASE / "checkpoints/research/sbifix_20260927/sbifix_HYBD_s20260929.pth", "tf_efficientnet_b4.ap_in1k", 380, 3),
        "RepViT20": (BASE / "checkpoints/research/ffpp_unified_20260925/ffpp3_FLAT_repvit20.pth", "repvit_m0_9.dist_300e_in1k", 224, 3),
        "MASK": (BASE / "checkpoints/research/cgd_20260927/cgd_MASK_s20260928.pth", "cgdnet:1", 380, 3),
        "HYBPE": (BASE / "checkpoints/research/cgd_20260927/cgd_HYBPE_s20260928.pth", "cgdnet:0", 380, 3),
        "RU-effb4": (BASE / "checkpoints/research/retouch_unified_20260929/ru_effb4_s20260929.pth", "runet:effb4", 380, 3),
        "RU2-effb4": (BASE / "checkpoints/research/retouch_unified_20260929/ru_ru2_effb4_s20260929.pth", "runet:effb4", 380, 3),
        "RU-clipe": (BASE / "checkpoints/research/retouch_unified_20260929/ru_clipe_s20260929.pth", "ruclip:1", 224, 3),
        "RU-clipe-s2": (BASE / "checkpoints/research/retouch_unified_20260929/ru_clipe_s20260930.pth", "ruclip:1", 224, 3),
        "RU2-effb4-s2": (BASE / "checkpoints/research/retouch_unified_20260929/ru_ru2_effb4_s20260930.pth", "runet:effb4", 380, 3),
        "RU3-effb4": (BASE / "checkpoints/research/retouch_unified_20260929/ru_ru3_effb4_s20260929.pth", "runet3:effb4:0", 380, 3),
        "RU3e-effb4": (BASE / "checkpoints/research/retouch_unified_20260929/ru_ru3e_effb4_s20260929.pth", "runet3:effb4:1", 380, 3),
        "RU4e-effb4": (BASE / "checkpoints/research/retouch_unified_20260929/ru_ru4e_effb4_s20260929.pth", "runet3:effb4:1", 380, 3),
        "RU-clipe4": (BASE / "checkpoints/research/retouch_unified_20260929/ru_clipe4_s20260929.pth", "ruclipt:clipe4_s20260929", 224, 3)}


class DS(Dataset):
    def __init__(self, p, size):
        self.p = p; self.t = transforms.Compose([transforms.Resize((size, size)), transforms.ToTensor(), transforms.Normalize([0.5] * 3, [0.5] * 3)])

    def __len__(self):
        return len(self.p)

    def __getitem__(self, i):
        return self.t(Image.open(self.p[i]).convert("RGB")), i


def rows(p):
    r = [l.split("\t") for l in Path(p).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return [x[0] for x in r], np.array([int(x[1]) for x in r]), np.array([x[2] for x in r])


def score_ours(name, paths):
    ck, arch, size, k = OURS[name]
    if arch.startswith("runet:"):
        import sys; sys.path.insert(0, str(BASE / "results/research/retouch_unified_20260929")); from train_ru import RUNet
        net = RUNet(arch.split(":")[1]); net.load_state_dict(torch.load(ck, map_location="cpu")); net = net.cuda().eval()
        m = lambda x: net(x)[0]
    elif arch.startswith("runet3:"):
        import sys; sys.path.insert(0, str(BASE / "results/research/retouch_unified_20260929")); from train_ru3 import RUNet3
        _, ar, hd = arch.split(":"); net = RUNet3(ar, head=hd == "1"); net.load_state_dict(torch.load(ck, map_location="cpu")); net = net.cuda().eval()
        m = lambda x: net(x)[0]
    elif arch.startswith("cgdnet:"):
        import sys; sys.path.insert(0, str(BASE / "results/research/cgd_20260927")); from train_cgd import CGDNet
        net = CGDNet(head=arch.endswith("1")); net.load_state_dict(torch.load(ck, map_location="cpu")); net = net.cuda().eval()
        m = lambda x: net(x)[0]
    else:
        m = timm.create_model(arch, pretrained=False, num_classes=k); m.load_state_dict(torch.load(ck, map_location="cpu")); m = m.cuda().eval()
    out = np.zeros((len(paths), k), np.float32)
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        for x, i in DataLoader(DS(paths, size), batch_size=96, num_workers=6):
            out[i.numpy()] = torch.softmax(m(x.cuda()).float(), 1).cpu().numpy()
    torch.cuda.empty_cache()
    return out


def video_auc(y, s, v):
    by = defaultdict(list); yy = {}
    for yi, si, vi in zip(y, s, v):
        by[vi].append(si); yy[vi] = yi
    ks = list(by)
    return roc_auc_score([yy[k] for k in ks], [np.mean(by[k]) for k in ks])


def main():
    R = {}
    for sname, sp in SETS.items():
        paths, y, v = rows(sp)
        for name in OURS:
            if not OURS[name][0].is_file():
                continue
            f = HERE / f"ours_frames_{name}_{sname}.npz"
            if f.is_file():
                p = np.load(f)["p"]
            elif OURS[name][1].startswith("ruclip"):   # CLIP arms: frames are seeded from eval_ru.py score dumps, never scored here
                continue
            else:
                p = score_ours(name, paths); np.savez(f, p=p)
            s = p[:, 1]
            R.setdefault(name, {})[sname] = {"frame": round(float(roc_auc_score(y, s)), 4), "video": round(float(video_auc(y, s, v)), 4)}
            if p.shape[1] == 3:
                am = p.argmax(1); by = defaultdict(list)
                for a, vi, yi in zip(am, v, y):
                    if yi == 0:
                        by[vi].append(a == 1)
                R[name][sname]["real_called_fake_frame"] = round(float((am[y == 0] == 1).mean() * 100), 2)
                R[name][sname]["real_called_fake_video"] = round(float(np.mean([np.mean(b) > 0.5 for b in by.values()]) * 100), 2)
        for name, pat in PUB.items():
            f = HERE / (pat.format(name) if sname == "cdf" else f"cdfstd_dfdv2_{name}.npz")
            if not f.is_file():
                continue
            s = np.load(f)["std"]
            if len(s) != len(y):
                continue
            R.setdefault(name, {})[sname] = {"frame": round(float(roc_auc_score(y, s)), 4), "video": round(float(video_auc(y, s, v)), 4)}
        print(sname, "done", flush=True)
    json.dump(R, open(HERE / "video_level.json", "w"), indent=1)
    L = ["| model | CDFv2 frame | CDFv2 video | DFD frame | DFD video |", "|---|---|---|---|---|"]
    for n, r in sorted(R.items(), key=lambda kv: -kv[1].get("cdf", {}).get("video", 0)):
        c, d = r.get("cdf", {}), r.get("dfd", {})
        L.append(f"| {n} | {c.get('frame', '')} | {c.get('video', '')} | {d.get('frame', '')} | {d.get('video', '')} |")
    (HERE / "video_level.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    main()
