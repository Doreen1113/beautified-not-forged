#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
LF=/c/My_Project/AIGC/splits/research/ffpp_benchmark_20260925/wdf_subset_test.txt
for n in effort fadapter sbi xception effnb4 f3net spsl ucf recce core srm univfd npr clipe5f_s20260929 clipe5b_s20260929 clipe5_s20260929 clipe5fb_s20260929 clipe5fbp0_s20260929 clipe5fbp1_s20260929 clipe5fb_s20260930 clipe5fbp0_s20260930 clipe5fbE_s20260929 clipe5fbp0E_s20260929; do $PY -u extra_set_eval.py score wdf $LF $n >> extra_wdf.log 2>&1; done
$PY -u extra_set_eval.py analyse wdf $LF >> extra_wdf.log 2>&1; echo "WDF DONE $(date)" >> add6.done
