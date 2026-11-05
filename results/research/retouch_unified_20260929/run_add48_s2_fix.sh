#!/bin/bash
# Addendum 48 seed 2: probes skipped because the model was not registered in smooth_probe38 (fixed 2026-10-22), then SCE readout for seed 2.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
$PY -u smooth_probe38.py score clipe5bzxs_s20260930 >> smooth38_score.log 2>&1
$PY -u bct.py score clipe5bzxs_s20260930 >> bct_score.log 2>&1
$PY -u sce_eval.py clipe5b_s20260930 clipe5bzxs_s20260930 > sce_s2.log 2>&1; cp SCE.md SCE_s2.md; cp sce.json sce_s2.json
echo "ADD48 s2 probes+SCE done $(date)" >> add48_local.log
