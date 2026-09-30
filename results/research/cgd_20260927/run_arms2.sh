#!/bin/bash
cd ~/AIGC_sbifix/results/research/cgd_20260927
for ARM in HYBPE MASK; do
  AIGC_BASE=$HOME/AIGC_sbifix ~/venvs/sbifix/bin/python -u train_cgd.py --arm $ARM --workers 12 > train_${ARM}_s20260928.log 2>&1
done
