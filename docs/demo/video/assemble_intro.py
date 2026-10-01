import json, subprocess, glob, os
FF = "/home/intern_2603055/miniconda3/envs/comfyui/bin/ffmpeg"; D = "/home/intern_2603055/demo_page/intro"
cards = json.load(open(f"{D}/cards/cards.json"))
def run(args): subprocess.run([FF, "-y", "-loglevel", "error"] + args, check=True)
def card_clip(png, secs, out):
    run(["-loop", "1", "-t", str(secs), "-i", png, "-f", "lavfi", "-t", str(secs), "-i", "anullsrc=r=48000:cl=stereo",
         "-vf", f"scale=1280:720,fade=t=in:st=0:d=0.4,fade=t=out:st={secs - 0.4}:d=0.4,format=yuv420p", "-r", "30",
         "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-shortest", out])
parts = []
for k, c in enumerate(cards):
    out = f"{D}/p{k:02d}.mp4"; card_clip(f"{D}/{c['file']}", c["secs"], out); parts.append(out)
    if c["file"].endswith("05_demo.png"):
        web = sorted(glob.glob("/home/intern_2603055/demo_page/video2/*.webm"), key=os.path.getmtime)[-1]
        dur = float(subprocess.run([FF.replace("ffmpeg", "ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", web],
                                   capture_output=True, text=True).stdout)
        out = f"{D}/p{k:02d}b.mp4"
        run(["-i", web, "-f", "lavfi", "-t", str(dur), "-i", "anullsrc=r=48000:cl=stereo",
             "-vf", f"scale=1280:720,fps=30,fade=t=in:st=0:d=0.4,fade=t=out:st={dur - 0.5}:d=0.5,format=yuv420p",
             "-c:v", "libx264", "-crf", "20", "-c:a", "aac", "-shortest", out]); parts.append(out)
open(f"{D}/list.txt", "w").write("".join(f"file '{p}'\n" for p in parts))
run(["-f", "concat", "-safe", "0", "-i", f"{D}/list.txt", "-c", "copy", "-movflags", "+faststart", f"{D}/intro.mp4"])
print(subprocess.run([FF.replace("ffmpeg", "ffprobe"), "-v", "error", "-show_entries", "format=duration:format=size", "-of", "csv=p=0", f"{D}/intro.mp4"], capture_output=True, text=True).stdout)
for t in (3, 12, 40, 60, 95, 118):
    run(["-ss", str(t), "-i", f"{D}/intro.mp4", "-frames:v", "1", "-vf", "scale=426:-1", f"{D}/f{t:03d}.png"])
