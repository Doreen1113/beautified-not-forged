#!/bin/bash
# Addendum 36: full main-model chain for clipe5y (checkpoint by the main model's rule, not ffpp_auc).
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; T=clipe5y_s20260929
until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_$T.json"; do sleep 300; done
unset SEL; bash run_add6_eval.sh $T clipe5y 20260929 RU-$T RUCLIPE5y remote
$PY -u smooth_evasion.py score $T >> smooth_evasion2.log 2>&1
$PY -u cdf_filtered_eval.py score $T >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $T >> dfd_v3_ours.log 2>&1
FSRC=dfdff $PY -u cdf_filtered_eval.py score $T >> dfd_filteredff_score.log 2>&1; FSRC=cdfff $PY -u cdf_filtered_eval.py score $T >> cdf_filteredff_score.log 2>&1
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 $PY -u score_cdfb.py --models RU-$T > score_RU-${T}_v3.log 2>&1 && $PY -u fair_cdfb.py RU-$T > fair_RU-$T.log 2>&1)
(cd ../df40_eval_20261012 && $PY -u df40_eval.py score $T >> score_ext.log 2>&1 && $PY -u df40_eval.py analyse > analyse_ext.log 2>&1)
(cd ../alipair_zeroshot_20260929 && $PY -u eval_published_ali.py analyse > analyse_new3.log 2>&1)
$PY smooth_evasion.py analyse > smooth_evasion2_table.txt 2>&1
echo "ADD36 DONE $(date)" >> add6.done
