"""Physical retouching quantities from pixel-aligned (original, retouched) pairs — the verifiable ground truth for the
explanation heads and the sanity check on what each vendor operation actually does.

Per pair (landmarks on the ORIGINAL define all regions; retouched landmarks re-detected for geometric ratios):
  eye_ratio   = mean eye width (retouched) / mean eye width (original)         (eye enlarging)
  jaw_ratio   = jaw width (retouched) / jaw width (original)                    (face lifting / slimming; <1 = slimmer)
  dL_skin     = mean LAB-L change inside the face hull, retouched - original    (whitening)
  hf_ratio    = high-frequency energy (|x - gauss3(x)| on L) inside the hull, retouched / original   (smoothing; <1 = smoother)
  mad_hull    = mean |retouched - original| inside hull (overall edit magnitude)

python measure_pairs.py <name> <pairs.tsv>   # pairs.tsv: orig<TAB>retouched<TAB>group  -> pairs_<name>.tsv
"""
import sys
from pathlib import Path

import cv2
import numpy as np

BASE = Path(r"C:\My_Project\AIGC")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE))
from filters_v2.scale_normalized_filters import get_landmarks, JAW_LEFT, JAW_RIGHT, LEFT_EYE, RIGHT_EYE  # noqa: E402


def geo(lm):
    jaw = float(np.linalg.norm(lm[JAW_LEFT] - lm[JAW_RIGHT]))
    eye = float(np.mean([np.linalg.norm(lm[e[0]] - lm[e[1]]) for e in (LEFT_EYE, RIGHT_EYE)]))
    return jaw, eye


def hull_mask(lm, h, w):
    m = np.zeros((h, w), np.uint8); cv2.fillConvexPoly(m, cv2.convexHull(lm.astype(np.float32)).astype(np.int32), 255); return m > 0


def measure(po, pr):
    o = cv2.imread(str(po)); r = cv2.imread(str(pr))
    if o is None or r is None:
        return None
    o, r = o[..., ::-1], r[..., ::-1]
    if o.shape != r.shape:   # Tencent composites are 512x512 renders of the 1024 original: compare at the retouched size
        o = cv2.resize(o, (r.shape[1], r.shape[0]), interpolation=cv2.INTER_AREA)
    o = np.ascontiguousarray(o); r = np.ascontiguousarray(r)
    lo = get_landmarks(np.ascontiguousarray(o)); lr = get_landmarks(np.ascontiguousarray(r))
    if lo is None or lr is None:
        return None
    jo, eo = geo(lo); jr, er = geo(lr)
    h, w = o.shape[:2]; m = hull_mask(lo, h, w)
    Lo = cv2.cvtColor(o, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32); Lr = cv2.cvtColor(r, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
    hf = lambda L: np.abs(L - cv2.GaussianBlur(L, (0, 0), 3))[m].mean()
    return {"eye_ratio": er / eo, "jaw_ratio": jr / jo, "dL_skin": float((Lr - Lo)[m].mean()),
            "hf_ratio": float(hf(Lr) / max(hf(Lo), 1e-6)), "mad_hull": float(np.abs(r.astype(np.float32) - o.astype(np.float32))[m].mean()),
            "jaw_px": jo, "eye_px": eo}


def main():
    name, tsv = sys.argv[1], Path(sys.argv[2])
    rows = [l.split("\t") for l in tsv.read_text(encoding="utf-8").splitlines() if l.strip()]
    out = ["orig\tretouched\tgroup\teye_ratio\tjaw_ratio\tdL_skin\thf_ratio\tmad_hull\tjaw_px\teye_px"]
    for i, (po, pr, g) in enumerate(rows):
        m = measure(po, pr)
        if m:
            out.append("\t".join([po, pr, g] + [f"{m[k]:.5f}" for k in ("eye_ratio", "jaw_ratio", "dL_skin", "hf_ratio", "mad_hull", "jaw_px", "eye_px")]))
        if i % 500 == 0:
            print(i, len(rows), flush=True)
    (HERE / f"pairs_{name}.tsv").write_text("\n".join(out) + "\n", encoding="utf-8")
    import pandas as pd
    df = pd.read_csv(HERE / f"pairs_{name}.tsv", sep="\t")
    print(df.groupby("group")[["eye_ratio", "jaw_ratio", "dL_skin", "hf_ratio", "mad_hull"]].median().round(4).to_string())
    print("DONE", len(df))


if __name__ == "__main__":
    main()
