#!/bin/bash
# Addendum 67 chain (local). Arm A trains on gsplat-ubuntu (run_add67_ubuntu.sh there: precompute, then clipe5R25_s20260929).
# Here: copy the re-synthesised frames once the precompute is done, train arm B (binary + re-synthesis) on the local GPU,
# then evaluate both arms with the per-arm chain used for every earlier arm (run_add6_eval.sh steps, without the explanation step).
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; R=gsplat-ubuntu; RB=AIGC_sbifix/results/research/retouch_unified_20260929
LOG=add67_chain.log; echo "start $(date)" >> $LOG
until timeout 30 ssh -n $R "grep -q 'RESYNTH DONE' $RB/add67_ubuntu.log"; do sleep 300; done
echo "resynth done on ubuntu $(date)" >> $LOG
mkdir -p /c/My_Project/AIGC/resynth_flux
ssh -n $R "cd AIGC_sbifix && tar cf - resynth_flux" | tar xf - -C /c/My_Project/AIGC
echo "copied $(find /c/My_Project/AIGC/resynth_flux -name '*.png' | wc -l) frames $(date)" >> $LOG
$PY -u train_ru5.py --binary --resynth 0.25 --seed 20260929 --workers 8 > train_ru_clipe5bR25_s20260929.log 2>&1
echo "arm B trained $(date)" >> $LOG

evalarm () {   # $1 tag, $2 arm, $3 remote|local, $4 selection criterion (empty = c2)
  T=$1; ARM=$2; CK=/c/My_Project/AIGC/checkpoints/research/retouch_unified_20260929
  if [ "$3" = "remote" ]; then
    for e in 01 02 03 04 05 06 07 08; do scp -q $R:AIGC_sbifix/checkpoints/research/retouch_unified_20260929/ru_${T}_e$e.pth $CK/; done
    for f in meta_ru_$T.json train_ru_$T.csv train_ru_$T.log; do scp -q $R:$RB/$f . ; done
  fi
  $PY -u select_epoch.py --tag $T ${4:+--criterion $4} > select_$T.log 2>&1
  $PY -u leak_probe.py $T > leak_probe_$T.log 2>&1
  $PY -u eval_ru.py --arm $ARM --seed 20260929 > eval_$T.log 2>&1
  (cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 $PY -u score_cdfb.py --models RU-$T > score_RU-${T}_v3.log 2>&1 && $PY -u fair_cdfb.py RU-$T > fair_RU-$T.log 2>&1)
  $PY -u eval_vendor_val.py --arm $ARM --seed 20260929 > vendor_val_$T.log 2>&1
  $PY -u compare_sota.py $T > compare_sota_$T.log 2>&1
  $PY -u smooth_evasion.py score $T >> smooth_evasion67.log 2>&1
  (cd ../df40_eval_20261012 && $PY -u df40_eval.py score $T >> score_ext.log 2>&1 && $PY -u diag3way.py $T >> diag3way67.log 2>&1)
  echo "$T evaluated $(date)" >> $LOG
}
evalarm clipe5bR25_s20260929 clipe5bR25 local ffpp_auc
until timeout 30 ssh -n $R "grep -q 'ADD67 A TRAIN DONE' $RB/add67_ubuntu.log"; do sleep 300; done
evalarm clipe5R25_s20260929 clipe5R25 remote
(cd ../df40_eval_20261012 && $PY -u df40_eval.py analyse > analyse_67.log 2>&1)
$PY -u readout67.py > readout67.log 2>&1
echo "ADD67 DONE $(date)" >> $LOG
