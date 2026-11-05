# 旁白稿（zh-TW）

總長 4 分 13.3 秒；17 段真人錄音，0 段 zh-TW-HsiaoYuNeural（rate +3%）

錄音方式：每一段存成 `audio/rec/<id>.m4a`（或 wav／mp3），再跑 `python narration.py --no-tts`，有錄音的段落會用錄音，其餘用合成聲音。

## t1  00:00 – 00:10（旁白 8.7 s）

Beautified is not forged。這是我們的專題：一個分得出 beautification 和 forgery、而且 evidence 可以查核的 face checker。

## b1  00:10 – 00:21（旁白 10.2 s）

現在的 deepfake detector 被用在 content moderation、identity verification 和 fact-checking。可是大家上傳照片之前，常常先開美顏。

## b2  00:21 – 00:34（旁白 11.5 s）

問題就出在這裡。左邊是一張 real 的照片，經過 retouching service 最強的 smoothing 之後，四個 2025 年的 detector 全部把它從 real 判成 fake。

## b3  00:34 – 00:43（旁白 7.8 s）

右邊是一支 face swap 影片，套上手機 app 的 beauty preset 之後，同樣四個 detector 有三個讓它過關。

## b4  00:43 – 01:00（旁白 15.3 s）

我們把十七個已發表的 detector 用 official weights 全部重跑一次：十六個把 smoothing 過的 real 判得比原圖更 fake。原因很簡單，binary detector 只有 real 和 fake 兩個答案，沒有 beautified 這個選項。

## b5  01:00 – 01:08（旁白 5.7 s）

所以我們把 beautified 做成第三類，而且 model 指出的 evidence 要能驗證。

## m1  01:08 – 01:35（旁白 26.0 s）

先找原因。同一個 model、同一份 data，只改 training 時哪一類看過 smoothing。只給 fake 看，false alarm 升到 64%；只給 real 看，false alarm 降到 4%，但 smoothing 過的 face swap 會多漏掉五十幾個百分點；兩類都看，false alarm 降到 12%。關鍵在 training recipe。

## m2  01:35 – 01:58（旁白 21.6 s）

再來是 data。Commercial app 一次套好幾種美顏，又不會說改了哪裡。我們用 optical flow 把 shape 的變化拆成 eye 和 contour，剩下的 residual 用 low-pass 拆成 tone 和 texture，每個 component 都有精確的 footprint。一萬八千多張 render，變成五萬筆 single-operation 的訓練資料。

## m3  01:58 – 02:18（旁白 18.9 s）

Model 是凍結的 CLIP ViT-L/14，只訓練 LoRA 和四個 head，三百一十六萬個參數。Classification head 判三類，operation head 判四種操作，evidence head 輸出 16 乘 16 的 evidence map，直接用 footprint 監督。

## m4  02:18 – 02:28（旁白 8.7 s）

說明文字不用 language model。程式照 model output 組句，每一句顯示前都經過 rule checker，不符合的不會出現。

## r1  02:28 – 02:42（旁白 12.8 s）

成果。FF++ test set 上，real、forged、beautified 的 recall 是 82.7、90.9、86.7%，beautified 被判成 forged 的只有 4.3%。

## r2  02:42 – 03:01（旁白 17.4 s）

換到 training 完全沒看過的 Alibaba retouching service：smoothing 有 98.8% 判成 beautified，任何 operation、任何 strength 被判成 forged 都不到 1%。十四種 Instagram filter 也有 86% 以上判成 beautified。

## r3  03:01 – 03:18（旁白 15.8 s）

跟已發表的 detector 公平比較，只用一樣的 FF++ training videos。Celeb-DF-B beautification 之後的 AUC 0.872，高於所有已發表的方法；DFD 加十六種新 filter 也是最高。

## r4  03:18 – 03:40（旁白 20.1 s）

Evidence head 標的區域是不是真正的理由？把那個區域 restore 回原圖，94% 的 forged 判定會消失，heat map 只有一半。另外 VLM 寫的描述，blind matching 只有五成，跟丟銅板一樣，所以我們讓程式寫句子，361 張全部通過 checker。

## r5  03:40 – 03:56（旁白 15.3 s）

整套系統在 browser 裡跑：MediaPipe 找臉，ONNX Runtime 跑 EfficientNet-B4，程式畫出 evidence 輪廓、點名部位、組句、檢查。照片不會上傳，iPhone 上一張 0.59 秒。

## f1  03:56 – 04:08（旁白 10.2 s）

接下來：涵蓋 reenactment、降低原圖被判成 beautified 的比例、補強 monochrome filter，讓更多 operation 可以跨 service 點名。

## e1  04:08 – 04:13（旁白 3.3 s）

Beautified is not forged。謝謝。
