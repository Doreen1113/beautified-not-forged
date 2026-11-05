#!/bin/bash
# CADDM and LAA-Net (recrop) on every source (2026-10-12). Same steps as run_newbase.sh, plus commercial retouching.
# Starts after the fast part of the DF40 chain so the two do not share the GPU and the CPU cores.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
until grep -q "DF40 FAST DONE" ../df40_eval_20261012/done.txt 2>/dev/null; do sleep 300; done
for n in caddm laanetr; do
  (cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 $PY -u score_cdfb.py --models $n > score_${n}_v3.log 2>&1 && $PY -u fair_cdfb.py $n > fair_$n.log 2>&1)
  echo "NEWBASE2 $n cdfb $(date)" >> add6.done
  $PY -u cdf_filtered_eval.py score $n >> newbase2.log 2>&1; $PY -u dfd_v3_eval.py score $n >> newbase2.log 2>&1
  for S in dfdff cdfff; do FSRC=$S $PY -u cdf_filtered_eval.py score $n >> newbase2.log 2>&1; done
  for st in cdf dfd; do (cd ../ffpp_benchmark_20260925 && $PY -u dfb_crop_eval.py score $st $n >> dfb_crop_eval.log 2>&1); done
  echo "NEWBASE2 $n all $(date)" >> add6.done
done
(cd ../alipair_zeroshot_20260929 && $PY -u eval_published_ali.py score >> score_new2.log 2>&1 && $PY -u eval_published_ali.py analyse > analyse_new2.log 2>&1)
for S in "" "FSRC=dfdff" "FSRC=cdfff"; do env $S $PY -u cdf_filtered_eval.py analyse >> analyse_all.log 2>&1; done
$PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1; (cd ../ffpp_benchmark_20260925 && $PY -u dfb_crop_eval.py analyse >> dfb_crop_eval.log 2>&1)
echo "NEWBASE2 DONE $(date)" >> add6.done
