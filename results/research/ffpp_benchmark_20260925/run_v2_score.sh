#!/bin/bash
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; export PYTHONIOENCODING=utf-8
cd /c/My_Project/AIGC/results/research/ffpp_benchmark_20260925
until grep -q "BUILD V2 DONE" run_v2.log 2>/dev/null; do sleep 120; done
SP=/c/My_Project/AIGC/splits/research/ffpp_benchmark_20260925
echo "=== $(date +%H:%M) ours on v2 ==="
$PY -u score_ours_standard.py --sets cdf2,dfd2 > ours_v2.log 2>&1; grep -a "^\[" ours_v2.log
M=xception,effnb4,f3net,spsl,sbi,ucf,recce,core,srm
echo "=== $(date +%H:%M) competitors CDF v2 ==="
$PY -u rescore_cdf_standard.py --models $M --std $SP/celebdf_std32v2.txt --tag _v2 > comp_cdf_v2.log 2>&1; grep -a "^\[" comp_cdf_v2.log
echo "=== $(date +%H:%M) competitors DFD v2 ==="
$PY -u rescore_cdf_standard.py --models $M --std $SP/dfd_std32v2.txt --tag _dfdv2 > comp_dfd_v2.log 2>&1; grep -a "^\[" comp_dfd_v2.log
echo "V2 SCORE DONE"
