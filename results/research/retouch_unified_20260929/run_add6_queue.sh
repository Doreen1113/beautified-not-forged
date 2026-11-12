#!/bin/bash
# Addendum 6 queue on the local GPU: evaluate the softmax ablation, then train + evaluate the two remaining ablations.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
until grep -q "clipe5_s20260929 evaluated" add6.done; do sleep 120; done
bash run_add6_eval.sh clipe5x_s20260929 clipe5x 20260929 RU-clipe5x RUCLIPE5X local
$PY -u train_ru5.py --no-grade --seed 20260929 --workers 12 > train_ru_clipe5g0_s20260929.log 2>&1
echo "clipe5g0 trained $(date)" >> add6.done
$PY -u train_ru5.py --no-vendor-fake --seed 20260929 --workers 12 > train_ru_clipe5v0_s20260929.log 2>&1
echo "clipe5v0 trained $(date)" >> add6.done