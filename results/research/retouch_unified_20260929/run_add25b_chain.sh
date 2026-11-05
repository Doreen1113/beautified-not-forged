#!/bin/bash
# Addendum 25 second seeds: evaluate P0 / P2 / P1 (seed 20260930) as each finishes on Ubuntu; score on every source incl. official crops; pair.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
one() {
  T=$1; ARM=${T%_s*}
  until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_$T.json"; do sleep 300; done
  export SEL=ffpp_auc
  bash run_add6_eval.sh $T $ARM ${T#*_s} RU-$T RUCLIPE${ARM#clipe} remote
  $PY -u cdf_filtered_eval.py score $T >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $T >> dfd_v3_ours.log 2>&1
  FSRC=dfd $PY -u cdf_filtered_eval.py score $T >> dfd_filtered_score.log 2>&1; FSRC=dfdff $PY -u cdf_filtered_eval.py score $T >> dfd_filteredff_score.log 2>&1; FSRC=cdfff $PY -u cdf_filtered_eval.py score $T >> cdf_filteredff_score.log 2>&1
  for st in cdf dfd; do (cd ../ffpp_benchmark_20260925 && $PY -u dfb_crop_eval.py score $st $T >> dfb_crop_eval.log 2>&1); done
  echo "ADD25B $T DONE $(date)" >> add6.done
}
one clipe5fbp0_s20260930; one clipe5fb_s20260930; one clipe5fbp1_s20260930
for S in "" "FSRC=dfd" "FSRC=dfdff" "FSRC=cdfff"; do env $S $PY -u cdf_filtered_eval.py analyse >> analyse_all.log 2>&1; done
$PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1; (cd ../ffpp_benchmark_20260925 && $PY -u dfb_crop_eval.py analyse >> dfb_crop_eval.log 2>&1)
(cd ../celebdfb_v2_20260927 && $PY pair_cdfb.py RU-clipe5fb_s20260930 RU-clipe5fbp0_s20260930 RU-clipe5fbp1_s20260930 RU-clipe5fbp0_s20260930 RU-clipe5fb_s20260930 RU-clipe5fbp1_s20260930 >> pair_cdfb.log 2>&1)
echo "ADD25B DONE $(date)" >> add6.done
