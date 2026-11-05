"""Create train_ru5b.py from train_ru5.py (train_ru5.py must not be edited while Windows runs are active) with three options:
--train-on-xs      expert for smoothed inputs: every item is replaced by its smoothed copy x_s (both classes smoothed by one operator),
                   forged BCE + map loss on x_s, no consistency term (Addendum 48)
--ffpp-methods     comma list of FF++ manipulations kept among the observed forgeries, e.g. Face2Face,FaceSwap (Addendum 49)
--precision        bf16 (default, as every other arm) | fp16 | fp32 (for GPUs without bf16; Addendum 48 note)
python make_train_ru5b.py"""
from pathlib import Path

H = Path(__file__).resolve().parent; s = (H / "train_ru5.py").read_text(encoding="utf-8")


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:70]); s = s.replace(old, new)


# argparse
rep('    ap.add_argument("--cons-hinge", action="store_true",',
    '    ap.add_argument("--train-on-xs", action="store_true", help="Addendum 48: smoothing expert, every item replaced by its smoothed copy (needs --smooth-consistency > 0 only to build x_s; the term itself is not used)")\n'
    '    ap.add_argument("--ffpp-methods", default="", help="Addendum 49: keep only these FF++ manipulations among observed forgeries, comma list")\n'
    '    ap.add_argument("--precision", choices=["bf16", "fp16", "fp32"], default="bf16")\n'
    '    ap.add_argument("--cons-hinge", action="store_true",')
# precision: autocast dtype everywhere
rep('torch.autocast("cuda", dtype=torch.bfloat16)', 'AC()', 3)
rep('    a = ap.parse_args()\n    if a.smooth_consistency:',
    '    a = ap.parse_args()\n    import contextlib\n    global AC\n    AC = (lambda: contextlib.nullcontext()) if a.precision == "fp32" else (lambda: torch.autocast("cuda", dtype=torch.float16 if a.precision == "fp16" else torch.bfloat16))\n    if a.smooth_consistency:')
# ffpp-methods: filter observed forgeries before the dataset is built
rep('    ds = (RUData7 if a.ar else RUData5)(rows, 224, a.seed,',
    '    if a.ffpp_methods:\n        keep = [m.strip() for m in a.ffpp_methods.split(",") if m.strip()]\n        n0 = len(rows); rows = [r for r in rows if r["src"] != "ffpp_fake" or any(("\\\\" + m + "\\\\") in r["path"] or ("/" + m + "/") in r["path"] for m in keep)]\n        print(f"ffpp-methods {keep}: observed forgeries {n0} -> {len(rows)} rows", flush=True)\n    ds = (RUData7 if a.ar else RUData5)(rows, 224, a.seed,')
# train-on-xs: use x_s in place of x, plain binary loss path
rep('            if a.smooth_consistency:\n                x = torch.cat([x, batch[9].flatten(0, 1).cuda(non_blocking=True)])',
    '            if a.smooth_consistency and a.train_on_xs:\n                x = batch[9].flatten(0, 1).cuda(non_blocking=True)   # Addendum 48: the smoothed copies only\n            elif a.smooth_consistency:\n                x = torch.cat([x, batch[9].flatten(0, 1).cuda(non_blocking=True)])')
rep('        if a.smooth_consistency:   # Addendum 46: out covers [x; x_s]',
    '        if a.smooth_consistency and a.train_on_xs:   # Addendum 48: forged BCE + map loss on the smoothed copies\n            zf = out[4][:, 0].float(); lc = F.binary_cross_entropy_with_logits(zf, zb[:, 0]); lm = mask_loss(out[3], m, mm)\n            return lc + a.wm * lm, (float(lc.detach()), 0.0, 0.0, float(lm.detach()))\n        if a.smooth_consistency:   # Addendum 46: out covers [x; x_s]')
# meta
rep('"cons_stopgrad": a.cons_stopgrad, "cons_hinge": a.cons_hinge,', '"cons_stopgrad": a.cons_stopgrad, "cons_hinge": a.cons_hinge, "train_on_xs": a.train_on_xs, "ffpp_methods": a.ffpp_methods, "precision": a.precision,')
# variant letters are unchanged; the arms are told apart by --tag-suffix
(H / "train_ru5b.py").write_text(s, encoding="utf-8"); print("train_ru5b.py written")
