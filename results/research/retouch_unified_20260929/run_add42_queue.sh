#!/bin/bash
# Addendum 42 (second seeds of clipe5y and clipe5b), runs on gsplat-ubuntu after the Addendum 40 run (P3) has finished.
cd ~/AIGC_sbifix/results/research/retouch_unified_20260929; source ~/venvs/sbifix/bin/activate; export AIGC_BASE=$HOME/AIGC_sbifix PYTHONIOENCODING=utf-8
while pgrep -f "train_ru5.py --binary --ffpp-only --beauty fake" > /dev/null; do sleep 120; done
FREE=$(python -c 'import torch;print(int(torch.cuda.mem_get_info()[0]/2**30))' 2>/dev/null); echo "free GPU GiB at start: $FREE $(date)" > add42_queue.log
python -u train_ru5.py --sym-smooth --seed 20260930 --workers 12 > train_ru_clipe5y_s20260930.log 2>&1 &
sleep 600
python -u train_ru5.py --binary --seed 20260930 --workers 12 > train_ru_clipe5b_s20260930.log 2>&1 &
wait; echo "ADD42 TRAIN DONE $(date)" >> add42_queue.log
