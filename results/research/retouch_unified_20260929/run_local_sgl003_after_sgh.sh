#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929
until [ -f meta_ru_clipe5bzsgh_s20260929.json ]; do sleep 300; done
PYTHONIOENCODING=utf-8 /c/Users/2603055/AppData/Local/miniconda3/python.exe -u train_ru5.py --binary --smooth-consistency 0.03 --cons-stopgrad --tag-suffix sgl003 --seed 20260929 --workers 8 > train_ru_clipe5bzsgl003_s20260929.log 2>&1
echo "local train clipe5bzsgl003_s20260929 ended $(date) (am. 9)" >> add46_chain.log
