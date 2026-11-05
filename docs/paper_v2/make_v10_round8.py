"""Round 8 (2026-10-29): Addendum 63/64 closures, one sentence each in Limitations (pre-registered reading rule of Add. 64:
'(1) fails -> one sentence in the limitations'). Exact string replacement in the three main variants; abort if an anchor is
missing or repeated; idempotent (a file already carrying the sentence is left alone).
Sources: results/research/retouch_unified_20260929/CDFB_GATE.md, CDFB_RPPG.md."""
from pathlib import Path

NOTE = ("% results/research/retouch_unified_20260929/CDFB_GATE.md (Addendum 63): dFA +11.5..+17.1, dMISS -5.4..-10.4\n"
        "% results/research/retouch_unified_20260929/CDFB_RPPG.md (Addendum 64): AUC 0.514; peak agreement 0.439 vs 0.187")
FULL_OLD = ("Language-model explanations did not differ from template sentences in any measured respect and\n"
            "were removed; localisation of part-level forgeries and its restoration test are in the supplement.")
FULL_NEW = FULL_OLD + (
    "\nTwo further channels were tested without training and closed: weighting the texture--identity fusion by the model's own\n"
    "beautified estimate moves the error from misses to false alarms, since the estimate rises on beautified genuine faces as on\n"
    "beautified forgeries; and the pulse signal of remote photoplethysmography has no separation to lose on Celeb-DF (video AUC\n"
    "0.51), because the swaps inherit the driving video's pulse (peak frequency agreement with the source video 44\\% against\n"
    "19\\% by chance).\n" + NOTE)
CONF_OLD = "Language-model explanations were removed (supplement), as was part-level localisation."
CONF_NEW = CONF_OLD + (
    "\nTwo further reference-free channels were closed: a fusion weighted by the model's own beautified estimate trades misses for\n"
    "false alarms, and the remote-photoplethysmography pulse has no separation on Celeb-DF (video AUC 0.51; the swaps inherit the\n"
    "driving video's pulse).\n" + NOTE)
for f, old, new in (("main_v10.tex", FULL_OLD, FULL_NEW), ("main_v10j.tex", FULL_OLD, FULL_NEW), ("main_v10c.tex", CONF_OLD, CONF_NEW)):
    p = Path(f); t = p.read_text(encoding="utf-8")
    if "(Addendum 64): AUC 0.514" in t:
        assert t.count(NOTE) == 1 and ("44\\% against" in t or f == "main_v10c.tex"), f
        print("already patched", f); continue
    assert t.count(old) == 1, (f, t.count(old))
    p.write_text(t.replace(old, new), encoding="utf-8"); print("patched", f)
