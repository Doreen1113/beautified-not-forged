"""Post-hoc checks on the saved per-frame spectra (bandenergy_frames.npz) and parsed FA (fa_parsed.json):
  1. threshold scan: E_hf(t) loss for t = 0.02 .. 0.45 cycles/pixel and the band [t, t+0.1), with pooled / mean per-detector
     Spearman and the fixed-effects partial R2 of logit(FA) on loss, 7 Celeb-DF forms (native and view256);
  2. matched-form contrasts: FA differences between forms that remove a similar amount of in-face texture but differ in one
     property (face-local vs whole-crop at the same kernel; edge-preserving bilateral vs uniform Gaussian blend at the same
     E_hf loss; median vs bilateral), per detector, with sign counts and Wilcoxon signed-rank tests;
  3. mean radial power spectra per form relative to untreated.
Writes bandenergy_extra.json, bandenergy_extra.md and fig_bandenergy_supp.{pdf,png}.
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy import stats

B = Path(r"C:\My_Project\AIGC"); HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); from bandenergy import FORMS, ALIFORMS, PUB, RBINS, fixed_effects, logit  # noqa: E402
sys.path.insert(0, str(B / "docs/paper_v2")); import figstyle as FS; FS.apply()  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

npz = dict(np.load(HERE / "bandenergy_frames.npz")); fa = json.loads((HERE / "fa_parsed.json").read_text())["published"]
res = json.loads((HERE / "bandenergy.json").read_text())
FA = lambda d, c: fa[d]["fa"][c]


def ehf_from_rad(rad, t0, t1=None):
    """Energy share in [t0, t1) from the binned, total-normalised radial spectrum (bins RBINS, left edges)."""
    lo = RBINS[:-1]; m = (lo >= t0) if t1 is None else ((lo >= t0) & (lo < t1))
    return rad[:, m].sum(1)


def mean_log_loss(ec, eu):
    """Mean over frames of -log(E_form / E_untreated); frames with zero energy in the band (a few frames of fl06/fl12 in
    narrow bands above 0.28 c/px) are excluded and counted."""
    v = (ec > 0) & (eu > 0); return float(np.mean(-np.log(ec[v] / eu[v]))), int((~v).sum())


def corr_block(x, forms, dets):
    X = np.array([x[c] for d in dets for c in forms]); Y = np.array([FA(d, c) for d in dets for c in forms]); D = [d for d in dets for c in forms]
    per = [stats.spearmanr(np.array([x[c] for c in forms]), np.array([FA(d, c) for c in forms])).statistic for d in dets]
    fe = fixed_effects(X, logit(Y), D)
    return {"pooled_spearman": float(stats.spearmanr(X, Y).statistic), "pooled_pearson": float(stats.pearsonr(X, Y).statistic),
            "mean_detector_spearman": float(np.mean(per)), "fe_partial_r2": fe["partial_r2"], "fe_t": fe["t"]}


out = {"threshold_scan": {}, "band_scan": {}, "matched_contrasts": {}, "spectra": {}}
TS = np.round(np.arange(0.02, 0.46, 0.01), 2)
for tag in ("native", "view"):
    sc, bc = [], []
    for t in TS:
        u = ehf_from_rad(npz[f"cdf_{tag}_untreated_rad"], t); xx = {c: mean_log_loss(ehf_from_rad(npz[f"cdf_{tag}_{c}_rad"], t), u) for c in FORMS}
        x = {c: v[0] for c, v in xx.items()}; r = corr_block(x, FORMS, PUB); r["t"] = float(t); r["loss"] = x; r["n_excluded"] = {c: v[1] for c, v in xx.items()}; sc.append(r)
        if t + 0.1 <= 0.5:
            ub = ehf_from_rad(npz[f"cdf_{tag}_untreated_rad"], t, t + 0.1)
            xx = {c: mean_log_loss(ehf_from_rad(npz[f"cdf_{tag}_{c}_rad"], t, t + 0.1), ub) for c in FORMS}; xb = {c: v[0] for c, v in xx.items()}
            rb = corr_block(xb, FORMS, PUB); rb["band"] = [float(t), float(t + 0.1)]; rb["loss"] = xb; rb["n_excluded"] = {c: v[1] for c, v in xx.items()}; bc.append(rb)
    out["threshold_scan"][tag] = sc; out["band_scan"][tag] = bc

# ---- matched contrasts (FA differences, percentage points, over the 17 published detectors)
LV = lambda c: res["loss_per_form"]["lapvar_native"][c]["mean"]; EH = lambda c: res["loss_per_form"]["ehf0.25_native"][c]["mean"]; MD = lambda c: res["loss_per_form"]["mad_native"][c]["mean"]
CON = [("fl06 - bil9", "fl06", "bil9", "same bilateral kernel class (d 9, sigma ~48-50), applied inside the face hull only vs the whole crop"),
       ("fl12 - bil21", "fl12", "bil21", "face-local bilateral (d ~19, sigma ~96) vs whole-crop bilateral (21, 100, 100)"),
       ("fl12 - bil15", "fl12", "bil15", "face-local bilateral (d ~19, sigma ~96) vs whole-crop bilateral (15, 80, 80)"),
       ("bil21 - gblend", "bil21", "gblend", "edge-preserving bilateral vs uniform 50% Gaussian blend with the same E_hf(0.25) loss"),
       ("bil15 - gblend", "bil15", "gblend", "edge-preserving bilateral that removes LESS high-frequency energy than the Gaussian blend"),
       ("bil9 - median5", "bil9", "median5", "bilateral that removes LESS high-frequency energy than the 5x5 median"),
       ("fl06 - median5", "fl06", "median5", "face-local bilateral that removes LESS high-frequency energy than the 5x5 median")]
for lab, a, b, why in CON:
    d = np.array([FA(k, a) - FA(k, b) for k in PUB]); dn = np.array([FA(k, a) - FA(k, b) for k in PUB if k != "npr"])
    w = stats.wilcoxon(d, alternative="two-sided"); wn = stats.wilcoxon(dn, alternative="two-sided")
    out["matched_contrasts"][lab] = {"why": why, "loss_a": {"ehf0.25": EH(a), "lapvar_hull": LV(a), "mad_hull": MD(a)}, "loss_b": {"ehf0.25": EH(b), "lapvar_hull": LV(b), "mad_hull": MD(b)},
                                     "delta_fa": {k: float(FA(k, a) - FA(k, b)) for k in PUB}, "n_positive": int((d > 0).sum()), "n_negative": int((d < 0).sum()), "median_delta": float(np.median(d)),
                                     "wilcoxon_p": float(w.pvalue), "excluding_npr": {"n_positive": int((dn > 0).sum()), "median_delta": float(np.median(dn)), "wilcoxon_p": float(wn.pvalue)}}

# ---- spectra: ratio of mean radial spectra, form / untreated (view256, eight forms; native, seven forms)
for tag in ("native", "view"):
    u = npz[f"cdf_{tag}_untreated_rad"].mean(0); sp = {c: (npz[f"cdf_{tag}_{c}_rad"].mean(0) / u).tolist() for c in FORMS}
    ua = npz[f"ali_{tag}_untreated_rad"].mean(0); sp.update({c: (npz[f"ali_{tag}_{c}_rad"].mean(0) / ua).tolist() for c in ALIFORMS})
    out["spectra"][tag] = {"bins_left_edge": RBINS[:-1].tolist(), "ratio": sp, "untreated_mean_spectrum_celebdf": u.tolist(), "untreated_mean_spectrum_commercial": ua.tolist()}
(HERE / "bandenergy_extra.json").write_text(json.dumps(out, indent=1))

# ---- markdown
L = ["### Threshold scan (7 Celeb-DF forms, 17 detectors): E_hf(t) loss as predictor of FA", "",
     "| t (c/px) | pooled Spearman native | mean det. Spearman native | FE partial R2 native | pooled Spearman view256 | mean det. Spearman view256 | FE partial R2 view256 |", "|---|---|---|---|---|---|---|"]
for a, b in zip(out["threshold_scan"]["native"], out["threshold_scan"]["view"]):
    if round(a["t"] * 100) % 5 == 0 or a["t"] in (0.02, 0.03):
        L.append(f"| {a['t']:.2f} | {a['pooled_spearman']:+.3f} | {a['mean_detector_spearman']:+.3f} | {a['fe_partial_r2']:.3f} | {b['pooled_spearman']:+.3f} | {b['mean_detector_spearman']:+.3f} | {b['fe_partial_r2']:.3f} |")
best = max(out["threshold_scan"]["native"], key=lambda r: r["fe_partial_r2"]); bestv = max(out["threshold_scan"]["view"], key=lambda r: r["fe_partial_r2"])
L += ["", f"Best threshold by FE partial R2: native t={best['t']:.2f} (R2 {best['fe_partial_r2']:.3f}, pooled rho {best['pooled_spearman']:+.3f}); "
          f"view256 t={bestv['t']:.2f} (R2 {bestv['fe_partial_r2']:.3f}, pooled rho {bestv['pooled_spearman']:+.3f}).", "",
      "### Band scan (energy in [t, t+0.1)), native", "", "| band | pooled Spearman | mean det. Spearman | FE partial R2 |", "|---|---|---|---|"]
for r in out["band_scan"]["native"]:
    if round(r["band"][0] * 100) % 5 == 0 or r["band"][0] in (0.02, 0.03):
        L.append(f"| [{r['band'][0]:.2f}, {r['band'][1]:.2f}) | {r['pooled_spearman']:+.3f} | {r['mean_detector_spearman']:+.3f} | {r['fe_partial_r2']:.3f} |")
L += ["", "### Matched-form contrasts (FA difference in percentage points, 17 published detectors; Wilcoxon signed-rank)", "",
      "| contrast | what differs | in-face loss a vs b (E_hf0.25 box / Laplacian hull / mean abs change hull) | detectors with dFA > 0 | median dFA | p | excl. NPR: n>0, median, p |", "|---|---|---|---|---|---|---|"]
for lab, r in out["matched_contrasts"].items():
    la, lb = r["loss_a"], r["loss_b"]; e = r["excluding_npr"]
    L.append(f"| {lab} | {r['why']} | {la['ehf0.25']:.2f}/{la['lapvar_hull']:.2f}/{la['mad_hull']:.1f} vs {lb['ehf0.25']:.2f}/{lb['lapvar_hull']:.2f}/{lb['mad_hull']:.1f} | "
             f"{r['n_positive']}/17 | {r['median_delta']:+.1f} | {r['wilcoxon_p']:.2g} | {e['n_positive']}/16, {e['median_delta']:+.1f}, {e['wilcoxon_p']:.2g} |")
(HERE / "bandenergy_extra.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))

# ---- supplementary figure: (a) spectra ratio per form, (b) threshold scan, (c) matched contrasts per detector
GEN = "#56B4E9"; FAMC = {"cnn": FS.CNN, "clip": FS.CLIP, "gen": GEN}; fam = res["family"]
NAME = {"bil9": "bilateral d9", "bil15": "bilateral d15", "bil21": "bilateral d21", "median5": "median 5", "gblend": "Gaussian blend", "fl06": "face-local 6%", "fl12": "face-local 12%", "Smoothing_90": "service S-90"}
COL = {"bil9": "#9ecae1", "bil15": "#4292c6", "bil21": "#08519c", "fl06": "#fdae6b", "fl12": "#e6550d", "gblend": "#009E73", "median5": "#CC79A7", "Smoothing_90": "#222222"}
fig, axs = plt.subplots(1, 3, figsize=(FS.FULL, 2.6), layout="constrained", gridspec_kw={"width_ratios": [1.1, 1.0, 1.4]})
ax = axs[0]; lo = RBINS[:-1]; m = lo <= 0.5
for c in FORMS + ["Smoothing_90"]:
    ax.plot(lo[m], np.log(np.array(out["spectra"]["view"]["ratio"][c])[m]), color=COL[c], lw=1.0 if c != "Smoothing_90" else 0.9, ls="-" if c != "Smoothing_90" else (0, (3, 1.5)), label=NAME[c])
ax.axhline(0, color=FS.MUTED, lw=0.5); ax.axvline(0.25, color=FS.GRID, lw=0.6)
ax.text(0.255, 0.22, "t = 0.25", fontsize=FS.FS_NOTE, color=FS.MUTED, va="bottom")
ax.set_xlabel("radial frequency (cycles/pixel, 256-px view)"); ax.set_ylabel("log power ratio, form / untreated"); ax.set_title("(a) where each form removes energy", loc="left")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.3), ncol=3, fontsize=FS.FS_NOTE - 0.5, handlelength=1.0, labelspacing=0.2, columnspacing=0.8)
ax = axs[1]
for tag, ls, lab in (("native", "-", "stored frame"), ("view", (0, (3, 1.5)), "256-px view")):
    sc = out["threshold_scan"][tag]
    ax.plot([r["t"] for r in sc], [r["pooled_spearman"] for r in sc], color=FS.INK, ls=ls, lw=1.0, label=f"pooled Spearman, {lab}")
    ax.plot([r["t"] for r in sc], [r["fe_partial_r2"] for r in sc], color=FS.OURS, ls=ls, lw=1.0, label=f"partial R$^2$ (detector offsets), {lab}")
ax.axhline(0, color=FS.MUTED, lw=0.5); ax.set_ylim(-0.5, 1.0); ax.set_xlabel("threshold t (cycles/pixel)"); ax.set_ylabel("FA vs E$_{hf}$(t) loss, 7 forms")
ax.set_title("(b) no threshold predicts accusation", loc="left"); ax.legend(loc="upper left", fontsize=FS.FS_NOTE - 0.5, handlelength=1.4, labelspacing=0.2)
ax = axs[2]; pairs = [("fl06 - bil9", "face-local 6%\n$-$ bilateral d9\nsame kernel"), ("bil21 - gblend", "bilateral d21\n$-$ Gaussian blend\nsame E$_{hf}$ loss"), ("bil9 - median5", "bilateral d9\n$-$ median 5\nless E$_{hf}$ loss")]
rng = np.random.default_rng(0)
for j, (lab, txt) in enumerate(pairs):
    d = out["matched_contrasts"][lab]["delta_fa"]; xs = j + rng.uniform(-0.18, 0.18, len(PUB))
    for k, x in zip(PUB, xs):
        ax.scatter(x, d[k], s=11, color=FAMC[fam[k]], marker={"cnn": "o", "clip": "s", "gen": "^"}[fam[k]], edgecolor="white", linewidth=0.3, zorder=3)
    ax.hlines(out["matched_contrasts"][lab]["median_delta"], j - 0.28, j + 0.28, color=FS.INK, lw=1.0, zorder=4)
    ax.text(j, -108, txt, ha="center", va="top", fontsize=FS.FS_NOTE - 0.5, color=FS.INK, linespacing=1.1)
ax.axhline(0, color=FS.MUTED, lw=0.5); ax.set_xlim(-0.5, 2.5); ax.set_ylim(-100, 100); ax.set_xticks([]); ax.set_ylabel("FA difference (points)")
ax.set_title("(c) matched forms", loc="left")
h = [plt.Line2D([], [], ls="", marker=mk, color=FAMC[f], markersize=4, label=n) for f, mk, n in (("cnn", "o", "face-forgery CNN"), ("gen", "^", "generated-image"), ("clip", "s", "CLIP-based"))]
ax.legend(handles=h, loc="lower right", fontsize=FS.FS_NOTE - 0.5, handlelength=1.0, labelspacing=0.2)
FS.save(fig, HERE / "fig_bandenergy_supp"); print("supp figure written")
