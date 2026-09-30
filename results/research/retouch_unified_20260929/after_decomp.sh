#!/bin/bash
# When all 12 decomposition shards are done: rebuild manifests (with vendor_single), smoke-test RU2, train RU2-EffB4 locally,
# then evaluate (Alibaba blind, FF++/CDFv2/DFD, Celeb-DF-B) and compare with SBI.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929
export PYTHONIOENCODING=utf-8
until [ "$(ls decomp_tencent_[0-3].tsv decomp_megvii_[0-7].tsv 2>/dev/null | wc -l)" = "12" ]; do sleep 60; done
python -u build_manifest.py > build_manifest_ru2.log 2>&1
python -u train_ru.py --arch effb4 --arm ru2 --workers 12 --max-steps 20 > smoke_ru2.log 2>&1 || exit 1
python -u train_ru.py --arch effb4 --arm ru2 --workers 12 > train_ru_ru2_effb4_s20260929.log 2>&1
python -u eval_ru.py --arch effb4 --arm ru2 > eval_ru2_effb4.log 2>&1
python -u compare_sbi.py effb4_s20260929 ru2_effb4_s20260929 > compare_sbi_ru2.log 2>&1
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 python -u score_cdfb.py --models RU2-effb4 > score_RU2-effb4.log 2>&1 && CDFB_TAG=v3 python -u analyze_cdfb.py > analyze_RU2-effb4.log 2>&1)
(cd /c/My_Project/AIGC && python docs/paper_v2/make_tables_ali.py) >> tables_ru.log 2>&1
echo "RU2 effb4 evaluated $(date)" >> after_ru.done
