#!/bin/bash
# RU3 / RU3-E (Ubuntu): pull when finished, evaluate (Alibaba once, FF++/CDFv2/DFD, Celeb-DF-B, vendor-val, explanation
# for RU3-E), then regenerate tables. Runs both arms in whichever order they finish.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929
export PYTHONIOENCODING=utf-8
R=gsplat-ubuntu; RB='~/AIGC_sbifix/results/research/retouch_unified_20260929'; CK=/c/My_Project/AIGC/checkpoints/research/retouch_unified_20260929
done_arms=""
while [ "$(echo $done_arms | wc -w)" -lt 2 ]; do
  for ARM in ru3 ru3e; do
    echo "$done_arms" | grep -qw $ARM && continue
    timeout 30 ssh -n $R "test -f $RB/meta_ru_${ARM}_effb4_s20260929.json" || continue
    scp -q $R:AIGC_sbifix/checkpoints/research/retouch_unified_20260929/ru_${ARM}_effb4_s20260929.pth $CK/
    for f in meta_ru_${ARM}_effb4_s20260929.json train_ru_${ARM}_effb4_s20260929.csv train_ru_${ARM}_effb4_s20260929.log; do scp -q $R:$RB/$f . ; done
    python -u eval_ru.py --arch effb4 --arm $ARM > eval_${ARM}_effb4.log 2>&1
    python -u eval_vendor_val.py --arch effb4 --arm $ARM > vendor_val_${ARM}.log 2>&1
    (cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 python -u score_cdfb.py --models RU3${ARM#ru3}-effb4 > score_${ARM}.log 2>&1 && CDFB_TAG=v3 python -u analyze_cdfb.py > analyze_${ARM}.log 2>&1)
    if [ "$ARM" = "ru3e" ]; then (cd ../cgd_20260927 && python -u eval_cgd_explain.py --arm RU3E --seed 20260929 --mech donor,sd,sdxl > explain_RU3E.log 2>&1); fi
    python -u compare_sbi.py effb4_s20260929 ru2_effb4_s20260929 ${ARM}_effb4_s20260929 > compare_sbi_${ARM}.log 2>&1
    (cd /c/My_Project/AIGC && python docs/paper_v2/make_tables_ali.py) >> tables_ru.log 2>&1
    echo "$ARM evaluated $(date)" >> after_ru.done; done_arms="$done_arms $ARM"
  done
  sleep 600
done
