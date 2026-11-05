"""Export 50 records of results/research/explain_vlm_20261012/evidence.jsonl as the T2 equivalence fixture.

The expected text comes from the Python module explain_v2.py (imported, not re-implemented). Records are chosen with
seed 0, stratified over (decision, whole-face, any operation at/above threshold) so that every sentence branch is
covered; the 16x16 evidence map of each record is included for the contour-overlay check page.

  python docs/demo_ru/test/make_fixture.py
-> docs/demo_ru/test/fixture_t2.json  (data)   and   fixture_t2.js  (same data as window.T2_FIXTURE, for file:// pages)
"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "results" / "research" / "explain_vlm_20261012"
sys.path.insert(0, str(EXP))
import explain_v2  # noqa: E402

HERE = Path(__file__).resolve().parent
N = 50


def stratum(j):
    above = any(j["operations"][o] >= j["operation_threshold"] for o in explain_v2.OPS)
    return (j["decision"], explain_v2.is_whole(j), above if j["decision"] == "filter" else None)


def main():
    recs = [json.loads(l) for l in (EXP / "evidence.jsonl").open(encoding="utf-8")]
    maps = np.load(EXP / "evidence_maps.npz")
    groups = {}
    for r in recs:
        groups.setdefault(stratum(r), []).append(r)
    rng = np.random.default_rng(0)
    for k in groups:
        groups[k] = [groups[k][i] for i in rng.permutation(len(groups[k]))]
    keys = sorted(groups, key=lambda k: (str(k[0]), str(k[1]), str(k[2])))
    chosen = []
    while len(chosen) < N:  # round robin over strata so that rare branches are represented
        progressed = False
        for k in keys:
            if groups[k] and len(chosen) < N:
                chosen.append(groups[k].pop()); progressed = True
        if not progressed:
            break
    out = []
    for r in chosen:
        s1, s2, s3, s4 = explain_v2.t2_sentences(r)
        j = {k: v for k, v in r.items() if k not in ("image", "x0")}  # no local file paths in the fixture
        j["image"] = Path(r["image"]).name
        j["x0"] = Path(r["x0"]).name if r.get("x0") else None
        j["t2_sentences"] = [s1, s2, s3, s4]
        j["t2_text"] = explain_v2.compose(r)
        j["old_template_text"] = r["template_text"]
        j["evidence_map16"] = [[round(float(v), 4) for v in row] for row in maps[r["id"]]]
        out.append(j)
    counts = {}
    for r in chosen:
        counts[str(stratum(r))] = counts.get(str(stratum(r)), 0) + 1
    fixture = {"source": "results/research/explain_vlm_20261012/evidence.jsonl + evidence_maps.npz",
               "expected_from": "explain_v2.t2_sentences / compose (Python), run by make_fixture.py", "seed": 0,
               "n": len(out), "strata_counts": counts, "records": out}
    txt = json.dumps(fixture, ensure_ascii=False, indent=1)
    (HERE / "fixture_t2.json").write_text(txt, encoding="utf-8")
    (HERE / "fixture_t2.js").write_text("window.T2_FIXTURE = " + txt + ";\n", encoding="utf-8")
    print("records", len(out)); print(json.dumps(counts, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
