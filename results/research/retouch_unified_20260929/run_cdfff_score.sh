#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8 FSRC=cdfff; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
for n in effort fadapter sbi clipe5f_s20260929 clipe5fg0_s20260929 clipe5b_s20260929 clipe5_s20260929 clipe5_s20260930 clipe4r_s20260929 xception effnb4 f3net spsl ucf recce core srm univfd npr clipe5af_s20260929 clipe5rf_s20260929 clipe5awpf_s20260929 clipe5fb_s20260929 clipe5feb_s20260929 clipe5fbp0_s20260929; do $PY -u cdf_filtered_eval.py score $n >> cdf_filteredff_score.log 2>&1; done
$PY -u cdf_filtered_eval.py analyse >> cdf_filteredff_score.log 2>&1; echo "CDF_FILTEREDFF BASE DONE $(date)" >> add6.done
