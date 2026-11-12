#!/bin/bash
# Addendum 42: evaluate the second seeds of the symmetric-view variant (Addendum 36 chain) and the binary control
# (Addendum 9 chain + the same extra sources). Training runs on gsplat-ubuntu (run_add42_queue.sh there).
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; RV=../review_v4_exps_20261016
$PY -u smooth_evasion.py score clipe5_s20260930 >> smooth_evasion2.log 2>&1      # main model seed 2, for within-seed comparisons
for T in clipe5y_s20260930 clipe5b_s20260930; do
  until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_$T.json"; do sleep 300; done
  if [ $T = clipe5y_s20260930 ]; then unset SEL; bash run_add6_eval.sh $T clipe5y 20260930 RU-$T RUCLIPE5y remote
  else SEL=ffpp_auc bash run_add6_eval.sh $T clipe5b 20260930 RU-$T RUCLIPE5B remote; unset SEL; fi
  $PY -u smooth_evasion.py score $T >> smooth_evasion2.log 2>&1
  $PY -u cdf_filtered_eval.py score $T >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $T >> dfd_v3_ours.log 2>&1
  FSRC=dfdff $PY -u cdf_filtered_eval.py score $T >> dfd_filteredff_score.log 2>&1; FSRC=cdfff $PY -u cdf_filtered_eval.py score $T >> cdf_filteredff_score.log 2>&1
  FSRC=dfd $PY -u cdf_filtered_eval.py score $T >> dfd_filtered_score.log 2>&1
  (cd ../df40_eval_20261012 && $PY -u df40_eval.py score $T >> score_ext.log 2>&1)
  (cd $RV && for S in fb fbj blfw; do $PY -u ar_source.py score $S $T >> run_ar.log 2>&1; done; $PY -u ffpp_val_thr.py score $T >> run_ffval.log 2>&1)
  echo "ADD42 $T scored $(date)" >> add6.done
done
(cd ../celebdfb_v2_20260927 && $PY -u fair_cdfb.py RU-clipe5y_s20260930 RU-clipe5b_s20260930 RU-clipe5-s2 > fair_add42.log 2>&1)
(cd ../df40_eval_20261012 && $PY -u df40_eval.py analyse > analyse_ext.log 2>&1)
for S in "" "FSRC=dfdff" "FSRC=cdfff" "FSRC=dfd"; do env $S $PY -u cdf_filtered_eval.py analyse >> analyse_all.log 2>&1; done
$PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1
$PY smooth_evasion.py analyse > smooth_evasion2_table.txt 2>&1
(cd $RV && $PY -u ar_source.py analyse > ar_analyse.log 2>&1; $PY -u ffpp_val_thr.py analyse > ffval_analyse.log 2>&1; $PY -u identity_boot.py > identity_boot.log 2>&1; [ -f readout42.py ] && $PY -u readout42.py > readout42.log 2>&1)
echo "ADD42 DONE $(date)" >> add6.done
