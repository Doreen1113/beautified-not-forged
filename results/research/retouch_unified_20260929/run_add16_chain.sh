#!/bin/bash
# Addendum 16: after the Addendum 15 chain, score the worst-case and random runs on the fresh DFD source and probe them;
# then evaluate the worst-of-4 control (trained on Ubuntu after the random run).
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
until grep -q "ADD15 DONE" add6.done; do sleep 300; done
for t in clipe5af_s20260929 clipe5rf_s20260929; do FSRC=dfd $PY -u cdf_filtered_eval.py score $t >> dfd_filtered_score.log 2>&1; done
FSRC=dfd $PY -u cdf_filtered_eval.py analyse >> dfd_filtered_score.log 2>&1
$PY -u adv_probe.py clipe5af_s20260929 clipe5rf_s20260929 >> adv_probe.log 2>&1
echo "ADD16A DONE $(date)" >> add6.done
until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_clipe5kf_s20260929.json"; do sleep 300; done
SEL=ffpp_f1 bash run_add6_eval.sh clipe5kf_s20260929 clipe5kf 20260929 RU-clipe5kf_s20260929 RUCLIPE5kf remote
$PY -u cdf_filtered_eval.py score clipe5kf_s20260929 >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score clipe5kf_s20260929 >> dfd_v3_ours.log 2>&1
FSRC=dfd $PY -u cdf_filtered_eval.py score clipe5kf_s20260929 >> dfd_filtered_score.log 2>&1
$PY -u cdf_filtered_eval.py analyse >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1; FSRC=dfd $PY -u cdf_filtered_eval.py analyse >> dfd_filtered_score.log 2>&1
$PY -u adv_probe.py clipe5kf_s20260929 >> adv_probe.log 2>&1
echo "ADD16 DONE $(date)" >> add6.done
