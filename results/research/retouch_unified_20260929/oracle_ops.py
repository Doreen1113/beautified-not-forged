"""Addendum 59: single-image detectability ceiling of each beautification operation (oracle setting).
For each Alibaba operation at level 90 (and 30 for the operations that pass), a dedicated binary classifier
(timm efficientnet_b0, ImageNet init) is trained to tell the vendor render from untouched FFHQ originals, in the most
favourable setting: same vendor, same level, lossless PNG, 384 px face crop (ffhq_boxes), identity-disjoint split by FFHQ
index (70 % train / 30 % test, seed 0); in training both the original and the render of a training face are used.
Test: unpaired AUROC (renders vs originals of the held-out faces) and paired rank; robustness: the same test set after JPEG
q90 + resize to 256 px and back (a social-media round trip). Smoothing is the positive control.
python oracle_ops.py [op ...]   (default EyeEnlarging_90 FaceLifting_90 Whitening_90 Smoothing_90) -> oracle_ops.json, ORACLE_OPS.md"""
import io
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC")
ORIG = B / "ffhq_originals/Part2"; ALI = B / "FFHQ_ali_process"; SIZE = 384; EPOCHS = 6; BS = 24
BOXES = json.loads((HERE / "ffhq_boxes.json").read_text())   # module level: DataLoader workers re-import on Windows


def crop(stem, path):
    box = BOXES[stem]; im = Image.open(path).convert("RGB").crop(tuple(box)); return im.resize((SIZE, SIZE), Image.BICUBIC)


def degrade(im):
    small = im.resize((256, 256), Image.BICUBIC); buf = io.BytesIO(); small.save(buf, "JPEG", quality=90)
    return Image.open(io.BytesIO(buf.getvalue())).convert("RGB").resize((SIZE, SIZE), Image.BICUBIC)


class DS(Dataset):
    def __init__(self, items, train, deg=False):
        self.items, self.train, self.deg = items, train, deg

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        stem, path, y = self.items[i]; im = crop(stem, path)
        if self.deg:
            im = degrade(im)
        a = np.asarray(im, np.float32) / 255.0
        if self.train and np.random.rand() < 0.5:
            a = a[:, ::-1]
        a = (a - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
        return torch.from_numpy(np.ascontiguousarray(a.transpose(2, 0, 1))).float(), y, i


def run(op):
    import timm
    from sklearn.metrics import roc_auc_score
    stems = [s for s in sorted(p.stem for p in ORIG.glob("*.png")) if s in BOXES and (ALI / op / f"{(int(s) // 1000) * 1000}" / f"{s}.png").is_file()]
    rng = np.random.default_rng(0); perm = rng.permutation(len(stems)); ntr = int(0.7 * len(stems))
    tr, te = [stems[i] for i in perm[:ntr]], [stems[i] for i in perm[ntr:]]
    rp = lambda s: ALI / op / f"{(int(s) // 1000) * 1000}" / f"{s}.png"
    train = [(s, ORIG / f"{s}.png", 0) for s in tr] + [(s, rp(s), 1) for s in tr]
    test = [(s, ORIG / f"{s}.png", 0) for s in te] + [(s, rp(s), 1) for s in te]
    torch.manual_seed(0); m = timm.create_model("efficientnet_b0", pretrained=True, num_classes=1).cuda()
    opt = torch.optim.AdamW(m.parameters(), lr=3e-4, weight_decay=1e-4); sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, EPOCHS)
    for ep in range(EPOCHS):
        m.train()
        for x, y, _ in DataLoader(DS(train, True), batch_size=BS, shuffle=True, num_workers=6, drop_last=True):
            with torch.autocast("cuda", dtype=torch.bfloat16):
                loss = torch.nn.functional.binary_cross_entropy_with_logits(m(x.cuda()).float().squeeze(1), y.float().cuda())
            opt.zero_grad(); loss.backward(); opt.step()
        sched.step(); print(op, "epoch", ep, round(float(loss), 4), flush=True)
    out = {}
    m.eval()
    for name, deg in (("lossless", False), ("jpeg90_resize256", True)):
        s = np.zeros(len(test), np.float32)
        with torch.no_grad():
            for x, _, i in DataLoader(DS(test, False, deg), batch_size=48, num_workers=6):
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    s[i.numpy()] = m(x.cuda()).float().squeeze(1).cpu().numpy()
        y = np.array([t[2] for t in test]); n = len(te)
        auc = roc_auc_score(y, s); paired = float((s[n:] > s[:n]).mean() * 100)
        bs = [roc_auc_score(np.r_[np.zeros(len(b)), np.ones(len(b))], np.r_[s[:n][b], s[n:][b]]) for b in [rng.integers(0, n, n) for _ in range(500)]]
        out[name] = {"auroc": round(float(auc), 4), "auroc_ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)], "paired_rank": round(paired, 1)}
    out["n_train_faces"], out["n_test_faces"] = len(tr), len(te)
    out["cross"] = {}   # Addendum 59 amendment 1: score the held-out renders of every operation with this classifier
    for other in ["EyeEnlarging_90", "FaceLifting_90", "Whitening_90", "Smoothing_90"]:
        rpo = lambda s_, o_=other: ALI / o_ / f"{(int(s_) // 1000) * 1000}" / f"{s_}.png"
        te_o = [s_ for s_ in te if rpo(s_).is_file()]
        items = [(s_, ORIG / f"{s_}.png", 0) for s_ in te_o] + [(s_, rpo(s_), 1) for s_ in te_o]
        sc = np.zeros(len(items), np.float32)
        with torch.no_grad():
            for x, _, i in DataLoader(DS(items, False), batch_size=48, num_workers=6):
                with torch.autocast("cuda", dtype=torch.bfloat16):
                    sc[i.numpy()] = m(x.cuda()).float().squeeze(1).cpu().numpy()
        yy = np.array([t[2] for t in items]); out["cross"][other] = round(float(roc_auc_score(yy, sc)), 4)
    torch.save(m.state_dict(), HERE / f"oracle_{op}.pth")
    print(op, json.dumps(out), flush=True); return out


def main():
    ops = sys.argv[1:] or ["EyeEnlarging_90", "FaceLifting_90", "Whitening_90", "Smoothing_90"]
    f = HERE / "oracle_ops.json"; res = json.loads(f.read_text()) if f.is_file() else {}
    for op in ops:
        res[op] = run(op); f.write_text(json.dumps(res, indent=1))
    L = ["# Addendum 59: single-image detectability ceiling (dedicated EfficientNet-B0 per operation, Alibaba, identity-disjoint)", "",
         "| operation | AUROC lossless [CI] | paired rank % | AUROC after JPEG q90 + resize 256 [CI] | paired rank % |", "|---|---|---|---|---|"]
    for op, r in res.items():
        L.append(f"| {op} | {r['lossless']['auroc']} {r['lossless']['auroc_ci']} | {r['lossless']['paired_rank']} | {r['jpeg90_resize256']['auroc']} {r['jpeg90_resize256']['auroc_ci']} | {r['jpeg90_resize256']['paired_rank']} |")
    ops4 = ["EyeEnlarging_90", "FaceLifting_90", "Whitening_90", "Smoothing_90"]
    if all("cross" in res.get(o, {}) for o in ops4):
        L += ["", "Cross-operation AUROC (rows: classifier trained on; columns: held-out renders of; diagonal = own operation):", "",
              "| trained on / tested on | " + " | ".join(ops4) + " |", "|---" * 5 + "|"]
        for o in ops4:
            L.append(f"| {o} | " + " | ".join(str(res[o]["cross"][c]) for c in ops4) + " |")
    (HERE / "ORACLE_OPS.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    main()
