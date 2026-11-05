#!/bin/bash
# Addendum 46 (+ amendment 1), runs on gsplat-ubuntu: 400-step smoke of clipe5z (L_cons trend across the end of warm-up),
# then clipe5z s1 -> clipe5bz s1 -> clipe5z s2 -> clipe5bz s2, strictly sequential.
cd ~/AIGC_sbifix/results/research/retouch_unified_20260929; source ~/venvs/sbifix/bin/activate; export AIGC_BASE=$HOME/AIGC_sbifix PYTHONIOENCODING=utf-8
L=add46_queue.log
while pgrep -f "train_ru5.py" > /dev/null; do sleep 120; done
FREE=$(python -c 'import torch;print(int(torch.cuda.mem_get_info()[0]/2**30))' 2>/dev/null); echo "free GPU GiB at start: $FREE $(date)" > $L
echo "train_ru5.py md5 $(md5sum train_ru5.py | cut -c1-32)" >> $L
python -u train_ru5.py --smooth-consistency 1.0 --seed 20260929 --workers 14 --max-steps 400 > smoke_clipe5z_s20260929.log 2>&1 || { echo "SMOKE FAILED $(date)" >> $L; exit 1; }
echo "smoke ok $(date)" >> $L
for RUN in "--smooth-consistency 1.0 --seed 20260929:clipe5z_s20260929" "--binary --smooth-consistency 1.0 --seed 20260929:clipe5bz_s20260929" \
           "--smooth-consistency 1.0 --seed 20260930:clipe5z_s20260930" "--binary --smooth-consistency 1.0 --seed 20260930:clipe5bz_s20260930"; do
  ARGS=${RUN%%:*}; T=${RUN##*:}
  echo "start $T ($ARGS) $(date)" >> $L
  python -u train_ru5.py $ARGS --workers 14 > train_ru_$T.log 2>&1
  echo "end $T exit $? $(date)" >> $L
done
echo "ADD46 TRAIN DONE $(date)" >> $L
