#!/bin/bash
# Addendum 48 second seed of the smoothing expert, local bf16; evaluation via the same steps as run_add46_seed2_chain.sh.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; RV=../review_v4_exps_20261016; LOG=add48_local.log; T=clipe5bzxs_s20260930
echo "ADD48 local start $(date)" >> $LOG
$PY -u train_ru5b.py --binary --smooth-consistency 1.0 --train-on-xs --tag-suffix xs --seed 20260930 --workers 12 > train_ru_$T.log 2>&1
until [ -f meta_ru_$T.json ]; do sleep 120; done
echo "ADD48 $T trained $(date)" >> $LOG
SEL=ffpp_auc bash run_add6_eval.sh $T clipe5bzxs 20260930 RU-$T RUCLIPE5BZXS local; unset SEL
$PY -u smooth_probe38.py score $T >> smooth38_score.log 2>&1
$PY -u smooth_evasion.py score $T >> smooth_evasion2.log 2>&1
$PY -u cdf_filtered_eval.py score $T >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $T >> dfd_v3_ours.log 2>&1
(cd ../df40_eval_20261012 && $PY -u df40_eval.py score $T >> score_ext.log 2>&1)
$PY -u bct.py score $T >> bct_score.log 2>&1
echo "ADD48 $T scored $(date)" >> $LOG
