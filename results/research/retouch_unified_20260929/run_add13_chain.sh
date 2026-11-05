#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
until [ -f meta_ru_clipe5f_s20260930.json ]; do sleep 120; done
SEL=ffpp_f1 bash run_add6_eval.sh clipe5f_s20260930 clipe5f 20260930 RU-clipe5f-s2 RUCLIPE5F local
until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_clipe5fg0_s20260929.json"; do sleep 300; done
SEL=ffpp_f1 bash run_add6_eval.sh clipe5fg0_s20260929 clipe5fg0 20260929 RU-clipe5fg0 RUCLIPE5FG0 remote
echo "ADD13 DONE $(date)" >> add6.done