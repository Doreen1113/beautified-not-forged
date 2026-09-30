#!/bin/bash
# RU data pipeline: wait for the FFHQ Part7 download, landmarks, vendor pair measurements (3 parallel), manifest, content
# audit, ship to Ubuntu, then launch EffB4 training on Ubuntu once the MASK seed-2 run has released the GPU.
cd /c/My_Project/AIGC/results/research/retouch_unified_20260929
export PYTHONIOENCODING=utf-8
until grep -q "^DONE" download_part7.log; do sleep 60; done
python -u prep_ffhq.py > prep_ffhq2.log 2>&1
python - <<'EOF'
from pathlib import Path
import re
B = Path(r"C:\My_Project\AIGC"); O = B / "ffhq_originals/Part7"
for name, root in (("tencent", B / "FFHQ_four_process"), ("megvii", B / "FFHQ_megvii_four_process")):
    rows = []
    for line in (root / "clean_output/clean_paths.txt").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line: continue
        k = re.search(r"(\d{5})\.png$", line).group(1)
        if (O / f"{k}.png").is_file(): rows.append(f"{O / (k + '.png')}\t{line}\t{name}")
    n = 3; parts = [rows[i::n] for i in range(n)]
    for i, pr in enumerate(parts): Path(f"pairs_{name}_in{i}.tsv").write_text("\n".join(pr) + "\n", encoding="utf-8")
    print(name, len(rows))
EOF
for name in tencent megvii; do
  for i in 0 1 2; do python -u measure_pairs.py ${name}${i} pairs_${name}_in${i}.tsv > measure_${name}${i}.log 2>&1 & done
  wait
  python - <<EOF
from pathlib import Path
parts = [Path(f"pairs_${name}{i}.tsv").read_text(encoding="utf-8").splitlines() for i in range(3)]
out = [parts[0][0]] + [l for p in parts for l in p[1:] if l.strip()]
Path("pairs_${name}.tsv").write_text("\n".join(out) + "\n", encoding="utf-8"); print("${name}", len(out) - 1)
EOF
done
python -u build_manifest.py > build_manifest.log 2>&1
python -u audit_keys.py > audit_keys.log 2>&1
bash ship_ru.sh > ship_ru.log 2>&1
until timeout 30 ssh -n gsplat-ubuntu "test -f ~/AIGC_sbifix/results/research/cgd_20260927/meta_MASK_s20260929.json"; do sleep 300; done
ssh -n gsplat-ubuntu 'cd ~/AIGC_sbifix/results/research/retouch_unified_20260929 && source ~/venvs/sbifix/bin/activate && AIGC_BASE=$HOME/AIGC_sbifix PYTHONIOENCODING=utf-8 nohup python -u train_ru.py --arch effb4 --workers 14 > train_ru_effb4_s20260929.log 2>&1 &'
echo "RU effb4 launched on Ubuntu $(date)" >> pipeline_ru.done
