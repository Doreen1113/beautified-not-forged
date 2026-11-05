#!/bin/bash
# Part-level explanation on the leak-free donor set (donor_v2; manifest_test_donor_v2.tsv) for the paper's models.
cd /c/My_Project/AIGC/results/research/cgd_20260927; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
until grep -q "CDF_FILTERED DONE" ../retouch_unified_20260929/add6.done; do sleep 180; done
for a in "RUCLIPE5 20260929" "RUCLIPE5 20260930" "RUCLIPE4R 20260929" "RU4E 20260929" "RUCLIPE5B 20260929"; do set -- $a
  $PY -u eval_cgd_explain.py --arm $1 --seed $2 --mech donor_v2 > explain_${1}_s${2}_donor_v2.log 2>&1
done
echo "DONOR_V2 DONE $(date)" >> ../retouch_unified_20260929/add6.done