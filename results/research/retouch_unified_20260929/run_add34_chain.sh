#!/bin/bash
# Addendum 34: evaluate the class-symmetric smoothing arm (two seeds) on every source, plus the extended evasion test.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
# reference arms for the extended evasion test (independent of the new training)
$PY -u smooth_evasion.py score clipe5fbp0_s20260929 clipe5fbp0_s20260930 clipe5fb_s20260929 clipe5fb_s20260930 clipe5fbg0o_s20260929 clipe5fbg0o_s20260930 clipe5fbg0p1o_s20260929 clipe5fbp1_s20260929 clipe5_s20260929 clipe5b_s20260929 >> smooth_evasion2.log 2>&1
echo "ADD34 refs DONE $(date)" >> add6.done
one() {
  T=$1; ARM=${T%_s*}
  until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_$T.json"; do sleep 300; done
  export SEL=ffpp_auc
  bash run_add6_eval.sh $T $ARM ${T#*_s} RU-$T RUCLIPE${ARM#clipe} remote
  $PY -u smooth_evasion.py score $T >> smooth_evasion2.log 2>&1
  $PY -u cdf_filtered_eval.py score $T >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $T >> dfd_v3_ours.log 2>&1
  (cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 $PY -u score_cdfb.py --models RU-$T > score_RU-${T}_v3.log 2>&1 && $PY -u fair_cdfb.py RU-$T > fair_RU-$T.log 2>&1)
  echo "ADD34 $T core DONE $(date)" >> add6.done
  FSRC=dfdff $PY -u cdf_filtered_eval.py score $T >> dfd_filteredff_score.log 2>&1; FSRC=cdfff $PY -u cdf_filtered_eval.py score $T >> cdf_filteredff_score.log 2>&1
  (cd ../df40_eval_20261012 && $PY -u df40_eval.py score $T >> score_ext.log 2>&1)
  echo "ADD34 $T DONE $(date)" >> add6.done
}
one clipe5fbg0oy_s20260929; one clipe5fbg0oy_s20260930
$PY smooth_evasion.py analyse > smooth_evasion2_table.txt 2>&1
echo "ADD34 DONE $(date)" >> add6.done
