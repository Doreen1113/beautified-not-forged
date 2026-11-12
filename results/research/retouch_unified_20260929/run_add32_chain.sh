#!/bin/bash
# Addendum 32: evaluate the smoothing-only arms as each finishes on Ubuntu (same steps as run_add25c_chain.sh).
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
one() {
  T=$1; ARM=${T%_s*}
  until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_$T.json"; do sleep 300; done
  export SEL=ffpp_auc
  bash run_add6_eval.sh $T $ARM ${T#*_s} RU-$T RUCLIPE${ARM#clipe} remote
  $PY -u cdf_filtered_eval.py score $T >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $T >> dfd_v3_ours.log 2>&1
  FSRC=dfdff $PY -u cdf_filtered_eval.py score $T >> dfd_filteredff_score.log 2>&1; FSRC=cdfff $PY -u cdf_filtered_eval.py score $T >> cdf_filteredff_score.log 2>&1
  echo "ADD32 $T DONE $(date)" >> add6.done
}
one clipe5fbg0o_s20260929; one clipe5fbg0o_s20260930; one clipe5fbg0p1o_s20260929
echo "ADD32 DONE $(date)" >> add6.done
