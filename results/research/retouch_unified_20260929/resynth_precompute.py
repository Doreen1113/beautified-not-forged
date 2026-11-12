"""Addendum 67: re-synthesised genuine frames (every pixel decoder-rendered, content and size unchanged) for use as pseudo-forgeries.
Each training base frame exactly as RUData3._base returns it (FF++ c23 dense train real frames as stored; FFHQ originals cropped to
their manifest box and capped to 512) is encoded and decoded by the FLUX.1 VAE (16-channel AutoencoderKL; chosen because no DF40,
Celeb-DF or FF++ generator uses it, whereas the SD VAE is the decoder of several DF40 entire-face-synthesis methods) and stored
losslessly at the base frame's size: <AIGC_BASE>/resynth_flux/<src>/<stem>.png.
python resynth_precompute.py [--limit N]   (run in an environment with diffusers; GPU)"""
import argparse
import os
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image

HERE = Path(__file__).resolve().parent; sys.path.insert(0, str(HERE))
BASE = Path(os.environ.get("AIGC_BASE", r"C:\My_Project\AIGC")); OUT = BASE / "resynth_flux"
CAP = 512


def read_manifest(f):
    rows = []
    lines = Path(f).read_text(encoding="utf-8").splitlines(); hd = lines[0].split("\t")
    for l in lines[1:]:
        if l.strip():
            rows.append(dict(zip(hd, l.split("\t"))))
    return rows


def cap(rgb):
    h, w = rgb.shape[:2]; f = CAP / max(h, w)
    return rgb if f >= 1 else cv2.resize(rgb, (max(8, int(w * f)), max(8, int(h * f))), interpolation=cv2.INTER_AREA)


def base_image(r):
    if r["src"] == "ffpp_real":
        return np.array(Image.open(BASE / "FaceForensics_protocol_frames_dense/train/real" / f"{r['stem']}.jpg").convert("RGB"))
    im = np.array(Image.open(r["path"].replace("C:\\My_Project\\AIGC", str(BASE)).replace("\\", "/")).convert("RGB"))
    b = r.get("box", "-")
    if b and b != "-":
        x0, y0, x1, y1 = [int(float(v)) for v in b.split()]; im = np.ascontiguousarray(im[y0:y1, x0:x1])
    return cap(im)


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--reverse-shard", type=int, default=-1, help="helper process: walk the list from the end, every nshard-th frame")
    ap.add_argument("--nshard", type=int, default=3); a = ap.parse_args()
    from diffusers import AutoencoderKL
    vae = AutoencoderKL.from_pretrained("black-forest-labs/FLUX.1-Fill-dev", subfolder="vae", torch_dtype=torch.bfloat16, local_files_only=True).cuda().eval()
    rows = [r for r in read_manifest(HERE / "manifest_train.tsv") if r["src"] in ("ffpp_real", "ffhq_orig")]
    seen, todo = set(), []
    for r in rows:
        k = (r["src"], r["stem"])
        if k not in seen:
            seen.add(k); todo.append(r)
    if a.limit:
        todo = todo[: a.limit]
    if a.reverse_shard >= 0:
        todo = todo[::-1][a.reverse_shard::a.nshard]
    print("unique base frames", len(todo), flush=True); err = []
    for i, r in enumerate(todo):
        q = OUT / r["src"] / f"{r['stem']}.png"
        if q.is_file():
            continue
        q.parent.mkdir(parents=True, exist_ok=True)
        rgb = base_image(r); h, w = rgb.shape[:2]; H, W = (h + 15) // 16 * 16, (w + 15) // 16 * 16
        x = np.pad(rgb, ((0, H - h), (0, W - w), (0, 0)), mode="reflect")
        t = torch.from_numpy(x).permute(2, 0, 1)[None].float().div(127.5).sub(1).cuda().to(torch.bfloat16)
        y = vae.decode(vae.encode(t).latent_dist.mode()).sample
        y = ((y.float().clamp(-1, 1) + 1) * 127.5).round().byte()[0].permute(1, 2, 0).cpu().numpy()[:h, :w]
        tmp = q.with_suffix(".tmp.png"); Image.fromarray(y).save(tmp); os.replace(tmp, q)
        if i < 3 or i % 2000 == 0:
            d = np.abs(y.astype(np.int16) - rgb.astype(np.int16)); print(i, r["src"], r["stem"], (h, w), "mean |diff|", round(float(d.mean()), 2),
                                                                      "PSNR", round(float(10 * np.log10(255 ** 2 / max((d.astype(np.float32) ** 2).mean(), 1e-6))), 2), flush=True)
    print("done", len(todo), flush=True)


if __name__ == "__main__":
    main()
