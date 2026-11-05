#!/bin/sh
# Addendum 70 evaluation chain, part 2 (2026-10-30). Epoch selection moved to gsplat-ubuntu after the local run managed
# 2 of 12 epochs in 6.5 h (CPU contention). Waits for select_<tag>.json there, fetches it, copies the selected epoch
# (all 12 are local) to ru_<tag>.pth, then runs the gate scripts locally and readout70.py. Log: add70_chain.log.
cd "$(dirname "$0")"
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; R=gsplat-ubuntu; RB=AIGC_sbifix/results/research/retouch_unified_20260929
CK=/c/My_Project/AIGC/checkpoints/research/retouch_unified_20260929; T=ru7we_effb4_s20260929; LOG=add70_chain.log
echo "part 2 start $(date)" >> $LOG
until timeout 60 ssh -n $R "grep -q SELECTED $RB/select_$T.log"; do sleep 120; done
scp -q $R:$RB/select_$T.json . && scp -q $R:$RB/select_$T.log select_${T}_ubuntu.log
E=$($PY -c "import json; print('%02d' % json.load(open('select_$T.json'))['selected_epoch'])")
cp $CK/ru_${T}_e$E.pth $CK/ru_$T.pth
echo "selected e$E on ubuntu $(date)" >> $LOG
$PY -u eval_ru.py --arm ru7we --arch effb4 --seed 20260929 > eval_$T.log 2>&1
echo "eval_ru done $(date)" >> $LOG
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 $PY -u score_cdfb.py --models RU7We-effb4 > score_RU7We-effb4_v3.log 2>&1 && $PY -u fair_cdfb.py RU7We-effb4 > fair_RU7We-effb4.log 2>&1)
echo "celebdfb done $(date)" >> $LOG
$PY -u eval_fairbeauty_pairs.py $T > fairbeauty_$T.log 2>&1
echo "fairface done $(date)" >> $LOG
(cd ../cgd_20260927 && $PY -u eval_cgd_explain.py --arm RU7WE --seed 20260929 --mech donor,sd,sdxl > explain_RU7WE_s20260929.log 2>&1)
echo "restoration done $(date)" >> $LOG
$PY -u eval_vendor_val.py --arm ru7we --arch effb4 --seed 20260929 > vendor_val_$T.log 2>&1
echo "vendor val done $(date)" >> $LOG
$PY -u readout70.py > readout70.log 2>&1
echo "ADD70 DONE $(grep VERDICT readout70.log) $(date)" >> $LOG
