"""Table of training / validation / test accuracy of the two main models on every data source (tables/tab_splits.tex).
Every value is read from results/research/retouch_unified_20260929/split_eval.json (split_eval.py) and the partition sizes
from the manifests that the training scripts read.

python docs/paper_v2/make_tables_splits.py
"""
import json
from pathlib import Path

B = Path(r"C:\My_Project\AIGC"); RU = B / "results/research/retouch_unified_20260929"; OUT = B / "docs/paper_v2/tables"
J = json.loads((RU / "split_eval.json").read_text())
MODELS = ["Ours", "Ours-lite"]


def sizes():
    """Full partition sizes (the accuracy on the training partition is measured on the sample in split_eval.json)."""
    def count(f, col, keep=None):
        rows = [l.split("\t") for l in Path(f).read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
        return rows if keep is None else [r for r in rows if keep(r)]
    U = B / "results/research/ffpp_unified_20260925"; PE = B / "results/research/partedit_20260927"
    n = {}
    for sp in ("train", "val", "test"):
        r = count(U / f"ffpp3_{sp}.txt", 1)
        for i, c in enumerate(("real", "fake", "filter")):
            n[("ffpp", c, sp)] = sum(1 for x in r if x[1] == str(i))
    meta = json.loads((RU / "meta_ru_ru4e_effb4_s20260929.json").read_text())
    tr = count(RU / "manifest_train.tsv", 2)
    n[("vendor", "original", "train")] = sum(1 for x in tr if x[2] == "ffhq_orig")
    n[("vendor", "render", "train")] = sum(1 for x in tr if x[2] in ("tencent", "megvii"))
    n[("vendor", "component", "train")] = meta["n_single"]          # cleaned components the models were trained on
    for s, v in J["Ours"]["vendor/val"]["by_source"].items():
        n[("vendor", s, "val")] = v["n"]
    for s, v in J["Ours"]["vendor/test"]["by_source"].items():
        n[("vendor", s, "test")] = v["n"]
    n[("part", "fake", "train")] = sum(len(count(PE / f"manifest_train_{m}.tsv", 1)) for m in ("donor", "sd"))
    n[("part", "fake", "test")] = J["Ours"]["part/test"]["n"]
    return n


def acc(model, key, row):
    """(value, how) for one cell; None when the partition does not exist."""
    R = J[model]
    src, cls = key
    if src == "ffpp":
        def get(sp):
            r = R.get(f"ffpp/{sp}")
            return None if r is None else (r["macro_f1"] if cls == "macro" else r["recall"][cls])
    elif src == "vendor":
        target = "real" if cls == "original" else "filter"
        def get(sp):
            r = R.get(f"vendor/{sp}")
            if r is None or cls not in r["by_source"]:
                return None
            return r["by_source"][cls][target]
    else:
        def get(sp):
            r = R.get(f"part/{sp}")
            return None if r is None else r["recall"]["fake"]
    return [get(sp) for sp in ("train", "val", "test")]


def fmt(v):
    return "--" if v is None else f"{v:.1f}"


def fmtn(v):
    return "--" if v is None else f"{v:,}"


def main():
    n = sizes()
    rows = [("FF++ c23", "real", ("ffpp", "real"), "recall"), ("", "fake", ("ffpp", "fake"), "recall"),
            ("", "filter", ("ffpp", "filter"), "recall"), ("", "macro-F1", ("ffpp", "macro"), "macro-F1"),
            ("Commercial", "originals $\\to$ real", ("vendor", "original"), ""),
            ("", "renders $\\to$ filter", ("vendor", "render"), ""),
            ("", "components $\\to$ filter", ("vendor", "component"), ""),
            ("Part-level", "forgeries $\\to$ fake", ("part", "fake"), "")]
    L = [r"\begin{tabular}{@{}llrrr|rrr|rrr@{}}", r"\toprule",
         r" & & \multicolumn{3}{c|}{Images} & \multicolumn{3}{c|}{\ours{}} & \multicolumn{3}{c}{\ours{}-lite} \\",
         r"Data & Class & train & val & test & train & val & test & train & val & test \\", r"\midrule"]
    for k, (data, lab, key, _) in enumerate(rows):
        if k in (4, 7):
            L.append(r"\midrule")
        src, cls = key
        if cls == "macro":
            ns = ["", "", ""]
        else:
            nk = {"ffpp": cls, "vendor": cls, "part": "fake"}[src]
            ns = [fmtn(n.get((src, nk, sp))) for sp in ("train", "val", "test")]
        cells = [fmt(v) for m in MODELS for v in acc(m, key, None)]
        L.append(f"{data} & {lab} & " + " & ".join(ns) + " & " + " & ".join(cells) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_splits.tex").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))


if __name__ == "__main__":
    main()
