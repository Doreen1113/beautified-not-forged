#!/bin/bash
# Launch RU4 (Addendum 4) on each GPU as soon as it frees: local -> clipe4 after CLIP-E seed 2; Ubuntu -> ru4e (EffB4) after
# both RU3 jobs. Then evaluate (Alibaba once, FF++/CDFv2/DFD, explanation on held-out part edits).
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
R=gsplat-ubuntu; RB=AIGC_sbifix/results/research/retouch_unified_20260929
scp -q train_ru3.py train_ru_clip.py eval_ru.py PRE_DECLARED.md $R:$RB/
ssh -n $R "mkdir -p ~/AIGC_sbifix/results/research/partedit_20260927"
scp -q ../partedit_20260927/manifest_train_donor.tsv ../partedit_20260927/manifest_train_sd.tsv $R:AIGC_sbifix/results/research/partedit_20260927/
(
  until [ -f meta_ru_clipe_s20260930.json ]; do sleep 300; done
  python -u train_ru_clip.py --head --arm ru4 --workers 12 > train_ru_clipe4_s20260929.log 2>&1
  python -u eval_ru.py --arm clipe4 > eval_clipe4.log 2>&1
  (cd ../cgd_20260927 && python -u eval_cgd_explain.py --arm RUCLIPE4 --seed 20260929 --mech donor,sd,sdxl > explain_RUCLIPE4.log 2>&1)
  python -u compare_sbi.py clipe_s20260929 clipe4_s20260929 > compare_sbi_clipe4.log 2>&1
  echo "clipe4 evaluated $(date)" >> after_ru.done
) &
(
  until timeout 30 ssh -n $R "test -f $RB/meta_ru_ru3_effb4_s20260929.json -a -f $RB/meta_ru_ru3e_effb4_s20260929.json"; do sleep 300; done
  ssh -n $R "cd $RB && source ~/venvs/sbifix/bin/activate && AIGC_BASE=\$HOME/AIGC_sbifix PYTHONIOENCODING=utf-8 setsid nohup python -u train_ru3.py --arch effb4 --arm ru4 --head --workers 14 < /dev/null > train_ru_ru4e_effb4_s20260929.log 2>&1 &"
  until timeout 30 ssh -n $R "test -f $RB/meta_ru_ru4e_effb4_s20260929.json"; do sleep 600; done
  scp -q $R:AIGC_sbifix/checkpoints/research/retouch_unified_20260929/ru_ru4e_effb4_s20260929.pth /c/My_Project/AIGC/checkpoints/research/retouch_unified_20260929/
  for f in meta_ru_ru4e_effb4_s20260929.json train_ru_ru4e_effb4_s20260929.csv train_ru_ru4e_effb4_s20260929.log; do scp -q $R:$RB/$f . ; done
  python -u eval_ru.py --arch effb4 --arm ru4e > eval_ru4e_effb4.log 2>&1
  (cd ../cgd_20260927 && python -u eval_cgd_explain.py --arm RU4E --seed 20260929 --mech donor,sd,sdxl > explain_RU4E.log 2>&1)
  python -u compare_sbi.py ru3e_effb4_s20260929 ru4e_effb4_s20260929 > compare_sbi_ru4e.log 2>&1
  echo "ru4e evaluated $(date)" >> after_ru.done
) &
wait
