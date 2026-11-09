"""Narration voice with Qwen3-TTS on the local GPU (conda env qwen3tts).

python docs/capstone/video/tts_local.py samples            -> audio/samples/*.wav: one test sentence in several voices
python docs/capstone/video/tts_local.py all <ref.wav> "<ref transcript>"   -> audio/rec/<id>.wav for every beat, cloned
                                                                              from the reference recording
Numbers are read in Chinese words (the model loops on raw digits); a beat that comes out longer than 0.16 s per character
is generated again.
"""
import json
import re
import sys
import time
from pathlib import Path

import soundfile as sf
import torch
from qwen_tts import Qwen3TTSModel

H = Path(__file__).resolve().parent; AUD = H / "audio"
D = "零一二三四五六七八九"
TEST = ("問題就出在這裡。左邊是一張 real 的照片，經過 retouching service 最強的 smoothing 之後，四個二零二五年的 detector 全部把它從 real 判成 fake。"
        "右邊是一支 face swap 影片，套上手機 app 的 beauty preset 之後，同樣四個 detector 有三個讓它過關。")


def int_zh(n):
    n = int(n)
    if n == 0:
        return "零"
    digits = str(n)
    if len(digits) > 4:
        return "".join(D[int(c)] for c in digits)
    units = ["", "十", "百", "千"]; s = ""
    for i, c in enumerate(digits):
        p = len(digits) - 1 - i
        if c == "0":
            if s and not s.endswith("零") and p > 0 and any(ch != "0" for ch in digits[i + 1:]):
                s += "零"
        else:
            s += (D[int(c)] if not (c == "1" and p == 1 and i == 0) else "") + units[p]
    return s


def num_zh(m):
    s = int_zh(m.group(1))
    if m.group(2):
        s += "點" + "".join(D[int(c)] for c in m.group(2))
    return s


def spoken(t):
    t = re.sub(r"(\d{4}) 年", lambda m: "".join(D[int(c)] for c in m.group(1)) + "年", t)
    t = t.replace("ViT-L/14", "ViT-L 十四").replace("FF++", "FF plus plus").replace("Celeb-DF-B", "Celeb D F B").replace("DFD", "D F D")
    t = re.sub(r"(\d+)(?:\.(\d+))?%", lambda m: "百分之" + num_zh(m), t)
    t = re.sub(r"(\d+)(?:\.(\d+))?", num_zh, t)
    return t


def beats():
    src = (H / "narration.py").read_text(encoding="utf-8")
    m = re.search(r"BEATS = \[(.*?)\n\]\n", src, re.S)
    return [(b[0], b[2]) for b in eval("[" + m.group(1) + "]")]


def load(name):
    return Qwen3TTSModel.from_pretrained(name, device_map="cuda:0", dtype=torch.bfloat16)


def gen(model, prompt, text):
    st = spoken(text)
    for attempt in range(3):
        w, sr = model.generate_voice_clone(text=st, language="Chinese", voice_clone_prompt=prompt)
        if len(w[0]) / sr / len(st) < 0.16:
            break
        print("  too long, retry", flush=True)
    return w[0], sr, st


def main():
    mode = sys.argv[1]
    if mode == "samples":
        out = AUD / "samples"; out.mkdir(parents=True, exist_ok=True)
        base = load("Qwen/Qwen3-TTS-12Hz-1.7B-Base")
        refs = [("member", AUD / "member_ref.wav", sys.argv[2] if len(sys.argv) > 2 else None),
                ("hsiaoyu", AUD / "r3.mp3", None)]
        for name, ref, txt in refs:
            if not ref.exists():
                print("no", ref); continue
            t0 = time.time()
            p = (base.create_voice_clone_prompt(ref_audio=str(ref), ref_text=spoken(txt)) if txt
                 else base.create_voice_clone_prompt(ref_audio=str(ref), x_vector_only_mode=True))
            w, sr, _ = gen(base, p, TEST); sf.write(out / f"clone_{name}.wav", w, sr); print("clone", name, f"{len(w)/sr:.1f}s", f"{time.time()-t0:.0f}s", flush=True)
        del base; torch.cuda.empty_cache()
        cv = load("Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice")
        for spk in ["Vivian", "Serena", "Ryan", "Aiden", "Ono_Anna", "Sohee", "Uncle_Fu", "Dylan", "Eric"]:
            try:
                w, sr = cv.generate_custom_voice(text=spoken(TEST), language="Chinese", speaker=spk)
                sf.write(out / f"preset_{spk}.wav", w[0], sr); print("preset", spk, f"{len(w[0])/sr:.1f}s", flush=True)
            except Exception as e:  # noqa: BLE001
                print("preset fail", spk, str(e)[:120], flush=True)
        print("DONE", flush=True)
    elif mode == "all":
        ref, txt = Path(sys.argv[2]), (sys.argv[3] if len(sys.argv) > 3 else None)
        base = load("Qwen/Qwen3-TTS-12Hz-1.7B-Base")
        p = (base.create_voice_clone_prompt(ref_audio=str(ref), ref_text=spoken(txt)) if txt
             else base.create_voice_clone_prompt(ref_audio=str(ref), x_vector_only_mode=True))
        rec = AUD / "rec"; rec.mkdir(exist_ok=True); done = {}
        for bid, text in beats():
            t0 = time.time(); w, sr, st = gen(base, p, text); sf.write(rec / f"{bid}.wav", w, sr); done[bid] = st
            print(bid, f"{len(w)/sr:.1f}s for {len(st)} chars, {time.time()-t0:.0f}s", flush=True)
        (rec / "spoken.json").write_text(json.dumps(done, ensure_ascii=False, indent=1), encoding="utf-8")
        print("DONE", flush=True)


if __name__ == "__main__":
    main()
