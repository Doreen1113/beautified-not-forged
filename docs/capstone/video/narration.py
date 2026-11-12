"""Narration of the capstone video (Chinese, zh-TW): the beats, their text, the audio and the timeline.

Every beat is one narration cue. Its audio is either a recording (audio/rec/<id>.wav|.m4a|.mp3, a team member reading the
beat; any format ffmpeg decodes) or, when there is none, Microsoft's neural voice through edge-tts (free, online). The
timeline is derived from the real audio durations, so the picture never runs ahead of the voice: a beat lasts
max(audio + TAIL, min).

python docs/capstone/video/narration.py                     -> audio/<id>.mp3 (TTS for beats without a recording),
                                                               audio/narration.wav, cues.js / cues.json, subtitles.srt,
                                                               narration_script.md
python docs/capstone/video/narration.py --no-tts            -> rebuild the timeline from the audio files already there
python docs/capstone/video/narration.py --voice zh-TW-HsiaoYuNeural --rate -2%
"""
import asyncio
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

H = Path(__file__).resolve().parent; AUD = H / "audio"; AUD.mkdir(exist_ok=True); REC = AUD / "rec"
VOICE = "zh-TW-HsiaoYuNeural"; RATE = "+3%"; PITCH = "+0Hz"
SR = 48000; TAIL = 0.75           # seconds of picture after each cue's voice ends
LEAD = 0.6                        # the voice of a beat starts this long after the beat begins (the scene fades in first)

# id, minimum beat length (s), narration. On-screen text is English; the voice and subtitles are Chinese. Technical terms
# stay in English in the voice as well (real / fake / beautified, evidence head, footprint, LoRA ...): that is how the
# team says them. Numbers: docs/capstone/report_v3/report.tex.
BEATS = [
    ("t1", 7.0, "Beautified is not forged。這是我們的專題：一個分得出 beautification 和 forgery、而且 evidence 可以查核的 face checker。"),
    ("b1", 9.0, "現在的 deepfake detector 被用在 content moderation、identity verification 和 fact-checking。可是大家上傳照片之前，常常先開美顏。"),
    ("b2", 10.0, "問題就出在這裡。左邊是一張 real 的照片，經過 retouching service 最強的 smoothing 之後，四個 2025 年的 detector 全部把它從 real 判成 fake。"),
    ("b3", 9.0, "右邊是一支 face swap 影片，套上手機 app 的 beauty preset 之後，同樣四個 detector 有三個讓它過關。"),
    ("b4", 13.0, "我們把十七個已發表的 detector 用 official weights 全部重跑一次：十六個把 smoothing 過的 real 判得比原圖更 fake。"
                 "原因很簡單，binary detector 只有 real 和 fake 兩個答案，沒有 beautified 這個選項。"),
    ("b5", 8.0, "所以我們把 beautified 做成第三類，而且 model 指出的 evidence 要能驗證。"),
    ("m1", 15.0, "先找原因。同一個 model、同一份 data，只改 training 時哪一類看過 smoothing。"
                 "只給 fake 看，false alarm 升到 64%；只給 real 看，false alarm 降到 4%，但 smoothing 過的 face swap 會多漏掉五十幾個百分點；"
                 "兩類都看，false alarm 降到 12%。關鍵在 training recipe。"),
    ("m2", 16.0, "再來是 data。Commercial app 一次套好幾種美顏，又不會說改了哪裡。我們用 optical flow 把 shape 的變化拆成 eye 和 contour，"
                 "剩下的 residual 用 low-pass 拆成 tone 和 texture，每個 component 都有精確的 footprint。一萬八千多張 render，變成五萬筆 single-operation 的訓練資料。"),
    ("m3", 14.0, "Model 是凍結的 CLIP ViT-L/14，只訓練 LoRA 和四個 head，三百一十六萬個參數。"
                 "Classification head 判三類，operation head 判四種操作，evidence head 輸出 16 乘 16 的 evidence map，直接用 footprint 監督。"),
    ("m4", 9.0, "說明文字不用 language model。程式照 model output 組句，每一句顯示前都經過 rule checker，不符合的不會出現。"),
    ("r1", 11.0, "成果。FF++ test set 上，real、forged、beautified 的 recall 是 82.7、90.9、86.7%，beautified 被判成 forged 的只有 4.3%。"),
    ("r2", 13.0, "換到 training 完全沒看過的 Alibaba retouching service：smoothing 有 98.8% 判成 beautified，任何 operation、任何 strength 被判成 forged 都不到 1%。"
                 "十四種 Instagram filter 也有 86% 以上判成 beautified。"),
    ("r3", 12.0, "跟已發表的 detector 公平比較，只用一樣的 FF++ training videos。Celeb-DF-B beautification 之後的 AUC 0.872，高於所有已發表的方法；"
                 "DFD 加十六種新 filter 也是最高。"),
    ("r4", 16.0, "Evidence head 標的區域是不是真正的理由？把那個區域 restore 回原圖，94% 的 forged 判定會消失，heat map 只有一半。"
                 "另外 VLM 寫的描述，blind matching 只有五成，跟丟銅板一樣，所以我們讓程式寫句子，361 張全部通過 checker。"),
    ("r5", 15.0, "整套系統在 browser 裡跑：MediaPipe 找臉，ONNX Runtime 跑 EfficientNet-B4，程式畫出 evidence 輪廓、點名部位、組句、檢查。"
                 "照片不會上傳，iPhone 上一張 0.59 秒。"),
    ("f1", 10.0, "接下來：涵蓋 reenactment、降低原圖被判成 beautified 的比例、補強 monochrome filter，讓更多 operation 可以跨 service 點名。"),
    ("e1", 5.0, "Beautified is not forged。謝謝。"),
]


def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def decode(path):
    """any audio file -> float32 mono at SR."""
    r = subprocess.run([ffmpeg(), "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32)


def trim(a, thr=0.004, keep=0.12):
    """Cut the silence at both ends (keep a short margin)."""
    idx = np.flatnonzero(np.abs(a) > thr)
    if len(idx) == 0:
        return a
    s, e = max(0, idx[0] - int(keep * SR)), min(len(a), idx[-1] + int(keep * SR))
    return a[s:e]


def recording(bid):
    """A team member's recording of this beat, if there is one."""
    if REC.is_dir():
        for p in sorted(REC.iterdir()):
            if p.stem == bid and p.suffix.lower() in (".wav", ".m4a", ".mp3", ".aac", ".flac", ".ogg", ".mp4"):
                return p
    return None


async def tts(text, out):
    import edge_tts
    for attempt in range(4):           # the free endpoint sometimes returns nothing; retry
        try:
            await edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH).save(str(out)); return
        except Exception as e:         # noqa: BLE001
            print("tts retry", out.name, e, flush=True); await asyncio.sleep(1.5)
    raise RuntimeError(f"tts failed: {out.name}")


def chunks(text):
    """Subtitle chunks: split at 。；： and at ，when a piece runs long; weight = character count (timing share)."""
    parts = [p for p in re.split(r"(?<=[。；：])", text) if p.strip()]
    out = []
    for p in parts:
        if len(p) > 26:
            sub = [q for q in re.split(r"(?<=，)", p) if q.strip()]
            cur = ""
            for q in sub:
                if cur and len(cur) + len(q) > 24:
                    out.append(cur); cur = q
                else:
                    cur += q
            if cur:
                out.append(cur)
        else:
            out.append(p)
    return [c.strip() for c in out]


def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    global VOICE, RATE, PITCH
    args = sys.argv[1:]
    if "--voice" in args:
        VOICE = args[args.index("--voice") + 1]
    if "--rate" in args:
        RATE = args[args.index("--rate") + 1]
    if "--pitch" in args:
        PITCH = args[args.index("--pitch") + 1]
    do_tts = "--no-tts" not in args
    if do_tts:
        async def all_tts():
            for bid, _, text in BEATS:
                if recording(bid):
                    print("recording", bid, recording(bid).name, flush=True); continue
                await tts(text, AUD / f"{bid}.mp3"); print("tts", bid, flush=True)
        asyncio.run(all_tts())
    audio = {bid: trim(decode(recording(bid) or AUD / f"{bid}.mp3")) for bid, _, _ in BEATS}
    cues, t = [], 0.0
    for bid, mn, text in BEATS:
        dur = len(audio[bid]) / SR
        length = max(LEAD + dur + TAIL, mn)
        subs, acc, total = [], 0, sum(len(c) for c in chunks(text))
        for c in chunks(text):
            subs.append({"t0": round(LEAD + dur * acc / total, 3), "t1": round(LEAD + dur * (acc + len(c)) / total, 3), "text": c}); acc += len(c)
        cues.append({"id": bid, "start": round(t, 3), "voice": round(t + LEAD, 3), "audio": round(dur, 3), "end": round(t + length, 3),
                     "min": mn, "text": text, "subs": subs, "source": "recording" if recording(bid) else VOICE})
        t += length
    total = t
    track = np.zeros(int(total * SR) + SR, np.float32)
    for c in cues:
        a = audio[c["id"]]; s = int(c["voice"] * SR); track[s:s + len(a)] += a
    peak = np.abs(track).max(); track = track / peak * 0.89 if peak > 0 else track
    wav = AUD / "narration.wav"
    subprocess.run([ffmpeg(), "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-", "-c:a", "pcm_s16le", str(wav)],
                   input=track.tobytes(), check=True)
    (H / "cues.json").write_text(json.dumps({"voice": VOICE, "rate": RATE, "pitch": PITCH, "total": round(total, 3), "cues": cues}, ensure_ascii=False, indent=1), encoding="utf-8")
    (H / "cues.js").write_text("window.CUES = " + json.dumps({"total": round(total, 3), "cues": cues}, ensure_ascii=False) + ";\n", encoding="utf-8")
    srt, k = [], 1
    for c in cues:
        for s in c["subs"]:
            srt.append(f"{k}\n{srt_time(c['start'] + s['t0'])} --> {srt_time(c['start'] + s['t1'])}\n{s['text']}\n"); k += 1
    (H / "subtitles.srt").write_text("\n".join(srt), encoding="utf-8")
    rec = sum(1 for c in cues if c["source"] == "recording")
    md = ["# 旁白稿（zh-TW）\n", f"總長 {int(total // 60)} 分 {total % 60:04.1f} 秒；{rec} 段真人錄音，{len(cues) - rec} 段 {VOICE}（rate {RATE}）\n",
          "錄音方式：每一段存成 `audio/rec/<id>.m4a`（或 wav／mp3），再跑 `python narration.py --no-tts`，有錄音的段落會用錄音，其餘用合成聲音。\n"]
    for c in cues:
        md.append(f"## {c['id']}  {srt_time(c['start'])[3:8]} – {srt_time(c['end'])[3:8]}（旁白 {c['audio']:.1f} s）\n\n{c['text']}\n")
    (H / "narration_script.md").write_text("\n".join(md), encoding="utf-8")
    for c in cues:
        print(f"{c['id']:3s} {c['start']:6.1f} -> {c['end']:6.1f}  voice {c['audio']:5.1f}s  min {c['min']:4.1f}  {c['source']}")
    print(f"total {total:.1f} s = {int(total // 60)}:{total % 60:04.1f}")


if __name__ == "__main__":
    main()
