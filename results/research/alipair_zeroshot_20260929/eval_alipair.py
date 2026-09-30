"""Zero-shot evaluation of the FF++-only three-way models on Alibaba commercial retouching pairs (see PRE_DECLARED.md).

python eval_alipair.py  -> boxes.json, probs_<model>.npz, results.json, RESULTS.md
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import timm
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

BASE = Path(r"C:\My_Project\AIGC")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE / "results/research/cgd_20260927"))
ORIG = BASE / "ffhq_originals/Part2"
ALI = BASE / "FFHQ_ali_process"
TYPES = ["EyeEnlarging", "FaceLifting", "Smoothing", "Whitening"]
LEVELS = [30, 60, 90]
MARGIN = 0.35
CK = BASE / "checkpoints/research"
EFFB4, REPVIT = "tf_efficientnet_b4.ap_in1k", "repvit_m0_9.dist_300e_in1k"
MODELS = {"HYB": (CK / "sbiscale_20260926/sbiscale_HYB_s20260927.pth", EFFB4, 380),
          "HYB-F": (CK / "sbifix_20260927/sbifix_HYB_s20260928.pth", EFFB4, 380),
          "HYB-D": (CK / "sbifix_20260927/sbifix_HYBD_s20260928.pth", EFFB4, 380),
          "SUP-F": (CK / "sbifix_20260927/sbifix_SUP_s20260928.pth", EFFB4, 380),
          "MASK": (CK / "cgd_20260927/cgd_MASK_s20260928.pth", "cgdnet", 380),
          "RepViT": (CK / "ffpp_unified_20260925/ffpp3_FLAT_repvit20.pth", REPVIT, 224)}
NORM = transforms.Normalize([0.5] * 3, [0.5] * 3)
TF = {s: transforms.Compose([transforms.Resize((s, s)), transforms.ToTensor(), NORM]) for s in (380, 224)}


def boxes():
    f = HERE / "boxes.json"
    if f.is_file():
        return json.loads(f.read_text())
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision
    lmk = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_buffer=open(BASE / "face_landmarker.task", "rb").read()), num_faces=1))
    out = {}
    for p in sorted(ORIG.glob("*.png")):
        bgr = cv2.imread(str(p)); h, w = bgr.shape[:2]
        res = lmk.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)))
        if not res.face_landmarks:
            continue
        lm = np.array([[q.x * w, q.y * h] for q in res.face_landmarks[0]])
        (x0, y0), (x1, y1) = lm.min(0), lm.max(0); bw, bh = x1 - x0, y1 - y0
        x0, x1, y0, y1 = x0 - bw * MARGIN, x1 + bw * MARGIN, y0 - bh * MARGIN, y1 + bh * MARGIN
        out[p.stem] = [max(0, int(x0)), max(0, int(y0)), min(w, int(x1)), min(h, int(y1))]
    f.write_text(json.dumps(out)); print("boxes", len(out), flush=True)
    return out


class DS(Dataset):
    def __init__(self, items):
        self.items = items

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        p, b = self.items[i]
        im = Image.open(p).convert("RGB").crop(tuple(b))
        return TF[380](im), TF[224](im), i


def load(name):
    ck, arch, _ = MODELS[name]
    if arch == "cgdnet":
        from train_cgd import CGDNet
        net = CGDNet(head=True); net.load_state_dict(torch.load(ck, map_location="cpu")); net = net.cuda().eval()
        return lambda x: net(x)[0]
    m = timm.create_model(arch, pretrained=False, num_classes=3); m.load_state_dict(torch.load(ck, map_location="cpu")); m = m.cuda().eval()
    return m


def main():
    B = boxes(); idx = sorted(B)
    items = [(str(ORIG / f"{k}.png"), B[k]) for k in idx]; keys = [("orig", 0)] * len(idx)
    for t in TYPES:
        for lv in LEVELS:
            for k in idx:
                p = ALI / f"{t}_{lv}" / f"{(int(k) // 1000) * 1000}" / f"{k}.png"
                if p.is_file():
                    items.append((str(p), B[k])); keys.append((t, lv))
    ref = [it[0] for it in items]
    print("items", len(items), flush=True)
    nets = {n: load(n) for n in MODELS}
    P = {n: np.full((len(items), 3), np.nan, np.float32) for n in MODELS}
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        for j, (x380, x224, i) in enumerate(DataLoader(DS(items), batch_size=48, num_workers=8, persistent_workers=True)):
            for n, net in nets.items():
                x = (x224 if MODELS[n][2] == 224 else x380).cuda()
                P[n][i.numpy()] = torch.softmax(net(x).float(), 1).cpu().numpy()
            if j % 50 == 0:
                print(f"batch {j}/{len(items) // 48}", flush=True)
    for n in MODELS:
        np.savez(HERE / f"probs_{n}.npz", p=P[n], path=np.array(ref), group=np.array([f"{a}_{b}" for a, b in keys]))
    analyse()


def analyse():
    lock = set(l.split("\t")[5].strip() for l in (BASE / "results/research/retouching_benchmark_20260823/heldout_manifest.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.split("\t")[1] == "0")
    R = {}
    for n in MODELS:
        z = np.load(HERE / f"probs_{n}.npz"); p, path, grp = z["p"], z["path"], z["group"]
        stem = np.array([Path(s).stem for s in path])
        o = grp == "orig_0"; po = dict(zip(stem[o], p[o]))
        am = p.argmax(1)
        r = {"orig": {c: round(float((am[o] == i).mean() * 100), 2) for i, c in enumerate(["real", "fake", "filter"])}, "n_orig": int(o.sum())}
        spec = 100 - r["orig"]["filter"]
        def block(mask):
            pf = p[mask, 2]; of = np.array([po[s][2] for s in stem[mask]])
            f = float((am[mask] == 2).mean() * 100)
            return {"n": int(mask.sum()), "to_real": round(float((am[mask] == 0).mean() * 100), 2),
                    "to_fake": round(float((am[mask] == 1).mean() * 100), 2), "to_filter": round(f, 2),
                    "balanced_acc": round((f + spec) / 2, 2), "paired_excess_pp": round(f - r["orig"]["filter"], 2),
                    "paired_rank": round(float(((pf > of) + 0.5 * (pf == of)).mean() * 100), 2)}
        ret = grp != "orig_0"
        r["pooled"] = block(ret)
        r["pooled_excl_lock"] = block(ret & ~np.isin(stem, list(lock)))
        r["by_group"] = {g: block(grp == g) for g in sorted(set(grp[ret]))}
        R[n] = r
    json.dump(R, open(HERE / "results.json", "w"), indent=1)
    L = ["# ALIPAIR zero-shot (FF++-only three-way models on Alibaba commercial retouching pairs)", "",
         "v8.17 reference (retouching_benchmark_20260823): balanced 50.7–51.2 %, specificity 3.9–4.8 %, paired rank 62.6–66.1 %.", "",
         "| model | orig real/fake/filter | retouched real/fake/filter | balanced | paired excess (pp) | paired rank | excl. 440 lock: balanced / rank |",
         "|---|---|---|---|---|---|---|"]
    for n, r in R.items():
        o, q, e = r["orig"], r["pooled"], r["pooled_excl_lock"]
        L.append(f"| {n} | {o['real']}/{o['fake']}/{o['filter']} | {q['to_real']}/{q['to_fake']}/{q['to_filter']} | {q['balanced_acc']} | "
                 f"{q['paired_excess_pp']} | {q['paired_rank']} | {e['balanced_acc']} / {e['paired_rank']} |")
    L += ["", "## Per type × level (paired excess pp / paired rank %)", "",
          "| model | " + " | ".join(f"{t[:6]}{lv}" for t in TYPES for lv in LEVELS) + " |", "|---|" + "---|" * 12]
    for n, r in R.items():
        L.append(f"| {n} | " + " | ".join(f"{r['by_group'][f'{t}_{lv}']['paired_excess_pp']:+.0f} / {r['by_group'][f'{t}_{lv}']['paired_rank']:.0f}"
                                          for t in TYPES for lv in LEVELS) + " |")
    (HERE / "RESULTS.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analyse":
        analyse()
    else:
        main()
