#!/bin/bash
# GenD and DFD-HR on every source (2026-10-11). DFD-HR is slow (~0.13 s per frame).
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
for n in gend dfdhr; do
  (cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 $PY -u score_cdfb.py --models $n > score_${n}_v3.log 2>&1 && $PY -u fair_cdfb.py $n > fair_$n.log 2>&1)
  echo "NEWBASE $n cdfb $(date)" >> add6.done
  $PY -u cdf_filtered_eval.py score $n >> newbase.log 2>&1; $PY -u dfd_v3_eval.py score $n >> newbase.log 2>&1
  for S in dfd dfdff cdfff; do FSRC=$S $PY -u cdf_filtered_eval.py score $n >> newbase.log 2>&1; done
  for st in cdf dfd; do (cd ../ffpp_benchmark_20260925 && $PY -u dfb_crop_eval.py score $st $n >> dfb_crop_eval.log 2>&1); done
  echo "NEWBASE $n all $(date)" >> add6.done
done
for S in "" "FSRC=dfd" "FSRC=dfdff" "FSRC=cdfff"; do env $S $PY -u cdf_filtered_eval.py analyse >> analyse_all.log 2>&1; done
$PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1; (cd ../ffpp_benchmark_20260925 && $PY -u dfb_crop_eval.py analyse >> dfb_crop_eval.log 2>&1)
echo "NEWBASE DONE $(date)" >> add6.done
