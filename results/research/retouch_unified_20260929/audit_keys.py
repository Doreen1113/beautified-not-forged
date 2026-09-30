"""Content-key audit: decoded-pixel SHA256 of FFHQ Part7 (train base) vs Part2 originals and every Alibaba image (test). Expect 0."""
import hashlib, sys
from pathlib import Path
import numpy as np
from PIL import Image
from concurrent.futures import ProcessPoolExecutor
B = Path(r"C:\My_Project\AIGC")
def key(p):
    return hashlib.sha256(np.asarray(Image.open(p).convert("RGB")).tobytes()).hexdigest()
def keys(paths):
    with ProcessPoolExecutor(12) as ex: return set(ex.map(key, [str(p) for p in paths], chunksize=64))
if __name__ == "__main__":
    tr = sorted((B / "ffhq_originals/Part7").glob("*.png"))
    te = sorted((B / "ffhq_originals/Part2").glob("*.png")) + sorted((B / "FFHQ_ali_process").glob("*_*/*/*.png"))
    kt = keys(tr); ke = keys(te)
    print(f"train {len(tr)} test {len(te)} overlap {len(kt & ke)}")
