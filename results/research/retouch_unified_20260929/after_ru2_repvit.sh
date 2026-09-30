#!/bin/bash
# RU2-RepViT (Ubuntu): when finished, pull, evaluate (Alibaba, FF++/CDFv2/DFD, Celeb-DF-B), export TFLite with the four
# deployment gates, install the ONNX into the browser demo, regenerate paper tables.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929
export PYTHONIOENCODING=utf-8
R=gsplat-ubuntu; RB='~/AIGC_sbifix/results/research/retouch_unified_20260929'; CK=/c/My_Project/AIGC/checkpoints/research/retouch_unified_20260929
until timeout 30 ssh -n $R "test -f $RB/meta_ru_ru2_repvit_s20260929.json"; do sleep 300; done
scp -q $R:AIGC_sbifix/checkpoints/research/retouch_unified_20260929/ru_ru2_repvit_s20260929.pth $CK/
for f in meta_ru_ru2_repvit_s20260929.json train_ru_ru2_repvit_s20260929.csv train_ru_ru2_repvit_s20260929.log; do scp -q $R:$RB/$f . ; done
python -u eval_ru.py --arch repvit --arm ru2 > eval_ru2_repvit.log 2>&1
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 python -u score_cdfb.py --models RU2-repvit > score_RU2-repvit.log 2>&1 && CDFB_TAG=v3 python -u analyze_cdfb.py > analyze_RU2-repvit.log 2>&1)
python -u export_ru_tflite.py --arm ru2 > export_ru2.log 2>&1
if python -c "import json,sys; sys.exit(0 if json.load(open('export_ru_ru2.json'))['G4'] else 1)"; then
  cp /c/My_Project/AIGC/results/mobile_export/ru_ru2_repvit/ru_ru2_repvit.onnx /c/My_Project/AIGC/docs/demo_ru/models/ru_repvit.onnx
  echo "demo model -> RU2 RepViT" >> after_ru.done
fi
(cd /c/My_Project/AIGC && python docs/paper_v2/make_tables_ali.py) >> tables_ru.log 2>&1
echo "RU2 repvit evaluated $(date)" >> after_ru.done
