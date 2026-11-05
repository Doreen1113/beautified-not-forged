"""Band-energy mechanism analysis (2026-10-18): does the loss of high-frequency (texture) energy inside the face explain how
much each published detector accuses skin-smoothed genuine faces?

Inputs (read only): smooth_probe38.py frame list / cached renders (Addendum 38, Celeb-DF-v2 genuine frames, seven smoothing
forms), SMOOTH38.md (false-alarm rate per detector and form at the 5%-FPR threshold), alipair_zeroshot_20260929 (commercial
Smoothing-30/60/90 renders in the shared-box crops the detectors scored, published_ali.json accusation at 5% FPR).

Statistic per frame and form (same landmark-hull bounding box for the untreated frame and every form of that frame):
  E_hf(thr) = power at radial frequency > thr (cycles/pixel, Nyquist 0.5) / total power, luminance, 2-D Hann window, DC removed.
  texture loss of a form = mean over frames of log(E_hf(form) / E_hf(untreated))      (primary thr 0.25; also 0.15, 0.35)
  alternatives: (a) mean |x_s - x| over RGB inside the landmark hull; (b) log Laplacian-variance ratio inside the hull.
Each statistic is computed at the stored resolution ("native") and on the crop resized to a 256-px longer side ("view256",
roughly what the detectors see; needed to put the 960-px commercial crops on the same footing as the ~330-px Celeb-DF frames).

CPU only. python bandenergy.py            -> bandenergy_frames.npz, fa_parsed.json, bandenergy.json, bandenergy_tables.md
"""
import json
import os
import re
import sys
from pathlib import Path

os.environ["CUDA_VISIBLE_DEVICES"] = ""
import cv2
import numpy as np
from scipy import stats

B = Path(r"C:\My_Project\AIGC"); RU = B / "results/research/retouch_unified_20260929"; HERE = RU / "bandenergy_20261018"
ALI = B / "results/research/alipair_zeroshot_20260929"; CROPS = B / "alipair_crops"
FORMS = ["bil9", "bil15", "bil21", "median5", "gblend", "fl06", "fl12"]
ALIFORMS = ["Smoothing_30", "Smoothing_60", "Smoothing_90"]
PUB = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "univfd", "npr", "effort", "fadapter", "gend", "dfdhr", "caddm", "laanetr"]
THR = [0.125, 0.15, 0.25, 0.35]; PRIMARY = 0.25
N_FRAMES, N_PAIRS, SEED, VIEW, N_BOOT = 400, 200, 0, 256, 200
RBINS = np.arange(0.0, 0.72, 0.01)   # radial-spectrum bins (cycles/pixel), saved for auditing


# ----------------------------------------------------------------------------------------------------------------- statistics
def landmarker():
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision
    lmk = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_buffer=open(B / "face_landmarker.task", "rb").read()), num_faces=1))

    def detect(rgb):
        h, w = rgb.shape[:2]
        res = lmk.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)))
        return np.array([[q.x * w, q.y * h] for q in res.face_landmarks[0]], np.float32) if res.face_landmarks else None
    return detect


def lum(rgb):
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)


def box_of(lm, h, w):
    x0, y0 = np.floor(lm.min(0)).astype(int); x1, y1 = np.ceil(lm.max(0)).astype(int)
    return max(x0, 0), max(y0, 0), min(x1 + 1, w), min(y1 + 1, h)


def hull(lm, h, w):
    m = np.zeros((h, w), np.uint8); cv2.fillConvexPoly(m, cv2.convexHull(lm.astype(np.float32)).astype(np.int32), 255); return m > 0


def spectrum(Lbox):
    """Windowed 2-D power spectrum of a luminance box; returns (E_hf at each THR, binned radial power spectrum)."""
    h, w = Lbox.shape; win = np.outer(np.hanning(h), np.hanning(w)).astype(np.float32)
    x = (Lbox - Lbox.mean()) * win
    P = np.abs(np.fft.fft2(x)) ** 2; P[0, 0] = 0.0
    r = np.sqrt(np.fft.fftfreq(h)[:, None] ** 2 + np.fft.fftfreq(w)[None, :] ** 2)
    tot = P.sum(); e = np.array([P[r > t].sum() / tot for t in THR])
    rad = np.histogram(r, bins=RBINS, weights=P)[0] / tot
    return e, rad


def frame_stats(rgb0, rgbs, lm):
    """rgb0 untreated, rgbs dict form -> RGB (same size), lm landmarks on rgb0. Returns dict of per-form statistics at
    native resolution and at the VIEW resolution."""
    out = {}
    for tag, scale in (("native", 1.0), ("view", VIEW / max(rgb0.shape[:2]))):
        if scale != 1.0:
            sz = (int(round(rgb0.shape[1] * scale)), int(round(rgb0.shape[0] * scale)))
            rs = lambda im: cv2.resize(im, sz, interpolation=cv2.INTER_AREA)
            im0 = rs(rgb0); ims = {c: rs(v) for c, v in rgbs.items()}; l = lm * scale
        else:
            im0, ims, l = rgb0, rgbs, lm
        h, w = im0.shape[:2]; x0, y0, x1, y1 = box_of(l, h, w); m = hull(l, h, w); mb = m[y0:y1, x0:x1]
        L0 = lum(im0); e0, rad0 = spectrum(L0[y0:y1, x0:x1]); lap0 = cv2.Laplacian(L0, cv2.CV_32F, ksize=3)[y0:y1, x0:x1][mb].var()
        d = {"untreated": {"ehf": e0, "rad": rad0, "lapvar": lap0, "mad": 0.0, "box": (x0, y0, x1, y1), "hull_px": int(mb.sum())}}
        for c, im in ims.items():
            L = lum(im); e, rad = spectrum(L[y0:y1, x0:x1]); lap = cv2.Laplacian(L, cv2.CV_32F, ksize=3)[y0:y1, x0:x1][mb].var()
            mad = float(np.abs(im[y0:y1, x0:x1].astype(np.float32) - im0[y0:y1, x0:x1].astype(np.float32))[mb].mean())
            d[c] = {"ehf": e, "rad": rad, "lapvar": lap, "mad": mad}
        out[tag] = d
    return out


def collect(detect):
    """Per-frame statistics for the Celeb-DF genuine subset and the commercial pairs."""
    meta = json.loads((RU / "smooth38_list.json").read_text()); y = np.array(meta["y"]); ok = np.array(meta["lm_ok"]); P = meta["paths"]
    rng = np.random.default_rng(SEED); gi = np.where((y == 0) & ok)[0]; sel = np.sort(rng.choice(gi, N_FRAMES, replace=False))
    rec = {"cdf": {"idx": [], "stem": [], "video": []}, "ali": {"stem": []}}
    S = {tag: {c: {"ehf": [], "rad": [], "lapvar": [], "mad": []} for c in ["untreated"] + FORMS} for tag in ("native", "view")}
    boxes = {tag: [] for tag in ("native", "view")}; fails = 0
    for n, i in enumerate(sel):
        rgb0 = cv2.cvtColor(cv2.imread(P["untreated"][i]), cv2.COLOR_BGR2RGB); lm = detect(rgb0)
        if lm is None:
            fails += 1; continue
        rgbs = {c: cv2.cvtColor(cv2.imread(P[c][i]), cv2.COLOR_BGR2RGB) for c in FORMS}
        assert all(v.shape == rgb0.shape for v in rgbs.values())
        st = frame_stats(rgb0, rgbs, lm)
        rec["cdf"]["idx"].append(int(i)); rec["cdf"]["stem"].append(Path(P["untreated"][i]).stem); rec["cdf"]["video"].append(meta["video"][i])
        for tag in ("native", "view"):
            boxes[tag].append(st[tag]["untreated"]["box"])
            for c in ["untreated"] + FORMS:
                for k in ("ehf", "rad", "lapvar", "mad"):
                    S[tag][c][k].append(st[tag][c][k])
        if n % 50 == 0:
            print("cdf", n, N_FRAMES, flush=True)
    print("cdf done; landmark failures", fails, flush=True)
    # commercial pairs: the shared-box crops the detectors scored (eval_published_ali.py crops)
    keys = sorted(json.loads((ALI / "boxes.json").read_text())); rng2 = np.random.default_rng(SEED); ks = sorted(rng2.choice(keys, N_PAIRS, replace=False))
    A = {tag: {c: {"ehf": [], "rad": [], "lapvar": [], "mad": []} for c in ["untreated"] + ALIFORMS} for tag in ("native", "view")}
    aboxes = {tag: [] for tag in ("native", "view")}; afails = 0
    for n, k in enumerate(ks):
        rgb0 = cv2.cvtColor(cv2.imread(str(CROPS / f"orig_0__{k}.png")), cv2.COLOR_BGR2RGB); lm = detect(rgb0)
        if lm is None:
            afails += 1; continue
        rgbs = {c: cv2.cvtColor(cv2.imread(str(CROPS / f"{c}__{k}.png")), cv2.COLOR_BGR2RGB) for c in ALIFORMS}
        assert all(v.shape == rgb0.shape for v in rgbs.values())
        st = frame_stats(rgb0, rgbs, lm); rec["ali"]["stem"].append(k)
        for tag in ("native", "view"):
            aboxes[tag].append(st[tag]["untreated"]["box"])
            for c in ["untreated"] + ALIFORMS:
                for kk in ("ehf", "rad", "lapvar", "mad"):
                    A[tag][c][kk].append(st[tag][c][kk])
        if n % 50 == 0:
            print("ali", n, N_PAIRS, flush=True)
    print("ali done; landmark failures", afails, flush=True)
    npz = {"thr": np.array(THR), "rbins": RBINS, "cdf_idx": np.array(rec["cdf"]["idx"]), "cdf_stem": np.array(rec["cdf"]["stem"]),
           "cdf_video": np.array(rec["cdf"]["video"]), "ali_stem": np.array(rec["ali"]["stem"]), "cdf_failures": fails, "ali_failures": afails}
    for tag in ("native", "view"):
        npz[f"cdf_box_{tag}"] = np.array(boxes[tag]); npz[f"ali_box_{tag}"] = np.array(aboxes[tag])
        for c in ["untreated"] + FORMS:
            for k in ("ehf", "rad", "lapvar", "mad"):
                npz[f"cdf_{tag}_{c}_{k}"] = np.array(S[tag][c][k])
        for c in ["untreated"] + ALIFORMS:
            for k in ("ehf", "rad", "lapvar", "mad"):
                npz[f"ali_{tag}_{c}_{k}"] = np.array(A[tag][c][k])
    np.savez(HERE / "bandenergy_frames.npz", **npz); return npz


# ---------------------------------------------------------------------------------------------------------- false-alarm rates
def parse_fa():
    """FA (%) per detector and form from the SMOOTH38.md table (cell = 'miss rise [CI] / FA [CI] class'), cross-checked
    against smooth38.json; Smoothing-30/60/90 accusation at the 5%-FPR threshold from published_ali.json."""
    md = (RU / "SMOOTH38.md").read_text(encoding="utf-8").splitlines()
    hdr = [l for l in md if l.startswith("| detector | AUC | miss |")][0]
    cols = [c.strip() for c in hdr.strip("|").split("|")][3:]; assert cols == FORMS, cols
    start = md.index(hdr) + 2; fa = {}; cell = re.compile(r"^([+-]?\d+\.\d) \[[^\]]*\] / (\d+\.\d) \[([^,]+),([^\]]+)\] (.*)$")
    for l in md[start:]:
        if not l.startswith("|"):
            break
        cs = [c.strip() for c in l.strip().strip("|").split("|")]; lab = cs[0]
        fa[lab] = {"auc": float(cs[1]), "miss": float(cs[2]), "fa": {}, "fa_ci": {}, "miss_rise": {}, "class": {}}
        for c, s in zip(FORMS, cs[3:]):
            m = cell.match(s); assert m, (lab, c, s)
            fa[lab]["fa"][c] = float(m.group(2)); fa[lab]["fa_ci"][c] = [float(m.group(3)), float(m.group(4))]
            fa[lab]["miss_rise"][c] = float(m.group(1)); fa[lab]["class"][c] = m.group(5)
    js = json.loads((RU / "smooth38.json").read_text()); lab2key = {v["label"]: k for k, v in js.items() if isinstance(v, dict) and "label" in v}
    for lab, r in fa.items():
        k = lab2key[lab]
        for c in FORMS:
            assert abs(js[k]["forms"][c]["fa"][0] - r["fa"][c]) < 1e-9, (lab, c)
        r["key"] = k
    ali = json.loads((ALI / "published_ali.json").read_text())
    for d in PUB:
        for c in ALIFORMS:
            fa[d]["fa"][c] = ali[d]["by_op"][c]["fake_at_t"]
        fa[d]["ali_t_5fpr_orig"] = ali[d]["t_5fpr_orig"]; fa[d]["ali_auroc_ret_vs_orig"] = ali[d]["auroc_ret_vs_orig"]
    out = {"published": {d: fa[d] for d in PUB}, "ours": {lab: r for lab, r in fa.items() if lab not in PUB},
           "source": {"celebdf_forms": str(RU / "SMOOTH38.md"), "cross_check": str(RU / "smooth38.json"), "commercial": str(ALI / "published_ali.json")},
           "note": "fa = false alarms (%) on smoothed genuine frames at the detector's 5%-FPR threshold set on untreated genuine frames "
                   "(Celeb-DF-v2, Addendum 38); Smoothing_* = share of commercial-retouched FFHQ faces scored above the 5%-FPR "
                   "threshold set on the FFHQ originals (alipair). NPR's commercial numbers are n/a in the paper (AUROC 0.40, inverted)."}
    (HERE / "fa_parsed.json").write_text(json.dumps(out, indent=1)); return out


# ------------------------------------------------------------------------------------------------------------------ analysis
def logit(p):
    p = np.clip(np.asarray(p, float) / 100.0, 0.005, 0.995); return np.log(p / (1 - p))


def fixed_effects(x, yv, det):
    """logit(FA) = a_det + b x. Returns slope, SE, t, p, partial R2 (share of the within-detector variance explained)."""
    det = np.asarray(det); ds = sorted(set(det)); X = np.column_stack([np.asarray(x, float)] + [(det == d).astype(float) for d in ds])
    beta, res, rank, _ = np.linalg.lstsq(X, yv, rcond=None); fit = X @ beta; ssr = float(((yv - fit) ** 2).sum())
    X0 = X[:, 1:]; b0 = np.linalg.lstsq(X0, yv, rcond=None)[0]; ssr0 = float(((yv - X0 @ b0) ** 2).sum())
    dof = len(yv) - X.shape[1]; s2 = ssr / dof; cov = s2 * np.linalg.inv(X.T @ X); se = float(np.sqrt(cov[0, 0]))
    t = float(beta[0] / se); p = float(2 * stats.t.sf(abs(t), dof))
    return {"slope": float(beta[0]), "se": se, "t": t, "p": p, "partial_r2": 1 - ssr / ssr0, "n": int(len(yv)), "dof": int(dof)}


def loss_of(npz, src, tag, c, stat, thr_i, idx=None):
    """Per-frame loss values for one form: -log(E_hf ratio) / log(lapvar ratio) / mad (mad is already 'loss-like')."""
    u = npz[f"{src}_{tag}_untreated_{stat if stat != 'mad' else 'ehf'}"]; v = npz[f"{src}_{tag}_{c}_{stat if stat != 'mad' else 'ehf'}"]
    if stat == "ehf":
        r = -np.log(v[:, thr_i] / u[:, thr_i])
    elif stat == "lapvar":
        r = -np.log(v / u)
    else:
        r = npz[f"{src}_{tag}_{c}_mad"]
    return r if idx is None else r[idx]


STATS = [("ehf", 0.125), ("ehf", 0.15), ("ehf", 0.25), ("ehf", 0.35), ("lapvar", None), ("mad", None)]


def stat_name(stat, thr):
    return f"ehf{thr}" if stat == "ehf" else stat


def analyse(npz, fa):
    rng = np.random.default_rng(SEED); nc, na = len(npz["cdf_stem"]), len(npz["ali_stem"])
    draws_c = [rng.integers(0, nc, nc) for _ in range(N_BOOT)]; draws_a = [rng.integers(0, na, na) for _ in range(N_BOOT)]
    res = {"n_frames_celebdf": int(nc), "n_pairs_commercial": int(na), "seed": SEED, "n_boot": N_BOOT, "view_px": VIEW, "thresholds_cpp": THR,
           "primary": {"stat": "ehf", "thr": PRIMARY, "resolution": "native for the 7 Celeb-DF forms; view256 for the 8-form analysis"},
           "loss_per_form": {}, "per_detector": {}, "pooled": {}, "ours_per_detector": {}}
    pub = PUB; famlab = {d: ("gen" if d in ("univfd", "npr") else "clip" if d in ("effort", "fadapter", "gend", "dfdhr") else "cnn") for d in pub}
    res["family"] = famlab
    for stat, thr in STATS:
        ti = THR.index(thr) if thr is not None else None; sn = stat_name(stat, thr)
        for tag in ("native", "view"):
            key = f"{sn}_{tag}"; L = {}
            for c in FORMS:
                v = loss_of(npz, "cdf", tag, c, stat, ti); bs = [loss_of(npz, "cdf", tag, c, stat, ti, d).mean() for d in draws_c]
                L[c] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "n": int(len(v)),
                        "share_frames_with_loss": float((v > 0).mean())}
            for c in ALIFORMS:
                v = loss_of(npz, "ali", tag, c, stat, ti); bs = [loss_of(npz, "ali", tag, c, stat, ti, d).mean() for d in draws_a]
                L[c] = {"mean": float(v.mean()), "sd": float(v.std(ddof=1)), "ci": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], "n": int(len(v)),
                        "share_frames_with_loss": float((v > 0).mean())}
            res["loss_per_form"][key] = L
            # ---- correlations: 7 forms (Celeb-DF), 8 forms (+ Smoothing_90, NPR excluded), 10 forms (+ S30, S60, NPR excluded)
            # 7forms: Celeb-DF forms, 17 detectors; 8forms: + commercial S-90, NPR excluded (its commercial numbers are n/a);
            # 8forms_all: the plotted set (17 detectors on the 7 forms, 16 on S-90); 10forms: + S-30/S-60, NPR excluded
            ok_ = lambda d, c: not (d == "npr" and c in ALIFORMS)
            for setname, forms, dets in (("7forms", FORMS, pub), ("8forms", FORMS + ["Smoothing_90"], [d for d in pub if d != "npr"]),
                                         ("8forms_all", FORMS + ["Smoothing_90"], pub), ("10forms", FORMS + ALIFORMS, [d for d in pub if d != "npr"])):
                per = {}; fs_of = {d: [c for c in forms if ok_(d, c)] for d in dets}
                for d in dets:
                    x = np.array([L[c]["mean"] for c in fs_of[d]]); fv = np.array([fa["published"][d]["fa"][c] for c in fs_of[d]])
                    sp = stats.spearmanr(x, fv); pe = stats.pearsonr(x, fv)
                    per[d] = {"spearman": float(sp.statistic), "spearman_p": float(sp.pvalue), "pearson": float(pe.statistic), "pearson_p": float(pe.pvalue),
                              "pearson_logit": float(stats.pearsonr(x, logit(fv)).statistic), "n_forms": len(fs_of[d])}
                res["per_detector"].setdefault(key, {})[setname] = per
                pts_ = [(d, c) for d in dets for c in fs_of[d]]
                X = np.array([L[c]["mean"] for d, c in pts_]); Y = np.array([fa["published"][d]["fa"][c] for d, c in pts_])
                D = [d for d, c in pts_]; sp = stats.spearmanr(X, Y); pe = stats.pearsonr(X, Y); fe = fixed_effects(X, logit(Y), D)
                # bootstrap over frames: re-estimate every form's loss, FA fixed
                src_draw = lambda c, j: (loss_of(npz, "ali", tag, c, stat, ti, draws_a[j]).mean() if c in ALIFORMS else loss_of(npz, "cdf", tag, c, stat, ti, draws_c[j]).mean())
                bsp, bpe, bfe, bper = [], [], [], []
                for j in range(N_BOOT):
                    Lj = {c: src_draw(c, j) for c in forms}; Xj = np.array([Lj[c] for d, c in pts_])
                    bsp.append(stats.spearmanr(Xj, Y).statistic); bpe.append(stats.pearsonr(Xj, Y).statistic); bfe.append(fixed_effects(Xj, logit(Y), D)["slope"])
                    bper.append(np.mean([stats.spearmanr(np.array([Lj[c] for c in fs_of[d]]), np.array([fa["published"][d]["fa"][c] for c in fs_of[d]])).statistic for d in dets]))
                res["pooled"].setdefault(key, {})[setname] = {
                    "n_points": int(len(X)), "n_detectors": len(dets), "n_forms": len(forms),
                    "spearman": float(sp.statistic), "spearman_p": float(sp.pvalue), "spearman_ci_frames": [float(np.percentile(bsp, 2.5)), float(np.percentile(bsp, 97.5))],
                    "pearson": float(pe.statistic), "pearson_p": float(pe.pvalue), "pearson_ci_frames": [float(np.percentile(bpe, 2.5)), float(np.percentile(bpe, 97.5))],
                    "pearson_logit": float(stats.pearsonr(X, logit(Y)).statistic),
                    "mean_per_detector_spearman": float(np.mean([per[d]["spearman"] for d in dets])),
                    "mean_per_detector_spearman_ci_frames": [float(np.percentile(bper, 2.5)), float(np.percentile(bper, 97.5))],
                    "median_per_detector_spearman": float(np.median([per[d]["spearman"] for d in dets])),
                    "n_detectors_spearman_ge_0.5": int(sum(per[d]["spearman"] >= 0.5 for d in dets)),
                    "fixed_effects_logit": fe, "fixed_effects_slope_ci_frames": [float(np.percentile(bfe, 2.5)), float(np.percentile(bfe, 97.5))]}
            # ---- our arms (7 Celeb-DF forms only; their commercial labels are not matched to SMOOTH38 labels)
            x7 = np.array([L[c]["mean"] for c in FORMS]); po = {}
            for lab, r in fa["ours"].items():
                fv = np.array([r["fa"][c] for c in FORMS]); sp = stats.spearmanr(x7, fv)
                po[lab] = {"spearman": float(sp.statistic) if np.isfinite(sp.statistic) else None, "pearson": float(stats.pearsonr(x7, fv).statistic) if fv.std() > 0 else None,
                           "fa_range": [float(fv.min()), float(fv.max())]}
            res["ours_per_detector"][key] = po
    # which statistic predicts best (8-form, view256; and 7-form native)
    rank = []
    for stat, thr in STATS:
        sn = stat_name(stat, thr)
        for tag in ("native", "view"):
            for setname in ("7forms", "8forms", "8forms_all", "10forms"):
                p = res["pooled"][f"{sn}_{tag}"][setname]
                rank.append({"stat": sn, "resolution": tag, "set": setname, "pooled_spearman": p["spearman"], "mean_detector_spearman": p["mean_per_detector_spearman"],
                             "fe_partial_r2": p["fixed_effects_logit"]["partial_r2"], "fe_t": p["fixed_effects_logit"]["t"]})
    res["ranking"] = rank
    # mean radial spectra per form (audit / optional plot)
    res["mean_radial_spectrum"] = {tag: {c: npz[f"cdf_{tag}_{c}_rad"].mean(0).tolist() for c in ["untreated"] + FORMS} for tag in ("native", "view")}
    res["mean_radial_spectrum_commercial"] = {tag: {c: npz[f"ali_{tag}_{c}_rad"].mean(0).tolist() for c in ["untreated"] + ALIFORMS} for tag in ("native", "view")}
    res["mean_ehf_untreated"] = {tag: {"celebdf": npz[f"cdf_{tag}_untreated_ehf"].mean(0).tolist(), "commercial": npz[f"ali_{tag}_untreated_ehf"].mean(0).tolist()} for tag in ("native", "view")}
    res["box_size_px"] = {tag: {"celebdf_mean_wh": [float((npz[f"cdf_box_{tag}"][:, 2] - npz[f"cdf_box_{tag}"][:, 0]).mean()), float((npz[f"cdf_box_{tag}"][:, 3] - npz[f"cdf_box_{tag}"][:, 1]).mean())],
                                "commercial_mean_wh": [float((npz[f"ali_box_{tag}"][:, 2] - npz[f"ali_box_{tag}"][:, 0]).mean()), float((npz[f"ali_box_{tag}"][:, 3] - npz[f"ali_box_{tag}"][:, 1]).mean())]} for tag in ("native", "view")}
    (HERE / "bandenergy.json").write_text(json.dumps(res, indent=1)); return res


def tables(res, fa):
    """Markdown tables for BANDENERGY.md."""
    L = []; fmt = lambda v: f"{v:+.3f}"
    L += ["### Texture loss per form (mean over frames of -log(E_hf(form)/E_hf(untreated)); 95% CI over frames)", "",
          "| form | E_hf 0.25 native | E_hf 0.25 view256 | E_hf 0.15 native | E_hf 0.35 native | Laplacian-var loss native | mean abs change native (8-bit) |", "|---|---|---|---|---|---|---|"]
    order = sorted(FORMS + ALIFORMS, key=lambda c: res["loss_per_form"]["ehf0.25_native"][c]["mean"])
    for c in order:
        r = lambda k: res["loss_per_form"][k][c]
        L.append(f"| {c} | {r('ehf0.25_native')['mean']:.3f} [{r('ehf0.25_native')['ci'][0]:.3f},{r('ehf0.25_native')['ci'][1]:.3f}] | "
                 f"{r('ehf0.25_view')['mean']:.3f} [{r('ehf0.25_view')['ci'][0]:.3f},{r('ehf0.25_view')['ci'][1]:.3f}] | {r('ehf0.15_native')['mean']:.3f} | {r('ehf0.35_native')['mean']:.3f} | "
                 f"{r('lapvar_native')['mean']:.3f} | {r('mad_native')['mean']:.2f} |")
    L += ["", "(Smoothing_30/60/90 are the commercial renders on 960-px crops: their native-resolution numbers are not on the same pixel grid as the ~330-px Celeb-DF frames; compare them in the view256 column.)", ""]
    for setname, title in (("7forms", "seven Celeb-DF forms, native resolution"), ("8forms", "eight forms (+ commercial Smoothing-90), view256, NPR excluded")):
        tag = "native" if setname == "7forms" else "view"
        L += [f"### Per-detector correlation of FA with texture loss ({title})", "",
              "| detector | family | Spearman E_hf0.25 | Pearson E_hf0.25 | Spearman E_hf0.15 | Spearman E_hf0.35 | Spearman Laplacian | Spearman mean-abs-change |", "|---|---|---|---|---|---|---|---|"]
        for d in PUB:
            if setname == "8forms" and d == "npr":
                continue
            g = lambda k: res["per_detector"][f"{k}_{tag}"][setname][d]
            L.append(f"| {d} | {res['family'][d]} | {g('ehf0.25')['spearman']:+.2f} | {g('ehf0.25')['pearson']:+.2f} | {g('ehf0.15')['spearman']:+.2f} | {g('ehf0.35')['spearman']:+.2f} | {g('lapvar')['spearman']:+.2f} | {g('mad')['spearman']:+.2f} |")
        L.append("")
    L += ["### Pooled detector x form correlation (FA vs loss) and fixed-effects fit logit(FA) = a_detector + b * loss", "",
          "| statistic | resolution | set | points | pooled Spearman [95% CI, frames] | pooled Pearson | mean per-detector Spearman [CI] | detectors with rho >= 0.5 | FE slope (t) | FE partial R2 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for stat, thr in STATS:
        sn = stat_name(stat, thr)
        for tag in ("native", "view"):
            for setname in ("7forms", "8forms", "8forms_all", "10forms"):
                p = res["pooled"][f"{sn}_{tag}"][setname]; fe = p["fixed_effects_logit"]
                L.append(f"| {sn} | {tag} | {setname} | {p['n_points']} | {p['spearman']:+.3f} [{p['spearman_ci_frames'][0]:+.3f},{p['spearman_ci_frames'][1]:+.3f}] | {p['pearson']:+.3f} | "
                         f"{p['mean_per_detector_spearman']:+.3f} [{p['mean_per_detector_spearman_ci_frames'][0]:+.3f},{p['mean_per_detector_spearman_ci_frames'][1]:+.3f}] | {p['n_detectors_spearman_ge_0.5']}/{p['n_detectors']} | "
                         f"{fe['slope']:+.2f} ({fe['t']:+.1f}) | {fe['partial_r2']:.3f} |")
    L += ["", "### Our arms (7 Celeb-DF forms, E_hf 0.25 native): Spearman of FA with texture loss", "", "| arm | Spearman | FA range (%) |", "|---|---|---|"]
    for lab, r in res["ours_per_detector"]["ehf0.25_native"].items():
        L.append(f"| {lab} | {'n/a' if r['spearman'] is None else f'{r['spearman']:+.2f}'} | {r['fa_range'][0]:.1f} - {r['fa_range'][1]:.1f} |")
    (HERE / "bandenergy_tables.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    HERE.mkdir(exist_ok=True)
    fa = parse_fa(); print("FA parsed:", len(fa["published"]), "published,", len(fa["ours"]), "ours", flush=True)
    f = HERE / "bandenergy_frames.npz"
    if f.is_file() and "--recompute" not in sys.argv:
        npz = dict(np.load(f)); print("frame statistics cached", flush=True)
    else:
        npz = collect(landmarker())
    res = analyse(npz, fa); tables(res, fa)
