"""Round 9 (2026-10-29): Addenda 65, 68, 69 (results/research/refcond_20261029/PRE_DECLARED.md) in the identity subsection of
main_v10, main_v10j (full paragraph) and main_v10c (source comment only; the sentence did not fit the 8-page body). Reading rules: Add. 65 'one sentence with the ICC and the null
gain'; Add. 68 'a reference of the same person helps exactly for the edit whose natural variation is identity-stable'; Add. 69
'the Addendum 68 2-D ratio stays the reported measurement'. Adds two bib entries checked against IEEE Xplore / DOAJ and dblp
(rathgeb2020diff: IEEE Access 8, 106373-106385, doi 10.1109/ACCESS.2020.3000254; tddfav2: ECCV 2020, 152-168,
doi 10.1007/978-3-030-58529-7_10). Exact string insertion after a unique anchor; abort if the anchor is missing or repeated;
idempotent. Strings are raw so that LaTeX backslashes survive."""
from pathlib import Path

ANCHOR = "% AUC 0.59 without a reference: FFPP_ARCFACE.md (Addendum 53)"
NOTE = ("% results/research/refcond_20261029/REFCOND_65.md (Add. 65): C1 ours 0.720 -> 0.718, gain -0.002 [-0.015, 0.011]; ICC ours 0.14,\n"
        "% texture detectors 0.12-0.46, skin texture 0.06-0.07, skin colour 0.14-0.32, face width 0.66. GEO68.md (Add. 68): face width,\n"
        "% jaw 0.10 (-2.25 %), 0.635 -> 0.727, gain +0.092 [+0.067, +0.116]; ours +0.002..+0.010. GEO3D_69.md (Add. 69): -0.22 %, gain +0.028.")
FULL = r"""
A reference of the claimed person does not, however, catch the beautification itself. Across one person's untreated
videos, the share of score variance that belongs to the person (intraclass correlation, ICC) is 0.14 for our beautified score,
0.12--0.46 for the texture detectors and 0.06--0.32 for skin texture and colour; subtracting the person's reference mean leaves
the preset-only AUC where it was (ours 0.720 and 0.718, gain $-0.002$ [$-0.015$, 0.011]; seven texture detectors $-0.023$ to
$+0.005$). Face width is identity-stable (ICC 0.66): on the benchmark's genuine videos narrowed by 2.25\%, the same reference
lifts the video AUC of a landmark width ratio from 0.635 to 0.727 (gain $+0.092$ [0.067, 0.116], short of the pre-declared
$+0.10$), while our beautified score gains nothing on the same images. The variation that hides a light colour or texture edit
belongs to the capture, not to the person, so a reference helps only for edits of the person's geometry, the part that
differential retouching detection reads from landmarks~\cite{rathgeb2020diff}. A 3D morphable-model fit~\cite{tddfav2} is
steadier across one person's videos but registers 0.2\% of the 2.25\% narrowing, so it is the wrong instrument for edits of
this size.
""" + NOTE
CONF = r"""
% Add. 65/68/69 sentence omitted in the IJCB cut: it pushed the conclusion onto p. 9 (2026-10-29 build).
""" + NOTE
BIB = r"""
@article{rathgeb2020diff,
  title   = {Differential Detection of Facial Retouching: A Multi-Biometric Approach},
  author  = {Rathgeb, Christian and Satnoianu, Cristian-Ionut and Haryanto, Nicolas E. and Bernardo, Kevin and Busch, Christoph},
  journal = {IEEE Access},
  volume  = {8}, pages = {106373--106385}, year = {2020},
  doi     = {10.1109/ACCESS.2020.3000254}
}
@inproceedings{tddfav2,
  title     = {Towards Fast, Accurate and Stable {3D} Dense Face Alignment},
  author    = {Guo, Jianzhu and Zhu, Xiangyu and Yang, Yang and Yang, Fan and Lei, Zhen and Li, Stan Z.},
  booktitle = {European Conference on Computer Vision (ECCV)},
  pages     = {152--168}, year = {2020},
  doi       = {10.1007/978-3-030-58529-7_10}
}
"""
for f, add in (("main_v10.tex", FULL), ("main_v10j.tex", FULL), ("main_v10c.tex", CONF)):
    p = Path(f); t = p.read_text(encoding="utf-8")
    if "REFCOND_65.md (Add. 65)" in t:
        assert t.count(NOTE) == 1, f; print("already patched", f); continue
    assert t.count(ANCHOR) == 1, (f, t.count(ANCHOR))
    p.write_text(t.replace(ANCHOR, ANCHOR + add.rstrip("\n")), encoding="utf-8"); print("patched", f)
b = Path("refs_v8.bib"); t = b.read_text(encoding="utf-8")
if "rathgeb2020diff" not in t:
    b.write_text(t.rstrip() + "\n" + BIB, encoding="utf-8"); print("bib added")
else:
    print("bib already has entries")
