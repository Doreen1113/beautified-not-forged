"""Export an RU RepViT model (three heads concatenated: 3 class logits + 4 presence logits + 4 quantities) to TFLite and
prove it is deployable, with the same four gates as export_mobile_tflite.py:
  G1 ONNX export, G2 TFLite file produced, G3 stock tf.lite.Interpreter loads and allocates, G4 outputs match PyTorch on
  real images (softmax |dprob| < 1e-3, identical argmax). Then a 200-image decision-agreement check on Alibaba
  originals/renders and FF++ test frames, file size and single-thread CPU latency.

python export_ru_tflite.py --arm ru1|ru2  -> results/mobile_export/ru_<arm>_repvit/{*.onnx,*.tflite}, export_ru_<arm>.json
"""
import argparse
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image

HERE = Path(__file__).resolve().parent; BASE = Path(r"C:\My_Project\AIGC")
sys.path.insert(0, str(HERE))
from train_ru import RUNet, CKPT, to_t, crop  # noqa: E402


class Flat(nn.Module):
    def __init__(self, m):
        super().__init__(); self.m = m

    def forward(self, x):
        a, b, c = self.m(x); return torch.cat([a, b, c], 1)


def images(n=200):
    boxes = json.loads((HERE / "ffhq_boxes.json").read_text()); rng = np.random.default_rng(0)
    orig = sorted((BASE / "ffhq_originals/Part2").glob("*.png")); items = []
    for p in rng.choice(orig, n // 4, replace=False):
        items.append((p, boxes[p.stem]))
        g = rng.choice(["EyeEnlarging_90", "FaceLifting_90", "Whitening_90", "Smoothing_60"])
        q = BASE / "FFHQ_ali_process" / g / f"{(int(p.stem) // 1000) * 1000}" / f"{p.stem}.png"
        if q.is_file():
            items.append((q, boxes[p.stem]))
    ff = [l.split("\t")[0] for l in (BASE / "results/research/ffpp_unified_20260925/ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
    for p in rng.choice(ff, n - len(items), replace=False):
        items.append((Path(p), None))
    return torch.stack([to_t(crop(np.array(Image.open(p).convert("RGB")), b), 224, False) for p, b in items])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--arm", default="ru1"); a = ap.parse_args()
    tag = "repvit_s20260929" if a.arm == "ru1" else "ru2_repvit_s20260929"
    net = RUNet("repvit"); net.load_state_dict(torch.load(CKPT / f"ru_{tag}.pth", map_location="cpu")); net.eval()
    model = Flat(net).eval()
    X = images(200); out = BASE / f"results/mobile_export/ru_{a.arm}_repvit"; shutil.rmtree(out, ignore_errors=True); out.mkdir(parents=True)
    with torch.no_grad():
        ref = torch.cat([model(X[i:i + 25]) for i in range(0, len(X), 25)]).numpy()
    R = {"arm": a.arm, "params_M": round(sum(p.numel() for p in net.parameters()) / 1e6, 2)}
    onnx_p = out / f"ru_{a.arm}_repvit.onnx"
    torch.onnx.export(model, X[:1], str(onnx_p), input_names=["input"], output_names=["out"], opset_version=17, dynamo=False)
    R["G1"] = onnx_p.is_file(); R["onnx_mb"] = round(onnx_p.stat().st_size / 2 ** 20, 2)
    import onnx2tf
    onnx2tf.convert(input_onnx_file_path=str(onnx_p), output_folder_path=str(out / "tf"), non_verbose=True)
    tfl = sorted((out / "tf").glob("*float32.tflite"))
    R["G2"] = bool(tfl)
    if not tfl:
        print(json.dumps(R)); return
    tfl = tfl[0]; R["tflite_mb"] = round(tfl.stat().st_size / 2 ** 20, 2)
    import tensorflow as tf
    it = tf.lite.Interpreter(model_path=str(tfl), num_threads=1); it.allocate_tensors(); R["G3"] = True
    ind, outd = it.get_input_details()[0], it.get_output_details()[0]
    def run(x):
        arr = np.transpose(x.numpy(), (0, 2, 3, 1)) if ind["shape"][-1] == 3 else x.numpy()
        it.set_tensor(ind["index"], arr.astype(np.float32)); it.invoke(); return it.get_tensor(outd["index"])[0]
    got = np.stack([run(X[i:i + 1]) for i in range(len(X))])
    sm = lambda v: np.exp(v - v.max(1, keepdims=True)) / np.exp(v - v.max(1, keepdims=True)).sum(1, keepdims=True)
    dprob = float(np.abs(sm(got[:, :3]) - sm(ref[:, :3])).max())
    R["G4_max_dlogit"] = float(np.abs(got[:, :3] - ref[:, :3]).max()); R["G4_max_dprob"] = dprob
    R["decision_agreement"] = f"{int((got[:, :3].argmax(1) == ref[:, :3].argmax(1)).sum())}/{len(X)}"
    R["presence_agreement"] = f"{int(((got[:, 3:7] > 0) == (ref[:, 3:7] > 0)).all(1).sum())}/{len(X)}"
    R["G4"] = bool(dprob < 1e-3 and (got[:, :3].argmax(1) == ref[:, :3].argmax(1)).all())
    for _ in range(5):
        run(X[:1])
    t = time.perf_counter()
    for i in range(50):
        run(X[i:i + 1])
    R["cpu_ms_1thread"] = round((time.perf_counter() - t) / 50 * 1000, 2)
    (HERE / f"export_ru_{a.arm}.json").write_text(json.dumps(R, indent=1)); print(json.dumps(R, indent=1))


if __name__ == "__main__":
    main()
