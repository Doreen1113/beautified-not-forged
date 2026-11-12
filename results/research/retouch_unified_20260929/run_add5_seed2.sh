#!/bin/bash
# Addendum 5, seed 20260930 again: the first attempt could not read checkpoints written under transformers 4 (key prefix).
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
S=20260930; N=RU-clipe4r-s2; T=clipe4r_s$S
$PY -u select_epoch.py --tag $T > select_$T.log 2>&1
$PY -u eval_ru.py --arm clipe4r --seed $S > eval_$T.log 2>&1
$PY -u eval_vendor_val.py --arm clipe4r --seed $S > vendor_val_$T.log 2>&1
COMPARE_SBI_OUT=compare_sbi_$T.json $PY -u compare_sbi.py $T > compare_sbi_$T.log 2>&1
$PY -u compare_sota.py $T > compare_sota_$T.log 2>&1
(cd ../cgd_20260927 && $PY -u eval_cgd_explain.py --arm RUCLIPE4R --seed $S --mech donor,sd,sdxl > explain_RUCLIPE4R_s$S.log 2>&1)
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 $PY -u score_cdfb.py --models $N > score_${N}_v3.log 2>&1)
$PY -c "
import numpy as np
from pathlib import Path
for d in ('cdf', 'dfd'):
    z = np.load(f'{d}_scores_$T.npz'); np.savez(Path('../ffpp_benchmark_20260925') / f'ours_frames_${N}_{d}.npz', p=z['P'])
"
$PY -u leak_probe.py $T > leak_probe_$T.log 2>&1
echo "$T RE-evaluated $(date)" >> add5.done
