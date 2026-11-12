#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
$PY -u fb_ops_probe.py measure > fb_ops_measure.log 2>&1
$PY -u fb_ops_probe.py score clipe5_s20260929 clipe7_s20260929 > fb_ops_score.log 2>&1
$PY -u fb_ops_probe.py analyse > fb_ops_analyse.log 2>&1
echo "ADD55 DONE $(date)" >> add6.done
