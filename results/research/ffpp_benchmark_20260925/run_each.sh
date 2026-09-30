#!/bin/bash
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; export PYTHONIOENCODING=utf-8
cd /c/My_Project/AIGC/results/research/ffpp_benchmark_20260925
for M in xception effnb4 spsl f3net ucf recce core srm sbi npr univfd ours3_mnv4_10ep; do
  if [ -f "scores_${M}.npz" ]; then echo "=== skip $M (done) ==="; continue; fi
  echo "=== $(date +%H:%M:%S) $M ==="
  $PY -u run_benchmark.py --models $M --escape-n 400 > log_${M}.txt 2>&1
  rc=$?
  if [ $rc -ne 0 ]; then echo "  rc=$rc  (see log_${M}.txt)"; fi
  grep -a "^\[${M}\]" log_${M}.txt 2>/dev/null | grep -vi warn
done
echo "=== ALL MODELS ATTEMPTED ==="
