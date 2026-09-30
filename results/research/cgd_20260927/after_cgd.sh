#!/bin/bash
# When an arm finishes locally, run detection bars, Celeb-DF-B scoring and explanation bars for it.
ARM=${1:-CGD}
cd /c/My_Project/AIGC/results/research/cgd_20260927
until [ -f meta_${ARM}_s20260928.json ]; do sleep 300; done
export PYTHONIOENCODING=utf-8
python -u eval_cgd_detect.py > eval_detect_${ARM}.log 2>&1
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 python -u score_cdfb.py --models cgd_${ARM} > score_cgd_${ARM}.log 2>&1 && CDFB_TAG=v3 python -u analyze_cdfb.py > analyze_cgd_${ARM}.log 2>&1)
N=100000; [ "$ARM" = "HYBPE" ] && N=1200
python -u eval_cgd_explain.py --arm ${ARM} --mech donor,sd --n $N > explain_${ARM}.log 2>&1
echo "${ARM} evaluated $(date)" >> after_cgd.done
