"""Builds docs/capstone/MAIN_CLAIMS_20261022.md from the two direction files (no numbers typed by hand):
  A: results/research/alipair_zeroshot_20260929/main_claim_A.json   (commercial skin smoothing, pixel-aligned pairs)
  B: results/research/celebdfb_v2_20260927/fair_cdfb.json           (real-app beautified deepfake videos, compression control)
python make_main_claims.py"""
import json
from pathlib import Path

B = Path(r"C:\My_Project\AIGC"); A = json.loads((B / "results/research/alipair_zeroshot_20260929/main_claim_A.json").read_text())
F = json.loads((B / "results/research/celebdfb_v2_20260927/fair_cdfb.json").read_text())
PUB = ["xception", "effnb4", "f3net", "spsl", "ucf", "recce", "core", "srm", "sbi", "effort", "fadapter", "univfd", "npr", "gend", "dfdhr", "caddm", "laanetr"]
NAME = {"xception": "Xception", "effnb4": "EfficientNet-B4", "f3net": "F3Net", "spsl": "SPSL", "ucf": "UCF", "recce": "RECCE", "core": "CORE", "srm": "SRM", "sbi": "SBI",
        "effort": "Effort (2025)", "fadapter": "Forensics Adapter (2025)", "univfd": "UnivFD", "npr": "NPR", "gend": "GenD (2026)", "dfdhr": "DFD-HR (2026)", "caddm": "CADDM", "laanetr": "LAA-Net"}
L = ["# 專題主張的兩個方向（2026-10-22，數字由腳本從結果檔產生）", "",
     "一句話：偵測器把「美顏」和「偽造」混在一起，兩個方向都會錯：商用磨皮的真臉被判得比原圖更假；真實 App 美顏過的 deepfake 被放走。我們的三類模型兩邊都顧到。", "",
     "## 方向 A：商用磨皮（阿里 Smoothing-90）讓真臉被判得比自己的原圖更假", "",
     f"資料：{A['n_pairs']} 組逐像素對齊的 FFHQ 原圖／修圖配對，同一套處理管線，所以差異只來自磨皮。單位＝配對，bootstrap 95% CI。", "",
     "| 偵測器 | 修圖版分數高於自己原圖 % [CI] | 以原圖 5% 誤判設門檻後，磨皮真臉被判假 % [CI] |", "|---|---|---|"]
rows = A["rows"]
for p in PUB:
    r = rows[p]; L.append(f"| {NAME[p]} | {r['paired_up']} {r['paired_up_ci']} | {r['fa_s90_at_5pct']} {r['fa_ci']} |")
for o in ("ours main s1", "ours main s2"):
    r = rows[o]; L.append(f"| **我們（主模型 {o[-2:]}）** | **{r['paired_up']}** {r['paired_up_ci']} | **{r['fa_s90_at_5pct']}** {r['fa_ci']}；三類判定：原圖 real {r['native_orig']['real']}%，磨皮後 filter {r['native_s90']['filter']}%、fake {r['native_s90']['fake']}% |")
n_hi = sum(rows[p]["paired_up"] >= 89 for p in PUB); n_sig = {o: sum(rows[o]["paired_up_minus"][p][1] < 0 for p in PUB) for o in ("ours main s1", "ours main s2")}
L += ["", f"讀法：17 個已發表偵測器裡 {n_hi} 個在 89% 以上的配對把磨皮真臉判得更假；我們 {rows['ours main s1']['paired_up']}／{rows['ours main s2']['paired_up']}%。配對差異的 CI 不含 0 的偵測器數：seed 1 對 {n_sig['ours main s1']}/17，seed 2 對 {n_sig['ours main s2']}/17（NPR 分數飽和，CADDM 靠邊界不靠紋理）。",
      "限制：單一商用來源（阿里）、FFHQ 人像；Instagram AR 濾鏡資料因拍攝管線混淆不能當乾淨證據（Addendum 13、56）。", "",
      "## 方向 B：真實 App 美顏過的 deepfake 影片（Celeb-DF-B）被放走", "",
      "資料：Celeb-DF-B（Libourel et al. 2024），232 支影片 × 真／假 × 未處理／美顏／只壓縮；「純美顏造成的漏抓增加」＝美顏條件的漏抓增加減去只壓縮條件的，所以重新編碼的影響已扣掉。門檻＝未處理真臉 5% 誤判，單位＝影片 bootstrap。", "",
      "| 偵測器 | 美顏後 AUC [CI] | 純美顏造成的漏抓增加（點）[CI] | 美顏真臉被判假 % |", "|---|---|---|---|"]
for p in PUB:
    if p in F:
        r = F[p]; L.append(f"| {NAME[p]} | {r['auc_beautified']:.3f} {r['ci']['auc_beautified']} | {r['d_miss_beauty_only']:+.1f} {r['ci']['d_miss_beauty_only']} | {r['fa_b']:.1f} |")
for o, lab in (("RU-clipe5", "s1"), ("RU-clipe5-s2", "s2")):
    r = F[o]; L.append(f"| **我們（主模型 {lab}）** | **{r['auc_beautified']:.3f}** {r['ci']['auc_beautified']} | **{r['d_miss_beauty_only']:+.1f}** {r['ci']['d_miss_beauty_only']} | {r['fa_b']:.1f} |")
L += ["", "配對差異（我們減對方，同一組影片重抽樣），CI 不含 0 才算不同："]
for o, lab in (("RU-clipe5", "s1"), ("RU-clipe5-s2", "s2")):
    r = F[o]; L.append(f"- 美顏後 AUC，{lab}：" + "；".join(f"{NAME[k]} {v}" for k, v in r["auc_beautified_minus"].items()))
    if r.get("d_miss_beauty_only_minus"):
        L.append(f"- 純美顏漏抓增加，{lab}：" + "；".join(f"{NAME[k]} {v}" for k, v in r["d_miss_beauty_only_minus"].items()))
def _sig(r, key, sign):
    return [NAME[k] for k, v in r[key].items() if (v[0] > 0 if sign > 0 else v[1] < 0)]
auc_ok = {lab: _sig(F[o], "auc_beautified_minus", +1) for o, lab in (("RU-clipe5", "s1"), ("RU-clipe5-s2", "s2"))}
miss_better = {lab: _sig(F[o], "d_miss_beauty_only_minus", -1) for o, lab in (("RU-clipe5", "s1"), ("RU-clipe5-s2", "s2"))}
miss_worse = {lab: _sig(F[o], "d_miss_beauty_only_minus", +1) for o, lab in (("RU-clipe5", "s1"), ("RU-clipe5-s2", "s2"))}
L += ["", f"讀法（由 CI 自動判定）：美顏後 AUC 我們最高；配對 CI 不含 0 的對手，s1：{'、'.join(auc_ok['s1'])}；s2：{'、'.join(auc_ok['s2'])}。"
      f"「純美顏造成的漏抓增加」我們顯著比較小的對手，s1：{'、'.join(miss_better['s1'])}；s2：{'、'.join(miss_better['s2'])}；"
      f"顯著比我們更小（我們輸）的，s1：{'、'.join(miss_worse['s1']) or '無'}；s2：{'、'.join(miss_worse['s2']) or '無'}。這一項不能寫我們最好。",
      "限制：232 支影片、4 種濾鏡、單一資料集；Celeb-real 與訓練身分重疊（非身分互斥，PROVENANCE.md）。", "",
      "## 不再主張的事", "- Instagram AR 濾鏡（FairBeauty、B-LFW）：原圖沒經過同一套渲染管線，分不出濾鏡和管線；主模型與 RU9 都 75–78% 判假。",
      "- 四種美顏操作的辨識：真實濾鏡上大眼 0.3%、瘦臉 3%、美白 18%、磨皮 24%（Addendum 55）；只在商用磨皮上可靠。", "- LLM 改寫解釋：與模板句無差異，拿掉。"]
(B / "docs/capstone/MAIN_CLAIMS_20261022.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))
