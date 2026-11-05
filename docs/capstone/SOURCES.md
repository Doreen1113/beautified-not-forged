# 數字來源：海報（poster.html／poster_en.html）與報告（REPORT.md）

每個出現在海報上的數字，對應的來源檔與章節。路徑相對於專案根目錄 `C:\My_Project\AIGC`。海報 HTML 內每個數字旁另有 `<!-- src: ... -->` 註解。2026-10-15：海報區塊編號改為 1–5（原本「可驗證的解釋」與「對照」都標 3；第三欄改為先放對照（4）再放部署（5）），數字未變。英文報告與英文海報的來源見文末英文段落。

## 第 1 區　問題：美顏會騙過偵測器

| 海報上的數字 | 意思 | 來源 |
|---|---|---|
| 15／17、89–99% | 17 個已發表偵測器中，15 個在「磨皮 90」與其原圖配對中，給磨皮圖較高 P(fake) 的比例落在 89.2%（LAA-Net）到 99.3%（SRM）；另兩個為 CADDM 60.9%、NPR n/a（分數飽和） | `docs/paper_v2/tables/tab_v4_retouch.tex`，欄「above own original (%)」；同值見 `results/research/alipair_zeroshot_20260929/smoothing90_thresholdfree.json` 鍵 `paired_up` |
| 長條圖各值（SRM 99.3、DFD-HR 99.0、GenD 98.5、F3Net 97.8、SPSL 97.3、CORE 96.6、RECCE 96.5、SBI 96.2、Effort 95.6、UCF 95.4、Xception 95.2、EfficientNet-B4 93.7、Forensics Adapter 93.3、UnivFD 90.4、LAA-Net 89.2、CADDM 60.9、NPR n/a） | 同上 | 同上；圖由 `docs/capstone/src/make_retouch_chart.py` 產生 |
| 我們 32.5% | 主模型（三類，full data）同一指標 | `tab_v4_retouch.tex` 列「\ours{}, three-way, full data」 |
| 「最新的 GenD、DFD-HR」 | 「the two most recent」 | `docs/paper_v2/main.tex` §Results「Beautification hurts every detector」段 |

註：NPR 在 json 中 `paired_up` 為 31.8，但論文表標為 n/a（分數飽和），海報依論文表。

## 第 2 區　我們的偵測器

| 海報上的數字 | 意思 | 來源 |
|---|---|---|
| 0.947 | 主模型 Celeb-DF-v2 影片層級 AUC | `docs/paper_v2/main.tex` §Forgery detection under each detector's own preprocessing：「at video level 0.947 and 0.970」 |
| Effort 0.927、Forensics Adapter 0.956 | 基線 Celeb-DF-v2 影片 AUC，各自前處理（DFB crop） | `docs/paper_v2/tables/tab_reproduce.tex`（supplement Table S1），欄「Celeb-DF-v2 video AUC」「ours, DFB crop」 |
| 0.891、0.942 | 主模型 Celeb-DF-v2、DFD 影格 AUC | `docs/paper_v2/tables/tab_v4_twosided.tex` 列「\ours{} (full data, three-way)」（= `clipe5_s20260929`，見 `docs/paper_v2/make_tables_v4.py`）；main.tex 同段亦寫 frame 0.891、0.942 |
| Effort 0.879／0.933、Forensics Adapter 0.899／0.940 | 基線影格 AUC，各自前處理 | `tab_reproduce.tex`「ours, DFB crop」欄 |
| 「配對 95% 區間全部含 0，打平」 | vs Effort [−0.013, 0.038]、vs FA [−0.030, 0.013]（CDFv2）；[−0.006, 0.025]、[−0.013, 0.017]（DFD） | `main.tex` 同上段 |
| FF++ 測試集三類召回 82.7／90.9／86.7% | 同資料來源（in-domain），`ffpp3_test.txt` | `results/research/retouch_unified_20260929/RESULTS_clipe5_s20260929.md` §FF++ / cross-dataset，`indomain` {real 82.67, fake 90.86, filter 86.7}（`eval_ru.py` 的 `eval_ffpp`） |

說明：`tab_v4_twosided.tex` 只有影格 AUC；影片層級數字取自 main.tex 與 tab_reproduce.tex。基線用的是各自前處理（論文的比較規則），而 tab_v4_twosided.tex 中的 Effort／FA 是「我們的裁切」（0.881／0.939、0.887／0.940）。DFD 影片層級（我們 0.970）沒有對應的基線數字，所以海報只放 DFD 影格。

## 第 3 區　可驗證的解釋

| 海報上的數字 | 意思 | 來源 |
|---|---|---|
| 94.0%、93.5–94.0% | 主模型證據頭：還原指名區域後判定翻轉率（donor 94.0、SD-1.5 93.6、SDXL 93.5） | `docs/paper_v2/tables/tab_cgd_explain_all.tex` 列「\ours{} (CLIP ViT-L/14 + LoRA)」 |
| 上限 93.6–94.1% | 還原真正被改區域的翻轉率（ceil.） | 同上 |
| IoU 0.83–0.84 | IoU$_7$ 0.834／0.841／0.831 | 同上 |
| Grad-CAM 50.9%、45.4–50.9%、IoU 0.26–0.37、上限 85.2–85.9% | 列「no head, Grad-CAM」 | 同上 |
| 中心固定位置 38.6–40.9% | 列「centre prior / random region」flip 欄 | 同上 |
| 部位名稱 85.4%、證據圖 87.8%、82 張 | holdout 文字版還原測試 fake 合併：text_flip、map_flip、n | `results/research/explain_vlm_20261012/HOLDOUT_FINAL.md` §3 |
| 0 則出貨文字未通過再驗 | 設計 p3（英文 p3en1、中文 p3r1z），兩種語言 × 一般／專業兩種風格 × 四題 LLM 追問，「shipped fail」欄全部 0（把關 v3 ＋ LLM 部分把關含 G10）；p3r1 也是 0 | `results/research/explain_vlm_20261012/nl_v5/P3_RESULTS_ZHLABEL.md` §Styles、§Q&A 欄「shipped fail」（英文欄與 `P3_RESULTS.md` 相同）；`P3_RESULTS_ZHLABEL.notes.md` 表 |
| 361 張 | holdout 筆數 | 同上；`HOLDOUT_FINAL.md` 開頭 |
| 退回模板 一般 英文 0.0%／中文 0.0%，專業 0.0%／0.0% | p3 fallback：en general 0.0 [0.0, 0.0]、zh general（p3r1z）0.0 [0.0, 0.0]、en pro 0.0 [0.0, 0.0]、zh pro（p3r1z）0.0 [0.0, 0.0]（p3r1 為 0.8、1.7） | `results/research/explain_vlm_20261012/nl_v5/P3_RESULTS_ZHLABEL.md` §Styles 欄「fallback [CI]」 |
| LLM 追問查核前內容錯誤 0；四題中三題退回 0%，「有沒有美顏？」約 20%（漏了操作名稱） | §Q&A 八格「pre-gate H1–H5 any」皆 0.0；fallback 英文 0.0／0.0／20.8／0.0、中文（p3r1z）0.0／0.0／20.5／0.0；失敗者 75／75 皆為有操作達門檻的美顏判定、回答只寫判定與區域 | `results/research/explain_vlm_20261012/nl_v5/P3_RESULTS_ZHLABEL.md` §Q&A；`P3_RESULTS.notes.md` §What the remaining failures are；`P3_RESULTS_ZHLABEL.notes.md` |
| 設計句（LLM 只寫文字，數字與校準句由程式寫入，每句查核；LLM 文字不得有任何數字） | p3 組合規則與 G10；G8、G9 | `results/research/explain_vlm_20261012/nl_v5/PRE_DECLARED_NL.md` §17；`gate_v3.py`（§16） |
| 代價句：每種風格約 20 種不同句子 | holdout 上 LLM 部分的相異字串數：英文一般 20、專業 18，中文 19、20（最常見一句出現 64–121 次） | `results/research/explain_vlm_20261012/nl_v5/P3_RESULTS.notes.md` §Observations the bars do not show |
| 例句（中文海報） | 網頁範例 2，一般說明，p3r1z：LLM 寫「模型的判定是偽造，也就是「偽造（身分被替換或合成）」。證據集中在嘴巴。」，程式加「（判定分數 1.00）」與校準句；追問「為什麼判定為假？」LLM 回答「模型的判定是偽造，證據集中在嘴巴。」（程式未加內容）。海報上紫字＝`server_code_added` | `docs/capstone/src/record_demo_log.json` 鍵 `server_llm_text`、`server_code_added`、`server_text`、`llmq_llm_text`、`nl_calls`（2026-10-15 以 p3r1z 重錄，見文末 Demo 動畫段；p3r1 那次錄影存為 `src/record_demo_log_run2_p3r1_english_key.json`） |
| 例句（英文海報） | 同一張範例 2，p3en1 | `docs/capstone/src/record_demo_log_en.json` 同名鍵 |
| Qwen2.5-7B | 寫手模型 | `REPORT_DRAFT.md` §3、§5.10 |

## 第 4 區（對照）　一般 VLM 的解釋

| 海報上的數字／引文 | 來源 |
|---|---|
| Qwen2-VL-7B 對改過的圖與原圖都寫「眼睛細緻，邊緣清晰，顏色均勻。」 | `results/research/explain_vlm_20261012/MATCHING_v2.md` §6 第 7 例（`part_forgery:donor:280__f0544__eyes`）；`report/REPORT_DRAFT.md` §6 第 2 例 |
| 177 組中 102 組同一句 | `REPORT_DRAFT.md` §5.2 讀法第 2 點、§6 |
| 我們的模板文字「模型判定為偽造（分數 1.00）。證據集中在眼睛（證據平均 0.98）。…」 | `results/research/explain_vlm_20261012/composed_v2.jsonl`，同 id，`explanation_zh_final`（原文寫「模型判定為 fake」「evidence 平均」）；海報照網頁顯示的樣子寫（`docs/demo_ru/index.html` `showT2` 把類別鍵與「evidence 平均」換成中文） |
| FakeVLM 判定錯 37.7% | `HOLDOUT_FINAL.md` §5 (a)（real+fake，n=281，CI [32.0, 43.4]） |
| “This is a real image. The person exhibits natural skin textures…” | `HOLDOUT_FINAL.md` §5 (c) 最常見段落 |
| BLEU-4 6.8／38.9／44.4；CIDEr-D 0.186／4.196／4.322 | `REPORT_DRAFT.md` §5.4 表（原始：`MATCHING_v4_LORA.md` §8） |
| 盲配對 52.8%（未微調）、51.3%（LoRA） | `HOLDOUT_FINAL.md` §2 列 F；`HOLDOUT_V4_LORA.md`（亦見 `REPORT_DRAFT.md` §5.3、§5.4） |

## 第 5 區　部署

| 海報上的數字 | 來源 |
|---|---|
| 0.18–0.56 s；EfficientNet-B4 0.56 s、RepViT 證據版 0.18 s | `docs/demo_ru/README.md`：Evidence head in the browser 段「wall 563–568 ms per image (median 556)」；`models/ru4e_repvit.onnx` 段「wall median 176 ms (B4 559 ms)」；headless Chrome、WASM 1 執行緒、20 張 |
| 66.97 MB、17.6 M | README §Models、§Page design |
| 18.11 MB、4.72 M | README `models/ru4e_repvit.onnx` 段 |
| RepViT 快速版 約 19 MB、4.7 M、數十 ms | `docs/demo_ru/index.html` 模型選項文字「約 19 MB」；README「4.7 M」「tens of ms」 |
| 478 個特徵點 | README 開頭；`index.html`「關於這個系統」 |
| 商用修圖平衡準確率 66.2%（小模型）、72.6%（預設） | README `models/ru4e_repvit.onnx` 段 Validation |
| 解釋句 50／50、整條流程 20／20 | README §Tests（`run_test_headless.py` 50 PASS、`run_test_evidence_headless.py` 20 PASS） |
| 一般說明往返中位數 1.06 s（中文海報）／1.17 s（英文海報） | 設計 p3 的 headless 測試：`docs/demo_ru/test/server_headless_result.json`（中文，p3r1z）與 `server_headless_result_en.json`（英文）鍵 `latency_client.explain_general.median_ms` 1060.9／1167.8（2026-10-15 重跑；中文 p3r1 那次 876.5 存為 `server_headless_result_p3r1.json`；舊值 1.52 s 為 p2，見 README §Server mode） |

## 頁尾

| 海報上的數字 | 來源 |
|---|---|
| FF++ 真臉 100 張有 26 張判為美顏 | `HOLDOUT_FINAL.md` §1，ffpp_real {'filter': 26} |
| 盲配對 52.8% [49.4, 56.2] | `HOLDOUT_FINAL.md` §2 列 F |
| 並非每個事前門檻都通過：「有沒有美顏？」退回 20.5%（中文）、20.8%（英文），門檻 10%；中文提示詞看過結果後改過一次（類別改中文標籤）並重跑一次 | `results/research/explain_vlm_20261012/nl_v5/P3_RESULTS_ZHLABEL.md` §Bars（英文 11／12、中文 p3r1z 11／12）；§Q&A fallback 20.5 [13.2, 30.5]、20.8 [13.3, 30.8]；改動 `PRE_DECLARED_NL.md` §17.8（p3r1 時為 18.3% 與專業查核前 3.6%、中文 10／12，`P3_RESULTS.md`；更舊版此列為 p2 的「五題合併 32.4%」，`QA_ROUTE_RESULTS.md` §2） |
| 網頁模型與主模型判定一致 43／50 | `REPORT_DRAFT.md` §7 第 13 項（`demo_export/export_report.json`） |
| holdout 361 張、事前固定 | `REPORT_DRAFT.md` §4.4 |
| 人工評分尚未進行 | `REPORT_DRAFT.md` §5.9 |

## 流程圖（pipeline.svg／pipeline.png）

圖中的數字與名詞：MediaPipe 478 個特徵點（README）、16×16 證據圖（`REPORT_DRAFT.md` §1、§3）、眼／鼻／嘴／皮膚／輪廓五部位與 rule B（§3）、Qwen2.5-7B 一般／專業與追問（§3「三層解釋」）、還原測試位置（§5.5）、幻覺查核位置（§4.3、§5.10）。2026-10-15 改為最終設計（p3 ＋ 把關 v3 ＋ G10）：「LLM 寫文字（不寫數字）」→「程式加上數字」（判定分數；專業版另加證據平均與操作分數；校準說明句，`nl_v5/nl_p3.py` `compose`，`PRE_DECLARED_NL.md` §17.2）→「自動查核」：六項 H1–H6、分數對門檻（G7）、事實完整、不得宣稱確定（G8）、分數不得掛在部位上（G9）、LLM 的文字不得有數字（G10）（`gate_v3.py`、`nl_p3.llm_gate`，§16、§17.4）→ 不通過重寫一次（sampling，重新加數字與查核）→ 程式模板。

## Demo 動畫（demo.gif）

字幕不含統計數字。畫面上的分數與 LLM 文字是錄影當下網頁與 `nl_v5/nl_server.py` 的實際輸出，記錄在 `docs/capstone/src/record_demo_log.json`。2026-10-15 以設計 p3 重錄（一般說明，追問「為什麼判定為假？」，範例 2），同日因 LLM 回答出現英文類別鍵「fake」，改用 p3r1z 後再重錄一次，細節見文末 "Demo animation" 段。

## English poster (poster_en.html / poster_en.pdf)

Same panels, numbers and sources as the Chinese poster above; the `<!-- src: ... -->` comments are carried over unchanged. Two differences (2026-10-15, design p3): the quoted example is the English recording (`src/record_demo_log_en.json`), and the server-mode round trip is the English one, 1.17 s (`server_headless_result_en.json`), where the Chinese poster gives 1.06 s. The "Ours (code template)" quote shows the Chinese template as the page displays it (class label and 證據平均 in Chinese). Panel numbers are 1–5 in both versions (1 problem, 2 detector, 3 explanation, 4 comparison with a general VLM, 5 deployment). Figures: `pipeline_en.svg` (`src/make_pipeline.py --en`) and `img/retouch_paired_en.svg` (`src/make_retouch_chart.py --en`), same data as the Chinese figures. English renderings of the Chinese quotes are our translations.

## Report (REPORT.md / REPORT.pdf)

Paths relative to `C:\My_Project\AIGC`. "PD" = `results/research/explain_vlm_20261012/PRE_DECLARED.md`; "EV" = `results/research/explain_vlm_20261012/`; "NL" = `results/research/explain_vlm_20261012/nl_v5/`; "T/" = `docs/paper_v2/tables/`.

### Cover (摘要) and Abstract

| Number | Source |
|---|---|
| 17 detectors, 15 of them at 89–99% of pairs, 2,210 faces | `T/tab_v4_retouch.tex` column "above own original"; `docs/paper_v2/main_v4.tex` §Results "Commercial retouching" |
| thirteen accuse 36–69% at the 5%-FPR threshold | `main_v4.tex` §Results (36.3–68.7%); `T/tab_v4_retouch.tex` column "above 5%-FPR thr." |
| on par / behind on DF40 reenactment | `T/tab_v4_df40.tex` paired-difference rows; `main_v4.tex` §Untreated forgery detection |
| 54% to 2–6% | `T/tab_v4_tradeoff.tex` column "above thr.": P0 54.2; P2 smoothing only 2.3 / 5.3; P2 symmetric smoothing 5.9 / 6.1 |
| 94.0% vs Grad-CAM 50.9% | `T/tab_cgd_explain_all.tex` rows "Ours" (donor flip 94.0) and "no head, Grad-CAM" (donor flip 50.9) |
| 361 holdout images, 0 shipped failures | `NL/QA_ROUTE_RESULTS.md` §1 (改動後出貨失敗 0 / 0); `EV/HOLDOUT_FINAL.md` |

### Section 3 System

| Number | Source |
|---|---|
| 478 landmarks, 35% margin | `docs/demo_ru/README.md` first paragraph |
| rank-16 LoRA, two heads, product of Bernoullis, operation threshold 0.5 | `main_v4.tex` §Model; `EV/report/REPORT_DRAFT.md` §4.2 (T2 threshold 0.5) |
| 61,510 part-level forgeries, two training services, Alibaba test only | `main_v4.tex` §Supervision from paired edits |
| 16×16 map, rule B, whole face when eyes, nose, mouth ≥ 0.5 | `EV/report/REPORT_DRAFT.md` §3; `docs/demo_ru/README.md` §Evidence head in the browser, step 3 |
| H1–H6, G7, fact check, G8, G9, one sampled regeneration, four fixed questions | `NL/PRE_DECLARED_NL.md` §4, §13, §14, §16; `NL/nl_server.py` docstring; `NL/gate_v3.py` |

### Section 4 (Table 1, Figure 2)

| Number | Source |
|---|---|
| Table 1 all rows | `T/tab_v4_retouch.tex` (Smoothing-90 columns: above own original, median P(fake), above 5%-FPR thr.); identical values in `T/tab_v4_retouch_main.tex` |
| SBI 0.208→0.991, GenD 0.228→0.921, LAA-Net 0.234→0.969 | same table |
| LAA-Net threshold 0.992 | `main_v4.tex` §Results, "LAA-Net's threshold is 0.992" |
| whitening / slimming / eye enlarging 3.7–8.1% for 13 of 16 | `main_v4.tex` §Results; `T/tab_v4_perop.tex` |
| Celeb-DF-B: Effort 0.909→0.807, Forensics Adapter 0.909→0.828 | `T/tab_v4_twosided.tex` columns AUC, AUC_b |
| Figure 2 | `img/retouch_paired_en.png`, `src/make_retouch_chart.py --en` (values from `T/tab_v4_retouch.tex`) |

### Section 5

| Number | Source |
|---|---|
| FF++ recall 82.7 / 90.9 / 86.7 | `results/research/retouch_unified_20260929/RESULTS_clipe5_s20260929.md`, key `indomain` |
| Table 2 Celeb-DF-v2 and DFD rows, paired intervals | as for poster panel 2 above (`main_v4.tex` §Untreated forgery detection; `T/tab_reproduce.tex` "DFB crop"; `T/tab_v4_twosided.tex`) |
| Table 2 DF40 rows and differences | `T/tab_v4_df40.tex` rows Effort, Forensics Adapter, "Ours, three-way, full data", "paired difference" block; nine face-swap and twelve reenactment methods from `main_v4.tex` Table caption |
| Table 3 all values | `T/tab_v4_tradeoff.tex` columns "above thr.", "above own orig.", "miss rise, strong bil.", "untreated video AUC Celeb-DF-v2", "DF40 reenactment AUC FF++ dom." |
| main model 34.9 / 79.8 / 90.1%; symmetric variant 1.0 / 1.6 / 1.7% | `T/tab_v4_evasion.tex` columns "false alarms, smoothed genuine" bil. light / mid / strong |
| variant Celeb-DF-v2 0.954, DFD 0.983, flip down 1.4–1.6 vs limit 1.0 | `main_v4.tex` §Skin smoothing, "Another tuning scheme, and the main model" |
| Effort scheme 56.9 → 14.5%, 88.4% | `T/tab_v4_tradeoff.tex` rows "Effort scheme" |
| GenD 0.935, DFD-HR 0.932 reenactment; 98.5 / 99.0% | `T/tab_v4_df40.tex`; `T/tab_v4_retouch.tex` |

### Section 6

| Number | Source |
|---|---|
| Table 4 | `T/tab_cgd_explain_all.tex` rows centre prior, Grad-CAM, Grad-CAM++, Score-CAM, Ours |
| text flip 85.4, map 87.8, random 13.9, n = 82, difference −2.4 [−5.6, 0.0] | `EV/HOLDOUT_FINAL.md` §3 row "fake all" |
| holdout composition 100 / 40 / 72 / 99 / 50; 429-image development set | `EV/report/REPORT_DRAFT.md` §4.4 (PD §4, §7) |
| T2 zero failures on 361 | `EV/HOLDOUT_FINAL.md` §1 |
| Table 5 before-check columns | `NL/NL_RESULTS.md` §1 rows Qwen2.5-7B 一般 / 專業 |
| Table 5 fallback 5.8 [2.0, 9.7], 1.1 [0.2, 2.4], shipped failures 0 | `NL/QA_ROUTE_RESULTS.md` §1 |
| 3% bar not met; 1.5B and 0.5B failed all bars | `NL/NL_RESULTS.md` §8 summary table and §1 |
| Table 6 and combined 32.4 [28.4, 37.3] | `NL/QA_ROUTE_RESULTS.md` §2 |
| "What does the score mean?" moved to a fixed answer | `NL/PRE_DECLARED_NL.md` §14 |
| Table 5 English rows, facts preserved English 98.9 / 98.3 | `NL/NL_RESULTS_EN.md` §Styles rows general en / expert en (columns pre-gate H1–H6 any, H1–H6, fallback, shipped fail, facts preserved) |
| Table 6 English columns; combined 0.8 [0.3, 1.4], 11.5 [7.2, 16.8], Chinese same four 16.8 [12.0, 22.8] | `NL/NL_RESULTS_EN.md` §Q&A (columns H1–H5 any, fallback) and "Four questions combined" line; bars from §Bars (4b) |
| English line paragraph: three dev failures, p2en1 changes, expert sentence merging, bars | `NL/PROMPT_LOG_NL.md` entry 2026-10-15 「英文線 p2en → p2en1」; `NL/NL_RESULTS_EN.notes.md` "What happened"; `NL/PRE_DECLARED_NL.md` §15 |
| Table 5 column "Fallback with G8, G9" (6.6 [2.6, 10.6], 19.4 [12.4, 26.0], 55.4 [46.2, 64.9], 74.5 [64.4, 82.4]) | `NL/GATE_V3_RESULTS.md` table, rows zh general / zh pro / en general / en pro, column "fallback after (gate v3)"; `NL/out/gate_v3_rerun_holdout.json` |
| G8/G9 paragraph: 390 English and 206 Chinese blocked texts; 197 / 179 / 15 (12 restating); 56 / 80 / 30 / 40 false blocks; all before→after fallback rates | `NL/GATE_V3_RESULTS.md` (column "shipped texts blocked", fallback before/after) and `NL/GATE_V3_RESULTS.notes.md` §Hand check (categories counted by hand-read of every blocked text); definitions `NL/PRE_DECLARED_NL.md` §16 |
| Design p3 paragraph and Table 5b (all p3 cells: pre-gate H1–H6 any of the composed text, fallback, facts preserved, H1–H5 of the questions, per-question fallback 0.0 / 0.0 / 20.8 / 0.0 and 0.0 / 0.0 / 18.3 / 0.0; bars 11 / 12 and 10 / 12) — p3en1 and p3r1 | `NL/P3_RESULTS.md` §Styles, §Q&A, §Bars (`NL/P3_RESULTS.json` keys `p3`, `bars`); prompts, composition rule, G10 and bars pre-declared in `NL/PRE_DECLARED_NL.md` §17; outputs `NL/out/holdout_p3en1_7b.jsonl`, `NL/out/holdout_p3r1_7b.jsonl` |
| Table 5b p3r1z rows and the "Chinese class labels (p3r1z)" paragraph: 0.0 / 0.0 / 100.0 (plain and expert), questions 0.0 / 0.0 / 20.5 / 0.0, 11 of 12 bars; English keys in p3r1 shipped texts 272 expert, 3 plain, 266 / 266 / 332 / 266 per question, 0 in p3r1z; 19 and 18 distinct strings | `NL/P3_RESULTS_ZHLABEL.md` §Styles, §Q&A, §Bars; `NL/P3_RESULTS_ZHLABEL.notes.md` (English-key counts and distinct strings counted from `NL/out/holdout_p3r1_7b.jsonl` and `NL/out/holdout_p3r1z_7b.jsonl`); change and rerun declared in `NL/PRE_DECLARED_NL.md` §17.8 and `NL/PROMPT_LOG_NL.md` (last entries) |
| Table 5b columns "Earlier prompt under G8, G9" (before check any rule 55.7 / 77.8 / 10.8 / 22.2; fallback 55.4 / 74.5 / 6.6 / 19.4; questions 37.4 / 0.0 / 13.9 / 48.2 and 40.4 / 24.1 / 5.0 / 35.7) | `NL/P3_RESULTS.md` columns "p2 line: pre v3 any" and "p2 line: fallback under v3 (upper bound)" (the latter = `NL/GATE_V3_RESULTS.md` "fallback after (gate v3)") |
| model's own words missing a fact 0.3% (English plain), 0% elsewhere | `NL/P3_RESULTS.md` §Styles column "LLM part: G10 / G8 / G9 / facts missing" |
| development results, the revision (two Q&A items removed, "always state the decision … region" added), "Was it retouched?" 0 → 15–18% on development | `NL/PROMPT_LOG_NL.md` entries 2026-10-15（晚）「設計 p3」, 「p3en → p3en1、p3 → p3r1」 and their result tables |
| 75 of 75 failures are beautified decisions with an operation above the threshold; ten H3 texts 「…包括磨皮和美白」, three H6; twelve Chinese plain G7; about 20 distinct LLM strings per style, most frequent 64–121 times | `NL/P3_RESULTS.notes.md` §What the remaining failures are, §Observations the bars do not show (counted from the holdout outputs) |
| Example texts, English page (design p3: LLM explanation with code-added "(decision score 1.00)" and calibration sentence; "Is this certain?"; LLM answer to "Why is it judged fake?") | `docs/capstone/src/record_demo_log_en.json` keys `server_text`, `server_llm_text`, `server_code_added`, `server_prompt` (p3en1), `fixed_answer`, `llm_answer`, `llmq_llm_text`, `nl_calls[*].res.attempts` (recorded 2026-10-15 with design p3); earlier recordings `src/record_demo_log_en_run1_rejected.json` (score-on-mouth answer), `src/record_demo_log_en_run2_gate_v2.json` (certainty clause) and `src/record_demo_log_en_run3_gate_v3_p2en1.json` (p2en1 under gate v3, both texts template) |
| Example texts, Chinese page (explanation, 為什麼判定為假？, 可以確定嗎？), design p3 with p3r1z | `docs/capstone/src/record_demo_log.json` keys `server_text`, `server_llm_text`, `server_code_added`, `server_prompt` (p3r1z), `llm_answer`, `llmq_llm_text`, `fixed_answer`, `nl_calls[*].res.attempts`; earlier recordings quoted in the same paragraph: `src/record_demo_log_run1_gate_v2_p2_rejected.json` key `llm_answer` (p2, score after the region) and `src/record_demo_log_run2_p3r1_english_key.json` key `llmq_llm_text` (p3r1, 「模型的判定是 fake…」) |
| Figure 3 | `img/screen_mobile_example2_en_crop.png` = `docs/demo_ru/test/screens/412_example2.png` (English page) cropped to the top 412×400 px, the same box as the earlier Chinese crop `img/screen_mobile_example2_crop.png` |

### Section 7

| Number | Source |
|---|---|
| positive control 95.3–99.3% | `EV/report/REPORT_DRAFT.md` §5.2 table, JC column (MATCHING_v3 §1, MATCHING_v3_32B §1) |
| Table 7 development rows (A, E, G, I) | `EV/MATCHING_v2.md` §1 (row A), `EV/MATCHING_v3.md` §1 (row E), `EV/MATCHING_v3_32B.md` §1 (row G), `EV/MATCHING_v4_LORA.md` §1 (row I) |
| Table 7 holdout rows | `EV/HOLDOUT_FINAL.md` §2 row F (52.8, 36.4%); `EV/HOLDOUT_V4_LORA.md` row F (51.3, 74.5%) |
| FakeVLM 50.8 [48.3, 53.2], 37.3%, 37.7% [32.0, 43.4], quoted paragraph | `EV/HOLDOUT_FINAL.md` §5 |
| 102 of 177, quoted sentence | `EV/MATCHING_v2.md` §5, §6 |
| Table 8 | `EV/MATCHING_v4_LORA.md` §8 (1,150 samples) |
| VLM latency 0.74–1.08 s, GPU 1.17 → 17.82 GB | `EV/HOLDOUT_FINAL.md` §4 |

### Section 8

| Number | Source |
|---|---|
| Table 9 sizes, parameters, inputs, wall times, balanced accuracy 72.6 / 66.2 | `docs/demo_ru/README.md` §Models and §Evidence head in the browser (wall median 556 ms; RepViT wall median 176 ms); fast RepViT "約 19 MB" from `docs/demo_ru/index.html` |
| 50 / 50, 20 / 20, 7.4×10⁻⁶, 43 / 50 | `docs/demo_ru/README.md` §Tests and §Models (`demo_export/export_report.json`) |
| main model 37–50 ms on GPU | `EV/HOLDOUT_FINAL.md` §4 (0.037 s) and `EV/bench_latency.log` (0.0496 s) |
| about 16 GB | `docs/demo_ru/README.md` §Server mode |
| 10 records, 100 texts per language, 0 re-check failures (gate v3 + LLM-part gate with G10 + composition check, 59 model texts per language); code answers 1 of 60 per language ("Was it retouched?", Alibaba eye-enlargement record); medians 1.17 / 1.06 s plain, 1.08 / 1.12 s expert, 0.64 / 0.52 s questions, 2–3 ms fixed; regenerations 1 / 1; Chinese texts with an English class key 0 | `docs/demo_ru/test/server_headless_result_en.json` and `server_headless_result.json` (re-run 2026-10-15 with design p3; Chinese re-run again with p3r1z, key `zh_texts_with_english_key`; the p3r1 Chinese run is kept as `server_headless_result_p3r1.json`, 43 of its 100 texts showed an English key or "evidence"): keys `texts_failing_recheck`, `sources`, `prompts`, `llm_texts_rechecked_p3`, `regenerated`, `latency_client`; per-row `source`, `mode`, `p3_llm_part_and_composition_pass` |
| earlier prompts under the same check: 19 (en) and 11 (zh) of 60 replaced | previous run of the same test (gate v3, prompts p2en1 / p2, 2026-10-15), as listed in the previous version of this row (`sources` 19 / 11 template or code of 60); that run's result files were overwritten by the p3 run and were not kept, so this number can no longer be re-read from a file |

### Section 9

| Number | Source |
|---|---|
| 26 of 100 | `EV/HOLDOUT_FINAL.md` §1 |
| 73.5% vs 75% | `main_v4.tex` §Results, commercial retouching paragraph |
| 90.1% | `T/tab_v4_evasion.tex` |
| 40-pair human check prepared, not run | `EV/human_check/README.md` |
| 37 ms and 49.6 ms under load | `EV/HOLDOUT_FINAL.md` §4; `EV/bench_latency.log` |
| G8 false block 「無法確定是哪一種修圖」; English plain fallback 0.8% → at most 55.4% | `NL/GATE_V3_RESULTS.notes.md` §Hand check (40 Chinese false blocks); `NL/GATE_V3_RESULTS.md` row en general |
| H3 rejects 「…均未達門檻，包括磨皮和美白」; p3 brings English plain fallback to 0.0%, misses one bar (en) and two (zh, p3r1); the Chinese label change and rerun (p3r1z, misses one bar: `NL/P3_RESULTS_ZHLABEL.md` §Bars, `NL/PRE_DECLARED_NL.md` §17.8); about 20 distinct strings; class gloss copied for a mouth-only forgery | `NL/P3_RESULTS.notes.md`; `NL/P3_RESULTS.md` §Bars; `src/record_demo_log_en.json` key `server_llm_text` |
| example of uncaught filler "indicating that the mean evidence is consistent across the entire region" | `NL/NL_RESULTS_EN.notes.md` §Gaps the gate does not see |

## Demo animation (demo.gif), re-recorded 2026-10-15 with design p3 (Chinese prompt p3r1z)

`python docs/capstone/src/record_demo.py --lang zh --llm-q 0` with `nl_v5/nl_server.py` (gate v3, default prompt design p3; Chinese prompt `p3r1z`, `PRE_DECLARED_NL.md` §17 and §17.8) started for the recording and stopped afterwards (only that process). Page opened with `?lang=zh`, Chinese captions, server mode General style (一般說明). Steps: load, example 3, example 2, Settings, server mode on example 2, fixed question 「可以確定嗎？」, then 「為什麼判定為假？」. Log: `src/record_demo_log.json` (with `nl_calls`: the facts record sent and the full server reply, including `llm_text`, `code_added`, `attempts`). Captions chosen by `record_demo.py` from the reply: step 5 「5. 伺服器模式（範例 2）：LLM 寫文字，分數與校準句由程式加上，通過查核」 (reply `source` llm with `code_added`), step 7 「7. 追問「為什麼判定為假？」：LLM 回答，通過查核」 (reply `source` llm, nothing added).

Recorded texts, checked by hand against example 2's record (decision fake; probabilities real 0 / fake 1 / filter 0; named part mouth; mean evidence mouth 0.98; operations 0.36 / 0.24 / 0.17 / 0.15, all below 0.5; calibration note):

- Explanation (LLM, greedy, passed the LLM-part gate and gate v3 at the first attempt). LLM text: 「模型的判定是偽造，也就是「偽造（身分被替換或合成）」。證據集中在嘴巴。」 Code added 「（判定分數 1.00）」 and 「分數是模型的原始輸出，不是校準過的機率，分數高也不代表判定正確。」. Shown: 「模型的判定是偽造，也就是「偽造（身分被替換或合成）」（判定分數 1.00）。證據集中在嘴巴。分數是模型的原始輸出，不是校準過的機率，分數高也不代表判定正確。」 Badge: 「LLM 撰寫文字，數字與分數說明由程式加上，已通過檢查」. Decision, score and region are in the record; 「身分被替換或合成」 is the class definition copied from the fact list (only the mouth was replaced in this image); the calibration sentence is code-written.
- 「可以確定嗎？」 (fixed): 「無法確定。分數是模型的原始輸出，不是校準過的機率，判定也可能出錯。」
- 「為什麼判定為假？」 (LLM, greedy, passed at the first attempt, nothing added by code): 「模型的判定是偽造，證據集中在嘴巴。」 Both claims are in the record.

Earlier Chinese recordings, kept: `src/record_demo_log_run1_gate_v2_p2_rejected.json` (prompt p2 under gate v2; explanation 「模型判定為偽造，分數是 1.00。證據集中在嘴巴部位。判定分數是模型的原始輸出，不是校準過的機率。」, answer 「模型的判定是偽造。證據集中在嘴巴，分數為 1.00。」, which places the score after the region and would fail G9b) and `src/record_demo_log_run2_p3r1_english_key.json` (design p3 with p3r1; explanation 「判定是偽造（判定分數 1.00）。證據集中在嘴巴。…」, answer 「模型的判定是 fake，證據集中在嘴巴。」 with the English class key copied from the fact list, which led to p3r1z). The first frame of the animation shows the page's English start screen for a moment before it switches to Chinese (page loads, then applies `?lang=zh`).

## English demo animation (demo_en.gif), re-recorded 2026-10-15 with design p3

`python docs/capstone/src/record_demo.py --lang en --llm-q 0` with `nl_v5/nl_server.py` (gate v3, default prompt design p3 = `p3en1`, `PRE_DECLARED_NL.md` §17) started for the recording and stopped afterwards. The page is opened with `?lang=en`; captions are English; server mode uses the General style. Steps: load, example 3, example 2, Settings (three models), server mode on example 2, fixed question "Is this certain?", then "Why is it judged fake?". Log: `src/record_demo_log_en.json` (includes `nl_calls`: every request with its facts record and the server reply, including `llm_text`, `code_added` and the attempts). `record_demo.py` captions steps 5 and 7 from the server's reply: template → "…did not pass the checks; template shown"; LLM text with code additions (`code_added`) → "5. Server mode (General): LLM writes the words; code adds the score and calibration sentence"; LLM answer → "7. "Why is it judged fake?": LLM answer, no numbers; passed the checks". This recording used the last two.

Recorded texts, checked by hand against example 2's record (decision fake, probabilities real 0 / fake 1 / filter 0, named part mouth, mean evidence 0.98, operations all below 0.5, calibration note):

- Explanation (LLM, greedy, passed the LLM-part gate and gate v3 at the first attempt). LLM text: "The model's decision is fake, that is, the "fake (identity replaced or synthesized)" class. The evidence is concentrated on the mouth." Code added "(decision score 1.00)" and "The score is the model's raw output, not a calibrated probability, and a high score does not mean the decision is correct." Shown: "The model's decision is fake, that is, the "fake (identity replaced or synthesized)" class (decision score 1.00). The evidence is concentrated on the mouth. The score is the model's raw output, not a calibrated probability, and a high score does not mean the decision is correct." Badge: "LLM wording, numbers and score note by code; passed the checks". Decision, score 1.00 and region mouth are in the record; the calibration sentence is code-written. The class gloss "identity replaced or synthesized" is the class definition copied from the fact list; example 2 is a part-level forgery (only the mouth replaced), so it describes the class, not this image.
- "Is this certain?" (fixed): "No. The score is the model's raw output, not a calibrated probability, and the decision can be wrong."
- "Why is it judged fake?" (LLM, greedy, passed at the first attempt, nothing added by code): "The model's decision is that the photo is fake, with the evidence concentrated on the mouth." Both claims are in the record.

Earlier recordings, kept: `src/record_demo_log_en_run1_rejected.json` (first recording; its "Why is it judged fake?" answer attached the score to the mouth and passed gate v2), `src/record_demo_log_en_run2_gate_v2.json` (second recording under gate v2, step 7 = "What does this score mean?"; its explanation carried the negated certainty clause) and `src/record_demo_log_en_run3_gate_v3_p2en1.json` (third recording, prompt p2en1 under gate v3: explanation failed G8 twice and the answer failed G9a twice, so both showed the template / code answer). The Chinese `demo.gif` was re-recorded with design p3 the same evening (section above).

## English poster and report screenshots (2026-10-15)

`img/screen_mobile_example2_en_crop.png` (from `docs/demo_ru/test/screens/412_example2.png`, box (0, 0, 412, 400)) and `img/screen_desktop_example3_en_crop.png` (from `docs/demo_ru/test/screens/1366_example3.png`, box (180, 505, 1190, 900)); the boxes are the ones of the earlier Chinese crops, found by matching those crops against their full screenshots. `poster_en.html` now uses both English crops, the caption "the page is in Chinese" was removed, and the intro sentence says the LLM writes "the sentences (English or Chinese)". `poster.html` (Chinese) keeps the Chinese crops.

## English poster update (2026-10-16, after `REVIEW_20261016.md`)

`poster_en.html` / `poster_en.pdf` (re-printed with headless Chrome, one page, 594 × 841 mm). Changes and sources:
panel 1 text: 32.5% explained as "below 50% = render scored lower than its original" plus the main model's own decisions
on Smoothing-90 renders (beautified 98.8%, fake 0.8%; `RU/RESULTS_clipe5_s20260929.md` Smoothing_90 row) and the binary
control's 9.1% vs 8.6% (`T/tab_v4_retouch.tex`); the bar chart no longer bolds our value (`src/make_retouch_chart.py`).
Panel 2 table: bold removed; GenD and DFD-HR columns (Celeb-DF-v2 video / frame and DFD frame from `T/tab_reproduce.tex`
"DFB crop": 0.960 / 0.900 / 0.932 and 0.951 / 0.886 / 0.942); new row DF40 reenactment FF++ domain 0.718 / 0.808 / 0.828 /
0.935 / 0.932 (`T/tab_v4_df40.tex`); note text from `results/research/ffpp_benchmark_20260925/DFB_CROP_EVAL.md` paired
intervals and `T/tab_v4_df40.tex` (GenD / DFD-HR face-swap differences, binary control 0.842). Panel 3: "part-level"
and "Grad-CAM on a separate model" (`results/research/cgd_20260927/train_cgd.py`, HYBPE = EfficientNet-B4 without head).
Panel 5: fast RepViT file 18.14 MB (size of `docs/demo_ru/models/ru_repvit.onnx`), latency "not measured".
Limitations: DF40 reenactment 0.502 (`T/tab_v4_df40.tex`); 90.1% / 1.7% / +28–34 (`T/tab_v4_evasion.tex`); 26 and 10 of
100 (`EV/HOLDOUT_FINAL.md` §1); "Was it retouched?" 20.8 / 20.5 (as before). Footer: holdout read five times (see
`paper/SOURCES_PAPER.md`); web/main agreement 43/50 decisions and 38/50 parts (`docs/demo_ru/README.md`).

The capstone report is now also written as a paper: `paper/capstone.pdf`, numbers in `paper/SOURCES_PAPER.md`.
