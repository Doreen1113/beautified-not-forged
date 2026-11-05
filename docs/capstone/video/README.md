# Capstone video (≤ 5 min): `capstone_video.mp4`

1920 × 1080, 30 fps, H.264 + AAC, 4 min 48 s. Chinese narration and subtitles; on-screen text, figures and numbers in English, the same
as the report (`docs/capstone/report_v3/report.tex`) and the final deck (`docs/meeting_20261103/`). Four parts, as the
department asks: background and the problem (0:00–1:20), method (1:20–2:50), results and system (2:50–4:30), future work
(4:30–4:48). It is a showcase of the result, not a progress report: no related-work slide, the audit as a grid of 17 detectors, the idea on one screen.

## How it is made (all deterministic, nothing drawn by hand)

| step | file | output |
|---|---|---|
| narration | `narration.py` (beats, zh-TW spoken text with the technical terms in English; a recorded voice in `audio/rec/<id>.m4a` is used for any beat that has one, the rest is edge-tts `zh-TW-HsiaoYuNeural`, free Microsoft online voice; `--voice`, `--rate` change it) | `audio/<id>.mp3`, `audio/narration.wav`, `cues.js` / `cues.json` (timeline derived from the real audio lengths), `subtitles.srt`, `narration_script.md` |
| demo recording | `record_demo.py` (headless Chrome, DevTools screencast of `docs/demo_ru/index.html`, example 2, light theme, 1180 px) | `demo/f*.jpg`, `demo/demo_frames.js`, `demo/record.json` |
| the film | `film.html` + `film.css` + `film.js`: a 1920 × 1080 page whose every element is a function of the time `t`; `window.seek(t)` sets the frame | — |
| render | `render.py`: headless Chrome steps `seek(t)` at 30 fps, PNG frames piped to ffmpeg (libx264, crf 18), narration muxed | `capstone_video.mp4` (`film_video.mp4` = picture only) |

Rebuild: `python narration.py` (or `--no-tts` to keep the voice files) → `python record_demo.py` → `python render.py --preview 4,30,60`
to look → `python render.py`. Open `film.html#play` over HTTP from the repository root for a silent real-time preview, or
`film.html#t=123.4` for one moment.

Figures come from `docs/capstone/report_v3/figs/` and `docs/meeting_20261103/assets/`; the demo clip is the shipped page.
Every number on screen is in the report; nothing is computed here.
