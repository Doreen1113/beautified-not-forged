#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
ev() {
  T=$1; ARM=${T%_s*}; export SEL=ffpp_f1
  bash run_add6_eval.sh $T $ARM ${T#*_s} RU-$T RUCLIPE${ARM#clipe} local
  $PY -u cdf_filtered_eval.py score $T >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $T >> dfd_v3_ours.log 2>&1
  for S in dfd dfdff cdfff; do FSRC=$S $PY -u cdf_filtered_eval.py score $T >> ${S}_score_extra.log 2>&1; done
  for st in cdf dfd; do (cd ../ffpp_benchmark_20260925 && $PY -u dfb_crop_eval.py score $st $T >> dfb_crop_eval.log 2>&1); done
  $PY -u evidence_probe.py $T >> evidence_probe.log 2>&1
  echo "ADD28R $T DONE $(date)" >> add6.done
}
ev clipe5mf_s20260929; ev clipe5mfp0_s20260929
for S in "" "FSRC=dfd" "FSRC=dfdff" "FSRC=cdfff"; do env $S $PY -u cdf_filtered_eval.py analyse >> analyse_all.log 2>&1; done
$PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1; (cd ../ffpp_benchmark_20260925 && $PY -u dfb_crop_eval.py analyse >> dfb_crop_eval.log 2>&1)
(cd ../celebdfb_v2_20260927 && $PY pair_cdfb.py RU-clipe5mf_s20260929 RU-clipe5f RU-clipe5mf_s20260929 RU-clipe5mfp0_s20260929 RU-clipe5mf_s20260929 RU-clipe5fb_s20260929 >> pair_cdfb.log 2>&1)
echo "ADD28R DONE $(date)" >> add6.done
