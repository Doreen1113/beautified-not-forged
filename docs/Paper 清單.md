# Paper 清單

---

## ⚠️ 2026-08-27 全清單引用稽核結果（Chunk C + 補完輪，本清單全部條目已查證完畢）

> **查證方法**：清單內 **68 個 arXiv ID 全部**以 arXiv 官方 API 逐一取回標題／作者／期刊欄位，
> 與本清單所寫標題逐字比對（**ID 指向另一篇論文＝捏造/誤植的指紋**，本輪之前已出現兩次）；
> 非 arXiv 條目（IEEE / ACM / Springer / Elsevier / CVF / ICLR / IJCAI）以 dblp API 與出版社頁面查證
> 標題、作者、卷期、頁碼與**會議 vs workshop**。
>
> **總計**：查證 68 個 arXiv ID + 約 24 個非 arXiv 出處。
> **捏造引用 2 件**（皆為稍早輪次發現、已於本檔標示待刪除）：`Deceptive Beauty: The Risks of
> AI-Enhanced Appearance`（arXiv 2409.00375 實為心臟 MRI 論文）、`DeFakeQ: Deepfake Detection
> via Quantization`（arXiv 2412.01799 實為機器人中介軟體論文 HPRM）。
> **本輪新增 1 件 arXiv ID 指錯論文**：HEIE 標的 **2412.10667 實為量子模擬演算法論文**（正確 ID 2411.17261）——
> 這是**第三個 ID 對不上**的案例，但與前兩件不同，HEIE 論文本身真實存在，屬**誤植 ID + 標題漏字**而非捏造。
> **會議/期刊出處錯誤 4 件**：MoE-FFD（TIFS→**TDSC**）、AntifakePrompt（主會議→**ICLR 2025 Workshop**）、
> Information Fusion 綜述（2025→**vol.132, 2026**）、Fake or JPEG（年份含糊→**ECCV 2024 Workshops, pp.80-95**）。
> **領域錯誤 1 件**：GRIDEX 為**音訊／頻譜圖**鑑識（已標示）。
> **作者群錯誤 2 件**：Rathgeb IEEE Access 2020（誤植成另一篇 CVPRW 2020 的作者群）、
> Ibsen WIFS 2021（漏列第二作者 González-Soler）。
> **標題誤植／截斷 9 件**（見下方彙整）。
>
> **標題誤植／截斷彙整（ID 與論文皆正確，僅本清單標題需修正，投稿參考文獻務必用左欄正式標題）**
>
> | 正式標題（arXiv 官方） | 本清單原寫法 |
> |---|---|
> | Spot the Fake: Large Multimodal Model-Based Synthetic Image Detection with Artifact Explanation (2503.14905) | 「FakeVLM: Towards a Multimodal Deepfake Detection Model」（FakeVLM 是模型名） |
> | A Sanity Check for AI-generated Image Detection (2406.19435) | 「Chameleon / AIDE」（資料集/方法名） |
> | An Explainable FFT-Based Spatial-Frequency Fusion Framework for Deepfake Detection (2607.17441) | 「MSCA-FFT: Explainable FFT-Based Spatial-Frequency Fusion」 |
> | HEIE: ... AIGC Image **Implausibility Evaluator** (2411.17261) | 「... AIGC Image Evaluation」 |
> | **Knowing What You Cannot Explain:** Learning to Reject Low-Quality Explanations (2507.12900) | 缺主標題 |
> | Circumventing shortcuts in audio-visual deepfake detection datasets **with unsupervised learning** (2412.00175) | 標題截斷；且**未標出處＝CVPR 2025 highlight** |
> | Navigating Shortcuts, Spurious Correlations, and Confounders: **From Origins via Detection to Mitigation** (2412.05152) | 標題截斷 |
> | A Gentle Introduction to Conformal Prediction **and Distribution-Free Uncertainty Quantification** (2107.07511) | 標題截斷 |
> | **FRRffusion:** Unveiling Authenticity with Diffusion-Based Face Retouching Reversal (2405.07582) | 缺方法名前綴 |
> | RISE: Randomized Input Sampling for Explanation **of Black-box Models** (1806.07421) | 標題截斷 |
> | SIDA: ... Explanation with **Large Multimodal Model** (CVPR 2025) | 縮寫成 "LMM" |
> | Improving the Perturbation-Based Explanation of Deepfake Detectors Through the Use of Adversarially-Generated Samples (2502.03957) | 僅寫「WACVW 2025 續作」，正式出處為 **AI4MFDD Workshop @ WACV 2025** |
> | Assessing the **(Un)Trustworthiness** of Saliency Maps ...（preprint arXiv:2008.02766） | RSNA 正式版標題無 "(Un)"，兩版標題不同，引用時擇一勿混用 |
>
> **另補正的出處欄位**：`Open Set Face Forgery Detection via Dual-Level Evidence Collection`（2512.04331）
> **已被 IEEE FG 2026 接受**；`M²F²-Det`（CVPR 2025 **Oral** 已確認）preprint 為 **arXiv:2503.20188**；
> `Tsigos et al. MAD'24` 的作者序為 Tsigos, Apostolidis, **Baxevanakis**, ..., Mezaris（本清單原寫法漏列）。
>
> **查證為完全正確、無須更動的重點條目**（避免日後重複查）：ShuffleNetV2 (1807.11164)、RetouchingFFHQ (2307.10642)、
> Grad-CAM++ (1710.11063, WACV 2018)、F³-Net/Thinking in Frequency (2007.09355, ECCV 2020 poster)、DF40 (2406.13495)、
> FakeShield (**ICLR 2025** 已由 dblp/openreview 確認)、ForgeryNet (**CVPR 2021 Oral** 已由 arXiv comment 確認)、
> DFFD (1910.01717, CVPR 2020)、FALdetector (1906.05856, ICCV 2019)、TFMD (**Computers & Security 2023**, Cao/Chen/Ye)、
> MoFRR (**ICCV 2025** 已由 CVF 確認)、X²-DFD (**NeurIPS 2025 主會議**已由 proceedings.neurips.cc 確認)、
> ED⁴ (**IEEE TIP 2025** 已由 IEEE Xplore 確認)、QMDD (**IJCAI 2025** proceedings/2025/0059 可直接開啟)、
> LOKI (**ICLR 2025 Spotlight** 已確認)、SIDA (CVPR 2025)、Libourel et al. (**IWBF 2024**，EURECOM/IEEE Xplore 皆可查)、
> Concas et al. Deceptive Beauty (2509.14120, MetroXRAINE 2025，arXiv comment 明載)、
> DeFakeQ 真本 (2604.08847)、ExDDV (**WACV 2026**，arXiv comment 明載)、Ivy-Fake (**ICMR 2026**)、
> 「Is It Certainly a Deepfake?」(**ICCV 2025 Workshop STREAM**)、Ferrara et al. (1901.08811, IET Biometrics)、
> Raja et al. (2006.06458, **TIFS**, DOI 10.1109/TIFS.2020.3035252)、
> Rathgeb/Dantcheva/Busch 美顏綜述 (**IEEE Access 7:152667-152678, 2019**)、
> Guo et al. HiFi-IFDL (**CVPR 2023, pp.3155-3165**)、ACM TOMM 2025 sharpening mask (**vol.21, 180:1-180:18**)、
> Bharati et al. (**TIFS 11:1903-1913, 2016**)、MDRF (1709.07598, **IJCB 2017**)、Tomsett (**AAAI 2020, pp.6021-6029**)、
> Hedström (**xAI 2024, pp.403-420**)、Geirhos (**Nature MI 2, 665-673, 2020**)、
> Implicit Identity Leakage/CADDM (**CVPR 2023, pp.3994-4004**)、SelectiveNet (**ICML 2019, pp.2151-2159**)、
> DAD-HCNN（**CVPRW 2020，已逐字讀完全文**，數字見 `results/research/citation_audit_20260827/DADHCNN_NUMBERS.md`）。
>
> **仍待查（不得寫進投稿稿）**：① XPlainVerse / Explainable Deepfake Detection Challenge 的 **ACM MM 2026 出處**仍未證實
> （arXiv 頁面未載，兩篇為同一批作者）；② Rathgeb 差分式修圖偵測的 **D-EER 具體數字**仍為 snippet 來源；
> ③ `docs/paper_draft_zh.md` 反覆引用的 **Bharati et al. IJCB 2017「79.3-97.5% 二元修圖偵測 accuracy」**
> 無法由摘要證實（需查全文表格），這是對照表的承重數字，投稿前必須逐字核對。

---

## 核心使用中

| 論文 | 用途 | 狀態 |
|------|------|------|
| [ShuffleNet V2: Practical Guidelines for Efficient CNN Architecture Design](https://arxiv.org/abs/1807.11164) (ECCV 2018) | 主 backbone，空間分支 | ✅ 使用中 |
| [RetouchingFFHQ: A Large-scale Dataset for Fine-grained Face Retouching Detection](https://arxiv.org/abs/2307.10642) | Filter 訓練資料 + MAM 架構參考 | ✅ 使用中 |
| [Grad-CAM++: Improved Visual Explanations for Deep Convolutional Networks](https://arxiv.org/abs/1710.11063) | 可解釋性熱力圖，target layer: conv5 | ✅ 使用中 |
| [Thinking in Frequency: Face Forgery Detection by Mining Frequency-aware Clues](https://arxiv.org/abs/2007.09355) (ECCV 2020) | FFT branch 設計依據 | ✅ 使用中 |

---

## 參考 / 引用中

| 論文 | 用途 | 狀態 |
|------|------|------|
| [DF40: Toward Next-Generation Deepfake Detection](https://arxiv.org/abs/2406.13495) (NeurIPS 2024) | Cross-dataset eval protocol；Domain gap 是公認難題的依據 | ✅ 參考中 |
| [FakeShield: Explainable Image Forgery Detection and Localization via Multi-modal LLMs](https://openreview.net/pdf?id=pAQzEY7M03) (ICLR 2025) | 輸出格式設計 + FakeShield mask 概念 | ✅ 參考中 |
| ~~[HEIE: MLLM-Based Hierarchical Explainable AIGC Image Evaluation](https://arxiv.org/abs/2412.10667) (CVPR 2025)~~ → 更正為 [HEIE: MLLM-Based Hierarchical Explainable AIGC Image **Implausibility Evaluator**](https://arxiv.org/abs/2411.17261) — Yang et al., **CVPR 2025** | ⚠️ **2026-08-27 更正：第三個 arXiv ID 對不上的引用。** 原標的 arXiv **2412.10667 實際上是「A simple quantum simulation algorithm with near-optimal precision scaling」（Kalev & Hen，量子模擬演算法，已刊 Quantum Sci. Technol. 10 045052, 2025）**，與 AIGC 偵測完全無關。所幸 HEIE 這篇論文**確實存在**（不同於前兩個捏造案例），正確 arXiv 為 **2411.17261**，且確為 CVPR 2025（openaccess 有 `Yang_HEIE_..._CVPR_2025_paper.pdf`）；另原標題**漏字**，正式標題結尾是 "Image **Implausibility Evaluator**" 而非 "Image Evaluation"。ID 與標題皆已更正。 | ✅ 參考中（ID/標題已更正） |
| ~~[Deceptive Beauty: The Risks of AI-Enhanced Appearance](https://arxiv.org/abs/2409.00375) (2024)~~ | ⛔ **2026-08-27 查證：這個引用是錯的。arXiv 2409.00375 實際上是心臟 MRI 影像品質評估論文（Nabavi et al.），與本主題完全無關；且查無「Deceptive Beauty: The Risks of AI-Enhanced Appearance」這篇論文存在。**正確的 Deceptive Beauty 論文見下方 Concas et al. 2025 條目。**投稿前必須移除或替換此引用**。 | ❌ 錯誤引用，待刪除 |
| [Impact and Detection of Facial Beautification in Face Recognition: An Overview](https://www.researchgate.net/publication/336705492) (IEEE Access 2019) | Filter 分類定義依據（磨皮/美白/大眼/瘦臉） | ✅ 參考中 |
| [Detecting GANs and Retouching Based Digital Alterations via DAD-HCNN](https://openaccess.thecvf.com/content_CVPRW_2020/papers/w39/Jain_Detecting_GANs_and_Retouching_Based_Digital_Alterations_via_DAD-HCNN_CVPRW_2020_paper.pdf) (CVPRW 2020) | ⚠️ **必引 related work，架構高度重疊**：三層 CNN+SVM 級聯（L1 original-vs-altered → L2 retouched-vs-GAN → L3 哪個GAN），概念上與我們的 Layer1→Layer2→artifact_classifier 相同，且早我們6年（前作 On Detecting GANs and Retouching based Synthetic Alterations, BTAS 2018, 同作者）。**差異化論點（2026-08-27 逐字讀完全文比對，見下）**：① 他們 retouching 只用單一工具（PortraitPro）從未測跨演算法泛化，我們的 Alibaba 跨演算法失敗（3-35%）是他們完全沒碰過的開放問題；② 他們無 fake+filter 複合類別，我們的核心安全發現（Fake+Filter→Real）在他們的分類法之外；③ 零邊緣部署/模型大小/延遲討論；④ 他們的「explainability」僅指多一層類別標籤，非自然語言/evidence map；⑤ 99%+ 數字建立在小型封閉單一來源資料集（CelebA-trained GAN + 單一retouching工具），未做內容重疊稽核或跨資料集OOD測試。**可借鑑技巧**：patch-based CNN+SVM（每 patch 各自分類，圖片級=patch預測正規化直方圖）讓分類器原生自帶空間定位地圖，可作為 P2-A1 patch evidence head 的簡化參考設計。論文定位不可寫「我們發明階層式架構」，應寫「檢驗既有階層式分解在跨演算法泛化/複合安全情境/邊緣部署/開放世界資料完整性下的表現」。 | ✅ 必引，novelty framing 已更正 |
| [On Detecting GANs and Retouching based Synthetic Alterations](https://arxiv.org/abs/1901.09237) — Anubhav Jain, Richa Singh, Mayank Vatsa, **IEEE BTAS 2018, pp. 1-7**（⚠️ **2026-08-27 補正**：原本連到 `iab-rubric.org/` 這個**機構首頁而非論文**，無法驗證；已補 dblp 確認的正式出處 BTAS 2018 pp.1-7 與 preprint arXiv:1901.09237） | DAD-HCNN 的前作，同一批作者更早提出 GAN+retouching 二元偵測，是階層式分解想法的更原始出處，related work 應一併引用 | ✅ 必引 |
| [Hierarchical Fine-Grained Image Forgery Detection and Localization](https://openaccess.thecvf.com/content/CVPR2023/papers/Guo_Hierarchical_Fine-Grained_Image_Forgery_Detection_and_Localization_CVPR_2023_paper.pdf) (CVPR 2023) | 局部偽造定位，Grad-CAM 區域標注的相關方法 | ✅ 參考中 |

---

## 2026-08-27 文獻調查新增（Angle 1：Fake+Filter→Real 安全發現的前作）

> ⚠️ **本次調查最重要的結論：「fake 疊 filter 會被判成 real」這個現象已被發表兩次（2024、2025），
> 「首次發現」的宣稱必須撤回。**兩篇都明確把「修復」列為 future work、都沒有做，
> 也都停留在二分類框架（filter 不是獨立類別）。我們剩下可主張的是**修復方法 + 三分類框架 + 系統性型別/強度掃描**。

| 論文 | 用途 / 為何必引 | 狀態 |
|------|------|------|
| [A Case Study on How Beautification Filters Can Fool Deepfake Detectors](https://www.eurecom.fr/publication/7648/download/sec-publi-7648.pdf) — Libourel, Husseini, Mirabet-Herranz, Dugelay, **IWBF 2024** (EURECOM)。資料集：https://celebdfb.eurecom.fr/ | 🔴 **最高優先必引，直接撞我們的 #1 novelty**。建 **Celeb-DF-B**（Celeb-DF 抽 232 real + 232 fake，各套 4 種 Instagram 美顏濾鏡 → 928 影片，四類 Real / Real-Beautified / Fake / Fake-Beautified）。三個 FF++ 訓練的偵測器 video-level AUC 全掉約 0.15（CADDM 0.91→0.76、RECCE 0.81→0.66、FTCN 0.80→0.64）。**RECCE 的 FNR 在美顏後上升、平均分數往 real 位移 −0.07 ⇒ 就是我們的 fake+filter→real**；CADDM/FTCN 反向（+0.1/+0.3）。另有 21 人主觀實驗（accuracy 0.69→0.66，recall 0.70→0.76）。**未提出任何修復**，結語僅寫「future challenges include mitigating…」。→ 我們的定位必須從「首次發現」改為「首次修復 + 首次以三分類框架處理」。此資料集也應設法取得作為外部驗證集。 | 🔴 必引，novelty 需改寫 |
| [Deceptive Beauty: Evaluating the Impact of Beauty Filters on Deepfake and Morphing Attack Detection](https://arxiv.org/abs/2509.14120) — Concas, La Cava, Panzino, Orrù, Masala, Marcialis, **IEEE MetroXRAINE 2025**（Univ. Cagliari） | 🔴 **必引**。用可調半徑（c=3%~5% 臉高）的 smoothing 濾鏡，AlexNet/VGG19 在 Celeb-DF（deepfake）與 AMSL/FRLL（morphing）上做**非對稱拆解**（F-Real vs F-Fake、F-Real vs O-Fake、**O-Real vs F-Fake ← 正是我們的攻擊情境**）。VGG19 APCER（fake 被當 real）**30.1%→48.4%**；O-Real vs F-Fake AUC **75.7→67.1**（AlexNet 反而 84.1→89.3，架構相依）；morphing 情境更慘（VGG19 F-Real vs O-Fake AUC 87.2→0.9%）。Fig.4 直接標「Filtered deepfake image, classified as bona fide」。**修復同樣只列為 future work**（濾鏡增強、多分類器融合、manipulation-invariant 特徵），未實作。→ 這是我們最直接的量化對照對象：他們 48.4% APCER vs 我們 2.80% stress error。**注意：我們原本引的 arXiv 2409.00375「Deceptive Beauty: The Risks of AI-Enhanced Appearance」不存在，正確的是這一篇。** | 🔴 必引，取代錯誤引用 |
| [Making DeepFakes more spurious: evading deep face forgery detection via trace removal attack](https://arxiv.org/abs/2203.11433) (IEEE TDSC) | Anti-forensics 對照組：主動移除偽造痕跡的攻擊。用來凸顯對比——這類攻擊需要最佳化與模型知識，而美顏濾鏡攻擊只需要在 Instagram 點一下。 | ✅ 參考 |
| [Generating Higher-Quality Anti-Forensics DeepFakes with Adversarial Sharpening Mask](https://dl.acm.org/doi/10.1145/3729233) (ACM TOMM 2025) | 同上，anti-forensics 最新代表作，related work 需一句帶過 | ✅ 參考 |
| [Adversarial and generative AI-based anti-forensics in audio-visual deepfake detection: A comprehensive review](https://www.sciencedirect.com/science/article/abs/pii/S1566253525011820) (Information Fusion) | Anti-forensics 綜述，一次引用涵蓋整條線。⚠️ **2026-08-27 更正卷期年份**：dblp 著錄為 **Inf. Fusion, vol. 132, art. 104120, 2026**（作者 Qurat Ul Ain, Fatima Khalid, Hafsa Ilyas, Ali Javed, Khalid Mahmood Malik, Khan Muhammad, Aun Irtaza），且完整標題結尾為 "... A comprehensive review **and analysis**"。原標「2025」為線上先行日期，正式卷期年份應寫 2026。 | ✅ 參考 |
| [Face morphing detection in the presence of printing/scanning and heterogeneous image sources](https://arxiv.org/abs/1901.08811) — Ferrara, Franco, Maltoni (IET Biometrics 2021) | ⚠️ **生物辨識社群的既有常識**：人工修圖/後處理可掩蓋 morph 痕跡，比 deepfake 社群早很多年。不引會被該領域 reviewer 抓。 | ✅ 建議引 |
| [Morphing Attack Detection — Database, Evaluation Platform and Benchmarking](https://arxiv.org/abs/2006.06458) — Raja et al. (IEEE TIFS 2021) | 同上，MAD 後處理穩健性的標準參考 | ✅ 建議引 |
| [Realism to Deception: Investigating Deepfake Detectors Against Face Enhancement](https://arxiv.org/abs/2509.07178) — Saeed, Haq, Malik (2025) | 🔴 **第三篇同主題前作**：把 face enhancement 直接當 anti-forensic attack，FF++/DFD/CelebDF-v2 上 **ASR 高達 64.63%**，且已測過 adversarial training 作為緩解。與我們的 2.80% stress error 直接可比。 | 🔴 必引 |

---

## 2026-08-27 文獻調查新增（Angle 2/3：三分類與跨演算法泛化）

| 論文 | 為何必引 | 狀態 |
|------|------|------|
| [ForgeryNet: A Versatile Benchmark for Comprehensive Forgery Analysis](https://arxiv.org/abs/2103.05630) — He et al., **CVPR 2021 Oral** | 🔴 **必引**。2.9M 影像/221K 影片，官方就有 **3-way protocol：real / identity-replaced / identity-remained**——用「身份是否保留」當切分軸，與我們的 real/fake/filter 概念軸相同。但 identity-remained = GAN 語意屬性編輯（StarGANv2/MaskGAN/SC-FEGAN），**不是**美顏修圖。不引＝被 reviewer 直接問「這不是已經有了嗎」。 | 🔴 必引 |
| [On the Detection of Digital Face Manipulation (DFFD)](https://arxiv.org/pdf/1910.01717) — Dang, Liu, Stehouwer, Liu, Jain, **CVPR 2020** | 🔴 **必引**。含 18,416 張 FaceApp 影像作為 "attribute manipulation"，但那是語意屬性替換（性別/年齡/鬍子/眼鏡），**不是**磨皮/美白/瘦臉；且 DFFD 的 protocol 是**二分類**。論文必須明寫「為何 FaceApp attribute swap ≠ 我們的 filter class」，否則 reviewer 會直接假設重複。另外 DFFD 的 **IINC** 定位指標我們已在用。 | 🔴 必引 |
| [Detecting Photoshopped Faces by Scripting Photoshop (FALdetector)](https://arxiv.org/abs/1906.05856) — Wang, Wang, Owens, Zhang, Efros, **ICCV 2019** | 🔴 **本次調查認定最重要的遺漏引用**。專偵測 Photoshop Face-aware Liquify 的幾何美顏（≈我們的 face_reshaping / eye_enlarging），能贏過人類、能定位、還能部分「還原」形變場。**作者自陳的 limitation 就是單一工具泛化問題**——正是我們 Angle 3 的核心。 | 🔴 必引 |
| [Three-classification face manipulation detection using attention-based feature decomposition (TFMD)](https://www.sciencedirect.com/science/article/abs/pii/S0167404822004163) — Computers & Security 2023 | ⚠️ **標題直接撞我們的框架**（"three-classification face manipulation detection"），但三類是 real / face replacement / face reenactment，完全沒有美顏。當作「證明我們論點的反例」引用；不引很危險。 | 🔴 必引 |
| [MoFRR: Mixture of Diffusion Models for Face Retouching Restoration](https://arxiv.org/abs/2507.19770) — Liu, Ying et al., **ICCV 2025** | 🔴 **RetouchingFFHQ 原團隊的新作**，推出 **RetouchingFFHQ++（>100 萬張、4 個商用 API）**，並用 sparse MoE（每種修圖一個 expert + 一個共享 expert 抓通用修圖痕跡）。① 我們文件裡「RetouchingFFHQ 有 3 個 API」的敘述已過時；② 共享 expert 是文獻中最接近「跨演算法泛化的結構性解法」的設計，且出自資料集原團隊，代表他們自己也認為單一模型不夠。 | 🔴 必引 |
| RetouchingFFHQ **Table 5 / Table 7（跨 API 結果）** — 已引論文，但幾乎確定沒引到這張表 | 🔴 **我們 Angle 3 最強的外部證據**。Megvii→Tencent 直接遷移 Sum TP 從 .931 崩到 **.196**；逐項目：eye .783 / lift .376 / **smooth .086 / whiten .041**——**幾何濾鏡部分存活、光度濾鏡完全崩潰**，與我們 Alibaba 的失敗模式同構。他們的 MAM 模組跨 API 只買到 **+0.005~+0.013 Sum TP**（雜訊等級），唯一有效解法是在目標 API 上 finetune（.196→.907）。⚠️ 注意 Megvii→Alibaba 直接遷移他們拿到 .594/.607（因為他們的 Alibaba 子集是單一操作、比較簡單），**不可拿我們的 3-35% 型別準確率直接說「推翻他們」**，指標不同，必須寫清楚。 | 🔴 必引（引表，不只引資料集） |
| [Differential Detection of Facial Retouching: A Multi-Biometric Approach](https://ieeexplore.ieee.org/document/9109348) — ~~Rathgeb, Dogan, Stockhardt, De Marsico, Busch~~ → ⚠️ **2026-08-27 更正作者群**：正確作者為 **Rathgeb, Satnoianu, Haryanto, Bernardo, Busch**（dblp / IEEE Access 8:106373-106385, 2020 確認）。原列的 Dogan / Stockhardt / De Marsico 是**同年另一篇** Rathgeb 等人的 "Plastic Surgery: An Obstacle for Deep Face Recognition?"（CVPRW 2020）的作者群，兩篇作者名單被混淆。卷期頁碼 **IEEE Access 8:106373-106385, 2020** 經查證正確 ＋ [PRNU-based Detection of Facial Retouching](https://ietresearch.onlinelibrary.wiley.com/doi/full/10.1049/iet-bmt.2019.0196) (IET Biometrics 2020) | 🔴 **唯一明確宣稱跨工具穩健的前作**。差分式（需要同人參考影像）+ PRNU 感測器雜訊。六個手機美顏 App（AirBrush/BeautyPlus/Bestie/FotoRus/InstaBeauty/YouCamPerfect），leave-one-app-out protocol，指標是 **D-EER** 不是 accuracy。論文必須說明「他們的差分假設（要有可信參考影像）我們沒有」。⚠️ 具體 D-EER 數字為 snippet 來源，投稿前需查原文。 | 🔴 必引 |
| [Differential Anomaly Detection for Facial Images](https://arxiv.org/pdf/2110.03464) — Ibsen, **González-Soler**, Rathgeb, Fischer, Drozdowski, Busch, **WIFS 2021**（⚠️ 2026-08-27 補正：原漏列第二作者 Lázaro J. González-Soler） | 已直接查證：用 InstaBeauty/FotoRus 當修圖測試集，**BPCER100 > 40%**，作者自陳修圖「只是溫和改變外觀、不改變身份」所以最難。獨立佐證「修圖是最硬的殘留案例」。 | ✅ 建議引 |
| [Demography-based Facial Retouching Detection using Subclass Supervised Sparse Autoencoder (MDRF)](https://arxiv.org/abs/1709.07598) — Bharati, Vatsa, Singh, Bowyer, Tong, **IJCB 2017** | 跨族群（印度/華人/白人）修圖偵測準確率大幅波動——**十年前就有的「學到語料庫、不是學到操作」同型病理**，替我們的 meta-finding 提供時間深度。 | ✅ 建議引 |
| [OpenFilter / FairBeauty + B-LFW](https://arxiv.org/pdf/2207.12319) (NeurIPS 2022 D&B)、[LFW-Beautified](https://arxiv.org/pdf/2203.06082)、[On the Effect of Selfie Beautification Filters on Face Detection and Recognition](https://arxiv.org/pdf/2110.08934) (PRL 2022) | ⚠️ **公開的 LFW-美顏資料集本來就存在，我們卻自建了 OpenCV pipeline**。reviewer 會問為什麼不用。至少應該當作額外的跨工具 OOD 集評測一次——這是成本極低、價值極高的實驗。 | 🔴 必引＋建議實驗 |
| [Benchmarking Unified Face Attack Detection via Hierarchical Prompt Tuning (HiPTune)](https://arxiv.org/html/2505.13327v2) (2025)、[Language-guided HiFi-IFDL](https://arxiv.org/pdf/2410.23556) (2024)、[EfficientNet-Based Multi-Class Detection of Real, Deepfake, and Plastic Surgery Faces](https://arxiv.org/abs/2509.12258) (2025) | 防守性引用：證明我們知道 2024-25 的階層式分類法現況（HiPTune 54 種攻擊的 coarse-to-fine 樹），且知道已有人做過「real/deepfake/整形」三分類。**「階層式分類法」在 2026 已經不是 novelty。** | ✅ 建議引 |

---

## 2026-08-27 文獻調查新增（Angle 4/5：輕量部署與自然語言解釋）

| 論文 | 為何必引 | 狀態 |
|------|------|------|
| [MesoNet: a Compact Facial Video Forgery Detection Network](https://arxiv.org/abs/1809.00888) — Afchar, Nozick, Yamagishi, Echizen, **IEEE WIFS 2018** | 🔴 輕量偵測的經典基準點（Meso-4 = **27,977 參數**；FF/Face2Face 高壓縮下 83.2%/81.3%）。做輕量主題不引它＝不熟文獻。**但它也從未報告 MB 或 ms**——正是我們要對比的「參數少 ≠ 有部署」。 | 🔴 必引 |
| [DefakeHop++: An Enhanced Lightweight Deepfake Detector](https://arxiv.org/abs/2205.00211) — Chen, Hu, You, Kuo (2022) | 🔴 **238K 參數（MobileNetV3 的 16%）、FF++ video AUC 99.3%，但零 MB、零 ms、零裝置**。我們「參數量 vs 真實部署」論證的最佳反例。 | 🔴 必引 |
| **DeFakeQ**（⚠️ 我們現有清單裡的 arXiv 2412.01799 連結需查證，正確版本疑為 arXiv:2604.08847 "Enabling Real-Time Deepfake Detection on Edge Devices via Adaptive Bidirectional Quantization"） | 🔴🔴 **我們 Angle 4 最危險的競爭者**：Swin-Base 334.8MB → **31.8MB**，**在 Android 手機實測 25ms/幀、≤50ms 最壞、87mW**。**他們在真手機上量了、我們沒有**（我們只有桌機 CPU 15.68ms，iPhone 實測仍是 TODO）。代價是量化掉 **−9.4pp AUC**（86.5→77.1），而我們 TFLite 是 **769/769 決策零損失**。這組對比是我們唯一站得住的反擊。**投稿前務必補真機數字。** | 🔴 必引，且必須正面對決 |
| [Unlocking the Potential of Lightweight Quantized Models for Deepfake Detection (QMDD)](https://www.ijcai.org/proceedings/2025/0059.pdf) — Tao, Qin, Ding, Tan, **IJCAI 2025** | 🔴 **必引且必須預先回應**。他們的 **Shifted Logarithmic Redistribution Quantizer** 就是「把不平衡 activation 展開以避免近零區間資訊損失」——正是 reviewer 會拿來問「你的 FFT int8 崩潰為什麼不用這招」的東西。我們必須說明有沒有試、為何不適用。 | 🔴 必引 |
| [A Brief Review for Compression and Transfer Learning Techniques in DeepFake Detection](https://arxiv.org/abs/2504.21066) — Karathanasis et al. (2025) | 「int8 對純空間域偵測器沒問題」的引用來源，用來凸顯我們 FFT 分支失效的特殊性。（他們全跑在 2×T4 GPU，零裝置實測。） | ✅ 必引 |
| ~~[MSCA-FFT: Explainable FFT-Based Spatial-Frequency Fusion](https://arxiv.org/html/2607.17441) (2026)~~ → 正式標題為 [An Explainable FFT-Based Spatial-Frequency Fusion Framework for Deepfake Detection](https://arxiv.org/abs/2607.17441) — Kirui, Cho, Liu et al. (2026) | ⚠️ **2026-08-27 更正標題**：arXiv 2607.17441 的標題**不含 "MSCA-FFT"**（那應是內文方法名，非論文標題），且原標題漏掉結尾 "Framework for Deepfake Detection"。ID 正確、論文存在，僅標題誤植；參考文獻須用正式標題。🔴 **架構上離我們 DualBranch 最近的鄰居**（Xception + **log-scaled** FFT magnitude 分支，CDF-v2 99.98% AUC）。兩個必須處理的點：① 必須定位差異；② **他們的 log scaling 正是能避免我們 7.6e9 動態範圍問題的設計選擇**——我們得說明為何用原始 magnitude、改 log 的代價是什麼。 | 🔴 必引 |
| [MoE-FFD: Mixture of Experts for Generalized and Parameter-Efficient Face Forgery Detection](https://arxiv.org/abs/2404.08452) (**IEEE TDSC** 2025) | 「參數高效 ≠ 可部署」的代表（backbone 仍是 ViT-B，無 MB/ms）。⚠️ **2026-08-27 更正 venue：是 IEEE TDSC（Trans. on Dependable and Secure Computing），不是 TIFS**（arXiv PDF 頁首明載 "SUBMITTED TO IEEE TRANSACTIONS ON DEPENDABLE AND SECURE COMPUTING"）。 | ✅ 建議引 |
| [Common Sense Reasoning for Deepfake Detection (DD-VQA)](https://arxiv.org/abs/2402.00126) — Zhang, Colman, Guo, Shahriyari, Bharaj, **ECCV 2024** | 🔴 **人臉偽造「用文字解釋而非熱圖」這條線的起點**。缺這篇＝不熟文獻。 | 🔴 必引 |
| [SIDA: Social Media Image Deepfake Detection, Localization and Explanation with LMM](https://openaccess.thecvf.com/content/CVPR2025/html/Huang_SIDA_Social_Media_Image_Deepfake_Detection_Localization_and_Explanation_with_CVPR_2025_paper.html) — **CVPR 2025** | 🔴 「偵測＋定位＋解釋」三合一的參考點，SID-Set 30 萬張。 | 🔴 必引 |
| [X²-DFD: A framework for eXplainable and eXtendable Deepfake Detection](https://arxiv.org/abs/2410.06126) — Chen et al., **NeurIPS 2025** | 🔴 **與我們 evidence head 構想最近的已發表親戚**：其 "Weak Feature Supplementing" 就是「把專用低階 artifact 分析器的量測結果餵進解釋路徑，而不是讓 MLLM 自由生成」。**必須明確引用並說明差異**。 | 🔴 必引 |
| [Rethinking Vision-Language Model in Face Forensics (M²F²-Det)](https://openaccess.thecvf.com/content/CVPR2025/papers/Guo_Rethinking_Vision-Language_Model_in_Face_Forensics_Multi-Modal_Interpretable_Forged_Face_CVPR_2025_paper.pdf) — Guo et al., **CVPR 2025 Oral** | 🔴 同時輸出判決與解釋；CVPR Oral，reviewer 必知。 | 🔴 必引 |
| [VIGIL: Part-Grounded Structured Reasoning for Generalizable Deepfake Detection](https://arxiv.org/pdf/2603.21526) (2026) | 🔴🔴 **與我們 novelty 撞得最兇的一篇**：明講「將 region-level 解釋建立在 forensic signals 而非 template-like rationales 上」——幾乎逐字是我們的賣點。**寫論文前必須先讀完這篇。** | 🔴 必引，最高碰撞風險 |
| [XPlainVerse: A Million-Scale Benchmark for Explainable Deepfake Detection](https://arxiv.org/pdf/2607.03562) ＋ [Explainable Deepfake Detection Challenge](https://arxiv.org/html/2607.21007v1) (⚠️ **ACM MM 2026 出處未經證實**，arXiv 頁面未載明，引用前須查 ACM DL 或改標為 arXiv preprint) | 🔴 **定義了目前解釋品質的評測標準**：BERTScore-F1 + **SLE（可讀性）** + LLM 評分的 **EntityScore / EvidenceScore**（占最終分數 60%）。**若我們只報 BLEU/CIDEr 會顯得過時。**其動機句「現有解釋 fluent but weakly tied to actual image artifacts」也正是我們的立論。 | 🔴 必引 |
| [GRIDEX: Grid-Grounded Forensic Explanations for **Deepfake Spectrogram Analysis**](https://arxiv.org/html/2606.18738) (CSIRO Data61, 2026) | ⚠️ **2026-08-27 更正：這是「音訊／頻譜圖」領域的 deepfake 偵測，不是影像**——原本清單裡標題被截斷（少了 "for Deepfake Spectrogram Analysis"）而看不出來，**若當成影像鑑識的 prior art 引用會是實質錯誤**。仍可引用，但必須明確標示為跨領域類比。內容價值不變：schema 結構化解釋的既有前作（固定欄位 tuple + FieldAcc/CovAvg 指標），我們的 structured JSON schema 在架構上不是新的；同時它是我們最好的支持證據——**即使有固定 schema + Qwen2.5-VL-3B，FieldAcc 只有 0.333**（欄位三次錯兩次），正是「用確定性量測值生成、而非讓 VLM 產生欄位」的論據。 | 🔴 必引（須標明音訊領域） |
| [ExDDV: A New Dataset for Explainable Deepfake Detection in Video](https://arxiv.org/abs/2503.14421) (**WACV 2026**) | 關鍵結論：**只有文字監督不夠，必須加上點擊（空間）監督**才能同時定位與描述。直接支持我們 patch evidence head 的設計賭注。 | ✅ 必引 |
| [LOKI: A Comprehensive Synthetic Data Detection Benchmark using Large Multimodal Models](https://proceedings.iclr.cc/paper_files/paper/2025/hash/afd6374c7f2839cba22f537f15f4f760-Abstract-Conference.html) (ICLR 2025 Spotlight)、[Ivy-Fake: A Unified Explainable Framework and Benchmark for Image and Video AIGC Detection](https://arxiv.org/abs/2506.00979) (ICMR 2026)、[AntifakePrompt](https://arxiv.org/abs/2310.17419) (**ICLR 2025 Workshop on Building Trust in LLMs**)、[Bi-LORA](https://arxiv.org/abs/2404.01959) (arXiv preprint，無 peer-reviewed venue，勿標會議) | 防守性引用群：LOKI/Ivy-Fake 是標準解釋性 benchmark；AntifakePrompt/Bi-LORA 是「VLM 當分類器、其實沒有真正解釋」的對照類別。⚠️ **2026-08-27 更正**：AntifakePrompt 是 **workshop 論文非主會議**（把 workshop 當主會議引用是 reviewer 必抓的錯誤）；LOKI 原本用 GitHub 網址代替論文引用，已補正式出處與完整標題；Ivy-Fake 標題補上副標。 | ✅ 建議引 |

---

## 2026-08-27 文獻調查新增（Angle 6/7/8：忠實度、語料庫捷徑、棄權）

| 論文 | 為何必引 | 狀態 |
|------|------|------|
| [Sanity Checks for Saliency Maps](https://arxiv.org/abs/1810.03292) — Adebayo, Gilmer, Muelly, Goodfellow, Hardt, Kim, **NeurIPS 2018** | 🔴 我們 randomization test 的出處。⚠️ **注意**：他們做的是**逐層 cascading randomization**，且 vanilla Grad-CAM 在他們的設定下**是有反應的**。我們只做 classifier-head randomization 是最弱版本，必須寫明用了哪個變體，否則會被質疑。 | 🔴 必引 |
| [Assessing the Trustworthiness of Saliency Maps for Localizing Abnormalities in Medical Imaging](https://pubs.rsna.org/doi/full/10.1148/ryai.2021200267) — Arun et al., **Radiology: AI 2021** | 🔴🔴 **我們 Angle 6 貢獻的直接方法論前作**——8 種 saliency 方法（含 Grad-CAM++）、randomization + GT 定位 + **平凡空間先驗對照組**，結論「全部至少不過一項、全部輸給專用定位網路」。**我們的發現在 reviewer 眼中就是「Arun et al. 2021 套到 deepfake 上」。不引＝致命。** | 🔴 必引 |
| [Sanity Checks for Saliency Metrics](https://ojs.aaai.org/index.php/AAAI/article/view/6064) — Tomsett et al., **AAAI 2020** | 🔴 證明 saliency 忠實度**指標本身**統計上不可靠。**我們需要它來替 0.787 vs 0.787 的「無差異」宣稱辯護**（需要等價性檢定 TOST，不是「沒拒絕虛無假設」）。 | 🔴 必引 |
| [Towards Quantitative Evaluation of Explainable AI Methods for Deepfake Detection](https://arxiv.org/abs/2404.18649) — Tsigos, Apostolidis, Mezaris et al., **MAD'24 @ ACM ICMR** ＋ [WACVW 2025 續作](https://arxiv.org/abs/2502.03957) | 🔴 **同領域最接近的前作**：在 FF++ 偵測器上比較 Grad-CAM++/RISE/SHAP/LIME/SOBOL，**結論 LIME 最好**，且主張通用 deletion/insertion 不適合 deepfake 偵測器。**關鍵：他們沒有任何平凡/隨機/中心對照組**——這正是我們的切入點。 | 🔴 必引 |
| [A Fresh Look at Sanity Checks for Saliency Maps (Smooth-/Efficient-MPRT)](https://link.springer.com/chapter/10.1007/978-3-031-63787-2_21) — Hedström et al., xAI 2024 ＋ [Revisiting Sanity Checks](https://arxiv.org/abs/2110.14297) — Yona & Greenfeld | 🔴 **對我們所依賴檢定的既有批評**：Hedström 明確指出「用原始熱圖的 Spearman 相關」這個量測有偏差——**正是我們回報的 0.83~0.97 的量測方式**。必須補 Efficient-MPRT 才站得住。 | 🔴 必引 |
| [What Do Different Evaluation Metrics Tell Us About Saliency Models?](https://arxiv.org/abs/1604.03605) — Bylinskii et al., **TPAMI 2019**（＋MIT300 benchmark） | 🔴 我們「中心高斯先驗對照組」的來源正當性：在**人眼注視 saliency** 領域，center-bias baseline 是 MIT300 的標準配備，且 shuffled AUC (sAUC) 專門懲罰中心偏差。**這個對照從未被引進 XAI-for-forensics**——這個跨領域移植就是我們的方法論貢獻（是 control，不是 method，要如實定位）。 | 🔴 必引 |
| [ED⁴: Explicit Data-level Debiasing for Deepfake Detection](https://arxiv.org/abs/2408.06779) — Ba, Liu, Jiang et al., **IEEE TIP 2025** | 🔴🔴 **最接近我們發現(i)的既有主張**：他們明確命名 **"spatial bias"——偵測器慣性預期偽造線索出現在影像中心**，並提出 AdvSCM 消除它。同時也命名 content bias / specific-forgery bias（Angle 7 也要引）。**建議實驗**：在 ED⁴-debias 過的偵測器上重跑我們的 saliency 評測——若中心先驗打平消失，我們就從「又一個負面結果」升級成「因果診斷」。 | 🔴 必引 |
| [RISE: Randomized Input Sampling for Explanation](https://arxiv.org/abs/1806.07421) — Petsiuk et al., BMVC 2018 | deletion/insertion 指標的出處，必引。 | 🔴 必引 |
| [Grad-CAM++ is Equivalent to Grad-CAM With Positive Gradients](https://arxiv.org/abs/2205.10838) | reviewer 會問「為何用 ++ 不用 vanilla」——這篇說差別很小，先引先擋。 | ✅ 建議引 |
| [Shortcut Learning in Deep Neural Networks](https://www.nature.com/articles/s42256-020-00257-z) — Geirhos et al., **Nature Machine Intelligence 2020** | 🔴 「捷徑學習」這個詞本身的出處。 | 🔴 必引 |
| [Unmasking Clever Hans Predictors (SpRAy)](https://www.nature.com/articles/s41467-019-08987-4) — Lapuschkin et al., **Nature Communications 2019** ＋ [Finding and Removing Clever Hans (ClArC)](https://arxiv.org/abs/1912.11425) (Information Fusion 2022) | 🔴🔴 **「系統性驗證捷徑學習的方法論」已經有名字了：SpRAy / ClArC。**我們不可宣稱發明了驗證方法論，只能宣稱「本任務的具體實例化」。這是本次調查對 Angle 7 最重要的壞消息之一。 | 🔴 必引 |
| [Implicit Identity Leakage](https://openaccess.thecvf.com/content/CVPR2023/html/Dong_Implicit_Identity_Leakage_The_Stumbling_Block_to_Improving_Deepfake_Detection_CVPR_2023_paper.html) — Dong et al., **CVPR 2023**（即 CADDM） | 🔴 **deepfake 捷徑學習的旗艦前作**：二元偵測器學到的是身份表徵而非操弄痕跡。不引＝不熟本領域。（注意：CADDM 同時也是 Celeb-DF-B 論文評測的三個偵測器之一。） | 🔴 必引 |
| [Fake or JPEG? Revealing Common Biases in Generated Image Detection Datasets](https://link.springer.com/chapter/10.1007/978-3-031-92089-9_6) — Grommelt, Weiss, Pfreundt, Keuper，⚠️ **2026-08-27 補正出處：ECCV 2024 Workshops, pp. 80-95（Springer LNCS，2025 出版）；preprint 為 arXiv:2403.17608。原本只寫「2024/2025」會讓 reviewer 無法判定是 workshop 論文——本清單稍早已因 AntifakePrompt 犯過同型錯誤，此處一併標明。** | 🔴 影像鑑識中最乾淨的「學到語料庫、不是學到操弄」量化結果：GenImage 的 JPEG／尺寸偏差修正後跨生成器表現 **+11pp（ResNet-50 71.7→82.7）**。 | 🔴 必引 |
| [Circumventing shortcuts in audio-visual deepfake detection datasets](https://arxiv.org/abs/2412.00175) | 🔴 **最有殺傷力的修辭錨點**：FakeAVCeleb 與 AV-Deepfake1M 的偽造影片開頭都有一小段靜音，**一個只判斷靜音的平凡分類器就能拿 >98%**。 | 🔴 必引 |
| [Deepfake Detection that Generalizes Across Benchmarks](https://arxiv.org/abs/2508.06248) — Yermakov, Cech, Matas, Fritz (2025) | §4.4 的經驗證據：**必須用同一來源影片的配對 real/fake 訓練**才能抑制捷徑學習，否則模型會利用表層高階差異。直接關係到我們 split 的建構方式；同時它也是目前 cross-dataset 表的 SOTA（CDFv2 96.5 / DFDC 87.0 video AUC）。 | 🔴 必引 |
| [Navigating Shortcuts, Spurious Correlations, and Confounders](https://arxiv.org/abs/2412.05152) — Steinmann et al. (2024) | 統一分類法／綜述，讓我們把自己的 protocol **定位在既有地圖之內**而不是宣稱另立門戶。 | ✅ 必引 |
| [DeepfakeBench](https://arxiv.org/abs/2307.01426) (NeurIPS 2023 D&B) | 前處理不一致導致比較不公平；也是 frame-level AUC 標準表的來源。reviewer 會問「你的效應在標準化 pipeline 下還在嗎」。 | 🔴 必引 |
| [A Sanity Check for AI-generated Image Detection](https://arxiv.org/abs/2406.19435) — Yan, Li, Cai et al., **ICLR 2025**（提出 Chameleon 資料集與 AIDE 偵測器；⚠️ **2026-08-27 更正**：原以 "Chameleon / AIDE" 當標題引用，那是資料集/方法名，論文正式標題為 "A Sanity Check for AI-generated Image Detection"；ICLR 2025 已由 proceedings.iclr.cc 確認） | 🔴 **我們「語料庫捷徑」meta-finding 的最強外部佐證**：所有 baseline 在 real 上 94-100%、在 fake 上只有 1-22%，而整體準確率完全掩蓋這件事。 | 🔴 必引 |
| [Selective Classification for Deep Neural Networks](https://arxiv.org/abs/1705.08500) (NeurIPS 2017) ＋ [SelectiveNet](https://proceedings.mlr.press/v97/geifman19a.html) (ICML 2019) ＋ Chow's rule (1957/1970) | 🔴 棄權／選擇性預測的標準形式與 **risk–coverage 曲線**。我們的 gate 必須跟 Chow 規則（max-softmax 門檻）在相同 coverage 下對比。 | 🔴 必引 |
| [Learning to Reject Low-Quality Explanations (LtX / REX / ULER)](https://arxiv.org/abs/2507.12900) — Stradiotti, Pesenti, Teso, Davis (2025) | 🔴🔴 **「無法好好解釋時就棄權」這個框架已經被別人正式化了，而且早我們一年。**他們定義 LtX、提出兩個方法、在 8 個 benchmark 上比較（低品質解釋率降低 20-32%）。**但他們零鑑識、零 deepfake**——我們只能宣稱「第一個鑑識領域的實例化」。本次調查對 Angle 8 最危險的遺漏。 | 🔴 必引 |
| [Is It Certainly a Deepfake? Reliability Analysis in Detection & Generation Ecosystem](https://arxiv.org/abs/2509.17550) — Kose, Rhodes, Ciftci, Demir, **ICCV 2025 Workshop** | 🔴 自稱「第一個 deepfake 偵測器的全面不確定性分析」（BNN + MC-dropout、aleatoric/epistemic、像素級不確定性圖）。**「deepfake 偵測器該知道自己不知道」這塊已經很擁擠**，我們必須相對定位。 | 🔴 必引 |
| [Uncertainty-Aware Deepfake Detection via Multi-View Structural Learning](https://arxiv.org/html/2607.28769) (2026)、[Open Set Face Forgery Detection via Dual-Level Evidence Collection](https://arxiv.org/abs/2512.04331)、[Attack-Aware Deepfake Detection under Counter-Forensic Manipulations](https://arxiv.org/abs/2512.22303) | UQ／evidential／open-set 直接競爭者群。最後一篇是 arXiv 上唯一使用 "abstention quality" 當 deepfake 指標的論文。 | ✅ 必引 |
| [A Gentle Introduction to Conformal Prediction](https://arxiv.org/abs/2107.07511) — Angelopoulos & Bates | ⚠️ **arXiv 上 `"deepfake" AND "conformal prediction"` 命中數 = 0**。split-conformal 大約 20 行程式碼就能給出無分布假設的覆蓋保證——**本次調查發現的最便宜的 novelty**。 | ⏳ 建議做 |

---

## 2026-08-27 外部推薦引用查證（4 篇新推薦 + 3 篇防守性引用，逐一獨立查證）

> ⚠️ **查證背景**：使用者收到一批外部搜尋工具給的論文推薦，鑑於本清單稍早已抓到 3 件
> arXiv ID 指錯論文（Deceptive Beauty / DeFakeQ 舊版 / HEIE），本輪對每一篇**重新獨立**
> 用 arXiv 官方頁面或出版社頁面核對標題、作者、venue、年份與**具體數字**，不採信外部工具原始描述。
> **結果：4 篇新推薦全部 VERIFIED（含全部具體數字）；3 篇防守性引用全部確認存在。0 件捏造。**

| 論文 | 查證結果 |
|------|------|
| [LRD-Net: A Lightweight Real-Centered Detection Network for Cross-Domain Face Forgery Detection](https://arxiv.org/abs/2604.10862) — Xuecen Zhang, Vipin Chaudhary (2026-04-13) | ✅ **VERIFIED，含全部數字**。已逐字讀 arXiv 摘要：**2.63M 參數（比傳統方法少約9x）、訓練快 8x 以上、推論快近 10x、在 DiFF benchmark 上達 SOTA cross-domain 準確率**，四項數字與外部推薦描述完全吻合，非誇大。架構為 MobileNetV3-based spatial backbone + Multi-Scale Wavelet Guidance Module 產生的**序列式**頻率引導（作者自陳與我們及多數文獻的**平行雙分支**設計不同，這點必須在 related work 提及）。⚠️ **對照時須注意**：SOTA 主張限定在 **DiFF**（diffusion-based face forgery）benchmark，非泛用 cross-dataset 基準；我們可比較對象是**參數量**（我們三模型合計 25.75MB／各模型 ~1.26-2M 參數量級 vs 此文 2.63M 單模型）而非直接比 AUC（無共同測試集）。 |
| ~~"Real-Time Deepfake Detection on Embedded Systems"（MobileNetV2, Samsung Galaxy A31 實測, AUC 0.8718, 100-200ms/frame）~~ | ❌ **NOT FOUND**。多輪 WebSearch（含精確片語搜尋「Samsung Galaxy A31」+ AUC 數值＋MobileNetV2 embedded 各種組合）查無任何論文同時符合「MobileNetV2」＋「Galaxy A31 實機」＋「AUC 0.8718」＋「100-200ms」。找到的相關論文（如 MobileNetV2+SVM deepfake 偵測、DeepConfGuard MobileNetV2+BiLSTM）數字與 venue 皆對不上（如 MobileNetV2+SVM 报告的是 accuracy 94.8%/precision 93.5%/recall 95.6%，不是 AUC 0.8718；也没有 Galaxy A31）。**不排除是外部工具把多篇論文的片段拼接成一篇不存在的複合體**（與本 session 已抓到的三次捏造模式一致）。**未加入清單，也未寫入具體錯誤 ID（因外部推薦本身未給 arXiv ID，無 ID 可標記為誤植）**。 |
| [FL-TENB4: A Federated-Learning-Enhanced Tiny EfficientNetB4-Lite Approach for Deepfake Detection in CCTV Environments](https://www.mdpi.com/1424-8220/25/3/788) — Jimin Ha, Abir El Azzaoui, Jong Hyuk Park, **Sensors 25(3):788, 2025**（DOI 10.3390/s25030788） | ✅ **VERIFIED，含數字**。已用 PMC 全文核對：FaceForensics++ c23 上 **Accuracy 94.2% / F1 93.5% / ROC-AUC 0.96 / 推論延遲 12ms/frame / 模型 4.2MB**，外部推薦的「EfficientNetB4-Lite + TinyML + CCTV + AUC 0.96」四項全部命中；額外查到 c0/c40 的完整表格（AUC 0.97→0.94 隨壓縮惡化）。**可比較對象**：他們模型 4.2MB／12ms vs 我們三模型合計 25.75MB／三階段均 15.68ms——他們單模型更小更快但只做二分類（無 filter 第三類）、且未做跨資料集 OOD（僅 FF++ 內部 c0/c23/c40）。 |
| insightface.ai 月度 arXiv 文獻整理（blog.insightface.ai） | ✅ **VERIFIED 為真實且持續更新的資源**（非可引用論文）。查到 2026 年 3、5、6、7 月的「Deepfake Detection Papers」與「Face Swapping Papers」月度整理文章持續發佈（如 `insightface.ai/blog/july-2026-deepfake-detection-papers`），內容涵蓋 explainable forensics／physiological cues／incremental learning 等主題。**可作為持續文獻監測的實務工具**（訂閱/定期查看），**不作為投稿引用文獻**。 |

**防守性引用（較低查證強度，僅確認存在與基本屬性，不逐字核對數字）：**

| 論文 | 查證結果 |
|------|------|
| [Hierarchical supervisions with two-stream network for Deepfake detection (HTNet)](https://www.sciencedirect.com/science/article/abs/pii/S0167865523001678) — Liang, Wang, Jin, Pan, Liu, **Pattern Recognition Letters, vol. 172, pp. 121-127, 2023** | ✅ **存在確認**。空間流+頻率流雙流架構，coarse-to-fine 階層式監督（先二分類再細分），與 TFMD／DAD-HCNN 同類「階層式但無 filter 類別」防守性引用群。 |
| [A novel forgery classification method based on multi-scale feature capsule network in mobile edge computing](https://onlinelibrary.wiley.com/doi/abs/10.1002/spe.3245) — Zhichao Lian, Ling Wang, **Software: Practice and Experience, vol. 54, no. 9, pp. 1651-1670, 2024** | ✅ **存在確認**。Residual-guided 多尺度空間注意力 + DCT 頻率模組 + capsule network 分類器，FF++/DFD/FakeAVCeleb 上驗證，「mobile edge computing」情境但論文未報告實機 MB/ms（與我們「參數少≠有部署」論證方向一致，可作反例引用）。 |
| [Enhancing Deepfake Detection Through Hybrid MobileNet-LSTM Model with Real-Time Image and Video Analysis](https://ieeexplore.ieee.org/document/10867159/) (IEEE, 2025)（同一工作亦有 ResearchSquare/SciTePress preprint 版本） | ✅ **存在確認**。MobileNet 空間特徵 + LSTM 時序特徵 + Grad-CAM 可解釋性，多個平台（IEEE Xplore、SciTePress、ResearchSquare）皆有對應版本，內容一致；未逐字核對數字。 |

---

## 計劃使用（第二階段）

| 論文 | 用途 | 狀態 |
|------|------|------|
| [Spot the Fake: Large Multimodal Model-Based Synthetic Image Detection with Artifact Explanation](https://arxiv.org/abs/2503.14905) — Wen, Ye, Feng et al. (2025) | 知識蒸餾 teacher model；FakeClue dataset 來源。⚠️ **2026-08-27 更正標題**：arXiv 2503.14905 的正式標題是 "Spot the Fake: ..."，**「FakeVLM」是該論文提出的模型名稱，不是論文標題**；原本以 "FakeVLM: Towards a Multimodal Deepfake Detection Model" 當標題引用會在參考文獻中對不上（此標題查無此論文）。ID 本身正確，僅標題誤植。 | ⏳ 計劃使用（標題已更正） |
| ~~[DeFakeQ: Deepfake Detection via Quantization](https://arxiv.org/abs/2412.01799)~~ | ⛔ **2026-08-27 查證：第二個捏造引用。** arXiv 2412.01799 實際上是「HPRM: High-Performance Robotic Middleware for Intelligent Autonomous Systems」（Kwok et al., 2024），一篇**機器人中介軟體**論文，與 deepfake 完全無關；且查無「DeFakeQ: Deepfake Detection via Quantization」這個標題的論文。真正的 DeFakeQ 見下一列。**投稿前必須刪除此列。** | ❌ 捏造引用，待刪除 |
| [DeFakeQ: Enabling Real-Time Deepfake Detection on Edge Devices via Adaptive Bidirectional Quantization](https://arxiv.org/abs/2604.08847) (2026) | **真正的 DeFakeQ**（Li, Sun, Zheng, Ma, Lam）。已逐字核對：Swin-Base **334.8MB→31.8MB**、Android **25 ms/幀**、**87 mW**、量化代價 AUC **86.5→77.1（DFD 資料集）**。**這是本領域唯一在真手機上量測過的部署工作**，我們的 15.68ms 是桌機 CPU，論述上必須誠實區分；可用來對比「他們量化省空間但付 9.4pp AUC，我們保持 fp32 且決策逐位元組一致」的取捨。 | ✅ 必引 |
| [LRD-Net: A Lightweight Real-Centered Detection Network for Cross-Domain Face Forgery Detection](https://arxiv.org/abs/2604.10862) — Xuecen Zhang, Vipin Chaudhary (2026) | 🔴 **2026-08-27 新增，已獨立查證數字**。**2.63M 參數**（MobileNetV3-based spatial backbone + Multi-Scale Wavelet Guidance Module 序列式頻率引導，非我們的平行雙分支）、訓練快 **8x**、推論快 **10x**、DiFF benchmark 上 SOTA cross-domain 準確率。**比較基準**：他們單模型 2.63M 參數 vs 我們三模型堆疊 25.75MB／各模型 1-2M 參數量級；他們 SOTA 主張限定在 diffusion-based forgery（DiFF），非泛用跨資料集，引用時須註明比較範圍不同，不可直接宣稱「贏過/輸給」。 | 🔴 必引 |
| [FL-TENB4: A Federated-Learning-Enhanced Tiny EfficientNetB4-Lite Approach for Deepfake Detection in CCTV Environments](https://www.mdpi.com/1424-8220/25/3/788) — Ha, El Azzaoui, Park, **Sensors 25(3):788, 2025** | 🔴 **2026-08-27 新增，已獨立查證數字**。FF++ c23：Accuracy 94.2%／F1 93.5%／**AUC 0.96**／延遲 **12ms/frame**／模型 **4.2MB**。**比較基準**：他們單模型 4.2MB／12ms（二分類，無 filter 第三類，僅 FF++ 內部評測、無跨資料集 OOD）vs 我們三模型 25.75MB／15.68ms（三分類 + artifact 子型別 + 已驗證跨資料集 OOD）。Federated Learning 設計目標（隱私保護的分散式訓練）與我們的邊緣推論部署目標不同，引用時須區分「聯邦學習」與「邊緣推論」兩件事。 | ✅ 參考中 |
| [Distilling the Knowledge in a Neural Network](https://arxiv.org/abs/1503.02531) (Hinton 2015) | 知識蒸餾方法論 | ⏳ 計劃使用 |
| [Deep Compression](https://arxiv.org/abs/1510.00149) | 模型壓縮（剪枝 + 量化） | ⏳ 計劃使用 |
| [MobileNetV4: Universal Models for the Mobile Ecosystem](https://arxiv.org/abs/2404.10518) | Edge 部署備選 backbone | ⏳ 評估中 |

---

## 其他相關（已閱，暫不使用）

| 論文 | 備注 |
|------|------|
| [LFFD: A Light and Fast Face Detector for Edge Devices](https://arxiv.org/abs/1904.10633) | 輕量人臉偵測，若需要 face detection 模組可參考 |
| [EleGANt: Exquisite and Locally Editable GAN for Makeup Transfer](https://www.ecva.net/papers/eccv_2022/papers_ECCV/papers/136760714.pdf) (ECCV 2022) | Makeup transfer，不在目前偵測範圍 |
| [Unveiling Authenticity with Diffusion-based Face Retouching Reversal](https://arxiv.org/abs/2405.07582) | 修圖還原方向，非目前任務 |
| [AutoRetouch: Automatic Professional Face Retouching](https://openaccess.thecvf.com/content/WACV2021/papers/Shafaei_AutoRetouch_Automatic_Professional_Face_Retouching_WACV_2021_paper.pdf) (WACV 2021) | 生成美顏資料可參考，暫無計劃 |

## 2026-09-04 文獻查證輪（`lit_check_20260904.md`，回應 Q1/Q2/Q3/Q6 定位問題）

> 每條均經 arXiv/CVF/官方 GitHub 頁面查證；抽查兩條（FreqNet, SBI）由本 agent
> 二次獨立 WebFetch 覆核通過。標 UNVERIFIED 者未經證實，不得引用。

| 條目 | 定位用途 |
|------|------|
| [F3-Net: Thinking in Frequency](https://arxiv.org/abs/2007.09355) (ECCV 2020) | 空間+頻域雙分支範式的源頭，Xception 48.9M 參數 |
| [SPSL: Spatial-Phase Shallow Learning](https://arxiv.org/abs/2103.01856) (CVPR 2021) | 同代雙分支方法，Xception-scale |
| [Two-branch Recurrent Network](https://arxiv.org/abs/2008.03412) (ECCV 2020) | 影片級雙分支，非輕量 |
| [FreqNet: Frequency-Aware Deepfake Detection](https://arxiv.org/abs/2403.07240) (AAAI 2024) | ✅ 二次覆核：1.9M 參數、17-GAN 平均準確率 92.8%——**唯一 <2M 參數的頻域偵測器**，但為一般 GAN 影像偵測非人臉/影片，訓練於 ProGAN/LSUN |
| [FreqBlender](https://arxiv.org/abs/2404.13872) (NeurIPS 2024) | 頻域用於**資料合成**而非推論分支，範式轉移證據 |
| [FreqDebias](https://arxiv.org/abs/2509.22412) (CVPR 2025) | 明確把「依賴特定頻段」當作 bias 要消除，非優勢 |
| [SBI: Self-Blended Images](https://arxiv.org/abs/2204.08376) (CVPR 2022 Oral) | ✅ 二次覆核：純空間、FF++ real-only 合成 pseudo-fake，本專案 Layer1 SBI 訓練即此法 |
| [UnivFD](https://arxiv.org/abs/2302.10174)（CVPR 2023，題名查證）| CLIP 探針，無頻域分支，304M 參數 |
| [LAA-Net](https://arxiv.org/abs/2401.13856) (CVPR 2024) | EfficientNet-B4+FPN，無頻域，CDF2 video AUC 95.40 |
| [Effort](https://arxiv.org/abs/2411.15633) (ICML 2025，Oral 未經 icml.cc 證實) | CLIP SVD 分解，無頻域 |
| [Forensics Adapter](https://arxiv.org/abs/2411.19715) (CVPR 2025) | frozen CLIP + 5.7M adapter，無頻域 |
| [DefakeHop++](https://arxiv.org/abs/2205.00211)（preprint）| 238K 參數含 DFT 子模組，但為 PixelHop 非 CNN，準確率疑似 within-dataset |
| [DeepfakeBench](https://arxiv.org/abs/2307.01426) (NeurIPS 2023 D&B) | 標準協定：FF++ c23 單一來源訓練，F3Net/SPSL/SRM 三個列為「頻域偵測器」皆 Xception |
| [DF40](https://arxiv.org/abs/2406.13495) (NeurIPS 2024 D&B) | 4 種協定皆源自 FF++/CDF 真實影片，image-level |
| [GM-DF](https://arxiv.org/abs/2406.20078)（venue 未證實）| **明確報告直接合併多資料集訓練會準確率急遽退步**——多來源捷徑風險的直接文獻證據 |
| [ProDet](https://arxiv.org/abs/2408.17052) (NeurIPS 2024) | 「1+1<2」現象：naive 混合 deepfake+blendfake 比單用 blendfake 更差 |
| [CNNDetection](https://arxiv.org/abs/1912.11035) (CVPR 2020) | **靜態 GAN 影像訓練→影片幀評測的既有前例**（ProGAN/LSUN 訓練，"Deepfake" 欄位測 FF++ 影格），本專案靜態訓練/影片評測矛盾的隱性先例 |
| [RetouchingFFHQ](https://arxiv.org/abs/2307.10642) (ACM MM 2023) | ✅ PDF 全文讀取：**多標籤×多強度**（4 操作×4 級，可共存），跨 API（Alibaba 保留作 cross-API 驗證）——本專案單標籤 4-class 封閉集設計之對照基準 |
| [MoFRR / RetouchingFFHQ++](https://arxiv.org/abs/2507.19770) (ICCV 2025) | 同上延伸，4 API（含 PortraitPro），5 級 PSNR 強度，多標籤 router |
| [Celeb-DF-B](https://www.eurecom.fr/en/publication/7481) (IWBF 2024, Libourel et al.) | ✅ PDF 全文讀取：4 類 Real/Real-Beautified/Fake/Fake-Beautified，**濾鏡視為強健性擾動非獨立訓練類別**；RECCE 分數向 real 偏移 −0.07（本專案已在 production 精確復現） |
| [Rathgeb et al. 2020](https://ieeexplore.ieee.org/document/9130787) (IEEE Access) | 唯一驗證「訓練時不知道修圖演算法」的差異式偵測協定，D-EER<10%（精確 leave-one-app 表未證實）|

**Q1/Q2/Q6 綜合判定**（詳見 `lit_check_20260904.md`）：
1. 空間+頻域雙分支是 **2020-2021 年代範式**，2023-2025 跨域 SOTA（SBI/UnivFD/LAA-Net/
   Effort/Forensics Adapter/GenD）**全數無推論期頻域分支**；未找到任何 ShuffleNetV2+
   頻域分支的既有文獻——**非過時到有人做過我們沒做，是這條路線本身正在被淘汰**。
   建議論文定位為「邊緣預算下的傳統雙分支基準」，非 novelty。
2. 未找到同時滿足「≤3M 參數＋真實裝置 MB/ms＋跨資料集 AUC 附 CI」三項的既有比較對象；
   `DeFakeQ`（IEEE，31.8MB/25ms/Android/87mW）是唯一有真機量測者。**本專案數字
   可能是第一個填滿全部三欄的**，但不可宣稱跨域效能具競爭力（production CDFv2
   0.568 遠低於 SBI/LAA-Net 等級的 ≥0.93 video AUC）。
3. **標準協定是單一來源 FF++ c23 訓練**；本專案 ~10 來源混合**相對業界不尋常**；
   文獻記載的風險是**語料庫捷徑**（GM-DF 證實直接合併多資料集會準確率急遽退步；
   ProDet 的 1+1<2 現象），**不是來源太少**——本專案的「語料庫捷徑」meta-finding
   應定位為此文獻脈絡的一個實例，非獨立發現。
4. 靜態訓練→影片評測有隱性先例（CNNDetection→UnivFD→FreqNet 的 "Deepfake" 欄位）
   但**無任何論文公開論證此設計**——本專案應誠實陳述此為已知但未經充分論證的協定。
5. RetouchingFFHQ／MoFRR（僅有的兩個美顏分類基準）皆用**多標籤×多強度**，
   與本專案完全相同的四種操作名稱——**單標籤封閉 4-class 是業界的異數**，
   佐證第 4 節提出的「改多標籤+強度迴歸」修法有明確文獻先例可依循。

## 2026-09-05 同協定外部對照（`EXTERNAL-BASELINES-20260905`）新增引用（權重來源見 `results/research/external_baselines_20260905/models.json`）
- Ojha, Li, Lee. *Towards Universal Fake Image Detectors that Generalize Across Generative Models* (UnivFD), CVPR 2023 — CLIP ViT-L/14 線性探針，ProGAN 訓練。
- Tan et al. *Rethinking the Up-Sampling Operations in CNN-based Generative Network for Generalizable Deepfake Detection* (NPR), CVPR 2024。
- Shiohara & Yamasaki. *Detecting Deepfakes with Self-Blended Images* (SBI), CVPR 2022 — EfficientNet-B4，FF++ c23。
- Yan et al. *DeepfakeBench: A Comprehensive Benchmark of Deepfake Detection*, NeurIPS 2023 D&B — 本輪 Xception／EfficientNet-B4／SPSL／F3Net／UCF／RECCE／CORE／SRM 權重來源（release v1.0.1，FF++ c23）。
- Liu et al. *Spatial-Phase Shallow Learning* (SPSL), CVPR 2021；Qian et al. *Thinking in Frequency* (F3Net), ECCV 2020；Yan et al. *UCF: Uncovering Common Features for Generalizable Deepfake Detection*, ICCV 2023；Cao et al. *End-to-End Reconstruction-Classification Learning* (RECCE), CVPR 2022；Ni et al. *CORE: Consistent Representation Learning*, CVPRW 2022；Luo et al. *Generalizing Face Forgery Detection with High-frequency Features* (SRM), CVPR 2021。
- 用途：P1/P2/P3 三協定同影像對照；**結論見 registry 條目，P3 為本專案唯一同協定全勝項，P2 全面落後**。
