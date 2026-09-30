"""Blur-shortcut probe: FF++ test reals under downscale/blur, P(fake) per detector (see PRE_DECLARED Addendum 2)."""
import sys, json, tempfile, os
import numpy as np, torch, timm, cv2
from PIL import Image
from torchvision import transforms
B = r"C:\My_Project\AIGC"; sys.path.insert(0, B + r"\results\research\external_baselines_20260905"); import zoo
def main():
    rows = [l.split("\t") for l in open(B + r"\results\research\ffpp_unified_20260925\ffpp3_test.txt", encoding="utf-8").read().splitlines()[1:]]
    ff = [np.array(Image.open(r[0]).convert("RGB")) for r in rows if r[1] == "0"][::4][:300]
    def down(a, f):
        h, w = a.shape[:2]; s = cv2.resize(a, (max(8, int(w / f)), max(8, int(h / f))), interpolation=cv2.INTER_AREA); return cv2.resize(s, (w, h), interpolation=cv2.INTER_LINEAR)
    conds = {"orig": ff, "down2": [down(a, 2) for a in ff], "blur1.5": [cv2.GaussianBlur(a, (0, 0), 1.5) for a in ff], "jpeg30": [cv2.imdecode(cv2.imencode(".jpg", a[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 30])[1], 1)[..., ::-1] for a in ff]}
    tmp = tempfile.mkdtemp(); paths = {}
    for k, ims in conds.items():
        paths[k] = []
        for i, a in enumerate(ims):
            p = os.path.join(tmp, f"{k}_{i}.png"); Image.fromarray(a).save(p); paths[k].append(p)
    def ours(ck, k, arch, size):
        m = timm.create_model(arch, pretrained=False, num_classes=k); m.load_state_dict(torch.load(ck, map_location="cpu")); m = m.cuda().eval()
        T = transforms.Compose([transforms.Resize((size, size)), transforms.ToTensor(), transforms.Normalize([0.5] * 3, [0.5] * 3)])
        def f(ps):
            with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
                return torch.cat([torch.softmax(m(torch.stack([T(Image.open(p).convert("RGB")) for p in ps[i:i + 32]]).cuda()).float(), 1).cpu() for i in range(0, len(ps), 32)]).numpy()
        return f
    E = "tf_efficientnet_b4.ap_in1k"
    R = {}
    for name, f in {"HYB-L-s2": ours(B + r"\checkpoints\research\sbiscale_20260926\sbiscale_HYB_s20260927.pth", 3, E, 380),
                    "HYB-F": ours(B + r"\checkpoints\research\sbifix_20260927\sbifix_HYB_s20260928.pth", 3, E, 380),
                    "HYBD-F": ours(B + r"\checkpoints\research\sbifix_20260927\sbifix_HYBD_s20260928.pth", 3, E, 380),
                    "SBI-F": ours(B + r"\checkpoints\research\sbifix_20260927\sbifix_SBI_s20260928.pth", 2, E, 380),
                    "RepViT": ours(B + r"\checkpoints\research\ffpp_unified_20260925\ffpp3_FLAT_repvit20.pth", 3, "repvit_m0_9.dist_300e_in1k", 224)}.items():
        R[name] = {k: {"p_fake": float(f(ps)[:, 1].mean()), "argmax_fake": float((f(ps).argmax(1) == 1).mean() * 100)} for k, ps in paths.items()}
        print(name, {k: round(v["argmax_fake"], 1) for k, v in R[name].items()}, flush=True)
    for b in ["sbi", "xception", "effnb4", "ucf"]:
        m = zoo.ZOO[b]()
        R[b] = {k: {"p_fake": float(np.mean(s := np.asarray(m.score(ps)))), "over_0.5": float((s > 0.5).mean() * 100)} for k, ps in paths.items()}
        print(b, {k: (round(v["p_fake"], 3), round(v["over_0.5"], 1)) for k, v in R[b].items()}, flush=True); del m; torch.cuda.empty_cache()
    json.dump(R, open(B + r"\results\research\sbifix_20260927\blur_probe.json", "w"), indent=1); print("DONE")


if __name__ == "__main__":
    main()
