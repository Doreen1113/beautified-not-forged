#!/bin/bash
# Addendum 15: evaluate the worst-case run (local) and the random-operator control (Ubuntu), then RU8.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
one() {  # $1 tag  $2 arm  $3 where  $4 selection rule
  SEL=$4 bash run_add6_eval.sh $1 $2 20260929 RU-$1 RUCLIPE${2#clipe} $3
  $PY -u cdf_filtered_eval.py score $1 >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $1 >> dfd_v3_ours.log 2>&1
}
until [ -f meta_ru_clipe5af_s20260929.json ]; do sleep 180; done
one clipe5af_s20260929 clipe5af local ffpp_f1
until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_clipe5rf_s20260929.json"; do sleep 300; done
one clipe5rf_s20260929 clipe5rf remote ffpp_f1
$PY -u cdf_filtered_eval.py analyse >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1
echo "ADD15 DONE $(date)" >> add6.done
