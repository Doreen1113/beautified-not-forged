#!/bin/bash
cd /c/My_Project/AIGC/results/research/sbifix_20260927
CK=/c/My_Project/AIGC/checkpoints/research/sbifix_20260927
until timeout 30 ssh -n gsplat-ubuntu "test -f ~/AIGC_sbifix/results/research/sbifix_20260927/meta_HYBD_s20260929.json"; do sleep 300; done
scp -q gsplat-ubuntu:AIGC_sbifix/checkpoints/research/sbifix_20260927/sbifix_HYBD_s20260929.pth $CK/
for f in meta_HYBD_s20260929.json train_HYBD_s20260929.csv train_HYBD_s20260929.log; do scp -q gsplat-ubuntu:AIGC_sbifix/results/research/sbifix_20260927/$f . ; done
SBIFIX_SEED=20260929 PYTHONIOENCODING=utf-8 python -u eval_sbifix.py > eval_after_HYBD_s2.log 2>&1
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 PYTHONIOENCODING=utf-8 python -u score_cdfb.py --models HYBD-F-s2 > score_HYBD_s2.log 2>&1 && CDFB_TAG=v3 PYTHONIOENCODING=utf-8 python -u analyze_cdfb.py > analyze_after_HYBD_s2.log 2>&1)
echo "HYBD s2 done $(date)" >> after_hybd_s2.done
