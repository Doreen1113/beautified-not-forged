#!/bin/sh
# Addendum 70 evaluation chain (local GPU). Waits for the Ubuntu training (run_add70_ubuntu.sh writes "ADD70 TRAIN DONE"),
# fetches the 12 epochs, selects on validation (C2), then runs the gate scripts and readout70.py. Log: add70_chain.log.
cd "$(dirname "$0")"
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; R=gsplat-ubuntu
RB=AIGC_sbifix/results/research/retouch_unified_20260929; RC=AIGC_sbifix/checkpoints/research/retouch_unified_20260929
CK=/c/My_Project/AIGC/checkpoints/research/retouch_unified_20260929; T=ru7we_effb4_s20260929; LOG=add70_chain.log
echo "start $(date)" >> $LOG
until timeout 60 ssh -n $R "grep -q 'ADD70 TRAIN DONE' $RB/add70_ubuntu.log"; do sleep 300; done
echo "train done on ubuntu $(date)" >> $LOG
for e in 01 02 03 04 05 06 07 08 09 10 11 12; do scp -q $R:$RC/ru_${T}_e$e.pth $CK/ || echo "missing e$e" >> $LOG; done
for f in meta_ru_$T.json train_ru_$T.csv train_ru_$T.log; do scp -q $R:$RB/$f . ; done
echo "fetched $(ls $CK | grep -c "ru_${T}_e") epochs $(date)" >> $LOG
$PY -u select_epoch_ru.py --tag $T --epochs 12 > select_$T.log 2>&1
echo "selected $(grep SELECTED select_$T.log | cut -c1-120) $(date)" >> $LOG
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
