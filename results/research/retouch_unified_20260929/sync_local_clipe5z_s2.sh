#!/bin/bash
# when the local clipe5z s2 training finishes, copy its outputs to Ubuntu so run_add46_chain.sh (which fetches from Ubuntu) continues
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; T=clipe5z_s20260930
until [ -f meta_ru_$T.json ]; do sleep 600; done
scp -q meta_ru_$T.json train_ru_$T.csv train_ru_$T.log gsplat-ubuntu:~/AIGC_sbifix/results/research/retouch_unified_20260929/
scp -q /c/My_Project/AIGC/checkpoints/research/retouch_unified_20260929/ru_${T}_e0*.pth gsplat-ubuntu:~/AIGC_sbifix/checkpoints/research/retouch_unified_20260929/
echo "synced local $T to Ubuntu $(date)" >> add46_chain.log
