#!/bin/bash
# After the binary control finishes on the Ubuntu box: evaluate it here; then wait for RU7 and evaluate it.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_clipe5b_s20260929.json"; do sleep 300; done
until grep -q "QUEUE2 DONE" add6.done; do sleep 120; done
SEL=ffpp_auc bash run_add6_eval.sh clipe5b_s20260929 clipe5b 20260929 RU-clipe5b RUCLIPE5B remote
bash run_add8_eval.sh 20260929