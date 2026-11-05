#!/bin/bash
cd /c/My_Project/AIGC/results/research/alipair_zeroshot_20260929; export PYTHONIOENCODING=utf-8; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
$PY -u eval_published_ali.py score > score_new.log 2>&1; $PY -u eval_published_ali.py analyse > analyse_new.log 2>&1; echo "ALI NEW DONE $(date)" >> ../retouch_unified_20260929/add6.done
