#!/bin/bash
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929
bash run_add6_eval.sh clipe6_s20260929 clipe6 20260929 RU-clipe6 RUCLIPE6 remote
bash run_add6_eval.sh clipe5_s20260930 clipe5 20260930 RU-clipe5-s2 RUCLIPE5 remote
bash run_add6_eval.sh clipe5g0_s20260929 clipe5g0 20260929 RU-clipe5g0 RUCLIPE5G0 local
bash run_add6_eval.sh clipe5v0_s20260929 clipe5v0 20260929 RU-clipe5v0 RUCLIPE5V0 local
echo "QUEUE2 DONE $(date)" >> add6.done
