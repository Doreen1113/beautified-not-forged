"""Create train_ru6.py from train_ru5b.py (train_ru5b.py must not be edited while runs are active) with two options (Addendum 56):
--multi-op P   with probability P a scripted beautification draw (_rop: the genuine 'synthetic' filter item and the landmark
               branch of beautification on forged faces) is replaced by mo_chain.apply: a random non-empty subset of
               {eye, jaw, white, smooth}, GPUPixel-style reshape + ported GPUPixel smoothing + whitening, multi-hot presence
--multi-k1     ablation: the same operators from mo_chain but always exactly one operation (no composition)
python make_train_ru6.py"""
from pathlib import Path

H = Path(__file__).resolve().parent; s = (H / "train_ru5b.py").read_text(encoding="utf-8")


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:70]); s = s.replace(old, new)


rep('sym_smooth=False, cons=False, cons_op="bilateral"):',
    'sym_smooth=False, cons=False, cons_op="bilateral", multi_op=0.0, multi_k1=False):')
rep('        self.cons_op = cons_op   # Amendment 7: bilateral (SIC) or gauss (ablation)',
    '        self.cons_op = cons_op   # Amendment 7: bilateral (SIC) or gauss (ablation)\n        self.multi_op, self.multi_k1 = multi_op, multi_k1   # Addendum 56')
rep('    def _rop(self, img, lm, rng):\n        """random_op_v2; under no_smooth the smoothing operation is redrawn."""',
    '    def _rop(self, img, lm, rng):\n        """random_op_v2; under no_smooth the smoothing operation is redrawn. Addendum 56: multi-operation chain with prob multi_op."""\n'
    '        if self.multi_op > 0 and rng.random() < self.multi_op:\n'
    '            import mo_chain\n'
    '            ops_ = [str(rng.choice(["eye", "jaw", "white", "smooth"]))] if self.multi_k1 else None\n'
    '            out, pres, q, _ = mo_chain.apply(img, lm, rng, ops=ops_)\n'
    '            return out, pres, q, "multi"')
rep('    ap.add_argument("--train-on-xs", action="store_true",',
    '    ap.add_argument("--multi-op", type=float, default=0.0, help="Addendum 56: probability that a scripted beautification draw is the multi-operation chain")\n'
    '    ap.add_argument("--multi-k1", action="store_true", help="Addendum 56 ablation: mo_chain operators, one operation at a time")\n'
    '    ap.add_argument("--train-on-xs", action="store_true",')
rep('**({"p_arfake": a.ar_fake} if a.ar else {}))',
    '**({"p_arfake": a.ar_fake} if a.ar else {}), **({"multi_op": a.multi_op, "multi_k1": a.multi_k1} if a.multi_op > 0 else {}))')
rep('"train_on_xs": a.train_on_xs,', '"train_on_xs": a.train_on_xs, "multi_op": a.multi_op, "multi_k1": a.multi_k1,')
(H / "train_ru6.py").write_text(s, encoding="utf-8"); print("train_ru6.py written")
