#!/bin/bash
# Evaluate an RU7 run fetched from the Ubuntu box: standard chain, then the AR-filter tests. $1 = seed.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; S=$1; T=clipe7_s$S; N=RU-clipe7; [ "$S" = "20260930" ] && N=RU-clipe7-s2
until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_$T.json"; do sleep 300; done
bash run_add6_eval.sh $T clipe7 $S $N RUCLIPE7 remote
$PY -u eval_fairbeauty_pairs.py $T > eval_fairbeauty_$T.log 2>&1
$PY -u eval_insta.py $T > eval_insta_$T.log 2>&1
echo "$T AR-evaluated $(date)" >> add6.done
