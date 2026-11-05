#!/bin/bash
# Official-crop scores for the arms trained after the first DFB pass (P0, P1, D1, 3-step), then re-analyse. Waits for each arm's local evaluation marker.
cd /c/My_Project/AIGC/results/research/ffpp_benchmark_20260925; export PYTHONIOENCODING=utf-8; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
M=/c/My_Project/AIGC/results/research/retouch_unified_20260929/add6.done
until grep -q "ADD25 clipe5fbp1_s20260929 DONE" $M; do sleep 300; done
for st in cdf dfd; do for n in clipe5fb_s20260929 clipe5fbp0_s20260929 clipe5fbp1_s20260929; do $PY -u dfb_crop_eval.py score $st $n >> dfb_crop_eval.log 2>&1; done; done
$PY -u dfb_crop_eval.py analyse >> dfb_crop_eval.log 2>&1; echo "DFB EVAL ROUND2 DONE $(date)" >> $M
