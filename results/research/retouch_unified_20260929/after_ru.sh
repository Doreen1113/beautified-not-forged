#!/bin/bash
# When RU effb4 finishes on Ubuntu: launch RU repvit there, pull the effb4 checkpoint + logs, evaluate locally
# (Alibaba blind test, FF++/CDFv2/DFD, Celeb-DF-B), regenerate the paper table. Then the same for repvit.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929
export PYTHONIOENCODING=utf-8
R=gsplat-ubuntu; RB='~/AIGC_sbifix'; CK=/c/My_Project/AIGC/checkpoints/research/retouch_unified_20260929; mkdir -p $CK
until [ -f pipeline_ru.done ]; do sleep 300; done
for ARCH in effb4 repvit; do
  until timeout 30 ssh -n $R "test -f $RB/results/research/retouch_unified_20260929/meta_ru_${ARCH}_s20260929.json"; do sleep 600; done
  if [ "$ARCH" = "effb4" ]; then
    ssh -n $R "cd $RB/results/research/retouch_unified_20260929 && source ~/venvs/sbifix/bin/activate && AIGC_BASE=\$HOME/AIGC_sbifix PYTHONIOENCODING=utf-8 nohup python -u train_ru.py --arch repvit --workers 14 > train_ru_repvit_s20260929.log 2>&1 &"
  fi
  scp -q $R:$RB/checkpoints/research/retouch_unified_20260929/ru_${ARCH}_s20260929.pth $CK/
  for f in meta_ru_${ARCH}_s20260929.json train_ru_${ARCH}_s20260929.csv train_ru_${ARCH}_s20260929.log; do scp -q $R:$RB/results/research/retouch_unified_20260929/$f . ; done
  python -u eval_ru.py --arch $ARCH > eval_ru_${ARCH}.log 2>&1
  (cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 python -u score_cdfb.py --models RU-${ARCH} > score_RU-${ARCH}.log 2>&1 && CDFB_TAG=v3 python -u analyze_cdfb.py > analyze_RU-${ARCH}.log 2>&1)
  (cd /c/My_Project/AIGC && python docs/paper_v2/make_tables_ali.py) >> tables_ru.log 2>&1
  echo "RU ${ARCH} evaluated $(date)" >> after_ru.done
done
