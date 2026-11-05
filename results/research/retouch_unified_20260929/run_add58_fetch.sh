#!/bin/bash
# Local: wait for each W seed on gsplat-ubuntu, fetch, evaluate on the Addendum 58 endpoints.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; LOG=add58_local.log; RV=../review_v4_exps_20261016
for T in clipe7W_s20260929 clipe7W_s20260930; do
  until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_$T.json"; do sleep 600; done
  echo "ADD58 $T trained, fetching $(date)" >> $LOG
  bash run_add6_eval.sh $T clipe7W ${T##*_s} RU-$T RUCLIPE7W remote
  $PY -u eval_fairbeauty_pairs.py $T >> eval_fb_add58.log 2>&1
  $PY -u ar_pipeline_control.py $T >> ar_ctrl_add58.log 2>&1
  (cd $RV && $PY -u ar_source.py score fb $T >> ar_add58.log 2>&1 && $PY -u ar_source.py score blfw $T >> ar_add58.log 2>&1)
  echo "ADD58 $T evaluated $(date)" >> $LOG
done
