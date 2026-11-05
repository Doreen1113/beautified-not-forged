#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
/c/Users/2603055/AppData/Local/miniconda3/python.exe -u train_ru5.py --softmax --seed 20260929 --workers 12 > train_ru_clipe5x_s20260929.log 2>&1
echo "clipe5x trained $(date)" >> add6.done