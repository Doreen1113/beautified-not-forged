"""Explanation bars E1-E5 (PRE_DECLARED §5) on held-out part edits (FF++ test partition) and filter test frames.

For each model: evidence map (evidence head for MASK/CGD; Grad-CAM / Grad-CAM++ / Score-CAM for HYBPE, all at the last
conv block), thresholded to a region of the same area as the GT mask (area-matched, so IoU is comparable across
methods), then:
  IoU7   : 7x7 cell IoU against GT;  IoUpx : pixel IoU
  flip_pred : P(fake) argmax leaves `fake` after restoring the predicted region to the source frame
  flip_comp : same after restoring the complement;   flip_rand : area-matched random square
Only correctly detected items count (as pre-declared). Also E5 on filter test frames (p_filter drop when restoring
the predicted region).

python eval_cgd_explain.py --arm CGD [--seed 20260928] [--mech donor,sd] -> explain_<ARM>_s<seed>.json
"""
import argparse
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

HERE = Path(__file__).resolve().parent
BASE = Path(os.environ.get("AIGC_BASE", r"C:\My_Project\AIGC"))
sys.path.insert(0, str(HERE))
from train_cgd import CGDNet, MODEL, NORM, SIZE, remap  # noqa: E402

PE = BASE / "results/research/partedit_20260927"
UNI = BASE / "results/research/ffpp_unified_20260925"
TEST_REAL = BASE / "FaceForensics_protocol_frames/test/real"
TF = transforms.Compose([transforms.Resize((SIZE, SIZE)), transforms.ToTensor(), NORM])


def load_items(mechs):
    out = []
    for mech in mechs:
        f = PE / f"manifest_test_{mech}.tsv"
        if not f.is_file():
            continue
        for l in f.read_text(encoding="utf-8").splitlines()[1:]:
            c = l.split("\t")
            out.append({"x": remap(c[0]), "m": remap(c[4]), "x0": remap(c[5]), "part": c[6], "mech": mech})
    return out


def filter_items(n=600, seed=0):
    rows = [l.split("\t") for l in (UNI / "ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    fl = [r for r in rows if r[1] == "2"]
    rng = np.random.default_rng(seed); rng.shuffle(fl)
    out = []
    for r in fl[:n]:
        b = os.path.basename(r[0]); vid, fr = b.split("__")[:2]
        q = TEST_REAL / f"{vid}__{fr}.jpg"
        if q.is_file():
            out.append({"x": remap(r[0]), "x0": str(q), "src": r[3]})
    return out


# ---------------------------------------------------------------- evidence maps
class CAM:
    def __init__(self, net):
        self.net = net; self.a = None; self.g = None
        blk = net.m.conv_head
        blk.register_forward_hook(lambda m, i, o: setattr(self, "a", o))
        blk.register_full_backward_hook(lambda m, gi, go: setattr(self, "g", go[0]))

    def gradcam(self, x, cls, pp=False):
        x = x.clone().requires_grad_(True)
        lo, _ = self.net(x); self.net.zero_grad(); lo[0, cls].backward()
        a, g = self.a[0], self.g[0]
        if pp:  # Grad-CAM++
            g2, g3 = g ** 2, g ** 3
            alpha = g2 / (2 * g2 + (a.sum((1, 2), keepdim=True) * g3) + 1e-8)
            w = (alpha * F.relu(g)).sum((1, 2))
        else:
            w = g.mean((1, 2))
        return F.relu((w[:, None, None] * a).sum(0)).detach()

    @torch.no_grad()
    def scorecam(self, x, cls, k=32):
        lo, _ = self.net(x); a = self.a[0]
        idx = a.flatten(1).abs().sum(1).topk(k).indices
        base = torch.softmax(lo, 1)[0, cls]
        maps = F.interpolate(a[idx][:, None], size=x.shape[-2:], mode="bilinear", align_corners=False)[:, 0]
        maps = (maps - maps.flatten(1).min(1)[0][:, None, None]) / (maps.flatten(1).max(1)[0][:, None, None] - maps.flatten(1).min(1)[0][:, None, None] + 1e-8)
        sc = torch.softmax(self.net(x * maps[:, None])[0], 1)[:, cls] - base
        return F.relu((F.relu(sc)[:, None, None] * a[idx]).sum(0))


def region_from_map(cam, area_frac, S=SIZE):
    cam = F.interpolate(cam[None, None].float(), size=(S, S), mode="bilinear", align_corners=False)[0, 0]
    k = max(1, int(round(area_frac * S * S)))
    thr = cam.flatten().topk(k).values[-1]
    return (cam >= thr).float()


_K25 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))


def footprint_gt(im, im0):
    """Addendum 2: true edit footprint = |x-x0|>6 dilated by the feather width (native res), resized to SIZE."""
    a, a0 = np.array(im).astype(np.float32), np.array(im0).astype(np.float32)
    fp = cv2.dilate((np.abs(a - a0).max(2) > 6).astype(np.uint8), _K25)
    return torch.from_numpy(cv2.resize(fp.astype(np.float32), (SIZE, SIZE), interpolation=cv2.INTER_AREA) > 0.5).float().cuda()


def dilate_t(mask):
    return torch.from_numpy(cv2.dilate(mask.cpu().numpy().astype(np.uint8), _K25)).float().cuda()


def centre_prior(area, S=SIZE):
    yy, xx = torch.meshgrid(torch.linspace(-1, 1, S), torch.linspace(-1, 1, S), indexing="ij")
    return region_from_map(torch.exp(-(yy ** 2 + xx ** 2) / 0.3).cuda(), area)


def iou(a, b):
    a, b = a.bool(), b.bool(); u = (a | b).sum().item()
    return (a & b).sum().item() / u if u else 0.0


def iou7(a, b):
    return iou(F.adaptive_avg_pool2d(a[None, None], 7)[0, 0] > 0.5, F.adaptive_avg_pool2d(b[None, None], 7)[0, 0] > 0.5)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, choices=["HYPBE", "HYBPE", "MASK", "MASKD", "CGD", "CGDD", "CGD-ZERO", "CGD-BLUR", "CGD-NOHOLD", "RU3E", "RU4E", "RUCLIPE", "RUCLIPE4"])
    ap.add_argument("--seed", type=int, default=20260928)
    ap.add_argument("--mech", default="donor,sd,sdxl")
    ap.add_argument("--n", type=int, default=100000)
    a = ap.parse_args()
    if a.arm in ("RU3E", "RU3E-repvit", "RU4E"):
        # RU3-E (retouch_unified_20260929/train_ru3.py): same input size/normalisation as CGDNet (380, 0.5); adapt to (logits, ev)
        sys.path.insert(0, str(BASE / "results/research/retouch_unified_20260929")); from train_ru3 import RUNet3
        arch = "repvit" if a.arm.endswith("repvit") else "effb4"
        inner = RUNet3(arch, head=True); inner.load_state_dict(torch.load(BASE / f"checkpoints/research/retouch_unified_20260929/ru_{a.arm.lower()}_{arch}_s{a.seed}.pth", map_location="cpu"))
        class _W(torch.nn.Module):
            head = True
            def __init__(self, m): super().__init__(); self.m = m
            def forward(self, x):
                o = self.m(x); return o[0], o[3]
        net = _W(inner).cuda().eval(); cam = None
    elif a.arm in ("RUCLIPE", "RUCLIPE4"):
        # RU-CLIP-E: the harness composites at 380 px with 0.5 normalisation; the wrapper converts to 224 px + CLIP normalisation
        sys.path.insert(0, str(BASE / "results/research/retouch_unified_20260929")); from train_ru_clip import load_clip
        from train_ru3 import CLIP_MEAN, CLIP_STD
        inner = load_clip(f"clipe{'4' if a.arm.endswith('4') else ''}_s{a.seed}", head=True)
        class _WC(torch.nn.Module):
            head = True
            def __init__(self, m):
                super().__init__(); self.m = m
                self.register_buffer("mu", torch.tensor(CLIP_MEAN).view(1, 3, 1, 1)); self.register_buffer("sd", torch.tensor(CLIP_STD).view(1, 3, 1, 1))
            def forward(self, x):
                x = F.interpolate(x * 0.5 + 0.5, size=(224, 224), mode="bilinear", align_corners=False); x = (x - self.mu) / self.sd
                o = self.m(x); return o[0], o[3]
        net = _WC(inner).cuda().eval(); cam = None
    else:
        net = CGDNet(head=a.arm != "HYBPE")
        net.load_state_dict(torch.load(BASE / f"checkpoints/research/cgd_20260927/cgd_{a.arm}_s{a.seed}.pth", map_location="cpu"))
        net = net.cuda().eval(); cam = CAM(net)
    methods = ["evidence"] if net.head else ["gradcam", "gradcampp", "scorecam"]
    rng = np.random.default_rng(0)
    R = {}
    for mech in a.mech.split(","):
        items = load_items([mech])[: a.n]
        if not items:
            continue
        acc = {m: {"iou7": [], "ioupx": [], "flip_pred": [], "flip_comp": [], "flip_rand": [], "flip_centre": [], "iou7_centre": []} for m in methods}
        ceil = []
        n_det = 0
        for it in items:
            x = TF(Image.open(it["x"]).convert("RGB"))[None].cuda()
            im = Image.open(it["x"]).convert("RGB"); im0 = Image.open(it["x0"]).convert("RGB").resize(im.size)
            x0 = TF(im0)[None].cuda()
            gt = footprint_gt(im, im0)
            with torch.no_grad():
                lo, ev = net(x)
            if lo.argmax().item() != 1:
                continue
            n_det += 1
            area = gt.mean().item()
            with torch.no_grad():
                ceil.append(net((1 - gt[None, None]) * x + gt[None, None] * x0)[0].argmax().item() != 1)
                cp = centre_prior(area)
            for m in methods:
                if m == "evidence":
                    e = torch.sigmoid(ev[0, 0]).float()
                elif m == "gradcam":
                    e = cam.gradcam(x, 1)
                elif m == "gradcampp":
                    e = cam.gradcam(x, 1, pp=True)
                else:
                    e = cam.scorecam(x, 1)
                reg = region_from_map(e, area)
                s = int(np.sqrt(area) * SIZE); yy, xx = rng.integers(0, SIZE - s + 1, 2)
                rnd = torch.zeros(SIZE, SIZE, device="cuda"); rnd[yy:yy + s, xx:xx + s] = 1
                with torch.no_grad():
                    def dec(mask):
                        xr = (1 - mask) * x + mask * x0
                        return net(xr)[0].argmax().item() != 1
                    acc[m]["iou7"].append(iou7(reg, gt)); acc[m]["ioupx"].append(iou(reg, gt))
                    regd = dilate_t(reg)
                    acc[m]["flip_pred"].append(dec(regd[None, None])); acc[m]["flip_comp"].append(dec(1 - regd[None, None]))
                    acc[m]["flip_rand"].append(dec(dilate_t(rnd)[None, None]))
                    acc[m]["flip_centre"].append(dec(dilate_t(cp)[None, None])); acc[m]["iou7_centre"].append(iou7(cp, gt))
        R[mech] = {"n_items": len(items), "n_detected": n_det, "detect_rate": n_det / len(items), "flip_ceiling_gt": float(np.mean(ceil)) if ceil else None,
                   **{m: {k: float(np.mean(v)) if v else None for k, v in d.items()} for m, d in acc.items()}}
        print(mech, json.dumps(R[mech], indent=None), flush=True)
    # E5: filters
    fi = filter_items(); drops = {m: [] for m in methods}; nd = 0
    for it in fi:
        x = TF(Image.open(it["x"]).convert("RGB"))[None].cuda()
        x0 = TF(Image.open(it["x0"]).convert("RGB").resize(Image.open(it["x"]).size))[None].cuda()
        with torch.no_grad():
            lo, ev = net(x)
        if lo.argmax().item() != 2:
            continue
        nd += 1; p0 = torch.softmax(lo, 1)[0, 2].item()
        for m in methods:
            e = torch.sigmoid(ev[0, 0]).float() if m == "evidence" else (cam.gradcam(x, 2) if m == "gradcam" else cam.gradcam(x, 2, pp=True) if m == "gradcampp" else cam.scorecam(x, 2))
            reg = region_from_map(e, 0.25)
            with torch.no_grad():
                p1 = torch.softmax(net((1 - reg) * x + reg * x0)[0], 1)[0, 2].item()
            drops[m].append(p0 - p1)
    R["filter_E5"] = {"n_detected": nd, **{m: float(np.mean(v)) if v else None for m, v in drops.items()}}
    print("filter_E5", R["filter_E5"], flush=True)
    json.dump(R, open(HERE / f"explain_{a.arm}_s{a.seed}.json", "w"), indent=1)


if __name__ == "__main__":
    main()
