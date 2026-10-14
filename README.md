# The Fallen Star — a 60-minute painted film made in pure Python

The pilot's laughing star falls to asteroid B612, and the boy, his sheep and the little star Pip carry it home.
Every frame is painted by code: brush strokes, light, characters and motion are all numpy/OpenCV. No images or 3D models are used.
Subtitles are in English and 中文, with a synthesized score and no voices.

![scenes](stills/s03_check.jpg)

## Layout
| Path | What it is |
|---|---|
| `core.py` | the painting engine: brush strokes, washes, paper, scene light (`core.ENV`) |
| `rig.py`, `motion.py`, `cam.py` | character rigs, natural motion curves, camera |
| `boy2.py`, `boy_anim.py`, `sheep.py`, `sheep_anim.py`, `pip.py`, `pilot.py`, `moth.py`, `clockmaker.py` … | characters |
| `bg.py`, `env.py`, `places.py`, `props*.py` | backgrounds and props |
| `film/s01.py` … `film/s13.py` | the 13 scenes: shots, acting, subtitles, sound cues |
| `film/base.py`, `film/cast.py`, `film/audio.py` | scene framework and music/sound synth |
| `film/render_scene.py`, `film/join_scene.py`, `film/par.sh` | restart-safe chunked renderer |
| `trailer/` | the 59-second trailer (picture + score) |
| `stills/` | one check frame per scene |
| `docs/` | plan, script, production notes |
| `*_try.py`, `test_*.py`, `shot_test*.py` | look-development tests |

## Render
Requires Python 3 with numpy, opencv-python, Pillow and scipy, plus ffmpeg.

```bash
bash film/par.sh s01        # 4 workers render scene 1 in 30 s chunks, then join it -> out/scenes/S01.mp4
python3 film/render_scene.py s05 2   # a single worker; 2 = motion-blur samples per frame
```
Each scene takes about 2 hours on 4 cores. Re-running a script skips chunks that are already finished.
