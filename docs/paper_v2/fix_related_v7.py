from pathlib import Path
p = Path(__file__).resolve().parent / "main_v7.tex"; s = p.read_text(encoding="utf-8")
R = [
 ("Concas et al.~\cite{concas2025} report both errors for two CNNs under a smoothing\nfilter.",
  "Concas et al.~\cite{concas2025} apply smoothing filters at test time to genuine, forged or both test images and report both\nerrors for two CNNs."),
 ("Balestriero et al.~\cite{balestriero2022} show that augmentation and regularisation\nact differently per class.",
  "Balestriero et al.~\cite{balestriero2022} show that augmentation and regularisation\nact differently per class, and Ricker et al.~\cite{ricker2026biasid} train a generated-image detector with JPEG applied to the\nreal class only or the fake class only and find that the direction of the resulting error flips; they study scene images and\ncompression, train neither the both-classes case nor a fix, and do not consider faces or beautification."),
 ("This is shortcut learning~\cite{geirhos2020} under class-dependent\naugmentation~\cite{balestriero2022} in a setting where the sign of the resulting error can be measured.",
  "This is shortcut learning~\cite{geirhos2020} under class-dependent\naugmentation~\cite{balestriero2022}; Ricker et al.~\cite{ricker2026biasid} observed the same sign flip for JPEG in\ngenerated-image detection with one-class training, and we measure the full design, with the both-classes arm, for skin\nsmoothing in face-forgery detection."),
]
for a, b in R:
    c = s.count(a); print(c, a[:50]); s = s.replace(a, b) if c == 1 else s
p.write_text(s, encoding="utf-8")
