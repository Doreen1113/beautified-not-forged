"""Score the two 2025 SOTA detectors (Effort ICML'25, Forensics Adapter CVPR'25; official weights, authors' preprocessing) on
every set of the paper, writing the same score files the existing harnesses read (PRE_DECLARED Addendum 3: descriptive).

  ffpp_benchmark_20260925/scores_<d>.npz            real / fake / filter / escape  (FF++ test + escape set; B1 curves, Table I)
  ffpp_benchmark_20260925/cdfstd_v2_<d>.npz         std  (CDFv2 std32v2)      -> video_level.py
  ffpp_benchmark_20260925/cdfstd_dfdv2_<d>.npz      std  (DFD std32v2)
  celebdfb_v2_20260927/scores_v3/<d>.npz            p (N,3), binary padded    -> analyze_cdfb.py
  alipair_zeroshot_20260929/published_scores_<d>.npz s/group/stem              -> eval_published_ali.py analyse

python score_sota.py [effort fadapter]
"""
import sys
from pathlib import Path

import numpy as np

B = Path(r"C:\My_Project\AIGC"); R = B / "results/research"; sys.path.insert(0, str(B / "external_baselines"))
sys.path.insert(0, str(R / "alipair_zeroshot_20260929"))
UNI = R / "ffpp_unified_20260925"; SP = B / "splits/research/ffpp_benchmark_20260925"; BD = R / "ffpp_benchmark_20260925"


def rows(p):
    return [l.split("\t") for l in Path(p).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]


def main():
    dets = sys.argv[1:] or ["effort", "fadapter"]
    import importlib
    for d in dets:
        det = importlib.import_module({"effort": "effort_score", "fadapter": "fadapter_score"}[d]).Detector()
        score = lambda paths: np.asarray(det.score([str(p) for p in paths]), np.float32)
        # FF++ test + escape set (B1 curves)
        f = BD / f"scores_{d}.npz"
        if not f.is_file():
            t = rows(UNI / "ffpp3_test.txt"); y = np.array([int(r[1]) for r in t]); s = score([r[0] for r in t])
            esc = [l.split("\t")[0] for l in (B / "ffpp_escape_cache/manifest.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
            np.savez(f, real=s[y == 0], fake=s[y == 1], filter=s[y == 2], escape=score(esc)); print(d, "ffpp done", flush=True)
        # CDFv2 / DFD standard frame lists
        for nm, lst in (("v2", "celebdf_std32v2.txt"), ("dfdv2", "dfd_std32v2.txt")):
            f = BD / f"cdfstd_{nm}_{d}.npz"
            if not f.is_file():
                t = rows(SP / lst); np.savez(f, std=score([r[0] for r in t]), old=np.zeros(0, np.float32)); print(d, nm, "done", flush=True)
        # Celeb-DF-B v3
        f = R / "celebdfb_v2_20260927/scores_v3" / f"{d}.npz"
        if not f.is_file():
            t = rows(B / "splits/research/celebdfb_v2_20260927/cdfb_std32v3.txt"); paths = [r[0] for r in t]; s = score(paths)
            np.savez(f, p=np.stack([1 - s, s, np.zeros_like(s)], 1), paths=np.array(paths)); print(d, "cdfb done", flush=True)
        # Alibaba pairs (shared-box crops)
        f = R / "alipair_zeroshot_20260929" / f"published_scores_{d}.npz"
        if not f.is_file():
            from eval_published_ali import listing
            paths, g, st = listing(); np.savez(f, s=score(paths), group=g, stem=st); print(d, "alibaba done", flush=True)
        del det
        import torch; torch.cuda.empty_cache()
    print("DONE")


if __name__ == "__main__":
    main()
