# 專題故事線（2026-10-23）

> 用途：專題（清大資工專題）找回一條主線。專題講的是**系統**：一個會回答「真的／偽造／只是美顏」、把證據圈在臉上、說出口的每一句都經程式對帳的人臉檢查系統；加上「讓 AI 自由描述的解釋不可靠」的證據，以及一個真人測試。專題可以和實驗室論文不同。
>
> 依據：`MAIN_CLAIMS_20261022.md`、`JUDGE_REHEARSAL_20261022.md`、`GAP_VS_WINNERS_20261021.md`、`REPORT.md`、`human_study/PRE_DECLARED_HUMAN_STUDY.md`、`results/research/retouch_unified_20260929/FINDINGS.md`（Addendum 49、54、55、56、57 與 10-23 段）、`docs/Fake&Filter定義.docx`（組員的類別定義）。寫法參照三份 skill：ljg-xray-paper（問題／視角／結果、承重概念零術語、餐巾紙一句話＋圖、Δ≈0 就寫 0）、intro-drafter（六段邏輯鏈）、paper-writer（只用結構建議）。
>
> 規則：路徑一律相對於 `C:\My_Project\AIGC`；每個數字附來源檔；差異落在 seed 間變動內就寫 0。兩個結果還沒出來，受影響的句子各寫兩版：**Addendum 59**（單張照片能不能分辨大眼／瘦臉／美白）與**真人測試 H1**。

---

## 1. X 光：問題、視角、結果

### 1.1 三句話

**問題。** 美顏 App 和修圖服務會把臉上的皮膚磨平。現在抓偽造人臉的程式只回答「真」或「假」，沒有「只是美顏過」這個選項，所以一張只磨過皮的真人照片常被說成假的；就算判對了，它給的理由（一張熱圖，或一段 AI 自己寫的描述）也沒有人能查證。

**視角。** 不比誰的分數高，而是把「拿給一個人看的判定」拆成三個承諾，每個承諾配一個可能失敗的測試：答案分三種（真的、偽造、只是美顏）；圈出來的位置真的是判定的理由；說出口的每一句都對得上模型自己算出來的結果。最後問一個關於人的問題：這樣有沒有讓人判得更準。

**結果。** 以下是實驗量到的：

- **答案。** 同一個架構、同樣只用 FF++ 訓練，不給任何美顏例子時，商用磨皮（阿里 Smoothing-90）過的真臉有 54.2／56.1／43.5% 被說成假（三個 seed）；把磨皮同時給真臉和偽造臉看，降到 5.9／6.1%（`docs/paper_v2/tables/tab_v4_tradeoff.tex`，列 P0 與 P2 symmetric smoothing）。完整系統把這批磨皮真臉 98.8% 說成「美顏」、0.8% 說成「偽造」（`results/research/alipair_zeroshot_20260929/main_claim_A.json`，`ours main s1` 的 `native_s90`）。
- **同一個改動對「美顏過的 deepfake 被放走」的影響是 0。** Celeb-DF-B 美顏後 AUC：不給美顏 0.860／0.883／0.883，給了 0.866／0.888（同上表 Celeb-DF-B 欄），差異在 seed 間變動之內。
- **「美顏」這個答案本身不是誣告消失的原因。** 用同一份資料、只學真／假的對照模型，在同一門檻下誣告 9.1%，三類主模型 8.6%，差 0；三類模型多給的是「美顏」這個答案本身（配對讀法 70.5% → 32.5%），代價是表情重演變差（FF++ 域 AUC 0.842 → 0.718）（同上表，binary control 列與 ours three-way 列）。
- **位置。** 把圈起來的區域換回原圖像素，局部偽造的判定有 93.5–94.0% 翻回去；把真正被改的地方換回去是 93.6–94.1%；同一骨幹上的 Grad-CAM 45.4–50.9%，固定圈臉中間 38.6–40.9%（`docs/paper_v2/tables/tab_cgd_explain_all.tex`）。美顏類弱很多：換回指名部位讓美顏分數平均降 0.370，隨便換一個別的部位降 0.210（`results/research/explain_vlm_20261012/HOLDOUT_FINAL.md` §3）。
- **句子。** 讓 AI 自己看圖寫描述，盲配對在 holdout 上只有 51.3–52.8%（丟銅板 50%），同一套裁判分辨兩個不同的人是 95.3–99.3%（`HOLDOUT_FINAL.md` §2、`results/research/explain_vlm_20261012/HOLDOUT_V4_LORA.md`、`results/research/explain_vlm_20261012/report/REPORT_DRAFT.md` §5.2）。所以句子由程式從模型結果組出，再由規則查核。讓語言模型改寫我們的句子，結果和模板沒有差別（每種風格約 20 種字串，`results/research/explain_vlm_20261012/nl_v5/P3_RESULTS.notes.md`），差 0，撤回。
- **人。** 真人測試尚未施測，兩版結果句寫在第 3、5、6 節。

我們自己的破口（同樣是量到的，第 7 節展開）：美顏過的 deepfake 影片有 16.6% 被我們說成「美顏」（同一批未美顏時 3.6%）；商用服務沒修過的原圖有 20.8% 被說成美顏；四種美顏操作只認得出磨皮。

實驗支持的解讀（屬於論文，不是專題主張）：偵測器把「比周圍更平滑的臉」讀成換臉留下的痕跡；只磨臉的邊緣一圈幾乎不會被誣告，整臉磨平才會（`results/research/retouch_unified_20260929/BDRY38.md`，Addendum 57）。

### 1.2 三個承重概念（拿掉名字也講得通）

**(1) 跟自己的原圖比。** 場景是一台體重計。

1. 你剪頭髮前量一次，剪完再量一次。剪完重了 0.1 公斤，可能只是誤差。
2. 100 個人都在剪頭髮前後各量一次，有 95 個「剪完變重」。這台體重計把頭髮讀成了重量，而且跟你把「過重」的線畫在哪裡無關。
3. 換成偵測器：同一張臉、修圖前後各給一次偽造分數，數「修圖後比較高」的組數比例。50% 表示修圖沒影響；17 個已發表偵測器有 15 個落在 89–99%（`main_claim_A.json` 的 `paired_up`）。

這叫「配對、不設門檻的讀法」（paired, threshold-free）。它不需要先選門檻，所以沒人能說「是你門檻設壞了」。

**(2) 還原測試。** 場景是修車。

1. 師傅說「異音來自左前輪」。換掉左前輪，異音停了，他說對了。
2. 但如果隨便換一顆輪子，異音也常常停，他那句話就沒什麼價值；要比的是「他指的那顆」和「隨便一顆」差多少。
3. 換成系統：它在臉上圈一塊說「證據在這」。把這塊換回原圖的像素再問一次，判定從「偽造」翻回去的比例就是分數；換回真正被改的地方是上限，固定圈臉中間是對照。我們的圈 93.5–94.0%，上限 93.6–94.1%，Grad-CAM 45.4–50.9%，臉中間 38.6–40.9%；反過來只換圈外，翻轉 0.1–0.4%（`tab_cgd_explain_all.tex`）。

這叫 restoration test：圈的地方「夠」（換掉它判定就變）而且「必要」（不換它判定就不變）。

**(3) 盲配對。** 場景是星座運勢。

1. 兩張運勢，一張寫給你，一張寫給你朋友，請第三個人看你一眼，猜哪張是你的。
2. 如果運勢真的在寫你，他猜得出來；如果他只猜對一半，運勢就是對誰都成立的萬用句。
3. 換成 AI：一張被改過的臉和它的原圖，各請 AI 寫一句描述；另一個 AI 看改過的那張，猜哪句是寫它的。結果 51.3–52.8%；177 組裡有 102 組，改過的臉和原圖拿到一字不差的同一句「眼睛細緻，邊緣清晰，顏色均勻。」（`results/research/explain_vlm_20261012/MATCHING_v2.md` §6）。

這叫 blind matching（M1）。它量的是「這句話有沒有看圖」；BLEU、CIDEr 量的是「像不像參考答案」，所以後者會給一個不看圖的常數句最高分（BLEU-4 44.4，微調模型 38.9，`results/research/explain_vlm_20261012/MATCHING_v4_LORA.md` §8）。

一般術語，一句話帶過：

- **對帳（查核器）**：像把收據逐行對銀行帳單；句子裡的判定、部位、操作、數字都必須在模型輸出的那筆紀錄裡找得到，找不到就不顯示。
- **「原圖只誤判 5%」的門檻**：先把嚴格度調到 100 張沒修過的照片只冤枉 5 張，再看修過的照片被冤枉幾張。
- **AUC**：隨機拿一張真、一張假，系統把假的那張排在前面的機率；0.5 等於猜。

### 1.3 餐巾紙一句話

> 抓假照片的程式只會說真或假，所以把磨過皮的真人說成假的；我們的系統會說真的、假的、還是只是美顏，把理由圈在臉上，只說程式對過帳的話，因為 AI 自己看圖寫的理由跟丟銅板差不多，最後再找真人測它有沒有幫人判得更準。

英文版（海報與簡報第一頁）：

> Fake-face detectors only say real or fake, so they call a skin-smoothed real face fake; our system says real, forged or just beautified, circles its reason on the face, and says only what code has checked, because the reasons an AI writes for itself match their own photo about as often as a coin flip; then we test with real people whether it helps them judge.

這句話有五個子句，第 5 節的網站一頁證明一個子句。

### 1.4 餐巾紙圖

```
   BEFORE                                  AFTER skin smoothing (same person)
   +-------+                               +-------+
   |  o o  |  -------- beauty app ------>  |  o o  |
   |   -   |                               |   -   |
   +-------+                               +-------+
       |                                       |
       |  real/fake detector (SBI, median)     |
       +--->  0.21 . . . . . . . . . 0.99  <---+   ==> "FAKE"  (15 of 17 detectors)
       |                                       |
       |  our system                           |
       +--->  real . . . . . . beautified  <---+   (98.8 %)
                                    |
             +----------------------+----------------------+
             |                      |                      |
           WHICH?                 WHERE?                  WHY?
      real / forged /        circle on the face     4 sentences written
        beautified                                  by code, then checked
             |                      |                      |
      test: same model       test: put original     test: free AI text is
      w/o beauty data:       pixels back inside     matched to its own
      44-56 % called fake;   the circle; answer     photo 51-53 %
      with it: 6 %           flips 94 %             (coin = 50 %)
      (escape: 0 change)     (Grad-CAM 45-51 %)     -> code writes instead
             \                      |                      /
              +---------------------+---------------------+
                                    |
                                  PEOPLE
                      do students judge better with it?
                         (24 people, result pending)
```

---

## 2. 這是什麼樣的專題

### 2.1 解一個問題，不是刷一個指標

問題是一個具體的人會遇到的事：他的照片只是開了美顏，系統卻說他造假，而且系統給的理由沒有人能查。所以成功的標準不是某個 AUC 比別人高，而是三個承諾各自通過一個可能失敗的測試，再加上一個人的測試。由此推出兩條寫作規則：

- **和已發表偵測器的比較是稽核**，用來證明問題存在（17 個裡 15 個在 89–99% 的配對把磨皮真臉判得更假），不是排行榜。報告和海報不寫「我們比 X 好」。
- **公平對照只有一種**：我們自己的架構，有美顏訓練 vs 沒有美顏訓練（同資料、同骨幹、同選模規則，只差訓練時有沒有給磨皮）。結果照實寫：誣告 43.5–56.1% → 5.9–6.1%；美顏 deepfake 的放行改變 0；代價是強磨皮假臉的漏抓比未處理時多 14.6／17.5 點，未處理 Celeb-DF-v2 影片 AUC 0.938–0.940 → 0.919／0.934（`tab_v4_tradeoff.tex`）。

### 2.2 一條主線

一個人拿到一張臉的判定時要知道三件事，系統的每一部分只回答其中一件，最後一環問人：

```
  ANSWER  ------>  WHERE  ------>  SENTENCES  ------>  PEOPLE
  real / forged /  circle on the   composed by code,   do they judge
  beautified       face            checked by code     better with it?
```

「讓 AI 自由描述不可靠」的實驗是「句子」這一環的理由（為什麼不讓 AI 自己寫），不是另一條線。17 個偵測器的量測是「為什麼需要第三個答案」的理由，也不是另一條線。

### 2.3 範圍內

| 項目 | 主張到哪裡為止 | 證據 |
|---|---|---|
| 三種答案（靜態人臉照片） | 商用磨皮真臉：美顏 98.8%、偽造 0.8%；同架構有／無美顏訓練：誣告 43.5–56.1% → 5.9–6.1% | `main_claim_A.json`；`tab_v4_tradeoff.tex` |
| 證據位置 | 局部偽造：還原測試 93.5–94.0%；美顏：較弱（0.370 對 0.210）；整臉換臉：句子說「證據遍布整臉」 | `tab_cgd_explain_all.tex`；`HOLDOUT_FINAL.md` §1、§3 |
| 對過帳的句子 | 程式從紀錄組出四句，規則查核器（H1–H6、G7–G10）逐句對帳；361 張 holdout 上模板句失敗 0 則（依構造本來就該是 0）；查核器擋下語言模型改寫的錯句 390（英）／206（中）則 | `HOLDOUT_FINAL.md` §1；`results/research/explain_vlm_20261012/nl_v5/GATE_V3_RESULTS.notes.md` |
| 自由描述不可靠 | 盲配對 51.3–52.8%、FakeVLM 50.8%、BLEU 偏好常數句 | `HOLDOUT_FINAL.md` §2、§5；`HOLDOUT_V4_LORA.md`；`MATCHING_v4_LORA.md` §8 |
| 真人測試 | 12 張臉、3 個條件、目標 24 人，H1 事前門檻 +10 點 | `docs/capstone/human_study/PRE_DECLARED_HUMAN_STUDY.md`（Amendment 3） |
| 瀏覽器系統 | 照片不上傳；每張 0.18–0.56 秒（桌機 headless Chrome、單執行緒） | `docs/demo_ru/README.md` |
| 17 個已發表偵測器 | 只當「問題存在」的稽核 | `main_claim_A.json` |

### 2.4 範圍外（明確不主張）

| 項目 | 理由與數字 |
|---|---|
| 現場自拍 demo | 沒修過的一般照片常被說成美顏或偽造：商用服務原圖 20.8% 說成美顏（`main_claim_A.json`，`native_orig`），holdout 100 張未修 FF++ 真臉 26 張說成美顏、10 張說成偽造（`HOLDOUT_FINAL.md` §1），一般 FairFace 照片只有 23.2% 說成真的（`results/research/retouch_unified_20260929/PRE_DECLARED.md` Addendum 58 診斷段） |
| Instagram AR 濾鏡 | FairBeauty、B-LFW 的原圖沒走過同一條渲染管線，分不出是濾鏡還是管線；把臉塗灰後原圖 100%、濾鏡版 99.5% 都判假（`FINDINGS.md` 2026-10-22 16:40 段；Addendum 13、56） |
| 表情重演 | DF40 重演 AUC：FF++ 域 0.718、Celeb-DF 域 0.502（等於猜）（`tab_v4_tradeoff.tex`、`docs/paper_v2/tables/tab_v4_df40.tex`） |
| 大眼、瘦臉、美白的命名 | 真實 AR 濾鏡上的召回：大眼 0.003、瘦臉 0.03、美白 0.18、磨皮 0.24（`results/research/retouch_unified_20260929/FB_OPS.md`，Addendum 55）。單張照片能不能做到，Addendum 59 正在測，句子兩版見下 |
| 任何偵測器排名 | 未處理資料上和 Effort、Forensics Adapter 打平（配對 CI 含 0，`REPORT.md` Table 2）；Celeb-DF-B「美顏後 AUC 17 個裡最高」是論文的主張，而且公平對照顯示這個差距主要來自基礎訓練配方，不是美顏訓練（`FINDINGS.md` 2026-10-11 第三個 seed 段），專題不主張 |
| 語言模型改寫解釋 | 測過；數字和校準句移交程式後，模型的文字每種風格約 20 種字串，和模板沒有差別（`P3_RESULTS.notes.md`），撤回 |

**Addendum 59 影響的句子（兩版）。** 事前規則：只學單一操作的模型在無損圖上 AUROC < 0.90 判定「單張照片做不到」，≥ 0.95 判定「有痕跡、我們沒學到」，中間算「弱」（`results/research/retouch_unified_20260929/PRE_DECLARED.md` Addendum 59）。

- 版本 A（< 0.90）：「在商用強度下，大眼、瘦臉、美白在一張照片裡留下的痕跡，連只學這一件事的模型都分不出來（AUROC x），所以系統只說『磨皮』，這是資料本身的上限。」
- 版本 B（≥ 0.95）：「只學這一件事的模型在單張照片上分得出大眼、瘦臉、美白（AUROC x），是我們的系統沒學到；系統目前只說『磨皮』，命名其他三種是可以修的下一步。」
- 中間值時用：「痕跡很弱，只學這件事的模型 AUROC x，經過分享時的壓縮與縮放降到 y，所以系統不命名它。」

進度註記（不可引用為結論）：截至 2026-10-23 18:41 只跑完大眼一項，無損 AUROC 0.933 [0.922, 0.943]，JPEG q90＋縮到 256 px 後 0.833 [0.817, 0.851]（`results/research/retouch_unified_20260929/oracle_ops.json`），落在「弱」區間；瘦臉在跑，美白與磨皮（正對照）未跑。

### 2.5 論文的機制實驗：一句話

實驗室論文另外研究了偵測器為什麼把磨皮當成偽造、為什麼調門檻救不了（皮膚比周圍平滑的臉正好像換臉留下的痕跡，`BDRY38.md`、`FINDINGS.md` Addendum 47、57），專題只引用「訓練時磨皮要給真假兩邊」這個結論，不重做、不主張。

---

## 3. 報告引言的六段邏輯鏈

報告本文是英文；下面用中文寫出每段要說的內容，翻成英文時數字與來源不變。每段 2–4 句。

**段 1　背景與實例。** 社群上的人臉照片很多經過美顏 App 或修圖服務處理，而人臉偽造偵測器只回答「真」或「假」。以 FFHQ 第 17006 張為例：同一個人、沒有任何偽造，只經過阿里修圖服務最強的磨皮（Smoothing-90），SBI 的偽造分數從 0.711 升到 0.999、DFD-HR 從 0.426 升到 0.936、Forensics Adapter 從 0.104 升到 0.844，三者都超過各自「原圖只誤判 5%」的門檻（`docs/demo_ru/cases/cases.json` 案例 `A_17006`，由 `docs/demo_ru/build_cases.py` 以固定種子 20261022 抽出，不是人挑的）。這不是個案：2,210 組逐像素對齊的原圖／磨皮配對中，17 個已發表偵測器有 15 個在 89–99% 的配對把磨皮版打得比原圖更假，固定在原圖 5% 誤判的門檻時有 13 個誣告 36–69% 的磨皮真臉（`results/research/alipair_zeroshot_20260929/main_claim_A.json`；整理於 `docs/capstone/MAIN_CLAIMS_20261022.md`）。

**段 2　既有做法的不足（三個）。** 第一，二元偵測器沒有「美顏」這個答案，磨皮真臉只能被說成假，或被歸進「真」而看不出它修過。第二，回答「證據在哪」的常見做法是事後熱圖，但在同一個骨幹上把 Grad-CAM 圈出的區域換回原圖，只有 45.4–50.9% 的局部偽造判定會消失，和固定圈臉中間的 38.6–40.9% 相差不大（`docs/paper_v2/tables/tab_cgd_explain_all.tex`）。第三，回答「為什麼」的常見做法是讓視覺語言模型自由描述，但這些描述在盲配對中只配對成功 51.3–52.8%（`results/research/explain_vlm_20261012/HOLDOUT_FINAL.md` §2、`HOLDOUT_V4_LORA.md`），端到端的 FakeVLM 50.8%（`HOLDOUT_FINAL.md` §5），而文獻常報的 BLEU-4 給一個不看圖的常數句 44.4 分，高於微調過的模型 38.9 分（`results/research/explain_vlm_20261012/MATCHING_v4_LORA.md` §8）。

**段 3　問題本質與目標。** 使用者需要的不是更高的 AUC，而是三個問題的答案：這張臉是真的、被偽造、還是只被美顏；證據在臉的哪裡；系統說的話對不對得上它自己算出來的東西。這件事有三個硬限制：只有一張照片、沒有原圖可比；照片不能離開使用者的裝置；顯示的每一句都必須能用程式對回模型輸出，對不上就不顯示。目標因此是：給一張靜態人臉照片，回答三種之一、圈出證據位置、只顯示對過帳的句子，並用真人測試檢查這樣有沒有讓人判得更準。

**段 4　關鍵挑戰（三個，各對應段 2 的一個不足）。** 第一，第三個答案可能變成假臉的藏身處：同一架構若只讓真臉在訓練時看到磨皮，會學到「皮膚平滑就是真的」，強磨皮假臉的漏抓因此多 56.4–62.9 點（`docs/paper_v2/tables/tab_v4_tradeoff.tex` 列 P1 smoothing only；`docs/capstone/REPORT.md` Table 3）。第二，圈出的位置必須真的是判定的理由，而事後熱圖只比固定猜臉中間好一點（段 2 的數字）。第三，語言模型寫的句子會出錯，而且錯得讓規則看不出來：示範錄影時一句 "The model's decision is fake, with a score of 1.00 concentrated on the mouth." 通過了當時的查核，補上 G8、G9 兩條規則後，存檔的 holdout 輸出中有 390 則英文、206 則中文已出貨文字被擋下（`docs/capstone/REPORT.md` §6.2；`results/research/explain_vlm_20261012/nl_v5/GATE_V3_RESULTS.notes.md`）。

**段 5　解法（一個模組對一個挑戰）。** 對第一個挑戰，偵測器（CLIP ViT-L/14＋LoRA，與實驗室論文共用）輸出真、偽造、美顏三類，訓練時把磨皮同時給真臉和偽造臉；在只用 FF++ 的公平對照中，這讓商用磨皮真臉的誣告從 43.5–56.1% 降到 5.9–6.1%，美顏 deepfake 的 AUC 不變（0.860–0.883 對 0.866–0.888，`tab_v4_tradeoff.tex`）；回到段 1 的 17006，系統對原圖說「真的」、對磨皮版說「美顏」，偽造分數 0.003 與 0.001（`cases.json`）。對第二個挑戰，證據頭用每個編輯的精確範圍訓練，輸出 16×16 證據圖，再用 478 個臉部特徵點對到眼、鼻、嘴、皮膚、輪廓或整臉，並以還原測試驗證。對第三個挑戰，程式從模型輸出的紀錄組出四句（判定與分數、部位、達門檻的美顏操作、一句「分數不是校準過的機率」），每句顯示前由規則查核器對回紀錄；語言模型改寫測過後撤回，因為數字與校準句移交程式後，它的文字每種風格只剩約 20 種字串（`results/research/explain_vlm_20261012/nl_v5/P3_RESULTS.notes.md`）。整套在瀏覽器內執行，照片不上傳，每張 0.18–0.56 秒（`docs/demo_ru/README.md`，桌機 headless Chrome）。

**段 6　貢獻（四點，各對應一節）。**

1. 一個回答三種、圈出證據、只顯示對過帳句子的人臉檢查系統，在瀏覽器內執行（§3、§9）。
2. 對系統每個承諾各做一個可能失敗的測試：有／無美顏訓練的公平對照（誣告 43.5–56.1% → 5.9–6.1%，放行改變 0，代價照列）；還原測試（93.5–94.0%，Grad-CAM 45.4–50.9%）；查核器擋下的錯句（390／206 則）（§4–§6）。
3. 自由描述式解釋不可靠的證據（盲配對 51.3–52.8%、FakeVLM 50.8%、BLEU 偏好常數句），說明為什麼系統不讓任何模型描述影像（§7）。
4. 事前登記的真人測試（目標 24 人、12 張臉、三個條件）（§8），結果句兩版：
   - H1 成立：「看到我們的圈和句子時，受試者三選一的正確率比只看判定高 X 點［95% CI］，達到事前門檻 +10 點。」
   - H1 不成立：「看到我們的圈和句子時，受試者的正確率沒有比只看判定高到事前門檻（差 X 點［95% CI］）；部位指認、過度信任（描述性）與 SUS 照事前登記全部報告。」

**建議的報告章節對應**：§1 引言、§2 相關研究、§3 系統、§4 答案對不對（17 偵測器稽核放開頭當問題證據，接公平對照與逃逸路線）、§5 圈的位置是不是理由、§6 句子對不對得上、§7 為什麼不讓 AI 自由描述、§8 人看了有沒有比較準、§9 部署、§10 做不到的事。現行 `REPORT.md` 的 §4（17 偵測器）與 §5.2（機制對照）依此縮短。

**鏈的檢查**：段 1 的 17006 在段 5 回來；三個不足 → 三個挑戰 → 三個模組一一對應；目標的四個動詞（回答、圈出、只顯示對過帳、測人）對應貢獻 1–4。

---

## 4. 分工聲明（三句）

本專題和實驗室投稿論文共用三樣東西：偵測器本身（CLIP ViT-L/14＋LoRA 三類模型與證據頭）、17 個已發表偵測器的量測，以及有／無美顏訓練的對照實驗；報告引用它們，並在每個數字旁標出結果檔。專題自己建造的是把偵測器輸出變成人能看、能查的部分：以臉部特徵點命名部位、程式組句與規則查核器、語言模型改寫與視覺語言模型自由描述的測試、在瀏覽器內執行並附有標準答案案例的網站，以及事前登記的真人測試。專題的主張只落在後者（答案、位置、句子、人），不主張任何偵測器排名，論文的機制分析也不算專題貢獻。

（逐支腳本的歸屬以 `JUDGE_REHEARSAL_20261022.md` 第 2 節表格第 2 列的草稿為起點，送出前由組員逐項確認；這三句放在報告 §1 結尾與簡報第 2 頁頁尾。）

---

## 5. Demo 網站：五頁，一頁證明一個子句

| 頁 | 證明的子句 | 主要畫面 | 現況 |
|---|---|---|---|
| 1 問題 | 「只會說真或假，所以把磨過皮的真人說成假的」 | 一組修圖前後＋各偵測器判定；17 偵測器配對長條圖 | `docs/demo_ru/cases.html` A 分頁已有案例，缺整體圖 |
| 2 三種答案 | 「會說真的、假的、還是只是美顏」 | 同組案例的三類判定；有／無美顏訓練對照；逃逸路線 | 待做（案例資料已有） |
| 3 圈在臉上 | 「把理由圈在臉上」 | 內建範例分析、輪廓、部位；還原測試動畫與數字 | `docs/demo_ru/index.html` 已有分析，缺還原測試區塊 |
| 4 對過帳的句子 | 「只說程式對過帳的話，因為 AI 自己寫的理由跟丟銅板差不多」 | 紀錄 → 四句 → 查核表；被擋下的真實錯句；盲配對與 BLEU | 待做（材料卡片已有） |
| 5 人 | 「找真人測它有沒有幫人判得更準」 | 設計、三條件截圖、正確率長條＋CI | 待做（等施測） |

### 頁 1　問題（由 `cases.html` 的 A 分頁改）

- 畫面：第一屏是 `A_17006` 修圖前後兩張，下面一列偵測器（Effort、Forensics Adapter、DFD-HR、SBI、我們）的分數與「判假／不判假」；第二屏是 17 個偵測器「修圖版比原圖更假」的配對比例長條圖，畫 50% 線與 95% CI；「換一組」按鈕在 8 組固定種子案例之間切換，旁邊固定顯示整體數字 15/17、89–99%。
- 資料與檔案：
  - 案例影像：`docs/demo_ru/cases/A_<id>_orig.jpg`、`A_<id>_s90.jpg`（8 組，`docs/demo_ru/build_cases.py` 產生）。
  - 每個偵測器每張圖的分數、門檻與判定：`docs/demo_ru/cases/cases.json` 的 `thresholds.alibaba` 與 `cases[id 以 A_ 開頭].verdicts.{effort,fadapter,dfdhr,sbi,ours}.{original,beautified}.{score,called_fake}`。
  - 17 偵測器整體：`results/research/alipair_zeroshot_20260929/main_claim_A.json` 的 `rows.<det>.paired_up`、`paired_up_ci`、`fa_s90_at_5pct`、`fa_ci`（現有圖 `docs/capstone/img/retouch_paired_en.png` 沒有 CI，建議改由這個 json 重畫）。
  - 中位數（SBI 0.208 → 0.991 等）：`docs/paper_v2/tables/tab_v4_retouch.tex`（`REPORT.md` Table 1）。

### 頁 2　三種答案

- 畫面：(a) 同 8 組案例，我們的三類判定（原圖「真的」、磨皮版「美顏」），旁邊整體數字：原圖 真 78.4／美顏 20.8／偽造 0.8%，磨皮版 美顏 98.8／偽造 0.8%；(b) 公平對照小表：同架構不給美顏 vs 對稱給磨皮，三欄＝商用磨皮真臉被判假、美顏 deepfake AUC、強磨皮假臉漏抓增加；(c)「多一個答案的代價」一行：同資料只學真假的模型，誣告 9.1% 對 8.6%（差 0），表情重演 0.842 對 0.718；(d) 逃逸路線：美顏過的 deepfake 16.6% 被說成美顏（未美顏 3.6%），在展場本機另顯示 Celeb-DF-B 案例。每個美顏判定旁同時顯示偽造分數。
- 資料與檔案：
  - 三類判定整體：`main_claim_A.json` 的 `rows["ours main s1"|"ours main s2"].native_orig`、`native_s90`。
  - 公平對照與代價：`docs/paper_v2/tables/tab_v4_tradeoff.tex` 列 P0、P2 symmetric smoothing、ours three-way、binary control（`docs/paper_v2/make_tables_v4.py` 產生；原始值在 `results/research/alipair_zeroshot_20260929/exposure_ali.json` 與 `results/research/celebdfb_v2_20260927/fair_cdfb.json` 的 `RU-clipe5fbp0_s20260929`、`_s20260930`、`_s20261001`、`RU-clipe5fbg0oy_s20260929`、`_s20260930`）。
  - 逃逸路線：`fair_cdfb.json` 的 `RU-clipe5.native.synthesis.filter`（3.6）與 `RU-clipe5.native.synthesis_beautified.filter`（16.6），第二個 seed `RU-clipe5-s2`（3.9、16.1）。
  - Celeb-DF-B 案例：`cases.json` 中 `public: false` 的 `B_deepfake_*`、`B_genuine_*` 與對應 jpg（資料集禁止再散布，只在展場本機顯示）。

### 頁 3　圈在臉上（`index.html`）

- 畫面：四個內建範例，按下去顯示判定、輪廓、指名部位與四句話；旁邊「還原測試」區塊：同一張圖把圈內換回原圖後判定翻回，接著整體數字（我們 93.5–94.0%、上限 93.6–94.1%、Grad-CAM 45.4–50.9%、臉中間 38.6–40.9%；美顏類 0.370 對 0.210）。頁首寫明「網頁跑的是較小的 EfficientNet-B4 模型，和主模型 50 張裡判定一致 43 張、部位一致 38 張」。上傳按鈕保留但不放在第一屏，旁邊寫未修照片的誤判率（頁 2 的 20.8%）。
- 資料與檔案：
  - 分析路徑：`docs/demo_ru/index.html`、`demo_core.js`、`evidence_overlay.js`、`face_masks.js`、`explain_t2.js`、`models/ru4e_effb4.onnx`、`examples/ex1.png`–`ex4.png`。
  - 還原測試整體數字：`docs/paper_v2/tables/tab_cgd_explain_all.tex`（ours、no head Grad-CAM、centre prior 三列）；`results/research/explain_vlm_20261012/HOLDOUT_FINAL.md` §3（fake all n=82：85.4／87.8／13.9；filter all n=62：0.370／0.373／0.210），原始逐張值 `restoration_holdout.json`。
  - 對照圖：`docs/capstone/paper/figs/fig_evidence_gradcam.png`（項目清單 `fig_evidence_gradcam_items.json`）。
  - 一致率 43/50、38/50：`docs/demo_ru/README.md` 的 ONNX 匯出段。

### 頁 4　對過帳的句子（新頁）

- 畫面：左欄是一筆紀錄（判定、三類分數、四個操作分數、各部位證據平均、指名部位）→ 程式組出的四句 → 查核表（每條規則通過或不通過）；下面三個被擋下的真實錯句：英文的「…does not indicate how certain the model is」（G8）、「score of 1.00 concentrated on the mouth」（G9）、中文裡出現英文類別鍵「模型的判定是 fake」。右欄是盲配對：同一句寫給改過的臉與原圖的例子、51.3–52.8% 對丟銅板 50% 與兩人對照 95.3–99.3%、BLEU 表（常數句 44.4 最高）。頁尾一行：「我們也試過讓語言模型改寫，結果和模板沒有差別，所以出貨的是模板。」
- 資料與檔案：
  - 紀錄與組句：`results/research/explain_vlm_20261012/evidence_holdout.jsonl`；組句程式 `results/research/explain_vlm_20261012/explain_v2.py` 與網頁版 `docs/demo_ru/explain_t2.js`。
  - 查核規則：`results/research/explain_vlm_20261012/validate_text.py`（H1–H6）、`nl_v5/gate_v3.py`（G8、G9）、`nl_v5/nl_p3.py`（G10）。
  - 被擋下的錯句：`docs/capstone/src/record_demo_log_en_run2_gate_v2.json`、`record_demo_log_run1_gate_v2_p2_rejected.json`、`record_demo_log_run2_p3r1_english_key.json`；整批數字 `nl_v5/GATE_V3_RESULTS.notes.md`（390／206），例句 `nl_v5/GATE_V3_RESULTS.md`；卡片 `docs/capstone/examples_png/card_gate_catches.png`。
  - 盲配對：`HOLDOUT_FINAL.md` §2（52.8）、`HOLDOUT_V4_LORA.md`（51.3）、`HOLDOUT_FINAL.md` §5（FakeVLM 50.8、判錯 37.7%）、`MATCHING_v2.md` §6（102/177 與例句）、`report/REPORT_DRAFT.md` §5.2（對照 95.3–99.3）、`MATCHING_v4_LORA.md` §8（BLEU、CIDEr）；卡片 `docs/capstone/examples_png/card_vlm_observation_pairs.png`、`card_fakevlm_vs_ours.png`。
  - 語言模型撤回的依據：`nl_v5/P3_RESULTS.notes.md`（約 20 種字串）。

### 頁 5　人（新頁）

- 畫面：一張設計圖（12 張臉＝真 4、偽造 4、美顏 4；三個條件依受試者編號輪替）、三個條件的截圖、主要結果長條（三條件三選一正確率＋95% CI，配對 bootstrap）、部位指認、SUS。標題用兩版之一：
  - H1 成立：「看到圈和對過帳的句子，人判得比只看判定準 X 點。」
  - H1 不成立：「看到圈和對過帳的句子，人沒有判得比較準（差 X 點）；我們照事前登記報告。」
- 資料與檔案：`docs/capstone/human_study/PRE_DECLARED_HUMAN_STUDY.md`（設計與四次修正）、`study.html`、`screens/study_trial_C0.png`、`study_trial_C1.png`、`study_trial_C2.png`、`analyse.py` 的輸出（尚未產生；輸入為 Google Sheet 匯出的 CSV，建議輸出到 `docs/capstone/human_study/RESULTS.md` 與 `results.json`）。`materials/` 的影像不放上公開網址（`human_study/README.md` 記載授權不允許再散布）。

### 跨頁要先處理的四件事

1. **授權衝突。** `build_cases.py` 把阿里案例標成 `public: true`，但 `human_study/README.md` 記載 RetouchingFFHQ 的人臉裁切授權不允許公開再散布。公開網址上線前要確認；確認前比照 Celeb-DF-B，只在展場本機顯示影像，公開版只放分數。
2. **範例 3 與主張不一致。** `index.html` 的範例 3 是阿里「大眼 90」，但系統只認得出磨皮；換成一張 Smoothing-90，或保留並讓頁面明寫「這種操作系統認不出來」。
3. **每個案例旁都放整體數字**（案例是固定種子抽的，不是挑的），單一案例好不好看都不影響整體。
4. **42.4% 這個數字暫時不要用。** `GAP_VS_WINNERS` 與 `JUDGE_REHEARSAL` 引用「網頁 B4 模型把 42.4% 的 Celeb-DF-v2 真臉判假」，但它標註的 `REVIEW_20261016.md` 第 121 行寫的是主模型 18.94%（出自 `RESULTS_clipe5_s20260929.md`），42.4% 沒有找到原始結果檔。

---

## 6. 海報英文稿（約 750 字）

> 版面建議：每區一張圖或截圖，字只放下面這些。方括號內是待填的數字或二選一的句子。

**BEAUTIFIED IS NOT FORGED**
*A face checker that says real, forged or beautified, shows where its evidence is, and checks every sentence it shows*

**Fake-face detectors only say real or fake, so they call a skin-smoothed real face fake. Our system adds a third answer, beautified, circles its evidence on the face, and shows only sentences that code has checked against the model's output, because free-form explanations written by vision-language models match their own photo about as often as a coin flip.**

**1. The problem.** One FFHQ face (no. 17006), before and after a commercial service's strongest skin smoothing: same person, nothing forged. SBI's forgery score rises from 0.711 to 0.999, DFD-HR's from 0.426 to 0.936. Across 2,210 such pairs, 15 of 17 published detectors score the smoothed face as more forged than its own original in 89-99% of pairs (50% means no effect). These detectors are an audit of the problem, not a leaderboard.

**2. The system.** The photo is analysed in the browser and never uploaded. The detector (CLIP ViT-L/14 with LoRA) returns one of three answers. An evidence head marks where the evidence is, and face landmarks name the part: eyes, nose, mouth, skin, contour or whole face. Code writes four sentences from the result: answer and score, part, beautification operations above threshold, and a note that the score is not a calibrated probability. A rule checker matches every sentence to the result before it is shown.

**3. Is the answer right?** The fair comparison is our own architecture trained with and without beautified examples, on the same public data and nothing from the retouching service. Without them, 43.5-56.1% of the commercially smoothed real faces are called fake (three seeds); with skin smoothing shown to both real and forged training faces, 5.9-6.1%. On phone-app beautified deepfake videos the change makes no difference (AUC 0.86-0.89 either way). The price: heavily smoothed forgeries are missed 15-18 points more often. The full system calls 98.8% of the smoothed real faces beautified and 0.8% forged.

**4. Is the circle the reason?** Put the original pixels back inside the circle and ask again. On held-out part-level forgeries the answer flips in 93.5-94.0% of cases; restoring the true edited region flips 93.6-94.1%, Grad-CAM on the same backbone 45-51%, a fixed circle mid-face 39-41%. Restoring everything outside the circle flips at most 0.4%. For beautified faces the evidence is weaker: restoring the named part lowers the beautified score by 0.37, a random part by 0.21.

**5. Why code writes the sentences.** Vision-language models asked to describe the circled region fail a blind test. A judge sees an edited face and two descriptions, one written for it and one for its untouched original, and picks its own: 51-53% on held-out pairs, where a coin gives 50% and two different people are told apart 95-99% of the time. In 102 of 177 pairs both faces got the same sentence word for word, yet BLEU-4 ranks a constant sentence (44.4) above the fine-tuned describer (38.9). A language model allowed to reword our facts needed two extra rules, which blocked 390 English and 206 Chinese texts; with numbers moved to code its wording shrank to about 20 forms per style, so we ship the code template.

**6. Do people judge better?** 24 students, 12 faces each (4 real, 4 forged, 4 beautified), three conditions rotated across people: answer only; answer with our circle and checked sentences; answer with a FakeVLM description. Bar written before the first participant: our condition at least 10 points more accurate than answer only.
[If met:] With our explanation, people were [X] points more accurate [95% CI] and named the changed part in [Y]% of trials.
[If not met:] Our explanation did not make people more accurate ([X] points [95% CI]); the other measures are reported as declared.

**7. What it cannot do.** Beautified deepfakes can hide in the new answer: 16.6% of beautified deepfake videos are called beautified, 3.6% before beautification. Untouched photos are often called beautified (20.8% of the service's originals), so we show prepared cases with known answers, not live selfies. Beautified here means smoothed.
[Oracle below 0.90:] At commercial strength, eye enlargement, face slimming and whitening leave too little in one image even for a model trained on that task alone, so the system does not name them.
[Oracle at least 0.95:] A model trained on that task alone finds eye enlargement, face slimming and whitening in one image; ours did not learn them, which is the next step.
Instagram AR filters could not be tested cleanly, reenactment is at chance in the Celeb-DF domain (AUC 0.502), and the browser runs a smaller model that agrees with the main one on 43 of 50 decisions.

*Every number has a 95% bootstrap interval and a source file in the report; thresholds and pass bars were set before each run; published detectors ran with released weights. Shared with a lab paper: the detector and the 17-detector audit. Built for this capstone: part naming, sentence composer and checker, language-model tests, browser system, human study.*

---

## 7. 簡報必須主動講的三件不舒服的事

每件都放在「代價」那一頁，在評審問之前講。

**事實 1：我們自己的逃逸路線。** Celeb-DF-B 美顏過的 deepfake 影片，主模型的三類判定有 16.6%（第二個 seed 16.1%）說成「美顏」，同一批影片未美顏時是 3.6%（3.9%）；也就是美顏把大約 12.5 點的假臉搬進了美顏類（`results/research/celebdfb_v2_20260927/fair_cdfb.json`，`RU-clipe5`／`RU-clipe5-s2` 的 `native.synthesis` 與 `native.synthesis_beautified`；`FINDINGS.md` 2026-10-23 Addendum 54 段末）。

> 一句回答：「對，美顏過的假影片大約每六支有一支會被我們歸成美顏，這是多一個答案的代價，所以結果頁在每個美顏判定旁邊都同時顯示偽造分數和這個比例。」

**事實 2：沒修過的照片也常被說成美顏，所以不做現場自拍。** 商用服務 2,210 張原圖有 20.8% 被說成美顏（`main_claim_A.json`，`native_orig`）；holdout 100 張未修 FF++ 真臉有 26 張被說成美顏、10 張被說成偽造（`HOLDOUT_FINAL.md` §1）；一般 FairFace 照片只有 23.2% 被說成真的（`PRE_DECLARED.md` Addendum 58 診斷段）；Celeb-DF-v2 真臉影格 18.94% 被判偽造（`results/research/retouch_unified_20260929/RESULTS_clipe5_s20260929.md`）。

> 一句回答：「對，一般照片不在我們訓練過的範圍裡，所以我們只展示用固定種子抽出、有標準答案的案例，並把這些誤判率放在案例旁邊；把一般照片加進真臉訓練的重訓（Addendum 58）結果出來以前，這句話不改。」

**事實 3：「美顏」其實只等於「磨皮」，而且多這個答案讓表情重演變差。** 四種操作在真實 AR 濾鏡上的召回：大眼 0.003、瘦臉 0.03、美白 0.18、磨皮 0.24（`FB_OPS.md`，Addendum 55），能可靠認出的只有商用磨皮（98.8% 說成美顏）。同一份資料只學真假的對照模型，表情重演 AUC 0.842（FF++ 域）、0.647（Celeb-DF 域），三類主模型 0.718、0.502（`tab_v4_tradeoff.tex`）。Instagram AR 濾鏡因原圖沒走過同一條渲染管線，無法乾淨地測。

> 一句回答（依 Addendum 59 結果擇一）：
> - 單任務模型 < 0.90：「對，商用強度的大眼、瘦臉、美白，連只學這一件事的模型都從一張照片分不出來（AUROC x），所以系統只說磨皮，重演與 AR 濾鏡列在範圍外。」
> - 單任務模型 ≥ 0.95：「對，只學這一件事的模型分得出來（AUROC x），是我們的系統沒學到，這是下一步；重演與 AR 濾鏡列在範圍外。」
> - 介於中間：「痕跡很弱（AUROC x，分享時的壓縮後 y），所以系統不命名它；重演與 AR 濾鏡列在範圍外。」

---

## 送出前要確認的事

1. Addendum 59 跑完後，把第 2.4、6、7 節的兩版句子擇一，填入 x、y。
2. 真人測試跑完後，把第 3 節貢獻 4、第 5 節頁 5、第 6 節第 6 區的兩版句子擇一，填入 X、Y。
3. 第 4 節的分工由組員逐支腳本確認。
4. 第 5 節「跨頁四件事」的授權確認與範例 3 替換。
