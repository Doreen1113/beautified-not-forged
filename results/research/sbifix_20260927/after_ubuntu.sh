#!/bin/bash
# Pull finished Ubuntu arms (SBI then SUP), evaluate locally: FF++/CDF/DFD bars + Celeb-DF-B.
cd /c/My_Project/AIGC/results/research/sbifix_20260927
CK=/c/My_Project/AIGC/checkpoints/research/sbifix_20260927; mkdir -p $CK
for ARM in ${ARMS:-SBI SUP}; do
  until timeout 30 ssh -n gsplat-ubuntu "test -f ~/AIGC_sbifix/results/research/sbifix_20260927/meta_${ARM}_s20260928.json"; do sleep 120; done
  scp -q gsplat-ubuntu:AIGC_sbifix/checkpoints/research/sbifix_20260927/sbifix_${ARM}_s20260928.pth $CK/
  for f in meta_${ARM}_s20260928.json train_${ARM}_s20260928.csv train_${ARM}_s20260928.log; do scp -q gsplat-ubuntu:AIGC_sbifix/results/research/sbifix_20260927/$f . ; done
  PYTHONIOENCODING=utf-8 python -u eval_sbifix.py > eval_after_${ARM}.log 2>&1
  (cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 PYTHONIOENCODING=utf-8 python -u score_cdfb.py --models ${ARM}-F > score_${ARM}F.log 2>&1 && CDFB_TAG=v3 PYTHONIOENCODING=utf-8 python -u analyze_cdfb.py > analyze_after_${ARM}.log 2>&1)
  echo "${ARM} evaluated $(date)"
done
