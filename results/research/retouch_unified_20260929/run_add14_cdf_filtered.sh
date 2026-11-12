#!/bin/bash
# Score every detector on Celeb-DF-v2 untreated vs held-out-filtered (Addendum 14). Runs alongside training; one model per process.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
for n in sbi effort fadapter xception effnb4 f3net spsl ucf recce core srm univfd npr clipe4r_s20260929 clipe5_s20260929 clipe5_s20260930 clipe5b_s20260929 clipe5f_s20260929; do
  $PY -u cdf_filtered_eval.py score $n >> cdf_filtered_eval.log 2>&1
done
$PY -u cdf_filtered_eval.py analyse >> cdf_filtered_eval.log 2>&1
echo "CDF_FILTERED DONE $(date)" >> add6.done