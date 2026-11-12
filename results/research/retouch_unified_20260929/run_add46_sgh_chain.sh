#!/bin/bash
# Addendum 46 (+ amendment 1): local evaluation chain for the SIC arms. Training runs on gsplat-ubuntu (run_add46_queue2.sh),
# order clipe5z s1 -> clipe5bz s1 -> clipe5z s2 -> clipe5bz s2; each arm is evaluated as soon as its meta file exists.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; RV=../review_v4_exps_20261016; LOG=add46_sgh_chain.log
echo "ADD46 chain start $(date)" >> $LOG
# within-seed references not yet scored on the Addendum 38 face-local forms
until [ -f smooth38_list.json ]; do sleep 60; done
for T in clipe5bzsgh_s20260929; do
  until [ -f meta_ru_$T.json ]; do sleep 300; done
  A=${T%%_s*}; S=${T##*_s}; CG=RUCLIPE${A#clipe}; CG=${CG^^}
  echo "ADD46 $T trained, evaluating $(date)" >> $LOG
  if [ $A = clipe5z ]; then unset SEL; bash run_add6_eval.sh $T $A $S RU-$T $CG local        # main-model rule (C2)
  else SEL=ffpp_auc bash run_add6_eval.sh $T $A $S RU-$T $CG local; unset SEL; fi           # binary: FF++ validation AUC
  $PY -u smooth_evasion.py score $T >> smooth_evasion2.log 2>&1
  $PY -u smooth_probe38.py score $T >> smooth38_score.log 2>&1
  $PY -u cdf_filtered_eval.py score $T >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $T >> dfd_v3_ours.log 2>&1
  FSRC=dfdff $PY -u cdf_filtered_eval.py score $T >> dfd_filteredff_score.log 2>&1; FSRC=cdfff $PY -u cdf_filtered_eval.py score $T >> cdf_filteredff_score.log 2>&1
  FSRC=dfd $PY -u cdf_filtered_eval.py score $T >> dfd_filtered_score.log 2>&1
  (cd ../df40_eval_20261012 && $PY -u df40_eval.py score $T >> score_ext.log 2>&1)
  (cd $RV && $PY -u ffpp_val_thr.py score $T >> run_ffval.log 2>&1)      # deployable threshold of the clipe5z decision rule
  $PY -u readout46.py > readout46.log 2>&1
  echo "ADD46 $T scored $(date)" >> $LOG
done
(cd ../df40_eval_20261012 && $PY -u df40_eval.py analyse > analyse_ext.log 2>&1)
for S in "" "FSRC=dfdff" "FSRC=cdfff" "FSRC=dfd"; do env $S $PY -u cdf_filtered_eval.py analyse >> analyse_all.log 2>&1; done
$PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1
$PY smooth_evasion.py analyse > smooth_evasion2_table.txt 2>&1
$PY -u smooth_probe38.py analyse > smooth38_analyse.log 2>&1
(cd ../alipair_zeroshot_20260929 && $PY -u exposure_ali.py > exposure_ali_add46.log 2>&1)
$PY -u readout46.py > readout46.log 2>&1
echo "ADD46 DONE $(date)" >> $LOG; echo "ADD46 DONE $(date)" >> add6.done
