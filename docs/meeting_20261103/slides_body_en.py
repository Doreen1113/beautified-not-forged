# ============================================================================ English slides of the final meeting deck (2026-11-03)
# Same slides, numbers and figures as slides_body.py, slide text in English; speaker notes in Chinese (same text as
# slides_body.py). assemble.py en prepends the deck helpers of slides_body.py (everything before "NOTES = []").
# Numbers: docs/capstone/report_v3/report.tex and its SOURCES.md.
NOTES = []

# ============================================================================ 1 title
s = prs.slides.add_slide(BLANK)
pill(s, -1.2, 0.9, 10.2, 4.8); square(s, 8.75, 0.75); square(s, 0.55, 5.95)
text(s, 0.9, 1.6, 8.0, 1.0, "Beautified Is Not Forged", size=40, font=SERIF, bold=True)
text(s, 0.9, 2.55, 7.7, 1.0, "A face detector that tells beautification from forgery, with checkable evidence", size=19, font=SERIF, color=MUTED)
text(s, 0.9, 3.85, 7.6, 0.4, "Capstone project results  ·  3 November 2026", size=15)
text(s, 0.9, 4.35, 7.6, 0.4, "林沁瑩  陳柏蓉  余晨杉", size=15)
text(s, 9.3, 6.2, 3.6, 0.6, "Advisor: Prof. Shang-Hong Lai", size=12, color=MUTED, italic=True, align=PP_ALIGN.RIGHT)
number(s)
NOTES.append("老師好，這是我們專題的成果報告。主題是：美顏過的照片不是偽造。我們依序講問題、成因、方法，"
             "然後是各種測試的成績：三類測試、各種修圖類型、沒見過的修圖服務、不同資料集，最後是可解釋性和手機上的系統。")

# ============================================================================ 2 problem
s = content("Problem", "A beautified photo is neither real nor fake for a binary detector")
_, _, pw, ph = mine(s, "teaser", 0.6, 1.45, 8.5, 4.3)
caption(s, 0.6, 1.5 + ph + 0.05, 8.5, "(a) FFHQ original vs Alibaba Smoothing-90; (b) Celeb-DF face swap vs app beauty preset (Celeb-DF-B). "
        "Black ticks: each detector's threshold at 5% false alarms.")
callout(s, 9.4, 1.5, 3.35, 1.75, "After commercial skin smoothing, four 2025 detectors all flip a genuine photo from real to forged",
        head="False alarm", size=14)
callout(s, 9.4, 3.4, 3.35, 1.6, "After an app beauty preset, three of the same four detectors let a face-swap video through", bg=AMBER_BG, color=AMBER,
        head="Miss", size=14)
text(s, 9.4, 5.2, 3.35, 1.0, "Detectors serve content moderation, remote identity checks and fact-checking; photos are often beautified before upload.",
     size=13, color=MUTED)
text(s, 0.6, 6.25, 12.1, 0.5, "One edit, two errors: a binary detector has no “beautified” answer, so it must force the photo into real or fake.",
     size=17, bold=True)
NOTES.append("問題是這樣：偽造偵測器被用在內容審核、遠端身分驗證和事實查核，但照片上傳前常常先經過美顏。左邊是一張真人照片，經過商用修圖的最強磨皮後，"
             "四個 2025 年的偵測器全部從真變偽造，這是冤枉。右邊是一支換臉影片，套上手機 app 的美顏後，同樣四個偵測器裡有三個讓它通過，這是漏抓。"
             "原因是二分類偵測器只有 real 和 fake，美顏過的真人兩者都不是。")

# ============================================================================ 3 prior work and the gap
s = content("Related work", "What prior work found, what it left open, and what we do")
rows = [["Prior work", "Finding", "Left open"],
        ["Libourel et al., IWBF 2024 (Celeb-DF-B)", "App beautification lowers video AUC: CADDM 0.91→0.76, RECCE 0.81→0.66, FTCN 0.80→0.64",
         "“Strongly recommends” dedicated filter detection, but does not build or test it"],
        ["Saeed et al., BMVC-W 2025", "Facial enhancement lets face swaps evade detection; adversarial training on one enhancement fails on another",
         "Measures misses only, not false alarms"],
        ["Concas et al., MetroXRAINE 2025", "One beauty filter raises EER on CelebDF (AlexNet 22.3→28.1%, VGG19 30.2→35.2%)", "One filter, two CNNs"],
        ["RetouchingFFHQ, ACM MM 2023", "Large-scale retouching data; detects retouching operations on genuine photos",
         "No forgery class: cannot say whether a retouched face is also forged"],
        ["ForgeryNet, CVPR 2021", "Multi-class forgery analysis benchmark", "Identity-preserving edits still labelled fake"],
        ["Grad-CAM; FakeVLM 2025", "Post-hoc heat maps; vision-language models write free-text explanations",
         "Heat maps are not trained to mark the edit; the text is not tested"]]
gf = table(s, rows, 0.6, 1.4, [3.3, 5.3, 3.55], row_h=0.58, size=12, align="lll")
for r in range(1, 7):
    gf.table.cell(r, 2).text_frame.paragraphs[0].runs[0].font.color.rgb = RED
steps = [("1  Measure both directions", "17 detectors, pixel-aligned pairs", BLUE, NOTE_BG),
         ("2  Find the cause", "Controlled experiment: change only which class sees smoothing", GREEN, GREEN_BG),
         ("3  Build the beautified class", "Three-class model + evidence head + checked sentences", PURPLE, PURPLE_BG)]
for k, (h, b, c, bg) in enumerate(steps):
    callout(s, 0.6 + k * 4.08, 5.75, 3.95, 1.1, b, bg=bg, color=c, head=h, size=14)
NOTES.append("別人怎麼處理這個問題？Libourel 等人 2024 年做了 Celeb-DF-B，發現 app 美顏讓偵測器的 AUC 掉 0.15 左右，結論是強烈建議要有專門的濾鏡偵測，"
             "但他們沒有做。Saeed 等人只量了換臉逃過偵測這一邊，而且發現對一種美顏做對抗訓練，換一種就沒用。Concas 等人只用一個濾鏡、兩個 CNN。"
             "RetouchingFFHQ 這類修圖偵測沒有偽造類；ForgeryNet 有多類別，但保留身分的編輯還是算 fake。解釋方面，熱圖是事後算的，VLM 的文字沒有被檢驗。"
             "所以我們做三件事：第一，在像素對齊的配對上同時量兩個方向；第二，用控制實驗找成因；第三，把 Libourel 建議的美顏類別真的做出來，而且證據和句子都經過檢驗。")

# ============================================================================ 4 audit
s = content("Audit", "16 of 17 published detectors accuse a smoothed genuine face")
mine(s, "twoaxis", 0.6, 1.4, 6.4, 5.4, align="left")
for i, (big, lab) in enumerate([("15 / 17", "score the smoothed genuine face as more fake than its original in 89–99% of pairs"),
                                ("13 / 17", "call 36–69% of smoothed genuine faces fake at their own threshold"),
                                ("14 / 17", "miss 3–22 points more face-swap videos after app beautification (re-encoding removed)")]):
    stat(s, 7.5, 1.45 + i * 1.45, 5.2, big, lab, big_size=36, h_big=0.65, label_h=0.6)
callout(s, 7.5, 5.85, 5.25, 0.95, "Our model (star) sits in the lower left: no published detector is lower on both axes.", bg=NOTE_BG,
        color=BLUE, size=14)
NOTES.append("我們把 17 個已發表的偵測器用各自的官方權重和前處理重跑。左圖橫軸是冤枉、縱軸是漏抓，越靠左下越好。"
             "15 個在 89 到 99% 的配對裡把磨皮的真人判得比原圖更假，13 個在自己的門檻下把三到七成的磨皮真人判成 fake，"
             "影片上 14 個的漏抓增加 3 到 22 點。我們的模型是星號，兩個方向都在左下角。")

# ============================================================================ 5 cause
s = content("Cause", "Which class saw smoothing in training decides the error")
mine(s, "exposure", 0.6, 1.45, 8.3, 4.5)
rows = [("P0", "No beautification", "accused 43.5–56.1%", MUTED), ("P3", "Forged class only", "accused 63.8%", RED),
        ("P1", "Real class only", "accused ≈ 1%, misses +51–63", AMBER), ("P2", "Both classes", "accused 6.9–11.7%", GREEN)]
for i, (k, a, b, c) in enumerate(rows):
    y = 1.5 + i * 0.98
    box(s, 9.2, y, 3.55, 0.86, WHITE, radius=0.12, line=RGBColor(0xD6, 0xDB, 0xE3))
    text(s, 9.38, y + 0.1, 0.6, 0.66, k, size=20, font=SERIF, bold=True, color=c, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 10.0, y + 0.08, 2.65, 0.72, [[(a, {"bold": True})], [(b, {"color": c})]], size=14)
callout(s, 0.6, 6.05, 12.15, 0.8, "With architecture, data and recipe fixed, which class saw smoothing decides the false alarms: the fix is the training recipe.",
        bg=GREEN_BG, color=GREEN, head="Finding  ", size=15)
NOTES.append("這是找原因的控制實驗。同一個 CLIP 模型、同一份 FF++ 資料、同一個配方，只改訓練時哪一類看過磨皮。"
             "只給偽造類看，冤枉衝到 64%；只給真人類看，冤枉降到 1%，可是磨皮過的換臉就漏抓多五六十點；兩類都看，冤枉降到 7 到 12%。"
             "所以問題出在訓練曝露，解法就是訓練配方。")

# ============================================================================ 6 method overview
s = content("Method", "Paired edits with exact footprints, one backbone, four heads")
mine(s, "overview", 0.6, 1.35, 8.95, 5.7, align="left")
for i, (head, msg, c, bg) in enumerate([("Exact footprints", "Every edited image has a pixel-aligned original, so the edit region M is known", BLUE, NOTE_BG),
                                        ("Both classes see beauty", "Half of the forged samples are also beautified, so smoothing is not a forgery cue", GREEN, GREEN_BG),
                                        ("Evidence head is tested", "The classifier does not read the map; a restoration test checks it is the reason", PURPLE, PURPLE_BG)]):
    callout(s, 9.8, 1.5 + i * 1.82, 2.95, 1.65, msg, bg=bg, color=c, head=head, size=13)
NOTES.append("這頁是整個方法的總覽，後面兩頁再分別放大資料和模型。"
             "第一區是訓練資料，共三種，共同點是每一張編輯過的圖都有像素對齊的原圖，所以改了哪些像素是確定的，我們叫它 footprint M。"
             "第一列是 FF++ 的真人和換臉影格，兩類都會被套上美顏，共 41,512 張，這就是上一頁實驗裡兩類都看過磨皮的做法。"
             "第二列是商用修圖：一張騰訊或曠視的修圖被拆成大眼、輪廓、色調、紋理四個單一操作，共 50,112 筆，下一頁會講怎麼拆。"
             "第三列是部位偽造：只把鼻子這類部位換成別人的，其餘像素完全不動，所以藍色的 footprint就是被改的地方，共 61,510 張。"
             "第二區是模型：一個凍結的 CLIP ViT-L/14，只在 24 層加 LoRA，總共 3 億多參數裡只訓練 320 萬。"
             "上面接四個 head：classification head 給 forged 和 beautified 兩個分數，forged 的判定只看 forged 分數，美顏分數再高也搶不走，所以美顏過的換臉還是會被判偽造；"
             "operation head 給四個操作分數；quantity head 輸出四個修圖量做輔助；evidence head 輸出 16×16 的 evidence map，用 footprint M 直接監督。"
             "第三區是在沒看過的圖上的實際輸出：上面是鼻子被換掉的偽造，判 forged 1.00，證據落在鼻子；"
             "下面是訓練沒用過的修圖服務做的大眼，判 beautified 0.98，證據落在眼睛。"
             "最下面那段文字是程式根據模型輸出組出來、檢查過才顯示的解釋。"
             "第四區是三個可能推翻我們的測試，及格標準都是事先寫好的："
             "訓練曝露讓冤枉從 54% 降到 12%；把證據標出的區域還原，94% 的偽造判定消失，熱圖只有 45 到 57%；"
             "視覺語言模型的自由描述盲配對只有 51 到 53%，跟擲硬幣一樣，所以每一句都改由程式寫。"
             "第五區是部署：在 iPhone 瀏覽器上一張 0.59 秒，照片不上傳。"
             "右邊三個重點：footprint 是精確的、兩類都看美顏、evidence head 有被檢驗。")

# ============================================================================ 7 data engine
s = content("Method · data", "A commercial render, split into single operations with exact footprints")
_, _, pw, ph = mine(s, "engine", 0.6, 1.35, 12.1, 5.25)
caption(s, 0.6, 1.4 + ph + 0.05, 12.1, "Tencent render (FFHQ 60002; whitening, smoothing, slimming and eye enlarging in one pass): optical flow f splits "
        "the geometry, the residual P splits tone and texture. 18,734 renders → 50,112 single operations.", align=PP_ALIGN.CENTER)
NOTES.append("這是資料引擎，是我們最原創的部分。商用 app 一次套好幾種美顏，也不告訴你改了哪裡。我們用光流把形狀的變化拆成眼睛和輪廓，"
             "光流解釋不了的殘差再用低通拆成色調和紋理。四個分量合起來重建誤差 108 dB，每個分量都有自己的 footprint。"
             "騰訊和曠視 18,734 張修圖變成 50,112 筆單一操作的訓練資料；阿里完全不拆，只拿來測試。")

# ============================================================================ 8 model
s = content("Method · model", "CLIP ViT-L/14 with LoRA; the evidence head learns the exact footprint")
_, _, pw, ph = mine(s, "model", 0.6, 1.35, 12.1, 5.25)
caption(s, 0.6, 1.4 + ph + 0.05, 12.1, "303.2 M frozen, 3.16 M trained (96 LoRA adapters + four heads); P(forged) = σ(f): the forgery score does not "
        "read the beauty score b.", align=PP_ALIGN.CENTER)
NOTES.append("這頁放大模型。Backbone 是 CLIP ViT-L/14，24 個 Transformer block 全部凍結，只在每層 attention 加 rank 16 的 LoRA，"
             "總共只訓練 316 萬個參數，大約是全部的 1%。輸出分兩路。CLS token 接三個 head：classification head 給 forged 和 beautified 兩個分數，"
             "forged 的判定只看 forged 分數，美顏分數再高也搶不走；operation head 給四個操作分數；quantity head 只用來輔助訓練。"
             "256 個 patch token 接 evidence head，輸出 16×16 的 evidence map，直接用 footprint M 監督。"
             "網頁再把 evidence map 對到臉部部位，點名最強的那一個，這個例子是 nose。")

# ============================================================================ 9 three-class on FF++ test
s = content("Results · three-class", "Three-class test on FF++: 82.7 / 90.9 / 86.7% recall")
heat_matrix(s, 0.6, 1.85, 1.45, [[1088, 78, 150], [352, 4819, 133], [118, 57, 1141]], ["real", "forged", "beautified"])
text(s, 0.6, 6.45, 5.8, 0.4, "FF++ c23 test: 7,936 frames, 140 videos, unused in training and selection; main model, seed 1.", size=12,
     color=MUTED, italic=True)
text(s, 6.95, 1.45, 5.8, 0.4, "Share called forged per face-swap method (%)", size=16, bold=True, color=BLUE)
bar_chart(s, 6.85, 1.85, 5.9, 2.1, ["Deepfakes", "FaceSwap", "Face2Face", "NeuralTextures"], [98.64, 96.22, 93.51, 75.08],
          [RED, RED, RED, AMBER], size=13)
text(s, 6.95, 4.25, 5.8, 0.4, "Where the errors go", size=16, bold=True, color=BLUE)
text(s, 6.95, 4.7, 5.8, 1.7, [[("real → beautified 11.4%, real → forged 5.9%", {})],
                              [("beautified → real 9.0%, beautified → forged 4.3%", {})],
                              [("Most errors fall between real and beautified; beautified is rarely called forged", {"bold": True})]],
     size=15, spacing=6)
NOTES.append("三類測試的成績：FF++ 測試集 7,936 張，訓練和挑模型都沒用過。真實 82.7%、偽造 90.9%、美顏 86.7%。"
             "右邊是四種換臉方法：Deepfakes 98.6%、FaceSwap 96.2%、Face2Face 93.5%，NeuralTextures 只改嘴部紋理，比較難，75%。"
             "錯誤的方向多半是真人和美顏互相混淆，美顏被判成偽造只有 4.3%。")

# ============================================================================ 10 per filter type (FF++ test)
s = content("Results · filter types", "Each beauty operation and filter type is called “beautified”, not “forged”")
cats = ["skin smoothing", "face slimming", "whitening", "eye enlarging",
        "brannan", "toaster", "valencia", "nashville", "hudson", "xpro2", "walden", "rise", "gingham", "stinson", "willow",
        "lark", "aden", "maven"]
vals = [94.23, 86.0, 81.88, 49.34, 100.0, 97.96, 97.1, 96.92, 96.55, 96.3, 95.65, 95.35, 94.44, 93.75, 91.49, 87.72, 86.67, 86.05]
bar_chart(s, 0.5, 1.35, 7.4, 5.6, cats, vals, [AMBER] * 4 + [PURPLE] * 14, size=12)
text(s, 8.3, 1.5, 4.5, 0.4, "Share called beautified (%)", size=16, bold=True, color=BLUE)
text(s, 8.3, 1.95, 4.45, 1.0, [[("■ ", {"color": AMBER}), ("4 beauty operations (smoothing, slimming, whitening, eyes)", {})],
                              [("■ ", {"color": PURPLE}), ("14 Instagram-style filters", {})]], size=14, spacing=4)
stat(s, 8.3, 3.1, 4.4, "≤ 10.7%", "called forged, for any type (highest: whitening)", big_size=34, h_big=0.65, label_h=0.6)
stat(s, 8.3, 4.5, 4.4, "86–100%", "of each Instagram filter called beautified", big_size=34, h_big=0.65, label_h=0.6)
caption(s, 8.3, 5.9, 4.4, "Applied to FF++ test videos (unseen in training); eye enlarging is hardest (49.3%, most of the rest called real). "
        "Unseen filters: slides 12–13.", h=0.7)
NOTES.append("各種修圖類型的成績：在 FF++ 測試影片上套用四種美顏操作和 14 種 Instagram 風格濾鏡。磨皮 94%、瘦臉 86%、美白 82% 判成美顏；"
             "大眼最難，一半判美顏、其餘多判真實。14 種濾鏡 86 到 100% 判美顏。任何一種被判成偽造的比例都不超過 11%。")

# ============================================================================ 11 unseen commercial service, per operation and strength
s = content("Results · unseen service", "Alibaba, a retouching service never used in training")
rows = [["Operation", "beautified, 30", "60", "90", "forged (max)", "above own original"],
        ["Skin smoothing", "90.5", "99.0", "98.8", "0.8", "97.6–99.4"],
        ["Whitening", "51.5", "63.6", "72.3", "0.8", "85.4–92.2"],
        ["Eye enlarging", "46.5", "59.8", "69.7", "0.5", "92.4–97.6"],
        ["Face slimming", "46.1", "53.7", "61.3", "0.4", "84.1–93.7"],
        ["Untouched original", "20.8", "", "", "0.8", "real 78.4"]]
gf = table(s, rows, 0.6, 1.55, [2.45, 1.6, 0.8, 0.8, 1.45, 1.95], row_h=0.58, size=15)
table_marks(gf, bold=[(1, 1), (1, 2), (1, 3)])
caption(s, 0.6, 5.2, 9.05, "2,210 pairs of FFHQ originals and Alibaba renders at strength 30 / 60 / 90 (%). Above own original: share of pairs "
        "in which the render's beautified score exceeds that of its own original.", h=0.6)
stat(s, 9.95, 1.5, 2.85, "98.8%", "commercial smoothing called beautified", big_size=40, h_big=0.75, label_h=0.45)
stat(s, 9.95, 2.9, 2.85, "≤ 0.8%", "called forged, any operation and strength", big_size=40, h_big=0.75, label_h=0.7)
stat(s, 9.95, 4.55, 2.85, "84–99%", "of pairs: each operation scores above its own original", big_size=34, h_big=0.7, label_h=0.7)
NOTES.append("這是訓練完全沒見過的修圖服務阿里，四種操作、三種強度各 2,210 對。磨皮強度 60 以上 99% 判美顏；美白、大眼、瘦臉強度越高越容易判美顏。"
             "關鍵是任何操作、任何強度被判成偽造都不超過 0.8%。而且和自己的原圖比，修過的那張美顏分數比較高的比例是 84 到 99%，"
             "也就是模型看得出改變，只是弱的修圖在絕對門檻上會判成真實。")

# ============================================================================ 12 across datasets and filter sources
s = content("Results · cross-dataset", "Across datasets and filters, with the same training data as the baselines")
rows = [["Test set", "Filter source", "Ours, FF++ only", "Ours, full data", "Best published"],
        ["Celeb-DF-B", "4 app beauty presets", "0.872 / 0.870", "0.866 / 0.883", "0.838 DFD-HR"],
        ["Celeb-DF-v2", "11 held-out filters", "0.851", "0.873 / 0.875", "0.856 GenD"],
        ["DFD", "16 fresh filters", "0.932", "0.931 / 0.931", "0.928 DFD-HR"],
        ["Celeb-DF-v2", "GPUPixel engine, accused %", "--", "13.7 / 13.1", "14 of 15 > 15"],
        ["FFHQ pairs", "Alibaba S-90, accused %", "--", "8.6 / 12.5", "6.3 CADDM"]]
gf = table(s, rows, 0.6, 1.45, [1.55, 2.6, 1.65, 1.65, 1.6], row_h=0.5, size=13)
table_marks(gf, bold=[(1, 2), (2, 3), (3, 2), (4, 3), (5, 4)])
caption(s, 0.6, 4.55, 9.05, "Top three rows: AUC after beautification or filtering (higher is better); bottom two: accusation rate (lower is "
        "better). Bold = best in the row. FF++ only: the FF++ c23 training videos of Effort, Forensics Adapter, GenD and DFD-HR, no "
        "commercial renders or part edits (--: no such training data, not reported).", h=0.75)
callout(s, 0.6, 5.4, 9.05, 1.4, "Trained on FF++ only: Celeb-DF-B AUC 0.872 after beautification, above every published detector; paired 95% "
        "intervals against Effort, Forensics Adapter and SBI all above 0. With the full data, the paired intervals against the six "
        "strongest detectors are also all above 0.", bg=GREEN_BG, color=GREEN, head="Fair comparison (same training data)", size=14)
text(s, 9.95, 1.45, 2.9, 0.4, "Celeb-DF-B decisions (%)", size=15, bold=True, color=BLUE)
stacked_chart(s, 9.8, 1.8, 3.0, 4.95, ["genuine", "genuine + beauty", "deepfake", "deepfake + beauty"],
              [("real", [70.8, 30.5, 8.3, 5.4]), ("forged", [16.0, 22.1, 88.0, 78.0]), ("beautified", [13.2, 47.4, 3.6, 16.6])],
              [GREEN, RED, AMBER], size=11)
NOTES.append("這頁是公平比較。第三欄是只用 FF++ 訓練的版本，訓練影片跟 Effort、Forensics Adapter、GenD、DFD-HR 完全一樣，沒有用商用修圖和部位偽造。"
             "它在 Celeb-DF-B 美顏後 AUC 0.872，高於所有已發表偵測器，而且跟 Effort、Forensics Adapter、SBI 的配對信賴區間都大於 0；DFD 加 16 種新濾鏡也是最高。"
             "所以優勢來自配方，不是資料量。第四欄是完整資料的系統版本，當成系統能做到多好的參考。右邊是 Celeb-DF-B 上的三類判定。")

# ============================================================================ 12b per held-out filter
import json as _json
PF = _json.loads((H / "per_filter_auc.json").read_text(encoding="utf-8"))
COLS = ["Ours s1", "Ours s2", "Effort", "Forensics Adapter", "GenD", "DFD-HR"]
HEAD = ["Filter", "Ours s1", "Ours s2", "Effort", "FA", "GenD", "DFD-HR"]
MONO = {"inkwell", "moon", "grayscale"}
s = content("Results · per filter", "Each held-out filter: AUC after filtering")


def filter_table(ds, x, title):
    fl = [k for k in PF[ds]["Ours s1"] if k != "all"] + ["all"]
    rows = [HEAD]
    for k in fl:
        rows.append([("pooled" if k == "all" else k)] + [f"{PF[ds][c][k]['auc_f']:.3f}" for c in COLS])
    text(s, x, 1.35, 6.0, 0.35, title, size=15, bold=True, color=BLUE)
    gf = table(s, rows, x, 1.75, [1.3, 0.78, 0.78, 0.78, 0.78, 0.78, 0.8], row_h=0.255, size=11)
    marks = []
    for r, k in enumerate(fl, start=1):
        vals = [PF[ds][c][k]["auc_f"] for c in COLS]; best = max(vals)
        marks += [(r, 1 + j) for j, v in enumerate(vals) if v == best]
        if k in MONO:
            for c in range(7):
                gf.table.cell(r, c).text_frame.paragraphs[0].runs[0].font.color.rgb = RED
        if k == "all":
            gf.table.cell(r, 0).text_frame.paragraphs[0].runs[0].font.bold = True
    table_marks(gf, bold=marks)
    wins = sum(max(PF[ds]["Ours s1"][k]["auc_f"], PF[ds]["Ours s2"][k]["auc_f"]) >
               max(PF[ds][c][k]["auc_f"] for c in COLS[2:]) for k in fl if k != "all")
    return wins, len(fl) - 1


w1, n1 = filter_table("cdf", 0.6, "Celeb-DF-v2 + 11 held-out filters")
w2, n2 = filter_table("dfd", 6.95, "DFD + 16 fresh filters")
caption(s, 0.6, 6.5, 12.1, f"Bold = highest in the row. Pooled, ours is highest; filter by filter we win {w1}/{n1} (Celeb-DF-v2) and {w2}/{n2} "
        "(DFD). Red = monochrome filters (inkwell, moon, grayscale), our weakest group. Frame AUC per filter, from existing scores.", h=0.6)
NOTES.append(f"這頁把上一頁合併的濾鏡成績拆開來看，每一列是一種訓練沒見過的濾鏡，數字是套上濾鏡後的 AUC，粗體是該列最高。合併起來我們最高，"
             f"但逐一看並不是每一種都贏：Celeb-DF-v2 的 11 種贏 {w1} 種，DFD 的 16 種贏 {w2} 種。最明顯的弱點是黑白濾鏡，inkwell、moon、grayscale 三種"
             "我們都輸，這是目前看到最一致的弱點，原因還沒有做實驗分析。")

# ============================================================================ 13 explainability
s = content("Explainability", "The marked region is the reason, and code writes every sentence")
_, _, pw1, ph1 = mine(s, "evidence", 0.6, 1.45, 6.0, 3.2, align="left")
_, _, pw2, ph2 = mine(s, "explain", 6.85, 1.45, 5.9, 3.2, align="left")
y2 = 1.5 + max(ph1, ph2) + 0.2
stat(s, 0.6, y2, 2.9, "94%", "of forged decisions removed by restoring the marked part (ceiling 94.1%)", big_size=40, h_big=0.75, label_h=0.75)
stat(s, 3.6, y2, 2.9, "51%", "with Grad-CAM (Score-CAM 57%)", color=MUTED, big_size=40, h_big=0.75, label_h=0.75)
stat(s, 6.85, y2, 2.9, "51–53%", "blind matching of VLM free-text descriptions (chance 50%)", color=RED, big_size=36, h_big=0.75, label_h=0.75)
stat(s, 9.85, y2, 2.9, "361 / 361", "code-composed sentences on the holdout pass six rules", color=GREEN, big_size=34, h_big=0.75, label_h=0.75)
NOTES.append("可解釋性有兩個測試。左邊：把 evidence head 標的區域換回原圖，94% 的偽造判定消失，跟上限只差 0.1；熱圖只有一半左右，所以 evidence head 標的就是理由。"
             "右邊：視覺語言模型的自由描述，盲配對回原照片只有 51 到 53%，跟擲硬幣一樣，所以我們讓程式根據模型輸出組句，"
             "每一句出貨前都由規則檢查器對照，361 張 holdout 全部通過。")

# ============================================================================ 14 system
s = content("System", "The browser page: 0.59 s per photo on an iPhone, nothing uploaded")
_, _, pw, ph = mine(s, "screenshot", 0.6, 1.45, 8.0, 4.85, align="left")
caption(s, 0.6, 1.5 + ph + 0.05, 8.0, "Example: FF++ test frame with the mouth replaced by another person's (part-level forgery). Yellow = strongest "
        "12% of the evidence; cyan = evidence score 0.5 or more; named part: mouth.")
stat(s, 9.0, 1.45, 3.8, "0.59 s", "iPhone Safari median (P90 0.79 s)", big_size=40, h_big=0.75, label_h=0.4)
stat(s, 9.0, 2.75, 3.8, "0.51 s", "desktop (one WebAssembly thread)", big_size=40, h_big=0.75, label_h=0.4)
stat(s, 9.0, 4.05, 3.8, "95.7%", "everyday photos (FairFace) called real", big_size=40, h_big=0.75, label_h=0.4)
text(s, 9.0, 5.45, 3.8, 0.9, "MediaPipe finds the face → ONNX Runtime Web runs EfficientNet-B4 (67 MB) → code draws the outline, names the part, "
     "composes and checks the sentences", size=13)
NOTES.append("系統：整條流程在瀏覽器裡跑，MediaPipe 找臉、ONNX Runtime 跑 67 MB 的 EfficientNet-B4、程式畫出證據輪廓並組句，照片不上傳。"
             "iPhone 上一張 0.59 秒，桌機 0.51 秒；一般網路照片 FairFace 有 95.7% 判真實。"
             "截圖是網頁內建的範例 2：FF++ 測試影格只把嘴巴換成別人的，證據輪廓和點名部位都落在嘴巴上。這是挑來展示輪廓的例子，整體效果看上一頁還原測試的 94%。")

# ============================================================================ 15 conclusion
s = content("Conclusion", "Results and limitations")
cards = [("16 / 17", "published detectors score a smoothed genuine face as more fake", "both directions, 17 detectors"),
         ("54% → 12%", "false alarms: the cause is which class saw smoothing", "controlled, same model and data"),
         ("94% vs 51%", "restoring the marked part removes the forged decision", "Grad-CAM heat map: 51%"),
         ("0.59 s", "per photo in an iPhone browser", "nothing uploaded")]
for i, (big, lab, sub) in enumerate(cards):
    card(s, 0.6 + i * 3.06, 1.45, 2.9, 2.7, big, lab, sub, big_size=30 if len(big) > 7 else 38)
text(s, 0.6, 4.4, 12.1, 0.4, "Limitations", size=17, font=SERIF, bold=True)
lims = [("Reenactment", "DF40 reenactment AUC 0.50 / 0.56, outside the training coverage"),
        ("Originals", "20.8% / 19.6% of untouched FFHQ originals called beautified"),
        ("Beauty + swap", "10.9 / 9.8 points of face-swap videos land in beautified; the page always shows the fake score"),
        ("Named operations", "across services only smoothing is reliable (AUROC 0.999), others 0.69–0.72; monochrome filters are weakest")]
for k, (h, b) in enumerate(lims):
    x = 0.6 + (k % 2) * 6.1; y = 4.9 + (k // 2) * 0.95
    box(s, x, y, 5.9, 0.82, GREY_BG, radius=0.12)
    text(s, x + 0.25, y + 0.1, 5.5, 0.62, [[(h + "  ", {"bold": True}), (b, {})]], size=13, anchor=MSO_ANCHOR.MIDDLE)
NOTES.append("總結：第一，16/17 個已發表偵測器會冤枉磨皮的真人；第二，我們找出成因是訓練曝露，只改哪一類看過磨皮，冤枉從 54% 降到 12%；"
             "第三，evidence head 標的區域是判定的真正理由；第四，整套在 iPhone 瀏覽器 0.59 秒跑完。限制是重演類偽造不在涵蓋內、兩成原圖會被判美顏、"
             "一部分美顏換臉會落到美顏類所以頁面一律顯示偽造分數、跨廠牌只有磨皮能可靠點名。以上是我們的成果，謝謝老師。")

# ---------------------------------------------------------------------------- notes, save
assert len(NOTES) == len(prs.slides) == 16, (len(NOTES), len(prs.slides))
for sl, note in zip(prs.slides, NOTES):
    sl.notes_slide.notes_text_frame.text = note
out = H / "final_meeting_20261103_en.pptx"
prs.save(out)
print("saved", out, len(prs.slides), "slides (speaker notes in Chinese: speaker_notes_zh.md)")
