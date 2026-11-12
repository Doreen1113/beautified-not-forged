#!/bin/bash
# Round 2 queue on the local GPU (Addendum 18): after the worst-case run finishes, R2-3 seed 2 then R2-1 seed 2.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
until [ -f meta_ru_clipe5af_s20260929.json ]; do sleep 180; done
until [ -f fit_operator_prior_wide.npz ]; do scp -q gsplat-ubuntu:AIGC_sbifix/results/research/retouch_unified_20260929/fit_operator_prior_wide.npz . 2>/dev/null || sleep 120; done
scp -q gsplat-ubuntu:AIGC_sbifix/results/research/retouch_unified_20260929/fit_operator_wide.json gsplat-ubuntu:AIGC_sbifix/results/research/retouch_unified_20260929/FIT_OPERATOR_WIDE.md . 2>/dev/null
$PY -u train_ru5.py --binary --adv worst --adv-wide --adv-prior --seed 20260930 --workers 12 > train_ru_clipe5awpb_s20260930.log 2>&1
$PY -u train_ru5.py --ffpp-only --adv worst --adv-wide --adv-prior --seed 20260930 --workers 12 > train_ru_clipe5awpf_s20260930.log 2>&1
echo "ADD18 LOCAL TRAINING DONE $(date)" >> add6.done
