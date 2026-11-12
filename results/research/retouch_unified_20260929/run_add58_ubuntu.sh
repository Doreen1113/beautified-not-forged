#!/bin/bash
cd ~/AIGC_sbifix/results/research/retouch_unified_20260929; source ~/venvs/sbifix/bin/activate; export AIGC_BASE=$HOME/AIGC_sbifix PYTHONIOENCODING=utf-8
L=add58_ubuntu.log; echo "start $(date); train_ru7w.py md5 $(md5sum train_ru7w.py | cut -c1-32)" > $L
python -u train_ru7w.py --ar --ar-p 0 --tag-suffix Wsmoke --seed 20260929 --workers 14 --max-steps 220 > smoke_clipe7W.log 2>&1 || { echo "SMOKE FAILED $(date)" >> $L; exit 1; }
grep -q "bases" smoke_clipe7W.log && echo "smoke ok $(grep -m1 bases smoke_clipe7W.log) $(date)" >> $L
for S in 20260929 20260930; do
  python -u train_ru7w.py --ar --ar-p 0 --tag-suffix W --seed $S --workers 14 > train_ru_clipe7W_s$S.log 2>&1
  echo "end clipe7W_s$S exit $? $(date)" >> $L
done
