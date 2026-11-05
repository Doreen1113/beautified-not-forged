"""Single-step overfitting probe (PRE_DECLARED Addendum 16), FF++ val frames only.

For each checkpoint: accuracy of the forged decision (P(forged) > 0.5) and mean P(forged) on genuine and forged FF++ val
frames under no edit, a random draw of the beautification operator, the 1-step search used in training and a 10-step
search (step 0.3). A model whose 10-step accuracy is far below its 1-step accuracy has overfitted to the single step.
python adv_probe.py <tag> ...  -> adv_probe.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
import adv_beauty as AB
from leak_probe import build_a, load
from train_ru3 import to_t2

N = 400


def main():
    A = build_a(); rng = np.random.default_rng(3)
    real = [x for x in A if x[1] == "real"]; fake = [x for x in A if x[1] == "fake"]
    pick = [real[i] for i in rng.choice(len(real), N // 2, False)] + [fake[i] for i in rng.choice(len(fake), N // 2, False)]
    y = torch.tensor([0.0] * (N // 2) + [1.0] * (N // 2)).cuda()
    f = HERE / "adv_probe.json"; out = json.loads(f.read_text()) if f.is_file() else {}
    for tag in sys.argv[1:]:
        model, size, norm = load(tag); fn = lambda v: model(v)[4][:, 0]
        X = torch.stack([to_t2(np.array(Image.open(p[0]).convert("RGB")), size, False, norm) for p in pick]).cuda()
        res = {}
        for name, kw in (("none", None), ("random", {"random_only": True}), ("1-step", {"step": 1.0}), ("10-step", {"step": 0.3, "steps": 10}), ("worst-of-4", {"k": 4})):
            P = []
            for i in range(0, N, 40):
                torch.manual_seed(100 + i); x = X[i:i + 40]; t = y[i:i + 40]
                xa = x if kw is None else AB.worst_case(fn, x, t, **kw)
                with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
                    P.append(torch.sigmoid(fn(xa).float()).cpu().numpy())
            P = np.concatenate(P); g, k = P[:N // 2], P[N // 2:]
            res[name] = {"genuine_acc": round(100 * float((g <= 0.5).mean()), 1), "forged_acc": round(100 * float((k > 0.5).mean()), 1),
                         "genuine_p": round(float(g.mean()), 3), "forged_p": round(float(k.mean()), 3)}
        out[tag] = res; f.write_text(json.dumps(out, indent=1)); print(tag, json.dumps(res), flush=True)
        del model; torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
