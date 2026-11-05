#!/bin/bash
# Addendum 5, local GPU: RU4-CLIP re-run (seed 20260929) with every epoch saved, then validation-only epoch selection.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
$PY -u train_ru_clip.py --head --arm ru4 --suffix r --save-all --seed 20260929 --workers 12 > train_ru_clipe4r_s20260929.log 2>&1
$PY -u select_epoch.py --tag clipe4r_s20260929 > select_clipe4r_s20260929.log 2>&1
echo "clipe4r s20260929 trained+selected $(date)" >> add5.done
