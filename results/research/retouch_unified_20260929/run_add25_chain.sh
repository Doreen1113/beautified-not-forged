#!/bin/bash
# Addendum 25 evaluation: P0 and P1 (trained on Ubuntu), each as soon as its training finishes; then catch-up scoring of the
# binary arms on the full-frame DFD source.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
one() {
  T=$1; ARM=${T%_s*}
  until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_$T.json"; do sleep 300; done
  export SEL=ffpp_auc
  bash run_add6_eval.sh $T $ARM ${T#*_s} RU-$T RUCLIPE${ARM#clipe} remote
  $PY -u cdf_filtered_eval.py score $T >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $T >> dfd_v3_ours.log 2>&1
  FSRC=dfd $PY -u cdf_filtered_eval.py score $T >> dfd_filtered_score.log 2>&1; FSRC=dfdff $PY -u cdf_filtered_eval.py score $T >> dfd_filteredff_score.log 2>&1
  $PY -u cdf_filtered_eval.py analyse >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1
  FSRC=dfd $PY -u cdf_filtered_eval.py analyse >> dfd_filtered_score.log 2>&1; FSRC=dfdff $PY -u cdf_filtered_eval.py analyse >> dfd_filteredff_score.log 2>&1
  echo "ADD25 $T DONE $(date)" >> add6.done
}
one clipe5fbp0_s20260929
one clipe5fbp1_s20260929
for T in clipe5fb_s20260929 clipe5feb_s20260929 clipe5awpb_s20260930; do
  [ -f /c/My_Project/AIGC/checkpoints/research/retouch_unified_20260929/ru_$T.pth ] && FSRC=dfdff $PY -u cdf_filtered_eval.py score $T >> dfd_filteredff_score.log 2>&1
done
FSRC=dfdff $PY -u cdf_filtered_eval.py analyse >> dfd_filteredff_score.log 2>&1
echo "ADD25 DONE $(date)" >> add6.done
