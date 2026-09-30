#!/bin/bash
# Pull HYBPE then MASK from Ubuntu when finished, then run the local auto-eval (after_cgd.sh <ARM>).
cd /c/My_Project/AIGC/results/research/cgd_20260927
CK=/c/My_Project/AIGC/checkpoints/research/cgd_20260927; mkdir -p $CK
for ARM in HYBPE MASK; do
  until timeout 30 ssh -n gsplat-ubuntu "test -f ~/AIGC_sbifix/results/research/cgd_20260927/meta_${ARM}_s20260928.json"; do sleep 300; done
  scp -q gsplat-ubuntu:AIGC_sbifix/checkpoints/research/cgd_20260927/cgd_${ARM}_s20260928.pth $CK/
  for f in meta_${ARM}_s20260928.json train_${ARM}_s20260928.csv train_${ARM}_s20260928.log; do scp -q gsplat-ubuntu:AIGC_sbifix/results/research/cgd_20260927/$f . ; done
  bash after_cgd.sh $ARM
done
