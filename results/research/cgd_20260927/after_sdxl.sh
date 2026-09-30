#!/bin/bash
# When the SDXL held-out set is complete (E4), evaluate every head on it and regenerate the paper tables.
cd /c/My_Project/AIGC/results/research/cgd_20260927
PE=../partedit_20260927
until grep -a -q "^DONE" $PE/gen_test_sdxl2.log 2>/dev/null; do sleep 300; done
export PYTHONIOENCODING=utf-8
for ARM in MASK CGD CGDD; do
  python -u eval_cgd_explain.py --arm $ARM --mech donor,sd,sdxl > explain_${ARM}_sdxl.log 2>&1
done
python -u eval_cgd_explain.py --arm HYBPE --mech donor,sd,sdxl --n 1200 > explain_HYBPE_sdxl.log 2>&1
cd /c/My_Project/AIGC && python docs/paper_v2/make_tables_cgd.py
echo "sdxl evaluated $(date)" >> results/research/cgd_20260927/after_cgd.done
