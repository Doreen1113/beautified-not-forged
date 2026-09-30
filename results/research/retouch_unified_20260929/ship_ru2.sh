#!/bin/bash
# Ship RU2 data/code to Ubuntu and queue RU2-EffB4 seed 20260930 after RU1-RepViT finishes (launch detached: ssh returns).
set -e
L=/c/My_Project/AIGC; R=gsplat-ubuntu; RB='~/AIGC_sbifix'
cd $L && tar cf - vendor_single | ssh $R "cd $RB && tar xf -"
scp -q $L/results/research/retouch_unified_20260929/{train_ru.py,ops.py,eval_ru.py,manifest_train.tsv,manifest_val.tsv,manifest_stats.json,PRE_DECLARED.md} $R:$RB/results/research/retouch_unified_20260929/
cat > /tmp/queue_ru2.sh <<'EOQ'
#!/bin/bash
cd ~/AIGC_sbifix/results/research/retouch_unified_20260929
until [ -f meta_ru_repvit_s20260929.json ]; do sleep 120; done
source ~/venvs/sbifix/bin/activate
AIGC_BASE=$HOME/AIGC_sbifix PYTHONIOENCODING=utf-8 python -u train_ru.py --arch effb4 --arm ru2 --seed 20260930 --workers 14 > train_ru_ru2_effb4_s20260930.log 2>&1
EOQ
scp -q /tmp/queue_ru2.sh $R:$RB/results/research/retouch_unified_20260929/queue_ru2.sh
ssh -n $R "cd $RB/results/research/retouch_unified_20260929 && chmod +x queue_ru2.sh && setsid nohup ./queue_ru2.sh < /dev/null > queue_ru2.out 2>&1 &"
echo shipped-and-queued
