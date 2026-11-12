#!/bin/bash
# second seeds of the lambda 0.03, one-sided and Gaussian arms on the local GPU, sequential; train_ru5.py must not be edited while this runs
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; PY=/c/Users/2603055/AppData/Local/miniconda3/python.exe; export PYTHONIOENCODING=utf-8
for RUN in "--binary --smooth-consistency 0.03 --cons-stopgrad --tag-suffix sgl003 --seed 20260930:clipe5bzsgl003_s20260930" \
           "--binary --smooth-consistency 1.0 --cons-hinge --tag-suffix sgh --seed 20260930:clipe5bzsgh_s20260930" \
           "--binary --smooth-consistency 1.0 --cons-stopgrad --cons-op gauss --tag-suffix sgG --seed 20260930:clipe5bzsgG_s20260930"; do
  ARGS=${RUN%%:*}; T=${RUN##*:}
  [ -f meta_ru_$T.json ] && { echo "skip $T $(date)" >> add46_chain.log; continue; }
  echo "local train $T started $(date) md5 $(md5sum train_ru5.py | cut -c1-32)" >> add46_chain.log
  $PY -u train_ru5.py $ARGS --workers 8 > train_ru_$T.log 2>&1
  echo "local train $T ended exit $? $(date)" >> add46_chain.log
done
