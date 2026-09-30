#!/bin/bash
# MASK-D (evidence head + symmetric degradation, Addendum 3): when the local run finishes, run detection bars,
# Celeb-DF-B scoring, explanation bars on donor/sd/sdxl, and the robustness sweep; then regenerate the paper tables.
ARM=MASKD
cd /c/My_Project/AIGC/results/research/cgd_20260927
until [ -f meta_${ARM}_s20260928.json ]; do sleep 600; done
export PYTHONIOENCODING=utf-8
python -u eval_cgd_detect.py > eval_detect_${ARM}.log 2>&1
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 python -u score_cdfb.py --models cgd_${ARM} > score_cgd_${ARM}.log 2>&1 && CDFB_TAG=v3 python -u analyze_cdfb.py > analyze_cgd_${ARM}.log 2>&1)
MECH=donor,sd; grep -a -q "^DONE" ../partedit_20260927/gen_test_sdxl2.log 2>/dev/null && MECH=donor,sd,sdxl
python -u eval_cgd_explain.py --arm ${ARM} --mech $MECH > explain_${ARM}.log 2>&1
python -u eval_completeness.py --arm ${ARM} > completeness_${ARM}.log 2>&1
(cd /c/My_Project/AIGC && python docs/paper_v2/make_tables_cgd.py && python docs/paper_v2/make_tables.py) > tables_${ARM}.log 2>&1
echo "${ARM} evaluated $(date)" >> after_cgd.done
