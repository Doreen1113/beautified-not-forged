"""The paper's main model, in one place (PRE_DECLARED Addendum 5).

Until 2026-10-05 the main model was clipe4_s20260929, the epoch chosen by filter F1. The Addendum 5 re-run clipe4r_s20260929
(epoch chosen on validation data by C2) replaces it; clipe4r_s20260930 is the second seed. Scripts that used to hard-code the
tag import it from here, and write their outputs with SUFFIX so that the results of the earlier checkpoint stay on disk.
Set RU_MAIN_TAG to run a script for another checkpoint.
"""
import os

OLD_TAG = "clipe4_s20260929"
MAIN_TAG = os.environ.get("RU_MAIN_TAG", "clipe5_s20260929")   # 2026-10-11: RU5 (Addendum 6) is the paper's three-way model
SEED2_TAG = "clipe5_s20260930"
LITE_TAG = "ru4e_effb4_s20260929"
SUFFIX = "" if MAIN_TAG == OLD_TAG else f"_{MAIN_TAG}"
# names of the same checkpoints in the Celeb-DF-B / video-level registries and in the part-edit harness
CB_NAME = {"clipe4_s20260929": "RU-clipe4", "clipe4r_s20260929": "RU-clipe4r", "clipe4r_s20260930": "RU-clipe4r-s2", "clipe5_s20260929": "RU-clipe5", "clipe5_s20260930": "RU-clipe5-s2"}
CGD_ARM = {"clipe4_s20260929": ("RUCLIPE4", 20260929), "clipe4r_s20260929": ("RUCLIPE4R", 20260929), "clipe4r_s20260930": ("RUCLIPE4R", 20260930), "clipe5_s20260929": ("RUCLIPE5", 20260929), "clipe5_s20260930": ("RUCLIPE5", 20260930)}
