#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
for n in clipe5_s20260929 clipe5_s20260930 clipe5f_s20260929 clipe5fg0_s20260929 clipe5b_s20260929 clipe4r_s20260929; do
  $PY -u cdf_filtered_eval.py score $n >> cdf_filtered_ours.log 2>&1
  $PY -u dfd_v3_eval.py score $n >> dfd_v3_ours.log 2>&1
done
$PY -u cdf_filtered_eval.py analyse >> cdf_filtered_ours.log 2>&1
$PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1
echo "OURS RESCORED $(date)" >> add6.done
