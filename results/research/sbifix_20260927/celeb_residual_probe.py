"""What still separates untreated Celeb-DF genuine frames from FF++ genuine frames for HYBD? Probe: crop margin, colour
statistics (histogram-match FF++ reals to Celeb reals), chroma subsampling, and Celeb frames histogram-matched to FF++."""
import sys, json
import numpy as np, torch, timm, cv2
from PIL import Image
from torchvision import transforms
from skimage.exposure import match_histograms
B = r"C:\My_Project\AIGC"
sys.path.insert(0, B)
import extract_ffpp_protocol_frames as E


def main():
    T = transforms.Compose([transforms.Resize((380, 380)), transforms.ToTensor(), transforms.Normalize([0.5] * 3, [0.5] * 3)])
    m = timm.create_model("tf_efficientnet_b4.ap_in1k", pretrained=False, num_classes=3)
    m.load_state_dict(torch.load(B + r"\checkpoints\research\sbifix_20260927\sbifix_HYBD_s20260928.pth", map_location="cpu")); m = m.cuda().eval()
    def probs(ims):
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            return torch.cat([torch.softmax(m(torch.stack([T(Image.fromarray(a)) for a in ims[i:i + 32]]).cuda()).float(), 1).cpu() for i in range(0, len(ims), 32)]).numpy()
    rows = [l.split("\t") for l in open(B + r"\results\research\ffpp_unified_20260925\ffpp3_test.txt", encoding="utf-8").read().splitlines()[1:]]
    ff = [np.array(Image.open(r[0]).convert("RGB")) for r in rows if r[1] == "0"][::4][:300]
    cdf = [l.split("\t") for l in open(B + r"\splits\research\ffpp_benchmark_20260925\celebdf_std32v2.txt", encoding="utf-8").read().splitlines()[1:]]
    cd = [np.array(Image.open(r[0]).convert("RGB")) for r in cdf if r[1] == "0"][::20][:300]
    R = {}
    def rep(name, ims):
        p = probs(ims); R[name] = {"fake": round(float((p.argmax(1) == 1).mean() * 100), 1), "filter": round(float((p.argmax(1) == 2).mean() * 100), 1), "p_fake": round(float(p[:, 1].mean()), 3)}
        print(f"{name:34s} ->fake {R[name]['fake']:5.1f}%  ->filter {R[name]['filter']:5.1f}%  p_fake {R[name]['p_fake']:.3f}", flush=True)
    rep("FF++ real", ff); rep("CDF real", cd)
    # colour: FF++ matched to a random Celeb reference, and Celeb matched to FF++
    rng = np.random.default_rng(0)
    rep("FF++ real, hist-matched to CDF", [match_histograms(a, cd[int(rng.integers(0, len(cd)))], channel_axis=-1).astype(np.uint8) for a in ff])
    rep("CDF real, hist-matched to FF++", [match_histograms(a, ff[int(rng.integers(0, len(ff)))], channel_axis=-1).astype(np.uint8) for a in cd])
    # grey-world / saturation
    def desat(a, f):
        hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV).astype(np.float32); hsv[..., 1] *= f; return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2RGB)
    rep("FF++ real, saturation x0.7", [desat(a, 0.7) for a in ff]); rep("CDF real, saturation x1.3", [desat(a, 1.3) for a in cd])
    # crop margin: shrink / enlarge the FF++ crop (simulate face-scale shift)
    def rescale_crop(a, f):
        h, w = a.shape[:2]; ch, cw = int(h * f), int(w * f); y0, x0 = (h - ch) // 2, (w - cw) // 2
        return a[max(0, y0):y0 + ch, max(0, x0):x0 + cw] if f < 1 else cv2.copyMakeBorder(a, (ch - h) // 2, (ch - h) // 2, (cw - w) // 2, (cw - w) // 2, cv2.BORDER_REFLECT_101)
    rep("FF++ real, crop tighter 0.8", [rescale_crop(a, 0.8) for a in ff]); rep("FF++ real, crop looser 1.25", [rescale_crop(a, 1.25) for a in ff])
    rep("CDF real, crop tighter 0.8", [rescale_crop(a, 0.8) for a in cd]); rep("CDF real, crop looser 1.25", [rescale_crop(a, 1.25) for a in cd])
    # sharpen Celeb (opposite of blur)
    rep("CDF real, unsharp", [cv2.addWeighted(a, 1.6, cv2.GaussianBlur(a, (0, 0), 1.5), -0.6, 0) for a in cd])
    # size stats
    R["crop_h_median"] = {"ff": float(np.median([a.shape[0] for a in ff])), "cdf": float(np.median([a.shape[0] for a in cd]))}
    R["mean_rgb"] = {"ff": [float(x) for x in np.mean([a.reshape(-1, 3).mean(0) for a in ff], 0)], "cdf": [float(x) for x in np.mean([a.reshape(-1, 3).mean(0) for a in cd], 0)]}
    R["mean_sat"] = {"ff": float(np.mean([cv2.cvtColor(a, cv2.COLOR_RGB2HSV)[..., 1].mean() for a in ff])), "cdf": float(np.mean([cv2.cvtColor(a, cv2.COLOR_RGB2HSV)[..., 1].mean() for a in cd]))}
    R["laplacian_var"] = {"ff": float(np.median([cv2.Laplacian(cv2.cvtColor(a, cv2.COLOR_RGB2GRAY), cv2.CV_64F).var() for a in ff])), "cdf": float(np.median([cv2.Laplacian(cv2.cvtColor(a, cv2.COLOR_RGB2GRAY), cv2.CV_64F).var() for a in cd]))}
    print(json.dumps({k: R[k] for k in ("crop_h_median", "mean_rgb", "mean_sat", "laplacian_var")}, indent=None))
    json.dump(R, open(B + r"\results\research\sbifix_20260927\celeb_residual_probe.json", "w"), indent=1); print("DONE")


if __name__ == "__main__":
    main()
