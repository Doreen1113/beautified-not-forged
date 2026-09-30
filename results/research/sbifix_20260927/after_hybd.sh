#!/bin/bash
cd /c/My_Project/AIGC/results/research/sbifix_20260927
ARMS=HYBD bash after_ubuntu.sh > after_hybd_pull.log 2>&1
PYTHONIOENCODING=utf-8 python -u blur_probe.py > blur_probe_hybd.log 2>&1
echo "HYBD done $(date)" >> after_hybd.done
