"""Addendum-3 blur probe for CGDNet arms on the SAME 300 FF++ test reals as sbifix/blur_probe.py (rows[r1=='0'][::4][:300])."""
import sys, json, numpy as np, torch, cv2
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
from train_cgd import CGDNet, SIZE, NORM
from torchvision import transforms
B = Path(r"C:\My_Project\AIGC"); TF = transforms.Compose([transforms.Resize((SIZE, SIZE)), transforms.ToTensor(), NORM])
rows = [l.split("\t") for l in (B / "results/research/ffpp_unified_20260925/ffpp3_test.txt").read_text(encoding="utf-8").splitlines()[1:]]
ff = [np.array(Image.open(r[0]).convert("RGB")) for r in rows if r[1] == "0"][::4][:300]
def down(a, f):
    h, w = a.shape[:2]; s = cv2.resize(a, (max(8, int(w / f)), max(8, int(h / f))), interpolation=cv2.INTER_AREA); return cv2.resize(s, (w, h), interpolation=cv2.INTER_LINEAR)
conds = {"orig": ff, "down2": [down(a, 2) for a in ff], "blur1.5": [cv2.GaussianBlur(a, (0, 0), 1.5) for a in ff],
         "jpeg30": [cv2.imdecode(cv2.imencode(".jpg", a[..., ::-1], [cv2.IMWRITE_JPEG_QUALITY, 30])[1], 1)[..., ::-1] for a in ff]}
out = {}
for arm, seed in (("MASKD", 20260928), ("MASK", 20260928), ("MASK", 20260929)):
    net = CGDNet(head=True); net.load_state_dict(torch.load(B / f"checkpoints/research/cgd_20260927/cgd_{arm}_s{seed}.pth", map_location="cpu")); net = net.cuda().eval()
    r = {}
    for k, ims in conds.items():
        P = []
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            for i in range(0, len(ims), 32):
                P.append(torch.softmax(net(torch.stack([TF(Image.fromarray(np.ascontiguousarray(a))) for a in ims[i:i + 32]]).cuda())[0].float(), 1).cpu())
        P = torch.cat(P).numpy(); r[k] = round(float((P.argmax(1) == 1).mean() * 100), 1)
    out[f"{arm}_s{seed}"] = r; print(arm, seed, r, flush=True)
json.dump(out, open(Path(__file__).resolve().parent / "blur_probe_cgd.json", "w"), indent=1)
