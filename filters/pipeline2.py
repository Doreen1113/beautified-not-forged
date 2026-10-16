"""整合 4 個 filter 腳本，對 10 張 AIGuard/real 圖跑完並輸出 avg metrics table。

執行環境：mediapipe_env
    conda activate mediapipe_env
    python filters/pipeline.py
"""

import os
import random
import warnings
import cv2
import numpy as np
import pandas as pd
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
from skimage.metrics import structural_similarity as ssim
import matplotlib
matplotlib.use("Agg")  # 不開視窗，直接存檔
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore")

BASE   = r"C:\Users\oooba\project\AIGC_Detection"
REAL   = r"C:\CVLab\train"
MODEL  = os.path.join(BASE, "face_landmarker.task")
OUTPUT_DIR = os.path.join(BASE, "filter_data", "clean_output")        # 輸出濾鏡圖根目錄
CLEAN_TXT  = os.path.join(OUTPUT_DIR, "clean_paths.txt")               # 供分類器讀取的 txt

# 【關鍵過濾設定】：每個角色只取幾張照片（建議設 3 ~ 5 張）
SAMPLES_PER_PERSON = 3

# ──────────────────────────────────────────────
# 讀取圖檔
# ──────────────────────────────────────────────
def select_filtered_images(samples_per_person=3, seed=42):
    """
    依檔名中的角色 ID 分組，並對每個人只保留固定數量的影格照片。
    例：018_f0165.jpg -> 角色為 018
    """
    random.seed(seed)
    exts = ('.jpg', '.jpeg', '.png', '.JPG', '.PNG')
    
    if not os.path.exists(REAL):
        print(f"錯誤：找不到來源路徑 {REAL}")
        return []

    # 1. 抓取目錄下所有圖片
    all_files = [os.path.join(REAL, f) for f in os.listdir(REAL) if f.endswith(exts)]
    print(f"原始資料夾內共有 {len(all_files)} 張影格圖片。")

    # 2. 按照角色 ID (檔名前綴) 分組
    person_dict = {}
    for path in all_files:
        filename = os.path.basename(path)
        # 以底線分割，抓取前綴作為角色 ID (若無底線則以檔名作為單一 ID)
        person_id = filename.split('_')[0] if '_' in filename else filename
        if person_id not in person_dict:
            person_dict[person_id] = []
        person_dict[person_id].append(path)

    print(f"分析完成：共包含 {len(person_dict)} 位獨立角色。")

    # 3. 每個角色只挑選指定張數 (若該角色總張數不足則全取)
    selected_paths = []
    for pid, paths in person_dict.items():
        # 排序後均勻抽樣，能取到該角色在影片不同時間點的狀態
        sorted_paths = sorted(paths)
        if len(sorted_paths) <= samples_per_person:
            chosen = sorted_paths
        else:
            # 均勻間隔取樣 (比純隨機更能涵蓋不同表情)
            step = len(sorted_paths) / samples_per_person
            chosen = [sorted_paths[int(i * step)] for i in range(samples_per_person)]
            
        selected_paths.extend(chosen)

    print(f"過濾完成！從四萬多張中篩選出 {len(selected_paths)} 張具代表性的人像進行轉換。\n")
    return selected_paths

# ──────────────────────────────────────────────
# Helper: MediaPipe-based face bbox + skin mask (shared by Smoothing & Whitening)
# ──────────────────────────────────────────────
def _face_bbox_from_mp(landmarks):
    """從 MediaPipe face mesh 468 點算出臉的 bounding box (x, y, w, h)。"""
    xs, ys = landmarks[:, 0], landmarks[:, 1]
    x, y = int(np.min(xs)), int(np.min(ys))
    w, h = int(np.max(xs)) - x, int(np.max(ys)) - y
    return (x, y, w, h)

def _skin_mask_mp(image, face):
    x, y, w, h = face
    fmask = np.zeros(image.shape[:2], np.uint8)
    cv2.ellipse(fmask, (x+w//2, y+int(h*0.52)), (int(w*0.44), int(h*0.48)), 0, 0, 360, 255, -1)
    ycrcb = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    smask = cv2.inRange(ycrcb, np.array([0,133,77]), np.array([255,173,127]))
    mask = cv2.bitwise_and(fmask, smask)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,7))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    mask = cv2.GaussianBlur(mask, (21,21), 0)
    return mask if np.count_nonzero(mask > 32) > 300 else None


# ──────────────────────────────────────────────
# Common image metrics
# ──────────────────────────────────────────────
def common_metrics(before, after):
    psnr = float(cv2.PSNR(before, after))
    b_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    a_gray = cv2.cvtColor(after,  cv2.COLOR_BGR2GRAY)
    ssim_val = float(ssim(b_gray, a_gray, data_range=255))
    return psnr, ssim_val


# ══════════════════════════════════════════════
# Filter 1: Skin Smoothing  (bilateral filter)
# ══════════════════════════════════════════════
def run_smoothing(image):
    lm = _get_landmarks(image)
    if lm is None:
        return None
    face = _face_bbox_from_mp(lm)
    mask = _skin_mask_mp(image, face)
    if mask is None:
        return None

    x, y, w, h = face
    roi = image[y:y+h, x:x+w].copy()
    mask_roi = mask[y:y+h, x:x+w]

    smoothed_roi = cv2.bilateralFilter(roi, 15, 80, 80)
    skin_px = mask_roi > 64
    result = image.copy()
    result[y:y+h, x:x+w][skin_px] = smoothed_roi[skin_px]

    # metric: Laplacian variance reduction in skin region
    lap_before = cv2.Laplacian(cv2.cvtColor(image,  cv2.COLOR_BGR2GRAY), cv2.CV_32F)
    lap_after  = cv2.Laplacian(cv2.cvtColor(result, cv2.COLOR_BGR2GRAY), cv2.CV_32F)
    valid = mask > 64
    var_b = float(np.mean(lap_before[valid]**2))
    var_a = float(np.mean(lap_after[valid]**2))
    texture_reduction_pct = (var_b - var_a) / var_b * 100 if var_b > 0 else 0.0

    psnr, ssim_val = common_metrics(image, result)
    return {"psnr": psnr, "ssim": ssim_val,
            "specific_label": "texture_reduction_%",
            "specific_value": round(texture_reduction_pct, 2),
            "_after": result}


# ══════════════════════════════════════════════
# Filter 2: Whitening
# ══════════════════════════════════════════════
def run_whitening(image, strength=0.15):
    lm = _get_landmarks(image)
    if lm is None:
        return None
    face = _face_bbox_from_mp(lm)
    mask = _skin_mask_mp(image, face)
    if mask is None:
        return None

    mask_f = mask.astype(np.float32) / 255.0
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab[:,:,0] += strength * (255.0 - lab[:,:,0])
    brightened = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
    hsv = cv2.cvtColor(brightened, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:,:,1] *= 1.0 - 0.18 * strength
    whitened = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
    blend = mask_f[:,:,None]
    result = np.clip(image.astype(np.float32)*(1-blend) + whitened.astype(np.float32)*blend, 0, 255).astype(np.uint8)

    valid = mask > 64
    lab_b = cv2.cvtColor(image,  cv2.COLOR_BGR2LAB)
    lab_a = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
    brightness_delta = float(np.mean(lab_a[:,:,0][valid]) - np.mean(lab_b[:,:,0][valid]))

    psnr, ssim_val = common_metrics(image, result)
    return {"psnr": psnr, "ssim": ssim_val,
            "specific_label": "brightness_delta(L)",
            "specific_value": round(brightness_delta, 2),
            "_after": result}


# ══════════════════════════════════════════════
# Filter 3: Eye Enlarging  (mediapipe solutions)
# ══════════════════════════════════════════════
_face_mesh = None

def _get_face_mesh():
    global _face_mesh
    if _face_mesh is None:
        _face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True, max_num_faces=1,
            refine_landmarks=False, min_detection_confidence=0.5)
    return _face_mesh

LEFT_EYE  = (33, 133, 159, 145)
RIGHT_EYE = (362, 263, 386, 374)
FACE_W    = (234, 454)

def _get_landmarks(image):
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    res = _get_face_mesh().process(rgb)
    if not res.multi_face_landmarks:
        return None
    h, w = image.shape[:2]
    return np.array([(lm.x*w, lm.y*h)
                     for lm in res.multi_face_landmarks[0].landmark], np.float32)

def _eye_warp(image, landmarks, scale=1.18, radius_factor=1.70):
    h, w = image.shape[:2]
    result = image.copy()
    for eye_idx in (LEFT_EYE, RIGHT_EYE):
        pts = landmarks[list(eye_idx)]
        center = np.mean(pts, axis=0)
        eye_w = np.linalg.norm(landmarks[eye_idx[0]] - landmarks[eye_idx[1]])
        radius = max(eye_w * radius_factor, 8.0)
        cx, cy = center

        x0 = max(0, int(cx - radius)); x1 = min(w, int(cx + radius + 1))
        y0 = max(0, int(cy - radius)); y1 = min(h, int(cy + radius + 1))
        gx, gy = np.meshgrid(np.arange(x0, x1, dtype=np.float32),
                              np.arange(y0, y1, dtype=np.float32))
        dx, dy = gx - cx, gy - cy
        nd = np.clip(np.sqrt(dx**2 + dy**2) / radius, 0.0, 1.0)
        ls = 1.0 + (scale - 1.0) * (1.0 - nd)**2
        map_x = (cx + dx / ls).astype(np.float32)
        map_y = (cy + dy / ls).astype(np.float32)
        roi = cv2.remap(image, map_x, map_y, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT_101)
        alpha = np.clip((1.0 - nd) / 0.18, 0.0, 1.0)[:,:,None]
        blended = image[y0:y1, x0:x1].astype(np.float32)*(1-alpha) + roi.astype(np.float32)*alpha
        result[y0:y1, x0:x1] = np.clip(blended, 0, 255).astype(np.uint8)
    return result

def run_eye_enlarging(image, scale=1.18):
    lm = _get_landmarks(image)
    if lm is None:
        return None
    result = _eye_warp(image, lm, scale)
    lm_after = _get_landmarks(result)

    def eye_ratio(pts):
        le = (np.linalg.norm(pts[LEFT_EYE[0]] - pts[LEFT_EYE[1]]) +
              np.linalg.norm(pts[RIGHT_EYE[0]] - pts[RIGHT_EYE[1]])) / 2
        fw = np.linalg.norm(pts[FACE_W[0]] - pts[FACE_W[1]])
        return le / fw if fw > 0 else 0.0

    ratio_before = eye_ratio(lm)
    ratio_after  = eye_ratio(lm_after) if lm_after is not None else ratio_before
    ratio_change_pct = float((ratio_after - ratio_before) / ratio_before * 100) if ratio_before > 0 else 0.0

    psnr, ssim_val = common_metrics(image, result)
    return {"psnr": psnr, "ssim": ssim_val,
            "specific_label": "eye_ratio_change_%",
            "specific_value": round(ratio_change_pct, 2),
            "_after": result}


# ══════════════════════════════════════════════
# Filter 4: Lower-Cheek / Jawline Reshaping (下臉頰與下顎瘦臉)
# ══════════════════════════════════════════════
_landmarker = None

def _get_landmarker():
    global _landmarker
    if _landmarker is None:
        with open(MODEL, "rb") as f:
            model_data = f.read()
        opts = vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(model_asset_buffer=model_data),
            num_faces=1)
        _landmarker = vision.FaceLandmarker.create_from_options(opts)
    return _landmarker

def _get_landmarks_tasks(image_bgr):
    rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    res = _get_landmarker().detect(mp_img)
    if not res.face_landmarks:
        return None
    h, w = image_bgr.shape[:2]
    return np.array([[lm.x*w, lm.y*h] for lm in res.face_landmarks[0]], np.float32)

def run_face_reshaping(image, shrink_strength=0.18):
    """
    針對臉頰以下（下顎骨/下頰輪廓）進行內縮收窄。
    錨點選用 MediaPipe 468 點中的下顎兩側點：
      - 172: 左側下顎線 (Lower Left Cheek / Jaw)
      - 397: 右側下顎線 (Lower Right Cheek / Jaw)
    收縮中心選用下巴頂點：
      - 152: 下巴底端中心 (Chin Tip)
    """
    pts = _get_landmarks_tasks(image)
    if pts is None:
        return None
    h, w = image.shape[:2]

    # 目標中心改為下巴尖端 (pts[152])，形成 V 臉向上向內收斂
    chin_center = pts[152]

    map_x, map_y = np.meshgrid(np.arange(w, dtype=np.float32),
                               np.arange(h, dtype=np.float32))

    # 以左右顴骨距離作為臉寬基準，計算下顎的作用半徑
    cheek_dist = float(np.linalg.norm(pts[234] - pts[454]))
    radius = max(cheek_dist * 0.22, 25.0)

    # 左右下顎錨點：172 (左下頰), 397 (右下頰)
    lower_jaw_indices = (172, 397)

    for jaw_idx in lower_jaw_indices:
        cx, cy = pts[jaw_idx]

        # 計算從下顎輪廓指向下巴尖端 (chin_center) 的向量
        vec = chin_center - np.array([cx, cy], dtype=np.float32)
        vec_len = np.linalg.norm(vec)
        if vec_len > 0:
            dir_vec = (vec / vec_len) * (radius * shrink_strength)
        else:
            continue

        x0, x1 = max(0, int(cx - radius)), min(w, int(cx + radius + 1))
        y0, y1 = max(0, int(cy - radius)), min(h, int(cy + radius + 1))

        gx = map_x[y0:y1, x0:x1]
        gy = map_y[y0:y1, x0:x1]

        dx = gx - cx
        dy = gy - cy
        dist = np.sqrt(dx**2 + dy**2)

        # 權重衰減
        within = dist < radius
        ratio = (1.0 - dist / radius)
        weight = np.where(within, ratio * ratio, 0.0)

        # 邊界保護：若 y 座標高於顴骨或鼻下緣 (pts[2] 鼻底)，減輕變形，確保只改臉頰以下
        nose_bottom_y = pts[2][1]
        vertical_mask = np.clip((gy - nose_bottom_y) / (radius * 0.5), 0.0, 1.0)
        weight *= vertical_mask

        # 反向重映射內縮
        map_x[y0:y1, x0:x1] -= dir_vec[0] * weight
        map_y[y0:y1, x0:x1] -= dir_vec[1] * weight

    result = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)
    
    return {"_after": result}


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
FILTERS = {
    "Smoothing":     run_smoothing,
    "Whitening":     run_whitening,
    "Eye Enlarging": run_eye_enlarging,
    "Face Reshaping":run_face_reshaping,
}

def save_comparison(before, after, out_path, filter_name):
    """存 before/after 左右對比圖，標題在圖上方（matplotlib 樣式）。"""
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(cv2.cvtColor(before, cv2.COLOR_BGR2RGB))
    axes[0].set_title("Before (Original)", fontsize=14, pad=8)
    axes[0].axis("off")
    axes[1].imshow(cv2.cvtColor(after, cv2.COLOR_BGR2RGB))
    axes[1].set_title(f"After ({filter_name})", fontsize=14, pad=8)
    axes[1].axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=120, bbox_inches="tight")
    plt.close(fig)


def main():
    images = select_filtered_images(samples_per_person=SAMPLES_PER_PERSON)
    print(f"Selected {len(images)} images\n")

    out_root = os.path.join(BASE, "filter_data", "custom_dataset")
    os.makedirs(out_root, exist_ok=True)
    os.makedirs(os.path.dirname(CLEAN_TXT), exist_ok=True)

    all_generated_paths = []

    for filter_name, fn in FILTERS.items():
        filter_slug = filter_name.lower().replace(" ", "_")
        filter_dir = os.path.join(out_root, filter_slug)
        os.makedirs(filter_dir, exist_ok=True)
        print(f"[{filter_name}] 開始處理...")

        count = 0
        for img_path in images:
            img = cv2.imread(img_path)
            if img is None:
                continue
            try:
                res = fn(img)
                if res is None or "_after" not in res:
                    continue

                stem = os.path.splitext(os.path.basename(img_path))[0]
                out_file = os.path.join(filter_dir, f"{stem}.png")

                # 直接儲存純淨濾鏡圖（不要再拼 before/after 對比圖）
                cv2.imwrite(out_file, res["_after"])
                all_generated_paths.append(out_file)
                count += 1
            except Exception as e:
                print(f"  ERROR {os.path.basename(img_path)}: {e}")

        print(f"  -> {filter_name} 完成，成功生成 {count} 張\n")

    # 寫入 clean_paths.txt 供 train_artifact_classifier_v3.py 讀取
    with open(CLEAN_TXT, "w", encoding="utf-8") as f:
        for p in all_generated_paths:
            f.write(f"{p}\n")

    print("=" * 60)
    print(f"全部完成！共產出 {len(all_generated_paths)} 張訓練圖片。")
    print(f"路徑清單已存至: {CLEAN_TXT}")

    print("=" * 80)
    print("FILTER PIPELINE — AVERAGE METRICS TABLE (10 images)")
    print("=" * 80)
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))

    out_csv = os.path.join(BASE, "results", "filter_metrics.csv")
    df.to_csv(out_csv, index=False)
    print(f"\nSaved → {out_csv}")

    # also save per-image detail
    detail_csv = os.path.join(BASE, "results", "filter_metrics_detail.csv")
    pd.DataFrame(per_image_rows).to_csv(detail_csv, index=False)
    print(f"Detail → {detail_csv}")


if __name__ == "__main__":
    main()
