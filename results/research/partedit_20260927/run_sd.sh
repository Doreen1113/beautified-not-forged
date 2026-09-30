#!/bin/bash
cd /c/My_Project/AIGC/results/research/partedit_20260927
export HF_HUB_OFFLINE=0 PYTHONIOENCODING=utf-8
python -u gen_partedit.py --partition test --mech sd --all-parts > gen_test_sd.log 2>&1
python -u gen_partedit.py --partition train --mech sd --n 20000 > gen_train_sd.log 2>&1
