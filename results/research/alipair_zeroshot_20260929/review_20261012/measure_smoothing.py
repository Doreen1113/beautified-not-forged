"""Review 2026-10-12, point 4: what the service's Smoothing does to pixels versus the scripted smoothing seen in training and
versus plain blur. 120 identities of the unseen service, at the training geometry (crop, long side capped to 512) and at the
224-px model input. Read-only on data; writes measure_smoothing.json / .md here."""
import json
import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
HERE = Path(__file__).resolve().parent; RU = HERE.parent.parent / "retouch_unified_20260929"; sys.path.insert(0, str(RU))
from ops import op_smooth, hull_mask  # noqa: E402
BASE = Path(r"C:\My_Project\AIGC"); N = 120


def cap(rgb, lm):
    h, w = rgb.shape[:2]; f = 512 / max(h, w)
    if f >= 1:
        return rgb, lm
    return cv2.resize(rgb, (max(8, int(w * f)), max(8, int(h * f))), interpolation=cv2.INTER_AREA), lm * f


def L(rgb):
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)


def stats(o, r, lm, sig):
    h, w = o.shape[:2]; m = hull_mask(lm, h, w); k = max(3, int(0.06 * w)) | 1
    out = ~(cv2.dilate(m.astype(np.uint8), np.ones((k, k), np.uint8)) > 0)
    Lo, Lr = L(o), L(r); ho = np.abs(Lo - cv2.GaussianBlur(Lo, (0, 0), sig)); hr = np.abs(Lr - cv2.GaussianBlur(Lr, (0, 0), sig))
    gx = cv2.Sobel(Lo, cv2.CV_32F, 1, 0); gy = cv2.Sobel(Lo, cv2.CV_32F, 0, 1); g = np.hypot(gx, gy); gi = g[m]
    hi = m & (g >= np.quantile(gi, 0.9)); lo = m & (g <= np.quantile(gi, 0.5))
    d = np.abs(r.astype(np.float32) - o.astype(np.float32)).mean(2)
    return dict(hf_face=hr[m].mean() / max(ho[m].mean(), 1e-6), hf_bg=(hr[out].mean() / max(ho[out].mean(), 1e-6)) if out.sum() > 50 else np.nan,
                hf_edges=hr[hi].mean() / max(ho[hi].mean(), 1e-6), hf_flat=hr[lo].mean() / max(ho[lo].mean(), 1e-6),
                dL=float((Lr - Lo)[m].mean()), mad_face=d[m].mean(), mad_bg=d[out].mean() if out.sum() > 50 else np.nan)


def face_gauss(rgb, lm, s):
    h, w = rgb.shape[:2]; m = hull_mask(lm, h, w); a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), max(2.0, 0.01 * w))[..., None]
    return np.clip(rgb * (1 - a) + cv2.GaussianBlur(rgb, (0, 0), s) * a, 0, 255).astype(np.uint8)


def main():
    boxes = json.loads((RU / "ffhq_boxes.json").read_text()); z = np.load(RU / "ffhq_landmarks.npz")
    stems = [k for k in sorted(boxes) if 17000 <= int(k) < 20000 and k in z.files]; stems = stems[:: max(1, len(stems) // N)][:N]
    rng = np.random.default_rng(0); acc = {}
    for k in stems:
        b = boxes[k]; o = np.array(Image.open(BASE / "ffhq_originals/Part2" / f"{k}.png").convert("RGB"))[b[1]:b[3], b[0]:b[2]]
        lm = z[k].copy(); lm[:, 0] -= b[0]; lm[:, 1] -= b[1]; o, lm = cap(np.ascontiguousarray(o), lm)
        V = {}
        for lv in (30, 60, 90):
            p = BASE / "FFHQ_ali_process" / f"Smoothing_{lv}" / f"{(int(k) // 1000) * 1000}" / f"{k}.png"
            if p.is_file():
                r = np.array(Image.open(p).convert("RGB"))[b[1]:b[3], b[0]:b[2]]; V[f"service Smoothing_{lv}"] = cap(np.ascontiguousarray(r), lm)[0]
        V["scripted op_smooth frac .055 mix .11 (median of training range)"] = op_smooth(o, lm, rng, frac=0.055, mix=0.11)[0]
        V["scripted op_smooth frac .055 mix .40 (top of training range)"] = op_smooth(o, lm, rng, frac=0.055, mix=0.40)[0]
        V["scripted op_smooth frac .08 mix 1.0 (outside training range)"] = op_smooth(o, lm, rng, frac=0.08, mix=1.0)[0]
        V["scripted global bilateral (9,50,50) [beautify]"] = cv2.bilateralFilter(o, 9, 50, 50)
        V["scripted global bilateral (21,100,100) [beautify]"] = cv2.bilateralFilter(o, 21, 100, 100)
        V["global Gaussian sigma 1.0 [sym_degrade, all arms incl. P0]"] = cv2.GaussianBlur(o, (0, 0), 1.0)
        V["global Gaussian sigma 2.0 [sym_degrade, all arms incl. P0]"] = cv2.GaussianBlur(o, (0, 0), 2.0)
        V["face-only Gaussian sigma 1.5 (not in any arm)"] = face_gauss(o, lm, 1.5)
        V["JPEG q60 (not smoothing; reference)"] = cv2.imdecode(cv2.imencode(".jpg", o[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 60])[1], 1)[..., ::-1]
        o2 = np.asarray(Image.fromarray(o).resize((224, 224), Image.BILINEAR)); lm2 = lm * np.array([224 / o.shape[1], 224 / o.shape[0]])
        for name, r in V.items():
            if r.shape != o.shape:
                continue
            a = stats(o, r, lm, 1.5); r2 = np.asarray(Image.fromarray(np.ascontiguousarray(r)).resize((224, 224), Image.BILINEAR)); c = stats(o2, r2, lm2, 1.0)
            acc.setdefault(name, []).append([a["hf_face"], a["hf_bg"], a["hf_edges"], a["hf_flat"], a["dL"], a["mad_face"], a["mad_bg"], c["hf_face"], c["hf_bg"], c["hf_edges"], c["hf_flat"], c["mad_face"], c["mad_bg"]])
    cols = ["hf_face@512", "hf_bg@512", "hf_edges@512", "hf_flat@512", "dL", "mad_face@512", "mad_bg@512", "hf_face@224", "hf_bg@224", "hf_edges@224", "hf_flat@224", "mad_face@224", "mad_bg@224"]
    out = {k: dict(zip(cols, [round(float(x), 3) for x in np.nanmedian(np.array(v), 0)]), n=len(v)) for k, v in acc.items()}
    (HERE / "measure_smoothing.json").write_text(json.dumps(out, indent=1))
    Ls = ["# Smoothing: service vs scripted vs blur (medians over identities; hf = high-frequency energy ratio to the original, 1 = unchanged)", "",
          "| edit | n | " + " | ".join(cols) + " |", "|---|---|" + "---|" * len(cols)]
    for k, v in out.items():
        Ls.append(f"| {k} | {v['n']} | " + " | ".join(str(v[c]) for c in cols) + " |")
    (HERE / "measure_smoothing.md").write_text("\n".join(Ls) + "\n", encoding="utf-8"); print("\n".join(Ls))


if __name__ == "__main__":
    main()
