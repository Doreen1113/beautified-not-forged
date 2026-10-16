"""
Artifact Type Classifier (4-Class Fine-grained Filter Detector)
- Backbone: ShuffleNetV2 1.0x (Lightweight, Mobile-friendly)
- Classes: eye_enlarging / face_reshaping / smoothing / whitening
- Dataset Splits: train / val / test (Direct Folder Ingestion)
- Metrics: Acc, Macro-F1, Precision, Recall, Macro-AUROC, Confusion Matrix
"""

import os
import csv
import time
from pathlib import Path
from PIL import Image
import numpy as np

import torch
import torch.nn as nn
import torchvision.models as tv_models
from torchvision import transforms
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
)
from IPython.display import FileLink

# ──────────────────────────────────────────────
# 1. Kaggle 路徑與超參數設定
# ──────────────────────────────────────────────
# 資料集掛載根目錄（請確認與右側 Input 中的資料夾名稱一致）
DATASET_ROOT = "/kaggle/input/datasets/angelyu33/filter-dataset"

# 權重檔與指標紀錄輸出路徑（必須指向可寫入的 working 目錄）
SAVE_PATH    = "/kaggle/working/artifact_classifier_v3.pth"
RESULTS_CSV  = "/kaggle/working/artifact_classifier_v3_results.csv"

# 4 類濾鏡細分類（依照字母排序對齊 ImageFolder 慣例）
CLASSES      = ["eye_enlarging", "face_reshaping", "smoothing", "whitening"]
CLASS_INDEX  = {c: i for i, c in enumerate(CLASSES)}
NUM_CLASSES  = len(CLASSES)

EPOCHS       = 15
BATCH_SIZE   = 64
LR           = 1e-3

# ──────────────────────────────────────────────
# 2. 資料集類別與影像預處理
# ──────────────────────────────────────────────
transform_train = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.ColorJitter(brightness=0.2, contrast=0.2),
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
])

transform_val = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5]),
])

class ArtifactDataset(Dataset):
    def __init__(self, paths, labels, transform=None):
        self.paths = paths
        self.labels = labels
        self.transform = transform

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, idx):
        img = Image.open(self.paths[idx]).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, self.labels[idx]

def collect_split_data(root, split_name):
    """
    自動在 DATASET_ROOT 下遞迴搜尋 train / val / test 分割目錄，
    並依照 4 類濾鏡子資料夾讀取圖檔路徑與數值標籤。
    """
    matched = list(Path(root).rglob(split_name))
    if not matched:
        raise FileNotFoundError(f"找不到分割資料夾: {split_name}，請確認資料集結構。")
    split_dir = str(matched[0])

    paths, labels = [], []
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp"}
    
    for cls in CLASSES:
        cls_path = os.path.join(split_dir, cls)
        if not os.path.isdir(cls_path):
            continue
        for f in os.listdir(cls_path):
            if Path(f).suffix.lower() in valid_exts:
                paths.append(os.path.join(cls_path, f))
                labels.append(CLASS_INDEX[cls])
                
    return paths, labels

# ──────────────────────────────────────────────
# 3. 模型建構與評估邏輯
# ──────────────────────────────────────────────
def build_model():
    model = tv_models.shufflenet_v2_x1_0(
        weights=tv_models.ShuffleNet_V2_X1_0_Weights.DEFAULT
    )
    model.fc = nn.Linear(model.fc.in_features, NUM_CLASSES)
    return model

def evaluate(model, loader, device):
    """
    驗證評估：計算 Accuracy, Macro-F1, Precision, Recall, Macro-AUROC
    """
    model.eval()
    all_preds, all_labels, all_probs = [], [], []
    
    with torch.no_grad():
        for imgs, labels in loader:
            logits = model(imgs.to(device))
            probs  = torch.softmax(logits, dim=1)
            preds  = probs.argmax(dim=1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())
            all_probs.extend(probs.cpu().numpy())
            
    all_preds  = np.array(all_preds)
    all_labels = np.array(all_labels)
    all_probs  = np.array(all_probs)

    acc   = (all_preds == all_labels).mean()
    f1    = f1_score(all_labels, all_preds, average="macro")
    prec  = precision_score(all_labels, all_preds, average="macro", zero_division=0)
    rec   = recall_score(all_labels, all_preds, average="macro", zero_division=0)
    
    try:
        auroc = roc_auc_score(all_labels, all_probs, multi_class="ovr", average="macro")
    except Exception:
        auroc = 0.0

    return acc, f1, prec, rec, auroc

# ──────────────────────────────────────────────
# 4. 主執行流程
# ──────────────────────────────────────────────
if __name__ == "__main__":
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"執行裝置: {device}")
    if device == "cuda":
        print(f"顯卡型號: {torch.cuda.get_device_name(0)}")

    # 1. 載入 3 個獨立資料集
    tr_p, tr_l = collect_split_data(DATASET_ROOT, "train")
    va_p, va_l = collect_split_data(DATASET_ROOT, "val")
    te_p, te_l = collect_split_data(DATASET_ROOT, "test")

    print(f"影像數量 -> Train: {len(tr_p)} | Val: {len(va_p)} | Test: {len(te_p)}")

    train_ds = ArtifactDataset(tr_p, tr_l, transform_train)
    val_ds   = ArtifactDataset(va_p, va_l, transform_val)
    test_ds  = ArtifactDataset(te_p, te_l, transform_val)

    # Kaggle 環境穩定設置：num_workers=2
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=2, pin_memory=True)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=2, pin_memory=True)
    test_loader  = DataLoader(test_ds,  batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=2, pin_memory=True)

    # 2. 初始化模型、優化器與學習率排程
    model     = build_model().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS)
    criterion = nn.CrossEntropyLoss()

    best_val_f1 = 0.0
    records = []

    print("\n" + "=" * 60)
    print("開始訓練 (Training Loop)...")
    print("=" * 60)

    for epoch in range(1, EPOCHS + 1):
        model.train()
        t0 = time.time()
        total_loss = 0.0

        for imgs, labels_b in train_loader:
            imgs, labels_b = imgs.to(device), labels_b.to(device)
            optimizer.zero_grad()
            loss = criterion(model(imgs), labels_b)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * imgs.size(0)

        scheduler.step()

        # 每個 Epoch 結束在 Val 集驗證
        acc, f1, prec, rec, auroc = evaluate(model, val_loader, device)
        avg_loss = total_loss / len(train_ds)
        elapsed  = time.time() - t0

        print(f"[{epoch:02d}/{EPOCHS}] loss={avg_loss:.4f}  "
              f"Acc={acc:.4f}  F1={f1:.4f}  Prec={prec:.4f}  "
              f"Rec={rec:.4f}  AUROC={auroc:.4f}  ({elapsed:.1f}s)")

        records.append([epoch, f"{avg_loss:.4f}", f"{acc:.4f}", f"{f1:.4f}",
                        f"{prec:.4f}", f"{rec:.4f}", f"{auroc:.4f}"])

        # 以 Val Macro-F1 作為權重儲存依據
        if f1 > best_val_f1:
            best_val_f1 = f1
            torch.save(model.state_dict(), SAVE_PATH)
            print(f"  -> 已儲存最佳模型 (Val F1={best_val_f1:.4f})")

    print("\n" + "=" * 60)
    print(f"訓練完成！最佳 Val F1: {best_val_f1:.4f}")
    print(f"權重儲存位置: {SAVE_PATH}")
    print("=" * 60)

    # 3. 輸出每輪訓練紀錄 CSV
    with open(RESULTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["epoch", "loss", "acc", "f1_macro", "prec_macro", "rec_macro", "auroc"])
        writer.writerows(records)
    print(f"指標紀錄已儲存至: {RESULTS_CSV}")

    # 4. 載入最佳權重，在獨立 Test Set 進行最終盲測
    print("\n" + "=" * 60)
    print("執行獨立測試集最終評估 (Held-out Test Evaluation)...")
    print("=" * 60)
    model.load_state_dict(torch.load(SAVE_PATH, map_location=device))
    model.eval()

    test_preds, test_trues = [], []
    with torch.no_grad():
        for imgs, labels_b in test_loader:
            preds = model(imgs.to(device)).argmax(dim=1)
            test_preds.extend(preds.cpu().numpy())
            test_trues.extend(labels_b.numpy())

    print("\n【分類效能評估報告 (Classification Report)】")
    print(classification_report(test_trues, test_preds, target_names=CLASSES, digits=4))

    print("【混淆矩陣 (Confusion Matrix)】")
    print(confusion_matrix(test_trues, test_preds))