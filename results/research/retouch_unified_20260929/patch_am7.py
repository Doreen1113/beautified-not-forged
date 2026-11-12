"""Amendment 7: --cons-op gauss, a Gaussian-blur consistency operator with the same spatial support and kernel scale as the
skin-smoothing operator (ablation: is it the smoothing signature or any blur?). Applies to train_ru5.py in place."""
from pathlib import Path

p = Path(__file__).resolve().parent / "train_ru5.py"; s = p.read_text(encoding="utf-8")

# 1. import hull_mask and the jaw indices
old = "from ops import random_op_v2, op_smooth  # noqa: E402"
assert s.count(old) == 1
s = s.replace(old, "from ops import random_op_v2, op_smooth, hull_mask, JAW_LEFT, JAW_RIGHT  # noqa: E402")

# 2. Gaussian face-local operator (module level, after the import block: insert before 'class RUData5')
old = "class RUData5("
assert s.count(old) == 1
gauss = '''def op_gauss_facelocal(rgb, lm, rng, frac, mix):
    """Amendment 7 ablation: the face-local operator of op_smooth with the bilateral filter replaced by a Gaussian blur of the
    same kernel scale (sigma = d / 4), blended inside the same feathered hull with the same mix. Uniform blur, not edge-preserving."""
    h, w = rgb.shape[:2]; m = hull_mask(lm, h, w)
    jaw_w = float(np.linalg.norm(lm[JAW_LEFT] - lm[JAW_RIGHT])); d = int(np.clip(round(frac * jaw_w), 5, 45)) | 1
    sm = cv2.GaussianBlur(rgb, (0, 0), max(0.8, d / 4.0))
    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), max(2.0, 0.01 * w))[..., None] * mix
    return np.clip(rgb * (1 - a) + sm * a, 0, 255).astype(np.uint8)


'''
s = s.replace(old, gauss + old, 1)

# 3. dataset: cons_op parameter
old = "sym_smooth=False, cons=False):"
assert s.count(old) == 1
s = s.replace(old, 'sym_smooth=False, cons=False, cons_op="bilateral"):')
old = "        self.cons = cons   # Addendum 46"
assert s.count(old) == 1
s = s.replace(old, "        self.cons_op = cons_op   # Amendment 7: bilateral (SIC) or gauss (ablation)\n" + old)

# 4. _smoothed_views: branch on cons_op
old = '                d = [(9, 50, 50), (15, 80, 80), (21, 100, 100)][int(rs.integers(0, 3))]; s_ = cv2.bilateralFilter(im, *d); forms.append(f"bil{d[0]}")'
assert s.count(old) == 1
s = s.replace(old, '''                d = [(9, 50, 50), (15, 80, 80), (21, 100, 100)][int(rs.integers(0, 3))]
                if self.cons_op == "gauss":
                    s_ = cv2.GaussianBlur(im, (0, 0), d[0] / 4.0); forms.append(f"gauss{d[0]}")
                else:
                    s_ = cv2.bilateralFilter(im, *d); forms.append(f"bil{d[0]}")''')
old = '                s_ = op_smooth(im, l2, rs, frac=float(rs.uniform(0.03, 0.14)), mix=float(rs.uniform(0.3, 1.0)))[0]; forms.append("face-local")'
assert s.count(old) == 1
s = s.replace(old, '''                fr_, mx_ = float(rs.uniform(0.03, 0.14)), float(rs.uniform(0.3, 1.0))
                if self.cons_op == "gauss":
                    s_ = op_gauss_facelocal(im, l2, rs, fr_, mx_); forms.append("face-local-gauss")
                else:
                    s_ = op_smooth(im, l2, rs, frac=fr_, mix=mx_)[0]; forms.append("face-local")''')

# 5. argparse, dataset kwargs, meta
old = '    ap.add_argument("--cons-stopgrad", action="store_true",'
assert s.count(old) == 1
s = s.replace(old, '    ap.add_argument("--cons-op", choices=["bilateral", "gauss"], default="bilateral", help="Amendment 7: operator of the consistency view (gauss = ablation with a uniform blur of the same support and scale)")\n' + old)
old = '**({"cons": True} if a.smooth_consistency else {})'
assert s.count(old) == 1
s = s.replace(old, '**({"cons": True, "cons_op": a.cons_op} if a.smooth_consistency else {})')
old = '"cons_stopgrad": a.cons_stopgrad, "grad_ckpt": a.grad_ckpt,'
assert s.count(old) == 1
s = s.replace(old, '"cons_stopgrad": a.cons_stopgrad, "cons_op": a.cons_op, "grad_ckpt": a.grad_ckpt,')
p.write_text(s, encoding="utf-8"); print("patched train_ru5.py")
