#!/bin/bash
# After score_sota.py: fold the two SOTA detectors into every analysis and rebuild the paper tables/figures.
cd /c/My_Project/AIGC/results/research/sota_baselines_20260929
export PYTHONIOENCODING=utf-8
until grep -q "^DONE" score_sota.log; do sleep 60; done
python -u add_sota_bench.py > add_sota_bench.log 2>&1
(cd ../ffpp_benchmark_20260925 && python -u video_level.py > video_level_sota.log 2>&1)
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 python -u analyze_cdfb.py > analyze_sota.log 2>&1)
(cd ../alipair_zeroshot_20260929 && python -u eval_published_ali.py analyse > analyse_sota.log 2>&1)
cd /c/My_Project/AIGC && python docs/paper_v2/make_tables.py && python docs/paper_v2/make_tables_ali.py && python docs/paper_v2/make_figures.py && python docs/paper_v2/make_fig_ali.py
echo "sota folded in $(date)" >> results/research/sota_baselines_20260929/after_sota.done
