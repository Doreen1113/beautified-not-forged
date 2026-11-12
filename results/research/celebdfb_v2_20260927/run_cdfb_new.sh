#!/bin/bash
cd /c/My_Project/AIGC/results/research/celebdfb_v2_20260927; export PYTHONIOENCODING=utf-8; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
for T in clipe5fbg0o_s20260929 clipe5fbg0o_s20260930 clipe5fbn_s20260929 clipe5fbn_s20260930 clipe5fbg0p1o_s20260929 clipe5fbp1n_s20260929; do
  N=RU-$T; CDFB_TAG=v3 $PY -u score_cdfb.py --models $N > score_${N}_v3.log 2>&1 && $PY -u fair_cdfb.py $N > fair_$N.log 2>&1
done
echo "CDFB NEW DONE $(date)" >> ../retouch_unified_20260929/add6.done
