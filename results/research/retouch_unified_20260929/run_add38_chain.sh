#!/bin/bash
# Addenda 38 / 39: score the 17 published detectors (one process each) and our arms on the materialised smoothed crops.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
until [ -f smooth38_list.json ]; do sleep 60; done
for n in effort fadapter gend dfdhr xception effnb4 f3net spsl ucf recce core srm sbi univfd npr caddm laanetr; do
  $PY -u smooth_probe38.py score $n >> smooth38_score.log 2>&1
done
echo "ADD38 published DONE $(date)" >> add6.done
for t in clipe5fbp0_s20260929 clipe5fbp0_s20260930 clipe5fbp0_s20261001 clipe5fb_s20260929 clipe5fb_s20260930 clipe5fbg0p1o_s20260929 clipe5fbg0oy_s20260929 clipe5fbg0oy_s20260930 clipe5_s20260929 clipe5y_s20260929 clipe5b_s20260929; do
  $PY -u smooth_probe38.py score $t >> smooth38_score.log 2>&1
done
$PY -u smooth_probe38.py analyse > smooth38_analyse.log 2>&1
echo "ADD38 DONE $(date)" >> add6.done
