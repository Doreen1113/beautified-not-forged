#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
until grep -q "QUEUE2 DONE" add6.done; do sleep 120; done
/c/Users/2603055/AppData/Local/miniconda3/python.exe -u train_ru5.py --ffpp-only --seed 20260929 --workers 12 > train_ru_clipe5f_s20260929.log 2>&1
echo "clipe5f trained $(date)" >> add6.done