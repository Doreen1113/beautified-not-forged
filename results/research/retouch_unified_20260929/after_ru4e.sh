#!/bin/bash
# After chain_ru4.sh has evaluated RU4-E (EffB4): Celeb-DF-B v3, video-level frames, vendor-val, secondary threshold, tables.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929; export PYTHONIOENCODING=utf-8
until grep -q "ru4e evaluated" after_ru.done 2>/dev/null; do sleep 600; done
(cd ../celebdfb_v2_20260927 && CDFB_TAG=v3 python -u score_cdfb.py --models RU4e-effb4 > score_ru4e_v3.log 2>&1 && CDFB_TAG=v3 python -u analyze_cdfb.py > analyze_ru4e_v3.log 2>&1)
python - <<'PY'
import numpy as np
from pathlib import Path
for d in ("cdf", "dfd"):
    z = np.load(f"{d}_scores_ru4e_effb4_s20260929.npz"); np.savez(Path("../ffpp_benchmark_20260925") / f"ours_frames_RU4e-effb4_{d}.npz", p=z["P"])
PY
(cd ../ffpp_benchmark_20260925 && python -u video_level.py > video_level_ru4e.log 2>&1)
python -u eval_vendor_val.py --arch effb4 --arm ru4e > vendor_val_ru4e.log 2>&1
python -u val_threshold.py > val_threshold_ru4e.log 2>&1
(cd ../sota_baselines_20260929 && python -u add_sota_bench.py > add_sota_ru4e.log 2>&1)
(cd /c/My_Project/AIGC/docs/paper_v2 && python make_tables.py > /dev/null 2>&1; python make_tables_ali.py > /dev/null 2>&1; python make_tables_cgd.py > /dev/null 2>&1)
echo "ru4e post-processed $(date)" >> after_ru.done
