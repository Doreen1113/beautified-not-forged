"""Export Ours-lite (ru4e: EfficientNet-B4 + three heads, the browser-sized version of the paper model) to ONNX for the
web demo, and check the ONNX graph against PyTorch on real test images.

Outputs: logits (1,3) real/fake/filter, presence (1,4) eye/contour/tone/texture logits, evidence (1,1,12,12) logits.
Input: (1,3,380,380), RGB in [0,1] normalised as (x-0.5)/0.5 (same as eval_ru.DS for EfficientNet-B4).

python export_demo_onnx.py -> docs/demo/models/ours_lite.onnx, export_demo_onnx.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import onnxruntime as ort
import torch
from PIL import Image

HERE = Path(__file__).resolve().parent; B = Path(r"C:\My_Project\AIGC")
sys.path.insert(0, str(HERE))
from train_ru3 import RUNet3, to_t2  # noqa: E402

OUT = B / "docs/demo/models/ours_lite.onnx"


class Wrap(torch.nn.Module):
    def __init__(self, m):
        super().__init__(); self.m = m

    def forward(self, x):
        lo, pr, _q, ev = self.m(x)
        return lo, pr, ev


def main():
    net = RUNet3("effb4", head=True)
    net.load_state_dict(torch.load(B / "checkpoints/research/retouch_unified_20260929/ru_ru4e_effb4_s20260929.pth", map_location="cpu"))
    w = Wrap(net).eval()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    torch.onnx.export(w, torch.zeros(1, 3, 380, 380), OUT, input_names=["input"], output_names=["logits", "presence", "evidence"],
                      opset_version=17, dynamo=False)
    sess = ort.InferenceSession(str(OUT), providers=["CPUExecutionProvider"])
    rows = [l.split("\t") for l in (B / "results/research/ffpp_unified_20260925/ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:]]
    paths = [r[0] for r in rows][::97][:60]
    dmax, agree = 0.0, 0
    for p in paths:
        x = to_t2(np.array(Image.open(p).convert("RGB")), 380, False, "half")[None]
        with torch.no_grad():
            a = [t.numpy() for t in w(x)]
        b = sess.run(None, {"input": x.numpy()})
        dmax = max(dmax, max(float(np.abs(u - v).max()) for u, v in zip(a, b)))
        agree += int(a[0].argmax() == b[0].argmax())
    rep = {"onnx": str(OUT), "size_MB": round(OUT.stat().st_size / 1e6, 1), "n": len(paths), "max_abs_diff": dmax,
           "decision_agreement": f"{agree}/{len(paths)}"}
    (HERE / "export_demo_onnx.json").write_text(json.dumps(rep, indent=1)); print(rep)


if __name__ == "__main__":
    main()
