#!/bin/bash
# Local: wait for the EM arm on gsplat-ubuntu, fetch its epochs, evaluate with the Addendum 56 battery.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; LOG=add56_local.log; RV=../review_v4_exps_20261016; T=clipe5fbEM_s20260929
until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_$T.json"; do sleep 600; done
echo "ADD56 $T trained on ubuntu, fetching $(date)" >> $LOG
SEL=ffpp_auc bash run_add6_eval.sh $T clipe5fbEM 20260929 RU-$T RUCLIPE5M remote
$PY -u eval_fairbeauty_pairs.py $T >> eval_fb_add56.log 2>&1
$PY -u ar_pipeline_control.py $T >> ar_ctrl_add56.log 2>&1
(cd $RV && $PY -u ar_source.py score fb $T >> ar_add56.log 2>&1 && $PY -u ar_source.py score blfw $T >> ar_add56.log 2>&1 && $PY -u ar_source.py analyse >> ar_add56.log 2>&1)
$PY -u smooth_probe38.py score $T >> smooth38_score.log 2>&1
for c in clipe5fbE_s20260929 clipe5fbE_s20260930; do $PY -u eval_fairbeauty_pairs.py $c >> eval_fb_add56.log 2>&1; done   # the plug-in control on the same endpoint
echo "ADD56 $T evaluated $(date)" >> $LOG
