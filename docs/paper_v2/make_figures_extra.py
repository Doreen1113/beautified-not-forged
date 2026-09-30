"""Qualitative / explainability figures for docs/paper_v2 (read-only inference; values from results files).

fig_qual  : Celeb-DF-B beautified examples, SBI decision vs ours, with Grad-CAM of ours (incl. a failure case)
fig_cam   : Grad-CAM of ours on FF++ test: fake / filter / beautified fake
fig_tsne  : penultimate-feature t-SNE, our binary SBI-recipe model vs our three-way HYB, same FF++ test images

python docs/paper_v2/make_figures_extra.py
"""
import json
import sys
from pathlib import Path

import cv2
import matplotlib
import numpy as np
import timm
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

BASE = Path(r"C:\My_Project\AIGC")
sys.path.insert(0, str(BASE / "docs/paper_v2"))
import make_figures as MF  # noqa: E402  shared style (rcParams, palette, save)

R = BASE / "results/research"
CDFB = R / "celebdfb_v2_20260927"
EFFB4 = "tf_efficientnet_b4.ap_in1k"
HYB_CK = BASE / "checkpoints/research/sbiscale_20260926/sbiscale_HYB_s20260927.pth"
SBIL_CK = BASE / "checkpoints/research/sbiscale_20260926/sbiscale_SBI.pth"
T = transforms.Compose([transforms.Resize((380, 380)), transforms.ToTensor(), transforms.Normalize([0.5] * 3, [0.5] * 3)])
CLS = ["real", "fake", "filter"]
COL = {"real": "#2f7d32", "fake": "#B64342", "filter": "#8a6d00"}


def load(ck, k):
    m = timm.create_model(EFFB4, pretrained=False, num_classes=k)
    m.load_state_dict(torch.load(ck, map_location="cpu")); return m.cuda().eval()


def gradcam(m, path, cls=None):
    """Grad-CAM on the last conv block (timm EfficientNet: conv_head)."""
    feats, grads = {}, {}
    h1 = m.conv_head.register_forward_hook(lambda mod, i, o: feats.__setitem__("a", o))
    h2 = m.conv_head.register_full_backward_hook(lambda mod, gi, go: grads.__setitem__("g", go[0]))
    x = T(Image.open(path).convert("RGB"))[None].cuda().requires_grad_(True)
    lo = m(x); p = torch.softmax(lo, 1)[0].detach().cpu().numpy()
    c = int(lo.argmax()) if cls is None else cls
    m.zero_grad(); lo[0, c].backward()
    a, g = feats["a"][0], grads["g"][0]
    cam = F.relu((g.mean((1, 2))[:, None, None] * a).sum(0)).detach().cpu().numpy()
    h1.remove(); h2.remove()
    cam = cam / (cam.max() + 1e-8)
    return p, c, cam


def overlay(path, cam, size=(190, 230)):
    im = np.array(Image.open(path).convert("RGB").resize(size))
    hm = cv2.applyColorMap((cv2.resize(cam, size) * 255).astype(np.uint8), cv2.COLORMAP_JET)[..., ::-1]
    return (0.55 * im + 0.45 * hm).astype(np.uint8), im


def fig_qual():
    rows = [l.split("\t") for l in (BASE / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    paths = np.array([r[0] for r in rows]); folder = np.array([r[3] for r in rows]); vid = np.array([r[2] for r in rows])
    ann = {}
    for l in (BASE / "external_data/celebdfb/Celeb-DF-B/annotation.csv").read_text(encoding="utf-8").splitlines()[1:]:
        n_, t_, p_ = l.strip().split(";"); ann[(n_[:-4], t_)] = p_
    preset = np.array([r[4] or ann.get((r[2], "fake"), "") for r in rows])
    sbi = np.load(CDFB / "scores_v3/sbi.npz")["p"][:, 1]
    hyb = np.load(CDFB / "scores_v3/HYB-L-s2.npz")["p"]; ah = hyb.argmax(1)
    thr = json.load(open(CDFB / "results_v3.json"))["sbi"]["threshold"]
    rng = np.random.default_rng(3)

    def pick(mask, n):
        idx = np.where(mask)[0]; out, seen = [], set()
        for i in rng.permutation(idx):
            if vid[i] not in seen:
                out.append(i); seen.add(vid[i])
            if len(out) == n:
                break
        return out
    sel = [("beautified genuine", i) for i in pick((folder == "real_beautified") & (sbi > thr) & (ah == 2), 3)]
    sel += [("beautified deepfake", i) for i in pick((folder == "synthesis_beautified") & (sbi <= thr) & (ah == 1), 3)]
    sel += [("failure: beautified deepfake", i) for i in pick((folder == "synthesis_beautified") & (preset == "california_dreamin") & (ah == 0), 1)]
    m = load(HYB_CK, 3)
    fig, axes = plt.subplots(1, len(sel), figsize=(7.1, 1.75), squeeze=False)
    for j, (kind, i) in enumerate(sel):
        p, c, cam = gradcam(m, paths[i])
        ov, im = overlay(paths[i], cam)
        sbi_dec = "fake" if sbi[i] > thr else "real"
        truth_ok_sbi = (sbi_dec == "fake") == ("deepfake" in kind)
        a = axes[0, j]; a.imshow(im)
        a.set_title(kind.replace("beautified ", "beautified\n"), fontsize=6.6, color=MF.INK)
        a.text(0.5, -0.06, f"SBI: {sbi_dec} ({sbi[i]:.2f})", fontsize=6.4, ha="center", va="top", transform=a.transAxes,
               color=MF.C_OURS if truth_ok_sbi else MF.C_SBI)
        a.text(0.5, -0.22, f"Ours: {CLS[c]} ({p[c]:.2f})", fontsize=6.4, ha="center", va="top", transform=a.transAxes,
               color=COL[CLS[c]], fontweight="bold")
        a.set_xticks([]); a.set_yticks([])
        for s in a.spines.values():
            s.set_visible(True); s.set_linewidth(0.6); s.set_color(MF.MUTED)
    fig.tight_layout(pad=0.4, rect=(0, 0.1, 1, 1))
    MF.save(fig, "fig_qual")
    json.dump([{"kind": k, "path": str(paths[i]), "preset": str(preset[i]), "sbi": float(sbi[i]), "ours": hyb[i].tolist()} for k, i in sel],
              open(MF.OUT / "fig_qual_items.json", "w"), indent=1)


def ffpp_sets(n=300, seed=0):
    rng = np.random.default_rng(seed)
    uni = R / "ffpp_unified_20260925"
    rows = [l.split("\t") for l in (uni / "ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    by = {k: [r[0] for r in rows if r[1] == str(k)] for k in range(3)}
    esc = [l.split("\t")[0] for l in (BASE / "ffpp_escape_cache/manifest.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    ho = [l.split("\t")[0] for l in (uni / "ffpp3_test_heldout_filter.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    S = {"real": by[0], "fake": by[1], "filter (seen)": by[2], "beautified fake": esc, "filter (unseen)": ho}
    return {k: list(rng.choice(v, min(n, len(v)), replace=False)) for k, v in S.items()}


def fig_cam():
    S = ffpp_sets(40, seed=5)
    m = load(HYB_CK, 3)
    picks = [("fake", S["fake"]), ("filter (seen)", S["filter (seen)"]), ("beautified fake", S["beautified fake"])]
    fig, axes = plt.subplots(2, 6, figsize=(7.1, 2.75))
    j = 0
    for name, lst in picks:
        want = 2 if name == "filter (seen)" else 1
        got = 0
        for pth in lst:
            p, c, cam = gradcam(m, pth)
            if c != want:
                continue
            ov, im = overlay(pth, cam)
            axes[0, j].imshow(im); axes[1, j].imshow(ov)
            axes[0, j].set_title(name, fontsize=7)
            axes[1, j].set_xlabel(f"{CLS[c]} ({p[c]:.2f})", fontsize=6.6, color=COL[CLS[c]], fontweight="bold")
            j += 1; got += 1
            if got == 2:
                break
    for a in axes.ravel():
        a.set_xticks([]); a.set_yticks([])
    fig.tight_layout(pad=0.4)
    MF.save(fig, "fig_cam")


@torch.no_grad()
def feats(m, paths):
    out = []
    for i in range(0, len(paths), 48):
        x = torch.stack([T(Image.open(p).convert("RGB")) for p in paths[i:i + 48]]).cuda()
        with torch.autocast("cuda", dtype=torch.bfloat16):
            out.append(m.forward_head(m.forward_features(x), pre_logits=True).float().cpu())
    return torch.cat(out).numpy()


@torch.no_grad()
def feats_official_sbi(paths):
    """Official SBI checkpoint (efficientnet_pytorch EffNet-B4, /255 input, no normalisation) -- pooled features."""
    sys.path.insert(0, str(R / "external_baselines_20260905"))
    import zoo
    net = zoo.SBI().m
    tf = transforms.Compose([transforms.Resize((380, 380)), transforms.ToTensor()])
    out = []
    for i in range(0, len(paths), 32):
        x = torch.stack([tf(Image.open(q).convert("RGB")) for q in paths[i:i + 32]]).to(next(net.parameters()).device)
        f = net.extract_features(x)
        out.append(torch.nn.functional.adaptive_avg_pool2d(f, 1).flatten(1).float().cpu())
    return torch.cat(out).numpy()


def fig_tsne():
    from sklearn.manifold import TSNE
    S = ffpp_sets(300, seed=1)
    names = list(S)
    cols = {"real": "#2f7d32", "fake": "#B64342", "filter (seen)": "#d4a017", "beautified fake": "#6b1d1c",
            "filter (unseen)": "#3775BA"}
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.1))
    stats = {}
    for ax, (title, ck, k) in zip(axes, [("(a) binary SBI (official checkpoint, EffNet-B4)", None, 2),
                                          ("(b) three-way HYB (ours, EffNet-B4)", HYB_CK, 3)]):
        if ck is None:
            X = np.concatenate([feats_official_sbi(S[n]) for n in names]); m = None
        else:
            m = load(ck, k)
            X = np.concatenate([feats(m, S[n]) for n in names])
        y = np.concatenate([[i] * len(S[n]) for i, n in enumerate(names)])
        Z = TSNE(2, perplexity=35, init="pca", random_state=0).fit_transform(X)
        for i, n in enumerate(names):
            ax.scatter(Z[y == i, 0], Z[y == i, 1], s=4, color=cols[n], alpha=0.75, lw=0, label=n)
        ax.set_title(title); ax.set_xticks([]); ax.set_yticks([])
        for s in ("left", "bottom"):
            ax.spines[s].set_visible(False)
        # quantitative companion: 10-NN purity of beautified fakes w.r.t. the fake class
        from sklearn.neighbors import NearestNeighbors
        ref = np.isin(y, [0, 1, 2]); nn = NearestNeighbors(n_neighbors=10).fit(X[ref])
        _, ind = nn.kneighbors(X[y == 3]); yr = y[ref]
        stats[title] = {"beautified_fake_knn_fake_frac": float((yr[ind] == 1).mean()),
                        "beautified_fake_knn_real_frac": float((yr[ind] == 0).mean())}
        del m; torch.cuda.empty_cache()
    axes[1].legend(loc="center left", bbox_to_anchor=(1.0, 0.5), markerscale=3, fontsize=7)
    fig.tight_layout()
    MF.save(fig, "fig_tsne")
    json.dump(stats, open(MF.OUT / "fig_tsne_stats.json", "w"), indent=1); print(stats)


if __name__ == "__main__":
    which = sys.argv[1:] or ["qual", "cam", "tsne"]
    for w in which:
        {"qual": fig_qual, "cam": fig_cam, "tsne": fig_tsne}[w](); print(w, "done")
