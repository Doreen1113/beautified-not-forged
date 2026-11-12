"""Addenda 38 and 39 (PRE_DECLARED.md, 2026-10-16): smoothed forgeries / smoothed genuine faces for the 17 published
detectors and our arms, and the dose response of the four released CLIP detectors.

Frames: the smooth_evasion.py list (Celeb-DF-v2 test, our crop, every 4th frame, 4,016 frames).
Conditions (all frames): untreated (original JPEG), bil9 / bil15 / bil21 (whole-crop bilateral (9,50,50) / (15,80,80) /
(21,100,100)), median5, gblend (as smooth_evasion.py), fl06 / fl12 (ops.op_smooth frac 0.06 / 0.12, mix 1, face hull of
MediaPipe landmarks detected on the crop).
Dose conditions (genuine frames only, Addendum 39): vig010 .. vig080 (vignette term of random_grade), fl03 / fl09.
Treated crops are written once as lossless PNG under OUT and every model reads the same files.

python smooth_probe38.py prep                 -> landmarks + PNGs + smooth38_list.json
python smooth_probe38.py score <name> ...     -> smooth38_<name>.npz   (published name or our checkpoint tag)
python smooth_probe38.py analyse              -> smooth38.json, SMOOTH38.md, dose39.json, DOSE39.md
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC")
LIST = B / "splits/research/ffpp_benchmark_20260925/celebdf_std32v2.txt"
OUT = Path(r"N:\2603055\AIGC\smooth_probe_20261016")
FORMS = ["bil9", "bil15", "bil21", "median5", "gblend", "fl06", "fl12"]
DOSE = ["vig010", "vig020", "vig040", "vig060", "vig080", "fl03", "fl09"]
PUB = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "univfd", "npr", "effort", "fadapter", "gend", "dfdhr", "caddm", "laanetr"]
CLIP4 = {"effort": "head", "fadapter": "clip_post_process.second_process.4", "gend": "model.linear", "dfdhr": "head"}
OURS = {"clipe5fbp0_s20260929": "P0 s1", "clipe5fbp0_s20260930": "P0 s2", "clipe5fbp0_s20261001": "P0 s3", "clipe5fb_s20260929": "P2 s1",
        "clipe5fb_s20260930": "P2 s2", "clipe5fbg0p1o_s20260929": "P1 smoothing only s1", "clipe5fbg0oy_s20260929": "P2 symmetric s1",
        "clipe5fbg0oy_s20260930": "P2 symmetric s2", "clipe5_s20260929": "main", "clipe5y_s20260929": "symmetric-view variant",
        "clipe5b_s20260929": "binary control", "clipe5fbp3_s20260929": "P3 forged only s1"}
OURS.update({"clipe5_s20260930": "main s2", "clipe5b_s20260930": "binary control s2", "clipe5z_s20260929": "SIC factorised s1", "clipe5bz_s20260929": "SIC binary s1",
             "clipe5z_s20260930": "SIC factorised s2", "clipe5bz_s20260930": "SIC binary s2", "clipe5bzl0_s20260929": "SIC binary, lambda 0 control", "clipe5bzl03_s20260929": "SIC binary, lambda 0.3 (am. 3)", "clipe5bzl01_s20260929": "SIC binary, lambda 0.1 (am. 3)", "clipe5bzsg_s20260929": "SIC binary, stop-gradient (am. 4)", "clipe5bzsg_s20260930": "SIC binary, stop-gradient s2 (am. 4)", "clipe5fbzsg_s20260929": "FF++-only SIC-sg (am. 4/5)", "clipe5bzsgl03_s20260929": "SIC-sg lambda 0.3 (am. 6)", "clipe5bzsgl01_s20260929": "SIC-sg lambda 0.1 (am. 6)", "clipe5bzsgG_s20260929": "SIC-sg Gaussian ablation (am. 7)", "clipe5bzsgh_s20260929": "SIC-h one-sided (am. 8)", "clipe5bzsgl003_s20260929": "SIC-sg lambda 0.03 (am. 9)", "clipe5bzsgl01_s20260930": "SIC-sg lambda 0.1 s2 (am. 6)", "clipe5bzsgl003_s20260930": "SIC-sg lambda 0.03 s2", "clipe5bzsgh_s20260930": "SIC-h one-sided s2", "clipe5bzsgG_s20260930": "SIC-sg Gaussian ablation s2", "clipe5bzxs_s20260929": "smoothing expert (Add. 48)", "clipe5fbp0F2_s20260929": "P0 F2F+FS only (Add. 49)", "clipe5bzEsg_s20260929": "SIC-sg Effort tuning (Add. 50)"})
OURS.update({"clipe5bzxs_s20260929": "smoothing expert s1 (Add. 48)", "clipe5bzxs_s20260930": "smoothing expert s2 (Add. 48)", "clipe5fbp0F2_s20260929": "FF++ F2F+FS only (Add. 49)", "clipe5M_s20260929": "multi-op s1 (Add. 56)", "clipe5M_s20260930": "multi-op s2 (Add. 56)", "clipe5M1_s20260929": "multi-op k1 ablation (Add. 56)", "clipe5fbEM_s20260929": "Effort-tuning + multi-op (Add. 56)"})
   # Addendum 46


def rows():
    r = [l.split("\t") for l in LIST.read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    return [x for x in r if int(Path(x[0]).stem.rsplit("__f", 1)[1]) % 4 == 0]


def apply(im, c, lm):
    import cv2
    from ops import op_smooth
    if c.startswith("bil"):
        d = int(c[3:]); return cv2.bilateralFilter(im, d, {9: 50, 15: 80, 21: 100}[d], {9: 50, 15: 80, 21: 100}[d])
    if c == "median5":
        return cv2.medianBlur(im, 5)
    if c == "gblend":
        return cv2.addWeighted(im, 0.5, cv2.GaussianBlur(im, (0, 0), 2.0), 0.5, 0)
    if c.startswith("fl"):
        if lm is None:
            return im
        return op_smooth(im, lm, np.random.default_rng(0), frac=int(c[2:]) / 100.0, mix=1.0)[0]
    if c.startswith("vig"):
        s = int(c[3:]) / 100.0; h, w = im.shape[:2]; x = im.astype(np.float32) / 255.0
        yy, xx = np.mgrid[0:h, 0:w]; r = np.hypot((yy - h / 2) / (h / 2), (xx - w / 2) / (w / 2))
        x = x * (1 - s * np.clip(r - 0.4, 0, None)[..., None] ** 1.5).astype(np.float32)
        return np.clip(x * 255.0, 0, 255).astype(np.uint8)
    raise ValueError(c)


def prep():
    import cv2
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision
    sys.path.insert(0, str(HERE))
    r = rows(); lmk = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_buffer=open(B / "face_landmarker.task", "rb").read()), num_faces=1))
    for c in FORMS + DOSE:
        (OUT / c).mkdir(parents=True, exist_ok=True)
    ok = np.zeros(len(r), bool); paths = {c: [] for c in ["untreated"] + FORMS + DOSE}
    for i, x in enumerate(r):
        bgr = cv2.imread(x[0]); rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB); h, w = rgb.shape[:2]
        res = lmk.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
        lm = np.array([[q.x * w, q.y * h] for q in res.face_landmarks[0]], np.float32) if res.face_landmarks else None
        ok[i] = lm is not None; stem = Path(x[0]).stem; paths["untreated"].append(x[0])
        for c in FORMS + (DOSE if x[1] == "0" else []):
            f = OUT / c / f"{stem}.png"
            if not f.is_file():
                cv2.imwrite(str(f), cv2.cvtColor(apply(rgb, c, lm), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_PNG_COMPRESSION, 1])
            paths[c].append(str(f))
        if i % 500 == 0:
            print(i, len(r), int(ok[:i + 1].sum()), flush=True)
    meta = {"paths": paths, "y": [int(x[1]) for x in r], "video": [x[2] for x in r], "lm_ok": ok.tolist()}
    (HERE / "smooth38_list.json").write_text(json.dumps(meta)); print("prep done", len(r), "frames; landmarks", int(ok.sum()), flush=True)


def score(name):
    f = HERE / f"smooth38_{name}.npz"
    if f.is_file():
        print(name, "cached"); return
    import torch
    meta = json.loads((HERE / "smooth38_list.json").read_text()); P = meta["paths"]; y = np.array(meta["y"])
    conds = ["untreated"] + FORMS + (DOSE if name in CLIP4 else [])
    out = {}
    if name in OURS:
        sys.path.insert(0, str(HERE)); from leak_probe import load; from train_ru3 import to_t2; from PIL import Image
        model, size, norm = load(name)
        for c in conds:
            ps = P[c]; s = np.zeros(len(ps), np.float32)
            with torch.no_grad():
                for i in range(0, len(ps), 32):
                    x = torch.stack([to_t2(np.array(Image.open(p).convert("RGB")), size, False, norm) for p in ps[i:i + 32]]).cuda()
                    with torch.autocast("cuda", dtype=torch.bfloat16):
                        s[i:i + 32] = torch.softmax(model(x)[0].float(), 1)[:, 1].cpu().numpy()
            out[c] = s
    elif name in CLIP4:   # adapter preprocessing and forward, plus a hook on the final 2-way linear layer
        sys.path.insert(0, str(B / "external_baselines")); import importlib; det = importlib.import_module(f"{name}_score").Detector()
        mod = det.model
        for a in CLIP4[name].split("."):
            mod = mod[int(a)] if a.isdigit() else getattr(mod, a)
        cap = []; h = mod.register_forward_hook(lambda m, i, o: cap.append((i[0].detach().float().cpu(), o.detach().float().cpu())))
        W = mod.weight.detach().float().cpu().numpy(); w = W[1] - W[0]
        for c in conds:
            ps = P[c]; s = np.full(len(ps), np.nan, np.float32); z = np.full(len(ps), np.nan, np.float32); F = None
            for i in range(0, len(ps), 32):
                t = [det._load(p) for p in ps[i:i + 32]]; assert all(v is not None for v in t)
                cap.clear(); pr = det._forward(torch.stack(t)); n = len(t)
                fi, fo = cap[-1]; fi, fo = fi[:n].numpy(), fo[:n].numpy()
                s[i:i + n] = pr[:n]; z[i:i + n] = fo[:, 1] - fo[:, 0]
                F = fi if F is None else np.concatenate([F, fi])
            d = np.abs(1 / (1 + np.exp(-z.astype(np.float64))) - s)
            assert np.nanmax(d) < 2e-3, (name, c, float(np.nanmax(d)))   # the hooked logit is the one behind the reported prob
            out[c] = s; out["z_" + c] = z; out["F_" + c] = F.astype(np.float16)
        h.remove(); out["w"] = w
        F0 = out["F_untreated"].astype(np.float32); g = np.where(y == 0)[0]
        for c in conds[1:]:
            Fc = out["F_" + c].astype(np.float32); base = F0 if len(Fc) == len(F0) else F0[g]; dF = Fc - base
            out["cos_" + c] = (dF @ w / (np.linalg.norm(dF, axis=1) * np.linalg.norm(w) + 1e-12)).astype(np.float32)
            out["dfn_" + c] = np.linalg.norm(dF, axis=1).astype(np.float32)
        for k in [k for k in out if k.startswith("F_")]:
            del out[k]
    else:
        if name in ("caddm", "laanetr"):
            sys.path.insert(0, str(B / "external_baselines")); import importlib; det = importlib.import_module(f"{name}_score").Detector()
        else:
            sys.path.insert(0, str(B / "results/research/external_baselines_20260905")); import zoo; det = zoo.ZOO[name]()
        for c in conds:
            out[c] = np.asarray(det.score(P[c]), np.float32)
    np.savez(f, **out); print(name, "done", {c: int(np.isnan(out[c]).sum()) for c in conds}, flush=True)


def analyse():
    from sklearn.metrics import roc_auc_score
    meta = json.loads((HERE / "smooth38_list.json").read_text()); y = np.array(meta["y"]); v = np.array(meta["video"]); ok = np.array(meta["lm_ok"])
    g, f = y == 0, y == 1; gi = np.where(g)[0]
    uv = np.unique(v); by = {k: np.where(v == k)[0] for k in uv}; rng = np.random.default_rng(0)
    draws = [np.concatenate([by[k] for k in rng.choice(uv, len(uv))]) for _ in range(1000)]
    names = [n for n in PUB + list(OURS) if (HERE / f"smooth38_{n}.npz").is_file()]
    res = {"n_frames": int(len(y)), "n_genuine": int(g.sum()), "n_forged": int(f.sum()), "n_videos": int(len(uv)), "landmarks_found": {"genuine": int((ok & g).sum()), "forged": int((ok & f).sum())}}

    def stat(S, idx):
        o = []
        yy = y[idx]; gg, ff = yy == 0, yy == 1; t = np.nanquantile(S["untreated"][idx][gg], 0.95)
        for c in FORMS:
            m = np.ones(len(idx), bool) if not c.startswith("fl") else ok[idx]
            u = S["untreated"][idx]; s = S[c][idx]
            o += [(u[ff & m] <= t).mean() * 100, (s[ff & m] <= t).mean() * 100 - (u[ff & m] <= t).mean() * 100, (s[gg & m] > t).mean() * 100]
        return np.array(o)

    for n in names:
        z = np.load(HERE / f"smooth38_{n}.npz"); S = {c: z[c].astype(np.float64) for c in ["untreated"] + FORMS}
        a = stat(S, np.arange(len(y))); bs = np.array([stat(S, d) for d in draws]); t = np.nanquantile(S["untreated"][g], 0.95)
        r = {"label": OURS.get(n, n), "miss_untreated": round(float(a[0]), 1), "forms": {}}
        for k, c in enumerate(FORMS):
            m = np.ones(len(y), bool) if not c.startswith("fl") else ok
            ci = lambda j: [round(float(np.nanpercentile(bs[:, j], q)), 1) for q in (2.5, 97.5)]
            mr, fa = [round(float(a[3 * k + 1]), 1)] + ci(3 * k + 1), [round(float(a[3 * k + 2]), 1)] + ci(3 * k + 2)
            yy = y[m]; sc = S[c][m]; k2 = ~np.isnan(sc)
            r["forms"][c] = {"miss_untreated_subset": round(float(a[3 * k]), 1), "miss_rise": mr, "fa": fa,
                             "auc_both_smoothed": round(float(roc_auc_score(yy[k2], sc[k2])), 3),
                             "forged_falls": round(float((S[c][f & m] < S["untreated"][f & m]).mean() * 100), 1),
                             "genuine_rises": round(float((S[c][g & m] > S["untreated"][g & m]).mean() * 100), 1),
                             "class": " + ".join([s_ for s_, c_ in (("accuses", fa[1] > 5.0), ("lets through", mr[1] > 0)) if c_]) or "neither"}
        r["auc_untreated"] = round(float(roc_auc_score(y[~np.isnan(S["untreated"])], S["untreated"][~np.isnan(S["untreated"])])), 3)
        old = HERE / f"smooth_evasion2_{n}.npz"
        if old.is_file():   # Addendum 38 sanity check
            o2 = np.load(old)["S"].astype(np.float64)
            r["sanity_auc_diff_vs_smooth_evasion2"] = round(float(max(abs(roc_auc_score(y, o2[:, j]) - roc_auc_score(y, S[c])) for j, c in zip(range(6), ["untreated"] + FORMS[:5]))), 4)
        res[n] = r
    # ---- Addendum 39: dose response, genuine frames
    dose = {}
    for n in [k for k in CLIP4 if (HERE / f"smooth38_{k}.npz").is_file()]:
        z = np.load(HERE / f"smooth38_{n}.npz"); u = z["untreated"].astype(np.float64); zu = z["z_untreated"].astype(np.float64)
        t = np.nanquantile(u[g], 0.95); gap = float(np.nanmean(zu[f]) - np.nanmean(zu[g])); d = {"gap_forged_minus_genuine_logit": round(gap, 3), "levels": {}}
        vg = v[g]; ug = np.unique(vg); byg = {k: np.where(vg == k)[0] for k in ug}; r2 = np.random.default_rng(1)
        dg = [np.concatenate([byg[k] for k in r2.choice(ug, len(ug))]) for _ in range(1000)]
        for c in ["bil9", "bil15", "bil21", "fl03", "fl06", "fl09", "fl12", "vig010", "vig020", "vig040", "vig060", "vig080"]:
            sc = z[c].astype(np.float64); zc = z["z_" + c].astype(np.float64); cs = z["cos_" + c].astype(np.float64)
            if len(sc) == len(y):
                sc, zc, cs = sc[g], zc[g], cs[g]
            m = ok[g] if c.startswith("fl") else np.ones(len(sc), bool)
            dz = zc - zu[g]; bm = [float(np.median(dz[b][m[b]])) for b in dg]
            d["levels"][c] = {"n": int(m.sum()), "mean_p": round(float(sc[m].mean()), 3), "above_thr": round(float((sc[m] > t).mean() * 100), 1),
                              "median_dlogit": [round(float(np.median(dz[m])), 3)] + [round(float(np.percentile(bm, q)), 3) for q in (2.5, 97.5)],
                              "mean_dlogit": round(float(dz[m].mean()), 3), "share_rises": round(float((dz[m] > 0).mean() * 100), 1),
                              "dlogit_over_gap": round(float(np.median(dz[m]) / gap), 3), "mean_abs_cos": round(float(np.abs(cs[m]).mean()), 3),
                              "mean_cos": round(float(cs[m].mean()), 3)}
        d["untreated_mean_p"] = round(float(u[g].mean()), 3)
        for fam, lv in (("vignette", ["vig010", "vig020", "vig040", "vig060", "vig080"]), ("face_local_smoothing", ["fl03", "fl06", "fl09", "fl12"]), ("whole_crop_bilateral", ["bil9", "bil15", "bil21"])):
            mm = [0.0] + [d["levels"][c]["mean_dlogit"] for c in lv]
            d[f"dose_response_{fam}"] = bool(all(mm[i + 1] >= mm[i] - 0.1 for i in range(len(mm) - 1)) and d["levels"][lv[-1]]["median_dlogit"][1] > 0)
        dose[n] = d
    (HERE / "smooth38.json").write_text(json.dumps(res, indent=1)); (HERE / "dose39.json").write_text(json.dumps(dose, indent=1))
    L = ["# Addendum 38: smoothed forgeries and smoothed genuine faces (Celeb-DF-v2, our crop, threshold 5% FPR on untreated genuine)", "",
         f"{res['n_frames']} frames ({res['n_genuine']} genuine, {res['n_forged']} forged, {res['n_videos']} videos); face-local forms on frames with landmarks: "
         f"{res['landmarks_found']['genuine']} genuine, {res['landmarks_found']['forged']} forged. Cells: miss rise [95% CI] / false alarms on smoothed genuine [95% CI]; class.", "",
         "| detector | AUC | miss | " + " | ".join(FORMS) + " |", "|---|---|---|" + "---|" * len(FORMS)]
    for n in names:
        r = res[n]
        L.append(f"| {r['label']} | {r['auc_untreated']:.3f} | {r['miss_untreated']:.1f} | " + " | ".join(
            f"{q['miss_rise'][0]:+.1f} [{q['miss_rise'][1]:+.1f},{q['miss_rise'][2]:+.1f}] / {q['fa'][0]:.1f} [{q['fa'][1]:.1f},{q['fa'][2]:.1f}] {q['class']}" for q in r["forms"].values()) + " |")
    L += ["", "AUC with both classes smoothed:", "", "| detector | " + " | ".join(FORMS) + " |", "|---|" + "---|" * len(FORMS)]
    for n in names:
        L.append(f"| {res[n]['label']} | " + " | ".join(f"{q['auc_both_smoothed']:.3f}" for q in res[n]["forms"].values()) + " |")
    L += ["", "Classes per form (published detectors only):", ""]
    for c in FORMS:
        cl = [res[n]["forms"][c]["class"] for n in names if n in PUB]
        L.append(f"- {c}: " + ", ".join(f"{k} {cl.count(k)}" for k in sorted(set(cl))))
    L += ["", "Sanity (our models, max |frame AUC difference| against smooth_evasion2): " + ", ".join(f"{n} {res[n]['sanity_auc_diff_vs_smooth_evasion2']}" for n in names if "sanity_auc_diff_vs_smooth_evasion2" in res[n])]
    (HERE / "SMOOTH38.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    D = ["# Addendum 39: dose response on genuine Celeb-DF-v2 frames, released CLIP detectors", "",
         "Cells: mean P(fake) / share above the 5%-FPR threshold / median logit shift [95% CI] / shift as share of the forged-genuine gap / mean |cos(dF, w)|", ""]
    for n, d in dose.items():
        D += [f"## {n} (untreated mean P {d['untreated_mean_p']}, forged-genuine logit gap {d['gap_forged_minus_genuine_logit']}; dose response: vignette {d['dose_response_vignette']}, "
              f"face-local smoothing {d['dose_response_face_local_smoothing']}, whole-crop bilateral {d['dose_response_whole_crop_bilateral']})", "",
              "| level | n | mean P | above thr % | median dlogit | /gap | rises % | mean |cos| |", "|---|---|---|---|---|---|---|---|"]
        for c, q in d["levels"].items():
            D.append(f"| {c} | {q['n']} | {q['mean_p']} | {q['above_thr']} | {q['median_dlogit'][0]:+.3f} [{q['median_dlogit'][1]:+.3f},{q['median_dlogit'][2]:+.3f}] | {q['dlogit_over_gap']:+.3f} | {q['share_rises']} | {q['mean_abs_cos']} |")
        D.append("")
    (HERE / "DOSE39.md").write_text("\n".join(D) + "\n", encoding="utf-8"); print("\n".join(L)); print("\n".join(D))


if __name__ == "__main__":
    if sys.argv[1] == "prep":
        prep()
    elif sys.argv[1] == "score":
        for nm in sys.argv[2:]:
            score(nm)
    else:
        analyse()
