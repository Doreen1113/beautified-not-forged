"""Estimate-and-invert photometric canonicalisation (PRE_DECLARED Addendum 20).

A small network E looks at a face crop and predicts the parameters v of the invertible part of the beautification operator
(tone curve, colour matrix, saturation, contrast, luminance and tint field; smoothing and grain are not invertible and are
left alone). The canonical image is B^{-1}(x; E(x)) with the exact algebraic inverse (adv_beauty.apply_inverse): E is trained
to recover u for random edits (parameter loss) so that B^{-1}(B(x0; u); E(B(x0; u))) ~ x0 (pixel loss), and to predict the
identity for untreated frames. The detector then reads the
canonical image. Global photometric changes are removed before detection; local inconsistencies (forgery evidence) survive a
global inverse; non-invertible edits are left to the detector.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision

import adv_beauty as AB

OFF = -6.0   # sigmoid(-6 - 1) ~ 0: smoothing and grain disabled in the canonicaliser
SHAPES = {"gamma": (3, 1, 1), "gain": (3, 1, 1), "lift": (3, 1, 1), "M": (3, 3), "sat": (1, 1, 1), "con": (1, 1, 1), "field": (1, 4, 4), "tint": (3, 4, 4)}


def ident(name):
    """Unconstrained value at which the component is the identity, under the current bounds."""
    bd = AB.bounds(); lg = lambda s: float(torch.logit(torch.tensor(float(s))))
    return {"gamma": lg((1 - bd["gam0"]) / bd["gam"]), "gain": lg((1 - bd["gain0"]) / bd["gain"]), "lift": 0.0, "M": 0.0, "sat": lg(1 / bd["sat"]),
            "con": lg((1 - bd["con0"]) / bd["con"]), "field": lg((1 - bd["fld0"]) / bd["fld"]), "tint": lg((1 - bd["tint0"]) / bd["tint"])}[name]


class Canon(nn.Module):
    def __init__(self, res=112):
        super().__init__()
        self.res = res; self.n = sum(int(torch.tensor(s).prod()) for s in SHAPES.values())
        bb = torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1); bb.fc = nn.Identity(); self.bb = bb
        self.head = nn.Linear(512, self.n); nn.init.zeros_(self.head.weight); nn.init.zeros_(self.head.bias)   # starts at the identity edit
        self.register_buffer("mean", torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)); self.register_buffer("std", torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1))

    def params(self, x01):
        """x01: batch in [0, 1]. Returns the operator parameters (unconstrained) predicted for each image, identity + offset."""
        z = F.interpolate(x01, size=(self.res, self.res), mode="bilinear", align_corners=False)
        o = self.head(self.bb((z - self.mean) / self.std)); u = {}; k = 0
        for name, shp in SHAPES.items():
            m = int(torch.tensor(shp).prod()); u[name] = ident(name) + o[:, k:k + m].view(x01.shape[0], *shp); k += m
        u["smooth"] = torch.full((x01.shape[0], 1, 1, 1), OFF, device=x01.device); u["grain"] = torch.full((x01.shape[0], 1, 1, 1), OFF, device=x01.device)
        return u

    def forward(self, x_norm):
        """CLIP-normalised batch in, CLIP-normalised canonical batch out."""
        return AB.renorm(self.canon01(AB.denorm(x_norm.float()).clamp(0, 1))).to(x_norm.dtype)

    def canon01(self, x01, return_params=False):
        """Predict the forward edit under the wide bounds and undo it exactly (adv_beauty.apply_inverse)."""
        prev = (AB.WIDE, AB.INVERSE); AB.WIDE, AB.INVERSE = True, False
        try:
            u = self.params(x01); y = AB.apply_inverse(x01, u)
            return (y, u) if return_params else y
        finally:
            AB.WIDE, AB.INVERSE = prev
