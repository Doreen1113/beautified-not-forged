#!/bin/bash
# Addendum 56: multi-operation beautification arms, local bf16, one at a time after the Addendum 48 expert (seed 2) finishes training.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; LOG=add56_local.log; RV=../review_v4_exps_20261016
echo "ADD56 queue start $(date); train_ru6.py md5 $(md5sum train_ru6.py | cut -c1-32); mo_chain.py md5 $(md5sum mo_chain.py | cut -c1-32)" >> $LOG
until [ -f meta_ru_clipe5bzxs_s20260930.json ]; do sleep 300; done
grep -q "step 200" smoke_clipe5Msmoke.log || { echo "SMOKE NOT PASSED, abort $(date)" >> $LOG; exit 1; }

evaluate () {   # $1 tag, $2 arm (for eval_ru), $3 seed, $4 selection criterion ("" = C2 three-class rule)
  T=$1
  SEL=$4 bash run_add6_eval.sh $T $2 $3 RU-$T RUCLIPE5M local
  $PY -u eval_fairbeauty_pairs.py $T >> eval_fb_add56.log 2>&1
  $PY -u ar_pipeline_control.py $T >> ar_ctrl_add56.log 2>&1
  $PY -u fb_ops_probe.py score $T >> fb_ops_score.log 2>&1; $PY -u fb_ops_probe.py analyse > fb_ops_analyse.log 2>&1
  (cd $RV && $PY -u ar_source.py score fb $T >> ar_add56.log 2>&1 && $PY -u ar_source.py score blfw $T >> ar_add56.log 2>&1 && $PY -u ar_source.py analyse >> ar_add56.log 2>&1)
  $PY -u smooth_probe38.py score $T >> smooth38_score.log 2>&1
  echo "ADD56 $T evaluated $(date)" >> $LOG
}

train () {   # $1 tag, rest = args
  T=$1; shift
  echo "ADD56 $T training $(date)" >> $LOG
  $PY -u train_ru6.py "$@" --workers 12 > train_ru_$T.log 2>&1
  [ -f meta_ru_$T.json ] || { echo "ADD56 $T FAILED $(date)" >> $LOG; return 1; }
}

train clipe5M_s20260929 --multi-op 0.5 --tag-suffix M --seed 20260929 && evaluate clipe5M_s20260929 clipe5M 20260929 "" &
until [ -f meta_ru_clipe5M_s20260929.json ]; do sleep 120; done
train clipe5M1_s20260929 --multi-op 0.5 --multi-k1 --tag-suffix M1 --seed 20260929 && evaluate clipe5M1_s20260929 clipe5M1 20260929 "" &
until [ -f meta_ru_clipe5M1_s20260929.json ]; do sleep 120; done
train clipe5M_s20260930 --multi-op 0.5 --tag-suffix M --seed 20260930 && evaluate clipe5M_s20260930 clipe5M 20260930 "" &
until [ -f meta_ru_clipe5M_s20260930.json ]; do sleep 120; done
train clipe5fbEM_s20260929 --ffpp-only --binary --tune effort --multi-op 0.5 --tag-suffix M --seed 20260929 && evaluate clipe5fbEM_s20260929 clipe5fbEM 20260929 ffpp_auc &
wait
echo "ADD56 DONE $(date)" >> $LOG; echo "ADD56 DONE $(date)" >> add6.done
