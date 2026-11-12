#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
$PY -u gpx_probe.py prep > gpx_prep.log 2>&1
for n in xception effnb4 f3net spsl ucf recce core srm sbi univfd npr effort fadapter gend dfdhr caddm laanetr clipe5b_s20260929 clipe5b_s20260930 clipe5bzl0_s20260929 clipe5bzsg_s20260929 clipe5bzsg_s20260930; do
  $PY -u gpx_probe.py score $n >> gpx_score.log 2>&1
done
$PY -u gpx_probe.py analyse > gpx_analyse.log 2>&1; echo "ADD54 DONE $(date)" >> add6.done
