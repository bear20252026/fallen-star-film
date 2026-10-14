# The Fallen Star, painted-in-code version: production notes

bear approved the v3 test look (2026-10-08 12:25Z: "make the movie like the test").
Story and timing: ../plan.md and ../script.md (13 scenes, exactly 60:00). Subtitles EN + 中文, no voices.

## Engine
Code: scratchpad/paint/ (backup: ../FallenStar_engine.zip and ../paint-engine.tgz, refresh after each scene).
- core.py painting + scene light (core.ENV), rig.py, motion.py, boy2/boy_anim, sheep/sheep_anim, pip, props, bg, env, cam.
- film/: scene framework. Each scene file sNN.py defines DURATION, shots, performances, subtitles, sound cues.
- render: film/render_scene.py SCENE renders 30 s chunks straight to mp4 (no frame files), 4 workers, restart-safe.
- 2 motion-blur samples per frame (~2.7 s/frame/core) -> about 20 min of rendering per film minute on 4 cores.

## Delivery
Each finished scene: /mnt/project-files/sheep-film2/painted/scenes/SNN.mp4 and a copy on bear's PC
(D:\codex1\FallenStar_painted\, files under 30 MB each, split if needed). Final: parts under 450 MB.

## Status
(updated as scenes finish)

## Status 2026-10-08 14:00Z
All 13 scenes are written and checked with test stills (S01–S13, exactly 60:00).
Rendering one after another (about 2 hours per scene). Finished scenes appear in `painted/scenes/SNN.mp4`
and are copied to bear's PC at `D:\codex1\FallenStar_painted\`.
