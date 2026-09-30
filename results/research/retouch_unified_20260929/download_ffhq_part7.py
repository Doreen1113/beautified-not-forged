"""Download the FFHQ originals (level-0) for the Tencent/Megvii composite base indices (60000-69999, HF Part7),
same source and verification as retouching_benchmark_20260823/download_ffhq_originals.py. Only indices present in the
cleaned Tencent or Megvii lists are fetched.

python download_ffhq_part7.py
"""
import re
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from huggingface_hub import hf_hub_download

BASE = Path(r"C:\My_Project\AIGC")
OUT = BASE / "ffhq_originals"
REPO = "marcosv/ffhq-dataset"


def wanted():
    idx = set()
    for cp in (BASE / "FFHQ_four_process/clean_output/clean_paths.txt", BASE / "FFHQ_megvii_four_process/clean_output/clean_paths.txt"):
        for line in cp.read_text(encoding="utf-8").splitlines():
            m = re.search(r"(\d{5})\.png$", line.strip())
            if m:
                idx.add(int(m.group(1)))
    return sorted(idx)


def fetch(i):
    rel = f"Part{i // 10000 + 1}/{i:05d}.png"
    dst = OUT / rel
    if dst.exists() and dst.stat().st_size > 100_000:
        return "cached"
    try:
        hf_hub_download(REPO, rel, repo_type="dataset", local_dir=str(OUT)); return "ok"
    except Exception as e:  # noqa: BLE001
        return f"ERR {type(e).__name__}"


def main():
    idx = wanted(); print(f"indices: {len(idx)} range {idx[0]}..{idx[-1]}", flush=True)
    n = 0; err = 0
    with ThreadPoolExecutor(8) as ex:
        for r in ex.map(fetch, idx):
            n += 1; err += r.startswith("ERR")
            if n % 500 == 0:
                print(f"{n}/{len(idx)} err={err}", flush=True)
    print(f"DONE {n} err={err}", flush=True)


if __name__ == "__main__":
    main()
