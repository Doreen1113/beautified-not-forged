#!/bin/bash
# Round 2 evaluation (Addendum 18): each arm as soon as its training finishes; every test source read once per arm.
# $1 tag, $2 selection (ffpp_f1 | ffpp_auc | c2), $3 local|remote
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe
one() {
  T=$1; ARM=${T%_s*}
  if [ "$3" = "remote" ]; then
    until timeout 30 ssh -n gsplat-ubuntu "test -f AIGC_sbifix/results/research/retouch_unified_20260929/meta_ru_$T.json"; do sleep 300; done
  else
    until [ -f meta_ru_$T.json ]; do sleep 300; done
  fi
  if [ "$2" = "c2" ]; then unset SEL; else export SEL=$2; fi
  bash run_add6_eval.sh $T $ARM ${T#*_s} RU-$T RUCLIPE${ARM#clipe} $3
  $PY -u cdf_filtered_eval.py score $T >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py score $T >> dfd_v3_ours.log 2>&1
  FSRC=dfd $PY -u cdf_filtered_eval.py score $T >> dfd_filtered_score.log 2>&1
  $PY -u cdf_filtered_eval.py analyse >> cdf_filtered_ours.log 2>&1; $PY -u dfd_v3_eval.py analyse >> dfd_v3_ours.log 2>&1; FSRC=dfd $PY -u cdf_filtered_eval.py analyse >> dfd_filtered_score.log 2>&1
  $PY -u adv_probe.py $T >> adv_probe.log 2>&1
  echo "ADD18 $T DONE $(date)" >> add6.done
}
one clipe5awpf_s20260929 ffpp_f1 remote
one clipe5awpb_s20260929 ffpp_auc remote
one clipe5awpb_s20260930 ffpp_auc local
one clipe5awpd_s20260929 c2 remote
one clipe5awpf_s20260930 ffpp_f1 local
echo "ADD18 DONE $(date)" >> add6.done
