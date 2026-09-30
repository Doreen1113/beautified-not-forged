#!/bin/bash
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; export PYTHONIOENCODING=utf-8
cd /c/My_Project/AIGC/results/research/ffpp_benchmark_20260925
echo "=== $(date +%H:%M) CDF v2 ==="; $PY -u build_cdf_standard_v2.py --frames 32 --workers 4 > build_cdf_v2.log 2>&1; tail -3 build_cdf_v2.log
echo "=== $(date +%H:%M) DFD v2 ==="; $PY -u build_dfd_standard_v2.py --frames 32 --workers 4 > build_dfd_v2.log 2>&1; tail -3 build_dfd_v2.log
echo "BUILD V2 DONE"
