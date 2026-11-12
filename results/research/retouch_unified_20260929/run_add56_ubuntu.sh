#!/bin/bash
# Addendum 56 EM arm on gsplat-ubuntu (bf16): train_ru9.py is the local train_ru6.py of Addendum 56 (md5 ef5f7c40...),
# renamed because train_ru6.py on this box is the RU6 script of Addendum 7.
cd ~/AIGC_sbifix/results/research/retouch_unified_20260929; source ~/venvs/sbifix/bin/activate; export AIGC_BASE=$HOME/AIGC_sbifix PYTHONIOENCODING=utf-8
L=add56_ubuntu.log; T=clipe5fbEM_s20260929
echo "start $(date); train_ru9.py md5 $(md5sum train_ru9.py | cut -c1-32)" > $L
python -u train_ru9.py --ffpp-only --binary --tune effort --multi-op 0.5 --tag-suffix Msmoke --seed 20260929 --workers 14 --max-steps 220 > smoke_$T.log 2>&1 || { echo "SMOKE FAILED $(date)" >> $L; exit 1; }
echo "smoke ok $(date)" >> $L
python -u train_ru9.py --ffpp-only --binary --tune effort --multi-op 0.5 --tag-suffix M --seed 20260929 --workers 14 > train_ru_$T.log 2>&1
echo "end $T exit $? $(date)" >> $L
