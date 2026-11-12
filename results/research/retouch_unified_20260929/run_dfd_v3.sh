#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
until grep -q "DONOR_V2 DONE" add6.done; do sleep 180; done
for n in sbi effort fadapter xception effnb4 f3net spsl ucf recce core srm clipe4r_s20260929 clipe5_s20260929 clipe5_s20260930 clipe5b_s20260929 clipe5f_s20260929; do
  $PY -u dfd_v3_eval.py score $n >> dfd_v3_eval.log 2>&1
done
$PY -u dfd_v3_eval.py analyse >> dfd_v3_eval.log 2>&1
echo "DFD_V3 DONE $(date)" >> add6.done