"""English T2 fixture (2026-10-15): the same 50 records as fixture_t2.json, with the expected English sentences computed
by the Python twin results/research/explain_vlm_20261012/nl_v5/explain_v2_en.py (imported, not re-implemented).

  python docs/demo_ru/test/make_fixture_en.py   -> fixture_t2_en.json + fixture_t2_en.js (window.T2_FIXTURE_EN)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "results" / "research" / "explain_vlm_20261012" / "nl_v5"))
import explain_v2_en  # noqa: E402


def synthetic():
    """Branches the 50 real records do not reach (they name one part and at most one operation): 2 and 3 parts, 2 and 4
    operations at/above threshold, a 0.50 boundary score. Marked synthetic; not model outputs."""
    base = {"probabilities": {"real": 0.05, "fake": 0.10, "filter": 0.85}, "operation_threshold": 0.5,
            "evidence_mean_per_part": {"eyes": 0.62, "nose": 0.31, "mouth": 0.55, "skin": 0.58, "contour": 0.12}, "whole_face": False}
    return [
        {**base, "id": "synthetic:two_parts_two_ops", "decision": "filter", "named_parts": ["eyes", "mouth"],
         "operations": {"eye_enlargement": 0.66, "face_slimming": 0.12, "skin_brightening": 0.08, "skin_smoothing": 0.91}},
        {**base, "id": "synthetic:three_parts_four_ops", "decision": "filter", "named_parts": ["eyes", "skin", "mouth"],
         "operations": {"eye_enlargement": 0.50, "face_slimming": 0.77, "skin_brightening": 0.93, "skin_smoothing": 0.99}},
        {**base, "id": "synthetic:fake_two_parts", "decision": "fake", "probabilities": {"real": 0.01, "fake": 0.97, "filter": 0.02},
         "named_parts": ["nose", "mouth"], "operations": {"eye_enlargement": 0.1, "face_slimming": 0.1, "skin_brightening": 0.1, "skin_smoothing": 0.1}},
        {**base, "id": "synthetic:filter_boundary_049", "decision": "filter", "named_parts": ["contour"],
         "operations": {"eye_enlargement": 0.49, "face_slimming": 0.5, "skin_brightening": 0.2, "skin_smoothing": 0.3}},
    ]


def main():
    fx = json.loads((HERE / "fixture_t2.json").read_text(encoding="utf-8"))
    out = []
    for r in fx["records"] + synthetic():
        j = {k: v for k, v in r.items() if k not in ("t2_sentences", "t2_text", "old_template_text", "evidence_map16")}
        j["t2_sentences_en"] = list(explain_v2_en.t2_sentences_en(r))
        j["t2_text_en"] = explain_v2_en.compose_en(r)
        out.append(j)
    fixture = {"source": "fixture_t2.json (same 50 records)", "expected_from": "nl_v5/explain_v2_en.t2_sentences_en / compose_en (Python)",
               "note": "records 1-50 = fixture_t2.json; 51-54 synthetic branch cases (multi-part, multi-operation, 0.50 boundary)",
               "n": len(out), "records": out}
    txt = json.dumps(fixture, ensure_ascii=False, indent=1)
    (HERE / "fixture_t2_en.json").write_text(txt, encoding="utf-8")
    (HERE / "fixture_t2_en.js").write_text("window.T2_FIXTURE_EN = " + txt + ";\n", encoding="utf-8")
    print("records", len(out))
    for r in out[-4:]:
        print(r["decision"], "|", r["t2_text_en"])


if __name__ == "__main__":
    main()
