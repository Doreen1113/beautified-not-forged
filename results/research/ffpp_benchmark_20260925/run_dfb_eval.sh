#!/bin/bash
# Addendum 24: when the DeepfakeBench crops are built, score the ten baselines and our models on them, then analyse.
cd /c/My_Project/AIGC/results/research/ffpp_benchmark_20260925; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
until grep -q "DFB CROPS DONE" ../retouch_unified_20260929/add6.done; do sleep 120; done
for st in cdf dfd; do
  for n in effort fadapter clipe5b_s20260929 clipe5awpb_s20260930 clipe5f_s20260929 clipe5_s20260929 xception effnb4 f3net spsl ucf recce core srm clipe5feb_s20260929 clipe5fb_s20260929; do
    if [ -f /c/My_Project/AIGC/checkpoints/research/retouch_unified_20260929/ru_$n.pth ] || [ "${n#clipe}" = "$n" ]; then $PY -u dfb_crop_eval.py score $st $n >> dfb_crop_eval.log 2>&1; fi
  done
done
$PY -u dfb_crop_eval.py analyse >> dfb_crop_eval.log 2>&1
echo "DFB EVAL DONE $(date)" >> ../retouch_unified_20260929/add6.done
