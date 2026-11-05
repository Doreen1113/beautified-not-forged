#!/bin/bash
# Addendum 28 on the local GPU: M2 then M0; each evaluated as soon as it finishes (selection ffpp_f1, all sources, official crops).
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
ev() {
  T=$1; ARM=${T%_s*}; export SEL=ffpp_f1
  bash run_add6_eval.sh $T $ARM ${T#*_s} RU-$T RUCLIPE${ARM#clipe} local
  $PY -u cdf_filtered_eval.py score $T >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $T >> dfd_v3_ours.log 2>&1
  for S in dfd dfdff cdfff; do FSRC=$S $PY -u cdf_filtered_eval.py score $T >> ${S}_score_extra.log 2>&1; done
  for st in cdf dfd; do (cd ../ffpp_benchmark_20260925 && $PY -u dfb_crop_eval.py score $st $T >> dfb_crop_eval.log 2>&1); done
  $PY -u evidence_probe.py $T >> evidence_probe.log 2>&1
  echo "ADD28 $T DONE $(date)" >> add6.done
}
$PY -u train_ru5.py --ffpp-only --mil 0.05 --seed 20260929 --workers 12 > train_ru_clipe5mf_s20260929.log 2>&1
$PY -u train_ru5.py --ffpp-only --mil 0.05 --beauty none --seed 20260929 --workers 12 > train_ru_clipe5mfp0_s20260929.log 2>&1 &
TR=$!; ev clipe5mf_s20260929; wait $TR; ev clipe5mfp0_s20260929
for S in "" "FSRC=dfd" "FSRC=dfdff" "FSRC=cdfff"; do env $S $PY -u cdf_filtered_eval.py analyse >> analyse_all.log 2>&1; done
$PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1; (cd ../ffpp_benchmark_20260925 && $PY -u dfb_crop_eval.py analyse >> dfb_crop_eval.log 2>&1)
(cd ../celebdfb_v2_20260927 && $PY pair_cdfb.py RU-clipe5mf_s20260929 RU-clipe5f RU-clipe5mf_s20260929 RU-clipe5mfp0_s20260929 >> pair_cdfb.log 2>&1)
echo "ADD28 DONE $(date)" >> add6.done
