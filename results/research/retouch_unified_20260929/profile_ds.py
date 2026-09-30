import time, sys, numpy as np
sys.path.insert(0, ".")
from train_ru import RUData, read_manifest, ARCH
from pathlib import Path
rows = read_manifest("manifest_train.tsv"); ds = RUData(rows, 380, 1); ds.epoch = 1
rng = np.random.default_rng(0); idx = rng.choice(len(ds), 40, replace=False)
t = time.time()
for i in idx: ds[int(i)]
print(f"mean per photo (triplet): {(time.time()-t)/40:.3f}s")
# split by base type
ff = [i for i in idx if ds.bases[int(i)]["src"] == "ffpp_real"]; fh = [i for i in idx if ds.bases[int(i)]["src"] == "ffhq_orig"]
for name, ii in (("ffpp", ff), ("ffhq", fh)):
    t = time.time()
    for i in ii: ds[int(i)]
    print(name, len(ii), f"{(time.time()-t)/max(1,len(ii)):.3f}s")
