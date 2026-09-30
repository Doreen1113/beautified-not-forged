#!/bin/bash
# RU-CLIP (local): when training finishes, evaluate on Alibaba (once), FF++/CDFv2/DFD, Celeb-DF-B; paired comparison vs SBI.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929
export PYTHONIOENCODING=utf-8
TAG=${1:-clipe}
until [ -f meta_ru_${TAG}_s20260929.json ]; do sleep 600; done
python -u eval_ru.py --arm ${TAG} > eval_${TAG}.log 2>&1
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 python -u score_cdfb.py --models RU-${TAG} > score_${TAG}.log 2>&1 && CDFB_TAG=v3 python -u analyze_cdfb.py > analyze_${TAG}.log 2>&1)
python -u compare_sbi.py effb4_s20260929 ru2_effb4_s20260929 ${TAG}_s20260929 > compare_sbi_${TAG}.log 2>&1
(cd /c/My_Project/AIGC && python docs/paper_v2/make_tables_ali.py) >> tables_ru.log 2>&1
echo "${TAG} evaluated $(date)" >> after_ru.done
