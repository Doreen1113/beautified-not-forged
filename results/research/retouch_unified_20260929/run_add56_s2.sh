#!/bin/bash
# Addendum 56 seed 2 restart: the first attempt died at step ~2,200 with a DataLoader MemoryError (host RAM, four evaluations
# running at the same time). Same arguments, 6 workers instead of 12 (workers do not change the data stream: per-item seeds).
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; LOG=add56_local.log; RV=../review_v4_exps_20261016; T=clipe5M_s20260930
mv train_ru_$T.log train_ru_${T}_attempt1.log
echo "ADD56 $T restart (6 workers) $(date)" >> $LOG
$PY -u train_ru6.py --multi-op 0.5 --tag-suffix M --seed 20260930 --workers 6 > train_ru_$T.log 2>&1
[ -f meta_ru_$T.json ] || { echo "ADD56 $T FAILED again $(date)" >> $LOG; exit 1; }
SEL= bash run_add6_eval.sh $T clipe5M 20260930 RU-$T RUCLIPE5M local
$PY -u eval_fairbeauty_pairs.py $T >> eval_fb_add56.log 2>&1
$PY -u ar_pipeline_control.py $T >> ar_ctrl_add56.log 2>&1
$PY -u fb_ops_probe.py score $T >> fb_ops_score.log 2>&1; $PY -u fb_ops_probe.py analyse > fb_ops_analyse.log 2>&1
(cd $RV && $PY -u ar_source.py score fb $T >> ar_add56.log 2>&1 && $PY -u ar_source.py score blfw $T >> ar_add56.log 2>&1 && $PY -u ar_source.py analyse >> ar_add56.log 2>&1)
$PY -u smooth_probe38.py score $T >> smooth38_score.log 2>&1
echo "ADD56 $T evaluated $(date)" >> $LOG
