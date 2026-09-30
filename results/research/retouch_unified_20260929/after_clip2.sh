#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
until [ -f meta_ru_clipe_s20260930.json ]; do sleep 600; done
python -u eval_ru.py --arm clipe --seed 20260930 > eval_clipe_s2.log 2>&1
python -u compare_sbi.py effb4_s20260929 clipe_s20260929 clipe_s20260930 > compare_sbi_clipe2.log 2>&1
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 python -u score_cdfb.py --models RU-clipe-s2 > score_clipe_s2.log 2>&1 && CDFB_TAG=v3 python -u analyze_cdfb.py > analyze_clipe_s2.log 2>&1)
echo "clipe s2 evaluated $(date)" >> after_ru.done
