"""Addendum 52: published identity detectors (ICT, ICT-Ref; Dong et al. CVPR 2022) under smoothing.
Probe set, conditions, reference videos and readouts are those of Addendum 51 (id_ref_probe.py).
ICT code/weights: official repo github.com/LightDXY/ICT_DeepFake (release v0.1.0 ICT_Base.pth, ref.pkl;
RetinaFace Resnet50_Final.pth from the repo's Drive link), used unchanged. What is re-implemented here, and why:
  * get_face(): line-for-line copy of the repo's preprocess.py alignment (RetinaFace R50, 5-point similarity warp to the
    317x317 template with padding 30), made callable on an in-memory image instead of the hard-coded video loop.
  * the ViT: the repo subclasses timm==0.3.4 VisionTransformer (incompatible with torch 2.x). Rebuilt from timm's Block
    with the same parameter names; the released state dict loads with strict=True (no missing/unexpected key).
  * KNN_CUDA (k=1, Euclidean) replaced by torch.cdist argmin (same result).
  * ICT score = ||inner - outer||^2; ICT-Ref score = the repo's ict_eval.py formula (dist1*w1 + dist2*w2 + dist3*w3 with
    thres=thres2=tau=0.5, 0.75 sigmoid weights). Higher = forged.
python ict_probe.py embed   --ict-repo <ICT_DeepFake dir> --weights <dir with ICT_Base.pth, ref.pkl, retinaface/>
python ict_probe.py analyse --weights <dir>   -> ict_probe.json, ICT_PROBE.md"""
import argparse
import json
import sys
from functools import partial
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from id_ref_probe import CDF, CONDS, NREF_FR, NREF_VID, claimed  # noqa: E402

IMSIZE = 317
STD = (np.array([[85.82991, 115.7792], [169.0532, 114.3381], [127.574, 167.0006], [90.6964, 204.7014],
                 [167.3069, 203.3733]]) + 30) / 317 * IMSIZE


class ICT(nn.Module):
    """combface_base_patch8_112 of the repo (timm 0.3.4 ViT forward + outer token + shared BN + l2 norm)."""

    def __init__(self):
        super().__init__()
        from timm.models.vision_transformer import Block
        d = 384
        self.patch_embed = nn.Module(); self.patch_embed.proj = nn.Conv2d(3, d, 8, 8)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, d)); self.outer_token = nn.Parameter(torch.zeros(1, 1, d))
        self.pos_embed = nn.Parameter(torch.zeros(1, 14 * 14 + 2, d))
        self.blocks = nn.ModuleList([Block(d, 12, 4.0, qkv_bias=True, norm_layer=partial(nn.LayerNorm, eps=1e-6)) for _ in range(12)])
        self.norm = nn.LayerNorm(d, eps=1e-6); self.bn = nn.BatchNorm1d(d)

    def forward(self, x):
        B = x.shape[0]; x = self.patch_embed.proj(x).flatten(2).transpose(1, 2)
        x = torch.cat((self.cls_token.expand(B, -1, -1), self.outer_token.expand(B, -1, -1), x), 1) + self.pos_embed
        for b in self.blocks:
            x = b(x)
        x = self.norm(x); i, o = self.bn(x[:, 0].float()), self.bn(x[:, 1].float())
        return nn.functional.normalize(i, dim=1), nn.functional.normalize(o, dim=1)


class Aligner:
    def __init__(self, repo, wdir, dev):
        sys.path.insert(0, str(Path(repo))); sys.path.insert(0, str(Path(repo) / "align"))   # align/ first (its models, data), root for "align.utils"
        from data import cfg_re50
        from layers.functions.prior_box import PriorBox
        from models.retinaface import RetinaFace
        from utils.box_utils import decode, decode_landm
        from utils.nms.py_cpu_nms import py_cpu_nms
        self.PriorBox, self.decode, self.decode_landm, self.nms = PriorBox, decode, decode_landm, py_cpu_nms
        cfg = dict(cfg_re50); cfg["pretrain"] = False; self.cfg = cfg
        net = RetinaFace(cfg=cfg, phase="test")
        sd = torch.load(Path(wdir) / "retinaface" / "Resnet50_Final.pth", map_location="cpu", weights_only=True)
        sd = {k.split("module.", 1)[-1] if k.startswith("module.") else k: v for k, v in sd.items()}
        mk = net.load_state_dict(sd, strict=False); assert not mk.missing_keys, mk
        self.net = net.to(dev).eval(); self.dev = dev

    @torch.no_grad()
    def get_face(self, ori_img):
        """preprocess.py get_face (confidence 0.02, top_k 5000, nms 0.4, keep_top_k 750, resize=1); returns RGB 317x317 or None."""
        import skimage.transform
        height, width, _ = ori_img.shape
        if height > IMSIZE * 4 or width > IMSIZE * 4:
            me = max(height, width); height = int(height / (me / (IMSIZE * 4))); width = int(width / (me / (IMSIZE * 4)))
        if height < IMSIZE and width < IMSIZE:
            height, width = height * 2, width * 2
        ori_img = cv2.resize(ori_img, (width, height), cv2.INTER_LINEAR)
        img = np.float32(ori_img.copy()); ih, iw, _ = img.shape
        scale = torch.Tensor([iw, ih, iw, ih]).to(self.dev)
        img -= (104, 117, 123); img = torch.from_numpy(img.transpose(2, 0, 1)).unsqueeze(0).to(self.dev)
        loc, conf, landms = self.net(img)
        prior = self.PriorBox(self.cfg, image_size=(ih, iw)).forward().to(self.dev)
        boxes = (self.decode(loc.data.squeeze(0), prior, self.cfg["variance"]) * scale).cpu().numpy()
        scores = conf.squeeze(0).data.cpu().numpy()[:, 1]
        s1 = torch.Tensor([iw, ih] * 5).to(self.dev)
        landms = (self.decode_landm(landms.data.squeeze(0), prior, self.cfg["variance"]) * s1).cpu().numpy()
        inds = np.where(scores > 0.02)[0]; boxes, landms, scores = boxes[inds], landms[inds], scores[inds]
        order = scores.argsort()[::-1][:5000]; boxes, landms, scores = boxes[order], landms[order], scores[order]
        dets = np.hstack((boxes, scores[:, None])).astype(np.float32, copy=False); keep = self.nms(dets, 0.4)
        dets, landms = dets[keep][:750], landms[keep][:750]
        if len(landms) == 0:
            return None, 0.0
        tf = skimage.transform.estimate_transform("similarity", dst=landms[0].reshape(5, 2), src=STD)
        face = (skimage.transform.warp(ori_img, tf, output_shape=(IMSIZE, IMSIZE, 3)) * 255).astype(np.uint8)
        return face[:, :, ::-1].copy(), float(dets[0, 4])   # BGR -> RGB (the repo writes BGR with cv2, reads with PIL)


def ict_model(wdir, dev):
    m = ICT(); sd = torch.load(Path(wdir) / "ICT_Base.pth", map_location="cpu", weights_only=True)["model"]
    m.load_state_dict(sd, strict=True); return m.to(dev).eval()


def embed(a):
    from PIL import Image
    from torchvision import transforms as T
    dev = torch.device("cuda"); al = Aligner(a.ict_repo, a.weights, dev); net = ict_model(a.weights, dev)
    tf = T.Compose([T.Resize((112, 112)), T.ToTensor(), T.Normalize([0.5] * 3, [0.5] * 3)])

    @torch.no_grad()
    def emb(faces):
        x = torch.stack([tf(Image.fromarray(f)) for f in faces]).to(dev); i, o = net(x); return i.cpu().numpy(), o.cpu().numpy()

    m = json.loads((HERE / "smooth38_list.json").read_text()); vid = m["video"]
    keep = [i for i, v in enumerate(vid) if not v.startswith("YouTube") and claimed(v)]
    test = {l.split()[1].strip() for l in (CDF / "List_of_testing_videos.txt").read_text().splitlines() if l.strip()}
    ids = sorted({claimed(vid[i]) for i in keep}); RI, RO, RL = [], [], []; ref_log = {}
    for k in ids:   # same videos / frame indices as id_ref_probe.embed()
        vids = sorted(p for p in (CDF / "Celeb-real").glob(f"{k}_*.mp4") if f"Celeb-real/{p.name}" not in test)[:NREF_VID]; fs = []; nfr = 0
        for p in vids:
            cap = cv2.VideoCapture(str(p)); n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            for t in np.linspace(0, n - 1, NREF_FR + 2)[1:-1].astype(int):
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(t)); ok, fr = cap.read(); nfr += 1
                f = al.get_face(fr)[0] if ok else None
                if f is not None:
                    fs.append(f)
            cap.release()
        if fs:
            i, o = emb(fs); RI.append(i); RO.append(o); RL += [k] * len(fs)
        ref_log[k] = {"videos": len(vids), "frames": nfr, "aligned": len(fs)}; print(k, ref_log[k], flush=True)
    out = {"keep": np.array(keep), "ref_inner": np.concatenate(RI), "ref_outer": np.concatenate(RO), "ref_lab": np.array(RL)}
    for c in CONDS:
        I = np.full((len(keep), 384), np.nan, np.float32); O = I.copy(); sc = np.zeros(len(keep), np.float32); bf = np.full(len(keep), np.nan, np.float32)
        buf, bj = [], []
        for j, i in enumerate(keep):
            img = cv2.imread(m["paths"][c][i]); f, s = al.get_face(img) if img is not None else (None, 0.0); sc[j] = s
            if f is not None:
                bf[j] = float((f.max(2) == 0).mean()); buf.append(f); bj.append(j)
            if len(buf) == 128 or (j == len(keep) - 1 and buf):
                ii, oo = emb(buf); I[bj] = ii; O[bj] = oo; buf, bj = [], []
            if j % 500 == 0:
                print(c, j, flush=True)
        out[f"{c}_inner"], out[f"{c}_outer"], out[f"{c}_det"], out[f"{c}_border"] = I, O, sc, bf
    np.savez(HERE / "ict_emb.npz", **out); (HERE / "ict_ref_log.json").write_text(json.dumps(ref_log, indent=1))


def ict_ref_score(ei, eo, qi, qo):
    """ict_eval.py evaluate(): k=1 nearest neighbours in the reference set, then the weighted distance."""
    ei_t, eo_t, qi_t, qo_t = (torch.from_numpy(np.ascontiguousarray(x)).double() for x in (ei, eo, qi, qo))
    n_in = torch.cdist(ei_t, qi_t).argmin(1); n_out = torch.cdist(eo_t, qo_t).argmin(1)
    q2, r1 = qo_t[n_in], qi_t[n_in]; q1, r2 = qi_t[n_out], qo_t[n_out]
    d1 = ((ei_t - eo_t) ** 2).sum(1); d2 = ((eo_t - q2) ** 2).sum(1); d3 = ((ei_t - q1) ** 2).sum(1)
    w2 = 0.75 / (1 + torch.exp((((ei_t - r1) ** 2).sum(1) - 0.5) / 0.5)); w3 = 0.75 / (1 + torch.exp((((eo_t - r2) ** 2).sum(1) - 0.5) / 0.5))
    return (d1 * (2 - w2 - w3) + d2 * w2 + d3 * w3).numpy()


def analyse(a):
    from sklearn.metrics import roc_auc_score
    m = json.loads((HERE / "smooth38_list.json").read_text()); z = np.load(HERE / "ict_emb.npz"); zi = np.load(HERE / "id_ref_emb.npz")
    keep = z["keep"]; assert np.array_equal(keep, zi["keep"])
    y = np.array(m["y"])[keep]; vid = np.array(m["video"])[keep]; cl = np.array([claimed(v) for v in vid]); n = len(keep)
    R = dict(zip(zi["ref_ids"], zi["ref"])); has = np.array([c in R for c in cl])
    rel = torch.load(Path(a.weights) / "ref.pkl", map_location="cpu", weights_only=True)
    QI, QO, QL = z["ref_inner"], z["ref_outer"], z["ref_lab"]
    dets = {"clipe5b": "smooth38_clipe5b_s20260929.npz", "effort": "smooth38_effort.npz", "gend": "smooth38_gend.npz", "sbi": "smooth38_sbi.npz"}
    S = {}
    for c in CONDS:
        I, O = z[f"{c}_inner"], z[f"{c}_outer"]; okc = ~np.isnan(I[:, 0])
        for nm in ["ICT", "ICT-Ref (ours ref)", "ICT-Ref (released ref.pkl)", "ICT-Ref (claimed-id ref, exploratory)"]:
            S[(nm, c)] = np.full(n, np.nan)
        S[("ICT", c)][okc] = ((I[okc] - O[okc]) ** 2).sum(1)
        S[("ICT-Ref (ours ref)", c)][okc] = ict_ref_score(I[okc], O[okc], QI, QO)
        S[("ICT-Ref (released ref.pkl)", c)][okc] = ict_ref_score(I[okc], O[okc], rel["inner"].numpy(), rel["outer"].numpy())
        for k in np.unique(cl):
            jj = np.where(okc & (cl == k))[0]
            if len(jj) and (QL == k).any():
                S[("ICT-Ref (claimed-id ref, exploratory)", c)][jj] = ict_ref_score(I[jj], O[jj], QI[QL == k], QO[QL == k])
        e = zi[c]; S[("identity (ArcFace, Add.51)", c)] = np.array([1 - float(e[j] @ R[cl[j]]) if has[j] and not np.isnan(e[j, 0]) else np.nan for j in range(n)])
        for d, f in dets.items():
            S[(d, c)] = np.load(HERE / f)[c][keep].astype(float)
    names = ["ICT", "ICT-Ref (ours ref)", "ICT-Ref (released ref.pkl)", "ICT-Ref (claimed-id ref, exploratory)", "identity (ArcFace, Add.51)"] + list(dets)
    a51 = has & np.all([~np.isnan(S[("identity (ArcFace, Add.51)", c)]) for c in CONDS], 0) & np.all([~np.isnan(S[(d, c)]) for d in dets for c in CONDS], 0)
    ictok = np.all([~np.isnan(z[f"{c}_inner"][:, 0]) for c in CONDS], 0); ok = a51 & ictok
    weak = {c: round(float(((z[f"{c}_det"] > 0.02) & (z[f"{c}_det"] < 0.5)).mean() * 100), 2) for c in CONDS}
    res = {"n_addendum51": int(a51.sum()), "n": int(ok.sum()), "n_genuine": int((y[ok] == 0).sum()), "n_forged": int((y[ok] == 1).sum()),
           "ict_align_fail_pct": {c: {"all": round(float(np.isnan(z[f"{c}_inner"][:, 0]).mean() * 100), 2),
                                      "genuine": round(float(np.isnan(z[f"{c}_inner"][y == 0, 0]).mean() * 100), 2),
                                      "forged": round(float(np.isnan(z[f"{c}_inner"][y == 1, 0]).mean() * 100), 2)} for c in CONDS},
           "ict_weak_detection_pct(score<0.5)": weak,
           "aligned_black_border_pct_mean": {c: round(float(np.nanmean(z[f"{c}_border"]) * 100), 2) for c in CONDS},
           "ref": {"ours_frames": int(len(QL)), "ours_ids": int(len(np.unique(QL))), "released_frames": int(rel["inner"].shape[0])},
           "auc": {}, "op5": {}, "median": {}}
    tg = cl[ok]; ut = np.unique(tg); rng = np.random.default_rng(0); by = {t: np.where(tg == t)[0] for t in ut}
    BS = [np.concatenate([by[t] for t in rng.choice(ut, len(ut))]) for _ in range(500)]; yy = y[ok]
    for nm in names:
        res["auc"][nm] = {}; res["op5"][nm] = {}; res["median"][nm] = {}; d0 = S[(nm, "untreated")][ok]
        t = np.quantile(d0[yy == 0], 0.95)
        for c in CONDS:
            s = S[(nm, c)][ok]; bs = [roc_auc_score(yy[ii], s[ii]) - roc_auc_score(yy[ii], d0[ii]) for ii in BS if len(np.unique(yy[ii])) == 2]
            res["auc"][nm][c] = {"auc": round(float(roc_auc_score(yy, s)), 4), "drop": round(float(roc_auc_score(yy, s) - roc_auc_score(yy, d0)), 4),
                                 "drop_vs_untreated_ci": [round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]}
            res["op5"][nm][c] = {"fa": round(float((s[yy == 0] > t).mean() * 100), 1), "miss": round(float((s[yy == 1] <= t).mean() * 100), 1)}
            res["median"][nm][c] = {"genuine": round(float(np.median(s[yy == 0])), 4), "forged": round(float(np.median(s[yy == 1])), 4)}
    (HERE / "ict_probe.json").write_text(json.dumps(res, indent=1))
    L = [f"# Addendum 52: ICT / ICT-Ref under smoothing (Celeb-DF-v2 test, Celeb-real vs Celeb-synthesis; n {res['n']}: {res['n_genuine']} genuine / {res['n_forged']} forged; Addendum 51 set n {res['n_addendum51']} intersected with ICT alignment success in all five conditions)", "",
         f"ICT alignment failure % (of {n} probes): {json.dumps(res['ict_align_fail_pct'])}", "",
         f"Weak RetinaFace detections (0.02 < score < 0.5) %: {weak}; mean black-border share of the aligned 317 crop %: {res['aligned_black_border_pct_mean']}", "",
         f"Reference sets: ours {res['ref']['ours_frames']} aligned frames over {res['ref']['ours_ids']} identities (Addendum 51 videos/frames, ICT alignment); released ref.pkl {res['ref']['released_frames']} entries.", "",
         "AUC per condition; brackets = 95% CI of (AUC under condition - AUC untreated), bootstrap over claimed identities (500, seed 0).", "",
         "| score | " + " | ".join(CONDS) + " |", "|---" * (len(CONDS) + 1) + "|"]
    for nm, r in res["auc"].items():
        L.append(f"| {nm} | " + " | ".join(f"{r[c]['auc']}" + (f" ({r[c]['drop']:+.4f}) {r[c]['drop_vs_untreated_ci']}" if c != "untreated" else "") for c in CONDS) + " |")
    L += ["", "False alarm on genuine / miss on forged (%) at the threshold = 95th percentile on untreated genuine, held fixed:", "",
          "| score | " + " | ".join(CONDS) + " |", "|---" * (len(CONDS) + 1) + "|"]
    for nm, r in res["op5"].items():
        L.append(f"| {nm} | " + " | ".join(f"{r[c]['fa']} / {r[c]['miss']}" for c in CONDS) + " |")
    L += ["", "Median score (genuine / forged):", "", "| score | " + " | ".join(CONDS) + " |", "|---" * (len(CONDS) + 1) + "|"]
    for nm, r in res["median"].items():
        L.append(f"| {nm} | " + " | ".join(f"{r[c]['genuine']} / {r[c]['forged']}" for c in CONDS) + " |")
    (HERE / "ICT_PROBE.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    p = argparse.ArgumentParser(); p.add_argument("cmd", choices=["embed", "analyse"]); p.add_argument("--ict-repo"); p.add_argument("--weights", required=True)
    a = p.parse_args(); {"embed": embed, "analyse": analyse}[a.cmd](a)
