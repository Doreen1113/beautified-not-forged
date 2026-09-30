"""
AIGC & Filter Detection Pipeline — 主入口
==========================================
Usage:
    # 單張圖片
    python pipeline.py --image path/to/face.jpg

    # 整個資料夾
    python pipeline.py --folder path/to/images/ --save_heatmap

    # 指定輸出目錄
    python pipeline.py --folder path/to/images/ --output_dir results/pipeline_out/

Output:
    - 每張圖的 JSON（prediction / confidence / artifact_type / suspicious_region / explanation）
    - summary.csv（整批結果摘要）
    - Grad-CAM heatmap（--save_heatmap 時）
"""

import argparse
import io
import json
import os
import sys
import csv
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as tv_models
from torchvision import transforms
from PIL import Image
import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decision_rule import (decide as _decide,
                           MANIP_THRESHOLD as _MANIP_THRESHOLD,
                           FILTER_THRESHOLD as _FILTER_THRESHOLD)

# ──────────────────────────────────────────────
# 設定
# ──────────────────────────────────────────────
BASE                  = r"C:\My_Project\AIGC"
# v8.11 hierarchical classifier (2026-08-02 拍板，Phase 1最終候選，取代v8.8單一3-class模型):
#   Layer1: real vs manipulated (fake ∪ filter) 二分類
#   Layer2: 僅在Layer1判為manipulated時啟動，fake vs filter 二分類
# 對外輸出schema維持與v8.8相容（同樣是real/fake/filter三選一 + class_probs），
# 差別只在內部推論改成兩階段串接。舊的v8.8單模型權重仍保留於磁碟供對照，不再是預設路徑。
# 2026-08-10：Layer1 更新為 v811d（round4 hard-neg fine-tune，全部6項gate對照Layer1c
# 無退步、Shadow real recall +1.4pp、fake+filter端到端誤判4.06%→3.71%），完整對照見
# TODO.md「Layer 2（fake vs filter）辨識瓶頸」章節。Layer1c保留在磁碟供對照，不再是預設路徑。
# 2026-08-20：Layer1 更新為 v8.17（P1-R9 Self-Blended Images pilot 候選，
# shufflenet_v2_layer1_v817sbi.pth，SHA256 e3057270...），為v8.11凍結後第一個
# 正式核准並套用的production變更。核准依據：Freeze-Gate A全過（True Test filter
# recall 91.97%仍≥90%門檻，唯一退步項）、Freeze-Gate C穩健性20種擾動條件下
# 同一trade-off無放大、fp32 TFLite合併20.913MB/14.22ms未退步、threshold-only
# frontier 9/9勝出、雙陷阱檢查皆過。完整證據見
# docs/team/change_proposals/20260820_p1_r9_sbi_layer1_sbiaug.md，
# 研究過程見 results/research/p1_r9_sbi_pilot_20260819/。
# v811d 保留在磁碟供對照/rollback，不再是預設路徑。
LAYER1_WEIGHTS_PATH   = os.path.join(BASE, "shufflenet_v2_layer1_v817sbi.pth")
# 2026-09-12 v8.19-rr APPROVED and APPLIED (user-approved 2026-09-12 on the
# recommendation relayed from the group meeting): Layer2 -> render_rand_20260911
# seed 3, i.e. production Layer2 v811 fine-tuned with class-independent rendering
# randomisation (crop jitter -> 96-160px resample -> JPEG q50-95 -> back to 224,
# p=0.5, production split, NO new images). SHA256 005c364a...; byte-identical copy
# of checkpoints/research/render_rand_20260911/shufflenet_v2_layer2_L2RR_s20260913.pth.
# Ships WITH decision_rule.FILTER_THRESHOLD = 0.72 (pre-declared); the weights and
# the threshold are one unit -- do not wire one without the other.
# BUYS: real commercial filters, zero-shot -- B-LFW 0.45% -> 13.30% filter,
#   FairBeauty 12.9% -> 33.6%; AIGuard/unseen AUROC 0.841 -> 0.892; Shadow 12.2 -> 17.6.
# COSTS: P3 filtered-real -> fake 0.0% -> 1.2% (3/249), fake+filter stress
#   2.80% -> 3.23%, True Test filter 91.97 -> 90.76, Alibaba 97.71 -> 96.80,
#   FF++ zero-shot frame AUROC 0.575 -> 0.550. Both headline costs fall INSIDE the
#   incumbent's own 95% CI (stress CI [1.92, 3.76]; the old "0/249" has a
#   Clopper-Pearson upper bound of 1.47%), while the gains are far outside noise.
#   Mechanism replicated on three seeds. All six pre-declared hard gates pass.
# Proposal/approval: docs/team/change_proposals/20260911_render_rand_layer2.md
# Evidence: results/research/render_rand_20260911/FINDINGS.md (§7 = this seed)
# ROLLBACK: set LAYER2_WEIGHTS_PATH back to shufflenet_v2_layer2_v811.pth AND
#   decision_rule.FILTER_THRESHOLD back to 0.5 (v8.17 weights untouched on disk,
#   SHA256 8470ad52...); backups pipeline_pre_rr_20260912.py.bak /
#   decision_rule_pre_rr_20260912.py.bak.
LAYER2_WEIGHTS_PATH   = os.path.join(BASE, "shufflenet_v2_layer2_v819rr.pth")
# 2026-08-22: was hardcoded "v8.11" in two output dicts below despite Layer1
# having moved to v8.17 on 2026-08-20 (TODO.md C1.9.12). Single source of
# truth now -- bump this whenever LAYER1/LAYER2/ARTIFACT_WEIGHTS_PATH changes
# production version, not the two dict literals directly.
MODEL_VERSION = "v8.19-rr"
# 2026-08-22 (P2-CompleteFix, approved): switched v3 -> v6. v6 fixes the root
# cause v4 got wrong -- v4 tried to fix whitening by oversampling its training
# data 64% relative to the other 3 classes, which broke smoothing/
# face_reshaping (see the 2026-08-21 revert history below, kept for context).
# v6 instead fixes the actual data-construction bugs: (a) filter_data/lfw_*
# folders existed for whitening/face_reshaping/eye_enlarging but were never
# cleaned/included due to a class-name matching bug (fixed, generic
# normalize_class()); (b) smoothing had NO second base-image source at all --
# generated one (filters/generate_lfw_smoothing.py, reusing the existing
# apply_smoothing algorithm, 4,032 images). End-to-end validation (True Test
# full population + Alibaba clean n=500/type, via pipeline.py's actual
# hierarchical_predict()->classify_artifact() chain):
#   True Test: smoothing 100.0% (flat), face_reshaping 95.2% (flat),
#              whitening 50.0%->90.3%, eye_enlarging 4.8%->72.6%
#   Alibaba (cross-algorithm): all 4 types statistically flat vs v3 --
#              NOT improved, but critically NOT regressed either.
# Known remaining limitation: cross-algorithm generalization itself is NOT
# solved by this fix. A blind training-time augmentation attempt (never
# looked at Alibaba images) to improve it was tried and FAILED -- made
# Alibaba significantly worse by amplifying the eye_enlarging attractor --
# and was discarded, not applied here. See
# results/research/p2_artifact_completefix_20260821/COMPLETEFIX_FINDINGS.md
# and docs/team/change_proposals/20260821_p2_artifact_completefix_v6.md.
# v3/v4/v5 all remain on disk for rollback (one-line change back).
#
# --- 2026-08-21 revert history (v4, kept for context) ---
# REVERTED to v3 same-day after urgent diagnosis
# (results/research/p2_urgent_v4_diagnosis_20260821/DIAGNOSIS.md) found v4
# (whitening-diversity fine-tune, seed=42, briefly in production) causes a
# severe, previously-undetected end-to-end regression on smoothing (True
# Test 100.0%->52.4%) and face_reshaping (95.2%->22.6%), root-caused to
# systematic misclassification as "whitening". The isolated regression check
# in results/research/p2_r3_whitening_validation_20260821/ missed this
# because its 400-image reserve was drawn from filter_data/{cls} (the
# training source pool itself), not from True Test / Alibaba (the
# population classify_artifact() actually serves in production) -- a
# population-choice error (Known trap #5), not a power/sample-size error.
ARTIFACT_WEIGHTS_PATH = os.path.join(BASE, "artifact_classifier_v6.pth")
# 2026-08-31 (p2_evidence_wire_20260831, user-delegated authority recorded in
# docs/MASTER_PLAN_20260826.md): Layer2 patch evidence head, wired into the
# EXPLANATION layer for the FILTER class only. Pre-wiring conditions met:
# oracle-relative faithfulness 6/6 (registry P2A1-EVIDENCEHEAD-R2-20260828)
# and SBI mask localization PASS (P2-SBIMASK1: IoU@10% 0.4485 vs centre-prior
# 0.4009, paired CI [+0.0358, +0.0590]). OPTIONAL and fail-safe: if this file
# is missing or the head errors, the pipeline behaves exactly as before
# (legacy ARTIFACT_REGION_MAP regions, no appended sentence). The decision
# path (prediction/confidence/class_probs/artifact_types) never touches this.
EVIDENCE_HEAD_WEIGHTS_PATH = os.path.join(
    BASE, "checkpoints", "research", "p2a1_evidence_head_r2_20260828",
    "evidence_head_r2_last.pth")
CLASSES          = ["real", "fake", "filter"]
# 2026-08-11: pipeline.py previously had NO face-detection gate at all -- any
# input (a landscape photo, a cat, a blank image) was forced through the
# real/fake/filter classifier and given a confident-looking answer. Every
# other face-processing script in this project (stress_test_v811_pipeline.py,
# generate_vggface2_filters.py, etc.) already gates on MediaPipe face
# detection before doing anything else; production inference did not. Added
# below using the exact same MediaPipe FaceLandmarker pattern already used
# project-wide, not a new detector.
FACE_LANDMARKER_PATH = os.path.join(BASE, "face_landmarker.task")
# ImageFolder alphabetical order → matches training class index
ARTIFACT_CLASSES = ["eye_enlarging", "face_reshaping", "smoothing", "whitening"]
# Map classifier output to artifact tag used in templates
ARTIFACT_TAG_MAP = {
    "eye_enlarging":  "eye_enlarging",
    "face_reshaping": "face_reshaping",
    "smoothing":      "smoothing",
    "whitening":      "whitening",
}
IMG_EXTS = {".jpg", ".jpeg", ".png", ".jfif", ".bmp", ".webp"}

# Rule-based: artifact_type -> suspicious_regions for filter class.
# eye_enlarging is the ONLY filter type with region-level, GT-backed
# localization support (see docs/phase2_story.md, docs/Dataset 清單.md
# 2026-08-02 entry): visualizing LAB-diff heatmaps against the self-built
# filter pipeline's own before/after pairs showed whitening/smoothing
# genuinely affect nearly the entire face oval (the skin mask used at
# generation time IS an ellipse spanning most of the face), and
# face_reshaping's fixed 60px warp radius saturates most regions at dataset
# scale (unlike eye_enlarging's self-scaling radius). Listing specific
# sub-regions for these three would misrepresent them as more localized than
# they actually are, so they map to a single whole-face marker instead.
# 2026-08-21 (P2-R2, approved): empirically-fitted sub-regions, derived from
# the per-type paired ground-truth difference masks (const_prior_maps.npy,
# results/research/p2_r1_tierA_localization_20260821 + p2_r2_empirical_
# region_map_20260821), NOT hand-drawn anatomy. Held-out IoU vs the old
# hand-drawn boxes: +0.19 (aligned-crop domain), +0.14 (VGGFace2 wild
# domain), all 15 (stratum x type) cells significant. Kept as a table
# separate from FACE_REGIONS so Grad-CAM's top_activated_regions() and any
# future region-scoring tooling keep using the original anatomical boxes
# unchanged. See docs/team/change_proposals/20260821_p2_r2_empirical_region_map.md.
EMPIRICAL_FILTER_REGIONS = {
    "emp_smoothing_lower":  (124, 187,  82, 144),
    "emp_smoothing_upper":  ( 86, 120,  65, 159),
    "emp_whitening_center": ( 71, 204,  58, 164),
    "emp_eye_left":         ( 84, 121,  63,  99),
    "emp_eye_right":        ( 84, 121, 118, 161),
    "emp_reshape_left":     ( 80, 159,  13,  96),
    "emp_reshape_right":    ( 81, 157, 130, 211),
}

ARTIFACT_REGION_MAP = {
    "eye_enlarging":  ["emp_eye_left", "emp_eye_right"],
    "face_reshaping": ["emp_reshape_left", "emp_reshape_right"],
    "smoothing":      ["emp_smoothing_upper", "emp_smoothing_lower"],
    "whitening":      ["emp_whitening_center"],
    "unknown_filter": [],
}

# ──────────────────────────────────────────────
# Face-presence gate (2026-08-11, new)
# ──────────────────────────────────────────────
_face_landmarker = None


def _get_face_landmarker():
    """Lazy singleton, same MediaPipe FaceLandmarker pattern used project-wide
    (e.g. stress_test_v811_pipeline.py, generate_vggface2_filters.py)."""
    global _face_landmarker
    if _face_landmarker is None:
        with open(FACE_LANDMARKER_PATH, "rb") as f:
            model_data = f.read()
        opts = mp_vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_buffer=model_data),
            num_faces=1)
        _face_landmarker = mp_vision.FaceLandmarker.create_from_options(opts)
    return _face_landmarker


def _detect_landmarks(pil_img):
    """Returns the 468 FaceMesh landmarks of the largest detected face, or None.
    2026-08-28 (XAI-2): factored out of has_face() so the evidence-driven
    explanation can reuse the SAME detection call/model rather than adding a
    second detector. has_face() behaviour is unchanged."""
    rgb = np.array(pil_img.convert("RGB"))
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    res = _get_face_landmarker().detect(mp_img)
    if not res.face_landmarks:
        return None
    return res.face_landmarks[0]


def has_face(pil_img):
    """True if MediaPipe detects a face in the image. Every real/fake/filter
    classification this pipeline makes is only meaningful for a face crop;
    previously there was no check at all, so a non-face input (landscape,
    object, blank image) silently got a confident real/fake/filter verdict
    anyway. See TODO.md / non-face gate discussion, 2026-08-11."""
    return _detect_landmarks(pil_img) is not None


# ──────────────────────────────────────────────
# Preprocessing
# ──────────────────────────────────────────────
def preprocess_jpeg(img_pil, quality=85):
    """Re-encode at fixed JPEG quality — 統一壓縮程度，改善 domain gap。"""
    buf = io.BytesIO()
    img_pil.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    return Image.open(buf).convert("RGB")

# ──────────────────────────────────────────────
# Model
# ──────────────────────────────────────────────
class FFTBranch(nn.Module):
    def __init__(self, out_dim=256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(),
            nn.MaxPool2d(4),
            nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(),
            nn.MaxPool2d(2),
            nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(),
            nn.AdaptiveAvgPool2d(4),
            nn.Flatten(),
            nn.Linear(128 * 4 * 4, out_dim), nn.ReLU(),
        )

    def forward(self, x):
        fft = torch.fft.fft2(x, norm='ortho')
        fft = torch.fft.fftshift(fft, dim=(-2, -1))
        mag = torch.log(torch.abs(fft) + 1e-8)
        return self.net(mag)


class DualBranchModel(nn.Module):
    def __init__(self, num_classes=3):
        super().__init__()
        backbone = tv_models.shufflenet_v2_x1_0(
            weights=tv_models.ShuffleNet_V2_X1_0_Weights.DEFAULT)
        backbone.fc = nn.Identity()
        self.spatial_branch = backbone
        self.fft_branch     = FFTBranch(out_dim=256)
        self.classifier     = nn.Sequential(
            nn.Linear(1024 + 256, 512), nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(512, num_classes),
        )

    def forward(self, x):
        spatial = self.spatial_branch(x)
        freq    = self.fft_branch(x)
        return self.classifier(torch.cat([spatial, freq], dim=1))

    def extract_features(self, x):
        """Return 1280-dim features (before classifier)."""
        with torch.no_grad():
            spatial = self.spatial_branch(x)
            freq    = self.fft_branch(x)
        return torch.cat([spatial, freq], dim=1)


def hierarchical_predict(input_tensor, l1_model, l2_model, requires_grad=False):
    """Runs the v8.11 Layer1(real vs manipulated) -> Layer2(fake vs filter)
    chain and returns a result dict shaped to match the old 3-class model's
    output exactly (prediction/confidence/class_probs), so downstream code
    (artifact classification, region head, explanation templates) doesn't
    need to know the classifier is now two-stage.

    class_probs are a genuine composite distribution, not just the winning
    layer's raw softmax: P(real)=L1.P(real); P(fake)=L1.P(manip)*L2.P(fake);
    P(filter)=L1.P(manip)*L2.P(filter) -- these sum to 1 and are directly
    comparable to the old single-model output.
    """
    ctx = torch.enable_grad() if requires_grad else torch.no_grad()
    with ctx:
        l1_logits = l1_model(input_tensor)
        l1_probs = torch.softmax(l1_logits, dim=1)[0]
        p_real, p_manip = float(l1_probs[0].detach()), float(l1_probs[1].detach())

        l2_logits = l2_model(input_tensor)
        l2_probs = torch.softmax(l2_logits, dim=1)[0]
        p_fake_given_manip, p_filter_given_manip = float(l2_probs[0].detach()), float(l2_probs[1].detach())

    p_fake = p_manip * p_fake_given_manip
    p_filter = p_manip * p_filter_given_manip
    class_probs_arr = [p_real, p_fake, p_filter]

    # 2026-08-26 (DECISION-RULE-UNIFY-20260826): explicit Layer1 gate via the
    # shared decision_rule.decide() at the published operating point (0.5),
    # replacing composite argmax (implicit image-dependent gate 0.51-0.67) so
    # the product decides exactly as every published gate number was read.
    # Note confidence = composite prob of the chosen class, which under an
    # explicit gate can be below max(class_probs) for near-boundary images.
    # 2026-09-12 (v8.19-rr): Layer2 now has an explicit pre-declared gate too
    # (filter iff p_filter|manip > 0.72). Passed explicitly rather than relying on
    # the module default so this call site states the full operating point.
    prediction = _decide(p_real, p_manip, p_fake_given_manip, p_filter_given_manip,
                         _MANIP_THRESHOLD, _FILTER_THRESHOLD)
    pred_idx = CLASSES.index(prediction)
    confidence = class_probs_arr[pred_idx]

    # which layer's decision actually determined the final label -- used to
    # pick which model/class-index Grad-CAM++ should explain
    if prediction == "real":
        gradcam_layer, gradcam_class_idx = "l1", 0
    else:
        gradcam_layer = "l2"
        gradcam_class_idx = 0 if prediction == "fake" else 1

    return {
        "prediction": prediction,
        "confidence": confidence,
        "class_probs": {c: p for c, p in zip(CLASSES, class_probs_arr)},
        "gradcam_layer": gradcam_layer,
        "gradcam_class_idx": gradcam_class_idx,
    }

# ──────────────────────────────────────────────
# Grad-CAM++
# ──────────────────────────────────────────────
class GradCAMPlusPlus:
    def __init__(self, model, target_layer):
        self.model = model
        self._act  = None
        self._grad = None
        target_layer.register_forward_hook(
            lambda m, i, o: setattr(self, '_act', o.detach()))
        target_layer.register_full_backward_hook(
            lambda m, gi, go: setattr(self, '_grad', go[0].detach()))

    def generate(self, inp, class_idx):
        self.model.zero_grad()
        out = self.model(inp)
        out[0, class_idx].backward()

        features  = self._act
        gradients = self._grad

        grads_power_2 = gradients ** 2
        grads_power_3 = gradients ** 3
        sum_features  = torch.sum(features, dim=[2, 3], keepdim=True)

        alpha_denom = 2 * grads_power_2 + sum_features * grads_power_3
        alpha_denom = torch.where(alpha_denom != 0, alpha_denom, torch.ones_like(alpha_denom))
        alpha   = grads_power_2 / alpha_denom
        weights = torch.sum(alpha * torch.relu(gradients), dim=[2, 3], keepdim=True)

        cam = torch.relu((weights * features).sum(dim=1)).squeeze()
        cam = cam.cpu().numpy()
        cam = cv2.resize(cam, (224, 224))
        if cam.max() > cam.min():
            cam = (cam - cam.min()) / (cam.max() - cam.min())
        return cam

# ──────────────────────────────────────────────
# Region analysis
# ──────────────────────────────────────────────
FACE_REGIONS = {
    "forehead":    (10,  65,  40, 184),
    "left_eye":    (60, 100,  30, 110),
    "right_eye":   (60, 100, 114, 194),
    "nose":        (90, 150,  75, 149),
    "left_cheek":  (100, 175,  15,  90),
    "right_cheek": (100, 175, 134, 209),
    "mouth":       (148, 185,  65, 159),
    "jaw":         (170, 214,  40, 184),
}

REGION_DISPLAY = {
    "forehead": "forehead", "left_eye": "left eye area",
    "right_eye": "right eye area", "nose": "nose area",
    "left_cheek": "left cheek", "right_cheek": "right cheek",
    "mouth": "mouth area", "jaw": "jaw area",
    "face": "the face",  # whole-face marker, see ARTIFACT_REGION_MAP note
}

# 2026-08-21 (P2-R2, approved): display strings for EMPIRICAL_FILTER_REGIONS.
REGION_DISPLAY.update({
    "emp_smoothing_lower":  "lower face and jaw",
    "emp_smoothing_upper":  "eye and nose-bridge area",
    "emp_whitening_center": "central face",
    "emp_eye_left":         "left eye area",
    "emp_eye_right":        "right eye area",
    "emp_reshape_left":     "left cheek and jaw",
    "emp_reshape_right":    "right cheek and jaw",
})

def top_activated_regions(cam, top_k=2):
    scores = {name: float(cam[y0:y1, x0:x1].mean())
              for name, (y0, y1, x0, x1) in FACE_REGIONS.items()}
    return [r for r, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]]

# ──────────────────────────────────────────────
# Artifact classifier (4-class, runs only when prediction == "filter")
# ──────────────────────────────────────────────
def build_artifact_model():
    model = tv_models.shufflenet_v2_x1_0()
    model.fc = nn.Linear(model.fc.in_features, len(ARTIFACT_CLASSES))
    return model

transform_artifact = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3),
])

# 2026-08-11: `classify_artifact` is a closed-set 4-way softmax classifier --
# it has no "none of the above" output, so a filter type we never trained on
# (or any other out-of-distribution input reaching this path) was previously
# always forced into one of the 4 known classes, with a confidence number
# that looks legitimate but is meaningless for OOD input. This threshold adds
# the missing open-set behavior (TODO.md C2章節): below it, report
# "unknown_filter" instead of guessing.
# NOTE: 0.6 is a reasoned default (comfortably above the 0.25 4-class random
# baseline, not so strict it rejects confident correct calls), NOT a
# calibrated value -- there is no held-out "genuinely novel filter type"
# dataset yet to calibrate against (see TODO.md C2 "Unseen filter/fake
# 資料集上的open-set評估", still open). Revisit once that eval exists.
ARTIFACT_UNKNOWN_THRESHOLD = 0.6


def classify_artifact(pil_img, artifact_model, device):
    """Return (artifact_tag, confidence) using the trained classifier.
    Returns ("unknown_filter", confidence) if the top class's confidence is
    below ARTIFACT_UNKNOWN_THRESHOLD, rather than forcing a guess."""
    tensor = transform_artifact(pil_img).unsqueeze(0).to(device)
    with torch.no_grad():
        probs = torch.softmax(artifact_model(tensor), dim=1)[0]
    idx  = int(probs.argmax())
    conf = float(probs[idx])
    if conf < ARTIFACT_UNKNOWN_THRESHOLD:
        return "unknown_filter", conf
    cls  = ARTIFACT_CLASSES[idx]
    tag  = ARTIFACT_TAG_MAP[cls]
    return tag, conf



# ──────────────────────────────────────────────
# Evidence head (2026-08-31, p2_evidence_wire_20260831)
# ──────────────────────────────────────────────
# PatchEvidenceHeadV2 is copied VERBATIM from
# results/research/p2a1_evidence_head_r2_20260828/train_evidence_head_r2.py
# (the trained checkpoint's defining module), with the single mechanical
# substitution `pipeline.FFTBranch` -> `FFTBranch` (same class, this module).
# Copied rather than imported because that training script itself does
# `import pipeline` at module top (circular import).
class PatchEvidenceHeadV2(nn.Module):
    """Round-2 architecture: spatial patch head (per-class pooling: sparse
    for fake, dense for filter) + warm-started FFT branch feeding a
    zero-initialized global logit bias."""

    def __init__(self):
        super().__init__()
        backbone = tv_models.shufflenet_v2_x1_0(weights=None)
        backbone.fc = nn.Identity()
        self.spatial_branch = backbone
        self.fft_branch = FFTBranch(out_dim=256)
        self.patch_head = nn.Sequential(
            nn.Conv2d(1024, 256, 1), nn.ReLU(inplace=True),
            nn.Conv2d(256, 2, 1),
        )
        self.fft_logit = nn.Linear(256, 2)
        nn.init.zeros_(self.fft_logit.weight)
        nn.init.zeros_(self.fft_logit.bias)

    def conv5_features(self, x):
        b = self.spatial_branch
        x = b.conv1(x)
        x = b.maxpool(x)
        x = b.stage2(x)
        x = b.stage3(x)
        x = b.stage4(x)
        x = b.conv5(x)
        return x  # (B,1024,7,7)

    def forward(self, x):
        feat = self.conv5_features(x)
        patch_logits = self.patch_head(feat)               # (B,2,7,7)
        B = patch_logits.shape[0]
        flat = patch_logits.view(B, 2, -1)                 # (B,2,49)
        fake_pool = flat[:, 0].topk(min(10, flat.shape[2]), dim=1).values.mean(1)
        filt_pool = flat[:, 1].mean(1)                     # dense
        pooled = torch.stack([fake_pool, filt_pool], dim=1)  # (B,2)
        fft_bias = self.fft_logit(self.fft_branch(x))       # (B,2), starts at 0
        image_logits = pooled + fft_bias
        return image_logits, patch_logits


# Lazy fail-safe singleton. A load failure is cached so we log once, not once
# per image, and the pipeline permanently falls back to legacy behaviour for
# the process lifetime.
_evidence_head = None
_evidence_head_failed = False


def _get_evidence_head(device):
    global _evidence_head, _evidence_head_failed
    if _evidence_head_failed:
        return None
    if _evidence_head is None:
        try:
            m = PatchEvidenceHeadV2().to(device)
            m.load_state_dict(torch.load(EVIDENCE_HEAD_WEIGHTS_PATH,
                                         map_location=device))
            m.eval()
            _evidence_head = m
            print(f"Evidence head loaded from {EVIDENCE_HEAD_WEIGHTS_PATH}")
        except Exception as e:
            _evidence_head_failed = True
            print(f"[evidence-head] unavailable ({e}) -- filter explanations "
                  f"fall back to legacy region behaviour")
            return None
    return _evidence_head


# Cell -> region assignment for the head's 7x7 patch grid, derived
# GEOMETRICALLY from the existing 224x224 FACE_REGIONS boxes (defined in the
# Region analysis section above; built lazily on first use inside
# _build_evidence_cell_map). Each 32x32 grid cell is assigned to the named region whose box
# covers its centre (fixed priority order: eyes > nose > mouth > skin boxes >
# jaw); cells covered by no box -> "skin" if the centre falls inside the
# central face area (40..190, 40..184), else "face_contour". Five output
# regions per the team proposal: eye boxes -> eyes; nose; mouth;
# forehead/cheeks -> skin; jaw/border cells -> face_contour.
# Resulting table (rows = grid y 0..6, E=eyes N=nose M=mouth S=skin
# C=face_contour), verified by results/research/p2_evidence_wire_20260831:
#   C S S S S S C
#   C S S S S S C
#   C E E S E E C
#   S S N N N S S
#   S S N N N S S
#   C C M M M C C
#   C C C C C C C
# (eyes 4 cells, nose 6, mouth 3, skin 19, face_contour 17)
_EVIDENCE_BOX_TO_REGION = {
    "left_eye": "eyes", "right_eye": "eyes", "nose": "nose", "mouth": "mouth",
    "forehead": "skin", "left_cheek": "skin", "right_cheek": "skin",
    "jaw": "face_contour",
}
_EVIDENCE_BOX_PRIORITY = ["left_eye", "right_eye", "nose", "mouth",
                          "forehead", "left_cheek", "right_cheek", "jaw"]
_EVIDENCE_CENTRAL_FACE = (40, 190, 40, 184)  # y0, y1, x0, x1
_evidence_cell_map = None  # lazy: FACE_REGIONS is defined later in this file


def _build_evidence_cell_map():
    global _evidence_cell_map
    if _evidence_cell_map is None:
        cell_map = {}
        for i in range(7):
            for j in range(7):
                cy, cx = 32 * i + 16, 32 * j + 16
                assigned = None
                for box in _EVIDENCE_BOX_PRIORITY:
                    y0, y1, x0, x1 = FACE_REGIONS[box]
                    if y0 <= cy < y1 and x0 <= cx < x1:
                        assigned = _EVIDENCE_BOX_TO_REGION[box]
                        break
                if assigned is None:
                    y0, y1, x0, x1 = _EVIDENCE_CENTRAL_FACE
                    assigned = ("skin" if (y0 <= cy < y1 and x0 <= cx < x1)
                                else "face_contour")
                cell_map[(i, j)] = assigned
        _evidence_cell_map = cell_map
    return _evidence_cell_map


# 2026-08-31 (post-wire correction, results/research/p2_evidence_wire_20260831/
# verify_filter_localization_vs_center.py): the FIRST wiring attempt scored
# each region by the MEAN of the head's sigmoid map over that region's cells.
# That is confounded by region SIZE -- nose has only 6 of 49 cells, skin has
# 19 -- so a small region needs only a local peak to win the mean, while a
# large region's peak gets diluted by averaging over cells with no signal.
# Symptom caught in the wiring's own non-regression eval: 296/298 filter
# images had "nose" as the top region regardless of artifact_type, which is
# the same shape as the Grad-CAM/centre-prior failure this project already
# caught once (eval2_xai1_rigor_20260826). A direct check (same script)
# confirmed the raw head map DOES beat a centre-Gaussian prior on IoU@10%
# against the R2 round's own filter GT masks (paired diff +0.0451, CI
# [+0.0268, +0.0637], n=100) -- so the underlying map carries real signal --
# but per type the margin is uneven (eye_enlarging +0.11, smoothing +0.03,
# whitening +0.02, face_reshaping +0.0009 -- statistically tied with the
# centre prior). The fix: score regions by PROBABILITY MASS (sum, not mean)
# relative to what a centre prior would assign the SAME region -- this
# removes the region-size confound (mass-vs-mass is size-neutral) and only
# credits a region above what pure centrality already explains.
# _CENTER_CELL_MASS is the analytic 7x7 mass table of a centre Gaussian
# (sigma=56px on the 224px frame, matching the SBI/verify-script control),
# normalized to sum 1 -- fixed, does not depend on the image.
_CENTER_CELL_MASS = np.array([
    [0.003085, 0.006863, 0.011109, 0.013087, 0.011220, 0.007000, 0.003178],
    [0.006863, 0.015267, 0.024713, 0.029113, 0.024960, 0.015573, 0.007070],
    [0.011109, 0.024713, 0.040004, 0.047127, 0.040404, 0.025209, 0.011445],
    [0.013087, 0.029113, 0.047127, 0.055516, 0.047597, 0.029697, 0.013483],
    [0.011220, 0.024960, 0.040404, 0.047597, 0.040807, 0.025461, 0.011559],
    [0.007000, 0.015573, 0.025209, 0.029697, 0.025461, 0.015886, 0.007212],
    [0.003178, 0.007070, 0.011445, 0.013483, 0.011559, 0.007212, 0.003274],
])


def evidence_regions_for_filter(input_tensor, device):
    """FILTER-class evidence regions from the patch head, scored RELATIVE TO
    a centre-prior baseline over the same 5-region grouping (see the
    2026-08-31 correction note above for why raw per-region means are
    unusable). Returns an ordered list of (region, delta_mass) for regions
    whose head probability mass exceeds the centre prior's mass for that same
    region, or None if no region clears the baseline or on any failure
    (fail-safe: caller then behaves exactly as the pre-wire pipeline -- no
    region claim rather than an uninformative one).

    Map extraction matches evidence_plugin_r2._map_for: sigmoid over
    patch_logits[0, class_idx] with class_idx=1 (filter).
    """
    try:
        head = _get_evidence_head(device)
        if head is None:
            return None
        with torch.no_grad():
            _, patch_logits = head(input_tensor)
        pm = torch.sigmoid(patch_logits[0, 1]).detach().cpu().numpy()  # (7,7)
        total = float(pm.sum())
        if not np.isfinite(total) or total <= 0:
            return None
        p_head = pm / total  # probability mass per cell, sums to 1
        cell_map = _build_evidence_cell_map()
        head_mass, center_mass = {}, {}
        for (i, j), region in cell_map.items():
            head_mass[region] = head_mass.get(region, 0.0) + float(p_head[i, j])
            center_mass[region] = center_mass.get(region, 0.0) + float(_CENTER_CELL_MASS[i, j])
        delta = {r: head_mass[r] - center_mass.get(r, 0.0) for r in head_mass}
        ordered = sorted(delta.items(), key=lambda kv: kv[1], reverse=True)
        picked = [(r, d) for r, d in ordered if d > 0]
        if not picked:
            return None  # no region beats what centrality alone would predict
        return picked
    except Exception as e:
        print(f"[evidence-head] per-image failure ({e}) -- legacy filter "
              f"explanation used for this image")
        return None


def _evidence_region_clause(evidence_regions):
    """The LEADING clause of the filter explanation when evidence regions are
    available (2026-09-01, p2_xai2_evidence_regions_20260901 / MASTER_PLAN
    P2-A1 item (b)): names the regions the patch evidence head actually
    scored above the centre-prior baseline for THIS image, with each
    region's quantified mass delta. This is the region-listing half of what
    used to be a single tail sentence (`_evidence_sentence`, pre-2026-09-01);
    it is split out so the explanation can lead with it instead of appending
    it as an afterthought after the artifact-type/measurement text. No
    numbers changed, only where they appear."""
    lst = ", ".join(f"{r} (+{d:.3f} mass over centre-prior)" for r, d in evidence_regions)
    return (f"Model evidence concentrates in: {lst} -- these regions "
            f"received more of the model's attention than a centred-face "
            f"prior alone would predict.")


def _evidence_validation_clause(evidence_regions):
    """The trailing validation/caveat clause of the filter explanation when
    evidence regions are available -- the other half of the pre-2026-09-01
    `_evidence_sentence`. Unchanged wording and numbers; kept separate from
    `_evidence_region_clause` so the region claim can lead the explanation
    while the supporting validation citation still closes it.

    2026-08-31 correction (carried over verbatim): the first version of this
    sentence cited "IoU@10% 0.449 vs centre-prior 0.401" (P2-SBIMASK1) -- that
    number validated the head's FAKE-class map on self-generated SBI images,
    not the FILTER-class regions actually being reported here. The correct
    citation is the FILTER-class map's own validation, verified against a
    centre-prior control that round 1 of this wiring had not run
    (results/research/p2_evidence_wire_20260831/verify_filter_localization_vs_center.py,
    n=100 True-Test-filter GT masks, the same masks used to build
    ARTIFACT_REGION_MAP): paired IoU@10% head 0.6103 vs centre-prior 0.5652,
    diff +0.0451 CI [+0.0268, +0.0637] (excludes 0). That check also found the
    margin is UNEVEN by type -- eye_enlarging +0.11, smoothing +0.03,
    whitening +0.02, but face_reshaping ties the centre prior (+0.0009, no
    signal) -- which is why regions here are reported only when they clear a
    centre-prior baseline (see evidence_regions_for_filter), not from a raw
    score, and why the wording below reports a validated overall property of
    the map rather than a per-type guarantee."""
    return (f" On a held-out set with independent ground-truth masks this "
            f"map beats a centre-prior baseline overall (IoU@10% 0.61 vs "
            f"0.57, paired diff significant), though the margin varies by "
            f"filter type and is not significant for face_reshaping -- this "
            f"is supporting, not conclusive, evidence.")


# ──────────────────────────────────────────────
# Image statistics for artifact discrimination
# ──────────────────────────────────────────────
def compute_skin_stats(image_np):
    """
    Compute texture variance and brightness in central skin region.
    Returns (texture_var, brightness_L).
    Note: FFT high-freq analysis was tested but JPEG preprocessing normalizes
    frequency content, making it ineffective for smoothing detection.
    """
    h, w = image_np.shape[:2]
    y0, y1 = int(h * 0.15), int(h * 0.85)
    x0, x1 = int(w * 0.15), int(w * 0.85)
    skin_rgb = image_np[y0:y1, x0:x1]

    # Texture: Laplacian variance (smoothing reduces this significantly)
    gray = cv2.cvtColor(skin_rgb, cv2.COLOR_RGB2GRAY)
    texture_var = float(cv2.Laplacian(gray.astype(np.uint8), cv2.CV_32F).var())

    # Brightness: LAB L channel (whitening raises this)
    lab = cv2.cvtColor(skin_rgb, cv2.COLOR_RGB2LAB)
    brightness_L = float(lab[:, :, 0].mean())

    return texture_var, brightness_L

# Thresholds calibrated on AIGuard real baseline:
# Real images: texture 360~1070, brightness 105~144
_SMOOTH_TEXTURE_THR  = 210   # below → smoothing (strongly smoothed: ~194)
_WHITE_BRIGHT_THR    = 147   # above → whitening (strongly whitened: ~149)

# ──────────────────────────────────────────────
# Artifact inference
# ──────────────────────────────────────────────
def infer_artifact_type(prediction, regions, image_np):
    if prediction == "real":
        return []
    if prediction == "fake":
        return []

    texture_var, brightness_L = compute_skin_stats(image_np)

    activated = set(regions)
    eye_r     = {"left_eye", "right_eye"}
    cheek_r   = {"left_cheek", "right_cheek", "jaw"}

    artifacts = []

    # Primary: image statistics for skin-processing filters
    if texture_var < _SMOOTH_TEXTURE_THR:
        artifacts.append("smoothing")
    if brightness_L > _WHITE_BRIGHT_THR:
        artifacts.append("whitening")

    # Secondary: Grad-CAM regions for geometric filters
    # Statistics take priority; Grad-CAM used as best-effort fallback
    if not artifacts:
        if activated & eye_r:
            artifacts.append("eye_enlarging")
        elif activated & cheek_r:
            artifacts.append("face_reshaping")

    return artifacts or ["unknown_filter"]

# ──────────────────────────────────────────────
# XAI-2 (2026-08-28, results/research/p2_xai2_evidence_text_20260828/):
# evidence-driven filter explanations.
#
# WHY THIS EXISTS. The previous filter templates asserted, per image, that
# "Skin texture variance is reduced", "Abnormal brightness elevation detected",
# and "Abnormal eye-to-face ratio detected". Two of those quantities were never
# computed at all, and this round measured all of them properly on the paired
# True Test set (249 filtered images vs their OWN 249 LFW base photos).
#
# The result, which is why the wording below is so cautious: the PAIRED effects
# are overwhelming, and the SINGLE-IMAGE discriminative power is near chance.
#   whitening   brightness_L : sign rate 1.000, p=7.6e-12  | single-image AUROC 0.5537
#   smoothing   texture_var  : sign rate 0.016, p=6.0e-12  | single-image AUROC 0.5521
#   eye_enlarge eye_area     : sign rate 0.952, p=1.1e-11  | single-image AUROC 0.5510
#   reshaping   face_aspect  : sign rate 0.000, p=7.6e-12  | single-image AUROC 0.7457
# Between-subject spread dwarfs the within-subject filter effect (e.g. authentic
# brightness_L sd=27.2 vs whitening's +4.04 median shift), so at inference --
# where there is no base photo to compare against -- an abnormality assertion is
# not supported for any type except, weakly, face_reshaping's face_aspect.
#
# This is the same defect, and the same fix, as P2-R7 applied to the fake class
# (p2_explanation_v2_20260823: paired sign rate 74.2%, p=3.9e-95, but AUROC
# 0.539 single-image -> assertion removed). Pre-declared rule for this round:
# AUROC >=0.75 may assert atypicality; 0.60-0.75 may report the value only;
# <0.60 the claim is REMOVED. Applied verbatim below.
#
# Reference ranges are (p05, p50, p95) over True Test real, n=250.
# Classification is NOT affected by anything in this block -- text only.
# ──────────────────────────────────────────────
_REAL_REF = {
    "texture_var":     (52.35, 137.03, 299.86),
    "brightness_L":    (75.09, 112.48, 161.32),
    "eye_width_ratio": (0.1696, 0.1850, 0.2044),
    "eye_area_ratio":  (0.0037, 0.0085, 0.0137),
    "jaw_face_ratio":  (0.7711, 0.8056, 0.8375),
    "face_aspect":     (1.1044, 1.2017, 1.3039),
}

# (measure key, human-readable name, unit format, validated single-image AUROC)
_EVIDENCE_FOR_TYPE = {
    "smoothing":      [("texture_var", "skin-texture variance (Laplacian)", "{:.1f}", 0.5521)],
    "whitening":      [("brightness_L", "mean skin lightness (LAB L*)", "{:.1f}", 0.5537)],
    "eye_enlarging":  [("eye_area_ratio", "eye-area-to-face-area ratio", "{:.4f}", 0.5510),
                       ("eye_width_ratio", "eye-width-to-face-width ratio", "{:.4f}", 0.5445)],
    "face_reshaping": [("face_aspect", "face height-to-width ratio", "{:.3f}", 0.7457),
                       ("jaw_face_ratio", "jaw-width-to-face-width ratio", "{:.4f}", 0.5661)],
}

# canonical MediaPipe FaceMesh indices (see the round's measure_geometry.py)
_LM_IDX = dict(l_eye_out=33, l_eye_in=133, r_eye_in=362, r_eye_out=263,
               l_eye_up=159, l_eye_lo=145, r_eye_up=386, r_eye_lo=374,
               face_l=234, face_r=454, face_top=10, face_bot=152,
               jaw_l=172, jaw_r=397)


def measure_filter_evidence(pil_img, image_np):
    """Measured quantities for the filter-class explanation. Returns a dict of
    measure-key -> float (missing keys if landmarks unavailable). Pure
    measurement: no thresholds, no claims."""
    ev = {}
    texture_var, brightness_L = compute_skin_stats(image_np)
    ev["texture_var"] = texture_var
    ev["brightness_L"] = brightness_L

    lms = _detect_landmarks(pil_img)
    if lms is None:
        return ev
    h, w = image_np.shape[:2]
    P = [(l.x * w, l.y * h) for l in lms]

    def d(a, b):
        return float(np.hypot(P[a][0] - P[b][0], P[a][1] - P[b][1]))

    I = _LM_IDX
    face_w = d(I["face_l"], I["face_r"])
    face_h = d(I["face_top"], I["face_bot"])
    if face_w <= 0 or face_h <= 0:
        return ev
    ew = (d(I["l_eye_out"], I["l_eye_in"]) + d(I["r_eye_in"], I["r_eye_out"])) / 2
    eh_l, eh_r = d(I["l_eye_up"], I["l_eye_lo"]), d(I["r_eye_up"], I["r_eye_lo"])
    ev["eye_width_ratio"] = ew / face_w
    ev["eye_area_ratio"] = ((d(I["l_eye_out"], I["l_eye_in"]) * eh_l) +
                            (d(I["r_eye_in"], I["r_eye_out"]) * eh_r)) / 2 / (face_w * face_h)
    ev["jaw_face_ratio"] = d(I["jaw_l"], I["jaw_r"]) / face_w
    ev["face_aspect"] = face_h / face_w
    return ev


def _position_phrase(value, ref):
    """Where this image's value sits relative to the authentic reference."""
    p05, p50, p95 = ref
    if value < p05:
        return "below the 5th percentile of"
    if value > p95:
        return "above the 95th percentile of"
    return "within" if abs(value - p50) else "at the median of"


def build_filter_explanation(artifact_types, evidence, evidence_regions=None):
    """Evidence-driven text: every clause reports a quantity measured on THIS
    image, with the authentic reference range and the validated strength of that
    measurement. No abnormality is asserted unless the pre-declared AUROC bar
    was met (see block comment above).

    2026-09-01 (p2_xai2_evidence_regions_20260901, MASTER_PLAN P2-A1 item (b)):
    when `evidence_regions` from the validated patch evidence head is
    available, the explanation now LEADS with the region claim (which named
    regions -- eyes/nose/mouth/skin/face_contour -- scored above the
    centre-prior baseline for this image) and the artifact-type/measured
    statistics are phrased as SUPPORTING that region claim, closing with the
    same validation-citation clause as before. Previously
    (p2_evidence_wire_20260831) the region sentence was merely APPENDED after
    the artifact-type lead and measured-stats block; this is a pure reorder
    of existing clauses -- no number added, changed, or removed, and no
    classification-path change. When no region clears the centre-prior bar
    (`evidence_regions is None`), the text is IDENTICAL to the pre-2026-09-01
    wording (artifact-type lead, then measured stats, no region clause) --
    fail-safe, no forced region claim. Note the evidence regions do NOT go
    into `suspicious_regions` -- the schema's enum
    (structured-output.schema.json v2.1.0) does not admit them, so
    suspicious_regions keeps the legacy ARTIFACT_REGION_MAP names unchanged."""
    atype = artifact_types[0] if artifact_types else "unknown_filter"
    has_regions = bool(evidence_regions)
    validation_tail = _evidence_validation_clause(evidence_regions) if has_regions else ""

    if has_regions:
        lead = (f"{_evidence_region_clause(evidence_regions)} Artifact classifier's "
                 f"top filter type: {atype.replace('_', ' ')}.")
    else:
        lead = ("Classified as filter-processed (identity-preserving beautification). "
                f"Artifact classifier's top filter type: {atype.replace('_', ' ')}.")

    if atype == "unknown_filter" or atype not in _EVIDENCE_FOR_TYPE:
        return (lead + " No filter type reached the confidence threshold, so no "
                       "type-specific measurement is reported for this image."
                + validation_tail)

    clauses, aurocs = [], []
    for key, name, fmt, auroc in _EVIDENCE_FOR_TYPE[atype]:
        if key not in evidence:
            continue
        val = evidence[key]
        p05, p50, p95 = _REAL_REF[key]
        v, rng = fmt.format(val), f"{fmt.format(p05)}-{fmt.format(p95)}, median {fmt.format(p50)}"
        pos = _position_phrase(val, _REAL_REF[key])
        clauses.append(f"{name} = {v} ({pos} the authentic reference range {rng})")
        aurocs.append(auroc)
    if not clauses:
        return (lead + " Facial landmarks were unavailable, so no geometric "
                       "measurement is reported." + validation_tail)

    measured_prefix = "Supporting measurement on this image" if has_regions else "Measured on this image"
    measured = f"{measured_prefix}: " + "; ".join(clauses) + "."
    # one caveat per explanation, governed by the WEAKEST measurement reported,
    # rather than repeating the same sentence after every clause
    weakest = min(aurocs)
    if weakest >= 0.75:
        caveat = (f"On our paired held-out test these measurements separate this filter "
                  f"type from authentic faces at AUROC {weakest:.2f} or better, so they "
                  f"are supporting, not conclusive, evidence.")
    elif weakest >= 0.60:
        caveat = (f"Single-image discriminative power is limited (AUROC as low as "
                  f"{weakest:.2f} on our paired held-out test), so these values are "
                  f"reported rather than asserted as abnormal.")
    else:
        caveat = (f"On our paired held-out test these measurements separate filtered "
                  f"from authentic faces at AUROC as low as {weakest:.2f}, close to "
                  f"chance for a single image, so they are reported as measurements "
                  f"and are not the basis for the classification, which rests on the "
                  f"model's learned features.")
    return f"{lead} {measured} {caveat}{validation_tail}"


# ──────────────────────────────────────────────
# Explanation templates
# ──────────────────────────────────────────────
TEMPLATES = {
    "non_face":      "No face detected in this image. This pipeline only classifies face crops; real/fake/filter labels are not meaningful for non-face input.",
    "real":          "No significant manipulation artifacts detected. The image appears authentic.",
    # whole-face filters (smoothing/whitening/face_reshaping): {region}
    # resolves to "the face" via REGION_DISPLAY["face"] -- see
    # ARTIFACT_REGION_MAP note on why these are whole-face, not per-region.
    "smoothing":     "Skin texture variance is reduced across {region}. Bilateral filter artifacts detected — unnatural surface smoothness spanning the whole face.",
    "whitening":     "Abnormal brightness elevation detected across {region}. Skin tone whitening filter artifacts identified.",
    "face_reshaping":"Unnatural facial contour detected across {region}, most consistent with geometric compression around the jawline and cheeks (face-slimming filter).",
    # eye_enlarging: the one filter type with region-level, GT-backed localization
    "eye_enlarging": "Abnormal eye-to-face ratio detected in {region}. Geometric distortion consistent with eye enlargement filter.",
    "unknown_filter":"Subtle manipulation artifacts detected. Filter type undetermined.",
}

# 2026-08-22 (P2 fake-explanation FIX round, results/research/
# p2_fake_explanation_fix_20260822/): replaces the old constant
# TEMPLATES["ai_generated"] string (0 bits entropy, 296/296 identical in the
# QA round's audit). Conditions on confidence tier (hierarchical_predict's
# own composite probability, already computed) and this image's OWN
# compute_skin_stats() texture_var (already computed for filter class,
# reused not reimplemented) rather than asserting the same texture claim
# for every fake -- Task 3 of the FIX round found the texture effect is
# real under a paired FF++ design (Wilcoxon p=1.7e-27) but heterogeneous by
# manipulation method (FaceSwap ~null), so this conditions on the MEASURED
# value per image instead of asserting it unconditionally. Does NOT name
# any FACE_REGIONS box -- Fix A/B/C/D (ablation-based selection, center-bias
# correction, contrastive-vs-real, and causal-effect abstention) were all
# implemented and evaluated; none reduced the false-positive overclaiming
# rate below 100% on the FF++ population (see FAKE_EXPLANATION_FIX_FINDINGS.md
# Task 2/6), so no region claim is made here either.
# 2026-08-26 (EVAL-2 calibration round, results/research/
# eval2_calibration_20260826/): the former "high / moderate / lower
# confidence" adjectives are removed. The >=0.90 "high" tier was unreachable
# (composite score never exceeded 0.889 on 13,244 images), and no precision
# label transfers out of distribution: dev-fitted temperature scaling made
# AIGuard/unseen ECE worse (0.247 -> 0.320) and a calibrated ">=0.95" tier was
# only 77.7% precise there. The wording below therefore reports the raw score
# and its position relative to the decision boundary, and says explicitly
# that the score is not a calibrated probability. Band boundary 0.80 is the
# raw bucket whose empirical precision on unseen (80.0%) came closest to its
# nominal value; it is a reporting boundary, not a precision guarantee.
_FAKE_CONF_TIERS = [
    (0.80, "(model score {score:.2f}, well above the decision boundary; this score is "
           "not a calibrated probability and should not be read as a percentage "
           "chance, especially on images unlike the training data)"),
    (0.0,  "(model score {score:.2f}, close to the decision boundary; this call "
           "warrants extra scrutiny and the score is not a calibrated probability)"),
]

# 2026-08-23 (P2-R7 correction): the texture clause previously asserted that
# this image's skin-texture variance was "measurably reduced relative to
# typical authentic photos". That comparative per-image claim is NOT
# supported by the evidence it was based on. P2-R7 Approach C
# (results/research/p2_explanation_v2_20260823/) reproduced the underlying
# paired effect strongly (fake frame vs its OWN real partner: lap_var sign
# rate 74.2%, p=3.9e-95) but showed the corresponding SINGLE-IMAGE
# discrimination is AUROC 0.539 -- i.e. near chance. At inference there is no
# real partner to compare against, so the paired evidence cannot license the
# per-image assertion the sentence was making. Rewritten below to state only
# what is actually true at inference time: the measured value's range, and an
# explicit statement that this measurement alone is not reliable evidence.
# The classification itself is unaffected (this function only builds text).
def build_fake_explanation(confidence, image_np):
    conf_phrase = next(p for thr, p in _FAKE_CONF_TIERS if confidence >= thr)
    conf_phrase = conf_phrase.format(score=confidence)
    base = f"Classified as AI-generated (synthetic) facial imagery {conf_phrase}."
    texture_var, _brightness_L = compute_skin_stats(image_np)
    if texture_var < _SMOOTH_TEXTURE_THR:
        texture_clause = (" Measured skin-texture variance for this image falls in the lower "
                           "range; on its own this reading does not reliably separate synthetic "
                           "from authentic faces, and it is reported as a descriptive "
                           "observation rather than as the basis for the classification.")
    else:
        texture_clause = (" Measured skin-texture variance for this image is not unusually low; "
                           "the classification rests on the model's global spatial and "
                           "frequency-domain features rather than on any single measured "
                           "statistic.")
    return base + texture_clause


def build_explanation(prediction, artifact_types, regions, confidence=None,
                      image_np=None, pil_img=None, evidence_regions=None):
    if prediction == "non_face":
        return TEMPLATES["non_face"]
    if prediction == "real":
        return TEMPLATES["real"]
    if prediction == "fake":
        return build_fake_explanation(confidence, image_np)
    # filter class -- 2026-08-28 (XAI-2): evidence-driven text replaces the
    # fixed cue-bank templates. The old TEMPLATES entries are retained above for
    # provenance and for the legacy no-image path below, but the production path
    # measures this image and reports what it measured.
    if pil_img is not None and image_np is not None:
        evidence = measure_filter_evidence(pil_img, image_np)
        return build_filter_explanation(artifact_types, evidence,
                                        evidence_regions=evidence_regions)
    region_str = " and ".join(REGION_DISPLAY.get(r, r) for r in regions)
    if not artifact_types:
        return TEMPLATES["unknown_filter"].format(region=region_str)
    return " ".join(
        TEMPLATES.get(a, TEMPLATES["unknown_filter"]).format(region=region_str)
        for a in artifact_types
    )

# ──────────────────────────────────────────────
# Single-image inference
# ──────────────────────────────────────────────
transform_infer = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5]*3, [0.5]*3),
])

def run_single(image_path, l1_model, l2_model, gradcam_l1, gradcam_l2,
               artifact_model, device,
               save_heatmap=False, output_dir=None, jpeg_preprocess=True):
    try:
        pil_img = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {"error": str(e), "image": str(image_path)}

    if jpeg_preprocess:
        pil_img = preprocess_jpeg(pil_img, quality=85)

    # 2026-08-11: face-presence gate, checked BEFORE any classifier runs (both
    # for correctness -- a non-face input has no meaningful real/fake/filter
    # answer -- and to skip wasted inference on inputs we're about to reject).
    if not has_face(pil_img):
        return {
            "schema_version":     "2.1.0",
            "model_version":      MODEL_VERSION,
            "image":              os.path.basename(image_path),
            "prediction":         "non_face",
            "confidence":         None,
            "class_probs":        None,
            "artifact_types":     [],
            "suspicious_regions": [],
            "explanation":        TEMPLATES["non_face"],
        }

    image_np     = np.array(pil_img.resize((224, 224)))
    input_tensor = transform_infer(pil_img).unsqueeze(0).to(device)

    hp = hierarchical_predict(input_tensor, l1_model, l2_model, requires_grad=save_heatmap)
    prediction = hp["prediction"]
    confidence = hp["confidence"]
    all_probs  = {c: round(p, 4) for c, p in hp["class_probs"].items()}

    # suspicious_regions: source depends on prediction class.
    # fake -> intentionally always []: our CURRENT fake-class training sources
    # (AIGuard, DF40 diffusion/EFS methods) are whole-face synthesis with no
    # official manipulation mask, so there is no region-level ground truth to
    # train or validate against for these (the FakeVLM-distilled region head
    # this used to call was found to be near-total label degeneracy -- 6/8
    # regions at 99.5-100% positive rate, no-image baseline already explained
    # 87% of its reported F1). NOTE (2026-08-11): this is a property of our
    # current fake sources, not of "fake" in general -- FaceForensics++
    # DOES ship official binary manipulation masks for its classic methods
    # (Deepfakes/Face2Face/FaceSwap/NeuralTextures), which we don't currently
    # train on. If FF++ is added later, region-level fake explanations become
    # possible for that subset specifically -- see TODO.md 2026-08-11 entry.
    # Fake explanations are global-level only for now (Grad-CAM++ heatmap +
    # a single non-localized sentence), not per-region claims.
    if prediction in ("real", "fake"):
        regions = []
    else:
        # filter: derive from artifact_type after classification (below)
        regions = []  # filled in after artifact_types determined below

    # Artifact type
    # 2026-08-22: image_np_for_stat is now needed unconditionally (also by
    # build_fake_explanation() below for the fake branch), not just in the
    # infer_artifact_type() fallback -- compute it once up front instead of
    # only inside the else branch (was previously unbound when
    # prediction=="filter" and artifact_model is not None, i.e. every normal
    # production filter call -- caught by smoke test before this shipped).
    image_np_for_stat = np.array(pil_img.resize((224, 224)))
    if prediction == "filter" and artifact_model is not None:
        art_tag, _ = classify_artifact(pil_img, artifact_model, device)
        artifact_types = [art_tag]
    else:
        artifact_types = infer_artifact_type(prediction, regions, image_np_for_stat)

    # filter regions: rule-based from artifact_type
    # (2026-08-31 p2_evidence_wire: suspicious_regions intentionally STAYS on
    # the legacy ARTIFACT_REGION_MAP names -- the schema enum does not admit
    # evidence-head region names. Evidence output is explanation-text only.)
    evidence_regions = None
    if prediction == "filter":
        regions = ARTIFACT_REGION_MAP.get(artifact_types[0] if artifact_types else "unknown_filter", [])
        # evidence head (fail-safe, filter class ONLY -- fake stays
        # global-only per the P2 fake-explanation FIX round finding)
        evidence_regions = evidence_regions_for_filter(input_tensor, device)

    explanation = build_explanation(prediction, artifact_types, regions,
                                     confidence=confidence, image_np=image_np_for_stat,
                                     pil_img=pil_img,
                                     evidence_regions=evidence_regions)

    result = {
        "schema_version":    "2.1.0",
        "model_version":     MODEL_VERSION,
        "image":             os.path.basename(image_path),
        "prediction":        prediction,
        "confidence":        round(confidence, 4),
        "class_probs":       all_probs,
        "artifact_types":    artifact_types,
        "suspicious_regions": regions,
        "explanation":       explanation,
    }

    if save_heatmap and output_dir:
        gradcam = gradcam_l1 if hp["gradcam_layer"] == "l1" else gradcam_l2
        cam      = gradcam.generate(input_tensor, hp["gradcam_class_idx"])
        stem     = Path(image_path).stem
        img_bgr  = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
        hmap_col = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
        overlay  = cv2.addWeighted(img_bgr, 0.55, hmap_col, 0.45, 0)
        _, binary_mask = cv2.threshold((cam * 255).astype(np.uint8), 115, 255, cv2.THRESH_BINARY)

        hmap_path = os.path.join(output_dir, f"{stem}_heatmap.jpg")
        mask_path = os.path.join(output_dir, f"{stem}_mask.jpg")
        cv2.imwrite(hmap_path, overlay)
        cv2.imwrite(mask_path, binary_mask)
        result["heatmap_path"] = hmap_path
        result["mask_path"]    = mask_path

    return result

# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="AIGC & Filter Detection Pipeline")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--image",  help="Path to a single image")
    group.add_argument("--folder", help="Path to a folder of images")
    parser.add_argument("--save_heatmap",   action="store_true", help="Save Grad-CAM heatmap")
    parser.add_argument("--output_dir",     default=None,        help="Output directory")
    parser.add_argument("--no_jpeg_preproc",action="store_true", help="Disable JPEG preprocessing")
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")
    print(f"Loading v8.11 hierarchical classifier:")
    print(f"  Layer1 (real vs manipulated): {LAYER1_WEIGHTS_PATH}")
    print(f"  Layer2 (fake vs filter):      {LAYER2_WEIGHTS_PATH}")

    l1_model = DualBranchModel(num_classes=2).to(device)
    l1_model.load_state_dict(torch.load(LAYER1_WEIGHTS_PATH, map_location=device))
    l1_model.eval()
    gradcam_l1 = GradCAMPlusPlus(l1_model, l1_model.spatial_branch.conv5)

    l2_model = DualBranchModel(num_classes=2).to(device)
    l2_model.load_state_dict(torch.load(LAYER2_WEIGHTS_PATH, map_location=device))
    l2_model.eval()
    gradcam_l2 = GradCAMPlusPlus(l2_model, l2_model.spatial_branch.conv5)

    artifact_model = None
    if os.path.exists(ARTIFACT_WEIGHTS_PATH):
        artifact_model = build_artifact_model().to(device)
        artifact_model.load_state_dict(
            torch.load(ARTIFACT_WEIGHTS_PATH, map_location=device))
        artifact_model.eval()
        print(f"Artifact classifier loaded from {ARTIFACT_WEIGHTS_PATH}")
    else:
        print("Artifact classifier not found — using heuristic fallback")

    # NOTE: the FakeVLM-distilled region head (region_head_v1.pth) that used
    # to provide "fake" class suspicious_regions has been removed (2026-08-02).
    # Phase 2 found it was near-total label degeneracy (docs/phase2_story.md);
    # fake explanations are now intentionally global-level only.

    jpeg_pre = not args.no_jpeg_preproc

    # ── single image ──
    if args.image:
        out_dir = args.output_dir or os.path.join(BASE, "explanation_output")
        os.makedirs(out_dir, exist_ok=True)
        result = run_single(args.image, l1_model, l2_model, gradcam_l1, gradcam_l2,
                            artifact_model, device,
                            save_heatmap=args.save_heatmap,
                            output_dir=out_dir,
                            jpeg_preprocess=jpeg_pre)
        print(json.dumps(result, indent=2, ensure_ascii=False))

        json_path = os.path.join(out_dir, Path(args.image).stem + "_result.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\nJSON saved to {json_path}")
        return

    # ── folder ──
    folder   = args.folder
    out_dir  = args.output_dir or os.path.join(folder, "pipeline_output")
    os.makedirs(out_dir, exist_ok=True)

    image_files = sorted([
        p for p in Path(folder).iterdir()
        if p.suffix.lower() in IMG_EXTS
    ])
    print(f"Found {len(image_files)} images in {folder}")

    results = []
    for i, img_path in enumerate(image_files, 1):
        r = run_single(str(img_path), l1_model, l2_model, gradcam_l1, gradcam_l2,
                       artifact_model, device,
                       save_heatmap=args.save_heatmap,
                       output_dir=out_dir,
                       jpeg_preprocess=jpeg_pre)
        results.append(r)
        print(f"[{i:3d}/{len(image_files)}] {r['image']:40s} "
              f"→ {r.get('prediction','ERR'):6s} "
              f"({r.get('confidence', 0):.3f})  "
              f"artifact: {r.get('artifact_type', [])}")

    # Save summary CSV
    csv_path = os.path.join(out_dir, "summary.csv")
    csv_fields = ["image", "prediction", "confidence",
                  "prob_real", "prob_fake", "prob_filter",
                  "artifact_types", "suspicious_regions", "explanation"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        for r in results:
            row = dict(r)
            probs = r.get("class_probs", {})
            row["prob_real"]   = probs.get("real",   "")
            row["prob_fake"]   = probs.get("fake",   "")
            row["prob_filter"] = probs.get("filter", "")
            row["artifact_types"]     = "|".join(r.get("artifact_types", []))
            row["suspicious_regions"] = "|".join(r.get("suspicious_regions", []))
            writer.writerow(row)

    # Save all JSONs
    json_path = os.path.join(out_dir, "all_results.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Print summary stats
    preds = [r.get("prediction") for r in results if "prediction" in r]
    print(f"\n{'='*50}")
    print(f"Summary: {len(results)} images")
    for cls in CLASSES:
        n = preds.count(cls)
        print(f"  {cls:8s}: {n:4d} ({n/len(preds)*100:.1f}%)")
    print(f"\nCSV  → {csv_path}")
    print(f"JSON → {json_path}")


if __name__ == "__main__":
    main()
