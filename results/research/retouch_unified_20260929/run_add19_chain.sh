#!/bin/bash
# Addendum 19 evaluation: the consistency arm and the 3-step arm, each as soon as its Ubuntu training finishes.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
one() {
  T=$1; ARM=${T%_s*}
  until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_$T.json"; do sleep 300; done
  export SEL=ffpp_f1
  bash run_add6_eval.sh $T $ARM ${T#*_s} RU-$T RUCLIPE${ARM#clipe} remote
  $PY -u cdf_filtered_eval.py score $T >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $T >> dfd_v3_ours.log 2>&1
  FSRC=dfd $PY -u cdf_filtered_eval.py score $T >> dfd_filtered_score.log 2>&1
  $PY -u cdf_filtered_eval.py analyse >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1; FSRC=dfd $PY -u cdf_filtered_eval.py analyse >> dfd_filtered_score.log 2>&1
  $PY -u adv_probe.py $T >> adv_probe.log 2>&1
  echo "ADD19 $T DONE $(date)" >> add6.done
}
one clipe5awptf_s20260929
one clipe5awps3f_s20260929
echo "ADD19 DONE $(date)" >> add6.done
