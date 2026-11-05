"""Addendum 60: dedicated operation classifiers trained on the training vendors (Megvii + Tencent single-operation
components, FFHQ Part7) and tested on Alibaba (FFHQ Part2, never trained on).
python xvendor_ops.py [op ...]   (default white eye jaw smooth) -> xvendor_ops.json, XVENDOR_OPS.md"""
import io
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC")
SIZE = 384; EPOCHS = 6; BS = 24; N_PER_CLASS = 7000
BOXES = json.loads((HERE / "ffhq_boxes.json").read_text())
ALI_OP = {"eye": "EyeEnlarging", "jaw": "FaceLifting", "white": "Whitening", "smooth": "Smoothing"}
TRAIN_STEMS = None


def rows_train(op):
    """(path, box_in_that_image, label); originals are reduced to 512 px first, like the components."""
    man = [l.split("\t") for l in (HERE / "manifest_train.tsv").read_text(encoding="utf-8").splitlines()[1:]]
    orig = [(r[0], None, 0) for r in man if r[2] == "ffhq_orig"]
    comp = [(r[0], tuple(int(v) for v in r[3].split()), 1) for r in man if r[2] == "vendor_single" and f"\\{op}\\" in r[0]]
    rng = np.random.default_rng(0)
    comp = [comp[i] for i in rng.choice(len(comp), min(N_PER_CLASS, len(comp)), replace=False)]
    return orig + comp


def load(path, box):
    im = Image.open(path).convert("RGB")
    if box is None:   # an FFHQ original (1024 px): bring to the 512 px scale of the components, then crop its own box / 2
        stem = Path(path).stem; b = BOXES[stem]
        im = im.resize((512, 512), Image.LANCZOS); box = tuple(int(round(v / 2)) for v in b)
    return im.crop(box).resize((SIZE, SIZE), Image.BICUBIC)


def degrade(im):
    small = im.resize((256, 256), Image.BICUBIC); buf = io.BytesIO(); small.save(buf, "JPEG", quality=90)
    return Image.open(io.BytesIO(buf.getvalue())).convert("RGB").resize((SIZE, SIZE), Image.BICUBIC)


class DS(Dataset):
    def __init__(self, items, train, deg=False):
        self.items, self.train, self.deg = items, train, deg

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        path, box, y = self.items[i]; im = load(path, box)
        if self.deg:
            im = degrade(im)
        a = np.asarray(im, np.float32) / 255.0
        if self.train and np.random.rand() < 0.5:
            a = a[:, ::-1]
        a = (a - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
        return torch.from_numpy(np.ascontiguousarray(a.transpose(2, 0, 1))).float(), y, i


def ali_items(alias, level):
    """Alibaba test pairs at 512 px scale too (the vendor renders are 1024 px like the originals)."""
    orig = B / "ffhq_originals/Part2"; out = []
    for p in sorted(orig.glob("*.png")):
        s = p.stem; r = B / "FFHQ_ali_process" / f"{alias}_{level}" / f"{(int(s) // 1000) * 1000}" / f"{s}.png"
        if s in BOXES and r.is_file():
            out.append((s, p, r))
    return out


def score(m, items, deg=False):
    s = np.zeros(len(items), np.float32)
    with torch.no_grad():
        for x, _, i in DataLoader(DS(items, False, deg), batch_size=48, num_workers=6):
            with torch.autocast("cuda", dtype=torch.bfloat16):
                s[i.numpy()] = m(x.cuda()).float().squeeze(1).cpu().numpy()
    return s


def run(op):
    import timm
    from sklearn.metrics import roc_auc_score
    train = rows_train(op); print(op, "train", sum(t[2] == 0 for t in train), "orig /", sum(t[2] == 1 for t in train), "components", flush=True)
    torch.manual_seed(0); m = timm.create_model("efficientnet_b0", pretrained=True, num_classes=1).cuda()
    opt = torch.optim.AdamW(m.parameters(), lr=3e-4, weight_decay=1e-4); sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, EPOCHS)
    w = torch.tensor([sum(t[2] == 0 for t in train) / max(1, sum(t[2] == 1 for t in train))]).cuda()
    for ep in range(EPOCHS):
        m.train()
        for x, y, _ in DataLoader(DS(train, True), batch_size=BS, shuffle=True, num_workers=6, drop_last=True):
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss = torch.nn.functional.binary_cross_entropy_with_logits(m(x.cuda()).float().squeeze(1), y.float().cuda(), pos_weight=w)
            opt.zero_grad(); loss.backward(); opt.step()
        sched.step(); print(op, "epoch", ep, round(float(loss.detach()), 4), flush=True)
    m.eval(); torch.save(m.state_dict(), HERE / f"xvendor_{op}.pth"); rng = np.random.default_rng(0); out = {"levels": {}, "cross90": {}}
    base = ali_items(ALI_OP[op], 90); o_items = [(str(p), None, 0) for _, p, _ in base]; so = score(m, o_items); so_d = score(m, o_items, True)
    idx = {s: k for k, (s, _, _) in enumerate(base)}
    for lv in (30, 60, 90):
        pairs = ali_items(ALI_OP[op], lv); r_items = [(str(r), BOXES_ALI(s), 1) for s, _, r in pairs]; sr = score(m, r_items)
        k = np.array([idx[s] for s, _, _ in pairs]); y = np.r_[np.zeros(len(so)), np.ones(len(sr))]
        auc = roc_auc_score(y, np.r_[so, sr]); n = len(sr)
        bs = [roc_auc_score(np.r_[np.zeros(len(b)), np.ones(len(b))], np.r_[so[k][b], sr[b]]) for b in [rng.integers(0, n, n) for _ in range(500)]]
        d = {"auroc": round(float(auc), 4), "ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)], "paired_rank": round(float((sr > so[k]).mean() * 100), 1)}
        if lv == 90:
            srd = score(m, r_items, True); d["auroc_jpeg"] = round(float(roc_auc_score(y, np.r_[so_d, srd])), 4)
        out["levels"][lv] = d
    for other, alias in ALI_OP.items():
        pairs = ali_items(alias, 90); sr = score(m, [(str(r), BOXES_ALI(s), 1) for s, _, r in pairs])
        out["cross90"][other] = round(float(roc_auc_score(np.r_[np.zeros(len(so)), np.ones(len(sr))], np.r_[so, sr])), 4)
    print(op, json.dumps(out), flush=True); return out


def BOXES_ALI(stem):
    return None   # Alibaba renders are 1024 px pixel-aligned with their originals: same handling as an original (load() uses the stem's box)


def main():
    # Alibaba renders go through load() with box None, exactly like the FFHQ originals: 1024 -> 512 px, then the stem's box / 2
    ops = sys.argv[1:] or ["white", "eye", "jaw", "smooth"]
    f = HERE / "xvendor_ops.json"; res = json.loads(f.read_text()) if f.is_file() else {}
    for op in ops:
        res[op] = run(op); f.write_text(json.dumps(res, indent=1))
    L = ["# Addendum 60: dedicated operation classifiers, trained on Megvii + Tencent components (FFHQ Part7), tested on Alibaba (FFHQ Part2)", "",
         "| op | AUROC L30 | L60 | L90 [CI] | paired rank L90 % | L90 after JPEG | cross AUROC on other ops' L90 renders |", "|---|---|---|---|---|---|---|"]
    for op, r in res.items():
        lv = r["levels"]; key = lambda k: lv.get(k, lv.get(str(k)))
        L.append(f"| {op} | {key(30)['auroc']} | {key(60)['auroc']} | {key(90)['auroc']} {key(90)['ci']} | {key(90)['paired_rank']} | {key(90)['auroc_jpeg']} | {r['cross90']} |")
    (HERE / "XVENDOR_OPS.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    main()
