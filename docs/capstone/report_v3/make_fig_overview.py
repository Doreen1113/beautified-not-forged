"""Figure 2 of the two-column report: the method at the full text width (18.13 cm, IEEEtran a4 \\textwidth), images and
shapes instead of prose. Top: (1) training pairs with exact footprints, (2) the model, (3) its outputs on two held-out
images. Bottom: the three tests that could fail and the on-device timing, as headline numbers. Every detail sentence is in
the caption. Tiles: make_tiles_method.py (method_*), make_tiles_model.py (model_ev16.png); numbers: figs/method_numbers.json
(main model clipe5 seed 20260929) and the report's tables (exposure P0 54.2 -> P2 11.7, restoration 94.0 vs heat maps
45-57, blind matching 50.8-52.8, iPhone median 0.59 s).
python make_fig_overview.py  -> figs/fig_overview.{html,pdf,png}"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent; OUT = HERE / "figs"
N = json.loads((OUT / "method_numbers.json").read_text(encoding="utf-8"))


def composed_sentence():
    """The sentence of panel 3, written by the project's composer (explain_v2_en.compose_en) from the main model's record
    and checked by the shipped gate (gate_v3.gate_check_v3_en: H1-H6, G7-G9); the figure is not drawn if a check fails."""
    nl = Path(r"C:\My_Project\AIGC\results\research\explain_vlm_20261012\nl_v5")
    sys.path.insert(0, str(nl)); sys.path.insert(0, str(nl.parent))
    import explain_v2_en as E
    import gate_v3 as G
    f = N["fake"]; pm, ops, pr = f["part_means"], f["ops_eye_contour_tone_texture"], f["p_real_fake_filter"]
    rec = {"decision": "fake", "probabilities": {"real": round(pr[0], 2), "fake": round(pr[1], 2), "filter": round(pr[2], 2)},
           "named_parts": [f["named"]], "whole_face": all(pm[k] >= 0.5 for k in ("eyes", "nose", "mouth")),
           "evidence_mean_per_part": {k: round(pm[k], 2) for k in ("eyes", "nose", "mouth", "skin", "contour")},
           "operation_threshold": 0.5,
           "operations": dict(zip(("eye_enlargement", "face_slimming", "skin_brightening", "skin_smoothing"), [round(x, 2) for x in ops]))}
    text = E.compose_en(rec)
    R = G.gate_check_v3_en(rec, text, "general")
    assert not R["any_v3"], R["why"]
    (OUT / "overview_sentence.json").write_text(json.dumps({"record": rec, "text": text, "gate_v3": {k: R[k] for k in R if isinstance(R[k], bool)}}, indent=1), encoding="utf-8")
    return text


SENTENCE = composed_sentence()
W_CM = 18.13; PX = 96 / 2.54
fk, fl = N["fake"], N["filter"]
assert fk["named"] == "nose" and fl["named"] == "eyes", (fk["named"], fl["named"])
fk_p = fk["p_real_fake_filter"][1]; fl_p = fl["p_real_fake_filter"][2]; fk_ev = fk["part_means"]["nose"]


def img(src, w, h=None, cls=""):
    h = h or w
    return f'<img class="t {cls}" src="{src}" style="width:{w}cm;height:{h}cm">'


ARR = '<svg class="ar" viewBox="0 0 14 10"><path d="M0 5h9M7 1.2l5 3.8-5 3.8" fill="none" stroke="#374151" stroke-width="1.5"/></svg>'

# ---------------------------------------------------------------- (2) the model as a drawing: tokens, 24 blocks, heads
def model_svg():
    s = 37.8                     # px per cm
    W, H = 4.62 * s, 3.1 * s
    g = []
    def txt(x, y, v, size=10.7, anchor="start", fill="#374151", bold=False):
        return f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{" font-weight=\"700\"" if bold else ""}>{v}</text>'
    # tokens (CLS first)
    g.append(txt(0.32 * s, 0.26 * s, "257", 9.3, "middle"))
    for i in range(7):
        y = 0.42 * s + i * 0.3 * s
        if i == 5:
            g.append(txt(0.32 * s, y + 0.22 * s, "&#8942;", 10.7, "middle", "#6b7280")); continue
        g.append(f'<rect x="{0.14*s:.1f}" y="{y:.1f}" width="{0.36*s:.1f}" height="{0.24*s:.1f}" rx="2" fill="{"#9aa3ad" if i == 0 else "#e3e7ec"}" stroke="#8c939b" stroke-width="0.6"/>')
    g.append(f'<path d="M{0.56*s:.1f} {1.32*s:.1f}h{0.26*s:.1f}M{0.76*s:.1f} {1.22*s:.1f}l{0.08*s:.1f} {0.1*s:.1f}l-{0.08*s:.1f} {0.1*s:.1f}" fill="none" stroke="#374151" stroke-width="1.3"/>')
    # 24 blocks as a stack, a LoRA adapter on each
    x0, y0, bw, bh, dy = 0.98 * s, 0.42 * s, 1.85 * s, 0.3 * s, 0.3 * s
    for k in range(6, -1, -1):
        x, y = x0 + k * 0.06 * s, y0 + k * dy
        g.append(f'<path d="M{x:.1f} {y+bh:.1f} L{x+0.12*s:.1f} {y:.1f} H{x+bw+0.12*s:.1f} L{x+bw:.1f} {y+bh:.1f} Z" fill="{"#e3e8ee" if k == 0 else "#eef1f5"}" stroke="#8c939b" stroke-width="0.6"/>')
        g.append(f'<rect x="{x+bw-0.34*s:.1f}" y="{y+0.06*s:.1f}" width="{0.3*s:.1f}" height="{bh-0.12*s:.1f}" rx="2" fill="#0f4d92"/>')
    g.append(txt(x0 + 0.18 * s, y0 + 0.23 * s, "ViT-L/14", 10.7, "start", "#1f2937", True))
    g.append(txt(x0 + bw * 0.55, y0 + 7 * dy + 0.34 * s, "24 blocks, frozen", 10.7, "middle"))
    g.append(txt(x0 + bw + 0.3 * s, y0 + 0.05 * s, "LoRA", 10.7, "start", "#0f4d92", True))
    g.append(txt(x0 + bw + 0.3 * s, y0 + 0.42 * s, "r = 16", 10.7, "start", "#0f4d92"))
    # outputs
    xs = x0 + bw + 0.48 * s
    g.append(f'<path d="M{xs:.1f} {1.62*s:.1f}h{0.3*s:.1f}M{xs+0.22*s:.1f} {1.52*s:.1f}l{0.08*s:.1f} {0.1*s:.1f}l-{0.08*s:.1f} {0.1*s:.1f}" fill="none" stroke="#374151" stroke-width="1.3"/>')
    g.append(txt(xs + 0.38 * s, 1.45 * s, "CLS", 10.7))
    g.append(txt(xs + 0.38 * s, 1.82 * s, "+ 256", 10.7))
    return f'<svg viewBox="0 0 {W:.0f} {H:.0f}" style="width:4.62cm;height:3.1cm;display:block">{"".join(g)}</svg>'



html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Method overview</title>
<style>
  @page {{ margin: 0; }}
  :root {{ --ink:#1f2937; --muted:#6b7280; --line:#d6dbe3; --panel:#f6f8fb; --nn:#0f4d92; --code:#1b7f4c; --chk:#6a3d9a;
          --fake:#d55e00; --real:#009e73; --beau:#c98a00; --m:#26a6dc; }}
  * {{ box-sizing:border-box; }}
  html, body {{ margin:0; padding:0; background:#fff; }}
  body {{ width:{W_CM}cm; font-family:Arial, "Liberation Sans", Helvetica, sans-serif; color:var(--ink); font-size:8.5pt;
         line-height:1.22; padding:0.24cm 0 0.04cm; overflow:hidden; }}
  .top {{ display:grid; grid-template-columns:6.75cm 0.32cm 5.0cm 0.32cm 5.74cm; align-items:stretch; }}
  .bot {{ display:grid; grid-template-columns:13.38cm 4.43cm; column-gap:0.32cm; margin-top:0.42cm; }}
  .panel {{ position:relative; background:var(--panel); border:0.45pt solid var(--line); border-radius:0.24cm; padding:0.42cm 0.2cm 0.16cm; }}
  .chip {{ position:absolute; top:-0.2cm; left:0.2cm; font-size:8.5pt; font-weight:700; color:#fff; padding:0.04cm 0.22cm; border-radius:0.3cm; white-space:nowrap; }}
  .nn > .chip {{ background:var(--nn); }} .ink > .chip {{ background:#374151; }} .chk > .chip {{ background:var(--chk); }} .code > .chip {{ background:var(--code); }}
  .join {{ display:flex; align-items:center; justify-content:center; }}
  .ar {{ width:0.3cm; height:0.22cm; display:block; }}
  .t {{ display:block; object-fit:cover; border-radius:0.09cm; box-shadow:0 0.6pt 2pt rgba(0,0,0,.30); }}
  .b-real {{ outline:1.4pt solid var(--real); }} .b-fake {{ outline:1.4pt solid var(--fake); }} .b-beau {{ outline:1.4pt solid var(--beau); }}
  .card {{ background:#fff; border:0.45pt solid var(--line); border-radius:0.14cm; padding:0.09cm 0.12cm 0.07cm; margin-bottom:0.11cm; }}
  .card:last-child {{ margin-bottom:0; }}
  .strip {{ display:flex; align-items:flex-end; gap:0.06cm; }}
  .cell {{ display:flex; flex-direction:column; align-items:center; }}
  .lab {{ font-size:8pt; line-height:1.05; margin-top:0.05cm; text-align:center; white-space:nowrap; }}
  .lab.real {{ color:var(--real); font-weight:700; }} .lab.fake {{ color:var(--fake); font-weight:700; }} .lab.beau {{ color:var(--beau); font-weight:700; }} .lab.m {{ color:var(--m); font-weight:700; }}
  .mid {{ align-self:center; margin-bottom:0.32cm; }}
  .foot {{ display:flex; justify-content:space-between; align-items:baseline; gap:0.2cm; font-size:8pt; color:var(--muted); margin-top:0.05cm; }}
  .foot b {{ color:var(--ink); font-size:8.5pt; white-space:nowrap; }}
  .foot span {{ white-space:nowrap; }}
  .heads {{ display:grid; grid-template-columns:1fr 1.28cm; column-gap:0.12cm; margin-top:0.04cm; align-items:start; }}
  .pill {{ display:block; background:#fff; border:0.7pt solid var(--nn); border-radius:0.12cm; padding:0.035cm 0.1cm; font-size:8pt; line-height:1.15; margin-bottom:0.07cm; }}
  .pill b {{ color:var(--nn); }}
  .pill.aux {{ border-color:#9db4d6; color:var(--muted); }}
  .evmap {{ text-align:center; font-size:8pt; line-height:1.05; }}
  .evmap img {{ width:1.28cm; height:1.28cm; display:block; border-radius:0.06cm; margin-bottom:0.04cm; }}
  .mnote {{ font-size:8pt; color:var(--muted); margin-top:0.02cm; }}
  .mnote b {{ color:var(--nn); }}
  .ex {{ display:grid; grid-template-columns:1.5cm 1.5cm 1fr; column-gap:0.1cm; align-items:center; margin-bottom:0.13cm; }}
  .verdict {{ font-size:8pt; line-height:1.25; }}
  .verdict .v {{ display:inline-block; font-size:8pt; font-weight:700; padding:0.01cm 0.12cm; white-space:nowrap; border-radius:0.3cm; margin-bottom:0.04cm; }}
  .v.fake {{ color:var(--fake); background:#fbe8dc; }} .v.beau {{ color:#9a6a00; background:#fbf0d6; }}
  .verdict b {{ font-weight:700; }}
  .says {{ background:#fff; border:0.45pt solid var(--line); border-left:2.4pt solid var(--code); border-radius:0.1cm; padding:0.06cm 0.12cm; font-size:8pt; line-height:1.22; }}
  .says .badge {{ display:inline-block; font-size:7.6pt; color:var(--code); border:0.5pt solid var(--code); border-radius:0.25cm; padding:0 0.12cm; margin-top:0.04cm; }}
  .tests {{ display:grid; grid-template-columns:repeat(3, 1fr); column-gap:0.18cm; }}
  .metric {{ background:#fff; border:0.45pt solid var(--line); border-top:2.4pt solid var(--chk); border-radius:0.12cm; padding:0.08cm 0.14cm 0.09cm; }}
  .metric .k {{ font-size:8pt; font-weight:700; color:var(--chk); }}
  .metric .big {{ font-size:15pt; font-weight:700; line-height:1.15; letter-spacing:-0.2pt; margin:0.02cm 0; white-space:nowrap; }}
  .metric .big small {{ font-size:9pt; font-weight:700; color:var(--muted); }}
  .metric .d {{ font-size:8pt; color:var(--muted); line-height:1.2; }}
  .metric .d b {{ color:var(--ink); }}
  .metric.dev {{ border-top-color:var(--code); }} .metric.dev .k {{ color:var(--code); }}
  .good {{ color:var(--real); }} .bad {{ color:var(--fake); }}
  .legend {{ font-size:8pt; color:var(--muted); margin-top:0.16cm; white-space:nowrap; }}
  .legend i {{ display:inline-block; width:0.26cm; height:0.18cm; border-radius:0.05cm; vertical-align:-0.03cm; margin:0 0.08cm 0 0.32cm; }}
  .legend i:first-child {{ margin-left:0; }}
  .legend i.o {{ background:#fff; border:1.4pt solid; }}
</style></head><body>

<div class="top">
  <div class="panel nn"><div class="chip">1&nbsp; Training pairs with exact footprints</div>
    <div class="card">
      <div class="strip">
        <div class="cell">{img("method_ffpp_real.png", 1.25, 1.25, "b-real")}<div class="lab real">genuine</div></div>
        <div class="cell mid">{ARR}</div>
        <div class="cell">{img("method_ffpp_filter.png", 1.25, 1.25, "b-beau")}<div class="lab beau">beautified</div></div>
        <div class="cell">{img("method_ffpp_fake.png", 1.25, 1.25, "b-fake")}<div class="lab fake">forged</div></div>
        <div class="cell">{img("method_ffpp_fake_filter.png", 1.25, 1.25, "b-fake")}<div class="lab fake">+ beautified</div></div>
      </div>
      <div class="foot"><span><b style="font-size:8pt">both classes see smoothing</b></span><b>41,512 frames</b></div>
    </div>
    <div class="card">
      <div class="strip">
        <div class="cell">{img("method_vendor_O.png", 0.86, 1.03, "b-real")}<div class="lab">O</div></div>
        <div class="cell">{img("method_vendor_R.png", 0.86, 1.03, "b-beau")}<div class="lab">R</div></div>
        <div class="cell mid">{ARR}</div>
        <div class="cell">{img("method_comp_eye.png", 0.86, 1.03, "b-beau")}<div class="lab">eye</div></div>
        <div class="cell">{img("method_comp_contour.png", 0.86, 1.03, "b-beau")}<div class="lab">contour</div></div>
        <div class="cell">{img("method_comp_tone.png", 0.86, 1.03, "b-beau")}<div class="lab">tone</div></div>
        <div class="cell">{img("method_comp_texture.png", 0.86, 1.03, "b-beau")}<div class="lab">texture</div></div>
      </div>
      <div class="foot"><span>one render &rarr; 4 operations</span><b>50,112 items</b></div>
    </div>
    <div class="card">
      <div class="strip">
        <div class="cell">{img("method_part_x0.png", 1.25, 1.25, "b-real")}<div class="lab">original</div></div>
        <div class="cell mid">{ARR}</div>
        <div class="cell">{img("method_part_x.png", 1.25, 1.25, "b-fake")}<div class="lab fake">donor nose</div></div>
        <div class="cell" style="margin-left:0.1cm">{img("method_part_M.png", 1.25, 1.25)}<div class="lab m">footprint M</div></div>
      </div>
      <div class="foot"><span>part-level: outside <b style="font-size:8pt;color:#26a6dc">M</b> untouched</span><b>61,510 edits</b></div>
    </div>
  </div>
  <div class="join">{ARR}</div>
  <div class="panel nn"><div class="chip">2&nbsp; One backbone, four heads</div>
    {model_svg()}
    <div class="heads">
      <div>
        <span class="pill"><b>forged f, beautified b</b><br>P(forged) = &sigma;(f), the score never reads b</span>
        <span class="pill"><b>4 operations</b> eye, contour, tone, texture</span>
        <span class="pill aux">4 measured amounts, auxiliary</span>
      </div>
      <div class="evmap"><img src="model_ev16.png"><b style="color:#0f4d92">evidence</b><br>16&times;16, vs <span style="color:#26a6dc;font-weight:700">M</span></div>
    </div>
    <div class="mnote"><b>3.2 M</b> of 306 M parameters trained</div>
  </div>
  <div class="join">{ARR}</div>
  <div class="panel ink" style="display:flex;flex-direction:column;justify-content:space-around"><div class="chip">3&nbsp; Outputs on held-out images</div>
    <div class="ex">
      {img("method_out_fake_in.png", 1.5, 1.5, "b-fake")}{img("method_out_fake_ev.png", 1.5, 1.5)}
      <div class="verdict"><span class="v fake">forged {fk_p:.2f}</span><br>evidence:<br><b>nose</b></div>
    </div>
    <div class="ex">
      {img("method_out_filter_in.png", 1.5, 1.8, "b-beau")}{img("method_out_filter_ev.png", 1.5, 1.8)}
      <div class="verdict"><span class="v beau">beautified {fl_p:.2f}</span><br>evidence:<br><b>eyes</b><br><span style="color:#6b7280">unseen service</span></div>
    </div>
    <div class="says">{SENTENCE}<br><span class="badge">composed by code, checked</span></div>
  </div>
</div>

<div class="bot">
  <div class="panel chk"><div class="chip">4&nbsp; Three tests that could have failed</div>
    <div class="tests">
      <div class="metric"><div class="k">Exposure</div><div class="big"><span class="bad">54%</span> <small>&rarr;</small> <span class="good">12%</span></div>
        <div class="d">smoothed genuine faces accused: no smoothing in training vs <b>smoothing seen by both classes</b></div></div>
      <div class="metric"><div class="k">Restoration</div><div class="big"><span class="good">94%</span> <small>vs 45&ndash;57%</small></div>
        <div class="d">forgery decisions removed by restoring the marked region: <b>our evidence head</b> vs heat maps</div></div>
      <div class="metric"><div class="k">Matching</div><div class="big"><span class="bad">51&ndash;53%</span> <small>&asymp; coin flip</small></div>
        <div class="d">a judge pairs a VLM description with its own photo; so <b>code writes every sentence</b></div></div>
    </div>
  </div>
  <div class="panel code"><div class="chip">5&nbsp; On the device</div>
    <div class="metric dev"><div class="k">Browser, iPhone</div><div class="big">0.59 s <small>per photo</small></div>
      <div class="d">landmarks, model, part and sentences run in the page; <b>nothing is uploaded</b></div></div>
  </div>
</div>

<div class="legend"><i class="o" style="border-color:#009e73"></i>genuine<i class="o" style="border-color:#c98a00"></i>beautified<i class="o" style="border-color:#d55e00"></i>forged<i style="background:#26a6dc"></i>exact footprint M<i style="background:#0f4d92"></i>trained (LoRA, heads)<i style="background:#e3e7ec;border:0.5pt solid #8c939b"></i>frozen</div>
</body></html>
"""
(OUT / "fig_overview.html").write_text(html, encoding="utf-8")
subprocess.run([sys.executable, str(HERE / "render_html_fig.py"), str(OUT / "fig_overview.html"), str(round(W_CM * PX))], check=True)
print("fig_overview ok")
