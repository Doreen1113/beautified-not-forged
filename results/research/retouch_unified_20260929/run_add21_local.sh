#!/bin/bash
# Addendum 21 on the local GPU: after R2-3 seed 2, the equal-data binary baseline (D1) and D1 + part-level forgeries (D2); evaluate each.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
ev() {
  T=$1; ARM=${T%_s*}; export SEL=ffpp_auc
  bash run_add6_eval.sh $T $ARM ${T#*_s} RU-$T RUCLIPE${ARM#clipe} local
  $PY -u cdf_filtered_eval.py score $T >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $T >> dfd_v3_ours.log 2>&1
  FSRC=dfd $PY -u cdf_filtered_eval.py score $T >> dfd_filtered_score.log 2>&1
  $PY -u cdf_filtered_eval.py analyse >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1; FSRC=dfd $PY -u cdf_filtered_eval.py analyse >> dfd_filtered_score.log 2>&1
  echo "ADD21 $T DONE $(date)" >> add6.done
}
until [ -f meta_ru_clipe5awpb_s20260930.json ]; do sleep 120; done
$PY -u train_ru5.py --binary --ffpp-only --ffpp-parts --seed 20260929 --workers 12 > train_ru_clipe5feb_s20260929.log 2>&1 &
TR=$!; ev clipe5awpb_s20260930; wait $TR
$PY -u train_ru5.py --binary --ffpp-only --seed 20260929 --workers 12 > train_ru_clipe5fb_s20260929.log 2>&1 &
TR=$!; ev clipe5feb_s20260929; wait $TR
ev clipe5fb_s20260929
echo "ADD21 DONE $(date)" >> add6.done
