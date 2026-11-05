# Addendum 52: ICT / ICT-Ref under smoothing (Celeb-DF-v2 test, Celeb-real vs Celeb-synthesis; n 3504: 836 genuine / 2668 forged; Addendum 51 set n 3504 intersected with ICT alignment success in all five conditions)

ICT alignment failure % (of 3504 probes): {"untreated": {"all": 0.0, "genuine": 0.0, "forged": 0.0}, "bil15": {"all": 0.0, "genuine": 0.0, "forged": 0.0}, "bil21": {"all": 0.0, "genuine": 0.0, "forged": 0.0}, "fl06": {"all": 0.0, "genuine": 0.0, "forged": 0.0}, "fl12": {"all": 0.0, "genuine": 0.0, "forged": 0.0}}

Weak RetinaFace detections (0.02 < score < 0.5) %: {'untreated': 0.0, 'bil15': 0.0, 'bil21': 0.0, 'fl06': 0.0, 'fl12': 0.0}; mean black-border share of the aligned 317 crop %: {'untreated': 5.88, 'bil15': 5.84, 'bil21': 5.46, 'fl06': 5.95, 'fl12': 5.87}

Reference sets: ours 1080 aligned frames over 54 identities (Addendum 51 videos/frames, ICT alignment); released ref.pkl 2420 entries.

AUC per condition; brackets = 95% CI of (AUC under condition - AUC untreated), bootstrap over claimed identities (500, seed 0).

| score | untreated | bil15 | bil21 | fl06 | fl12 |
|---|---|---|---|---|---|
| ICT | 0.7898 | 0.6789 (-0.1109) [-0.1457, -0.0806] | 0.6664 (-0.1234) [-0.1695, -0.0831] | 0.7518 (-0.0380) [-0.0513, -0.0259] | 0.6983 (-0.0915) [-0.126, -0.0604] |
| ICT-Ref (ours ref) | 0.863 | 0.7811 (-0.0819) [-0.1068, -0.0599] | 0.7546 (-0.1084) [-0.1462, -0.0686] | 0.8355 (-0.0276) [-0.0364, -0.0197] | 0.7828 (-0.0803) [-0.102, -0.0568] |
| ICT-Ref (released ref.pkl) | 0.9325 | 0.8804 (-0.0521) [-0.0684, -0.0362] | 0.8402 (-0.0923) [-0.119, -0.0649] | 0.9189 (-0.0136) [-0.019, -0.0079] | 0.8881 (-0.0444) [-0.0604, -0.0275] |
| ICT-Ref (claimed-id ref, exploratory) | 0.793 | 0.7111 (-0.0819) [-0.1118, -0.0558] | 0.7024 (-0.0906) [-0.1318, -0.0501] | 0.7617 (-0.0313) [-0.0399, -0.0227] | 0.7133 (-0.0797) [-0.1082, -0.0532] |
| identity (ArcFace, Add.51) | 0.9962 | 0.9839 (-0.0123) [-0.0219, -0.0053] | 0.9629 (-0.0333) [-0.0545, -0.0166] | 0.9946 (-0.0015) [-0.0034, -0.0003] | 0.9815 (-0.0147) [-0.0264, -0.0053] |
| clipe5b | 0.9244 | 0.8229 (-0.1016) [-0.1238, -0.0812] | 0.7776 (-0.1468) [-0.1755, -0.1199] | 0.8869 (-0.0376) [-0.0686, -0.0105] | 0.7507 (-0.1737) [-0.2135, -0.135] |
| effort | 0.8966 | 0.8124 (-0.0841) [-0.1085, -0.0588] | 0.7795 (-0.1170) [-0.1476, -0.0862] | 0.7626 (-0.1339) [-0.1824, -0.0968] | 0.663 (-0.2335) [-0.2843, -0.1912] |
| gend | 0.904 | 0.8042 (-0.0997) [-0.1348, -0.0646] | 0.7343 (-0.1697) [-0.2101, -0.1273] | 0.6645 (-0.2395) [-0.2918, -0.1872] | 0.6055 (-0.2985) [-0.3478, -0.2477] |
| sbi | 0.8323 | 0.6997 (-0.1326) [-0.1831, -0.0918] | 0.5764 (-0.2559) [-0.3161, -0.2004] | 0.6376 (-0.1947) [-0.2623, -0.1345] | 0.5726 (-0.2597) [-0.3371, -0.1948] |

False alarm on genuine / miss on forged (%) at the threshold = 95th percentile on untreated genuine, held fixed:

| score | untreated | bil15 | bil21 | fl06 | fl12 |
|---|---|---|---|---|---|
| ICT | 5.0 / 65.3 | 2.3 / 87.8 | 2.5 / 85.3 | 3.7 / 73.3 | 4.7 / 75.7 |
| ICT-Ref (ours ref) | 5.0 / 46.6 | 2.9 / 70.4 | 7.2 / 64.1 | 4.1 / 54.6 | 5.5 / 56.5 |
| ICT-Ref (released ref.pkl) | 5.0 / 32.3 | 4.7 / 52.7 | 12.3 / 39.8 | 4.9 / 40.0 | 7.1 / 39.1 |
| ICT-Ref (claimed-id ref, exploratory) | 5.0 / 62.9 | 3.1 / 80.8 | 5.4 / 72.5 | 4.3 / 69.8 | 5.4 / 69.5 |
| identity (ArcFace, Add.51) | 5.0 / 0.1 | 19.4 / 0.1 | 40.0 / 0.0 | 6.3 / 0.2 | 21.3 / 0.3 |
| clipe5b | 5.0 / 33.8 | 43.2 / 14.4 | 53.5 / 14.9 | 56.6 / 3.8 | 88.0 / 1.8 |
| effort | 5.0 / 33.4 | 41.5 / 16.8 | 66.5 / 5.3 | 94.9 / 0.1 | 100.0 / 0.0 |
| gend | 5.0 / 30.6 | 88.0 / 0.6 | 96.8 / 0.1 | 98.8 / 0.0 | 100.0 / 0.0 |
| sbi | 5.0 / 55.0 | 74.2 / 5.7 | 92.6 / 1.2 | 98.2 / 0.1 | 100.0 / 0.0 |

Median score (genuine / forged):

| score | untreated | bil15 | bil21 | fl06 | fl12 |
|---|---|---|---|---|---|
| ICT | 0.7631 / 0.9159 | 0.733 / 0.8106 | 0.7656 / 0.834 | 0.756 / 0.881 | 0.7969 / 0.8807 |
| ICT-Ref (ours ref) | 1.4556 / 1.9231 | 1.4745 / 1.7489 | 1.5774 / 1.8063 | 1.4548 / 1.8547 | 1.5667 / 1.8467 |
| ICT-Ref (released ref.pkl) | 1.187 / 1.9084 | 1.275 / 1.751 | 1.4326 / 1.8374 | 1.1884 / 1.8432 | 1.3634 / 1.8455 |
| ICT-Ref (claimed-id ref, exploratory) | 1.4514 / 1.7616 | 1.4625 / 1.6298 | 1.5534 / 1.72 | 1.4425 / 1.7029 | 1.5531 / 1.725 |
| identity (ArcFace, Add.51) | 0.2461 / 0.6451 | 0.3182 / 0.6426 | 0.3831 / 0.6647 | 0.2571 / 0.6421 | 0.3177 / 0.6344 |
| clipe5b | 0.0534 / 0.999 | 0.9883 / 0.9984 | 0.9914 / 0.9982 | 0.9948 / 0.9999 | 0.9994 / 0.9999 |
| effort | 0.3546 / 0.8951 | 0.7307 / 0.9063 | 0.8474 / 0.9442 | 0.9538 / 0.978 | 0.9786 / 0.9851 |
| gend | 0.2196 / 0.9166 | 0.9464 / 0.9822 | 0.9692 / 0.9845 | 0.9773 / 0.985 | 0.988 / 0.9904 |
| sbi | 0.1765 / 0.7971 | 0.9527 / 0.9851 | 0.9913 / 0.9941 | 0.9996 / 0.9998 | 0.9995 / 0.9996 |

## 執行說明（2026-10-21）

- **有跑**：ICT 與 ICT-Ref（Dong et al. CVPR 2022，官方 repo `LightDXY/ICT_DeepFake`，release v0.1.0 的 `ICT_Base.pth` 與 `ref.pkl`、repo 指定的 RetinaFace `Resnet50_Final.pth`，權重未改）。repo 與權重放在 `C:\My_Project\AIGC\external_models\ict_20261021\`。腳本 `ict_probe.py`（embed／analyse）。
- **跟官方 code 不同的地方（只是工程上的替換，數學上相同）**：官方 ViT 繼承 timm==0.3.4（不相容 torch 2.x），改用目前 timm 的 `Block` 重建、參數名稱相同，`strict=True` 載入無缺漏或多餘 key；KNN_CUDA（k=1）換成 `torch.cdist` argmin；`get_face()` 從 `preprocess.py` 逐行照抄（RetinaFace R50、5 點 similarity warp 到 317×317 模板、padding 30），改成可以對記憶體中的影像呼叫。ICT 分數＝‖inner−outer‖²，ICT-Ref 分數＝`ict_eval.py` 的加權距離公式（thres=tau=0.5）。分數越高越偏 fake。
- **ICT-Ref reference set（主結果）**：用 Addendum 51 的同一組非 test Celeb-real 影片與幀（54 個身分、1,080 幀，每個身分 4 支影片 × 5 幀），經 ICT 自己的對齊流程後，對整個 pool 做 k=1 KNN（與官方作法相同，不使用 claimed identity）。另外列兩個次要版本：(a) 官方 `ref.pkl`（2,420 筆，**來源與內容不明，可能含 Celeb-DF 身分甚至 test 影片，不能當成乾淨比較**）；(b) 把 pool 限縮到 claimed identity 的版本（探索用，不在 Addendum 52 的設計內）。
- **對齊失敗率**：五個條件都是 0.0%（RetinaFace 信心值 <0.5 的偵測也是 0%）。對齊後的 317 crop 因為原 probe crop 的邊界，平均有約 5.5–6% 黑邊，各條件差不多；reference 幀用的是完整影片畫面，沒有黑邊（這是 probe 與 reference 之間的差異，已記錄）。
- **合理性檢查**：對齊結果有目視確認；FF++ 官方 log（`weights/ff_eval.log`）沒有重現，因為作者對齊好的 FF++ 子集沒有下載。未處理影像上 ICT 0.790、ICT-Ref 0.863，與方法本身的設計相符（有 reference 比沒有好）。
- **ID-Reveal 沒有跑**（`external_models\id_reveal_20261021\id-reveal` 有 clone 下來檢查）：它的 Temporal ID Network 輸入是 **3DDFA 的 62 維 3DMM 係數，取自連續的 25 fps 影格序列**（demo 設定 `time=100` 幀，滑動視窗）。repo 只提供網路與預先抽好的特徵，沒有 3DDFA 前處理；我們的 probe 是每支影片 32 幀的稀疏取樣、而且平滑是逐張套在 PNG 上，不存在連續 100 幀的序列。在 Addendum 51 的 probe 上跑 ID-Reveal，必須對完整影片的每一幀重新套平滑、再自己接 3DDFA，這樣就不是「相同的 PNG」，也超出 Addendum 52 的設計範圍。此外，它的訊號是臉部動作（3DMM 表情／姿態）的時間序列，本來就不是讀紋理。

## 判定（依 Addendum 52 的原文）

1. 「ICT-Ref 的 AUC 下降不超過 0.03」→ **不成立**。主結果的下降：bil15 −0.082 [−0.107, −0.060]、bil21 −0.108、fl06 −0.028、fl12 −0.080 [−0.102, −0.057]。只有 fl06 在 0.03 以內。即使用官方 ref.pkl，bil15 也降 −0.052、fl12 降 −0.044。
2. 條件句「ICT-Ref 若下降 >0.05，代表 Addendum 51 的身分結果只限於 ArcFace distance，論文要寫明」→ **觸發**（bil15、bil21、fl12 三個條件，CI 都完全在 −0.05 以下）。
3. 「plain ICT 的下降比 ICT-Ref 大，但比紋理偵測器小」→ **只部分成立**。四個條件的點估計都是 ICT 比 ICT-Ref 掉得多（−0.111／−0.123／−0.038／−0.092），但 CI 重疊。和紋理偵測器比：在 fl12 成立（−0.092，紋理偵測器 −0.17 到 −0.30）、在 fl06 大致成立（與 clipe5b −0.038 打平）；在 bil15／bil21 不成立（ICT −0.111 落在紋理偵測器 −0.084 到 −0.133 的範圍內）。
4. 「在固定門檻下，兩者對平滑後的真臉誤判都比未處理時多」→ **不成立**。ICT 的 FA 反而下降（5.0 → 2.3–4.7%）；ICT-Ref 只有在 bil21（7.2%）和 fl12（5.5%）略高於 5%。ICT 系列的失敗方向相反：平滑把**假臉**往真臉推（假臉的中位數下降，例如 ICT 0.916→0.811），所以漏判上升（ICT 65→74–88%、ICT-Ref 47→55–70%）。紋理偵測器則是把真臉往假臉推（FA 41–100%）。

解讀：在相同 probe 上，身分不受平滑影響的現象只出現在「ArcFace distance 加 claimed-person reference」，沒有在已發表的身分偵測器 ICT／ICT-Ref 上出現。ICT 的 inner／outer 一致性也被平滑削弱，但它失敗的方向是漏判，不是誣告。
