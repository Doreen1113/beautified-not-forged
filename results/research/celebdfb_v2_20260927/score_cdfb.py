"""Score every model on the Celeb-DF-B v2 frames (PRE_DECLARED §4). Cached per model.

python score_cdfb.py [--models a,b]  -> scores/<model>.npz  {p: (N,3) probs; binary models pad filter=0}
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import timm
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

BASE = Path(r"C:\My_Project\AIGC")
HERE = Path(__file__).resolve().parent
import os
TAG = os.environ.get("CDFB_TAG", "v2")
SPLIT = BASE / f"splits/research/celebdfb_v2_20260927/cdfb_std32{TAG}.txt"
SC = "scores" if TAG == "v2" else f"scores_{TAG}"
sys.path.insert(0, str(BASE / "results/research/external_baselines_20260905")); sys.path.insert(0, str(BASE))
PUBLISHED = ["xception", "effnb4", "spsl", "f3net", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter", "univfd", "npr"]
CU, CS = BASE / "checkpoints/research/ffpp_unified_20260925", BASE / "checkpoints/research/sbiscale_20260926"
CF = BASE / "checkpoints/research/sbifix_20260927"
REPVIT, EFFB4 = "repvit_m0_9.dist_300e_in1k", "tf_efficientnet_b4.ap_in1k"
OURS = {"ours_repvit20": (CU / "ffpp3_FLAT_repvit20.pth", REPVIT, 224, 3),
        "ours_repvit40": (CU / "ffpp3_FLAT_repvit40.pth", REPVIT, 224, 3),
        "HYB-L": (CS / "sbiscale_HYB.pth", EFFB4, 380, 3),
        "SBI-L": (CS / "sbiscale_SBI.pth", EFFB4, 380, 2),
        "HYB-L-s2": (CS / "sbiscale_HYB_s20260927.pth", EFFB4, 380, 3),
        "SBI-F": (CF / "sbifix_SBI_s20260928.pth", EFFB4, 380, 2),
        "HYB-F": (CF / "sbifix_HYB_s20260928.pth", EFFB4, 380, 3),
        "SUP-F": (CF / "sbifix_SUP_s20260928.pth", EFFB4, 380, 3),
        "HYBD-F": (CF / "sbifix_HYBD_s20260928.pth", EFFB4, 380, 3),
        "HYBD-F-s2": (CF / "sbifix_HYBD_s20260929.pth", EFFB4, 380, 3),
        "FASB-L": (CS / "sbiscale_FASB.pth", EFFB4, 380, 3)}


class DS(Dataset):
    def __init__(self, p, size, clip=False):
        self.p = p
        mean, std = ([0.48145466, 0.4578275, 0.40821073], [0.26862954, 0.26130258, 0.27577711]) if clip else ([0.5] * 3, [0.5] * 3)
        self.t = transforms.Compose([transforms.Resize((size, size)), transforms.ToTensor(), transforms.Normalize(mean, std)])

    def __len__(self):
        return len(self.p)

    def __getitem__(self, i):
        return self.t(Image.open(self.p[i]).convert("RGB")), i


CG = BASE / "checkpoints/research/cgd_20260927"
for _a in ("HYBPE", "MASK", "MASKD", "CGD", "CGDD", "CGD-ZERO", "CGD-BLUR", "CGD-NOHOLD"):
    OURS[f"cgd_{_a}"] = (CG / f"cgd_{_a}_s20260928.pth", "cgdnet:" + ("0" if _a == "HYBPE" else "1"), 380, 3)
OURS["cgd_MASK-s2"] = (CG / "cgd_MASK_s20260929.pth", "cgdnet:1", 380, 3)
RU = BASE / "checkpoints/research/retouch_unified_20260929"
OURS["RU-effb4"] = (RU / "ru_effb4_s20260929.pth", "runet:effb4", 380, 3)
OURS["RU-repvit"] = (RU / "ru_repvit_s20260929.pth", "runet:repvit", 224, 3)
OURS["RU2-effb4"] = (RU / "ru_ru2_effb4_s20260929.pth", "runet:effb4", 380, 3)
OURS["RU2-repvit"] = (RU / "ru_ru2_repvit_s20260929.pth", "runet:repvit", 224, 3)
OURS["RU2-effb4-s2"] = (RU / "ru_ru2_effb4_s20260930.pth", "runet:effb4", 380, 3)
OURS["RU3-effb4"] = (RU / "ru_ru3_effb4_s20260929.pth", "runet3:effb4:0", 380, 3)
OURS["RU3e-effb4"] = (RU / "ru_ru3e_effb4_s20260929.pth", "runet3:effb4:1", 380, 3)
OURS["RU-clip"] = (RU / "ru_clip_s20260929.pth", "ruclip:0", 224, 3)
OURS["RU-clipe"] = (RU / "ru_clipe_s20260929.pth", "ruclip:1", 224, 3)
OURS["RU-clipe-s2"] = (RU / "ru_clipe_s20260930.pth", "ruclip:1:20260930", 224, 3)
OURS["RU-clipe4"] = (RU / "ru_clipe4_s20260929.pth", "ruclipt:clipe4_s20260929", 224, 3)
OURS["RU-clipe4r"] = (RU / "ru_clipe4r_s20260929.pth", "ruclipt:clipe4r_s20260929", 224, 3)      # Addendum 5 re-runs, epoch chosen by C2
OURS["RU-clipe4r-s2"] = (RU / "ru_clipe4r_s20260930.pth", "ruclipt:clipe4r_s20260930", 224, 3)
OURS["RU-clipe5"] = (RU / "ru_clipe5_s20260929.pth", "ruclipt:clipe5_s20260929", 224, 3)
OURS["RU-clipe5x"] = (RU / "ru_clipe5x_s20260929.pth", "ruclipt:clipe5x_s20260929", 224, 3)
OURS["RU-clipe5-s2"] = (RU / "ru_clipe5_s20260930.pth", "ruclipt:clipe5_s20260930", 224, 3)
OURS["RU-clipe5g0"] = (RU / "ru_clipe5g0_s20260929.pth", "ruclipt:clipe5g0_s20260929", 224, 3)
OURS["RU-clipe5v0"] = (RU / "ru_clipe5v0_s20260929.pth", "ruclipt:clipe5v0_s20260929", 224, 3)
OURS["RU-clipe6"] = (RU / "ru_clipe6_s20260929.pth", "ruclipt:clipe6_s20260929", 224, 3)
OURS["RU-clipe7"] = (RU / "ru_clipe7_s20260929.pth", "ruclipt:clipe7_s20260929", 224, 3)
OURS["RU-clipe7-s2"] = (RU / "ru_clipe7_s20260930.pth", "ruclipt:clipe7_s20260930", 224, 3)
OURS["RU-clipe5b"] = (RU / "ru_clipe5b_s20260929.pth", "ruclipt:clipe5b_s20260929", 224, 3)
# Addendum 58 (in-the-wild genuine bases)
OURS["RU-clipe7W_s20260929"] = (RU / "ru_clipe7W_s20260929.pth", "ruclipt:clipe7W_s20260929", 224, 3)
OURS["RU-clipe7W_s20260930"] = (RU / "ru_clipe7W_s20260930.pth", "ruclipt:clipe7W_s20260930", 224, 3)
# Addendum 56 (multi-operation beautification arms)
OURS["RU-clipe5M_s20260929"] = (RU / "ru_clipe5M_s20260929.pth", "ruclipt:clipe5M_s20260929", 224, 3)
OURS["RU-clipe5M_s20260930"] = (RU / "ru_clipe5M_s20260930.pth", "ruclipt:clipe5M_s20260930", 224, 3)
OURS["RU-clipe5M1_s20260929"] = (RU / "ru_clipe5M1_s20260929.pth", "ruclipt:clipe5M1_s20260929", 224, 3)
OURS["RU-clipe5fbEM_s20260929"] = (RU / "ru_clipe5fbEM_s20260929.pth", "ruclipt:clipe5fbEM_s20260929", 224, 3)
OURS["RU-clipe5f"] = (RU / "ru_clipe5f_s20260929.pth", "ruclipt:clipe5f_s20260929", 224, 3)
OURS["RU-clipe5f-s2"] = (RU / "ru_clipe5f_s20260930.pth", "ruclipt:clipe5f_s20260930", 224, 3)
OURS["RU-clipe5fg0"] = (RU / "ru_clipe5fg0_s20260929.pth", "ruclipt:clipe5fg0_s20260929", 224, 3)
OURS["RU-clipe8"] = (RU / "ru_clipe8_s20260929.pth", "ruclipt:clipe8_s20260929", 224, 3)
for _t in ("clipe5af_s20260929", "clipe5rf_s20260929", "clipe5af_s20260930", "clipe5a_s20260929", "clipe5ab_s20260929", "clipe5kf_s20260929",
           "clipe5awpf_s20260929", "clipe5awpf_s20260930", "clipe5awpb_s20260929", "clipe5awpb_s20260930", "clipe5awpd_s20260929",
           "clipe5awptf_s20260929", "clipe5awps3f_s20260929", "clipe5fb_s20260929", "clipe5feb_s20260929", "clipe5feb_s20260930",
           "clipe5fbn_s20260929", "clipe5fbn_s20260930", "clipe5fbp1n_s20260929", "clipe5fbg0o_s20260929", "clipe5fbg0o_s20260930", "clipe5fbg0oy_s20260929", "clipe5fbg0oy_s20260930", "clipe5y_s20260929", "clipe5fbg0oyE_s20260929", "clipe5fbg0oyEi_s20260929", "clipe5fbg0p1o_s20260929", "clipe5fbg0p1o_s20260930", "clipe5fbg0p1o_s20261001", "clipe5fbp0_s20260929", "clipe5fbp1_s20260929", "clipe5fbp0_s20260930", "clipe5fbp1_s20260930", "clipe5fb_s20260930", "clipe5fbp0_s20261001", "clipe5fb_s20261001", "clipe5fbp1_s20261001", "clipe5fbp0E_s20260929", "clipe5fbE_s20260929", "clipe5fbp0E_s20260930", "clipe5fbE_s20260930", "clipe5fbEi0_s20260929", "clipe5fbEi_s20260929", "clipe5fbp0Ei_s20260929", "clipe5mf_s20260929", "clipe5mfp0_s20260929", "clipe5mf_s20260930", "clipe5fbp3_s20260929", "clipe5y_s20260930", "clipe5b_s20260930"):   # Addenda 42, 16, 18, 19, 21, 25, 26, 28, 40
    OURS["RU-" + _t] = (RU / f"ru_{_t}.pth", "ruclipt:" + _t, 224, 3)
for _t in ("clipe5z_s20260929", "clipe5bz_s20260929", "clipe5z_s20260930", "clipe5bz_s20260930", "clipe5bzl0_s20260929", "clipe5bzl03_s20260929", "clipe5bzl01_s20260929", "clipe5bzsg_s20260929", "clipe5bzsg_s20260930", "clipe5fbzsg_s20260929", "clipe5bzsgl03_s20260929", "clipe5bzsgl01_s20260929", "clipe5bzsgG_s20260929", "clipe5bzsgh_s20260929", "clipe5bzsgl003_s20260929", "clipe5bzsgl01_s20260930", "clipe5bzsgl003_s20260930", "clipe5bzsgh_s20260930", "clipe5bzsgG_s20260930", "clipe5bzxs_s20260929", "clipe5fbp0F2_s20260929", "clipe5bzEsg_s20260929"):   # Addendum 46 (+ am. 3, 4)
    OURS["RU-" + _t] = (RU / f"ru_{_t}.pth", "ruclipt:" + _t, 224, 3)
for _t in ("clipe5R25_s20260929", "clipe5bR25_s20260929"):   # Addendum 67 (re-synthesis pseudo-forgeries)
    OURS["RU-" + _t] = (RU / f"ru_{_t}.pth", "ruclipt:" + _t, 224, 3)
OURS["RU4e-effb4"] = (RU / "ru_ru4e_effb4_s20260929.pth", "runet3:effb4:1", 380, 3)
OURS["RU7We-effb4"] = (RU / "ru_ru7we_effb4_s20260929.pth", "runet3:effb4:1", 380, 3)   # Addendum 70 (factorised cls, train_ru3.RUNet3 loads it)


def ours(name, paths):
    ck, arch, size, k = OURS[name]
    if arch.startswith("runet3:"):
        sys.path.insert(0, str(BASE / "results/research/retouch_unified_20260929")); from train_ru3 import RUNet3
        _, ar, hd = arch.split(":"); net = RUNet3(ar, head=hd == "1"); net.load_state_dict(torch.load(ck, map_location="cpu")); net = net.cuda().eval()
        m = lambda x: net(x)[0]
    elif arch.startswith("ruclipt:"):
        sys.path.insert(0, str(BASE / "results/research/retouch_unified_20260929")); from train_ru_clip import load_clip
        net = load_clip(arch.split(":")[1], head=True).cuda().eval(); m = lambda x: net(x)[0]
    elif arch.startswith("ruclip:"):
        sys.path.insert(0, str(BASE / "results/research/retouch_unified_20260929")); from train_ru_clip import load_clip
        parts = arch.split(":"); hd = parts[1] == "1"; seed = parts[2] if len(parts) > 2 else "20260929"
        net = load_clip(f"clip{'e' if hd else ''}_s{seed}", head=hd).cuda().eval()
        m = lambda x: net(x)[0]
    elif arch.startswith("runet:"):
        sys.path.insert(0, str(BASE / "results/research/retouch_unified_20260929")); from train_ru import RUNet
        net = RUNet(arch.split(":")[1]); net.load_state_dict(torch.load(ck, map_location="cpu")); net = net.cuda().eval()
        m = lambda x: net(x)[0]
    elif arch.startswith("cgdnet:"):
        sys.path.insert(0, str(BASE / "results/research/cgd_20260927")); from train_cgd import CGDNet
        net = CGDNet(head=arch.endswith("1")); net.load_state_dict(torch.load(ck, map_location="cpu")); net = net.cuda().eval()
        m = lambda x: net(x)[0]
    else:
        m = timm.create_model(arch, pretrained=False, num_classes=k)
        m.load_state_dict(torch.load(ck, map_location="cpu")); m = m.cuda().eval()
    out = np.zeros((len(paths), 3), np.float32)
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        for x, i in DataLoader(DS(paths, size, clip=arch.startswith("ruclip")), batch_size=96, num_workers=6):
            out[i.numpy(), :k] = torch.softmax(m(x.cuda()).float(), 1).cpu().numpy()
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--models", default=""); a = ap.parse_args()
    paths = [l.split("\t")[0] for l in SPLIT.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    (HERE / SC).mkdir(exist_ok=True)
    names = a.models.split(",") if a.models else [n for n in OURS if OURS[n][0].is_file()] + PUBLISHED
    for n in names:
        f = HERE / SC / f"{n}.npz"
        if f.is_file():
            print(n, "cached", flush=True); continue
        if n in OURS:
            p = ours(n, paths)
        else:
            if n in ("gend", "dfdhr", "caddm", "laanetr", "effort", "fadapter"):   # adapters added 2026-10-11 (effort, fadapter: 2026-10-29) (external_baselines/<name>_score.py)
                sys.path.insert(0, str(BASE / "external_baselines")); import importlib; m = importlib.import_module(f"{n}_score").Detector()
            else:
                import zoo
                m = zoo.ZOO[n]()
            s = np.asarray(m.score(paths), np.float32)
            p = np.stack([1 - s, s, np.zeros_like(s)], 1); del m
        np.savez(f, p=p, paths=np.array(paths))
        print(n, "done", len(paths), flush=True)
        torch.cuda.empty_cache()
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
