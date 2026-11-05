"""Style fixes from STYLE_CHECK_v7.md: repeated phrases, sentence-initial ordinals, some colon sentences."""
from pathlib import Path

p = Path(__file__).resolve().parent / "main_v7.tex"; s = p.read_text(encoding="utf-8")
R = [
    ("\\item A controlled exposure study showing that the class receiving smoothed views sets the sign of the error, including an\nevasion route opened by genuine-only views.",
     "\\item A controlled exposure study in which the class receiving smoothed views decides whether the detector accuses or lets\nforgeries through, including an evasion route opened by genuine-only views."),
    ("\\caption{Which class receives smoothed training views sets the sign of the error.", "\\caption{The class that receives smoothed training views decides the direction of the error."),
    ("Seventeen published detectors share one failure: a skin-smoothed genuine face is scored as more forged than the same face\nuntouched, because",
     "Seventeen published detectors share one failure. They rank a skin-smoothed genuine face above its own original because"),
    ("The failure comes from training: the class that receives smoothed views sets the sign of the error, and genuine-only\nviews open an evasion route.",
     "The failure comes from training. Which class receives smoothed views decides whether the error is an accusation or an\nevasion, and genuine-only views open an evasion route."),
    ("Three findings from FF++-only arms", "The FF++-only arms with pre-registered bars give three findings"),
    ("(supplement Sec.~\\ref{S-sec:chain},\nTable~\\ref{S-tab:tradeofffull}). First, no other view substitutes for smoothing:", "(supplement Sec.~\\ref{S-sec:chain},\nTable~\\ref{S-tab:tradeofffull}). No other view substitutes for smoothing."),
    ("Second, genuine-only smoothing views are an evasion route: P1-smooth", "Genuine-only smoothing views are an evasion route. P1-smooth"),
    ("Third, a class-asymmetric form is learnt as a label: when genuine items", "A class-asymmetric form is learnt as a label. When genuine items"),
    ("\\textbf{The cue is the signature, not the blur.}", "\\textbf{The cue is the beautification signature.}"),
]
n = 0
for a, b in R:
    c = s.count(a)
    if c != 1:
        print("SKIP (count %d): %s" % (c, a[:70])); continue
    s = s.replace(a, b); n += 1
p.write_text(s, encoding="utf-8"); print("applied", n, "of", len(R))
