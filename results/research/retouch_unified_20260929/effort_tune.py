"""Effort's parameter-efficient tuning (Yan et al., ICML 2025), copied from the authors' released code
external_baselines/Effort/DeepfakeBench/training/detectors/effort_detector.py (SVDResidualLinear, apply_svd_residual_to_self_attn,
replace_with_svd_residual), so that the exposure rule of PRE_DECLARED Addendum 25 can be applied to Effort's own tuning scheme
inside our training pipeline (plug-in test, Addendum 26). Each nn.Linear of every self-attention block is split by SVD into a
frozen main part (top r = 1023 singular components) and a trainable residual (the remaining components); the released
detector trains with plain cross-entropy (its regularisers are defined but not used in get_losses), and so do we.
Only the forward path is reproduced here; the regulariser methods are omitted.
"""
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

R_DEFAULT = 1024 - 1


class SVDResidualLinear(nn.Module):
    def __init__(self, in_features, out_features, r, bias=True, init_weight=None):
        super().__init__()
        self.in_features, self.out_features, self.r = in_features, out_features, r
        self.weight_main = nn.Parameter(torch.Tensor(out_features, in_features), requires_grad=False)
        if init_weight is not None:
            self.weight_main.data.copy_(init_weight)
        else:
            nn.init.kaiming_uniform_(self.weight_main, a=math.sqrt(5))
        if bias:
            self.bias = nn.Parameter(torch.Tensor(out_features)); nn.init.zeros_(self.bias)
        else:
            self.register_parameter("bias", None)
        self.S_residual = None

    def forward(self, x):
        if hasattr(self, "U_residual") and hasattr(self, "V_residual") and self.S_residual is not None:
            weight = self.weight_main + self.U_residual @ torch.diag(self.S_residual) @ self.V_residual
        else:
            weight = self.weight_main
        return F.linear(x, weight.to(x.dtype), None if self.bias is None else self.bias.to(x.dtype))


def replace_with_svd_residual(module, r):
    new = SVDResidualLinear(module.in_features, module.out_features, r, bias=module.bias is not None, init_weight=module.weight.data.clone())
    if module.bias is not None:
        new.bias.data.copy_(module.bias.data)
    U, S, Vh = torch.linalg.svd(module.weight.data.float(), full_matrices=False); r = min(r, len(S))
    new.weight_main.data.copy_(U[:, :r] @ torch.diag(S[:r]) @ Vh[:r, :])
    if len(S) - r > 0:
        new.S_residual = nn.Parameter(S[r:].clone()); new.U_residual = nn.Parameter(U[:, r:].clone()); new.V_residual = nn.Parameter(Vh[r:, :].clone())
        new.S_r = nn.Parameter(S[:r].clone(), requires_grad=False); new.U_r = nn.Parameter(U[:, :r].clone(), requires_grad=False); new.V_r = nn.Parameter(Vh[:r, :].clone(), requires_grad=False)
    return new


def apply_svd_residual_to_self_attn(model, r=R_DEFAULT):
    for name, module in model.named_children():
        if "self_attn" in name:
            for sub_name, sub in list(module.named_modules()):
                if isinstance(sub, nn.Linear):
                    parent = module
                    for mn in sub_name.split(".")[:-1]:
                        parent = getattr(parent, mn)
                    setattr(parent, sub_name.split(".")[-1], replace_with_svd_residual(sub, r))
        else:
            apply_svd_residual_to_self_attn(module, r)
    for pn, p in model.named_parameters():
        p.requires_grad = any(x in pn for x in ("S_residual", "U_residual", "V_residual"))
    return model
