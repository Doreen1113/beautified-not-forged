"""How varied are the explanation sentences in practice? Run explain_ours.explain on fixed test samples (every k-th item,
chosen before looking): FF++ test genuine, FF++ test forgeries (4 methods), Alibaba renders (4 ops x level 90) and
held-out part-level forgeries (donor / SD / SDXL). Count distinct sentences overall and per predicted label.

python sentence_stats.py -> sentence_stats.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
from explain_ours import explain, load_clip, BOX, ALI, B  # noqa: E402


def samples():
    rows = [l.split("\t") for l in (B / "results/research/ffpp_unified_20260925/ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:]]
    real = [r[0] for r in rows if r[1] == "0"][::13][:100]
    fake = [r[0] for r in rows if r[1] == "1"][::53][:100]
    ali = [(ALI / f"{op}_90/17000/{k}.png", BOX[k]) for op in ("EyeEnlarging", "FaceLifting", "Whitening", "Smoothing")
           for k in sorted(BOX)[::40][:25] if (ALI / f"{op}_90/17000/{k}.png").exists()]
    parts = [p for m in ("donor", "sd", "sdxl") for p in sorted((B / "ffpp_partedit/test" / m).glob("*.jpg"))[::121][:33]]
    return ([("FF++ genuine", p, None) for p in real] + [("FF++ forgery", p, None) for p in fake]
            + [("Alibaba render", p, b) for p, b in ali] + [("part forgery", p, None) for p in parts])


def main():
    net = load_clip("clipe4_s20260929", head=True).cuda().eval()
    per_group, per_label, allc = {}, {}, Counter()
    for g, p, b in samples():
        o, _, _ = explain(net, p, b)
        per_group.setdefault(g, Counter())[o["explanation"]] += 1
        per_label.setdefault(o["label"], Counter())[o["explanation"]] += 1; allc[o["explanation"]] += 1
    out = {"n_images": sum(allc.values()), "distinct_sentences": len(allc),
           "per_label": {k: {"n": sum(v.values()), "distinct": len(v), "sentences": dict(v.most_common())} for k, v in per_label.items()},
           "per_group": {k: dict(v.most_common()) for k, v in per_group.items()}}
    (HERE / "sentence_stats.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("n_images", "distinct_sentences")}),
          {k: (v["n"], v["distinct"]) for k, v in out["per_label"].items()})
    for k, v in out["per_label"].items():
        print("==", k); [print(f"  {c:4d}  {s}") for s, c in v["sentences"].items()]


if __name__ == "__main__":
    main()
