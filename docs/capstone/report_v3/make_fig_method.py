"""Figure: the method on one page (figs/fig_method.html -> .pdf/.png via render_html_fig.py). Three training-supervision
sources with exact footprints, the model with its heads and loss, the main model's outputs on two held-out images, the
three tests that could fail, and the browser. Tiles from make_tiles_method.py; numbers from figs/method_numbers.json
(main model clipe5 seed 20260929) and the report text (counts and the three test results).
python make_fig_method.py"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent; OUT = HERE / "figs"
N = json.loads((OUT / "method_numbers.json").read_text(encoding="utf-8"))
WIDTH_CM = 14.66; PX = 96 / 2.54

fk = N["fake"]; fl = N["filter"]
CLS = ["real", "forged", "beautified"]
fk_cls = CLS[int(max(range(3), key=lambda i: fk["p_real_fake_filter"][i]))]; fk_p = max(fk["p_real_fake_filter"])
fl_cls = CLS[int(max(range(3), key=lambda i: fl["p_real_fake_filter"][i]))]; fl_p = max(fl["p_real_fake_filter"])
OPS = ["eye", "contour", "tone", "texture"]
ops = lambda v: " &middot; ".join(f"{o}&thinsp;{x:.2f}" for o, x in zip(OPS, v))

ARROW = '<div class="arrow"><svg viewBox="0 0 16 10"><path d="M0 5h11M9 1l5 4-5 4" fill="none" stroke="#1f2937" stroke-width="1.6"/></svg></div>'
ARROW_B = '<div class="arrow"><svg viewBox="0 0 16 10"><path d="M0 5h11M9 1l5 4-5 4" fill="none" stroke="#0f4d92" stroke-width="1.8"/></svg></div>'


def tile(src, w, h, cls="", extra=""):
    return f'<img class="t {cls}" src="{src}" style="width:{w}cm;height:{h}cm;{extra}">'


def col(w, inner):
    return f'<div class="col" style="width:{w}cm">{inner}</div>'


html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Method overview</title>
<style>
  @page {{ margin: 0; }}
  :root {{ --ink:#1f2937; --muted:#6b7280; --line:#d6dbe3; --nn:#0f4d92; --code:#1b7f4c; --chk:#6a3d9a; --chk-bg:#efe9f8;
          --fake:#d55e00; --real:#009e73; --beau:#c98a00; --m:#26a6dc; }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin:0; padding:0; background:#fff; }}
  body {{ width:{WIDTH_CM}cm; font-family: Arial, "Liberation Sans", Helvetica, sans-serif; color:var(--ink); font-size:8.5pt; line-height:1.22;
         padding:0.24cm 0 0.02cm 0; overflow:hidden; }}
  .row {{ display:flex; gap:0.28cm; margin-bottom:0.36cm; align-items:stretch; }}
  .panel {{ position:relative; border-radius:0.22cm; background:#f7f8fb; border:0.4pt solid var(--line); padding:0.44cm 0.22cm 0.18cm; overflow:hidden; }}
  .panel > .chip {{ position:absolute; top:-0.19cm; left:0.22cm; font-size:8.5pt; font-weight:700; color:#fff; padding:0.045cm 0.22cm; border-radius:0.3cm; white-space:nowrap; }}
  .panel {{ overflow:visible; }}
  .nn > .chip {{ background:var(--nn); }} .code > .chip {{ background:var(--code); }} .chk > .chip {{ background:var(--chk); }} .ink > .chip {{ background:#374151; }}
  .flow {{ display:flex; align-items:flex-start; gap:0.08cm; }}
  .col {{ display:flex; flex-direction:column; align-items:center; flex:none; }}
  .t {{ display:block; object-fit:cover; border-radius:0.1cm; box-shadow:0 1px 2.5px rgba(0,0,0,.28); }}
  .t.b-real {{ outline:1.5pt solid var(--real); }} .t.b-fake {{ outline:1.5pt solid var(--fake); }} .t.b-beau {{ outline:1.5pt solid var(--beau); }}
  .cap {{ margin-top:0.08cm; text-align:center; font-size:8pt; line-height:1.12; width:100%; }}
  .cap b.real {{ color:var(--real); }} .cap b.fake {{ color:var(--fake); }} .cap b.beau {{ color:var(--beau); }}
  .arrow {{ flex:none; width:0.36cm; display:flex; align-items:center; justify-content:center; }}
  .arrow svg {{ width:0.36cm; height:0.26cm; }}
  .note {{ font-size:8pt; color:var(--muted); line-height:1.2; }}
  .note b {{ color:var(--ink); font-weight:700; }}
  .mlab {{ font-size:7.5pt; color:var(--m); font-weight:700; text-align:center; margin-top:0.03cm; }}
  .node {{ background:#fff; border:0.5pt solid var(--line); border-radius:0.12cm; padding:0.05cm 0.1cm; font-size:7.8pt; text-align:center; line-height:1.18; width:100%; }}
  .bb {{ width:2.5cm; flex:none; background:linear-gradient(90deg,#d4e3f6,#9dbde5); border:0.6pt solid var(--nn); border-radius:0.14cm; padding:0.12cm 0.1cm; color:var(--nn); text-align:center; font-size:7.8pt; line-height:1.2; }}
  .bb b {{ font-size:9pt; display:block; margin-bottom:0.04cm; }}
  .heads {{ display:flex; flex-direction:column; gap:0.09cm; flex:none; width:6.3cm; }}
  .head {{ background:#fff; border:0.6pt solid var(--nn); border-radius:0.12cm; padding:0.06cm 0.13cm; font-size:8pt; line-height:1.2; }}
  .head b {{ color:var(--nn); }}
  .ex {{ display:flex; align-items:center; gap:0.1cm; }}
  .ex .txt {{ font-size:8pt; line-height:1.2; flex:1; }}
  .ex .txt b.c {{ font-size:9pt; }}
  .tests {{ display:flex; flex-direction:column; gap:0.1cm; }}
  .test {{ display:grid; grid-template-columns:1.7cm 1fr; column-gap:0.14cm; align-items:center; background:#fff; border:0.5pt solid var(--chk); border-left:3pt solid var(--chk); border-radius:0.1cm; padding:0.05cm 0.1cm; font-size:8pt; line-height:1.2; }}
  .test .k {{ font-weight:700; color:var(--chk); }}
  .test .k small {{ display:block; font-weight:400; color:var(--muted); font-size:7.3pt; line-height:1.1; }}
  .test .v b {{ color:var(--ink); }}
  .dep {{ font-size:8pt; line-height:1.22; }}
  .dep b {{ color:var(--code); }}
  .legend {{ font-size:8pt; color:var(--muted); margin-top:-0.14cm; padding-left:0.06cm; white-space:nowrap; }}
  .legend i {{ display:inline-block; width:0.26cm; height:0.18cm; border-radius:0.05cm; vertical-align:-0.03cm; margin:0 0.08cm 0 0.28cm; }}
  .legend i:first-child {{ margin-left:0; }}
  svg text {{ font-family: Arial, "Liberation Sans", Helvetica, sans-serif; }}
</style></head><body>

<!-- ============================================================ row 1: supervision -->
<div class="row">
  <div class="panel nn" style="width:4.55cm">
    <div class="chip">1 FF++ triplet, drawn on the fly</div>
    <div class="flow" style="gap:0.14cm; justify-content:center">
      {col(1.15, tile("method_ffpp_real.png", 1.15, 1.38, "b-real") + '<div class="cap"><b class="real">genuine</b></div>')}
      {col(1.15, tile("method_ffpp_filter.png", 1.15, 1.38, "b-beau") + '<div class="cap"><b class="beau">beautified</b></div>')}
      {col(1.15, tile("method_ffpp_fake.png", 1.15, 1.38, "b-fake") + '<div class="cap"><b class="fake">forged</b></div>')}
    </div>
    <div class="note" style="margin-top:0.1cm">A scripted beautification and a self-blend or observed forgery from one genuine frame; <b>the forged item is beautified too</b>, half of the time.</div>
  </div>

  <div class="panel nn" style="width:9.83cm">
    <div class="chip">2 Commercial render split into single operations</div>
    <div class="flow">
      {col(1.0, tile("method_vendor_O.png", 1.0, 1.2, "b-real") + '<div class="cap">original <i>O</i></div>')}
      {col(1.0, tile("method_vendor_R.png", 1.0, 1.2, "b-beau") + '<div class="cap">render <i>R</i></div>')}
      <div class="col" style="width:2.05cm; justify-content:center; height:1.2cm; gap:0.08cm; margin:0 0.04cm">
        <div class="node">warp <i>f</i>: optical flow <i>O</i>&rarr;<i>R</i></div>
        <div class="node">residual <i>P</i> = <i>R</i> &minus; <i>O</i>(<i>x</i>+<i>f</i>)</div>
      </div>
      {ARROW}
      {col(1.0, tile("method_comp_eye.png", 1.0, 1.2, "b-beau") + '<div class="cap">eye</div>')}
      {col(1.0, tile("method_comp_contour.png", 1.0, 1.2, "b-beau") + '<div class="cap">contour</div>')}
      {col(1.0, tile("method_comp_tone.png", 1.0, 1.2, "b-beau") + '<div class="cap">tone</div>')}
      {col(1.0, tile("method_comp_texture.png", 1.0, 1.2, "b-beau") + '<div class="cap">texture</div>')}
    </div>
    <div class="note" style="margin-top:0.08cm">Warps of <i>O</i> by <i>f</i> (eyes, elsewhere) and the low- and high-pass parts of <i>P</i>, shown as |<i>C</i>&thinsp;&minus;&thinsp;<i>O</i>| with the exact footprint <i>M</i> outlined; in sequence they rebuild <i>R</i> at 108 dB. <b>18,734 renders</b> (Tencent, Megvii) give <b>50,112</b> items; Alibaba is held out for testing.</div>
  </div>
</div>

<!-- ============================================================ row 2: part-level forgeries + model -->
<div class="row">
  <div class="panel nn" style="width:4.55cm">
    <div class="chip">3 Part-level forgery, exact <i>M</i></div>
    <div class="flow" style="gap:0.1cm; justify-content:center">
      {col(1.1, tile("method_part_x0.png", 1.1, 1.1, "b-real") + '<div class="cap">original <i>x</i><sub>0</sub></div>')}
      {ARROW}
      {col(1.1, tile("method_part_x.png", 1.1, 1.1, "b-fake") + '<div class="cap"><b class="fake">donor nose</b></div>')}
      {col(1.1, tile("method_part_M.png", 1.1, 1.1) + '<div class="cap mlab" style="margin-top:0.08cm">footprint <i>M</i></div>')}
    </div>
    <div class="note" style="margin-top:0.1cm"><b>61,510</b> on FF++ frames: eyes, nose or mouth from a donor or inpainted; outside <i>M</i> every pixel is the original's.</div>
  </div>

  <div class="panel nn" style="width:9.83cm">
    <div class="chip">4 One backbone, its heads</div>
    <div class="flow" style="align-items:center">
      <div class="bb"><b>CLIP ViT-L/14</b>frozen, LoRA rank 16 on all attention projections: 3.2 M of 306 M trained<div style="margin-top:0.08cm;font-size:7.5pt;color:#374151">browser: EfficientNet-B4, 17.6 M, same heads</div></div>
      {ARROW_B}
      <div class="heads">
        <div class="head"><b>Class logits</b> <i>f</i> (forged), <i>b</i> (beautified): P(forged)&thinsp;=&thinsp;&sigma;(<i>f</i>), P(beautified)&thinsp;=&thinsp;(1&minus;&sigma;(<i>f</i>))&thinsp;&sigma;(<i>b</i>), P(real)&thinsp;=&thinsp;(1&minus;&sigma;(<i>f</i>))(1&minus;&sigma;(<i>b</i>)). The forgery score never reads <i>b</i>.</div>
        <div class="head"><b>Operation head</b>: eye &middot; contour &middot; tone &middot; texture present or not (BCE on beautified items).</div>
        <div class="head"><b>Evidence head</b>: 1&thinsp;&times;&thinsp;1 conv on the 16&thinsp;&times;&thinsp;16 tokens, trained against <i>M</i> (BCE + Dice). The classifier does not read it, so (5) tests it.</div>
      </div>
    </div>
    <div class="note" style="margin-top:0.1cm">Loss = BCE(<i>f</i>) + BCE(<i>b</i>) + BCE(ops) + 2&thinsp;L1(amounts) + BCE(<i>m</i>,&thinsp;<i>M</i>) + Dice(<i>m</i>,&thinsp;<i>M</i>); the auxiliary amount head and the encoder are drawn in Figure&nbsp;5. AdamW 10<sup>&minus;4</sup>, 8 epochs; checkpoint chosen on validation data only.</div>
  </div>
</div>

<!-- ============================================================ row 3: outputs, tests, browser -->
<div class="row" style="margin-bottom:0.24cm">
  <div class="panel ink" style="width:4.3cm">
    <div class="chip">Main model, held-out</div>
    <div class="ex">
      {tile("method_out_fake_in.png", 0.95, 0.95, "b-fake")}{tile("method_out_fake_ev.png", 0.95, 0.95, "b-fake")}
      <div class="txt"><b class="c" style="color:var(--fake)">{fk_cls} {fk_p:.2f}</b><br>evidence: <b>{fk["named"]}</b><br><span class="note">operations all &le; {max(fk["ops_eye_contour_tone_texture"]):.2f}</span></div>
    </div>
    <div class="note" style="margin:0.04cm 0 0.12cm">FF++ test frame, nose from a donor</div>
    <div class="ex">
      {tile("method_out_filter_in.png", 0.95, 0.95, "b-beau")}{tile("method_out_filter_ev.png", 0.95, 0.95, "b-beau")}
      <div class="txt"><b class="c" style="color:var(--beau)">{fl_cls} {fl_p:.2f}</b><br>evidence: <b>{fl["named"]}</b><br><span class="note">eye {fl["ops_eye_contour_tone_texture"][0]:.2f}, others &le; {max(fl["ops_eye_contour_tone_texture"][1:]):.2f}</span></div>
    </div>
    <div class="note" style="margin-top:0.04cm">Alibaba eye render, a service never used in training</div>
  </div>

  <div class="panel chk" style="width:7.2cm">
    <div class="chip">5 Three tests that could fail</div>
    <div class="tests">
      <div class="test"><div class="k">Exposure<small>which class saw smoothing</small></div><div class="v">Smoothing seen by forged faces only: <b>54%</b> of smoothed genuine faces accused; by both classes: <b>12%</b>; by genuine only: deepfakes escape.</div></div>
      <div class="test"><div class="k">Restoration<small>is the mark the reason?</small></div><div class="v">Original pixels put back inside the marked region remove <b>94%</b> of part-level forgery decisions; a post-hoc heat map: about half.</div></div>
      <div class="test"><div class="k">Matching<small>does text carry the image?</small></div><div class="v">A judge pairs a VLM description with its own photo about as often as a <b>coin flip</b>; so code writes the sentences and a rule checker matches each to the record.</div></div>
    </div>
  </div>

  <div class="panel code" style="width:2.6cm">
    <div class="chip">6 Browser</div>
    <div class="dep"><b>MediaPipe</b> landmarks &rarr; crop &rarr; <b>ONNX Runtime Web</b> (EfficientNet-B4, 67 MB) &rarr; contour, part, checked sentences.<span class="note" style="display:block;margin-top:0.08cm">0.59 s per photo on an iPhone, 0.51 s on a desktop; nothing uploaded.</span></div>
  </div>
</div>
<div class="legend"><i style="background:var(--nn)"></i>training and model<i style="background:#374151"></i>outputs<i style="background:var(--chk)"></i>tests<i style="background:var(--code)"></i>code on the device<i style="background:var(--m)"></i>exact footprint <i>M</i></div>
</body></html>
"""
(OUT / "fig_method.html").write_text(html, encoding="utf-8")
subprocess.run([sys.executable, str(HERE / "render_html_fig.py"), str(OUT / "fig_method.html"), str(round(WIDTH_CM * PX))], check=True)
print("fig_method ok:", fk_cls, fk_p, fk["part"], "|", fl_cls, fl_p)
