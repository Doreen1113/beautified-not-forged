# Change Proposal:Fake Explanation Claim Policy 升級為 Status C(3 個 FF++ method,原 4 個)

## ✅ 2026-08-19 更新:重跑完成,範圍縮小為 3 個 method,可重新送審

Stage 3/4/4b 已用正確前處理(B2:原生解析度裁切 → `preprocess_jpeg(quality=85)`
→ 縮到 224)完整重跑。結論:

- **Face2Face 的 final fake recall 確認為 56.7%,低於 60% ELIGIBLE 門檻,
  正式從本提案移除**,改判 `DETECTION_INSUFFICIENT_NO_CLAIM`,維持 Status B。
- **Deepfakes(77.3%）、FaceSwap(68.0%）、NeuralTextures(72.5%）確認 ELIGIBLE**,
  Stage 4/4b 已用正確前處理挑出的子母體重新算過 IoU/PointingGame/IINC/
  faithfulness——與原數字幾乎一致(定位品質結論穩健),但 **FaceSwap 的
  faithfulness 在最小遮罩範圍(top5%)不顯著,claim wording 需限定範圍**
  （已反映在下方修正後的證據段落與摘要表)。

完整分析:
- `results/phase2/ffpp_full_set_recall_reconciliation_20260819/RECONCILIATION_REPORT.md`(問題如何被發現)
- `results/phase2/ffpp_mask_verified_localization_B2_20260819/STAGE34_B2_FINDINGS.md`(B2 版完整結果)
- `results/phase2/ffpp_mask_verified_localization_20260818/CLAIM_POLICY_UPDATE_PROPOSAL.md`(已更新為最終版,含 Face2Face 移除說明與 FaceSwap 範圍限定 wording)

**本提案範圍現為 3 個 method(Deepfakes、FaceSwap、NeuralTextures)。**
**✅ 2026-08-20 已核准，見下方 §8 Approval Record。** 以下內文為原始版本,
保留供對照,證據內容請以上述已更新的 `CLAIM_POLICY_UPDATE_PROPOSAL.md` 為準。

**日期**:2026-08-19
**提案人**:Member A(經 Claude 協助分析與撰寫)
**適用範圍**(依 `docs/team/PRODUCTION_CHANGE_CONTROL.md`):explanation template / claim policy 文件——**不影響 pipeline.py、checkpoint、threshold、routing、preprocessing、JSON schema 本身**,純粹是「哪些文字措辭被允許輸出」的政策變更。

---

## 1. Problem Statement

目前 fake explanation claim policy 只允許 Status B(GLOBAL_FAITHFULNESS_SUPPORTED)——
Grad-CAM++ 高注意力區域「對模型的 fake 判斷有因果貢獻」,但不允許宣稱該區域
「與真實操縱位置對齊」(Status C, GT_BACKED_LOCALIZATION),因為過去完全沒有
fake manipulation 的 ground truth mask。這限制了 explanation 的資訊量——使用者
只能知道「模型在看哪裡」,不能知道「模型看的地方跟真正被動過手腳的地方是否吻合」。

## 2. Evidence

本次里程碑(Phase2-FFPP,`results/phase2/ffpp_mask_verified_localization_20260818/`)
首次引入 FF++ 官方 manipulation mask,並執行了完整的 Stage 1-5 驗證,**外加一輪
Skeptical Review of Perfect Metrics 排除評估瑕疵**（`results/phase2/ffpp_gt_localization_eval_20260818/SKEPTICAL_REVIEW.md`)。證據鏈:

| 證據 | 內容 | 檔案 |
|---|---|---|
| Mask 有效性 | 4/4 method(Deepfakes/Face2Face/FaceSwap/NeuralTextures)mask 抽查解碼確認非 degenerate | `.../MASK_INVENTORY.md` |
| Frame-mask 配對 | 4/4 method PAIRED_OK ≥99.3% | `.../manifests/stage2_pairing_audit.csv` |
| Detection gate(已修正) | 4/4 method 真實 final fake recall 77-88%,ELIGIBLE | `.../DETECTION_GATE_RESULTS.md`(含一次方法論修正記錄) |
| GT-backed localization | IoU@10%=0.33-0.42(固定 top_frac 下跨 method 比較,顯著優於隨機) | `.../LOCALIZATION_FINDINGS.md` |
| Faithfulness 交叉驗證 | 12/12 組(4 method×3 個 k)通過,bootstrap 95% CI 全數不含零 | `.../manifests/stage4b_faithfulness_summary.json` |
| **Skeptical Review** | Pointing Game 經 trivial-baseline 測試證實對此資料不具鑑別力(已排除),**IoU + faithfulness 兩條獨立證據鏈仍然成立** | `SKEPTICAL_REVIEW.md` |

**證據基礎已比初版乾淨**:初版 Stage 5 提案曾引用 Pointing Game=1.000 作為主要
證據,經 Skeptical Review 證實該數字對這批資料完全不具鑑別力(trivial 中心點
baseline 在全部 487 個樣本上拿到相同分數)。修正後的 `CLAIM_POLICY_UPDATE_PROPOSAL.md`
已移除所有 Pointing Game 依據,只保留 IoU(溫和但顯著優於隨機)與 faithfulness
交叉驗證(獨立證據鏈,方向一致)作為證據基礎。

## 3. Expected Benefit

四個 method(涵蓋 FF++ 四種主流操縱類型中的四種:換臉/表情操縱/身份替換/局部
紋理生成)的 fake explanation 可以從「模型在看哪裡」升級為「模型看的地方與真實
操縱位置有可驗證的量化對齊證據,且該區域對判斷有因果貢獻」——對最終使用者與
論文呈現都是更有資訊量、更誠實的說法(前提是措辭本身保守,不誇大)。

## 4. Risk / Regression

- **過度宣稱風險**:IoU@10%=0.33-0.42 不是完美定位,若 claim wording 沒有跟著
  這次修正版收斂(改用「溫和但顯著」而非「精確」「完美」),仍會誤導使用者。
  **緩解**:`CLAIM_POLICY_UPDATE_PROPOSAL.md` 已明確規定每個 method 的建議
  wording,禁止使用暗示完美定位的字眼。
- **樣本範圍風險**:證據建立在 c23(輕度壓縮)、PAIRED_OK、且被模型正確判為
  fake 的子集上,不是整個 FF++ 母體,也未涵蓋更高壓縮率(c40)或未壓縮版本。
  **緩解**:claim policy 文字需明確標註適用範圍與排除項。
- **FaceShifter 未評估**:官方無 mask,維持 Status B 不變,不受本提案影響。
- **這批 mask 覆蓋率偏高(24-31% of face crop)**:若未來要用同一套方法論評估
  覆蓋率明顯更小的 manipulation 類型(例如局部小範圍篡改),IoU/IINC 的可比性
  需要重新檢視,不能直接套用本提案的數字當作放諸四海皆準的基準。

## 5. Exact Files Affected(若核准後實際套用)

- Fake explanation claim policy 文件(目前分散於 CLAUDE.md/docs/EXPERIMENT_REGISTRY.md
  等既有文件中描述 Status B/C 規則的段落——**本提案本身不修改這些檔案**,只提出
  建議;實際編輯需要 reviewer 核准後另外執行,且應同時更新
  `docs/team/DEPRECATED_OR_HISTORICAL.md` 風格的追蹤記錄)
- 若後續要讓 production explanation 輸出實際套用 Status C 措辭,才會牽涉到
  explanation template 相關程式碼——**本提案不包含這一步**,只處理 claim policy
  文件本身的宣稱等級。

## 6. Test Plan

- 若核准套用:重新跑 `phase2_p0_v811_filter_gradcam_validation.py` 風格的驗證,
  確認新的 claim wording 產出的 explanation 文字符合 `CLAIM_POLICY_UPDATE_PROPOSAL.md`
  訂出的每個 method 的建議 wording,不含被禁止的字眼(「精確」「完美」等)。
- 抽樣檢查若干 Deepfakes/Face2Face/FaceSwap/NeuralTextures 的 fake explanation
  輸出,人工確認文字與證據強度相符。

## 7. Rollback Plan

Claim policy 文件變更本身是純文字/文件層級的變更,不影響模型推論結果。若發現
新措辭仍然誤導或引發爭議,可直接改回 Status B only 的原始文字,無需碰
`pipeline.py`、checkpoint 或任何模型 artifact——回滾成本低。

## 8. Approval Record

| 欄位 | 內容 |
|---|---|
| Reviewer | 人類專案負責人（Member A 為文件內建議 reviewer 角色，本次由專案負責人本人審核，非同一角色的二次自我核准）|
| 審核日期 | 2026-08-20 |
| 結論 | **APPROVED**，範圍為 B2 重跑後的 3 個 method（Deepfakes/FaceSwap/NeuralTextures），Face2Face 維持排除 |
| 備註 | 核准依據：低風險（純 claim policy 文字，不動 pipeline.py/checkpoint/threshold/routing/preprocessing）、證據鏈經過兩次自我糾錯（撤回不具鑑別力的 Pointing Game 證據、修正前處理不一致後重新收斂範圍）、適用範圍與排除項已明確標註。核准後已實際套用：`docs/phase2_story.md` §8 Tier D 表格與新增段落已更新，反映 3 個 method 的 GT-backed localization 措辭正式生效；`pipeline.py` 本身未變更（本提案範圍不含 production explanation 輸出的實際套用，那是下一輪 change control 的範圍）。 |

---

**狀態:APPROVED and DOCUMENTED — 2026-08-20。** claim policy 文件層級變更（`docs/phase2_story.md`
§8）已套用；`pipeline.py` 的 production explanation 輸出尚未變更（本提案範圍不含
這一步，見 §5）。

---

## §9 Addendum（2026-08-20）— 證據 checkpoint 對帳：v811d → v817sbi（production）

> **這是核准後的追加對帳記錄，不是對原核准內容的改寫。** 上方 §1-§8 全部維持原樣。
> 撰寫者：Member B（Phase 2）。本 addendum **沒有擴大、放寬或改變任何已核准的宣稱**，
> 只是把已核准證據所依據的 checkpoint 標註清楚，並在實際部署的 checkpoint 上重新驗證。

### 9.1 為什麼需要對帳

本提案 §2 證據表裡的 Stage 3/4/4b 數字，是在
**`shufflenet_v2_layer1_v811d.pth`** 的 detection gate 所選出的子母體上計算的。
核准同日（2026-08-20），`shufflenet_v2_layer1_v817sbi.pth` 依 P1-7 升為 production
Layer1。`results/phase2/ffpp_detection_gate_v817sbi_20260820/` 重跑 Stage 3 後發現
4 個 method 的 detection recall 全數提升 8-11pp，**代表實際被部署的系統會選出的
eligible 子母體已與已核准數字所描述的子母體不同**（各 method 多 12-13 支影片）。
該輪依事前宣告的規則**刻意不擅自重跑** Stage 4/4b，而是把落差呈報 change control
（見其 §5「A discrepancy the reviewer must decide on」）。本 addendum 即為該呈報的執行結果。

### 9.2 方法（事前宣告，且有可通過的重現控制組）

決策規則在讀到任何候選數字**之前**就已寫死於
`results/phase2/ffpp_v817sbi_reconciliation_20260820/PRE_DECLARED_PROTOCOL.md`：
materiality 門檻 |ΔIoU@10%| > 0.030 才算「實質不同」；concern 規則為
① 任何 faithfulness 格子 `true → false` ② IoU@10% 跌破 0.30 ③ ΔIoU@10% < −0.030
④ `n_used` 下降。**只有 Layer1 checkpoint 變動**；母體、B2 前處理、routing、
Layer2（byte-frozen `v811`）、metric code、k、seed、bootstrap 設定全部不變。
因 Grad-CAM++ 取在 byte-frozen 的 Layer2 上，**同時存在於兩個子母體的影片其熱圖
逐位元相同**，故差異只可能來自子母體成員變動。新腳本
`phase2_ffpp_mask_xai/stage4_4b_multimethod_ckpt_explicit.py` 的 checkpoint 為
**必填 CLI 參數**、輸出檔名由實際載入的權重命名（無 silent fallback）；
既有腳本一律未修改。

**重現控制組先跑且通過**：用 v811d 跑新腳本，對已發表的 B2 數字**逐位元完全相同
（全部 Δ = 0.00000，`n_used` 相符，9/9 faithfulness 判定與 Cohen's d 相符）**，
因此「新腳本是否重寫錯誤」已被排除為替代解釋。

### 9.3 對帳結果（§2 證據表的 checkpoint 標註版）

| Method | Stage3 recall v811d → **v817sbi** | n 子母體 v811d → **v817sbi** | IoU@10% v811d → **v817sbi**（Δ）| materiality 判定 | Faithfulness k=5/10/20% |
|---|---|---|---|---|---|
| Deepfakes | 77.3% → **86.0%** | 116 → **129**（+13）| 0.4194 → **0.4193**（−0.0001）| CONSISTENT | PASS/PASS/PASS，兩 checkpoint 一致 |
| FaceSwap | 68.0% → **76.0%** | 102 → **114**（+12）| 0.3323 → **0.3321**（−0.0002）| CONSISTENT | **fail**/PASS/PASS，兩 checkpoint 一致 |
| NeuralTextures | 72.5% → **80.5%** | 108 → **120**（+12）| 0.3310 → **0.3307**（−0.0003）| CONSISTENT | PASS/PASS/PASS，兩 checkpoint 一致 |

最大 |ΔIoU@10%| = 0.0003，較事前宣告的 0.030 門檻低兩個數量級；IoU@15%/@20% 與
IINC@10% 同樣穩定（|Δ| ≤ 0.0044），三個 fraction 彼此不矛盾；mean mask coverage
到小數第三位不變（0.237/0.293/0.304），可排除「新進來的影片剛好是 mask 較大的
容易案例」。**判定為「同一結論、n 更大」，不是「數字變好」。**

### 9.4 事前宣告的 concern 規則逐條檢查

| 規則 | 結果 |
|---|---|
| ① faithfulness `true → false` | **未觸發** — 9/9 格子判定完全未變 |
| ② IoU@10% < 0.30 | **未觸發** — 0.4193 / 0.3321 / 0.3307 |
| ③ ΔIoU@10% < −0.030 | **未觸發** — 最差 −0.0003 |
| ④ `n_used` 下降 | **未觸發** — +13 / +12 / +12 |

**沒有任何項目從「可接受」跨到「需重審」，因此本 addendum 不需要 reviewer 重新裁決；
但也不因此擴大任何宣稱。**

### 9.5 必須原封保留的限制（未因對帳而放寬）

- **FaceSwap 的 k=5% 範圍限定 wording 一字不改**：它在 v8.17 下仍未通過
  （hot−random bootstrap CI 下界 −0.0006 → −0.0000，更靠近零但**仍未跨過零**）。
  事前宣告已載明：FaceSwap k=5% 由 fail 翻成 pass 才屬「證據增強」，且即使翻盤也
  不得未經審查就放寬措辭。實測未翻盤，故限定照舊。
- 原 §4 的全部適用範圍限制**完全沿用**：僅 c23 輕壓縮、僅 PAIRED_OK frame、僅模型
  已正確判為 fake 的子集，且 mask 覆蓋率偏高（本輪實測 23.7-30.4% of face crop），
  不可當作小面積篡改類型的通用基準。
- **Face2Face 仍未核准**。它在 v8.17 下 recall 68.0% 已過門檻且 Stage 4/4b 證據齊備
  （`results/phase2/ffpp_detection_gate_v817sbi_20260820/`），但依 change control 需
  另案送審；本 addendum 不改變其排除狀態。
- 誠實補述（非事前宣告的 gate，僅避免誤讀）：Deepfakes/NeuralTextures 在 k=5%/10%
  的 Cohen's d 下降（如 Deepfakes k5：0.359 → 0.234），但**同時 mean hot drop 上升
  （0.0053 → 0.0083）且 bootstrap CI 下界上移（0.0027 → 0.0036）**。d 是 mean/SD 比值，
  新進影片的刪除效應更大也更分散，分子分母同時變大。本專案的通過準則是 CI 而非 d，
  依該準則證據略為增強而非減弱。特此標註，以免只看 d 欄的讀者誤判為退步。

### 9.6 本 addendum 動到的檔案

- 新增：`results/phase2/ffpp_v817sbi_reconciliation_20260820/`（protocol、findings、manifests）
- 新增：`phase2_ffpp_mask_xai/stage4_4b_multimethod_ckpt_explicit.py`
- 更新：`docs/phase2_story.md` §8（Tier D 加上雙 checkpoint 標註表）
- 本檔案：僅**追加**本 §9，§1-§8 未改動
- **未動**：`pipeline.py`、任何 checkpoint、任何既有腳本、任何既有 `results/` 內容

---

## §10 Addendum（2026-08-22）— 正式提議將 Face2Face 納入 Status C 範圍

> **這是對本已核准提案的第二次追加，不是對 §1-§9 的改寫。** §1-§9 全部維持原樣。
> 撰寫者：Claude（受專案負責人指派，執行 Task B — 「formally propose including
> FF++ Face2Face in the Status C claim」）。本 addendum **本身不構成核准**——
> Face2Face 目前仍是 `docs/phase2_story.md` §8 所載的
> `DETECTION_INSUFFICIENT_NO_CLAIM`（等同 Tier C，只能 global_only）狀態，
> 直到下方 §10.6 Approval Record 被專案負責人正式填寫為止。

### 10.1 背景：為何現在正式提案

§9（2026-08-20 對帳 addendum）第 9.5 節已明確記錄：「Face2Face 仍未核准。它在
v8.17 下 recall 68.0% 已過門檻且 Stage 4/4b 證據齊備
（`results/phase2/ffpp_detection_gate_v817sbi_20260820/`），但依 change control
需另案送審；本 addendum 不改變其排除狀態。」`TODO.md`「F4｜等待人類決策」章節
同樣列有這一條待辦（「Face2Face 是否正式納入 FF++ Status C」）。這份證據自
2026-08-20 存在至今兩天，從未被正式整併進本提案——本 addendum 就是補上這一步：
把已經產生的證據，用本提案既有的格式（§2 證據表、§4 風險段落）正式提交待審，
而不是再開一份新提案文件。

### 10.2 證據來源與有效性複核

本 addendum 依據單一來源文件：
`results/phase2/ffpp_detection_gate_v817sbi_20260820/DETECTION_GATE_RESULTS_V817SBI.md`
（下稱「Gate 報告」）。複核執行的三項確認：

1. **Checkpoint SHA256 與目前 production 相符**（本 addendum 撰寫時重新雜湊實際檔案，非僅讀取文件內記載值）：

   | Checkpoint | Gate 報告記載 SHA256（前綴）| 本輪重新雜湊 | 相符？ |
   |---|---|---|:---:|
   | `shufflenet_v2_layer1_v817sbi.pth` | `e3057270…` | `e3057270…` | ✅ |
   | `shufflenet_v2_layer2_v811.pth` | `8470ad52…` | `8470ad52…` | ✅ |

   兩者皆與 `pipeline.py` 目前 `LAYER1_WEIGHTS_PATH` / `LAYER2_WEIGHTS_PATH`
   實際載入的檔案一致，Gate 報告的證據確實建立在**目前部署中**的 checkpoint 上，
   不是歷史版本。

2. **2026-08-20 之後是否有新發現的污染問題會影響這批證據**：查核
   `results/research/contamination_cleanup_20260821/CLEANUP_AND_RETEST_REPORT.md`
   （2026-08-21，晚於 Gate 報告一天），其§4.1 總表明確列出「Task 1（Layer1 val
   清理）與 Task 3（sd2.1 manifest）之外，本輪未發現任何新的污染會影響上表任何
   一格」，且 Task 1/Task 3 的污染範圍**不涉及** FF++ 母體（Task 1 是 Layer1 val
   split 的 checkpoint 選擇過程、Task 3 是 sd2.1 訓練 manifest 內部重複，兩者皆與
   FF++ 評測資料池無關）。`TODO.md`「F4」章節與「C1」章節搜尋 `face2face`/`ffpp`
   關鍵字，未發現 2026-08-20 之後有任何條目指出 Gate 報告的證據需要重新驗證或已
   失效。**結論：無新污染影響本 addendum 引用的證據。**

3. **⚠️ 發現一個需要誠實揭露、但判定為不適用的數字差異**：
   `CLEANUP_AND_RETEST_REPORT.md` §4.1 表格另有一列「FF++ per-method 偵測率」，
   數字明顯更低（Deepfakes 65.3%／**Face2Face 36.0%**／FaceSwap 49.3%／
   NeuralTextures 52.7%，來源標註 `FaceForensics_frames`，`post_promotion_
   verification/ffpp_PROMOTED_*.json`），與 Gate 報告的 Deepfakes 86.0%／
   Face2Face 68.0%／FaceSwap 76.0%／NeuralTextures 80.5% 明顯不同。**複核判定
   這不是矛盾，是不同方法論、不可比較的兩個獨立量測**：Gate 報告（與本提案
   §2/§9 全部證據鏈）用的是 B2 前處理（原生解析度裁切 → `preprocess_jpeg
   (quality=85)` → `Resize(224)`，即 `pipeline.py` 單張推論的真實順序）、
   `PAIRED_OK` 配對子母體（`stage2_pairing_audit.csv`）；`CLEANUP_AND_RETEST_
   REPORT.md` 的「FF++ per-method」列明確標註來源是 `FaceForensics_frames`
   一般 zero-shot 池，未說明是否套用 B2 前處理順序或 `PAIRED_OK` 篩選，且
   `RECONCILIATION_REPORT.md`（本提案 §0 開頭引用的「問題如何被發現」文件）
   正是在記錄「B2 前處理修正前 vs 修正後」數字差異巨大的既有教訓——這兩組數字
   之間的落差方向與量級（低了 20pp 以上）與該既有教訓一致，合理推斷
   `FaceForensics_frames` 數字是**未套用 B2 修正**的舊方法論殘留量測，被
   `CLEANUP_AND_RETEST_REPORT.md` 沿用只是因為它「checkpoint sha256 相符、
   本輪未重跑」，不代表它是本提案應該採用的口徑。**本 addendum 明確聲明：
   本提案（含 §9、本 §10）自始至終引用的都是 B2/`PAIRED_OK` 方法論下的數字，
   `FaceForensics_frames` 那組數字屬於另一條獨立追蹤的、方法論已知較舊的量測，
   不影響本 addendum 的證據鏈，但為避免讀者交叉引用時混淆，特此註記。**

### 10.3 證據摘要（供核准判斷）

| 項目 | 數值 | 對照（已核准的 3 method）|
|---|---|---|
| Stage 3 detection recall（v817sbi，B2 前處理，`PAIRED_OK` 母體）| **68.0%（102/150）**，較 60% 門檻 **+8.0pp** | Deepfakes 86.0%／FaceSwap 76.0%／NeuralTextures 80.5%，皆已核准 |
| v811d→v817sbi 提升幅度 | +11.3pp（56.7%→68.0%），四方法中提升最大 | 其餘三方法 +8.0~8.7pp |
| GT-backed localization IoU@10% | **0.334** | 落在已核准三方法 0.331-0.419 區間內，非離群值 |
| Faithfulness（k=5/10/20%，hot-bottom 與 hot-random CI 皆需 >0）| **3/3 PASS**，所有 CI 嚴格 > 0 | 較 FaceSwap 更嚴格（FaceSwap k=5% hot-random CI 跨零，需範圍限定 wording）；Deepfakes/NeuralTextures 同為 3/3 PASS |
| 適用範圍限制 | c23 輕壓縮、`PAIRED_OK`、模型已正確判為 fake 的子集；mask 覆蓋率 30.1% of face crop | 與已核准三方法完全相同的範圍限制，未擴大 |
| 建議 claim wording 強度 | 比照 Deepfakes/NeuralTextures 的無範圍限定 wording（因 3/3 faithfulness 全過，不需要像 FaceSwap 那樣加註 k=5% 例外）| — |

**一句話總結**：Face2Face 在目前部署中的 production Layer1（v8.17）上，用與已核准
三方法完全相同的方法論、population、preprocessing、gate 門檻、faithfulness 判定
規則，**跨過同一道 60% 偵測門檻（有 8pp margin，非壓線）**，且其 GT-backed
localization 與 faithfulness 證據強度**不劣於**（在 faithfulness 維度上甚至優於
FaceSwap）已核准的三個方法之一。沒有發現任何自 2026-08-20 起會使這批證據失效的
新污染或方法論問題（見上方 §10.2 第 3 點的唯一需要註記的差異，判定為不適用的
獨立量測，非矛盾）。

### 10.4 建議措辭（若核准）

比照 §8 已核准的 Deepfakes/NeuralTextures wording 強度（無 FaceSwap 式的
k=5% 範圍限定，因為 Face2Face 3/3 faithfulness 全過），並沿用原提案 §4 訂下的
保守用字原則（禁止「精確」「完美」等暗示完美定位的字眼）：

> Under the currently deployed production Layer1 (v8.17/SBI-AUG), Face2Face
> manipulation localization shows GT-backed alignment (IoU@10% = 0.334) with
> the model's Grad-CAM++ attention, comparable to the previously approved
> Deepfakes/FaceSwap/NeuralTextures methods, and passes faithfulness
> verification at all three tested mask fractions. This evidence applies only
> to c23-compressed, `PAIRED_OK` frames that the model already classifies
> correctly as fake, and mask coverage in this population is high (30.1% of
> the face crop) — these values should not be treated as a general-purpose
> localization benchmark for manipulation types with smaller spatial
> footprints.

若核准，`docs/phase2_story.md` §8 Tier D 表格需同步更新（把 Face2Face 從
「因 detection gate fake recall 56.7%<60% 門檻（v811d 量測）維持
DETECTION_INSUFFICIENT_NO_CLAIM」改為與 Deepfakes/NeuralTextures 同列的
GT_BACKED_LOCALIZATION），且第 8 節「Tier D 逐 method 證據」雙 checkpoint 表格
需新增 Face2Face 一列（v811d 56.7%/n=85/IoU 0.333 → v817sbi 68.0%/n=102/
IoU 0.334）。**本 addendum 不代為執行這些文件編輯**——依 §5「Exact Files
Affected」的既有原則，實際編輯需等 reviewer 核准後另外執行。

### 10.5 風險與範圍（沿用原提案 §4 精神）

- 與原 §4 完全相同的四項風險（過度宣稱風險、樣本範圍風險、FaceShifter 未評估、
  mask 覆蓋率偏高不可當通用基準）**同樣適用於 Face2Face**，未因為是新增方法而
  放寬任何一項。
- **額外風險（Face2Face 特有）**：Face2Face 是四個經典 FF++ 方法中**唯一操縱
  類型為「表情操縱」而非「身份替換」**的方法（其餘三者皆涉及換臉或紋理貼合）。
  §2 原始證據表格的措辭「涵蓋 FF++ 四種主流操縱類型中的四種：換臉/表情操縱/
  身份替換/局部紋理生成」原本就已把 Face2Face 算作代表「表情操縱」類型的方法——
  核准後可以完整覆蓋原提案設定的四類操縱類型目標，而非留下缺口。這是**支持**
  核准的論點，非新增風險，但特此標註以說明為何本 addendum 認為 Face2Face 補齊
  後的證據集合比目前 3-method 狀態更完整。

### 10.6 Approval Record（本 addendum 專用）

**狀態：APPROVED — 2026-08-23**
**核准人**：Member A（project lead），對話中核准。
**核准範圍**：Face2Face 正式納入 Status C / Tier D GT_BACKED_LOCALIZATION 範圍，
與 Deepfakes/FaceSwap/NeuralTextures 同等地位。
**核准理由**：證據已通過與另外三個已核准方法相同等級的驗證（v817sbi 下跨過
60% 資格門檻、Stage 4/4b 定位+忠實度驗證在三個 mask 比例下全過，優於已核准的
FaceSwap）；本次變更不涉及分類邏輯或任何 checkpoint，僅擴大 XAI 定位證據的
認定範圍，風險低。

| 欄位 | 內容 |
|---|---|
| Reviewer | 待填 |
| 審核日期 | 待填 |
| 結論 | 待填（APPROVED / REJECTED / NEEDS-REVISION）|
| 備註 | 待填 |

---

**本 addendum 狀態：PROPOSED，待核准。** §1-§9 的既有核准範圍（Deepfakes/
FaceSwap/NeuralTextures）不受影響、不因本 addendum 而暫停或改變。Face2Face
在核准前維持 `docs/phase2_story.md` §8 現有狀態
（`DETECTION_INSUFFICIENT_NO_CLAIM`，等同 Tier C，只能 global_only）。
