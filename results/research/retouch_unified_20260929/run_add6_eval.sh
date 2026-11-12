#!/bin/bash
# Addendum 6: evaluate a finished RU5 run. $1 = tag (clipe5_s20260929 ...), $2 = arm for eval_ru (clipe5 | clipe5x), $3 = seed,
# $4 = Celeb-DF-B registry name, $5 = part-edit harness arm, $6 = "remote" to fetch the epochs from the Ubuntu box first.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; T=$1; ARM=$2; S=$3; N=$4; CG=$5
R=gsplat-ubuntu; RB=AIGC_sbifix/results/research/retouch_unified_20260929; RC=AIGC_sbifix/checkpoints/research/retouch_unified_20260929
CK=/c/My_Project/AIGC/checkpoints/research/retouch_unified_20260929
if [ "$6" = "remote" ]; then
  for e in 01 02 03 04 05 06 07 08; do scp -q $R:$RC/ru_${T}_e$e.pth $CK/; done
  for f in meta_ru_$T.json train_ru_$T.csv train_ru_$T.log; do scp -q $R:$RB/$f . ; done
fi
$PY -u select_epoch.py --tag $T ${SEL:+--criterion $SEL} > select_$T.log 2>&1   # SEL: c2 (default) | ffpp_f1 | ffpp_auc
$PY -u leak_probe.py $T > leak_probe_$T.log 2>&1
echo "$T selected+validated $(date)" >> add6.done
$PY -u eval_ru.py --arm $ARM --seed $S > eval_$T.log 2>&1
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 $PY -u score_cdfb.py --models $N > score_${N}_v3.log 2>&1 && $PY -u fair_cdfb.py $N > fair_$N.log 2>&1)
$PY -u eval_vendor_val.py --arm $ARM --seed $S > vendor_val_$T.log 2>&1
$PY -u compare_sota.py $T > compare_sota_$T.log 2>&1
(cd ../cgd_20260927 && $PY -u eval_cgd_explain.py --arm $CG --seed $S --mech donor,sd,sdxl > explain_${CG}_s$S.log 2>&1)
echo "$T evaluated $(date)" >> add6.done
