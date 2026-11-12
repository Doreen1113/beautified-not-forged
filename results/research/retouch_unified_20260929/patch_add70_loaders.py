"""Addendum 70: let the existing evaluation code load the browser W model (ru_ru7we_effb4_s<seed>.pth, RUNet3 layout with a
2-output cls = factorised forged / beautified logits). Backward compatible: a checkpoint with a 3-output cls behaves exactly as
before. Exact string replacement, abort if an anchor is missing or repeated, atomic write (temp + os.replace), idempotent.
python patch_add70_loaders.py"""
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
EDITS = [
    (HERE / "train_ru3.py",
     """    def forward(self, x):
        fm = self.backbone.forward_features(x); f = fm.mean((2, 3))
        out = (self.cls(f), self.pres(f), self.q(f))
        return out + (self.ev(fm),) if self.head else out
""",
     """    def forward(self, x):
        fm = self.backbone.forward_features(x); f = fm.mean((2, 3)); c = self.cls(f)
        if c.shape[1] == 2:   # Addendum 70: factorised forged / beautified logits -> log of the joint (real, fake, filter)
            z = c.float(); nf, nb = F.logsigmoid(-z[:, 0]), F.logsigmoid(-z[:, 1])
            c = torch.stack([nf + nb, F.logsigmoid(z[:, 0]), nf + F.logsigmoid(z[:, 1])], 1)
        out = (c, self.pres(f), self.q(f))
        return out + (self.ev(fm),) if self.head else out

    def load_state_dict(self, sd, strict=True, **k):   # Addendum 70: a checkpoint whose cls has 2 outputs is a factorised model
        w = sd.get("cls.weight")
        if w is not None and w.shape[0] != self.cls.out_features:
            self.cls = nn.Linear(self.cls.in_features, w.shape[0]).to(self.cls.weight.device)
        return super().load_state_dict(sd, strict=strict, **k)
"""),
    (HERE / "eval_ru.py", 'elif a.arm in ("ru3", "ru3e", "ru4e"):', 'elif a.arm in ("ru3", "ru3e", "ru4e", "ru7we"):'),
    (HERE / "eval_vendor_val.py", 'elif a.arm in ("ru3", "ru3e", "ru4e"):', 'elif a.arm in ("ru3", "ru3e", "ru4e", "ru7we"):'),
    (HERE.parent / "cgd_20260927/eval_cgd_explain.py", 'if a.arm in ("RU3E", "RU3E-repvit", "RU4E", "RU4E-repvit"):',
     'if a.arm in ("RU3E", "RU3E-repvit", "RU4E", "RU4E-repvit", "RU7WE"):'),
    (HERE.parent / "celebdfb_v2_20260927/score_cdfb.py",
     'OURS["RU4e-effb4"] = (RU / "ru_ru4e_effb4_s20260929.pth", "runet3:effb4:1", 380, 3)\n',
     'OURS["RU4e-effb4"] = (RU / "ru_ru4e_effb4_s20260929.pth", "runet3:effb4:1", 380, 3)\n'
     'OURS["RU7We-effb4"] = (RU / "ru_ru7we_effb4_s20260929.pth", "runet3:effb4:1", 380, 3)   # Addendum 70 (factorised cls, train_ru3.RUNet3 loads it)\n'),
]
for p, old, new in EDITS:
    t = p.read_text(encoding="utf-8")
    if new in t:
        print("already patched", p.name); continue
    assert t.count(old) == 1, (p, t.count(old))
    tmp = p.with_suffix(p.suffix + ".tmp"); tmp.write_text(t.replace(old, new), encoding="utf-8"); os.replace(tmp, p); print("patched", p.name)
