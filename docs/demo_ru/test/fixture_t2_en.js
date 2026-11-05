window.T2_FIXTURE_EN = {
 "source": "fixture_t2.json (same 50 records)",
 "expected_from": "nl_v5/explain_v2_en.t2_sentences_en / compose_en (Python)",
 "note": "records 1-50 = fixture_t2.json; 51-54 synthetic branch cases (multi-part, multi-operation, 0.50 boundary)",
 "n": 54,
 "records": [
  {
   "id": "ffhq_demo_edit:17042_nose",
   "group": "ffhq_demo_edit",
   "truth": "fake",
   "box": [
    0,
    20,
    497,
    512
   ],
   "src": "ffhq:17042:nose:donor=17044",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.05,
    "face_slimming": 0.01,
    "skin_brightening": 0.03,
    "skin_smoothing": 0.2
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.16,
    "nose": 0.99,
    "mouth": 0.55,
    "skin": 0.31,
    "contour": 0.0
   },
   "evidence_peak": 0.998,
   "named_parts": [
    "nose"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence on the nose.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "nose"
    ],
    "named_region_area_frac": 0.0531,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.9995,
    "p_label_after_named_restored": 0.0019,
    "harness_decision": "fake",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original",
    "footprint_area_frac": 0.6101,
    "footprint_restored_flips_decision": true,
    "map_topk_restored_flips_decision": true
   },
   "image": "17042_nose.jpg",
   "x0": "17042_x0.png",
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is concentrated on the nose (mean evidence 0.99).",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is concentrated on the nose (mean evidence 0.99). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_fake:Deepfakes:288_321__f0390",
   "group": "ffpp_fake",
   "truth": "fake",
   "box": null,
   "src": "ffpp:Deepfakes",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.06,
    "face_slimming": 0.01,
    "skin_brightening": 0.19,
    "skin_smoothing": 0.17
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.9,
    "nose": 1.0,
    "mouth": 1.0,
    "skin": 0.86,
    "contour": 0.38
   },
   "evidence_peak": 0.999,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence across the whole face.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "288_321__f0390.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is spread over the whole face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is spread over the whole face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:EyeEnlarging_90:17778",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    7,
    96,
    949,
    1024
   ],
   "src": "alibaba:EyeEnlarging_90:17778",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.35,
    "fake": 0.02,
    "filter": 0.63
   },
   "operations": {
    "eye_enlargement": 0.37,
    "face_slimming": 0.06,
    "skin_brightening": 0.12,
    "skin_smoothing": 0.03
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.76,
    "nose": 0.57,
    "mouth": 0.24,
    "skin": 0.54,
    "contour": 0.39
   },
   "evidence_peak": 0.908,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: operation unclear.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes"
    ],
    "named_region_area_frac": 0.1001,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.6985,
    "p_label_after_named_restored": 0.374,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17778.png",
   "x0": "17778.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.63).",
    "The evidence is concentrated on the eyes (mean evidence 0.76).",
    "None of the four operations reaches the threshold of 0.5.",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.63). The evidence is concentrated on the eyes (mean evidence 0.76). None of the four operations reaches the threshold of 0.5. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:FaceLifting_90:17567",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    14,
    42,
    977,
    1024
   ],
   "src": "alibaba:FaceLifting_90:17567",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.35,
    "fake": 0.0,
    "filter": 0.65
   },
   "operations": {
    "eye_enlargement": 0.09,
    "face_slimming": 0.51,
    "skin_brightening": 0.02,
    "skin_smoothing": 0.03
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.25,
    "nose": 0.12,
    "mouth": 0.21,
    "skin": 0.35,
    "contour": 0.53
   },
   "evidence_peak": 0.869,
   "named_parts": [
    "contour"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: face reshaped.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "contour"
    ],
    "named_region_area_frac": 0.2439,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.5938,
    "p_label_after_named_restored": 0.2371,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17567.png",
   "x0": "17567.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.65).",
    "The evidence is concentrated on the face contour (mean evidence 0.53).",
    "Operations at or above the threshold of 0.5: face slimming (0.51).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.65). The evidence is concentrated on the face contour (mean evidence 0.53). Operations at or above the threshold of 0.5: face slimming (0.51). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:Whitening_90:17473",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    98,
    60,
    999,
    1024
   ],
   "src": "alibaba:Whitening_90:17473",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.42,
    "fake": 0.0,
    "filter": 0.58
   },
   "operations": {
    "eye_enlargement": 0.02,
    "face_slimming": 0.02,
    "skin_brightening": 0.47,
    "skin_smoothing": 0.01
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.69,
    "nose": 0.7,
    "mouth": 0.63,
    "skin": 0.66,
    "contour": 0.58
   },
   "evidence_peak": 0.818,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: operation unclear.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes",
     "nose",
     "mouth",
     "skin",
     "contour"
    ],
    "named_region_area_frac": 0.4253,
    "named_region_restored_flips_decision": false,
    "p_label_before": 0.6818,
    "p_label_after_named_restored": 0.5171,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17473.png",
   "x0": "17473.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.58).",
    "The evidence is spread over the whole face.",
    "None of the four operations reaches the threshold of 0.5.",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.58). The evidence is spread over the whole face. None of the four operations reaches the threshold of 0.5. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffhq_demo_edit:17023_white",
   "group": "ffhq_demo_edit",
   "truth": "filter",
   "box": [
    0,
    35,
    472,
    512
   ],
   "src": "ffhq:17023:white",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.0,
    "fake": 0.02,
    "filter": 0.98
   },
   "operations": {
    "eye_enlargement": 0.0,
    "face_slimming": 0.0,
    "skin_brightening": 1.0,
    "skin_smoothing": 0.0
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.99,
    "nose": 1.0,
    "mouth": 0.88,
    "skin": 0.96,
    "contour": 0.86
   },
   "evidence_peak": 0.998,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: skin brightened.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes",
     "nose",
     "mouth",
     "skin",
     "contour"
    ],
    "named_region_area_frac": 0.4811,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.9821,
    "p_label_after_named_restored": 0.1767,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17023_white.jpg",
   "x0": "17023_x0.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.98).",
    "The evidence is spread over the whole face.",
    "Operations at or above the threshold of 0.5: skin whitening (1.00).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.98). The evidence is spread over the whole face. Operations at or above the threshold of 0.5: skin whitening (1.00). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_real:142__f0778",
   "group": "ffpp_real",
   "truth": "real",
   "box": null,
   "src": "ffpp:real",
   "model": "clipe5_s20260929",
   "decision": "real",
   "probabilities": {
    "real": 0.89,
    "fake": 0.01,
    "filter": 0.1
   },
   "operations": {
    "eye_enlargement": 0.06,
    "face_slimming": 0.02,
    "skin_brightening": 0.01,
    "skin_smoothing": 0.01
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.0,
    "nose": 0.0,
    "mouth": 0.0,
    "skin": 0.0,
    "contour": 0.0
   },
   "evidence_peak": 0.0,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "No manipulation detected.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "decision is real: nothing to restore; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "142__f0778.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is real (score 0.89).",
    "No manipulation was detected on the face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is real (score 0.89). No manipulation was detected on the face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_fake:Face2Face:995_233__f0486",
   "group": "ffpp_fake",
   "truth": "fake",
   "box": null,
   "src": "ffpp:Face2Face",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.22,
    "face_slimming": 0.01,
    "skin_brightening": 0.02,
    "skin_smoothing": 0.21
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.09,
    "nose": 0.71,
    "mouth": 0.92,
    "skin": 0.21,
    "contour": 0.01
   },
   "evidence_peak": 0.988,
   "named_parts": [
    "mouth"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence on the mouth.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "995_233__f0486.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is concentrated on the mouth (mean evidence 0.92).",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is concentrated on the mouth (mean evidence 0.92). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_fake:FaceSwap:732_691__f0193",
   "group": "ffpp_fake",
   "truth": "fake",
   "box": null,
   "src": "ffpp:FaceSwap",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.02,
    "face_slimming": 0.01,
    "skin_brightening": 0.66,
    "skin_smoothing": 0.02
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.94,
    "nose": 1.0,
    "mouth": 0.89,
    "skin": 0.68,
    "contour": 0.19
   },
   "evidence_peak": 0.999,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence across the whole face.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "732_691__f0193.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is spread over the whole face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is spread over the whole face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_real:257__f0346",
   "group": "ffpp_real",
   "truth": "real",
   "box": null,
   "src": "ffpp:real",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.48,
    "fake": 0.01,
    "filter": 0.51
   },
   "operations": {
    "eye_enlargement": 0.01,
    "face_slimming": 0.01,
    "skin_brightening": 0.2,
    "skin_smoothing": 0.0
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.07,
    "nose": 0.05,
    "mouth": 0.05,
    "skin": 0.05,
    "contour": 0.03
   },
   "evidence_peak": 0.148,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: operation unclear.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "257__f0346.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is filter (score 0.51).",
    "The evidence is concentrated on the eyes (mean evidence 0.07).",
    "None of the four operations reaches the threshold of 0.5.",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.51). The evidence is concentrated on the eyes (mean evidence 0.07). None of the four operations reaches the threshold of 0.5. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_real:314__f0370",
   "group": "ffpp_real",
   "truth": "real",
   "box": null,
   "src": "ffpp:real",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.05,
    "fake": 0.29,
    "filter": 0.66
   },
   "operations": {
    "eye_enlargement": 0.01,
    "face_slimming": 0.01,
    "skin_brightening": 0.01,
    "skin_smoothing": 0.79
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.71,
    "nose": 0.16,
    "mouth": 0.12,
    "skin": 0.15,
    "contour": 0.02
   },
   "evidence_peak": 0.935,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: skin smoothed.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "314__f0370.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is filter (score 0.66).",
    "The evidence is concentrated on the eyes (mean evidence 0.71).",
    "Operations at or above the threshold of 0.5: skin smoothing (0.79).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.66). The evidence is concentrated on the eyes (mean evidence 0.71). Operations at or above the threshold of 0.5: skin smoothing (0.79). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:FaceLifting_90:17213",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    0,
    82,
    933,
    1024
   ],
   "src": "alibaba:FaceLifting_90:17213",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.38,
    "fake": 0.01,
    "filter": 0.62
   },
   "operations": {
    "eye_enlargement": 0.09,
    "face_slimming": 0.04,
    "skin_brightening": 0.17,
    "skin_smoothing": 0.03
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.67,
    "nose": 0.59,
    "mouth": 0.64,
    "skin": 0.57,
    "contour": 0.5
   },
   "evidence_peak": 0.752,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: operation unclear.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes",
     "nose",
     "mouth",
     "skin",
     "contour"
    ],
    "named_region_area_frac": 0.4589,
    "named_region_restored_flips_decision": false,
    "p_label_before": 0.7624,
    "p_label_after_named_restored": 0.7324,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17213.png",
   "x0": "17213.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.62).",
    "The evidence is spread over the whole face.",
    "None of the four operations reaches the threshold of 0.5.",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.62). The evidence is spread over the whole face. None of the four operations reaches the threshold of 0.5. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:Whitening_90:17521",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    14,
    87,
    951,
    1024
   ],
   "src": "alibaba:Whitening_90:17521",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.11,
    "fake": 0.01,
    "filter": 0.88
   },
   "operations": {
    "eye_enlargement": 0.17,
    "face_slimming": 0.19,
    "skin_brightening": 0.2,
    "skin_smoothing": 0.85
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.81,
    "nose": 0.85,
    "mouth": 0.88,
    "skin": 0.81,
    "contour": 0.78
   },
   "evidence_peak": 0.922,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: skin smoothed.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes",
     "nose",
     "mouth",
     "skin",
     "contour"
    ],
    "named_region_area_frac": 0.4406,
    "named_region_restored_flips_decision": false,
    "p_label_before": 0.895,
    "p_label_after_named_restored": 0.921,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17521.png",
   "x0": "17521.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.88).",
    "The evidence is spread over the whole face.",
    "Operations at or above the threshold of 0.5: skin smoothing (0.85).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.88). The evidence is spread over the whole face. Operations at or above the threshold of 0.5: skin smoothing (0.85). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_real:701__f0282",
   "group": "ffpp_real",
   "truth": "real",
   "box": null,
   "src": "ffpp:real",
   "model": "clipe5_s20260929",
   "decision": "real",
   "probabilities": {
    "real": 0.59,
    "fake": 0.01,
    "filter": 0.4
   },
   "operations": {
    "eye_enlargement": 0.05,
    "face_slimming": 0.03,
    "skin_brightening": 0.26,
    "skin_smoothing": 0.0
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.0,
    "nose": 0.0,
    "mouth": 0.0,
    "skin": 0.0,
    "contour": 0.0
   },
   "evidence_peak": 0.002,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "No manipulation detected.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "decision is real: nothing to restore; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "701__f0282.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is real (score 0.59).",
    "No manipulation was detected on the face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is real (score 0.59). No manipulation was detected on the face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_fake:Face2Face:552_851__f0156",
   "group": "ffpp_fake",
   "truth": "fake",
   "box": null,
   "src": "ffpp:Face2Face",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.05,
    "face_slimming": 0.01,
    "skin_brightening": 0.03,
    "skin_smoothing": 0.46
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.27,
    "nose": 0.96,
    "mouth": 0.42,
    "skin": 0.23,
    "contour": 0.04
   },
   "evidence_peak": 0.997,
   "named_parts": [
    "nose"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence on the nose.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "552_851__f0156.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is concentrated on the nose (mean evidence 0.96).",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is concentrated on the nose (mean evidence 0.96). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_fake:FaceSwap:047_862__f0116",
   "group": "ffpp_fake",
   "truth": "fake",
   "box": null,
   "src": "ffpp:FaceSwap",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.07,
    "face_slimming": 0.03,
    "skin_brightening": 0.09,
    "skin_smoothing": 0.1
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.91,
    "nose": 0.99,
    "mouth": 0.91,
    "skin": 0.69,
    "contour": 0.35
   },
   "evidence_peak": 0.999,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence across the whole face.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "047_862__f0116.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is spread over the whole face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is spread over the whole face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:EyeEnlarging_90:17268",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    65,
    80,
    975,
    1024
   ],
   "src": "alibaba:EyeEnlarging_90:17268",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.33,
    "fake": 0.25,
    "filter": 0.42
   },
   "operations": {
    "eye_enlargement": 0.37,
    "face_slimming": 0.05,
    "skin_brightening": 0.07,
    "skin_smoothing": 0.05
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.43,
    "nose": 0.75,
    "mouth": 0.2,
    "skin": 0.31,
    "contour": 0.07
   },
   "evidence_peak": 0.874,
   "named_parts": [
    "nose"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: operation unclear.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "nose"
    ],
    "named_region_area_frac": 0.056,
    "named_region_restored_flips_decision": false,
    "p_label_before": 0.4195,
    "p_label_after_named_restored": 0.4955,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17268.png",
   "x0": "17268.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.42).",
    "The evidence is concentrated on the nose (mean evidence 0.75).",
    "None of the four operations reaches the threshold of 0.5.",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.42). The evidence is concentrated on the nose (mean evidence 0.75). None of the four operations reaches the threshold of 0.5. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:EyeEnlarging_90:17364",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    0,
    0,
    1001,
    1024
   ],
   "src": "alibaba:EyeEnlarging_90:17364",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.0,
    "fake": 0.0,
    "filter": 0.99
   },
   "operations": {
    "eye_enlargement": 1.0,
    "face_slimming": 0.0,
    "skin_brightening": 0.0,
    "skin_smoothing": 0.0
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.97,
    "nose": 0.58,
    "mouth": 0.05,
    "skin": 0.56,
    "contour": 0.28
   },
   "evidence_peak": 0.99,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: eyes enlarged.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes"
    ],
    "named_region_area_frac": 0.1063,
    "named_region_restored_flips_decision": false,
    "p_label_before": 0.9953,
    "p_label_after_named_restored": 0.878,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17364.png",
   "x0": "17364.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.99).",
    "The evidence is concentrated on the eyes (mean evidence 0.97).",
    "Operations at or above the threshold of 0.5: eye enlargement (1.00).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.99). The evidence is concentrated on the eyes (mean evidence 0.97). Operations at or above the threshold of 0.5: eye enlargement (1.00). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:Whitening_90:17213",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    0,
    82,
    933,
    1024
   ],
   "src": "alibaba:Whitening_90:17213",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.35,
    "fake": 0.0,
    "filter": 0.65
   },
   "operations": {
    "eye_enlargement": 0.06,
    "face_slimming": 0.02,
    "skin_brightening": 0.21,
    "skin_smoothing": 0.02
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.68,
    "nose": 0.64,
    "mouth": 0.68,
    "skin": 0.58,
    "contour": 0.54
   },
   "evidence_peak": 0.779,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: operation unclear.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes",
     "nose",
     "mouth",
     "skin",
     "contour"
    ],
    "named_region_area_frac": 0.4717,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.7311,
    "p_label_after_named_restored": 0.4194,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17213.png",
   "x0": "17213.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.65).",
    "The evidence is spread over the whole face.",
    "None of the four operations reaches the threshold of 0.5.",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.65). The evidence is spread over the whole face. None of the four operations reaches the threshold of 0.5. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:EyeEnlarging_90:17721",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    77,
    89,
    1024,
    1024
   ],
   "src": "alibaba:EyeEnlarging_90:17721",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.02,
    "fake": 0.01,
    "filter": 0.98
   },
   "operations": {
    "eye_enlargement": 0.01,
    "face_slimming": 0.01,
    "skin_brightening": 0.97,
    "skin_smoothing": 0.0
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.9,
    "nose": 0.94,
    "mouth": 0.91,
    "skin": 0.92,
    "contour": 0.79
   },
   "evidence_peak": 0.967,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: skin brightened.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes",
     "nose",
     "mouth",
     "skin",
     "contour"
    ],
    "named_region_area_frac": 0.4643,
    "named_region_restored_flips_decision": false,
    "p_label_before": 0.9721,
    "p_label_after_named_restored": 0.9535,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17721.png",
   "x0": "17721.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.98).",
    "The evidence is spread over the whole face.",
    "Operations at or above the threshold of 0.5: skin whitening (0.97).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.98). The evidence is spread over the whole face. Operations at or above the threshold of 0.5: skin whitening (0.97). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:Whitening_90:17106",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    61,
    50,
    951,
    1024
   ],
   "src": "alibaba:Whitening_90:17106",
   "model": "clipe5_s20260929",
   "decision": "real",
   "probabilities": {
    "real": 0.73,
    "fake": 0.0,
    "filter": 0.26
   },
   "operations": {
    "eye_enlargement": 0.04,
    "face_slimming": 0.07,
    "skin_brightening": 0.09,
    "skin_smoothing": 0.02
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.0,
    "nose": 0.0,
    "mouth": 0.0,
    "skin": 0.0,
    "contour": 0.0
   },
   "evidence_peak": 0.004,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "No manipulation detected.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "decision is real: nothing to restore; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "17106.png",
   "x0": "17106.png",
   "t2_sentences_en": [
    "The model's decision is real (score 0.73).",
    "No manipulation was detected on the face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is real (score 0.73). No manipulation was detected on the face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_fake:FaceSwap:388_308__f0361",
   "group": "ffpp_fake",
   "truth": "fake",
   "box": null,
   "src": "ffpp:FaceSwap",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.04,
    "face_slimming": 0.01,
    "skin_brightening": 0.09,
    "skin_smoothing": 0.19
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.71,
    "nose": 0.97,
    "mouth": 0.25,
    "skin": 0.29,
    "contour": 0.11
   },
   "evidence_peak": 0.995,
   "named_parts": [
    "nose"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence on the nose.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "388_308__f0361.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is concentrated on the nose (mean evidence 0.97).",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is concentrated on the nose (mean evidence 0.97). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_fake:FaceSwap:683_607__f0243",
   "group": "ffpp_fake",
   "truth": "fake",
   "box": null,
   "src": "ffpp:FaceSwap",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.16,
    "face_slimming": 0.07,
    "skin_brightening": 0.33,
    "skin_smoothing": 0.28
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.94,
    "nose": 0.99,
    "mouth": 0.93,
    "skin": 0.77,
    "contour": 0.3
   },
   "evidence_peak": 1.0,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence across the whole face.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "683_607__f0243.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is spread over the whole face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is spread over the whole face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_real:420__f0212",
   "group": "ffpp_real",
   "truth": "real",
   "box": null,
   "src": "ffpp:real",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.4,
    "fake": 0.01,
    "filter": 0.59
   },
   "operations": {
    "eye_enlargement": 0.1,
    "face_slimming": 0.18,
    "skin_brightening": 0.03,
    "skin_smoothing": 0.05
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.0,
    "nose": 0.0,
    "mouth": 0.0,
    "skin": 0.0,
    "contour": 0.0
   },
   "evidence_peak": 0.005,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: operation unclear.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "420__f0212.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is filter (score 0.59).",
    "The evidence is concentrated on the eyes (mean evidence 0.00).",
    "None of the four operations reaches the threshold of 0.5.",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.59). The evidence is concentrated on the eyes (mean evidence 0.00). None of the four operations reaches the threshold of 0.5. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffhq_demo_edit:17024_smooth",
   "group": "ffhq_demo_edit",
   "truth": "filter",
   "box": [
    19,
    36,
    486,
    512
   ],
   "src": "ffhq:17024:smooth",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.43,
    "fake": 0.09,
    "filter": 0.48
   },
   "operations": {
    "eye_enlargement": 0.04,
    "face_slimming": 0.04,
    "skin_brightening": 0.03,
    "skin_smoothing": 0.5
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.0,
    "nose": 0.0,
    "mouth": 0.0,
    "skin": 0.0,
    "contour": 0.0
   },
   "evidence_peak": 0.004,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: skin smoothed.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes"
    ],
    "named_region_area_frac": 0.087,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.4323,
    "p_label_after_named_restored": 0.1994,
    "harness_decision": "real",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17024_smooth.jpg",
   "x0": "17024_x0.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.48).",
    "The evidence is concentrated on the eyes (mean evidence 0.00).",
    "Operations at or above the threshold of 0.5: skin smoothing (0.50).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.48). The evidence is concentrated on the eyes (mean evidence 0.00). Operations at or above the threshold of 0.5: skin smoothing (0.50). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:Smoothing_90:17106",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    61,
    50,
    951,
    1024
   ],
   "src": "alibaba:Smoothing_90:17106",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.06,
    "fake": 0.04,
    "filter": 0.9
   },
   "operations": {
    "eye_enlargement": 0.07,
    "face_slimming": 0.1,
    "skin_brightening": 0.09,
    "skin_smoothing": 0.96
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.87,
    "nose": 0.88,
    "mouth": 0.9,
    "skin": 0.84,
    "contour": 0.79
   },
   "evidence_peak": 0.933,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: skin smoothed.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes",
     "nose",
     "mouth",
     "skin",
     "contour"
    ],
    "named_region_area_frac": 0.4752,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.9051,
    "p_label_after_named_restored": 0.2714,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17106.png",
   "x0": "17106.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.90).",
    "The evidence is spread over the whole face.",
    "Operations at or above the threshold of 0.5: skin smoothing (0.96).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.90). The evidence is spread over the whole face. Operations at or above the threshold of 0.5: skin smoothing (0.96). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:FaceLifting_90:17419",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    97,
    73,
    968,
    1024
   ],
   "src": "alibaba:FaceLifting_90:17419",
   "model": "clipe5_s20260929",
   "decision": "real",
   "probabilities": {
    "real": 0.56,
    "fake": 0.0,
    "filter": 0.43
   },
   "operations": {
    "eye_enlargement": 0.06,
    "face_slimming": 0.34,
    "skin_brightening": 0.07,
    "skin_smoothing": 0.1
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.18,
    "nose": 0.13,
    "mouth": 0.23,
    "skin": 0.2,
    "contour": 0.27
   },
   "evidence_peak": 0.441,
   "named_parts": [
    "contour"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "No manipulation detected.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "decision is real: nothing to restore; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "17419.png",
   "x0": "17419.png",
   "t2_sentences_en": [
    "The model's decision is real (score 0.56).",
    "No manipulation was detected on the face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is real (score 0.56). No manipulation was detected on the face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "part_forgery:sdxl:507__f0212__eyes",
   "group": "part_forgery",
   "truth": "fake",
   "box": null,
   "src": "partedit:sdxl:eyes",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.21,
    "face_slimming": 0.13,
    "skin_brightening": 0.01,
    "skin_smoothing": 0.09
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.99,
    "nose": 0.19,
    "mouth": 0.0,
    "skin": 0.29,
    "contour": 0.2
   },
   "evidence_peak": 0.999,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence on the eyes.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "true_part": "eyes",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes"
    ],
    "named_region_area_frac": 0.0991,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.9994,
    "p_label_after_named_restored": 0.0026,
    "harness_decision": "fake",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original",
    "footprint_area_frac": 0.0724,
    "footprint_restored_flips_decision": true,
    "map_topk_restored_flips_decision": true
   },
   "image": "507__f0212__eyes.jpg",
   "x0": "507__f0212.jpg",
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is concentrated on the eyes (mean evidence 0.99).",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is concentrated on the eyes (mean evidence 0.99). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_fake:NeuralTextures:507_418__f0201",
   "group": "ffpp_fake",
   "truth": "fake",
   "box": null,
   "src": "ffpp:NeuralTextures",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.06,
    "face_slimming": 0.01,
    "skin_brightening": 0.01,
    "skin_smoothing": 0.43
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.62,
    "nose": 0.83,
    "mouth": 0.98,
    "skin": 0.75,
    "contour": 0.48
   },
   "evidence_peak": 0.985,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence across the whole face.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "507_418__f0201.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is spread over the whole face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is spread over the whole face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_real:141__f0275",
   "group": "ffpp_real",
   "truth": "real",
   "box": null,
   "src": "ffpp:real",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.36,
    "fake": 0.14,
    "filter": 0.5
   },
   "operations": {
    "eye_enlargement": 0.2,
    "face_slimming": 0.09,
    "skin_brightening": 0.06,
    "skin_smoothing": 0.18
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.0,
    "nose": 0.0,
    "mouth": 0.0,
    "skin": 0.0,
    "contour": 0.0
   },
   "evidence_peak": 0.004,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: operation unclear.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "141__f0275.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is filter (score 0.50).",
    "The evidence is concentrated on the eyes (mean evidence 0.00).",
    "None of the four operations reaches the threshold of 0.5.",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.50). The evidence is concentrated on the eyes (mean evidence 0.00). None of the four operations reaches the threshold of 0.5. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:FaceLifting_90:17106",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    61,
    50,
    951,
    1024
   ],
   "src": "alibaba:FaceLifting_90:17106",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.06,
    "fake": 0.0,
    "filter": 0.94
   },
   "operations": {
    "eye_enlargement": 0.02,
    "face_slimming": 0.92,
    "skin_brightening": 0.02,
    "skin_smoothing": 0.01
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.06,
    "nose": 0.07,
    "mouth": 0.42,
    "skin": 0.43,
    "contour": 0.78
   },
   "evidence_peak": 0.986,
   "named_parts": [
    "contour"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: face reshaped.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "contour"
    ],
    "named_region_area_frac": 0.2428,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.9188,
    "p_label_after_named_restored": 0.1928,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17106.png",
   "x0": "17106.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.94).",
    "The evidence is concentrated on the face contour (mean evidence 0.78).",
    "Operations at or above the threshold of 0.5: face slimming (0.92).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.94). The evidence is concentrated on the face contour (mean evidence 0.78). Operations at or above the threshold of 0.5: face slimming (0.92). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_real:399__f0468",
   "group": "ffpp_real",
   "truth": "real",
   "box": null,
   "src": "ffpp:real",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.11,
    "fake": 0.01,
    "filter": 0.87
   },
   "operations": {
    "eye_enlargement": 0.0,
    "face_slimming": 0.0,
    "skin_brightening": 0.94,
    "skin_smoothing": 0.0
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.91,
    "nose": 0.86,
    "mouth": 0.9,
    "skin": 0.77,
    "contour": 0.51
   },
   "evidence_peak": 0.958,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: skin brightened.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "399__f0468.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is filter (score 0.87).",
    "The evidence is spread over the whole face.",
    "Operations at or above the threshold of 0.5: skin whitening (0.94).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.87). The evidence is spread over the whole face. Operations at or above the threshold of 0.5: skin whitening (0.94). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_real:682__f0781",
   "group": "ffpp_real",
   "truth": "real",
   "box": null,
   "src": "ffpp:real",
   "model": "clipe5_s20260929",
   "decision": "real",
   "probabilities": {
    "real": 0.71,
    "fake": 0.04,
    "filter": 0.24
   },
   "operations": {
    "eye_enlargement": 0.06,
    "face_slimming": 0.17,
    "skin_brightening": 0.01,
    "skin_smoothing": 0.02
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.0,
    "nose": 0.0,
    "mouth": 0.0,
    "skin": 0.0,
    "contour": 0.0
   },
   "evidence_peak": 0.002,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "No manipulation detected.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "decision is real: nothing to restore; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "682__f0781.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is real (score 0.71).",
    "No manipulation was detected on the face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is real (score 0.71). No manipulation was detected on the face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_fake:NeuralTextures:479_706__f0119",
   "group": "ffpp_fake",
   "truth": "fake",
   "box": null,
   "src": "ffpp:NeuralTextures",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.26,
    "fake": 0.42,
    "filter": 0.33
   },
   "operations": {
    "eye_enlargement": 0.01,
    "face_slimming": 0.01,
    "skin_brightening": 0.01,
    "skin_smoothing": 0.93
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.0,
    "nose": 0.0,
    "mouth": 0.0,
    "skin": 0.0,
    "contour": 0.0
   },
   "evidence_peak": 0.001,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence on the eyes.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "479_706__f0119.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is fake (score 0.42).",
    "The evidence is concentrated on the eyes (mean evidence 0.00).",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 0.42). The evidence is concentrated on the eyes (mean evidence 0.00). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_fake:Deepfakes:347_314__f0045",
   "group": "ffpp_fake",
   "truth": "fake",
   "box": null,
   "src": "ffpp:Deepfakes",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.1,
    "face_slimming": 0.01,
    "skin_brightening": 0.11,
    "skin_smoothing": 0.1
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.89,
    "nose": 1.0,
    "mouth": 1.0,
    "skin": 0.85,
    "contour": 0.37
   },
   "evidence_peak": 0.999,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence across the whole face.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "347_314__f0045.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is spread over the whole face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is spread over the whole face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:Whitening_90:17364",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    0,
    0,
    1001,
    1024
   ],
   "src": "alibaba:Whitening_90:17364",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.27,
    "fake": 0.0,
    "filter": 0.73
   },
   "operations": {
    "eye_enlargement": 0.41,
    "face_slimming": 0.06,
    "skin_brightening": 0.16,
    "skin_smoothing": 0.03
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.79,
    "nose": 0.38,
    "mouth": 0.12,
    "skin": 0.45,
    "contour": 0.32
   },
   "evidence_peak": 0.922,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: operation unclear.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes"
    ],
    "named_region_area_frac": 0.1038,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.8321,
    "p_label_after_named_restored": 0.2022,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17364.png",
   "x0": "17364.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.73).",
    "The evidence is concentrated on the eyes (mean evidence 0.79).",
    "None of the four operations reaches the threshold of 0.5.",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.73). The evidence is concentrated on the eyes (mean evidence 0.79). None of the four operations reaches the threshold of 0.5. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:FaceLifting_90:17886",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    62,
    50,
    1024,
    1024
   ],
   "src": "alibaba:FaceLifting_90:17886",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.06,
    "fake": 0.0,
    "filter": 0.94
   },
   "operations": {
    "eye_enlargement": 0.01,
    "face_slimming": 0.88,
    "skin_brightening": 0.02,
    "skin_smoothing": 0.01
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.06,
    "nose": 0.08,
    "mouth": 0.68,
    "skin": 0.45,
    "contour": 0.71
   },
   "evidence_peak": 0.97,
   "named_parts": [
    "contour"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: face reshaped.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "contour"
    ],
    "named_region_area_frac": 0.2543,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.9489,
    "p_label_after_named_restored": 0.3007,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17886.png",
   "x0": "17886.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.94).",
    "The evidence is concentrated on the face contour (mean evidence 0.71).",
    "Operations at or above the threshold of 0.5: face slimming (0.88).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.94). The evidence is concentrated on the face contour (mean evidence 0.71). Operations at or above the threshold of 0.5: face slimming (0.88). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:EyeEnlarging_90:17001",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    0,
    55,
    960,
    1024
   ],
   "src": "alibaba:EyeEnlarging_90:17001",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.0,
    "fake": 0.0,
    "filter": 0.99
   },
   "operations": {
    "eye_enlargement": 0.01,
    "face_slimming": 0.01,
    "skin_brightening": 0.99,
    "skin_smoothing": 0.0
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.99,
    "nose": 0.99,
    "mouth": 0.99,
    "skin": 0.98,
    "contour": 0.95
   },
   "evidence_peak": 0.994,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: skin brightened.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes",
     "nose",
     "mouth",
     "skin",
     "contour"
    ],
    "named_region_area_frac": 0.4707,
    "named_region_restored_flips_decision": false,
    "p_label_before": 0.9916,
    "p_label_after_named_restored": 0.9717,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17001.png",
   "x0": "17001.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.99).",
    "The evidence is spread over the whole face.",
    "Operations at or above the threshold of 0.5: skin whitening (0.99).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.99). The evidence is spread over the whole face. Operations at or above the threshold of 0.5: skin whitening (0.99). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_real:607__f0366",
   "group": "ffpp_real",
   "truth": "real",
   "box": null,
   "src": "ffpp:real",
   "model": "clipe5_s20260929",
   "decision": "real",
   "probabilities": {
    "real": 0.66,
    "fake": 0.01,
    "filter": 0.34
   },
   "operations": {
    "eye_enlargement": 0.15,
    "face_slimming": 0.03,
    "skin_brightening": 0.01,
    "skin_smoothing": 0.09
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.0,
    "nose": 0.0,
    "mouth": 0.0,
    "skin": 0.0,
    "contour": 0.0
   },
   "evidence_peak": 0.001,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "No manipulation detected.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "decision is real: nothing to restore; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "607__f0366.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is real (score 0.66).",
    "No manipulation was detected on the face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is real (score 0.66). No manipulation was detected on the face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "part_forgery:donor:949__f0189__mouth",
   "group": "part_forgery",
   "truth": "fake",
   "box": null,
   "src": "partedit:donor:mouth",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.05,
    "face_slimming": 0.01,
    "skin_brightening": 0.14,
    "skin_smoothing": 0.01
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.0,
    "nose": 0.12,
    "mouth": 0.98,
    "skin": 0.24,
    "contour": 0.02
   },
   "evidence_peak": 0.998,
   "named_parts": [
    "mouth"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence on the mouth.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "true_part": "mouth",
   "restoration_test": {
    "available": true,
    "named_region": [
     "mouth"
    ],
    "named_region_area_frac": 0.05,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.9986,
    "p_label_after_named_restored": 0.0164,
    "harness_decision": "fake",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original",
    "footprint_area_frac": 0.091,
    "footprint_restored_flips_decision": true,
    "map_topk_restored_flips_decision": true
   },
   "image": "949__f0189__mouth.jpg",
   "x0": "949__f0189.jpg",
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is concentrated on the mouth (mean evidence 0.98).",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is concentrated on the mouth (mean evidence 0.98). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_fake:Deepfakes:630_623__f0079",
   "group": "ffpp_fake",
   "truth": "fake",
   "box": null,
   "src": "ffpp:Deepfakes",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.05,
    "face_slimming": 0.01,
    "skin_brightening": 0.08,
    "skin_smoothing": 0.15
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.99,
    "nose": 0.99,
    "mouth": 0.99,
    "skin": 0.94,
    "contour": 0.61
   },
   "evidence_peak": 0.999,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence across the whole face.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "630_623__f0079.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is spread over the whole face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is spread over the whole face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:FaceLifting_90:17364",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    0,
    0,
    1001,
    1024
   ],
   "src": "alibaba:FaceLifting_90:17364",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.26,
    "fake": 0.0,
    "filter": 0.74
   },
   "operations": {
    "eye_enlargement": 0.43,
    "face_slimming": 0.17,
    "skin_brightening": 0.05,
    "skin_smoothing": 0.02
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.83,
    "nose": 0.29,
    "mouth": 0.11,
    "skin": 0.52,
    "contour": 0.43
   },
   "evidence_peak": 0.921,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: operation unclear.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes"
    ],
    "named_region_area_frac": 0.1018,
    "named_region_restored_flips_decision": false,
    "p_label_before": 0.8397,
    "p_label_after_named_restored": 0.8577,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17364.png",
   "x0": "17364.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.74).",
    "The evidence is concentrated on the eyes (mean evidence 0.83).",
    "None of the four operations reaches the threshold of 0.5.",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.74). The evidence is concentrated on the eyes (mean evidence 0.83). None of the four operations reaches the threshold of 0.5. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_fake:NeuralTextures:026_012__f0088",
   "group": "ffpp_fake",
   "truth": "fake",
   "box": null,
   "src": "ffpp:NeuralTextures",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.28,
    "fake": 0.36,
    "filter": 0.36
   },
   "operations": {
    "eye_enlargement": 0.01,
    "face_slimming": 0.01,
    "skin_brightening": 0.0,
    "skin_smoothing": 0.87
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.0,
    "nose": 0.0,
    "mouth": 0.0,
    "skin": 0.0,
    "contour": 0.0
   },
   "evidence_peak": 0.001,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: skin smoothed.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "026_012__f0088.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is filter (score 0.36).",
    "The evidence is concentrated on the eyes (mean evidence 0.00).",
    "Operations at or above the threshold of 0.5: skin smoothing (0.87).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.36). The evidence is concentrated on the eyes (mean evidence 0.00). Operations at or above the threshold of 0.5: skin smoothing (0.87). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffhq_demo_edit:17040_white",
   "group": "ffhq_demo_edit",
   "truth": "filter",
   "box": [
    29,
    15,
    493,
    512
   ],
   "src": "ffhq:17040:white",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.0,
    "fake": 0.04,
    "filter": 0.96
   },
   "operations": {
    "eye_enlargement": 0.0,
    "face_slimming": 0.0,
    "skin_brightening": 1.0,
    "skin_smoothing": 0.0
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 1.0,
    "nose": 1.0,
    "mouth": 1.0,
    "skin": 1.0,
    "contour": 0.84
   },
   "evidence_peak": 1.0,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: skin brightened.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes",
     "nose",
     "mouth",
     "skin",
     "contour"
    ],
    "named_region_area_frac": 0.456,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.9708,
    "p_label_after_named_restored": 0.1372,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17040_white.jpg",
   "x0": "17040_x0.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.96).",
    "The evidence is spread over the whole face.",
    "Operations at or above the threshold of 0.5: skin whitening (1.00).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.96). The evidence is spread over the whole face. Operations at or above the threshold of 0.5: skin whitening (1.00). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:FaceLifting_90:17937",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    0,
    47,
    998,
    1024
   ],
   "src": "alibaba:FaceLifting_90:17937",
   "model": "clipe5_s20260929",
   "decision": "real",
   "probabilities": {
    "real": 0.86,
    "fake": 0.0,
    "filter": 0.14
   },
   "operations": {
    "eye_enlargement": 0.03,
    "face_slimming": 0.06,
    "skin_brightening": 0.01,
    "skin_smoothing": 0.03
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.0,
    "nose": 0.0,
    "mouth": 0.0,
    "skin": 0.0,
    "contour": 0.0
   },
   "evidence_peak": 0.0,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "No manipulation detected.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "decision is real: nothing to restore; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "17937.png",
   "x0": "17937.png",
   "t2_sentences_en": [
    "The model's decision is real (score 0.86).",
    "No manipulation was detected on the face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is real (score 0.86). No manipulation was detected on the face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "part_forgery:donor:128__f0138__mouth",
   "group": "part_forgery",
   "truth": "fake",
   "box": null,
   "src": "partedit:donor:mouth",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.0,
    "fake": 1.0,
    "filter": 0.0
   },
   "operations": {
    "eye_enlargement": 0.08,
    "face_slimming": 0.01,
    "skin_brightening": 0.08,
    "skin_smoothing": 0.12
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.0,
    "nose": 0.34,
    "mouth": 0.99,
    "skin": 0.23,
    "contour": 0.02
   },
   "evidence_peak": 0.999,
   "named_parts": [
    "mouth"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence on the mouth.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "true_part": "mouth",
   "restoration_test": {
    "available": true,
    "named_region": [
     "mouth"
    ],
    "named_region_area_frac": 0.0399,
    "named_region_restored_flips_decision": true,
    "p_label_before": 1.0,
    "p_label_after_named_restored": 0.0685,
    "harness_decision": "fake",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original",
    "footprint_area_frac": 0.1595,
    "footprint_restored_flips_decision": true,
    "map_topk_restored_flips_decision": true
   },
   "image": "128__f0138__mouth.jpg",
   "x0": "128__f0138.jpg",
   "t2_sentences_en": [
    "The model's decision is fake (score 1.00).",
    "The evidence is concentrated on the mouth (mean evidence 0.99).",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 1.00). The evidence is concentrated on the mouth (mean evidence 0.99). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffpp_fake:Face2Face:706_479__f0178",
   "group": "ffpp_fake",
   "truth": "fake",
   "box": null,
   "src": "ffpp:Face2Face",
   "model": "clipe5_s20260929",
   "decision": "fake",
   "probabilities": {
    "real": 0.07,
    "fake": 0.92,
    "filter": 0.01
   },
   "operations": {
    "eye_enlargement": 0.05,
    "face_slimming": 0.01,
    "skin_brightening": 0.01,
    "skin_smoothing": 0.61
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.75,
    "nose": 0.66,
    "mouth": 0.94,
    "skin": 0.67,
    "contour": 0.32
   },
   "evidence_peak": 0.964,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Forgery detected; evidence across the whole face.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "706_479__f0178.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is fake (score 0.92).",
    "The evidence is spread over the whole face.",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 0.92). The evidence is spread over the whole face. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "ffhq_demo_edit:17020_real",
   "group": "ffhq_demo_edit",
   "truth": "real",
   "box": [
    0,
    28,
    483,
    512
   ],
   "src": "ffhq:17020:real",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.4,
    "fake": 0.0,
    "filter": 0.6
   },
   "operations": {
    "eye_enlargement": 0.05,
    "face_slimming": 0.12,
    "skin_brightening": 0.33,
    "skin_smoothing": 0.05
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.52,
    "nose": 0.44,
    "mouth": 0.45,
    "skin": 0.41,
    "contour": 0.41
   },
   "evidence_peak": 0.65,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: operation unclear.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": false,
    "named_region_restored_flips_decision": null,
    "note": "no pixel-aligned original for this image; only the group statistic from the held-out set may be quoted, not a claim about this image"
   },
   "image": "17020_real.jpg",
   "x0": null,
   "t2_sentences_en": [
    "The model's decision is filter (score 0.60).",
    "The evidence is concentrated on the eyes (mean evidence 0.52).",
    "None of the four operations reaches the threshold of 0.5.",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.60). The evidence is concentrated on the eyes (mean evidence 0.52). None of the four operations reaches the threshold of 0.5. The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:EyeEnlarging_90:17156",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    68,
    34,
    996,
    1024
   ],
   "src": "alibaba:EyeEnlarging_90:17156",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.01,
    "fake": 0.0,
    "filter": 0.99
   },
   "operations": {
    "eye_enlargement": 0.99,
    "face_slimming": 0.01,
    "skin_brightening": 0.01,
    "skin_smoothing": 0.0
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.96,
    "nose": 0.49,
    "mouth": 0.1,
    "skin": 0.6,
    "contour": 0.39
   },
   "evidence_peak": 0.988,
   "named_parts": [
    "eyes"
   ],
   "whole_face": false,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: eyes enlarged.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes"
    ],
    "named_region_area_frac": 0.1051,
    "named_region_restored_flips_decision": true,
    "p_label_before": 0.993,
    "p_label_after_named_restored": 0.2519,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17156.png",
   "x0": "17156.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.99).",
    "The evidence is concentrated on the eyes (mean evidence 0.96).",
    "Operations at or above the threshold of 0.5: eye enlargement (0.99).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.99). The evidence is concentrated on the eyes (mean evidence 0.96). Operations at or above the threshold of 0.5: eye enlargement (0.99). The score is the model's raw output, not a calibrated probability."
  },
  {
   "id": "alibaba:FaceLifting_90:17001",
   "group": "alibaba",
   "truth": "filter",
   "box": [
    0,
    55,
    960,
    1024
   ],
   "src": "alibaba:FaceLifting_90:17001",
   "model": "clipe5_s20260929",
   "decision": "filter",
   "probabilities": {
    "real": 0.02,
    "fake": 0.0,
    "filter": 0.98
   },
   "operations": {
    "eye_enlargement": 0.0,
    "face_slimming": 0.04,
    "skin_brightening": 0.93,
    "skin_smoothing": 0.0
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.84,
    "nose": 0.9,
    "mouth": 0.95,
    "skin": 0.9,
    "contour": 0.86
   },
   "evidence_peak": 0.978,
   "named_parts": [
    "whole face"
   ],
   "whole_face": true,
   "landmarks_found": true,
   "template_text": "Beautified, identity kept: skin brightened.",
   "calibration_note": "scores are raw model outputs, not calibrated probabilities",
   "restoration_test": {
    "available": true,
    "named_region": [
     "eyes",
     "nose",
     "mouth",
     "skin",
     "contour"
    ],
    "named_region_area_frac": 0.4441,
    "named_region_restored_flips_decision": false,
    "p_label_before": 0.9768,
    "p_label_after_named_restored": 0.974,
    "harness_decision": "filter",
    "note": "computed on this image offline (x0 available); region = landmark part mask(s) named by rule B, dilated 25 px at 380 px, restored from the original"
   },
   "image": "17001.png",
   "x0": "17001.png",
   "t2_sentences_en": [
    "The model's decision is filter (score 0.98).",
    "The evidence is spread over the whole face.",
    "Operations at or above the threshold of 0.5: skin whitening (0.93).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.98). The evidence is spread over the whole face. Operations at or above the threshold of 0.5: skin whitening (0.93). The score is the model's raw output, not a calibrated probability."
  },
  {
   "probabilities": {
    "real": 0.05,
    "fake": 0.1,
    "filter": 0.85
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.62,
    "nose": 0.31,
    "mouth": 0.55,
    "skin": 0.58,
    "contour": 0.12
   },
   "whole_face": false,
   "id": "synthetic:two_parts_two_ops",
   "decision": "filter",
   "named_parts": [
    "eyes",
    "mouth"
   ],
   "operations": {
    "eye_enlargement": 0.66,
    "face_slimming": 0.12,
    "skin_brightening": 0.08,
    "skin_smoothing": 0.91
   },
   "t2_sentences_en": [
    "The model's decision is filter (score 0.85).",
    "The evidence is concentrated on the eyes (mean evidence 0.62) and the mouth (mean evidence 0.55).",
    "Operations at or above the threshold of 0.5: eye enlargement (0.66), skin smoothing (0.91).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.85). The evidence is concentrated on the eyes (mean evidence 0.62) and the mouth (mean evidence 0.55). Operations at or above the threshold of 0.5: eye enlargement (0.66), skin smoothing (0.91). The score is the model's raw output, not a calibrated probability."
  },
  {
   "probabilities": {
    "real": 0.05,
    "fake": 0.1,
    "filter": 0.85
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.62,
    "nose": 0.31,
    "mouth": 0.55,
    "skin": 0.58,
    "contour": 0.12
   },
   "whole_face": false,
   "id": "synthetic:three_parts_four_ops",
   "decision": "filter",
   "named_parts": [
    "eyes",
    "skin",
    "mouth"
   ],
   "operations": {
    "eye_enlargement": 0.5,
    "face_slimming": 0.77,
    "skin_brightening": 0.93,
    "skin_smoothing": 0.99
   },
   "t2_sentences_en": [
    "The model's decision is filter (score 0.85).",
    "The evidence is concentrated on the eyes (mean evidence 0.62), the skin (mean evidence 0.58) and the mouth (mean evidence 0.55).",
    "Operations at or above the threshold of 0.5: eye enlargement (0.50), face slimming (0.77), skin whitening (0.93), skin smoothing (0.99).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.85). The evidence is concentrated on the eyes (mean evidence 0.62), the skin (mean evidence 0.58) and the mouth (mean evidence 0.55). Operations at or above the threshold of 0.5: eye enlargement (0.50), face slimming (0.77), skin whitening (0.93), skin smoothing (0.99). The score is the model's raw output, not a calibrated probability."
  },
  {
   "probabilities": {
    "real": 0.01,
    "fake": 0.97,
    "filter": 0.02
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.62,
    "nose": 0.31,
    "mouth": 0.55,
    "skin": 0.58,
    "contour": 0.12
   },
   "whole_face": false,
   "id": "synthetic:fake_two_parts",
   "decision": "fake",
   "named_parts": [
    "nose",
    "mouth"
   ],
   "operations": {
    "eye_enlargement": 0.1,
    "face_slimming": 0.1,
    "skin_brightening": 0.1,
    "skin_smoothing": 0.1
   },
   "t2_sentences_en": [
    "The model's decision is fake (score 0.97).",
    "The evidence is concentrated on the nose (mean evidence 0.31) and the mouth (mean evidence 0.55).",
    null,
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is fake (score 0.97). The evidence is concentrated on the nose (mean evidence 0.31) and the mouth (mean evidence 0.55). The score is the model's raw output, not a calibrated probability."
  },
  {
   "probabilities": {
    "real": 0.05,
    "fake": 0.1,
    "filter": 0.85
   },
   "operation_threshold": 0.5,
   "evidence_mean_per_part": {
    "eyes": 0.62,
    "nose": 0.31,
    "mouth": 0.55,
    "skin": 0.58,
    "contour": 0.12
   },
   "whole_face": false,
   "id": "synthetic:filter_boundary_049",
   "decision": "filter",
   "named_parts": [
    "contour"
   ],
   "operations": {
    "eye_enlargement": 0.49,
    "face_slimming": 0.5,
    "skin_brightening": 0.2,
    "skin_smoothing": 0.3
   },
   "t2_sentences_en": [
    "The model's decision is filter (score 0.85).",
    "The evidence is concentrated on the face contour (mean evidence 0.12).",
    "Operations at or above the threshold of 0.5: face slimming (0.50).",
    "The score is the model's raw output, not a calibrated probability."
   ],
   "t2_text_en": "The model's decision is filter (score 0.85). The evidence is concentrated on the face contour (mean evidence 0.12). Operations at or above the threshold of 0.5: face slimming (0.50). The score is the model's raw output, not a calibrated probability."
  }
 ]
};
