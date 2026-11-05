#!/bin/bash
# Addendum 40 (P3, forged-only exposure), runs on gsplat-ubuntu. Smoke test first, then the full run.
cd ~/AIGC_sbifix/results/research/retouch_unified_20260929; source ~/venvs/sbifix/bin/activate; export AIGC_BASE=$HOME/AIGC_sbifix PYTHONIOENCODING=utf-8
python -u train_ru5.py --binary --ffpp-only --beauty fake --seed 20260929 --workers 14 --max-steps 30 > smoke_clipe5fbp3_s20260929.log 2>&1 || exit 1
python -u train_ru5.py --binary --ffpp-only --beauty fake --seed 20260929 --workers 14 > train_ru_clipe5fbp3_s20260929.log 2>&1
