"""CGD tables: detection (arms vs HYBPE) and explanation (evidence head vs post-hoc, with ceiling and controls).
Reads results/research/cgd_20260927/{eval_cgd_detect.json, explain_*_s20260928.json}.

python docs/paper_v2/make_tables_cgd.py -> docs/paper_v2/tables/tab_cgd_detect.tex, tab_cgd_explain.tex
"""
import json
from pathlib import Path

BASE = Path(r"C:\My_Project\AIGC")
R = BASE / "results/research/cgd_20260927"
OUT = BASE / "docs/paper_v2/tables"; OUT.mkdir(parents=True, exist_ok=True)
CB = BASE / "results/research/celebdfb_v2_20260927/results_v3.json"
VL = BASE / "results/research/ffpp_benchmark_20260925/video_level.json"
PEND = r"\textit{pend.}"
ARMS = [("HYBPE", r"\ours{}-PE (no head)"), ("MASK", r"\textbf{+ evidence head (ours)}"), ("MASKD", r"+ evidence head + symmetric degradation"), ("CGD", r"+ consistency loss (43k edits)"),
        ("CGDD", r"+ consistency + symmetric degradation"), ("CGD-ZERO", r"CGD, zero fill (GAIN)"), ("CGD-BLUR", r"CGD, blur fill"),
        ("CGD-NOHOLD", r"CGD, no hold term")]


def jl(p):
    p = Path(p); return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else None


def f3(x):
    return PEND if x is None else f"{x:.3f}"


def pc(x):
    return PEND if x is None else f"{100 * x:.1f}"


def tab_detect():
    D = jl(R / "eval_cgd_detect.json") or {}; cb = jl(CB) or {}; vl = jl(VL) or {}
    def v(k, s_):
        x = vl.get(k, {}).get(s_, {}).get("video"); return "--" if x is None else f"{x:.3f}"
    L = [r"\begin{tabular}{lcccccccc}", r"\toprule",
         r" & \multicolumn{2}{c}{CDFv2} & \multicolumn{2}{c}{DFD} & & & & Celeb-DF-B \\", r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}",
         r"Variant & frame & video & frame & video & FF++ real/fake/filter & FA / MISS & B1 & AUC / accus. \\", r"\midrule"]
    for k, lab in ARMS:
        d = D.get(k)
        if d is None:
            continue
        c = cb.get(f"cgd_{k}", {})
        acc = c.get("FA0"); acc = "--" if acc is None else f"{acc:.1f}"
        L.append(f"{lab} & {f3(d['cdf']['auc'])} & {v(k, 'cdf')} & {f3(d['dfd']['auc'])} & {v(k, 'dfd')} & {d['indomain']['real']:.1f}/{d['indomain']['fake']:.1f}/{d['indomain']['filter']:.1f} & "
                 f"{d['FA']:.1f} / {d['MISS']:.1f} & {len(d['b1_dominated_by'])}/{d['b1_n_detectors']} & {f3(c.get('auc_untreated'))} / {acc} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_cgd_detect.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


def _explain_rows(spec):
    """spec: (json key, method, label). One row per entry; the ceiling is the restore-GT-footprint flip rate on that
    model's own detected items, so it is a per-row number."""
    rows = []
    for k, meth, lab in spec:
        e = jl(R / f"explain_{k}_s{'20260929' if k.startswith('RU') else '20260928'}.json")
        if e is None or meth not in e.get("donor", {}):
            continue
        cells = []
        for mech in ("donor", "sd", "sdxl"):
            d = e.get(mech); m = d.get(meth) if d else None
            if m is None:
                cells += ["--"] * 4; continue
            cells += [f"{m['iou7']:.3f}", f"{100 * m['flip_pred']:.1f}", f"{100 * d['flip_ceiling_gt']:.1f}", f"{100 * m['flip_comp']:.1f}"]
        rows.append(f"{lab} & " + " & ".join(cells) + r" \\")
    return rows


def _explain_table(rows, name):
    e = jl(R / "explain_MASK_s20260928.json") or {}
    ctrl = []
    for mech in ("donor", "sd", "sdxl"):
        m = e[mech]["evidence"]
        ctrl += [f"{m['iou7_centre']:.3f}", f"{100 * m['flip_centre']:.1f}", "--", f"{100 * m['flip_rand']:.1f}"]
    L = [r"\begin{tabular}{l cccc cccc cccc}", r"\toprule",
         r" & \multicolumn{4}{c}{donor transplant} & \multicolumn{4}{c}{SD-1.5 inpaint} & \multicolumn{4}{c}{SDXL inpaint (unseen editor)} \\",
         r"\cmidrule(lr){2-5}\cmidrule(lr){6-9}\cmidrule(lr){10-13}",
         r"Map & IoU$_7$ & flip & ceil. & compl. & IoU$_7$ & flip & ceil. & compl. & IoU$_7$ & flip & ceil. & compl. \\", r"\midrule",
         r"centre prior / random region (last col.) & " + " & ".join(ctrl) + r" \\", r"\midrule"] + rows + [r"\bottomrule", r"\end{tabular}"]
    (OUT / name).write_text("\n".join(L) + "\n", encoding="utf-8")


def tab_explain():
    main = [("HYBPE", "scorecam", r"Score-CAM, same backbone, no head"),
            ("RUCLIPE", "evidence", r"head, vendor data, no part edits (CLIP)"),
            ("MASK", "evidence", r"head, part edits, FF++ only (EffNet-B4)"),
            ("RU4E", "evidence", r"\ours{}-lite (EffNet-B4)"),
            ("RUCLIPE4", "evidence", r"\textbf{\ours{}} (CLIP ViT-L/14 + LoRA)")]
    _explain_table(_explain_rows(main), "tab_cgd_explain.tex")
    full = [("HYBPE", "gradcam", r"no head, Grad-CAM"), ("HYBPE", "gradcampp", r"no head, Grad-CAM++"), ("HYBPE", "scorecam", r"no head, Score-CAM"),
            ("MASK", "evidence", r"head, part edits, FF++ only"), ("MASKD", "evidence", r"+ symmetric degradation"),
            ("CGD", "evidence", r"+ restoration-consistency loss"), ("CGDD", "evidence", r"+ consistency + symmetric degradation"),
            ("RU3E", "evidence", r"head, vendor data, no part edits (EffNet-B4)"), ("RUCLIPE", "evidence", r"head, vendor data, no part edits (CLIP)"),
            ("RU4E", "evidence", r"\ours{}-lite (EffNet-B4)"), ("RUCLIPE4", "evidence", r"\ours{} (CLIP ViT-L/14 + LoRA)")]
    _explain_table(_explain_rows(full), "tab_cgd_explain_all.tex")


SRC = [("real", "genuine"), ("Deepfakes", "Deepfakes"), ("Face2Face", "Face2Face"), ("FaceSwap", "FaceSwap"), ("NeuralTextures", "NeuralTextures"),
       ("filter:smoothing", "smoothing"), ("filter:whitening", "whitening"), ("filter:eye_enlarging", "eye enlarging"),
       ("filter:face_reshaping_slim", "face slimming"), ("filter:pilgram", "photometric (14)")]


def tab_completeness(arm="MASK"):
    """Per-source FF++ test recall and routing for the evidence-head model, plus latency / size for the three deployable models."""
    C = jl(R / f"completeness_{arm}.json")
    if C is None:
        return
    per = C["per_source"]["per_source"]
    L = [r"\begin{tabular}{llrrrr}", r"\toprule", r"Class & Source & $n$ & $\to$real & $\to$fake & $\to$filter \\", r"\midrule"]
    for k, lab in SRC:
        d = per.get(k)
        if d is None:
            continue
        cls = "real" if k == "real" else ("fake" if not k.startswith("filter") else "filter")
        cells = [f"{d['to'][c]:.1f}" for c in ("real", "fake", "filter")]
        i = {"real": 0, "fake": 1, "filter": 2}[cls]; cells[i] = r"\textbf{" + cells[i] + "}"
        L.append(f"{cls} & {lab} & {d['n']} & " + " & ".join(cells) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_persource.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    lat = C["latency"]
    L = [r"\begin{tabular}{lrrrr}", r"\toprule", r"Model & Params (M) & Input & CPU (ms) & GPU (ms) \\", r"\midrule"]
    for k, d in lat.items():
        L.append(f"{k} & {d['params_M']:.1f} & {d['input']} & {d['cpu_ms']:.1f} & {d['gpu_ms']:.1f} \\\\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_latency.tex").write_text("\n".join(L) + "\n", encoding="utf-8")
    R_ = C["robustness"]
    L = [r"\begin{tabular}{l" + "c" * 10 + "}", r"\toprule",
         "Model & " + " & ".join(R_["HYB"].keys()) + r" \\", r"\midrule"]
    for name, d in R_.items():
        L.append(name.replace("(evidence head)", "") + " & " + " & ".join(f"{v['real']:.0f}/{v['fake']:.0f}" for v in d.values()) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}"]
    (OUT / "tab_robust.tex").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    tab_detect(); tab_explain(); tab_completeness(); print("cgd tables ->", OUT)
