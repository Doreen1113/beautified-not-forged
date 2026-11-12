#!/bin/bash
# waits for the Ubuntu->103 mirror, runs two 30-step smokes on a 4090 (--grad-ckpt), then starts sg s2 (GPU0) and FF++-only sg s1 (GPU1)
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; LOG=add46_103_launch.log
until ssh -o ConnectTimeout=20 gsplat-ubuntu "grep -q RSYNC_DONE ~/rsync_103.log"; do sleep 60; done
echo "mirror done $(date)" >> $LOG
scp -q train_ru5.py cvlab-103:/mnt/sdb/doreen071/AIGC_sbifix/results/research/retouch_unified_20260929/train_ru5.py   # patched copy (grad-ckpt flag)
ssh cvlab-103 'bash /mnt/sdb/doreen071/run_103.sh 0 "--binary --smooth-consistency 1.0 --cons-stopgrad --tag-suffix sgsmoke103 --seed 20260929 --max-steps 30" clipe5bzsgsmoke103_s20260929; bash /mnt/sdb/doreen071/run_103.sh 1 "--ffpp-only --binary --smooth-consistency 1.0 --cons-stopgrad --tag-suffix sgsmoke103 --seed 20260929 --max-steps 30" clipe5fbzsgsmoke103_s20260929'
for T in clipe5bzsgsmoke103_s20260929 clipe5fbzsgsmoke103_s20260929; do
  ssh cvlab-103 "grep 'smoke step 30' /mnt/sdb/doreen071/AIGC_sbifix/results/research/retouch_unified_20260929/train_ru_$T.log; tail -2 /mnt/sdb/doreen071/AIGC_sbifix/results/research/retouch_unified_20260929/train_ru_$T.log | cut -c1-200" >> $LOG 2>&1
done
if grep -q "clipe5bzsgsmoke103.*\|smoke step 30" $LOG && [ $(grep -c "smoke step 30" $LOG) -ge 2 ]; then
  ssh cvlab-103 'cd /mnt/sdb/doreen071 && nohup bash run_103.sh 0 "--binary --smooth-consistency 1.0 --cons-stopgrad --tag-suffix sg --seed 20260930" clipe5bzsg_s20260930 > /dev/null 2>&1 &
                 nohup bash run_103.sh 1 "--ffpp-only --binary --smooth-consistency 1.0 --cons-stopgrad --tag-suffix sg --seed 20260929" clipe5fbzsg_s20260929 > /dev/null 2>&1 & sleep 2; echo launched'
  echo "full runs launched on 103 $(date)" >> $LOG
else
  echo "SMOKE FAILED on 103, nothing launched $(date)" >> $LOG
fi
