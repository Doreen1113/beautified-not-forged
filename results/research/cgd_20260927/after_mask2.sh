#!/bin/bash
# MASK seed 2 (Ubuntu, s20260929): pull when finished, then detection bars (seed-named outputs), Celeb-DF-B and explanation.
cd /c/My_Project/AIGC/results/research/cgd_20260927
CK=/c/My_Project/AIGC/checkpoints/research/cgd_20260927
until timeout 30 ssh -n gsplat-ubuntu "test -f ~/AIGC_sbifix/results/research/cgd_20260927/meta_MASK_s20260929.json"; do sleep 600; done
scp -q gsplat-ubuntu:AIGC_sbifix/checkpoints/research/cgd_20260927/cgd_MASK_s20260929.pth $CK/
for f in meta_MASK_s20260929.json train_MASK_s20260929.csv train_MASK_s20260929.log; do scp -q gsplat-ubuntu:AIGC_sbifix/results/research/cgd_20260927/$f . ; done
export PYTHONIOENCODING=utf-8
CGD_SEED=20260929 python -u eval_cgd_detect.py > eval_detect_MASK_s2.log 2>&1
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 python -u score_cdfb.py --models cgd_MASK-s2 > score_cgd_MASK-s2.log 2>&1 && CDFB_TAG=v3 python -u analyze_cdfb.py > analyze_cgd_MASK-s2.log 2>&1)
MECH=donor,sd; grep -a -q "^DONE" ../partedit_20260927/gen_test_sdxl2.log 2>/dev/null && MECH=donor,sd,sdxl
python -u eval_cgd_explain.py --arm MASK --seed 20260929 --mech $MECH > explain_MASK_s2.log 2>&1
echo "MASK seed2 evaluated $(date)" >> after_cgd.done
