#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
until [ -f meta_ru_clipe5bzsgh_s20260930.json ]; do sleep 300; done
echo "local train clipe5bzsgG_s20260930 started $(date) md5 $(md5sum train_ru5.py | cut -c1-32)" >> add46_chain.log
/c/Users/2603055/AppData/Local/miniconda3/python.exe -u train_ru5.py --binary --smooth-consistency 1.0 --cons-stopgrad --cons-op gauss --tag-suffix sgG --seed 20260930 --workers 8 > train_ru_clipe5bzsgG_s20260930.log 2>&1
echo "local train clipe5bzsgG_s20260930 ended exit $? $(date)" >> add46_chain.log
