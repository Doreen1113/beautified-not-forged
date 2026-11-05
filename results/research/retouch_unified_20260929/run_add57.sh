#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
$PY -u bdry_probe.py prep > bdry_prep.log 2>&1
for n in xception effnb4 f3net spsl ucf recce core srm sbi univfd npr effort fadapter gend dfdhr caddm laanetr clipe5b_s20260929 clipe5_s20260929 clipe5bzl0_s20260929 clipe5bzsg_s20260929; do
  $PY -u bdry_probe.py score $n >> bdry_score.log 2>&1
done
$PY -u bdry_probe.py analyse > bdry_analyse.log 2>&1; echo "ADD57 DONE $(date)" >> add6.done
