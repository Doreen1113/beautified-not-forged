#!/bin/bash
# Addendum 5 evaluation chain (local GPU, detached): for each re-run seed, once its epoch has been chosen on validation data,
# one Alibaba read + FF++ / CDFv2 / DFD, vendor validation, paired tests vs SBI / Effort / Forensics Adapter, held-out part
# edits (E1), Celeb-DF-B, video-level frames, and the re-encoding control. Outputs are named by the tag.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
R=gsplat-ubuntu; RB=AIGC_sbifix/results/research/retouch_unified_20260929; RC=AIGC_sbifix/checkpoints/research/retouch_unified_20260929
CK=/c/My_Project/AIGC/checkpoints/research/retouch_unified_20260929

evalseed() {   # $1 seed, $2 model name in the Celeb-DF-B / video-level registries
  S=$1; N=$2; T=clipe4r_s$S
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
  $PY -u pipeline_trace_probe.py $T > pipeline_trace_$T.log 2>&1
  echo "$T evaluated $(date)" >> add5.done
}

# seed 20260929: trained and selected by run_add5_local.sh
until [ -f select_clipe4r_s20260929.json ]; do sleep 120; done
evalseed 20260929 RU-clipe4r

# seed 20260930: trained on the Ubuntu box; fetch every epoch, choose the epoch here with the same script
until timeout 30 ssh -n $R "test -f $RB/meta_ru_clipe4r_s20260930.json"; do sleep 300; done
for e in 01 02 03 04 05 06 07 08; do scp -q $R:$RC/ru_clipe4r_s20260930_e$e.pth $CK/; done
for f in meta_ru_clipe4r_s20260930.json train_ru_clipe4r_s20260930.csv train_ru_clipe4r_s20260930.log; do scp -q $R:$RB/$f . ; done
$PY -u select_epoch.py --tag clipe4r_s20260930 > select_clipe4r_s20260930.log 2>&1
evalseed 20260930 RU-clipe4r-s2

(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 $PY -u analyze_cdfb.py > analyze_add5_v3.log 2>&1)
(cd ../ffpp_benchmark_20260925 && $PY -u video_level.py > video_level_add5.log 2>&1)
echo "ADD5 ALL DONE $(date)" >> add5.done
