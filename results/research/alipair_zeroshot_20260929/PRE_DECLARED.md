# ALIPAIR-ZEROSHOT-20260929 — FF++-only 三類模型在阿里巴巴商用修圖配對上的零樣本表現

**目的（診斷，不選模型）**：新論文線（FF++ c23 only）的所有 filter 數字都來自自建腳本濾鏡。這一輪量它們在
**真實商用美顏演算法**（Alibaba，4 型別 × 3 強度）上是否有訊號，決定下一階段研究（還原式解釋／商用美顏泛化）的起點。

**資料**：`ffhq_originals/Part2/*.png`（2,210 張 FFHQ 原圖，index 17001–19999）與 `FFHQ_ali_process/{EyeEnlarging,FaceLifting,Smoothing,Whitening}_{30,60,90}/<千位>/<index>.png`
按 index 配對。新線模型從未看過 FFHQ 或 Alibaba 任何影像（FF++ c23 only），因此 2,210 組全部可用；另報排除
`retouching_benchmark_20260823` 鎖定的 440 張負類後的數字作為對照。

**前處理**：與 FF++ 訓練相同的裁切（MediaPipe landmark hull，每邊 35% margin，`extract_ffpp_protocol_frames.detect_and_crop` 同式），
裁切框**由原圖計算、原圖與修圖版共用**（像素對齊配對，不讓裁切差異混入）。原生解析度裁切後直接交給模型的 Resize。

**模型**：HYB（sbiscale s2）、HYB-F、HYB-D、SUP-F、MASK（evidence head）、RepViT（ours-S）。全部 argmax 原生規則，無門檻調整。

**指標**（與 `retouching_benchmark_20260823` 同定義，方便對照 v8.17）：
- 原圖路由（real/fake/filter %）；specificity = 原圖**未**被判 filter 的比例
- 修圖版路由；balanced accuracy（filter vs 非 filter）= (修圖判 filter% + 原圖未判 filter%) / 2
- 配對排序率 = P(p_filter(修圖) > p_filter(原圖))，平手 0.5
- 配對超額 = 修圖判 filter% − 原圖判 filter%
- 修圖版被判 fake 的比例（誣告）

**判讀規則（事前）**：v8.17 基準 balanced 50.7–51.2%、配對排序 62.6–66.1%。
- 新線最佳模型 balanced ≥ 65% 且配對排序 ≥ 75% ⇒ 已有可用訊號，下一階段從「提升」出發；
- balanced < 60% ⇒ 與 v8.17 同屬機率水準，下一階段必須先解決商用美顏泛化本身。
不用這一輪的結果挑任何模型或門檻。
